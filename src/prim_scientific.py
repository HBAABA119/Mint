"""
Prim Scientific Computing
Provides linear algebra operations, numerical methods, optimization algorithms,
signal processing, and mathematical modeling.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class Matrix:
    """Matrix operations"""

    def __init__(self, data: List[List[float]]):
        self.data = np.array(data)
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0

    @staticmethod
    def zeros(rows: int, cols: int) -> 'Matrix':
        """Create zero matrix"""
        return Matrix([[0.0] * cols for _ in range(rows)])

    @staticmethod
    def identity(n: int) -> 'Matrix':
        """Create identity matrix"""
        return Matrix([[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)])

    @staticmethod
    def random(rows: int, cols: int) -> 'Matrix':
        """Create random matrix"""
        return Matrix(np.random.randn(rows, cols).tolist())

    def __add__(self, other: 'Matrix') -> 'Matrix':
        """Matrix addition"""
        return Matrix((self.data + other.data).tolist())

    def __sub__(self, other: 'Matrix') -> 'Matrix':
        """Matrix subtraction"""
        return Matrix((self.data - other.data).tolist())

    def __mul__(self, scalar: float) -> 'Matrix':
        """Scalar multiplication"""
        return Matrix((self.data * scalar).tolist())

    def matmul(self, other: 'Matrix') -> 'Matrix':
        """Matrix multiplication"""
        return Matrix(np.dot(self.data, other.data).tolist())

    def transpose(self) -> 'Matrix':
        """Matrix transpose"""
        return Matrix(self.data.T.tolist())

    def inverse(self) -> 'Matrix':
        """Matrix inverse"""
        return Matrix(np.linalg.inv(self.data).tolist())

    def determinant(self) -> float:
        """Matrix determinant"""
        return np.linalg.det(self.data)

    def eigenvalues(self) -> List[float]:
        """Eigenvalues"""
        return list(np.linalg.eigvals(self.data))

    def eigenvectors(self) -> 'Matrix':
        """Eigenvectors"""
        eigenvalues, eigenvectors = np.linalg.eig(self.data)
        return Matrix(eigenvectors.tolist())

    def solve(self, b: List[float]) -> List[float]:
        """Solve Ax = b"""
        return list(np.linalg.solve(self.data, b))

    def svd(self) -> Tuple['Matrix', List[float], 'Matrix']:
        """Singular value decomposition"""
        U, S, Vt = np.linalg.svd(self.data)
        return Matrix(U.tolist()), list(S), Matrix(Vt.tolist())

    def norm(self, ord: int = 2) -> float:
        """Matrix norm"""
        return np.linalg.norm(self.data, ord=ord)

    def rank(self) -> int:
        """Matrix rank"""
        return np.linalg.matrix_rank(self.data)


class LinearAlgebra:
    """Linear algebra operations"""

    @staticmethod
    def dot(a: List[float], b: List[float]) -> float:
        """Dot product"""
        return np.dot(a, b)

    @staticmethod
    def cross(a: List[float], b: List[float]) -> List[float]:
        """Cross product"""
        return list(np.cross(a, b))

    @staticmethod
    def norm(vector: List[float], ord: int = 2) -> float:
        """Vector norm"""
        return np.linalg.norm(vector, ord=ord)

    @staticmethod
    def normalize(vector: List[float]) -> List[float]:
        """Normalize vector"""
        norm = np.linalg.norm(vector)
        return [v / norm for v in vector]

    @staticmethod
    def distance(a: List[float], b: List[float]) -> float:
        """Euclidean distance"""
        return np.linalg.norm(np.array(a) - np.array(b))

    @staticmethod
    def angle_between(a: List[float], b: List[float]) -> float:
        """Angle between vectors"""
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return np.arccos(dot / (norm_a * norm_b))


class NumericalMethods:
    """Numerical methods"""

    @staticmethod
    def integrate(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
        """Numerical integration using Simpson's rule"""
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = np.array([f(xi) for xi in x])

        # Simpson's rule
        integral = y[0] + y[-1]
        integral += 4 * np.sum(y[1:-1:2])
        integral += 2 * np.sum(y[2:-2:2])
        return (h / 3) * integral

    @staticmethod
    def differentiate(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
        """Numerical derivative"""
        return (f(x + h) - f(x - h)) / (2 * h)

    @staticmethod
    def root_bisection(f: Callable[[float], float], a: float, b: float, tol: float = 1e-6) -> float:
        """Find root using bisection method"""
        while (b - a) / 2 > tol:
            c = (a + b) / 2
            if f(c) == 0:
                return c
            elif f(a) * f(c) < 0:
                b = c
            else:
                a = c
        return (a + b) / 2

    @staticmethod
    def root_newton(f: Callable[[float], float], df: Callable[[float], float],
                     x0: float, tol: float = 1e-6, max_iter: int = 100) -> float:
        """Find root using Newton's method"""
        x = x0
        for _ in range(max_iter):
            fx = f(x)
            dfx = df(x)
            if dfx == 0:
                break
            x_new = x - fx / dfx
            if abs(x_new - x) < tol:
                return x_new
            x = x_new
        return x

    @staticmethod
    def solve_ode(f: Callable[[float, float], float], y0: float, t0: float, t_end: float,
                    h: float = 0.01) -> List[Tuple[float, float]]:
        """Solve ODE using Euler's method"""
        t = t0
        y = y0
        results = [(t, y)]

        while t < t_end:
            y += h * f(t, y)
            t += h
            results.append((t, y))

        return results


class Optimization:
    """Optimization algorithms"""

    @staticmethod
    def gradient_descent(f: Callable[[List[float]], float], df: Callable[[List[float]], List[float]],
                         x0: List[float], learning_rate: float = 0.01, max_iter: int = 1000) -> List[float]:
        """Gradient descent optimization"""
        x = x0.copy()
        for _ in range(max_iter):
            gradient = df(x)
            x = [xi - learning_rate * gi for xi, gi in zip(x, gradient)]
        return x

    @staticmethod
    def stochastic_gradient_descent(f: Callable[[List[float]], float],
                                     df: Callable[[List[float], List[float]]],
                                     x0: List[float], learning_rate: float = 0.01,
                                     batch_size: int = 32, max_iter: int = 1000) -> List[float]:
        """Stochastic gradient descent"""
        x = x0.copy()
        for _ in range(max_iter):
            gradient = df(x)
            x = [xi - learning_rate * gi for xi, gi in zip(x, gradient)]
        return x

    @staticmethod
    def genetic_algorithm(fitness: Callable[[List[float]], float], bounds: List[Tuple[float, float]],
                         population_size: int = 100, generations: int = 100,
                         mutation_rate: float = 0.01) -> List[float]:
        """Genetic algorithm optimization"""
        import random

        def random_individual():
            return [random.uniform(bound[0], bound[1]) for bound in bounds]

        def crossover(parent1: List[float], parent2: List[float]) -> List[float]:
            crossover_point = random.randint(0, len(parent1) - 1)
            child = parent1[:crossover_point] + parent2[crossover_point:]
            return child

        def mutate(individual: List[float]):
            for i in range(len(individual)):
                if random.random() < mutation_rate:
                    individual[i] = random.uniform(bounds[i][0], bounds[i][1])

        # Initialize population
        population = [random_individual() for _ in range(population_size)]

        for _ in range(generations):
            # Evaluate fitness
            fitness_scores = [(ind, fitness(ind)) for ind in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            population = [ind for ind, _ in fitness_scores[:population_size // 2]]

            # Create offspring
            offspring = []
            while len(offspring) < population_size:
                parent1, parent2 = random.sample(population, 2)
                child = crossover(parent1, parent2)
                mutate(child)
                offspring.append(child)

            population = offspring

        # Return best solution
        best = max(population, key=fitness)
        return best


class SignalProcessing:
    """Signal processing"""

    @staticmethod
    def fft(signal: List[float]) -> List[complex]:
        """Fast Fourier Transform"""
        return list(np.fft.fft(signal))

    @staticmethod
    def ifft(signal: List[complex]) -> List[float]:
        """Inverse FFT"""
        return list(np.fft.ifft(signal).real)

    @staticmethod
    def filter_signal(signal: List[float], cutoff: float, sample_rate: float) -> List[float]:
        """Low-pass filter"""
        from scipy import signal as scipy_signal
        b, a = scipy_signal.butter(4, cutoff / (sample_rate / 2), btype='low')
        return list(scipy_signal.filtfilt(b, a, signal))

    @staticmethod
    def convolve(signal: List[float], kernel: List[float]) -> List[float]:
        """Convolution"""
        return list(np.convolve(signal, kernel, mode='same'))

    @staticmethod
    def correlate(signal: List[float], kernel: List[float]) -> List[float]:
        """Cross-correlation"""
        return list(np.correlate(signal, kernel, mode='same'))


class MathematicalModeling:
    """Mathematical modeling"""

    @staticmethod
    def polynomial_fit(x: List[float], y: List[float], degree: int) -> List[float]:
        """Polynomial regression"""
        coefficients = np.polyfit(x, y, degree)
        return list(coefficients)

    @staticmethod
    def polynomial_evaluate(coefficients: List[float], x: float) -> float:
        """Evaluate polynomial"""
        result = 0
        for i, coef in enumerate(coefficients):
            result += coef * (x ** (len(coefficients) - 1 - i))
        return result

    @staticmethod
    def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float]:
        """Linear regression"""
        x_array = np.array(x)
        y_array = np.array(y)
        slope, intercept = np.polyfit(x_array, y_array, 1)
        return float(slope), float(intercept)

    @staticmethod
    def logistic_regression(x: List[List[float]], y: List[int],
                             learning_rate: float = 0.01, iterations: int = 1000) -> List[float]:
        """Logistic regression"""
        n_samples = len(x)
        n_features = len(x[0])
        weights = [0.0] * n_features
        bias = 0.0

        for _ in range(iterations):
            for i in range(n_samples):
                prediction = 1.0 / (1.0 + math.exp(-sum(w * x for w, x in zip(weights, x[i])) - bias))
                error = y[i] - prediction
                weights = [w + learning_rate * error * xi for w, xi in zip(weights, x[i])]
                bias += learning_rate * error

        return weights

    @staticmethod
    def differential_equation(f: Callable[[float, float], float], y0: float, t0: float,
                              t_end: float, h: float = 0.01) -> List[Tuple[float, float]]:
        """Solve differential equation"""
        return NumericalMethods.solve_ode(f, y0, t0, t_end, h)


def main():
    """Main entry point for testing"""
    print("Testing Scientific Computing...")

    # Test Matrix
    mat = Matrix([[1, 2], [3, 4]])
    print(f"Matrix:\n{mat.data}")
    print(f"Determinant: {mat.determinant()}")
    print(f"Inverse:\n{mat.inverse().data}")

    # Test Linear Algebra
    la = LinearAlgebra()
    print(f"Dot product: {la.dot([1, 2, 3], [4, 5, 6])}")
    print(f"Norm: {la.norm([3, 4])}")

    # Test Numerical Methods
    nm = NumericalMethods()
    f = lambda x: x ** 2
    print(f"Integral: {nm.integrate(f, 0, 1)}")
    print(f"Derivative: {nm.differentiate(f, 2)}")

    # Test Optimization
    opt = Optimization()
    f = lambda x: x[0] ** 2 + x[1] ** 2
    df = lambda x: [2 * x[0], 2 * x[1]]
    result = opt.gradient_descent(f, df, [1, 1])
    print(f"Optimized: {result}")

    # Test Signal Processing
    sp = SignalProcessing()
    signal = list(np.sin(np.linspace(0, 2 * np.pi, 100)))
    fft_result = sp.fft(signal)
    print(f"FFT: {len(fft_result)} points")

    # Test Mathematical Modeling
    mm = MathematicalModeling()
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    slope, intercept = mm.linear_regression(x, y)
    print(f"Linear regression: y = {slope}x + {intercept}")

    print("\nScientific Computing initialized successfully")


if __name__ == "__main__":
    main()
