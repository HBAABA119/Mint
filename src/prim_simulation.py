"""
Prim Simulation Framework
Provides Monte Carlo simulation, agent-based modeling, discrete event simulation,
system dynamics, and stochastic processes.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class SimulationType(Enum):
    """Simulation types"""
    MONTE_CARLO = "monte_carlo"
    AGENT_BASED = "agent_based"
    DISCRETE_EVENT = "discrete_event"
    SYSTEM_DYNAMICS = "system_dynamics"
    STOCHASTIC = "stochastic"


@dataclass
class Agent:
    """Agent for agent-based modeling"""
    id: int
    position: Tuple[float, float]
    state: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)


class MonteCarloSimulation:
    """Monte Carlo simulation"""

    def __init__(self):
        self.samples: List[float] = []
        self.trials: int = 0

    def run(self, n_trials: int, distribution: Callable, *args) -> List[float]:
        """Run Monte Carlo simulation"""
        self.samples = [distribution(*args) for _ in range(n_trials)]
        self.trials = n_trials
        return self.samples

    def estimate_mean(self) -> float:
        """Estimate mean"""
        return np.mean(self.samples)

    def estimate_variance(self) -> float:
        """Estimate variance"""
        return np.var(self.samples)

    def confidence_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval"""
        from scipy import stats
        mean = np.mean(self.samples)
        std = np.std(self.samples)
        n = len(self.samples)

        alpha = 1 - confidence
        t_value = stats.t.ppf(1 - alpha/2, n - 1)
        margin = t_value * std / np.sqrt(n)

        return (mean - margin, mean + margin)

    def pi_estimation(self, n_points: int = 10000) -> float:
        """Estimate pi using Monte Carlo"""
        points_inside = 0

        for _ in range(n_points):
            x = random.random() * 2 - 1
            y = random.random() * 2 - 1

            if x**2 + y**2 <= 1:
                points_inside += 1

        return 4 * points_inside / n_points


class AgentBasedModel:
    """Agent-based modeling"""

    def __init__(self):
        self.agents: List[Agent] = []
        self.time_step = 0
        self.history: List[Dict[str, Any]] = []

    def add_agent(self, agent: Agent):
        """Add agent to model"""
        self.agents.append(agent)

    def remove_agent(self, agent_id: int):
        """Remove agent from model"""
        self.agents = [a for a in self.agents if a.id != agent_id]

    def step(self):
        """Advance simulation by one time step"""
        self.time_step += 1

        # Update agents
        for agent in self.agents:
            self._update_agent(agent)

        # Record state
        self.history.append({
            "time_step": self.time_step,
            "agents": len(self.agents),
            "state": [a.state.copy() for a in self.agents]
        })

    def _update_agent(self, agent: Agent):
        """Update agent state (simplified)"""
        # Move agent randomly
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        agent.position = (agent.position[0] + dx, agent.position[1] + dy)

        # Update state
        agent.state["x"] = agent.position[0]
        agent.state["y"] = agent.position[1]

    def get_statistics(self) -> Dict[str, float]:
        """Get simulation statistics"""
        if not self.agents:
            return {}

        positions = [a.position for a in self.agents]
        x_positions = [p[0] for p in positions]
        y_positions = [p[1] for p in positions]

        return {
            "num_agents": len(self.agents),
            "mean_x": np.mean(x_positions),
            "mean_y": np.mean(y_positions),
            "std_x": np.std(x_positions),
            "std_y": np.std(y_positions)
        }


class DiscreteEventSimulation:
    """Discrete event simulation"""

    def __init__(self):
        self.events: List[Tuple[float, Callable]] = []
        self.current_time = 0.0
        self.event_count = 0

    def schedule_event(self, time: float, event: Callable):
        """Schedule event at time"""
        self.events.append((time, event))
        self.events.sort(key=lambda x: x[0])

    def run(self, max_time: float = float('inf')):
        """Run simulation"""
        while self.events and self.current_time < max_time:
            time, event = self.events.pop(0)
            self.current_time = time
            event()
            self.event_count += 1

    def get_time(self) -> float:
        """Get current simulation time"""
        return self.current_time

    def get_event_count(self) -> int:
        """Get number of events processed"""
        return self.event_count


class SystemDynamics:
    """System dynamics modeling"""

    def __init__(self):
        self.variables: Dict[str, float] = {}
        self.equations: Dict[str, Callable] = {}
        self.time = 0.0
        self.history: List[Dict[str, float]] = []

    def add_variable(self, name: str, initial_value: float):
        """Add variable to model"""
        self.variables[name] = initial_value

    def add_equation(self, name: str, equation: Callable):
        """Add equation for variable"""
        self.equations[name] = equation

    def step(self, dt: float = 0.1):
        """Advance simulation by dt"""
        # Update variables using equations
        for name, equation in self.equations.items():
            self.variables[name] = equation(self.variables, self.time)

        self.time += dt

        # Record state
        self.history.append({
            "time": self.time,
            **self.variables.copy()
        })

    def run(self, duration: float, dt: float = 0.1):
        """Run simulation for duration"""
        steps = int(duration / dt)

        for _ in range(steps):
            self.step(dt)

    def get_history(self) -> List[Dict[str, float]]:
        """Get simulation history"""
        return self.history.copy()


class StochasticProcess:
    """Stochastic processes"""

    @staticmethod
    def random_walk(n_steps: int, step_size: float = 1.0) -> List[float]:
        """Generate random walk"""
        steps = np.random.normal(0, step_size, n_steps)
        return np.cumsum(steps).tolist()

    @staticmethod
    def brownian_motion(n_steps: int, dt: float = 0.01, volatility: float = 1.0) -> List[float]:
        """Generate Brownian motion"""
        steps = np.random.normal(0, volatility * np.sqrt(dt), n_steps)
        return np.cumsum(steps).tolist()

    @staticmethod
    def geometric_brownian_motion(n_steps: int, dt: float = 0.01, mu: float = 0.1,
                                sigma: float = 0.2, initial_price: float = 100.0) -> List[float]:
        """Generate geometric Brownian motion"""
        prices = [initial_price]

        for _ in range(n_steps):
            dW = np.random.normal(0, np.sqrt(dt))
            S_t = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * dW)
            prices.append(S_t)

        return prices

    @staticmethod
    def poisson_process(rate: float, duration: float) -> List[float]:
        """Generate Poisson process"""
        events = []
        t = 0.0

        while t < duration:
            inter_arrival = np.random.exponential(1.0 / rate)
            t += inter_arrival
            if t < duration:
                events.append(t)

        return events


class QueueSimulation:
    """Queue simulation"""

    def __init__(self, num_servers: int = 1):
        self.queue: List[float] = []
        self.num_servers = num_servers
        self.servers = [None] * num_servers
        self.current_time = 0.0
        self.completed_jobs = 0
        self.wait_times: List[float] = []

    def arrive(self, time: float, service_time: float):
        """Customer arrives"""
        self.current_time = time

        # Try to assign to free server
        for i, server in enumerate(self.servers):
            if server is None:
                self.servers[i] = self.current_time + service_time
                return

        # No free server, add to queue
        self.queue.append(self.current_time)

    def depart(self, time: float):
        """Customer departs"""
        self.current_time = time
        self.completed_jobs += 1

        # Find departing server
        for i, server in enumerate(self.servers):
            if server and server <= self.current_time:
                self.servers[i] = None

                # Assign next job from queue
                if self.queue:
                    arrival_time = self.queue.pop(0)
                    wait_time = self.current_time - arrival_time
                    self.wait_times.append(wait_time)

    def get_statistics(self) -> Dict[str, float]:
        """Get queue statistics"""
        return {
            "queue_length": len(self.queue),
            "completed_jobs": self.completed_jobs,
            "avg_wait_time": np.mean(self.wait_times) if self.wait_times else 0.0
        }


class CellularAutomaton:
    """Cellular automaton"""

    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.generation = 0

    def initialize_random(self, density: float = 0.5):
        """Initialize with random cells"""
        self.grid = (np.random.random((self.height, self.width)) < density).astype(int)

    def step(self):
        """Advance to next generation"""
        new_grid = np.zeros_like(self.grid)

        for i in range(self.height):
            for j in range(self.width):
                # Count neighbors
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.height and 0 <= nj < self.width:
                            neighbors += self.grid[ni, nj]

                # Apply rules (Conway's Game of Life)
                if self.grid[i, j] == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[i, j] = 0
                    else:
                        new_grid[i, j] = 1
                else:
                    if neighbors == 3:
                        new_grid[i, j] = 1

        self.grid = new_grid
        self.generation += 1

    def get_grid(self) -> np.ndarray:
        """Get current grid"""
        return self.grid.copy()


def create_monte_carlo() -> MonteCarloSimulation:
    """Create Monte Carlo simulation"""
    return MonteCarloSimulation()


def create_agent_based_model() -> AgentBasedModel:
    """Create agent-based model"""
    return AgentBasedModel()


def create_discrete_event() -> DiscreteEventSimulation:
    """Create discrete event simulation"""
    return DiscreteEventSimulation()


def main():
    """Main entry point for testing"""
    print("Testing Simulation Framework...")

    # Test Monte Carlo
    mc = create_monte_carlo()
    samples = mc.run(10000, random.random)
    print(f"Monte Carlo: mean={mc.estimate_mean():.4f}, var={mc.estimate_variance():.4f}")

    pi_estimate = mc.pi_estimation(10000)
    print(f"Pi estimate: {pi_estimate:.4f}")

    # Test Agent-Based Model
    abm = create_agent_based_model()
    for i in range(10):
        agent = Agent(id=i, position=(random.random() * 100, random.random() * 100))
        abm.add_agent(agent)

    abm.step()
    stats = abm.get_statistics()
    print(f"Agent-based model: {stats['num_agents']} agents")

    # Test Discrete Event Simulation
    des = create_discrete_event()
    des.schedule_event(1.0, lambda: print("Event at t=1"))
    des.schedule_event(2.0, lambda: print("Event at t=2"))
    des.run(max_time=3.0)
    print(f"Discrete event: {des.get_event_count()} events processed")

    # Test System Dynamics
    sd = SystemDynamics()
    sd.add_variable("x", 0.0)
    sd.add_variable("y", 1.0)
    sd.add_equation("x", lambda vars, t: vars["y"])
    sd.add_equation("y", lambda vars, t: -vars["x"])

    sd.run(duration=10.0, dt=0.1)
    print(f"System dynamics: {len(sd.get_history())} time steps")

    # Test Stochastic Process
    bm = StochasticProcess.brownian_motion(100)
    print(f"Brownian motion: {len(bm)} steps")

    gbm = StochasticProcess.geometric_brownian_motion(100)
    print(f"GBM: {len(gbm)} steps, final price={gbm[-1]:.2f}")

    # Test Queue Simulation
    queue_sim = QueueSimulation(num_servers=2)
    queue_sim.arrive(0.0, 1.0)
    queue_sim.arrive(0.5, 1.5)
    queue_sim.depart(1.0)
    queue_stats = queue_sim.get_statistics()
    print(f"Queue simulation: {queue_stats}")

    # Test Cellular Automaton
    ca = CellularAutomaton(width=50, height=50)
    ca.initialize_random(density=0.3)
    ca.step()
    print(f"Cellular automaton: generation {ca.generation}")

    print("\nSimulation Framework initialized successfully")


if __name__ == "__main__":
    main()
