_db_modules = {}


def _get_db_module(db_type: str):
    """Lazy load database modules"""
    if db_type not in _db_modules:
        if db_type == "mongodb":
            try:
                from pymongo import MongoClient

                _db_modules["mongodb"] = MongoClient
            except ImportError:
                raise ImportError(
                    "pymongo is required for MongoDB storage. Install with: pip install pymongo"
                )

        elif db_type == "mysql":
            try:
                import mysql.connector

                _db_modules["mysql"] = mysql.connector
            except ImportError:
                raise ImportError(
                    "mysql-connector-python is required for MySQL storage. Install with: pip install mysql-connector-python"
                )

        elif db_type == "postgresql":
            try:
                import psycopg2

                _db_modules["postgresql"] = psycopg2
            except ImportError:
                raise ImportError(
                    "psycopg2 is required for PostgreSQL storage. Install with: pip install psycopg2-binary"
                )

        elif db_type == "sqlite":
            import sqlite3

            _db_modules["sqlite"] = sqlite3

    return _db_modules[db_type]
