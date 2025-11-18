import os
import pickle

import numpy as np

from .anomaly_prediction_model_base import AnomalyBasePredictionModel
from .scikit_model_descriptions import ScikitBaseDescription, ScikitRegressor
from ....util.dataset import Dataset


class ScikitAnomalyPredictionModel(AnomalyBasePredictionModel):

    def __init__(self,
                 scikit_regressor: ScikitBaseDescription = ScikitRegressor(),
                 output_dir: str = "scikit_pred_model_out",
                 verbose=False):
        super().__init__(output_dir=output_dir, verbose=verbose)
        self.build_description = scikit_regressor
        self.regressors = []
        self.label_per_regressor = []

    def persist_model_trainables(self, path_like: str = 'saved_trainable_values', **kwargs):
        regressors_file = os.path.join(self.output_dir, path_like)
        label_per_regressor_file = os.path.join(os.path.dirname(os.path.join(self.output_dir, path_like)),
                                                "labels_per_regressor.persisted")
        with open(regressors_file, "wb") as file:
            pickle.dump(self.regressors, file)
        with open(label_per_regressor_file, "wb") as file:
            pickle.dump(self.label_per_regressor, file)

    def restore_model_trainables(self, path_like: str, **kwargs):
        regressors_file = os.path.join(self.output_dir, path_like)
        label_per_regressor_file = os.path.join(os.path.dirname(os.path.join(self.output_dir, path_like)),
                                                "labels_per_regressor.persisted")
        with open(regressors_file, "rb") as file:
            self.regressors = pickle.load(file)
        with open(label_per_regressor_file, "rb") as file:
            self.label_per_regressor = pickle.load(file)

    def build_model(self, nb_classes):
        result = []
        for i in range(nb_classes):
            result.append(self.build_description.build_model())
        return result

    def fit(self, dataset: Dataset):
        x_train, y_train = dataset.trainset_data, dataset.trainset_labels
        x_train = x_train.reshape((x_train.shape[0], np.prod(x_train.shape[1:])))
        nb_classes = dataset.train_classes()
        assert nb_classes > 0
        regressors_built = self.build_model(nb_classes)
        for i, regressor in zip(np.unique(y_train), regressors_built):
            # find the elements in the training data that belong to class `i`
            belonging_indexes = y_train == i

            true_anomaly_scores = np.ones((len(x_train),), dtype='float16')
            true_anomaly_scores[belonging_indexes] = 0

            regressor.fit(x_train, true_anomaly_scores)
            self.label_per_regressor.append(i)
        self.regressors = regressors_built

    def predict(self, x_test):
        x_test = x_test.reshape((x_test.shape[0], np.prod(x_test.shape[1:])))
        result_pred = []
        result_id = []
        for i, regressor in zip(self.label_per_regressor, self.regressors):
            preds = regressor.predict(x_test)
            result_pred.append(preds)
            result_id.append(i)
        return np.array(result_pred), np.array(result_id)
