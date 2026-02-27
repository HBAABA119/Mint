"""
Prim Engineering Applications
Provides control systems, signal processing, optimization, circuit analysis,
and mechanical engineering tools.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math


class ControlSystemType(Enum):
    """Control system types"""
    PID = "pid"
    STATE_SPACE = "state_space"
    LQR = "lqr"
    MPC = "mpc"


class SignalType(Enum):
    """Signal types"""
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"
    DIGITAL = "digital"


@dataclass
class PIDController:
    """PID controller"""
    kp: float = 1.0
    ki: float = 0.0
    kd: float = 0.0
    setpoint: float = 0.0
    integral: float = 0.0
    prev_error: float = 0.0

    def compute(self, measurement: float, dt: float) -> float:
        """Compute control output"""
        error = self.setpoint - measurement

        # Proportional
        p = self.kp * error

        # Integral
        self.integral += error * dt
        i = self.ki * self.integral

        # Derivative
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        d = self.kd * derivative

        self.prev_error = error

        return p + i + d

    def reset(self):
        """Reset controller state"""
        self.integral = 0.0
        self.prev_error = 0.0


class StateSpaceController:
    """State space controller"""

    def __init__(self, A: np.ndarray, B: np.ndarray, C: np.ndarray, D: np.ndarray):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.state = np.zeros(A.shape[0])

    def step(self, u: np.ndarray, dt: float) -> np.ndarray:
        """Advance system by dt"""
        # State update: x_dot = Ax + Bu
        x_dot = np.dot(self.A, self.state) + np.dot(self.B, u)
        self.state += x_dot * dt

        # Output: y = Cx + Du
        y = np.dot(self.C, self.state) + np.dot(self.D, u)

        return y

    def lqr_design(self, Q: np.ndarray, R: np.ndarray) -> np.ndarray:
        """Design LQR controller"""
        from scipy.linalg import solve_continuous_are
        P = solve_continuous_are(self.A, self.B, Q, R)
        K = np.linalg.inv(R) @ np.dot(self.B.T, P)
        return K


class SignalProcessor:
    """Signal processing utilities"""

    @staticmethod
    def fft(signal: np.ndarray) -> np.ndarray:
        """Fast Fourier Transform"""
        return np.fft.fft(signal)

    @staticmethod
    def ifft(signal: np.ndarray) -> np.ndarray:
        """Inverse FFT"""
        return np.fft.ifft(signal)

    @staticmethod
    def filter_signal(signal: np.ndarray, cutoff: float, sample_rate: float) -> np.ndarray:
        """Low-pass filter"""
        from scipy import signal as scipy_signal
        b, a = scipy_signal.butter(4, cutoff / (sample_rate / 2), btype='low')
        return scipy_signal.filtfilt(b, a, signal)

    @staticmethod
    def convolve(signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Convolution"""
        return np.convolve(signal, kernel, mode='same')

    @staticmethod
    def correlate(signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Cross-correlation"""
        return np.correlate(signal, kernel, mode='same')


class CircuitAnalyzer:
    """Circuit analysis"""

    def __init__(self):
        self.nodes: List[str] = []
        self.components: Dict[str, Dict[str, Any]] = {}
        self.voltages: Dict[str, float] = {}
        self.currents: Dict[str, float] = {}

    def add_resistor(self, name: str, value: float, node1: str, node2: str):
        """Add resistor to circuit"""
        self.components[name] = {
            "type": "resistor",
            "value": value,
            "node1": node1,
            "node2": node2
        }

    def add_voltage_source(self, name: str, value: float, node1: str, node2: str):
        """Add voltage source to circuit"""
        self.components[name] = {
            "type": "voltage_source",
            "value": value,
            "node1": node1,
            "node2": node2
        }

    def solve_dc(self) -> Dict[str, Any]:
        """Solve DC circuit analysis"""
        # Simplified nodal analysis
        nodes = set()
        for comp in self.components.values():
            nodes.add(comp["node1"])
            nodes.add(comp["node2"])

        nodes = list(nodes)
        n = len(nodes)

        # Build conductance matrix
        G = np.zeros((n, n))
        I = np.zeros(n)

        for comp_name, comp in self.components.items():
            if comp["type"] == "resistor":
                i = nodes.index(comp["node1"])
                j = nodes.index(comp["node2"])
                g = 1.0 / comp["value"]
                G[i, i] += g
                G[j, j] += g
                G[i, j] -= g
                G[j, i] -= g
            elif comp["type"] == "voltage_source":
                i = nodes.index(comp["node1"])
                j = nodes.index(comp["node2"])
                # Simplified voltage source handling
                I[i] += comp["value"] / 1e6  # Large conductance
                I[j] -= comp["value"] / 1e6
                G[i, i] += 1e6
                G[j, j] += 1e6

        # Solve for node voltages
        try:
            voltages = np.linalg.solve(G, I)
        except np.linalg.LinAlgError:
            voltages = np.zeros(n)

        # Store results
        for i, node in enumerate(nodes):
            self.voltages[node] = voltages[i]

        # Calculate currents
        for comp_name, comp in self.components.items():
            if comp["type"] == "resistor":
                v1 = self.voltages.get(comp["node1"], 0)
                v2 = self.voltages.get(comp["node2"], 0)
                current = (v1 - v2) / comp["value"]
                self.currents[comp_name] = current

        return {
            "voltages": self.voltages.copy(),
            "currents": self.currents.copy()
        }


class MechanicalSystem:
    """Mechanical system simulation"""

    def __init__(self):
        self.masses: List[float] = []
        self.spring_constants: List[float] = []
        self.damping_coefficients: List[float] = []
        self.positions: List[float] = []
        self.velocities: List[float] = []

    def add_mass_spring_damper(self, mass: float, k: float, c: float,
                                initial_position: float = 0.0,
                                initial_velocity: float = 0.0):
        """Add mass-spring-damper system"""
        self.masses.append(mass)
        self.spring_constants.append(k)
        self.damping_coefficients.append(c)
        self.positions.append(initial_position)
        self.velocities.append(initial_velocity)

    def step(self, dt: float = 0.01):
        """Advance simulation by dt"""
        for i in range(len(self.masses)):
            m = self.masses[i]
            k = self.spring_constants[i]
            c = self.damping_coefficients[i]

            # Force from spring and damper
            F = -k * self.positions[i] - c * self.velocities[i]

            # Acceleration
            a = F / m

            # Update velocity and position
            self.velocities[i] += a * dt
            self.positions[i] += self.velocities[i] * dt

    def get_energy(self) -> Dict[str, float]:
        """Calculate system energy"""
        kinetic_energy = 0.0
        potential_energy = 0.0

        for i in range(len(self.masses)):
            m = self.masses[i]
            k = self.spring_constants[i]

            kinetic_energy += 0.5 * m * self.velocities[i]**2
            potential_energy += 0.5 * k * self.positions[i]**2

        return {
            "kinetic": kinetic_energy,
            "potential": potential_energy,
            "total": kinetic_energy + potential_energy
        }


class OptimizationEngine:
    """Optimization for engineering problems"""

    @staticmethod
    def minimize(f: Callable[[np.ndarray], float], x0: np.ndarray,
                  method: str = "bfgs") -> np.ndarray:
        """Minimize function"""
        from scipy.optimize import minimize

        result = minimize(f, x0, method=method)
        return result.x

    @staticmethod
    def constrained_minimize(f: Callable[[np.ndarray], float],
                             x0: np.ndarray,
                             constraints: List[Dict[str, Any]]) -> np.ndarray:
        """Minimize with constraints"""
        from scipy.optimize import minimize

        result = minimize(f, x0, constraints=constraints)
        return result.x

    @staticmethod
    def multi_objective(objectives: List[Callable], x0: np.ndarray) -> np.ndarray:
        """Multi-objective optimization"""
        # Weighted sum approach
        def weighted_sum(x):
            return sum(obj(x) for obj in objectives)

        return OptimizationEngine.minimize(weighted_sum, x0)


class FiniteElement:
    """Finite element method"""

    def __init__(self):
        self.nodes: List[np.ndarray] = []
        self.elements: List[Tuple[int, int]] = []
        self.stiffness: Optional[np.ndarray] = None
        self.displacements: Optional[np.ndarray] = None

    def add_node(self, position: np.ndarray):
        """Add node to mesh"""
        self.nodes.append(position)

    def add_element(self, node1: int, node2: int):
        """Add element (simplified 1D)"""
        self.elements.append((node1, node2))

    def assemble_stiffness(self, E: float = 1.0, A: float = 1.0):
        """Assemble stiffness matrix"""
        n = len(self.nodes)
        K = np.zeros((n, n))

        for node1, node2 in self.elements:
            # Simplified 1D element stiffness
            length = np.linalg.norm(self.nodes[node1] - self.nodes[node2])
            k = E * A / length

            K[node1, node1] += k
            K[node1, node2] -= k
            K[node2, node1] -= k
            K[node2, node2] += k

        self.stiffness = K

    def solve(self, loads: np.ndarray, fixed_nodes: List[int]) -> np.ndarray:
        """Solve for displacements"""
        if self.stiffness is None:
            raise RuntimeError("Stiffness matrix not assembled")

        K = self.stiffness.copy()
        f = loads.copy()

        # Apply boundary conditions
        for node in fixed_nodes:
            K[node, :] = 0
            K[:, node] = 0
            K[node, node] = 1
            f[node] = 0

        # Solve
        displacements = np.linalg.solve(K, f)
        self.displacements = displacements

        return displacements


class ControlSystemDesigner:
    """Control system design tools"""

    @staticmethod
    def pid_tune(system_response: Callable, Kp_range: Tuple[float, float],
                 Ki_range: Tuple[float, float], Kd_range: Tuple[float, float]) -> PIDController:
        """Auto-tune PID controller"""
        best_kp, best_ki, best_kd = 1.0, 0.0, 0.0
        best_error = float('inf')

        for kp in np.linspace(Kp_range[0], Kp_range[1], 10):
            for ki in np.linspace(Ki_range[0], Ki_range[1], 10):
                for kd in np.linspace(Kd_range[0], Kd_range[1], 10):
                    pid = PIDController(kp=kp, ki=ki, kd=kd)

                    # Simulate response
                    error = 0.0
                    for t in np.linspace(0, 10, 100):
                        y = system_response(t)
                        u = pid.compute(y, 0.1)
                        error += abs(pid.setpoint - y)

                    if error < best_error:
                        best_error = error
                        best_kp, best_ki, best_kd = kp, ki, kd

        return PIDController(kp=best_kp, ki=best_ki, kd=best_kd)

    @staticmethod
    def bode_plot(system_func: Callable, frequencies: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Bode plot data"""
        magnitude = []
        phase = []

        for w in frequencies:
            s = 1j * w
            response = system_func(s)

            magnitude_db = 20 * np.log10(np.abs(response))
            phase_deg = np.angle(response, deg=True)

            magnitude.append(magnitude_db)
            phase.append(phase_deg)

        return np.array(magnitude), np.array(phase)


def create_pid_controller(kp: float = 1.0, ki: float = 0.0, kd: float = 0.0) -> PIDController:
    """Create PID controller"""
    return PIDController(kp=kp, ki=ki, kd=kd)


def main():
    """Main entry point for testing"""
    print("Testing Engineering Applications...")

    # Test PID Controller
    pid = create_pid_controller(kp=2.0, ki=0.1, kd=0.5)
    pid.setpoint = 10.0
    output = pid.compute(measurement=8.0, dt=0.1)
    print(f"PID output: {output:.4f}")

    # Test State Space Controller
    A = np.array([[-1, 1], [0, -2]])
    B = np.array([[1], [0]])
    C = np.array([[1, 0]])
    D = np.array([[0]])

    ssc = StateSpaceController(A, B, C, D)
    y = ssc.step(np.array([[1.0]]), dt=0.01)
    print(f"State space output: {y}")

    # Test Signal Processor
    sp = SignalProcessor()
    signal = np.sin(np.linspace(0, 2*np.pi, 100))
    fft_result = sp.fft(signal)
    print(f"FFT: {len(fft_result)} points")

    # Test Circuit Analyzer
    ca = CircuitAnalyzer()
    ca.add_resistor("R1", 1000.0, "n1", "n2")
    ca.add_voltage_source("V1", 5.0, "n1", "n2")
    results = ca.solve_dc()
    print(f"Circuit voltages: {len(results['voltages'])} nodes")

    # Test Mechanical System
    ms = MechanicalSystem()
    ms.add_mass_spring_damper(mass=1.0, k=10.0, c=0.5)
    ms.step(dt=0.01)
    energy = ms.get_energy()
    print(f"Mechanical energy: {energy['total']:.4f}")

    # Test Optimization
    def objective(x):
        return (x[0] - 1)**2 + (x[1] - 2)**2

    opt = OptimizationEngine()
    result = opt.minimize(objective, np.array([0.0, 0.0]))
    print(f"Optimization result: {result}")

    # Test Finite Element
    fe = FiniteElement()
    fe.add_node(np.array([0.0, 0.0]))
    fe.add_node(np.array([1.0, 0.0]))
    fe.add_node(np.array([2.0, 0.0]))
    fe.add_element(0, 1)
    fe.add_element(1, 2)
    fe.assemble_stiffness(E=200e9, A=0.001)

    loads = np.array([0.0, 1000.0, 0.0])
    displacements = fe.solve(loads, fixed_nodes=[0])
    print(f"Finite element: {len(displacements)} displacements")

    print("\nEngineering Applications initialized successfully")


if __name__ == "__main__":
    main()
