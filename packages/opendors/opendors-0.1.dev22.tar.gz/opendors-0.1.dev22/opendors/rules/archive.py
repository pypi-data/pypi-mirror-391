import json
from collections import namedtuple
import time
from typing import Dict, Any, Optional, Callable

import requests
from requests.structures import CaseInsensitiveDict

from opendors.abc import WorkflowRule
from opendors.model import VersionType, SourceCodeRepository, VCS

SwhIdentifiers = namedtuple("IDs", ["swh_id", "swh_dir_id"])


class SWHIdError(Exception):
    pass


class SWHIdRetriever(WorkflowRule):
    """
    TODO
    SWH tokens can be got with an auth account here:
    https://auth.softwareheritage.org/auth/realms/SoftwareHeritage/account
    """

    def __init__(
        self,
        input_json: str,
        output_json: str,
        swh_token: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.output_json = output_json
        self.base_url = "https://archive.softwareheritage.org/api/1"
        self.headers = {
            "Authorization": f"Bearer {swh_token}",
            "Content-Type": "application/json",
        }
        self.rate_limit = 1200  # Default rate limit (calls per hour)
        self.rate_limit_remaining = 1200  # Default remaining calls
        self.rate_limit_reset = 0  # Default reset time (Unix timestamp)

    def run(self) -> None:
        self.log.debug(f"Retrieving Software Heritage archive data for file {self.input_json}.")

        corpus = self.read_corpus(self.input_json)
        software = corpus.research_software[0]

        for repo in software.repositories:
            if repo.accessible and repo.latest is not None:
                swh_identifiers = self.retrieve_swh_ids(repo)
                if swh_identifiers is not None:
                    repo.latest.swh_id = swh_identifiers.swh_id
                    repo.latest.swh_dir_id = swh_identifiers.swh_dir_id

        self.write_corpus(corpus, self.output_json)
        self.close_logging()

    def retrieve_swh_ids(self, repo: SourceCodeRepository) -> SwhIdentifiers:
        latest = repo.latest
        if latest.version_type == VersionType.TAG:
            if latest.tag_sha is not None:
                # Only git repositories have tag shas
                return self._retrieve_swh_ids_release(repo)
            else:
                return self._retrieve_swh_ids_revision(repo)
        elif latest.version_type == VersionType.REVISION:
            return self._retrieve_swh_ids_revision(repo)
        else:
            raise NotImplementedError("SWH retrieval not implemented for VersionTypes BRANCH, PATH, NAME.")

    def _retrieve_swh_ids_release(self, repo: SourceCodeRepository, new_snp: bool = False) -> SwhIdentifiers | None:
        """
        Works only on git because tag_sha is not recorded for SVN repos!

        :param repo:
        :param new_snp:
        :return:
        """

        def handle_missing_snapshot():
            if new_snp:
                self.log.warning(f"Release {repo.latest.tag_sha} could not be found in newly created snapshot.")
                return
            snp_id = self.save_swh_snapshot(repo)
            if snp_id is not None:
                return self._retrieve_swh_ids_release(repo, True)

        try:
            response = self.get(
                f"release/{repo.latest.tag_sha}/",
                not_found_handler=handle_missing_snapshot,
            )
            if response is not None:
                data = response.json()
                revision_id = self.extract_revision_id(data)
                if revision_id is not None:
                    swh_ids = self._retrieve_swh_ids_revision(repo, revision_id)
                    if swh_ids is not None:
                        return SwhIdentifiers(
                            swh_ids.swh_id,
                            swh_ids.swh_dir_id,
                        )
                self.log.debug(
                    f"In lieu of revision + directory SWH ids, "
                    f"constructing release id for latest version of {repo.clone_url}."
                )
                return SwhIdentifiers(self.construct_swh_id("rel", data["id"]), None)
        except Exception as he:
            self.log.warning(
                f"Something went wrong retrieving SWH IDs for latest version {repo.latest.tag_sha} "
                f"of repo {repo.clone_url}: {he}"
            )

    def _retrieve_swh_ids_revision(
        self, repo: SourceCodeRepository, revision_id: str = None, new_snp: bool = False
    ) -> SwhIdentifiers | None:
        if revision_id is None and repo.latest.revision_id is not None:
            revision_id = repo.latest.revision_id

        def handle_missing_snapshot():
            if new_snp:
                self.log.warning(f"Revision {revision_id} could not be found in newly created snapshot.")
                return
            snp_id = self.save_swh_snapshot(repo)
            if snp_id is not None:
                self._retrieve_swh_ids_revision(repo, revision_id, True)

        if repo.vcs == VCS.svn:
            return self._retrieve_swh_id_svn_revision(repo, revision_id, not_found_handler=handle_missing_snapshot)
        try:
            response = self.get(f"revision/{revision_id}/", not_found_handler=handle_missing_snapshot)
            if response is not None:
                data = response.json()
                self.log.debug(
                    f"Successfully retrieved revision + directory SWH ids for latest version of {repo.clone_url}."
                )
                return SwhIdentifiers(
                    self.construct_swh_id("rev", data["id"]),
                    self.construct_swh_id("dir", data["directory"]),
                )
        except Exception as he:
            self.log.warning(
                f"Something went wrong retrieving SWH IDs for latest version {repo.latest.tag_sha} "
                f"of repo {repo.clone_url}: {he}"
            )

    @staticmethod
    def construct_swh_id(typ: str, sha: str) -> str:
        return f"swh:1:{typ}:{sha}"

    def save_swh_snapshot(self, repo: SourceCodeRepository) -> str | None:
        url_path = f"origin/save/{repo.vcs.value}/url/{str(repo.clone_url).removesuffix('.git')}/"
        response = self.post(url_path)
        data = response.json()
        if response.status_code == 403:
            self.log.warning(f"The repository URL is blacklisted for the Software Heritage Archive: {repo.clone_url}.")
        elif response.status_code == 200:
            if data["save_request_status"] == "accepted":
                visit = self.track_swh_request(data["id"])
                if visit is not None:
                    if visit["save_task_status"] == "succeeded":
                        self.log.info(f"Successfully created new SWH snapshot for {repo.clone_url}.")
                        return visit["snapshot_swhid"]
                    elif visit["save_task_status"] == "failed":
                        note = "No failure note"
                        if "note" in visit:
                            note = visit["note"]
                        self.log.warning(
                            f"Creating a new SWH snapshot for {repo.clone_url} failed: "
                            f"{note if note is not None else 'reason unclear'}."
                        )
                        return None
                else:
                    self.log.warning(f"Could not check completion status for snapshot request {data['id']}.")
                    return None
        return None

    def track_swh_request(self, request_id: str) -> dict | None:
        wait_time = 30
        while True:
            try:
                has_completed, result = self.save_completed(f"origin/save/{request_id}/")
                if has_completed:
                    return result
                else:
                    self.log.info(f"Save not completed, waiting {wait_time / 60} mins.")
                    time.sleep(wait_time)
                    wait_time = wait_time * 2 if wait_time < 1800 else 3600  # Exponential backoff with 1hr max.
            except SWHIdError:
                return None

    def save_completed(self, url_path: str) -> (bool, dict | None):
        response = self.get(url_path)
        if response.status_code == 200:
            data = response.json()
            if data["save_task_status"] in ["succeeded", "failed"]:
                return True, data
            else:
                return False, data
        else:
            raise SWHIdError(f"Non 200 status code for querying SWH API with {url_path}.")

    @staticmethod
    def extract_revision_id(release_data: dict) -> str | None:
        if release_data["target_type"] == "revision":
            return release_data["target"]
        else:
            return None

    ###################################################################

    def _update_rate_limit_info(self, headers: CaseInsensitiveDict[str, str]) -> None:
        """
        Update rate limit information from response headers.
        """
        if "X-RateLimit-Limit" in headers:
            self.rate_limit = int(headers["X-RateLimit-Limit"])

        if "X-RateLimit-Remaining" in headers:
            self.rate_limit_remaining = int(headers["X-RateLimit-Remaining"])

        if "X-RateLimit-Reset" in headers:
            self.rate_limit_reset = int(headers["X-RateLimit-Reset"])

    def _wait_for_rate_limit_reset(self) -> None:
        """
        Wait until the rate limit resets if necessary.
        """
        if self.rate_limit_remaining <= 0:
            current_time = time.time()
            if self.rate_limit_reset > current_time:
                wait_time = self.rate_limit_reset - current_time + 1  # Add 1 second buffer
                self.log.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds for reset.")
                time.sleep(wait_time)
                self.rate_limit_remaining = self.rate_limit  # Reset the counter
            else:
                # If reset time is in the past, just wait a short time and try again
                self.log.warning("Rate limit reset time is in the past. Waiting 5 seconds.")
                time.sleep(5)

    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: int = 2,
        not_found_handler: Optional[Callable[[str], Any]] = None,
    ) -> requests.Response:
        """
        Make an API request, respecting rate limits.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/').rstrip('/')}"
        url = url + "/" if "?" not in url else url
        retries = 0

        while retries <= max_retries:
            # Check and wait for rate limit if necessary
            self._wait_for_rate_limit_reset()

            try:
                self.log.debug(f"Making {method} request to {url}.")
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=30,  # Set a reasonable timeout
                )

                # Update rate limit information
                self._update_rate_limit_info(response.headers)

                # Log remaining rate limit
                self.log.debug(f"Rate limit remaining: {self.rate_limit_remaining}/{self.rate_limit}.")

                # Handle 404
                if response.status_code == 404 and not_found_handler is not None:
                    self.log.info(f"Resource not found (404) at {url}. Calling handler function.")
                    return not_found_handler()

                # Raise an exception for 4XX/5XX responses
                response.raise_for_status()

                return response

            except requests.exceptions.HTTPError as he:
                status_code = he.response.status_code

                # Handle 404 errors with custom handler if provided
                if status_code == 404 and not_found_handler is not None:
                    self.log.info(f"Resource not found (404) at {url}. Calling handler function.")
                    return not_found_handler(endpoint)

                # Handle rate limiting (status code 429)
                if status_code == 429:
                    self._update_rate_limit_info(he.response.headers)
                    self.log.warning("Rate limit exceeded (429 response). Waiting for reset.")
                    self._wait_for_rate_limit_reset()
                    retries += 1
                    continue

                # Server errors might be temporary
                elif 500 <= status_code < 600:
                    if retries < max_retries:
                        wait_time = retry_delay * (2**retries)  # Exponential backoff
                        self.log.warning(f"Server error {status_code}. Retrying in {wait_time} seconds.")
                        time.sleep(wait_time)
                        retries += 1
                        continue
                    else:
                        self.log.error(f"Failed after {max_retries} retries with server error {status_code}.")
                        raise

                # Client errors (4XX) other than 429 are likely not going to be resolved by retrying
                else:
                    self.log.error(f"Client error: {status_code} - {he.response.text}.")
                    raise

            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ):
                if retries < max_retries:
                    wait_time = retry_delay * (2**retries)
                    self.log.warning(f"Connection error or timeout. Retrying in {wait_time} seconds.")
                    time.sleep(wait_time)
                    retries += 1
                    continue
                else:
                    self.log.error(f"Failed after {max_retries} retries with connection error")
                    raise

        # Should not reach here, but just in case
        raise requests.exceptions.RequestException("Maximum retries exceeded.")

    def get(self, endpoint: str, not_found_handler: Optional[Callable[[str], Any]] = None) -> requests.Response:
        return self.make_request("GET", endpoint, not_found_handler=not_found_handler, max_retries=10)

    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self.make_request("POST", endpoint, json_data=json_data)

    def close_logging(self):
        handlers = self.log.handlers[:]
        for handler in handlers:
            self.log.removeHandler(handler)
            handler.close()

    def _retrieve_swh_id_svn_revision(
        self,
        repo: SourceCodeRepository,
        revision_id: str,
        not_found_handler: Optional[Callable[[str], Any]] = None,
    ) -> SwhIdentifiers | None:
        """Retrieve Software Heritage identifiers for a specific SVN revision."""
        try:
            # Validate inputs
            if not revision_id or not repo.clone_url:
                self.log.error("Invalid revision_id or clone URL")
                return None

            # Get latest visit and snapshot
            latest_visit_url = f"origin/{repo.clone_url}/visit/latest/?require_snapshot=true"
            response = self.get(latest_visit_url, not_found_handler=not_found_handler)
            if not response:
                self.log.error("Failed to get latest visit")
                return None
            data = self._parse_json_response(response, "visit data")
            if not data or "snapshot_url" not in data:
                self.log.error(f"No snapshot URL in response for {latest_visit_url}.")
                return None

            snp_url = data["snapshot_url"].removeprefix(self.base_url)
            snp_response = self.get(snp_url)
            if not snp_response:
                self.log.error("Failed to get snapshot data")
                return None

            # Process snapshot data and get HEAD target
            snp_data = self._parse_json_response(snp_response, "snapshot data")
            if not snp_data:
                return None

            target_url = self._extract_head_target_url(snp_data)
            if not target_url:
                return None

            # Get HEAD revision data
            head_response = self.get(target_url)
            if not head_response:
                self.log.error("Failed to get HEAD revision data")
                return None

            head_data = self._parse_json_response(head_response, "HEAD data")
            if not head_data:
                return None

            # Check if HEAD is target revision
            svn_rev = self._extract_svn_revision(head_data)
            if not svn_rev:
                return None

            if svn_rev == revision_id:
                return self._create_identifiers(head_data)
            elif int(svn_rev) < int(revision_id):
                self.log.info(f"Latest revision in snapshot is earlier than revision {svn_rev}, creating new snapshot")
                snp_id = self.save_swh_snapshot(repo)
                if snp_id is not None:
                    return self._retrieve_swh_ids_revision(repo, revision_id, True)
                else:
                    # Give up
                    return None

            # Search in revision log
            log_url = f"{target_url}log/{self._swh_log_limit(svn_rev, revision_id)}"
            log_response = self.get(log_url)
            if not log_response:
                self.log.error("Failed to get revision log")
                return None

            log_data = self._parse_json_response(log_response, "log data")
            if not log_data or not isinstance(log_data, list) or not log_data:
                self.log.error("Invalid log data format")
                return None

            # Find target revision in log
            target_log = log_data[-1]
            target_rev = self._extract_svn_revision(target_log)

            if target_rev == revision_id:
                self._log_revision_info(target_log, revision_id)
                return self._create_identifiers(target_log)
            else:
                self.log.error(f"Wrong revision found: {target_rev} != {revision_id}")
                return None

        except Exception as e:
            self.log.error(f"Unexpected error in SVN revision retrieval: {str(e)}")
            return None

    def _parse_json_response(self, response: requests.Response, context: str) -> dict | None:
        """Parse JSON response with error handling."""
        try:
            return response.json()
        except ValueError as e:
            self.log.error(f"Invalid JSON in {context}: {str(e)}")
            return None

    def _extract_head_target_url(self, snp_data: dict) -> str | None:
        """Extract HEAD target URL from snapshot data."""
        try:
            target_url = snp_data.get("branches", {}).get("HEAD", {}).get("target_url")
            if not target_url:
                self.log.error(f"Could not retrieve target URL from data {json.dumps(snp_data, indent=4)}")
                return None
            return target_url.removeprefix(self.base_url)
        except Exception as e:
            self.log.error(f"Error extracting HEAD target URL: {str(e)}")
            return None

    def _extract_svn_revision(self, data: dict) -> str | None:
        """Extract SVN revision from response data."""
        try:
            for header in data.get("extra_headers", []):
                if len(header) >= 2 and header[0] == "svn_revision":
                    return header[1]
            return None
        except Exception as e:
            self.log.error(f"Error extracting SVN revision: {str(e)}")
            return None

    def _create_identifiers(self, data: dict) -> SwhIdentifiers:
        """Create SWH identifiers from response data."""
        return SwhIdentifiers(
            self.construct_swh_id("rev", data["id"]),
            self.construct_swh_id("dir", data["directory"]),
        )

    def _log_revision_info(self, log_entry: dict, revision_id: str) -> None:
        """Log revision information."""
        log_info = {
            "url": log_entry["url"],
            "id": log_entry["id"],
            "directory": log_entry["directory"],
            "extra_headers": log_entry["extra_headers"],
        }
        self.log.info(f"Target revision is correct revision {revision_id}: {json.dumps(log_info)}")

    @staticmethod
    def _swh_log_limit(latest_rev: str, revision_id: str) -> str:
        """
        Calulate the log limit to retrieve,
        based on the latest revision id and the revision id we want to retrieve the SWH identifiers for.

        :param latest_rev:
        :param revision_id:
        :return:
        """
        try:
            limit = int(latest_rev) - int(revision_id) + 1
            return f"?limit={limit}"
        except ValueError:
            return ""
