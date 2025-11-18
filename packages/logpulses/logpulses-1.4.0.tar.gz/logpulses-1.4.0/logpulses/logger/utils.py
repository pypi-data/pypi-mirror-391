import json
import tracemalloc
from .encoders import CustomJSONEncoder


def print_log(log_data):
    print("\n" + "=" * 80)
    print(json.dumps(log_data, indent=2, ensure_ascii=False, cls=CustomJSONEncoder))
    print("=" * 80 + "\n")


def get_memory_usage_delta(start):
    try:
        snap = tracemalloc.take_snapshot()
        stats = snap.compare_to(start, "lineno")
        kb = sum(stat.size_diff for stat in stats) / 1024
        return f"{kb:.2f} KB" if kb > 0 else "< 1 KB"
    except:
        return "N/A"
