import os
import pickle

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from .tsc_prediction_model_base import TSCBasePredictionModel
from ....util.dataset import Dataset


class ClassificationScikitPredictionModel(TSCBasePredictionModel):
    def __init__(self,
                 scikit_classifier=RandomForestClassifier(),
                 sample_weights=None,
                 verbose: bool = True,
                 output_dir: str = "scikit_classifier_out"):
        super().__init__(output_dir=output_dir, verbose=verbose)
        self.classifier = scikit_classifier
        self.sample_weights = sample_weights
        self.model_description = str(type(self.classifier))

    def persist_model_trainables(self, path_like: str = 'saved_trainable_values', **kwargs):
        with open(os.path.join(self.output_dir, path_like), "wb") as file:
            pickle.dump(self.classifier, file)

    def restore_model_trainables(self, path_like, dataset: Dataset = None, **kwargs):
        with open(path_like, "rb") as file:
            self.classifier = pickle.load(file)

    def fit(self, dataset: Dataset, *args, **kwargs):
        x_train, y_train = dataset.trainset_data, dataset.trainset_labels
        x_train = x_train.reshape((x_train.shape[0], np.prod(x_train.shape[1:])))
        self.classifier = self.classifier.fit(x_train, y_train, sample_weight=self.sample_weights)

    def predict(self, x_test, y_true, x_train, y_train, y_test, return_df_metrics=True):
        x_test = x_test.reshape((x_test.shape[0], np.prod(x_test.shape[1:])))
        return self.classifier.predict(x_test)
