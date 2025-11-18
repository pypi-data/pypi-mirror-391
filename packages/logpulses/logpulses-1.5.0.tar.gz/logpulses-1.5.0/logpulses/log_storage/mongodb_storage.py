from datetime import datetime, timedelta
from typing import Dict, Any
from logpulses.log_storage.base import LogStorage
from pymongo import MongoClient


class MongoDBStorage(LogStorage):
    """MongoDB storage with immediate cleanup on every log write."""

    def __init__(
        self,
        connection_string: str,
        database_name: str = "logs_db",
        collection_name: str = "logs",
        cleanup_days: int = 7,
    ):
        self.client = MongoClient(connection_string)
        self.collection = self.client[database_name][collection_name]
        self.cleanup_days = cleanup_days

        # Create TTL index (optional but helpful)
        self._create_ttl_index()

        # Immediate cleanup on startup
        try:
            deleted = self.cleanup_old_logs()
            print(f"🧹 MongoDB startup cleanup deleted: {deleted} documents")
        except Exception as e:
            print(f"⚠️ MongoDB startup cleanup failed: {e}")

    def _create_ttl_index(self):
        """Create TTL index for MongoDB auto-expiration"""
        try:
            self.collection.create_index(
                "created_at", expireAfterSeconds=self.cleanup_days * 86400  # 86400 = 1 day
            )
        except Exception as e:
            print(f"⚠️ Could not create TTL index: {e}")

    def store_log(self, log_data: Dict[str, Any]):
        """Insert log + immediately clean older logs"""
        try:
            log_data["created_at"] = datetime.now()

            self.collection.insert_one(log_data)

            # 🔥 Immediate cleanup after inserting log
            try:
                self.cleanup_old_logs()
            except Exception as e:
                print(f"⚠️ MongoDB cleanup failed after insert: {e}")

            return True

        except Exception as e:
            print(f"❌ MongoDB Error: {e}")
            return False

    def cleanup_old_logs(self, days: int = None):
        """Delete logs older than X days (immediate cleanup)"""
        days = days or self.cleanup_days
        cutoff = datetime.now() - timedelta(days=days)

        try:
            result = self.collection.delete_many({"created_at": {"$lt": cutoff}})
            return result.deleted_count
        except Exception as e:
            print(f"❌ Error during MongoDB cleanup: {e}")
            return 0

    def close(self):
        self.client.close()
