from .base import BaseServiceException


class BaseDbException(BaseServiceException):
    """
    Base class for database-related exceptions.
    Use this as parent for all DB error types.
    """
    pass


class DbQueryException(BaseDbException):
    """
    Database query errors - records to db_query_errors_count metric.
    Use for query execution failures, syntax errors, etc.
    
    Example:
        raise DbQueryException("Query timeout", "SQLAlchemyError", query="upsert_user")
    """
    def __init__(self, message: str, error_type: str, query: str):
        super().__init__(message=message, error_type=error_type, query=query, record_method_name="record_db_query_error")


class DbConnectionPoolException(BaseDbException):
    """
    Database connection pool errors - records to db_connection_pool_errors_count metric.
    Use for connection timeout, pool exhaustion, connection failures, etc.
    
    Example:
        raise DbConnectionPoolException("Connection pool exhausted", "timeout")
    """
    def __init__(self, message: str, error_type: str):
        super().__init__(message=message, error_type=error_type, record_method_name="record_db_connection_pool_error")


class DbTransactionException(BaseDbException):
    """
    Database transaction errors - records to db_transaction_errors_count metric.
    Use for transaction rollbacks, commit failures, deadlocks, etc.
    
    Example:
        raise DbTransactionException("Transaction rolled back", "DeadlockError", query="update_user", reason="deadlock")
    """
    def __init__(self, message: str, error_type: str, query: str, reason: str):
        super().__init__(
            message=message, 
            error_type=error_type, 
            query=query,
            reason=reason,
            record_method_name="record_db_transaction_error"
        )
