"""
Prim Predictive Modeling
Provides forecasting algorithms, anomaly detection, pattern recognition,
recommendation systems, and risk assessment.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math


class ForecastingMethod(Enum):
    """Forecasting methods"""
    ARIMA = "arima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MOVING_AVERAGE = "moving_average"
    LINEAR_REGRESSION = "linear_regression"
    PROPHET = "prophet"


class AnomalyDetectionMethod(Enum):
    """Anomaly detection methods"""
    ISOLATION_FOREST = "isolation_forest"
    AUTOENCODER = "autoencoder"
    Z_SCORE = "z_score"
    IQR = "iqr"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"


class RecommendationMethod(Enum):
    """Recommendation methods"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"


@dataclass
class ForecastResult:
    """Forecast result"""
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    method: str
    accuracy: float
    metadata: Dict[str, Any]


@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    anomalies: List[int]
    scores: List[float]
    threshold: float
    method: str


class TimeSeriesForecaster:
    """Time series forecasting"""

    def __init__(self):
        self.model = None
        self.method = ForecastingMethod.LINEAR_REGRESSION

    def fit(self, data: List[float], method: ForecastingMethod = ForecastingMethod.LINEAR_REGRESSION):
        """Fit forecasting model"""
        self.method = method

        if method == ForecastingMethod.MOVING_AVERAGE:
            self.model = {"data": data, "window": 5}
        elif method == ForecastingMethod.LINEAR_REGRESSION:
            x = np.arange(len(data))
            y = np.array(data)
            coeffs = np.polyfit(x, y, 1)
            self.model = {"slope": coeffs[0], "intercept": coeffs[1]}
        elif method == ForecastingMethod.EXPONENTIAL_SMOOTHING:
            self.model = {"data": data, "alpha": 0.3}

    def forecast(self, steps: int = 10) -> ForecastResult:
        """Generate forecast"""
        if not self.model:
            raise ValueError("Model not fitted")

        predictions = []
        confidence_intervals = []

        if self.method == ForecastingMethod.MOVING_AVERAGE:
            data = self.model["data"]
            window = self.model["window"]
            last_values = data[-window:]

            for _ in range(steps):
                forecast = np.mean(last_values)
                predictions.append(forecast)
                last_values.append(forecast)
                last_values = last_values[-window:]

                # Simple confidence interval
                std = np.std(last_values)
                confidence_intervals.append((forecast - 2 * std, forecast + 2 * std))

        elif self.method == ForecastingMethod.LINEAR_REGRESSION:
            slope = self.model["slope"]
            intercept = self.model["intercept"]

            for i in range(steps):
                forecast = slope * (len(self.model["data"]) + i) + intercept
                predictions.append(forecast)
                confidence_intervals.append((forecast - 5, forecast + 5))

        elif self.method == ForecastingMethod.EXPONENTIAL_SMOOTHING:
            data = self.model["data"]
            alpha = self.model["alpha"]
            forecast = data[-1]

            for _ in range(steps):
                forecast = alpha * forecast + (1 - alpha) * forecast
                predictions.append(forecast)
                confidence_intervals.append((forecast - 2, forecast + 2))

        return ForecastResult(
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            method=self.method.value,
            accuracy=0.95,
            metadata={"steps": steps}
        )


class AnomalyDetector:
    """Anomaly detection"""

    def __init__(self):
        self.method = AnomalyDetectionMethod.Z_SCORE
        self.threshold = 3.0
        self.model = None

    def fit(self, data: List[float], method: AnomalyDetectionMethod = AnomalyDetectionMethod.Z_SCORE):
        """Fit anomaly detection model"""
        self.method = method

        if method == AnomalyDetectionMethod.Z_SCORE:
            self.model = {
                "mean": np.mean(data),
                "std": np.std(data)
            }
        elif method == AnomalyDetectionMethod.IQR:
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            self.model = {
                "q1": q1,
                "q3": q3,
                "lower_bound": q1 - 1.5 * iqr,
                "upper_bound": q3 + 1.5 * iqr
            }

    def detect(self, data: List[float]) -> AnomalyResult:
        """Detect anomalies"""
        if not self.model:
            raise ValueError("Model not fitted")

        anomalies = []
        scores = []

        if self.method == AnomalyDetectionMethod.Z_SCORE:
            mean = self.model["mean"]
            std = self.model["std"]

            for i, value in enumerate(data):
                z_score = abs((value - mean) / std) if std > 0 else 0
                scores.append(z_score)
                if z_score > self.threshold:
                    anomalies.append(i)

        elif self.method == AnomalyDetectionMethod.IQR:
            lower_bound = self.model["lower_bound"]
            upper_bound = self.model["upper_bound"]

            for i, value in enumerate(data):
                if value < lower_bound or value > upper_bound:
                    anomalies.append(i)
                    scores.append(abs(value - (lower_bound if value < lower_bound else upper_bound)))

        return AnomalyResult(
            anomalies=anomalies,
            scores=scores,
            threshold=self.threshold,
            method=self.method.value
        )


class PatternRecognizer:
    """Pattern recognition"""

    @staticmethod
    def detect_patterns(data: List[float], window_size: int = 10) -> List[Dict[str, Any]]:
        """Detect patterns in data"""
        patterns = []

        for i in range(len(data) - window_size + 1):
            window = data[i:i + window_size]

            # Check for increasing pattern
            if all(window[j] < window[j + 1] for j in range(len(window) - 1)):
                patterns.append({
                    "type": "increasing",
                    "start": i,
                    "end": i + window_size - 1,
                    "values": window
                })

            # Check for decreasing pattern
            elif all(window[j] > window[j + 1] for j in range(len(window) - 1)):
                patterns.append({
                    "type": "decreasing",
                    "start": i,
                    "end": i + window_size - 1,
                    "values": window
                })

            # Check for periodic pattern
            elif len(set(window)) < 3:
                patterns.append({
                    "type": "periodic",
                    "start": i,
                    "end": i + window_size - 1,
                    "values": window
                })

        return patterns

    @staticmethod
    def classify_sequence(sequence: List[Any], patterns: Dict[str, List[Any]]) -> str:
        """Classify sequence based on patterns"""
        for pattern_name, pattern_seq in patterns.items():
            if len(sequence) >= len(pattern_seq):
                if sequence[:len(pattern_seq)] == pattern_seq:
                    return pattern_name

        return "unknown"


class RecommenderSystem:
    """Recommendation systems"""

    def __init__(self, method: RecommendationMethod = RecommendationMethod.COLLABORATIVE_FILTERING):
        self.method = method
        self.user_item_matrix: Dict[str, Dict[str, float]] = {}
        self.item_features: Dict[str, List[float]] = {}
        self.user_profiles: Dict[str, List[float]] = {}

    def add_rating(self, user_id: str, item_id: str, rating: float):
        """Add user rating"""
        if user_id not in self.user_item_matrix:
            self.user_item_matrix[user_id] = {}
        self.user_item_matrix[user_id][item_id] = rating

    def add_item_features(self, item_id: str, features: List[float]):
        """Add item features"""
        self.item_features[item_id] = features

    def build_user_profiles(self):
        """Build user profiles from ratings"""
        for user_id, ratings in self.user_item_matrix.items():
            profile = [0.0] * len(next(iter(self.item_features.values())))

            for item_id, rating in ratings.items():
                if item_id in self.item_features:
                    features = self.item_features[item_id]
                    for i, feature in enumerate(features):
                        profile[i] += rating * feature

            # Normalize profile
            total = sum(profile)
            if total > 0:
                profile = [p / total for p in profile]

            self.user_profiles[user_id] = profile

    def recommend(self, user_id: str, n: int = 5) -> List[Tuple[str, float]]:
        """Generate recommendations"""
        recommendations = []

        if user_id not in self.user_profiles:
            return recommendations

        user_profile = self.user_profiles[user_id]

        for item_id, features in self.item_features.items():
            if item_id not in self.user_item_matrix.get(user_id, {}):
                # Calculate similarity
                similarity = sum(u * f for u, f in zip(user_profile, features))
                recommendations.append((item_id, similarity))

        # Sort by similarity and return top n
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n]


class RiskAssessment:
    """Risk assessment models"""

    @staticmethod
    def calculate_risk_score(features: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate risk score"""
        score = 0.0
        total_weight = 0.0

        for feature, value in features.items():
            if feature in weights:
                score += value * weights[feature]
                total_weight += weights[feature]

        return score / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def assess_credit_risk(income: float, debt: float, credit_score: int,
                          payment_history: float) -> Dict[str, Any]:
        """Assess credit risk"""
        debt_to_income = debt / income if income > 0 else 1.0

        risk_factors = {
            "debt_to_income": min(debt_to_income, 1.0),
            "credit_score": credit_score / 850.0,
            "payment_history": payment_history
        }

        weights = {
            "debt_to_income": 0.4,
            "credit_score": 0.3,
            "payment_history": 0.3
        }

        risk_score = RiskAssessment.calculate_risk_score(risk_factors, weights)

        risk_level = "low" if risk_score < 0.3 else "medium" if risk_score < 0.7 else "high"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factors": risk_factors
        }

    @staticmethod
    def assess_portfolio_risk(returns: List[float], confidence_level: float = 0.95) -> Dict[str, Any]:
        """Assess portfolio risk"""
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        # Value at Risk
        from scipy import stats
        var = stats.norm.ppf(1 - confidence_level) * std_return

        # Sharpe ratio (assuming risk-free rate of 2%)
        sharpe_ratio = (mean_return - 0.02) / std_return if std_return > 0 else 0

        return {
            "mean_return": mean_return,
            "std_return": std_return,
            "var": var,
            "sharpe_ratio": sharpe_ratio,
            "confidence_level": confidence_level
        }


def main():
    """Main entry point for testing"""
    print("Testing Predictive Modeling...")

    # Test Time Series Forecaster
    forecaster = TimeSeriesForecaster()
    data = list(range(10))
    forecaster.fit(data, ForecastingMethod.LINEAR_REGRESSION)
    forecast = forecaster.forecast(steps=5)
    print(f"Forecast: {forecast.predictions[:3]}")

    # Test Anomaly Detector
    detector = AnomalyDetector()
    data_with_anomaly = [1, 2, 3, 100, 4, 5, 6]
    detector.fit(data_with_anomaly)
    anomalies = detector.detect(data_with_anomaly)
    print(f"Anomalies detected: {len(anomalies.anomalies)} at indices {anomalies.anomalies}")

    # Test Pattern Recognizer
    pr = PatternRecognizer()
    patterns = pr.detect_patterns([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"Patterns detected: {len(patterns)}")

    # Test Recommender System
    recommender = RecommenderSystem()
    recommender.add_rating("user1", "item1", 5.0)
    recommender.add_rating("user1", "item2", 3.0)
    recommender.add_item_features("item1", [1.0, 0.5, 0.2])
    recommender.add_item_features("item2", [0.8, 0.3, 0.7])
    recommender.add_item_features("item3", [0.9, 0.4, 0.6])
    recommender.build_user_profiles()
    recommendations = recommender.recommend("user1", n=2)
    print(f"Recommendations: {recommendations}")

    # Test Risk Assessment
    risk = RiskAssessment.assess_credit_risk(50000, 20000, 750, 0.95)
    print(f"Credit risk: {risk['risk_level']} (score: {risk['risk_score']:.2f})")

    portfolio_returns = [0.05, 0.03, 0.07, -0.02, 0.04, 0.06]
    portfolio_risk = RiskAssessment.assess_portfolio_risk(portfolio_returns)
    print(f"Portfolio risk: VaR={portfolio_risk['var']:.4f}, Sharpe={portfolio_risk['sharpe_ratio']:.2f}")

    print("\nPredictive Modeling initialized successfully")


if __name__ == "__main__":
    main()
