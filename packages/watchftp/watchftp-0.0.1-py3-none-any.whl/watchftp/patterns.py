"""Pattern compilation helpers for watchftp."""
from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase
import re
from typing import Callable, Iterable

try:  # pragma: no cover - optional dependency fallback
    from wcmatch import glob as wc_glob
except ImportError:  # pragma: no cover - fallback if wcmatch is missing
    wc_glob = None

Matcher = Callable[[str], bool]


def _compile_glob(pattern: str, case_sensitive: bool) -> Matcher:
    if wc_glob:
        flags = wc_glob.BRACE | wc_glob.GLOBSTAR
        if not case_sensitive:
            flags |= wc_glob.IGNORECASE

        compiled = wc_glob.compile(pattern, flags=flags)

        def _match(value: str) -> bool:
            return bool(compiled.match(value))

        return _match

    if not case_sensitive:
        pattern = pattern.lower()

        def _match(value: str) -> bool:
            return fnmatchcase(value.lower(), pattern)

        return _match

    return lambda value: fnmatchcase(value, pattern)


def _compile_regex(pattern: str, case_sensitive: bool) -> Matcher:
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern, flags=flags)
    return lambda value: bool(regex.search(value))


@dataclass
class PatternMatcher:
    include: list[Matcher]
    exclude: list[Matcher]

    def matches(self, relative_path: str) -> bool:
        """True when path matches include set and is not excluded."""

        included = any(m(relative_path) for m in self.include) if self.include else True
        if not included:
            return False
        return not any(m(relative_path) for m in self.exclude)

    def should_prune(self, relative_dir: str) -> bool:
        """Return True if subtree should be pruned entirely."""

        return any(m(relative_dir.rstrip("/") + "/") for m in self.exclude)


@dataclass
class CompiledWatchPath:
    root: str
    matcher: PatternMatcher

    def is_under_root(self, remote_path: str) -> bool:
        return remote_path == self.root or remote_path.startswith(self.root.rstrip("/") + "/")

    def relative(self, remote_path: str) -> str:
        if not self.is_under_root(remote_path):  # pragma: no cover - safeguard
            raise ValueError(f"{remote_path} is outside root {self.root}")
        rel = remote_path[len(self.root) :].lstrip("/")
        return rel or "."

    def matches(self, remote_path: str) -> bool:
        rel = self.relative(remote_path)
        return self.matcher.matches(rel)

    def should_prune(self, directory_path: str) -> bool:
        rel = self.relative(directory_path)
        return self.matcher.should_prune(rel)


def compile_watch_paths(paths: Iterable["WatchPath"], *, case_sensitive: bool) -> list[CompiledWatchPath]:
    from .settings import WatchPath  # local import to avoid cycles

    compiled: list[CompiledWatchPath] = []
    for path_cfg in paths:
        include = [
            _compile_regex(p, case_sensitive) if path_cfg.use_regex else _compile_glob(p, case_sensitive)
            for p in path_cfg.include
        ]
        exclude = [
            _compile_regex(p, case_sensitive) if path_cfg.use_regex else _compile_glob(p, case_sensitive)
            for p in path_cfg.exclude
        ]
        matcher = PatternMatcher(include=include, exclude=exclude)
        compiled.append(CompiledWatchPath(root=path_cfg.root, matcher=matcher))
    return compiled


__all__ = ["PatternMatcher", "CompiledWatchPath", "compile_watch_paths"]
