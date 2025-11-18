import unittest

import numpy as np

from useckit.tests.test_utils import make_some_intelligent_noise
from useckit.util.dataset import Dataset
from useckit.util.dataset_windowsliced import WindowslicedDataset


class TestUseckit(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.x_train, self.y_train = make_some_intelligent_noise(labels=3, shape=(15, 10, 1))
        self.x_val, self.y_val = make_some_intelligent_noise(labels=3, shape=(15, 10, 1))
        self.x_test, self.y_test = make_some_intelligent_noise(labels=3, shape=(15, 10, 1))

    def test_dataset_initialization_train(self):
        exception_thrown = False
        try:
            data = Dataset(trainset_data=self.x_train,
                           trainset_labels=self.y_train)
        except ValueError:
            exception_thrown = True
        assert exception_thrown

    def test_dataset_initialization_trainval(self):
        data = Dataset(trainset_data=self.x_train,
                       trainset_labels=self.y_train,
                       validationset_data=self.x_val,
                       validationset_labels=self.y_val)
        return data

    def test_dataset_initialization_trainvalenroll(self):
        data = Dataset(trainset_data=self.x_train,
                       trainset_labels=self.y_train,
                       validationset_data=self.x_val,
                       validationset_labels=self.y_val,
                       testset_enrollment_data=self.x_test,
                       testset_enrollment_labels=self.y_test)
        return data

    def test_dataset_initialization_trainvalenrolltest(self):
        data = Dataset(trainset_data=self.x_train,
                       trainset_labels=self.y_train,
                       validationset_data=self.x_val,
                       validationset_labels=self.y_val,
                       testset_enrollment_data=self.x_test,
                       testset_enrollment_labels=self.y_test,
                       testset_matching_data=self.x_test,
                       testset_matching_labels=self.y_test)
        return data

    def test_dataset_initialization_traintest(self):
        data = Dataset(trainset_data=self.x_train,
                       trainset_labels=self.y_train,
                       testset_enrollment_data=self.x_test,
                       testset_enrollment_labels=self.y_test)
        return data

    def test_slicing(self):
        input_data, input_label = make_some_intelligent_noise(labels=3, shape=(15, 10, 1))
        data = WindowslicedDataset(window_slicing_size=4,
                                   window_slicing_stride=2,
                                   trainset_data=input_data,
                                   trainset_labels=input_label,
                                   testset_enrollment_data=input_data,
                                   testset_enrollment_labels=input_label,
                                   testset_matching_data=input_data,
                                   testset_matching_labels=input_label
                                   )
        assert data.trainset_data.shape == data.validationset_data.shape == data.testset_enrollment_data.shape == \
               data.testset_matching_data.shape == (60, 4, 1)
        assert data.trainset_labels.shape == data.validationset_labels.shape == \
               data.testset_enrollment_labels.shape == data.testset_matching_labels.shape == (60,)
        slicedsample_origin_target = np.array([[i, i, i, i] for i in range(15)], dtype=int).flatten()
        assert np.array_equal(data.trainset_slicedsample_origin, data.validationset_slicedsample_origin) and \
               np.array_equal(data.validationset_slicedsample_origin, data.testset_enrollment_slicedsample_origin) and \
               np.array_equal(data.testset_enrollment_slicedsample_origin,
                              data.testset_matching_slicedsample_origin) and \
               np.array_equal(data.testset_matching_slicedsample_origin, slicedsample_origin_target)

        for i in range(15):
            assert np.array_equal(data.trainset_sliceorigin_mask[i], (slicedsample_origin_target == i))


if __name__ == '__main__':
    unittest.main()
