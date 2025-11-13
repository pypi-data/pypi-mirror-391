# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
Metrics calculation utilities.
"""

from typing import List, Dict
import math


class MetricsCalculator:
    """
    Calculate various metrics for epistemic auditing.
    """

    @staticmethod
    def height_from_uncertainties(q1: float, q2: float) -> float:
        """
        Compute height metric from Q1 and Q2.

        Height = 1 - sqrt(Q1**2 + Q2**2)

        Args:
            q1: Aleatoric uncertainty [0, 1]
            q2: Epistemic uncertainty [0, 1]

        Returns:
            Height [0, 1]
        """
        return 1.0 - math.sqrt(q1**2 + q2**2)

    @staticmethod
    def confidence_interval(
        value: float,
        confidence_level: float = 0.95,
        margin: float = 0.05
    ) -> tuple:
        """
        Compute confidence interval.

        Args:
            value: Point estimate
            confidence_level: Confidence level (e.g., 0.95 for 95% CI)
            margin: Margin of error

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        lower = max(0.0, value - margin)
        upper = min(1.0, value + margin)
        return (lower, upper)

    @staticmethod
    def accuracy_from_height(height: float) -> float:
        """
        Estimate accuracy from height metric.

        Args:
            height: Height metric [0, 1]

        Returns:
            Estimated accuracy [0, 1]
        """
        # Placeholder: linear relationship
        # In practice, this would be learned from data
        return height

    @staticmethod
    def entropy(probabilities: List[float]) -> float:
        """
        Compute Shannon entropy.

        Args:
            probabilities: List of probabilities summing to 1

        Returns:
            Entropy value
        """
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def kl_divergence(p: List[float], q: List[float]) -> float:
        """
        Compute KL divergence between two distributions.

        KL(P||Q) = sum(P(x) * log(P(x) / Q(x)))

        Args:
            p: First probability distribution
            q: Second probability distribution

        Returns:
            KL divergence value
        """
        if len(p) != len(q):
            raise ValueError("Distributions must have same length")

        kl = 0.0
        for p_i, q_i in zip(p, q):
            if p_i > 0:
                if q_i > 0:
                    kl += p_i * math.log(p_i / q_i)
                else:
                    return float('inf')  # Infinite divergence
        return kl

    @staticmethod
    def mutual_information(
        joint_probs: List[List[float]]
    ) -> float:
        """
        Compute mutual information.

        I(X;Y) = sum sum P(x,y) log(P(x,y) / (P(x)P(y)))

        Args:
            joint_probs: 2D array of joint probabilities

        Returns:
            Mutual information value
        """
        # Compute marginals
        p_x = [sum(row) for row in joint_probs]
        p_y = [sum(col) for col in zip(*joint_probs)]

        mi = 0.0
        for i, row in enumerate(joint_probs):
            for j, p_xy in enumerate(row):
                if p_xy > 0:
                    mi += p_xy * math.log(p_xy / (p_x[i] * p_y[j]))

        return mi

    @staticmethod
    def aggregate_metrics(audits: List) -> Dict[str, float]:
        """
        Aggregate metrics across multiple audits.

        Args:
            audits: List of EpistemicAudit objects

        Returns:
            Dictionary of aggregated metrics
        """
        if not audits:
            return {}

        n = len(audits)

        return {
            "avg_q1": sum(a.q1 for a in audits) / n,
            "avg_q2": sum(a.q2 for a in audits) / n,
            "avg_height": sum(a.height for a in audits) / n,
            "avg_ece": sum(a.ece for a in audits) / n,
            "avg_brier": sum(a.brier for a in audits) / n,
            "reliable_rate": sum(1 for a in audits if a.verdict == "RELIABLE") / n,
            "uncertain_rate": sum(1 for a in audits if a.verdict == "UNCERTAIN") / n,
            "unreliable_rate": sum(1 for a in audits if a.verdict == "UNRELIABLE") / n,
        }

    @staticmethod
    def f1_score(precision: float, recall: float) -> float:
        """
        Compute F1 score.

        F1 = 2 * (precision * recall) / (precision + recall)

        Args:
            precision: Precision score
            recall: Recall score

        Returns:
            F1 score
        """
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    @staticmethod
    def auc_roc(
        true_labels: List[int],
        scores: List[float]
    ) -> float:
        """
        Compute Area Under ROC Curve (placeholder).

        Args:
            true_labels: True binary labels
            scores: Predicted scores

        Returns:
            AUC-ROC score [0, 1]
        """
        # TODO: Implement actual AUC calculation
        # Placeholder implementation
        return 0.85
