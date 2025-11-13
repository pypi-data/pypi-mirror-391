import asyncio
import json
import logging
import queue
import threading
import time
from typing import Any, Dict, Optional

from matrice_common.stream.matrice_stream import MatriceStream
from matrice_inference.server.stream.utils import CameraConfig

from matrice_inference.server.stream.worker_metrics import WorkerMetrics


class ProducerWorker:
    """Handles message production to streams with clean resource management."""

    DEFAULT_DB = 0

    def __init__(
        self,
        worker_id: int,
        output_queue: queue.PriorityQueue,
        camera_configs: Dict[str, CameraConfig],
        message_timeout: float,
        analytics_publisher: Optional[Any] = None,
        use_shared_metrics: Optional[bool] = True,
    ):
        self.worker_id = worker_id
        self.output_queue = output_queue
        self.camera_configs = camera_configs
        self.message_timeout = message_timeout
        self.analytics_publisher = analytics_publisher
        self.running = False
        self.producer_streams: Dict[str, MatriceStream] = {}
        # self.metrics = WorkerMetrics( # ADD
        #     worker_id=f"producer_worker_{worker_id}",
        #     worker_type="producer"
        # )
        # self.metrics = WorkerMetrics.get_shared("producer")
        if use_shared_metrics:
            self.metrics = WorkerMetrics.get_shared("producer")
        else:
            self.metrics = WorkerMetrics(
                worker_id=f"producer_worker_{worker_id}",
                worker_type="producer"
            )

        self.logger = logging.getLogger(f"{__name__}.producer.{worker_id}")
    
    def start(self) -> threading.Thread:
        """Start the producer worker in a separate thread."""
        self.running = True
        self.metrics.mark_active()  # ADD
        thread = threading.Thread(
            target=self._run,
            name=f"ProducerWorker-{self.worker_id}",
            daemon=False
        )
        thread.start()
        return thread
    
    def stop(self):
        """Stop the producer worker."""
        self.running = False
        self.metrics.mark_inactive()  # ADD

    async def remove_camera_stream(self, camera_id: str) -> bool:
        """Remove producer stream for a specific camera.

        Args:
            camera_id: ID of camera whose stream should be removed

        Returns:
            bool: True if successfully removed, False otherwise
        """
        try:
            if camera_id in self.producer_streams:
                stream = self.producer_streams[camera_id]
                await stream.async_close()
                del self.producer_streams[camera_id]
                self.logger.info(f"Removed producer stream for camera {camera_id}")
                return True
            else:
                self.logger.warning(f"No producer stream found for camera {camera_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error removing producer stream for camera {camera_id}: {e}")
            return False
    
    def _run(self) -> None:
        """Main producer loop with proper resource management."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.logger.info(f"Started producer worker {self.worker_id}")

        try:
            loop.run_until_complete(self._initialize_streams())
            self._process_messages(loop)
        except Exception as e:
            self.logger.error(f"Fatal error in producer worker: {e}")
        finally:
            self._cleanup_resources(loop)

    def _process_messages(self, loop: asyncio.AbstractEventLoop) -> None:
        """Main message processing loop."""
        while self.running:
            # ADD: Start timing
            start_time = time.time()
            task_processed = False
            
            try:
                task = self._get_task_from_queue()
                if task:
                    task_processed = True
                    loop.run_until_complete(self._send_message_safely(task))
            except Exception as e:
                self.logger.error(f"Producer error: {e}")
                time.sleep(0.1)
            finally:
                # ADD: Record metrics only if task was processed
                if task_processed:
                    latency_ms = (time.time() - start_time) * 1000
                    self.metrics.record_latency(latency_ms)
                    self.metrics.record_throughput(count=1)
                else:
                    # No task - mark inactive for this iteration
                    self.metrics.mark_inactive()

    def _get_task_from_queue(self) -> Optional[Dict[str, Any]]:
        """Get task from output queue with timeout handling."""
        try:
            priority, timestamp, task_data = self.output_queue.get(timeout=self.message_timeout)
            return task_data
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Error getting task from queue: {e}")
            return None

    def _cleanup_resources(self, loop: asyncio.AbstractEventLoop) -> None:
        """Clean up streams and event loop resources."""
        for stream in self.producer_streams.values():
            try:
                loop.run_until_complete(stream.async_close())
            except Exception as e:
                self.logger.error(f"Error closing producer stream: {e}")

        try:
            loop.close()
        except Exception as e:
            self.logger.error(f"Error closing event loop: {e}")

        self.logger.info(f"Producer worker {self.worker_id} stopped")

    async def _initialize_streams(self) -> None:
        """Initialize producer streams for all cameras with proper error handling."""
        try:
            from matrice_common.stream.matrice_stream import MatriceStream, StreamType

            for camera_id, camera_config in self.camera_configs.items():
                try:
                    await self._initialize_camera_stream(camera_id, camera_config, StreamType)
                except Exception as e:
                    self.logger.error(f"Failed to initialize producer stream for camera {camera_id}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to initialize producer streams: {e}")
            raise

    async def _initialize_camera_stream(
        self, camera_id: str, camera_config: CameraConfig, StreamType: Any
    ) -> None:
        """Initialize producer stream for a single camera."""
        from matrice_common.stream.matrice_stream import MatriceStream

        stream_type = self._get_stream_type(camera_config.stream_config, StreamType)
        stream_params = self._build_stream_params(camera_config.stream_config, stream_type, StreamType)

        producer_stream = MatriceStream(stream_type, **stream_params)
        await producer_stream.async_setup(camera_config.output_topic)
        self.producer_streams[camera_id] = producer_stream

        self.logger.info(
            f"Initialized {stream_type.value} producer stream for camera {camera_id} in worker {self.worker_id}"
        )

    def _get_stream_type(self, stream_config: Dict[str, Any], StreamType: Any) -> Any:
        """Determine stream type from configuration."""
        stream_type_str = stream_config.get("stream_type", "kafka").lower()
        return StreamType.KAFKA if stream_type_str == "kafka" else StreamType.REDIS

    def _build_stream_params(self, stream_config: Dict[str, Any], stream_type: Any, StreamType: Any) -> Dict[str, Any]:
        """Build stream parameters based on type."""
        if stream_type == StreamType.KAFKA:
            return {
                "bootstrap_servers": stream_config.get("bootstrap_servers", "localhost:9092"),
                "sasl_username": stream_config.get("sasl_username", "matrice-sdk-user"),
                "sasl_password": stream_config.get("sasl_password", "matrice-sdk-password"),
                "sasl_mechanism": stream_config.get("sasl_mechanism", "SCRAM-SHA-256"),
                "security_protocol": stream_config.get("security_protocol", "SASL_PLAINTEXT"),
            }
        else:
            return {
                "host": stream_config.get("host", "localhost"),
                "port": stream_config.get("port", 6379),
                "password": stream_config.get("password"),
                "username": stream_config.get("username"),
                "db": stream_config.get("db", self.DEFAULT_DB),
            }
    
    async def _send_message_safely(self, task_data: Dict[str, Any]) -> None:
        """Send message to the appropriate stream with validation and error handling."""
        try:
            if not self._validate_task_data(task_data):
                return

            camera_id = task_data["camera_id"]

            if not self._validate_camera_availability(camera_id):
                return

            await self._send_message_to_stream(task_data, camera_id)

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    def _validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate that task data contains required fields."""
        required_fields = ["camera_id", "message_key", "data"]
        for field in required_fields:
            if field not in task_data:
                self.logger.error(f"Missing required field '{field}' in task data")
                return False
        return True

    def _validate_camera_availability(self, camera_id: str) -> bool:
        """Validate that camera and its stream are available."""
        if camera_id not in self.camera_configs:
            self.logger.warning(f"Camera {camera_id} not found in camera configs")
            return False

        camera_config = self.camera_configs[camera_id]
        if not camera_config.enabled:
            self.logger.debug(f"Camera {camera_id} is disabled, skipping message")
            return False

        # Check if producer stream exists, if not it will be created lazily
        if camera_id not in self.producer_streams:
            self.logger.info(f"Producer stream not found for camera {camera_id}, will be created on first send")

        return True

    async def _send_message_to_stream(self, task_data: Dict[str, Any], camera_id: str) -> None:
        """Send message to the stream for the specified camera with data validation."""
        # Create producer stream dynamically if it doesn't exist (for cameras added after startup)
        if camera_id not in self.producer_streams:
            camera_config = self.camera_configs[camera_id]
            try:
                from matrice_common.stream.matrice_stream import StreamType
                await self._initialize_camera_stream(camera_id, camera_config, StreamType)
                self.logger.info(f"Dynamically created producer stream for camera {camera_id}")
            except Exception as e:
                self.logger.error(f"Failed to create producer stream for camera {camera_id}: {e}")
                raise

        producer_stream = self.producer_streams[camera_id]
        camera_config = self.camera_configs[camera_id]
        
        # Validate data structure before sending
        data_to_send = task_data.get("data", {})
        
        # Check for post_processing_result and agg_summary
        if "post_processing_result" in data_to_send:
            post_proc_result = data_to_send["post_processing_result"]
            if isinstance(post_proc_result, dict):
                if "agg_summary" not in post_proc_result:
                    self.logger.warning(
                        f"Message for camera={camera_id} missing 'agg_summary' in post_processing_result. "
                        f"Available keys: {list(post_proc_result.keys())}"
                    )
                else:
                    agg_summary = post_proc_result.get("agg_summary", {})
                    if isinstance(agg_summary, dict) and agg_summary:
                        frame_keys = list(agg_summary.keys())
                        self.logger.debug(
                            f"Sending message for camera={camera_id} with agg_summary containing {len(frame_keys)} frame(s): {frame_keys}"
                        )
                    elif not agg_summary:
                        self.logger.warning(
                            f"Message for camera={camera_id} has empty agg_summary"
                        )
        else:
            self.logger.warning(
                f"Message for camera={camera_id} missing 'post_processing_result'. "
                f"Available keys: {list(data_to_send.keys())}"
            )

        await producer_stream.async_add_message(
            camera_config.output_topic,
            json.dumps(data_to_send),
            key=task_data["message_key"]
        )
        
        # Notify analytics publisher if available
        if self.analytics_publisher:
            try:
                self.analytics_publisher.enqueue_analytics_data(task_data)
            except Exception as e:
                self.logger.debug(f"Failed to enqueue analytics data: {e}")

