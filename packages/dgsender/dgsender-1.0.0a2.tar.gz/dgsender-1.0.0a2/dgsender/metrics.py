import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    name: str
    type: MetricType
    value: float
    tags: Dict[str, str]
    timestamp: float


class Metrics:
    """
    Metrics collector for monitoring sender operations
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._metrics: Dict[str, Metric] = {}
        self._callbacks: Dict[str, Callable[[Metric], None]] = {}

    def counter(self, name: str, value: float = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric"""
        if not self.enabled:
            return

        metric = Metric(
            name=name,
            type=MetricType.COUNTER,
            value=value,
            tags=tags or {},
            timestamp=time.time()
        )
        self._store_metric(metric)

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric"""
        if not self.enabled:
            return

        metric = Metric(
            name=name,
            type=MetricType.GAUGE,
            value=value,
            tags=tags or {},
            timestamp=time.time()
        )
        self._store_metric(metric)

    def timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> 'Timer':
        """Create a timer context manager"""
        return Timer(self, name, tags or {})

    def timeit(self, name: str, tags: Optional[Dict[str, str]] = None) -> Callable:
        """Decorator for timing function execution"""

        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.timer(name, tags):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def _store_metric(self, metric: Metric) -> None:
        """Store metric and trigger callbacks"""
        self._metrics[metric.name] = metric

        # Trigger callbacks
        for callback_name, callback in self._callbacks.items():
            try:
                callback(metric)
            except Exception as e:
                # Don't break metrics if callback fails
                pass

    def register_callback(self, name: str, callback: Callable[[Metric], None]) -> None:
        """Register a callback for new metrics"""
        self._callbacks[name] = callback

    def unregister_callback(self, name: str) -> None:
        """Unregister a callback"""
        self._callbacks.pop(name, None)

    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a specific metric"""
        return self._metrics.get(name)

    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all collected metrics"""
        return self._metrics.copy()

    def clear_metrics(self) -> None:
        """Clear all metrics"""
        self._metrics.clear()


class Timer:
    """Context manager for timing operations"""

    def __init__(self, metrics: Metrics, name: str, tags: Dict[str, str]):
        self.metrics = metrics
        self.name = name
        self.tags = tags
        self.start_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.metrics.gauge(f"{self.name}.duration", duration, self.tags)

            # Also create a timer metric
            timer_metric = Metric(
                name=f"{self.name}.timer",
                type=MetricType.TIMER,
                value=duration,
                tags=self.tags,
                timestamp=time.time()
            )
            self.metrics._store_metric(timer_metric)


class NullMetrics(Metrics):
    """Null object pattern for metrics when disabled"""

    def __init__(self):
        super().__init__(enabled=False)

    def counter(self, name: str, value: float = 1, tags: Optional[Dict[str, str]] = None) -> None:
        pass

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        pass

    def timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> 'Timer':
        return Timer(self, name, tags or {})