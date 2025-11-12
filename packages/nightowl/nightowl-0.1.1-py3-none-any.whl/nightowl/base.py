import os
import logging
from typing import Optional
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from .config import BaseMetricsConfig
from .helper import create_counter, create_histogram, get_labels

logger = logging.getLogger(__name__)


# Global metrics registry
# This allows exceptions to access the metrics instance for automatic recording
_metrics_instance: Optional['BaseMetrics'] = None

def set_metrics_instance(metrics):
    """
    Register a metrics instance globally.
    Called automatically by BaseMetrics.__init__()
    """
    global _metrics_instance
    _metrics_instance = metrics

def get_metrics_instance():
    """
    Get the globally registered metrics instance.
    Used by exception classes to access recording methods.
    """
    return _metrics_instance

class BaseMetrics:
    """
    Base metrics class that ALL services inherit from.
    """
    
    def __init__(self, config: Optional[BaseMetricsConfig] = None):
        config = config if config is not None else BaseMetricsConfig()

        self.stage = config.stage
        self.app_name = config.app_name
        self.project = config.project
        self.db_name = getattr(config, 'db_name', None)  # Optional for DB services
        
        # Initialize base metrics
        self._init_base_metrics()
        
        # Initialize mixin metrics if any mixins are used
        # Child classes with mixins should call mixin init methods
        self._init_mixin_metrics()

        # Register the metrics instance globally
        set_metrics_instance(self)
        
        logger.info(f"Metrics initialized for {self.project}, app: {self.app_name}, stage: {self.stage}")
    
    def _init_mixin_metrics(self):
        """Override this in child classes to initialize mixin metrics"""
        pass
    
    def _init_base_metrics(self):
        """Metrics definitions for core metrics"""
        
        # Request counter
        self.request_count = create_counter(
            self.app_name,
            "requests",
            "Total API requests received",
            ["endpoint"]
        )

        # Latency histogram
        self.latency = create_histogram(
            self.app_name,
            "latency",
            "Latency in seconds",
            ["endpoint"]
        )
        
        # Latency histogram for async requests
        self.latency_async = create_histogram(
            self.app_name,
            "latency_async",
            "Latency in seconds for async requests",
            ["endpoint", "outcome"]
        )
        
        # General errors
        self.general_errors_count = create_counter(
            self.app_name,
            "general_errors",
            "Total general errors by type",
            ["error_type"]
        )

        # Platform errors
        self.platform_errors_count = create_counter(
            self.app_name,
            "platform_errors",
            "Total platform errors by type",
            ["error_type", "platform"]
        )

    def _get_labels(self, **extra_labels) -> dict:
        """Helper to build label dict dynamically with standard labels"""
        return get_labels(self.project, self.app_name, self.stage, **extra_labels)


    def initialize_base_metrics(self, 
                               endpoints: list[str], 
                               general_error_types: list[str],
                               platform_error_types: Optional[list[str]] = None,
                               platforms: Optional[list[str]] = None):
        """
        Pre-initialize base metrics with label combinations.
        
        This ensures metrics appear in Prometheus even before events occur.
        
        Args:
            endpoints: List of endpoint names
            general_error_types: List of general error types
            platform_error_types: Optional list of platform-specific error types (only if service uses platforms)
            platforms: Optional list of platform names (e.g., ["line", "telegram"])
        """


        for endpoint in endpoints:
            self.request_count.labels(**self._get_labels(endpoint=endpoint))
            self.latency.labels(**self._get_labels(endpoint=endpoint))
        
        logger.info(f"Base metrics initialized for request and latency metrics")

        for error_type in general_error_types:
            self.general_errors_count.labels(**self._get_labels(error_type=error_type))

        logger.info(f"Base metrics initialized for general error metrics")
        
        # Platform metrics are optional - only initialise if both lists provided
        if platform_error_types and platforms:
            for platform in platforms:
                for error_type in platform_error_types:
                    self.platform_errors_count.labels(**self._get_labels(error_type=error_type, platform=platform))
            logger.info(f"Base metrics initialized for platform error metrics")
    

    # ========== Basic Methods for Recording and Exporting Metrics ==========

    def record_request(self, endpoint: str):
        self.request_count.labels(**self._get_labels(endpoint=endpoint)).inc()

    def record_latency(self, endpoint: str):
        return self.latency.labels(**self._get_labels(endpoint=endpoint)).time()
    
    # def record_latency_async(self, endpoint: str, duration: float):
    #     return self.latency.labels(**self._get_labels(endpoint=endpoint)).observe(duration)

    def record_general_error(self, error_type: str):
        """Record a general error"""
        self.general_errors_count.labels(**self._get_labels(error_type=error_type)).inc()
    
    def record_platform_error(self, error_type: str, platform: str):
        """Record a platform-specific error (only for services that use platforms)"""
        self.platform_errors_count.labels(**self._get_labels(error_type=error_type, platform=platform)).inc()
    
    def export_metrics(self):
        """Export metrics in Prometheus format"""
        metrics_output = generate_latest()
        return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)

