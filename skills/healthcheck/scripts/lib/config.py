"""Load the local inventory without ever writing it into the repository."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

DEFAULT_PATH = Path.home() / ".config" / "healthcheck" / "config.toml"


class Config:
    def __init__(self, data: dict, path: Path, exists: bool) -> None:
        self.data = data
        self.path = path
        self.exists = exists

    def get(self, *keys, default=None):
        node = self.data
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node


def load(path: str | None = None) -> Config:
    target = Path(os.path.expanduser(path)) if path else DEFAULT_PATH
    if not target.is_file():
        return Config({}, target, False)
    with target.open("rb") as handle:
        return Config(tomllib.load(handle), target, True)


def expand(value: str) -> str:
    return os.path.expanduser(os.path.expandvars(value))


def as_path(value: str) -> Path:
    return Path(expand(value))
