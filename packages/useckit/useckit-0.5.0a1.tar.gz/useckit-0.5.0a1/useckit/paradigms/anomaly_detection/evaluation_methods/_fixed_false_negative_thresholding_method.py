import math
import math
import os

import numpy as np
import pandas as pd

from useckit.paradigms.anomaly_detection.evaluation_methods.anomaly_evaluation_method_base import \
    BaseThresholdingMethod
from useckit.paradigms.anomaly_detection.prediction_models.anomaly_prediction_model_base import \
    AnomalyBasePredictionModel


class FixedFalseNegativeThresholdingMethod(BaseThresholdingMethod):

    def __init__(self, anomaly_detection_model: AnomalyBasePredictionModel, output_dir: str,
                 target_false_negative_rate=0.05):
        self.target_false_negative_rate = target_false_negative_rate
        self.anomaly_detection_model = anomaly_detection_model
        self.output_dir = output_dir

    def compute_thresholds(self, enrollment_data: np.ndarray, enrollment_labels: np.ndarray) -> [float]:
        result = dict()
        prediction, labels = self.anomaly_detection_model.predict(enrollment_data)

        columns = [f'{i}\'th model prediction' for i in list(range(len(prediction)))]
        pred_df = pd.DataFrame(prediction.transpose(), columns=columns)
        pred_df.to_csv(os.path.join(self.output_dir, 'enrollment_data_raw_predictions.csv'))

        for user_index, anomaly_predictions in zip(labels, prediction):
            same_user_predictions = anomaly_predictions[enrollment_labels == user_index]
            same_user_predictions = np.sort(same_user_predictions)
            threshold_cutoff_index = len(same_user_predictions) * (1 - self.target_false_negative_rate)
            threshold_cutoff_index = math.floor(threshold_cutoff_index)
            result[user_index] = same_user_predictions[threshold_cutoff_index]

        result_copy = dict()
        for key, value in result.items():
            result_copy[str(key)] = [value]  # need to cast keys to str for pandas...
        result_df = pd.DataFrame(result_copy)
        result_df.to_csv(os.path.join(self.output_dir, 'model_thresholds.csv'))
        return result
