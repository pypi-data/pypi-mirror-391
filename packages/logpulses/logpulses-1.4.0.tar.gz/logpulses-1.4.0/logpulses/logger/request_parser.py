import json


def parse_request_body(method, body_bytes, query_params):
    request_data = {}

    if method in ("POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
        if body_bytes:
            try:
                request_data["body"] = json.loads(body_bytes)
            except:
                request_data["body"] = body_bytes.decode("utf-8", "replace")[:500]
        if query_params:
            request_data["queryParams"] = query_params

    elif method in ("GET", "HEAD"):
        if query_params:
            request_data["queryParams"] = query_params
        else:
            return "No query parameters"

    return request_data or "No data"
