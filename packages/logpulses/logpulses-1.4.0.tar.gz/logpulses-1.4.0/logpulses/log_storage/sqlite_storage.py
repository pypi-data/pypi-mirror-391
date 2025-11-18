import json
from datetime import datetime, timedelta
from typing import Dict, Any
from logpulses.log_storage.base import LogStorage
from logpulses.log_storage.utils import _get_db_module


class SQLiteStorage(LogStorage):
    """Store logs in SQLite with immediate cleanup (no scheduler)."""

    def __init__(self, db_path: str = "logs.db", table_name: str = "logs", cleanup_days: int = 7):
        sqlite3 = _get_db_module("sqlite")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.table_name = table_name
        self.cleanup_days = cleanup_days

        # Create table if not exists
        self._create_table()

        # Perform immediate cleanup on startup
        try:
            deleted = self.cleanup_old_logs()
            print(f"🧹 SQLite startup cleanup deleted {deleted} rows")
        except Exception as e:
            print(f"⚠️ SQLite startup cleanup failed: {e}")

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                route TEXT,
                method TEXT,
                status_code INTEGER,
                processing_time_ms REAL,
                log_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_created_at ON {self.table_name}(created_at)"
        )
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_route ON {self.table_name}(route)"
        )
        self.conn.commit()
        cursor.close()
        print(f"✅ SQLite table '{self.table_name}' ready")

    def store_log(self, log_data: Dict[str, Any]) -> bool:
        """Store log in SQLite and immediately clean old records."""
        try:
            cursor = self.conn.cursor()

            timestamp = log_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            route = log_data.get("request", {}).get("route", "")
            method = log_data.get("request", {}).get("method", "")
            status_code = log_data.get("response", {}).get("status", 0)

            processing_time = float(
                log_data.get("performance", {}).get("processingTime", "0").replace(" ms", "")
            )

            cursor.execute(
                f"""
                INSERT INTO {self.table_name}
                (timestamp, route, method, status_code, processing_time_ms, log_data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (timestamp, route, method, status_code, processing_time, json.dumps(log_data)),
            )

            self.conn.commit()
            cursor.close()

            # 🔥 Immediately clean old logs
            try:
                self.cleanup_old_logs()
            except Exception as e:
                print(f"⚠️ SQLite cleanup failed after insert: {e}")

            return True

        except Exception as e:
            print(f"❌ Failed to store log in SQLite: {e}")
            return False

    def cleanup_old_logs(self, days: int = None) -> int:
        """Delete logs older than X days."""
        cleanup_days = days or self.cleanup_days
        cutoff = (datetime.now() - timedelta(days=cleanup_days)).strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE created_at < ?",
                (cutoff,),
            )
            deleted_count = cursor.rowcount
            self.conn.commit()
            cursor.close()
            return deleted_count

        except Exception as e:
            print(f"❌ Error during SQLite cleanup: {e}")
            return 0

    def close(self):
        """Close SQLite connection"""
        self.conn.close()
