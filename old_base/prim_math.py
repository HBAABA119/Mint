"""
Prim Mathematical Computing
Provides symbolic mathematics, optimization algorithms, differential equations,
linear algebra operations, and number theory.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math


class OptimizationMethod(Enum):
    """Optimization methods"""
    GRADIENT_DESCENT = "gradient_descent"
    NEWTON = "newton"
    BFGS = "bfgs"
    SIMULATED_ANNEALING = "simulated_annealing"
    GENETIC_ALGORITHM = "genetic_algorithm"


class SolverType(Enum):
    """Solver types"""
    ODE = "ode"
    PDE = "pde"
    INTEGRAL = "integral"
    ROOT = "root"


@dataclass
class SymbolicExpression:
    """Symbolic mathematical expression"""
    expression: str
    variables: List[str]
    value: Optional[float] = None


class SymbolicMath:
    """Symbolic mathematics"""

    def __init__(self):
        self.variables: Dict[str, float] = {}
        self.expressions: List[SymbolicExpression] = []

    def define_variable(self, name: str, value: float):
        """Define a symbolic variable"""
        self.variables[name] = value

    def define_expression(self, expression: str) -> SymbolicExpression:
        """Define a symbolic expression"""
        # Extract variables from expression
        import re
        variables = list(set(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression)))
        variables = [v for v in variables if v not in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']]

        expr = SymbolicExpression(
            expression=expression,
            variables=variables
        )
        self.expressions.append(expr)
        return expr

    def evaluate(self, expression: SymbolicExpression) -> float:
        """Evaluate symbolic expression"""
        # Replace variables with values
        eval_expr = expression.expression
        for var, val in self.variables.items():
            eval_expr = eval_expr.replace(var, str(val))

        # Evaluate
        return eval(eval_expr)

    def differentiate(self, expression: SymbolicExpression, variable: str) -> str:
        """Symbolic differentiation (simplified)"""
        # Simplified differentiation - would use symbolic library in practice
        expr = expression.expression

        # Power rule
        if variable in expr:
            if f"{variable}^2" in expr:
                return f"2*{variable}"
            elif f"{variable}^3" in expr:
                return f"3*{variable}^2"

        return "0"

    def integrate(self, expression: SymbolicExpression, variable: str) -> str:
        """Symbolic integration (simplified)"""
        # Simplified integration - would use symbolic library in practice
        expr = expression.expression

        # Basic integration rules
        if variable in expr:
            if expr == variable:
                return f"{variable}^2/2"
            elif f"{variable}^2" in expr:
                return f"{variable}^3/3"

        return f"integrate({expr}, {variable})"


class DifferentialEquations:
    """Differential equation solvers"""

    @staticmethod
    def solve_ode(f: Callable[[float, float], float], y0: float, t0: float,
                   t_end: float, h: float = 0.01) -> List[Tuple[float, float]]:
        """Solve ordinary differential equation"""
        t = t0
        y = y0
        results = [(t, y)]

        while t < t_end:
            # Euler's method
            y += h * f(t, y)
            t += h
            results.append((t, y))

        return results

    @staticmethod
    def solve_ode_rk4(f: Callable[[float, float], float], y0: float, t0: float,
                      t_end: float, h: float = 0.01) -> List[Tuple[float, float]]:
        """Solve ODE using Runge-Kutta 4th order"""
        t = t0
        y = y0
        results = [(t, y)]

        while t < t_end:
            k1 = h * f(t, y)
            k2 = h * f(t + h/2, y + k1/2)
            k3 = h * f(t + h/2, y + k2/2)
            k4 = h * f(t + h, y + k3)

            y += (k1 + 2*k2 + 2*k3 + k4) / 6
            t += h
            results.append((t, y))

        return results

    @staticmethod
    def solve_system(f: Callable[[float, List[float]], List[float]],
                     y0: List[float], t0: float, t_end: float,
                     h: float = 0.01) -> List[Tuple[float, List[float]]]:
        """Solve system of ODEs"""
        t = t0
        y = y0.copy()
        results = [(t, y.copy())]

        while t < t_end:
            k1 = h * np.array(f(t, y))
            k2 = h * np.array(f(t + h/2, y + k1/2))
            k3 = h * np.array(f(t + h/2, y + k2/2))
            k4 = h * np.array(f(t + h, y + k3))

            y = y + (k1 + 2*k2 + 2*k3 + k4) / 6
            t += h
            results.append((t, y.tolist()))

        return results


class Optimization:
    """Optimization algorithms"""

    @staticmethod
    def gradient_descent(f: Callable[[List[float]], float],
                         df: Callable[[List[float]], List[float]],
                         x0: List[float], learning_rate: float = 0.01,
                         max_iter: int = 1000, tol: float = 1e-6) -> List[float]:
        """Gradient descent optimization"""
        x = x0.copy()

        for _ in range(max_iter):
            gradient = df(x)
            x_new = [xi - learning_rate * gi for xi, gi in zip(x, gradient)]

            # Check convergence
            if max(abs(nx - xi) for nx, xi in zip(x_new, x)) < tol:
                break

            x = x_new

        return x

    @staticmethod
    def newton_method(f: Callable[[float], float], df: Callable[[float], float],
                      x0: float, max_iter: int = 100, tol: float = 1e-6) -> float:
        """Newton's method for root finding"""
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
    def simulated_annealing(f: Callable[[List[float]], float],
                            bounds: List[Tuple[float, float]],
                            initial_temp: float = 1000.0,
                            cooling_rate: float = 0.95,
                            iterations: int = 1000) -> List[float]:
        """Simulated annealing optimization"""
        import random

        # Initialize random solution
        x = [random.uniform(b[0], b[1]) for b in bounds]
        best_x = x.copy()
        best_value = f(x)

        temp = initial_temp

        for _ in range(iterations):
            # Generate neighbor
            x_new = [random.uniform(max(b[0], xi - 0.1), min(b[1], xi + 0.1))
                     for xi, b in zip(x, bounds)]

            value_new = f(x_new)
            value_current = f(x)

            # Accept or reject
            delta = value_new - value_current
            if delta < 0 or random.random() < math.exp(-delta / temp):
                x = x_new

            # Update best
            if value_new < best_value:
                best_x = x_new.copy()
                best_value = value_new

            # Cool down
            temp *= cooling_rate

        return best_x

    @staticmethod
    def genetic_algorithm(fitness: Callable[[List[float]], float],
                         bounds: List[Tuple[float, float]],
                         population_size: int = 100,
                         generations: int = 100,
                         mutation_rate: float = 0.01) -> List[float]:
        """Genetic algorithm optimization"""
        import random

        def random_individual():
            return [random.uniform(b[0], b[1]) for b in bounds]

        def crossover(parent1, parent2):
            crossover_point = random.randint(0, len(parent1) - 1)
            child = parent1[:crossover_point] + parent2[crossover_point:]
            return child

        def mutate(individual):
            for i in range(len(individual)):
                if random.random() < mutation_rate:
                    individual[i] = random.uniform(bounds[i][0], bounds[i][1])

        # Initialize population
        population = [random_individual() for _ in range(population_size)]

        for _ in range(generations):
            # Evaluate fitness
            fitness_scores = [(ind, fitness(ind)) for ind in population]
            fitness_scores.sort(key=lambda x: x[1])

            # Select best individuals
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


class LinearAlgebra:
    """Linear algebra operations"""

    @staticmethod
    def solve_linear_system(A: List[List[float]], b: List[float]) -> List[float]:
        """Solve linear system Ax = b"""
        from numpy.linalg import solve
        return list(solve(np.array(A), np.array(b)))

    @staticmethod
    def eigen_decomposition(A: List[List[float]]) -> Tuple[List[float], List[List[float]]]:
        """Eigenvalue decomposition"""
        from numpy.linalg import eig
        eigenvalues, eigenvectors = eig(np.array(A))
        return list(eigenvalues), eigenvectors.tolist()

    @staticmethod
    def svd(A: List[List[float]]) -> Tuple[List[List[float]], List[float], List[List[float]]]:
        """Singular value decomposition"""
        from numpy.linalg import svd
        U, S, Vt = svd(np.array(A))
        return U.tolist(), list(S), Vt.tolist()

    @staticmethod
    def matrix_power(A: List[List[float]], n: int) -> List[List[float]]:
        """Matrix power"""
        A_np = np.array(A)
        result = np.linalg.matrix_power(A_np, n)
        return result.tolist()


class NumberTheory:
    """Number theory operations"""

    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if number is prime"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False

        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False

        return True

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Greatest common divisor"""
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Least common multiple"""
        return abs(a * b) // NumberTheory.gcd(a, b)

    @staticmethod
    def prime_factors(n: int) -> List[int]:
        """Prime factorization"""
        factors = []
        d = 2

        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1

        if n > 1:
            factors.append(n)

        return factors

    @staticmethod
    def fibonacci(n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return n

        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b

        return a


class SpecialFunctions:
    """Special mathematical functions"""

    @staticmethod
    def gamma(x: float) -> float:
        """Gamma function"""
        from scipy.special import gamma
        return gamma(x)

    @staticmethod
    def beta(x: float, y: float) -> float:
        """Beta function"""
        from scipy.special import beta
        return beta(x, y)

    @staticmethod
    def erf(x: float) -> float:
        """Error function"""
        from scipy.special import erf
        return erf(x)

    @staticmethod
    def bessel_j(n: int, x: float) -> float:
        """Bessel function of first kind"""
        from scipy.special import jv
        return jv(n, x)

    @staticmethod
    def legendre(n: int, x: float) -> float:
        """Legendre polynomial"""
        from scipy.special import legendre
        return legendre(n)(x)


def create_symbolic_math() -> SymbolicMath:
    """Create symbolic math instance"""
    return SymbolicMath()


def main():
    """Main entry point for testing"""
    print("Testing Mathematical Computing...")

    # Test Symbolic Math
    sym_math = create_symbolic_math()
    sym_math.define_variable("x", 5.0)
    expr = sym_math.define_expression("x^2 + 2*x + 1")
    value = sym_math.evaluate(expr)
    print(f"Expression value: {value}")

    derivative = sym_math.differentiate(expr, "x")
    print(f"Derivative: {derivative}")

    # Test Differential Equations
    de = DifferentialEquations()
    f = lambda t, y: -y  # dy/dt = -y
    solution = de.solve_ode(f, y0=1.0, t0=0, t_end=1.0)
    print(f"ODE solution: {len(solution)} points")

    # Test Optimization
    opt = Optimization()
    f = lambda x: x[0]**2 + x[1]**2
    df = lambda x: [2*x[0], 2*x[1]]
    result = opt.gradient_descent(f, df, [1.0, 1.0])
    print(f"Optimized: {result}")

    # Test Linear Algebra
    la = LinearAlgebra()
    A = [[1, 2], [3, 4]]
    b = [5, 11]
    solution = la.solve_linear_system(A, b)
    print(f"Linear solution: {solution}")

    # Test Number Theory
    nt = NumberTheory()
    print(f"Is 17 prime: {nt.is_prime(17)}")
    print(f"GCD(12, 18): {nt.gcd(12, 18)}")
    print(f"LCM(12, 18): {nt.lcm(12, 18)}")
    print(f"Prime factors of 60: {nt.prime_factors(60)}")
    print(f"Fibonacci(10): {nt.fibonacci(10)}")

    # Test Special Functions
    sf = SpecialFunctions()
    print(f"Gamma(5): {sf.gamma(5):.2f}")
    print(f"Beta(2, 3): {sf.beta(2, 3):.2f}")
    print(f"erf(1): {sf.erf(1):.4f}")

    print("\nMathematical Computing initialized successfully")


if __name__ == "__main__":
    main()
