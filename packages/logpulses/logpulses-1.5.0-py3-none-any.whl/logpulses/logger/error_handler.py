import json
from starlette.responses import Response


ERROR_MAP = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    413: "Payload Too Large",
    415: "Unsupported Media Type",
    422: "Validation Error",
    429: "Rate Limit Exceeded",
    500: "Internal Server Error",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}


def categorize_error(status_code):
    if status_code in ERROR_MAP:
        return ERROR_MAP[status_code]
    if 400 <= status_code < 500:
        return "Client Error"
    if 500 <= status_code < 600:
        return "Server Error"
    return "Unknown Error"


def create_error_response(e, status_code):
    body = {
        "error": type(e).__name__,
        "detail": str(e),
        "statusCode": status_code,
    }
    return Response(
        content=json.dumps(body),
        status_code=status_code,
        media_type="application/json",
    )
