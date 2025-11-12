"""FTP/FTPS connector using aioftp."""
from __future__ import annotations

import asyncio
import datetime as dt
from typing import AsyncIterator

import aioftp

from ..settings import WatchConfig
from .base import Connector, RemoteEntry


class FTPConnector(Connector):
    def __init__(self, config: WatchConfig):
        super().__init__(config)
        self._client: aioftp.Client | None = None
        self._dir_semaphore = asyncio.Semaphore(config.per_dir_concurrency)

    async def connect(self) -> None:  # pragma: no cover - network interaction
        if self._client:
            return
        self._client = aioftp.Client()
        await self._client.connect(self.config.host, self.config.port)
        await self._client.login(self.config.username, self.config.password)

    async def close(self) -> None:  # pragma: no cover - network interaction
        if self._client:
            await self._client.quit()
            self._client = None

    async def listdir(self, path: str) -> AsyncIterator[RemoteEntry]:  # pragma: no cover - network interaction
        if not self._client:
            raise RuntimeError("connector not connected")
        async with self._dir_semaphore:
            async for entry_path, info in self._client.list(path, recursive=False):
                facts = getattr(info, "facts", {}) or {}
                remote_path = str(entry_path)
                if not remote_path.startswith("/"):
                    remote_path = f"{path.rstrip('/')}/{remote_path}" if path != "/" else f"/{remote_path}"
                yield RemoteEntry(
                    path=remote_path,
                    type=facts.get("type", "file"),
                    size=_parse_optional_int(facts.get("size")),
                    mtime=_parse_mtime(facts.get("modify")),
                    unique=facts.get("unique"),
                    perms=facts.get("perm"),
                    metadata=facts,
                )

    def acquire_limit(self) -> asyncio.Semaphore:
        return self._dir_semaphore


def _parse_optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_mtime(value: str | None) -> float | None:
    if not value:
        return None
    try:
        # RFC 3659 format: YYYYMMDDHHMMSS[.sss]
        base = value.split(".")[0]
        dt_obj = dt.datetime.strptime(base, "%Y%m%d%H%M%S")
        return dt_obj.timestamp()
    except ValueError:
        return None


__all__ = ["FTPConnector"]
