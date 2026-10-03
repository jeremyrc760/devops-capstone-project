"""Prometheus instrumentation for the Accounts API."""
from contextlib import contextmanager
from time import perf_counter

from flask import g, request
from prometheus_client import Counter, Gauge, Histogram, Info, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware


HTTP_REQUESTS = Counter(
    "accounts_http_requests_total",
    "Total Accounts API HTTP requests.",
    ("method", "route", "status_code"),
)
HTTP_REQUEST_DURATION = Histogram(
    "accounts_http_request_duration_seconds",
    "Accounts API HTTP request duration in seconds.",
    ("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "accounts_http_requests_in_progress",
    "Accounts API HTTP requests currently being processed.",
    ("method", "route"),
)
ACCOUNT_OPERATIONS = Counter(
    "accounts_operations_total",
    "Total Accounts API business operations.",
    ("operation", "outcome"),
)
DB_OPERATION_DURATION = Histogram(
    "accounts_db_operation_duration_seconds",
    "Accounts database operation duration in seconds.",
    ("operation",),
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5),
)
DB_ERRORS = Counter(
    "accounts_db_errors_total",
    "Total Accounts database operation errors.",
    ("operation",),
)
SERVICE_INFO = Info(
    "accounts_service",
    "Accounts API build information.",
)

EXCLUDED_PATHS = {"/health", "/metrics"}
ENDPOINT_OPERATIONS = {
    "create_accounts": "create",
    "list_accounts": "list",
    "get_accounts": "read",
    "update_accounts": "update",
    "delete_accounts": "delete",
}


def _request_route():
    """Return a bounded route label instead of a raw URL containing IDs."""
    if request.url_rule is None:
        return "unmatched"
    return request.url_rule.rule


def _operation_outcome(status_code):
    if 200 <= status_code < 300:
        return "success"
    if status_code == 404:
        return "not_found"
    if 400 <= status_code < 500:
        return "client_error"
    return "server_error"


def _start_request_metrics():
    if request.path in EXCLUDED_PATHS:
        return

    route = _request_route()
    method = request.method
    g.accounts_metrics = {
        "method": method,
        "route": route,
        "operation": ENDPOINT_OPERATIONS.get(request.endpoint),
        "start_time": perf_counter(),
        "in_progress": True,
    }
    HTTP_REQUESTS_IN_PROGRESS.labels(method=method, route=route).inc()


def _record_request_metrics(status_code):
    metrics = getattr(g, "accounts_metrics", None)
    if not metrics or not metrics["in_progress"]:
        return

    method = metrics["method"]
    route = metrics["route"]
    duration = perf_counter() - metrics["start_time"]

    HTTP_REQUESTS.labels(
        method=method,
        route=route,
        status_code=str(status_code),
    ).inc()
    HTTP_REQUEST_DURATION.labels(method=method, route=route).observe(duration)
    HTTP_REQUESTS_IN_PROGRESS.labels(method=method, route=route).dec()
    metrics["in_progress"] = False

    operation = metrics["operation"]
    if operation:
        ACCOUNT_OPERATIONS.labels(
            operation=operation,
            outcome=_operation_outcome(status_code),
        ).inc()


def _finish_request_metrics(response):
    _record_request_metrics(response.status_code)
    return response


def _cleanup_request_metrics(error):
    if error is not None:
        _record_request_metrics(500)


def init_metrics(app):
    """Register request instrumentation and mount the Prometheus endpoint."""
    if app.extensions.get("accounts_prometheus_metrics"):
        return

    SERVICE_INFO.info({"version": "1.0"})
    app.before_request(_start_request_metrics)
    app.after_request(_finish_request_metrics)
    app.teardown_request(_cleanup_request_metrics)
    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app,
        {"/metrics": make_wsgi_app()},
    )
    app.extensions["accounts_prometheus_metrics"] = True


@contextmanager
def observe_database_operation(operation):
    """Measure a database operation and count failures without swallowing them."""
    start_time = perf_counter()
    try:
        yield
    except Exception:
        DB_ERRORS.labels(operation=operation).inc()
        raise
    finally:
        DB_OPERATION_DURATION.labels(operation=operation).observe(
            perf_counter() - start_time
        )
