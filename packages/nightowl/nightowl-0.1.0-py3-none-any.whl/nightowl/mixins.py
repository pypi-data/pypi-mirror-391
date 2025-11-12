from .helper import create_counter, create_histogram, create_gauge
from typing import Optional

class DbMetricsMixin:
    """
    Mixin for database metrics.
    
    Assumes the class using this mixin has:
    - self.app_name
    - self._get_labels(**extra_labels)
    """
    
    def _init_db_metrics(self):
        """Initialize database-specific metrics"""
        self.db_query_count = create_counter(
            self.app_name,
            "db_queries",
            "Total database queries",
            ["query", "status", "db_name"],
        )

        self.db_query_errors_count = create_counter(
            self.app_name,
            "db_errors",
            "Total database errors",
            ["query", "error_type", "db_name"],
        )

        self.db_connection_pool_errors_count = create_counter(
            self.app_name,
            "db_connection_pool_errors",
            "Total database connection errors such as timeout, failed attempts, etc.",
            ["error_type", "db_name"],
        )

        self.db_latency = create_histogram(
            self.app_name,
            "db_latency",
            "Latency in seconds for database operations",
            ["query", "db_name"],
        )

        self.db_query_retries_count = create_counter(
            self.app_name,
            "db_query_retries",
            "Total database query retries",
            ["query", "reason", "db_name"],
        )

        self.db_transaction_errors_count = create_counter(
            self.app_name,
            "db_transaction_errors",
            "Total database transaction aborts/rollbacks",
            ["query", "reason", "db_name"],
        )

        self.db_availability = create_gauge(
            self.app_name,
            "db_availability",
            "Health status of the database",
            ["db_name"],
        )
    
    def _get_db_labels(self, **extra_labels) -> dict:
        """Helper that always includes db_name for DB metrics"""
        return self._get_labels(db_name=self.db_name, **extra_labels)
    

    def initialize_db_metrics(self, 
                            queries: list[str], 
                            error_types: list[str], 
                            connection_pool_error_types: Optional[list[str]] = None, 
                            transaction_error_reasons: Optional[list[str]] = None, 
                            query_retry_reasons: Optional[list[str]] = None):
        """
        Pre-initialize db metrics with label combinations.
        
        This ensures metrics appear in Prometheus even before events occur.
        """
        # Combine default reasons with provided ones
        transaction_reasons = ["rollback"] + (transaction_error_reasons or [])
        retry_reasons = ["timeout"] + (query_retry_reasons or [])
        connection_pool_error_types = ["timeout", "failed_attempts"] + (connection_pool_error_types or [])
        
        for query in queries:
            self.db_query_count.labels(**self._get_db_labels(query=query, status="success"))
            self.db_query_count.labels(**self._get_db_labels(query=query, status="error"))
            self.db_latency.labels(**self._get_db_labels(query=query))
        
            for error_type in error_types:
                self.db_query_errors_count.labels(**self._get_db_labels(query=query, error_type=error_type))
            
            for transaction_error_reason in transaction_reasons:
                self.db_transaction_errors_count.labels(**self._get_db_labels(query=query, reason=transaction_error_reason))
            
            for query_retry_reason in retry_reasons:
                self.db_query_retries_count.labels(**self._get_db_labels(query=query, reason=query_retry_reason))
        
        for connection_pool_error_type in connection_pool_error_types:
            self.db_connection_pool_errors_count.labels(**self._get_db_labels(error_type=connection_pool_error_type))
        
        # Initialize availability with default labels only
        self.db_availability.labels(**self._get_db_labels()).set(0)

    # ========== Methods for Recording DB Metrics ==========
    
    def record_db_query(self, query: str, status: str):
        self.db_query_count.labels(**self._get_db_labels(query=query, status=status)).inc()
    
    def record_db_query_error(self, query: str, error_type: str):
        self.db_query_errors_count.labels(**self._get_db_labels(query=query, error_type=error_type)).inc()
    
    def record_db_connection_pool_error(self, error_type: str):
        self.db_connection_pool_errors_count.labels(**self._get_db_labels(error_type=error_type)).inc()
    
    def record_db_latency(self, query: str):
        return self.db_latency.labels(**self._get_db_labels(query=query)).time()
    
    def record_db_transaction_error(self, query: str, reason: str):
        self.db_transaction_errors_count.labels(**self._get_db_labels(query=query, reason=reason)).inc()
    
    def record_db_query_retry(self, query: str, reason: str):
        self.db_query_retries_count.labels(**self._get_db_labels(query=query, reason=reason)).inc()
    
    def record_db_availability(self, status: bool):
        """Record database availability status (1 for up, 0 for down)"""
        self.db_availability.labels(**self._get_db_labels()).set(1 if status else 0)