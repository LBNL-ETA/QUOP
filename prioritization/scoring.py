import numpy as np
import pandas as pd
import scipy.stats as ss
# IO
from adapter.i_o import IO

from prioritization.label_map import Labels

import logging
log = logging.getLogger(__name__)


class MetricScore(object):
    """The class performs the scoring of the
    quantification results for all options
    and scenarios. Each scenario contains
    the same set of options. All options
    are characterized by an identical set of
    quantifiers, each mutually comparable
    among the options.

    Parameters:

        scoring_df: pandas dataframe
            A table containing the scenario, the low filter,
            the high filter, a global weight,
            and a layer 0 attribute named column. Further columns are
            layer 0 quantification results
            for various option. There may be any number of options.

            Low and high filter value columns can either take a
            numerical value, or one of the following strings: 'min',
            and 'max'. Those strings indicate that the scoring will occur
            linearly between the minimum and/or maximum value
            for a given layer 0 category accross all scenarios.

            See test_inputs.xlsx stored under prioritization.tests
            for an example `scoring` input table.

        score_limit_df: pandas dataframe
            A table containing the overall minimum and the
            maximum score values.

        log_level: None or python logger logging level,
            Logging level. It can be used to deprecate logger messages
            below a certain level.
            For Example: log_level = logging.ERROR will only throw error
            messages and ignore INFO, DEBUG and WARNING.

            Default: logging.DEBUG
    """
    def __init__(
        self,
        scoring_df,
        score_limit_df,
        layer_0_label,
        log_level=logging.DEBUG,
    ):

        # set log level
        self.log_level = log_level
        logging.getLogger().setLevel(log_level)

        self.l = Labels().set_scoring()
        self.layer_0_label = layer_0_label
        self.score_limit_df=score_limit_df

        self.scoring_df = self.determine_limits(
            scoring_df)

    def determine_limits(
        self,
        scoring_df):
        """Based on the values of the
        low and the high filter, including those
        set to min or max, determines
        the final accross the scenarios low and
        high filter value for each layer 0 entity.

        Parameters:

            scoring_df: pandas dataframe
                A table containing the scenario, the low filter,
                the high filter, and a column named the same as the
                layer 0 attribute. All other labels the
                code will interpret as layer 0 quantification results
                for various option. There may be any number of options.

                Low and high filter value columns can either take a
                numerical value, or one of the following strings: 'min',
                and 'max'. Those strings indicate that the scoring will occur
                linearly between the minimum and/or maximum value
                for a given layer 0 category accross all scenarios.

        Returns:

            scoring_df_filters: pandas dataframe
                A table that replaces any instances of 'min' and 'max'
                strings with the actual filters determined based
                on the quantification results for all options
                and scenarios.
        """

        max_over_scenarios = scoring_df.groupby(
            [self.layer_0_label]).max(
                numeric_only=True).reset_index()

        max_over_scenarios['max ' + self.l['hifi']] = \
            max_over_scenarios.iloc[:,1:].max(axis=1)

        max_over_scenarios = max_over_scenarios.drop(
            columns=max_over_scenarios.columns.drop(
                [self.layer_0_label,'max ' + self.l['hifi']])
        )

        min_over_scenarios = scoring_df.groupby(
            [self.layer_0_label]).min(
                numeric_only=True).reset_index()

        min_over_scenarios['min ' + self.l['lofi']] = \
            min_over_scenarios.iloc[:,1:].min(axis=1)

        min_over_scenarios = min_over_scenarios.drop(
            columns=min_over_scenarios.columns.drop(
                [self.layer_0_label,'min ' + self.l['lofi']])
        )

        scoring_df_w_min_and_max = scoring_df.merge(
            max_over_scenarios, on=[self.layer_0_label],
            how='left'
        ).merge(
            min_over_scenarios, on=[self.layer_0_label],
            how='left'
        )

        scoring_df_filters = scoring_df.copy()

        scoring_df_filters[self.l['lofi']]=np.where(
            scoring_df_w_min_and_max[self.l['lofi']]==self.l['min'],
            scoring_df_w_min_and_max['min ' + self.l['lofi']],
            scoring_df_w_min_and_max[self.l['lofi']])

        scoring_df_filters[self.l['hifi']]=np.where(
            scoring_df_w_min_and_max[self.l['hifi']]==self.l['max'],
            scoring_df_w_min_and_max['max ' + self.l['hifi']],
            scoring_df_w_min_and_max[self.l['hifi']])

        return scoring_df_filters

    @staticmethod
    def linear_map(
        hifi,
        lofi,
        value,
        minscore,
        maxscore):
        """Scores values linearly between a low
        and the high limit, on a scale ranging
        from the given minimum and maximum limit.

        Parameters:

            hifi: integer or float
                High value filter

            lofi: integer or float
                Low value filter

            value: integer or float
                Value of the quantification result

            minscore: integer
                Minimum score

            maxscore: integer
                Maximum score

        Returns:

            mapped_score: float
                Linearly mapped score, between the
                minimum and the maximum score, proportional
                to the distances between the value and the
                value filters.
        """
        value = min(hifi,value)
        value = max(lofi,value)
        # between numeric inputs, or as min-max
        # among all scenarios linear fit
        mapped_score = minscore + \
            (maxscore - minscore) * \
                ((value - lofi)/(hifi-lofi))

        return mapped_score


    def apply_global_weight(
        self):
        """Applies the global weight that amplifies
        or attenuates chosen layer 0 entities.

        Returns:

            True - upon completion
        """
        self.scoring_df_long[self.l['fnl_score']] = \
            self.scoring_df_long[self.l['lin_score']] * \
                self.scoring_df_long[self.l['glob_wgt']]

        return True


    def score_results(self,
        decimals_in_scores=0):
        """Scores the quantification
        results for all options and scenarios.

        To do that, it applies the filtering, the
        global weighting, and the linear mapping of the
        quantification results for all layer 0
        entities, options, and accross all provided
        scenarios.

        Parameters:

            decimals_in_scores: integer
                Number of decimal places in the scored results.

                Default: 0.
        """

        options_res_cols = self.scoring_df.columns.drop(
                [self.l['sce'],self.layer_0_label,
                 self.l['hifi'],self.l['lofi'],self.l['glob_wgt']]
                 )

        self.scoring_df[self.l['min_score']] = \
            self.score_limit_df.loc[0, self.l['min_score']]

        self.scoring_df[self.l['max_score']] = \
            self.score_limit_df.loc[0, self.l['max_score']]

        self.scoring_df_long=pd.melt(
            self.scoring_df,
            id_vars=self.scoring_df.columns.drop(options_res_cols),
            value_vars=options_res_cols,
            var_name=self.l['options'],
            value_name='results')

        linear_map = np.vectorize(self.linear_map)

        self.scoring_df_long[self.l['lin_score']] = linear_map(
                self.scoring_df_long[self.l['hifi']],
                self.scoring_df_long[self.l['lofi']],
                self.scoring_df_long['results'],
                self.scoring_df_long[self.l['min_score']],
                self.scoring_df_long[self.l['max_score']],
                ).round(decimals_in_scores)

        self.apply_global_weight()

        scoring_results = self.scoring_df_long.pivot(
            columns=self.l['options'],
            values=self.l['fnl_score'],
            index=[self.l['sce'],self.layer_0_label]).reset_index()

        res = {
            'scored_results' : scoring_results,
            'scored_results_long' : self.scoring_df_long,
        }

        return res

    def plot_scores(self):
        """Plots the scored layer 0 results for provided
        scenarios and options.
        """
        pass