"""In-memory index and diff helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from .connectors.base import RemoteEntry


@dataclass
class IndexEntry:
    path: str
    type: str
    size: int | None
    mtime: float | None
    unique: str | None

    @classmethod
    def from_remote(cls, entry: RemoteEntry) -> "IndexEntry":
        return cls(
            path=entry.path,
            type=entry.type,
            size=entry.size,
            mtime=entry.mtime,
            unique=entry.unique,
        )


class DirectoryIndex:
    """Tracks remote entries and surfaces create/delete/modify diffs."""

    def __init__(self) -> None:
        self._entries: Dict[str, IndexEntry] = {}

    def apply(self, entries: Iterable[RemoteEntry]) -> Tuple[
        list[RemoteEntry],
        list[IndexEntry],
        list[tuple[IndexEntry, RemoteEntry]],
    ]:
        new_entries = {entry.path: entry for entry in entries}
        created: list[RemoteEntry] = []
        deleted: list[IndexEntry] = []
        modified: list[tuple[IndexEntry, RemoteEntry]] = []

        for path, entry in new_entries.items():
            previous = self._entries.get(path)
            if previous is None:
                created.append(entry)
            elif self._is_modified(previous, entry):
                modified.append((previous, entry))

        for path, prev_entry in list(self._entries.items()):
            if path not in new_entries:
                deleted.append(prev_entry)

        self._entries = {path: IndexEntry.from_remote(entry) for path, entry in new_entries.items()}
        return created, deleted, modified

    @staticmethod
    def _is_modified(previous: IndexEntry, current: RemoteEntry) -> bool:
        return (
            previous.type != current.type
            or previous.size != current.size
            or previous.mtime != current.mtime
            or previous.unique != current.unique
        )

    def restore(self, entries: Iterable[IndexEntry]) -> None:
        self._entries = {entry.path: entry for entry in entries}

    def snapshot(self) -> list[IndexEntry]:
        return list(self._entries.values())


__all__ = ["DirectoryIndex", "IndexEntry"]
