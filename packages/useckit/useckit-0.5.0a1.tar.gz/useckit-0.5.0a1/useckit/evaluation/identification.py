import os
from abc import ABC, abstractmethod

import numpy as np
from sklearn.metrics import confusion_matrix
from natsort import natsorted

from useckit.util.dataset import Dataset
from useckit.util.dataset_windowsliced import WindowslicedDataset
from useckit.util.plotting import plot_confusion_matrix
from useckit.util.utils import create_classification_report


class IdentificationModel(ABC):

    @abstractmethod
    def identify(self, samples: np.ndarray) -> np.ndarray:
        pass


def perform_identification_evaluation(identification_model: IdentificationModel, dataset: Dataset, output_folder: str):
    filename_prefix = 'windowslices_' if isinstance(dataset, WindowslicedDataset) else ''

    testset_data, testset_labels = dataset.testset_matching_data, dataset.testset_matching_labels

    model_predictions = identification_model.identify(testset_data)
    true_labels_reverse_transformed = dataset.reverse_label_transform(testset_labels)

    _output_results(model_predictions, true_labels_reverse_transformed, output_folder, dataset, filename_prefix)

    if isinstance(dataset, WindowslicedDataset):
        _perform_identification_evaluation_windowsliced(model_predictions, true_labels_reverse_transformed,
                                                        dataset, output_folder)


def _perform_identification_evaluation_windowsliced(model_prediction: np.ndarray,
                                                    true_labels_reverse_transformed: np.ndarray,
                                                    dataset: WindowslicedDataset, output_folder: str):
    sample_predictions, sample_labels = \
        dataset.apply_voting_for_testset_matching_slices(model_prediction, true_labels_reverse_transformed)
    _output_results(sample_predictions, sample_labels, output_folder, dataset, '')


def _output_results(predictions: np.ndarray, true_labels: np.ndarray, output_folder: str, dataset: Dataset,
                    filename_prefix: str = ''):
    confusion_matrix_filename = filename_prefix + 'confusion-matrix.pdf'
    classification_report_filename = filename_prefix + 'classification-report'

    matching_labels = np.concatenate((predictions, true_labels,), dtype=str)
    matching_labels = np.unique(matching_labels)
    matching_labels = np.array(natsorted(matching_labels))
    rejection_label_present = dataset.reject_label in matching_labels
    if rejection_label_present:
        matching_labels = matching_labels[matching_labels != dataset.reject_label]
        matching_labels = np.concatenate((matching_labels, np.array([dataset.reject_label]),), dtype=str)

    cm = confusion_matrix(true_labels, predictions, labels=matching_labels)
    os.makedirs(output_folder, exist_ok=True)
    create_classification_report(cm, matching_labels, output_folder, classification_report_filename)
    plot_confusion_matrix(cm, matching_labels, output_folder,
                          normalize=False, filename=confusion_matrix_filename)
