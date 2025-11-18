import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal
from logpulses.db_monitor.base import DatabaseMonitor, safe_serialize


class CassandraMonitor(DatabaseMonitor):
    """Cassandra monitoring"""

    @staticmethod
    def patch_cassandra():
        """Patch Cassandra driver to track operations"""
        try:
            from cassandra.cluster import Session

            original_execute = Session.execute
            original_execute_async = Session.execute_async

            def patched_execute(self, query, parameters=None, *args, **kwargs):
                start = time.time()
                try:
                    result = original_execute(self, query, parameters, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    CassandraMonitor.log_operation(
                        db_type="Cassandra",
                        operation="execute",
                        duration_ms=duration,
                        query=str(query),
                        params=parameters,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    CassandraMonitor.log_operation(
                        db_type="Cassandra",
                        operation="execute",
                        duration_ms=duration,
                        query=str(query),
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_execute_async(self, query, parameters=None, *args, **kwargs):
                start = time.time()
                try:
                    future = original_execute_async(self, query, parameters, *args, **kwargs)

                    # Add callback to track completion
                    def log_completion(result):
                        duration = (time.time() - start) * 1000
                        CassandraMonitor.log_operation(
                            db_type="Cassandra",
                            operation="execute_async",
                            duration_ms=duration,
                            query=str(query),
                            params=parameters,
                        )

                    def log_error(exception):
                        duration = (time.time() - start) * 1000
                        CassandraMonitor.log_operation(
                            db_type="Cassandra",
                            operation="execute_async",
                            duration_ms=duration,
                            query=str(query),
                            status="failed",
                            error=str(exception),
                        )

                    future.add_callback(log_completion)
                    future.add_errback(log_error)

                    return future
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    CassandraMonitor.log_operation(
                        db_type="Cassandra",
                        operation="execute_async",
                        duration_ms=duration,
                        query=str(query),
                        status="failed",
                        error=str(e),
                    )
                    raise

            Session.execute = patched_execute
            Session.execute_async = patched_execute_async

            print("✅ Cassandra monitoring patched successfully")
        except ImportError:
            print("ℹ️  Cassandra driver not installed, skipping Cassandra monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch Cassandra: {e}")
