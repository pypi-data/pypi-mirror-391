import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal
from logpulses.db_monitor.base import DatabaseMonitor, safe_serialize


class RedisMonitor(DatabaseMonitor):
    """Redis monitoring"""

    @staticmethod
    def patch_redis():
        """Patch Redis to track operations"""
        try:
            import redis
            from redis.client import Redis

            # Store original methods
            original_methods = {}
            redis_commands = [
                "get",
                "set",
                "delete",
                "exists",
                "expire",
                "ttl",
                "hget",
                "hset",
                "hgetall",
                "hdel",
                "hincrby",
                "lpush",
                "rpush",
                "lpop",
                "rpop",
                "lrange",
                "sadd",
                "srem",
                "smembers",
                "sismember",
                "zadd",
                "zrem",
                "zrange",
                "zscore",
                "incr",
                "decr",
                "incrby",
                "decrby",
                "keys",
                "scan",
                "mget",
                "mset",
                "pipeline",
                "execute",
            ]

            def create_patched_method(method_name, original_method):
                def patched_method(self, *args, **kwargs):
                    start = time.time()
                    try:
                        result = original_method(self, *args, **kwargs)
                        duration = (time.time() - start) * 1000

                        RedisMonitor.log_operation(
                            db_type="Redis",
                            operation=method_name,
                            duration_ms=duration,
                            params={
                                "args": safe_serialize(args[:2]),
                                "kwargs": safe_serialize(kwargs),
                            },
                        )
                        return result
                    except Exception as e:
                        duration = (time.time() - start) * 1000
                        RedisMonitor.log_operation(
                            db_type="Redis",
                            operation=method_name,
                            duration_ms=duration,
                            status="failed",
                            error=str(e),
                        )
                        raise

                return patched_method

            # Patch all Redis commands
            for cmd in redis_commands:
                if hasattr(Redis, cmd):
                    original_methods[cmd] = getattr(Redis, cmd)
                    setattr(Redis, cmd, create_patched_method(cmd, original_methods[cmd]))

            print("✅ Redis monitoring patched successfully")
        except ImportError:
            print("ℹ️  Redis not installed, skipping Redis monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch Redis: {e}")
