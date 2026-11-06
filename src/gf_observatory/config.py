"""Local-only config, never an authorization to write to WordBench workspaces."""
from dataclasses import dataclass
from pathlib import Path
import os
import tomllib
from .errors import require

@dataclass(frozen=True)
class Config:
    database: Path
    bind: str = "127.0.0.1"
    port: int = 8765
    max_archive_bytes: int = 250_000_000


def load_config(path: str | Path | None = None) -> Config:
    f = Path(path or os.environ.get("GF_OBSERVATORY_CONFIG", "observatory.toml")).expanduser().absolute()
    data = tomllib.loads(f.read_text(encoding="utf8")) if f.is_file() else {}
    api = data.get("api", {})
    state = data.get("state", {})
    require(data.get("security", {}).get("source_writes", False) is False,
            "OBS_CONFIG_UNSAFE", "Source writes cannot be enabled")
    bind = api.get("bind", "127.0.0.1")
    require(bind == "127.0.0.1", "OBS_CONFIG_UNSAFE", "Only 127.0.0.1 allowed")
    port = api.get("port", 8765)
    require(type(port) is int and 1 <= port <= 65535, "OBS_CONFIG_INVALID", "Invalid API port")
    db = Path(state.get("database", ".gf-observatory/observatory.sqlite3")).expanduser()
    if not db.is_absolute(): db = (f.parent/db).absolute()
    return Config(database=db, bind=bind, port=port)
