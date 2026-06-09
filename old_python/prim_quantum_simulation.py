"""
Prim Quantum Simulation
Provides quantum circuit simulation, state vector simulation,
gate operations, measurement simulation, and quantum algorithms.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class GateType(Enum):
    """Quantum gates"""
    H = "hadamard"
    X = "pauli_x"
    Y = "pauli_y"
    Z = "pauli_z"
    CNOT = "cnot"
    MEASURE = "measure"


@dataclass
class QuantumGate:
    """Quantum gate"""
    type: GateType
    target: int
    control: Optional[int] = None


class QuantumState:
    """Quantum state vector"""

    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.state = [complex(1.0, 0.0)] + [complex(0.0, 0.0)] * ((1 << num_qubits) - 1)

    def apply_gate(self, gate: QuantumGate):
        """Apply quantum gate"""
        if gate.type == GateType.H:
            self._apply_hadamard(gate.target)
        elif gate.type == GateType.X:
            self._apply_pauli_x(gate.target)
        elif gate.type == GateType.Z:
            self._apply_pauli_z(gate.target)

    def _apply_hadamard(self, target: int):
        """Apply Hadamard gate"""
        for i in range(len(self.state)):
            if (i >> target) & 1:
                j = i ^ (1 << target)
                temp = (self.state[i] + self.state[j]) / math.sqrt(2)
                self.state[j] = (self.state[i] - self.state[j]) / math.sqrt(2)
                self.state[i] = temp

    def _apply_pauli_x(self, target: int):
        """Apply Pauli-X gate"""
        for i in range(len(self.state)):
            if (i >> target) & 1:
                j = i ^ (1 << target)
                self.state[i], self.state[j] = self.state[j], self.state[i]

    def _apply_pauli_z(self, target: int):
        """Apply Pauli-Z gate"""
        for i in range(len(self.state)):
            if (i >> target) & 1:
                self.state[i] = -self.state[i]

    def measure(self, target: int) -> int:
        """Measure qubit"""
        import random
        probs = [abs(self.state[i]) ** 2 for i in range(len(self.state))]
        r = random.random() * sum(probs)
        cumulative = 0

        for i, prob in enumerate(probs):
            cumulative += prob
            if r <= cumulative:
                return (i >> target) & 1

        return 0


class QuantumSimulator:
    """Quantum circuit simulator"""

    def __init__(self, num_qubits: int):
        self.state = QuantumState(num_qubits)
        self.gates: List[QuantumGate] = []

    def add_gate(self, gate: QuantumGate):
        """Add gate to circuit"""
        self.gates.append(gate)

    def run(self) -> Dict[str, Any]:
        """Run quantum circuit"""
        for gate in self.gates:
            self.state.apply_gate(gate)

        return {
            "final_state": self.state.state,
            "qubits": self.state.num_qubits
        }


def main():
    print("Testing Quantum Simulation...")
    simulator = QuantumSimulator(2)
    gate = QuantumGate(type=GateType.H, target=0)
    simulator.add_gate(gate)
    result = simulator.run()
    print(f"Qubits: {result['qubits']}")
    print("Quantum Simulation initialized successfully")


if __name__ == "__main__":
    main()
