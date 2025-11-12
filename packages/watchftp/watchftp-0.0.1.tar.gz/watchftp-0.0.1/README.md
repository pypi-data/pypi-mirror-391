# watchftp

Async, polling-based watcher for FTP/SFTP endpoints with optional Redis-backed persistence and change streams.

## Overview

watchftp scans remote trees using protocol-native metadata (MLSD for FTP, AsyncSSH for SFTP), fingerprints directories, and emits batched change events (create/modify/delete/heuristic move). The engine is fully async, tuned for large trees (250k+ files), and can persist its state plus event stream in Redis for multi-consumer durability.

Key capabilities:

- **Async core**: aioftp + AsyncSSH connectors with bounded concurrency.
- **Pattern-aware traversal**: glob/regex includes/excludes compiled via `wcmatch` fallback.
- **Directory fingerprints**: Merkle-style digests to skip cold subtrees and detect changes efficiently.
- **Redis integration**: Optional persistence and Streams; tenants are fully namespaced (`wf:{tenant}:{server}:...`). Defaults to `redis://127.0.0.1:6379/0` when Redis streaming is enabled without a URL so local testing “just works”.
- **Config via Pydantic**: Load settings from environment variables using `pydantic-settings`, including scale presets, watch-root limits (with `-1` meaning unlimited), and security toggles.

## Getting Started

### Requirements

- Python 3.12+
- FTP/SFTP endpoints to monitor
- Optional Redis (local development uses `redis://127.0.0.1:6379/0`)

Install with [uv](https://docs.astral.sh/uv/) (recommended) or pip:

```bash
uv pip install -e .
# or
pip install -e .
```

### Quick start

```python
import asyncio
from watchftp import WatchConfig, WatchPath, Watcher, tune_for_scale

cfg = WatchConfig(
    tenant_id="demo-tenant",
    protocol="sftp",
    host="sftp.internal",
    username="svc",
    private_key="~/.ssh/id_ed25519",
    watch_paths=[WatchPath(root="/incoming", include=["**/*.csv"], exclude=["**/tmp/**"])]
)
tune_for_scale(cfg, "medium")

async def main():
    async with Watcher(cfg) as watcher:
        async for batch in watcher.watch():
            for event in batch:
                print(event.type, event.path)

asyncio.run(main())
```

Enable Redis streams and persistence by setting `cfg.event_bus = "redis_stream"` (or `WATCHFTP_EVENT_BUS=redis_stream`). If no `redis_url` is provided, the watcher will connect to `redis://127.0.0.1:6379/0` automatically for local development.

## Documentation

We publish docs with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). To preview locally:

```bash
uv pip install mkdocs mkdocs-material
mkdocs serve
```

Changes are automatically built and deployed to GitHub Pages whenever `pyproject.toml`'s version is bumped on `main` (see `.github/workflows/docs.yml`).

## Configuration

The main knobs live on `WatchConfig` (Pydantic model):

- `tenant_id`: required for namespacing Redis state.
- `watch_paths`: list of `WatchPath` roots with include/exclude patterns (glob or regex).
- `max_watch_roots`: cap per process (`-1` for unlimited).
- Concurrency knobs (`poll_interval`, `max_concurrency`, per-protocol limits).
- Security toggles (`ftps_verify_cert`, `sftp_known_hosts`, allowed ciphers).
- Persistence settings (`redis_url`, `redis_ttl_seconds`, `event_bus`).

Environment variables are loaded via `WatcherSettings` with the prefix `WATCHFTP_` (e.g., `WATCHFTP_TENANT`, `WATCHFTP_REDIS_URL`). Nested values use `__` (double underscore) separators.

- `configure_logging(level="INFO", structured=True)`: optional helper to emit JSON logs via `logging`. Call once in your app (`from watchftp import configure_logging`).
- `ensure_metrics_server(port=9464)`: starts the Prometheus HTTP endpoint (uses `prometheus-client`).

Example:

```python
from watchftp import configure_logging, ensure_metrics_server

configure_logging("INFO")
ensure_metrics_server()
```

## Project Roadmap

## Testing

- Unit tests (Redis + helpers): `python -m unittest`
- Integration tests (FTP/SFTP against pyftpdlib + AsyncSSH) require Python 3.12+ and can be run with `pytest -m integration`. They start ephemeral servers locally.

- **M0** (current): Config scaffolding, scheduler skeleton, Redis index + stream sink, unit tests.
- **M1**: Real FTP/SFTP traversal, diff engine polish, adaptive scheduler knobs.
- **M2**: Advanced Redis-backed recovery, rename heuristics, metrics exposure, docs/examples.

See [`docs/project.md`](docs/project.md) for the full PRD, architecture, and sizing matrix.
