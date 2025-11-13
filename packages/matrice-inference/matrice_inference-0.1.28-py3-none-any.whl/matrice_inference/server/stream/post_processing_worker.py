import asyncio
import base64
import logging
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional
from matrice_inference.server.stream.worker_metrics import WorkerMetrics


class PostProcessingWorker:
    """Handles post-processing with clean resource management and error handling."""

    def __init__(
        self,
        worker_id: int,
        postproc_queue: queue.PriorityQueue,
        output_queue: queue.PriorityQueue,
        postprocessing_executor: ThreadPoolExecutor,
        message_timeout: float,
        inference_timeout: float,
        post_processor: Optional[Any] = None,
        frame_cache: Optional[Any] = None,
        use_shared_metrics: Optional[bool] = True,
    ):
        self.worker_id = worker_id
        self.postproc_queue = postproc_queue
        self.output_queue = output_queue
        self.postprocessing_executor = postprocessing_executor
        self.message_timeout = message_timeout
        self.inference_timeout = inference_timeout
        self.post_processor = post_processor
        self.frame_cache = frame_cache
        self.running = False
        # self.metrics = WorkerMetrics(
        #     worker_id=f"post_processing_worker_{worker_id}",
        #     worker_type="post_processing"
        # )
        # self.metrics = WorkerMetrics.get_shared("post_processing")
        if use_shared_metrics:
            self.metrics = WorkerMetrics.get_shared("post_processing")
        else:
            self.metrics = WorkerMetrics(
                worker_id=f"post_processing_worker_{worker_id}",
                worker_type="post_processing"
            )

        self.logger = logging.getLogger(f"{__name__}.postproc.{worker_id}")
    
    def start(self) -> threading.Thread:
        """Start the post-processing worker in a separate thread."""
        self.running = True
        self.metrics.mark_active()  # ADD
        thread = threading.Thread(
            target=self._run,
            name=f"PostProcWorker-{self.worker_id}",
            daemon=False
        )
        thread.start()
        return thread
    
    def stop(self):
        """Stop the post-processing worker."""
        self.running = False
        self.metrics.mark_inactive()  # ADD

    
    def _run(self) -> None:
        """Main post-processing dispatcher loop with proper error handling."""
        self.logger.info(f"Started post-processing worker {self.worker_id}")

        try:
            while self.running:
                task = self._get_task_from_queue()
                if task:
                    self._process_postproc_task(*task)
        except Exception as e:
            self.logger.error(f"Fatal error in post-processing worker: {e}")
        finally:
            self.logger.info(f"Post-processing worker {self.worker_id} stopped")

    def _get_task_from_queue(self) -> Optional[tuple]:
        """Get task from post-processing queue with timeout handling."""
        try:
            return self.postproc_queue.get(timeout=self.message_timeout)
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Error getting task from queue: {e}")
            return None
    
    def _process_postproc_task(self, priority: int, timestamp: float, task_data: Dict[str, Any]) -> None:
        """Process a single post-processing task with proper error handling."""
        # ADD: Start timing
        start_time = time.time()
        try:
            if not self._validate_task_data(task_data):
                return

            result = self._execute_post_processing(task_data)

            if result["success"]:
                output_task = self._create_output_task(task_data, result)
                self.output_queue.put((priority, time.time(), output_task))
            else:
                self.logger.error(f"Post-processing failed: {result['error']}")

        except Exception as e:
            self.logger.error(f"Post-processing task error: {e}")
        
        finally:
            # ADD: Record metrics regardless of success/failure
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency(latency_ms)
            self.metrics.record_throughput(count=1)

    def _validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate that task data contains required fields."""
        required_fields = ["original_message", "model_result", "input_stream"]
        for field in required_fields:
            if field not in task_data:
                self.logger.error(f"Missing required field '{field}' in task data")
                return False
        return True

    def _execute_post_processing(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute post-processing task in thread pool."""
        future = self.postprocessing_executor.submit(self._run_post_processing, task_data)
        return future.result(timeout=self.inference_timeout)

    def _create_output_task(self, task_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Create output task from post-processing result, ensuring agg_summary is properly included."""
        safe_input_stream = self._prepare_safe_input_stream(task_data)
        frame_id = self._determine_frame_id(task_data, safe_input_stream)

        # Strip content before publishing to output topic
        try:
            if isinstance(safe_input_stream, dict):
                safe_input_stream["content"] = ""
        except Exception:
            pass

        # Extract post_processing_result and ensure agg_summary is present
        post_processing_result = result.get("post_processing_result", {})
        
        # Log warning if agg_summary is missing
        if "agg_summary" not in post_processing_result:
            self.logger.warning(
                f"Post-processing result missing 'agg_summary' for camera={task_data['original_message'].camera_id}, "
                f"frame_id={frame_id}. Available keys: {list(post_processing_result.keys())}"
            )
        else:
            self.logger.debug(
                f"Post-processing result includes agg_summary for camera={task_data['original_message'].camera_id}, "
                f"frame_id={frame_id}, agg_summary_keys={list(post_processing_result.get('agg_summary', {}).keys())}"
            )

        output_data = {
            "camera_id": task_data["original_message"].camera_id,
            "message_key": task_data["original_message"].message_key,
            "timestamp": task_data["original_message"].timestamp.isoformat(),
            "frame_id": frame_id,
            "model_result": task_data["model_result"],
            "input_stream": safe_input_stream,
            "post_processing_result": post_processing_result,
            "processing_time_sec": task_data["processing_time"],
            "metadata": task_data.get("metadata", {})
        }
        
        # Verify frame_id is present in output
        if not frame_id:
            self.logger.warning(
                f"Output task missing frame_id for camera={task_data['original_message'].camera_id}, "
                f"message_key={task_data['original_message'].message_key}"
            )

        return {
            "camera_id": task_data["original_message"].camera_id,
            "message_key": task_data["original_message"].message_key,
            "data": output_data,
        }

    def _prepare_safe_input_stream(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input stream for output with proper frame_id propagation."""
        try:
            input_stream = task_data.get("input_stream")
            if isinstance(input_stream, dict):
                safe_input_stream = dict(input_stream)  # shallow copy
                # Ensure frame_id propagation
                if "frame_id" not in safe_input_stream and "frame_id" in task_data:
                    safe_input_stream["frame_id"] = task_data["frame_id"]
                return safe_input_stream
        except Exception as e:
            self.logger.warning(f"Error preparing input stream: {e}")

        return task_data.get("input_stream", {})

    def _determine_frame_id(self, task_data: Dict[str, Any], safe_input_stream: Dict[str, Any]) -> Optional[str]:
        """Determine frame_id from task data or input stream."""
        frame_id = task_data.get("frame_id")
        if not frame_id and isinstance(safe_input_stream, dict):
            frame_id = safe_input_stream.get("frame_id")
        return frame_id

    def _run_post_processing(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run post-processing in thread pool with proper error handling."""
        try:
            if not self.post_processor:
                raise ValueError("Post processor not initialized")

            processing_params = self._extract_processing_params(task_data)
            loop = self._get_or_create_event_loop()

            result = loop.run_until_complete(
                self.post_processor.process(**processing_params)
            )

            post_processing_result = self._format_processing_result(
                result, task_data, processing_params["stream_key"]
            )

            return {
                "post_processing_result": post_processing_result,
                "success": True,
                "error": None
            }

        except Exception as e:
            self.logger.error(f"Post-processing execution error: {e}", exc_info=True)
            return self._create_error_result(str(e), task_data)

    def _extract_processing_params(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate post-processing parameters from task data."""
        input_stream_data = task_data.get("input_stream", {})
        input_content = self._decode_input_content(input_stream_data.get("content"))
        
        # Extract stream_info and add frame_id to it
        stream_info = input_stream_data.get("stream_info", {})
        if isinstance(stream_info, dict):
            # Add frame_id to stream_info if available
            frame_id = task_data.get("frame_id")
            if not frame_id and isinstance(input_stream_data, dict):
                frame_id = input_stream_data.get("frame_id")
            if frame_id:
                stream_info["frame_id"] = frame_id

        return {
            "data": task_data["model_result"],
            "input_bytes": input_content if isinstance(input_content, bytes) else None,
            "stream_key": task_data.get("stream_key"),
            "stream_info": stream_info
        }

    def _decode_input_content(self, content: Any) -> Any:
        """Decode base64 content if it's a string."""
        if content and isinstance(content, str):
            try:
                return base64.b64decode(content)
            except Exception as e:
                self.logger.warning(f"Failed to decode base64 input: {e}")
                return None
        return content

    def _get_or_create_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get existing event loop or create a new one for this thread."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _format_processing_result(self, result: Any, task_data: Dict[str, Any], stream_key: str) -> Dict[str, Any]:
        """Format post-processing result based on success status with validation."""
        try:
            if result.is_success():
                formatted_result = self._create_success_result(result, task_data["model_result"], stream_key)
                
                # Validate that agg_summary is present in the formatted result
                if "agg_summary" not in formatted_result:
                    self.logger.error(
                        f"Formatted success result missing 'agg_summary' for stream_key={stream_key}. "
                        f"This should never happen. Available keys: {list(formatted_result.keys())}"
                    )
                
                return formatted_result
            else:
                self.logger.warning(
                    f"Post-processing failed for stream_key={stream_key}: {result.error_message}"
                )
                return self._create_failure_result(result, task_data["model_result"], stream_key)
        except Exception as e:
            self.logger.error(
                f"Error formatting processing result for stream_key={stream_key}: {e}",
                exc_info=True
            )
            # Return a safe error result
            return {
                "status": "post_processing_failed",
                "error": f"Failed to format result: {str(e)}",
                "error_type": "FormattingError",
                "stream_key": stream_key,
                "agg_summary": {},
                "raw_results": task_data.get("model_result", [])
            }

    def _create_success_result(self, result: Any, model_result: Any, stream_key: str) -> Dict[str, Any]:
        """Create successful post-processing result with comprehensive agg_summary validation."""
        processed_raw_results = self._get_processed_raw_results(result, model_result)
        agg_summary = self._extract_agg_summary(result)
        
        # Validate agg_summary structure
        if not agg_summary:
            self.logger.warning(
                f"Empty agg_summary in post-processing result for stream_key={stream_key}, "
                f"usecase={getattr(result, 'usecase', 'unknown')}"
            )
        elif not isinstance(agg_summary, dict):
            self.logger.error(
                f"Invalid agg_summary type (expected dict, got {type(agg_summary)}) for stream_key={stream_key}"
            )
            agg_summary = {}
        else:
            # Log agg_summary frame keys for debugging
            frame_keys = list(agg_summary.keys())
            self.logger.debug(
                f"Successfully created post-processing result with agg_summary for stream_key={stream_key}, "
                f"frames={frame_keys}, usecase={getattr(result, 'usecase', 'unknown')}"
            )

        return {
            "status": "success",
            "processing_time": result.processing_time,
            "usecase": getattr(result, 'usecase', ''),
            "category": getattr(result, 'category', ''),
            "summary": getattr(result, 'summary', ''),
            "insights": getattr(result, 'insights', []),
            "metrics": getattr(result, 'metrics', {}),
            "predictions": getattr(result, 'predictions', []),
            "agg_summary": agg_summary,
            "raw_results": processed_raw_results,
            "stream_key": stream_key
        }

    def _create_failure_result(self, result: Any, model_result: Any, stream_key: str) -> Dict[str, Any]:
        """Create failed post-processing result."""
        agg_summary = self._extract_agg_summary(result)

        return {
            "status": "post_processing_failed",
            "error": result.error_message,
            "error_type": getattr(result, 'error_type', 'ProcessingError'),
            "processing_time": result.processing_time,
            "stream_key": stream_key,
            "agg_summary": agg_summary,
            "raw_results": model_result
        }

    def _get_processed_raw_results(self, result: Any, model_result: Any) -> list:
        """Get processed raw results, handling face recognition special case."""
        try:
            if hasattr(result, 'usecase') and result.usecase != 'face_recognition':
                return model_result
        except Exception as e:
            self.logger.warning(f"Failed to get processed raw results: {e}")
        return []

    def _extract_agg_summary(self, result: Any) -> Dict[str, Any]:
        """Extract aggregated summary from result data with comprehensive logging."""
        try:
            if not hasattr(result, 'data'):
                self.logger.warning(
                    f"Post-processing result missing 'data' attribute. "
                    f"Result type: {type(result)}, available attributes: {dir(result)}"
                )
                return {}
            
            if not isinstance(result.data, dict):
                self.logger.warning(
                    f"Post-processing result.data is not a dict (type: {type(result.data)}). "
                    f"Cannot extract agg_summary."
                )
                return {}
            
            agg_summary = result.data.get("agg_summary")
            
            if agg_summary is None:
                self.logger.warning(
                    f"Post-processing result.data missing 'agg_summary' key. "
                    f"Available keys: {list(result.data.keys())}, "
                    f"usecase: {getattr(result, 'usecase', 'unknown')}"
                )
                return {}
            
            if not isinstance(agg_summary, dict):
                self.logger.error(
                    f"Post-processing agg_summary is not a dict (type: {type(agg_summary)}). "
                    f"Converting to empty dict."
                )
                return {}
            
            # Log successful extraction with frame count
            frame_count = len(agg_summary)
            self.logger.debug(
                f"Successfully extracted agg_summary with {frame_count} frame(s): {list(agg_summary.keys())}"
            )
            
            return agg_summary
            
        except Exception as e:
            self.logger.error(
                f"Exception while extracting agg_summary: {e}", 
                exc_info=True
            )
            return {}

    def _create_error_result(self, error_message: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create error post-processing result."""
        return {
            "post_processing_result": {
                "status": "post_processing_failed",
                "error": error_message,
                "error_type": "ProcessingError",
                "stream_key": task_data.get("stream_key")
            },
            "success": False,
            "error": error_message
        }
