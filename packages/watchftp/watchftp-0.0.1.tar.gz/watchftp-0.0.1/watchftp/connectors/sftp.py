"""SFTP connector using AsyncSSH."""
from __future__ import annotations

import asyncio
from typing import AsyncIterator

from ..settings import WatchConfig
from .base import Connector, RemoteEntry


class SFTPConnector(Connector):
    def __init__(self, config: WatchConfig):
        super().__init__(config)
        self._conn = None
        self._sftp = None
        self._dir_semaphore = asyncio.Semaphore(config.per_dir_concurrency)

    async def connect(self) -> None:  # pragma: no cover - network interaction
        if self._conn:
            return
        import asyncssh  # lazy import

        connect_kwargs = dict(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            client_keys=[self.config.private_key] if self.config.private_key else None,
            known_hosts=self.config.sftp_known_hosts,
        )
        if self.config.sftp_allowed_ciphers:
            connect_kwargs["encryption_algs"] = self.config.sftp_allowed_ciphers
        self._conn = await asyncssh.connect(**connect_kwargs)
        self._sftp = await self._conn.start_sftp_client()

    async def close(self) -> None:  # pragma: no cover - network interaction
        if self._sftp:
            self._sftp.exit()
            self._sftp = None
        if self._conn:
            self._conn.close()
            await self._conn.wait_closed()
            self._conn = None

    async def listdir(self, path: str) -> AsyncIterator[RemoteEntry]:  # pragma: no cover - network interaction
        if not self._sftp:
            raise RuntimeError("connector not connected")
        async with self._dir_semaphore:
            async for entry in self._sftp.scandir(path):
                attrs = entry.attrs
                yield RemoteEntry(
                    path=f"{path.rstrip('/')}/{entry.filename}" if path != "/" else f"/{entry.filename}",
                    type=_entry_type_from_attrs(attrs),
                    size=attrs.size,
                    mtime=getattr(attrs, "mtime", None),
                    unique=None,
                    perms=str(getattr(attrs, "permissions", "")) if hasattr(attrs, "permissions") else None,
                    metadata={"owner": getattr(attrs, "owner", None), "group": getattr(attrs, "group", None)},
                )

    def acquire_limit(self) -> asyncio.Semaphore:
        return self._dir_semaphore


def _entry_type_from_attrs(attrs) -> str:
    if attrs is None:
        return "file"
    if getattr(attrs, "permissions", 0) & 0o040000:
        return "dir"
    if getattr(attrs, "permissions", 0) & 0o120000:
        return "link"
    return "file"


__all__ = ["SFTPConnector"]
