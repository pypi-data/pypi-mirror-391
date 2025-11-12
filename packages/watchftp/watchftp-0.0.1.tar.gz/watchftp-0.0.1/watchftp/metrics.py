"""Prometheus metrics helpers for watchftp."""
from __future__ import annotations

import logging
from typing import Iterable

from prometheus_client import Counter, Gauge, Histogram, start_http_server

from .types import EventBatch

logger = logging.getLogger(__name__)

_SCAN_DURATION = Histogram(
    "watchftp_scan_duration_seconds",
    "Duration of directory scans",
    labelnames=("tenant", "root"),
)
_SCAN_ERRORS = Counter(
    "watchftp_scan_errors_total",
    "Total scan errors",
    labelnames=("tenant",),
)
_EVENTS_EMITTED = Counter(
    "watchftp_events_emitted_total",
    "Events emitted by type",
    labelnames=("tenant", "type"),
)
_QUEUE_DEPTH = Gauge(
    "watchftp_event_queue_depth",
    "Number of batches waiting in the watcher queue",
    labelnames=("tenant",),
)


def observe_scan(tenant: str, root: str, duration: float) -> None:
    _SCAN_DURATION.labels(tenant=tenant, root=root).observe(duration)


def record_scan_error(tenant: str) -> None:
    _SCAN_ERRORS.labels(tenant=tenant).inc()


def record_events(batch: EventBatch) -> None:
    if not batch:
        return
    tenant = batch[0].tenant_id or "default"
    for event in batch:
        _EVENTS_EMITTED.labels(tenant=tenant, type=event.type.value).inc()


def set_queue_depth(tenant: str, depth: int) -> None:
    _QUEUE_DEPTH.labels(tenant=tenant).set(depth)


def ensure_metrics_server(port: int = 9464, addr: str = "0.0.0.0") -> None:
    """Start the Prometheus HTTP server if not already running."""

    try:
        start_http_server(port, addr)
        logger.info("metrics_server_started", port=port, addr=addr)
    except OSError as exc:  # pragma: no cover - startup race
        logger.warning("metrics_server_start_failed", error=str(exc))


__all__ = [
    "observe_scan",
    "record_scan_error",
    "record_events",
    "set_queue_depth",
    "ensure_metrics_server",
]
