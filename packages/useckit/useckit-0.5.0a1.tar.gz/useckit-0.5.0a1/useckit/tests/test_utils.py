import numpy as np

from useckit.util.dataset import Dataset
from useckit.util.dataset_windowsliced import WindowslicedDataset
from useckit.util.utils import make_some_intelligent_noise as make_some_intelligent_noise_util


def make_some_intelligent_noise(labels: int = 4, shape: tuple = (100, 100, 100), noisiness: float = 0.1):
    biases = np.array([i / labels for i in range(labels)]) + (1 / (2 * labels))
    x = []
    y = []
    shape = list(shape)
    shape[0] = int(shape[0] / labels)
    i = 0
    for b in biases:
        x.extend(np.random.normal(b, noisiness, shape))
        y.extend(np.ones((shape[0],)) * i)
        i += 1
    x = np.array(x)
    y = np.array(y)
    x = np.clip(x, -1, 1)
    return x, y


def make_dataset(*args, **kwargs):
    x_train, y_train, x_val, y_val, x_test_enroll, y_test_enroll, x_test_match, y_test_match = \
        _make_data(*args, **kwargs)
    return Dataset(x_train, y_train, x_val, y_val, x_test_enroll, y_test_enroll, x_test_match, y_test_match)


def make_windowsliced_dataset(window_slicing_stride: int, window_slicing_size: int, *args, **kwargs):
    x_train, y_train, x_val, y_val, x_test_enroll, y_test_enroll, x_test_match, y_test_match = \
        _make_data(*args, **kwargs)
    return WindowslicedDataset(window_slicing_stride, window_slicing_size, x_train, y_train, x_val, y_val,
                               x_test_enroll, y_test_enroll, x_test_match, y_test_match)


def _make_data(*args, **kwargs):
    if 'labels' not in kwargs:
        kwargs['labels'] = 6
    num_reject_labels = int(kwargs['labels'] / 3)
    reject_labels = []
    reject_label_masks = []

    x_train, y_train = make_some_intelligent_noise_util(*args, **kwargs)
    x_val, y_val = make_some_intelligent_noise_util(*args, **kwargs)
    x_test_enroll, y_test_enroll = make_some_intelligent_noise_util(*args, **kwargs)

    # remove the middle most labels to not have edge labels mess with random forests
    start_index = int(len(y_train) - num_reject_labels - (len(y_train) - num_reject_labels) / 2)
    for i in range(start_index, start_index + num_reject_labels, 1):
        if y_train[-i - 1] not in reject_labels:
            reject_labels.append(y_train[-i - 1])
            reject_label_masks.append(y_train == y_train[-i - 1])

    total_reject_label_mask = reject_label_masks[0]
    for mask in reject_label_masks:
        total_reject_label_mask = np.logical_or(total_reject_label_mask, mask)

    total_reject_label_mask = np.invert(total_reject_label_mask)

    x_train = x_train[total_reject_label_mask]
    y_train = y_train[total_reject_label_mask]
    x_val = x_val[total_reject_label_mask]
    y_val = y_val[total_reject_label_mask]
    x_test_enroll = x_test_enroll[total_reject_label_mask]
    y_test_enroll = y_test_enroll[total_reject_label_mask]

    x_test_match, y_test_match = make_some_intelligent_noise_util(*args, **kwargs)
    return x_train, y_train, x_val, y_val, x_test_enroll, y_test_enroll, x_test_match, y_test_match
