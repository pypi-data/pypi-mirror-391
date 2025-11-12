"""Structured logging helpers."""
from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

_DEFAULT_LEVEL = os.getenv("WATCHFTP_LOG_LEVEL", "INFO").upper()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key in ("args", "levelname", "levelno", "msg", "name", "exc_info", "exc_text", "stack_info", "lineno", "pathname", "filename", "module", "funcName", "created", "msecs", "relativeCreated", "thread", "threadName", "process", "processName"):
                continue
            if key.startswith("_"):
                continue
            base[key] = value
        return json.dumps(base, default=str)


def configure_logging(level: str | None = None, *, structured: bool = True) -> None:
    """Configure watchftp loggers.

    Parameters
    ----------
    level: str | None
        Log level (defaults to WATCHFTP_LOG_LEVEL env or INFO).
    structured: bool
        When True, emit JSON logs; otherwise use standard formatting.
    """

    level = (level or _DEFAULT_LEVEL).upper()
    handler = logging.StreamHandler(stream=sys.stderr)
    if structured:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))

    root = logging.getLogger("watchftp")
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)


__all__ = ["configure_logging", "JsonFormatter"]
