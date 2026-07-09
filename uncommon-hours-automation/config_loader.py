"""Config + path helpers shared across the pipeline.

Keeps all file access relative to the project root so the tools work no matter
what directory you launch them from (Windows Task Scheduler, PowerShell, etc.).
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def get_settings() -> dict:
    path = project_root() / "config" / "settings.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_sources() -> list[dict]:
    path = project_root() / "config" / "sources.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("sources", [])


def enabled_sources() -> list[dict]:
    return [s for s in get_sources() if s.get("enabled")]


def resolve(path_key: str) -> Path:
    """Resolve one of the settings['paths'] entries to an absolute Path."""
    settings = get_settings()
    rel = settings["paths"][path_key]
    p = project_root() / rel
    return p


def ensure_dirs() -> None:
    for key in ("downloads", "processed", "logs"):
        resolve(key).mkdir(parents=True, exist_ok=True)
    resolve("database").parent.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """A logger that writes to logs/<name>.log and to the console."""
    ensure_dirs()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    log_file = resolve("logs") / f"{name}.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger
