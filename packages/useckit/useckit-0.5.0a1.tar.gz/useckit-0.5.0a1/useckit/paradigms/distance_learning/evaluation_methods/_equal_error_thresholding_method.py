import os
from typing import Callable, Tuple

import numpy as np
import pandas as pd

from useckit.paradigms.distance_learning.evaluation_methods.distance_evaluation_method_base import \
    BaseThresholdingMethod
from useckit.paradigms.distance_learning.prediction_models.distance_prediction_model_base import \
    DistanceBasePredictionModel
from useckit.util.plotting import plot_roc_curve


class EqualErrorThresholding(BaseThresholdingMethod):

    def __init__(self,
                 distance_metric: DistanceBasePredictionModel,
                 pair_function: Callable[[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
                 output_dir: str):
        self.distance_metric = distance_metric
        self.pair_function = pair_function
        self.output_dir = output_dir

    def compute_threshold(self, enrollment_data: np.ndarray, enrollment_labels: np.ndarray) -> float:
        pairs_test, distances_in_pairs = self.pair_function(enrollment_data,
                                                            enrollment_labels)

        # split test pairs
        x_test_1 = pairs_test[:, 0]
        x_test_2 = pairs_test[:, 1]

        raw_distance_predictions = self.distance_metric.predict(x_test_1, x_test_2)
        raw_distance_predictions = np.squeeze(raw_distance_predictions)

        accept_reject_in_pairs = (distances_in_pairs * -1) + 1
        accept_reject_predictions = (raw_distance_predictions * -1) + 1

        fpr, tpr, threshold_roc, precision, recall, threshold_prc = \
            plot_roc_curve(accept_reject_in_pairs, accept_reject_predictions, self.output_dir)

        fnr = 1 - tpr
        eer_threshold = threshold_roc[np.nanargmin(np.absolute((fnr - fpr)))]

        # rates closest to the equal error rate among all possible thresholds
        eer_1 = fpr[np.nanargmin(np.absolute((fnr - fpr)))]
        eer_2 = fnr[np.nanargmin(np.absolute((fnr - fpr)))]

        roc_curve_dict = {'distance threshold': threshold_roc, 'false positive rate': fpr, 'true positive rate': tpr}
        prc_curve_dict = {'distance threshold': threshold_prc, 'precision': precision, 'recall': recall}
        raw_dict = {'raw distance predicted': raw_distance_predictions,
                    'same user in input pair': accept_reject_in_pairs}

        pd.DataFrame(roc_curve_dict).to_csv(os.path.join(self.output_dir, 'roc_curve_table.csv'))
        pd.DataFrame(prc_curve_dict).to_csv(os.path.join(self.output_dir, 'prc_curve_table.csv'))
        pd.DataFrame(raw_dict).to_csv(os.path.join(self.output_dir, 'raw_predictions.csv'))

        result = (eer_threshold * -1) + 1  # the result eer_threshold needs to be re-transformed into a distance, just
        # like the raw_distance_predictions were transformed into accept_reject_predictions earlier

        with open(os.path.join(self.output_dir, 'equal_error_rate.txt'), 'w') as f:
            f.write(f'Equal Error Rate candidates: \n{eer_1}\n{eer_2}\n\nEqual Error Rate distance: \n{result}')

        return result
