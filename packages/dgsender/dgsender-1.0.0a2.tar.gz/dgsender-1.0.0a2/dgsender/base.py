from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging


class BaseSender(ABC):
    """Base sender class with common functionality"""

    def __init__(self,
                 logger_instance: Optional[logging.Logger] = None,
                 metrics_instance=None):
        """
        Initialize base sender

        Args:
            logger_instance: Custom logger instance
            metrics_instance: Metrics collector instance (compatible with dgmetrics interface)
        """
        self.logger = logger_instance or logging.getLogger(__name__)
        self.metrics = metrics_instance

    @abstractmethod
    def send(self, *args, **kwargs):
        """Send message - to be implemented by subclasses"""
        pass

    def _log_error(self, message: str, exception: Optional[Exception] = None):
        """Common error logging method"""
        if exception:
            self.logger.error(f"{message}: {exception}")
        else:
            self.logger.error(message)

        # Record error metric if metrics available
        if self.metrics:
            self._record_metric_counter("sender.errors", tags={"sender_type": self.__class__.__name__})

    def _log_success(self, message: str):
        """Common success logging method"""
        self.logger.info(message)

        # Record success metric if metrics available
        if self.metrics:
            self._record_metric_counter("sender.success", tags={"sender_type": self.__class__.__name__})

    def _record_send_metric(self, message_type: str, duration: float, success: bool = True):
        """Record send operation metrics"""
        if not self.metrics:
            return

        tags = {
            "sender_type": self.__class__.__name__,
            "message_type": message_type,
            "success": str(success)
        }

        self._record_metric_counter("sender.requests", tags=tags)
        self._record_metric_gauge("sender.duration", duration, tags=tags)

        if success:
            self._record_metric_counter("sender.success", tags=tags)
        else:
            self._record_metric_counter("sender.failures", tags=tags)

    def _record_metric_counter(self, name: str, value: float = 1, tags: Optional[Dict[str, str]] = None):
        """Record counter metric with compatibility for different metrics implementations"""
        if not self.metrics:
            return

        try:
            # Try dgmetrics interface
            if hasattr(self.metrics, 'counter'):
                self.metrics.counter(name, value=value, tags=tags)
            # Try other common interfaces
            elif hasattr(self.metrics, 'increment'):
                self.metrics.increment(name, value=value, tags=tags)
            elif hasattr(self.metrics, 'incr'):
                self.metrics.incr(name, count=value, tags=tags)
        except Exception as e:
            # Don't break sending if metrics fail
            self.logger.warning(f"Failed to record metric {name}: {e}")

    def _record_metric_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record gauge metric with compatibility for different metrics implementations"""
        if not self.metrics:
            return

        try:
            # Try dgmetrics interface
            if hasattr(self.metrics, 'gauge'):
                self.metrics.gauge(name, value=value, tags=tags)
            # Try other common interfaces
            elif hasattr(self.metrics, 'set_gauge'):
                self.metrics.set_gauge(name, value=value, tags=tags)
            elif hasattr(self.metrics, 'gauge_set'):
                self.metrics.gauge_set(name, value=value, tags=tags)
        except Exception as e:
            # Don't break sending if metrics fail
            self.logger.warning(f"Failed to record metric {name}: {e}")

    def _record_metric_timer(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record timer metric with compatibility for different metrics implementations"""
        if not self.metrics:
            return

        try:
            # Try dgmetrics interface
            if hasattr(self.metrics, 'timer'):
                self.metrics.timer(name, value=duration, tags=tags)
            elif hasattr(self.metrics, 'histogram'):
                self.metrics.histogram(name, value=duration, tags=tags)
            elif hasattr(self.metrics, 'timing'):
                self.metrics.timing(name, value=duration * 1000, tags=tags)  # Convert to ms if needed
        except Exception as e:
            # Don't break sending if metrics fail
            self.logger.warning(f"Failed to record metric {name}: {e}")