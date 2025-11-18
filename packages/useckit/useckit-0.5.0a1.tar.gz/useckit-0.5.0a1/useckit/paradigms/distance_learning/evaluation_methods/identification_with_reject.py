import numpy as np

from ._equal_error_thresholding_method import EqualErrorThresholding
from ._sample_broadcasting import _create_all_distance_pairs
from .distance_evaluation_method_base import DistanceBaseEvaluationMethod, BaseThresholdingMethod
from ..prediction_models.distance_prediction_model_base import DistanceBasePredictionModel
from ....evaluation.identification_with_reject import IdentificationOrRejectModel, \
    perform_identification_or_reject_evaluation
from ....util.dataset import Dataset
from ....util.utils import contrastive_make_pairs


class DistanceIdentificationOrRejectModel(IdentificationOrRejectModel):

    def __init__(self,
                 distance_metric: DistanceBasePredictionModel,
                 enrollment_samples: np.ndarray,
                 enrollment_labels: np.ndarray,
                 rejection_threshold: float,
                 dataset: Dataset,
                 tradeoff_computation_speed_for_memory: bool):
        self.distance_metric = distance_metric
        self.enrolment_samples = enrollment_samples
        self.enrollment_labels = enrollment_labels
        self.rejection_threshold = rejection_threshold
        self.dataset = dataset
        self.tradeoff_computation_speed_for_memory = tradeoff_computation_speed_for_memory

    def identify_or_reject(self, samples: np.ndarray):
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
            if min_median_distance >= self.rejection_threshold:
                result[index] = -1
            else:
                result[index] = min_median_label
        return self.dataset.reverse_label_transform(result)


class IdentificationWithReject(DistanceBaseEvaluationMethod):

    def __init__(self,
                 output_dir: str = "evaluation_identification_with_reject",
                 threshold_method: BaseThresholdingMethod = None,
                 tradeoff_computation_speed_for_memory: bool = True):
        super().__init__(output_dir)
        self.threshold_method = threshold_method
        self.tradeoff_computation_speed_for_memory = tradeoff_computation_speed_for_memory

    def evaluate(self, dataset: Dataset, prediction_model: DistanceBasePredictionModel, **kwargs):
        if self.threshold_method is None:
            self.threshold_method = EqualErrorThresholding(prediction_model, contrastive_make_pairs, self.output_dir)

        threshold = self.threshold_method.compute_threshold(dataset.testset_enrollment_data,
                                                            dataset.testset_enrollment_labels)
        ident_or_reject_model = DistanceIdentificationOrRejectModel(prediction_model,
                                                                    dataset.testset_enrollment_data,
                                                                    dataset.testset_enrollment_labels,
                                                                    threshold,
                                                                    dataset, self.tradeoff_computation_speed_for_memory)
        perform_identification_or_reject_evaluation(ident_or_reject_model, dataset, self.output_dir)
