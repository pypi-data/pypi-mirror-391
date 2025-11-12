"""Event construction helpers."""
from __future__ import annotations

import itertools
import time
from typing import Iterable

from .connectors.base import RemoteEntry
from .index import IndexEntry
from .types import ChangeEvent, EventBatch, EventType

_event_counter = itertools.count()


def _next_event_id(prefix: str) -> str:
    return f"{prefix}-{next(_event_counter)}"


def _serialize_entry(entry: RemoteEntry | IndexEntry) -> dict[str, object]:
    payload = {
        "type": entry.type,
        "size": entry.size,
        "mtime": entry.mtime,
    }
    if getattr(entry, "unique", None):
        payload["unique"] = entry.unique
    return payload


def build_events(
    created: Iterable[RemoteEntry],
    deleted: Iterable[IndexEntry],
    modified: Iterable[tuple[IndexEntry, RemoteEntry]],
    *,
    tenant_id: str,
) -> EventBatch:
    ts = time.time()
    events: EventBatch = []

    for entry in created:
        events.append(
            ChangeEvent(
                id=_next_event_id("c"),
                type=EventType.CREATED,
                path=entry.path,
                ts=ts,
                old=None,
                new=_serialize_entry(entry),
                tenant_id=tenant_id,
            )
        )

    for entry in deleted:
        events.append(
            ChangeEvent(
                id=_next_event_id("d"),
                type=EventType.DELETED,
                path=entry.path,
                ts=ts,
                old=_serialize_entry(entry),
                new=None,
                tenant_id=tenant_id,
            )
        )

    for prev_entry, new_entry in modified:
        events.append(
            ChangeEvent(
                id=_next_event_id("m"),
                type=EventType.MODIFIED,
                path=new_entry.path,
                ts=ts,
                old=_serialize_entry(prev_entry),
                new=_serialize_entry(new_entry),
                tenant_id=tenant_id,
            )
        )

    return events


__all__ = ["build_events"]
