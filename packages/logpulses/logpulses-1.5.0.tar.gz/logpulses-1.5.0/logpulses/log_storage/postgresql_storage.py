import json
from datetime import datetime, timedelta
from typing import Dict, Any
from logpulses.log_storage.base import LogStorage
from logpulses.log_storage.utils import _get_db_module


class PostgreSQLStorage(LogStorage):
    """Store logs in PostgreSQL with immediate cleanup (no scheduler)."""

    def __init__(self, connection_string: str, table_name: str = "logs", cleanup_days: int = 7):
        psycopg2 = _get_db_module("postgresql")
        self.conn = psycopg2.connect(connection_string)
        self.table_name = table_name
        self.cleanup_days = cleanup_days

        # Create table if not exists
        self._create_table()

        # Initial cleanup at startup
        try:
            deleted = self.cleanup_old_logs()
            print(f"🧹 PostgreSQL startup cleanup deleted {deleted} rows")
        except Exception as e:
            print(f"⚠️ PostgreSQL startup cleanup failed: {e}")

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id BIGSERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                route VARCHAR(500),
                method VARCHAR(10),
                status_code INT,
                processing_time_ms FLOAT,
                log_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_created_at ON {self.table_name}(created_at)"
        )
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_route ON {self.table_name}(route)"
        )
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_status ON {self.table_name}(status_code)"
        )
        self.conn.commit()
        cursor.close()
        print(f"✅ PostgreSQL table '{self.table_name}' ready")

    def store_log(self, log_data: Dict[str, Any]) -> bool:
        """Insert log + immediately remove old logs."""
        try:
            cursor = self.conn.cursor()

            timestamp_str = log_data.get("timestamp")
            timestamp = (
                datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                if timestamp_str
                else datetime.now()
            )

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
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (timestamp, route, method, status_code, processing_time, json.dumps(log_data)),
            )

            self.conn.commit()
            cursor.close()

            # 🔥 Run cleanup immediately
            try:
                self.cleanup_old_logs()
            except Exception as e:
                print(f"⚠️ PostgreSQL cleanup failed after insert: {e}")

            return True

        except Exception as e:
            print(f"❌ Failed to store log in PostgreSQL: {e}")
            return False

    def cleanup_old_logs(self, days: int = None) -> int:
        """Delete rows older than X days."""
        cleanup_days = days or self.cleanup_days
        cutoff_date = datetime.now() - timedelta(days=cleanup_days)

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE created_at < %s",
                (cutoff_date,),
            )
            deleted_count = cursor.rowcount
            self.conn.commit()
            cursor.close()
            return deleted_count

        except Exception as e:
            print(f"❌ Error during PostgreSQL cleanup: {e}")
            return 0

    def close(self):
        """Close database connection."""
        self.conn.close()
