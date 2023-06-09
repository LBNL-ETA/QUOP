import numpy as np
import pandas as pd

# IO
from adapter.i_o import IO

from prioritization.label_map import Labels

import logging
log = logging.getLogger(__name__)
    

class PriorityWeights(object):
    """This class performs the three-layer priority weights 
    calculation for the purpose of any downstream option comparison.

    The calculation implements the Analytical Hierarchy Process (AHP) 
    as found in the publication by Thomas L. Saaty - The Analytic 
    Hierarchy Process: Decision Making In Complex Environments.

    The priority ratings need to be populated in the input file, 
    as instructed in the test_input.xlsx file located at
    prioritization.tests. The should be only one layer 2
    priority rating table, and a number of layer 1 priority
    rating tables equal to the count of unique entities of 
    the layer 2. Similarly, at layer 0 there should be one 
    priority rating table for each combination of layer 2 and 
    layer 1 entities.

    When provided such priority rating tables, the code in
    this class calculates priority scores resulting from the 
    priority ratings for each table. 
    
    In the next step, it normalizes the priority scores within 
    each priority rating table, to obtain the corresponding
    priority weights. 
    
    Then, based on the layer hierarchy tree identified in the 
    priority rating tables provided in the input file, the priority 
    weights are applied to calculate the inter layer 0 entity weights. 
    The hierarchy is recognized by looking at the upper left 
    corner label of each priority rating table.

    The inter layer 0 entity weights are calculated for each
    layer 2 entity (for example standpoint), and overall as 
    defined by the layer 2 priority weights.

    As a result, each layer 0 entity (option characteristic) is
    weighted by importance to each later 2 entity (for example, a 
    customer), and also by overall importance.

    Parameters:

        priority_weight_dfs: dict of pandas dataframes
            Dictionary with:

            * keys that are the input file
              table names carrying the priority rating
              information, that is all the table names that 
              are or include any of the following substrings:
              `layer_0`, `layer_1`, or `layer_2`, and
            * values that are the priority ratings
              found in such input tables

            Example: see an example with 3 layers, and two entities
            in each layer in the test_input.xslx in prioritization.tests 
            or the set up of the test_ahp.py module.    

        random_index: pandas dataframe
            Maps the order of the priority rating matrix 
            (number of rows and columns with ratings) to the expected 
            statistically average consistency index.

            Example: see test_input.xslx in prioritization.tests or 
            the set up of the test_ahp.py module. Values are from
            Saaty.

        log_level: None or python logger logging level,
            Logging level. It can be used to deprecate logger messages 
            below a certain level.
            For Example: log_level = logging.ERROR will only throw error
            messages and ignore INFO, DEBUG and WARNING.

            Default: logging.DEBUG
    """
    def __init__(
        self,
        priority_weight_dfs,
        random_index,
        log_level=logging.DEBUG):

        # set log level
        self.log_level = log_level
        logging.getLogger().setLevel(log_level)
    
        self.l = Labels().set_ahp()

        self.random_index = random_index

        self.layer_category = dict()

        # extract layer 2, 1, and 0 category label
        self.layer_category[2] = priority_weight_dfs[
            'layer_2'].columns[0]

        self.layer_category[1] = priority_weight_dfs[
                    'layer_1'].columns[0].split("/")[0]

        self.layer_category[0] = priority_weight_dfs[
                    'layer_0'].columns[0].split("/")[0]

        self.priority_weight_dfs=priority_weight_dfs

    def calc_priority_score_and_weight(
        self,
        df,
        df_key,
        drop_priority_ratings=True):
        """Performs the following steps for any priority rating
        input table:
        
        1. Processes a priority rating table to ensure data quality:

        * checks that the diagonal is populated with ones
        * calculates the lower left diagonal as the inverse of the
          upper right diagonal
        * checks the consistency of the priority ratings provided
        
        2. Calculates priority scores from priority ratings as their 
           product raised the power inversly proportional to the 
           rank of the priority rating matrix. 

        3. Calculates priority weights from priority scores.

        4. Identifies the position of the priority rating table
           in the prioritization hierarchy through saving the 
           upper left corner index, as it contains the standardized
           structure recognized in the remainder of this package 
           functionality.

        Parameters:

            df: pandas dataframe
                Priority rating table read in from the inputs.

            df_key: string
                Name of the priority rating table, as read in
                from the input file using the adapterio package. If
                excel input file is used, this value is the excel table
                name.

            drop_priority_ratings: boolean
                Once the priority weights are calculated from the 
                priority rating, the ratings are dropped if this 
                value is set to True, otherwise the ratings are 
                kept in the resulting dataframe.

                Default: True

        Returns:

            res: dictionary
                With the following keys:

                'priority_weights': pandas dataframe
                    Contains a column with the prioritization weights, 
                    and optionally keeps a column with the 
                    prioritization scores. 
                    Identifies all the layer labels, depending
                    on the position in the prioritization
                    hierarchy. For instance, if the processed 
                    priority rating table is of layer 2, it will
                    have one column populated with the layer 2 entities, 
                    such that each of the weights, and optionally ratings,
                    corresponds to one of those entities.
                    If the priority rating table processed is of any 
                    lower layer, for instance layer 0, there will be 
                    two additional columns in addition to the appropriate
                    layer 2 labeled column, namely columns indicating the
                    layer 1 and layer 0 entities described in the 
                    priority rating table.

                'corner_index' : string
                    Upper left corner index
        """
        # check columns and values in the first column 
        # are the same
        if list(
            df.columns[1:])!=list(df.iloc[:,0].values):
            msg = "Columns and rows should have the same, but transposed,"\
                " labels in all priority rating input tables, at all layers."\
                " Table {} appears to not satisfy this condition.".format(
                    df_key)

            log.error(msg)
            raise ValueError(msg)
        else:
            rating_columns = list(df.copy().columns.values[1:])
            corner_index = df.copy().columns[0]

        # check diagonal carries ones
        priority_responses = np.array(
            df.iloc[:,1:])
        if not \
            (1 == pd.Series(
                [priority_responses[i,i] for i in range(
                    len(priority_responses))]
                )
                ).all():

                msg = "Values along the priority rating matrix "\
                "diagonal in input table {} "\
                "should all equal 1, and some or all values appear to have "\
                "other values. Please double-check and correct it in the "\
                "input file.".format(df_key)

                log.error(msg)
                raise ValueError(msg)

        # populate lower triangle with 1/upper triangle
        for r in range(len(priority_responses)):
            for c in range(len(priority_responses)):
                if r>c:
                    priority_responses[r,c] = 1./priority_responses[c,r]

        df.iloc[:,1:] = priority_responses

        score_lbl_key = 3 - len(corner_index.split("/"))

        layer_label_prefix = self.layer_category[score_lbl_key] + " "

        # the score is a geometric mean
        df[layer_label_prefix + self.l['pr_score']] = \
            np.prod(priority_responses, axis=1)**(1./len(priority_responses))

        self.check_priority_matrix_consistency(
            priority_responses.astype(float), 
            df_key)

        # split first column if in layer 0 or 1, to learn what is(are) the 
        # upper layer(s)
        i = 1.
        if len(corner_index.split("/"))>1.:
            for lbl in corner_index.split("/"):
                if lbl==self.layer_category[score_lbl_key]:
                    df[lbl] = df[corner_index].copy()
                    cols = list(df.copy().columns.values)
                    df = df.loc[:,cols[-1:] + cols[:-1]]
                else:
                    df[self.layer_category[
                        score_lbl_key + i]] = lbl
                    cols = list(df.copy().columns.values)
                    df = df.loc[:,cols[-1:] + cols[:-1]]
                    i+=1.

            df = df.drop(columns=corner_index)

        df = self.calc_priority_weight(df,layer_label_prefix)

        if drop_priority_ratings:
            df = df.drop(columns=rating_columns)

        res = {
            'priority_weights' : df,
            'corner_index' : corner_index
        }

        return res

    # between numeric inputs, or as min-max among all scenarios
    # linear fit
    def calc_priority_weight(
        self,
        df,
        layer_label_prefix):
        """Calculates the priority weights as the 
        normalized priority score.

        Parameters:

            df: pandas dataframe
                A rating dataframe containing the 
                calculated priority score.

            layer_label_prefi: string
                Label of the lowerst layer attribute 
                represented in the priority rating table.
        """
        df[layer_label_prefix + self.l["pr_wgt"]] = \
            df[layer_label_prefix + self.l["pr_score"]]/\
                df[layer_label_prefix + self.l["pr_score"]].sum()

        return df

    def check_priority_matrix_consistency(
        self, 
        priority_scores_array,
        df_key,
        consistency_threshold=0.5): # *mg gracefully increased the threshold
        """Ensures a priority matrix is consistent.
        The calculation is based on the same source:  
        Thomas L. Saaty - The Analytic Hierarchy Process: 
        Decision Making In Complex Environments.

        Parameters:

            priority_scores_array: np.array
                A square array of priority responses

            df_key: string
                Key associated with the priority scores array

            consistency_threshold: float
                If the matrix inconsistency is calculated to
                be higher than this treshold, the matrix will
                be deemed as inconsistent.
        """
        
        eigenvalue = np.linalg.eigvals(priority_scores_array)[0]
        consistency_index = (eigenvalue - len(priority_scores_array))/\
            (len(priority_scores_array) - 1)

        if consistency_index==0:
            inconsistency_ratio=0.0
        else:
            try:
                inconsistency_ratio = (consistency_index*100)/\
                    (100*self.random_index.loc[
                        self.random_index[
                            self.l["pr_mtrx_ord"]]==len(priority_scores_array),
                        self.l['ri']].reset_index(drop=True)[0])
            except:
                breakpoint()

        if inconsistency_ratio>consistency_threshold:
            msg = "Priority ratings assigned in input table {} "\
                "might be inconsistent. Please revise the ratings, or "\
                "alternatively and with caution, increase the consistency "\
                "threshold.".format(df_key)
            log.error(msg)
            raise ValueError(msg)

        return True

    def calculate(self):
        """Performs the calculation of layer 2 
        and overall priority weights for all
        layer 0 entities.

        Recognizes the placement of each priority
        rating table based on the upper left input
        table label. Assigns the appropriate
        layer labels.

        Check resulting weights for consistency. The 
        priorty weights must sum to one over all
        layer 0 entities for each chosen layer 2 view 
        and overall.

        Returns:

            metric_weights: dictionary
                Dictionary holding the prioritization weights, 
                with the following keys:

                'weights_per_top_layer_entities': pandas dataframe
                    Holds all of the layer 0 entity weights per
                    layer 2 entities.
                    Contains 
                    - a column labeled as layer 0, with the
                    set of layer 0 attributes repeated a number of 
                    times equal the number of unique layer 2 entities
                    - a column with entities of the layer 2 attribute
                    repeated for each entity of the layer 0 attribute
                    - a column with priority weights summing to one for 
                    each layer 2 entity
                    - additional columns holding various layer-specific
                    intermediary scores and weights.

                'final_weights': pandas dataframe
                    Holds the overall layer 0 entity weights.
                    Contains:
                    - a column labeled as the layer 0 
                    attribute, populated with one exhaustive set of 
                    layer 0 attributes
                    - a final priority weight
                    column with values summing to one
                    - additional columns holding various layer-specific
                    intermediary scores and weights.

                'layer_0_label': string
                    Name of the layer 0 attribute, as provided
                    in the input file.

                'layer_1_label': string
                    Name of the layer 1 attribute, as provided
                    in the input file.

                'layer_2_label': string
                    Name of the layer 2 attribute, as provided
                    in the input file.
        """
        priority_weighted_inputs = dict()
        layer_weights = dict()

        for key in self.priority_weight_dfs:

            res = \
                self.calc_priority_score_and_weight(
                    self.priority_weight_dfs[key],
                    key,
                    drop_priority_ratings=True
                    )
            
            priority_weighted_inputs[key] = \
                res['priority_weights']
            
            try: 
                unique_corner_indices += [res['corner_index']]
            except: 
                unique_corner_indices = [res['corner_index']]

            if len(set(unique_corner_indices))!=len(unique_corner_indices):
                msg = 'Duplicate input table corner index found in {}.'\
                    "The priority rating hierarchy is incomplete"\
                    " and needs to be repaired in the input tables.".\
                    format(key)
                log.error(msg)
                raise ValueError(msg)

            if key=='layer_2':
                layer_weights[
                        self.layer_category[2]] = \
                            priority_weighted_inputs[key]
            
            for layer_number in [1, 0]:

                if self.layer_category[
                    layer_number] not in layer_weights.keys():

                    layer_weights[
                        self.layer_category[layer_number]] = dict()

                if 'layer_'+str(layer_number) in key:

                    layer_weights[
                        self.layer_category[layer_number]][key] = \
                        priority_weighted_inputs[key]

                    if 'compiled' not in layer_weights[
                        self.layer_category[layer_number]].keys():
                        
                        layer_weights[
                        self.layer_category[layer_number]]['compiled'] = \
                            priority_weighted_inputs[key]

                    else:
                        layer_weights[
                        self.layer_category[layer_number]]['compiled'] = \
                            pd.concat([layer_weights[
                        self.layer_category[layer_number]]['compiled'],
                            priority_weighted_inputs[key]], axis = 0)

        # layer 0 weights per each entity in layer 1
        weights_per_top_layer_entities = layer_weights[
            self.layer_category[0]
        ]['compiled'].merge(
            layer_weights[self.layer_category[1]]['compiled'], how = 'left', 
            on=[self.layer_category[2], self.layer_category[1]])

        weights_per_top_layer_entities[self.l["pr_wgt"]] = \
            weights_per_top_layer_entities[
                self.layer_category[0] + " " + self.l["pr_wgt"]] * \
            weights_per_top_layer_entities[
                self.layer_category[1] + " " + self.l["pr_wgt"]]       

        # final layer 0 weights (considering both layer 1 and layer 2 opinions)
        final_weights = weights_per_top_layer_entities.merge(
            layer_weights[self.layer_category[2]], how = 'left', 
            on=[self.layer_category[2]]
            )

        final_weights[self.l["final"] + " " + self.l["pr_wgt"]] = \
            final_weights[self.l["pr_wgt"]] * \
            final_weights[self.layer_category[2] + " " + self.l["pr_wgt"]]

        

        final_weights = final_weights.groupby(
            [self.layer_category[0]]).sum().reset_index()

        final_weights = final_weights.drop(columns=[
            self.layer_category[2],self.layer_category[1]
        ])

        metric_weights = {
            'weights_per_top_layer_entities': weights_per_top_layer_entities,
            'final_weights': final_weights,
            'layer_0_label': self.layer_category[0],
            'layer_1_label': self.layer_category[1],
            'layer_2_label': self.layer_category[2],
        }

        if not np.all(np.all(
            weights_per_top_layer_entities.groupby(
                self.layer_category[2]).sum()[
                    self.l["pr_wgt"]].values) ==np. array([1.,1.])):
                msg = "Priority weights do not sum to 1 for each top level category."\
                    " Please double check inputs."
                log.error(msg)
                raise Exception(msg)

        if not final_weights[
            self.l["final"] + " " + self.l["pr_wgt"]].sum().round(5)==1.:
                msg = "Final priority weights do not sum to 1. Please double-check inputs."
                log.error(msg)
                raise Exception(msg)

        return metric_weights

    def plot_weights(self):
        """Plotting capability custom taylored to represent
        the prioritization weights, for example per layer 2 
        entities, or overall.
        """
        # *mg likely the same as plotting scores
        # per standpoint stack bar metric group
        # per standpoint stack bar metric

        # final weights

        pass