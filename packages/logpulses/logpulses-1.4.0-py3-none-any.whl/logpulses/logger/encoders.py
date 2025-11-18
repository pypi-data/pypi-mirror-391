import json
from typing import Any
from logpulses.db_monitor import safe_serialize


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any):
        return safe_serialize(obj)
