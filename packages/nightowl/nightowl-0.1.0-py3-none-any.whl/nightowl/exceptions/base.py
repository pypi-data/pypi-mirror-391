import logging
from typing import Callable, Optional
from ..base import get_metrics_instance

logger = logging.getLogger(__name__)


class BaseServiceException(Exception):
    """
    Base exception class that automatically records metrics.
    
    Child classes specify which recording method to call via record_method_name.
    Metrics are recorded automatically when the exception is raised.
    
    Pattern:
        1. Service creates metrics instance (e.g., GatewayMetrics())
        2. Metrics instance registers itself globally
        3. Exception raised → looks up method → calls it → metric recorded
    """

    def __init__(self, message: str, error_type: str, record_method_name: str = None, log_level: Optional[int] = logging.ERROR, **record_method_args):
        """
        Args:
            message: Error message
            error_type: Type/category of error for metrics labels
            record_method_name: Name of the recording method to call (e.g., "record_general_error")
            log_level: Logging level (default: logging.ERROR)
            **record_method_args: Additional arguments to pass to the recording method (e.g., platform="line", query="select_users")
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.record_method_name = record_method_name
        self.log_level = log_level
        self.record_method_args = record_method_args

        # Always log the exception
        logger.log(self.log_level, f"[{self.__class__.__name__}] {message}")

        # Automatically record metrics if instance is available
        if get_metrics_instance() and self.record_method_name:
            record_method = getattr(get_metrics_instance(), self.record_method_name, None)
            if callable(record_method):
                try:
                    record_method(error_type=error_type, **self.record_method_args)
                except Exception as e:
                    logger.error(f"Error recording an exception: {self.__class__.__name__} - {e}")


class GeneralServiceException(BaseServiceException):
    """
    General service errors - records to general_errors_count metric.
    Use for errors that don't fit other categories.
    """
    def __init__(self, message: str, error_type: str):
        super().__init__(message=message, error_type=error_type, record_method_name="record_general_error")


class PlatformServiceException(BaseServiceException):
    """
    Platform-specific errors - records to platform_errors_count metric.
    Use for errors related to specific platforms (e.g., LINE, Telegram).
    """
    def __init__(self, message: str, error_type: str, platform: str):
        super().__init__(message=message, error_type=error_type, platform=platform, record_method_name="record_platform_error")


