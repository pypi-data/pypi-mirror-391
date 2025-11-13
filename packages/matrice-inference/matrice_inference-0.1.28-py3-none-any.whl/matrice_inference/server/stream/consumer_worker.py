# Import moved to method where it's needed to avoid circular imports
import asyncio
import json
import logging
import queue
import threading
import time
import base64
import copy
import cv2
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from matrice_inference.server.stream.utils import CameraConfig, StreamMessage
from matrice_inference.server.stream.worker_metrics import WorkerMetrics

class ConsumerWorker:
    """Handles message consumption from streams with optimized processing.
    
    Frame ID Management:
    -------------------
    This worker ensures frame_id uniqueness and consistency throughout the pipeline:
    
    1. Frame ID Source Priority:
       - Upstream frame_id (from message data) - preferred
       - Message key (if UUID-like)
       - Generated unique ID (camera_id + worker_id + uuid4)
    
    2. Frame Caching:
       - Frames are cached to Redis using: stream:frames:{frame_id}
       - frame_id MUST be unique across all apps and cameras
       - The same frame_id is used throughout the entire pipeline
    
    3. Multi-App Safety:
       - Each app deployment has unique camera_ids
       - Generated IDs include camera_id + worker_id + uuid4 for uniqueness
       - Redis prefix ensures isolation between different frame types
    
    4. Frame ID Flow:
       Consumer → Inference → Post-Processing → Producer
       The frame_id is preserved in task_data["frame_id"] at each stage
       and included in the final output message for client retrieval.
    """

    DEFAULT_PRIORITY = 1
    DEFAULT_DB = 0
    DEFAULT_CONNECTION_TIMEOUT = 120

    def __init__(
        self,
        camera_id: str,
        worker_id: int,
        stream_config: Dict[str, Any],
        input_topic: str,
        inference_queue: queue.PriorityQueue,
        message_timeout: float,
        camera_config: CameraConfig,
        frame_cache: Optional[Any] = None,
        use_shared_metrics: Optional[bool] = True,
    ):
        self.camera_id = camera_id
        self.worker_id = worker_id
        self.stream_config = stream_config
        self.input_topic = input_topic
        self.inference_queue = inference_queue
        self.message_timeout = message_timeout
        self.camera_config = camera_config
        self.running = False
        self.stream: Optional[Any] = None
        self.logger = logging.getLogger(f"{__name__}.consumer.{camera_id}.{worker_id}")
        # H.265 stream decoder instance (initialized lazily per worker)
        self._h265_stream_decoder = None
        # Optional frame cache for low-latency caching at ingestion
        self.frame_cache = frame_cache
        # self.metrics = WorkerMetrics(
        #     worker_id=f"consumer_worker_{camera_id}_{worker_id}",
        #     worker_type="consumer"
        # )
        # self.metrics = WorkerMetrics.get_shared("consumer")
        if use_shared_metrics:
            self.metrics = WorkerMetrics.get_shared("consumer")
        else:
            self.metrics = WorkerMetrics(
                worker_id=f"consumer_worker_{camera_id}_{worker_id}",
                worker_type="consumer"
            )

    
    def start(self) -> threading.Thread:
        """Start the consumer worker in a separate thread."""
        self.running = True
        self.metrics.mark_active()  # ADD
        thread = threading.Thread(
            target=self._run,
            name=f"Consumer-{self.camera_id}-{self.worker_id}",
            daemon=False
        )
        thread.start()
        return thread
    
    def stop(self):
        """Stop the consumer worker."""
        self.running = False
        self.metrics.mark_inactive()  # ADD
        try:
            if self._h265_stream_decoder is not None:
                self._h265_stream_decoder.stop()
        except Exception:
            pass
    
    def _run(self) -> None:
        """Main consumer loop with proper resource management."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.logger.info(f"Started consumer worker for camera {self.camera_id}")

        try:
            loop.run_until_complete(self._initialize_stream())
            self._consume_messages(loop)
        except Exception as e:
            self.logger.error(f"Fatal error in consumer worker: {e}")
        finally:
            self._cleanup_resources(loop)

    def _consume_messages(self, loop: asyncio.AbstractEventLoop) -> None:
        """Main message consumption loop."""
        while self.running and self.camera_config.enabled:
            # ADD: Start timing
            start_time = time.time()
            message_processed = False
            
            try:
                message_data = loop.run_until_complete(self._get_message_safely())
                if message_data:
                    message_processed = True
                    self._process_message(message_data)
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                time.sleep(1.0)
            finally:
                # ADD: Record metrics only if message was processed
                if message_processed:
                    latency_ms = (time.time() - start_time) * 1000
                    self.metrics.record_latency(latency_ms)
                    self.metrics.record_throughput(count=1)
                else:
                    # No message - mark inactive for this iteration
                    self.metrics.mark_inactive()

    def _cleanup_resources(self, loop: asyncio.AbstractEventLoop) -> None:
        """Clean up stream and event loop resources."""
        if self.stream:
            try:
                loop.run_until_complete(self.stream.async_close())
            except Exception as e:
                self.logger.error(f"Error closing stream: {e}")

        try:
            loop.close()
        except Exception as e:
            self.logger.error(f"Error closing event loop: {e}")

        self.logger.info(f"Consumer worker stopped for camera {self.camera_id}")

    async def _initialize_stream(self) -> None:
        """Initialize MatriceStream with proper configuration."""
        try:
            from matrice_common.stream.matrice_stream import MatriceStream, StreamType

            stream_type = self._get_stream_type()
            stream_params = self._build_stream_params(stream_type)

            self.stream = MatriceStream(stream_type, **stream_params)
            consumer_group = f"inference_consumer_{self.camera_id}_{self.worker_id}"
            await self.stream.async_setup(self.input_topic, consumer_group)

            self.logger.info(f"Initialized {stream_type.value} stream for consumer worker {self.worker_id}")

        except Exception as e:
            self.logger.error(f"Failed to initialize stream: {e}")
            raise

    def _get_stream_type(self):
        """Determine stream type from configuration."""
        from matrice_common.stream.matrice_stream import StreamType
        stream_type_str = self.stream_config.get("stream_type", "kafka").lower()
        return StreamType.KAFKA if stream_type_str == "kafka" else StreamType.REDIS

    def _build_stream_params(self, stream_type) -> Dict[str, Any]:
        """Build stream parameters based on type."""
        from matrice_common.stream.matrice_stream import StreamType

        if stream_type == StreamType.KAFKA:
            return {
                "bootstrap_servers": self.stream_config.get("bootstrap_servers", "localhost:9092"),
                "sasl_username": self.stream_config.get("sasl_username", "matrice-sdk-user"),
                "sasl_password": self.stream_config.get("sasl_password", "matrice-sdk-password"),
                "sasl_mechanism": self.stream_config.get("sasl_mechanism", "SCRAM-SHA-256"),
                "security_protocol": self.stream_config.get("security_protocol", "SASL_PLAINTEXT"),
            }
        else:
            return {
                "host": self.stream_config.get("host", "localhost"),
                "port": self.stream_config.get("port", 6379),
                "password": self.stream_config.get("password"),
                "username": self.stream_config.get("username"),
                "db": self.stream_config.get("db", self.DEFAULT_DB),
                "connection_timeout": self.stream_config.get("connection_timeout", self.DEFAULT_CONNECTION_TIMEOUT),
            }

    async def _get_message_safely(self) -> Optional[Dict[str, Any]]:
        """Safely get message from stream."""
        if not self.stream:
            self.logger.error("Stream not initialized")
            return None

        try:
            return await self.stream.async_get_message(self.message_timeout)
        except Exception as e:
            self.logger.debug(f"Error getting message: {e}")
            return None

    # -------------------- H.265 helpers --------------------
    def _decode_h265_frame(self, h265_bytes: bytes, width: int, height: int):
        """Decode a single H.265-encoded frame to OpenCV BGR image."""
        try:
            try:
                # Prefer local matrice_common implementation if available
                from matrice_common.video.h265_processor import H265FrameDecoder
                decoder = H265FrameDecoder()
                frame = decoder.decode_frame(h265_bytes, width=width, height=height)
                return frame
            except Exception as e:
                self.logger.error(f"H.265 single-frame decode failed: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Unexpected error in H.265 frame decode: {e}")
            return None

    def _ensure_h265_stream_decoder(self, width: int, height: int):
        """Ensure a continuous H.265 stream decoder exists with given dimensions."""
        if self._h265_stream_decoder is not None:
            return True
        try:
            from matrice_common.video.h265_processor import H265StreamDecoder
            decoder = H265StreamDecoder(width=width, height=height)
            if not decoder.start():
                self.logger.error("Failed to start H.265 stream decoder")
                return False
            self._h265_stream_decoder = decoder
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize H.265 stream decoder: {e}")
            return False

    def _frame_to_jpeg_bytes(self, frame) -> bytes:
        """Encode an OpenCV BGR frame to JPEG bytes."""
        try:
            ok, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            if not ok:
                raise RuntimeError("cv2.imencode failed")
            return buf.tobytes()
        except Exception as e:
            self.logger.error(f"Failed to encode frame to JPEG: {e}")
            return b""
    
    def _process_message(self, message_data: Dict[str, Any]) -> None:
        """Process incoming message and add to inference queue.
        
        This method:
        1. Extracts/generates a unique frame_id
        2. Handles codec-specific processing (H.264, H.265, JPEG, etc.)
        3. Caches the frame content to Redis with the frame_id
        4. Enqueues the task for inference with frame_id preserved
        
        Frame ID Consistency:
        - The frame_id is determined once at the start of processing
        - The same frame_id is used for cache writes and task data
        - frame_id is propagated through the entire pipeline
        - Output messages include the frame_id for client retrieval
        
        Multi-App Safety:
        - frame_id uniqueness ensures no collisions between apps
        - Redis prefix (stream:frames:) provides namespace isolation
        - Cache writes are non-blocking to prevent pipeline delays
        """
        try:
            message_key = self._extract_message_key(message_data)
            data = self._parse_message_data(message_data)
            input_stream = self._extract_input_stream(data)
            extra_params = self._normalize_extra_params(data)
            frame_id = self._determine_frame_id(data, message_data)

            self._enrich_input_stream(input_stream, frame_id)

            # Codec detection
            codec = None
            codec_lower = None
            try:
                if isinstance(input_stream, dict):
                    codec = input_stream.get("video_codec") or input_stream.get("compression_format")
                    if isinstance(codec, str):
                        codec_lower = codec.lower()
            except Exception:
                codec_lower = None

            # H.264 handling (frame-wise) - upstream always sends JPEG-encoded frames
            # Content is base64-encoded JPEG, ready for PIL/inference
            if codec_lower == "h264" and isinstance(input_stream, dict):
                stream_unit = input_stream.get("stream_unit", "frame")
                if isinstance(stream_unit, str) and stream_unit.lower() != "frame":
                    self.logger.warning("Received H.264 with non-frame stream_unit; skipping")
                    return
                content_b64 = input_stream.get("content")
                if isinstance(content_b64, str) and content_b64:
                    # Cache JPEG base64 as-is
                    self._cache_frame(frame_id, content_b64)
                    stream_msg = self._create_stream_message(message_key, data)
                    task_data = self._build_task_data(stream_msg, input_stream, extra_params, frame_id)
                    self.inference_queue.put((stream_msg.priority, time.time(), task_data))
                    return
                self.logger.warning("H.264 frame missing content; skipping")
                return

            # H.265 handling: convert to JPEG base64 before enqueuing
            if codec_lower in ["h265", "hevc"] and isinstance(input_stream, dict):
                # Resolve resolution
                width = None
                height = None
                try:
                    res = input_stream.get("stream_resolution") or input_stream.get("original_resolution") or {}
                    width = int(res.get("width")) if res and res.get("width") else None
                    height = int(res.get("height")) if res and res.get("height") else None
                except Exception:
                    width, height = None, None

                payload_b64 = input_stream.get("content")
                payload_bytes = b""
                if isinstance(payload_b64, str) and payload_b64:
                    try:
                        payload_bytes = base64.b64decode(payload_b64)
                    except Exception:
                        payload_bytes = b""

                stream_unit = input_stream.get("stream_unit", "frame")
                is_stream_chunk = bool(input_stream.get("is_video_chunk")) or (isinstance(stream_unit, str) and stream_unit.lower() != "frame")

                stream_msg = self._create_stream_message(message_key, data)

                if not is_stream_chunk:
                    # Single-frame H.265
                    if payload_bytes and width and height:
                        frame_img = self._decode_h265_frame(payload_bytes, width, height)
                        if frame_img is not None:
                            jpeg_bytes = self._frame_to_jpeg_bytes(frame_img)
                            if jpeg_bytes:
                                input_stream_jpeg = copy.deepcopy(input_stream)
                                input_stream_jpeg["content"] = base64.b64encode(jpeg_bytes).decode("utf-8")
                                input_stream_jpeg["video_codec"] = "jpeg"
                                # Low-latency cache write
                                self._cache_frame(frame_id, input_stream_jpeg["content"]) 
                                task_data = self._build_task_data(stream_msg, input_stream_jpeg, extra_params, frame_id)
                                self.inference_queue.put((stream_msg.priority, time.time(), task_data))
                                return
                    # Drop undecodable H.265 frame
                    self.logger.warning("Dropping H.265 frame due to missing payload/resolution or decode failure")
                    return
                else:
                    # Stream-chunk H.265 (emit at most one frame per message using upstream frame_id)
                    if width and height and self._ensure_h265_stream_decoder(width, height) and payload_bytes:
                        try:
                            self._h265_stream_decoder.decode_bytes(payload_bytes)
                            latest_frame = None
                            while True:
                                frame_img = self._h265_stream_decoder.read_frame()
                                if frame_img is None:
                                    break
                                latest_frame = frame_img
                            if latest_frame is not None:
                                jpeg_bytes = self._frame_to_jpeg_bytes(latest_frame)
                                if jpeg_bytes:
                                    input_stream_jpeg = copy.deepcopy(input_stream)
                                    input_stream_jpeg["content"] = base64.b64encode(jpeg_bytes).decode("utf-8")
                                    input_stream_jpeg["video_codec"] = "jpeg"
                                    # Keep upstream frame_id as-is
                                    try:
                                        input_stream_jpeg["frame_id"] = frame_id
                                    except Exception:
                                        pass
                                    # Low-latency cache write
                                    self._cache_frame(frame_id, input_stream_jpeg["content"]) 
                                    task_data = self._build_task_data(stream_msg, input_stream_jpeg, extra_params, frame_id)
                                    self.inference_queue.put((stream_msg.priority, time.time(), task_data))
                                    return
                        except Exception as e:
                            self.logger.error(f"H.265 stream decode error: {e}")
                    # No complete frame available yet for this chunk; skip forwarding
                    self.logger.debug("No decoded frame available from H.265 stream chunk for this message")
                    return

            # Default path (other formats): enqueue as-is
            stream_msg = self._create_stream_message(message_key, data)
            # Cache if there is a base64 content present
            try:
                if isinstance(input_stream, dict) and isinstance(input_stream.get("content"), str) and input_stream.get("content"):
                    self._cache_frame(frame_id, input_stream.get("content"))
            except Exception:
                pass
            task_data = self._build_task_data(stream_msg, input_stream, extra_params, frame_id)
            self.inference_queue.put((stream_msg.priority, time.time(), task_data))

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse message JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def _extract_message_key(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extract message key from Kafka/Redis message."""
        if not isinstance(message_data, dict):
            return None

        key = message_data.get('key') or message_data.get('message_key')
        if isinstance(key, bytes):
            return key.decode('utf-8')
        return key

    def _parse_message_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse message data from different stream formats."""
        for field in ['value', 'data']:
            if field in message_data:
                value = message_data[field]
                if isinstance(value, dict):
                    return value
                elif isinstance(value, (str, bytes)):
                    if isinstance(value, bytes):
                        value = value.decode('utf-8')
                    return json.loads(value)
        return message_data

    def _extract_input_stream(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract input stream from message data."""
        input_stream = data.get("input_stream", {})
        return input_stream if input_stream else data

    def _normalize_extra_params(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize extra_params to ensure it's a dictionary."""
        extra_params = data.get("extra_params", {})

        if isinstance(extra_params, dict):
            return extra_params
        elif isinstance(extra_params, list):
            return self._merge_list_params(extra_params)
        else:
            self.logger.warning(f"Invalid extra_params type {type(extra_params)}, using empty dict")
            return {}

    def _merge_list_params(self, params_list: list) -> Dict[str, Any]:
        """Merge list of dictionaries into single dictionary."""
        if not params_list:
            return {}

        if all(isinstance(item, dict) for item in params_list):
            merged = {}
            for item in params_list:
                merged.update(item)
            return merged

        return {}

    def _determine_frame_id(self, data: Dict[str, Any], message_data: Dict[str, Any]) -> str:
        """Determine frame ID from message data with guaranteed uniqueness.
        
        Priority:
        1. Existing frame_id from upstream (UUID expected)
        2. Message key (if it looks like a UUID)
        3. Generate unique ID with camera context
        """
        # First priority: explicit frame_id from upstream
        frame_id = data.get("frame_id")
        if frame_id and isinstance(frame_id, str) and frame_id.strip():
            self.logger.debug(f"Using upstream frame_id: {frame_id}")
            return str(frame_id).strip()

        # Second priority: message key (if it's a UUID-like string)
        fallback_key = message_data.get("key") or data.get("input_name")
        if fallback_key:
            key_str = str(fallback_key)
            # Check if it looks like a UUID (contains dashes and right length)
            if "-" in key_str and len(key_str) >= 32:
                self.logger.debug(f"Using message key as frame_id: {key_str}")
                return key_str
        
        # Last resort: generate unique ID with camera, worker, and high-precision timestamp
        import uuid
        generated_id = f"{self.camera_id}_{self.worker_id}_{uuid.uuid4()}"
        self.logger.warning(
            f"No upstream frame_id found, generated unique ID: {generated_id} "
            f"(message_key: {fallback_key})"
        )
        return generated_id

    def _enrich_input_stream(self, input_stream: Dict[str, Any], frame_id: str) -> None:
        """Add frame_id to input_stream if not present."""
        try:
            if isinstance(input_stream, dict) and "frame_id" not in input_stream:
                input_stream["frame_id"] = frame_id
        except Exception:
            pass

    def _create_stream_message(self, message_key: Optional[str], data: Dict[str, Any]) -> StreamMessage:
        """Create StreamMessage instance."""
        final_key = message_key or data.get("input_name") or f"{self.camera_id}_{int(time.time())}"

        return StreamMessage(
            camera_id=self.camera_id,
            message_key=final_key,
            data=data,
            timestamp=datetime.now(timezone.utc),
            priority=self.DEFAULT_PRIORITY
        )

    def _build_task_data(self, stream_msg: StreamMessage, input_stream: Dict[str, Any],
                        extra_params: Dict[str, Any], frame_id: str) -> Dict[str, Any]:
        """Build task data for inference queue."""
        return {
            "message": stream_msg,
            "input_stream": input_stream,
            "stream_key": stream_msg.message_key,
            "extra_params": extra_params,
            "camera_config": self.camera_config.__dict__,
            "frame_id": frame_id
        }

    def _cache_frame(self, frame_id: Optional[str], content_b64: Optional[str]) -> None:
        """Write frame to Redis cache if configured, non-blocking.

        Args:
            frame_id: Unique frame identifier (uuid expected)
            content_b64: Base64-encoded JPEG string
        """
        if not self.frame_cache:
            self.logger.debug("Frame cache not configured, skipping cache write")
            return
            
        # Validate frame_id
        if not frame_id or not isinstance(frame_id, str):
            self.logger.warning(
                f"Invalid frame_id for caching: {frame_id!r} (type: {type(frame_id).__name__})"
            )
            return
        
        frame_id = frame_id.strip()
        if not frame_id:
            self.logger.warning("Empty frame_id after stripping, skipping cache")
            return
            
        # Validate content
        if not content_b64 or not isinstance(content_b64, str):
            self.logger.warning(
                f"Invalid content for frame_id={frame_id}: "
                f"type={type(content_b64).__name__}, "
                f"len={len(content_b64) if content_b64 else 0}"
            )
            return
        
        try:
            content_len = len(content_b64)
            self.logger.debug(
                f"Caching frame: frame_id={frame_id}, camera={self.camera_id}, "
                f"worker={self.worker_id}, content_size={content_len} bytes"
            )
            self.frame_cache.put(frame_id, content_b64)
            self.logger.debug(f"Successfully queued frame {frame_id} for caching")
        except Exception as e:
            # Do not block pipeline on cache errors
            self.logger.error(
                f"Frame cache put failed: frame_id={frame_id}, camera={self.camera_id}, "
                f"worker={self.worker_id}, error={e}",
                exc_info=True
            )

