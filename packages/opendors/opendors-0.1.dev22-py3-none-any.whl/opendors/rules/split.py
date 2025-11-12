from pathlib import Path
from urllib.parse import urlparse

from opendors.abc import WorkflowRule
from opendors.model import VCS


########################################################################################################################
############################## Class
########################################################################################################################


class SoftwareSplitter(WorkflowRule):
    """
    TODO
    """

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

    ##################################################
    ########## Methods
    ##################################################

    @staticmethod
    def get_file_name_for_software(software) -> str:
        for r in software.repositories:
            if r.main_repo:
                return (
                    r.vcs
                    + "_"
                    + software.platform.split(".")[0]
                    + "_"
                    + urlparse(str(r.clone_url))
                    .path.lstrip("/")
                    .replace("/", "-")
                    .replace(".", "--")
                    + ".json"
                )
        return (
            "none_"
            + software.platform.split(".")[0]
            + "_"
            + urlparse(str(software.canonical_url))
            .path.lstrip("/")
            .replace("/", "-")
            .replace(".", "--")
            + ".json"
        )

    def dump_software(self, software):
        file_name = self.get_file_name_for_software(software)
        with open(Path(str(self.output_dir)) / file_name, "w") as fo:
            fo.write(software.model_dump_json())

    ##########
    ### Main method
    ##########
    def run(self) -> None:
        """
        Splits the ResearchSoftware in a given Corpus into separate files,
        determining a "main" SourceCodeRepository for each software.

        "Main" repositories are either the first encountered git repository,
        or the single Subversion repository for a software. Software with
        no repositories no main repository (e.g., with a single CVS repository)
        will maintain a value for `main_repo` of False.
        """
        c = self.read_corpus(self.input_json)

        if c is not None:
            len_software = len(c.research_software)
            for i, s in enumerate(c.research_software):
                if i % 1000 == 0:
                    self.log.debug("Processing software %i/%i.", i, len_software)
                # Pick the "best" repo, i.e., the first git repo, or the single svn repo
                first_svn_repo = None
                repo_found = False
                for repo in s.repositories:
                    if repo.vcs == VCS.git:
                        repo.main_repo = True
                        repo_found = True
                        break
                    elif repo.vcs == VCS.svn and first_svn_repo is None:
                        first_svn_repo = repo
                if not repo_found and first_svn_repo is not None:
                    first_svn_repo.main_repo = True
                self.dump_software(s)

        self.log.info("Wrote individual files for software.")
