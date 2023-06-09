import logging

log = logging.getLogger(__name__)


class Labels(object):
    """Maps input table headers to shorter strings
    used throughout the code. The purpose of the
    mapping dictionaries is to decouple the
    variables in the code from the input tables,
    so that an edit to a column label in the inputs
    only requires a single edit to the label map.
    """

    def __init__(
        self,
        log_level=logging.DEBUG,
    ):
        """Constructs the label class.

        Parameters:

            log_level : logging object
                Sets log level. Default: logging.DEBUG
        """

        # set log level
        self.log_level = log_level
        logging.getLogger().setLevel(log_level)

    def set_scoring(self):
        """Defines scaling labels.
        """
        self.scoring = {
            'min':'min',
            'max':'max',
            'options':'Options',
            # scoring input table mandatory labels
            'sce':'Scenario',
            'lofi':'Low Filter',
            'hifi':'High Filter',
            'glob_wgt':'Global Weights',
            # score range input table mandatory labels
            'min_score':'Min Score',
            'max_score':'Max Score',
            # table names and substrings
            'scoring' : 'scoring',
            'score_range' : 'score_range',
            'fnl_score' : 'Final Score',
            'lin_score' : "Score (Linear Map)",
        }

        return self.scoring


    def set_ahp(self):
        """Defines advanced hierarchy process (AHP)
        labels.
        """
        self.ahp = {
            "pr_score" : "Priority Score",
            "pr_wgt" : "Priority Weight",
            "pr_mtrx_ord" : "Priority Matrix Order",
            "ri" : "Average Consistency Index",
            "final" : "Final",
            # table names and substrings
            'random_index' : 'random_index',
            'layer_' : 'layer_'
        }

        return self.ahp

    def set_visual(self):
        """Defines visualization labels.
        """
        self.visual = {
            
        }

        return self.visual

    def set_results(self):
        """Defines results labels.
        """
        self.res = {
            "wgtd_score" : "Weighted Score",
            "bin" : "Bin",
        }

        return self.res



