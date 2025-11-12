from prometheus_client import Counter, Histogram, Gauge

"""
Helper functions to create Prometheus metrics.
"""

DEFAULT_LABELS = ["project", "app", "stage"]

def create_counter(app_name: str, metric_name: str, description: str, extra_labels: list[str]):
    return Counter(
        f"{app_name}_{metric_name}_total",
        description,
        extra_labels + DEFAULT_LABELS
    )

def create_histogram(app_name: str, metric_name: str, description: str, extra_labels: list[str]):
    return Histogram(
        f"{app_name}_{metric_name}_seconds",
        description,
        extra_labels + DEFAULT_LABELS
    )

def create_gauge(app_name: str, metric_name: str, description: str, extra_labels: list[str]):
    return Gauge(
        f"{app_name}_{metric_name}",
        description,
        extra_labels + DEFAULT_LABELS
    )

def get_labels(project: str, app: str, stage: str, **extra_labels) -> dict:
    """Helper to build label dict dynamically with standard labels"""
    return {
        "project": project,
        "app": app,
        "stage": stage,
        **extra_labels
    }
