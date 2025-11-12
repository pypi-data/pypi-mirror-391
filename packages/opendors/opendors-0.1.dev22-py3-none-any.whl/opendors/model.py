from collections import namedtuple
from datetime import datetime
from enum import Enum
from typing import Optional, Any, List, Literal, Annotated

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    field_validator,
    field_serializer,
    ConfigDict,
    Field,
)
from pydantic.dataclasses import dataclass


# ######################################################################################################################
# ############################ Enums
# ######################################################################################################################


class IdType(str, Enum):
    """Enum defining the type of identifier for a mentioning resource."""

    ARXIV = "arxiv"
    PMC = "pmc"
    DOI = "doi"


class MetadataSource(str, Enum):
    """Enum defining the data source for the data."""

    EXTRACT_URLS_PMC = "extract-urls-pmc"
    EXTRACT_URLS_ARXIV = "extract-urls-arxiv"
    JOSS = "joss"


class VCS(str, Enum):
    """Enum defining version control systems."""

    git = "git"
    svn = "svn"
    cvs = "cvs"


class Platform(str, Enum):
    """Enum defining source code repository platforms."""

    GITHUB_COM = "github.com"
    GITLAB_COM = "gitlab.com"
    BITBUCKET_ORG = "bitbucket.org"
    SOURCEFORGE_NET = "sourceforge.net"


class DeterminationSource(str, Enum):
    """Enum defining sources for determining the version of a software."""

    URL = "url"
    """Version was extracted from a mentioned VCS URL"""
    PUB_DATE = "publication-date"
    """Version was determined based on the last version before a given publication date of a mentioning work"""
    ARCHIVE_METADATA = "archive-metadata"
    """Version was determined from the metadata provided by an archive deposit of the version, e.g., on Zenodo"""
    RELATED_IDENTIFIER_URL = "related-identifier-url"
    """Version was determined parsing a URL supplied as related identifier in the software archive metadata"""


class VersionType(str, Enum):
    # Version is based on a URL for a tagged version in a source code repository.
    #
    # In git, tags are first class citizens, and can be checked out using '--branch'.
    # For git systems, therefore, the value of ver_tag is the tag.
    #
    # In Subversion, tags are basically directories in the tree (often called 'tags/').
    # Therefore, for svn systems, the value of ver_tag is the tag directory in the repository.
    #
    # Release URL pattern for gitlab.com: https://gitlab.com/user/repo/-/releases/<tag>
    # Release URL pattern for github.com: https://github.com/user/repo/releases/tag/<tag>
    TAG = "tag"
    # Version is based on a URL for a specific commit or revision.
    # In git, getting the commit is by cloning and resetting --hard.
    # In svn, getting the revision is by checkout -r <revision> <url>
    REVISION = "revision"
    # Version is based on a URL containing the name of a branch-like reference (e.g., tree/my-branch or tree/my-tag)
    # (i.e., a branch or a tag, of which either can be retrieved using the same command, e.g., `git checkout --branch`)
    #
    # In git, branches are first class citizens, and can be checked out using '--branch'.
    # For git systems, therefore, the value of ver_branch is the branch name.
    #
    # In Subversion, branches are basically directories in the tree (often called 'branches/').
    # Therefore, for svn systems, the value of ver_branch is the branch directory in the repository.
    BRANCH = "branch"
    # Temporary type for URL paths that may contain branches, tags or commits, but for which it is impossible to
    # determine the correct version type.
    # Will eventually be replaced with at least a revision based on publication date.
    PATH = "path"
    # Version is based on a named version in, e.g., a software archive that may not correspond to, e.g., a tag
    NAME = "name"

    def is_better_than(self, other):
        lst = [
            VersionType.TAG,  # Best version type
            VersionType.REVISION,  # Well-defined
            VersionType.BRANCH,  # Can at least yield revision or tag
            VersionType.PATH,  # Can be checked whether it includes a tag or a revision
            VersionType.NAME,  # May be unrelated to VCS history
            None,
        ]
        return lst.index(self) < lst.index(other)


class MetadataFile(str, Enum):
    """Enum defining software metadata files."""

    CFF = "CITATION.cff"
    CODEMETA = "codemeta.json"
    ZENODO = ".zenodo.json"


# ######################################################################################################################
# ############################ Plain classes
# ######################################################################################################################


class SvnStructure(namedtuple("Structure", ["url", "trunk", "branches", "tags", "compliance", "sub_dirs"])):
    def __hash__(self):
        return hash(self.url)


# ######################################################################################################################
# ############################ Base dataclass
# ######################################################################################################################


class NoExtraFieldsModel(BaseModel):
    """
    BaseModel subclass that disallows extra fields on model instances.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, use_attribute_docstrings=True)


# ######################################################################################################################
# ############################ Dataclasses
# ######################################################################################################################


class Language(NoExtraFieldsModel):
    """
    Represents a repository's programming language and the percentage of bytes of code for relevant files
    in the repository, as determined by the github-linguist Ruby package.

    See for more information:
    https://github.com/github-linguist/linguist/blob/559a6426942abcae16b6d6b328147476432bf6cb/docs/how-linguist-works.md
    """

    language: str
    fraction: float


class MentionId(NoExtraFieldsModel):
    id: str
    id_type: IdType


class MentionedVersion(NoExtraFieldsModel):
    """Represents a specific software source code state (here: version) mentioned in a work"""

    identification_url: Optional[AnyHttpUrl] = None
    """The URL that was used to identify the mentioned software version with maximal precision"""

    type: Optional[VersionType] = None
    """The type of the version, e.g., whether it refers to a tagged version, a specific revision, a branch head, ..."""

    based_on: Optional[DeterminationSource] = None
    """The source of the information from which the version of the mentioned software was determined"""

    version: Optional[str] = None
    """The actual expression of the version reference, i.e., the tag or revision identifier."""

    reference: Optional[str] = None
    """The reference to the version, i.e., the version name, tag name, revision name, branch name or path."""

    date: Optional[datetime] = None
    """The date of the version, i.e., committed date of the revision, or committed date of the tag."""

    archive_url: Optional[AnyHttpUrl] = None
    """A URL to an archive deposit of the determined version"""

    def is_better_than(self, other) -> bool:
        if self.type is None:
            return False
        elif other.type is None:
            return True
        else:
            return self.type.is_better_than(other.type)

    @field_validator("identification_url", "archive_url", mode="before")
    def wrap_url(cls, v):  # noqa: N805
        return _wrap_url(v)


DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
LAX_DATE_PATTERN = r"^\d{4}(?:-\d{2}(?:-\d{2})?)?$"
LAX_SHA1_OR_INTS_PATTERN = r"^([0-9a-f]{5,40}|\d+)$"
SWH_ID_PATTERN = r"^swh:[1-9]:(rel|rev):[0-9a-f]+(;(origin|visit|anchor|path|lines)=\S+)*$"
SWH_DIR_PATTERN = r"^swh:[1-9]:dir:[0-9a-f]+(;(origin|visit|anchor|path|lines)=\S+)*$"


class Mention(NoExtraFieldsModel):
    """Represents a mention of a research software within a work"""

    metadata_source: MetadataSource
    """The source of the mention metadata"""

    id: str
    """The mention identifier from the metadata source"""

    id_type: IdType
    """The type of the mention identifier, e.g., PMC identifier, ArXiv identifier, DOI, ..."""

    pub_date: Optional[str] = Field(pattern=LAX_DATE_PATTERN, default=None, title="Publication date")
    """The maximally precise date of the earliest publication of the mentioning work in the format YYYY[-MM[-DD]]"""

    version: Optional[MentionedVersion] = None
    """The version of the software mentioned in the mentioning work (may be approximate)"""

    mentioning_urls: set[str]
    """The URLs used to mention the software in the mentioning work"""


class LicenseData(NoExtraFieldsModel):
    """
    Represents information about detected licenses for a latest version.
    For each object, two required fields are completed:

    - license: provides the SPDX-2.0 identifier for the license
    - confidence: provides the confidence (in % (integers)) that the license has been detected correctly.
    """

    license: str
    confidence: int


class LatestVersion(NoExtraFieldsModel):
    """
    Represents information about the latest available version of the software in a source code repository
    at dataset construction.

    Note that this type does not distinguish between version and reference (e.g., commit sha and tag name for git).
    What is being recorded is the reference, i.e., either the tag name, or a revision identifier.
    """

    version: str
    """The commit sha or the tag name of the git ref to the latest version of a software in a source code repository"""

    version_type: Literal[VersionType.TAG, VersionType.REVISION]
    """The type of the latest version (only tag or revision)"""

    revision_id: Optional[Annotated[str, Field(pattern=LAX_SHA1_OR_INTS_PATTERN)]] = None
    """The commit sha (for git) or revision number (for svn) of the latest version tag or commit/revision."""

    tag_sha: Optional[Annotated[str, Field(pattern=LAX_SHA1_OR_INTS_PATTERN)]] = None
    """The tag sha of the latest version tag if the latest version is of a git repository and the tag is annotated."""

    languages: Optional[list[Language]] = None
    """A list of programming languages and their fractions as retrievable from the latest version"""

    date: Optional[datetime] = None
    """The date of the version, i.e., committed date of the revision, or committed date of the tag."""

    swh_id: Optional[Annotated[str, Field(pattern=SWH_ID_PATTERN)]] = None
    """The Software Heritage identifier of an archive of, or containing, the latest version."""

    swh_dir_id: Optional[Annotated[str, Field(pattern=SWH_DIR_PATTERN)]] = None
    """The Software Heritage 'dir' identifier of an archive of, or containing, the latest version."""

    licenses: Optional[list[LicenseData]] = None
    """List of detected licenses with confidences.
    Default None, and None when no licenses could be detected."""

    metadata_files: Optional[list[MetadataFile]] = None
    """List of detected metadata files.
    Default None, and None when no files could be detected."""

    id: Optional[str] = None
    """A string uniquely identifying the latest version.
    Identifies artifacts in the dataset."""


class SourceCodeRepository(NoExtraFieldsModel):
    """Represents a git or Subversion source code repository."""

    vcs: VCS
    """The version control system used by the repository"""

    clone_url: Optional[AnyHttpUrl] = None
    """The URL that can be used to retrieve a local copy of the repository via a VCS tool"""

    accessible: Optional[bool] = False
    """Whether the repository could be successfully accessed during dataset compilation, where 'accessible'
    describes a successful clone or checkout operation."""

    latest: Optional[LatestVersion] = None
    """Information about the latest version available from the repository at dataset construction"""

    main_repo: Optional[bool] = False
    """Whether this repository is regarded as containing 'the software'. This is relevant because Sourceforge
    projects that may be mentioned as 'the software' may contain more than one source code repository."""

    trunk: Optional[bool] = False
    """For SVN repositories, whether the repository has a trunk/ directory."""

    # ########
    # # "Private" fields, not represented, excluded from serialization
    # ########

    structure: Optional[SvnStructure] = Field(exclude=True, repr=False, default=None)

    @field_validator("clone_url", mode="before")
    def wrap_url(cls, v):  # noqa: N805
        return _wrap_url(v)

    def __hash__(self):
        return hash(self.clone_url)

    def __eq__(self, other):
        if isinstance(other, SourceCodeRepository):
            return (
                self.clone_url == other.clone_url
                and self.main_repo == other.main_repo
                and self.accessible == other.accessible
                and self.vcs == other.vcs
            )
        return False


class ProjectRepository(NoExtraFieldsModel):
    """Represents a single SourceCcodeRepository linked to a single ResearchSoftware."""

    project_url: AnyHttpUrl
    repository: SourceCodeRepository


class ResearchSoftware(NoExtraFieldsModel):
    """Represents a research software project."""

    canonical_url: AnyHttpUrl
    """A canonical URL for the software project on a version control platform"""

    mentions: list[Mention]
    """A list of mentions from the literature to this software"""

    repositories: Optional[List[SourceCodeRepository]] = Field(default=[])
    """A list of the source code repositories for the software project"""

    platform: Platform
    """The source code repository platform where the software project is hosted"""

    def add_repository(self, vcs: VCS, url: str):
        self.repositories.append(SourceCodeRepository(vcs=VCS[vcs], clone_url=AnyHttpUrl(url)))

    @field_validator("canonical_url", mode="before")
    def wrap_url(cls, v):  # noqa: N805
        return _wrap_url(v)

    @field_serializer("canonical_url", return_type=str)
    def ser_url(self, value) -> str:
        return _serialize_url(value)


class RepoValidatedResearchSoftware(ResearchSoftware):
    """
    Represents a ResearchSoftware object with an automatically added single SourceCodeRepository instance to
    the software's repositories field, if the software is not hosted on Sourceforge.
    """

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @field_validator("platform", mode="after")
    def auto_add_git_repos(cls, platform: Platform, info) -> Platform:  # noqa: N805
        """
        Runs on setting of the platform field, and computes a value for the repositories field based on the platform.

        :param platform: the given Platform
        :param info: the ValidationInfo
        :return: the given Platform
        """
        if platform and platform != Platform.SOURCEFORGE_NET:
            if "canonical_url" in info.data:
                info.data["repositories"] = [
                    SourceCodeRepository(vcs=VCS.git, clone_url=str(info.data["canonical_url"]) + ".git")
                ]
        return platform


@dataclass
class _AdditionResult:
    merged_software: bool = Field(default=False)
    added_mention: bool = Field(default=False)
    replaced_mention_version: bool = Field(default=False)
    added_mention_version: bool = Field(default=False)
    added_repo: bool = Field(default=False)


class Corpus(NoExtraFieldsModel):
    """Represents a corpus of research software repositories."""

    research_software: list[ResearchSoftware] = []
    """The software included in the corpus."""
    version: Optional[Annotated[str, Field(pattern=DATE_PATTERN)]] = None
    """The version of the corpus (format: YYYY-MM-DD)."""
    date: Optional[datetime] = None
    """The date of the version."""

    def timestamp(self):
        """Timestamps a Corpus object."""
        now = datetime.now()
        self.version = now.strftime("%Y-%m-%d")
        self.date = now

    # "Private" field, not part of the model
    _software_lut = {}

    def add_software(self, new_software: ResearchSoftware) -> _AdditionResult:
        """
        Adds a repository to a corpus safely, in that it checks

        - that if a repository with the URL already exists,
        the existing repository is used, and
        - that all mention IDs in the new repository are
        added to the existing repository only if they don't exist yet.

        Note that platform information is NOT overwritten, as it can be assumed
        that no canonical URL (which is checked for equality) can be pointing
        to more than one platform. Hence, the first incoming Platform is
        preserved.

        :param new_software: The repository to add
        """
        results = _AdditionResult()
        software_url = new_software.canonical_url
        if software_url in self._software_lut:
            results.merged_software = True
            existing_software = self._software_lut[software_url]
            ex_mention_lut = {ex_mention.id: ex_mention for ex_mention in existing_software.mentions}
            for mention in new_software.mentions:
                if mention.id not in ex_mention_lut:
                    existing_software.mentions.append(mention)
                    results.added_mention = True
                else:
                    ex_mention = ex_mention_lut[mention.id]
                    ex_mention.mentioning_urls.update(mention.mentioning_urls)
                    # Use the best available version
                    if mention.version is not None:
                        ex_version = ex_mention.version
                        if ex_version is None:
                            ex_mention.version = mention.version
                            results.added_mention_version = True
                        elif mention.version.is_better_than(ex_version):
                            ex_mention.version = mention.version
                            results.replaced_mention_version = True
            for repo in new_software.repositories:
                if repo not in existing_software.repositories:
                    existing_software.repositories.append(repo)
                    results.added_repo = True
        else:
            self._software_lut[software_url] = new_software
            self.research_software.append(new_software)
        return results


# ################################################
# ######## Functions
# ################################################


def _wrap_url(v: Any) -> AnyHttpUrl:
    """
    Wraps a string value into an instance of :class:AnyUrl.

    :param v: A value
    :return: An instance of :class:AnyUrl wrapping the value if it is a string
    """
    if isinstance(v, str) and v != "None":
        return AnyHttpUrl(v)
    else:
        return v


def _serialize_url(value: AnyHttpUrl | str) -> str:
    """
    Prepares a field serialization of an instance of AnyHttpUrl as a string.

    :return: The URL string
    """
    return str(value)
