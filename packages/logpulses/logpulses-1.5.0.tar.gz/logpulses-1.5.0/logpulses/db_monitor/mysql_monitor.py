import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal
from logpulses.db_monitor.base import DatabaseMonitor, safe_serialize


class MySQLMonitor(DatabaseMonitor):
    """MySQL monitoring with connection and query tracking"""

    @staticmethod
    def patch_mysql():
        """Patch MySQL connectors to track operations"""
        try:
            # Try mysql-connector-python
            import mysql.connector
            from mysql.connector import cursor as mysql_cursor

            original_execute = mysql_cursor.MySQLCursor.execute
            original_executemany = mysql_cursor.MySQLCursor.executemany
            original_connect = mysql.connector.connect

            def patched_execute(self, operation, params=None, multi=False):
                start = time.time()
                try:
                    result = original_execute(self, operation, params, multi)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="execute",
                        duration_ms=duration,
                        query=operation,
                        params=params,
                        result_count=self.rowcount if hasattr(self, "rowcount") else None,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="execute",
                        duration_ms=duration,
                        query=operation,
                        params=params,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_executemany(self, operation, seq_params):
                start = time.time()
                try:
                    result = original_executemany(self, operation, seq_params)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=operation,
                        result_count=self.rowcount if hasattr(self, "rowcount") else None,
                        metadata={"batch_size": len(list(seq_params)) if seq_params else 0},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=operation,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_connect(*args, **kwargs):
                conn_start = time.time()
                try:
                    connection = original_connect(*args, **kwargs)
                    conn_duration = (time.time() - conn_start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        metadata={
                            "host": kwargs.get("host", args[0] if args else "localhost"),
                            "database": kwargs.get("database", args[3] if len(args) > 3 else None),
                        },
                    )
                    return connection
                except Exception as e:
                    conn_duration = (time.time() - conn_start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        status="failed",
                        error=str(e),
                    )
                    raise

            mysql_cursor.MySQLCursor.execute = patched_execute
            mysql_cursor.MySQLCursor.executemany = patched_executemany
            mysql.connector.connect = patched_connect

            print("✅ MySQL (mysql-connector-python) monitoring patched successfully")
        except ImportError:
            pass

        try:
            # Try PyMySQL
            import pymysql
            import pymysql.cursors

            original_execute = pymysql.cursors.Cursor.execute
            original_executemany = pymysql.cursors.Cursor.executemany
            original_connect = pymysql.connect

            def patched_pymysql_execute(self, query, args=None):
                start = time.time()
                try:
                    result = original_execute(self, query, args)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=args,
                        result_count=self.rowcount,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=args,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_pymysql_executemany(self, query, args):
                start = time.time()
                try:
                    result = original_executemany(self, query, args)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        result_count=self.rowcount,
                        metadata={"batch_size": len(args) if args else 0},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_pymysql_connect(*args, **kwargs):
                conn_start = time.time()
                try:
                    connection = original_connect(*args, **kwargs)
                    conn_duration = (time.time() - conn_start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        metadata={
                            "host": kwargs.get("host", "localhost"),
                            "database": kwargs.get("database", kwargs.get("db")),
                        },
                    )
                    return connection
                except Exception as e:
                    conn_duration = (time.time() - conn_start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        status="failed",
                        error=str(e),
                    )
                    raise

            pymysql.cursors.Cursor.execute = patched_pymysql_execute
            pymysql.cursors.Cursor.executemany = patched_pymysql_executemany
            pymysql.connect = patched_pymysql_connect

            print("✅ MySQL (PyMySQL) monitoring patched successfully")
        except ImportError:
            pass
