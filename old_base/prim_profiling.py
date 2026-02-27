"""
Prim Advanced Profiling
Provides CPU profiling, memory profiling, call graph analysis,
performance tracing, and hot spot detection.
"""

import sys
import time
import tracemalloc
import cProfile
import pstats
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ProfilingType(Enum):
    """Profiling types"""
    CPU = "cpu"
    MEMORY = "memory"
    CALL_GRAPH = "call_graph"
    LINE_BY_LINE = "line_by_line"
    TRACING = "tracing"


@dataclass
class ProfileData:
    """Profile data"""
    function_name: str
    call_count: int
    total_time: float
    cum_time: float
    per_call_time: float
    memory_usage: int = 0


class CPUProfiler:
    """CPU profiler"""

    def __init__(self):
        self.profiler = cProfile.Profile()
        self.stats: Optional[pstats.Stats] = None

    def start(self):
        """Start profiling"""
        self.profiler.enable()

    def stop(self):
        """Stop profiling"""
        self.profiler.disable()
        self.stats = pstats.Stats(self.profiler)

    def profile_function(self, func: Callable, *args, **kwargs) -> Tuple[Any, pstats.Stats]:
        """Profile function"""
        self.start()
        result = func(*args, **kwargs)
        self.stop()
        return result, self.stats

    def get_stats(self) -> pstats.Stats:
        """Get profiling statistics"""
        return self.stats

    def get_top_functions(self, n: int = 10) -> List[ProfileData]:
        """Get top functions by time"""
        if not self.stats:
            return []

        stats_list = []
        for func, (cc, nc, tt, ct, callers) in self.stats.stats.items():
            stats_list.append(ProfileData(
                function_name=func,
                call_count=cc,
                total_time=tt,
                cum_time=ct,
                per_call_time=tt / cc if cc > 0 else 0
            ))

        stats_list.sort(key=lambda x: x.total_time, reverse=True)
        return stats_list[:n]

    def print_stats(self, sort_by: str = "cumulative"):
        """Print profiling statistics"""
        if self.stats:
            self.stats.strip_dirs()
            self.stats.sort_stats(sort_by)
            self.stats.print_stats()


class MemoryProfiler:
    """Memory profiler"""

    def __init__(self):
        self.snapshots: List[Tuple[float, int, int]] = []
        self.tracing = False

    def start_tracing(self):
        """Start memory tracing"""
        tracemalloc.start()
        self.tracing = True

    def stop_tracing(self):
        """Stop memory tracing"""
        tracemalloc.stop()
        self.tracing = False

    def take_snapshot(self) -> Tuple[float, int, int]:
        """Take memory snapshot"""
        current, peak = tracemalloc.get_traced_memory()
        snapshot = (time.time(), current, peak)
        self.snapshots.append(snapshot)
        return snapshot

    def profile_function(self, func: Callable, *args, **kwargs) -> Tuple[Any, Dict[str, int]]:
        """Profile function memory usage"""
        self.start_tracing()

        result = func(*args, **kwargs)

        current, peak = tracemalloc.get_traced_memory()
        self.stop_tracing()

        return result, {
            "current": current,
            "peak": peak
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if not self.snapshots:
            return {}

        current, peak = self.snapshots[-1][1:]
        return {
            "current": current,
            "peak": peak,
            "snapshots": len(self.snapshots)
        }


class CallGraphAnalyzer:
    """Call graph analyzer"""

    def __init__(self):
        self.call_graph: Dict[str, List[str]] = {}
        self.execution_times: Dict[str, float] = {}

    def build_graph(self, stats: pstats.Stats):
        """Build call graph from stats"""
        self.call_graph = {}
        self.execution_times = {}

        for func, (_, _, tt, ct, _) in stats.stats.items():
            self.execution_times[func] = ct

            # Build call graph
            self.call_graph[func] = []

        for func, (_, _, _, _, callers) in stats.stats.items():
            for caller in callers:
                if caller not in self.call_graph:
                    self.call_graph[caller] = []
                self.call_graph[caller].append(func)

    def get_hot_paths(self, n: int = 10) -> List[List[str]]:
        """Get hot execution paths"""
        paths = []

        for func in sorted(self.execution_times.keys(),
                         key=lambda f: self.execution_times[f],
                         reverse=True)[:n]:
            path = self._find_path(func)
            if path:
                paths.append(path)

        return paths

    def _find_path(self, func: str, path: Optional[List[str]] = None) -> Optional[List[str]]:
        """Find path to function"""
        if path is None:
            path = []

        path.append(func)

        # Find callers
        callers = []
        for caller, callees in self.call_graph.items():
            if func in callees:
                callers.append(caller)

        # Recursively find caller path
        for caller in callers:
            result = self._find_path(caller, path)
            if result:
                return result

        return path

    def visualize(self) -> str:
        """Generate call graph visualization"""
        # Simplified DOT format
        dot = "digraph call_graph {\n"

        for caller, callees in self.call_graph.items():
            caller_name = caller.split(":")[0]
            for callee in callees:
                callee_name = callee.split(":")[0]
                dot += f'  "{caller_name}" -> "{callee_name}";\n'

        dot += "}"
        return dot


class TracingProfiler:
    """Tracing profiler"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.tracing = False

    def start(self):
        """Start tracing"""
        self.tracing = True

    def stop(self):
        """Stop tracing"""
        self.tracing = False

    def trace_function(self, func: Callable, *args, **kwargs) -> Any:
        """Trace function execution"""
        if not self.tracing:
            return func(*args, **kwargs)

        start_time = time.time()
        start_memory = sys.getsizeof([]) * len(gc.get_objects())

        self.events.append({
            "type": "call",
            "function": func.__name__,
            "time": start_time,
            "memory": start_memory
        })

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            self.events.append({
                "type": "exception",
                "function": func.__name__,
                "error": str(e),
                "time": time.time()
            })
            raise

        end_time = time.time()
        end_memory = sys.getsizeof([]) * len(gc.get_objects())

        self.events.append({
            "type": "return",
            "function": func.__name__,
            "time": end_time,
            "duration": end_time - start_time,
            "memory_delta": end_memory - start_memory
        })

        return result

    def get_events(self) -> List[Dict[str, Any]]:
        """Get traced events"""
        return self.events.copy()

    def get_hot_spots(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get hot spots"""
        # Group events by function
        function_times: Dict[str, float] = {}

        for event in self.events:
            if event["type"] == "return":
                func = event["function"]
                if func not in function_times:
                    function_times[func] = 0
                function_times[func] += event.get("duration", 0)

        # Sort by total time
        sorted_funcs = sorted(function_times.items(),
                            key=lambda x: x[1],
                            reverse=True)

        return [
            {
                "function": func,
                "total_time": time,
                "avg_time": time / self._get_call_count(func)
            }
            for func, time in sorted_funcs[:n]
        ]

    def _get_call_count(self, func: str) -> int:
        """Get call count for function"""
        count = 0
        for event in self.events:
            if event["type"] == "call" and event["function"] == func:
                count += 1
        return count


class LineProfiler:
    """Line-by-line profiler"""

    def __init__(self):
        self.line_times: Dict[str, List[float]] = {}

    def profile_function(self, func: Callable) -> Callable:
        """Profile function line by line"""
        def wrapper(*args, **kwargs):
            import line_profiler
            lp = line_profiler.LineProfiler()

            lp_wrapper = lp(func)
            lp_wrapper(*args, **kwargs)

            # Get stats
            stats = lp.get_stats()

            func_name = func.__name__
            if func_name not in self.line_times:
                self.line_times[func_name] = []

            for line, hits, time in stats:
                self.line_times[func_name].append(time)

            return result

        return wrapper

    def get_slow_lines(self, func_name: str, n: int = 10) -> List[Tuple[int, float]]:
        """Get slowest lines"""
        if func_name not in self.line_times:
            return []

        lines = self.line_times[func_name]
        sorted_lines = sorted(enumerate(lines), key=lambda x: x[1], reverse=True)
        return sorted_lines[:n]


class PerformanceAnalyzer:
    """Performance analysis tools"""

    def __init__(self):
        self.cpu_profiler = CPUProfiler()
        self.memory_profiler = MemoryProfiler()
        self.call_graph_analyzer = CallGraphAnalyzer()
        self.tracing_profiler = TracingProfiler()

    def analyze_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Comprehensive function analysis"""
        results = {}

        # CPU profiling
        cpu_result, cpu_stats = self.cpu_profiler.profile_function(func, *args, **kwargs)
        results["cpu"] = {
            "result": cpu_result,
            "top_functions": self.cpu_profiler.get_top_functions(5)
        }

        # Memory profiling
        mem_result, mem_stats = self.memory_profiler.profile_function(func, *args, **kwargs)
        results["memory"] = {
            "result": mem_result,
            "stats": mem_stats
        }

        # Call graph
        if cpu_stats:
            self.call_graph_analyzer.build_graph(cpu_stats)
            results["call_graph"] = {
                "hot_paths": self.call_graph_analyzer.get_hot_paths(3)
            }

        return results

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "cpu_stats": self.cpu_profiler.get_stats() if self.cpu_profiler.stats else None,
            "memory_stats": self.memory_profiler.get_memory_stats(),
            "tracing_events": len(self.tracing_profiler.get_events()),
            "hot_spots": self.tracing_profiler.get_hot_spots()
        }


def create_profiler() -> PerformanceAnalyzer:
    """Create performance profiler"""
    return PerformanceAnalyzer()


def main():
    """Main entry point for testing"""
    print("Testing Advanced Profiling...")

    # Create profiler
    profiler = create_profiler()

    # Test function
    def test_function(n):
        result = 0
        for i in range(n):
            result += i
        return result

    # Analyze function
    results = profiler.analyze_function(test_function, 1000)
    print(f"CPU top functions: {len(results['cpu']['top_functions'])}")

    # Get summary
    summary = profiler.get_summary()
    print(f"Summary: {list(summary.keys())}")

    # Test tracing
    tracer = profiler.tracing_profiler
    tracer.start()
    test_function(100)
    tracer.stop()

    hot_spots = tracer.get_hot_spots()
    print(f"Hot spots: {len(hot_spots)}")

    print("\nAdvanced Profiling initialized successfully")


if __name__ == "__main__":
    main()
