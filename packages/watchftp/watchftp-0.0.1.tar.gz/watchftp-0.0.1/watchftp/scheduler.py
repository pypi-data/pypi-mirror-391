"""Async scheduler that coordinates scans and event emission."""
from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Iterable, List

from .connectors import FTPConnector, RemoteEntry, SFTPConnector
from .events import build_events
from .index import DirectoryIndex
from .metrics import observe_scan, record_events, record_scan_error
from .patterns import CompiledWatchPath, compile_watch_paths
from .redis import RedisIndexStore
from .settings import WatchConfig
from .types import EventBatch

PublishHook = Callable[[EventBatch], Awaitable[None]]

logger = logging.getLogger(__name__)


@dataclass(order=True)
class ScanTarget:
    next_scan: float
    matcher: CompiledWatchPath = field(compare=False)
    interval: float = field(default=0.0, compare=False)
    hot: bool = field(default=False, compare=False)


class Scheduler:
    """Coordinates connector activity, filters, and event emission (scaffold)."""

    def __init__(self, config: WatchConfig, publish: PublishHook):
        self._config = config
        self._publish = publish
        self._compiled_paths: list[CompiledWatchPath] = compile_watch_paths(
            config.paths,
            case_sensitive=config.case_sensitive,
        )
        self._connector = self._build_connector()
        self._index = DirectoryIndex()
        self._index_store = RedisIndexStore(config) if config.redis_enabled else None
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._queue: asyncio.PriorityQueue[ScanTarget] = asyncio.PriorityQueue()
        self._stub_mode = False
        self._stub_counter = 0

    def _build_connector(self):
        if self._config.protocol in {"ftp", "ftps"}:
            return FTPConnector(self._config)
        return SFTPConnector(self._config)

    async def start(self) -> None:
        if self._index_store:
            await self._index_store.start()
            restored = await self._index_store.load_index()
            if restored:
                self._index.restore(restored)
            hot_map = await self._index_store.load_hotness()
        else:
            hot_map = {}
        try:
            await self._connector.connect()
        except Exception as exc:  # pragma: no cover - network path
            self._stub_mode = True
            logger.debug("Connector connect failed (%s); falling back to stub mode", exc)
        else:
            self._stub_mode = False
        self._prime_queue(hot_map)
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop(), name="watchftp-scheduler")
        logger.info(
            "scheduler_started",
            tenant=self._config.tenant_id,
            stub_mode=self._stub_mode,
            paths=len(self._compiled_paths),
        )

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:  # pragma: no cover - shutdown path
                pass
            self._task = None
        await self._connector.close()
        if self._index_store:
            await self._index_store.stop()
        logger.info("scheduler_stopped", tenant=self._config.tenant_id)

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            target = await self._queue.get()
            now = time.monotonic()
            wait = target.next_scan - now
            if wait > 0:
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=wait)
                    if self._stop_event.is_set():
                        break
                except asyncio.TimeoutError:
                    pass
            if self._stop_event.is_set():
                break
            try:
                start = time.perf_counter()
                batch, changed = await self._scan_target(target)
                duration = time.perf_counter() - start
                observe_scan(self._config.tenant_id, target.matcher.root, duration)
                logger.debug(
                    "scan_complete",
                    root=target.matcher.root,
                    changed=changed,
                    duration=duration,
                )
            except Exception as exc:  # pragma: no cover - safety
                record_scan_error(self._config.tenant_id)
                logger.exception("scan_failed", root=target.matcher.root, error=str(exc))
                changed = False
                batch = []
            if batch:
                await self._publish(batch)
            target.interval = self._next_interval(target.interval, changed)
            target.hot = changed
            target.next_scan = time.monotonic() + self._jittered_interval(target.interval)
            self._queue.put_nowait(target)

    @property
    def compiled_paths(self) -> Iterable[CompiledWatchPath]:
        return tuple(self._compiled_paths)

    def _prime_queue(self, hot_map: dict[str, float]) -> None:
        now = time.monotonic()
        for path in self._compiled_paths:
            interval = self._config.poll_interval
            hot = False
            last_hot = hot_map.get(path.root)
            if last_hot and (time.time() - last_hot) <= max(self._config.dedup_window_s, 10):
                interval = self._config.hot_min_poll
                hot = True
            target = ScanTarget(
                next_scan=now + self._jittered_interval(interval),
                matcher=path,
                interval=interval,
                hot=hot,
            )
            self._queue.put_nowait(target)

    async def _scan_target(self, target: ScanTarget) -> tuple[EventBatch, bool]:
        entries = await self._collect_entries(target.matcher)
        created, deleted, modified = self._index.apply(entries)
        changed = bool(created or deleted or modified)
        if changed and self._index_store:
            await self._index_store.record_hot(target.matcher.root, time.time())
        if not self._stub_mode and self._index_store:
            await self._index_store.persist(created, deleted, modified)
        batch = build_events(created, deleted, modified, tenant_id=self._config.tenant_id)
        return batch, changed

    async def _collect_entries(self, matcher: CompiledWatchPath) -> List[RemoteEntry]:
        if self._stub_mode:
            return self._generate_stub_entries([matcher])
        entries: list[RemoteEntry] = []
        queue: list[str] = [matcher.root]
        try:
            while queue:
                current = queue.pop()
                async for entry in self._connector.listdir(current):
                    if not matcher.is_under_root(entry.path):
                        continue
                    if entry.type == "dir":
                        if matcher.should_prune(entry.path):
                            continue
                        queue.append(entry.path)
                    if matcher.matches(entry.path) or entry.type == "dir":
                        entries.append(entry)
        except NotImplementedError:
            self._stub_mode = True
            logger.debug("Connector listdir not implemented; switching to stub mode")
            return self._generate_stub_entries([matcher])
        if entries:
            return entries
        if self._stub_mode:
            return self._generate_stub_entries([matcher])
        return []

    def _generate_stub_entries(self, matchers: Iterable[CompiledWatchPath] | None = None) -> list[RemoteEntry]:
        self._stub_counter += 1
        heartbeat_ts = time.time()
        entries: list[RemoteEntry] = []
        matchers = matchers or self._compiled_paths
        for path in matchers:
            entries.append(
                RemoteEntry(
                    path=f"{path.root.rstrip('/')}/.watchftp-heartbeat",
                    type="file",
                    size=self._stub_counter,
                    mtime=heartbeat_ts,
                    unique=None,
                )
            )
        return entries

    def _next_interval(self, current: float, changed: bool) -> float:
        if current <= 0:
            current = self._config.poll_interval
        if changed:
            return max(self._config.hot_min_poll, current * 0.5)
        return min(self._config.poll_interval, current * 1.5)

    def _jittered_interval(self, base: float) -> float:
        jitter = max(0.05, base * 0.1)
        return max(0.05, base + random.uniform(-jitter, jitter))


__all__ = ["Scheduler"]
