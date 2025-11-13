# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
Calibration utilities for uncertainty quantification.
"""

from typing import List, Tuple
import math


class CalibrationScorer:
    """
    Compute calibration metrics for uncertainty estimates.
    """

    def __init__(self, n_bins: int = 15):
        """
        Initialize calibration scorer.

        Args:
            n_bins: Number of bins for ECE calculation
        """
        self.n_bins = n_bins

    def compute_ece(
        self,
        confidences: List[float],
        accuracies: List[float]
    ) -> float:
        """
        Compute Expected Calibration Error (ECE).

        ECE measures the difference between confidence and accuracy
        across binned predictions.

        Args:
            confidences: List of confidence scores [0, 1]
            accuracies: List of accuracy labels (0 or 1)

        Returns:
            ECE value [0, 1] where 0 = perfectly calibrated
        """
        if len(confidences) != len(accuracies):
            raise ValueError("Confidences and accuracies must have same length")

        if len(confidences) == 0:
            return 0.0

        # Create bins
        bins = self._create_bins(confidences, accuracies)

        # Compute ECE
        ece = 0.0
        total_samples = len(confidences)

        for bin_conf, bin_acc in bins:
            if len(bin_conf) > 0:
                avg_conf = sum(bin_conf) / len(bin_conf)
                avg_acc = sum(bin_acc) / len(bin_acc)
                bin_weight = len(bin_conf) / total_samples
                ece += bin_weight * abs(avg_conf - avg_acc)

        return ece

    def _create_bins(
        self,
        confidences: List[float],
        accuracies: List[float]
    ) -> List[Tuple[List[float], List[float]]]:
        """
        Bin predictions by confidence level.

        Args:
            confidences: Confidence scores
            accuracies: Accuracy labels

        Returns:
            List of (bin_confidences, bin_accuracies) tuples
        """
        bins = [[] for _ in range(self.n_bins)]
        bin_accs = [[] for _ in range(self.n_bins)]

        for conf, acc in zip(confidences, accuracies):
            bin_idx = min(int(conf * self.n_bins), self.n_bins - 1)
            bins[bin_idx].append(conf)
            bin_accs[bin_idx].append(acc)

        return list(zip(bins, bin_accs))

    def compute_brier(
        self,
        predictions: List[float],
        targets: List[float]
    ) -> float:
        """
        Compute Brier score.

        Brier = mean((prediction - target)^2)

        Args:
            predictions: Predicted probabilities [0, 1]
            targets: True labels (0 or 1)

        Returns:
            Brier score [0, 1] where 0 = perfect predictions
        """
        if len(predictions) != len(targets):
            raise ValueError("Predictions and targets must have same length")

        if len(predictions) == 0:
            return 0.0

        squared_errors = [(pred - target)**2 for pred, target in zip(predictions, targets)]
        return sum(squared_errors) / len(squared_errors)

    def reliability_diagram_data(
        self,
        confidences: List[float],
        accuracies: List[float]
    ) -> Tuple[List[float], List[float]]:
        """
        Get data for plotting reliability diagram.

        Args:
            confidences: Confidence scores
            accuracies: Accuracy labels

        Returns:
            Tuple of (bin_confidences, bin_accuracies)
        """
        bins = self._create_bins(confidences, accuracies)

        bin_conf_means = []
        bin_acc_means = []

        for bin_conf, bin_acc in bins:
            if len(bin_conf) > 0:
                bin_conf_means.append(sum(bin_conf) / len(bin_conf))
                bin_acc_means.append(sum(bin_acc) / len(bin_acc))
            else:
                bin_conf_means.append(0.0)
                bin_acc_means.append(0.0)

        return (bin_conf_means, bin_acc_means)


# Standalone functions for convenience
def compute_ece(
    confidences: List[float],
    accuracies: List[float],
    n_bins: int = 15
) -> float:
    """
    Compute Expected Calibration Error.

    Args:
        confidences: Confidence scores [0, 1]
        accuracies: Accuracy labels (0 or 1)
        n_bins: Number of bins

    Returns:
        ECE value [0, 1]
    """
    scorer = CalibrationScorer(n_bins=n_bins)
    return scorer.compute_ece(confidences, accuracies)


def compute_brier(
    predictions: List[float],
    targets: List[float]
) -> float:
    """
    Compute Brier score.

    Args:
        predictions: Predicted probabilities [0, 1]
        targets: True labels (0 or 1)

    Returns:
        Brier score [0, 1]
    """
    scorer = CalibrationScorer()
    return scorer.compute_brier(predictions, targets)


def temperature_scaling(
    logits: List[float],
    temperature: float = 1.0
) -> List[float]:
    """
    Apply temperature scaling to logits for calibration.

    Args:
        logits: Raw model logits
        temperature: Temperature parameter (T > 1 = less confident, T < 1 = more confident)

    Returns:
        Scaled probabilities
    """
    # Apply temperature scaling
    scaled_logits = [logit / temperature for logit in logits]

    # Softmax
    exp_logits = [math.exp(logit) for logit in scaled_logits]
    sum_exp = sum(exp_logits)
    probs = [exp_logit / sum_exp for exp_logit in exp_logits]

    return probs
