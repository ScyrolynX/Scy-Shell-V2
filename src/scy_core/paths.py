"""Portable path discovery for Scy-Shell across extracted releases, user installs, and system packages."""
from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    override = os.environ.get("SCY_SHELL_ROOT")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[2]


def schema_dir() -> Path:
    return project_root() / "schema"


def provenance_dir() -> Path:
    return project_root() / "provenance"


def adapters_dir() -> Path:
    return project_root() / "adapters"


def studio_dir() -> Path:
    return project_root() / "studio"


def lucid_engine_dir() -> Path | None:
    env_p = os.environ.get("SCY_LUCID_DIR")
    candidates = [
        Path(env_p) if env_p else None,
        project_root() / "engines" / "lucid",
        Path.home() / ".config" / "quickshell" / "lucid",
        Path("/usr/share/scy-shell/engines/lucid"),
    ]
    for c in candidates:
        if c is not None and (c / "shell.qml").exists():
            return c.resolve()
    return None


def mandara_engine_dir() -> Path | None:
    env_p = os.environ.get("SCY_MANDARA_DIR")
    candidates = [
        Path(env_p) if env_p else None,
        project_root() / "engines" / "mandara",
        Path("/usr/share/scy-shell/engines/mandara"),
    ]
    for c in candidates:
        if c is not None and (c / "Cargo.toml").exists():
            return c.resolve()
    return None


def lucid_keybinds_template() -> Path:
    eng = lucid_engine_dir()
    if eng is not None and (eng / "support" / "hypr" / "keybinds.json").exists():
        return eng / "support" / "hypr" / "keybinds.json"
    return schema_dir() / "lucid_keybinds_default.json"
