import re
import unittest
import os
import shutil
import urllib.request
import hashlib
import subprocess
from glob import glob
from statistics import median

import numpy as np
import pandas as pd
import tensorflow as tf
from joblib import Parallel, delayed
from keras import Sequential
from keras.src.layers import Dense
from keras.src.optimizers import Adam
from keras.src.utils import pad_sequences
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelBinarizer

import useckit

class TestModelBuilder_DIST(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.unittest_execution_counter = 1
        # make train pairs
        self.pairs_train, self.labels_train = self.make_pairs(x_train, y_train)

        # make validation pairs
        self.pairs_val, self.labels_val = self.make_pairs(x_val, y_val)

        # make test pairs
        self.pairs_test, self.labels_test = self.make_pairs(x_test, y_test)

    @classmethod
    def prepare_mnist_dataset(self):
        # Set custom save path
        save_path = "../mnist_data"
        os.makedirs(save_path, exist_ok=True)

        # Load MNIST dataset
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

        # Save dataset to custom location
        np.save(os.path.join(save_path, "x_train.npy"), x_train)
        np.save(os.path.join(save_path, "y_train.npy"), y_train)
        np.save(os.path.join(save_path, "x_test.npy"), x_test)
        np.save(os.path.join(save_path, "y_test.npy"), y_test)

        print("MNIST dataset saved successfully!")

    def make_pairs(x, y):
        """Creates a tuple containing image pairs with corresponding label.

        Arguments:
            x: List containing images, each index in this list corresponds to one image.
            y: List containing labels, each label with datatype of `int`.

        Returns:
            Tuple containing two numpy arrays as (pairs_of_samples, labels),
            where pairs_of_samples' shape is (2len(x), 2,n_features_dims) and
            labels are a binary array of shape (2len(x)).
        """

        num_classes = max(y) + 1
        digit_indices = [np.where(y == i)[0] for i in range(num_classes)]

        pairs = []
        labels = []

        for idx1 in range(len(x)):
            # add a matching example
            x1 = x[idx1]
            label1 = y[idx1]
            idx2 = random.choice(digit_indices[label1])
            x2 = x[idx2]

            pairs += [[x1, x2]]
            labels += [0]

            # add a non-matching example
            label2 = random.randint(0, num_classes - 1)
            while label2 == label1:
                label2 = random.randint(0, num_classes - 1)

            idx2 = random.choice(digit_indices[label2])
            x2 = x[idx2]

            pairs += [[x1, x2]]
            labels += [1]

        return np.array(pairs), np.array(labels).astype("float32")

if __name__ == '__main__':
    unittest.main()