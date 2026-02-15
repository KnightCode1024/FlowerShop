import time
from typing import Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
)

from entrypoint.config import config

APP_NAME = config.app.NAME

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of requests",
    ["method", "path", "handler", "status", "status_code", "app_name"],
)

HTTP_RESPONSES_TOTAL = Counter(
    "http_responses_total",
    "Total number of responses",
    ["status_code", "status", "path", "handler", "app_name"],
)

HTTP_EXCEPTIONS_TOTAL = Counter(
    "http_exceptions_total",
    "Total number of exceptions",
    ["path", "handler", "app_name"],
)

HTTP_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests in progress",
    ["path", "handler", "method", "app_name"],
)

HTTP_REQUESTS_DURATION = Histogram(
    "http_requests_duration_seconds",
    "Request duration in seconds (plural name)",
    ["path", "handler", "method", "app_name"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0, 2.5, 5, 10),
)

HTTP_REQUEST_DURATION_OLD = Histogram(
    "http_request_duration_seconds",
    "Request duration in seconds (singular / legacy name)",
    ["path", "handler", "method", "app_name"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0, 2.5, 5, 10),
)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        handler = path
        method = request.method
        labels = {
            "path": path,
            "handler": handler,
            "method": method,
            "app_name": APP_NAME,
        }

        HTTP_IN_PROGRESS.labels(**labels).inc()

        start = time.time()
        status_code = 500
        try:
            resp = await call_next(request)
            status_code = int(getattr(resp, "status_code", 500))
            return resp
        except Exception:
            HTTP_EXCEPTIONS_TOTAL.labels(path=path, handler=handler, app_name=APP_NAME).inc()
            raise
        finally:
            duration = time.time() - start
            status_code_str = str(status_code)
            status_class = f"{status_code // 100}xx" if isinstance(status_code, int) else status_code_str

            req_labels = {
                "method": method,
                "path": path,
                "handler": handler,
                "status": status_class,
                "status_code": status_code_str,
                "app_name": APP_NAME,
            }
            resp_labels = {
                "status_code": status_code_str,
                "status": status_class,
                "path": path,
                "handler": handler,
                "app_name": APP_NAME,
            }
            inprog_labels = {"path": path, "handler": handler, "method": method, "app_name": APP_NAME}
            hist_labels = {"path": path, "handler": handler, "method": method, "app_name": APP_NAME}

            try:
                HTTP_REQUESTS_TOTAL.labels(**req_labels).inc()
                HTTP_RESPONSES_TOTAL.labels(**resp_labels).inc()
                HTTP_REQUESTS_DURATION.labels(**hist_labels).observe(duration)
                HTTP_REQUEST_DURATION_OLD.labels(**hist_labels).observe(duration)
            finally:
                HTTP_IN_PROGRESS.labels(**inprog_labels).dec()
