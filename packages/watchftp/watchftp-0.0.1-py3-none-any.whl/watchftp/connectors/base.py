"""Connector interfaces for watchftp."""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Literal

from ..settings import WatchConfig

EntryType = Literal["file", "dir", "link", "other"]


@dataclass
class RemoteEntry:
    path: str
    type: EntryType
    size: int | None
    mtime: float | None
    unique: str | None = None
    perms: str | None = None
    metadata: dict[str, str] | None = None


class Connector(ABC):
    def __init__(self, config: WatchConfig):
        self.config = config

    def acquire_limit(self) -> asyncio.Semaphore | None:  # pragma: no cover - optional
        return None

    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    async def listdir(self, path: str) -> AsyncIterator[RemoteEntry]:
        ...

    async def stat(self, path: str) -> RemoteEntry | None:  # pragma: no cover - optional override
        raise NotImplementedError


__all__ = ["Connector", "RemoteEntry", "EntryType"]
