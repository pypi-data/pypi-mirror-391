import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal
from logpulses.db_monitor.base import DatabaseMonitor, safe_serialize


class MongoDBMonitor(DatabaseMonitor):
    """MongoDB monitoring with connection and query tracking"""

    @staticmethod
    def patch_pymongo():
        """Patch PyMongo to track operations automatically"""
        try:
            from pymongo import MongoClient
            from pymongo.collection import Collection

            # Store original methods
            original_find = Collection.find
            original_find_one = Collection.find_one
            original_insert_one = Collection.insert_one
            original_insert_many = Collection.insert_many
            original_update_one = Collection.update_one
            original_update_many = Collection.update_many
            original_delete_one = Collection.delete_one
            original_delete_many = Collection.delete_many
            original_aggregate = Collection.aggregate
            original_count_documents = Collection.count_documents

            # Patched methods
            def patched_find(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_find(self, *args, **kwargs)
                    # Materialize cursor to get count
                    result_list = list(result)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else kwargs.get("filter", {})),
                        result_count=len(result_list),
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    return iter(result_list)
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    raise

            def patched_find_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_find_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find_one",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else kwargs.get("filter", {})),
                        result_count=1 if result else 0,
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_insert_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_insert_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_one",
                        duration_ms=duration,
                        result_count=1,
                        metadata={"collection": self.name, "inserted_id": str(result.inserted_id)},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_insert_many(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_insert_many(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_many",
                        duration_ms=duration,
                        result_count=len(result.inserted_ids),
                        metadata={"collection": self.name, "count": len(result.inserted_ids)},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_many",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_update_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_update_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_one",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.modified_count,
                        metadata={"collection": self.name, "matched": result.matched_count},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_update_many(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_update_many(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_many",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.modified_count,
                        metadata={"collection": self.name, "matched": result.matched_count},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_many",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_delete_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_delete_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_one",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.deleted_count,
                        metadata={"collection": self.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_delete_many(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_delete_many(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_many",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.deleted_count,
                        metadata={"collection": self.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_many",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_aggregate(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_aggregate(self, *args, **kwargs)
                    result_list = list(result)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="aggregate",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else []),
                        result_count=len(result_list),
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    return iter(result_list)
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="aggregate",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_count_documents(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_count_documents(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="count_documents",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result,
                        metadata={"collection": self.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="count_documents",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            # Apply patches
            Collection.find = patched_find
            Collection.find_one = patched_find_one
            Collection.insert_one = patched_insert_one
            Collection.insert_many = patched_insert_many
            Collection.update_one = patched_update_one
            Collection.update_many = patched_update_many
            Collection.delete_one = patched_delete_one
            Collection.delete_many = patched_delete_many
            Collection.aggregate = patched_aggregate
            Collection.count_documents = patched_count_documents

            print("✅ MongoDB monitoring patched successfully")
        except ImportError:
            print("ℹ️  PyMongo not installed, skipping MongoDB monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch MongoDB: {e}")
