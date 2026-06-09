"""
Prim Data Mining
Provides clustering algorithms, association rule learning, feature selection,
dimensionality reduction, and text mining.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import math


class ClusteringAlgorithm(Enum):
    """Clustering algorithms"""
    K_MEANS = "k_means"
    DBSCAN = "dbscan"
    HIERARCHICAL = "hierarchical"
    MEAN_SHIFT = "mean_shift"
    GAUSSIAN_MIXTURE = "gaussian_mixture"


class AssociationRuleMethod(Enum):
    """Association rule methods"""
    APRIORI = "apriori"
    FP_GROWTH = "fp_growth"
    ECLAT = "eclat"


class DimensionalityReductionMethod(Enum):
    """Dimensionality reduction methods"""
    PCA = "pca"
    T_SNE = "t_sne"
    UMAP = "umap"
    LDA = "lda"
    AUTOENCODER = "autoencoder"


@dataclass
class Cluster:
    """Cluster"""
    id: int
    centroid: List[float]
    points: List[List[float]]
    label: str = ""


@dataclass
class AssociationRule:
    """Association rule"""
    antecedent: Set[str]
    consequent: Set[str]
    support: float
    confidence: float
    lift: float


class KMeans:
    """K-means clustering"""

    def __init__(self, k: int = 3, max_iterations: int = 100):
        self.k = k
        self.max_iterations = max_iterations
        self.centroids: Optional[List[List[float]]] = None
        self.labels: Optional[List[int]] = None

    def fit(self, data: List[List[float]]) -> 'KMeans':
        """Fit k-means model"""
        n_samples = len(data)
        n_features = len(data[0])

        # Initialize centroids randomly
        indices = np.random.choice(n_samples, self.k, replace=False)
        self.centroids = [data[i] for i in indices]

        for _ in range(self.max_iterations):
            # Assign points to clusters
            labels = []
            new_centroids = [[] for _ in range(self.k)]

            for point in data:
                distances = [self._distance(point, centroid) for centroid in self.centroids]
                cluster_id = np.argmin(distances)
                labels.append(cluster_id)
                new_centroids[cluster_id].append(point)

            # Update centroids
            new_centroids_list = []
            for cluster_points in new_centroids:
                if cluster_points:
                    new_centroid = [sum(col) / len(col) for col in zip(*cluster_points)]
                    new_centroids_list.append(new_centroid)
                else:
                    new_centroids_list.append(self.centroids[len(new_centroids_list)])

            # Check for convergence
            if all(np.allclose(old, new) for old, new in zip(self.centroids, new_centroids_list)):
                break

            self.centroids = new_centroids_list

        self.labels = labels
        return self

    def predict(self, data: List[List[float]]) -> List[int]:
        """Predict cluster labels"""
        labels = []
        for point in data:
            distances = [self._distance(point, centroid) for centroid in self.centroids]
            labels.append(np.argmin(distances))
        return labels

    def _distance(self, a: List[float], b: List[float]) -> float:
        """Calculate Euclidean distance"""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class DBSCAN:
    """DBSCAN clustering"""

    def __init__(self, eps: float = 0.5, min_samples: int = 5):
        self.eps = eps
        self.min_samples = min_samples
        self.labels: Optional[List[int]] = None

    def fit(self, data: List[List[float]]) -> 'DBSCAN':
        """Fit DBSCAN model"""
        n_samples = len(data)
        self.labels = [-1] * n_samples  # -1 = noise
        cluster_id = 0

        for i in range(n_samples):
            if self.labels[i] != -1:
                continue

            neighbors = self._region_query(data, i)

            if len(neighbors) < self.min_samples:
                self.labels[i] = -1
                continue

            self.labels[i] = cluster_id
            seeds = list(neighbors)

            while seeds:
                j = seeds.pop()

                if self.labels[j] == -1:
                    self.labels[j] = cluster_id

                if self.labels[j] != 0:
                    continue

                self.labels[j] = cluster_id
                j_neighbors = self._region_query(data, j)

                if len(j_neighbors) >= self.min_samples:
                    seeds.extend(j_neighbors)

            cluster_id += 1

        return self

    def _region_query(self, data: List[List[float]], point_idx: int) -> List[int]:
        """Query neighbors within epsilon"""
        neighbors = []
        for i, point in enumerate(data):
            if self._distance(data[point_idx], point) <= self.eps:
                neighbors.append(i)
        return neighbors

    def _distance(self, a: List[float], b: List[float]) -> float:
        """Calculate Euclidean distance"""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class Apriori:
    """Apriori algorithm for association rules"""

    def __init__(self, min_support: float = 0.1, min_confidence: float = 0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence

    def fit(self, transactions: List[List[str]]) -> 'Apriori':
        """Fit Apriori model"""
        self.transactions = transactions
        return self

    def generate_rules(self) -> List[AssociationRule]:
        """Generate association rules"""
        # Generate frequent itemsets
        frequent_itemsets = self._generate_frequent_itemsets()

        # Generate rules from frequent itemsets
        rules = []
        for itemset in frequent_itemsets:
            if len(itemset) >= 2:
                self._generate_rules_from_itemset(itemset, rules)

        return rules

    def _generate_frequent_itemsets(self) -> List[Set[str]]:
        """Generate frequent itemsets"""
        frequent_itemsets = []
        n_transactions = len(self.transactions)

        # Get all unique items
        all_items = set()
        for transaction in self.transactions:
            all_items.update(transaction)

        # Generate 1-itemsets
        c1 = [{item} for item in all_items]
        l1 = self._filter_itemsets(c1, n_transactions)

        frequent_itemsets.extend(l1)

        # Generate k-itemsets
        k = 2
        while True:
            ck = self._generate_candidates(l1 if k == 2 else frequent_itemsets, k)
            lk = self._filter_itemsets(ck, n_transactions)

            if not lk:
                break

            frequent_itemsets.extend(lk)
            k += 1

        return frequent_itemsets

    def _generate_candidates(self, itemsets: List[Set[str]], k: int) -> List[Set[str]]:
        """Generate candidate itemsets"""
        candidates = []
        n = len(itemsets)

        for i in range(n):
            for j in range(i + 1, n):
                itemset1 = list(itemsets[i])
                itemset2 = list(itemsets[j])

                # Check if k-2 items are common
                if len(set(itemset1) & set(itemset2)) == k - 2:
                    candidate = set(itemset1) | set(itemset2)
                    if len(candidate) == k:
                        candidates.append(candidate)

        return candidates

    def _filter_itemsets(self, itemsets: List[Set[str]], n_transactions: int) -> List[Set[str]]:
        """Filter itemsets by minimum support"""
        frequent = []

        for itemset in itemsets:
            support = sum(1 for t in self.transactions if itemset.issubset(set(t))) / n_transactions
            if support >= self.min_support:
                frequent.append(itemset)

        return frequent

    def _generate_rules_from_itemset(self, itemset: Set[str], rules: List[AssociationRule]):
        """Generate rules from itemset"""
        itemset_list = list(itemset)

        for i in range(len(itemset_list)):
            for j in range(i + 1, len(itemset_list)):
                antecedent = {itemset_list[i]}
                consequent = {itemset_list[j]}

                # Calculate support and confidence
                support = self._calculate_support(antecedent | consequent)
                confidence = self._calculate_confidence(antecedent, consequent)

                if confidence >= self.min_confidence:
                    lift = self._calculate_lift(antecedent, consequent)
                    rules.append(AssociationRule(antecedent, consequent, support, confidence, lift))

    def _calculate_support(self, itemset: Set[str]) -> float:
        """Calculate support"""
        return sum(1 for t in self.transactions if itemset.issubset(set(t))) / len(self.transactions)

    def _calculate_confidence(self, antecedent: Set[str], consequent: Set[str]) -> float:
        """Calculate confidence"""
        support_antecedent = self._calculate_support(antecedent)
        support_both = self._calculate_support(antecedent | consequent)
        return support_both / support_antecedent if support_antecedent > 0 else 0

    def _calculate_lift(self, antecedent: Set[str], consequent: Set[str]) -> float:
        """Calculate lift"""
        support_antecedent = self._calculate_support(antecedent)
        support_consequent = self._calculate_support(consequent)
        support_both = self._calculate_support(antecedent | consequent)
        return support_both / (support_antecedent * support_consequent) if support_antecedent * support_consequent > 0 else 0


class FeatureSelector:
    """Feature selection"""

    @staticmethod
    def select_k_best(data: List[List[float]], target: List[int], k: int) -> List[int]:
        """Select top k features"""
        from sklearn.feature_selection import SelectKBest, f_classif
        selector = SelectKBest(f_classif, k=k)
        selector.fit(data, target)
        selected = selector.get_support(indices=True)
        return list(selected)

    @staticmethod
    def variance_threshold(data: List[List[float]], threshold: float = 0.0) -> List[int]:
        """Select features with variance above threshold"""
        variances = np.var(data, axis=0)
        selected = [i for i, var in enumerate(variances) if var > threshold]
        return selected


class DimensionalityReducer:
    """Dimensionality reduction"""

    @staticmethod
    def pca(data: List[List[float]], n_components: int = 2) -> List[List[float]]:
        """Principal Component Analysis"""
        from sklearn.decomposition import PCA
        pca = PCA(n_components=n_components)
        reduced = pca.fit_transform(data)
        return reduced.tolist()


class TextMining:
    """Text mining"""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text"""
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    @staticmethod
    def remove_stopwords(tokens: List[str], stopwords: Optional[Set[str]] = None) -> List[str]:
        """Remove stopwords"""
        if stopwords is None:
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [token for token in tokens if token not in stopwords]

    @staticmethod
    def stem(tokens: List[str]) -> List[str]:
        """Stem tokens"""
        from nltk.stem import PorterStemmer
        stemmer = PorterStemmer()
        return [stemmer.stem(token) for token in tokens]

    @staticmethod
    def calculate_tf_idf(documents: List[List[str]]) -> Dict[str, Dict[str, float]]:
        """Calculate TF-IDF scores"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([' '.join(doc) for doc in documents])

        feature_names = vectorizer.get_feature_names_out()
        results = {}

        for i, doc in enumerate(documents):
            doc_scores = {}
            for j, word in enumerate(feature_names):
                score = tfidf_matrix[i, j]
                if score > 0:
                    doc_scores[word] = float(score)
            results[f"doc_{i}"] = doc_scores

        return results

    @staticmethod
    def sentiment_analysis(text: str) -> Dict[str, float]:
        """Sentiment analysis"""
        from textblob import TextBlob
        blob = TextBlob(text)
        sentiment = blob.sentiment

        return {
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity
        }


def main():
    """Main entry point for testing"""
    print("Testing Data Mining...")

    # Test K-Means
    kmeans = KMeans(k=3)
    data = [[1, 1], [1, 2], [2, 1], [8, 8], [8, 9], [9, 8], [5, 5]]
    kmeans.fit(data)
    labels = kmeans.predict(data)
    print(f"K-Means labels: {labels}")

    # Test DBSCAN
    dbscan = DBSCAN(eps=2, min_samples=2)
    dbscan.fit(data)
    print(f"DBSCAN labels: {dbscan.labels}")

    # Test Apriori
    apriori = Apriori(min_support=0.3, min_confidence=0.7)
    transactions = [
        ["milk", "bread", "eggs"],
        ["bread", "butter", "cheese"],
        ["milk", "bread", "butter"],
        ["eggs", "cheese", "milk"]
    ]
    apriori.fit(transactions)
    rules = apriori.generate_rules()
    print(f"Association rules: {len(rules)}")

    # Test Feature Selection
    fs = FeatureSelector()
    selected = fs.variance_threshold(data, threshold=0.5)
    print(f"Selected features: {selected}")

    # Test PCA
    dr = DimensionalityReducer()
    reduced = dr.pca(data, n_components=2)
    print(f"PCA reduced: {len(reduced)} samples, {len(reduced[0])} dimensions")

    # Test Text Mining
    tm = TextMining()
    text = "The quick brown fox jumps over the lazy dog."
    tokens = tm.tokenize(text)
    tokens = tm.remove_stopwords(tokens)
    print(f"Tokens: {tokens[:5]}")

    # Test Sentiment Analysis
    sentiment = tm.sentiment_analysis("I love this product! It's amazing.")
    print(f"Sentiment: polarity={sentiment['polarity']:.2f}, subjectivity={sentiment['subjectivity']:.2f}")

    print("\nData Mining initialized successfully")


if __name__ == "__main__":
    main()
