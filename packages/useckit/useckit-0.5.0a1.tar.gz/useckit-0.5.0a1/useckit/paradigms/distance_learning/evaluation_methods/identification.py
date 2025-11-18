import numpy as np

from ._sample_broadcasting import _create_all_distance_pairs
from .distance_evaluation_method_base import DistanceBaseEvaluationMethod
from ..prediction_models.distance_prediction_model_base import DistanceBasePredictionModel
from ....evaluation.identification import IdentificationModel, perform_identification_evaluation
from ....util.dataset import Dataset


class DistanceIdentificationModel(IdentificationModel):

    def __init__(self,
                 distance_metric: DistanceBasePredictionModel,
                 enrollment_samples: np.ndarray,
                 enrollment_labels: np.ndarray,
                 dataset: Dataset,
                 tradeoff_computation_speed_for_memory: bool):
        self.distance_metric = distance_metric
        self.enrolment_samples = enrollment_samples
        self.enrollment_labels = enrollment_labels
        self.dataset = dataset
        self.tradeoff_computation_speed_for_memory = tradeoff_computation_speed_for_memory

    def identify(self, samples: np.ndarray):
        result = np.zeros(shape=(len(samples),), dtype=int)

        distances, sample_indices = _create_all_distance_pairs(samples, self.enrolment_samples, self.distance_metric,
                                                               self.tradeoff_computation_speed_for_memory)

        for index, sample in enumerate(samples):
            index_mask = sample_indices == index
            distances_to_enrollment = distances[index_mask]  # These are all the predicted distances of this
            # loop-repetition's sample to all enrolment samples. They are ordered by the order that the
            # self.enrolment_samples array imposes

            min_median_distance = 1e1000  # just a stupidly large number
            min_median_label = 0  # just any number
            for enrol_label in np.unique(self.enrollment_labels):
                distances_to_enrol_label = distances_to_enrollment[self.enrollment_labels == enrol_label]  # These are
                # all the distances to the enrolment samples belonging to enrol_label
                if len(distances_to_enrol_label) <= 2:
                    median = min(distances_to_enrol_label)  # don't find the value closest to the median for just two
                    # values, but pick the smaller one
                else:
                    median_dist_index = \
                        np.nonzero(
                            distances_to_enrol_label == np.percentile(distances_to_enrol_label, 50,
                                                                      method='closest_observation')
                        )[0][0]  # This abomination finds the index of the closest value in the array to the median
                    median = distances_to_enrol_label[median_dist_index]  # median of distances to the enrolment samples
                    # belonging to enrol_label
                if median < min_median_distance:
                    min_median_distance = median
                    min_median_label = enrol_label

            result[index] = min_median_label
        return self.dataset.reverse_label_transform(result)


class IdentificationOnly(DistanceBaseEvaluationMethod):

    def __init__(self,
                 output_dir: str = "evaluation_identification",
                 tradeoff_computation_speed_for_memory: bool = True):
        super().__init__(output_dir)
        self.tradeoff_computation_speed_for_memory = tradeoff_computation_speed_for_memory

    def evaluate(self, dataset: Dataset, prediction_model: DistanceBasePredictionModel, **kwargs):
        perform_identification_evaluation(DistanceIdentificationModel(prediction_model,
                                                                      dataset.testset_enrollment_data,
                                                                      # FIXME # What? Why? This is correct!
                                                                      dataset.testset_enrollment_labels,  # FIXME
                                                                      dataset,
                                                                      self.tradeoff_computation_speed_for_memory),
                                          dataset,
                                          self.output_dir)
