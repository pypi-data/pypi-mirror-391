import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
from logpulses.log_storage.base import LogStorage


class LocalFileStorage(LogStorage):
    """Local JSONL log storage — immediate cleanup on startup and after each write."""

    def __init__(self, log_dir: str = "logs", cleanup_days: int = 7):
        self.log_dir = Path(log_dir)
        self.cleanup_days = cleanup_days
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Run an immediate cleanup at startup
        try:
            deleted = self.cleanup_old_logs()
            if deleted:
                print(f"🧹 Startup cleanup removed {deleted} old log file(s)")
        except Exception as e:
            print(f"⚠️ Startup cleanup error: {e}")

    def _get_log_file_path(self) -> Path:
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"logs_{date_str}.jsonl"

    def store_log(self, log_data: Dict[str, Any]) -> bool:
        """Write a JSON line and immediately remove old log files."""
        try:
            log_file = self._get_log_file_path()
            with open(log_file, "a", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            print(f"❌ Failed to store log locally: {e}")
            return False

        # Immediately clean old logs after writing
        try:
            deleted = self.cleanup_old_logs()
            if deleted:
                print(f"🧹 Cleanup after write removed {deleted} old log file(s)")
        except Exception as e:
            print(f"⚠️ Cleanup after write error: {e}")

        return True

    def cleanup_old_logs(self, days: int = None) -> int:
        """Delete log files older than `days`. Returns number of deleted files."""
        cleanup_days = days or self.cleanup_days
        cutoff_date = (datetime.now() - timedelta(days=cleanup_days)).date()
        deleted_count = 0

        try:
            for log_file in self.log_dir.glob("logs_*.jsonl"):
                try:
                    date_str = log_file.stem.replace("logs_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                        print(f"🗑️ Deleted old log file: {log_file.name}")
                except ValueError:
                    # filename not matching expected format
                    continue
                except Exception as e:
                    print(f"⚠️ Error deleting {log_file.name}: {e}")
                    continue

            return deleted_count
        except Exception as e:
            print(f"❌ Error during log cleanup: {e}")
            return deleted_count

    def close(self):
        """No persistent resources to close for file storage."""
        pass
