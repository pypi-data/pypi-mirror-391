import json
from abc import ABC, abstractmethod
from typing import Dict, Any


class LogStorage(ABC):
    """Abstract base class for log storage"""

    @abstractmethod
    def store_log(self, log_data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def cleanup_old_logs(self, days: int) -> int:
        pass

    @abstractmethod
    def close(self):
        pass
