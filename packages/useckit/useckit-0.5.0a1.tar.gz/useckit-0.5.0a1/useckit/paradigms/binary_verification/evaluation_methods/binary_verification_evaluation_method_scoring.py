import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sklearn.metrics import auc

from useckit import Dataset
from useckit.paradigms.binary_verification.evaluation_methods.binary_verification_evaluation_method_base import \
    VerificationBaseEvaluationMethod
from useckit.paradigms.binary_verification.prediction_models.verification_prediction_model_base import \
    VerificationBasePredictionModel


class BinaryScoringVerification(VerificationBaseEvaluationMethod):
    def evaluate(self, dataset: Dataset, prediction_model: VerificationBasePredictionModel, **kwargs):
        # The `prediction_model` contains fitted classifiers.

        # Extract multiclass_strategy from kwargs or set default to 'ovr'
        multiclass_strategy = kwargs["multiclass_classification_strategy"].lower()
        if multiclass_strategy not in ["ovr", "ovo"]:
            raise ValueError(f'multiclass_strategy must be either "ovr" or "ovo", but '
                             f'{multiclass_strategy} was provided.')
        self.multiclass_strategy = multiclass_strategy

        # Unpack prediction_model
        classifs = prediction_model.classifs
        self.output_dir = Path(prediction_model.output_dir).parent / "evaluation"
        self.verbose = prediction_model.verbose

        # Unpack dataset
        reject_label = dataset.reject_label
        matching_data = dataset.testset_matching_data
        matching_labels = dataset.testset_matching_labels

        # Prepare result storage
        if multiclass_strategy == "ovr":
            graph = self._run_ovr_with_matchingdata(classifs, matching_data, matching_labels,
                                                    getattr(dataset, 'testset_matching_slicedsample_origin', None))
        elif multiclass_strategy == "ovo":
            graph = self._run_ovo_with_matchingdata(classifs, matching_data, matching_labels,
                                                    getattr(dataset, 'testset_matching_slicedsample_origin', None))

        proba_metrics: pd.DataFrame = self._calculate_proba_based_predictions(graph,
                                                                              reverse_decision=kwargs.get("reverse_decision", False))

        proba_metrics.to_csv(Path(self.output_dir) / 'threshold-metrics.tsv', sep='\t', index=False)

        self.calc_and_plot_eer(proba_metrics)
        self.calc_and_plot_auc(proba_metrics)

    def _run_ovr_with_matchingdata(self, classifs, matching_data, matching_labels, slicedsample_origin=None):
        results = []

        # Test matching data for all classifiers
        for key in classifs.keys():
            classif = classifs[key]

            y_scores = classif.predict_proba(matching_data)[:, 0]
            y_true = (matching_labels == key).astype(int)

            results.append({'clf_class one label': key,
                            'y_scores': y_scores,
                            'y_true': y_true,
                            'matching_labels': matching_labels,
                            'slicedsample_origin': slicedsample_origin,  # can be None
                            'method': 'ovr'})

        return results

    def _run_ovo_with_matchingdata(self, classifs, matching_data, matching_labels, slicedsample_origin=None):
        results = []

        for key1 in classifs.keys():
            for key2 in classifs[key1].keys():
                classif = classifs[key1][key2]

                # Select data where the matching label is either label_one or label_other
                data_mask = (matching_labels == key1) | (matching_labels == key2)
                selected_data = matching_data[data_mask]
                selected_labels = matching_labels[data_mask]
                selected_slice_samples = slicedsample_origin[data_mask] if slicedsample_origin is not None else None

                # Compute probability scores for class corresponding to label_one
                y_scores = classif.predict_proba(selected_data)[:, 0]

                # Create true labels array: 1 where the label matches label_one, otherwise 0
                y_true = (selected_labels == key1).astype(int)

                # runtime validation
                if slicedsample_origin is not None:
                    assert len(y_scores) == len(y_true) == len(selected_labels) == len(selected_slice_samples), \
                        (f"The lengths of `y_scores` (len={len(y_scores)}), `y_true` (len={len(y_true)}), "
                         f"`selected_labels` (len={len(selected_labels)}), and `selected_slice_samples` "
                         f"(len={len(selected_slice_samples)}) must match, but they are not equal.")
                else:
                    assert len(y_scores) == len(y_true) == len(selected_labels), \
                        (f"The lengths of `y_scores` (len={len(y_scores)}), `y_true` (len={len(y_true)}), "
                         f"and `selected_labels` (len={len(selected_labels)}), must match, but they are not equal.")

                # Append results
                results.append({
                    'clf_class one label': key1,
                    'clf_class other label': key2,
                    'y_scores': y_scores,
                    'y_true': y_true,
                    'matching_labels': selected_labels,
                    'slicedsample_origin': selected_slice_samples,  # can be None when window slicing is not enabled
                    'method': 'ovo'
                })

        return results

    def _calculate_proba_based_predictions(self, verification_graph: list[dict], reverse_decision: bool = False) -> pd.DataFrame:
        all_possible_thresholds = np.unique(np.concatenate([r['y_scores'] for r in verification_graph]))
        epsilon = np.finfo(float).eps

        # add edge cases with the smallest possible adjustments
        min_score = min(all_possible_thresholds) - epsilon
        max_score = max(all_possible_thresholds) + epsilon

        # contains all possible thresholds
        all_possible_thresholds = np.concatenate([[min_score], all_possible_thresholds, [max_score]])

        # array to store results
        metric_results = []

        # bested loops for all combinations
        for i, threshold in enumerate(all_possible_thresholds):
            for edge in verification_graph:  # for every identity
                current_class_label_gt = edge['clf_class one label']  # current ground truth label
                slicedsample_origin = edge.get('slicedsample_origin')  # can be "None" if window slicing is not enabled

                window_slicing_is_enabled: bool = slicedsample_origin is not None

                if window_slicing_is_enabled:
                    # get unique samples if windowslicing is enabled so that we can initialize the voting_df
                    unique_samples: np.ndarray = np.unique(slicedsample_origin)
                else:
                    # if no window_slicing; create mask for compatibility
                    unique_samples = np.arange(len(edge['y_scores']))

                # initialization of one row per unique_sample with all metrics set to zero
                # index is: (sample_origin, threshold)
                voting_df = pd.DataFrame({'sample_origin': unique_samples,
                                          'threshold': [threshold]*len(unique_samples),
                                          'tp': [0]*len(unique_samples),
                                          'fp': [0]*len(unique_samples),
                                          'tn': [0]*len(unique_samples),
                                          'fn': [0]*len(unique_samples)}).set_index(["sample_origin", "threshold"])

                for usample in unique_samples:
                    if window_slicing_is_enabled:
                         # get all predictions for every unique sample sample when window slicing
                        get_mask: np.ndarray = edge['slicedsample_origin'] == usample
                    else:
                        # window slicing is not enabled
                        get_mask: np.ndarray = unique_samples == usample

                    # unpack edge for current unique sample
                    usample_scores_array: np.ndarray = edge['y_scores'][get_mask]  # array of prediction scores from clf
                    usample_gt_array: np.ndarray = edge['y_true'][get_mask]  # array of truth predictions (1=accept, 0=reject)
                    usample_matching_label_array: np.ndarray = edge['matching_labels'][get_mask]  # array of gt class labels

                    sample_ground_truth: np.ndarray = np.unique(usample_gt_array)
                    sample_matching_label: np.ndarray = np.unique(usample_matching_label_array)

                    # assert that no mix up happened between ground truths and matching labels
                    assert len(sample_ground_truth) == 1, (f"Expected `sample_ground_truth` to have only one "
                                                           f"element, but found {len(sample_ground_truth)} "
                                                           f"elements: {sample_ground_truth}")
                    assert len(sample_matching_label) == 1, (f"Expected `sample_matching_label` to have only one "
                                                             f"element, but found {len(sample_matching_label)} "
                                                             f"elements: {sample_matching_label}")

                    sample_ground_truth: int = sample_ground_truth[0]
                    sample_matching_label: int = sample_matching_label[0]

                    # majority_vote_values contains bools denoting whether sample should be accepted or rejected
                    if not reverse_decision:
                        majority_vote_values, majority_vote_counts = Counter(usample_scores_array < threshold).most_common()[0]
                    else:
                        majority_vote_values, majority_vote_counts = Counter(usample_scores_array >= threshold).most_common()[0]


                    accept_sample: bool = majority_vote_values
                    matching_label_equals_current_class: bool = current_class_label_gt == sample_matching_label

                    if accept_sample and matching_label_equals_current_class:
                        voting_df.loc[(usample, threshold), "tp"] += 1
                    elif accept_sample and not matching_label_equals_current_class:
                        voting_df.loc[(usample, threshold), "fp"] += 1
                    elif not accept_sample and matching_label_equals_current_class:
                        voting_df.loc[(usample, threshold), "fn"] += 1
                    elif not accept_sample and not matching_label_equals_current_class:
                        voting_df.loc[(usample, threshold), "tn"] += 1

                # store into list
                metric_results.append(voting_df)

        # concatenate voting_dfs for various thresholds and samples
        metric_df = pd.concat(metric_results).reset_index()

        # sum up how many TP, FP, TN, and FN exist per. sample_origin loses its meaning upon grouping by threshold.
        metric_df = metric_df.groupby("threshold").sum().drop(columns=["sample_origin"])

        assert len(np.unique(metric_df.sum(axis=1))) == 1, (f'There is an offset in sample calculation. '
                                                            f'Every row is suspected to have an equal amount of '
                                                            f'predictions per threshold, but instead more than one '
                                                            f'value was found: {np.unique(metric_df.sum(axis=1))}')

        # add additional metrics
        metric_df['tpr'] = metric_df.apply(lambda row: self.calculate_tpr(row['tp'], row['fn']), axis=1)
        metric_df['fpr'] = metric_df.apply(lambda row: self.calculate_fpr(row['fp'], row['tn']), axis=1)
        metric_df['tnr'] = metric_df.apply(lambda row: self.calculate_tnr(row['tn'], row['fp']), axis=1)
        metric_df['fnr'] = metric_df.apply(lambda row: self.calculate_fnr(row['fn'], row['tp']), axis=1)
        metric_df['acc'] = metric_df.apply(lambda row: self.calculate_acc(row['tp'], row['tn'], row['fp'], row['fn']),
                                           axis=1)
        metric_df['bacc'] = metric_df.apply(lambda row: self.calculate_bacc(row['tp'], row['tn'], row['fp'], row['fn']),
                                           axis=1)

        return metric_df.reset_index()

    def calc_and_plot_eer(self, df: pd.DataFrame):
        # Calculate the point where FPR and FNR are closest (EER)
        df['distance fpr to fnr'] = np.abs(df['fpr'] - df['fnr'])
        eer_threshold = df.loc[df['distance fpr to fnr'].idxmin(), 'threshold']
        eer_value = df.loc[df['distance fpr to fnr'].idxmin(), 'fpr']

        # Plotting
        plt.figure(figsize=(10, 5))
        plt.plot(df['threshold'], df['fpr'], label='False Positive Rate (FPR / FAR)')
        plt.plot(df['threshold'], df['fnr'], label='False Negative Rate (FNR / FRR)')
        plt.axvline(x=eer_threshold, color='r', linestyle='--', label=f'EER {eer_value:.4f} at threshold {eer_threshold:.4f}')
        plt.title('Equal Error Rate (EER) Analysis')
        plt.xlabel('Threshold')
        plt.ylabel('Error Rate')
        plt.legend()
        plt.grid(True)
        plt.savefig(Path(self.output_dir) / 'eer.pdf', bbox_inches="tight")

        if self.verbose:
            print(f"The Equal Error Rate (EER) is approximately {eer_value:.2f} at threshold {eer_threshold:.5f}")

        # Write data to a JSON file
        with open(Path(self.output_dir) / 'eer.json', 'w') as file:
            json.dump({"eer_threshold": eer_threshold, "eer_value": eer_value}, file, indent=4)

    def calc_and_plot_auc(self, df: pd.DataFrame):
        # Calculate the ROC curve and AUC
        df_sorted = df.sort_values(by="fpr")
        roc_auc = auc(x=df_sorted["fpr"].values, y=df_sorted["tpr"].values)

        # Plotting
        plt.figure(figsize=(6, 5))
        plt.plot(df.fpr, df.tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label=f'Random Guess (AUC = 0.5)')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC)')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.savefig(Path(self.output_dir) / 'roc_curve.pdf', bbox_inches="tight")

        if self.verbose:
            print(f"The Area Under the Curve (AUC) is {roc_auc:.2f}")

        # Write AUC to a JSON file
        with open(Path(self.output_dir) / 'auc.json', 'w') as file:
            json.dump({"auc_value": roc_auc}, file, indent=4)

    def calculate_tpr(self, tp, fn) -> float:
        """ Calculate True Positive Rate (Sensitivity or Recall) """
        try:
            value = tp / (tp + fn)
            if np.isnan(value):
                error_value = 0.0
                return error_value
            else:
                return value
        except ZeroDivisionError:
            return 0.0

    def calculate_fpr(self, fp, tn) -> float:
        """ Calculate False Positive Rate """
        try:
            return fp / (fp + tn)
        except ZeroDivisionError:
            return 1.0

    def calculate_tnr(self, tn, fp) -> float:
        """ Calculate True Negative Rate (Specificity) """
        try:
            return tn / (tn + fp)
        except ZeroDivisionError:
            return 0.0

    def calculate_fnr(self, fn, tp) -> float:
        """ Calculate False Negative Rate """
        try:
            return fn / (fn + tp)
        except ZeroDivisionError:
            return 1.0

    def calculate_acc(self, tp, tn, fp, fn) -> float:
        """ Calculate Accuracy """
        try:
            return (tp + tn) / (tp + tn + fp + fn)
        except ZeroDivisionError:
            return 0.0

    def calculate_bacc(self, tp, tn, fp, fn) -> float:
        """ Calculate Balanced Accuracy """
        sensitivity: float = self.calculate_tpr(tp, fn)
        specificity: float = self.calculate_tnr(tn, fp)
        return (sensitivity + specificity) / 2

    def calculate_mcc(self, tp, tn, fp, fn) -> float:
        """ Calculate Matthew's Correlation Coefficient """
        try:
            numerator = (tp * tn) - (fp * fn)
            denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
            return numerator / denominator
        except ZeroDivisionError:
            return 0.0

    def calculate_f1(self, tp, tn, fp, fn):
        """ Calculate F1 Score """
        try:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            return 2 * (precision * recall) / (precision + recall)
        except ZeroDivisionError:
            return 0.0
