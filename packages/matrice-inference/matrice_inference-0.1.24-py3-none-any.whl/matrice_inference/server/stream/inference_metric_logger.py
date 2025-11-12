import os
import time
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from matrice_inference.server.stream.worker_metrics import WorkerMetrics, MetricSnapshot
from matrice_inference.server.stream.metric_publisher import MetricPublisher, KafkaMetricPublisher, NoOpMetricPublisher 

logger = logging.getLogger(__name__)

class InferenceMetricLogger:
    """
    Background aggregator for worker metrics with periodic publishing.
    
    This class:
    - Runs on a dedicated background thread using threading.Timer
    - Periodically collects metrics from all workers via StreamingPipeline
    - Aggregates by worker_type (merges multiple instances)
    - Produces InferenceMetricLog matching the required schema
    - Publishes via configurable MetricPublisher
    - Handles graceful shutdown with timeout
    
    Thread Safety:
        - Timer-based execution ensures single aggregator thread
        - Worker metrics use internal locks for snapshot operations
        - No shared mutable state between collection cycles
    
    Lifecycle:
        logger = InferenceMetricLogger(pipeline, ...)
        logger.start()
        # ... runs in background ...
        logger.stop(timeout=10)
    """
    
    def __init__(
        self,
        streaming_pipeline: Any,  # StreamingPipeline reference
        interval_seconds: float = 300.0,  # 5 minutes default
        publisher: Optional[MetricPublisher] = None,
        deployment_id: Optional[str] = None,
        app_deploy_id: Optional[str] = None,
        action_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """
        Initialize metric logger.
        
        Args:
            streaming_pipeline: Reference to StreamingPipeline instance
            interval_seconds: Reporting interval (INFERENCE_METRIC_LOGGING_INTERVAL)
            publisher: MetricPublisher implementation (defaults to Kafka)
            deployment_id: Deployment identifier for metric log
            app_deploy_id: App deployment identifier
            action_id: Action identifier
            app_id: Application identifier
        """
        self.pipeline = streaming_pipeline
        self.interval_seconds = interval_seconds
        self.publisher = publisher
        
        # NOTE : Opt 1: Use `action_details` but API call overhead
        # NOTE : Opt 2: Extract these params from `server.py` via streaming_pipeline
        
        # Metric log identifiers
        self.deployment_id = deployment_id 
        self.app_deploy_id = app_deploy_id
        self.action_id = action_id
        self.app_id = app_id

        # State
        self._running = False
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._last_collection_time = time.time()
        
        # Statistics
        self._total_collections = 0
        self._failed_collections = 0
        self._failed_publishes = 0
        
        logger.info(
            f"Initialized InferenceMetricLogger: "
            f"interval={interval_seconds}s, "
            f"deployment_id={self.deployment_id}"
        )
    
    def start(self) -> None:
        """
        Start the background metric collection loop.
        
        Spawns a timer-based thread that wakes every interval_seconds
        to collect and publish metrics.
        
        Thread Safety:
            Uses lock to prevent multiple start calls from creating
            duplicate timer threads.
        """
        with self._lock:
            if self._running:
                logger.warning("Metric logger already running")
                return
            
            self._running = True
            self._last_collection_time = time.time()
            
            # Initialize default publisher if none provided
            if self.publisher is None:
                try:
                    self.publisher = KafkaMetricPublisher()
                except Exception as e:
                    logger.warning(
                        f"Failed to initialize Kafka publisher: {e}. "
                        f"Using NoOp publisher."
                    )
                    self.publisher = NoOpMetricPublisher()
            
            # Start timer loop
            self._schedule_next_collection()
            
            logger.info("Metric logger started")
    
    def stop(self, timeout: float = 10.0) -> None:
        """
        Stop the background metric collection loop.
        
        Args:
            timeout: Maximum time to wait for final collection (seconds)
        
        Note:
            Performs one final collection before stopping to avoid
            losing metrics from the last interval.
        """
        with self._lock:
            if not self._running:
                return
            
            self._running = False
            
            # Cancel pending timer
            if self._timer:
                self._timer.cancel()
                self._timer = None
        
        # Final collection outside lock to avoid deadlock
        try:
            logger.info("Performing final metric collection...")
            self._collect_and_publish()
        except Exception as e:
            logger.error(f"Error during final collection: {e}")
        
        # Close publisher
        if self.publisher:
            try:
                self.publisher.close()
            except Exception as e:
                logger.error(f"Error closing publisher: {e}")
        
        logger.info(
            f"Metric logger stopped. "
            f"Collections: {self._total_collections}, "
            f"Failed: {self._failed_collections}, "
            f"Publish failures: {self._failed_publishes}"
        )
    
    def wait(self, timeout: Optional[float] = None) -> None:
        """
        Wait for the metric logger to stop.
        
        Args:
            timeout: Maximum time to wait (None = wait indefinitely)
        
        Note:
            This is a passive wait - use stop() to actually stop the logger.
        """
        start_time = time.time()
        
        while self._running:
            if timeout and (time.time() - start_time) >= timeout:
                logger.warning(f"Wait timeout after {timeout}s")
                break
            time.sleep(0.1)
    
    def _schedule_next_collection(self) -> None:
        """Schedule the next metric collection using threading.Timer."""
        if not self._running:
            return
        
        self._timer = threading.Timer(
            self.interval_seconds,
            self._timer_callback
        )
        self._timer.daemon = False  # Non-daemon for graceful shutdown
        self._timer.start()
    
    def _timer_callback(self) -> None:
        """Timer callback that performs collection and reschedules."""
        try:
            self._collect_and_publish()
        except Exception as e:
            logger.error(f"Error in metric collection: {e}", exc_info=True)
            self._failed_collections += 1
        finally:
            # Schedule next collection
            self._schedule_next_collection()
    
    def _collect_and_publish(self) -> None:
        """
        Collect metrics from all workers, aggregate, and publish.
        
        This method:
        1. Determines interval boundaries
        2. Collects snapshots from all active workers
        3. Aggregates by worker_type
        4. Builds InferenceMetricLog
        5. Publishes via configured publisher
        6. Resets worker metrics for next interval
        """
        interval_end = time.time()
        interval_start = self._last_collection_time
        self._last_collection_time = interval_end
        
        try:
            # Collect snapshots from all workers
            snapshots = self._collect_worker_snapshots(interval_start, interval_end)
            
            if not snapshots:
                logger.debug("No worker snapshots collected (no active workers)")
                return
            
            # Aggregate by worker type
            aggregated = self._aggregate_by_type(snapshots)
            
            # Build metric log
            metric_log = self._build_metric_log(aggregated, interval_end)
            
            # Publish
            success = self.publisher.publish(metric_log)
            
            if success:
                self._total_collections += 1
                logger.info(
                    f"Published metrics: interval={self.interval_seconds}s, "
                    f"workers={len(snapshots)}, "
                    f"timestamp={metric_log['timestamp']}"
                )
            else:
                self._failed_publishes += 1
                logger.error("Failed to publish metric log")
                
        except Exception as e:
            logger.error(f"Error collecting/publishing metrics: {e}", exc_info=True)
            self._failed_collections += 1
    
    def _collect_worker_snapshots(self, interval_start: float, interval_end: float) -> List[MetricSnapshot]:
        """Collect snapshots from shared metrics instances (optimized)."""
        snapshots = []
        
        # Collect once per worker type (not per worker instance)
        worker_types_collected = set()
        
        try:
            # Inference workers
            if self.pipeline.inference_workers and "inference" not in worker_types_collected:
                worker = self.pipeline.inference_workers[0]  # Any worker, they share metrics
                snapshot = worker.metrics.snapshot_and_reset(interval_start, interval_end)
                snapshots.append(snapshot)
                worker_types_collected.add("inference")
            
            # Post-processing workers
            if self.pipeline.postproc_workers and "post_processing" not in worker_types_collected:
                worker = self.pipeline.postproc_workers[0]
                snapshot = worker.metrics.snapshot_and_reset(interval_start, interval_end)
                snapshots.append(snapshot)
                worker_types_collected.add("post_processing")
            
            # Producer workers
            if self.pipeline.producer_workers and "producer" not in worker_types_collected:
                worker = self.pipeline.producer_workers[0]
                snapshot = worker.metrics.snapshot_and_reset(interval_start, interval_end)
                snapshots.append(snapshot)
                worker_types_collected.add("producer")
            
            # Consumer workers (all share same metrics)
            if self.pipeline.consumer_workers and "consumer" not in worker_types_collected:
                for camera_workers in self.pipeline.consumer_workers.values():
                    if camera_workers:
                        worker = camera_workers[0]
                        snapshot = worker.metrics.snapshot_and_reset(interval_start, interval_end)
                        snapshots.append(snapshot)
                        worker_types_collected.add("consumer")
                        break
        
        except Exception as e:
            logger.error(f"Error accessing pipeline workers: {e}", exc_info=True)
        
        return snapshots
    
    def _aggregate_by_type(
        self,
        snapshots: List[MetricSnapshot]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate snapshots by worker_type.
        
        Combines metrics from multiple workers of the same type
        (e.g., multiple consumer instances) into single aggregated stats.
        
        Args:
            snapshots: List of MetricSnapshot objects
        
        Returns:
            Dictionary mapping worker_type to aggregated statistics
        """
        # Group snapshots by type
        by_type: Dict[str, List[MetricSnapshot]] = {
            "consumer": [],
            "inference": [],
            "post_processing": [],
            "producer": []
        }
        
        for snapshot in snapshots:
            if snapshot.worker_type in by_type:
                by_type[snapshot.worker_type].append(snapshot)
        
        # Aggregate each type
        aggregated = {}
        
        for worker_type, type_snapshots in by_type.items():
            if type_snapshots:
                aggregated[worker_type] = self._aggregate_snapshots(type_snapshots)
            else:
                # No active workers of this type - use inactive metrics
                aggregated[worker_type] = self._inactive_metrics()
        
        return aggregated
    
    def _aggregate_snapshots(self, snapshots: List[MetricSnapshot]) -> Dict[str, Any]:
        """
        Aggregate multiple snapshots into combined latency and throughput statistics.
        """
        if not snapshots:
            return self._inactive_metrics()

        all_latency_samples = []
        throughput_rates = []
        any_active = False

        # Fallback interval from first snapshot
        fallback_interval = snapshots[0].interval_end_ts - snapshots[0].interval_start_ts
        if fallback_interval <= 0:
            logger.debug("Fallback interval non-positive, defaulting to 1.0s")
            fallback_interval = 1.0

        total_throughput = 0

        for snapshot in snapshots:
            # Compute per-snapshot interval safely
            interval_seconds = snapshot.interval_end_ts - snapshot.interval_start_ts
            if interval_seconds <= 0:
                interval_seconds = fallback_interval

            # Compute and record per-worker rate
            worker_rate = snapshot.throughput_count / interval_seconds
            throughput_rates.append(worker_rate)

            # Aggregate latency and throughput data
            all_latency_samples.extend(snapshot.latency_samples)
            total_throughput += snapshot.throughput_count
            any_active = any_active or snapshot.was_active

        # Use modular stat calculators
        latency_stats = self._compute_latency_stats(all_latency_samples)
        throughput_stats = self._compute_throughput_stats(throughput_rates)

        return {
            "latency": latency_stats,
            "throughput": throughput_stats,
            "active": any_active,
            "total_throughput": total_throughput
        }

    
    def _compute_latency_stats(self, samples: List[float]) -> Dict[str, Any]:
        """
        Compute latency statistics from samples.
        
        Args:
            samples: List of latency measurements in milliseconds
        
        Returns:
            Dictionary with min, max, avg, p0, p50, p100, unit
        """
        if not samples:
            return {
                "min": -1,
                "max": -1,
                "avg": -1,
                "p0": -1,
                "p50": -1,
                "p100": -1,
                "unit": "ms"
            }
        
        sorted_samples = sorted(samples)
        n = len(sorted_samples)
        
        return {
            "min": sorted_samples[0],
            "max": sorted_samples[-1],
            "avg": sum(samples) / n,
            "p0": sorted_samples[0],
            "p50": WorkerMetrics._percentile(sorted_samples, 50),
            "p100": sorted_samples[-1],
            "unit": "ms"
        }
    
    def _compute_throughput_stats(self, rates: List[float]) -> Dict[str, Any]:
        """
        Compute throughput statistics from per-worker rates.

        Args:
            rates: List of per-worker throughput rates (msg/sec)

        Returns:
            Dictionary with min, max, avg, p0, p50, p100, unit
        """
        if not rates:
            return {
                "min": -1,
                "max": -1,
                "avg": -1,
                "p0": -1,
                "p50": -1,
                "p100": -1,
                "unit": "msg/sec"
            }

        sorted_rates = sorted(rates)
        n = len(sorted_rates)

        return {
            "min": sorted_rates[0],
            "max": sorted_rates[-1],
            "avg": sum(sorted_rates) / n,
            "p0": sorted_rates[0],
            "p50": WorkerMetrics._percentile(sorted_rates, 50),
            "p100": sorted_rates[-1],
            "unit": "msg/sec"
        }

    
    def _inactive_metrics(self) -> Dict[str, Any]:
        """
        Generate metrics structure for inactive worker type.
        
        Returns:
            Dictionary with -1 values indicating no activity
        """
        return {
            "latency": {
                "min": -1,
                "max": -1,
                "avg": -1,
                "p0": -1,
                "p50": -1,
                "p100": -1,
                "unit": "ms"
            },
            "throughput": {
                "min": -1,
                "max": -1,
                "avg": -1,
                "p0": -1,
                "p50": -1,
                "p100": -1,
                "unit": "msg/sec"
            },
            "active": False
        }
    
    def _build_metric_log(
        self,
        aggregated: Dict[str, Dict[str, Any]],
        timestamp: float
    ) -> Dict[str, Any]:
        """
        Build InferenceMetricLog matching required schema.
        
        Args:
            aggregated: Aggregated metrics by worker_type
            timestamp: Collection timestamp (Unix epoch)
        
        Returns:
            InferenceMetricLog dictionary ready for publishing
        """
        # Convert timestamp to ISO8601 UTC
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        iso_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return {
            "deployment_id": self.deployment_id,
            "app_deploy_id": self.app_deploy_id,
            "action_id": self.action_id,
            "app_id": self.app_id,
            "timestamp": iso_timestamp,
            "metrics": {
                "consumer": aggregated.get("consumer", self._inactive_metrics()),
                "inference": aggregated.get("inference", self._inactive_metrics()),
                "post_processing": aggregated.get("post_processing", self._inactive_metrics()),
                "producer": aggregated.get("producer", self._inactive_metrics())
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get logger statistics.
        
        Returns:
            Dictionary with collection statistics
        """
        return {
            "running": self._running,
            "interval_seconds": self.interval_seconds,
            "total_collections": self._total_collections,
            "failed_collections": self._failed_collections,
            "failed_publishes": self._failed_publishes,
            "last_collection_time": self._last_collection_time
        }