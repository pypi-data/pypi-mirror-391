import os
import pickle
from typing import Callable, Tuple

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from .distance_prediction_model_base import DistanceBasePredictionModel
from ....util.dataset import Dataset
from ....util.utils import contrastive_make_pairs


class ScikitDistancePredictionModel(DistanceBasePredictionModel):

    def __init__(self,
                 scikit_regressor=RandomForestRegressor(),
                 output_dir: str = "scikit_pred_model_out",
                 verbose=False,
                 pair_function: Callable[[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]] =
                 contrastive_make_pairs):
        super().__init__(output_dir=output_dir, verbose=verbose)
        self.regressor = scikit_regressor
        self.pair_function = pair_function

    def persist_model_trainables(self, path_like: str = 'saved_trainable_values', **kwargs):
        with open(os.path.join(self.output_dir, path_like), "wb") as file:
            pickle.dump(self.regressor, file)

    def restore_model_trainables(self, path_like: str, **kwargs):
        with open(path_like, "rb") as file:
            self.regressor = pickle.load(file)

    def fit(self, dataset: Dataset):
        pairs_train, labels_train = self.pair_function(dataset.trainset_data, dataset.trainset_labels)
        reshape_dim_1 = pairs_train.shape[0]
        reshape_dim_2 = np.prod(pairs_train.shape[1:])
        pairs_train = np.reshape(pairs_train, (reshape_dim_1, reshape_dim_2,))
        self.regressor = self.regressor.fit(pairs_train, labels_train)

    def predict(self, x_test_1, x_test_2):
        pairs = np.stack((x_test_1, x_test_2,), axis=1)
        reshape_dim_1 = pairs.shape[0]
        reshape_dim_2 = np.prod(pairs.shape[1:])
        pairs = np.reshape(pairs, (reshape_dim_1, reshape_dim_2,))
        y_pred = self.regressor.predict(pairs)
        return y_pred
