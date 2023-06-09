import unittest
from pandas.testing import assert_series_equal, assert_frame_equal

import numpy as np
import pandas as pd

from prioritization.ahp import PriorityWeights
from prioritization.process import Prioritizer
from prioritization.label_map import Labels

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class PrioritizerTests(unittest.TestCase):
    # class CifbCostsTests(CostsTests):
    """Tests the functionality of the priority
    weight calculation class with its methods."""

    @classmethod
    def setUp(self):
        """Defines example priority rating input
        matrices by reading them from the test input 
        file (see path below).
        """
        logger = logging.getLogger()
        logger_filename = "prioritization_run.log"

        fh = logging.FileHandler(logger_filename)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        self.inpath="prioritization/tests/test_input.xlsx"

        self.prioritizer = Prioritizer(
            inpath=self.inpath,
            writeout=False)

    def test_calculate(self):
        """Tests prioritization process.
        """
        # layer 2
        self.prioritizer.calculate()

        if self.inpath==r"prioritization/tests/cfh_test_input.xlsx":

            number_of_scenarios = len(self.prioritizer.scores_and_weights[
                'pivoted']['Scenario'].unique())

            number_of_layer_0_entities = len(
                self.prioritizer.scores_and_weights[
                'pivoted']['Layer 0'].unique())

            number_of_layer_2_entities = len(
                self.prioritizer.scores_and_weights[
                'pivoted']['Layer 2'].unique())

            self.assertTrue(
                self.prioritizer.scores_and_weights['pivoted'].shape\
                    == (int(number_of_layer_2_entities*\
                        number_of_layer_0_entities*\
                            number_of_scenarios), 7))

            self.assertTrue(
                self.prioritizer.scores_and_weights_top_layer['pivoted'].shape\
                    == (int(number_of_layer_0_entities*number_of_scenarios), 7))

        else:
            print(self.prioritizer.scores_and_weights)

