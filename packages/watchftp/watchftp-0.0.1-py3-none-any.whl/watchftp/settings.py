"""Configuration models and helpers for watchftp."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import (
    AnyUrl,
    BaseModel,
    Field,
    PositiveInt,
    field_validator,
    model_validator,
)
from pydantic_settings import SettingsConfigDict, BaseSettings

ScaleName = Literal["small", "medium", "large", "xl", "xxl"]
DEFAULT_REDIS_TTL_SECONDS = 30 * 24 * 60 * 60


class WatchPath(BaseModel):
    root: str = Field(..., description="Remote directory root (absolute path).")
    include: list[str] = Field(default_factory=lambda: ["**/*"])
    exclude: list[str] = Field(default_factory=list)
    use_regex: bool = Field(False, description="Interpret patterns as regex instead of glob.")

    @field_validator("root")
    @classmethod
    def normalize_root(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("/"):
            raise ValueError("root paths must be absolute (start with '/')")
        return value.rstrip("/") or "/"

    @model_validator(mode="after")
    def ensure_patterns_present(self) -> "WatchPath":
        if not self.include and not self.exclude:
            raise ValueError("at least one include or exclude pattern must be provided")
        return self


class WatchConfig(BaseModel):
    tenant_id: str = Field(..., min_length=1, description="Namespace for Redis keys/streams.")
    protocol: Literal["ftp", "ftps", "sftp"] = "sftp"
    host: str = Field(..., min_length=1)
    port: PositiveInt | None = None
    username: str = Field(..., min_length=1)
    password: str | None = None
    private_key: str | None = None
    watch_paths: list[WatchPath] = Field(..., alias="paths", min_length=1)
    max_watch_roots: int = Field(-1, description="Cap on roots per process; -1 means unlimited.")

    poll_interval: float = 2.0
    hot_min_poll: float = 1.0
    max_concurrency: int = 24
    per_dir_concurrency: int = 3
    ftp_mlsd_limit: int = 12
    ftp_stat_limit: int = 16
    sftp_stat_limit: int = 24
    event_batch_size: int = 128
    rename_window_s: int = 5

    redis_url: AnyUrl | None = Field(
        default=None,
        description="Redis connection string; optional.",
    )
    redis_ttl_seconds: int = Field(
        default=DEFAULT_REDIS_TTL_SECONDS,
        description="Redis Stream retention (seconds).",
    )
    event_bus: Literal["local", "redis_stream"] = "local"

    enable_hash: bool = False
    case_sensitive: bool = True
    dedup_window_s: int = 5

    ftps_verify_cert: bool = False
    ftps_ssl_context_file: Path | None = None
    sftp_known_hosts: Path | None = None
    sftp_allowed_ciphers: list[str] | None = None

    model_config = dict(populate_by_name=True, validate_assignment=True, extra="forbid")

    @field_validator("redis_ttl_seconds")
    @classmethod
    def validate_retention(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("redis_ttl_seconds must be positive")
        return value

    @model_validator(mode="after")
    def validate_watch_roots(self) -> "WatchConfig":
        if self.max_watch_roots != -1 and len(self.watch_paths) > self.max_watch_roots:
            raise ValueError(
                f"configured watch paths ({len(self.watch_paths)}) exceed max_watch_roots={self.max_watch_roots}"
            )
        return self

    @model_validator(mode="after")
    def set_default_port(self) -> "WatchConfig":
        if self.port is None:
            self.port = 22 if self.protocol == "sftp" else 21
        if self.protocol == "sftp" and self.port in {21, 990}:
            raise ValueError("sftp typically listens on port 22; explicitly set port if different")
        if self.protocol in {"ftp", "ftps"} and self.port == 22:
            raise ValueError("ftp/ftps default port is 21; adjust if intentional")
        return self

    @property
    def redis_enabled(self) -> bool:
        return self.redis_url is not None or self.event_bus == "redis_stream"

    def model_copy_with(self, **kwargs) -> "WatchConfig":
        data = self.model_dump()
        data.update(kwargs)
        return WatchConfig(**data)

    @property
    def paths(self) -> list[WatchPath]:
        """Backwards-compatible accessor for legacy naming."""

        return self.watch_paths


class WatcherSettings(BaseSettings, WatchConfig):
    """Environment-aware settings loader."""

    model_config = SettingsConfigDict(
        env_prefix="WATCHFTP_",
        env_file=".env",
        env_file_encoding="utf-8",
        # env_nested_delimiter="__",
        extra="ignore",
        validate_assignment=True,
        populate_by_name=True,
        case_sensitive=False,
    )


SIZING_PRESETS: dict[ScaleName, dict[str, int | float]] = {
    "small": dict(
        poll_interval=1.0,
        hot_min_poll=0.5,
        max_concurrency=16,
        per_dir_concurrency=2,
        ftp_mlsd_limit=8,
        ftp_stat_limit=8,
        sftp_stat_limit=16,
        event_batch_size=64,
        rename_window_s=3,
    ),
    "medium": dict(
        poll_interval=2.0,
        hot_min_poll=1.0,
        max_concurrency=24,
        per_dir_concurrency=3,
        ftp_mlsd_limit=12,
        ftp_stat_limit=16,
        sftp_stat_limit=24,
        event_batch_size=128,
        rename_window_s=5,
    ),
    "large": dict(
        poll_interval=3.0,
        hot_min_poll=1.5,
        max_concurrency=32,
        per_dir_concurrency=4,
        ftp_mlsd_limit=16,
        ftp_stat_limit=24,
        sftp_stat_limit=32,
        event_batch_size=256,
        rename_window_s=7,
    ),
    "xl": dict(
        poll_interval=5.0,
        hot_min_poll=2.0,
        max_concurrency=48,
        per_dir_concurrency=6,
        ftp_mlsd_limit=20,
        ftp_stat_limit=32,
        sftp_stat_limit=48,
        event_batch_size=256,
        rename_window_s=10,
    ),
    "xxl": dict(
        poll_interval=8.0,
        hot_min_poll=3.0,
        max_concurrency=64,
        per_dir_concurrency=8,
        ftp_mlsd_limit=24,
        ftp_stat_limit=40,
        sftp_stat_limit=64,
        event_batch_size=512,
        rename_window_s=15,
    ),
}


def tune_for_scale(config: WatchConfig, scale: ScaleName) -> WatchConfig:
    """Apply sizing presets in-place and return config."""

    if scale not in SIZING_PRESETS:
        raise ValueError(f"unknown scale '{scale}'")

    updates = SIZING_PRESETS[scale]
    for field, value in updates.items():
        setattr(config, field, value)
    return config


__all__ = [
    "WatchPath",
    "WatchConfig",
    "WatcherSettings",
    "tune_for_scale",
    "DEFAULT_REDIS_TTL_SECONDS",
    "SIZING_PRESETS",
]
