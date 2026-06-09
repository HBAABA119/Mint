"""
Prim Statistical Analysis
Provides advanced statistical methods, hypothesis testing, regression analysis,
time series analysis, and Bayesian inference.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math


class TestType(Enum):
    """Statistical test types"""
    T_TEST = "t_test"
    ANOVA = "anova"
    CHI_SQUARE = "chi_square"
    MANN_WHITNEY = "mann_whitney"
    KRUSKAL_WALLIS = "kruskal_wallis"


class RegressionType(Enum):
    """Regression types"""
    LINEAR = "linear"
    LOGISTIC = "logistic"
    POLYNOMIAL = "polynomial"
    RIDGE = "ridge"
    LASSO = "lasso"


@dataclass
class TestResult:
    """Statistical test result"""
    test_name: str
    statistic: float
    p_value: float
    critical_value: Optional[float] = None
    significant: bool = False
    confidence_level: float = 0.95
    interpretation: str = ""


class HypothesisTesting:
    """Hypothesis testing framework"""

    @staticmethod
    def t_test(sample: List[float], mu: float = 0, alternative: str = "two-sided") -> TestResult:
        """One-sample t-test"""
        n = len(sample)
        sample_mean = np.mean(sample)
        sample_std = np.std(sample, ddof=1)

        t_statistic = (sample_mean - mu) / (sample_std / math.sqrt(n))
        degrees_of_freedom = n - 1

        # Calculate p-value (simplified)
        from scipy import stats
        if alternative == "two-sided":
            p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), degrees_of_freedom))
        elif alternative == "greater":
            p_value = 1 - stats.t.cdf(t_statistic, degrees_of_freedom)
        else:
            p_value = stats.t.cdf(t_statistic, degrees_of_freedom)

        significant = p_value < 0.05

        return TestResult(
            test_name="One-sample t-test",
            statistic=t_statistic,
            p_value=p_value,
            significant=significant,
            interpretation=f"{'Reject' if significant else 'Fail to reject'} null hypothesis (p={p_value:.4f})"
        )

    @staticmethod
    def paired_t_test(sample1: List[float], sample2: List[float]) -> TestResult:
        """Paired t-test"""
        differences = [s1 - s2 for s1, s2 in zip(sample1, sample2)]
        return HypothesisTesting.t_test(differences, mu=0)

    @staticmethod
    def anova(*samples: List[float]) -> TestResult:
        """One-way ANOVA"""
        from scipy import stats
        f_statistic, p_value = stats.f_oneway(*samples)

        significant = p_value < 0.05

        return TestResult(
            test_name="One-way ANOVA",
            statistic=f_statistic,
            p_value=p_value,
            significant=significant,
            interpretation=f"{'Reject' if significant else 'Fail to reject'} null hypothesis (p={p_value:.4f})"
        )

    @staticmethod
    def chi_square_test(observed: List[int], expected: List[int]) -> TestResult:
        """Chi-square goodness of fit test"""
        from scipy import stats
        chi2_stat, p_value = stats.chisquare(f_obs=observed, f_exp=expected)

        significant = p_value < 0.05

        return TestResult(
            test_name="Chi-square test",
            statistic=chi2_stat,
            p_value=p_value,
            significant=significant,
            interpretation=f"{'Reject' if significant else 'Fail to reject'} null hypothesis (p={p_value:.4f})"
        )


class RegressionAnalysis:
    """Regression analysis"""

    @staticmethod
    def linear_regression(x: List[float], y: List[float]) -> Dict[str, Any]:
        """Linear regression"""
        x_array = np.array(x)
        y_array = np.array(y)

        # Calculate coefficients
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x ** 2)
        sum_y2 = np.sum(y ** 2)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared
        y_mean = np.mean(y)
        ss_total = np.sum((y - y_mean) ** 2)
        ss_residual = np.sum((y - (slope * x + intercept)) ** 2)
        r_squared = 1 - (ss_residual / ss_total)

        # Calculate standard error
        residuals = y - (slope * x + intercept)
        std_error = np.sqrt(np.sum(residuals ** 2) / (n - 2))

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "std_error": std_error,
            "equation": f"y = {slope:.4f}x + {intercept:.4f}"
        }

    @staticmethod
    def logistic_regression(x: List[List[float]], y: List[int], iterations: int = 1000,
                           learning_rate: float = 0.01) -> Dict[str, Any]:
        """Logistic regression"""
        n_samples = len(x)
        n_features = len(x[0])
        weights = [0.0] * n_features
        bias = 0.0

        for _ in range(iterations):
            for i in range(n_samples):
                z = sum(w * xi for w, xi in zip(weights, x[i])) + bias
                prediction = 1.0 / (1.0 + math.exp(-z))
                error = y[i] - prediction

                weights = [w + learning_rate * error * xi for w, xi in zip(weights, x[i])]
                bias += learning_rate * error

        return {
            "weights": weights,
            "bias": bias,
            "iterations": iterations
        }

    @staticmethod
    def polynomial_regression(x: List[float], y: List[float], degree: int) -> Dict[str, Any]:
        """Polynomial regression"""
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression

        poly_features = PolynomialFeatures(degree=degree)
        x_poly = poly_features.fit_transform(np.array(x).reshape(-1, 1))

        model = LinearRegression()
        model.fit(x_poly, y)

        return {
            "coefficients": list(model.coef_),
            "intercept": model.intercept_,
            "degree": degree,
            "r_squared": model.score(x_poly, y)
        }


class TimeSeriesAnalysis:
    """Time series analysis"""

    @staticmethod
    def moving_average(data: List[float], window: int) -> List[float]:
        """Calculate moving average"""
        return [np.mean(data[i:i + window]) for i in range(len(data) - window + 1)]

    @staticmethod
    def exponential_smoothing(data: List[float], alpha: float = 0.3) -> List[float]:
        """Exponential smoothing"""
        smoothed = [data[0]]
        for i in range(1, len(data)):
            smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[-1])
        return smoothed

    @staticmethod
    def detrend(data: List[float]) -> List[float]:
        """Remove trend from time series"""
        x = np.arange(len(data))
        y = np.array(data)

        # Fit linear trend
        coeffs = np.polyfit(x, y, 1)
        trend = np.polyval(coeffs, x)

        # Remove trend
        detrended = y - trend
        return list(detrended)

    @staticmethod
    def autocorrelation(data: List[float], max_lag: int = 10) -> List[float]:
        """Calculate autocorrelation"""
        n = len(data)
        mean = np.mean(data)
        variance = np.var(data)

        autocorr = []
        for lag in range(max_lag + 1):
            if lag == 0:
                autocorr.append(1.0)
            else:
                cov = np.sum((data[:n - lag] - mean) * (data[lag:] - mean)) / n
                autocorr.append(cov / variance)

        return autocorr


class BayesianInference:
    """Bayesian inference"""

    @staticmethod
    def bayesian_update(prior_mean: float, prior_std: float,
                        likelihood_mean: float, likelihood_std: float,
                        sample_mean: float, sample_size: int) -> Tuple[float, float]:
        """Bayesian update for normal distribution"""
        # Calculate posterior parameters
        prior_precision = 1.0 / (prior_std ** 2)
        likelihood_precision = sample_size / (likelihood_std ** 2)

        posterior_precision = prior_precision + likelihood_precision
        posterior_mean = (prior_precision * prior_mean + likelihood_precision * sample_mean) / posterior_precision
        posterior_std = math.sqrt(1.0 / posterior_precision)

        return posterior_mean, posterior_std

    @staticmethod
    def mcmc_sample(log_posterior: Callable, initial: List[float], iterations: int = 1000,
                    proposal_std: float = 1.0) -> List[List[float]]:
        """Markov Chain Monte Carlo sampling"""
        samples = [initial.copy()]

        for i in range(iterations):
            current = samples[-1].copy()

            # Propose new state
            proposed = [np.random.normal(x, proposal_std) for x in current]

            # Calculate acceptance probability
            log_post_current = log_posterior(current)
            log_post_proposed = log_posterior(proposed)

            acceptance_prob = min(1.0, math.exp(log_post_proposed - log_post_current))

            # Accept or reject
            if np.random.random() < acceptance_prob:
                samples.append(proposed)
            else:
                samples.append(current)

        return samples

    @staticmethod
    def conjugate_prior(alpha: int, beta: int, successes: int, failures: int) -> Tuple[float, float]:
        """Conjugate prior for binomial distribution"""
        posterior_alpha = alpha + successes
        posterior_beta = beta + failures

        posterior_mean = posterior_alpha / (posterior_alpha + posterior_beta)
        posterior_std = math.sqrt((posterior_alpha * posterior_beta) /
                                  ((posterior_alpha + posterior_beta) ** 2 *
                                   (posterior_alpha + posterior_beta + 1)))

        return posterior_mean, posterior_std


class AdvancedStatistics:
    """Advanced statistical methods"""

    @staticmethod
    def bootstrap(data: List[float], statistic: Callable, n_bootstrap: int = 1000,
                  confidence_level: float = 0.95) -> Tuple[float, List[float]]:
        """Bootstrap confidence interval"""
        n = len(data)
        bootstrap_stats = []

        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=n, replace=True)
            bootstrap_stats.append(statistic(sample))

        # Calculate confidence interval
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        lower = np.percentile(bootstrap_stats, lower_percentile)
        upper = np.percentile(bootstrap_stats, upper_percentile)
        estimate = np.mean(bootstrap_stats)

        return estimate, [lower, upper]

    @staticmethod
    def permutation_test(group1: List[float], group2: List[float],
                        n_permutations: int = 1000) -> TestResult:
        """Permutation test"""
        observed_diff = np.mean(group1) - np.mean(group2)
        combined = group1 + group2
        n1 = len(group1)

        extreme_count = 0
        for _ in range(n_permutations):
            np.random.shuffle(combined)
            perm_group1 = combined[:n1]
            perm_group2 = combined[n1:]
            perm_diff = np.mean(perm_group1) - np.mean(perm_group2)

            if abs(perm_diff) >= abs(observed_diff):
                extreme_count += 1

        p_value = extreme_count / n_permutations

        return TestResult(
            test_name="Permutation test",
            statistic=observed_diff,
            p_value=p_value,
            significant=p_value < 0.05,
            interpretation=f"{'Reject' if p_value < 0.05 else 'Fail to reject'} null hypothesis (p={p_value:.4f})"
        )

    @staticmethod
    def effect_size(group1: List[float], group2: List[float]) -> float:
        """Calculate Cohen's d effect size"""
        mean1 = np.mean(group1)
        mean2 = np.mean(group2)
        pooled_std = math.sqrt(((len(group1) - 1) * np.var(group1) +
                               (len(group2) - 1) * np.var(group2)) /
                              (len(group1) + len(group2) - 2))

        return (mean1 - mean2) / pooled_std


def main():
    """Main entry point for testing"""
    print("Testing Statistical Analysis...")

    # Test Hypothesis Testing
    ht = HypothesisTesting()
    sample = [1.2, 1.5, 1.8, 2.0, 2.2]
    result = ht.t_test(sample, mu=1.5)
    print(f"T-test: {result.statistic:.4f}, p={result.p_value:.4f}")

    # Test ANOVA
    group1 = [1.2, 1.5, 1.8]
    group2 = [2.0, 2.3, 2.6]
    group3 = [2.8, 3.1, 3.4]
    anova_result = ht.anova(group1, group2, group3)
    print(f"ANOVA: F={anova_result.statistic:.4f}, p={anova_result.p_value:.4f}")

    # Test Regression
    ra = RegressionAnalysis()
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    lin_reg = ra.linear_regression(x, y)
    print(f"Linear regression: {lin_reg['equation']}, R²={lin_reg['r_squared']:.4f}")

    # Test Time Series
    ts = TimeSeriesAnalysis()
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ma = ts.moving_average(data, window=3)
    print(f"Moving average: {ma[:3]}")

    # Test Bayesian Inference
    bi = BayesianInference()
    post_mean, post_std = bi.bayesian_update(0, 1, 0, 1, 0.5, 10)
    print(f"Bayesian update: mean={post_mean:.4f}, std={post_std:.4f}")

    # Test Bootstrap
    adv = AdvancedStatistics()
    estimate, ci = adv.bootstrap(sample, np.mean, n_bootstrap=100)
    print(f"Bootstrap: estimate={estimate:.4f}, CI=[{ci[0]:.4f}, {ci[1]:.4f}]")

    print("\nStatistical Analysis initialized successfully")


if __name__ == "__main__":
    main()
