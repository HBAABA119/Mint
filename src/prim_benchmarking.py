"""
Prim Benchmarking System
Provides performance benchmarking, regression testing, performance tracking,
comparative analysis, and benchmark reporting.
"""

import time
import statistics
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class BenchmarkType(Enum):
    """Benchmark types"""
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    CPU = "cpu"
    MEMORY = "memory"
    I_O = "i_o"


@dataclass
class BenchmarkResult:
    """Benchmark result"""
    name: str
    iterations: int
    total_time: float
    min_time: float
    max_time: float
    mean_time: float
    median_time: float
    std_dev: float
    operations_per_second: float


class Benchmark:
    """Benchmark runner"""

    def __init__(self):
        self.results: Dict[str, BenchmarkResult] = {}
        self.history: List[Dict[str, Any]] = []

    def run(self, name: str, func: Callable, iterations: int = 1000,
            warmup: int = 100) -> BenchmarkResult:
        """Run benchmark"""
        # Warmup
        for _ in range(warmup):
            func()

        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)

        # Calculate statistics
        total_time = sum(times)
        min_time = min(times)
        max_time = max(times)
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        ops_per_sec = iterations / total_time if total_time > 0 else 0

        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            min_time=min_time,
            max_time=max_time,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            operations_per_second=ops_per_sec
        )

        self.results[name] = result
        self.history.append({
            "name": name,
            "timestamp": time.time(),
            "mean_time": mean_time,
            "ops_per_sec": ops_per_sec
        })

        return result

    def compare(self, name1: str, name2: str) -> Dict[str, float]:
        """Compare two benchmarks"""
        if name1 not in self.results or name2 not in self.results:
            raise ValueError("Benchmarks not found")

        result1 = self.results[name1]
        result2 = self.results[name2]

        return {
            "speedup": result2.mean_time / result1.mean_time,
            "relative_performance": result1.operations_per_second / result2.operations_per_second
        }

    def get_history(self, name: str) -> List[Dict[str, Any]]:
        """Get benchmark history"""
        return [h for h in self.history if h["name"] == name]


class RegressionDetector:
    """Performance regression detection"""

    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold
        self.baselines: Dict[str, float] = {}

    def set_baseline(self, name: str, value: float):
        """Set baseline value"""
        self.baselines[name] = value

    def check_regression(self, name: str, current_value: float) -> bool:
        """Check for performance regression"""
        if name not in self.baselines:
            self.baselines[name] = current_value
            return False

        baseline = self.baselines[name]
        regression = (baseline - current_value) / baseline

        return regression > self.threshold

    def get_regressions(self) -> Dict[str, float]:
        """Get all regressions"""
        return {name: (baseline - current) / baseline
                for name, (baseline, current) in self.baselines.items()}


class PerformanceTracker:
    """Performance tracking over time"""

    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}
        self.timestamps: Dict[str, List[float]] = {}

    def record(self, name: str, value: float):
        """Record performance measurement"""
        if name not in self.measurements:
            self.measurements[name] = []
            self.timestamps[name] = []

        self.measurements[name].append(value)
        self.timestamps[name].append(time.time())

    def get_trend(self, name: str) -> str:
        """Get performance trend"""
        if name not in self.measurements or len(self.measurements[name]) < 2:
            return "insufficient_data"

        values = self.measurements[name]
        recent = values[-10:]
        older = values[-20:-10] if len(values) >= 20 else values[:10]

        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)

        if recent_avg > older_avg * 1.05:
            return "degrading"
        elif recent_avg < older_avg * 0.95:
            return "improving"
        else:
            return "stable"

    def get_statistics(self, name: str) -> Dict[str, float]:
        """Get performance statistics"""
        if name not in self.measurements:
            return {}

        values = self.measurements[name]

        return {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0
        }


class BenchmarkSuite:
    """Benchmark suite"""

    def __init__(self, name: str = "suite"):
        self.name = name
        self.benchmarks: Dict[str, Callable] = {}
        self.benchmark = Benchmark()

    def add_benchmark(self, name: str, func: Callable):
        """Add benchmark to suite"""
        self.benchmarks[name] = func

    def run_all(self, iterations: int = 1000) -> Dict[str, BenchmarkResult]:
        """Run all benchmarks"""
        results = {}

        for name, func in self.benchmarks.items():
            result = self.benchmark.run(name, func, iterations)
            results[name] = result

        return results

    def run_selected(self, names: List[str], iterations: int = 1000) -> Dict[str, BenchmarkResult]:
        """Run selected benchmarks"""
        results = {}

        for name in names:
            if name in self.benchmarks:
                func = self.benchmarks[name]
                result = self.benchmark.run(name, func, iterations)
                results[name] = result

        return results


class BenchmarkReporter:
    """Benchmark reporting"""

    def __init__(self):
        self.reports: List[Dict[str, Any]] = []

    def generate_report(self, results: Dict[str, BenchmarkResult]) -> str:
        """Generate benchmark report"""
        lines = []
        lines.append("=" * 60)
        lines.append("Benchmark Report")
        lines.append("=" * 60)
        lines.append("")

        for name, result in results.items():
            lines.append(f"Benchmark: {name}")
            lines.append(f"  Iterations: {result.iterations}")
            lines.append(f"  Total Time: {result.total_time:.4f}s")
            lines.append(f"  Mean Time: {result.mean_time:.6f}s")
            lines.append(f"  Median Time: {result.median_time:.6f}s")
            lines.append(f"  Std Dev: {result.std_dev:.6f}s")
            lines.append(f"  Ops/sec: {result.operations_per_second:.2f}")
            lines.append("")

        return "\n".join(lines)

    def save_report(self, results: Dict[str, BenchmarkResult], filepath: str):
        """Save report to file"""
        report = self.generate_report(results)

        with open(filepath, 'w') as f:
            f.write(report)

    def generate_comparison_report(self, baseline: Dict[str, BenchmarkResult],
                                    current: Dict[str, BenchmarkResult]) -> str:
        """Generate comparison report"""
        lines = []
        lines.append("=" * 60)
        lines.append("Performance Comparison Report")
        lines.append("=" * 60)
        lines.append("")

        for name in baseline:
            if name in current:
                base = baseline[name]
                curr = current[name]

                speedup = curr.mean_time / base.mean_time
                improvement = (base.mean_time - curr.mean_time) / base.mean_time * 100

                lines.append(f"Benchmark: {name}")
                lines.append(f"  Baseline: {base.mean_time:.6f}s")
                lines.append(f"  Current: {curr.mean_time:.6f}s")
                lines.append(f"  Speedup: {speedup:.2f}x")
                lines.append(f"  Improvement: {improvement:.2f}%")
                lines.append("")

        return "\n".join(lines)


def create_benchmark_suite(name: str = "suite") -> BenchmarkSuite:
    """Create benchmark suite"""
    return BenchmarkSuite(name)


def main():
    """Main entry point for testing"""
    print("Testing Benchmarking System...")

    # Create benchmark suite
    suite = create_benchmark_suite("test_suite")

    # Add benchmarks
    def fast_operation():
        return sum(range(100))

    def slow_operation():
        return sum(range(1000))

    suite.add_benchmark("fast", fast_operation)
    suite.add_benchmark("slow", slow_operation)

    # Run benchmarks
    results = suite.run_all(iterations=1000)
    print(f"Benchmarks run: {len(results)}")

    # Generate report
    reporter = BenchmarkReporter()
    report = reporter.generate_report(results)
    print(f"Report: {len(report)} characters")

    # Test regression detection
    regressor = RegressionDetector()
    regressor.set_baseline("test", 1.0)
    is_regression = regressor.check_regression("test", 0.8)
    print(f"Regression detected: {is_regression}")

    # Test performance tracker
    tracker = PerformanceTracker()
    for i in range(10):
        tracker.record("test", 1.0 + i * 0.01)

    trend = tracker.get_trend("test")
    print(f"Trend: {trend}")

    # Test comparison
    comparison = suite.benchmark.compare("fast", "slow")
    print(f"Comparison: {comparison}")

    print("\nBenchmarking System initialized successfully")


if __name__ == "__main__":
    main()
