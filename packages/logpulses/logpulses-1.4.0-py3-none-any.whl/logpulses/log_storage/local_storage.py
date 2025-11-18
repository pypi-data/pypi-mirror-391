import json, schedule, threading, time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
from logpulses.log_storage.base import LogStorage


class LocalFileStorage(LogStorage):
    def __init__(self, log_dir="logs", cleanup_days=7):
        self.log_dir = Path(log_dir)
        self.cleanup_days = cleanup_days
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._start_cleanup_scheduler()

    def _get_log_file_path(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"logs_{date_str}.jsonl"

    def store_log(self, log_data: Dict[str, Any]):
        try:
            with open(self._get_log_file_path(), "a", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False)
                f.write("\n")
            return True
        except Exception as e:
            print(f"❌ Failed to store log: {e}")
            return False

    def cleanup_old_logs(self, days=None):
        cleanup_days = days or self.cleanup_days
        cutoff = datetime.now() - timedelta(days=cleanup_days)
        deleted = 0

        for file in self.log_dir.glob("logs_*.jsonl"):
            try:
                date_str = file.stem.replace("logs_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff:
                    file.unlink()
                    deleted += 1
            except:
                pass

        return deleted

    def _start_cleanup_scheduler(self):
        def run():
            schedule.every().day.at("02:00").do(self.cleanup_old_logs)
            while True:
                schedule.run_pending()
                time.sleep(3600)

        threading.Thread(target=run, daemon=True).start()

    def close(self):
        pass
