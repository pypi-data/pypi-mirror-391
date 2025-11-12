import json
import subprocess
import time
from subprocess import CalledProcessError
import re

import urllib3
from ratelimit import sleep_and_retry, limits
from urllib3.exceptions import HTTPError, RequestError

from opendors.abc import WorkflowRule
from opendors.model import VCS, Platform
from opendors.rules.urls import get_sourceforge_api_url


########################################################################################################################
############################## Class
########################################################################################################################


class VCSRetriever(WorkflowRule):
    """
    Identifies the applicable version control system to use with a specific repository URL and saves these data in an
    OpenDORS Corpus.
    """

    def __init__(
        self,
        input_json: str,
        output_json: str,
        sourceforge_user: str,
        sourceforge_token: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.output_json = output_json
        self.sourceforge_user = sourceforge_user
        self.sourceforge_token = sourceforge_token

    ##################################################
    ########## Methods
    ##################################################

    @sleep_and_retry
    @limits(calls=1, period=2)
    def _get_sourceforge_vcs_data(self, url: str) -> list[tuple[VCS, str]] | None:
        """
        Identifies the applicable version control repositories for a Sourceforge project.
        This is necessary, because Sourceforge projects can provide >=1 either Subversion or Git repositories.

        :param url: The URL for the Sourceforge project
        :return: A list of tuples of VCS Enum and clone URL, or None if neither git nor svn are in the project's tools
        """
        api_url = get_sourceforge_api_url(url)
        try:
            response = urllib3.request(
                "GET",
                api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.sourceforge_token}",
                },
            )
            if response.status == 200:
                repos = []
                response_data = response.data.decode("utf-8").strip()
                data = json.loads(response_data)
                if "tools" in data:
                    for tool in data["tools"]:
                        if tool["name"] == VCS.git.value:
                            clone_url = self._get_best_clone_url(tool)
                            repos.append((VCS.git, clone_url)) if clone_url else None
                        elif tool["name"] == VCS.svn.value:
                            clone_url = self._get_best_clone_url(tool)
                            repos.append((VCS.svn, clone_url)) if clone_url else None
                        elif tool["name"] == VCS.cvs.value:
                            clone_url = self._get_best_clone_url(tool)
                            repos.append((VCS.cvs, clone_url)) if clone_url else None
                    if len(repos) == 0:
                        self.log.info(
                            f"No VCS tool registered for {url}: {json.dumps(data['tools'])}."
                        )
                        return None
                else:
                    self.log.info(f"No tools registered for {url}.")
                    return None
                return repos
            elif response.status == 429:
                self.log.warning("Too many requests, waiting 60 secs. before retrying.")
                time.sleep(60)
                return self._get_sourceforge_vcs_data(url)
            elif response.status == 404:
                transformed_url = self._transform_url_on_404(url)
                if transformed_url is not None:
                    self.log.debug(f"Retrying with new URL {transformed_url}")
                    return self._get_sourceforge_vcs_data(transformed_url)
                else:
                    return None
            else:
                self.log.error(
                    f"Status {response.status}: Could not retrieve repository data for project {url}: {api_url}."
                )
                return None
        except (HTTPError, RequestError) as e:
            self.log.warning(
                f"Failed to retrieve repository data for project {url}. Retrying in 10 secs.",
                exc_info=e,
            )
            time.sleep(10)
            self._get_sourceforge_vcs_data(url)

    def _transform_url_on_404(self, url) -> str | None:
        """
        Handles 404 errors described in https://gitlab.dlr.de/drus_st/opendorslib/-/issues/76:

        Known issues that could have caused a 404:

        - Project names including period characters ('.') cannot be requested, as the allowed regex for project names
        for API access is '[a-zA-Z0-9-]+' (cf. https://sourceforge.net/api-docs/#operation/GET_neighborhood-project)
        - Project names including uppercase characters must be transformed to lowercase, as the API is case-sensitive
        - Hyphenation in some project names is an artifact of PDF parsing and the correct URL path contains no hyphen,
        and therefore, a retry with hyphens removed is viable
        - Some project pages forward via 301, where the target project name may be resolvable via the API, but must
        be retrieved

        :param url: The URL of the Sourceforge project
        :return: A transformed URL to try again with, or None
        """
        url_split = url.split("/")
        url_stem = "/".join(url_split[0:-1])
        project_name = url_split[-1]
        has_upper = any(char.isupper() for char in project_name)
        has_hyphen = "-" in project_name
        has_period = "." in project_name
        if has_period:
            # URLs for project names with periods are illegal for the REST API
            self.log.debug("Project name contains period, returning None.")
            return None
        elif has_upper:
            self.log.debug(f"Transforming {url} to lowercase.")
            return url_stem + "/" + project_name.lower()
        elif has_hyphen:
            self.log.debug(f"Removing hyphens from {url}.")
            return url_stem + "/" + project_name.replace("-", "")
        else:
            target_url = self._has_project_url_forward(url)
            if target_url is not None:
                if target_url.startswith("https://sourceforge.net/directory/"):
                    return None
                return target_url
            else:
                return None

    ##########
    ### Main method
    ##########

    def run(self) -> None:
        """
        Runs the workflow rule.

        :return: None
        """
        corpus = self.read_corpus(self.input_json)
        total_software = len(corpus.research_software)
        for i_rs_in, rs_in in enumerate(corpus.research_software):
            self.log.debug(
                f"Determining VCS systems for {rs_in.canonical_url} ({i_rs_in + 1}/{total_software})"
            )
            if not rs_in.repositories:
                if rs_in.platform == Platform.SOURCEFORGE_NET:
                    lst_sf_vcs_data = self._get_sourceforge_vcs_data(
                        str(rs_in.canonical_url)
                    )
                    if lst_sf_vcs_data is not None:
                        for vcs, clone_url in lst_sf_vcs_data:
                            rs_in.add_repository(vcs=vcs, url=clone_url)
                            self.log.info(
                                f"Added {vcs} repository to software at {rs_in.canonical_url}."
                            )
                    time.sleep(0.5)  # Avoid too many requests response
                else:
                    # Safeguarding that the canonical git repo URL is set,
                    # even if setting it was forgotten beforehand.
                    rs_in.add_repository(VCS.git, str(rs_in.canonical_url) + ".git")
                    self.log.info(
                        f"Added git repository to software at {rs_in.canonical_url}."
                    )
        self.write_corpus(corpus, self.output_json)

    def _get_best_clone_url(self, tool: dict) -> str | None:
        """
        Attempts to get the "best" clone URL for this tool, going through a ranked list of keys
        that may be available in the tool dict, and returning the value of the first key that exists.
        :param tool: The tool dictionary returned by the SourceForge API
        :return: The optimal clone URL for the tool, stripped off any user information, or None
        """
        if "clone_url_https_anon" in tool:
            url_ = tool["clone_url_https_anon"]
        elif "clone_url_https" in tool:
            url_ = tool["clone_url_https"]
        elif tool["name"] == VCS.cvs.value and "url" in tool:
            url_ = tool["url"]
        else:
            self.log.warning(f"Could not determine best clone URL for tool: {tool}.")
            return None
        return url_.replace(f"{self.sourceforge_user}@", "")

    def _has_project_url_forward(self, url: str) -> str | None:
        """
        If a project URL has a 301 forward and returns the target URL, else returns None.

        :param url: The URL to check
        :return: The target URL, or None
        """
        response = urllib3.request("GET", url, redirect=False)
        if response.status == 301:
            target = response.headers.get("Location")
            self.log.debug(f"{url} forwards to {target}.")
            target = target.removesuffix("/")
            if target == url:
                return None
            return target
        return None


def git_ls_remote_head(clone_url_str: str) -> str:
    """
    Retrieve the commit hash for HEAD from a remote git repository.

    :param clone_url_str: The clone URL string to retrieve the HEAD hash for
    :return: The HEAD hash for the given git repository
    """
    try:
        stdout = subprocess.check_output(["git", "ls-remote", clone_url_str, "HEAD"])
        return re.split(r"\s+", stdout.decode("utf-8"), maxsplit=1)[0]
    except CalledProcessError:
        raise RuntimeError(
            f"Could not run 'git ls-remote' to retrieve the HEAD for repository {clone_url_str}."
        )
