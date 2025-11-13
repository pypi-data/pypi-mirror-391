"""
Streaming Gateway Metrics Collection and Reporting System.

This module provides comprehensive metrics collection for streaming gateways,
including per-camera throughput and latency statistics, with reporting via Kafka.
"""

import base64
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from kafka import KafkaProducer


@dataclass
class MetricsConfig:
    """Configuration for metrics collection and reporting."""

    # Collection and reporting intervals
    collection_interval: float = 1.0  # Collect metrics every second
    reporting_interval: float = 30.0  # Report aggregated metrics every 30 seconds
    history_window: int = 30  # Keep 30 seconds of history for statistics

    # Kafka configuration
    metrics_topic: str = "streaming_gateway_metrics"
    kafka_timeout: float = 5.0  # Timeout for Kafka operations

    # Statistics configuration
    calculate_percentiles: bool = True
    percentiles: List[int] = field(default_factory=lambda: [0, 50, 100])


class MetricsCalculator:
    """Calculate statistical metrics over time windows."""

    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict[str, float]:
        """
        Calculate min, max, avg, p0, p50, p100 from a list of values.

        Args:
            values: List of numeric values

        Returns:
            Dictionary with statistical metrics
        """
        if not values:
            return {
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "p0": 0.0,
                "p50": 0.0,
                "p100": 0.0,
            }

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(values) / count,
            "p0": sorted_values[0],  # Minimum
            "p50": sorted_values[count // 2],  # Median
            "p100": sorted_values[-1],  # Maximum
        }

    @staticmethod
    def calculate_fps(frame_count_start: int, frame_count_end: int, time_elapsed: float) -> float:
        """
        Calculate frames per second.

        Args:
            frame_count_start: Starting frame count
            frame_count_end: Ending frame count
            time_elapsed: Time elapsed in seconds

        Returns:
            Frames per second
        """
        if time_elapsed <= 0:
            return 0.0

        frame_diff = frame_count_end - frame_count_start
        return frame_diff / time_elapsed


class MetricsCollector:
    """Collects and aggregates streaming gateway metrics."""

    def __init__(self, streaming_gateway, config: MetricsConfig):
        """
        Initialize metrics collector.

        Args:
            streaming_gateway: StreamingGateway instance
            config: Metrics configuration
        """
        self.streaming_gateway = streaming_gateway
        self.config = config

        # Thread safety
        self._lock = threading.RLock()

        # Time-series history
        self.metrics_history: List[Dict[str, Any]] = []

        # Track frame counts for FPS calculation
        self.camera_frame_counts: Dict[str, List[tuple]] = {}  # camera_id -> [(timestamp, count)]

    def collect_snapshot(self) -> Dict[str, Any]:
        """
        Collect current metrics snapshot from streaming gateway.

        Returns:
            Dictionary containing current metrics state
        """
        with self._lock:
            try:
                # Get overall statistics from streaming gateway
                gateway_stats = self.streaming_gateway.get_statistics()

                # Get camera streamer for detailed metrics
                camera_streamer = self.streaming_gateway.camera_streamer
                if not camera_streamer:
                    return None

                # Collect per-camera metrics
                camera_metrics = {}

                # Get active stream keys
                stream_keys = gateway_stats.get("my_stream_keys", [])

                for stream_key in stream_keys:
                    # Get timing statistics for this stream
                    timing = camera_streamer.statistics.get_timing_stats(stream_key)

                    if timing:
                        # Get camera_id from the streaming gateway mapping
                        camera_id = self.streaming_gateway.get_camera_id_for_stream_key(stream_key)
                        if not camera_id:
                            # Fallback: try to extract from stream_key if mapping not available
                            camera_id = stream_key.split('_')[0] if '_' in stream_key else stream_key

                        camera_metrics[camera_id] = {
                            "stream_key": stream_key,
                            "read_time": timing.get("last_read_time_sec", 0.0),  # Camera reading latency
                            "write_time": timing.get("last_write_time_sec", 0.0),  # Gateway sending latency
                            "process_time": timing.get("last_process_time_sec", 0.0),  # Total processing time
                            "frame_size": timing.get("last_frame_size_bytes", 0),  # ACG frame size in bytes
                        }

                # Get transmission stats for frame counts
                transmission_stats = gateway_stats.get("transmission_stats", {})

                snapshot = {
                    "timestamp": time.time(),
                    "cameras": camera_metrics,
                    "frames_sent": transmission_stats.get("frames_sent_full", 0),
                    "total_frames_processed": transmission_stats.get("total_frames_processed", 0),
                }

                return snapshot

            except Exception as e:
                logging.error(f"Error collecting metrics snapshot: {e}", exc_info=True)
                return None

    def add_to_history(self, snapshot: Dict[str, Any]):
        """
        Add snapshot to rolling history window.

        Args:
            snapshot: Metrics snapshot to add
        """
        if not snapshot:
            return

        with self._lock:
            self.metrics_history.append(snapshot)

            # Prune old data outside the window
            cutoff_time = time.time() - self.config.history_window
            self.metrics_history = [
                m for m in self.metrics_history
                if m["timestamp"] > cutoff_time
            ]

    def get_aggregated_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Calculate aggregated metrics from accumulated timing history.

        Returns:
            Dictionary with aggregated per-camera metrics
        """
        with self._lock:
            if not self.metrics_history:
                return None

            try:
                # Get camera streamer for accessing timing statistics
                camera_streamer = self.streaming_gateway.camera_streamer
                if not camera_streamer:
                    return None

                # Get active stream keys from the most recent snapshot
                stream_keys = set()
                for snapshot in self.metrics_history:
                    for camera_id, metrics in snapshot.get("cameras", {}).items():
                        stream_keys.add(metrics.get("stream_key"))

                # Calculate statistics for each stream using accumulated history
                per_camera_metrics = []

                for stream_key in stream_keys:
                    if not stream_key:
                        continue

                    # Get real statistics from accumulated timing history
                    stats = camera_streamer.statistics.get_timing_statistics(stream_key)

                    if not stats:
                        continue

                    # Get camera_id from the streaming gateway mapping
                    camera_id = self.streaming_gateway.get_camera_id_for_stream_key(stream_key)
                    if not camera_id:
                        # Fallback: try to extract from stream_key if mapping not available
                        camera_id = stream_key.split('_')[0] if '_' in stream_key else stream_key

                    # Get read time statistics (already in milliseconds)
                    read_time_ms = stats.get("read_time_ms", {})
                    read_stats = {
                        "min": read_time_ms.get("min", 0.0),
                        "max": read_time_ms.get("max", 0.0),
                        "avg": read_time_ms.get("avg", 0.0),
                        "p0": read_time_ms.get("min", 0.0),
                        "p50": read_time_ms.get("avg", 0.0),  # Use avg as approximation for median
                        "p100": read_time_ms.get("max", 0.0),
                        "unit": "ms"
                    }

                    # Get write time statistics (already in milliseconds)
                    write_time_ms = stats.get("write_time_ms", {})
                    write_stats = {
                        "min": write_time_ms.get("min", 0.0),
                        "max": write_time_ms.get("max", 0.0),
                        "avg": write_time_ms.get("avg", 0.0),
                        "p0": write_time_ms.get("min", 0.0),
                        "p50": write_time_ms.get("avg", 0.0),
                        "p100": write_time_ms.get("max", 0.0),
                        "unit": "ms"
                    }

                    # Get FPS statistics (real calculations from timestamps)
                    fps_data = stats.get("fps", {})
                    fps_stats = {
                        "min": fps_data.get("min", 0.0),
                        "max": fps_data.get("max", 0.0),
                        "avg": fps_data.get("avg", 0.0),
                        "p0": fps_data.get("min", 0.0),
                        "p50": fps_data.get("avg", 0.0),
                        "p100": fps_data.get("max", 0.0),
                        "unit": "fps"
                    }

                    # Get frame size statistics
                    frame_size_data = stats.get("frame_size_bytes", {})
                    frame_size_stats = {
                        "min": frame_size_data.get("min", 0.0),
                        "max": frame_size_data.get("max", 0.0),
                        "avg": frame_size_data.get("avg", 0.0),
                        "p0": frame_size_data.get("min", 0.0),
                        "p50": frame_size_data.get("avg", 0.0),
                        "p100": frame_size_data.get("max", 0.0),
                        "unit": "bytes"
                    }

                    # Build camera metrics in the required format
                    camera_metric = {
                        "camera_id": camera_id,
                        "camera_reading": {
                            "throughput": fps_stats,
                            "latency": read_stats
                        },
                        "gateway_sending": {
                            "throughput": fps_stats,  # Same as camera reading
                            "latency": write_stats
                        },
                        "acg_frame_size": frame_size_stats
                    }

                    per_camera_metrics.append(camera_metric)

                return per_camera_metrics

            except Exception as e:
                logging.error(f"Error calculating aggregated metrics: {e}", exc_info=True)
                return None


class MetricsReporter:
    """Sends metrics to Kafka topic."""

    def __init__(self, session, streaming_gateway_id: str, config: MetricsConfig):
        """
        Initialize metrics reporter.

        Args:
            session: Session object for API calls
            streaming_gateway_id: ID of the streaming gateway
            config: Metrics configuration
        """
        self.session = session
        self.streaming_gateway_id = streaming_gateway_id
        self.config = config

        self.producer: Optional[KafkaProducer] = None
        self._init_kafka_producer()

    def _init_kafka_producer(self):
        """Initialize Kafka producer for metrics."""
        try:
            # Get Kafka configuration (same pattern as EventListener)
            response = self.session.rpc.get("/v1/actions/get_kafka_info")

            if not response or "data" not in response:
                logging.error("Failed to get Kafka info for metrics reporter")
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
            self.producer = KafkaProducer(**kafka_config)
            logging.info(f"Kafka metrics producer initialized: {bootstrap_servers}")

        except Exception as e:
            logging.error(f"Failed to initialize Kafka metrics producer: {e}", exc_info=True)
            self.producer = None

    def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Send metrics to Kafka topic.

        Args:
            metrics: Metrics payload to send

        Returns:
            True if successful, False otherwise
        """
        if not self.producer:
            logging.warning("Kafka producer not initialized, cannot send metrics")
            return False

        try:
            # Send to Kafka
            future = self.producer.send(
                self.config.metrics_topic,
                value=metrics,
                key=self.streaming_gateway_id
            )

            # Wait for send to complete with timeout
            future.get(timeout=self.config.kafka_timeout)

            logging.info(f"Metrics sent to Kafka topic '{self.config.metrics_topic}'")
            return True

        except Exception as e:
            logging.error(f"Failed to send metrics to Kafka: {e}", exc_info=True)
            return False

    def close(self):
        """Close Kafka producer."""
        if self.producer:
            try:
                self.producer.close(timeout=5)
                logging.info("Kafka metrics producer closed")
            except Exception as e:
                logging.error(f"Error closing Kafka producer: {e}")


class HeartbeatReporter:
    """Sends heartbeat messages to Kafka topic."""

    def __init__(self, session, streaming_gateway_id: str, topic: str = "streaming_gateway_heartbeat", kafka_timeout: float = 5.0):
        """
        Initialize heartbeat reporter.

        Args:
            session: Session object for API calls
            streaming_gateway_id: ID of the streaming gateway
            topic: Kafka topic to send heartbeats to (default: streaming_gateway_heartbeat)
            kafka_timeout: Timeout for Kafka operations
        """
        self.session = session
        self.streaming_gateway_id = streaming_gateway_id
        self.topic = topic
        self.kafka_timeout = kafka_timeout

        self.producer: Optional[KafkaProducer] = None
        self._init_kafka_producer()

    def _init_kafka_producer(self):
        """Initialize Kafka producer for heartbeats."""
        try:
            # Get Kafka configuration (same pattern as EventListener)
            response = self.session.rpc.get("/v1/actions/get_kafka_info")

            if not response or "data" not in response:
                logging.error("Failed to get Kafka info for heartbeat reporter")
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
            self.producer = KafkaProducer(**kafka_config)
            logging.info(f"Kafka heartbeat producer initialized: {bootstrap_servers}, topic: {self.topic}")

        except Exception as e:
            logging.error(f"Failed to initialize Kafka heartbeat producer: {e}", exc_info=True)
            self.producer = None

    def send_heartbeat(self, camera_config: Dict[str, Any]) -> bool:
        """
        Send heartbeat to Kafka topic.

        Args:
            camera_config: Camera configuration payload to send

        Returns:
            True if successful, False otherwise
        """
        if not self.producer:
            logging.warning("Kafka producer not initialized, cannot send heartbeat")
            return False

        try:
            # Build heartbeat message with cameraConfig wrapper
            heartbeat = {
                "streaming_gateway_id": self.streaming_gateway_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "cameraConfig": camera_config
            }

            # Send to Kafka
            future = self.producer.send(
                self.topic,
                value=heartbeat,
                key=self.streaming_gateway_id
            )

            # Wait for send to complete with timeout
            future.get(timeout=self.kafka_timeout)

            logging.info(f"Heartbeat sent to Kafka topic '{self.topic}' with {len(camera_config.get('cameras', []))} cameras")
            return True

        except Exception as e:
            logging.error(f"Failed to send heartbeat to Kafka: {e}", exc_info=True)
            return False

    def close(self):
        """Close Kafka producer."""
        if self.producer:
            try:
                self.producer.close(timeout=5)
                logging.info("Kafka heartbeat producer closed")
            except Exception as e:
                logging.error(f"Error closing Kafka heartbeat producer: {e}")


class MetricsManager:
    """
    Main orchestrator for metrics collection and reporting.

    This class coordinates the collection of metrics from the streaming gateway,
    calculates statistics, and reports them via Kafka.
    """

    def __init__(
        self,
        streaming_gateway,
        session,
        streaming_gateway_id: str,
        action_id: Optional[str] = None,
        config: Optional[MetricsConfig] = None
    ):
        """
        Initialize metrics manager.

        Args:
            streaming_gateway: StreamingGateway instance
            session: Session object for API calls
            streaming_gateway_id: ID of the streaming gateway
            action_id: Optional action ID
            config: Optional metrics configuration (uses default if not provided)
        """
        self.streaming_gateway = streaming_gateway
        self.session = session
        self.streaming_gateway_id = streaming_gateway_id
        self.action_id = action_id
        self.config = config or MetricsConfig()

        # Initialize components
        self.collector = MetricsCollector(streaming_gateway, self.config)
        self.reporter = MetricsReporter(session, streaming_gateway_id, self.config)

        # Tracking
        self.last_report_time = 0
        self.enabled = True

        logging.info("Metrics manager initialized")

    def collect_and_report(self):
        """
        Collect current metrics and report if interval has elapsed.

        This method should be called periodically (e.g., every 1-30 seconds)
        from the health monitoring loop.
        """
        if not self.enabled:
            return

        try:
            # Always collect current snapshot
            snapshot = self.collector.collect_snapshot()
            if snapshot:
                self.collector.add_to_history(snapshot)

            # Report if interval has elapsed
            current_time = time.time()
            if current_time - self.last_report_time >= self.config.reporting_interval:
                self._generate_and_send_report()
                self.last_report_time = current_time

        except Exception as e:
            logging.error(f"Error in metrics collect_and_report: {e}", exc_info=True)

    def _generate_and_send_report(self):
        """Generate metrics report and send to Kafka."""
        try:
            # Get aggregated metrics
            per_camera_metrics = self.collector.get_aggregated_metrics()

            if not per_camera_metrics:
                logging.debug("No metrics data available for reporting")
                return

            # Build report in the required format
            report = {
                "streaming_gateway_id": self.streaming_gateway_id,
                "action_id": self.action_id or "unknown",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "per_camera_metrics": per_camera_metrics
            }

            # Send report
            success = self.reporter.send_metrics(report)

            if success:
                logging.info(f"Metrics report sent successfully ({len(per_camera_metrics)} cameras)")

                # Clear timing history after successful reporting to prevent unbounded memory growth
                camera_streamer = self.streaming_gateway.camera_streamer
                if camera_streamer:
                    camera_streamer.statistics.clear_timing_history()
                    logging.debug("Cleared timing history after successful metrics reporting")
            else:
                logging.warning("Failed to send metrics report")

        except Exception as e:
            logging.error(f"Error generating/sending metrics report: {e}", exc_info=True)

    def stop(self):
        """Stop metrics collection and close resources."""
        self.enabled = False
        self.reporter.close()
        logging.info("Metrics manager stopped")
