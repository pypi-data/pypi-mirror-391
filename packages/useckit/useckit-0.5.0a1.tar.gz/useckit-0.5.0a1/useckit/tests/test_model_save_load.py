import os.path
import unittest
import tempfile
import numpy as np
from useckit.paradigms.anomaly_detection.prediction_models.auto_encoder_keras_prediction_model import \
    AutoEncoderKerasPredictionModel
from useckit.paradigms.anomaly_detection.prediction_models.scikit_anomaly_prediction_model import \
    ScikitAnomalyPredictionModel
from useckit.paradigms.distance_learning.prediction_models.scikit_distance_model import ScikitDistancePredictionModel
from useckit.paradigms.time_series_classification.prediction_models.classification_scikit_prediction_model import \
    ClassificationScikitPredictionModel
from useckit.paradigms.time_series_classification.prediction_models.classification_xgboost_prediction_model import \
    ClassificationXGBoostPredictionModel
from useckit.tests.test_utils import make_dataset
from useckit.util.dataset import Dataset


class TestUseckit(unittest.TestCase):
    @staticmethod
    def fit_save_load_eval(model_class, data: Dataset, save_path: str, instantiation_kwargs: dict, predict_kwargs: dict,
                           load_kwargs: dict):
        model = model_class(**instantiation_kwargs)
        x_test = data.testset_matching_data

        model.fit(data)
        model.persist_model_trainables(save_path)
        y1 = model.predict(x_test, **predict_kwargs)

        model = model_class(**instantiation_kwargs)
        model.restore_model_trainables(save_path, **load_kwargs)

        y2 = model.predict(x_test, **predict_kwargs)

        try:
            assert np.isclose(y1, y2).all()
        except ValueError as ve:
            if "The requested array has an inhomogeneous shape after 2 dimensions." in str(ve):
                assert np.isclose(y1[0], y2[0]).all()

    def test_tsc_scikit_prediction_model(self):
        model_class = ClassificationScikitPredictionModel
        self._test_scikit(model_class, 't_t_s_p_m.persisted')

    def test_distance_scikit_prediction_model(self):
        model_class = ScikitDistancePredictionModel
        data = make_dataset(shape=(100, 100))
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, 't_d_s_p_m.persisted')
            kwargs = {'output_dir': ''}
            args = {'x_test_2': data.testset_matching_data}
            self.fit_save_load_eval(model_class, data, save_path, kwargs, args, dict())

    def test_anomaly_scikit_prediction_model(self):
        model_class = ScikitAnomalyPredictionModel
        data = make_dataset(shape=(100, 100))
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, 't_a_s_p_m.persisted')
            kwargs = {'output_dir': ''}
            args = {}
            self.fit_save_load_eval(model_class, data, save_path, kwargs, args, dict())

    def test_xgb_prediction_model(self):
        model_class = ClassificationXGBoostPredictionModel
        self._test_scikit(model_class, 't_t_xgb_p_m.persisted')

    def _test_scikit(self, model_class, name):
        data = make_dataset(shape=(100, 100))
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, name)
            kwargs = {'output_dir': ''}
            y_train, y_val, _, y_test = data.view_one_hot_encoded_labels()
            y_true = np.argmax(y_val, axis=1)
            args = {'y_true': y_true, 'x_train': data.trainset_data, 'y_train': y_train, 'y_test': y_test}
            self.fit_save_load_eval(model_class, data, save_path, kwargs, args, dict())

    def test_encoders(self):
        model_class = AutoEncoderKerasPredictionModel
        data = make_dataset(shape=(16, 10, 10))
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, 't_enc.persisted')
            kwargs = {'output_dir': save_path, 'nb_epochs': 2}
            args = {}
            self.fit_save_load_eval(model_class, data, save_path, kwargs, args, {'dataset': data})


if __name__ == '__main__':
    unittest.main()
