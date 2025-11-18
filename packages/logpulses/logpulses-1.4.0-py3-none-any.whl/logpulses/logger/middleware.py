import json
import time
import platform
import tracemalloc
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse

# DB Monitor
from logpulses.db_monitor import db_operations, initialize_db_monitoring

# Storage
from logpulses.log_storage import create_log_storage, LogStorage

# Split modules
from .utils import print_log, get_memory_usage_delta
from .system_info import get_system_metrics, get_active_network_info, get_device_id
from .encoders import CustomJSONEncoder
from .request_parser import parse_request_body
from .error_handler import categorize_error, create_error_response
from starlette.requests import Request
from typing import Optional


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Universal middleware that logs ALL requests automatically with DB monitoring and storage.

    ✅ NO DECORATORS NEEDED!
    ✅ Automatically detects and tracks DB operations
    ✅ Supports MongoDB, MySQL, PostgreSQL, SQLAlchemy, Redis, Cassandra
    ✅ Tracks connection time and query execution time
    ✅ Works with all HTTP methods
    ✅ Supports log storage (local files, databases)
    ✅ Automatic log cleanup
    """

    def __init__(
        self,
        app,
        exclude_paths: list = None,
        enable_db_monitoring: bool = True,
        storage_type: Optional[str] = None,
        connection_string: Optional[str] = None,
        cleanup_days: int = 7,
        print_logs: bool = True,
        **storage_kwargs,
    ):
        """
        Initialize middleware with optional log storage.

        Args:
            app: FastAPI/Starlette app
            exclude_paths: List of paths to exclude from logging
            enable_db_monitoring: Enable database operation monitoring
            storage_type: Type of storage ('local', 'mongodb', 'mysql', 'postgresql', 'sqlite', None)
            connection_string: Database connection string (required for db storage)
            cleanup_days: Days after which to delete old logs (default: 7)
            print_logs: Whether to print logs to console (default: True)
            **storage_kwargs: Additional storage-specific arguments

        Examples:
            # Console logging only (default)
            app.add_middleware(RequestLoggingMiddleware)

            # Local file storage
            app.add_middleware(
                RequestLoggingMiddleware,
                storage_type='local',
                cleanup_days=7,
                log_dir='logs'
            )

            # MongoDB storage
            app.add_middleware(
                RequestLoggingMiddleware,
                storage_type='mongodb',
                connection_string='mongodb://localhost:27017',
                database_name='logs_db',
                cleanup_days=30
            )

            # MySQL storage
            app.add_middleware(
                RequestLoggingMiddleware,
                storage_type='mysql',
                connection_string='mysql://user:pass@localhost:3306/logs_db',
                cleanup_days=7
            )

            # PostgreSQL storage
            app.add_middleware(
                RequestLoggingMiddleware,
                storage_type='postgresql',
                connection_string='postgresql://user:pass@localhost:5432/logs_db',
                cleanup_days=14
            )

            # SQLite storage
            app.add_middleware(
                RequestLoggingMiddleware,
                storage_type='sqlite',
                db_path='logs.db',
                cleanup_days=7
            )
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.print_logs = print_logs
        self.storage: Optional[LogStorage] = None

        # Initialize database monitoring patches
        if enable_db_monitoring:
            try:
                initialize_db_monitoring()
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize database monitoring: {e}")

        # Initialize log storage if specified
        if storage_type:
            try:
                self.storage = create_log_storage(
                    storage_type=storage_type,
                    connection_string=connection_string,
                    cleanup_days=cleanup_days,
                    **storage_kwargs,
                )
                print(
                    f"✅ Log storage initialized: {storage_type.upper()} (cleanup: {cleanup_days} days)"
                )
            except Exception as e:
                print(f"❌ Failed to initialize log storage: {e}")
                print(f"⚠️  Falling back to console logging only")

    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Reset DB operations for this request
        db_operations.set([])

        # Start tracking
        tracemalloc.start()
        mem_snapshot = tracemalloc.take_snapshot()
        start_time = time.time()

        # Capture request info
        route_path = request.url.path
        method = request.method
        full_url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Cache request body
        body_bytes = await request.body()
        request_body_for_log = None
        body_size = len(body_bytes)

        # Parse request body for logging
        query_params = dict(request.query_params)
        query_string = str(request.url.query) if request.url.query else ""
        query_size = len(query_string.encode("utf-8")) if query_string else 0

        # Calculate total request size
        request_size = body_size + query_size

        # Build comprehensive request data structure
        request_data = {}

        # Handle request body for methods that typically have bodies
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            if body_bytes:
                try:
                    request_data["body"] = json.loads(body_bytes)
                except json.JSONDecodeError:
                    request_data["body"] = body_bytes.decode("utf-8", errors="replace")[:500]

            if query_params:
                request_data["queryParams"] = query_params

            if not request_data:
                request_body_for_log = "No body or query parameters"
            else:
                request_body_for_log = request_data

        # Handle GET and HEAD methods
        elif method in ("GET", "HEAD"):
            if query_params:
                request_body_for_log = {"queryParams": query_params}
            else:
                request_body_for_log = "No query parameters"

        # Handle other methods
        else:
            if body_bytes:
                try:
                    request_data["body"] = json.loads(body_bytes)
                except json.JSONDecodeError:
                    request_data["body"] = body_bytes.decode("utf-8", errors="replace")[:500]

            if query_params:
                request_data["queryParams"] = query_params

            if request_data:
                request_body_for_log = request_data
            else:
                request_body_for_log = "No data"

        # Response tracking
        status_code = 500
        response_body = None
        response_size = 0
        error_details = None

        try:
            # Call the next middleware/endpoint
            response = await call_next(request)
            status_code = response.status_code

            # Try to capture response body
            response_body_list = []
            async for chunk in response.body_iterator:
                response_body_list.append(chunk)

            response_body_bytes = b"".join(response_body_list)
            response_size = len(response_body_bytes)

            # Parse response body
            try:
                response_body = json.loads(response_body_bytes) if response_body_bytes else None
            except json.JSONDecodeError:
                response_body = response_body_bytes.decode("utf-8", errors="replace")
                if len(response_body) > 1000:
                    response_body = response_body[:1000] + "... (truncated)"

            # If response indicates an error, capture it
            if status_code >= 400:
                error_details = {
                    "statusCode": status_code,
                    "type": "HTTP Error",
                    "message": (
                        response_body
                        if isinstance(response_body, str)
                        else (
                            response_body.get("detail", "Unknown error")
                            if isinstance(response_body, dict)
                            else "Error occurred"
                        )
                    ),
                    "responseBody": response_body,
                }

            # Recreate response with the captured body
            from starlette.responses import Response as StarletteResponse

            response = StarletteResponse(
                content=response_body_bytes,
                status_code=status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as e:
            import traceback

            # Determine status code based on exception type
            if hasattr(e, "status_code"):
                status_code = e.status_code
            elif isinstance(e, ValueError):
                status_code = 400
            elif isinstance(e, KeyError):
                status_code = 400
            elif isinstance(e, TypeError):
                status_code = 400
            elif isinstance(e, PermissionError):
                status_code = 403
            elif isinstance(e, FileNotFoundError):
                status_code = 404
            elif isinstance(e, TimeoutError):
                status_code = 504
            elif isinstance(e, ConnectionError):
                status_code = 503
            else:
                status_code = 500

            error_details = {
                "type": type(e).__name__,
                "message": str(e),
                "statusCode": status_code,
                "traceback": traceback.format_exc(),
                "failurePoint": "Request processing",
                "exceptionModule": type(e).__module__,
                "hasStatusCode": hasattr(e, "status_code"),
            }

            # Create error response
            error_response_body = {
                "error": type(e).__name__,
                "detail": str(e),
                "statusCode": status_code,
            }

            response = Response(
                content=json.dumps(error_response_body),
                status_code=status_code,
                media_type="application/json",
            )

        finally:
            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000
            memory_used = get_memory_usage_delta(mem_snapshot)
            tracemalloc.stop()

            # Get DB operations
            db_ops = db_operations.get()

            # Calculate DB statistics
            db_stats = None
            if db_ops:
                total_db_time = sum(
                    float(op["duration_ms"]) for op in db_ops if "duration_ms" in op
                )
                db_types = list(set(op["type"] for op in db_ops))
                failed_ops = [op for op in db_ops if op.get("status") == "failed"]

                # Group operations by type
                operations_by_type = {}
                for op in db_ops:
                    db_type = op.get("type", "Unknown")
                    if db_type not in operations_by_type:
                        operations_by_type[db_type] = []
                    operations_by_type[db_type].append(op)

                # Calculate connection time statistics
                connection_ops = [op for op in db_ops if "connection_time_ms" in op]
                total_connection_time = sum(
                    float(op["connection_time_ms"]) for op in connection_ops
                )

                db_stats = {
                    "totalOperations": len(db_ops),
                    "totalDuration": f"{total_db_time:.2f} ms",
                    "totalConnectionTime": (
                        f"{total_connection_time:.2f} ms" if connection_ops else "0 ms"
                    ),
                    "databaseTypes": db_types,
                    "operationsByType": {
                        db_type: {
                            "count": len(ops),
                            "totalDuration": f"{sum(float(op['duration_ms']) for op in ops):.2f} ms",
                            "operations": ops,
                        }
                        for db_type, ops in operations_by_type.items()
                    },
                    "failedOperations": len(failed_ops),
                    "percentageOfRequestTime": f"{(total_db_time / processing_time * 100):.1f}%",
                }

                if failed_ops:
                    db_stats["failedOperationsDetails"] = failed_ops

            # Build log
            log_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "request": {
                    "route": route_path,
                    "method": method,
                    "fullUrl": full_url,
                    "clientIp": client_ip,
                    "userAgent": user_agent,
                    "size": (
                        {
                            "total": f"{request_size} bytes",
                            "body": f"{body_size} bytes",
                            "queryParams": f"{query_size} bytes",
                        }
                        if query_size > 0
                        else f"{request_size} bytes"
                    ),
                    "body": request_body_for_log,
                },
                "response": {
                    "status": status_code,
                    "success": status_code < 400,
                    "size": f"{response_size} bytes",
                    "body": (response_body if response_size < 5000 else "<response too large>"),
                },
                "performance": {
                    "processingTime": f"{processing_time:.2f} ms",
                    "memoryUsed": memory_used,
                },
                "system": get_system_metrics(),
                "network": get_active_network_info(),
                "server": {
                    "instanceId": get_device_id(),
                    "platform": platform.system(),
                    "hostname": platform.node(),
                },
            }

            # Add database stats if any DB operations occurred
            if db_stats:
                log_data["database"] = db_stats

            # Add error details if request failed
            if error_details:
                log_data["error"] = error_details
                log_data["failureAnalysis"] = {
                    "statusCode": status_code,
                    "category": self._categorize_error(status_code),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

            # Print logs to console if enabled
            if self.print_logs:
                print_log(log_data)

            # Store logs if storage is configured
            if self.storage:
                try:
                    self.storage.store_log(log_data)
                except Exception as e:
                    print(f"⚠️  Warning: Failed to store log: {e}")

        return response

    def _categorize_error(self, status_code):
        """Categorize error based on status code"""
        error_categories = {
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access denied",
            404: "Not Found - Resource doesn't exist",
            405: "Method Not Allowed - HTTP method not supported",
            408: "Request Timeout - Client took too long",
            409: "Conflict - Resource state conflict",
            410: "Gone - Resource permanently deleted",
            413: "Payload Too Large - Request body too big",
            415: "Unsupported Media Type - Invalid content type",
            422: "Unprocessable Entity - Validation error",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - Application error",
            501: "Not Implemented - Feature not available",
            502: "Bad Gateway - Upstream server error",
            503: "Service Unavailable - Server overloaded",
            504: "Gateway Timeout - Request timeout",
        }

        if status_code in error_categories:
            return error_categories[status_code]

        if 400 <= status_code < 500:
            return "Client Error - Request issue"
        elif 500 <= status_code < 600:
            return "Server Error - Backend issue"
        else:
            return "Unknown Error"

    def __del__(self):
        """Cleanup storage connection on middleware destruction"""
        if self.storage:
            try:
                self.storage.close()
            except Exception:
                pass
