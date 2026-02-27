"""
Prim Performance Profiler
Provides CPU usage analysis, memory allocation tracking, garbage collection monitoring,
function call frequency analysis, and time-based performance reports.
"""

import sys
import time
import tracemalloc
import gc
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json


class ProfilerMode(Enum):
    """Profiler modes"""
    CPU = "cpu"
    MEMORY = "memory"
    BOTH = "both"


@dataclass
class FunctionCall:
    """Function call information"""
    name: str
    file_path: str
    line_number: int
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    self_time: float = 0.0

    def update_stats(self, duration: float):
        """Update call statistics"""
        self.call_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.avg_time = self.total_time / self.call_count


@dataclass
class MemorySnapshot:
    """Memory snapshot at a point in time"""
    timestamp: float
    allocated: int
    freed: int
    current_usage: int
    peak_usage: int


@dataclass
class GCSnapshot:
    """Garbage collection snapshot"""
    timestamp: float
    generation: int
    collected: int
    uncollectable: int


@dataclass
class PerformanceReport:
    """Complete performance report"""
    start_time: float
    end_time: float
    total_duration: float
    function_calls: List[FunctionCall]
    memory_snapshots: List[MemorySnapshot]
    gc_snapshots: List[GCSnapshot]
    memory_leaks: List[Dict]


class PrimProfiler:
    """Main performance profiler for Prim language"""

    def __init__(self, mode: ProfilerMode = ProfilerMode.BOTH):
        self.mode = mode
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.is_running = False
        
        # CPU profiling
        self.function_calls: Dict[str, FunctionCall] = {}
        self.call_stack: List[Tuple[str, float]] = []
        self.function_timings: Dict[str, List[float]] = defaultdict(list)
        
        # Memory profiling
        self.memory_snapshots: List[MemorySnapshot] = []
        self.memory_leaks: List[Dict] = []
        self.peak_memory = 0
        self.initial_memory = 0
        
        # GC monitoring
        self.gc_snapshots: List[GCSnapshot] = []
        self.gc_stats = {
            'generation0': 0,
            'generation1': 0,
            'generation2': 0
        }
        
        # Callbacks
        self.gc_callback = None

    def start(self):
        """Start profiling"""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_time = time.time()
        
        # Start memory tracking
        if self.mode in [ProfilerMode.MEMORY, ProfilerMode.BOTH]:
            tracemalloc.start()
            self.initial_memory = tracemalloc.get_traced_memory()[0]
            self.peak_memory = self.initial_memory
        
        # Setup GC monitoring
        if self.mode in [ProfilerMode.MEMORY, ProfilerMode.BOTH]:
            self.gc_callback = self._gc_callback
            gc.callbacks.append(self.gc_callback)
        
        # Take initial snapshot
        self._take_memory_snapshot()

    def stop(self) -> PerformanceReport:
        """Stop profiling and generate report"""
        if not self.is_running:
            raise RuntimeError("Profiler is not running")
        
        self.is_running = False
        self.end_time = time.time()
        
        # Take final snapshot
        self._take_memory_snapshot()
        
        # Stop memory tracking
        if self.mode in [ProfilerMode.MEMORY, ProfilerMode.BOTH]:
            tracemalloc.stop()
        
        # Remove GC callback
        if self.gc_callback and self.gc_callback in gc.callbacks:
            gc.callbacks.remove(self.gc_callback)
        
        # Generate report
        report = PerformanceReport(
            start_time=self.start_time,
            end_time=self.end_time,
            total_duration=self.end_time - self.start_time,
            function_calls=list(self.function_calls.values()),
            memory_snapshots=self.memory_snapshots,
            gc_snapshots=self.gc_snapshots,
            memory_leaks=self.memory_leaks
        )
        
        return report

    def function_enter(self, name: str, file_path: str, line_number: int):
        """Record function entry"""
        if not self.is_running:
            return
        
        # Create or update function call info
        key = f"{file_path}:{name}"
        if key not in self.function_calls:
            self.function_calls[key] = FunctionCall(
                name=name,
                file_path=file_path,
                line_number=line_number
            )
        
        # Push to call stack
        self.call_stack.append((key, time.time()))

    def function_exit(self, name: str, file_path: str):
        """Record function exit"""
        if not self.is_running or not self.call_stack:
            return
        
        key = f"{file_path}:{name}"
        
        # Find matching entry
        for i, (stack_key, entry_time) in enumerate(self.call_stack):
            if stack_key == key:
                duration = time.time() - entry_time
                self.function_calls[key].update_stats(duration)
                self.function_timings[key].append(duration)
                del self.call_stack[i]
                break

    def record_memory_allocation(self, size: int):
        """Record memory allocation"""
        if not self.is_running:
            return
        
        current, peak = tracemalloc.get_traced_memory()
        self.peak_memory = max(self.peak_memory, peak)

    def _take_memory_snapshot(self):
        """Take a memory snapshot"""
        if self.mode not in [ProfilerMode.MEMORY, ProfilerMode.BOTH]:
            return
        
        try:
            current, peak = tracemalloc.get_traced_memory()
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                allocated=current,
                freed=0,  # Simplified
                current_usage=current,
                peak_usage=peak
            )
            self.memory_snapshots.append(snapshot)
        except:
            pass

    def _gc_callback(self, phase: str, info: Dict):
        """Garbage collection callback"""
        if phase == "start":
            return
        
        generation = info.get('generation', 0)
        collected = info.get('collected', 0)
        uncollectable = info.get('uncollectable', 0)
        
        snapshot = GCSnapshot(
            timestamp=time.time(),
            generation=generation,
            collected=collected,
            uncollectable=uncollectable
        )
        self.gc_snapshots.append(snapshot)
        
        # Update stats
        if generation == 0:
            self.gc_stats['generation0'] += 1
        elif generation == 1:
            self.gc_stats['generation1'] += 1
        elif generation == 2:
            self.gc_stats['generation2'] += 1

    def get_hotspots(self, top_n: int = 10) -> List[FunctionCall]:
        """Get top N functions by total time"""
        return sorted(
            self.function_calls.values(),
            key=lambda f: f.total_time,
            reverse=True
        )[:top_n]

    def get_memory_usage(self) -> Dict[str, int]:
        """Get current memory usage"""
        if self.mode not in [ProfilerMode.MEMORY, ProfilerMode.BOTH]:
            return {}
        
        try:
            current, peak = tracemalloc.get_traced_memory()
            return {
                'current': current,
                'peak': peak,
                'initial': self.initial_memory,
                'increase': current - self.initial_memory
            }
        except:
            return {}

    def get_gc_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics"""
        return self.gc_stats

    def format_report(self, report: PerformanceReport) -> str:
        """Format performance report as text"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("Prim Performance Report")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary
        lines.append("Summary:")
        lines.append(f"  Total Duration: {report.total_duration:.4f} seconds")
        lines.append(f"  Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.start_time))}")
        lines.append(f"  End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.end_time))}")
        lines.append("")
        
        # CPU Profiling
        if report.function_calls:
            lines.append("-" * 70)
            lines.append("CPU Profiling")
            lines.append("-" * 70)
            lines.append("")
            
            # Hotspots
            hotspots = sorted(report.function_calls, key=lambda f: f.total_time, reverse=True)[:10]
            if hotspots:
                lines.append("Top 10 Functions by Total Time:")
                lines.append("")
                lines.append(f"{'Function':<40} {'Calls':>8} {'Total':>10} {'Avg':>10} {'Min':>10} {'Max':>10}")
                lines.append("-" * 90)
                
                for func in hotspots:
                    name = f"{func.name} ({func.file_path}:{func.line_number})"
                    lines.append(f"{name:<40} {func.call_count:>8} {func.total_time:>10.4f} {func.avg_time:>10.4f} {func.min_time:>10.4f} {func.max_time:>10.4f}")
                lines.append("")
        
        # Memory Profiling
        if report.memory_snapshots:
            lines.append("-" * 70)
            lines.append("Memory Profiling")
            lines.append("-" * 70)
            lines.append("")
            
            if report.memory_snapshots:
                first = report.memory_snapshots[0]
                last = report.memory_snapshots[-1]
                
                lines.append("Memory Usage:")
                lines.append(f"  Initial: {self._format_bytes(first.current_usage)}")
                lines.append(f"  Final: {self._format_bytes(last.current_usage)}")
                lines.append(f"  Peak: {self._format_bytes(last.peak_usage)}")
                lines.append(f"  Increase: {self._format_bytes(last.current_usage - first.current_usage)}")
                lines.append("")
        
        # GC Statistics
        if report.gc_snapshots:
            lines.append("-" * 70)
            lines.append("Garbage Collection")
            lines.append("-" * 70)
            lines.append("")
            
            lines.append("GC Statistics:")
            lines.append(f"  Generation 0: {self.gc_stats['generation0']} collections")
            lines.append(f"  Generation 1: {self.gc_stats['generation1']} collections")
            lines.append(f"  Generation 2: {self.gc_stats['generation2']} collections")
            
            total_collected = sum(s.collected for s in report.gc_snapshots)
            lines.append(f"  Total Objects Collected: {total_collected}")
            lines.append("")
        
        return "\n".join(lines)

    def format_report_json(self, report: PerformanceReport) -> str:
        """Format performance report as JSON"""
        data = {
            'summary': {
                'total_duration': report.total_duration,
                'start_time': report.start_time,
                'end_time': report.end_time
            },
            'function_calls': [
                {
                    'name': f.name,
                    'file_path': f.file_path,
                    'line_number': f.line_number,
                    'call_count': f.call_count,
                    'total_time': f.total_time,
                    'min_time': f.min_time,
                    'max_time': f.max_time,
                    'avg_time': f.avg_time
                }
                for f in report.function_calls
            ],
            'memory_snapshots': [
                {
                    'timestamp': s.timestamp,
                    'allocated': s.allocated,
                    'current_usage': s.current_usage,
                    'peak_usage': s.peak_usage
                }
                for s in report.memory_snapshots
            ],
            'gc_snapshots': [
                {
                    'timestamp': s.timestamp,
                    'generation': s.generation,
                    'collected': s.collected,
                    'uncollectable': s.uncollectable
                }
                for s in report.gc_snapshots
            ],
            'gc_stats': self.gc_stats
        }
        
        return json.dumps(data, indent=2)

    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes as human-readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"


class ProfilerDecorator:
    """Decorator for profiling functions"""

    def __init__(self, profiler: PrimProfiler):
        self.profiler = profiler

    def __call__(self, func):
        """Wrap function for profiling"""
        def wrapper(*args, **kwargs):
            # Get function info
            name = func.__name__
            file_path = func.__code__.co_filename
            line_number = func.__code__.co_firstlineno
            
            # Record entry
            self.profiler.function_enter(name, file_path, line_number)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                return result
            finally:
                # Record exit
                self.profiler.function_exit(name, file_path)
        
        return wrapper


def profile_function(profiler: PrimProfiler):
    """Decorator factory for profiling functions"""
    return ProfilerDecorator(profiler)


class ProfilerCLI:
    """Command-line interface for profiler"""

    def __init__(self, profiler: PrimProfiler):
        self.profiler = profiler

    def run(self, script_path: str, output_format: str = "text"):
        """Profile a script"""
        print(f"Profiling: {script_path}")
        print(f"Mode: {self.profiler.mode.value}")
        print("")
        
        # Start profiling
        self.profiler.start()
        
        try:
            # Execute script
            with open(script_path, 'r') as f:
                code = f.read()
            
            # Simple execution (in real implementation, use the interpreter)
            exec(code, {})
            
        except Exception as e:
            print(f"Error executing script: {e}")
        finally:
            # Stop profiling and generate report
            report = self.profiler.stop()
            
            print("")
            print("=" * 70)
            print("Profiling Complete")
            print("=" * 70)
            print("")
            
            if output_format == "json":
                print(self.profiler.format_report_json(report))
            else:
                print(self.profiler.format_report(report))


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Prim Performance Profiler')
    parser.add_argument('script', help='Script to profile')
    parser.add_argument('--mode', choices=['cpu', 'memory', 'both'], default='both',
                       help='Profiling mode')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    mode = ProfilerMode(args.mode)
    profiler = PrimProfiler(mode)
    cli = ProfilerCLI(profiler)
    
    cli.run(args.script, args.format)


if __name__ == "__main__":
    main()
