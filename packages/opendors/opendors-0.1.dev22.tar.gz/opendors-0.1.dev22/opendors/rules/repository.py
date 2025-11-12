import hashlib
import json
import re
import shlex
import shutil
import subprocess
import tarfile
from collections.abc import Generator
import uuid
from collections import namedtuple
from json import JSONDecodeError
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from typing import Union, Any, NamedTuple
import time
import os

from git import Repo, Git
from git.exc import GitCommandError
from svine import SvnClient as Svn
from svine import SvnException

from opendors.abc import WorkflowRule
from opendors.model import (
    ResearchSoftware,
    VCS,
    Corpus,
    LatestVersion,
    VersionType,
    SourceCodeRepository,
    Platform,
    Mention,
    MentionedVersion,
    DeterminationSource,
    SvnStructure,
    Language,
    LicenseData,
    MetadataFile,
)
from opendors.rules.urls import determine_gitlab_subgroup_url_candidates

DatedShaRef = namedtuple("DatedShaRef", ["date", "ref", "sha", "tag_sha"])

PREFIX_COMMIT_ID = "rev:"
PREFIX_TAG_ID = "rel:"


def date_sort(to_sort: list[DatedShaRef]) -> list[DatedShaRef]:
    to_sort = [dsr for dsr in to_sort if dsr is not None]
    to_sort.sort(key=lambda dsr: dsr.date, reverse=True)
    return to_sort


class CloneRetrieverError(Exception):
    pass


class CloneRetriever(WorkflowRule):
    """
    TODO
    """

    def __init__(
        self,
        input_json: str,
        output_json: str,
        clone_dir: str,
        github_user: str,
        github_token: str,
        gitlab_user: str,
        gitlab_token: str,
        sourceforge_user: str,
        sourceforge_token: str,
        storage_dir: str = None,
        log_file: str = str(datetime.now().timestamp()) + ".log",
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.output_json = output_json
        self.clone_dir = clone_dir
        self.github_user = github_user
        self.github_token = github_token
        self.gitlab_user = gitlab_user
        self.gitlab_token = gitlab_token
        self.sourceforge_user = sourceforge_user
        self.sourceforge_token = sourceforge_token
        self.storage_dir = storage_dir
        self.git = Git()

    ##################################################
    ########## Methods
    ##################################################
    def get_clone_url(self, repo: SourceCodeRepository, platform: Platform) -> str:
        assert repo.vcs == VCS.git
        _url = "https://"
        user = token = ""
        if platform == Platform.GITHUB_COM:
            user = self.github_user
            token = self.github_token
        elif platform == Platform.GITLAB_COM:
            user = self.gitlab_user
            token = self.gitlab_token
        elif platform == Platform.SOURCEFORGE_NET:
            user = self.sourceforge_user
            token = self.sourceforge_token
        if platform != Platform.BITBUCKET_ORG:
            has_user = user != "" and user is not None
            has_token = token != "" and token is not None
            if not has_user or not has_token:
                raise CloneRetrieverError(
                    f"Username or token for {platform.value} not given, "
                    "cannot clone repository without login credentials."
                )
            login = user + ":" + token + "@"
            _url = _url + login + str(repo.clone_url)[8:]
        else:
            _url = _url + str(repo.clone_url)[8:]
        return _url

    def retrieve_git_repo(self, software: ResearchSoftware, repo: SourceCodeRepository) -> Repo | None:
        clone_suffix = uuid.uuid4().hex
        clone_path = Path(self.clone_dir) / clone_suffix
        try:
            light_clone = Repo.clone_from(
                self.get_clone_url(repo, software.platform),
                to_path=clone_path,
                multi_options=[
                    "--origin origin",
                    "--config transfer.fsckobjects=false",
                    "--no-checkout",
                    "--filter=tree:0",
                ],
                allow_unsafe_options=True,
            )
        except GitCommandError as e:
            self.log.debug("Cloning %s failed with following error.", repo.clone_url)
            self.log.debug(e)
            repo.accessible = False
            return None

        if light_clone is not None:
            repo.accessible = True
            return light_clone

    def get_version_from_publication_date(
        self,
        mention: Mention,
        tags: list[DatedShaRef],
        commits: list[DatedShaRef],
        identification_url: str = None,
    ) -> bool:
        date = mention.pub_date
        dt_date = self.convert_to_naive_datetime(date)
        last_version_before = self.get_last_version_before(dt_date, tags)
        if last_version_before is not None:
            mention.version = MentionedVersion(
                identification_url=identification_url,
                type=VersionType.TAG,
                based_on=DeterminationSource.PUB_DATE,
                version=last_version_before.sha,
                reference=last_version_before.ref,
                date=last_version_before.date,
            )
            return True
        else:
            last_commit_before = self.get_last_version_before(dt_date, commits)
            if last_commit_before is not None:
                mention.version = MentionedVersion(
                    identification_url=identification_url,
                    type=VersionType.REVISION,
                    based_on=DeterminationSource.PUB_DATE,
                    version=last_commit_before.ref,
                    reference=last_commit_before.ref,
                    date=last_commit_before.date,
                )
                return True
        return False

    @staticmethod
    def convert_to_naive_datetime(date):
        if re.fullmatch(r"\d{4}", date):
            date = date + "-01-01"
        elif re.fullmatch(r"\d{4}-\d{2}", date):
            date = date + "-01"
        date = [int(s) for s in date.split("-")]
        dt_date = datetime(date[0], date[1], date[2])
        return dt_date

    def set_mentions_versions(
        self,
        platform: Platform,
        mentions: list[Mention],
        tags: list[DatedShaRef],
        branches: dict[str, list[DatedShaRef]],
        date_sorted_commits: list[DatedShaRef],
        commit_dates: dict[str, datetime],
    ):
        for m in mentions:
            pub_date = self.convert_to_naive_datetime(m.pub_date)
            ver = m.version
            set_successfully = False
            if ver is None:
                set_successfully = self.get_version_from_publication_date(m, tags, date_sorted_commits)
            elif ver.type == VersionType.NAME:
                set_successfully = self.get_git_ref_from_name(pub_date, ver, tags, branches)
            elif ver.type == VersionType.PATH:
                set_successfully = self.get_git_ref_from_path(pub_date, platform, ver, tags, branches, commit_dates)
            elif ver.type == VersionType.BRANCH:
                rev = None
                if ver.version in branches:
                    date_ordered_dsr = branches[ver.version]
                    if date_ordered_dsr is not None:
                        rev = self._get_last_dsr_before(pub_date, date_ordered_dsr)
                else:
                    self.log.warning(f"Could not find branch name {ver.version} in branches.")
                if rev is not None:
                    branch = ver.version
                    ver.version = rev.sha
                    ver.reference = branch
                    ver.date = rev.date
                    set_successfully = True
                else:
                    set_successfully = self.get_version_from_publication_date(
                        m, tags, date_sorted_commits, ver.identification_url
                    )
            elif ver.type == VersionType.REVISION:
                set_successfully = self.get_revision_from_repo(ver, date_sorted_commits)
            elif ver.type == VersionType.TAG:
                set_successfully = self.get_revision_for_tag(ver, tags)
            # Catch cases where determining version didn't work
            if not set_successfully and ver is not None:
                if not self.get_version_from_publication_date(m, tags, date_sorted_commits, ver.identification_url):
                    # Even setting a publication date hasn't worked,
                    # so record current version as reference and remove version data
                    ver.reference = ver.version
                    ver.version = None
            else:
                self.log.debug("Mention %s has no version. Not setting version.", m)

    # ########
    # # Static methods
    # ########

    @staticmethod
    def _get_last_dsr_before(pub_date: datetime, ordered_dsr_list: [DatedShaRef]) -> DatedShaRef | None:
        for dsr in ordered_dsr_list:
            if dsr.date < pub_date:
                return dsr

    @staticmethod
    def get_git_ref_from_name(
        pub_date: datetime,
        version: MentionedVersion,
        tags: list[DatedShaRef],
        branches: dict[str, list[DatedShaRef]],
    ) -> bool:
        name = version.version
        # Check if name is a tag or branch, and set accordingly
        # Check tags
        for t in tags:
            if t.ref == name:
                version.type = VersionType.TAG
                version.version = t.sha
                version.reference = t.ref
                version.date = t.date
                return True
        # Check branches
        if name in branches:
            ordered_dsr = branches[name]
            last_dsr_before_pub_date = CloneRetriever._get_last_dsr_before(pub_date, ordered_dsr)
            if last_dsr_before_pub_date is None:
                return False
            commit = last_dsr_before_pub_date.sha
            version.type = VersionType.BRANCH
            version.version = commit
            version.reference = name
            version.date = last_dsr_before_pub_date.date
            return True
        return False

    def get_git_ref_from_path(
        self,
        pub_date: datetime,
        platform: Platform,
        version: MentionedVersion,
        tags: list[DatedShaRef],
        branches: dict[str, list[DatedShaRef]],
        commit_dates: dict[str, datetime],
    ) -> bool:
        if platform in [
            Platform.GITHUB_COM,
            Platform.GITLAB_COM,
            Platform.BITBUCKET_ORG,
        ]:
            ver = version.version
            if ver.startswith(("tree/", "blob/", "-/tree/", "-/blob/", "src/")):
                pot_ver = ver.split("/")[2 if ver.startswith("-") else 1]
                for tag in tags:
                    if tag.ref == pot_ver:
                        version.reference = tag.ref
                        version.version = tag.sha
                        version.type = VersionType.TAG
                        version.date = tag.date
                        return True
                if pot_ver in branches:
                    last_dsr_before_pub_date = CloneRetriever._get_last_dsr_before(pub_date, branches[pot_ver])
                    if last_dsr_before_pub_date is not None:
                        version.reference = last_dsr_before_pub_date.ref
                        version.version = last_dsr_before_pub_date.sha
                        version.type = VersionType.BRANCH
                        version.date = last_dsr_before_pub_date.date
                        return True
                    else:
                        self.log.debug(
                            f"Could not retrieve commit for existing branch {pot_ver} "
                            f"earlier than publication date {pub_date}."
                        )
                can_be_git_commit = re.fullmatch(r"[0-9a-f]{7,40}", pot_ver) is not None
                for commit_ref, commit_date in commit_dates.items():
                    if pot_ver == commit_ref:
                        version.reference = commit_ref
                        version.version = commit_ref
                        version.type = VersionType.REVISION
                        version.date = commit_date
                        return True
                    elif can_be_git_commit and commit_ref.startswith(pot_ver):
                        version.reference = commit_ref
                        version.version = commit_ref
                        version.type = VersionType.REVISION
                        version.date = commit_date
                        return True
        return False

    @staticmethod
    def retrieve_latest(repo, tags: list[DatedShaRef], commits: list[DatedShaRef]):
        if len(tags) > 0:
            latest_tag = tags[0]
            repo.latest = LatestVersion(
                version=latest_tag.ref,
                version_type=VersionType.TAG,
                date=latest_tag.date,
                revision_id=latest_tag.sha,
                tag_sha=latest_tag.tag_sha,
            )
        elif len(commits) > 0:
            latest_commit = commits[0]
            repo.latest = LatestVersion(
                version=latest_commit.ref,
                version_type=VersionType.REVISION,
                date=latest_commit.date,
                revision_id=latest_commit.sha,
            )

    @staticmethod
    def get_last_version_before(naive_date: datetime, sorted_refs: list[DatedShaRef]) -> DatedShaRef:
        for st in sorted_refs:
            std = st.date
            if std.tzinfo is not None and std.tzinfo.utcoffset(st.date) is not None:
                std = std.replace(tzinfo=None)
            if std < naive_date:
                return st

    @staticmethod
    def get_head_commit_date(_repo: Repo) -> DatedShaRef:
        c = _repo.active_branch.commit
        return DatedShaRef(
            ref=c.hexsha,
            date=datetime.fromtimestamp(c.committed_date),
            sha=c.hexsha,
            tag_sha=None,
        )

    @staticmethod
    def date_sort_git_tags(git_repo: Repo) -> list[DatedShaRef]:
        g = git_repo.git

        tags_output = g.for_each_ref(
            "refs/tags/*",
            format="%(refname:lstrip=2) == %(objectname) == %(objecttype) == %(creatordate:unix)",
        )
        dated_tags = []
        undated_tags = []
        for tag_str in tags_output.splitlines():
            is_undated = False
            tag_split = tag_str.split(" == ")
            tag_date_str = tag_split[3]
            if len(tag_date_str) == 0:
                is_undated = True
            tag_name = tag_split[0]
            tag_type = tag_split[2]
            sha = tag_split[1]
            if tag_type.strip() in ["commit", "blob", "tree"]:
                tag_sha = None
                commit_sha = sha
            elif tag_type.strip() == "tag":
                tag_sha = sha
                commit_sha = CloneRetriever._get_commit_sha_for_tag(g, tag_name)
            else:
                raise ValueError(f"Unhandled tag type: {tag_type}.")
            if is_undated:
                undated_tags.append(
                    DatedShaRef(
                        date=None,
                        sha=commit_sha,
                        ref=tag_name,
                        tag_sha=tag_sha,
                    )
                )
            else:
                dated_tags.append(
                    DatedShaRef(
                        date=datetime.fromtimestamp(int(tag_date_str)).replace(tzinfo=None),
                        sha=commit_sha,
                        ref=tag_name,
                        tag_sha=tag_sha,
                    )
                )

        return sorted(dated_tags, key=lambda dsr: dsr.date, reverse=True) + undated_tags

    def get_git_branches(self, git_repo: Repo, versions: dict[VersionType, set]) -> dict[str, list[DatedShaRef]]:
        remote = git_repo.remote()
        remote_name = remote.name
        branches = {}
        remote_branches = []
        remote_branches_str = git_repo.git.branch(r=True)
        for remote_branch_str in str(remote_branches_str).splitlines():
            remote_branch = remote_branch_str.strip()
            if " -> " in remote_branch:
                remote_branch = remote_branch.split(" -> ")[1].strip()
            remote_branches.append(remote_branch)

        if versions is not None:
            for filtered_branch_name in versions[VersionType.BRANCH].union(versions[None]):
                if (remote_branch_name := f"{remote_name}/{filtered_branch_name}") in remote_branches:
                    self.log.debug(f"Getting commits for remote branch {filtered_branch_name}.")
                    branch_name = remote_branch_name.split(remote_name + "/")[1]
                    if branch_name.startswith("HEAD"):
                        continue
                    remote_branch = f"remotes/{remote_name}/" + branch_name
                    branch_commits = list(
                        git_repo.iter_commits(remote_branch, max_count=None)
                    )  # Get all commits for the branch
                    commits = [
                        DatedShaRef(
                            date=datetime.fromtimestamp(c.committed_date),
                            sha=c.hexsha,
                            ref=branch_name,
                            tag_sha=None,
                        )
                        for c in branch_commits
                    ]
                    branches[branch_name] = commits
        return branches

    def get_git_commits(self, git_repo: Repo) -> (list[DatedShaRef], dict[str, datetime]):
        commits = []
        commit_date_map = {}
        try:
            for c in git_repo.iter_commits():
                date = datetime.fromtimestamp(c.committed_date)
                ref = str(c)
                commits.append(DatedShaRef(date=date, sha=ref, ref=ref, tag_sha=None))
                commit_date_map[ref] = date
        except ValueError as ve:
            sve = str(ve)
            if sve.startswith("Reference at") and sve.endswith("does not exist"):
                self.log.warning(f"No reference found for repo {git_repo}. May be an empty repo.")
            else:
                raise ve
        sorted_commits = sorted(commits, key=lambda cd: cd.date, reverse=True)
        return sorted_commits, commit_date_map

    ##########
    ### Main method
    ##########
    def run(self) -> None:
        """
        FIXME Document why GitLab subgroups are treated as separate software, while
        Sourceforge repos are always treated as separate repos of the same project, i.e.,
        because it cannot be determined whether the repos contain the same code at, e.g., different iterations
        (old SVN repo, new git repo), or whether different repos in the same SVN root are different projects
        or erratic use of SVN or different modules of the same project.
        """
        with open(str(self.input_json), "r") as s_inf:
            s = ResearchSoftware.model_validate_json(s_inf.read())
        lst_software = []
        if s is not None:
            if s.platform == Platform.GITLAB_COM:
                lst_software = self.evaluate_gitlab_repos(s)
            else:
                lst_software = [s]
            for software in lst_software:
                s.repositories = self.retrieve_repositories(software)

        # Write single software into a corpus for better merging
        c = Corpus(research_software=lst_software)
        self.write_corpus(c, self.output_json)

        abs_clone_dir = Path(self.clone_dir).absolute()
        if abs_clone_dir.exists():
            shutil.rmtree(self.clone_dir, ignore_errors=True)

    def evaluate_gitlab_repos(self, software: ResearchSoftware) -> [ResearchSoftware]:
        """
        Evaluates the GitLab repositories of a software: checks if repos can be cloned, and if not,
        if subgroups exist that may have led to hitherto incorrect determination of clone URLs.

        Attempts to fix clone URLs for subgroups, then returns the original software with a new configuration of
        repositories.

        :param software: A research software on the gitlab.com platform
        :return: The research software with evaluated repositories.
        """
        for r in software.repositories:
            if r.vcs == VCS.git:
                git_repo = self.retrieve_git_repo(software, r)
                if git_repo is None:
                    self.log.debug(f"GitLab repository {r.clone_url} not cloneable, checking potential subgroups.")
                    return self.determine_subgroups(software)
        return [software]

    def retrieve_from_repo(
        self, software: ResearchSoftware, repo: SourceCodeRepository
    ) -> (SourceCodeRepository, Union[Repo, Svn]):
        if repo.vcs == VCS.git:
            git_repo = self.retrieve_git_repo(software, repo)
            if repo.accessible and git_repo is not None:
                # Determine if tags and branches are potentially mentioned needed at all
                mentioned_versions = self.filter_tags_branches(software)

                date_sorted_tags = self.date_sort_git_tags(git_repo)
                branches = self.get_git_branches(git_repo, mentioned_versions)
                # Commits are needed anyway
                (
                    date_sorted_commits,
                    ref_date_map,
                ) = self.get_git_commits(git_repo)

                self.retrieve_latest(repo, date_sorted_tags, date_sorted_commits)
                if repo.main_repo:
                    self.set_mentions_versions(
                        software.platform,
                        software.mentions,
                        date_sorted_tags,
                        branches,
                        date_sorted_commits,
                        ref_date_map,
                    )
                return repo, git_repo
            else:
                return repo, None
        elif repo.vcs == VCS.svn:
            if repo.accessible:
                (
                    date_sorted_revisions,
                    revision_date_map,
                    date_sorted_tags,
                    branches,
                ) = self.get_revisions_svn(repo.structure)
                # First, get latest, then, get mentions
                self.set_latest_from_svn(repo, date_sorted_revisions, date_sorted_tags)
                if repo.main_repo:
                    self.set_mentions_versions(
                        software.platform,
                        software.mentions,
                        date_sorted_tags,
                        branches,
                        date_sorted_revisions,
                        revision_date_map,
                    )
                return repo, Svn(repo.structure.url.rstrip("/"))
            else:
                return repo, None
        else:
            self.log.debug(f"Ignoring non-git/svn repository {repo.clone_url} for software {software.canonical_url}.")
            return repo, None

    def determine_subgroups(self, software: ResearchSoftware) -> list[ResearchSoftware]:
        # Clone URL is being determined from mentioning URLs, could now potentially be determinable from PATH version,
        # e.g., "repo/-/tree/...". Collect URLs
        collected_urls = set()

        for m in software.mentions:
            for u in m.mentioning_urls:
                collected_urls.add(str(u))
            if m.version is not None and m.version.type == VersionType.PATH:
                collected_urls.add(str(m.version.identification_url))

        asserted_repos = set()

        for url in determine_gitlab_subgroup_url_candidates(collected_urls):
            try:
                self.git.ls_remote(
                    f"https://{self.gitlab_user}:{self.gitlab_token}@{url[8:]}"  # noqa E231
                )
            except GitCommandError:
                self.log.debug(f"Potential GitLab subgroup repository '{url}' does not exist.")
                continue
            asserted_repos.add(url)

        if len(asserted_repos) > 0:
            return self.reconfigure_gitlab_subgroup_repositories(software, asserted_repos)
        else:
            # The simplest case: GitLab repo cannot have a subgroup, hence simply doesn't exist
            return [software]

    @staticmethod
    def reconfigure_gitlab_subgroup_repositories(
        prev_software: ResearchSoftware, asserted_repos: set[str]
    ) -> list[ResearchSoftware]:
        def _remove_subgroup_prefix(repo_str: str, prev_ver: MentionedVersion) -> str:
            repo_path = "/".join(urlparse(repo_str).path.split("/")[3:])
            prev_ver_str = prev_ver.version
            return prev_ver_str.replace(repo_path + "/", "")

        lst_subgroup_software = []
        prev_ms = prev_software.mentions
        prev_repos = prev_software.repositories
        for subgroup_repo in asserted_repos:
            canon_url = subgroup_repo.split(".git")[0]
            new_repos = []
            new_mentions = []
            for r in prev_repos:
                new_repos.append(
                    SourceCodeRepository(
                        vcs=r.vcs,
                        clone_url=canon_url + ".git",
                        accessible=True,
                        latest=None,
                        main_repo=True,
                    )
                )
            for m in prev_ms:
                prev_version = m.version
                new_ver = None
                if prev_version is not None:
                    if prev_version.based_on == DeterminationSource.URL and canon_url in str(
                        prev_version.identification_url
                    ):
                        new_ver = MentionedVersion(
                            identification_url=prev_version.identification_url,
                            type=prev_version.type,
                            based_on=prev_version.based_on,
                            version=_remove_subgroup_prefix(canon_url, prev_version),
                            archive_url=prev_version.archive_url,
                        )
                new_mentioning_urls = set()
                new_mentioning_urls.update([u if u.startswith(canon_url) else None for u in m.mentioning_urls])
                if None in new_mentioning_urls:
                    new_mentioning_urls.remove(None)

                if len(new_mentioning_urls) > 0:
                    new_mentions.append(
                        Mention(
                            metadata_source=m.metadata_source,
                            id=m.id,
                            id_type=m.id_type,
                            mentioning_urls=new_mentioning_urls,
                            version=new_ver,
                            pub_date=m.pub_date,
                        )
                    )

            lst_subgroup_software.append(
                ResearchSoftware(
                    canonical_url=canon_url,
                    mentions=new_mentions,
                    platform=Platform.GITLAB_COM,
                    repositories=new_repos,
                )
            )

        return lst_subgroup_software

    @staticmethod
    def get_svn_root(url: str) -> str | None:
        remote = Svn(str(url))
        try:
            info = CloneRetriever.svn_info(remote)
            if info is not None and info.repository_root is not None:
                return info.repository_root
            else:
                return None
        except SvnException:
            raise

    @staticmethod
    def get_svn_dirs(root_url: str) -> set[str]:
        remote = Svn(str(root_url))
        dirs = set()
        try:
            for entry in CloneRetriever.svn_list(remote):
                # Entries are not URLs, but suffixes to the passed root_url!
                if entry.endswith("/"):
                    dirs.add(entry)
        except SvnException:
            pass
        return dirs

    @staticmethod
    def get_svn_structure_from_dirs(root_url: str, dirs: set[str]) -> SvnStructure:
        """

        :param root_url:
        :param dirs: A set of directory names, suffixed with "/"
        :return:
        """
        trunk = tags = branches = False
        compliance = 0
        sub_dirs = set()
        for dir_suffix in dirs:
            if dir_suffix.endswith("/"):
                sub_dirs.add(dir_suffix)
            if dir_suffix == "trunk/":
                trunk = True
                compliance += 1
            elif dir_suffix == "tags/":
                tags = True
                compliance += 1
            elif dir_suffix == "branches/":
                branches = True
                compliance += 1
        return SvnStructure(
            url=root_url.rstrip("/"),
            trunk=trunk,
            tags=tags,
            branches=branches,
            compliance=compliance,
            sub_dirs={d for d in sub_dirs},
        )

    def determine_svn_structures(self, root_structure: SvnStructure) -> set[SvnStructure]:
        sub_structures = set()

        # Construct URLs
        sub_dir_urls = {root_structure.url + "/" + sd for sd in root_structure.sub_dirs}

        for sub_dir_url in sub_dir_urls:
            sub_dir_dirs = self.get_svn_dirs(sub_dir_url)
            if len(sub_dir_dirs) > 0:
                url_structure = self.get_svn_structure_from_dirs(sub_dir_url, sub_dir_dirs)
                if url_structure.trunk:  # Only add structures which have at least a trunk
                    sub_structures.add(url_structure)
        return sub_structures

    @staticmethod
    def set_latest_from_svn(
        svn_repo: SourceCodeRepository,
        date_sorted_revisions: list[DatedShaRef],
        date_sorted_tags: list[DatedShaRef],
    ) -> LatestVersion | None:
        latest = typ = None
        if len(date_sorted_tags) > 0:
            latest = date_sorted_tags[0]
            typ = VersionType.TAG

        elif len(date_sorted_revisions) > 0:
            latest = date_sorted_revisions[0]
            typ = VersionType.REVISION
        if latest is not None and typ is not None:
            svn_repo.latest = LatestVersion(
                version=latest.ref,
                version_type=typ,
                languages=None,
                date=latest.date,
                revision_id=latest.sha,
            )
            return svn_repo.latest
        else:
            return None

    def get_revisions_svn(
        self, structure: SvnStructure, retry: bool = True
    ) -> tuple[
        list[DatedShaRef],
        dict[str, datetime],
        list[DatedShaRef],
        dict[str, list[DatedShaRef]],
    ]:
        def _treat_503(e: SvnException):
            if retry:
                self.log.warning(f"SVN error: {e}. Waiting, then retrying once.")
                time.sleep(5)
                self.get_revisions_svn(structure, False)
            else:
                self.log.error(
                    f"Could not retrieve branches from SVN repository at {structure.url}, due to an SVN error: {e}."
                )

        tags = []
        branches = {}
        if structure.trunk:
            revisions, rev_date_map = self.get_revisions_for_url(structure.url.rstrip("/") + "/trunk")
        else:
            revisions, rev_date_map = self.get_revisions_for_url(structure.url)
        if structure.tags:
            remote = Svn(structure.url.rstrip("/") + "/tags")
            try:
                for tag in CloneRetriever.svn_list(remote):
                    tags.append(self.get_latest_revision_for_url(structure.url.rstrip("/") + "/tags/" + tag))
            except SvnException as svne:
                _treat_503(svne)
        if structure.branches:
            remote = Svn(structure.url.rstrip("/") + "/branches")
            try:
                for branch in CloneRetriever.svn_list(remote):
                    branch_name = branch.rstrip("/")
                    branches[branch_name] = self.get_revisions_for_url(
                        structure.url.rstrip("/") + "/branches/" + branch
                    )[0]
            except SvnException as svne:
                _treat_503(svne)

        return date_sort(revisions), rev_date_map, date_sort(tags), branches

    def get_revisions_for_url(self, url: str) -> (list[DatedShaRef], dict[str, datetime]):
        revisions = []
        rev_date_map = {}
        remote = Svn(url)

        try:
            for log in CloneRetriever.svn_log(remote):
                revisions.append(
                    DatedShaRef(
                        date=log.date,
                        ref=str(log.revision),
                        sha=str(log.revision),
                        tag_sha=None,
                    )
                )
                rev_date_map[str(log.revision)] = log.date
        except (ValueError, AttributeError) as de:
            self.log.warning(
                f"Could not retrieve log from SVN repository at {url}, probably due to a decoding error: {de}.",
                exc_info=True,
            )
        except SvnException as svne:
            self.log.warning(f"Could not retrieve log from SVN repository at {url}, due to an SVN error: {svne}.")

        return revisions, rev_date_map

    def get_latest_revision_for_url(self, url: str) -> [DatedShaRef]:
        ref = url.rstrip("/").split("/")[-1]
        remote = Svn(url)

        try:
            for log in CloneRetriever.svn_log(remote, limit=1):
                return DatedShaRef(date=log.date, ref=ref, sha=str(log.revision), tag_sha=None)
        except (ValueError, AttributeError) as de:
            self.log.warning(
                f"Could not retrieve log from SVN repository at {url}, probably due to a decoding error: {de}.",
                exc_info=True,
            )
        except SvnException as svne:
            self.log.warning(f"Could not retrieve log from SVN repository at {url}, due to an SVN error: {svne}.")

    @staticmethod
    def get_revision_for_tag(version: MentionedVersion, tags: list[DatedShaRef]) -> bool:
        set_successfully = False
        for tag in tags:
            if tag.ref == version.version:
                version.reference = version.version
                version.version = tag.sha
                version.date = tag.date
                set_successfully = True
        return set_successfully

    @staticmethod
    def get_revision_from_repo(ver: MentionedVersion, date_sorted_commits: list[DatedShaRef]) -> bool:
        set_successfully = False
        for commit in date_sorted_commits:
            if ver.version == commit.sha:
                ver.reference = ver.version
                ver.date = commit.date
                set_successfully = True
        return set_successfully

    def determine_main_svn_repo(
        self, repositories: list[SourceCodeRepository], software_name: str
    ) -> list[SourceCodeRepository, SvnStructure]:
        """
        FIXME
        """
        if len(repositories) == 1:
            repositories[0].main_repo = True
            return repositories
        elif len(repositories) > 1:
            # First test for name suffix as this is the most reliable determinator
            # Collect sorted repo tuples where the potential software name is in the last path section of the clone URL
            # Then sort by compliance and pick first maximally compliant as main repo
            name_matching_repos = set()
            for repo in repositories:
                suffix = str(repo.clone_url).split("/")[-1]
                if software_name in suffix:
                    name_matching_repos.add(repo)
            if len(name_matching_repos) > 0:
                self.sort_by_compliance(name_matching_repos)[0].main_repo = True
                return repositories
            # Determine by compliance, then sorted alphabetically by clone URL
            compliance_clusters = {0: [], 1: [], 2: [], 3: []}
            for repo in repositories:
                compliance_clusters[repo.structure.compliance].append(repo)
            for cluster in compliance_clusters.values():
                cluster.sort(key=lambda r: r.clone_url)
            comp = 3
            while comp >= 0:
                if len(repo_lst := compliance_clusters[comp]) > 0:
                    repo_lst[0].main_repo = True
                    return repositories
                else:
                    comp -= 1
        return repositories

    def retrieve_repositories(self, software: ResearchSoftware) -> list[SourceCodeRepository]:
        num_repos = len(software.repositories)
        if num_repos == 0:
            self.log.debug(f"Skip software with no recorded repositories: {software.canonical_url}.")
            return software.repositories
        if software.platform == Platform.SOURCEFORGE_NET:
            input_repos = {"git": [], "svn": [], "cvs": []}
            for r in software.repositories:
                # Reset the information regarding which is the main repository
                if r.main_repo:
                    r.main_repo = False
                input_repos[str(r.vcs.value)].append(r)
            input_repos["svn"] = self.evaluate_svn_repos(input_repos["svn"])
            if len(input_repos["git"]) >= 1:
                # Set the first git repo to be the main repo
                input_repos["git"][0].main_repo = True
            elif len(input_repos["svn"]) >= 1:
                software_name = software.canonical_url.path.split("/")[-1]
                self.determine_main_svn_repo(input_repos["svn"], software_name)
            # Reset the repositories for software to evaluated ones
            evaluated_repos = []
            for r_lst in input_repos.values():
                evaluated_repos.extend(r_lst)
            software.repositories = evaluated_repos
            num_main_repos = sum(1 for r in software.repositories if r.main_repo)
            if num_main_repos == 1:
                for repo in software.repositories:
                    self.process_repo(software, repo)
            elif num_main_repos == 0 and len(software.repositories) == 1 and software.repositories[0].vcs == VCS.cvs:
                self.log.debug(f"Skipping single CVS repository software {software.canonical_url}.")
            else:
                raise CloneRetrieverError(
                    f"Software {software.canonical_url} has < 1 or > 1 repository marked as main repository: "
                    f"{software.repositories}"
                )
            return software.repositories

        else:
            if num_repos == 1:
                repo = software.repositories[0]
                repo.main_repo = True
                return [self.process_repo(software, repo)]
            else:
                raise CloneRetrieverError(
                    f"Found more than one repository for software {software.canonical_url} "
                    f"on platform {software.platform}."
                )

    @staticmethod
    def sort_by_compliance(repositories: set[SourceCodeRepository]):
        return sorted(repositories, key=lambda r: r.structure.compliance)

    def evaluate_svn_repos(self, input_repos: list[SourceCodeRepository]) -> list[SourceCodeRepository]:
        """
        Assesses the svn repository to see if it is actually a multi-repository repository, i.e.,
        if the repository root is in standard layout, or if not, if it contains a trunk/ directory,
        or if not, if any of the repo directories contain a trunk/ directory. If more than one repository
        is found at the repository URL, these are split into separate SourceCodeRepository entries
        in the software's repositories list.

        Else, only the single root repository is returned.

        :param input_repos: The list of input repositories to evaluate
        :return: A list of source code repositories for the given list of input repositories
        """
        evaluated_repos = []

        for input_repo in input_repos:
            try:
                root_url = self.get_svn_root(input_repo.clone_url)
                if root_url is None:
                    self.log.error(f"Could not retrieve root URL for repository at {input_repo.clone_url}.")
                    continue
            except SvnException:
                self.log.info(f"Repository at {input_repo.clone_url} is not accessible.")
                input_repo.accessible = False
                evaluated_repos.append(input_repo)
                continue
            dirs = self.get_svn_dirs(root_url)
            root_structure = self.get_svn_structure_from_dirs(root_url, dirs)
            input_repo.structure = root_structure
            input_repo.trunk = root_structure.trunk

            dir_structures = self.determine_svn_structures(root_structure)
            if len(dir_structures) == 0:
                self.log.debug(f"Single root repo: {root_structure}, no repos in directories.")
                # Only single root repo, regardless of existence of trunk/,
                # reset repo and return
                input_repo.clone_url = root_url.rstrip("/")
                input_repo.accessible = True
                evaluated_repos.append(input_repo)

            elif root_structure.trunk:
                self.log.debug(
                    f"Root is repo: {root_structure}, repos in directories: "
                    f"{[s.url.split('/')[-1] for s in dir_structures]}."
                )
                # Root is a repo, but other repos exist,
                # reset repo to root, add other repos
                input_repo.clone_url = root_url
                input_repo.accessible = True
                evaluated_repos.append(input_repo)
                for structure in dir_structures:
                    evaluated_repos.append(
                        SourceCodeRepository(
                            vcs=VCS.svn,
                            clone_url=structure.url.rstrip("/"),
                            accessible=True,
                            latest=None,
                            main_repo=False,
                            structure=structure,
                            trunk=structure.trunk,
                        ),
                    )

            else:
                self.log.debug(
                    f"No repo in root, repos in directories: {[s.url.split('/')[-1] for s in dir_structures]}."
                )
                # Root is no repo, remove root repo and add other repos
                for structure in dir_structures:
                    evaluated_repos.append(
                        SourceCodeRepository(
                            vcs=VCS.svn,
                            clone_url=structure.url.rstrip("/"),
                            accessible=True,
                            latest=None,
                            main_repo=False,
                            structure=structure,
                        ),
                    )
        return evaluated_repos

    @staticmethod
    def filter_tags_branches(
        software: ResearchSoftware,
    ) -> dict[VersionType, set[str]] | None:
        """
        Filters (potential) branch and tag names to retrieve from repo.

        :param software: The research software data
        :return:
        """
        versions = {
            VersionType.TAG: set(),
            VersionType.BRANCH: set(),
            VersionType.REVISION: set(),
            None: set(),
        }
        for m in software.mentions:
            v = m.version
            if v is None:
                continue
            if v.type in (VersionType.TAG, VersionType.BRANCH, VersionType.REVISION):
                versions[v.type].add(v.version)
            elif v.type == VersionType.NAME:
                versions[None].add(v.version)
            else:
                if v.version is not None and (version := CloneRetriever.determine_version(v.version)) is not None:
                    versions[None].add(version)
        return versions if any(s is not set() for s in versions.values()) else None

    @staticmethod
    def determine_version(path: str) -> str | None:
        """
        Determines a tag, branch or revision version from a path version.

        :param path: the path or name version to determine the tag name or branch name from
        """
        path = path.removeprefix("-/")
        if path.startswith(("tree/", "blob/", "src/")):
            version = path.split("/")[1]
            return version if version != "" else None
        return None

    def clone_latest_git(self, retrieved_repo: SourceCodeRepository, remote_repo: Repo) -> Repo | None:
        latest = retrieved_repo.latest
        if latest is None:
            return None
        else:
            try:
                remote_repo.git.checkout(latest.version)
                return remote_repo
            except GitCommandError as gce:
                self.log.error(f"Failed to checkout version {latest.version} from {remote_repo}.\n{gce}")
                return None

    @staticmethod
    def _determine_actual_svn_url(_local_svn_repo, repo) -> str:
        """

        :param _local_svn_repo:
        :param repo:
        :return:
        """
        if repo.trunk:
            return _local_svn_repo.removesuffix("/") + "/trunk"
        else:
            return _local_svn_repo

    def clone_latest_svn(self, retrieved_repo: SourceCodeRepository, remote_repo: Svn) -> Repo | None:
        latest = retrieved_repo.latest
        if latest is None:
            # Only processing repositories that have a latest version
            return None

        version = latest.version
        version_type = latest.version_type

        working_dir = self._prepare_working_dir()
        local_svn_dir = working_dir / "svn"
        local_git_dir = working_dir / "git"
        clone_url_project_full_path = retrieved_repo.clone_url.path.removeprefix("/p/")
        clone_url_project_path = "/".join(clone_url_project_full_path.split("/")[:2])
        local_svn_repo_url = self._determine_local_svn_repo_url(local_svn_dir, clone_url_project_full_path)

        # Prepare dumping remote repo
        rsync_cmd_str = f"rsync -ahPv svn.code.sf.net::p/{clone_url_project_path} {local_svn_dir}"  # noqa E231
        args = shlex.split(rsync_cmd_str)

        try:
            # Execute the command, capture stdout and stderr, and decode outputs to strings
            subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            self.log.error(
                f"Dumping remote SVN repository {clone_url_project_path} with rsync failed "
                f"with error code: {e.returncode}."
            )
            return None

        if version_type == VersionType.TAG:
            local_svn_tags_path = f"{local_svn_repo_url}/tags/{version}"
            try:
                self.log.debug("Cloning from %s to %s", local_svn_tags_path, local_git_dir)
                Git().svn("clone", local_svn_tags_path, local_git_dir)
            except GitCommandError as gce:
                self.log.error(
                    f"Failed to convert SVN repository to Git repository based "
                    f"on tag {version} from {remote_repo}.\n{gce}"
                )
                return None

        elif version_type == VersionType.REVISION:
            svn_url = self._determine_actual_svn_url(local_svn_repo_url, retrieved_repo)
            try:
                self.log.debug("Cloning from %s to %s", svn_url, local_git_dir)
                Git().svn("clone", "-r", version, svn_url, local_git_dir)
            except GitCommandError as gce:
                self.log.error(
                    f"Failed to convert SVN repository to Git repository based "
                    f"on revision {version} from {remote_repo}.\n{gce}"
                )
                return None

        local_git_repo = Repo(local_git_dir)
        try:
            log = local_git_repo.git.log()[-1]
            self.log.debug(f"Successfully retrieved last log message for local git repo: {log}.")
            return Repo(local_git_dir)
        except GitCommandError:
            self.log.error(
                f"Local git repository has no log: {local_git_dir}. This may be because the attempt to git-svn clone "
                f"an SVN repository at a specific revision failed as the revision doesn't exist at this URL."
            )
            return None

    def decode_json_from_string(self, result) -> Any | None:
        """TODO"""
        if result is not None and result.stdout != "" and result.stdout.strip().startswith("{"):
            try:
                return json.loads(result.stdout)
            except JSONDecodeError:
                self.log.error("Could not decode JSON string '%s'.", result.stdout)
                return None

    @staticmethod
    def parse_language_data(language_data: dict) -> list[Language]:
        languages = []
        for lang, vals in language_data.items():
            perc_str = vals["percentage"]
            fraction = float(perc_str) / 100
            languages.append(Language(language=lang, fraction=fraction))
        return languages

    def get_languages(self, retrieved_repo: SourceCodeRepository, clone_dir: Path) -> SourceCodeRepository:
        if retrieved_repo.accessible and retrieved_repo.latest is not None:
            try:
                # Execute the command, capture stdout and stderr, and decode outputs to strings
                cmd_str = f"github-linguist -j {clone_dir}"
                ghl_args = shlex.split(cmd_str)
                result = subprocess.run(
                    ghl_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False,
                    check=True,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                self.log.error(f"github-linguist failed with exit status {e.returncode}.")
                return retrieved_repo

            data = self.decode_json_from_string(result)
            if data is not None and len(data) > 0:
                retrieved_repo.latest.languages = self.parse_language_data(data)

        else:
            self.log.info(
                f"Repository {retrieved_repo.clone_url} is either not accessible "
                f"or no latest version could be determined."
            )

        return retrieved_repo

    @staticmethod
    def parse_license_data(data: dict, target_confidence: int = 50) -> list[LicenseData] | None:
        license_map = {}
        licenses = []
        matched_files = data["matched_files"]
        for mf in matched_files:
            v_license = mf["matched_license"]
            v_confidence = 0
            if "matcher" in mf and mf["matcher"] is not None:
                v_confidence = mf["matcher"]["confidence"]
            if v_license not in license_map or (v_license in license_map and license_map[v_license] < v_confidence):
                license_map[v_license] = v_confidence
        for licence, confidence in license_map.items():
            if licence != "NOASSERTION" and confidence >= target_confidence:
                licenses.append(LicenseData(license=licence, confidence=int(confidence)))
        return licenses if len(licenses) > 0 else None

    def get_licenses(self, latest_version: LatestVersion, clone_dir: Path) -> LatestVersion:
        try:
            # Execute the command, capture stdout and stderr, and decode outputs to strings
            cmd_str = f"licensee detect {clone_dir} --json"
            ghl_args = shlex.split(cmd_str)
            result = subprocess.run(
                ghl_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            # licensee exits with 1 if no license information was found,
            # see https://github.com/licensee/licensee/issues/576
            if e.returncode == 1:
                result = None
            else:
                self.log.error(f"licensee failed with exit status {e.returncode}.\n{e.stderr}")
                return latest_version

        data = self.decode_json_from_string(result)

        if data is not None and len(data) > 0:
            latest_version.licenses = self.parse_license_data(data)

        return latest_version

    def _prepare_working_dir(self) -> Path:
        """

        :return:
        """
        clone_suffix = uuid.uuid4().hex
        clone_path = Path(self.clone_dir) / clone_suffix
        clone_path.mkdir(parents=True)
        return clone_path.absolute()

    @staticmethod
    def _determine_local_svn_repo_url(local_svn_dir: Path, clone_url_project_path: str) -> str:
        """

        :param local_svn_dir:
        :param clone_url_project_path:
        :return:
        """
        svn_repo_dir = "/".join(clone_url_project_path.split("/")[1:])
        return f"file://{local_svn_dir}/{svn_repo_dir}"  # noqa E231

    @staticmethod
    def svn_info(remote: Svn, tries: int = 1) -> NamedTuple:
        if tries < 3:
            try:
                return remote.info()
            except SvnException:
                tries += 1
                CloneRetriever.svn_info(remote, tries)
        else:
            try:
                return remote.info()
            except SvnException:
                raise

    @staticmethod
    def svn_list(remote: Svn, tries: int = 1) -> Generator[str, None, None]:
        if tries < 3:
            try:
                return remote.list()
            except SvnException:
                tries += 1
                CloneRetriever.svn_list(remote, tries)
        else:
            try:
                return remote.list()
            except SvnException:
                raise

    @staticmethod
    def svn_log(remote: Svn, tries: int = 1, limit: int = None) -> Generator[Any, None, None]:
        if tries < 3:
            try:
                return remote.log(limit)
            except SvnException:
                tries += 1
                CloneRetriever.svn_log(remote, tries, limit)
        else:
            try:
                return remote.log(limit)
            except SvnException:
                raise

    @staticmethod
    def _get_commit_sha_for_tag(git, tag_name):
        output = git.show_ref("--dereference", "refs/tags/" + tag_name)
        for line in output.splitlines():
            if line.strip().endswith("^{}"):
                return line.split()[0].strip()

    def checkout_latest(self, retrieved_repo: SourceCodeRepository, remote_repo: Union[Repo | Svn]) -> Path | None:
        checkout_repo = None
        if retrieved_repo.vcs == VCS.git:
            checkout_repo = self.clone_latest_git(retrieved_repo, remote_repo)
        elif retrieved_repo.vcs == VCS.svn:
            checkout_repo = self.clone_latest_svn(retrieved_repo, remote_repo)
        if checkout_repo is not None:
            return Path(checkout_repo.working_tree_dir)
        else:
            return None

    def process_repo(self, software: ResearchSoftware, repo: SourceCodeRepository) -> SourceCodeRepository:
        retrieved_repo, remote_repo = self.retrieve_from_repo(software, repo)

        if retrieved_repo.latest is not None and remote_repo is not None:
            clone_dir = self.checkout_latest(retrieved_repo, remote_repo)

            if clone_dir is not None:
                self.get_languages(retrieved_repo, clone_dir)
                self.get_licenses(retrieved_repo.latest, clone_dir)
                self.get_metadata_files(retrieved_repo.latest, clone_dir)
                if self.storage_dir is not None:
                    self.store_clone(retrieved_repo, self.storage_dir, clone_dir)

        return repo

    def get_metadata_files(self, latest_version: LatestVersion, clone_dir: Path) -> LatestVersion:
        """
        Checks for the existence of metadata files in the root of the local
        repository in clone_dir and adds them to the metadata_files field
        of the latest_version.

        :param latest_version: The latest version of a repository to get metadata files for
        :param clone_dir: The directory where the local repo is located
        :return: The updated or unchanged latest version
        """
        files = [metadata_file for metadata_file in MetadataFile if (clone_dir / metadata_file.value).exists()]
        latest_version.metadata_files = files or None
        return latest_version

    def store_clone(self, retrieved_repo: SourceCodeRepository, storage_dir: str, clone_dir: Path) -> None:
        """
        Compresses the clone directory with lzma (xz) and compression level 9,
        and stores it in the given storage_dir.

        Returns None if the given clone_dir is larger than 5 GiB -
        following the recommendation in the GitHub docs:
        https://docs.github.com/en/repositories/working-with-files/managing-large-files/
        about-large-files-on-github#repository-size-limits -
        or on errors during the compression process.

        :param retrieved_repo: The repository with a latest version, for which to store the latest version cloned dir
        :param storage_dir: The directory to store the compressed clone directory in
        :param clone_dir: The clone directory to compress and store
        """
        if not clone_dir.exists():
            self.log.error(
                f"Failed to create lzma-compressed tarball for {retrieved_repo.clone_url} "
                f"as clone directory does not exist."
            )
            return None

        latest_version = retrieved_repo.latest

        if self.clone_dir_size(clone_dir) > 5368709120:
            self.log.warning(f"Repository {retrieved_repo.clone_url} is > 5 GiB, not storing.")
            latest_version.id = "<unassigned due to size limit>"
            return None

        storage_dir = Path(storage_dir)

        # Use hashlib to hash repo name, not used for security-relevant crypto
        m = hashlib.md5()  # nosec
        m.update(str(retrieved_repo.clone_url).encode("utf-8"))
        hsh = m.hexdigest()

        if latest_version.version is not None and latest_version.version != "":
            hsh = hsh + "." + latest_version.version
        else:
            hsh = hsh + "." + str(int(datetime.now().timestamp()))

        file_path = storage_dir / (hsh + ".tar.xz")
        self.log.info(f"Storing clone directory to {file_path}.")
        with tarfile.open(file_path, "w:xz", preset=9) as tar:
            try:
                tar.add(clone_dir, arcname=hsh)
            except FileNotFoundError as fnfe:
                self.log.error(
                    f"Failed to create lzma-compressed tarball for {retrieved_repo.clone_url} "
                    f"due to missing file '{fnfe.filename}'."
                )
                return None

        latest_version.id = hsh

    def clone_dir_size(self, clone_dir: Path | str) -> int:
        """Return total size of files in given path and subdirs."""
        total = 0
        for entry in os.scandir(clone_dir):
            if entry.is_dir(follow_symlinks=False):
                total += self.clone_dir_size(entry.path)
            else:
                total += entry.stat(follow_symlinks=False).st_size
        return total
