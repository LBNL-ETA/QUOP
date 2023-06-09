import unittest
from pandas.testing import assert_series_equal, assert_frame_equal

import numpy as np
import pandas as pd

from prioritization.ahp import PriorityWeights
from prioritization.label_map import Labels

import logging

logging.basicConfig(level=logging.DEBUG)



class PriorityWeightsTests(unittest.TestCase):
    # class CifbCostsTests(CostsTests):
    """Tests the functionality of the priority
    weight calculation class with its methods.
    """

    @classmethod
    def setUp(self):
        """Defines:
        * example priority rating input matrices 
        * the random index used for determination
        of priority rating consistency.
        """
        self.l = Labels().set_ahp()

        self.priority_weight_dfs = {
            'layer_2' : pd.DataFrame(
                data=[
                    ['A Layer 2', 1, 1],
                    ['B Layer 2', '', 1]
                ],
                columns=['Layer 2', 'A Layer 2', 'B Layer 2']),
            'layer_1' : pd.DataFrame(
                            data=[
                                ['A Layer 1', 1, 3],
                                ['B Layer 1', '', 1]
                            ],
                columns=['Layer 1/A Layer 2', 'A Layer 1', 'B Layer 1']),
            'layer_1a' : pd.DataFrame(
                            data=[
                                ['A Layer 1', 1, 5],
                                ['B Layer 1', '', 1]
                            ],
                columns=['Layer 1/B Layer 2', 'A Layer 1', 'B Layer 1']),

            'layer_0' : pd.DataFrame(
                            data=[
                                ['A Layer 0', 1, 1/3],
                                ['B Layer 0', '', 1]
                            ],
                columns=[
                    'Layer 0/A Layer 1/A Layer 2', 'A Layer 0', 'B Layer 0']),
            'layer_0a' : pd.DataFrame(
                            data=[
                                ['C Layer 0', 1, 7],
                                ['D Layer 0', '', 1]
                            ],
                columns=[
                    'Layer 0/B Layer 1/A Layer 2', 'C Layer 0', 'D Layer 0']),
            'layer_0b' : pd.DataFrame(
                            data=[
                                ['A Layer 0', 1, 9],
                                ['B Layer 0', '', 1]
                            ],
                columns=[
                    'Layer 0/B Layer 1/B Layer 2', 'A Layer 0', 'B Layer 0']),
            'layer_0c' : pd.DataFrame(
                            data=[
                                ['C Layer 0', 1, 1/9],
                                ['D Layer 0', '', 1]
                            ],
                columns=[
                    'Layer 0/A Layer 1/B Layer 2', 'C Layer 0', 'D Layer 0']),
        }

        # Example random index (average priority matrix 
        # consistency index for various matrix orders)
        ahp_ri = pd.DataFrame(data = [
            [2,0],
            [3, 0.58],
            [4, 0.9],
            [5, 1.12],
            [6, 1.24],
            [7, 1.32],
            [8, 1.41],
            ],
            columns = [
            'Priority Matrix Order', 'Average Consistency Index'])

        self.ahp = PriorityWeights(
            self.priority_weight_dfs, ahp_ri)

    def test_calc_priority_score_and_weight(self):
        """Tests calculation of the priority score and weight
        from a given priority rating matrix.
        """
        # layer 2

        priority_score_df = self.ahp.calc_priority_score_and_weight(
            self.priority_weight_dfs['layer_2'], 'layer_2')['priority_weights']

        self.assertTrue(
            (priority_score_df.columns.values==\
            ['Layer 2','Layer 2 Priority Score','Layer 2 Priority Weight']).\
                all()
            )

        self.assertTrue(
            (priority_score_df['Layer 2 Priority Weight']==\
            0.5).all()
            )

        # layer 1

        priority_score_df = self.ahp.calc_priority_score_and_weight(
            self.priority_weight_dfs['layer_1a'], 'layer_1a')['priority_weights']
        
        self.assertTrue(
            (priority_score_df.columns.values==\
            ['Layer 2','Layer 1',\
             'Layer 1 Priority Score','Layer 1 Priority Weight']).\
                all()
            )
        
        self.assertTrue(
            (np.array(priority_score_df[
                'Layer 1 Priority Score']).astype(float).round(2)==\
            np.array([2.23606, 0.447214]).round(2)).all()
            )

        # layer 0

        priority_score_df = self.ahp.calc_priority_score_and_weight(
            self.priority_weight_dfs['layer_0a'], 'layer_0a')['priority_weights']

        self.assertTrue(
            (priority_score_df.columns.values==\
            ['Layer 2','Layer 1','Layer 0',\
             'Layer 0 Priority Score','Layer 0 Priority Weight']).\
                all()
            )

        self.assertTrue(
            (np.array(priority_score_df[
                'Layer 0 Priority Score']).astype(float).round(2)==\
            np.array([2.645751, 0.377964]).round(2)).all()
            )

    def test_calculate(self):
        """Tests the full calculation of priority weights that 
        sum to one per each layer 2 entity, and overall.
        """
        priority_weights = self.ahp.calculate()

        self.assertTrue(
            (np.array(priority_weights[
                'final_weights'][
                    self.l["final"] + " " + self.l["pr_wgt"]]).astype(float).round(2)==\
            np.array([0.17, 0.29, 0.15, 0.39]).round(2)).all()
            )

        self.assertTrue(
            priority_weights[
                'weights_per_top_layer_entities'].shape[0] == 8)

    def test_plot_weights(self):
        """_summary_
        """
        priority_weights = self.ahp.calculate()
        self.ahp.plot_weights()

