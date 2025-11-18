import os
import pickle

import numpy as np

from useckit import Dataset
from useckit.paradigms.anomaly_detection.prediction_models.scikit_model_descriptions import ScikitBaseDescription
from useckit.paradigms.binary_verification.prediction_models.scikit_model_descriptions import ScikitClassif
from useckit.paradigms.binary_verification.prediction_models.verification_prediction_model_base import \
    VerificationBasePredictionModel


class VerificationSkLearnPredictionModel(VerificationBasePredictionModel):
    def __init__(self,
                 scikit_binary_classif: ScikitBaseDescription = ScikitClassif(),
                 output_dir: str = "scikit_pred_model_out",
                 verbose=False):
        super().__init__(output_dir=output_dir, verbose=verbose)
        self.build_description = scikit_binary_classif
        self.classifs = []
        self.labels_per_classif = []

    def persist_model_trainables(self, path_like: str = 'saved_trainable_values', **kwargs):
        classifs_file = os.path.join(self.output_dir, path_like)
        labels_per_classif_file = os.path.join(os.path.dirname(os.path.join(self.output_dir, path_like)),
                                                "labels_per_classif.persisted")
        with open(classifs_file, "wb") as file:
            pickle.dump(self.classifs, file)
        with open(labels_per_classif_file, "wb") as file:
            pickle.dump(self.labels_per_classif, file)

    def restore_model_trainables(self, path_like: str, **kwargs):
        classifs_file = os.path.join(self.output_dir, path_like)
        labels_per_classif_file = os.path.join(os.path.dirname(os.path.join(self.output_dir, path_like)),
                                                "labels_per_classif.persisted")
        with open(classifs_file, "rb") as file:
            self.classifs = pickle.load(file)
        with open(labels_per_classif_file, "rb") as file:
            self.labels_per_classif = pickle.load(file)

    def build_model(self, classes, **kwargs) -> dict:
        """Returns a dict of built models. The key of the dict is:
        * in OVR case: the class that the model was built for, or
        * in OVO case: a defaultdict where the first layer is class1 and the second layer is class2."""
        strat: str = kwargs["multiclass_classification_strategy"]

        if strat == "ovr":
            result = dict()
            for c in classes:
                assert c not in result.keys(), 'Error 1: key already exists.'
                # Assuming 'build_description.build_model()' method builds a model for the specific class
                result[c] = self.build_description.build_model()
        elif strat == "ovo":
            from collections import defaultdict
            result = defaultdict(dict)

            for i, c1 in enumerate(classes):
                for j, c2 in enumerate(classes):
                    if i >= j:  # Skip already considered or same class pairs
                        continue
                    result[c2][c1] = self.build_description.build_model()
        return result

    """def fit(self, dataset: Dataset, **kwargs):
        x_train, y_train = dataset.trainset_data, dataset.trainset_labels
        x_train = np.array([x.flatten() for x in x_train])
        unique_train_labels = dataset.get_unique_labels()
        assert len(unique_train_labels) > 0, "Dataset must have one or more classes to train one."
        classifs_built_dict: dict = self.build_model(unique_train_labels, **kwargs)

        # fit the different classifs
        for key in classifs_built_dict.keys():
            # find the elements in the training data that belong to class `i`
            if kwargs['multiclass_classification_strategy'] == "ovr":
                data_select = y_train == key
                y_train_clf = data_select.astype(int)  # cast boolean mask to int (0=False and 1=True)
                classifs_built_dict[key].fit(x_train, y_train_clf)
            elif kwargs['multiclass_classification_strategy'] == "ovo":
                for subkey in classifs_built_dict[key].keys():
                    left_model_key = key
                    right_model_key = subkey
                    data_select_left_accept = (y_train == left_model_key)
                    data_select_right_reject = (y_train == right_model_key)
                    data_to_accept = x_train[data_select_left_accept]
                    data_to_reject = x_train[data_select_right_reject]
                    x_train_clf = np.concatenate([data_to_accept, data_to_reject])
                    y_train_clf = [1] * len(data_to_accept) + [0] * len(data_to_reject)
                    classifs_built_dict[key][subkey].fit(x_train_clf, y_train_clf)

        self.classifs = classifs_built_dict"""

    def fit(self, dataset: Dataset, enable_parallel_fitting: bool = True, **kwargs):
        from joblib import Parallel, delayed

        x_train, y_train = dataset.trainset_data, dataset.trainset_labels
        x_train = np.array([x.flatten() for x in x_train])
        unique_train_labels = dataset.get_unique_labels()
        assert len(unique_train_labels) > 0, "Dataset must have one or more classes to train one."
        classifs_built_dict: dict = self.build_model(unique_train_labels, **kwargs)

        def fit_ovr_classifier(key, classifier):
            data_select = y_train == key
            y_train_clf = data_select.astype(int)  # cast boolean mask to int (0=False and 1=True)
            classifier.fit(x_train, y_train_clf)
            return key, classifier

        def fit_ovo_classifier(key, subkey, classifier):
            left_model_key = key
            right_model_key = subkey
            data_select_left_accept = (y_train == left_model_key)
            data_select_right_reject = (y_train == right_model_key)
            data_to_accept = x_train[data_select_left_accept]
            data_to_reject = x_train[data_select_right_reject]
            x_train_clf = np.concatenate([data_to_accept, data_to_reject])
            y_train_clf = [1] * len(data_to_accept) + [0] * len(data_to_reject)
            classifier.fit(x_train_clf, y_train_clf)
            return key, subkey, classifier

        if enable_parallel_fitting:
            if kwargs['multiclass_classification_strategy'] == "ovr":
                results = Parallel(n_jobs=-1)(
                    delayed(fit_ovr_classifier)(key, classifs_built_dict[key]) for key in classifs_built_dict.keys()
                )
                for key, classifier in results:
                    classifs_built_dict[key] = classifier

            elif kwargs['multiclass_classification_strategy'] == "ovo":
                results = Parallel(n_jobs=-1)(
                    delayed(fit_ovo_classifier)(key, subkey, classifs_built_dict[key][subkey])
                    for key in classifs_built_dict.keys()
                    for subkey in classifs_built_dict[key].keys()
                )
                for key, subkey, classifier in results:
                    classifs_built_dict[key][subkey] = classifier
        else:
            # fit the different classifs sequentially
            for key in classifs_built_dict.keys():
                if kwargs['multiclass_classification_strategy'] == "ovr":
                    _, classifs_built_dict[key] = fit_ovr_classifier(key, classifs_built_dict[key])
                elif kwargs['multiclass_classification_strategy'] == "ovo":
                    for subkey in classifs_built_dict[key].keys():
                        _, _, classifs_built_dict[key][subkey] = fit_ovo_classifier(key, subkey,
                                                                                    classifs_built_dict[key][subkey])

        self.classifs = classifs_built_dict

    def predict(self, x_test):
        x_test = x_test.reshape((x_test.shape[0], np.prod(x_test.shape[1:])))
        result_pred = []
        result_id = []
        for i, classif in zip(self.labels_per_classif, self.classifs):
            preds = classif.predict(x_test)
            result_pred.append(preds)
            result_id.append(i)
        return np.array(result_pred), np.array(result_id)
