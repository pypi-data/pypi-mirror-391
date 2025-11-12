"""Redis helpers and stream publisher."""
from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import quote

from .connectors.base import RemoteEntry
from .index import IndexEntry
from .settings import WatchConfig
from .types import EventBatch

REDIS_KEY_PREFIX = "wf"


def _encode_path(path: str) -> str:
    return quote(path, safe="")


@dataclass
class RedisNamespace:
    tenant_id: str
    server_id: str

    @classmethod
    def from_config(cls, config: WatchConfig) -> "RedisNamespace":
        server_id = f"{config.protocol}:{config.host}:{config.port}"
        return cls(tenant_id=config.tenant_id, server_id=server_id)

    @property
    def base(self) -> str:
        return f"{REDIS_KEY_PREFIX}:{self.tenant_id}:{self.server_id}"

    def entry_key(self, path: str) -> str:
        return f"{self.base}:entry:{_encode_path(path)}"

    def dir_key(self, path: str) -> str:
        return f"{self.base}:dir:{_encode_path(path)}"

    def scan_key(self) -> str:
        return f"{self.base}:scan"

    def stream_name(self) -> str:
        return f"{REDIS_KEY_PREFIX}:{self.tenant_id}:stream:{self.server_id}"

    def hotness_key(self) -> str:
        return f"{self.base}:hot"


def require_redis(config: WatchConfig) -> None:
    if not config.redis_enabled:
        raise ValueError("Redis is not configured but Redis-only feature was requested")
    if not config.tenant_id:
        raise ValueError("tenant_id is required for Redis operations")
    if not config.redis_url:
        raise ValueError("redis_url must be set to use Redis features")


class RedisStreamsSink:
    """Publishes events to a tenant-scoped Redis Stream."""

    def __init__(self, config: WatchConfig):
        require_redis(config)
        import redis.asyncio as redis_async  # lazy import

        self._config = config
        self._namespace = RedisNamespace.from_config(config)
        redis_url = str(config.redis_url)
        self._redis = redis_async.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=False,
        )
        self._stream = self._namespace.stream_name()
        self._ttl = config.redis_ttl_seconds
        self._ttl_applied = False

    async def start(self) -> None:
        await self._redis.ping()

    async def stop(self) -> None:
        await self._redis.aclose()

    async def publish(self, batch: EventBatch) -> None:
        if not batch:
            return
        pipe = self._redis.pipeline()
        for event in batch:
            fields = {
                b"type": event.type.value.encode(),
                b"path": event.path.encode(),
                b"ts": f"{event.ts:.6f}".encode(),
            }
            if event.old:
                fields[b"old"] = json.dumps(event.old, separators=(",", ":")).encode()
            if event.new:
                fields[b"new"] = json.dumps(event.new, separators=(",", ":")).encode()
            if event.tenant_id:
                fields[b"tenant"] = event.tenant_id.encode()
            pipe.xadd(self._stream, fields)
        if not self._ttl_applied:
            pipe.expire(self._stream, self._ttl)
            self._ttl_applied = True
        await pipe.execute()


class RedisIndexStore:
    """Persists directory entries and scan metadata in Redis."""

    def __init__(self, config: WatchConfig):
        require_redis(config)
        import redis.asyncio as redis_async  # lazy import

        self._config = config
        self._namespace = RedisNamespace.from_config(config)
        self._entries_index_key = f"{self._namespace.base}:entries"
        self._hotness_key = self._namespace.hotness_key()
        redis_url = str(config.redis_url)
        self._redis = redis_async.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def start(self) -> None:
        await self._redis.ping()

    async def stop(self) -> None:
        await self._redis.aclose()

    async def clear(self) -> None:
        keys = await self._redis.smembers(self._entries_index_key)
        if keys:
            entry_keys = [self._namespace.entry_key(path) for path in keys]
            await self._redis.delete(*entry_keys)
        await self._redis.delete(self._entries_index_key)
        await self._redis.delete(self._hotness_key)

    async def load_index(self) -> list[IndexEntry]:
        paths = await self._redis.smembers(self._entries_index_key)
        if not paths:
            return []
        pipe = self._redis.pipeline()
        for path in paths:
            pipe.get(self._namespace.entry_key(path))
        raw_entries = await pipe.execute()
        entries: list[IndexEntry] = []
        for payload in raw_entries:
            if not payload:
                continue
            data = json.loads(payload)
            entries.append(IndexEntry(**data))
        return entries

    async def persist(
        self,
        created: list[RemoteEntry],
        deleted: list[IndexEntry],
        modified: list[tuple[IndexEntry, RemoteEntry]],
    ) -> None:
        if not (created or deleted or modified):
            return
        pipe = self._redis.pipeline()
        for entry in created:
            index_entry = IndexEntry.from_remote(entry)
            pipe.set(self._namespace.entry_key(entry.path), json.dumps(index_entry.__dict__))
            pipe.sadd(self._entries_index_key, entry.path)
        for prev_entry in deleted:
            pipe.delete(self._namespace.entry_key(prev_entry.path))
            pipe.srem(self._entries_index_key, prev_entry.path)
        for _, new_entry in modified:
            index_entry = IndexEntry.from_remote(new_entry)
            pipe.set(self._namespace.entry_key(new_entry.path), json.dumps(index_entry.__dict__))
            pipe.sadd(self._entries_index_key, new_entry.path)
        await pipe.execute()

    async def load_hotness(self) -> dict[str, float]:
        if not await self._redis.exists(self._hotness_key):
            return {}
        entries = await self._redis.zrange(self._hotness_key, 0, -1, withscores=True)
        return {path: score for path, score in entries}

    async def record_hot(self, path: str, timestamp: float) -> None:
        await self._redis.zadd(self._hotness_key, {path: timestamp})


__all__ = [
    "RedisNamespace",
    "require_redis",
    "RedisStreamsSink",
    "RedisIndexStore",
]
