from typing import Optional
from .local_storage import LocalFileStorage
from .mongodb_storage import MongoDBStorage
from .mysql_storage import MySQLStorage
from .postgresql_storage import PostgreSQLStorage
from .sqlite_storage import SQLiteStorage
from .base import LogStorage


def create_log_storage(
    storage_type: str, connection_string: Optional[str] = None, cleanup_days: int = 7, **kwargs
) -> LogStorage:

    storage_type = storage_type.lower()

    if storage_type == "local":
        return LocalFileStorage(kwargs.get("log_dir", "logs"), cleanup_days)

    if storage_type == "mongodb":
        return MongoDBStorage(
            connection_string,
            kwargs.get("database_name", "logs_db"),
            kwargs.get("collection_name", "logs"),
            cleanup_days,
        )

    if storage_type == "mysql":
        return MySQLStorage(connection_string, kwargs.get("table_name", "logs"), cleanup_days)

    if storage_type == "postgresql":
        return PostgreSQLStorage(connection_string, kwargs.get("table_name", "logs"), cleanup_days)

    if storage_type == "sqlite":
        return SQLiteStorage(
            kwargs.get("db_path", "logs.db"), kwargs.get("table_name", "logs"), cleanup_days
        )

    raise ValueError(f"Unknown storage type: {storage_type}")
