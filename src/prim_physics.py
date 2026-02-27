"""
Prim Computational Physics
Provides quantum mechanics simulation, fluid dynamics, thermodynamics,
electromagnetism, and particle physics.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math


class PhysicsDomain(Enum):
    """Physics domains"""
    QUANTUM_MECHANICS = "quantum_mechanics"
    FLUID_DYNAMICS = "fluid_dynamics"
    THERMODYNAMICS = "thermodynamics"
    ELECTROMAGNETISM = "electromagnetism"
    PARTICLE_PHYSICS = "particle_physics"


@dataclass
class Particle:
    """Particle representation"""
    position: np.ndarray
    velocity: np.ndarray
    mass: float
    charge: float = 0.0
    spin: float = 0.0


class QuantumMechanics:
    """Quantum mechanics simulation"""

    def __init__(self):
        self.wavefunction: Optional[np.ndarray] = None
        self.hamiltonian: Optional[np.ndarray] = None

    def initialize_wavefunction(self, n_points: int):
        """Initialize wavefunction"""
        x = np.linspace(-10, 10, n_points)
        psi = np.exp(-x**2) / np.sqrt(np.sum(np.exp(-2*x**2)))
        self.wavefunction = psi

    def time_evolution(self, dt: float = 0.01):
        """Evolve wavefunction in time"""
        if self.wavefunction is None or self.hamiltonian is None:
            raise RuntimeError("Wavefunction or Hamiltonian not initialized")

        # Time evolution using Crank-Nicolson method (simplified)
        H = self.hamiltonian
        psi = self.wavefunction

        # Simplified time evolution
        psi_new = psi - 1j * dt * np.dot(H, psi)
        psi_new = psi_new / np.sqrt(np.sum(np.abs(psi_new)**2))

        self.wavefunction = psi_new

    def probability_density(self) -> np.ndarray:
        """Calculate probability density"""
        if self.wavefunction is None:
            raise RuntimeError("Wavefunction not initialized")

        return np.abs(self.wavefunction)**2

    def expectation_value(self, operator: np.ndarray) -> float:
        """Calculate expectation value"""
        if self.wavefunction is None:
            raise RuntimeError("Wavefunction not initialized")

        psi = self.wavefunction
        return np.real(np.conj(psi).T @ operator @ psi)


class FluidDynamics:
    """Fluid dynamics simulation"""

    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.velocity_x = np.zeros((height, width))
        self.velocity_y = np.zeros((height, width))
        self.pressure = np.zeros((height, width))
        self.density = np.ones((height, width))

    def initialize_flow(self, u0: float = 1.0):
        """Initialize uniform flow"""
        self.velocity_x[:, :] = u0

    def step(self, dt: float = 0.01):
        """Advance simulation by dt"""
        # Simplified Navier-Stokes (advection)
        dx = 1.0
        dy = 1.0

        # Advection (upwind scheme)
        ux_new = self.velocity_x.copy()
        uy_new = self.velocity_y.copy()

        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.velocity_x[i, j] > 0:
                    ux_new[i, j] -= self.velocity_x[i, j] * (self.velocity_x[i, j] - self.velocity_x[i, j-1]) / dx
                else:
                    ux_new[i, j] -= self.velocity_x[i, j] * (self.velocity_x[i, j+1] - self.velocity_x[i, j]) / dx

                if self.velocity_y[i, j] > 0:
                    uy_new[i, j] -= self.velocity_y[i, j] * (self.velocity_y[i, j] - self.velocity_y[i-1, j]) / dy
                else:
                    uy_new[i, j] -= self.velocity_y[i, j] * (self.velocity_y[i+1, j] - self.velocity_y[i, j]) / dy

        self.velocity_x = ux_new
        self.velocity_y = uy_new

    def get_velocity_field(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get velocity field"""
        return self.velocity_x, self.velocity_y

    def get_streamlines(self) -> List[List[Tuple[float, float]]]:
        """Calculate streamlines"""
        streamlines = []

        # Start streamlines from left boundary
        for i in range(0, self.height, 10):
            streamline = []
            x, y = 0.0, float(i)

            for _ in range(100):
                ix, iy = int(y), int(x)

                if ix < 0 or ix >= self.height or iy < 0 or iy >= self.width:
                    break

                vx = self.velocity_x[ix, iy]
                vy = self.velocity_y[ix, iy]

                streamline.append((x, y))

                # Move along velocity
                x += vx * 0.1
                y += vy * 0.1

            streamlines.append(streamline)

        return streamlines


class Thermodynamics:
    """Thermodynamics calculations"""

    @staticmethod
    def ideal_gas_law(pressure: float, volume: float, temperature: float) -> float:
        """Calculate moles using ideal gas law"""
        R = 8.314  # Gas constant
        n = (pressure * volume) / (R * temperature)
        return n

    @staticmethod
    def internal_energy(temperature: float, moles: float, cv: float = 20.8) -> float:
        """Calculate internal energy"""
        return moles * cv * temperature

    @staticmethod
    def entropy_change(temperature: float, heat: float) -> float:
        """Calculate entropy change"""
        return heat / temperature

    @staticmethod
    def gibbs_free_energy(enthalpy: float, temperature: float, entropy: float) -> float:
        """Calculate Gibbs free energy"""
        return enthalpy - temperature * entropy

    @staticmethod
    def heat_transfer(T1: float, T2: float, k: float, area: float, thickness: float) -> float:
        """Calculate heat transfer rate"""
        return k * area * (T1 - T2) / thickness


class Electromagnetism:
    """Electromagnetism calculations"""

    @staticmethod
    def electric_field(charge: float, distance: float) -> float:
        """Calculate electric field"""
        k = 8.99e9  # Coulomb's constant
        return k * charge / (distance**2)

    @staticmethod
    def magnetic_field(current: float, distance: float) -> float:
        """Calculate magnetic field from wire"""
        mu0 = 4 * np.pi * 1e-7  # Permeability of free space
        return mu0 * current / (2 * np.pi * distance)

    @staticmethod
    def lorentz_force(charge: float, velocity: np.ndarray, electric_field: np.ndarray,
                      magnetic_field: np.ndarray) -> np.ndarray:
        """Calculate Lorentz force"""
        F_electric = charge * electric_field
        F_magnetic = charge * np.cross(velocity, magnetic_field)
        return F_electric + F_magnetic

    @staticmethod
    def maxwell_equations(E: np.ndarray, B: np.ndarray, rho: float, J: np.ndarray) -> Dict[str, np.ndarray]:
        """Maxwell's equations (simplified)"""
        epsilon0 = 8.854e-12
        mu0 = 4 * np.pi * 1e-7

        # Gauss's law
        div_E = rho / epsilon0

        # Faraday's law
        curl_E = -np.cross(np.ones(3), B)

        # Ampere's law
        curl_B = mu0 * J + epsilon0 * np.cross(np.ones(3), E)

        # Gauss's law for magnetism
        div_B = np.zeros(3)

        return {
            "div_E": div_E,
            "curl_E": curl_E,
            "curl_B": curl_B,
            "div_B": div_B
        }


class ParticlePhysics:
    """Particle physics simulation"""

    def __init__(self):
        self.particles: List[Particle] = []

    def add_particle(self, particle: Particle):
        """Add particle to system"""
        self.particles.append(particle)

    def remove_particle(self, index: int):
        """Remove particle from system"""
        if 0 <= index < len(self.particles):
            del self.particles[index]

    def step(self, dt: float = 0.01):
        """Advance simulation by dt"""
        for particle in self.particles:
            # Simple motion (no forces)
            particle.position += particle.velocity * dt

    def calculate_forces(self) -> List[np.ndarray]:
        """Calculate forces between particles"""
        forces = []
        k = 8.99e9  # Coulomb's constant

        for i, p1 in enumerate(self.particles):
            force = np.zeros(3)

            for j, p2 in enumerate(self.particles):
                if i == j:
                    continue

                r = p1.position - p2.position
                distance = np.linalg.norm(r)

                if distance < 1e-10:
                    continue

                # Coulomb force
                F = k * p1.charge * p2.charge * r / (distance**3)
                force += F

            forces.append(force)

        return forces

    def kinetic_energy(self) -> float:
        """Calculate total kinetic energy"""
        total_ke = 0.0

        for particle in self.particles:
            v = np.linalg.norm(particle.velocity)
            total_ke += 0.5 * particle.mass * v**2

        return total_ke

    def potential_energy(self) -> float:
        """Calculate total potential energy"""
        total_pe = 0.0
        k = 8.99e9

        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i >= j:
                    continue

                r = np.linalg.norm(p1.position - p2.position)
                if r > 1e-10:
                    total_pe += k * p1.charge * p2.charge / r

        return total_pe


class MolecularDynamics:
    """Molecular dynamics simulation"""

    def __init__(self):
        self.atoms: List[Particle] = []
        self.box_size: float = 10.0
        self.temperature: float = 300.0

    def add_atom(self, atom: Particle):
        """Add atom to system"""
        self.atoms.append(atom)

    def initialize_lattice(self, n_atoms: int = 27):
        """Initialize cubic lattice"""
        n_per_side = int(n_atoms ** (1/3)) + 1
        spacing = self.box_size / n_per_side

        for i in range(n_per_side):
            for j in range(n_per_side):
                for k in range(n_per_side):
                    if len(self.atoms) >= n_atoms:
                        break

                    position = np.array([i, j, k]) * spacing
                    atom = Particle(
                        position=position,
                        velocity=np.random.randn(3) * 0.1,
                        mass=1.0
                    )
                    self.add_atom(atom)

    def step_verlet(self, dt: float = 0.001):
        """Velocity Verlet integration"""
        # Calculate forces
        forces = self._calculate_forces()

        # Update positions
        for i, atom in enumerate(self.atoms):
            atom.position += atom.velocity * dt + 0.5 * forces[i] / atom.mass * dt**2

        # Calculate new forces
        new_forces = self._calculate_forces()

        # Update velocities
        for i, atom in enumerate(self.atoms):
            atom.velocity += 0.5 * (forces[i] + new_forces[i]) / atom.mass * dt

    def _calculate_forces(self) -> List[np.ndarray]:
        """Calculate forces using Lennard-Jones potential"""
        forces = []

        for i, atom_i in enumerate(self.atoms):
            force = np.zeros(3)

            for j, atom_j in enumerate(self.atoms):
                if i == j:
                    continue

                r = atom_i.position - atom_j.position
                distance = np.linalg.norm(r)

                if distance < 1e-10 or distance > 3.0:
                    continue

                # Lennard-Jones force
                sigma = 1.0
                epsilon = 1.0

                sr = sigma / distance
                sr6 = sr**6
                sr12 = sr6**2

                F = 24 * epsilon * (2 * sr12 - sr6) / distance * r / distance
                force += F

            forces.append(force)

        return forces

    def get_temperature(self) -> float:
        """Calculate system temperature"""
        if not self.atoms:
            return 0.0

        kinetic_energy = 0.0
        for atom in self.atoms:
            v = np.linalg.norm(atom.velocity)
            kinetic_energy += 0.5 * atom.mass * v**2

        # T = 2*KE / (3*N*k_B)
        k_B = 1.381e-23  # Boltzmann constant
        temperature = 2 * kinetic_energy / (3 * len(self.atoms) * k_B)

        return temperature


def create_quantum_mechanics() -> QuantumMechanics:
    """Create quantum mechanics simulation"""
    return QuantumMechanics()


def create_fluid_dynamics(width: int = 100, height: int = 100) -> FluidDynamics:
    """Create fluid dynamics simulation"""
    return FluidDynamics(width, height)


def main():
    """Main entry point for testing"""
    print("Testing Computational Physics...")

    # Test Quantum Mechanics
    qm = create_quantum_mechanics()
    qm.initialize_wavefunction(100)
    qm.time_evolution(dt=0.01)
    prob_density = qm.probability_density()
    print(f"Quantum mechanics: {len(prob_density)} points")

    # Test Fluid Dynamics
    fd = create_fluid_dynamics(width=50, height=50)
    fd.initialize_flow(u0=1.0)
    fd.step(dt=0.01)
    vx, vy = fd.get_velocity_field()
    print(f"Fluid dynamics: {vx.shape} velocity field")

    # Test Thermodynamics
    n = Thermodynamics.ideal_gas_law(pressure=101325, volume=0.0224, temperature=273.15)
    print(f"Ideal gas: {n:.4f} moles")

    # Test Electromagnetism
    E_field = Electromagnetism.electric_field(charge=1.6e-19, distance=1e-10)
    print(f"Electric field: {E_field:.2e} N/C")

    # Test Particle Physics
    pp = ParticlePhysics()
    particle1 = Particle(
        position=np.array([0.0, 0.0, 0.0]),
        velocity=np.array([1.0, 0.0, 0.0]),
        mass=1.0,
        charge=1.0
    )
    particle2 = Particle(
        position=np.array([1.0, 0.0, 0.0]),
        velocity=np.array([-1.0, 0.0, 0.0]),
        mass=1.0,
        charge=-1.0
    )
    pp.add_particle(particle1)
    pp.add_particle(particle2)
    pp.step()
    ke = pp.kinetic_energy()
    print(f"Particle physics: kinetic energy = {ke:.4f}")

    # Test Molecular Dynamics
    md = MolecularDynamics()
    md.initialize_lattice(n_atoms=8)
    md.step_verlet()
    temp = md.get_temperature()
    print(f"Molecular dynamics: temperature = {temp:.2f} K")

    print("\nComputational Physics initialized successfully")


if __name__ == "__main__":
    main()
