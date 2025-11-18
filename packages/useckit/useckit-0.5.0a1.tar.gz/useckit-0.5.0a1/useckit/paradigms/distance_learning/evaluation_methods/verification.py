import numpy as np

from ._equal_error_thresholding_method import EqualErrorThresholding
from .distance_evaluation_method_base import DistanceBaseEvaluationMethod, BaseThresholdingMethod
from ..prediction_models.distance_prediction_model_base import DistanceBasePredictionModel
from ....evaluation.verification import VerificationModel, perform_verification_evaluation
from ....util.dataset import Dataset
from ....util.utils import contrastive_make_pairs


class DistanceVerificationModel(VerificationModel):

    def __init__(self,
                 distance_metric: DistanceBasePredictionModel,
                 enrollment_samples: np.ndarray,
                 enrollment_labels: np.ndarray,
                 rejection_threshold: float,
                 tradeoff_computation_speed_for_memory: bool):
        self.distance_metric = distance_metric
        self.enrollment_samples = enrollment_samples
        self.enrolment_labels = enrollment_labels
        self.rejection_threshold = rejection_threshold
        self.tradeoff_computation_speed_for_memory = tradeoff_computation_speed_for_memory

    def _create_distance_pairs_broadcasting(self, samples: np.ndarray, identity_claims: np.ndarray):
        sample_broadcast_array_shape = [len(samples) * len(self.enrollment_samples)]  # this is, in actuality, too big,
        # so the arrays need to be sliced down to size later
        for s in samples.shape[1:]:  # each other dimension needs to be equivalent to a single sample
            sample_broadcast_array_shape.append(s)
        sample_broadcast_array = np.zeros(shape=tuple(sample_broadcast_array_shape),
                                          dtype=self.enrollment_samples.dtype)
        enrolment_broadcast_array = np.zeros(shape=tuple(sample_broadcast_array_shape),
                                             dtype=self.enrollment_samples.dtype)
        sample_original_indices = np.zeros(
            shape=(len(samples) * len(self.enrollment_samples),))  # this will contain the original
        # indices of the broadcasted samples

        broadcast_index = 0
        for index, sample in enumerate(samples):
            i_claim = identity_claims[index]  # identity belonging to the one sample
            i_enrollment_samples = self.enrollment_samples[self.enrolment_labels == i_claim]  # all enrollment
            # samples of the claimed identity
            if len(i_enrollment_samples) <= 0:
                raise ValueError(f"Claimed identity {identity_claims[index]} was not part of the enrolled "
                                 f"identities {self.enrolment_labels}!")
            sample_broadcast = np.broadcast_to(sample, shape=i_enrollment_samples.shape)
            indices = np.ones(shape=(len(i_enrollment_samples),)) * index

            from_i = broadcast_index
            to_i = broadcast_index + len(i_enrollment_samples)

            sample_broadcast_array[from_i:to_i] = sample_broadcast
            enrolment_broadcast_array[from_i:to_i] = i_enrollment_samples
            sample_original_indices[from_i:to_i] = indices

            broadcast_index = to_i

        sample_broadcast_array = sample_broadcast_array[0:broadcast_index]
        enrolment_broadcast_array = enrolment_broadcast_array[0:broadcast_index]
        sample_original_indices = sample_original_indices[0:broadcast_index]  # broadcast_index points to the actual
        # length of this array
        distances = self.distance_metric.predict(sample_broadcast_array, enrolment_broadcast_array)

        return distances, sample_original_indices

    def _create_distance_pairs_iteration(self, samples: np.ndarray, identity_claims: np.ndarray):
        distances = np.zeros(
            shape=(len(samples) * len(self.enrollment_samples),))
        sample_original_indices = np.zeros(
            shape=(len(samples) * len(self.enrollment_samples),), dtype=int)  # this will contain the original
        # indices of the broadcasted samples. Both of these arrays are way too big and need to be sliced down to size
        # later

        broadcast_index = 0
        for index, sample in enumerate(samples):
            i_claim = identity_claims[index]  # identity claim belonging to the one sample
            i_enrollment_samples = self.enrollment_samples[self.enrolment_labels == i_claim]  # all enrollment
            # samples of the claimed identity
            if len(i_enrollment_samples) <= 0:
                raise ValueError(f"Claimed identity {identity_claims[index]} was not part of the enrolled "
                                 f"identities {self.enrolment_labels}!")
            sample_broadcast = np.broadcast_to(sample, shape=i_enrollment_samples.shape)
            indices = np.ones(shape=(len(i_enrollment_samples),)) * index

            from_i = broadcast_index
            to_i = broadcast_index + len(i_enrollment_samples)

            sample_distances = self.distance_metric.predict(sample_broadcast, i_enrollment_samples)
            distances[from_i:to_i] = sample_distances
            sample_original_indices[from_i:to_i] = indices

            broadcast_index = to_i

        distances = distances[0:broadcast_index]
        sample_original_indices = sample_original_indices[0:broadcast_index]  # broadcast_index points to the actual
        # length of this array
        return distances, sample_original_indices

    def verify(self, samples: np.ndarray, identity_claims: np.ndarray) -> bool:
        result = np.zeros(shape=(len(samples),))
        assert len(samples) == len(identity_claims)

        if self.tradeoff_computation_speed_for_memory:
            distances, sample_original_indices = self._create_distance_pairs_iteration(samples, identity_claims)
        else:
            distances, sample_original_indices = self._create_distance_pairs_broadcasting(samples, identity_claims)

        for index, sample in enumerate(samples):
            index_mask = sample_original_indices == index
            distances_to_enrollment = distances[index_mask]

            median_dist = np.median(distances_to_enrollment)
            result[index] = 1 if median_dist < self.rejection_threshold else 0
        return result == 1  # dirty transform to bool array


class Verification(DistanceBaseEvaluationMethod):

    def __init__(self,
                 output_dir: str = "evaluation_verification",
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
        verification_model = DistanceVerificationModel(prediction_model,
                                                       dataset.testset_enrollment_data,
                                                       dataset.testset_enrollment_labels,
                                                       threshold,
                                                       self.tradeoff_computation_speed_for_memory)
        perform_verification_evaluation(verification_model, dataset, self.output_dir)
