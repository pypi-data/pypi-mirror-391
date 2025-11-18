from abc import abstractmethod

from useckit import Dataset
from useckit.paradigms._paradigm_base import EvaluationMethodBase
from useckit.paradigms.binary_verification.prediction_models.verification_prediction_model_base import \
    VerificationBasePredictionModel


class VerificationBaseEvaluationMethod(EvaluationMethodBase):

    @abstractmethod
    def evaluate(self, dataset: Dataset, prediction_model: VerificationBasePredictionModel, **kwargs):
        pass
