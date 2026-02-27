"""
Prim Garbage Collector
Provides mark-and-sweep GC, generational GC, memory tracking, and GC statistics.
"""

import sys
import gc
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import weakref


class GCType(Enum):
    """Garbage collector types"""
    MARK_AND_SWEEP = "mark_and_sweep"
    GENERATIONAL = "generational"
    REFERENCE_COUNTING = "reference_counting"


class GCGeneration(Enum):
    """Generational GC generations"""
    YOUNG = "young"
    OLD = "old"
    PERMANENT = "permanent"


@dataclass
class GCStats:
    """Garbage collection statistics"""
    collections: int = 0
    objects_collected: int = 0
    bytes_collected: int = 0
    time_spent: float = 0.0
    memory_before: int = 0
    memory_after: int = 0


class GCObject:
    """Tracked GC object"""

    def __init__(self, obj: Any, generation: GCGeneration = GCGeneration.YOUNG):
        self.obj = obj
        self.generation = generation
        self.references: Set['GCObject'] = set()
        self.marked = False
        self.size = sys.getsizeof(obj) if obj else 0


class MarkAndSweepGC:
    """Mark-and-sweep garbage collector"""

    def __init__(self):
        self.objects: Dict[int, GCObject] = {}
        self.roots: Set[Any] = set()
        self.stats = GCStats()

    def track_object(self, obj: Any):
        """Track an object for GC"""
        if obj is None:
            return

        obj_id = id(obj)
        if obj_id not in self.objects:
            self.objects[obj_id] = GCObject(obj)

    def add_root(self, obj: Any):
        """Add a root object"""
        self.roots.add(obj)

    def remove_root(self, obj: Any):
        """Remove a root object"""
        self.roots.discard(obj)

    def collect(self) -> GCStats:
        """Run garbage collection"""
        import time

        start_time = time.time()
        self.stats.memory_before = self._get_memory_usage()

        # Mark phase
        self._mark()

        # Sweep phase
        self._sweep()

        end_time = time.time()
        self.stats.time_spent = end_time - start_time
        self.stats.memory_after = self._get_memory_usage()
        self.stats.collections += 1

        return self.stats

    def _mark(self):
        """Mark reachable objects"""
        # Reset marks
        for gc_obj in self.objects.values():
            gc_obj.marked = False

        # Mark from roots
        for root in self.roots:
            self._mark_object(root)

    def _mark_object(self, obj: Any):
        """Mark an object and its references"""
        if obj is None:
            return

        obj_id = id(obj)
        if obj_id not in self.objects:
            return

        gc_obj = self.objects[obj_id]
        if gc_obj.marked:
            return

        gc_obj.marked = True

        # Mark references
        for ref in gc_obj.references:
            self._mark_object(ref.obj)

    def _sweep(self):
        """Sweep unmarked objects"""
        to_remove = []

        for obj_id, gc_obj in self.objects.items():
            if not gc_obj.marked:
                to_remove.append(obj_id)
                self.stats.objects_collected += 1
                self.stats.bytes_collected += gc_obj.size

        for obj_id in to_remove:
            del self.objects[obj_id]

    def _get_memory_usage(self) -> int:
        """Get current memory usage"""
        return sum(gc_obj.size for gc_obj in self.objects.values())


class GenerationalGC:
    """Generational garbage collector"""

    def __init__(self):
        self.young_generation: Dict[int, GCObject] = {}
        self.old_generation: Dict[int, GCObject] = {}
        self.promotion_threshold = 3
        self.young_collections = 0
        self.old_collections = 0
        self.stats = GCStats()

    def track_object(self, obj: Any):
        """Track an object for GC"""
        if obj is None:
            return

        obj_id = id(obj)
        if obj_id not in self.young_generation and obj_id not in self.old_generation:
            self.young_generation[obj_id] = GCObject(obj, GCGeneration.YOUNG)

    def collect_young(self) -> GCStats:
        """Collect young generation"""
        self.young_collections += 1
        return self._collect_generation(self.young_generation, GCGeneration.YOUNG)

    def collect_old(self) -> GCStats:
        """Collect old generation"""
        self.old_collections += 1
        return self._collect_generation(self.old_generation, GCGeneration.OLD)

    def _collect_generation(self, generation: Dict[int, GCObject], gen_type: GCGeneration) -> GCStats:
        """Collect a specific generation"""
        import time

        start_time = time.time()
        stats = GCStats()

        # Mark phase
        for obj_id, gc_obj in generation.items():
            gc_obj.marked = False

        # Sweep phase
        to_remove = []
        to_promote = []

        for obj_id, gc_obj in generation.items():
            if not gc_obj.marked:
                to_remove.append(obj_id)
                stats.objects_collected += 1
                stats.bytes_collected += gc_obj.size
            elif gen_type == GCGeneration.YOUNG:
                # Check if object should be promoted
                if self.young_collections >= self.promotion_threshold:
                    to_promote.append(obj_id)

        for obj_id in to_remove:
            del generation[obj_id]

        for obj_id in to_promote:
            gc_obj = generation.pop(obj_id)
            gc_obj.generation = GCGeneration.OLD
            self.old_generation[obj_id] = gc_obj

        end_time = time.time()
        stats.time_spent = end_time - start_time
        stats.collections += 1

        return stats


class ReferenceCountingGC:
    """Reference counting garbage collector"""

    def __init__(self):
        self.ref_counts: Dict[int, int] = {}
        self.objects: Dict[int, Any] = {}
        self.stats = GCStats()

    def track_object(self, obj: Any):
        """Track an object for GC"""
        if obj is None:
            return

        obj_id = id(obj)
        if obj_id not in self.objects:
            self.objects[obj_id] = obj
            self.ref_counts[obj_id] = 1

    def add_reference(self, obj: Any):
        """Add a reference to an object"""
        if obj is None:
            return

        obj_id = id(obj)
        if obj_id in self.ref_counts:
            self.ref_counts[obj_id] += 1

    def remove_reference(self, obj: Any):
        """Remove a reference from an object"""
        if obj is None:
            return

        obj_id = id(obj)
        if obj_id in self.ref_counts:
            self.ref_counts[obj_id] -= 1

            if self.ref_counts[obj_id] <= 0:
                del self.ref_counts[obj_id]
                if obj_id in self.objects:
                    del self.objects[obj_id]
                    self.stats.objects_collected += 1

    def collect(self) -> GCStats:
        """Run garbage collection (check for circular references)"""
        import time

        start_time = time.time()

        # Check for circular references
        to_remove = []
        for obj_id, obj in self.objects.items():
            if self._has_circular_reference(obj):
                to_remove.append(obj_id)

        for obj_id in to_remove:
            del self.objects[obj_id]
            if obj_id in self.ref_counts:
                del self.ref_counts[obj_id]
            self.stats.objects_collected += 1

        end_time = time.time()
        self.stats.time_spent = end_time - start_time
        self.stats.collections += 1

        return self.stats

    def _has_circular_reference(self, obj: Any, visited: Optional[Set[int]] = None) -> bool:
        """Check if object has circular references"""
        if visited is None:
            visited = set()

        obj_id = id(obj)
        if obj_id in visited:
            return True

        visited.add(obj_id)

        # Check references (simplified)
        if hasattr(obj, '__dict__'):
            for attr in vars(obj).values():
                if self._has_circular_reference(attr, visited):
                    return True

        return False


class GarbageCollector:
    """Unified garbage collector"""

    def __init__(self, gc_type: GCType = GCType.MARK_AND_SWEEP):
        self.gc_type = gc_type

        if gc_type == GCType.MARK_AND_SWEEP:
            self.gc = MarkAndSweepGC()
        elif gc_type == GCType.GENERATIONAL:
            self.gc = GenerationalGC()
        elif gc_type == GCType.REFERENCE_COUNTING:
            self.gc = ReferenceCountingGC()
        else:
            self.gc = MarkAndSweepGC()

        self.enabled = True
        self.auto_collect = True
        self.collect_threshold = 1000

    def track_object(self, obj: Any):
        """Track an object for GC"""
        if self.enabled:
            self.gc.track_object(obj)

    def collect(self) -> GCStats:
        """Run garbage collection"""
        if not self.enabled:
            return GCStats()

        if isinstance(self.gc, GenerationalGC):
            return self.gc.collect_young()
        elif isinstance(self.gc, MarkAndSweepGC):
            return self.gc.collect()
        elif isinstance(self.gc, ReferenceCountingGC):
            return self.gc.collect()

        return GCStats()

    def get_stats(self) -> GCStats:
        """Get GC statistics"""
        if hasattr(self.gc, 'stats'):
            return self.gc.stats
        return GCStats()

    def enable(self):
        """Enable garbage collection"""
        self.enabled = True

    def disable(self):
        """Disable garbage collection"""
        self.enabled = False

    def set_auto_collect(self, auto: bool):
        """Set auto collection"""
        self.auto_collect = auto

    def set_collect_threshold(self, threshold: int):
        """Set collection threshold"""
        self.collect_threshold = threshold


def create_gc(gc_type: GCType = GCType.MARK_AND_SWEEP) -> GarbageCollector:
    """Create a garbage collector"""
    return GarbageCollector(gc_type)


def main():
    """Main entry point for testing"""
    print("Testing garbage collector...")

    # Test mark-and-sweep GC
    gc = create_gc(GCType.MARK_AND_SWEEP)

    # Create and track objects
    obj1 = {"data": "test"}
    obj2 = {"ref": obj1}

    gc.track_object(obj1)
    gc.track_object(obj2)

    # Add root
    gc.gc.add_root(obj1)

    # Collect
    stats = gc.collect()
    print(f"GC Stats: {stats.collections} collections, {stats.objects_collected} objects collected")

    # Test generational GC
    gen_gc = create_gc(GCType.GENERATIONAL)
    gen_gc.track_object(obj1)
    gen_gc.track_object(obj2)

    stats = gen_gc.collect()
    print(f"Generational GC: {stats.collections} collections")

    print("\nGarbage collector initialized successfully")


if __name__ == "__main__":
    main()
