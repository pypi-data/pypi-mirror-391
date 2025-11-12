# Nightowl - BrainAnalytics Internal Monitoring Package

Internal monitoring library for consistent Prometheus metrics and automatic exception tracking across all services.

This package provides **base metrics classes** and **exception classes** that can be extended to create custom metrics and exceptions for your service.

## Features

- ✅ Base metrics (requests, latency, errors)
- ✅ Automatic exception tracking - exceptions auto-record metrics
- ✅ Database metrics mixin (queries, errors, latency, availability)
- ✅ Platform support (optional)
- ✅ Extensible - create custom metrics and exceptions

## Installation

Add this package to your service's dependencies:

```bash
uv add "git+ssh://git@github.com/brainanalytics/nightowl.git"
```

This adds the dependency to your `pyproject.toml`. If it's already there, just run:
```bash
uv sync
```

**Note:** This is a private repository. Ensure you have:
- SSH access configured for GitHub
- Access to the `brainanalytics/nightowl` repository

If you need to set up SSH authentication:
```bash
# Test SSH connection
ssh -T git@github.com

# If authentication fails, configure SSH keys:
# 1. Generate key: ssh-keygen -t ed25519 -C "your_email@example.com"
# 2. Add to agent: ssh-add ~/.ssh/id_ed25519
# 3. Add public key to GitHub: Settings → SSH and GPG keys
```

**Verify access:**
```bash
# Test SSH connection to the repo
git ls-remote ssh://git@github.com/brainanalytics/nightowl.git
# ✅ Should show commit refs without errors

# Test dependency resolution (dry run)
uv sync --dry-run
# ✅ Should resolve dependencies without errors
```

## Quick Start

### Basic Usage

```python
from nightowl import BaseMetrics, BaseMetricsConfig
from nightowl.exceptions import GeneralServiceException

# Create and pre-initialize (or have a custom init function)
metrics = BaseMetrics(BaseMetricsConfig(app_name="my-service"))
metrics.initialize_base_metrics(
    endpoints=["/", "/api/users"],
    general_error_types=["ValidationError"]
)

# Record metrics
metrics.record_request(endpoint="/api/users")

# Exceptions
raise GeneralServiceException("Error occurred", "ValidationError")
```

### With Database

```python
from nightowl import BaseMetrics, DbMetricsConfig, DbMetricsMixin
from nightowl.exceptions import DbQueryException

class MyMetrics(DbMetricsMixin, BaseMetrics):
    def _init_mixin_metrics(self):
        self._init_db_metrics()

metrics = MyMetrics(DbMetricsConfig(app_name="service", db_name="postgres"))
metrics.initialize_base_metrics(endpoints=["/"], general_error_types=["Error"])
metrics.initialize_db_metrics(queries=["select_user"], error_types=["SQLAlchemyError"])

# DB metrics
metrics.record_db_query(query="select_user", status="success")
raise DbQueryException("Query failed", "TimeoutError", query="select_user")
```

### Custom Metrics and Exceptions

```python
from nightowl import BaseMetrics, create_counter
from nightowl.exceptions import GeneralServiceException

class CustomMetrics(BaseMetrics):
    def __init__(self, config=None):
        super().__init__(config)
        # Add custom metrics
        self.custom_count = create_counter(
            self.app_name, "custom_events", "Custom events", ["type"]
        )

# Custom exception
class CustomError(GeneralServiceException):
    def __init__(self, message: str):
        super().__init__(message, error_type="CustomError")

metrics = CustomMetrics()
metrics.custom_count.labels(**metrics._get_labels(type="event")).inc()
raise CustomError("Something went wrong")
```

## Exception System

Exceptions automatically record metrics when raised - no manual recording needed!

```python
from nightowl.exceptions import (
    GeneralServiceException,
    PlatformServiceException,
    DbQueryException,
    DbConnectionPoolException,
    DbTransactionException,
)

# All auto-record metrics
raise GeneralServiceException("Error", "ErrorType")
raise PlatformServiceException("Error", "BotError", platform="line")
raise DbQueryException("Failed", "TimeoutError", query="select_user")
```

**How it works:** Metrics instance registers itself globally. When exceptions are raised, they automatically find and use it to record metrics.

## Configuration

```bash
# Environment variables
PROJECT="my-project"
APP_NAME="my-service"
STAGE="production"
export DB_NAME="postgres"  # Optional
```

```python
# Or pass directly
from nightowl import BaseMetricsConfig, DbMetricsConfig

config = BaseMetricsConfig(app_name="service", stage="production")
# or
config = DbMetricsConfig(app_name="service", db_name="postgres")
```

## Available Metrics

**Base:** `requests_total`, `latency_seconds`, `general_errors_total`, `platform_errors_total`

**Database (DbMetricsMixin):** `db_queries_total`, `db_errors_total`, `db_latency_seconds`, `db_availability`, etc.

All metrics include labels: `project`, `app`, `stage`

## FastAPI Integration

```python
@app.get("/metrics")
async def publish_metrics():
    return export_metrics()
```

## Best Practices

**Create metrics at startup:**
```python
metrics = MyServiceMetrics()
metrics.initialize_base_metrics(...)
```

**Export convenience functions:**
```python
# metrics.py
metrics = MyServiceMetrics()
record_request = metrics.record_request
record_db_query = metrics.record_db_query
# Use: from .metrics import record_request
```

**Extend base exceptions:**
```python
class UserNotFoundError(GeneralServiceException):
    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} not found", error_type="UserNotFoundError")
```

## API Reference

**BaseMetrics:** `record_request()`, `record_latency()`, `record_general_error()`, `record_platform_error()`, `export_metrics()`

**DbMetricsMixin:** `record_db_query()`, `record_db_query_error()`, `record_db_latency()`, `record_db_availability()`, etc.

## License

MIT License - see LICENSE file for details.

