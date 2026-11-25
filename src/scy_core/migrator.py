"""Phase 11 — Non-Destructive Standalone Lucid 2 / Mandara -> Scy-Shell Config Migrator."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
import tomllib


class ScyConfigMigrator:
    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store

    def migrate_existing_configs(self) -> dict[str, Any]:
        backup_dir = self.store.create_backup(tag="pre-migration")
        imported_lucid = 0
        imported_mandara = 0

        # 1. Import existing ~/.config/lucid/settings.json if present
        lucid_settings = self.store.home / ".config" / "lucid" / "settings.json"
        if lucid_settings.exists():
            try:
                raw = json.loads(lucid_settings.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    for k, v in raw.items():
                        scy_id = f"scy.providers.lucid.prefs.{k}"
                        if scy_id in self.store.schema.by_id:
                            self.store.set_setting(scy_id, v, flush=False)
                            imported_lucid += 1
            except Exception:
                pass

        # 2. Import existing ~/.config/mandara/config.toml if present
        mandara_cfg = self.store.home / ".config" / "mandara" / "config.toml"
        if mandara_cfg.exists():
            try:
                mdoc = tomllib.loads(mandara_cfg.read_text(encoding="utf-8"))
                if isinstance(mdoc, dict):
                    imported_mandara = self._walk_mandara_dict(mdoc, "")
            except Exception:
                pass

        self.store.flush_all()
        return {
            "backup_dir": str(backup_dir),
            "imported_lucid_keys": imported_lucid,
            "imported_mandara_keys": imported_mandara,
        }

    def _walk_mandara_dict(self, node: dict[str, Any], prefix: str) -> int:
        count = 0
        for k, v in node.items():
            if k == "scy_gates":
                continue
            ptr = f"{prefix}/{k}"
            if isinstance(v, dict):
                count += self._walk_mandara_dict(v, ptr)
            else:
                meta = self.store.schema.by_orig.get(("mandara", ptr))
                if meta is not None:
                    self.store.set_setting(meta.scy_id, v, flush=False)
                    count += 1
        return count
