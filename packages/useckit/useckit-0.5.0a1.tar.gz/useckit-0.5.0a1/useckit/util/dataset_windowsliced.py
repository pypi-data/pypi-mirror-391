import sys
from collections import Counter
from typing import Union, Callable, Tuple

import numpy as np

from useckit.util.dataset import Dataset
from useckit.util.utils import _unison_shuffle_np_arrays_3


def _majority_vote_over(array: np.ndarray):
    if array.size == 0:  # Check if the array is empty
        return None
    c = Counter(array)
    return c.most_common(1)[0][0]  # returns the actual most common element


class WindowslicedDataset(Dataset):
    def __init__(self,
                 window_slicing_stride: int,
                 window_slicing_size: int,
                 trainset_data: Union[list, np.ndarray],
                 trainset_labels: Union[list, np.ndarray],
                 validationset_data: Union[list, np.ndarray] = None,
                 validationset_labels: Union[list, np.ndarray] = None,
                 testset_enrollment_data: Union[list, np.ndarray] = None,
                 testset_enrollment_labels: Union[list, np.ndarray] = None,
                 testset_matching_data: Union[list, np.ndarray] = None,
                 testset_matching_labels: Union[list, np.ndarray] = None,
                 normalization_check: bool = False,
                 shuffle_window_slices: bool = False,
                 voting_function: Callable[[np.ndarray], object] = _majority_vote_over,
                 ):
        self.voting_function = voting_function

        self.trainset_data: np.ndarray = trainset_data  # type hints here are just for IDE support
        self.trainset_labels: np.ndarray = trainset_labels
        self.validationset_data: np.ndarray = validationset_data
        self.validationset_labels: np.ndarray = validationset_labels
        self.testset_enrollment_data: np.ndarray = testset_enrollment_data
        self.testset_enrollment_labels: np.ndarray = testset_enrollment_labels
        self.testset_matching_data: np.ndarray = testset_matching_data
        self.testset_matching_labels: np.ndarray = testset_matching_labels
        self._setup_missing_sets()  # applying the replacement rules for missing sets in this way seems a little

        # convoluted but should be easier to maintain if the replacement rules change in the future

        def _len_or_none(data: np.ndarray):
            return None if data is None else len(data)

        trainset_origin_len = _len_or_none(self.trainset_data)
        validationset_origin_len = _len_or_none(self.validationset_data)
        testset_enrollment_origin_len = _len_or_none(self.testset_enrollment_data)
        testset_matching_origin_len = _len_or_none(self.testset_matching_data)

        trainset_data, trainset_labels, self.trainset_slicedsample_origin = self._transform_for_windowslicing(
            self.trainset_data, self.trainset_labels, window_slicing_stride, window_slicing_size, shuffle_window_slices)

        validationset_data, validationset_labels, self.validationset_slicedsample_origin = \
            self._transform_for_windowslicing(self.validationset_data, self.validationset_labels, window_slicing_stride,
                                              window_slicing_size, shuffle_window_slices)

        testset_enrollment_data, testset_enrollment_labels, self.testset_enrollment_slicedsample_origin = \
            self._transform_for_windowslicing(self.testset_enrollment_data, self.testset_enrollment_labels,
                                              window_slicing_stride, window_slicing_size, shuffle_window_slices)

        testset_matching_data, testset_matching_labels, self.testset_matching_slicedsample_origin = \
            self._transform_for_windowslicing(self.testset_matching_data, self.testset_matching_labels,
                                              window_slicing_stride, window_slicing_size, shuffle_window_slices)

        self._create_origin_masks(trainset_origin_len, validationset_origin_len, testset_enrollment_origin_len,
                                  testset_matching_origin_len)

        super().__init__(trainset_data, trainset_labels, validationset_data, validationset_labels,
                         testset_enrollment_data, testset_enrollment_labels, testset_matching_data,
                         testset_matching_labels, normalization_check)

    def _create_origin_masks(self, trainset_origin_len, validationset_origin_len, testset_enrollment_origin_len,
                             testset_matching_origin_len):
        def _create_origin_mask(origin_len, slicedsample_origin):
            if slicedsample_origin is None:
                return None
            else:
                result_origin_mask = []
                for origin_id in range(origin_len):
                    result_origin_mask.append(slicedsample_origin == origin_id)
                return np.array(result_origin_mask, dtype=bool)

        self.trainset_sliceorigin_mask = _create_origin_mask(trainset_origin_len, self.trainset_slicedsample_origin)
        self.validationset_sliceorigin_mask = _create_origin_mask(validationset_origin_len,
                                                                  self.validationset_slicedsample_origin)
        self.testset_enrollment_sliceorigin_mask = _create_origin_mask(testset_enrollment_origin_len,
                                                                       self.testset_enrollment_slicedsample_origin)
        self.testset_matching_sliceorigin_mask = _create_origin_mask(testset_matching_origin_len,
                                                                     self.testset_matching_slicedsample_origin)

    @staticmethod
    def _transform_for_windowslicing(data: Union[list, np.ndarray],
                                     labels: Union[list, np.ndarray],
                                     window_slicing_stride: int,
                                     window_slicing_size: int,
                                     shuffle_window_slices: bool):
        if data is None:
            return None, None, None

        if not len(data) == len(labels):
            raise ValueError("Critical: data and labels differ in size.")

        ret_sliced_data, ret_sliced_labels, ret_sample_origin_ids = [], [], []

        for origin_id, (sample, label) in enumerate(zip(data, labels)):
            array_slices, label_slices, sample_origin_ids = [], [], []

            lost_samples_cnt, added_cnt = 0, 0

            for step_idx in range(0, len(sample) - window_slicing_size + 1, window_slicing_stride):
                arr = np.array(sample[step_idx:step_idx + window_slicing_size],
                               dtype=float)  # this fails if the resulting array would be ragged

                if not arr.any():
                    pass  # do not append if slice consists only of zero
                else:
                    array_slices.append(arr)
                    label_slices.append(label)
                    sample_origin_ids.append(origin_id)

            for i in range(len(array_slices)):
                if len(array_slices[i]) == window_slicing_size:
                    ret_sliced_data.append(array_slices[i])
                    ret_sliced_labels.append(label_slices[i])
                    ret_sample_origin_ids.append(sample_origin_ids[i])
                    added_cnt += 1
                else:
                    lost_samples_cnt += 1

            if lost_samples_cnt > 0:
                print(f'Warning: during slicing  {lost_samples_cnt} malformed slices needed to be discarded. '
                      f'Check slicing parameters.', file=sys.stderr)

        try:
            ret_sliced_data = np.array(ret_sliced_data, dtype=float)
        except ValueError:
            print("Critical: slicing the data produced slices differing in size.", file=sys.stderr)
            raise

        ret_sliced_labels = np.array(ret_sliced_labels, dtype=str)
        ret_sample_origin_ids = np.array(ret_sample_origin_ids, dtype=int)

        print(f'Info: sliced window data takes up {round(ret_sliced_data.nbytes / 1024 / 1024, 2)}mb.')

        if shuffle_window_slices:
            return _unison_shuffle_np_arrays_3(ret_sliced_data, ret_sliced_labels, ret_sample_origin_ids)
        else:
            return ret_sliced_data, ret_sliced_labels, ret_sample_origin_ids

    def apply_voting_for_testset_matching_slices(self, predictions_slices: np.ndarray,
                                                 ground_truth_slices: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        ground_truth = np.zeros((len(self.testset_matching_sliceorigin_mask),), dtype=ground_truth_slices.dtype)
        predictions = np.zeros((len(self.testset_matching_sliceorigin_mask),), dtype=predictions_slices.dtype)

        for sample_id, sample_mask in enumerate(self.testset_matching_sliceorigin_mask):
            if np.any(sample_mask):
                predictions[sample_id] = self.voting_function(predictions_slices[sample_mask])
                ground_truth[sample_id] = ground_truth_slices[sample_mask][0]  # assuming consistency within slices
            else:
                predictions[sample_id] = None  # Default value for predictions when no slices match
                ground_truth[sample_id] = None  # Default value for ground truth when no slices match

        return predictions, ground_truth
