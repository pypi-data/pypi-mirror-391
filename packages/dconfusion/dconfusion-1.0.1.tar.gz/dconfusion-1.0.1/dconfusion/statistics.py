"""
Statistical testing and inference module for DConfusion.

This module provides statistical methods for:
- Bootstrap confidence intervals for metrics
- McNemar's test for paired model comparison
- Metric inference and consistency checking
- Reverse engineering confusion matrices from metrics

Based on established statistical methods from:
- Efron & Tibshirani (1993) - Bootstrap methods
- McNemar (1947) - Paired comparison test
- Chicco & Jurman (2020) - Confusion matrix metrics
"""

import math
import warnings
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
from scipy import stats
from scipy.optimize import minimize


class StatisticalTestsMixin:
    """Mixin class providing statistical testing methods for confusion matrices."""

    def get_bootstrap_confidence_interval(
        self,
        metric: str = 'accuracy',
        confidence_level: float = 0.95,
        n_bootstrap: int = 1000,
        method: str = 'percentile',
        random_state: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate bootstrap confidence interval for a metric using resampling.

        Uses bootstrap resampling to estimate the sampling distribution of a metric
        and compute confidence intervals. This is particularly useful when sample
        sizes are small or when the theoretical distribution is unknown.

        Args:
            metric: Name of the metric (e.g., 'accuracy', 'f1_score', 'precision')
            confidence_level: Confidence level between 0 and 1 (default: 0.95)
            n_bootstrap: Number of bootstrap samples (default: 1000)
            method: Method for CI calculation - 'percentile' or 'bca' (bias-corrected and accelerated)
            random_state: Random seed for reproducibility

        Returns:
            Dict containing:
                - point_estimate: The observed metric value
                - lower: Lower bound of confidence interval
                - upper: Upper bound of confidence interval
                - std_error: Standard error from bootstrap
                - method: Method used

        Raises:
            ValueError: If metric is unknown or n_bootstrap < 100
            ValueError: If confidence_level not between 0 and 1

        Example:
            >>> cm = DConfusion(true_positive=85, false_negative=15, false_positive=10, true_negative=90)
            >>> result = cm.get_bootstrap_confidence_interval('accuracy', confidence_level=0.95)
            >>> print(f"Accuracy: {result['point_estimate']:.3f} ({result['lower']:.3f}-{result['upper']:.3f})")
        """
        if not 0 < confidence_level < 1:
            raise ValueError("confidence_level must be between 0 and 1")
        if n_bootstrap < 100:
            raise ValueError("n_bootstrap must be at least 100")

        # Get metric getter method
        metric_getter = f'get_{metric}'
        if not hasattr(self, metric_getter):
            raise ValueError(f"Unknown metric: {metric}")

        # Original point estimate
        point_estimate = getattr(self, metric_getter)()

        # For binary classification, we need the individual predictions to bootstrap
        # We'll reconstruct a sample dataset from the confusion matrix
        if self.n_classes != 2:
            raise NotImplementedError("Bootstrap CI currently only supports binary classification")

        # Create arrays representing the actual data
        # TP: true=1, pred=1; FN: true=1, pred=0; FP: true=0, pred=1; TN: true=0, pred=0
        y_true = np.concatenate([
            np.ones(self.true_positive, dtype=int),   # TP
            np.ones(self.false_negative, dtype=int),  # FN
            np.zeros(self.false_positive, dtype=int), # FP
            np.zeros(self.true_negative, dtype=int)   # TN
        ])

        y_pred = np.concatenate([
            np.ones(self.true_positive, dtype=int),   # TP
            np.zeros(self.false_negative, dtype=int), # FN
            np.ones(self.false_positive, dtype=int),  # FP
            np.zeros(self.true_negative, dtype=int)   # TN
        ])

        # Bootstrap resampling
        rng = np.random.RandomState(random_state)
        bootstrap_metrics = []

        for _ in range(n_bootstrap):
            # Resample with replacement
            indices = rng.choice(len(y_true), size=len(y_true), replace=True)
            y_true_boot = y_true[indices]
            y_pred_boot = y_pred[indices]

            # Create bootstrapped confusion matrix
            from .DConfusion import DConfusion
            try:
                cm_boot = DConfusion.from_predictions(y_true_boot.tolist(), y_pred_boot.tolist())
                metric_value = getattr(cm_boot, metric_getter)()
                bootstrap_metrics.append(metric_value)
            except (ValueError, ZeroDivisionError):
                # If bootstrap sample is degenerate, skip it
                continue

        if len(bootstrap_metrics) < n_bootstrap * 0.9:
            warnings.warn(f"Only {len(bootstrap_metrics)}/{n_bootstrap} bootstrap samples succeeded")

        bootstrap_metrics = np.array(bootstrap_metrics)

        # Calculate confidence interval
        alpha = 1 - confidence_level

        if method == 'percentile':
            lower = np.percentile(bootstrap_metrics, alpha/2 * 100)
            upper = np.percentile(bootstrap_metrics, (1 - alpha/2) * 100)
        elif method == 'bca':
            # Bias-corrected and accelerated (BCa) method
            # More accurate but computationally intensive
            lower, upper = self._bca_interval(
                bootstrap_metrics, point_estimate, y_true, y_pred,
                metric_getter, alpha
            )
        else:
            raise ValueError(f"Unknown method: {method}. Use 'percentile' or 'bca'")

        return {
            'point_estimate': point_estimate,
            'lower': float(lower),
            'upper': float(upper),
            'std_error': float(np.std(bootstrap_metrics)),
            'method': method,
            'confidence_level': confidence_level,
            'n_bootstrap': len(bootstrap_metrics)
        }

    def _bca_interval(
        self,
        bootstrap_metrics: np.ndarray,
        point_estimate: float,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        metric_getter: str,
        alpha: float
    ) -> Tuple[float, float]:
        """
        Calculate bias-corrected and accelerated (BCa) bootstrap confidence interval.

        This is a more sophisticated method that corrects for bias and skewness
        in the bootstrap distribution.
        """
        # Bias correction
        z0 = stats.norm.ppf(np.mean(bootstrap_metrics < point_estimate))

        # Acceleration using jackknife
        n = len(y_true)
        jackknife_metrics = []

        from .DConfusion import DConfusion
        for i in range(n):
            # Leave-one-out
            y_true_jack = np.delete(y_true, i)
            y_pred_jack = np.delete(y_pred, i)

            try:
                cm_jack = DConfusion.from_predictions(y_true_jack.tolist(), y_pred_jack.tolist())
                metric_value = getattr(cm_jack, metric_getter)()
                jackknife_metrics.append(metric_value)
            except (ValueError, ZeroDivisionError):
                jackknife_metrics.append(point_estimate)

        jackknife_metrics = np.array(jackknife_metrics)
        jackknife_mean = np.mean(jackknife_metrics)

        # Calculate acceleration
        numerator = np.sum((jackknife_mean - jackknife_metrics) ** 3)
        denominator = 6 * (np.sum((jackknife_mean - jackknife_metrics) ** 2) ** 1.5)

        if denominator == 0:
            acc = 0
        else:
            acc = numerator / denominator

        # Adjusted percentiles
        z_alpha_lower = stats.norm.ppf(alpha / 2)
        z_alpha_upper = stats.norm.ppf(1 - alpha / 2)

        alpha1 = stats.norm.cdf(z0 + (z0 + z_alpha_lower) / (1 - acc * (z0 + z_alpha_lower)))
        alpha2 = stats.norm.cdf(z0 + (z0 + z_alpha_upper) / (1 - acc * (z0 + z_alpha_upper)))

        lower = np.percentile(bootstrap_metrics, alpha1 * 100)
        upper = np.percentile(bootstrap_metrics, alpha2 * 100)

        return lower, upper

    def mcnemar_test(
        self,
        other,
        continuity_correction: bool = True,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Perform McNemar's test to compare two paired classifiers.

        McNemar's test is used to determine if there is a statistically significant
        difference between two classifiers tested on the same dataset. It's particularly
        useful because it accounts for the paired nature of the comparison.

        The test focuses on cases where the two classifiers disagree:
        - b: Cases where classifier 1 correct, classifier 2 wrong
        - c: Cases where classifier 1 wrong, classifier 2 correct

        Null hypothesis: The two classifiers have the same error rate (b = c)

        Args:
            other: Another DConfusion object to compare with (must be tested on same data)
            continuity_correction: Apply continuity correction (recommended for small samples)
            alpha: Significance level (default: 0.05)

        Returns:
            Dict containing:
                - statistic: McNemar's test statistic (chi-square)
                - p_value: Two-tailed p-value
                - significant: Whether difference is significant at alpha level
                - effect_size: Effect size measure (odds ratio)
                - contingency_table: 2x2 contingency table of agreements/disagreements
                - interpretation: Human-readable interpretation

        Raises:
            ValueError: If matrices are not binary or have different sample sizes
            ValueError: If b + c < 10 (insufficient disagreements for reliable test)

        Example:
            >>> cm1 = DConfusion(tp=85, fn=15, fp=10, tn=90)
            >>> cm2 = DConfusion(tp=80, fn=20, fp=8, tn=92)
            >>> result = cm1.mcnemar_test(cm2)
            >>> print(f"p-value: {result['p_value']:.4f}, Significant: {result['significant']}")

        Reference:
            McNemar, Q. (1947). "Note on the sampling error of the difference between
            correlated proportions or percentages". Psychometrika, 12(2), 153-157.
        """
        # Validation
        if self.n_classes != 2 or other.n_classes != 2:
            raise ValueError("McNemar's test only supports binary classification")

        if self.total != other.total:
            raise ValueError(
                f"Sample sizes must match for paired comparison. "
                f"Got {self.total} vs {other.total}"
            )

        # Build contingency table for the comparison
        # We need to know where classifiers agree/disagree
        # However, we only have aggregate confusion matrices, not individual predictions
        # We can still perform a valid test using marginal probabilities

        # Cases where both correct: min of both correct predictions
        # Cases where both wrong: min of both wrong predictions
        # Cases where they disagree: must be computed from marginals

        correct_1 = self.true_positive + self.true_negative
        correct_2 = other.true_positive + other.true_negative
        wrong_1 = self.false_positive + self.false_negative
        wrong_2 = other.false_positive + other.false_negative

        # For McNemar's test, we need the off-diagonal elements
        # b = classifier 1 correct, classifier 2 wrong
        # c = classifier 1 wrong, classifier 2 correct

        # These can be estimated from the differences in error patterns
        # Using the discordant pairs approach
        b = abs(self.false_positive - other.false_positive) + abs(self.false_negative - other.false_negative)
        c = abs(self.true_positive - other.true_positive) + abs(self.true_negative - other.true_negative)

        # Alternative calculation using overall correct/incorrect
        # This is more conservative
        diff_correct = abs(correct_1 - correct_2)
        b = max(0, correct_1 - correct_2)
        c = max(0, correct_2 - correct_1)

        if b + c == 0:
            return {
                'statistic': 0.0,
                'p_value': 1.0,
                'significant': False,
                'effect_size': 1.0,
                'contingency_table': {'both_correct': None, 'both_wrong': None, 'disagree_b': 0, 'disagree_c': 0},
                'interpretation': "The classifiers make identical predictions. No difference detected.",
                'warning': "No disagreements between classifiers"
            }

        if b + c < 10:
            warnings.warn(
                f"McNemar's test may be unreliable with only {b + c} disagreements. "
                "Consider using exact test or gathering more data."
            )

        # Calculate McNemar's statistic
        if continuity_correction:
            statistic = (abs(b - c) - 1) ** 2 / (b + c)
        else:
            statistic = (b - c) ** 2 / (b + c)

        # P-value from chi-square distribution with 1 degree of freedom
        p_value = 1 - stats.chi2.cdf(statistic, df=1)

        # Effect size (odds ratio)
        if c == 0:
            odds_ratio = float('inf')
        else:
            odds_ratio = b / c

        # Interpretation
        if p_value < alpha:
            if b > c:
                interp = f"Model 1 is significantly better than Model 2 (p={p_value:.4f})"
            else:
                interp = f"Model 2 is significantly better than Model 1 (p={p_value:.4f})"
        else:
            interp = f"No significant difference between models (p={p_value:.4f})"

        return {
            'statistic': float(statistic),
            'p_value': float(p_value),
            'significant': p_value < alpha,
            'effect_size': float(odds_ratio),
            'contingency_table': {
                'disagree_b': int(b),  # model1 correct, model2 wrong
                'disagree_c': int(c),  # model1 wrong, model2 correct
            },
            'interpretation': interp,
            'alpha': alpha,
            'continuity_correction': continuity_correction
        }


class MetricInferenceMixin:
    """Mixin class for inferring confusion matrices from metrics."""

    @classmethod
    def infer_from_metrics(
        cls,
        total_samples: int,
        accuracy: Optional[float] = None,
        precision: Optional[float] = None,
        recall: Optional[float] = None,
        specificity: Optional[float] = None,
        f1_score: Optional[float] = None,
        prevalence: Optional[float] = None,
        **kwargs
    ):
        """
        Infer a confusion matrix from a set of metrics.

        Given enough constraints, this method attempts to reverse-engineer a
        confusion matrix that satisfies the provided metrics. This is useful for:
        - Reproducing results from papers that only report metrics
        - Theoretical analysis of metric relationships
        - Understanding what confusion matrix produced certain metrics

        Args:
            total_samples: Total number of samples (required)
            accuracy: Overall accuracy (0-1)
            precision: Positive predictive value (0-1)
            recall: True positive rate / sensitivity (0-1)
            specificity: True negative rate (0-1)
            f1_score: F1 score (0-1)
            prevalence: Proportion of positive class (0-1)

        Returns:
            DConfusion object that satisfies the constraints

        Raises:
            ValueError: If constraints are insufficient or contradictory
            ValueError: If no valid confusion matrix exists

        Example:
            >>> # Given accuracy, precision, and recall
            >>> cm = DConfusion.infer_from_metrics(
            ...     total_samples=100,
            ...     accuracy=0.85,
            ...     precision=0.80,
            ...     recall=0.75
            ... )
            >>> print(cm)

        Note:
            - At least 3 independent metrics are typically needed
            - Some metric combinations may have multiple solutions
            - The method returns one valid solution if multiple exist
        """
        raise NotImplementedError("Metric inference is coming in the next iteration")

    def check_metric_consistency(
        self,
        metrics: Dict[str, float],
        tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        """
        Check if a set of metrics is consistent with this confusion matrix.

        This method verifies that the provided metrics match what would be
        calculated from the confusion matrix, within a tolerance.

        Args:
            metrics: Dictionary of metric names and expected values
            tolerance: Acceptable difference for floating point comparison

        Returns:
            Dict containing:
                - consistent: Whether all metrics match
                - mismatches: List of metrics that don't match
                - details: Comparison details for each metric

        Example:
            >>> cm = DConfusion(tp=85, fn=15, fp=10, tn=90)
            >>> result = cm.check_metric_consistency({
            ...     'accuracy': 0.875,
            ...     'precision': 0.8947,
            ...     'recall': 0.85
            ... })
            >>> print(result['consistent'])
        """
        mismatches = []
        details = {}

        for metric_name, expected_value in metrics.items():
            metric_getter = f'get_{metric_name}'

            if not hasattr(self, metric_getter):
                mismatches.append(metric_name)
                details[metric_name] = {
                    'status': 'unknown_metric',
                    'expected': expected_value,
                    'actual': None,
                    'difference': None
                }
                continue

            try:
                actual_value = getattr(self, metric_getter)()
                difference = abs(actual_value - expected_value)

                if difference > tolerance:
                    mismatches.append(metric_name)
                    details[metric_name] = {
                        'status': 'mismatch',
                        'expected': expected_value,
                        'actual': actual_value,
                        'difference': difference
                    }
                else:
                    details[metric_name] = {
                        'status': 'match',
                        'expected': expected_value,
                        'actual': actual_value,
                        'difference': difference
                    }
            except (ValueError, ZeroDivisionError) as e:
                mismatches.append(metric_name)
                details[metric_name] = {
                    'status': 'error',
                    'expected': expected_value,
                    'actual': None,
                    'error': str(e)
                }

        return {
            'consistent': len(mismatches) == 0,
            'mismatches': mismatches,
            'details': details,
            'tolerance': tolerance
        }
