import unittest
from pandas.testing import assert_series_equal, assert_frame_equal

import numpy as np
import pandas as pd

from prioritization.scoring import MetricScore
from prioritization.label_map import Labels

import logging

logging.basicConfig(level=logging.DEBUG)



class MetricScoreTests(unittest.TestCase):
    # class CifbCostsTests(CostsTests):
    """Tests the functionality of the option
    scoring for each lowest layer category.
    """

    @classmethod
    def setUp(self):
        """Defines example results per scenario and
        option, and introduces filtering limits.
        """
        self.l = Labels().set_scoring()

        self.scoring_df = pd.DataFrame(
                data=[
                    ['Scenario A','A Layer 0','min','max',5,10,15,1],
                    ['Scenario A','B Layer 0','min',10,6,11,8,0.5],
                    ['Scenario A','C Layer 0',5,15,11.3,3,17,1],
                    ['Scenario A','D Layer 0',0,'max',-2,1,5,1],
                    ['Scenario B','A Layer 0','min','max',7,15,14,1],
                    ['Scenario B','B Layer 0','min',10,8,16,7,0.5],
                    ['Scenario B','C Layer 0',5,15,13.3,8,16,1],
                    ['Scenario B','D Layer 0',0,'max',0,6,4,1]
                ],
                columns=[
                    'Scenario','Layer 0','Low Filter','High Filter',\
                        'Option 1','Option 2','Option 3','Global Weights'])

        self.score_limit_df = pd.DataFrame(
                data=[
                    [1,10],
                ],
                columns=['Min Score','Max Score'])

        self.scoring = MetricScore(
            self.scoring_df,
            self.score_limit_df,
            'Layer 0')

    def test_linear_map(self):
        """Tests linear score map.
        """
        hifi = 20 
        lofi = 11 
        minscore = 1 
        maxscore = 10
    
        # value between hifi and lofi
        val = self.scoring.linear_map(
            hifi, 
            lofi, 
            15, 
            minscore, 
            maxscore
        )

        self.assertTrue(val, 5)

        # value above hifi
        val = self.scoring.linear_map(
            hifi, 
            lofi, 
            22, 
            minscore, 
            maxscore
        )

        self.assertTrue(val, hifi)

        # value below lofi
        val = self.scoring.linear_map(
            hifi, 
            lofi, 
            3, 
            minscore, 
            maxscore
        )

        self.assertTrue(val, lofi)

    def test_determine_limits(self):
        """Tests the determination of score
        limits.
        """

        self.scoring.determine_limits(
            self.scoring_df
        )

        self.assertFalse(
            (self.scoring.scoring_df[
                self.l['lofi']]==self.l['min']).any()
        )

        self.assertFalse(
            (self.scoring.scoring_df[
                self.l['hifi']]==self.l['max']).any()
        )

        self.assertTrue(
            (self.scoring_df.loc[
                self.scoring_df[self.l['hifi']]!=self.l['max'],self.l['hifi']]==\
            self.scoring.scoring_df.loc[
                self.scoring_df[self.l['hifi']]!=self.l['max'],self.l['hifi']]).all()
        )

        self.assertTrue(
            (self.scoring_df.loc[
                self.scoring_df[self.l['lofi']]!=self.l['min'],self.l['lofi']]==\
            self.scoring.scoring_df.loc[
                self.scoring_df[self.l['lofi']]!=self.l['min'],self.l['lofi']]).all()
        )

    def test_score_results(self):
        """Tests the results scoring.
        """
        self.scoring.determine_limits(
            self.scoring_df
        )

        res = self.scoring.score_results()

        self.assertTrue(
            res['scored_results'].shape[0]*3==\
                res['scored_results_long'].shape[0]
        )
    

