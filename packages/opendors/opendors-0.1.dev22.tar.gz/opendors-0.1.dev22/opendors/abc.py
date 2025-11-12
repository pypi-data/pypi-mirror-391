from pathlib import Path
import time

from pydantic import ValidationError

from abc import ABC, abstractmethod
from opendors.logging import get_logger
from opendors.model import Corpus


class WorkflowRule(ABC):
    """
    An abstract workflow rule.
    Provides a file logger for the provided log_file with log level log_level.
    """

    def __init__(
        self, name: str, log_file: str, log_level: str = "DEBUG", indent: int = 0
    ) -> None:
        """
        Initializes a workflow rule object.

        :param name: The name to pass to the logger
        :param log_file: The log file to log to
        :param log_level: The log level to log at, must be one of "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"
        :param indent: The indent of any JSON output the retriever creates
        """
        self.name = name
        self.log_file = log_file
        self.log_level = log_level
        self.indent = indent
        self.log = get_logger(self.name, self.log_file, self.log_level)

    @abstractmethod
    def run(self) -> None:
        """
        Runs the workflow rule.

        :return: None
        """
        pass

    def read_corpus(self, corpus_path: str | Path) -> Corpus:
        """
        Read a Corpus from a JSON serialization.

        :raise pydantic.ValidationError:
        :param corpus_path: The path to the JSON-serialized Corpus
        :return: the Corpus object
        """
        with open(corpus_path, "r") as fi:
            self.log.info("Reading Corpus JSON from %s.", corpus_path)
            try:
                c_in = Corpus.model_validate_json(fi.read())
            except ValidationError as ve:
                self.log.error("Cannot parse invalid OpenDORS JSON: %s.", corpus_path)
                raise ve
        return c_in

    def write_corpus(self, corpus: Corpus, corpus_path: str | Path) -> str:
        """
        Writes a Corpus object to a JSON file.

        :param corpus: The corpus object to serialize
        :param corpus_path: The path to write the Corpus JSON to
        :return: None
        """
        corpus_path = Path(corpus_path)
        parent_dir = corpus_path.parent.absolute()
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
        if self.indent > 0:
            model_json = corpus.model_dump_json(
                indent=self.indent, exclude_defaults=True
            )
        else:
            model_json = corpus.model_dump_json(exclude_defaults=True)

        with open(corpus_path, "w") as mj:
            self.log.info("Writing Corpus JSON to %s.", corpus_path)
            mj.write(model_json)

        return model_json

    def wait_until(self, ratelimit_reset: int) -> None:
        """
        Waits until the epoch time a second after the given ratelimit reset epoch is reached.
        Can be used by all workflow rules that make calls to rate-limited APIs.

        :param ratelimit_reset: The epoch second when the ratelimit is reset
        :return: None
        """
        now = int(time.time())
        wait_secs = ratelimit_reset - now
        self.log.debug(
            f"Ratelimit reached. Waiting until ratelimit is reset in {wait_secs / 60} minutes."
        )
        time.sleep(wait_secs + 1)
