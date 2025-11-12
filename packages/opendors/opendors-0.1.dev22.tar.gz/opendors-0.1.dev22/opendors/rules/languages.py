from pathlib import Path
import time

import urllib3
from pydantic import AnyHttpUrl
from ratelimit import sleep_and_retry, limits

from opendors.abc import WorkflowRule
from opendors.model import (
    Language,
    SourceCodeRepository,
    ResearchSoftware,
    VCS,
    Corpus,
    Platform,
    ProjectRepository,
)


# ######################################################################################################################
# ############################ GitHub API Retriever
# ######################################################################################################################


class GitHubAPILanguageRetriever(WorkflowRule):
    """
    Retrieves languages for repositories from the GitHub API.

    Relevant rate limits are as follows.

    - Primary rate limits for authenticated calls: 5,000 / hour
    - Secondary rate limit for single API endpoints (here: repo/languages): 900 / minute

    Therefore, ony one chunk of 5,000 research software projects are processed per hour,
    and only 900 calls to the repo/languages endpoint are made per minute. This is controlled
    via package ratelimit's annotations on the relevant methods.

    !!! Note:
        Working with live API data requires a GitHUb API token which must be set as
        environment variable 'GITHUB_TOKEN'.

    TODO: Optionally, wait until x-ratelimit-reset UTC epoch seconds if x-ratelimit-limit is 0
    """

    GITHUB_REST_API_VERSION = "2022-11-28"

    def __init__(
        self,
        input_json: str,
        output_json: str,
        github_token: str,
        github_user_agent: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.output_json = output_json
        self.github_token = github_token
        self.github_user_agent = github_user_agent
        self.repo_languages_lut = {}
        self.repo_status_lut = {}

    # ################################################
    # ######## Main method
    # ################################################

    def run(self) -> None:
        """
        Runs the workflow rule.
        """
        c = self.read_corpus(self.input_json)
        self._languages_for_software_list(c.research_software)

        self.write_corpus(c, self.output_json)

    # ################################################
    # ######## Methods
    # ################################################

    def _languages_for_software_list(
        self, software_list: list[ResearchSoftware]
    ) -> None:
        """
        Retrieves and adds language data for repositories in a given list of research software projects.

        :param software_list: A list of ResearchSoftware of fixed size, which is determined by the max number of API
        calls per hour.
        """
        total_software = len(software_list)
        ratelimit_remaining = self._get_remaining_ratelimit()
        ratelimit_reset = -1
        for i_software, software in enumerate(software_list):
            self.log.debug(
                f"Getting languages for repositories for software {i_software + 1}/{total_software}."
            )
            for repo in software.repositories:
                if ratelimit_remaining <= 1:
                    self.wait_until(ratelimit_reset)
                languages = None
                clone_url = repo.clone_url
                if repo.clone_url not in self.repo_languages_lut:
                    # Only get for yet unknown repositories
                    (
                        status,
                        retrieved_languages,
                        ratelimit_remaining,
                        ratelimit_reset,
                    ) = self._retrieve_languages_for_repo(repo)
                    if status == 200:
                        # Try to retrieve the HEAD commit hash
                        # try:
                        #     repo.head = git_ls_remote_head(str(repo.clone_url))
                        # except RuntimeError as re:
                        #     self.log.error(re)
                        # Build languages list
                        languages = []
                        for retrieved_language, fraction in retrieved_languages.items():
                            languages.append(
                                Language(language=retrieved_language, fraction=fraction)
                            )
                    self.repo_languages_lut[clone_url] = languages
                    self.repo_status_lut[clone_url] = status
                else:
                    languages = self.repo_languages_lut[clone_url]
                    status = self.repo_status_lut[clone_url]
                repo.accessible = status == 200
                # repo.head_langs = languages

    @sleep_and_retry
    @limits(calls=5000, period=3600)
    @sleep_and_retry
    @limits(calls=900, period=60)
    def _retrieve_languages_for_repo(
        self, repo: SourceCodeRepository
    ) -> tuple[int, dict[str, float], int, int]:
        """
        Retrieves languages for a GitHub repository via the GitHub API.

        !!! Note:
            Due to secondary rate limits, this method can only be called 900 times per minute
            up to a maximum of 5000 calls per hour.

        :param repo: the SourceCodeRepository to retrieve the languages information for
        :return: a dict with language names as keys and floats as values
        """
        if repo.vcs == VCS.git:
            user, repository = self._get_user_repo_from_github_url(repo.clone_url)
            response = urllib3.request(
                "GET",
                f"https://api.github.com/repos/{user}/{repository}/languages",
                headers={
                    "Accept": " application/vnd.github+json",
                    "Authorization": f"Bearer {self.github_token}",
                    "X-GitHub-Api-Version": self.GITHUB_REST_API_VERSION,
                    "User-Agent": self.github_user_agent,
                },
            )
            status = response.status
            self.log.debug(
                f"{status} status for GitHub API call against {user}/{repository}. Response: {response.json()}."
            )
            data = (
                self._fractions_for_languages(response.json())
                if status == 200
                else None
            )
            ratelimit_remaining = int(response.headers.get("X-RateLimit-Remaining"))
            ratelimit_reset = int(response.headers.get("X-RateLimit-Reset"))
            return status == 200, data, ratelimit_remaining, ratelimit_reset
        else:
            raise ValueError(f"Source code repository is not a git repository: {repo}.")

    def _get_remaining_ratelimit(self):
        ratelimit_response = urllib3.request(
            "GET",
            "https://api.github.com/rate_limit",
            headers={
                "Accept": " application/vnd.github+json",
                "Authorization": f"Bearer {self.github_token}",
                "X-GitHub-Api-Version": self.GITHUB_REST_API_VERSION,
                "User-Agent": self.github_user_agent,
            },
        )
        if ratelimit_response.status == 200:
            data = ratelimit_response.json()
            return data["resources"]["core"]["remaining"]
        else:
            self.log.warning(
                f"Cannot get remaining ratelimit for GitHub API: status {ratelimit_response.status} - "
                f"{ratelimit_response.json()}"
            )
            time.sleep(1)
            return self._get_remaining_ratelimit()

    # ################################################
    # ######## Static methods
    # ################################################

    @staticmethod
    def _fractions_for_languages(language_bytes: dict[str, int]) -> dict[str, float]:
        total = sum(language_bytes.values())
        return {
            k: float("{:.3f}".format(float(v / total)))
            for k, v in language_bytes.items()
        }

    @staticmethod
    def _get_user_repo_from_github_url(url: AnyHttpUrl) -> tuple[str, str]:
        """
        Gets the username and repository name from a canonical GitHub URL.

        :param url: A canonical GitHub repository URL
        :return: A tuple of the username string and the repository name string
        """
        url_parts = str(url).split("/")
        return url_parts[-2], url_parts[-1].removesuffix(".git")

    @staticmethod
    def _languages_from_github_api_data(data: dict) -> dict:
        """
        Parses the data from a call to the GitHub API repo/languages endpoint into a map from language names to 3-digit
        fractional floats of the fraction of bytes of code in that language in the repository.

        :param data: Data from a response requested from the GitHub REST API v2022-11-28 endpoint repo/languages
        :return: A dict[str, float] of programming language names to 3-digit fractional floats
        """
        languages = {}
        total = sum([b_code for b_code in data.values()])
        for language, b_codes in data.items():
            languages[language] = float("{:.3f}".format(b_codes / total))
        return languages


# ######################################################################################################################
# ############################ Corpus VCS Splitter
# ######################################################################################################################


class CorpusVCSSplitter(WorkflowRule):
    def __init__(
        self,
        input_json: str,
        output_dir: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.output_dir = output_dir

    # ################################################
    # ######## Main method
    # ################################################

    def run(self) -> None:
        output_path = Path(self.output_dir)
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        with open(self.input_json, "r") as ci:
            c = Corpus.model_validate_json(ci.read())
            total_software = len(c.research_software)
            for i_software, software in enumerate(c.research_software):
                self.log.debug(
                    f"Splitting repositories for software {i_software + 1}/{total_software}."
                )
                project_url = software.canonical_url
                for repo in software.repositories:
                    if software.platform == Platform.SOURCEFORGE_NET:
                        file_name = self._get_file_name(
                            repo.vcs.value, "sourceforge", repo.clone_url
                        )
                    else:
                        file_name = self._get_file_name(
                            repo.vcs.value, software.platform.value, project_url
                        )
                    with open(
                        output_path / file_name,
                        "w",
                    ) as fo:
                        fo.write(
                            ProjectRepository(
                                project_url=project_url, repository=repo
                            ).model_dump_json()
                        )

    # ################################################
    # ######## Static methods
    # ################################################

    @staticmethod
    def _get_file_name(vcs: str, platform: str, url: AnyHttpUrl) -> str:
        """
        TODO Mention double ~ explicitly!

        :param vcs:
        :param platform:
        :param url:
        :return:
        """
        platform = platform.split(".")[0]
        url_parts = str(url).split("/")
        return f"{vcs}~~{platform}~~{url_parts[-2]}~~{url_parts[-1]}.json"


class LinguistRetriever(WorkflowRule):
    def __init__(
        self,
        input_json: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.repo_languages_lut = {}
        self.repo_status_lut = {}

    def run(self) -> None:
        raise NotImplementedError("Currently unimplemented.")
