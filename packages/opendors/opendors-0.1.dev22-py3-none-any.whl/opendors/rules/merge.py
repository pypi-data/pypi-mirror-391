from opendors.abc import WorkflowRule
from opendors.model import Corpus


########################################################################################################################
############################## Class
########################################################################################################################


class CorpusMerger(WorkflowRule):
    """
    TODO
    """

    def __init__(
        self,
        input_jsons: list[str],
        output_json: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_jsons = input_jsons
        self.output_json = output_json

    ##################################################
    ########## Methods
    ##################################################

    ##########
    ### Main method
    ##########
    def run(self) -> None:
        c = Corpus()
        total_inputs = len(self.input_jsons)
        s_in_count = s_merged_count = 0

        for i_input, input_json in enumerate(self.input_jsons):
            self.log.debug("Merging input files %i/%i.", i_input + 1, total_inputs)
            c_in = self.read_corpus(input_json)
            for s_in in c_in.research_software:
                s_in_count += 1
                add_results = c.add_software(s_in)
                if add_results.merged_software:
                    s_merged_count += 1

        self.log.debug("Merged %i of %i incoming projects.", s_merged_count, s_in_count)
        try:
            assert s_in_count - s_merged_count == len(c.research_software)
        except AssertionError:
            self.log.error(
                f"Length of software list in merged corpus should be {s_in_count - s_merged_count}, "
                f"is {len(c.research_software)}."
            )
        self.write_corpus(c, self.output_json)
