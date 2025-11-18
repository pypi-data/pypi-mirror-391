import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal
from logpulses.db_monitor.base import DatabaseMonitor, safe_serialize


class SQLAlchemyMonitor(DatabaseMonitor):
    """SQLAlchemy ORM monitoring"""

    @staticmethod
    def patch_sqlalchemy():
        """Patch SQLAlchemy to track operations"""
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            @event.listens_for(Engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                context._query_start_time = time.time()

            @event.listens_for(Engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                duration = (time.time() - context._query_start_time) * 1000

                SQLAlchemyMonitor.log_operation(
                    db_type="SQLAlchemy",
                    operation="executemany" if executemany else "execute",
                    duration_ms=duration,
                    query=statement,
                    params=parameters,
                    result_count=cursor.rowcount if hasattr(cursor, "rowcount") else None,
                    metadata={"dialect": conn.dialect.name},
                )

            @event.listens_for(Engine, "connect")
            def connect(dbapi_conn, connection_record):
                connection_record._connected_at = time.time()

            @event.listens_for(Engine, "checkout")
            def checkout(dbapi_conn, connection_record, connection_proxy):
                if hasattr(connection_record, "_connected_at"):
                    conn_duration = (time.time() - connection_record._connected_at) * 1000
                    SQLAlchemyMonitor.log_operation(
                        db_type="SQLAlchemy",
                        operation="connection_checkout",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                    )

            print("✅ SQLAlchemy monitoring patched successfully")
        except ImportError:
            print("ℹ️  SQLAlchemy not installed, skipping SQLAlchemy monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch SQLAlchemy: {e}")
