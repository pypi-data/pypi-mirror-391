"""
Worker-level metrics storage with thread-safe collection and aggregation.

This module provides a lightweight, thread-safe metrics collection class for
streaming workers. Supports both instance-level and CLASS-LEVEL (shared) metrics.

CLASS-LEVEL METRICS (new):
    One WorkerMetrics instance shared across all workers of the same type.
    Accessed via WorkerMetrics.get_shared(worker_type) class method.
    Thread-safe with internal locking for concurrent worker access.

INSTANCE-LEVEL METRICS (legacy):
    Each worker has its own WorkerMetrics instance.
    Maintained for backward compatibility and testing.
"""

import threading
import time
from typing import Dict, List, Optional, Any, ClassVar
from dataclasses import dataclass


@dataclass
class MetricSnapshot:
    """Immutable snapshot of metrics for a time interval."""
    worker_id: str
    worker_type: str
    interval_start_ts: float
    interval_end_ts: float
    latency_samples: List[float]
    throughput_count: int
    was_active: bool


class WorkerMetrics:
    """
    Thread-safe metrics storage for worker instances.
    
    Supports two modes:
    1. INSTANCE MODE: Each worker creates its own WorkerMetrics (legacy)
    2. SHARED MODE: All workers of same type share one WorkerMetrics (new)
    
    SHARED MODE DESIGN:
        - One WorkerMetrics per worker_type stored in class-level registry
        - Workers access via WorkerMetrics.get_shared(worker_type)
        - All operations are thread-safe with internal locking
        - Transparent to worker code - still use self.metrics.record_*()
    
    Thread Safety:
        All public methods acquire internal lock before state modification.
        Lock is reentrant (RLock) to support nested calls if needed.
        Snapshot operation is atomic - no data corruption during collection.
    
    Memory Management:
        Shared mode significantly reduces memory overhead:
        - Instance mode: 4 workers × 1000 samples = 4000 floats
        - Shared mode: 1 shared × 1000 samples = 1000 floats (75% reduction)
    
    Backward Compatibility:
        Existing code using WorkerMetrics(worker_id, worker_type) continues
        to work unchanged. To use shared mode, workers call get_shared().
    """
    
    # Class-level registry for shared metrics instances
    _shared_metrics: ClassVar[Dict[str, 'WorkerMetrics']] = {}
    _shared_metrics_lock: ClassVar[threading.Lock] = threading.Lock()
    
    def __init__(
        self,
        worker_id: str,
        worker_type: str,
        latency_unit: str = "ms",
        throughput_unit: str = "msg/sec",
        max_samples: Optional[int] = None,
        _is_shared: bool = False
    ):
        """
        Initialize worker metrics storage.
        
        Args:
            worker_id: Unique identifier for this worker instance (or "shared" for shared mode)
            worker_type: Type of worker (consumer, inference, post_processing, producer)
            latency_unit: Unit string for latency measurements
            throughput_unit: Unit string for throughput rate
            max_samples: Maximum samples to retain (None = unlimited)
            _is_shared: Internal flag indicating this is a shared instance
        """
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.latency_unit = latency_unit
        self.throughput_unit = throughput_unit
        self.max_samples = max_samples
        self._is_shared = _is_shared
        
        # Thread synchronization - use RLock for reentrancy safety
        self._lock = threading.RLock()
        
        # Metric storage
        self._latency_samples: List[float] = []
        self._throughput_count: int = 0
        self._is_active: bool = False
        
        # Active worker count (only meaningful for shared instances)
        self._active_worker_count: int = 0
    
    @classmethod
    def get_shared(cls, worker_type: str) -> 'WorkerMetrics':
        """
        Get or create shared WorkerMetrics instance for a worker type.
        
        This is the primary method for workers to access class-level metrics.
        Thread-safe - multiple workers can call concurrently.
        
        Args:
            worker_type: Type of worker (consumer, inference, post_processing, producer)
        
        Returns:
            Shared WorkerMetrics instance for this worker type
        
        Example:
            # In worker __init__:
            self.metrics = WorkerMetrics.get_shared("inference")
            
            # In worker _run:
            self.metrics.record_latency(latency_ms)  # Thread-safe, shared storage
        """
        with cls._shared_metrics_lock:
            if worker_type not in cls._shared_metrics:
                # Create new shared instance
                cls._shared_metrics[worker_type] = cls(
                    worker_id=f"{worker_type}_shared",
                    worker_type=worker_type,
                    _is_shared=True
                )
            return cls._shared_metrics[worker_type]
    
    @classmethod
    def clear_shared_metrics(cls) -> None:
        """
        Clear all shared metrics instances.
        
        Used for testing and cleanup. Should not be called during normal operation.
        """
        with cls._shared_metrics_lock:
            cls._shared_metrics.clear()
    
    def record_latency(self, value_ms: float, timestamp: Optional[float] = None) -> None:
        """
        Record a latency measurement.
        
        Thread-safe for concurrent calls from multiple workers.
        
        Args:
            value_ms: Latency value in milliseconds
            timestamp: Optional timestamp (unused, for future extensions)
        """
        with self._lock:
            self._latency_samples.append(value_ms)
            self._is_active = True
    
    def record_throughput(self, count: int = 1, timestamp: Optional[float] = None) -> None:
        """
        Record throughput event(s).
        
        Thread-safe for concurrent calls from multiple workers.
        
        Args:
            count: Number of items processed (default: 1)
            timestamp: Optional timestamp (unused, for future extensions)
        """
        with self._lock:
            self._throughput_count += count
            self._is_active = True
    
    def mark_active(self) -> None:
        """
        Mark this worker as active for the current interval.
        
        For shared metrics, increments active worker count.
        Thread-safe.
        """
        with self._lock:
            self._is_active = True
            if self._is_shared:
                self._active_worker_count += 1
    
    def mark_inactive(self) -> None:
        """
        Mark this worker as inactive for the current interval.
        
        For shared metrics, decrements active worker count.
        Thread-safe.
        """
        with self._lock:
            if self._is_shared:
                self._active_worker_count = max(0, self._active_worker_count - 1)
                # Only mark inactive if no workers are active
                if self._active_worker_count == 0:
                    self._is_active = False
            else:
                self._is_active = False
    
    def set_running(self, running: bool) -> None:
        """Set worker running state."""
        if running:
            self.mark_active()
        else:
            self.mark_inactive()
    
    def snapshot_and_reset(
        self,
        interval_start_ts: float,
        interval_end_ts: float
    ) -> MetricSnapshot:
        """
        Capture current metrics and reset for next interval.
        
        This method atomically:
        1. Creates a snapshot of current metrics
        2. Clears internal storage for next interval
        3. Preserves active state
        
        Thread Safety:
            Atomic operation - entire snapshot under lock.
            Safe for concurrent access from multiple workers.
        
        Args:
            interval_start_ts: Start timestamp of the interval (Unix epoch)
            interval_end_ts: End timestamp of the interval (Unix epoch)
        
        Returns:
            MetricSnapshot containing interval data
        """
        with self._lock:
            snapshot = MetricSnapshot(
                worker_id=self.worker_id,
                worker_type=self.worker_type,
                interval_start_ts=interval_start_ts,
                interval_end_ts=interval_end_ts,
                latency_samples=self._latency_samples.copy(),
                throughput_count=self._throughput_count,
                was_active=self._is_active
            )
            
            # Reset for next interval
            self._latency_samples.clear()
            self._throughput_count = 0
            # Keep active state - don't reset to preserve worker liveness
            
            return snapshot
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """
        Generate summary statistics from current state without reset.
        
        Thread-safe.
        
        Returns:
            Dictionary with latency and throughput statistics
            
        Note:
            Returns -1 for metrics when no data available (inactive worker).
        """
        with self._lock:
            latency_stats = self._compute_latency_stats(self._latency_samples)
            
            # Throughput is instantaneous count (rate computed per interval elsewhere)
            throughput_stats = {
                "count": self._throughput_count,
                "unit": self.throughput_unit
            }
            
            return {
                "worker_id": self.worker_id,
                "worker_type": self.worker_type,
                "is_active": self._is_active,
                "is_shared": self._is_shared,
                "active_worker_count": self._active_worker_count if self._is_shared else 1,
                "latency": latency_stats,
                "throughput": throughput_stats
            }
    
    def _compute_latency_stats(self, samples: List[float]) -> Dict[str, Any]:
        """
        Compute latency statistics from samples.
        
        Args:
            samples: List of latency measurements
        
        Returns:
            Dictionary with min, max, avg, p0, p50, p100, unit
            Returns -1 for all metrics if no samples
        """
        if not samples:
            return {
                "min": -1,
                "max": -1,
                "avg": -1,
                "p0": -1,
                "p50": -1,
                "p100": -1,
                "unit": self.latency_unit
            }
        
        sorted_samples = sorted(samples)
        n = len(sorted_samples)
        
        return {
            "min": sorted_samples[0],
            "max": sorted_samples[-1],
            "avg": sum(samples) / n,
            "p0": sorted_samples[0],
            "p50": self._percentile(sorted_samples, 50),
            "p100": sorted_samples[-1],
            "unit": self.latency_unit
        }
    
    @staticmethod
    def _percentile(sorted_samples: List[float], percentile: float) -> float:
        """
        Calculate percentile from sorted samples using nearest-rank method.
        
        Args:
            sorted_samples: Pre-sorted list of values
            percentile: Percentile to calculate (0-100)
        
        Returns:
            Percentile value
        
        Complexity:
            O(1) given pre-sorted input
        """
        if not sorted_samples:
            return -1
        
        if percentile <= 0:
            return sorted_samples[0]
        if percentile >= 100:
            return sorted_samples[-1]
        
        n = len(sorted_samples)
        rank = (percentile / 100.0) * (n - 1)
        lower_idx = int(rank)
        upper_idx = min(lower_idx + 1, n - 1)
        
        # Linear interpolation
        fraction = rank - lower_idx
        return sorted_samples[lower_idx] * (1 - fraction) + sorted_samples[upper_idx] * fraction
    
    @classmethod
    def merge(cls, metrics_list: List['WorkerMetrics']) -> 'WorkerMetrics':
        """
        Merge multiple WorkerMetrics instances into one aggregate.
        
        NOTE: This method is deprecated for shared metrics mode.
        When using shared metrics, no merging is needed - all workers
        already write to the same instance.
        
        Kept for backward compatibility with instance-mode usage.
        
        Args:
            metrics_list: List of WorkerMetrics to merge
        
        Returns:
            New WorkerMetrics instance with combined data
        """
        if not metrics_list:
            raise ValueError("Cannot merge empty metrics list")
        
        first = metrics_list[0]
        merged = cls(
            worker_id=f"{first.worker_type}_merged",
            worker_type=first.worker_type,
            latency_unit=first.latency_unit,
            throughput_unit=first.throughput_unit
        )
        
        # Aggregate all samples and counts
        with merged._lock:
            for metrics in metrics_list:
                with metrics._lock:
                    merged._latency_samples.extend(metrics._latency_samples)
                    merged._throughput_count += metrics._throughput_count
                    merged._is_active = merged._is_active or metrics._is_active
        
        return merged
    
    @staticmethod
    def compute_interval_summary(snapshot: MetricSnapshot) -> Dict[str, Any]:
        """
        Compute aggregated statistics from a snapshot for reporting.
        
        Args:
            snapshot: MetricSnapshot from snapshot_and_reset()
        
        Returns:
            Dictionary with latency and throughput statistics for the interval
        """
        interval_seconds = snapshot.interval_end_ts - snapshot.interval_start_ts
        
        # Latency statistics
        if snapshot.latency_samples:
            sorted_samples = sorted(snapshot.latency_samples)
            n = len(sorted_samples)
            latency_stats = {
                "min": sorted_samples[0],
                "max": sorted_samples[-1],
                "avg": sum(snapshot.latency_samples) / n,
                "p0": sorted_samples[0],
                "p50": WorkerMetrics._percentile(sorted_samples, 50),
                "p100": sorted_samples[-1],
                "unit": "ms"
            }
        else:
            latency_stats = {
                "min": -1, "max": -1, "avg": -1,
                "p0": -1, "p50": -1, "p100": -1,
                "unit": "ms"
            }
        
        # Throughput statistics (rate per second)
        if interval_seconds > 0:
            throughput_rate = snapshot.throughput_count / interval_seconds
        else:
            throughput_rate = 0
        
        throughput_stats = {
            "min": throughput_rate,
            "max": throughput_rate,
            "avg": throughput_rate,
            "p0": throughput_rate,
            "p50": throughput_rate,
            "p100": throughput_rate,
            "unit": "msg/sec"
        }
        
        return {
            "latency": latency_stats,
            "throughput": throughput_stats,
            "active": snapshot.was_active
        }