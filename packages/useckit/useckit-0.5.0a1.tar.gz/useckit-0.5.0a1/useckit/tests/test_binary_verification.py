import json
import unittest
from glob import glob
import os

import numpy as np

from useckit.tests.test_utils import make_dataset, make_windowsliced_dataset
from useckit import Dataset
from useckit.paradigms.binary_verification.binary_verification_paradigm import BinaryVerificationParadigm
from useckit.paradigms.binary_verification.evaluation_methods.binary_verification_evaluation_method_scoring import \
    BinaryScoringVerification
from useckit.paradigms.binary_verification.prediction_models.verification_scikit_prediction_model import \
    VerificationSkLearnPredictionModel
from useckit.paradigms.binary_verification.prediction_models.scikit_model_descriptions import ScikitClassif
from useckit.util.dataset_windowsliced import WindowslicedDataset

from sklearn.ensemble import RandomForestClassifier


class TestBinaryVerification(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.unittest_execution_counter = 1

    def assert_function(self):
        print("CWD:", os.getcwd(), ", current unittest execution counter:", self.unittest_execution_counter)
        assert len(glob(f"_test_binary_verification*/experiment_{self.unittest_execution_counter}_Binary*/evaluation/auc.json",
                        recursive=True)) == 1
        assert len(
            glob(f"_test_binary_verification*/experiment_{self.unittest_execution_counter}_Binary*/evaluation/eer.json",
                 recursive=True)) == 1
        assert len(
            glob(f"_test_binary_verification*/experiment_{self.unittest_execution_counter}_Binary*/evaluation/eer.pdf",
                 recursive=True)) == 1
        assert len(
            glob(f"_test_binary_verification*/experiment_{self.unittest_execution_counter}_Binary*/evaluation/roc_curve.pdf",
                 recursive=True)) == 1
        assert len(glob(f"_test_binary_verification*/experiment_{self.unittest_execution_counter}_Binary*/evaluation/threshold-metrics.tsv",
                 recursive=True)) == 1
        with open(glob(f"_test_binary_verification*/experiment_{self.unittest_execution_counter}_Binary*/evaluation/auc.json", recursive=True)[0], 'r') as f:
            assert json.load(f)["auc_value"] > .85
        with open(glob(f"_test_binary_verification*/experiment_{self.unittest_execution_counter}_Binary*/evaluation/eer.json", recursive=True)[0], 'r') as h:
            assert json.load(h)["eer_value"] < .15
        self.unittest_execution_counter += 1

    def test_binary_verification(self, method='ovr'):
        # ovr = one vs rest case
        data = make_dataset(shape=(100, 100), noisiness=0)
        verif = BinaryVerificationParadigm(verbose=True,
                                           prediction_model=VerificationSkLearnPredictionModel(),
                                           evaluation_methods=[BinaryScoringVerification()],
                                           multiclass_classification_strategy=method,
                                           output_dir=f"_test_binary_verification_{method}")
        verif.evaluate(data)
        self.assert_function()

    def test_binary_verification_reverse(self, method='ovr'):
        # ovr = one vs rest case
        data = make_dataset(shape=(100, 100), noisiness=0)
        verif = BinaryVerificationParadigm(verbose=True,
                                           prediction_model=VerificationSkLearnPredictionModel(),
                                           evaluation_methods=[BinaryScoringVerification()],
                                           multiclass_classification_strategy=method,
                                           reverse_decision=True,
                                           output_dir=f"_test_binary_verification_{method}_reverse")
        verif.evaluate(data)
        self.assert_function()

    def test_binary_verification_rf(self, method='ovr'):
        # ovr = one vs rest case
        data = make_dataset(shape=(100, 100), noisiness=0)
        verif = BinaryVerificationParadigm(verbose=True,
                                           prediction_model=VerificationSkLearnPredictionModel(),
                                           evaluation_methods=[BinaryScoringVerification()],
                                           multiclass_classification_strategy=method,
                                           output_dir=f"_test_binary_verification_{method}_rf")
        verif.evaluate(data)
        self.assert_function()

    def test_binary_verification_reverse_rf(self, method='ovr'):
        # ovr = one vs rest case
        data = make_dataset(shape=(100, 100), noisiness=0)
        verif = BinaryVerificationParadigm(verbose=True,
                                           prediction_model=VerificationSkLearnPredictionModel(),
                                           evaluation_methods=[BinaryScoringVerification()],
                                           multiclass_classification_strategy=method,
                                           reverse_decision=True,
                                           output_dir=f"_test_binary_verification_{method}_rf_reverse")
        verif.evaluate(data)
        self.assert_function()

    def test_binary_verification_ovo(self):
        # ovo = one vs one case
        self.test_binary_verification(method='ovo')

    def test_binary_verification_windowsliced(self, method='ovr'):
        # ovo = one vs one case
        data = make_windowsliced_dataset(5, 10, shape=(20, 100), noisiness=0)
        verif = BinaryVerificationParadigm(verbose=True,
                                           prediction_model=VerificationSkLearnPredictionModel(),
                                           evaluation_methods=[BinaryScoringVerification()],
                                           multiclass_classification_strategy='ovr',
                                           output_dir=f"_test_binary_verification_windowsliced_{method}")
        verif.evaluate(data)
        self.assert_function()

    def test_binary_verification_windowsliced_ovo(self):
        # ovo = one vs one case
        self.test_binary_verification_windowsliced(method='ovo')

    def test_binary_verification_eatg(self, method='ovr'):
        x1 = np.load(glob("**/x1eatg.npy", recursive=True)[0])
        y1 = np.load(glob("**/y1eatg.npy", recursive=True)[0])
        x2 = np.load(glob("**/x2eatg.npy", recursive=True)[0])
        y2 = np.load(glob("**/y2eatg.npy", recursive=True)[0])

        useckit_dataset = Dataset(trainset_data=x1, trainset_labels=y1,
                                  testset_enrollment_data=x1, testset_enrollment_labels=y1,
                                  testset_matching_data=x2,
                                  testset_matching_labels=y2)

        prediction_model = VerificationSkLearnPredictionModel(
            scikit_binary_classif=ScikitClassif(scikit_classif_class=RandomForestClassifier)
        )

        verif = BinaryVerificationParadigm(verbose=True,
                                           prediction_model=prediction_model,
                                           evaluation_methods=[BinaryScoringVerification()],
                                           multiclass_classification_strategy=method,
                                           output_dir=f"_test_binary_verification_eatg_{method}")
        verif.evaluate(useckit_dataset)
        self.assert_function()

    def test_binary_verification_eatg_ovo(self):
        self.test_binary_verification_eatg(method='ovo')

    def test_binary_verification_eatg_windowslicing(self, method='ovr'):
        from useckit.paradigms.binary_verification.prediction_models.scikit_model_descriptions import ScikitClassif

        x1 = np.load(glob("**/x1eatg.npy", recursive=True)[0])
        y1 = np.load(glob("**/y1eatg.npy", recursive=True)[0])
        x2 = np.load(glob("**/x2eatg.npy", recursive=True)[0])
        y2 = np.load(glob("**/y2eatg.npy", recursive=True)[0])

        useckit_dataset = WindowslicedDataset(trainset_data=x1, trainset_labels=y1,
                                              testset_enrollment_data=x1, testset_enrollment_labels=y1,
                                              testset_matching_data=x2,
                                              testset_matching_labels=y2,
                                              window_slicing_stride=5,
                                              window_slicing_size=10)

        prediction_model = VerificationSkLearnPredictionModel(
            scikit_binary_classif=ScikitClassif(scikit_classif_class=RandomForestClassifier)
        )

        verif = BinaryVerificationParadigm(verbose=True,
                                           prediction_model=prediction_model,
                                           evaluation_methods=[BinaryScoringVerification()],
                                           multiclass_classification_strategy=method,
                                           output_dir=f"_test_binary_verification_eatg_windowslicing_{method}")
        verif.evaluate(useckit_dataset)
        self.assert_function()

    def test_binary_verification_eatg_windowslicing_ovo(self):
        self.test_binary_verification_eatg_windowslicing(method='ovo')


if __name__ == '__main__':
    unittest.main()
