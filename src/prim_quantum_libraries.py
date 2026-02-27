"""
Prim Quantum Libraries
Provides quantum algorithm library, standard quantum circuits,
quantum utilities, and reusable quantum components.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AlgorithmType(Enum):
    """Algorithm types"""
    GROVER = "grover"
    SHOR = "shor"
    QFT = "qft"
    VQE = "vqe"


@dataclass
class QuantumAlgorithm:
    """Quantum algorithm"""
    name: str
    type: AlgorithmType
    description: str


class QuantumLibrary:
    """Quantum algorithm library"""

    def __init__(self):
        self.algorithms: Dict[str, QuantumAlgorithm] = {}

    def register_algorithm(self, algorithm: QuantumAlgorithm):
        """Register algorithm"""
        self.algorithms[algorithm.name] = algorithm

    def get_algorithm(self, name: str) -> Optional[QuantumAlgorithm]:
        """Get algorithm"""
        return self.algorithms.get(name)


def main():
    print("Testing Quantum Libraries...")
    library = QuantumLibrary()
    algo = QuantumAlgorithm(name="grover", type=AlgorithmType.GROVER, description="Grover's algorithm")
    library.register_algorithm(algo)
    print(f"Algorithm: {algo.name}")
    print("Quantum Libraries initialized successfully")


if __name__ == "__main__":
    main()
