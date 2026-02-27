"""Read/write the rAthena .env configuration file."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Variables that only need a container restart
RESTART_ONLY = {
    "SERVER_NAME",
    "BASE_EXP_RATE",
    "JOB_EXP_RATE",
    "DROP_RATE",
    "CARD_DROP_RATE",
    "DB_USER",
    "DB_PASS",
    "DB_NAME",
    "DB_ROOT_PASS",
    "DB_PORT_EXPOSE",
}

# Variables that require a full rebuild
REBUILD_REQUIRED = {
    "PACKETVER",
    "BUILD_MODE",
    "RATHENA_BRANCH",
}

# Connection variables (local only, no server action needed)
CONNECTION = {
    "SERVER_IP",
    "SERVER_USER",
    "SERVER_SSH_PORT",
    "REMOTE_DIR",
}

RATE_VARS = {"BASE_EXP_RATE", "JOB_EXP_RATE", "DROP_RATE", "CARD_DROP_RATE"}


def rate_display(value: str) -> str:
    """Convert rate value to human-readable multiplier, e.g. '5000' -> '50x'."""
    try:
        return f"{int(value) // 100}x"
    except (ValueError, ZeroDivisionError):
        return value


@dataclass
class EnvLine:
    """One line from the .env file, preserving comments and blank lines."""

    raw: str
    key: str | None = None
    value: str | None = None


@dataclass
class Config:
    """Manages the rAthena .env file, preserving formatting."""

    path: Path
    lines: list[EnvLine] = field(default_factory=list)
    _index: dict[str, int] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> Config:
        path = Path(path)
        cfg = cls(path=path)
        if not path.exists():
            return cfg
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)", raw_line)
            if m:
                el = EnvLine(raw=raw_line, key=m.group(1), value=m.group(2))
                cfg._index[el.key] = len(cfg.lines)
            else:
                el = EnvLine(raw=raw_line)
            cfg.lines.append(el)
        return cfg

    def get(self, key: str, default: str = "") -> str:
        if key in self._index:
            return self.lines[self._index[key]].value or default
        return default

    def set(self, key: str, value: str) -> None:
        if key in self._index:
            idx = self._index[key]
            self.lines[idx].value = value
            self.lines[idx].raw = f"{key}={value}"
        else:
            el = EnvLine(raw=f"{key}={value}", key=key, value=value)
            self._index[key] = len(self.lines)
            self.lines.append(el)

    def save(self) -> None:
        self.path.write_text(
            "\n".join(line.raw for line in self.lines) + "\n",
            encoding="utf-8",
        )

    def diff(self, other: Config) -> list[tuple[str, str, str]]:
        """Return list of (key, old_value, new_value) for changed vars."""
        changes = []
        for key, idx in self._index.items():
            old_val = self.lines[idx].value
            new_val = other.get(key)
            if old_val != new_val:
                changes.append((key, old_val or "", new_val))
        return changes

    def needs_rebuild(self, changes: list[tuple[str, str, str]]) -> bool:
        return any(key in REBUILD_REQUIRED for key, _, _ in changes)

    def as_dict(self) -> dict[str, str]:
        return {
            line.key: line.value or ""
            for line in self.lines
            if line.key is not None
        }
