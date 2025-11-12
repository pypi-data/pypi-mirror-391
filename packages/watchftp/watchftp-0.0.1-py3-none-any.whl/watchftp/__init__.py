"""watchftp package exports."""
from __future__ import annotations

from importlib import metadata as _metadata

from .logging import configure_logging
from .metrics import ensure_metrics_server
from .settings import WatchConfig, WatchPath, WatcherSettings, tune_for_scale
from .types import ChangeEvent, EventType
from .watcher import Watcher

try:
    __version__ = _metadata.version("watchftp")
except _metadata.PackageNotFoundError:  # pragma: no cover - local dev
    __version__ = "0.0.0"

__all__ = [
    "WatchConfig",
    "WatchPath",
    "WatcherSettings",
    "Watcher",
    "ChangeEvent",
    "EventType",
    "configure_logging",
    "ensure_metrics_server",
    "tune_for_scale",
]
