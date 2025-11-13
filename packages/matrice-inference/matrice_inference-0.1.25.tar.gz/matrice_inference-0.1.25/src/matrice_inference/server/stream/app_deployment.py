
from typing import Dict, List, Optional, Any
import time
import logging
import asyncio
import base64
import json
from matrice_common.session import Session
from matrice_inference.server.stream.utils import CameraConfig
from matrice_inference.server.stream.app_event_listener import AppEventListener
from kafka import KafkaProducer


class AppDeployment:
    """Handles app deployment configuration and camera setup for streaming pipeline."""
    
    def __init__(self, session: Session, app_deployment_id: str, connection_timeout: int = 1200):  # Increased from 300 to 1200
        self.app_deployment_id = app_deployment_id
        self.rpc = session.rpc
        self.session = session
        self.connection_timeout = connection_timeout
        self.logger = logging.getLogger(__name__)

        # Event listener for dynamic topic updates (initialized separately)
        self.event_listener: Optional[AppEventListener] = None
        self.streaming_pipeline = None  # Reference to pipeline (set externally)
        self.event_loop = None  # Event loop reference for async operations

        # Heartbeat reporter for sending app deployment status
        self.heartbeat_producer: Optional[KafkaProducer] = None
        self.heartbeat_topic = "app_deployment_heartbeat"
        self.heartbeat_timeout = 5.0
        self._init_heartbeat_producer()
    
    def get_input_topics(self) -> List[Dict]:
        """Get input topics for the app deployment."""
        try:
            response = self.rpc.get(f"/v1/inference/get_input_topics_by_app_deployment_id/{self.app_deployment_id}")
            if response.get("success", False):
                return response.get("data", [])
            else:
                self.logger.error(f"Failed to get input topics: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            self.logger.error(f"Exception getting input topics: {str(e)}")
            return []
    
    def get_output_topics(self) -> List[Dict]:
        """Get output topics for the app deployment."""
        try:
            response = self.rpc.get(f"/v1/inference/get_output_topics_by_app_deployment_id/{self.app_deployment_id}")
            if response.get("success", False):
                return response.get("data", [])
            else:
                self.logger.error(f"Failed to get output topics: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            self.logger.error(f"Exception getting output topics: {str(e)}")
            return []
    
    def get_camera_configs(self) -> Dict[str, CameraConfig]:
        """
        Get camera configurations for the streaming pipeline.
        
        Returns:
            Dict[str, CameraConfig]: Dictionary mapping camera_id to CameraConfig
        """
        camera_configs = {}
        
        try:
            # Get input and output topics
            input_topics = self.get_input_topics()
            output_topics = self.get_output_topics()
            
            if not input_topics:
                self.logger.warning("No input topics found for app deployment")
                return camera_configs
            
            # Create mapping of camera_id to output topic
            output_topic_map = {}
            for output_topic in output_topics:
                camera_id = output_topic.get("cameraId")
                if camera_id:
                    output_topic_map[camera_id] = output_topic
            
            # Process each input topic to create camera config
            for input_topic in input_topics:
                try:
                    camera_id = input_topic.get("cameraId")
                    if not camera_id:
                        self.logger.warning("Input topic missing camera ID, skipping")
                        continue
                    
                    # Get corresponding output topic
                    output_topic = output_topic_map.get(camera_id)
                    if not output_topic:
                        self.logger.warning(f"No output topic found for camera {camera_id}, skipping")
                        continue
                    
                    # Get connection info for this server
                    server_id = input_topic.get("serverId")
                    server_type = input_topic.get("serverType", "redis").lower()
                    
                    if not server_id:
                        self.logger.warning(f"No server ID found for camera {camera_id}, skipping")
                        continue
                    
                    connection_info = self.get_and_wait_for_connection_info(server_type, server_id)
                    if not connection_info:
                        self.logger.error(f"Could not get connection info for camera {camera_id}, skipping")
                        continue
                    
                    # Create stream config
                    stream_config = connection_info.copy()
                    stream_config["stream_type"] = server_type
                    
                    # Validate stream_config
                    if not stream_config or "stream_type" not in stream_config:
                        self.logger.error(
                            f"Invalid stream_config for camera {camera_id}: {stream_config}, skipping"
                        )
                        continue
                    
                    # Log the configuration for debugging
                    self.logger.info(
                        f"Created camera config for {camera_id}: "
                        f"stream_type={server_type}, "
                        f"input_topic={input_topic.get('topicName')}, "
                        f"output_topic={output_topic.get('topicName')}, "
                        f"config_keys={list(stream_config.keys())}"
                    )
                    
                    # Create camera config
                    camera_config = CameraConfig(
                        camera_id=camera_id,
                        input_topic=input_topic.get("topicName"),
                        output_topic=output_topic.get("topicName"),
                        stream_config=stream_config,
                        enabled=True
                    )
                    
                    camera_configs[camera_id] = camera_config
                    
                except Exception as e:
                    self.logger.error(f"Error creating config for camera {camera_id}: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully created {len(camera_configs)} camera configurations")
            return camera_configs
            
        except Exception as e:
            self.logger.error(f"Error getting camera configs: {str(e)}")
            return camera_configs
    
    def get_and_wait_for_connection_info(self, server_type: str, server_id: str) -> Optional[Dict]:
        """Get the connection information for the streaming gateway."""
        def _get_kafka_connection_info():
            try:
                response = self.rpc.get(f"/v1/actions/get_kafka_server/{server_id}")
                if response.get("success", False):
                    data = response.get("data")
                    if (
                        data
                        and data.get("ipAddress")
                        and data.get("port")
                        and data.get("status") == "running"
                    ):
                        return {
                            'bootstrap_servers': f'{data["ipAddress"]}:{data["port"]}',
                            'sasl_mechanism': 'SCRAM-SHA-256',
                            'sasl_username': 'matrice-sdk-user',
                            'sasl_password': 'matrice-sdk-password',
                            'security_protocol': 'SASL_PLAINTEXT'
                        }
                    else:
                        self.logger.debug("Kafka connection information is not complete, waiting...")
                        return None
                else:
                    self.logger.debug("Failed to get Kafka connection information: %s", response.get("message", "Unknown error"))
                    return None
            except Exception as exc:
                self.logger.debug("Exception getting Kafka connection info: %s", str(exc))
                return None

        def _get_redis_connection_info():
            try:
                response = self.rpc.get(f"/v1/actions/redis_servers/{server_id}")
                if response.get("success", False):
                    data = response.get("data")
                    if (
                        data
                        and data.get("host")
                        and data.get("port")
                        and data.get("status") == "running"
                    ):
                        return {
                            'host': data["host"],
                            'port': int(data["port"]),
                            'password': data.get("password", ""),
                            'username': data.get("username"),
                            'db': data.get("db", 0),
                            'connection_timeout': 120  # Increased from 30 to 120
                        }
                    else:
                        self.logger.debug("Redis connection information is not complete, waiting...")
                        return None
                else:
                    self.logger.debug("Failed to get Redis connection information: %s", response.get("message", "Unknown error"))
                    return None
            except Exception as exc:
                self.logger.debug("Exception getting Redis connection info: %s", str(exc))
                return None

        start_time = time.time()
        last_log_time = 0
        
        while True:
            current_time = time.time()
            
            # Get connection info based on server type
            connection_info = None
            if server_type == "kafka":
                connection_info = _get_kafka_connection_info()
            elif server_type == "redis":
                connection_info = _get_redis_connection_info()
            else:
                raise ValueError(f"Unsupported server type: {server_type}")
            
            # If we got valid connection info, return it
            if connection_info:
                self.logger.info("Successfully retrieved %s connection information", server_type)
                return connection_info
            
            # Check timeout
            if current_time - start_time > self.connection_timeout:
                error_msg = f"Timeout waiting for {server_type} connection information after {self.connection_timeout} seconds"
                self.logger.error(error_msg)
                
                # Log the last response for debugging
                try:
                    if server_type == "kafka":
                        response = self.rpc.get(f"/v1/actions/get_kafka_server/{server_id}")
                    else:
                        response = self.rpc.get(f"/v1/actions/redis_servers/{server_id}")
                    self.logger.error("Last response received: %s", response)
                except Exception as exc:
                    self.logger.error("Failed to get last response for debugging: %s", str(exc))
                
                return None  # Return None instead of raising exception to allow graceful handling
            
            # Log waiting message every 10 seconds to avoid spam
            if current_time - last_log_time >= 10:
                elapsed = current_time - start_time
                remaining = self.connection_timeout - elapsed
                self.logger.info("Waiting for %s connection information... (%.1fs elapsed, %.1fs remaining)",
                           server_type, elapsed, remaining)
                last_log_time = current_time

            time.sleep(1)

    def _init_heartbeat_producer(self):
        """Initialize Kafka producer for heartbeats."""
        try:
            # Get Kafka configuration
            response = self.rpc.get("/v1/actions/get_kafka_info")

            if not response or "data" not in response:
                self.logger.error("Failed to get Kafka info for heartbeat reporter")
                return

            data = response.get("data", {})

            # Decode connection info
            ip = base64.b64decode(data["ip"]).decode("utf-8")
            port = base64.b64decode(data["port"]).decode("utf-8")
            bootstrap_servers = f"{ip}:{port}"

            # Create Kafka producer config
            kafka_config = {
                'bootstrap_servers': bootstrap_servers,
                'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                'key_serializer': lambda k: k.encode('utf-8') if k else None,
                'acks': 1,  # Wait for leader acknowledgment
                'retries': 3,
                'max_in_flight_requests_per_connection': 1,
            }

            # Add SASL authentication if available
            if "username" in data and "password" in data:
                username = base64.b64decode(data["username"]).decode("utf-8")
                password = base64.b64decode(data["password"]).decode("utf-8")

                kafka_config.update({
                    'security_protocol': 'SASL_PLAINTEXT',
                    'sasl_mechanism': 'SCRAM-SHA-256',
                    'sasl_plain_username': username,
                    'sasl_plain_password': password,
                })

            # Create producer
            self.heartbeat_producer = KafkaProducer(**kafka_config)
            self.logger.info(f"Kafka heartbeat producer initialized: {bootstrap_servers}, topic: {self.heartbeat_topic}")

        except Exception as e:
            self.logger.error(f"Failed to initialize Kafka heartbeat producer: {e}", exc_info=True)
            self.heartbeat_producer = None

    def send_heartbeat(self, camera_configs: Dict[str, CameraConfig]) -> bool:
        """
        Send heartbeat to Kafka topic with current camera configurations.

        Args:
            camera_configs: Dictionary of camera_id -> CameraConfig

        Returns:
            True if successful, False otherwise
        """
        if not self.heartbeat_producer:
            self.logger.warning("Kafka heartbeat producer not initialized, cannot send heartbeat")
            return False

        try:
            # Build camera config payload
            cameras = []
            for camera_id, config in camera_configs.items():
                camera_data = {
                    "camera_id": camera_id,
                    "input_topic": config.input_topic,
                    "output_topic": config.output_topic,
                    "stream_type": config.stream_config.get("stream_type", "unknown"),
                    "enabled": config.enabled
                }
                cameras.append(camera_data)

            # Build heartbeat message
            heartbeat = {
                "app_deployment_id": self.app_deployment_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "camera_count": len(cameras),
                "cameras": cameras
            }

            # Send to Kafka
            future = self.heartbeat_producer.send(
                self.heartbeat_topic,
                value=heartbeat,
                key=self.app_deployment_id
            )

            # Wait for send to complete with timeout
            future.get(timeout=self.heartbeat_timeout)

            self.logger.info(f"Heartbeat sent to Kafka topic '{self.heartbeat_topic}' with {len(cameras)} cameras")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send heartbeat to Kafka: {e}", exc_info=True)
            return False

    def close_heartbeat_producer(self):
        """Close Kafka heartbeat producer."""
        if self.heartbeat_producer:
            try:
                self.heartbeat_producer.close(timeout=5)
                self.logger.info("Kafka heartbeat producer closed")
            except Exception as e:
                self.logger.error(f"Error closing Kafka heartbeat producer: {e}")

    def initialize_event_listener(self, streaming_pipeline=None, event_loop=None) -> bool:
        """Initialize and start the app event listener.

        Args:
            streaming_pipeline: Reference to the StreamingPipeline instance for dynamic updates
            event_loop: Event loop for scheduling async tasks (optional, will try to get running loop)

        Returns:
            bool: True if successfully initialized and started
        """
        try:
            if self.event_listener and self.event_listener.is_listening:
                self.logger.warning("Event listener already running")
                return False

            self.streaming_pipeline = streaming_pipeline

            # Get or store event loop
            if event_loop:
                self.event_loop = event_loop
            else:
                try:
                    self.event_loop = asyncio.get_running_loop()
                except RuntimeError:
                    self.logger.warning("No running event loop found, async operations may not work")
                    self.event_loop = None

            # Create event listener
            self.event_listener = AppEventListener(
                session=self.session,
                app_deployment_id=self.app_deployment_id,
                on_topic_added=self._handle_topic_added,
                on_topic_deleted=self._handle_topic_deleted
            )

            # Start listening
            success = self.event_listener.start()
            if success:
                self.logger.info(f"App event listener started for deployment {self.app_deployment_id}")
            else:
                self.logger.error("Failed to start app event listener")

            return success

        except Exception as e:
            self.logger.error(f"Error initializing event listener: {e}")
            return False

    def stop_event_listener(self):
        """Stop the app event listener and close heartbeat producer."""
        if self.event_listener:
            self.event_listener.stop()
            self.event_listener = None
            self.logger.info("App event listener stopped")

        # Close heartbeat producer
        self.close_heartbeat_producer()

    def _handle_topic_added(self, event: Dict[str, Any]):
        """Handle topic added event.

        Args:
            event: Event dict containing topic information
        """
        try:
            topic_type = event.get('topicType')
            topic_data = event.get('data', {})
            camera_id = topic_data.get('cameraId')
            topic_name = topic_data.get('topicName')
            server_type = topic_data.get('serverType')

            self.logger.info(
                f"Topic added event received: {topic_type} topic for camera {camera_id} "
                f"(topic={topic_name}, server={server_type})"
            )

            # Validate required fields
            if not camera_id:
                self.logger.error("Topic added event missing cameraId, ignoring")
                return

            # For input topics, wait for corresponding output topic before adding camera
            if topic_type == 'input':
                self.logger.info(
                    f"Input topic added for camera {camera_id}. Will add to pipeline "
                    f"when corresponding output topic is available."
                )
                # Don't refresh yet - wait for output topic
                return

            # For output topics, try to refresh camera config (will succeed if input topic exists)
            if topic_type == 'output':
                # Refresh camera configs to include the new topic
                if not self.streaming_pipeline:
                    self.logger.error("No streaming pipeline reference, cannot add camera")
                    return

                if not self.event_loop:
                    self.logger.error("No event loop reference, cannot schedule async operation")
                    return
                
                if not self.event_loop.is_running():
                    self.logger.error("Event loop is not running, cannot schedule async operation")
                    return

                self.logger.info(f"Output topic added, attempting to add camera {camera_id} to pipeline")
                future = asyncio.run_coroutine_threadsafe(
                    self._refresh_camera_config(camera_id),
                    self.event_loop
                )
                
                # Optional: Add callback to log result
                def log_result(fut):
                    try:
                        fut.result()  # This will raise if the coroutine raised
                    except Exception as e:
                        self.logger.error(f"Failed to refresh camera config: {e}")
                
                future.add_done_callback(log_result)

        except Exception as e:
            self.logger.error(f"Error handling topic added event: {e}", exc_info=True)

    def _handle_topic_deleted(self, event: Dict[str, Any]):
        """Handle topic deleted event.

        Args:
            event: Event dict containing topic information
        """
        try:
            topic_type = event.get('topicType')
            topic_data = event.get('data', {})
            camera_id = topic_data.get('cameraId')
            topic_name = topic_data.get('topicName')

            self.logger.info(
                f"Topic deleted event received: {topic_type} topic for camera {camera_id} "
                f"(topic={topic_name})"
            )

            # Validate required fields
            if not camera_id:
                self.logger.error("Topic deleted event missing cameraId, ignoring")
                return

            # If input topic is deleted, log but don't remove from pipeline
            # (input topics may be shared, and removal should be based on output topic)
            if topic_type == 'input':
                self.logger.info(
                    f"Input topic deleted for camera {camera_id}. "
                    f"Camera will remain in pipeline unless output topic is also deleted."
                )
                return

            # If output topic is deleted, remove camera from pipeline
            if topic_type == 'output':
                if not self.streaming_pipeline:
                    self.logger.error("No streaming pipeline reference, cannot remove camera")
                    return

                if not self.event_loop:
                    self.logger.error("No event loop reference, cannot schedule async operation")
                    return
                
                if not self.event_loop.is_running():
                    self.logger.error("Event loop is not running, cannot schedule async operation")
                    return

                self.logger.info(f"Output topic deleted, removing camera {camera_id} from pipeline")
                future = asyncio.run_coroutine_threadsafe(
                    self._remove_camera_from_pipeline(camera_id),
                    self.event_loop
                )
                
                # Add callback to log result
                def log_result(fut):
                    try:
                        fut.result()  # This will raise if the coroutine raised
                    except Exception as e:
                        self.logger.error(f"Failed to remove camera from pipeline: {e}")
                
                future.add_done_callback(log_result)

        except Exception as e:
            self.logger.error(f"Error handling topic deleted event: {e}", exc_info=True)

    async def _refresh_camera_config(self, camera_id: str):
        """Refresh camera configuration and update pipeline.

        Args:
            camera_id: ID of camera to refresh
        """
        try:
            self.logger.info(f"Refreshing camera config for {camera_id}")

            # Get fresh camera configs
            camera_configs = self.get_camera_configs()

            # Check if camera still exists in configs
            if camera_id in camera_configs:
                new_config = camera_configs[camera_id]

                # Update or add camera in pipeline
                if self.streaming_pipeline:
                    success = await self.streaming_pipeline.add_camera_config(new_config)
                    if success:
                        self.logger.info(
                            f"✓ Successfully added/updated camera {camera_id} in pipeline "
                            f"(input={new_config.input_topic}, output={new_config.output_topic})"
                        )
                    else:
                        self.logger.error(f"✗ Failed to add/update camera {camera_id} in pipeline")
                else:
                    self.logger.error("No streaming pipeline available")
            else:
                self.logger.warning(
                    f"Camera {camera_id} not found in refreshed configs. "
                    f"This may indicate that both input and output topics are not yet available."
                )

        except Exception as e:
            self.logger.error(f"Error refreshing camera config for {camera_id}: {e}", exc_info=True)

    async def _remove_camera_from_pipeline(self, camera_id: str):
        """Remove camera from pipeline.

        Args:
            camera_id: ID of camera to remove
        """
        try:
            self.logger.info(f"Removing camera {camera_id} from pipeline")

            if self.streaming_pipeline:
                success = await self.streaming_pipeline.remove_camera_config(camera_id)
                if success:
                    self.logger.info(f"✓ Successfully removed camera {camera_id} from pipeline")
                else:
                    self.logger.warning(
                        f"✗ Failed to remove camera {camera_id} from pipeline "
                        f"(may have already been removed)"
                    )
            else:
                self.logger.error("No streaming pipeline available")

        except Exception as e:
            self.logger.error(f"Error removing camera {camera_id} from pipeline: {e}", exc_info=True)