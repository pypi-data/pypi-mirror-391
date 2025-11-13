"""
Streaming pipeline using MatriceStream and updated inference interface:
Direct processing with priority queues, dynamic camera configuration

Architecture:
Consumer workers (threading) -> Priority Queue -> Inference workers (threading) -> 
Priority Queue -> Post-processing workers (threading) -> Priority Queue -> Producer workers (threading)

Features:
- Start without initial configuration
- Dynamic camera configuration while running
- Support for both Kafka and Redis streams
- Integration with updated InferenceInterface and PostProcessor
- Maximum throughput with direct processing
- Low latency with no batching delays  
- Multi-camera support with topic routing
- Thread-based parallelism for inference and post-processing
- Non-blocking threading for consumers/producers
"""

import asyncio
import logging
import os
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from matrice_analytics.post_processing.post_processor import PostProcessor
from matrice_inference.server.inference_interface import InferenceInterface
from matrice_inference.server.stream.consumer_worker import ConsumerWorker
from matrice_inference.server.stream.inference_worker import InferenceWorker
from matrice_inference.server.stream.post_processing_worker import PostProcessingWorker
from matrice_inference.server.stream.producer_worker import ProducerWorker
from matrice_inference.server.stream.analytics_publisher import AnalyticsPublisher
from matrice_inference.server.stream.utils import CameraConfig
from matrice_inference.server.stream.inference_metric_logger import InferenceMetricLogger



class StreamingPipeline:
    """Optimized streaming pipeline with dynamic camera configuration and clean resource management."""

    DEFAULT_QUEUE_SIZE = 5000
    DEFAULT_MESSAGE_TIMEOUT = 10.0
    DEFAULT_INFERENCE_TIMEOUT = 30.0
    DEFAULT_SHUTDOWN_TIMEOUT = 30.0
    DEFAULT_METRIC_INTERVAL = 30.0  

    def __init__(
        self,
        inference_interface: InferenceInterface,
        post_processor: PostProcessor,
        inference_queue_maxsize: int = DEFAULT_QUEUE_SIZE,
        postproc_queue_maxsize: int = DEFAULT_QUEUE_SIZE,
        output_queue_maxsize: int = DEFAULT_QUEUE_SIZE,
        message_timeout: float = DEFAULT_MESSAGE_TIMEOUT,
        inference_timeout: float = DEFAULT_INFERENCE_TIMEOUT,
        shutdown_timeout: float = DEFAULT_SHUTDOWN_TIMEOUT,
        camera_configs: Optional[Dict[str, CameraConfig]] = None,
        app_deployment_id: Optional[str] = None,
        inference_pipeline_id: Optional[str] = None,
        enable_analytics_publisher: bool = True,
        
        deployment_id: Optional[str] = None,
        deployment_instance_id: Optional[str] = None,
        action_id: Optional[str] = None,
        use_shared_metrics: Optional[bool] = True,
        
        enable_metric_logging: bool = True,
        metric_logging_interval: float = DEFAULT_METRIC_INTERVAL,

    ):
        self.inference_interface = inference_interface
        self.post_processor = post_processor
        self.message_timeout = message_timeout
        self.inference_timeout = inference_timeout
        self.shutdown_timeout = shutdown_timeout
        self.app_deployment_id = app_deployment_id
        self.inference_pipeline_id = inference_pipeline_id
        self.enable_analytics_publisher = enable_analytics_publisher

        self.deployment_id = deployment_id
        self.deployment_instance_id = deployment_instance_id
        self.action_id = action_id

        # Metric logging configuration
        self.enable_metric_logging = enable_metric_logging
        self.metric_logging_interval = metric_logging_interval
        self.use_shared_metrics = use_shared_metrics


        self.camera_configs: Dict[str, CameraConfig] = camera_configs or {}
        self.running = False
        self.logger = logging.getLogger(__name__)

        # Event loop reference for async operations (set when pipeline starts)
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._event_loop_thread: Optional[threading.Thread] = None
        self._loop_thread_running = False

        self._setup_queues(inference_queue_maxsize, postproc_queue_maxsize, output_queue_maxsize)
        self._setup_executors()
        self._setup_workers()
        # Frame cache instance (initialized lazily at start)
        self.frame_cache = None
        # Analytics publisher instance (initialized lazily at start)
        self.analytics_publisher = None
        # Metric logger instance (initialized lazily at start)
        self.metric_logger = None

    def _setup_queues(self, inference_size: int, postproc_size: int, output_size: int) -> None:
        """Initialize priority queues for pipeline stages."""
        self.inference_queue = queue.PriorityQueue(maxsize=inference_size)
        self.postproc_queue = queue.PriorityQueue(maxsize=postproc_size)
        self.output_queue = queue.PriorityQueue(maxsize=output_size)

    def _setup_executors(self) -> None:
        """Initialize thread pool executors."""
        # Single-thread executors to preserve strict ordering
        self.inference_executor = ThreadPoolExecutor(max_workers=1)
        self.postprocessing_executor = ThreadPoolExecutor(max_workers=1)

    def _setup_workers(self) -> None:
        """Initialize worker containers."""
        self.consumer_workers: Dict[str, List[ConsumerWorker]] = {}
        self.inference_workers: List = []
        self.postproc_workers: List = []
        self.producer_workers: List = []
        self.worker_threads: List = []

    def _run_event_loop(self) -> None:
        """Run event loop in dedicated thread for the lifetime of the pipeline."""
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._loop_thread_running = True

        self.logger.info("Event loop thread started")

        try:
            # Run the event loop forever until stop() is called
            self._event_loop.run_forever()
        finally:
            self.logger.info("Event loop thread stopping")
            # Clean up pending tasks
            pending = asyncio.all_tasks(self._event_loop)
            for task in pending:
                task.cancel()
            # Allow tasks to complete cancellation
            self._event_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self._event_loop.close()
            self._loop_thread_running = False
            self.logger.info("Event loop thread stopped")

    def start(self) -> None:
        """Start the pipeline with proper error handling."""
        if self.running:
            self.logger.warning("Pipeline already running")
            return

        self.running = True

        # Start dedicated event loop thread
        self._event_loop_thread = threading.Thread(
            target=self._run_event_loop,
            daemon=True,
            name="PipelineEventLoop"
        )
        self._event_loop_thread.start()

        # Wait for event loop to be ready
        import time
        max_wait = 5.0
        wait_interval = 0.1
        elapsed = 0.0
        while not self._loop_thread_running and elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval

        if not self._loop_thread_running:
            self.logger.error("Event loop thread failed to start")
            self.running = False
            raise RuntimeError("Event loop thread failed to start")

        self.logger.info(f"Event loop thread ready (waited {elapsed:.2f}s)")
        self.logger.info("Starting streaming pipeline...")

        try:
            # Initialize frame cache before workers
            self._initialize_frame_cache()
            # Initialize analytics publisher (but don't start it yet)
            self._initialize_analytics_publisher()
            # Create workers (producer needs analytics publisher reference)
            # Schedule the async operation on the event loop
            future = asyncio.run_coroutine_threadsafe(
                self._create_workers(),
                self._event_loop
            )
            future.result(timeout=30.0)  # Wait for completion
            # Start all workers including analytics publisher
            self._start_workers()
            # Initialize and start metric logger after workers are started
            self._initialize_metric_logger()
            self._log_startup_info()
        except Exception as e:
            self.logger.error(f"Failed to start pipeline: {e}")
            self.stop()
            raise

    def _initialize_metric_logger(self) -> None:
        """
        Initialize and start InferenceMetricLogger for periodic metric reporting.
        
        The metric logger:
        - Runs on a background thread with configurable interval
        - Collects metrics from all active workers
        - Aggregates by worker type (consumer/inference/post_processing/producer)
        - Publishes to Kafka via RPC
        - Gracefully handles initialization failures (logs warning, continues)
        """
        if not self.enable_metric_logging:
            self.logger.info("Metric logging disabled")
            return
        
        try:
            from matrice_inference.server.stream.inference_metric_logger import (
                InferenceMetricLogger,
                KafkaMetricPublisher
            )
            
            self.metric_logger = InferenceMetricLogger(
                streaming_pipeline=self,
                interval_seconds=self.metric_logging_interval,
                # Will auto-initialize KafkaMetricPublisher
                publisher=None,  
                
                deployment_id=self.deployment_id,
                app_deploy_id=self.deployment_instance_id,
                action_id=self.action_id,
                app_id=None
            )
            
            # Start background collection
            self.metric_logger.start()
            
            self.logger.info(
                f"Initialized metric logger: interval={self.metric_logging_interval}s, "
                f"deployment_id={self.deployment_id}"
            )
            
        except ImportError as e:
            self.logger.warning(
                f"Metric logging dependencies not available: {e}. "
                f"Continuing without metric logging."
            )
            self.metric_logger = None
        except Exception as e:
            self.logger.warning(
                f"Failed to initialize metric logger: {e}. "
                f"Continuing without metric logging."
            )
            self.metric_logger = None

    def _log_startup_info(self) -> None:
        """Log pipeline startup information."""
        consumer_count = sum(len(workers) for workers in self.consumer_workers.values())
        self.logger.info(
            f"Pipeline started - Cameras: {len(self.camera_configs)}, "
            f"Consumers: {consumer_count}, Inference: {len(self.inference_workers)}, "
            f"PostProc: {len(self.postproc_workers)}, Producers: {len(self.producer_workers)}"
        )
    
    def stop(self) -> None:
        """Stop the pipeline gracefully with proper cleanup."""
        if not self.running:
            return

        self.logger.info("Stopping pipeline...")
        self.running = False

        # Stop metric logger first (before stopping workers)
        if self.metric_logger:
            try:
                self.logger.info("Stopping metric logger...")
                self.metric_logger.stop(timeout=10.0)
                self.logger.info("Metric logger stopped")
            except Exception as e:
                self.logger.error(f"Error stopping metric logger: {e}")

        self._stop_workers()
        self._wait_for_threads()
        self._shutdown_executors()

        # Stop frame cache if running
        try:
            if self.frame_cache:
                self.frame_cache.stop()
        except Exception:
            pass

        # Stop analytics publisher if running
        try:
            if self.analytics_publisher:
                self.analytics_publisher.stop()
        except Exception as e:
            self.logger.error(f"Error stopping analytics publisher: {e}")

        # Stop event loop thread
        if self._event_loop and self._loop_thread_running:
            try:
                self.logger.info("Stopping event loop thread...")
                self._event_loop.call_soon_threadsafe(self._event_loop.stop)
                if self._event_loop_thread:
                    self._event_loop_thread.join(timeout=5.0)
                self.logger.info("Event loop thread stopped")
            except Exception as e:
                self.logger.error(f"Error stopping event loop thread: {e}")

        self.logger.info("Pipeline stopped")

    def _wait_for_threads(self) -> None:
        """Wait for all worker threads to complete."""
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=self.shutdown_timeout)

    def _shutdown_executors(self) -> None:
        """Shutdown thread pool executors."""
        self.inference_executor.shutdown(wait=False)
        self.postprocessing_executor.shutdown(wait=False)
    
    async def add_camera_config(self, camera_config: CameraConfig) -> bool:
        """
        Add a camera configuration dynamically while pipeline is running.
        
        Args:
            camera_config: Camera configuration to add
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            camera_id = camera_config.camera_id
            
            if camera_id in self.camera_configs:
                self.logger.warning(f"Camera {camera_id} already exists, updating configuration")
                # Stop existing workers for this camera
                await self._stop_camera_workers(camera_id)
            
            # Add camera config
            self.camera_configs[camera_id] = camera_config
            
            # Create workers for this camera if pipeline is running
            if self.running:
                await self._create_camera_workers(camera_config)
                self._start_camera_workers(camera_id)
            
            self.logger.info(f"Successfully added camera configuration for {camera_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to add camera config for {camera_config.camera_id}: {str(e)}")
            return False
    
    async def remove_camera_config(self, camera_id: str) -> bool:
        """
        Remove a camera configuration dynamically.
        
        Args:
            camera_id: ID of camera to remove
            
        Returns:
            bool: True if successfully removed, False otherwise
        """
        try:
            if camera_id not in self.camera_configs:
                self.logger.warning(f"Camera {camera_id} does not exist")
                return False
            
            # Stop workers for this camera
            await self._stop_camera_workers(camera_id)
            
            # Remove camera config
            del self.camera_configs[camera_id]
            
            self.logger.info(f"Successfully removed camera configuration for {camera_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to remove camera config for {camera_id}: {str(e)}")
            return False
    
    async def update_camera_config(self, camera_config: CameraConfig) -> bool:
        """
        Update an existing camera configuration.
        
        Args:
            camera_config: Updated camera configuration
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        return await self.add_camera_config(camera_config)
    
    def enable_camera(self, camera_id: str) -> bool:
        """Enable a camera configuration."""
        return self._set_camera_state(camera_id, True, "enabled")

    def disable_camera(self, camera_id: str) -> bool:
        """Disable a camera configuration."""
        return self._set_camera_state(camera_id, False, "disabled")

    def _set_camera_state(self, camera_id: str, enabled: bool, state_name: str) -> bool:
        """Set camera enabled state."""
        if camera_id in self.camera_configs:
            self.camera_configs[camera_id].enabled = enabled
            self.logger.info(f"Camera {camera_id} {state_name}")
            return True
        return False
      
    
    async def _create_workers(self) -> None:
        """Create all worker instances for the pipeline."""
        await self._create_consumer_workers()
        self._create_inference_worker()
        self._create_postprocessing_worker()
        self._create_producer_worker()

    async def _create_consumer_workers(self) -> None:
        """Create consumer workers for all cameras."""
        for camera_config in self.camera_configs.values():
            await self._create_camera_workers(camera_config)

    def _create_inference_worker(self) -> None:
        """Create single inference worker."""
        worker = InferenceWorker(
            worker_id=0,
            inference_queue=self.inference_queue,
            postproc_queue=self.postproc_queue,
            inference_executor=self.inference_executor,
            message_timeout=self.message_timeout,
            inference_timeout=self.inference_timeout,
            inference_interface=self.inference_interface,
            use_shared_metrics=self.use_shared_metrics
        )
        self.inference_workers.append(worker)

    def _create_postprocessing_worker(self) -> None:
        """Create single post-processing worker."""
        worker = PostProcessingWorker(
            worker_id=0,
            postproc_queue=self.postproc_queue,
            output_queue=self.output_queue,
            postprocessing_executor=self.postprocessing_executor,
            message_timeout=self.message_timeout,
            inference_timeout=self.inference_timeout,
            post_processor=self.post_processor,
            frame_cache=self.frame_cache,
            use_shared_metrics=self.use_shared_metrics
        )
        self.postproc_workers.append(worker)

    def _create_producer_worker(self) -> None:
        """Create single producer worker."""
        worker = ProducerWorker(
            worker_id=0,
            output_queue=self.output_queue,
            camera_configs=self.camera_configs,
            message_timeout=self.message_timeout,
            analytics_publisher=self.analytics_publisher,
            use_shared_metrics=self.use_shared_metrics
        )
        self.producer_workers.append(worker)
    
    async def _create_camera_workers(self, camera_config: CameraConfig) -> None:
        """Create consumer workers for a specific camera."""
        camera_id = camera_config.camera_id

        worker = ConsumerWorker(
            camera_id=camera_id,
            worker_id=0,
            stream_config=camera_config.stream_config,
            input_topic=camera_config.input_topic,
            inference_queue=self.inference_queue,
            message_timeout=self.message_timeout,
            camera_config=camera_config,
            frame_cache=self.frame_cache,
            use_shared_metrics=self.use_shared_metrics
        )

        self.consumer_workers[camera_id] = [worker]
    
    def _start_workers(self) -> None:
        """Start all worker instances and track their threads."""
        self._start_all_camera_workers()
        self._start_worker_group(self.inference_workers)
        self._start_worker_group(self.postproc_workers)
        self._start_worker_group(self.producer_workers)
        
        # Start analytics publisher if initialized
        if self.analytics_publisher:
            try:
                analytics_thread = self.analytics_publisher.start()
                self.worker_threads.append(analytics_thread)
                self.logger.info("Started analytics publisher thread")
            except Exception as e:
                self.logger.error(f"Failed to start analytics publisher: {e}")

    def _start_all_camera_workers(self) -> None:
        """Start consumer workers for all cameras."""
        for camera_id in self.consumer_workers:
            self._start_camera_workers(camera_id)

    def _start_worker_group(self, workers: List) -> None:
        """Start a group of workers and track their threads."""
        for worker in workers:
            thread = worker.start()
            self.worker_threads.append(thread)
    
    def _start_camera_workers(self, camera_id: str) -> None:
        """Start consumer workers for a specific camera."""
        if camera_id in self.consumer_workers:
            self._start_worker_group(self.consumer_workers[camera_id])
    
    def _stop_workers(self) -> None:
        """Stop all worker instances gracefully."""
        self._stop_all_camera_workers()
        self._stop_worker_group(self.inference_workers)
        self._stop_worker_group(self.postproc_workers)
        self._stop_worker_group(self.producer_workers)

    def _stop_all_camera_workers(self) -> None:
        """Stop all camera consumer workers."""
        for workers in self.consumer_workers.values():
            self._stop_worker_group(workers)

    def _stop_worker_group(self, workers: List) -> None:
        """Stop a group of workers."""
        for worker in workers:
            worker.stop()
    
    async def _stop_camera_workers(self, camera_id: str) -> None:
        """Stop consumer workers and clean up producer streams for a specific camera."""
        # Stop consumer workers
        if camera_id in self.consumer_workers:
            self._stop_worker_group(self.consumer_workers[camera_id])
            del self.consumer_workers[camera_id]

        # Clean up producer streams for this camera
        for producer_worker in self.producer_workers:
            try:
                await producer_worker.remove_camera_stream(camera_id)
            except Exception as e:
                self.logger.error(f"Error removing producer stream for camera {camera_id}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics including frame cache statistics."""
        metrics = {
            "running": self.running,
            "camera_count": len(self.camera_configs),
            "enabled_cameras": sum(1 for config in self.camera_configs.values() if config.enabled),
            "queue_sizes": {
                "inference": self.inference_queue.qsize(),
                "postproc": self.postproc_queue.qsize(),
                "output": self.output_queue.qsize(),
            },
            "worker_counts": {
                "consumers": sum(len(workers) for workers in self.consumer_workers.values()),
                "inference_workers": len(self.inference_workers),
                "postproc_workers": len(self.postproc_workers),
                "producers": len(self.producer_workers),
            },
            "thread_counts": {
                "total_threads": len(self.worker_threads),
                "active_threads": len([t for t in self.worker_threads if t.is_alive()]),
            },
            "camera_configs": {
                camera_id: {
                    "input_topic": config.input_topic,
                    "output_topic": config.output_topic,
                    "enabled": config.enabled,
                    "stream_type": config.stream_config.get("stream_type", "kafka")
                }
                for camera_id, config in self.camera_configs.items()
            }
        }
        
        # Add frame cache metrics if available
        if self.frame_cache:
            try:
                metrics["frame_cache"] = self.frame_cache.get_metrics()
            except Exception as e:
                self.logger.warning(f"Failed to get frame cache metrics: {e}")
                metrics["frame_cache"] = {"error": str(e)}
        else:
            metrics["frame_cache"] = {"enabled": False}
        
        # Add analytics publisher metrics if available
        if self.analytics_publisher:
            try:
                metrics["analytics_publisher"] = self.analytics_publisher.get_metrics()
            except Exception as e:
                self.logger.warning(f"Failed to get analytics publisher metrics: {e}")
                metrics["analytics_publisher"] = {"error": str(e)}
        else:
            metrics["analytics_publisher"] = {"enabled": False}

        # Add Metric logger statistics
        if self.metric_logger:
            try:
                metrics["metric_logger"] = self.metric_logger.get_stats()
            except Exception as e:
                self.logger.warning(f"Failed to get metric logger stats: {e}")
                metrics["metric_logger"] = {"error": str(e)}
        else:
            metrics["metric_logger"] = {"enabled": False}
        
        return metrics

    def _initialize_frame_cache(self) -> None:
        """Initialize RedisFrameCache with TTL 10 minutes, deriving connection from Redis cameras if available."""
        try:
            # Find a Redis camera config for connection params
            host = "localhost"
            port = 6379
            password = None
            username = None
            db = 0

            for cfg in self.camera_configs.values():
                sc = cfg.stream_config or {}
                st = sc.get("stream_type", "redis").lower()  # Fixed: default to "redis" instead of "kafka"
                self.logger.debug(f"Frame cache init - Camera {cfg.camera_id}: stream_type={st}, config_keys={list(sc.keys())}")
                if st == "redis":
                    host = sc.get("host", host)
                    port = sc.get("port", port)
                    password = sc.get("password", password)
                    username = sc.get("username", username)
                    db = sc.get("db", db)
                    self.logger.info(f"Using Redis config from camera {cfg.camera_id}: {host}:{port}")
                    break

            # Lazy import to avoid dependency issues if not used
            from matrice_inference.server.stream.frame_cache import RedisFrameCache
            self.frame_cache = RedisFrameCache(
                host=host,
                port=port,
                db=db,
                password=password,
                username=username,
                ttl_seconds=600,  # 10 minutes
                worker_threads=1,  # conservative to avoid contention
            )
            self.frame_cache.start()
            self.logger.info("Initialized RedisFrameCache with 10-minute TTL")
        except Exception as e:
            self.frame_cache = None
            self.logger.warning(f"Frame cache initialization failed; proceeding without cache: {e}")

    def _initialize_analytics_publisher(self) -> None:
        """Initialize AnalyticsPublisher to send aggregated stats to Redis only."""
        if not self.enable_analytics_publisher:
            self.logger.info("Analytics publisher disabled")
            return

        try:
            # Find connection params from camera configs
            redis_host = "localhost"
            redis_port = 6379
            redis_password = None
            redis_username = None
            redis_db = 0

            # Extract Redis connection info from camera configs
            redis_found = False

            for cfg in self.camera_configs.values():
                sc = cfg.stream_config or {}
                st = sc.get("stream_type", "redis").lower()

                # Log for debugging
                self.logger.debug(
                    f"Analytics init - Camera {cfg.camera_id}: stream_type={st}, "
                    f"config_keys={list(sc.keys())}"
                )

                if st == "redis":
                    redis_host = sc.get("host", redis_host)
                    redis_port = sc.get("port", redis_port)
                    redis_password = sc.get("password", redis_password)
                    redis_username = sc.get("username", redis_username)
                    redis_db = sc.get("db", redis_db)
                    if not redis_found:
                        self.logger.info(f"Found Redis config from camera {cfg.camera_id}: {redis_host}:{redis_port}")
                        redis_found = True
                        break  # Use first Redis config found

            # Initialize analytics publisher (don't start yet) - Redis only
            self.analytics_publisher = AnalyticsPublisher(
                camera_configs=self.camera_configs,
                aggregation_interval=300,  # 5 minutes
                publish_interval=60,  # Publish every 60 seconds
                app_deployment_id=self.app_deployment_id,
                inference_pipeline_id=self.inference_pipeline_id,
                redis_host=redis_host,
                redis_port=redis_port,
                redis_password=redis_password,
                redis_username=redis_username,
                redis_db=redis_db,
                kafka_bootstrap_servers=None,
                enable_kafka=False,  # Disable Kafka publishing
            )

            self.logger.info(
                f"Initialized AnalyticsPublisher (Redis only: {redis_host}:{redis_port}, "
                f"aggregation: 5min, publish: 60s)"
            )
        except Exception as e:
            self.analytics_publisher = None
            self.logger.warning(f"Analytics publisher initialization failed; proceeding without it: {e}")
