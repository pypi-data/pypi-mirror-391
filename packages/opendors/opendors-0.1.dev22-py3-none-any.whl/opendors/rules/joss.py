import time

from pydantic import AnyHttpUrl, ValidationError
from ratelimit import limits, sleep_and_retry

from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout
from urllib3 import Retry

from opendors.abc import WorkflowRule
from opendors.rules.urls import (
    canonical_project_data,
    get_version_from_repository_urls,
    get_typed_version_from_git_url,
)
from opendors.model import (
    Corpus,
    Mention,
    MetadataSource,
    IdType,
    Platform,
    RepoValidatedResearchSoftware,
    ResearchSoftware,
    MentionedVersion,
    VersionType,
    DeterminationSource,
)

URL_PAPER_BASE = "https://joss.theoj.org/papers/"
"""Base URL path for JOSS papers."""

URL_PUBLISHED_PAPERS = f"{URL_PAPER_BASE}published"
"""Base URL path for published JOSS papers."""

ZENODO_API_BASE_URL = "https://zenodo.org/api/records/"

########################################################################################################################
############################## Class
########################################################################################################################


class JossRetriever(WorkflowRule):
    def __init__(
        self,
        platform_file: dict[str, str],
        zenodo_token: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.platform_file = platform_file
        self.zenodo_token = zenodo_token
        self.session = JossRetriever._create_session()

    ##################################################
    ########## Methods
    ##################################################

    ##########
    ### Main method
    ##########
    def run(self) -> None:
        """
        Retrieves all published papers from the JOSS website at https://joss.theoj.org/papers/published,
        and saves them as OpenDORS metadata JSON.
        """
        platform_corpus = {
            Platform.GITHUB_COM: Corpus(),
            Platform.GITLAB_COM: Corpus(),
            Platform.BITBUCKET_ORG: Corpus(),
            Platform.SOURCEFORGE_NET: Corpus(),
        }
        page = 1
        self.log.info("Getting JOSS papers metadata via https.")
        while True:
            self.log.info("Getting JOSS papers from page %i.", page)
            response = self._get_page(page)
            if response.status_code == 200:
                data = response.json()
                if data:
                    for paper in data:
                        if software := self._get_software_for_paper(paper["doi"]):
                            platform_corpus[software.platform].add_software(software)
                else:
                    self.log.info("No more data found. Finishing retrieval.")
                    break
            else:
                self.log.error(
                    f"Unexpected response status: {response.status_code}. Aborting retrieval and writing metadata."
                )
                break
            page += 1

        for platform, corpus in platform_corpus.items():
            out_file = self.platform_file[platform]
            self.write_corpus(corpus, out_file)

    @sleep_and_retry
    @limits(calls=1, period=1)
    def _get_page(self, page: int, retries: int = 1) -> requests.Response:
        """
        Retrieves the response for a page of published paper from JOSS via HTTP.

        :param page: The page number to retrieve the data for
        :return: A requests response containing the data for the page
        """
        try:
            response = self.get_request(f"{URL_PUBLISHED_PAPERS}.json?page={page}")
        except (ConnectionError, Timeout) as e:
            self.log.error("Error getting response for JOSS page %i. Aborting.", page)
            raise e
        return response

    @sleep_and_retry
    @limits(calls=1, period=1)
    def _get_software_for_paper(self, doi: str, retries: int = 1) -> ResearchSoftware | None:
        """
        Retrieves the HTTP response for a specific JOSS paper - identified by DOI - and
        transforms its data to an OpenDORS Repository datatype.

        :param doi: The DOI identifying the paper to retrieve
        :return: A Repository datatype containing the metadata for the retrieved paper
        """
        self.log.debug("Retrieving metadata for paper with DOI %s.", doi)
        try:
            response = self.get_request(f"{URL_PAPER_BASE}{doi}.json")
        except (ConnectionError, Timeout) as e:
            self.log.error(f"Error retrieving JOSS paper from {URL_PAPER_BASE}{doi}.json. Aborting.")
            raise e

        paper_data = response.json()
        orig_repo = paper_data["software_repository"]
        if canon_project_data := canonical_project_data(orig_repo):
            doi = paper_data["doi"]
            pub_date = JossRetriever._extract_publication_dates(paper_data)
            archive_url = paper_data["software_archive"]
            try:
                AnyHttpUrl(archive_url)
            except ValidationError:
                self.log.error(
                    f"The 'software_archive' value for JOSS paper {doi} is not a valid URL: {archive_url}. Ignoring."
                )
                archive_url = None
            software = RepoValidatedResearchSoftware(
                canonical_url=canon_project_data.canonical_url,
                mentions=[
                    Mention(
                        metadata_source=MetadataSource.JOSS,
                        id=doi,
                        id_type=IdType.DOI,
                        mentioning_urls={orig_repo},
                        pub_date=pub_date,
                        version=MentionedVersion(
                            archive_url=archive_url,
                        ),
                    )
                ],
                platform=canon_project_data.platform,
            )
            mention = software.mentions[0]
            if archive_url is not None and "10.5281" in str(archive_url):
                # Check if there is version metadata for this mention on Zenodo
                self.log.debug(f"Getting Zenodo metadata for software archive {archive_url}.")
                (
                    git_platform_version_url,
                    zenodo_version,
                ) = self._retrieve_zenodo_metadata(archive_url)
                mention.version = JossRetriever.set_version_from_zenodo_metadata(
                    mention.version, git_platform_version_url, zenodo_version
                )

            # Try and get a version out of the existing orig_repo URL
            url_version = get_version_from_repository_urls(
                software.platform,
                mention.version,
                software.repositories,
                mention.mentioning_urls,
            )
            if url_version.is_better_than(mention.version):
                mention.version = url_version

            return software
        else:
            self.log.info("Could not get a canonical URL for %s", orig_repo)

    @sleep_and_retry
    @limits(calls=5000, period=3600)
    @sleep_and_retry
    @limits(calls=100, period=60)
    def _retrieve_zenodo_metadata(self, archive_url: str) -> tuple[str, str] | tuple[None, None]:
        record = archive_url.split(".")[-1]
        try:
            r = self.get_request(f"{ZENODO_API_BASE_URL}{record}?access_token={self.zenodo_token}")
        except (ConnectionError, Timeout) as e:
            self.log.error(f"Error retrieving JOSS record {ZENODO_API_BASE_URL}{record}. Aborting.")
            raise e
        self.log.debug(
            f"Response to {ZENODO_API_BASE_URL}{record}:\n    {r.status_code}: {r.text}\n    Headers: {r.headers}"
            # TODO Remove
        )
        if r.status_code != 200:
            self.log.warning(f"Could not retrieve Zenodo metadata due to {r.status_code} status for record {record}.")
            return None, None
        else:
            if int(r.headers["X-RateLimit-Remaining"]) <= 1:
                self.wait_until(int(r.headers["X-RateLimit-Reset"]))
            zenodo_json = r.json()
            git_platform_url = self._get_git_platform_url(zenodo_json)
            zenodo_version = self._get_zenodo_version(zenodo_json, record)

            return git_platform_url, zenodo_version

    ##################################################
    ########## Static methods
    ##################################################

    @staticmethod
    def _extract_publication_dates(paper_data: dict) -> str:
        """
        Extracts publication year, month and day from a JOSS paper data dict.

        :param paper_data: The JOSS paper dict to extract publication dates from
        """
        iso_str = paper_data["published_at"]
        dt = datetime.fromisoformat(iso_str)
        month = f"-{str(dt.month).zfill(2)}" if dt.month else ""
        day = f"-{str(dt.day).zfill(2)}" if (dt.month and dt.day) else ""
        return str(dt.year) + month + day

    @staticmethod
    def set_version_from_zenodo_metadata(
        version: MentionedVersion, git_platform_version_url: str, archive_version: str
    ) -> MentionedVersion:
        if not version:
            version = MentionedVersion()
        version.version = archive_version
        if archive_version is not None:
            version.type = VersionType.NAME
            version.based_on = DeterminationSource.ARCHIVE_METADATA
        if git_platform_version_url:
            if Platform.SOURCEFORGE_NET not in git_platform_version_url:
                typed_version = get_typed_version_from_git_url(git_platform_version_url)
                if typed_version is not None:
                    version.identification_url = git_platform_version_url
                    version.type = typed_version.type
                    version.version = typed_version.version
                    version.based_on = DeterminationSource.RELATED_IDENTIFIER_URL
            elif "/ci/" in git_platform_version_url and "/tree" in git_platform_version_url:
                version.identification_url = git_platform_version_url
                version.type = VersionType.PATH
                version.version = git_platform_version_url.split("/ci/")[-1].split("/tree")[0]
                version.based_on = DeterminationSource.RELATED_IDENTIFIER_URL
        return version

    def _get_git_platform_url(self, zenodo_json) -> str:
        if "related_identifiers" in zenodo_json["metadata"]:
            rel_identifiers = zenodo_json["metadata"]["related_identifiers"]
            for rel_id in rel_identifiers:
                if (
                    rel_id["relation"] == "isSupplementTo"
                    and "resource_type" in rel_id
                    and rel_id["resource_type"] == "software"
                ):
                    rel_url = rel_id["identifier"]
                    if any(
                        x in rel_url
                        for x in (
                            Platform.GITHUB_COM,
                            Platform.GITLAB_COM,
                            Platform.BITBUCKET_ORG,
                        )
                    ):
                        return rel_url
                    elif "/ci/" in rel_url and "/tree" in rel_url:
                        return rel_url
                    else:
                        self.log.warning(f"Related identifier on Zenodo is not a Git-based platform: {rel_url}.")

    def _get_zenodo_version(self, zenodo_json: dict, record_id: str) -> str:
        if "metadata" in zenodo_json:
            m = zenodo_json["metadata"]
            if "version" in m:
                return m["version"]
            else:
                self.log.debug(
                    f"Did not find version in Zenodo metadata for record {record_id}: {zenodo_json['metadata']}"
                )

    def get_request(self, _url: str, retries: int = 1) -> requests.Response:
        """
        Tries to get a response for a JOSS request, retrying max. 4 times with an interval of 5 secs on connection and
        timeout errors, then raising the exception.

        :param _url: The URL to GET
        :param retries: The number of (re)tries already done
        :return: The response for the GET request
        """
        response = None
        try:
            response = self.session.get(_url)
        except (ConnectionError, Timeout) as e:
            self.log.warning(
                f"Error getting response for JOSS URL {_url}. Retrying in 5 secs (max. 5 times). Details: {e}"
            )
            if retries <= 5:
                retries += 1
                time.sleep(5)
                self.get_request(_url, retries)
            elif retries > 5:
                raise e
        return response

    @staticmethod
    def _create_session():
        session = requests.Session()
        retry = Retry(
            total=10,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
            raise_on_status=False,  # Don't raise exception on retry-able status codes
            respect_retry_after_header=True,  # Respect Retry-After header
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
