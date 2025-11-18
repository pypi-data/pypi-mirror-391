import os
from abc import ABC, abstractmethod

import numpy as np
from sklearn.metrics import confusion_matrix

from useckit.util.dataset import Dataset
from useckit.util.dataset_windowsliced import WindowslicedDataset
from useckit.util.plotting import plot_confusion_matrix
from useckit.util.utils import create_classification_report


class VerificationModel(ABC):

    @abstractmethod
    def verify(self, samples: np.ndarray, identity_claims: np.ndarray) -> np.ndarray:
        # identity_claims should be a 1-dim array of ints corresponding to the number transformed by the dataset used
        # in training. It should have the same size as the first dimension of samples
        # the result is a boolean array of same size as identity_claims
        pass


def perform_verification_evaluation(verification_model: VerificationModel, dataset: Dataset, output_folder: str):
    filename_prefix = 'windowslices-' if isinstance(dataset, WindowslicedDataset) else ''
    _verify_data_labels(dataset, verification_model, output_folder, filename_prefix, reverse_windowslicing=False)

    if isinstance(dataset, WindowslicedDataset):
        _verify_data_labels(dataset, verification_model, output_folder, '', reverse_windowslicing=True)


def _verify_data_labels(dataset: Dataset, verification_model: VerificationModel, output_folder: str,
                        filename_prefix: str, reverse_windowslicing: bool):
    testset_data, testset_labels = dataset.testset_matching_data, dataset.testset_matching_labels
    enrollment_labels = set(dataset.testset_enrollment_labels)
    if reverse_windowslicing:
        assert isinstance(dataset, WindowslicedDataset)
        number_verifications = len(dataset.testset_matching_sliceorigin_mask)
    else:
        number_verifications = len(testset_data)

    total_ground_truth = np.zeros(len(enrollment_labels) * number_verifications, dtype=bool)
    total_predictions = np.zeros(len(enrollment_labels) * number_verifications, dtype=bool)
    total_index = 0

    # make all predictions in one call to prediction, then later use the label_claims_array to split it back into the
    # predictions for the individual enrolment labels
    testset_data_array = []
    label_claims_array = []
    for enrolment_label in enrollment_labels:
        label_claims: np.ndarray = np.ones(shape=testset_labels.shape, dtype=int) * enrolment_label
        testset_data_array.append(testset_data)
        label_claims_array.append(label_claims)

    testset_data_array = np.concatenate(testset_data_array)
    label_claims_array = np.concatenate(label_claims_array)
    predictions_array = verification_model.verify(testset_data_array, label_claims_array)

    for enrolment_label in enrollment_labels:
        testset_labels: np.ndarray = testset_labels
        label_claims: np.ndarray = np.ones(shape=testset_labels.shape, dtype=int) * enrolment_label

        if reverse_windowslicing:
            ground_truth_slices: np.ndarray = testset_labels == label_claims
            predictions_slices: np.ndarray = predictions_array[label_claims_array == enrolment_label]
            predictions, ground_truth = dataset.apply_voting_for_testset_matching_slices(predictions_slices,
                                                                                         ground_truth_slices)
        else:
            ground_truth: np.ndarray = testset_labels == label_claims
            predictions: np.ndarray = predictions_array[label_claims_array == enrolment_label]

        total_ground_truth[total_index:total_index + len(ground_truth)] = ground_truth
        total_predictions[total_index:total_index + len(predictions)] = predictions
        total_index += len(ground_truth)

        label_reverse_transformed = str(dataset.reverse_label_transform(np.array([enrolment_label]))[0])
        label_sub_dir = os.path.join(output_folder, label_reverse_transformed)
        os.makedirs(label_sub_dir, exist_ok=True)

        _output_results(predictions, ground_truth, label_sub_dir, f'{filename_prefix}{label_reverse_transformed}-')

    _output_results(total_predictions, total_ground_truth, output_folder, f'{filename_prefix}total-')


def _output_results(predictions: np.ndarray, ground_truth: np.ndarray, output_folder: str,
                    filename_prefix: str = ''):
    os.makedirs(output_folder, exist_ok=True)
    cm = confusion_matrix(ground_truth, predictions, labels=[True, False])
    labels = ['accept', 'reject']
    create_classification_report(cm, labels, output_folder, filename=f'{filename_prefix}classification-report')
    plot_confusion_matrix(cm, target_names=labels, path=output_folder, normalize=False,
                          filename=f'{filename_prefix}confusion-matrix.pdf')
