import logging
import queue
import threading
import time
from typing import Optional, Dict, Any

try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None  # type: ignore


class RedisFrameCache:
    """Non-blocking Redis cache for frames with optimized resource management.

    Stores base64 string content under key 'stream:frames:{frame_id}' with field 'frame'.
    Each insert sets or refreshes the TTL.
    """

    DEFAULT_TTL_SECONDS = 300
    DEFAULT_MAX_QUEUE = 10000
    DEFAULT_WORKER_THREADS = 2
    DEFAULT_CONNECT_TIMEOUT = 2.0
    DEFAULT_SOCKET_TIMEOUT = 0.5
    DEFAULT_HEALTH_CHECK_INTERVAL = 30
    DEFAULT_PREFIX = "stream:frames:"

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        username: Optional[str] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        prefix: str = DEFAULT_PREFIX,
        max_queue: int = DEFAULT_MAX_QUEUE,
        worker_threads: int = DEFAULT_WORKER_THREADS,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        socket_timeout: float = DEFAULT_SOCKET_TIMEOUT,
    ) -> None:
        self.logger = logging.getLogger(f"{__name__}.frame_cache")
        self.ttl_seconds = max(1, int(ttl_seconds))
        self.prefix = prefix
        self.running = False
        self._worker_threads = max(1, int(worker_threads))

        self.queue: queue.Queue = queue.Queue(maxsize=max_queue)
        self.threads: list = []
        self._client: Optional[redis.Redis] = None
        
        # Metrics for monitoring and debugging
        self._metrics = {
            "frames_queued": 0,
            "frames_cached": 0,
            "frames_failed": 0,
            "frames_dropped": 0,
            "last_cache_time": None,
            "last_frame_id": None,
        }
        self._metrics_lock = threading.Lock()

        if not self._is_redis_available():
            return

        self._client = self._create_redis_client(
            host, port, db, password, username, connect_timeout, socket_timeout
        )

    def _is_redis_available(self) -> bool:
        """Check if Redis package is available."""
        if redis is None:
            self.logger.warning("redis package not installed; frame caching disabled")
            return False
        return True

    def _create_redis_client(
        self,
        host: str,
        port: int,
        db: int,
        password: Optional[str],
        username: Optional[str],
        connect_timeout: float,
        socket_timeout: float
    ) -> Optional[redis.Redis]:
        """Create Redis client with proper error handling."""
        try:
            return redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                username=username,
                socket_connect_timeout=connect_timeout,
                socket_timeout=socket_timeout,
                health_check_interval=self.DEFAULT_HEALTH_CHECK_INTERVAL,
                retry_on_timeout=True,
                decode_responses=True,
            )
        except Exception as e:
            self.logger.warning(f"Failed to initialize Redis client: {e}")
            return None

    def start(self) -> None:
        """Start the frame cache with worker threads."""
        if not self._client:
            self.logger.warning("Cannot start frame cache: Redis client not initialized")
            return
        
        if self.running:
            self.logger.warning("Frame cache already running")
            return

        self.running = True
        self._start_worker_threads()
        
        self.logger.info(
            f"Started RedisFrameCache: prefix={self.prefix}, ttl={self.ttl_seconds}s, "
            f"workers={self._worker_threads}, queue_size={self.queue.maxsize}"
        )

    def _start_worker_threads(self) -> None:
        """Start worker threads for processing cache operations."""
        for i in range(self._worker_threads):
            thread = threading.Thread(
                target=self._worker,
                name=f"FrameCache-{i}",
                daemon=True
            )
            thread.start()
            self.threads.append(thread)

    def stop(self) -> None:
        """Stop the frame cache and cleanup resources."""
        if not self.running:
            return

        self.running = False
        self._stop_worker_threads()
        self.threads.clear()

    def _stop_worker_threads(self) -> None:
        """Stop all worker threads gracefully."""
        # Signal threads to stop
        for _ in self.threads:
            try:
                self.queue.put_nowait(None)
            except queue.Full:
                pass

        # Wait for threads to finish
        for thread in self.threads:
            try:
                thread.join(timeout=2.0)
            except Exception as e:
                self.logger.warning(f"Error joining thread {thread.name}: {e}")

    def put(self, frame_id: str, base64_content: str) -> None:
        """Enqueue a cache write for the given frame.

        Args:
            frame_id: unique identifier for the frame (must be unique across all apps)
            base64_content: base64-encoded image string
        """
        if not self._is_cache_ready():
            self.logger.debug(
                f"Cache not ready for frame_id={frame_id}, skipping "
                f"(running={self.running}, client={self._client is not None})"
            )
            return

        if not self._validate_input(frame_id, base64_content):
            return

        try:
            # Build Redis key with prefix to avoid collisions
            key = f"{self.prefix}{frame_id}"
            content_len = len(base64_content)
            
            self.queue.put_nowait((key, base64_content, frame_id))
            
            # Update metrics
            with self._metrics_lock:
                self._metrics["frames_queued"] += 1
                self._metrics["last_frame_id"] = frame_id
            
            self.logger.debug(
                f"Queued frame for caching: frame_id={frame_id}, "
                f"redis_key={key}, content_size={content_len}, "
                f"queue_size={self.queue.qsize()}"
            )
        except queue.Full:
            self._handle_queue_full(frame_id)

    def _is_cache_ready(self) -> bool:
        """Check if cache is ready for operations."""
        return bool(self._client and self.running)

    def _validate_input(self, frame_id: str, base64_content: str) -> bool:
        """Validate input parameters."""
        if not frame_id or not isinstance(frame_id, str) or not frame_id.strip():
            self.logger.warning(
                f"Invalid frame_id: {frame_id!r} (type: {type(frame_id).__name__})"
            )
            return False
        if not base64_content or not isinstance(base64_content, str):
            self.logger.warning(
                f"Invalid base64_content for frame_id={frame_id}: "
                f"type={type(base64_content).__name__}, "
                f"len={len(base64_content) if base64_content else 0}"
            )
            return False
        return True

    def _handle_queue_full(self, frame_id: str) -> None:
        """Handle queue full condition."""
        with self._metrics_lock:
            self._metrics["frames_dropped"] += 1
        self.logger.warning(
            f"Frame cache queue full (size={self.queue.maxsize}); "
            f"dropping frame_id={frame_id}. Consider increasing max_queue or worker_threads."
        )

    def _worker(self) -> None:
        """Worker thread for processing cache operations."""
        while self.running:
            item = self._get_work_item()
            if item is None:
                continue
            if self._is_stop_signal(item):
                break

            self._process_cache_item(item)

    def _get_work_item(self) -> Optional[tuple]:
        """Get work item from queue with timeout."""
        try:
            return self.queue.get(timeout=0.5)
        except queue.Empty:
            return None

    def _is_stop_signal(self, item: tuple) -> bool:
        """Check if item is a stop signal."""
        return item is None

    def _process_cache_item(self, item: tuple) -> None:
        """Process a single cache item."""
        frame_id = "unknown"
        try:
            key, base64_content, frame_id = item
            self._store_frame_data(key, base64_content, frame_id)
        except ValueError as e:
            # Handle old tuple format without frame_id for backwards compatibility
            try:
                key, base64_content = item
                frame_id = key.replace(self.prefix, "") if key.startswith(self.prefix) else key
                self._store_frame_data(key, base64_content, frame_id)
            except Exception as inner_e:
                self.logger.error(f"Failed to unpack cache item: {inner_e}")
                with self._metrics_lock:
                    self._metrics["frames_failed"] += 1
        except Exception as e:
            self.logger.error(f"Failed to process cache item for frame_id={frame_id}: {e}")
            with self._metrics_lock:
                self._metrics["frames_failed"] += 1
        finally:
            self._mark_task_done()

    def _store_frame_data(self, key: str, base64_content: str, frame_id: str) -> None:
        """Store frame data in Redis with TTL.
        
        Uses Redis HSET + EXPIRE for atomic TTL management.
        Multiple apps can safely write to different frame_ids without conflicts.
        """
        start_time = time.time()
        try:
            content_len = len(base64_content)
            self.logger.debug(
                f"Writing to Redis: frame_id={frame_id}, key={key}, "
                f"content_size={content_len}, ttl={self.ttl_seconds}s"
            )
            
            # Store base64 string in Redis hash field 'frame', then set TTL
            self._client.hset(key, "frame", base64_content)
            self._client.expire(key, self.ttl_seconds)
            
            elapsed = time.time() - start_time
            
            # Update metrics
            with self._metrics_lock:
                self._metrics["frames_cached"] += 1
                self._metrics["last_cache_time"] = time.time()
                self._metrics["last_frame_id"] = frame_id
            
            self.logger.info(
                f"Successfully cached frame: frame_id={frame_id}, key={key}, "
                f"content_size={content_len}, ttl={self.ttl_seconds}s, "
                f"elapsed={elapsed:.3f}s"
            )
        except redis.RedisError as e:
            with self._metrics_lock:
                self._metrics["frames_failed"] += 1
            self.logger.error(
                f"Redis error caching frame: frame_id={frame_id}, key={key}, "
                f"error={e.__class__.__name__}: {e}"
            )
        except Exception as e:
            with self._metrics_lock:
                self._metrics["frames_failed"] += 1
            self.logger.error(
                f"Unexpected error caching frame: frame_id={frame_id}, key={key}, "
                f"error={e}", exc_info=True
            )

    def _mark_task_done(self) -> None:
        """Mark queue task as done."""
        try:
            self.queue.task_done()
        except Exception:
            pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics for monitoring and debugging.
        
        Returns:
            Dictionary containing cache metrics including:
            - frames_queued: Total frames queued for caching
            - frames_cached: Total frames successfully cached
            - frames_failed: Total frames that failed to cache
            - frames_dropped: Total frames dropped due to queue full
            - queue_size: Current queue size
            - last_cache_time: Timestamp of last successful cache
            - last_frame_id: Last frame_id cached
        """
        with self._metrics_lock:
            metrics = dict(self._metrics)
        
        metrics.update({
            "running": self.running,
            "queue_size": self.queue.qsize(),
            "queue_maxsize": self.queue.maxsize,
            "worker_threads": self._worker_threads,
            "prefix": self.prefix,
            "ttl_seconds": self.ttl_seconds,
        })
        
        return metrics


