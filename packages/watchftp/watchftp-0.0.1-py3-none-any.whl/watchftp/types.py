"""Shared types for watchftp."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class EventType(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class ChangeEvent:
    id: str
    type: EventType
    path: str
    ts: float
    old: dict[str, Any] | None = None
    new: dict[str, Any] | None = None
    tenant_id: str | None = None


EventBatch = list[ChangeEvent]

__all__ = ["EventType", "ChangeEvent", "EventBatch"]
