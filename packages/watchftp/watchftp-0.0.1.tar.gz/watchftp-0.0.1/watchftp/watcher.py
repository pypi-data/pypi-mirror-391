"""Watcher skeleton wiring configuration and event fans out."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable

import logging

from .metrics import record_events, set_queue_depth
from .redis import RedisStreamsSink
from .scheduler import Scheduler
from .settings import WatchConfig, WatcherSettings
from .types import EventBatch

EventCallback = Callable[[EventBatch], Awaitable[None]]


class Watcher:
    """High-level async watcher API.

    The implementation is currently a scaffold that wires configuration, event fan-out, and
    lifecycle hooks. Connector and scheduler integrations will push batches via `_publish`.
    """

    def __init__(self, config: WatchConfig | WatcherSettings):
        self._config = WatchConfig(**config.model_dump()) if isinstance(config, WatcherSettings) else config
        self._callbacks: list[EventCallback] = []
        self._event_queue: asyncio.Queue[EventBatch | None] = asyncio.Queue()
        self._running = False
        self._publisher_lock = asyncio.Lock()
        self._scheduler: Scheduler | None = None
        self._redis_sink: RedisStreamsSink | None = None
        self._logger = logging.getLogger("watchftp.watcher")

    @property
    def config(self) -> WatchConfig:
        return self._config

    @classmethod
    def from_env(cls) -> "Watcher":
        """Load configuration from environment variables using WatcherSettings."""

        settings = WatcherSettings()  # type: ignore[call-arg]
        return cls(settings)

    async def __aenter__(self) -> "Watcher":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()

    async def start(self) -> "Watcher":
        if self._running:
            return self
        if self._config.redis_enabled and not self._config.redis_url:
            # Fallback to local Redis when enabled but URL unset (dev convenience).
            self._config.redis_url = "redis://127.0.0.1:6379/0"
        self._event_queue = asyncio.Queue()
        self._running = True
        if self._config.redis_enabled:
            self._redis_sink = RedisStreamsSink(self._config)
            await self._redis_sink.start()
        self._scheduler = Scheduler(self._config, self._publish)
        await self._scheduler.start()
        self._logger.info("watcher_started", tenant=self._config.tenant_id)
        return self

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._scheduler:
            await self._scheduler.stop()
            self._scheduler = None
        if self._redis_sink:
            await self._redis_sink.stop()
            self._redis_sink = None
        await self._event_queue.put(None)
        self._logger.info("watcher_stopped", tenant=self._config.tenant_id)

    async def watch(self) -> AsyncIterator[EventBatch]:
        """Yield event batches emitted by the engine."""

        if not self._running:
            raise RuntimeError("watch() requires watcher.start() or async context manager")

        while True:
            batch = await self._event_queue.get()
            if batch is None:
                break
            yield batch

    def on_event(self, callback: EventCallback) -> None:
        """Register an async callback executed for every emitted batch."""

        self._callbacks.append(callback)

    async def snapshot(self, root: str) -> dict[str, object]:  # pragma: no cover - to be implemented
        raise NotImplementedError("snapshot() will be implemented during engine wiring")

    async def rescan(self, root: str) -> None:  # pragma: no cover - to be implemented
        raise NotImplementedError("rescan() will be implemented during engine wiring")

    async def _publish(self, events: EventBatch) -> None:
        """Fan out events to queue consumers and registered callbacks."""

        if not events:
            return
        async with self._publisher_lock:
            await self._event_queue.put(events)
            set_queue_depth(self._config.tenant_id, self._event_queue.qsize())
            if self._callbacks:
                await asyncio.gather(*(cb(events) for cb in self._callbacks))
            if self._redis_sink:
                await self._redis_sink.publish(events)
            record_events(events)


__all__ = ["Watcher", "EventCallback"]
