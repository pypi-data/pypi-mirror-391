import json
from datetime import datetime, timedelta
from typing import Dict, Any
from logpulses.log_storage.base import LogStorage
from logpulses.log_storage.utils import _get_db_module


class MySQLStorage(LogStorage):
    """Store logs in MySQL with immediate cleanup (no scheduler)"""

    def __init__(self, connection_string: str, table_name: str = "logs", cleanup_days: int = 7):
        mysql = _get_db_module("mysql")

        conn_params = self._parse_connection_string(connection_string)
        self.conn = mysql.connect(**conn_params)
        self.table_name = table_name
        self.cleanup_days = cleanup_days

        # Create table if not exists
        self._create_table()

        # Run cleanup once when the storage is created
        try:
            deleted = self.cleanup_old_logs()
            print(f"🧹 Initial cleanup: deleted {deleted} old rows")
        except Exception as e:
            print(f"⚠️ Initial cleanup failed: {e}")

    def _parse_connection_string(self, conn_str: str) -> Dict:
        """Parse MySQL connection string (mysql://user:password@host:port/db)"""
        from urllib.parse import urlparse

        parsed = urlparse(conn_str)
        return {
            "host": parsed.hostname,
            "port": parsed.port or 3306,
            "user": parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip("/"),
        }

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                route VARCHAR(500),
                method VARCHAR(10),
                status_code INT,
                processing_time_ms FLOAT,
                log_data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at),
                INDEX idx_route (route),
                INDEX idx_status (status_code)
            )
            """
        )
        self.conn.commit()
        cursor.close()
        print(f"✅ MySQL table '{self.table_name}' ready")

    def store_log(self, log_data: Dict[str, Any]) -> bool:
        """Store log in MySQL & immediately clean old rows"""
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

            # 🔥 Immediately clean old logs
            try:
                self.cleanup_old_logs()
            except Exception as e:
                print(f"⚠️ Cleanup failed after insert: {e}")

            return True

        except Exception as e:
            print(f"❌ Failed to store log in MySQL: {e}")
            return False

    def cleanup_old_logs(self, days: int = None) -> int:
        """Delete logs older than the given number of days"""
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
            print(f"❌ Error during MySQL cleanup: {e}")
            return 0

    def close(self):
        """Close MySQL connection"""
        self.conn.close()
