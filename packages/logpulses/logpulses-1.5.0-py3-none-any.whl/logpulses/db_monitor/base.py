"""
Universal Database Monitoring Module
Supports: MongoDB, MySQL, PostgreSQL, SQLAlchemy, Redis, Cassandra
Auto-tracks connection time and query execution time
"""

import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal

# Context variable to store DB operations (shared with logger)
db_operations = contextvars.ContextVar("db_operations", default=[])


# ============================================================================
# SERIALIZATION HELPERS
# ============================================================================


def safe_serialize(obj: Any) -> Any:
    """Safely serialize any object for logging"""
    try:
        # Handle MongoDB ObjectId
        if obj.__class__.__name__ == "ObjectId":
            return str(obj)

        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle date objects
        try:
            from datetime import date

            if isinstance(obj, date):
                return obj.isoformat()
        except:
            pass

        # Handle Decimal
        if isinstance(obj, Decimal):
            return float(obj)

        # Handle bytes
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except:
                return obj.hex()

        # Handle sets
        if isinstance(obj, set):
            return list(obj)

        # Handle dict
        if isinstance(obj, dict):
            return {k: safe_serialize(v) for k, v in obj.items()}

        # Handle list/tuple
        if isinstance(obj, (list, tuple)):
            return [safe_serialize(item) for item in obj]

        # Try converting to dict if object has __dict__
        if hasattr(obj, "__dict__"):
            return safe_serialize(obj.__dict__)

        # Fallback to string
        return str(obj)
    except Exception as e:
        return f"<serialization_error: {type(obj).__name__}>"


def truncate_query(query: str, max_length: int = 500) -> str:
    """Truncate long queries for logging"""
    if len(query) <= max_length:
        return query
    return query[:max_length] + f"... (truncated {len(query) - max_length} chars)"


class DatabaseMonitor:
    """Base class for database monitoring"""

    @staticmethod
    def log_operation(
        db_type: str,
        operation: str,
        duration_ms: float,
        query: Optional[str] = None,
        params: Optional[Any] = None,
        result_count: Optional[int] = None,
        connection_time_ms: Optional[float] = None,
        status: str = "success",
        error: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """Log a database operation"""
        ops = db_operations.get()

        log_entry = {
            "type": db_type,
            "operation": operation,
            "duration_ms": f"{duration_ms:.2f}",
            "timestamp": datetime.now().isoformat(),
            "status": status,
        }

        if connection_time_ms is not None:
            log_entry["connection_time_ms"] = f"{connection_time_ms:.2f}"

        if query:
            log_entry["query"] = truncate_query(str(query))

        if params:
            log_entry["params"] = safe_serialize(params)

        if result_count is not None:
            log_entry["result_count"] = result_count

        if error:
            log_entry["error"] = str(error)

        if metadata:
            log_entry["metadata"] = safe_serialize(metadata)

        ops.append(log_entry)
        db_operations.set(ops)
