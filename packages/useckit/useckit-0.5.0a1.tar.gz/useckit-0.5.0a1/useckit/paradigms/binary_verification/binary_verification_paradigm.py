from useckit import Dataset
from useckit.paradigms._paradigm_base import ParadigmBase, PredictionModelBase
from useckit.paradigms.binary_verification.evaluation_methods.binary_verification_evaluation_method_base import \
    VerificationBaseEvaluationMethod
from useckit.paradigms.binary_verification.evaluation_methods.binary_verification_evaluation_method_scoring import \
    BinaryScoringVerification
from useckit.paradigms.binary_verification.prediction_models.verification_scikit_prediction_model import \
    VerificationSkLearnPredictionModel


class BinaryVerificationParadigm(ParadigmBase):
    def __init__(self,
                 prediction_model: VerificationSkLearnPredictionModel = None,
                 evaluation_methods: [VerificationBaseEvaluationMethod] = None,
                 seed=42,
                 **base_kwargs
                 ):
        # This looks really stupid, but if the default value is initiated in the method head, not in the call to the
        # super constructor as below, python will only instantiate one object for all calls to this method, hence
        # causing different paradigms to share the same instances of prediction model or evaluation method.
        # For more information see:
        # https://florimond.dev/en/posts/2018/08/python-mutable-defaults-are-the-source-of-all-evil/
        super().__init__(
            prediction_model=VerificationSkLearnPredictionModel() if prediction_model is None else prediction_model,
            evaluation_methods=[BinaryScoringVerification()] if evaluation_methods is None else evaluation_methods,
            seed=seed,
            **base_kwargs)

    def restore_prediction_model_trainables(self,
                                            verification_paradigm_prediction_model_directory_path_like: str,
                                            dataset: Dataset,
                                            individual_models_file_name_path_like: str = 'best_model.hdf5') \
            -> PredictionModelBase:
        self.prediction_model.restore_model_trainables(verification_paradigm_prediction_model_directory_path_like,
                                                       dataset=dataset,
                                                       path_like_individual_models_file_name=
                                                       individual_models_file_name_path_like)
        return self.prediction_model
