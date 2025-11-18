import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal
from logpulses.db_monitor.base import DatabaseMonitor, safe_serialize


class PostgreSQLMonitor(DatabaseMonitor):
    """PostgreSQL monitoring with connection and query tracking"""

    @staticmethod
    def patch_postgresql():
        """Patch psycopg2 to track operations"""
        try:
            import psycopg2
            import psycopg2.extensions

            original_execute = psycopg2.extensions.cursor.execute
            original_executemany = psycopg2.extensions.cursor.executemany
            original_connect = psycopg2.connect

            def patched_execute(self, query, vars=None):
                start = time.time()
                try:
                    result = original_execute(self, query, vars)
                    duration = (time.time() - start) * 1000

                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=vars,
                        result_count=self.rowcount if self.rowcount >= 0 else None,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=vars,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_executemany(self, query, vars_list):
                start = time.time()
                try:
                    result = original_executemany(self, query, vars_list)
                    duration = (time.time() - start) * 1000

                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        result_count=self.rowcount if self.rowcount >= 0 else None,
                        metadata={"batch_size": len(vars_list) if vars_list else 0},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_connect(*args, **kwargs):
                conn_start = time.time()
                try:
                    connection = original_connect(*args, **kwargs)
                    conn_duration = (time.time() - conn_start) * 1000

                    # Extract database info from connection string or kwargs
                    db_info = {}
                    if "dbname" in kwargs:
                        db_info["database"] = kwargs["dbname"]
                    if "host" in kwargs:
                        db_info["host"] = kwargs["host"]

                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        metadata=db_info,
                    )
                    return connection
                except Exception as e:
                    conn_duration = (time.time() - conn_start) * 1000
                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        status="failed",
                        error=str(e),
                    )
                    raise

            psycopg2.extensions.cursor.execute = patched_execute
            psycopg2.extensions.cursor.executemany = patched_executemany
            psycopg2.connect = patched_connect

            print("✅ PostgreSQL monitoring patched successfully")
        except ImportError:
            print("ℹ️  psycopg2 not installed, skipping PostgreSQL monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch PostgreSQL: {e}")
