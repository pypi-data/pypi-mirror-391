"""Background monitor for camera configuration updates."""

import hashlib
import json
import logging
import threading
import time
from typing import Dict, Optional

from matrice_inference.server.stream.utils import CameraConfig
from matrice_inference.server.stream.stream_pipeline import StreamingPipeline
from matrice_inference.server.stream.app_deployment import AppDeployment


class CameraConfigMonitor:
    """Monitors and syncs camera configurations from app deployment API."""

    DEFAULT_CHECK_INTERVAL = 120  # seconds
    DEFAULT_HEARTBEAT_INTERVAL = 30  # seconds
    MAX_RETRY_ATTEMPTS = 5  # Maximum number of retry attempts per camera operation

    def __init__(
        self,
        app_deployment: AppDeployment,
        streaming_pipeline: StreamingPipeline,
        check_interval: int = DEFAULT_CHECK_INTERVAL,
        heartbeat_interval: int = DEFAULT_HEARTBEAT_INTERVAL
    ):
        """Initialize the camera config monitor.

        Args:
            app_deployment: AppDeployment instance to fetch configs
            streaming_pipeline: StreamingPipeline instance to update
            check_interval: Seconds between config checks
            heartbeat_interval: Seconds between heartbeat sends
        """
        self.app_deployment = app_deployment
        self.streaming_pipeline = streaming_pipeline
        self.check_interval = max(10, int(check_interval))  # Minimum 10 seconds
        self.heartbeat_interval = max(10, int(heartbeat_interval))  # Minimum 10 seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)

        # Track camera configs by hash to detect changes (thread-safe access)
        self.camera_hashes: Dict[str, str] = {}
        self._hashes_lock = threading.Lock()

        # Track retry attempts per camera (camera_id -> retry_count)
        self.retry_counts: Dict[str, int] = {}
        self._retry_lock = threading.Lock()

        # Track last heartbeat time
        self.last_heartbeat_time = 0

    def start(self) -> None:
        """Start the background monitoring thread."""
        if self.running:
            self.logger.warning("Camera config monitor already running")
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._monitor_loop,
            name="CameraConfigMonitor",
            daemon=False
        )
        self.thread.start()
        self.logger.info(f"Started camera config monitor (check interval: {self.check_interval}s)")

    def stop(self) -> None:
        """Stop the background monitoring thread."""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            self.logger.info("Stopped camera config monitor")

    def _monitor_loop(self) -> None:
        """Main monitoring loop - periodically sync camera configs and send heartbeats."""
        last_sync_time = 0

        while self.running:
            current_time = time.time()

            # Check if it's time to sync camera configs
            if current_time - last_sync_time >= self.check_interval:
                try:
                    self._sync_camera_configs()
                    last_sync_time = current_time
                except Exception as e:
                    self.logger.error(f"Error syncing camera configs: {e}")

            # Check and send heartbeat if needed (more frequent than config sync)
            try:
                self._send_heartbeat_if_needed()
            except Exception as e:
                self.logger.error(f"Error sending heartbeat: {e}")

            # Sleep for a short interval to allow quick shutdown and frequent heartbeat checks
            time.sleep(1)

    def _send_heartbeat_if_needed(self) -> None:
        """Send heartbeat if enough time has passed since last heartbeat."""
        current_time = time.time()

        # Check if it's time to send heartbeat
        if current_time - self.last_heartbeat_time < self.heartbeat_interval:
            return

        try:
            # Get current camera configs from streaming pipeline
            if self.streaming_pipeline and hasattr(self.streaming_pipeline, 'camera_configs'):
                camera_configs = self.streaming_pipeline.camera_configs

                # Send heartbeat with current configs
                success = self.app_deployment.send_heartbeat(camera_configs)

                if success:
                    self.last_heartbeat_time = current_time
                    self.logger.debug(f"Heartbeat sent successfully with {len(camera_configs)} cameras")
                else:
                    self.logger.warning("Failed to send heartbeat")
            else:
                self.logger.warning("Streaming pipeline not available or has no camera_configs")

        except Exception as e:
            self.logger.error(f"Error sending heartbeat: {e}", exc_info=True)

    def _sync_camera_configs(self) -> None:
        """Fetch latest configs from API and sync with pipeline."""
        try:
            # Fetch current configs from app deployment API
            latest_configs = self.app_deployment.get_camera_configs()
            
            if not latest_configs:
                self.logger.debug("No camera configs returned from API")
                return
            
            # Process each camera config
            for camera_id, camera_config in latest_configs.items():
                self._process_camera_config(camera_id, camera_config)
            
            # Optional: Remove cameras that are no longer in API
            # Uncomment if you want to auto-remove deleted cameras
            # self._remove_deleted_cameras(latest_configs)
            
        except Exception as e:
            self.logger.error(f"Failed to sync camera configs: {e}")

    def _should_retry_operation(self, camera_id: str) -> bool:
        """Check if we should retry an operation for this camera.

        Returns True if retry count is below maximum, False otherwise.
        """
        with self._retry_lock:
            retry_count = self.retry_counts.get(camera_id, 0)
            return retry_count < self.MAX_RETRY_ATTEMPTS

    def _increment_retry_count(self, camera_id: str) -> int:
        """Increment and return the retry count for a camera."""
        with self._retry_lock:
            self.retry_counts[camera_id] = self.retry_counts.get(camera_id, 0) + 1
            return self.retry_counts[camera_id]

    def _reset_retry_count(self, camera_id: str) -> None:
        """Reset the retry count for a camera after successful operation."""
        with self._retry_lock:
            if camera_id in self.retry_counts:
                del self.retry_counts[camera_id]

    def _process_camera_config(self, camera_id: str, camera_config: CameraConfig) -> None:
        """Process a single camera config - add new or update changed."""
        try:
            # Calculate config hash to detect changes
            config_hash = self._hash_camera_config(camera_config)

            # Thread-safe read of previous hash
            with self._hashes_lock:
                previous_hash = self.camera_hashes.get(camera_id)

            # Check if this is a new camera or config changed
            if previous_hash is None:
                # New camera - add it
                self._add_new_camera(camera_id, camera_config, config_hash)
            elif previous_hash != config_hash:
                # Config changed - update it
                self._update_changed_camera(camera_id, camera_config, config_hash)
            else:
                # No change - skip
                self.logger.debug(f"Camera {camera_id} config unchanged")

        except Exception as e:
            self.logger.error(f"Error processing camera {camera_id}: {e}")

    def _add_new_camera(self, camera_id: str, camera_config: CameraConfig, config_hash: str) -> None:
        """Add a new camera to the pipeline with retry logic."""
        try:
            # Check if we should retry this operation
            if not self._should_retry_operation(camera_id):
                # Max retries exceeded
                retry_count = self.retry_counts.get(camera_id, 0)
                self.logger.warning(
                    f"Max retry attempts ({self.MAX_RETRY_ATTEMPTS}) exceeded for camera {camera_id}, "
                    f"will retry on next successful event loop check"
                )
                return

            # Get event loop from streaming pipeline
            import asyncio
            event_loop = getattr(self.streaming_pipeline, '_event_loop', None)

            if not event_loop or not event_loop.is_running():
                # Increment retry count and log error
                retry_count = self._increment_retry_count(camera_id)
                self.logger.error(
                    f"No running event loop available in pipeline, cannot add camera {camera_id} "
                    f"(attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                )
                return

            # Schedule the coroutine on the pipeline's event loop
            future = asyncio.run_coroutine_threadsafe(
                self.streaming_pipeline.add_camera_config(camera_config),
                event_loop
            )

            # Wait for completion with timeout
            try:
                success = future.result(timeout=10.0)
                if success:
                    # Reset retry count on success
                    self._reset_retry_count(camera_id)
                    # Thread-safe write
                    with self._hashes_lock:
                        self.camera_hashes[camera_id] = config_hash
                    self.logger.info(f"Added new camera: {camera_id}")
                else:
                    retry_count = self._increment_retry_count(camera_id)
                    self.logger.warning(
                        f"Failed to add camera: {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                    )
            except TimeoutError:
                retry_count = self._increment_retry_count(camera_id)
                self.logger.error(
                    f"Timeout adding camera {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                )

        except Exception as e:
            retry_count = self._increment_retry_count(camera_id)
            self.logger.error(
                f"Error adding camera {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS}): {e}"
            )

    def _update_changed_camera(self, camera_id: str, camera_config: CameraConfig, config_hash: str) -> None:
        """Update an existing camera with changed config with retry logic."""
        try:
            # Check if we should retry this operation
            if not self._should_retry_operation(camera_id):
                # Max retries exceeded
                retry_count = self.retry_counts.get(camera_id, 0)
                self.logger.warning(
                    f"Max retry attempts ({self.MAX_RETRY_ATTEMPTS}) exceeded for camera {camera_id}, "
                    f"will retry on next successful event loop check"
                )
                return

            # Get event loop from streaming pipeline
            import asyncio
            event_loop = getattr(self.streaming_pipeline, '_event_loop', None)

            if not event_loop or not event_loop.is_running():
                # Increment retry count and log error
                retry_count = self._increment_retry_count(camera_id)
                self.logger.error(
                    f"No running event loop available in pipeline, cannot update camera {camera_id} "
                    f"(attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                )
                return

            # Schedule the coroutine on the pipeline's event loop
            future = asyncio.run_coroutine_threadsafe(
                self.streaming_pipeline.update_camera_config(camera_config),
                event_loop
            )

            # Wait for completion with timeout
            try:
                success = future.result(timeout=10.0)
                if success:
                    # Reset retry count on success
                    self._reset_retry_count(camera_id)
                    # Thread-safe write
                    with self._hashes_lock:
                        self.camera_hashes[camera_id] = config_hash
                    self.logger.info(f"Updated camera config: {camera_id}")
                else:
                    retry_count = self._increment_retry_count(camera_id)
                    self.logger.warning(
                        f"Failed to update camera: {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                    )
            except TimeoutError:
                retry_count = self._increment_retry_count(camera_id)
                self.logger.error(
                    f"Timeout updating camera {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                )

        except Exception as e:
            retry_count = self._increment_retry_count(camera_id)
            self.logger.error(
                f"Error updating camera {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS}): {e}"
            )

    def _remove_deleted_cameras(self, latest_configs: Dict[str, CameraConfig]) -> None:
        """Remove cameras that are no longer in the API response with retry logic."""
        # Thread-safe read
        with self._hashes_lock:
            current_camera_ids = set(self.camera_hashes.keys())

        latest_camera_ids = set(latest_configs.keys())
        deleted_camera_ids = current_camera_ids - latest_camera_ids

        for camera_id in deleted_camera_ids:
            try:
                # Check if we should retry this operation
                if not self._should_retry_operation(camera_id):
                    # Max retries exceeded
                    retry_count = self.retry_counts.get(camera_id, 0)
                    self.logger.warning(
                        f"Max retry attempts ({self.MAX_RETRY_ATTEMPTS}) exceeded for removing camera {camera_id}, "
                        f"will retry on next successful event loop check"
                    )
                    continue

                import asyncio
                event_loop = getattr(self.streaming_pipeline, '_event_loop', None)

                if not event_loop or not event_loop.is_running():
                    # Increment retry count and log error
                    retry_count = self._increment_retry_count(camera_id)
                    self.logger.error(
                        f"No running event loop available in pipeline, cannot remove camera {camera_id} "
                        f"(attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                    )
                    continue

                # Schedule the coroutine on the pipeline's event loop
                future = asyncio.run_coroutine_threadsafe(
                    self.streaming_pipeline.remove_camera_config(camera_id),
                    event_loop
                )

                # Wait for completion with timeout
                try:
                    success = future.result(timeout=10.0)
                    if success:
                        # Reset retry count on success
                        self._reset_retry_count(camera_id)
                        # Thread-safe delete
                        with self._hashes_lock:
                            del self.camera_hashes[camera_id]
                        self.logger.info(f"Removed deleted camera: {camera_id}")
                    else:
                        retry_count = self._increment_retry_count(camera_id)
                        self.logger.warning(
                            f"Failed to remove camera: {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                        )
                except TimeoutError:
                    retry_count = self._increment_retry_count(camera_id)
                    self.logger.error(
                        f"Timeout removing camera {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS})"
                    )

            except Exception as e:
                retry_count = self._increment_retry_count(camera_id)
                self.logger.error(
                    f"Error removing camera {camera_id} (attempt {retry_count}/{self.MAX_RETRY_ATTEMPTS}): {e}"
                )

    def _hash_camera_config(self, camera_config: CameraConfig) -> str:
        """Generate a hash of the camera config to detect changes."""
        try:
            # Create a dict with relevant config fields
            config_dict = {
                "camera_id": camera_config.camera_id,
                "input_topic": camera_config.input_topic,
                "output_topic": camera_config.output_topic,
                "stream_config": camera_config.stream_config,
                "enabled": camera_config.enabled
            }
            
            # Convert to JSON string (sorted for consistency) and hash
            config_str = json.dumps(config_dict, sort_keys=True)
            return hashlib.md5(config_str.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error hashing camera config: {e}")
            return ""

