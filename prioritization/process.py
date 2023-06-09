
import re
from datetime import datetime
from platform import python_version

import adapter
# import numpy as np
import pandas as pd
# import scipy.stats as ss
# IO
from adapter.i_o import IO

import prioritization
from prioritization.label_map import Labels
from prioritization.scoring import MetricScore
from prioritization.ahp import PriorityWeights

import logging
log = logging.getLogger(__name__)


class Prioritizer(object):
    """The class performs the steps of an evaluatory process,
    such as of a prioritization or a ranking process,
    that mutually compares options from various perspectives.
    The options can be, for example, a number of technologies
    used to provide the same or a similar utility. Each of the
    options needs to be described using the same set of quantitave
    characterizations, for example a set of metrics results.

    To evaluate the options, the prioritization process performs
    three steps as follows:

    1. The scoring - converts quantitative characterization
       results, given for all options, into mutually comparable
       quantitative characterization scores.

    2. The prioritization - calculates the relative importance,
       called a weight, of each of the individual quantitative
       characterization scores, from various standpoints.
       A standpoint represents an opinion of a stakeholder group,
       for instance, the customers, the government,
       or any chosen distinct participant in the value chain.

       The weighing of the characterization scores is performed
       within a group of characteristics, and among the groups,
       for each of the options. This step, essentially, enables us
       to learn what characteristic matters more from each specific
       perspective.

       Finally, a top level prioritization combines
       various standpoints, each given a desired importance,
       in the overall evaluation.

       Therefore, the prioritization weight development is structured
       into three layers:

       * layer 0 is an attribute containing the lowest level
         entities that quantify relevant characteristics associated
         with each distict option being evaluated for a given purpose.

       * layer 1 is an attribute containing entities that are
         groups of layer 0 entities, usually grouped
         based on anticipated stakeholder interest. One benefit of
         adding this layer is the simplification of mutual weighting of
         layer 0 entities. For example, it is easier to assess
         mutual importance of a smaller number of groups of characteristics,
         rather than the mutual imporatance of each individual one.

       * layer 2 - the entities of a layer 2 attribute are the
         stakeholders or stakeholder groups evaluating the options.
         The layer 2, therefore, allows the user of the tool, to
         amplify or attenduate the voice of each of the stakeholders,
         based on some goal, for instance customer
         satisfaction, or societal environmental gain.

    3. The ranking - once the scores are multiplied with the
       prioritization weights, the options can be ranked to
       indicate higher or lower benefit to a given
       stakeholeder, or overall. To perform the ranking, the
       total sum of scored and weighted results is calculated for
       each option. After that, the final scored and weighted
       results can be assigned to a number of equally spaced
       bins. The bins default to green, yellow, and red bin,
       where green indicates the highest quality bin brought by
       the option to each stakeholder and overall.

    The class performs the prioritization process steps as follows:

    1. Scores the metric results found in the dedicated table
       in the input file, for all provided scenario results.
       The minimum and the maximum overall score is also
       provided through an input table with a specific
       table name (see example input for more info on
       standardized table naming for code recognition - under
       prioritization/tests folder lives a file named
       test_input.xlsx).

    2. Calculates the prioritization weights for all
       level 0 entities (option quantifiers),
       from various stakeholder standpoints
       (level 1) and the standpoint-combined view (level 2).

    3. Ranks the options and categorizes them into a given number
       of bins.

    Parameters:

        inpath: string or None
            Full path to the input file. Example input file is
            provided as a part of the test suite.

            Default: None

        writeout: boolean
            Choice to write the evaluation results out into
            a dedicated folder, as provided in the run_parameters
            table of the input file.

            Default: False

        create_plots: boolean
            Choice to create plots based on the evaluation process
            results.

            Default: False

        os_mapping: dict
            A dictionary that maps the operating system to the
            default root part of the path. Update for your
            specific path, for instance {'win32': 'C:'} if your
            PC is a windows machine and the repository is stored
            at the C: drive.

            Default: {'win32': 'W:', 'darwin': '/Volumes/ees',
                     'linux': '/media/ees'}

        number_of_ranking_bins: integer
            Count of rating bins that the ranked options are
            categorized into.

            Default: 3.

        lower_ranking_limit_0: boolean
            If True, the rating bins are equidistant between 0 and
            the maximum final score among all options and, if applicable,
            standpoints. If False, the lower limit of the ranking is the
            minimum overall final score, instead of the 0.

            Default: True

        ranking_bin_labels: list of strings
            List of strings associated with each of the
            ranking bins, from worst to best.

            Default: ['red', 'yellow', 'green']

        log_level: None or python logger logging level,
            Logging level. It can be used to deprecate logger messages
            below a certain level.
            For Example: log_level = logging.ERROR will only throw error
            messages and ignore INFO, DEBUG and WARNING.

            Default: logging.DEBUG
    """
    def __init__(
        self,
        inpath=None,
        writeout=False,
        create_plots=False,
        os_mapping={'win32': 'W:', 'darwin': '/Volumes/ees',
                     'linux': '/media/ees'},
        number_of_ranking_bins=3,
        lower_ranking_limit_0=True,
        ranking_bin_labels=['red', 'yellow', 'green'],
        log_level=logging.DEBUG,
    ):

        self.ahp_l = Labels().set_ahp()
        self.sco_l = Labels().set_scoring()
        self.res_l = Labels().set_results()

        # start timer
        self.start_time = datetime.now()

        # set log level
        self.log_level = log_level
        logging.getLogger().setLevel(log_level)
        # log versions
        log.info("Python version: {}".format(python_version()))

        log.info("CFH task 4 prioritization package version: {}".format(
            prioritization.__version__))

        log.info("Adapter package version: {}".format(adapter.__version__))

        self.inpath = inpath

        self.read_inputs(
            writeout,
            os_mapping=os_mapping)

        self.writeout = writeout
        self.create_plots = create_plots

        self.set_up_inputs()

        self.number_of_ranking_bins = number_of_ranking_bins
        self.lower_ranking_limit_0 = lower_ranking_limit_0
        self.ranking_bin_labels = ranking_bin_labels


    def calculate(self):
        """Performs the main steps of the overall
        calculation:

        * calculates prioritization weights
        * calculates scores from quantification results
        * weighs scored quantification results for all
          options and layer 2 entities (standpoints)
        * calculates the final scores per layer 2 entity,
          and overall based on layer 2 entity weightings,
          that are effectively the appropriate sums of weighted
          scores
        * if enabled, saves the evaluation results into a database
          that already contains a copy of all of the input data
        * creates and saves plots that represent various
          steps in the calculation, including the weighted scored
          option quntifiers, as well as the final scores
        """

        self.calculate_weights()

        self.score_results()

        self.weigh_scored_results()

        self.calculate_final_scores()

        self.rank(
            number_of_ranking_bins=self.number_of_ranking_bins,
            lower_ranking_limit_0=self.lower_ranking_limit_0,
            ranking_bin_labels=self.ranking_bin_labels,
        )

        if self.writeout:
            self.save_evaluation_results()

        if self.create_plots:
            self.plot_evaluation_results()


    def read_inputs(self,
        writeout,
        os_mapping={'win32': 'W:', 'darwin': '/Volumes/ees',
                     'linux': '/media/ees'}):
        """Reads in all input tables and stores them in a dictionary
        with table names as keys and pandas dataframes as values.

        If writeout is enabled, initiates a results database in
        a path and with a version provided in the run_parameters
        table of the input file, and writes all the input tables
        into it (for more information on how this is done please
        see adapterio package on PyPI).


        Parameters:

            writeout: boolean
                Choice to write the evaluation results out into
                a dedicated folder, as provided in the run_parameters
                table of the input file.

                Default: False

            os_mapping: dict
                A dictionary that maps the operating system to the
                default root part of the path. Update for your
                specific path, for instance {'win32': 'C:'} if your
                PC is a windows machine and the repository is stored
                at the C: drive.

                Default: {'win32': 'W:', 'darwin': '/Volumes/ees',
                        'linux': '/media/ees'}
        """

        try:

            self.data_connection = IO(
                self.inpath,
                os_mapping=os_mapping
                     ).load(
                create_db=True,
                db_flavor="sqlite",
                close_db=False,
                skip_writeout=~writeout
            )

            self.inputs = self.data_connection["tables_as_dict_of_dfs"]

        except:
            msg = "Failed to read input tables from {}."

            log.error(msg.format(self.inpath))
            raise ValueError(msg.format(self.inpath))


    def set_up_inputs(self):
        """Extracts appropriate inputs to result scoring and
        weights calculation.
        """
        self.weights_inputs = dict()

        for key in self.inputs.keys():

            if self.ahp_l['layer_'] in key:
                self.weights_inputs[key]=\
                    self.inputs[key]

        self.ahp_ri = self.inputs[
            self.ahp_l["random_index"]]

        self.scoring_df = self.inputs[self.sco_l['scoring']]
        self.score_limit_df = self.inputs[
            self.sco_l['score_range']]


    def score_results(self):
        """Applies the functionality
        encapsulated in the MetricScore
        class to score the options
        quantification results.

        See the MetricScore documentation
        for further detail.
        """
        self.scoring = MetricScore(
            self.scoring_df,
            self.score_limit_df,
            self.layer_0_label).score_results()

        self.scored_results = self.scoring[
            'scored_results'
        ]

        self.scored_results_long = self.scoring[
            'scored_results_long'
        ]


    def calculate_weights(self):
        """Applies the AHP functionality
        encapsulated in the PriorityWeights
        class to determine the priority
        weights for all options and layer 0
        entities (quantifiers).

        See the PriorityWeights documentation
        for further detail.
        """

        self.weights = PriorityWeights(
            self.weights_inputs,
            self.ahp_ri
            ).calculate()

        for key in self.weights.keys():
            setattr(self, key, self.weights[key])


    def weigh_scored_results(self):
        """Weighs the scored results using the
        priority weights.
        """
        self.scores_and_weights = dict()

        self.scores_and_weights['long'] = \
            self.scored_results_long.merge(
            self.weights_per_top_layer_entities,
            on=self.layer_0_label,
            how='left'
        ).merge(self.final_weights.loc[
            :, [self.layer_0_label,
                self.ahp_l["final"] + " " + self.ahp_l['pr_wgt']]],
            on=self.layer_0_label,
            how='left'
        )

        self.scores_and_weights['long'][
            self.res_l['wgtd_score']] = \
            self.scores_and_weights['long'][
            self.ahp_l['pr_wgt']] * \
            self.scores_and_weights['long'][self.sco_l['fnl_score']]

        count_layer_2_entities = self.weights_inputs[
            self.ahp_l['layer_'] + '2'].shape[0]

        self.scores_and_weights['long'][
            self.ahp_l["final"] + " " + self.res_l['wgtd_score']] = \
            self.scores_and_weights['long'][
                self.ahp_l["final"] + " " + self.ahp_l['pr_wgt']] * \
            self.scores_and_weights['long'][self.sco_l['fnl_score']]/\
                count_layer_2_entities

        df=self.scores_and_weights[
            'long'].loc[:, [
                self.layer_2_label, self.layer_1_label,self.layer_0_label,
                self.sco_l['sce'], self.sco_l['options'],
                self.res_l['wgtd_score']
            ]]

        self.scores_and_weights['pivoted'] = df.pivot(
                values=self.res_l['wgtd_score'],
                index=df.columns.drop(
                    [self.sco_l['options'],self.res_l['wgtd_score']]),
                columns=self.sco_l['options']).reset_index().sort_values(
                    [self.layer_2_label,self.sco_l['sce'],self.layer_1_label]
                )


    def calculate_final_scores(self):
        """Aggregates the priority weighted option
        quantification scores to calculate the final
        evaluation scores.
        """
        self.scores_and_weights_top_layer = dict()

        self.scores_and_weights_top_layer['long'] = \
            (self.scores_and_weights['long'].groupby(
                [self.layer_0_label,
                 self.layer_1_label,
                 self.sco_l['sce'],
                self.sco_l['options']]).agg(
            {self.ahp_l["final"] + " " + self.res_l['wgtd_score'] : 'sum'})).\
                reset_index()

        self.scores_and_weights_top_layer['pivoted'] = \
            self.scores_and_weights_top_layer['long'].pivot(
            values=self.ahp_l["final"] + " " + self.res_l['wgtd_score'],
                columns=self.sco_l['options'],
            index=[self.layer_1_label, self.layer_0_label, self.sco_l['sce']]).\
                reset_index().sort_values(
                    [self.sco_l['sce'],self.layer_1_label]).\
                        reset_index()#.drop(
                    # columns=[self.layer_1_label]
                # )


    def rank(
        self,
        number_of_ranking_bins=3,
        ranking_bin_labels=['red','yellow','green'],
        lower_ranking_limit_0=True):
        """Ranks the options based on the final
        scores. Places the ranked options into a
        provided number of bins, that represents
        ratings. The ratings are associated with colors
        for easier understanding. For example, if there are
        three bins, the ratings are associated with green, yellow,
        and red, with green being assigned to some the top ranked
        options.

        The rating bins can be defined as equidistant linear bins
        between the minimum and maximum option-overall final score,
        or between 0 and the maximum such score.

        Parameters:

            number_of_ranking_bins: integer
                Count of rating bins that the ranked options are
                categorized into.

                Default: 3.

            ranking_bin_labels: list of strings
                List of strings associated with each of the
                ranking bins, from worst to best.

                Default: ['red', 'yellow', 'green']

            lower_ranking_limit_0: boolean
                If True, the rating bins are equidistant between 0 and
                the maximum final score among all options and, if applicable,
                standpoints. If False, the lower limit of the ranking is the
                minimum overall final score, instead of the 0.

                Default: False
        """
        if len(ranking_bin_labels) != number_of_ranking_bins:
            msg = "Number of ranking bins is {}. Please ensure that it "\
                "matches the number of ranking bin labels. Currently there "\
                    "are {} such labels in the input kwarg list."
            log.error(msg.format(
                number_of_ranking_bins, ranking_bin_labels
            ))
            raise ValueError

        # sum and rank weighted scores

        # sum Weighted Scores in each scenario and from each
        # standpoint, for each of the options, and then
        # rank the options within each sceanario and standpoint
        # from highest scored to lowest scored ones
        self.scores_and_weights['summed_and_ranked'] = self.\
            scores_and_weights['long'].loc[
                :,[self.sco_l['sce'],self.sco_l['options'],
                  self.layer_2_label,self.res_l['wgtd_score']]
                  ].groupby(
                    [self.sco_l['sce'],self.layer_2_label,self.sco_l['options']]
                    ).sum(
                ).reset_index().sort_values(
                    by=[
                    self.sco_l['sce'],self.layer_2_label,self.res_l['wgtd_score']],
                    ascending=[True, True, False])


        # sum Final Weighted Scores in each scenario
        # for each of the options, and then
        # rank the options within each scenario
        self.scores_and_weights_top_layer['summed_and_ranked'] = self.\
            scores_and_weights_top_layer['long'].loc[
                :,[self.sco_l['sce'], self.sco_l['options'],
                  self.ahp_l["final"] + " " + self.res_l['wgtd_score']]
                  ].groupby(
                    [self.sco_l['sce'],self.sco_l['options']]
                    ).sum(
                ).reset_index().sort_values(
                    by=[
                    self.sco_l['sce'],
                    self.ahp_l["final"] + " " + self.res_l['wgtd_score']
                    ],
                    ascending=[True, False])

        if lower_ranking_limit_0:
            bins = (self.scores_and_weights[
                'summed_and_ranked'][self.res_l['wgtd_score']].max()/3)*range(
                    number_of_ranking_bins + 1)
            bins_top_layer = (self.scores_and_weights_top_layer[
                'summed_and_ranked'][
                    self.ahp_l["final"] + " " + self.res_l['wgtd_score']].max(
                    )/3)*range(number_of_ranking_bins + 1)
        else:
            bins = bins_top_layer = number_of_ranking_bins

        self.scores_and_weights_top_layer['summed_and_ranked'][
            self.res_l['bin']] = pd.cut(
            self.scores_and_weights_top_layer['summed_and_ranked'][
                self.ahp_l["final"] + " " + self.res_l['wgtd_score']],
                bins_top_layer,
                labels = ranking_bin_labels)

        self.scores_and_weights['summed_and_ranked'][
            self.res_l['bin']] = pd.cut(
            self.scores_and_weights['summed_and_ranked'][
                self.res_l['wgtd_score']],
                bins,
                labels = ranking_bin_labels)


    def plot_evaluation_results(self):
        """Plots intermediary and final evaluation results.
        """
        # *mg plot results similarly to cycle 1
        # could include a call to plot_weights and plot_scores (see ahp.py and scoring.PY)
        # list all plot types in the docstring above
        pass

    def save_evaluation_results(self):
        """Saves various intermediary and final dataframes into
        tables of the results database. The tables created
        containg the scored quantification results, the priority
        weights, the priority weighted scores, the final scores, and
        the ranked and rated results.
        """
        # amca_base_eff_static write to the same db created at readin using adapter
        # refine docstring based on actual tables created
        pass