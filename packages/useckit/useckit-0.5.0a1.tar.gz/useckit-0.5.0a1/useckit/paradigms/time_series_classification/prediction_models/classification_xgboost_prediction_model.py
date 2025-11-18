import os

import numpy as np
from xgboost import XGBClassifier

from .classification_scikit_prediction_model import ClassificationScikitPredictionModel
from ....util.dataset import Dataset


class ClassificationXGBoostPredictionModel(ClassificationScikitPredictionModel):
    def persist_model_trainables(self, path_like: str = 'saved_trainable_values', **kwargs):
        path = os.path.join(self.output_dir, path_like)
        self.classifier.save_model(path)

    def restore_model_trainables(self, path_like, dataset: Dataset = None, **kwargs):
        self.classifier.load_model(path_like)

    def __init__(self,
                 xgb_classifier: XGBClassifier = XGBClassifier(),
                 sample_weights=None,
                 verbose: bool = True,
                 output_dir: str = "xgb_classifier_out",
                 xgb_fit_kwargs: dict = None):
        super().__init__(scikit_classifier=xgb_classifier, sample_weights=sample_weights, output_dir=output_dir,
                         verbose=verbose)
        self.xgb_fit_kwargs = {} if xgb_fit_kwargs is None else xgb_fit_kwargs

    def fit(self, dataset: Dataset, *args, **kwargs):
        x_train, y_train = dataset.trainset_data, dataset.trainset_labels
        x_train = x_train.reshape((x_train.shape[0], np.prod(x_train.shape[1:])))
        self.classifier = self.classifier.fit(x_train, y_train, sample_weight=self.sample_weights,
                                              **self.xgb_fit_kwargs)
