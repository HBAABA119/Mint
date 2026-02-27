"""
Prim Memory Manager
Provides advanced GC strategies, memory pooling, leak detection,
heap analysis, and custom allocators.
"""

import gc
import sys
import time
import threading
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class GCStrategy(Enum):
    """Garbage collection strategies"""
    MARK_AND_SWEEP = "mark_and_sweep"
    GENERATIONAL = "generational"
    REFERENCE_COUNTING = "reference_counting"
    HYBRID = "hybrid"


class MemoryPoolType(Enum):
    """Memory pool types"""
    OBJECT_POOL = "object_pool"
    BUFFER_POOL = "buffer_pool"
    THREAD_LOCAL = "thread_local"
    ARENA = "arena"


@dataclass
class MemoryBlock:
    """Memory block"""
    address: int
    size: int
    allocated: bool = False
    data: Optional[bytes] = None


@dataclass
class MemoryStats:
    """Memory statistics"""
    total_allocated: int = 0
    total_freed: int = 0
    current_usage: int = 0
    peak_usage: int = 0
    allocations: int = 0
    frees: int = 0
    gc_runs: int = 0
    gc_time: float = 0.0


class CustomGC:
    """Custom garbage collector"""

    def __init__(self, strategy: GCStrategy = GCStrategy.GENERATIONAL):
        self.strategy = strategy
        self.stats = MemoryStats()
        self.generation_thresholds = [1000, 10000]
        self.generation_counts = [0, 0, 0]

    def collect(self, generation: int = 0) -> int:
        """Run garbage collection"""
        start_time = time.time()
        freed = 0

        if self.strategy == GCStrategy.MARK_AND_SWEEP:
            freed = self._mark_and_sweep()
        elif self.strategy == GCStrategy.GENERATIONAL:
            freed = self._generational_gc(generation)
        elif self.strategy == GCStrategy.REFERENCE_COUNTING:
            freed = self._reference_counting_gc()
        elif self.strategy == GCStrategy.HYBRID:
            freed = self._hybrid_gc()

        self.stats.gc_runs += 1
        self.stats.gc_time += time.time() - start_time

        return freed

    def _mark_and_sweep(self) -> int:
        """Mark and sweep GC"""
        # Get all objects
        objects = gc.get_objects()
        marked = set()

        # Mark phase
        for obj in objects:
            if gc.is_tracked(obj):
                self._mark_from(obj, marked)

        # Sweep phase
        freed = 0
        for obj in objects:
            if obj not in marked and gc.is_tracked(obj):
                gc.collect()
                freed += 1

        return freed

    def _mark_from(self, obj, marked: set):
        """Mark reachable objects"""
        if obj in marked:
            return

        marked.add(obj)

        for ref in gc.get_referents(obj):
            self._mark_from(ref, marked)

    def _generational_gc(self, generation: int) -> int:
        """Generational GC"""
        self.generation_counts[generation] += 1

        # Only collect if threshold exceeded
        if self.generation_counts[generation] < self.generation_thresholds[generation]:
            return 0

        # Reset count
        self.generation_counts[generation] = 0

        # Collect this and younger generations
        freed = 0
        for gen in range(generation, 3):
            freed += self.collect()

        return freed

    def _reference_counting_gc(self) -> int:
        """Reference counting GC"""
        # Python's built-in GC handles this
        return gc.collect()

    def _hybrid_gc(self) -> int:
        """Hybrid GC approach"""
        # Use reference counting for young objects
        young_freed = gc.collect()

        # Use mark-and-sweep for old objects
        old_freed = self._mark_and_sweep()

        return young_freed + old_freed

    def get_stats(self) -> MemoryStats:
        """Get GC statistics"""
        self.stats.current_usage = sys.getsizeof([]) * len(gc.get_objects())
        self.stats.peak_usage = max(self.stats.peak_usage, self.stats.current_usage)
        return self.stats


class MemoryPool:
    """Memory pool for object reuse"""

    def __init__(self, pool_type: MemoryPoolType = MemoryPoolType.OBJECT_POOL,
                 initial_size: int = 100):
        self.pool_type = pool_type
        self.pool: List[Any] = []
        self.max_size = initial_size
        self.hits = 0
        self.misses = 0

    def acquire(self) -> Any:
        """Acquire object from pool"""
        if self.pool:
            self.hits += 1
            return self.pool.pop()

        self.misses += 1
        return self._create_object()

    def release(self, obj: Any):
        """Release object back to pool"""
        if len(self.pool) < self.max_size:
            self.pool.append(obj)

    def _create_object(self) -> Any:
        """Create new object (simplified)"""
        return {}

    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics"""
        return {
            "pool_size": len(self.pool),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }


class MemoryLeakDetector:
    """Memory leak detection"""

    def __init__(self):
        self.snapshots: List[Dict[str, int]] = []
        self.threshold = 1000

    def take_snapshot(self) -> Dict[str, int]:
        """Take memory snapshot"""
        snapshot = {
            "objects": len(gc.get_objects()),
            "timestamp": time.time()
        }
        self.snapshots.append(snapshot)
        return snapshot

    def detect_leak(self) -> bool:
        """Detect if memory is leaking"""
        if len(self.snapshots) < 2:
            return False

        # Compare latest snapshots
        recent = self.snapshots[-5:]
        growth = [recent[i+1]["objects"] - recent[i]["objects"]
                  for i in range(len(recent) - 1)]

        # Check if consistently growing
        return all(g > self.threshold for g in growth)

    def find_leaking_objects(self) -> List[Tuple[type, int]]:
        """Find objects with high counts"""
        object_counts = {}

        for obj in gc.get_objects():
            obj_type = type(obj)
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1

        # Sort by count
        sorted_counts = sorted(object_counts.items(),
                               key=lambda x: x[1], reverse=True)

        return sorted_counts[:10]


class HeapAnalyzer:
    """Heap analysis tools"""

    def __init__(self):
        self.gc = CustomGC()

    def analyze_heap(self) -> Dict[str, Any]:
        """Analyze heap usage"""
        objects = gc.get_objects()

        # Count by type
        type_counts = {}
        for obj in objects:
            obj_type = type(obj).__name__
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

        # Calculate sizes
        sizes = [sys.getsizeof(obj) for obj in objects]
        total_size = sum(sizes)
        avg_size = total_size / len(sizes) if sizes else 0

        return {
            "total_objects": len(objects),
            "total_size": total_size,
            "average_size": avg_size,
            "type_counts": dict(sorted(type_counts.items(),
                                       key=lambda x: x[1], reverse=True)[:10])
        }

    def find_largest_objects(self, n: int = 10) -> List[Tuple[Any, int]]:
        """Find largest objects"""
        objects = gc.get_objects()
        sized_objects = [(obj, sys.getsizeof(obj)) for obj in objects]
        sized_objects.sort(key=lambda x: x[1], reverse=True)
        return sized_objects[:n]

    def analyze_references(self, obj: Any) -> Dict[str, Any]:
        """Analyze object references"""
        referents = gc.get_referents(obj)
        referrers = gc.get_referrers(obj)

        return {
            "referents_count": len(referents),
            "referrers_count": len(referrers),
            "referent_types": [type(r).__name__ for r in referents],
            "referrer_types": [type(r).__name__ for r in referrers]
        }


class CustomAllocator:
    """Custom memory allocator"""

    def __init__(self):
        self.blocks: List[MemoryBlock] = []
        self.heap_size = 1024 * 1024  # 1MB
        self.allocated = 0

    def allocate(self, size: int) -> MemoryBlock:
        """Allocate memory block"""
        # Find free block
        for block in self.blocks:
            if not block.allocated and block.size >= size:
                block.allocated = True
                self.allocated += size
                return block

        # Create new block
        address = len(self.blocks)
        block = MemoryBlock(
            address=address,
            size=size,
            allocated=True
        )
        self.blocks.append(block)
        self.allocated += size

        return block

    def free(self, block: MemoryBlock):
        """Free memory block"""
        if block.allocated:
            block.allocated = False
            self.allocated -= block.size
            block.data = None

    def get_stats(self) -> Dict[str, Any]:
        """Get allocator statistics"""
        total_blocks = len(self.blocks)
        allocated_blocks = sum(1 for b in self.blocks if b.allocated)
        free_blocks = total_blocks - allocated_blocks

        return {
            "total_blocks": total_blocks,
            "allocated_blocks": allocated_blocks,
            "free_blocks": free_blocks,
            "allocated_memory": self.allocated,
            "utilization": allocated_blocks / total_blocks if total_blocks > 0 else 0
        }


class MemoryProfiler:
    """Memory profiling"""

    def __init__(self):
        self.profiles: List[Dict[str, Any]] = []

    def profile_function(self, func: Callable, *args, **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """Profile function memory usage"""
        gc.collect()
        start_memory = sys.getsizeof([]) * len(gc.get_objects())

        result = func(*args, **kwargs)

        gc.collect()
        end_memory = sys.getsizeof([]) * len(gc.get_objects())

        profile = {
            "function": func.__name__,
            "start_memory": start_memory,
            "end_memory": end_memory,
            "memory_delta": end_memory - start_memory,
            "timestamp": time.time()
        }

        self.profiles.append(profile)

        return result, profile

    def get_memory_usage(self) -> int:
        """Get current memory usage"""
        return sys.getsizeof([]) * len(gc.get_objects())

    def get_peak_memory(self) -> int:
        """Get peak memory usage"""
        if not self.profiles:
            return 0

        return max(p["end_memory"] for p in self.profiles)


def create_gc(strategy: GCStrategy = GCStrategy.GENERATIONAL) -> CustomGC:
    """Create garbage collector"""
    return CustomGC(strategy)


def create_memory_pool(pool_type: MemoryPoolType = MemoryPoolType.OBJECT_POOL) -> MemoryPool:
    """Create memory pool"""
    return MemoryPool(pool_type)


def main():
    """Main entry point for testing"""
    print("Testing Memory Manager...")

    # Test Custom GC
    gc_instance = create_gc(GCStrategy.GENERATIONAL)
    freed = gc_instance.collect()
    print(f"GC: freed {freed} objects")

    stats = gc_instance.get_stats()
    print(f"GC stats: {stats.allocated} allocations")

    # Test Memory Pool
    pool = create_memory_pool()
    obj1 = pool.acquire()
    pool.release(obj1)
    pool_stats = pool.get_stats()
    print(f"Pool: hit rate {pool_stats['hit_rate']:.2f}")

    # Test Memory Leak Detector
    leak_detector = MemoryLeakDetector()
    leak_detector.take_snapshot()
    # Simulate memory growth
    for _ in range(100):
        leak_detector.take_snapshot()

    is_leaking = leak_detector.detect_leak()
    print(f"Leak detected: {is_leaking}")

    # Test Heap Analyzer
    analyzer = HeapAnalyzer()
    heap_info = analyzer.analyze_heap()
    print(f"Heap: {heap_info['total_objects']} objects")

    # Test Custom Allocator
    allocator = CustomAllocator()
    block1 = allocator.allocate(1024)
    allocator.free(block1)
    alloc_stats = allocator.get_stats()
    print(f"Allocator: {alloc_stats['allocated_blocks']} allocated")

    # Test Memory Profiler
    profiler = MemoryProfiler()

    def test_func():
        data = [i for i in range(1000)]
        return sum(data)

    result, profile = profiler.profile_function(test_func)
    print(f"Profiling: {profile['memory_delta']} bytes delta")

    print("\nMemory Manager initialized successfully")


if __name__ == "__main__":
    main()
