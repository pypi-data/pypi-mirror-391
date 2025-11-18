import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal
from logpulses.db_monitor.base import DatabaseMonitor, safe_serialize


def monitor_db_operation(db_type: str = "Custom", operation_name: str = None):
    """
    Decorator to manually monitor any database operation

    Usage:
        @monitor_db_operation(db_type="MySQL", operation_name="get_user")
        def get_user_from_db(user_id):
            # your db code
            return user
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            op_name = operation_name or func.__name__

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000

                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    status="failed",
                    error=str(e),
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            op_name = operation_name or func.__name__

            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start) * 1000

                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    status="failed",
                    error=str(e),
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
