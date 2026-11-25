"""Scy-Shell v2.0 — Unified Lossless Config Store, Login-Safe Reconciliation, Migration & 16-Store Sync.

Architectural Guarantees:
1. Every one of the 2,026 settings (643 Lucid + 1,232 Mandara + 151 Scy-Shell native) has a
   deterministic persistence lifecycle across `config.toml`, native engine stores, and `design-tokens.json`.
2. SHA-256 Persistence Ledger (`persistence-ledger.json`) reconciles live edits made in QML (`prefs.json`,
   `blur.json`, `widgets.json`, `lucid-settings.lua`) or `mandara/config.toml` BEFORE flushing on login/startup,
   preventing stale `config.toml` values or defaults from EVER overwriting user preferences after re-login.
3. Versioned migrations (`v1 -> v2`) automatically snapshot before upgrading.
4. Corruption recovery restores from `.last-good` shadow copies and logs failures to `persistence-errors.log`.
5. Lock Screen (`11-lock-screen`) and Login Experience (`12-login`) remain strictly independent.
6. Single authoritative dock ownership is enforced across `scy.dock.mode`, `Prefs.dockEnabled`, and `[scy_gates]`.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

from .schema import (
    DEFAULT_ACTIVE_PROVIDERS,
    DEFAULT_PRESENTATIONS,
    ScySchema,
    SettingMeta,
)
from .toml_io import atomic_write_text, dumps_toml, get_pointer, load_toml, set_pointer

CURRENT_SCHEMA_VERSION = 2
MOJI_CONFIG_KEYS = frozenset({"giphyKey", "tenorKey", "gifDir", "pasteApps"})


def _sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _lua_val(val: Any) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return repr(val)
    s = str(val).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


def _parse_ini_general(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    out: dict[str, Any] = {}
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";", "[")) or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if v.lower() == "true":
            out[k] = True
        elif v.lower() == "false":
            out[k] = False
        else:
            try:
                out[k] = int(v)
            except ValueError:
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
    return out


class ScyConfigStore:
    """Authoritative persistent configuration backend for Scy-Shell v2.0."""

    def __init__(
        self,
        home_dir: Path | None = None,
        schema: ScySchema | None = None,
        skip_init_load: bool = False,
    ) -> None:
        self.home = (home_dir or Path.home()).resolve()
        self.config_dir = self.home / ".config" / "scy-shell"
        self.state_dir = self.home / ".local" / "state" / "scy-shell"
        self.backup_root = self.home / ".local" / "share" / "scy-shell" / "backups"

        self.config_path = self.config_dir / "config.toml"
        self.last_good_config_path = self.config_dir / "config.toml.last-good"
        self.dock_config_path = self.config_dir / "dock.json"
        self.pinned_apps_path = self.config_dir / "pinned-apps.json"

        self.runtime_state_path = self.state_dir / "runtime-state.json"
        self.live_values_path = self.state_dir / "live-values.json"
        self.design_tokens_path = self.state_dir / "design-tokens.json"
        self.login_greeter_path = self.state_dir / "login-greeter.json"
        self.ledger_path = self.state_dir / "persistence-ledger.json"
        self.error_log_path = self.state_dir / "persistence-errors.log"
        self.change_log_path = self.state_dir / "change-history.jsonl"
        self.preview_baseline_path = self.state_dir / "preview-baseline.json"

        # Complete native Lucid engine paths
        self.lucid_prefs_path = self.home / ".config" / "quickshell" / "lucidprefs" / "prefs.json"
        self.lucid_hypr_lua_path = self.home / ".config" / "hypr" / "lucid-settings.lua"
        self.lucid_blur_path = self.home / ".config" / "quickshell" / "blur.json"
        self.lucid_widgets_path = self.home / ".config" / "quickshell" / "lucidwidgets" / "widgets.json"
        self.lucid_widgets_legacy_path = self.home / ".config" / "quickshell" / "widgets.json"
        self.lucid_pinned_path = self.home / ".config" / "quickshell" / "pinned.json"
        self.lucid_moji_config_path = self.home / ".config" / "quickshell" / "lucidmoji" / "config.json"
        self.lucid_moji_state_path = self.home / ".config" / "quickshell" / "lucidmoji" / "state.json"
        self.lucid_app_paths = {
            "lumen": self.home / ".local" / "state" / "lucid" / "lumen.json",
            "lens": self.home / ".local" / "state" / "lucid" / "lens.json",
            "clock_app": self.home / ".local" / "state" / "lucid" / "clock.json",
            "shot_state": self.home / ".local" / "state" / "lucid" / "shot.json",
            "keys": self.home / ".config" / "quickshell" / "lucidkeys" / "state.json",
        }
        self.lucid_sddm_stage_path = self.state_dir / "staged-sddm-theme.conf"

        # Complete native Mandara engine paths
        self.mandara_config_path = self.home / ".config" / "mandara" / "config.toml"
        self.mandara_wallgen_path = self.home / ".config" / "mandara" / "wallgen.toml"
        self.mandara_greeter_stage_path = self.state_dir / "staged-greeter.toml"

        self.schema = schema or ScySchema()
        if skip_init_load:
            self.doc = self._default_doc()
        else:
            had_config = self.config_path.exists()
            self.doc = self._load_or_init()
            if not had_config:
                self.import_existing_engine_configs()
            else:
                self.reconcile_live_engine_stores()
            self._run_migrations_if_needed()
            self.flush_all()

    def log_persistence_error(self, message: str) -> None:
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self.error_log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"[{ts}] {message}\n")

    def _record_change(self, action: str, key: str, old_val: Any, new_val: Any) -> None:
        try:
            self.change_log_path.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "ts_ms": int(time.time() * 1000),
                "action": action,
                "key": key,
                "old": old_val,
                "new": new_val,
            }
            with self.change_log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as exc:
            self.log_persistence_error(f"Failed to append change log for {key}: {exc}")

    def _default_doc(self) -> dict[str, Any]:
        return {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "identity": {
                "primary_style": "scy-m3-expressive",
                "wallpaper": "",
                "matugen_scheme": "scheme-tonal-spot",
                "dark_mode": True,
                "accent_seed": "#ffb1c4",
                "font_family": "Google Sans",
                "mono_font_family": "JetBrains Mono",
                "reduced_motion": False,
            },
            "active_providers": dict(DEFAULT_ACTIVE_PROVIDERS),
            "presentations": dict(DEFAULT_PRESENTATIONS),
            "safety": {
                "conflict_policy": "prompt",
                "hyprland_trial_seconds": 15,
                "auto_backup": True,
            },
            "scy_native": {},
            "providers": {
                "lucid": {
                    "prefs": {},
                    "hypr": {},
                    "glass": {},
                    "apps": {},
                    "widget_opts": {},
                    "lock_widgets": {},
                    "sddm": {},
                },
                "mandara": {
                    "config": {},
                    "wallgen": {},
                    "greeter": {},
                },
            },
        }

    def _load_or_init(self) -> dict[str, Any]:
        base = self._default_doc()
        if not self.config_path.exists():
            if self.last_good_config_path.exists():
                try:
                    loaded = load_toml(self.last_good_config_path)
                    self._deep_merge(base, loaded)
                    self.log_persistence_error("Recovered missing config.toml from config.toml.last-good")
                except Exception as exc:
                    self.log_persistence_error(f"Failed to parse config.toml.last-good: {exc}")
            return base

        try:
            raw_txt = self.config_path.read_text(encoding="utf-8")
            if not raw_txt.strip():
                raise ValueError("Empty config.toml")
            loaded = load_toml(self.config_path)
            if not isinstance(loaded, dict) or ("providers" not in loaded and "schema_version" not in loaded):
                raise ValueError("Malformed top-level structure in config.toml")
            self._deep_merge(base, loaded)
            return base
        except Exception as exc:
            self.log_persistence_error(f"Corrupted config.toml detected ({exc}); initiating recovery")
            try:
                corrupt_dir = self.backup_root / f"corrupted-{time.strftime('%Y%m%d-%H%M%S')}-{int(time.time_ns() % 10000)}"
                corrupt_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.config_path, corrupt_dir / "config.toml.corrupted")
            except Exception:
                pass
            if self.last_good_config_path.exists():
                try:
                    loaded_good = load_toml(self.last_good_config_path)
                    self._deep_merge(base, loaded_good)
                    self.log_persistence_error("Successfully restored config state from config.toml.last-good")
                except Exception as exc2:
                    self.log_persistence_error(f"Fallback config.toml.last-good also unreadable: {exc2}")
            return base

    def _run_migrations_if_needed(self) -> None:
        ver = int(self.doc.get("schema_version", 1) or 1)
        if ver < CURRENT_SCHEMA_VERSION:
            if self.config_path.exists():
                self.create_backup(tag=f"migrate-v{ver}-to-v{CURRENT_SCHEMA_VERSION}")
            self.doc.setdefault("scy_native", {})
            # Sync scy.dock.mode from existing v1 dock provider & style without losing user choice
            dock_prov = self.doc["active_providers"].get("dock", "lucid")
            l_prefs = self.doc["providers"]["lucid"]["prefs"]
            if "scy.dock.mode" not in self.doc["scy_native"]:
                if dock_prov == "none":
                    self.doc["scy_native"]["scy.dock.mode"] = "disabled"
                elif dock_prov == "mandara":
                    self.doc["scy_native"]["scy.dock.mode"] = "rail"
                else:
                    st = str(l_prefs.get("dockStyle", "island"))
                    self.doc["scy_native"]["scy.dock.mode"] = st if st in ("island", "notch", "split") else "island"
            # Decouple Lock Screen from Login by default unless explicitly configured
            if "lockLoginSync" not in l_prefs:
                l_prefs["lockLoginSync"] = False
            self.doc["schema_version"] = CURRENT_SCHEMA_VERSION
            self._record_change("schema_migration", "schema_version", ver, CURRENT_SCHEMA_VERSION)

    @staticmethod
    def _deep_merge(dst: dict[str, Any], src: dict[str, Any]) -> None:
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                ScyConfigStore._deep_merge(dst[k], v)
            else:
                dst[k] = v

    def _load_ledger(self) -> dict[str, dict[str, Any]]:
        return _read_json(self.ledger_path)

    def _save_ledger(self) -> None:
        ledger: dict[str, dict[str, Any]] = {}
        tracked = {
            "lucid_prefs": (self.lucid_prefs_path, dict(self.doc["providers"]["lucid"]["prefs"])),
            "lucid_blur": (self.lucid_blur_path, dict(self.doc["providers"]["lucid"]["glass"])),
            "mandara_config": (self.mandara_config_path, None),
            "mandara_wallgen": (self.mandara_wallgen_path, None),
        }
        for name, (fpath, snap) in tracked.items():
            if fpath.exists():
                entry: dict[str, Any] = {
                    "sha256": _sha256_file(fpath),
                    "mtime_ns": fpath.stat().st_mtime_ns,
                }
                if snap is not None:
                    entry["keys"] = snap
                ledger[name] = entry
        _write_json(self.ledger_path, ledger)

    def reconcile_live_engine_stores(self) -> dict[str, int]:
        """Absorbs any external/live session edits made directly by Lucid QML (`Prefs.qml` -> `prefs.json`,
        `Glass.qml` -> `blur.json`) or Mandara (`mandara/config.toml`) since the last Scy-Shell flush.
        Prevents login startup (`scy-daemon`) from ever clobbering user changes back to stale values!"""
        ledger = self._load_ledger()
        absorbed = {"lucid_prefs": 0, "lucid_blur": 0, "mandara_config": 0, "mandara_wallgen": 0}
        l_store = self.doc["providers"]["lucid"]

        # 1. Reconcile ~/.config/quickshell/lucidprefs/prefs.json
        if self.lucid_prefs_path.exists():
            cur_hash = _sha256_file(self.lucid_prefs_path)
            rec = ledger.get("lucid_prefs", {})
            if cur_hash and cur_hash != rec.get("sha256"):
                disk_prefs = _read_json(self.lucid_prefs_path)
                prev_keys = rec.get("keys") or {}
                for k, disk_v in disk_prefs.items():
                    if k not in prev_keys or prev_keys.get(k) != disk_v:
                        if l_store["prefs"].get(k) != disk_v:
                            l_store["prefs"][k] = disk_v
                            absorbed["lucid_prefs"] += 1
                            # Keep scy.dock.* synchronized when user edits DockPage.qml directly!
                            if k == "dockStyle" and disk_v in ("island", "notch", "split") and self.doc["active_providers"].get("dock") == "lucid":
                                self.doc.setdefault("scy_native", {})["scy.dock.mode"] = disk_v
                            elif k == "dockIconSize" and isinstance(disk_v, int):
                                self.doc.setdefault("scy_native", {})["scy.dock.icon_size"] = disk_v
                            elif k == "dockSpacing" and isinstance(disk_v, int):
                                self.doc.setdefault("scy.dock.icon_spacing", disk_v)
                # Unpack updated hyprOptions / lockWidgetOpts if changed on disk
                raw_ho = disk_prefs.get("hyprOptions")
                if isinstance(raw_ho, str) and raw_ho.strip().startswith("{"):
                    try:
                        ho = json.loads(raw_ho)
                        if isinstance(ho, dict):
                            l_store["hypr"].update(ho)
                    except Exception:
                        pass
                raw_lo = disk_prefs.get("lockWidgetOpts")
                if isinstance(raw_lo, str) and raw_lo.strip().startswith("{"):
                    try:
                        lo = json.loads(raw_lo)
                        if isinstance(lo, dict):
                            for wid, wmap in lo.items():
                                if isinstance(wmap, dict):
                                    for ok, ov in wmap.items():
                                        l_store["lock_widgets"][f"lockOpts.{wid}.{ok}"] = ov
                    except Exception:
                        pass

        # 2. Reconcile blur.json
        if self.lucid_blur_path.exists():
            cur_hash = _sha256_file(self.lucid_blur_path)
            rec = ledger.get("lucid_blur", {})
            if cur_hash and cur_hash != rec.get("sha256"):
                disk_blur = _read_json(self.lucid_blur_path)
                for k, v in disk_blur.items():
                    if l_store["glass"].get(k) != v:
                        l_store["glass"][k] = v
                        absorbed["lucid_blur"] += 1

        # 3. Reconcile mandara/config.toml (excluding Scy-managed [scy_gates])
        m_store = self.doc["providers"]["mandara"]
        if self.mandara_config_path.exists():
            cur_hash = _sha256_file(self.mandara_config_path)
            rec = ledger.get("mandara_config", {})
            if cur_hash and cur_hash != rec.get("sha256"):
                try:
                    disk_m = load_toml(self.mandara_config_path)
                    disk_m.pop("scy_gates", None)
                    self._deep_merge(m_store["config"], disk_m)
                    absorbed["mandara_config"] += 1
                except Exception as exc:
                    self.log_persistence_error(f"Ignored malformed mandara/config.toml during reconcile: {exc}")

        if self.mandara_wallgen_path.exists():
            cur_hash = _sha256_file(self.mandara_wallgen_path)
            rec = ledger.get("mandara_wallgen", {})
            if cur_hash and cur_hash != rec.get("sha256"):
                try:
                    disk_w = load_toml(self.mandara_wallgen_path)
                    self._deep_merge(m_store["wallgen"], disk_w)
                    absorbed["mandara_wallgen"] += 1
                except Exception as exc:
                    self.log_persistence_error(f"Ignored malformed mandara/wallgen.toml during reconcile: {exc}")

        return absorbed

    def reconcile_startup_state(self) -> dict[str, int]:
        """Reconcile external session edits via persistence-ledger.json and flush atomic state."""
        absorbed = self.reconcile_live_engine_stores()
        self.flush_all()
        return absorbed

    def import_existing_engine_configs(self) -> None:
        """Non-destructively pull existing standalone Lucid or Mandara user settings on first run."""
        l_store = self.doc["providers"]["lucid"]
        if self.lucid_prefs_path.exists() and not l_store["prefs"]:
            l_store["prefs"] = _read_json(self.lucid_prefs_path)
            raw_ho = l_store["prefs"].get("hyprOptions")
            if isinstance(raw_ho, str) and raw_ho.strip().startswith("{") and not l_store["hypr"]:
                try:
                    ho = json.loads(raw_ho)
                    if isinstance(ho, dict):
                        l_store["hypr"].update(ho)
                except Exception:
                    pass
            raw_lo = l_store["prefs"].get("lockWidgetOpts")
            if isinstance(raw_lo, str) and raw_lo.strip().startswith("{") and not l_store["lock_widgets"]:
                try:
                    lo = json.loads(raw_lo)
                    if isinstance(lo, dict):
                        for wid, wmap in lo.items():
                            if isinstance(wmap, dict):
                                for ok, ov in wmap.items():
                                    l_store["lock_widgets"][f"lockOpts.{wid}.{ok}"] = ov
                except Exception:
                    pass

        if self.lucid_blur_path.exists() and not l_store["glass"]:
            l_store["glass"] = _read_json(self.lucid_blur_path)

        wpath = self.lucid_widgets_path if self.lucid_widgets_path.exists() else self.lucid_widgets_legacy_path
        if wpath.exists() and not l_store["widget_opts"]:
            wdoc = _read_json(wpath)
            for wtype, opts in (wdoc.get("scyWidgetDefaults") or {}).items():
                if isinstance(opts, dict):
                    for ok, ov in opts.items():
                        l_store["widget_opts"][f"widgets.{wtype}.{ok}"] = ov
            for inst in (wdoc.get("instances") or []):
                if isinstance(inst, dict) and isinstance(inst.get("opts"), dict) and inst.get("type"):
                    wtype = inst["type"]
                    for ok, ov in inst["opts"].items():
                        l_store["widget_opts"].setdefault(f"widgets.{wtype}.{ok}", ov)

        if (self.lucid_moji_config_path.exists() or self.lucid_moji_state_path.exists()) and "moji" not in l_store["apps"]:
            merged_moji: dict[str, Any] = {}
            merged_moji.update(_read_json(self.lucid_moji_state_path))
            merged_moji.update(_read_json(self.lucid_moji_config_path))
            if merged_moji:
                l_store["apps"]["moji"] = merged_moji

        for app_key, ap in self.lucid_app_paths.items():
            if ap.exists() and app_key not in l_store["apps"]:
                l_store["apps"][app_key] = _read_json(ap)

        if self.lucid_sddm_stage_path.exists() and not l_store["sddm"]:
            l_store["sddm"] = _parse_ini_general(self.lucid_sddm_stage_path)

        m_store = self.doc["providers"]["mandara"]
        if self.mandara_config_path.exists() and not m_store["config"]:
            m_store["config"] = load_toml(self.mandara_config_path)
        if self.mandara_wallgen_path.exists() and not m_store["wallgen"]:
            m_store["wallgen"] = load_toml(self.mandara_wallgen_path)
        if self.mandara_greeter_stage_path.exists() and not m_store["greeter"]:
            m_store["greeter"] = load_toml(self.mandara_greeter_stage_path)

    def _backup_targets(self) -> list[tuple[str, Path]]:
        targets: list[tuple[str, Path]] = [
            ("scy_config.toml", self.config_path),
            ("scy_dock.json", self.dock_config_path),
            ("scy_pinned_apps.json", self.pinned_apps_path),
            ("scy_design_tokens.json", self.design_tokens_path),
            ("scy_login_greeter.json", self.login_greeter_path),
            ("lucid_prefs.json", self.lucid_prefs_path),
            ("lucid_pinned.json", self.lucid_pinned_path),
            ("lucid_settings.lua", self.lucid_hypr_lua_path),
            ("lucid_blur.json", self.lucid_blur_path),
            ("lucid_widgets.json", self.lucid_widgets_path),
            ("lucid_moji_config.json", self.lucid_moji_config_path),
            ("lucid_moji_state.json", self.lucid_moji_state_path),
            ("lucid_sddm_stage.conf", self.lucid_sddm_stage_path),
            ("mandara_config.toml", self.mandara_config_path),
            ("mandara_wallgen.toml", self.mandara_wallgen_path),
            ("mandara_greeter.toml", self.mandara_greeter_stage_path),
        ]
        for app_k, ap in self.lucid_app_paths.items():
            targets.append((f"lucid_app_{app_k}.json", ap))
        return targets

    def _validate_restore_destination(self, raw_dest: str) -> Path:
        if not isinstance(raw_dest, str) or not raw_dest.strip() or "\x00" in raw_dest:
            raise ValueError(f"Invalid destination path in backup manifest: {raw_dest!r}")
        dst_raw = Path(raw_dest)
        if not dst_raw.is_absolute():
            raise ValueError(f"Backup destination path must be absolute: {raw_dest!r}")
        if dst_raw.is_symlink():
            raise ValueError(f"Refusing to overwrite symlink destination: {dst_raw}")
        dst = dst_raw.resolve()
        allowed_roots = (
            (self.home / ".config").resolve(),
            (self.home / ".local" / "state").resolve(),
            (self.home / ".local" / "share" / "scy-shell").resolve(),
        )
        if not any(dst.is_relative_to(root) for root in allowed_roots):
            raise ValueError(f"Unsafe backup destination outside managed user directories: {raw_dest}")
        if dst.is_relative_to(self.backup_root.resolve()):
            raise ValueError(f"Refusing to restore into backup storage directory: {raw_dest}")
        return dst

    @staticmethod
    def _atomic_copy_file(src: Path, dst: Path) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.parent / f".{dst.name}.scy-restore-{os.getpid()}-{time.time_ns()}.tmp"
        try:
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise

    def resolve_backup_dir(self, backup_ref: str | Path) -> Path:
        raw_str = str(backup_ref).strip() if backup_ref is not None else ""
        if not raw_str or "\x00" in raw_str:
            raise ValueError("Backup path or snapshot name must not be empty")
        candidate = Path(raw_str).expanduser()
        if not candidate.exists() and "/" not in raw_str and "\\" not in raw_str and raw_str not in (".", ".."):
            named = self.backup_root / raw_str
            if named.exists():
                candidate = named
        if candidate.is_symlink():
            raise ValueError(f"Refusing symlinked backup path: {candidate}")
        if not candidate.exists():
            raise FileNotFoundError(f"Backup directory does not exist: {candidate}")
        resolved = candidate.resolve()
        if not resolved.is_dir():
            raise ValueError(f"Backup path is not a directory: {resolved}")
        return resolved

    def create_backup(self, tag: str = "manual") -> Path:
        safe_tag = "".join(ch if (ch.isalnum() or ch in "-_") else "-" for ch in (tag or "manual")).strip("-") or "manual"
        ts = time.strftime("%Y%m%d-%H%M%S")
        bdir = self.backup_root / f"{ts}-{safe_tag}-{int(time.time_ns() % 100000)}"
        bdir.mkdir(parents=True, exist_ok=True)

        manifest_files: dict[str, str] = {}
        absent_files: list[str] = []
        for alias, src in self._backup_targets():
            if src.exists():
                self._atomic_copy_file(src, bdir / alias)
                manifest_files[alias] = str(src)
            else:
                absent_files.append(str(src))
        _write_json(
            bdir / "manifest.json",
            {
                "created_at": ts,
                "tag": safe_tag,
                "home": str(self.home),
                "files": manifest_files,
                "absent_files": absent_files,
            },
        )
        return bdir

    def restore_backup(self, backup_dir: str | Path) -> list[str]:
        bdir = self.resolve_backup_dir(backup_dir)
        mpath = bdir / "manifest.json"
        if mpath.is_symlink():
            raise ValueError(f"Refusing symlinked manifest in {bdir}")
        if not mpath.exists() or not mpath.is_file():
            raise FileNotFoundError(f"Backup manifest missing in {bdir}")

        try:
            manifest = json.loads(mpath.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError(f"Invalid JSON in backup manifest {mpath}: {exc}") from exc
        if not isinstance(manifest, dict):
            raise ValueError(f"Backup manifest in {bdir} must be a JSON object")

        raw_files = manifest.get("files")
        if not isinstance(raw_files, dict):
            raise ValueError(f"Backup manifest in {bdir} missing valid 'files' mapping")
        raw_absent = manifest.get("absent_files", [])
        if not isinstance(raw_absent, list):
            raise ValueError(f"Backup manifest in {bdir} has invalid 'absent_files' list")

        validated_copies: list[tuple[Path, Path, str]] = []
        seen_dests: set[Path] = set()
        for alias, orig_str in raw_files.items():
            if not isinstance(alias, str) or not alias or "/" in alias or "\\" in alias or alias in (".", ".."):
                raise ValueError(f"Invalid file alias in backup manifest: {alias!r}")
            src_raw = bdir / alias
            if src_raw.is_symlink():
                raise ValueError(f"Refusing symlinked payload file in backup: {src_raw}")
            src = src_raw.resolve()
            if not src.is_relative_to(bdir) or not src.exists() or not src.is_file():
                raise ValueError(f"Missing or invalid backup payload file for '{alias}' in {bdir}")
            dst = self._validate_restore_destination(orig_str)
            seen_dests.add(dst)
            validated_copies.append((src, dst, orig_str))

        validated_absent: list[Path] = []
        for orig_str in raw_absent:
            dst = self._validate_restore_destination(orig_str)
            if dst not in seen_dests:
                validated_absent.append(dst)

        rollback_bytes: dict[Path, bytes | None] = {}
        for _, dst, _ in validated_copies:
            rollback_bytes[dst] = dst.read_bytes() if dst.exists() else None
        for dst in validated_absent:
            rollback_bytes[dst] = dst.read_bytes() if dst.exists() else None

        restored: list[str] = []
        try:
            for src, dst, orig_str in validated_copies:
                self._atomic_copy_file(src, dst)
                restored.append(orig_str)
            for dst in validated_absent:
                if dst.exists():
                    dst.unlink()

            self.doc = self._load_or_init()
            self.import_existing_engine_configs()
            self._save_ledger()
            self.flush_runtime_state()
        except Exception:
            for dst, prev in rollback_bytes.items():
                try:
                    if prev is None:
                        dst.unlink(missing_ok=True)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        rtmp = dst.parent / f".{dst.name}.scy-rollback-{os.getpid()}-{time.time_ns()}.tmp"
                        rtmp.write_bytes(prev)
                        os.replace(rtmp, dst)
                except Exception:
                    pass
            try:
                self.doc = self._load_or_init()
                self.flush_runtime_state()
            except Exception:
                pass
            raise

        return restored

    # --- Provider & Presentation Switching (Internal Engine Routing) ---
    def get_provider(self, domain: str) -> Any:
        return self.doc["active_providers"].get(domain)

    def set_provider(self, domain: str, provider: str | dict[str, str]) -> tuple[bool, str]:
        ok, msg = self.schema.validate_provider(domain, provider)
        if not ok:
            return False, msg
        old_val = self.doc["active_providers"].get(domain)
        if self.doc["safety"].get("auto_backup", True) and self.config_path.exists():
            self.create_backup(f"provider-{domain}")
        self.doc["active_providers"][domain] = provider
        if domain == "dock" and isinstance(provider, str):
            sn = self.doc.setdefault("scy_native", {})
            if provider == "none":
                sn["scy.dock.mode"] = "disabled"
            elif provider == "mandara":
                sn["scy.dock.mode"] = "rail"
            else:
                cur_m = sn.get("scy.dock.mode", "")
                l_style = str(self.doc["providers"]["lucid"]["prefs"].get("dockStyle", "island"))
                fallback_m = l_style if l_style in ("island", "notch", "split") else "island"
                sn["scy.dock.mode"] = cur_m if cur_m in ("island", "notch", "split") else fallback_m
            self._sync_dock_single_owner_state()
        self._apply_exclusive_gates_to_engine_configs()
        self._record_change("provider.set", domain, old_val, provider)
        self.flush_all()
        return True, f"{domain} provider set to {provider}"

    def set_presentation(self, domain: str, value: str) -> tuple[bool, str]:
        ok, msg = self.schema.validate_presentation(domain, value)
        if not ok:
            return False, msg
        old_val = self.doc["presentations"].get(domain)
        self.doc["presentations"][domain] = value
        if domain in ("primary_identity", "mandara_surface_look"):
            self.doc["identity"]["primary_style"] = value
            if get_pointer(self.doc["providers"]["mandara"]["config"], "/looks/active", None) is None:
                set_pointer(self.doc["providers"]["mandara"]["config"], "/looks/active", value)
        self._record_change("presentation.set", domain, old_val, value)
        self.flush_all()
        return True, f"{domain} presentation set to {value}"

    def _sync_dock_single_owner_state(self, propagate_dock_tuning: bool = False) -> None:
        """Guarantees a single authoritative dock instance across Lucid QML (`Prefs.dockEnabled`)
        and Mandara Rust (`[scy_gates].dock_mode` + `[dock].enabled` + `[plugins].disabled`)."""
        sn = self.doc.setdefault("scy_native", {})
        l_prefs = self.doc["providers"]["lucid"]["prefs"]
        m_cfg = self.doc["providers"]["mandara"]["config"]

        dock_mode = str(sn.get("scy.dock.mode") or "")
        if not dock_mode:
            ap_dock = self.doc["active_providers"].get("dock", "lucid")
            if ap_dock == "none":
                dock_mode = "disabled"
            elif ap_dock == "mandara":
                dock_mode = "rail"
            else:
                dock_mode = str(l_prefs.get("dockStyle") or "island")

        if dock_mode == "disabled":
            self.doc["active_providers"]["dock"] = "none"
            l_prefs["dockEnabled"] = False
            set_pointer(m_cfg, "/dock/enabled", False)
            self._set_mandara_dock_plugin_enabled(False)
        elif dock_mode == "rail":
            self.doc["active_providers"]["dock"] = "mandara"
            l_prefs["dockEnabled"] = False
            set_pointer(m_cfg, "/dock/enabled", True)
            self._set_mandara_dock_plugin_enabled(True)
        else:
            # Primary Scy-Shell Dock (Lucid-inspired island / notch / split)
            self.doc["active_providers"]["dock"] = "lucid"
            l_prefs["dockEnabled"] = True
            if dock_mode in ("island", "notch", "split"):
                l_prefs["dockStyle"] = dock_mode
            set_pointer(m_cfg, "/dock/enabled", False)
            self._set_mandara_dock_plugin_enabled(False)

        if not propagate_dock_tuning:
            return

        # Propagate granular Dock Studio controls to both native engines
        if "scy.dock.icon_size" in sn:
            sz = int(sn["scy.dock.icon_size"])
            l_prefs["dockIconSize"] = sz
            set_pointer(m_cfg, "/dock/icon_size", sz)
        if "scy.dock.icon_spacing" in sn:
            sp = int(sn["scy.dock.icon_spacing"])
            l_prefs["dockSpacing"] = sp
        if "scy.dock.padding_inner" in sn:
            l_prefs["dockIconPadding"] = int(sn["scy.dock.padding_inner"])
        if "scy.dock.float_offset_y" in sn:
            l_prefs["dockBottomMargin"] = int(sn["scy.dock.float_offset_y"])
            set_pointer(m_cfg, "/dock/margin", int(sn["scy.dock.float_offset_y"]))
        if "scy.dock.magnify_enabled" in sn:
            mag = bool(sn["scy.dock.magnify_enabled"])
            l_prefs["dockMagnify"] = mag
            set_pointer(m_cfg, "/dock/magnification", mag)
        if "scy.dock.magnify_scale" in sn:
            sc = float(sn["scy.dock.magnify_scale"])
            l_prefs["dockHoverEffect"] = max(0.0, min(2.0, sc))
            set_pointer(m_cfg, "/dock/magnify", max(0, min(100, int(round((sc - 1.0) * 100)))))
        if "scy.dock.placement" in sn:
            pl = str(sn["scy.dock.placement"])
            if pl in ("bottom", "left", "right"):
                set_pointer(m_cfg, "/dock/position", pl)
        if "scy.dock.auto_hide_mode" in sn:
            ah = str(sn["scy.dock.auto_hide_mode"])
            l_prefs["dockAutoHide"] = ah != "never"
            l_prefs["dockDynamicHide"] = ah in ("dodge-windows", "dodge-maximized")

    def _set_mandara_dock_plugin_enabled(self, enabled: bool) -> None:
        p_tbl = self.doc["providers"]["mandara"]["config"].setdefault("plugins", {})
        en = [x for x in (p_tbl.get("enabled") or []) if isinstance(x, str)]
        dis = [x for x in (p_tbl.get("disabled") or []) if isinstance(x, str)]
        if enabled:
            if "dock" not in en:
                en.append("dock")
            dis = [x for x in dis if x != "dock"]
        else:
            en = [x for x in en if x != "dock"]
            if "dock" not in dis:
                dis.append("dock")
        p_tbl["enabled"] = en
        p_tbl["disabled"] = dis

    def _apply_dock_preset(self, preset: str) -> None:
        sn = self.doc.setdefault("scy_native", {})
        presets: dict[str, dict[str, Any]] = {
            "lucid-signature": {
                "scy.dock.mode": "island",
                "scy.dock.placement": "bottom",
                "scy.dock.icon_size": 42,
                "scy.dock.icon_spacing": 12,
                "scy.dock.magnify_enabled": True,
                "scy.dock.magnify_scale": 1.35,
                "scy.dock.float_offset_y": 14,
            },
            "carved-notch": {
                "scy.dock.mode": "notch",
                "scy.dock.placement": "bottom",
                "scy.dock.icon_size": 40,
                "scy.dock.icon_spacing": 10,
                "scy.dock.float_offset_y": 0,
            },
            "trinity-split": {
                "scy.dock.mode": "split",
                "scy.dock.placement": "bottom",
                "scy.dock.icon_size": 42,
                "scy.dock.icon_spacing": 12,
                "scy.dock.show_separators": True,
            },
            "left-studio-rail": {
                "scy.dock.mode": "island",
                "scy.dock.placement": "left",
                "scy.dock.icon_size": 38,
                "scy.dock.icon_spacing": 8,
                "scy.dock.magnify_enabled": False,
            },
            "minimal-float": {
                "scy.dock.mode": "island",
                "scy.dock.placement": "floating",
                "scy.dock.icon_size": 34,
                "scy.dock.icon_spacing": 8,
                "scy.dock.float_offset_y": 18,
                "scy.dock.auto_hide_mode": "dodge-windows",
            },
        }
        if preset in presets:
            sn.update(presets[preset])

    def _apply_performance_tier(self, tier: str) -> None:
        sn = self.doc.setdefault("scy_native", {})
        l_prefs = self.doc["providers"]["lucid"]["prefs"]
        if tier == "max-quality":
            sn["scy.effects.blur_strength"] = 4
            sn["scy.effects.blur_radius"] = 12
            sn["scy.effects.shadow_softness"] = 36
            sn["scy.effects.duration_scale"] = 1.0
            self.doc["identity"]["reduced_motion"] = False
            l_prefs["specialBlur"] = True
        elif tier == "balanced":
            sn["scy.effects.blur_strength"] = 3
            sn["scy.effects.blur_radius"] = 8
            sn["scy.effects.shadow_softness"] = 24
            sn["scy.effects.duration_scale"] = 1.0
            self.doc["identity"]["reduced_motion"] = False
            l_prefs["specialBlur"] = True
        elif tier == "performance":
            sn["scy.effects.blur_strength"] = 1
            sn["scy.effects.blur_radius"] = 4
            sn["scy.effects.shadow_softness"] = 8
            keep_anim = bool(sn.get("scy.performance.keep_animations_on_perf", True))
            sn["scy.effects.duration_scale"] = 0.65 if keep_anim else 0.0
            self.doc["identity"]["reduced_motion"] = not keep_anim
        elif tier == "battery":
            keep_blur = bool(sn.get("scy.performance.keep_blur_on_battery", False))
            sn["scy.effects.blur_strength"] = 2 if keep_blur else 0
            sn["scy.effects.blur_radius"] = 6 if keep_blur else 0
            sn["scy.effects.shadow_softness"] = 0
            sn["scy.effects.duration_scale"] = 0.4
            l_prefs["specialBlur"] = keep_blur

    def _apply_exclusive_gates_to_engine_configs(self) -> None:
        """Synchronize exclusive resource flags into Mandara's [scy_gates] without altering user settings."""
        self._sync_dock_single_owner_state()
        ap = self.doc["active_providers"]
        mcfg = self.doc["providers"]["mandara"]["config"]
        mcfg["scy_gates"] = {
            "managed_by_scy_shell": True,
            "owns_notifications": ap.get("notifications") == "mandara",
            "owns_polkit": ap.get("polkit") == "mandara",
            "owns_lock": ap.get("lock_screen") == "mandara",
            "owns_idle": ap.get("idle") == "mandara",
            "owns_night_light": ap.get("night_light") == "mandara",
            "owns_bt_agent": ap.get("bt_agent") == "mandara",
            "owns_clipboard": ap.get("clipboard") == "mandara",
            "owns_wallpaper": ap.get("wallpaper") == "mandara",
            "bar_mode": ap.get("bar", "lucid"),
            "dock_mode": ap.get("dock", "lucid"),
            "launcher_mode": ap.get("launcher", "lucid"),
            "desktop_widgets_mode": ap.get("desktop_widgets", "lucid"),
            "toast_renderer": self.doc["presentations"].get("toasts", "lucid"),
            "osd_renderer": ap.get("osd", "lucid"),
        }

    # --- Universal Type-Aware Setting Get / Set / Reset / Section Reset / Live Preview ---
    def get_setting(self, scy_id: str) -> Any:
        meta = self.schema.by_id.get(scy_id)
        if meta is None:
            raise KeyError(f"Unknown setting ID: {scy_id}")
        return self._read_meta_value(meta)

    def set_setting(
        self,
        scy_id: str,
        value: Any,
        flush: bool = True,
        validate: bool = True,
    ) -> SettingMeta:
        meta = self.schema.by_id.get(scy_id)
        if meta is None:
            raise KeyError(f"Unknown setting ID: {scy_id}")
        old_val = self._read_meta_value(meta)
        coerced = self.schema.validate_and_coerce(scy_id, value) if validate else value
        self._write_meta_value(meta, coerced)
        self._record_change("setting.set", scy_id, old_val, coerced)
        if flush:
            self.flush_all()
        return meta

    def reset_setting(self, scy_id: str, flush: bool = True) -> SettingMeta:
        meta = self.schema.by_id.get(scy_id)
        if meta is None:
            raise KeyError(f"Unknown setting ID: {scy_id}")
        old_val = self._read_meta_value(meta)
        if meta.source_project == "scy":
            self.doc.get("scy_native", {}).pop(scy_id, None)
        else:
            self._write_meta_value(meta, meta.default_value)
        self._record_change("setting.reset", scy_id, old_val, meta.default_value)
        if flush:
            self.flush_all()
        return meta

    def reset_section(self, section_id: str, create_backup: bool = True) -> dict[str, Any]:
        """Resets all modified settings belonging to one unified Studio section (01..15) back to defaults."""
        metas = self.schema.by_section(section_id)
        if not metas:
            raise ValueError(f"Unknown Studio section: {section_id}")
        if create_backup and self.config_path.exists():
            self.create_backup(tag=f"reset-sec-{section_id[:2]}")
        reset_keys: list[str] = []
        for meta in metas:
            if self._read_meta_value(meta) != meta.default_value:
                if meta.source_project == "scy":
                    self.doc.get("scy_native", {}).pop(meta.scy_id, None)
                else:
                    self._write_meta_value(meta, meta.default_value)
                reset_keys.append(meta.scy_id)
        self._record_change("section.reset", section_id, len(reset_keys), 0)
        self.flush_all()
        return {"section": section_id, "reset_count": len(reset_keys), "reset_keys": reset_keys}

    # --- Transactional Live Preview (Before / After / Apply / Revert) ---
    def stage_preview(self, changes: dict[str, Any]) -> dict[str, Any]:
        """Applies live preview changes immediately while recording a Before baseline for instant Revert."""
        if not self.preview_baseline_path.exists():
            baseline: dict[str, Any] = {}
            for sid in changes:
                if sid in self.schema.by_id:
                    baseline[sid] = self.get_setting(sid)
            _write_json(self.preview_baseline_path, {"created_at_ms": int(time.time() * 1000), "before": baseline})
        else:
            cur_base = _read_json(self.preview_baseline_path)
            before_map = cur_base.setdefault("before", {})
            for sid in changes:
                if sid in self.schema.by_id and sid not in before_map:
                    before_map[sid] = self.get_setting(sid)
            _write_json(self.preview_baseline_path, cur_base)

        applied: dict[str, Any] = {}
        for sid, val in changes.items():
            self.set_setting(sid, val, flush=False, validate=True)
            applied[sid] = self.get_setting(sid)
        self.flush_all()
        return self.get_preview_diff()

    def get_preview_diff(self) -> dict[str, Any]:
        if not self.preview_baseline_path.exists():
            return {"active": False, "changes": []}
        base = _read_json(self.preview_baseline_path)
        before_map = base.get("before") or {}
        diffs = []
        for sid, before_val in before_map.items():
            after_val = self.get_setting(sid)
            if before_val != after_val:
                diffs.append({"scy_id": sid, "before": before_val, "after": after_val})
        return {"active": len(diffs) > 0, "changes": diffs}

    preview_diff = get_preview_diff

    def commit_preview(self) -> dict[str, Any]:
        diff = self.get_preview_diff()
        self.preview_baseline_path.unlink(missing_ok=True)
        self.flush_runtime_state()
        return {"committed": True, "count": len(diff["changes"])}

    def revert_preview(self) -> dict[str, Any]:
        if not self.preview_baseline_path.exists():
            return {"reverted": False, "count": 0}
        base = _read_json(self.preview_baseline_path)
        before_map = base.get("before") or {}
        for sid, before_val in before_map.items():
            if sid in self.schema.by_id:
                self.set_setting(sid, before_val, flush=False, validate=False)
        self.preview_baseline_path.unlink(missing_ok=True)
        self.flush_all()
        return {"reverted": True, "count": len(before_map)}

    def get_all_values(self) -> dict[str, Any]:
        return {sid: self._read_meta_value(meta) for sid, meta in self.schema.by_id.items()}

    def _read_meta_value(self, meta: SettingMeta) -> Any:
        if meta.source_project == "scy":
            sn = self.doc.get("scy_native") or {}
            return sn.get(meta.scy_id, meta.default_value)

        if meta.source_project == "lucid":
            l_store = self.doc["providers"]["lucid"]
            if meta.scy_id.startswith("scy.providers.lucid.prefs."):
                return l_store["prefs"].get(meta.original_key, meta.default_value)
            if meta.scy_id.startswith("scy.providers.lucid.hypr."):
                return l_store["hypr"].get(meta.original_key, meta.default_value)
            if meta.scy_id == "scy.providers.lucid.glass.blurValue":
                return l_store["glass"].get("value", meta.default_value)
            if meta.scy_id.startswith("scy.providers.lucid.widget_opts."):
                return l_store["widget_opts"].get(meta.original_key, meta.default_value)
            if meta.scy_id.startswith("scy.providers.lucid.lock_widgets."):
                return l_store["lock_widgets"].get(meta.original_key, meta.default_value)
            if meta.scy_id.startswith("scy.providers.lucid.sddm."):
                k = meta.original_key.split(".", 1)[1]
                return l_store["sddm"].get(k, meta.default_value)
            parts = meta.scy_id.split(".")
            app_name, prop = parts[3], parts[4]
            return l_store["apps"].get(app_name, {}).get(prop, meta.default_value)

        m_store = self.doc["providers"]["mandara"]
        if meta.scy_id.startswith("scy.providers.mandara.config."):
            val = get_pointer(m_store["config"], meta.original_key, None)
            return meta.default_value if val is None else val
        if meta.scy_id.startswith("scy.providers.mandara.wallgen."):
            ptr = "/" + meta.original_key.replace(".", "/").removeprefix("wallgen/")
            val = get_pointer(m_store["wallgen"], ptr, None)
            return meta.default_value if val is None else val
        if meta.scy_id.startswith("scy.providers.mandara.greeter."):
            ptr = "/" + meta.original_key.replace(".", "/").removeprefix("greeter/")
            val = get_pointer(m_store["greeter"], ptr, None)
            return meta.default_value if val is None else val
        return meta.default_value

    def _write_meta_value(self, meta: SettingMeta, value: Any) -> None:
        if meta.source_project == "scy":
            sn = self.doc.setdefault("scy_native", {})
            sn[meta.scy_id] = value
            # Wire Scy-Shell native controls directly to real runtime subsystems
            if meta.scy_id == "scy.dock.preset":
                self._apply_dock_preset(str(value))
            if meta.scy_id.startswith("scy.dock."):
                self._sync_dock_single_owner_state(propagate_dock_tuning=(meta.scy_id != "scy.dock.mode"))
            elif meta.scy_id == "scy.performance.tier":
                self._apply_performance_tier(str(value))
            elif meta.scy_id == "scy.design.ui_font":
                self.doc["identity"]["font_family"] = str(value)
                self.doc["providers"]["lucid"]["prefs"]["fontFamily"] = str(value)
            elif meta.scy_id == "scy.design.mono_font":
                self.doc["identity"]["mono_font_family"] = str(value)
            elif meta.scy_id == "scy.login.mirror_lock_layout":
                self.doc["providers"]["lucid"]["prefs"]["lockLoginSync"] = bool(value)
            elif meta.scy_id == "scy.login.greeter_target":
                mapping = {"preserve": "preserve", "scy-sddm": "lucid-sddm", "scy-greetd": "mandara-greetd"}
                self.doc["active_providers"]["display_manager"] = mapping.get(str(value), "preserve")
            elif meta.scy_id == "scy.windows.layout_engine":
                self.doc["providers"]["lucid"]["hypr"]["general.layout"] = str(value)
            elif meta.scy_id == "scy.windows.dim_inactive":
                self.doc["providers"]["lucid"]["hypr"]["decoration.dim_inactive"] = bool(value)
            elif meta.scy_id == "scy.windows.dim_strength":
                pct = int(round(float(value) * 100)) if float(value) <= 1.0 else int(round(float(value)))
                self.doc["providers"]["lucid"]["hypr"]["decoration.dim_strength"] = max(5, min(80, pct))
            return

        if meta.source_project == "lucid":
            l_store = self.doc["providers"]["lucid"]
            if meta.scy_id.startswith("scy.providers.lucid.prefs."):
                l_store["prefs"][meta.original_key] = value
                if meta.original_key == "dockStyle" and value in ("island", "notch", "split"):
                    self.doc.setdefault("scy_native", {})["scy.dock.mode"] = value
                elif meta.original_key == "dockEnabled" and value is False and self.doc["active_providers"].get("dock") == "lucid":
                    self.doc.setdefault("scy_native", {})["scy.dock.mode"] = "disabled"
                elif meta.original_key == "hyprOptions" and isinstance(value, str):
                    try:
                        ho = json.loads(value)
                        if isinstance(ho, dict):
                            l_store["hypr"].update(ho)
                    except Exception:
                        pass
                elif meta.original_key == "lockWidgetOpts" and isinstance(value, str):
                    try:
                        lo = json.loads(value) if value.strip() else {}
                        if isinstance(lo, dict):
                            for wid, wmap in lo.items():
                                if isinstance(wmap, dict):
                                    for ok, ov in wmap.items():
                                        l_store["lock_widgets"][f"lockOpts.{wid}.{ok}"] = ov
                    except Exception:
                        pass
                return

            if meta.scy_id.startswith("scy.providers.lucid.hypr."):
                l_store["hypr"][meta.original_key] = value
                raw_ho = l_store["prefs"].get("hyprOptions", "{}")
                try:
                    parsed_ho = json.loads(raw_ho) if isinstance(raw_ho, str) and raw_ho.strip() else {}
                    if not isinstance(parsed_ho, dict):
                        parsed_ho = {}
                except Exception:
                    parsed_ho = {}
                parsed_ho[meta.original_key] = value
                if "hyprOptions" not in l_store["prefs"] or raw_ho == "{}" or str(raw_ho).startswith("{"):
                    l_store["prefs"]["hyprOptions"] = json.dumps(parsed_ho)
                return

            if meta.scy_id == "scy.providers.lucid.glass.blurValue":
                l_store["glass"]["value"] = float(value)
                return

            if meta.scy_id.startswith("scy.providers.lucid.widget_opts."):
                l_store["widget_opts"][meta.original_key] = value
                return

            if meta.scy_id.startswith("scy.providers.lucid.lock_widgets."):
                l_store["lock_widgets"][meta.original_key] = value
                raw_lo = l_store["prefs"].get("lockWidgetOpts", "")
                try:
                    parsed_lo = json.loads(raw_lo) if isinstance(raw_lo, str) and raw_lo.strip().startswith("{") else {}
                    if not isinstance(parsed_lo, dict):
                        parsed_lo = {}
                except Exception:
                    parsed_lo = {}
                kparts = meta.original_key.split(".", 2)
                if len(kparts) == 3:
                    _, wid, opt = kparts
                    parsed_lo.setdefault(wid, {})[opt] = value
                    if "lockWidgetOpts" not in l_store["prefs"] or raw_lo == "" or str(raw_lo).startswith("{"):
                        l_store["prefs"]["lockWidgetOpts"] = json.dumps(parsed_lo)
                return

            if meta.scy_id.startswith("scy.providers.lucid.sddm."):
                k = meta.original_key.split(".", 1)[1]
                l_store["sddm"][k] = value
                return

            parts = meta.scy_id.split(".")
            app_name, prop = parts[3], parts[4]
            l_store["apps"].setdefault(app_name, {})[prop] = value
            return

        # Mandara
        m_store = self.doc["providers"]["mandara"]
        if meta.scy_id.startswith("scy.providers.mandara.config."):
            if meta.value_type == "table":
                if not isinstance(value, dict):
                    raise TypeError(f"Setting {meta.scy_id} ({meta.original_key}) is a TOML table; expected dict")
                existing = get_pointer(m_store["config"], meta.original_key, {})
                merged = dict(existing) if isinstance(existing, dict) else {}
                self._deep_merge(merged, value)
                set_pointer(m_store["config"], meta.original_key, merged)
            else:
                set_pointer(m_store["config"], meta.original_key, value)
            return
        if meta.scy_id.startswith("scy.providers.mandara.wallgen."):
            ptr = "/" + meta.original_key.replace(".", "/").removeprefix("wallgen/")
            set_pointer(m_store["wallgen"], ptr, value)
            return
        if meta.scy_id.startswith("scy.providers.mandara.greeter."):
            ptr = "/" + meta.original_key.replace(".", "/").removeprefix("greeter/")
            set_pointer(m_store["greeter"], ptr, value)

    # --- Sync Pinned Apps Across Scy Dock, Lucid Dock & Mandara Dock ---
    def sync_pinned_apps(self, apps: list[str] | None = None) -> list[str]:
        if apps is None:
            if self.pinned_apps_path.exists():
                apps = json.loads(self.pinned_apps_path.read_text(encoding="utf-8"))
            elif self.lucid_pinned_path.exists():
                raw = json.loads(self.lucid_pinned_path.read_text(encoding="utf-8"))
                apps = raw if isinstance(raw, list) else raw.get("apps", [])
            else:
                apps = get_pointer(self.doc["providers"]["mandara"]["config"], "/dock/pinned", []) or []
        apps = [str(a) for a in apps]
        _write_json(self.pinned_apps_path, apps)
        _write_json(self.lucid_pinned_path, apps)
        set_pointer(self.doc["providers"]["mandara"]["config"], "/dock/pinned", apps)
        return apps

    def _collect_override_values(self) -> dict[str, Any]:
        overrides: dict[str, Any] = {}
        for sid, meta in self.schema.by_id.items():
            cur = self._read_meta_value(meta)
            if cur != meta.default_value:
                overrides[sid] = cur
        return overrides

    def _build_design_tokens_doc(self) -> dict[str, Any]:
        def val(sid: str) -> Any:
            m = self.schema.by_id.get(sid)
            return self._read_meta_value(m) if m else None

        return {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "typography": {
                "display_font": val("scy.design.display_font"),
                "ui_font": val("scy.design.ui_font"),
                "mono_font": val("scy.design.mono_font"),
                "heading_weight": val("scy.design.heading_weight"),
                "tracking_scale": val("scy.design.tracking_scale"),
                "icon_theme": val("scy.design.icon_theme"),
                "cursor_theme": val("scy.design.cursor_theme"),
                "cursor_size": val("scy.design.cursor_size"),
            },
            "colors": {
                "seed": self.doc["identity"].get("accent_seed", "#ffb1c4"),
                "dark_mode": bool(self.doc["identity"].get("dark_mode", True)),
                "wallpaper_extract": val("scy.design.wallpaper_extract"),
                "harmony": val("scy.design.palette_harmony"),
                "accent_intensity": val("scy.design.accent_intensity"),
                "component_accents": {
                    "bar": val("scy.design.bar_accent") if val("scy.design.bar_use_custom_accent") else "",
                    "dock": val("scy.design.dock_accent") if val("scy.design.dock_use_custom_accent") else "",
                    "control_center": val("scy.design.cc_accent") if val("scy.design.cc_use_custom_accent") else "",
                },
            },
            "materials": {
                "preset": val("scy.effects.material_preset"),
                "bg_opacity": val("scy.effects.bg_opacity"),
                "surface_opacity": val("scy.effects.surface_opacity"),
                "blur_strength": val("scy.effects.blur_strength"),
                "blur_radius": val("scy.effects.blur_radius"),
                "saturation": val("scy.effects.saturation"),
                "contrast": val("scy.effects.contrast"),
                "brightness": val("scy.effects.brightness"),
                "gradient_angle": val("scy.effects.gradient_angle"),
                "gradient_intensity": val("scy.effects.gradient_intensity"),
                "border_thickness": val("scy.effects.border_thickness"),
                "border_opacity": val("scy.effects.border_opacity"),
                "shadow_softness": val("scy.effects.shadow_softness"),
                "shadow_distance": val("scy.effects.shadow_distance"),
                "glow_intensity": val("scy.effects.glow_intensity"),
                "glass_reflection": val("scy.effects.glass_reflection"),
                "shader_preset": val("scy.effects.shader_preset"),
            },
            "motion": {
                "preset": val("scy.effects.motion_preset"),
                "duration_scale": val("scy.effects.duration_scale"),
                "delay_ms": val("scy.effects.delay_ms"),
                "spring_stiffness": val("scy.effects.spring_stiffness"),
                "spring_damping": val("scy.effects.spring_damping"),
                "entry_animation": val("scy.effects.entry_animation"),
                "exit_animation": val("scy.effects.exit_animation"),
                "workspace_animation": val("scy.effects.workspace_animation"),
            },
            "layout": {
                "preset": val("scy.layout.active_preset"),
                "global_scale": val("scy.layout.global_scale"),
                "corner_radius_scale": val("scy.layout.corner_radius_scale"),
                "spacing_scale": val("scy.layout.spacing_scale"),
                "outer_margin": val("scy.layout.outer_margin"),
                "bar_layer": val("scy.layout.bar_layer"),
                "multi_monitor_mode": val("scy.layout.multi_monitor_mode"),
                "compact_breakpoint": val("scy.layout.compact_breakpoint"),
            },
            "dynamic_island": {
                "enabled": val("scy.island.enabled"),
                "mode": val("scy.island.mode"),
                "width": val("scy.island.width"),
                "height": val("scy.island.height"),
                "expand_on_media": val("scy.island.expand_on_media"),
                "show_timer": val("scy.island.show_timer"),
                "show_notifications": val("scy.island.show_notifications"),
            },
            "dock": {
                "mode": val("scy.dock.mode"),
                "owner": self.doc["active_providers"].get("dock", "lucid"),
                "placement": val("scy.dock.placement"),
                "float_offset_x": val("scy.dock.float_offset_x"),
                "float_offset_y": val("scy.dock.float_offset_y"),
                "min_width": val("scy.dock.min_width"),
                "max_width": val("scy.dock.max_width"),
                "height_override": val("scy.dock.height_override"),
                "icon_size": val("scy.dock.icon_size"),
                "icon_spacing": val("scy.dock.icon_spacing"),
                "padding_inner": val("scy.dock.padding_inner"),
                "magnify_enabled": val("scy.dock.magnify_enabled"),
                "magnify_scale": val("scy.dock.magnify_scale"),
                "active_indicator": val("scy.dock.active_indicator"),
                "running_indicator": val("scy.dock.running_indicator"),
                "workspace_aware": val("scy.dock.workspace_aware"),
                "notification_badges": val("scy.dock.notification_badges"),
                "show_recent_apps": val("scy.dock.show_recent_apps"),
                "recent_limit": val("scy.dock.recent_limit"),
                "show_frequent_apps": val("scy.dock.show_frequent_apps"),
                "app_groups_enabled": val("scy.dock.app_groups_enabled"),
                "show_separators": val("scy.dock.show_separators"),
                "material": val("scy.dock.material"),
                "opacity": val("scy.dock.opacity"),
                "blur_enabled": val("scy.dock.blur_enabled"),
                "border_width": val("scy.dock.border_width"),
                "shadow_strength": val("scy.dock.shadow_strength"),
                "glow_strength": val("scy.dock.glow_strength"),
                "auto_hide_mode": val("scy.dock.auto_hide_mode"),
                "reveal_delay_ms": val("scy.dock.reveal_delay_ms"),
                "monitor_policy": val("scy.dock.monitor_policy"),
                "locked": val("scy.dock.locked"),
                "preset": val("scy.dock.preset"),
            },
            "lock_screen": {
                "clock_style": val("scy.lock.clock_style"),
                "date_format": val("scy.lock.date_format"),
                "show_weather": val("scy.lock.show_weather"),
                "show_media": val("scy.lock.show_media"),
                "notification_privacy": val("scy.lock.notification_privacy"),
                "wallpaper_override": val("scy.lock.wallpaper_override"),
                "glass_preset": val("scy.lock.glass_preset"),
                "show_avatar": val("scy.lock.show_avatar"),
                "auth_feedback": val("scy.lock.auth_feedback"),
                "show_system_info": val("scy.lock.show_system_info"),
            },
            "login_experience": {
                "greeter_target": val("scy.login.greeter_target"),
                "mirror_lock_layout": val("scy.login.mirror_lock_layout"),
                "user_list_style": val("scy.login.user_list_style"),
                "avatar_ring": val("scy.login.avatar_ring"),
                "password_style": val("scy.login.password_style"),
                "show_session_picker": val("scy.login.show_session_picker"),
                "show_power_actions": val("scy.login.show_power_actions"),
                "background_path": val("scy.login.background_path"),
                "background_blur": val("scy.login.background_blur"),
                "clock_24h": val("scy.login.clock_24h"),
                "login_animation": val("scy.login.login_animation"),
                "high_contrast": val("scy.login.high_contrast"),
                "ui_scale": val("scy.login.ui_scale"),
            },
        }

    def flush_runtime_state(self) -> None:
        overrides = self._collect_override_values()
        tokens_doc = self._build_design_tokens_doc()
        preview = self.get_preview_diff()
        state = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "updated_at_ms": int(time.time() * 1000),
            "identity": self.doc["identity"],
            "active_providers": self.doc["active_providers"],
            "presentations": self.doc["presentations"],
            "scy_gates": self.doc["providers"]["mandara"]["config"].get("scy_gates", {}),
            "dock_owner": self.doc["active_providers"].get("dock", "lucid"),
            "dock_mode": tokens_doc["dock"]["mode"],
            "active_profile": self.get_setting("scy.profiles.active"),
            "performance_tier": self.get_setting("scy.performance.tier"),
            "preview_active": preview["active"],
            "preview_change_count": len(preview["changes"]),
            "override_count": len(overrides),
        }
        _write_json(self.design_tokens_path, tokens_doc)
        _write_json(self.dock_config_path, tokens_doc["dock"])
        _write_json(self.login_greeter_path, tokens_doc["login_experience"])
        _write_json(self.runtime_state_path, state)
        _write_json(self.live_values_path, {"updated_at_ms": state["updated_at_ms"], "values": overrides})

    def flush_all(self) -> None:
        try:
            self._apply_exclusive_gates_to_engine_configs()
            rendered_toml = dumps_toml(
                self.doc,
                header_comment="Scy-Shell v2.0 Unified Configuration — Managed safely via `scy-shell` or Studio.",
            )
            atomic_write_text(self.config_path, rendered_toml)
            atomic_write_text(self.last_good_config_path, rendered_toml)

            # --- Write ALL Native Lucid Engine Stores ---
            l_store = self.doc["providers"]["lucid"]

            # 1. prefs.json
            if l_store["prefs"] or l_store["lock_widgets"] or l_store["hypr"]:
                merged_prefs = _read_json(self.lucid_prefs_path)
                merged_prefs.update(l_store["prefs"])
                if l_store["lock_widgets"] and "lockWidgetOpts" not in l_store["prefs"]:
                    nested_lo: dict[str, dict[str, Any]] = {}
                    for full_k, v in l_store["lock_widgets"].items():
                        kp = full_k.split(".", 2)
                        if len(kp) == 3:
                            nested_lo.setdefault(kp[1], {})[kp[2]] = v
                    merged_prefs["lockWidgetOpts"] = json.dumps(nested_lo)
                _write_json(self.lucid_prefs_path, merged_prefs)

            # 2. ~/.config/hypr/lucid-settings.lua
            if l_store["hypr"]:
                opt_lines = ["return {", "  options = {"]
                for k in sorted(l_store["hypr"]):
                    opt_lines.append(f"    [{_lua_val(k)}] = {_lua_val(l_store['hypr'][k])},")
                opt_lines.extend(["  }", "}"])
                atomic_write_text(self.lucid_hypr_lua_path, "\n".join(opt_lines) + "\n")

            # 3. blur.json
            if l_store["glass"]:
                merged_blur = _read_json(self.lucid_blur_path)
                merged_blur.update(l_store["glass"])
                _write_json(self.lucid_blur_path, merged_blur)

            # 4. lucidwidgets/widgets.json
            if l_store["widget_opts"]:
                wdoc = _read_json(self.lucid_widgets_path) or {
                    "nextId": 1,
                    "boardFull": True,
                    "laidScale": 1,
                    "preset": "",
                    "saved": [],
                    "last": [],
                    "stash": [],
                    "instances": [],
                }
                wdefs = wdoc.setdefault("scyWidgetDefaults", {})
                for full_k, v in l_store["widget_opts"].items():
                    kp = full_k.split(".", 2)
                    if len(kp) == 3:
                        _, wtype, opt = kp
                        wdefs.setdefault(wtype, {})[opt] = v
                        for inst in wdoc.get("instances", []):
                            if isinstance(inst, dict) and inst.get("type") == wtype:
                                inst.setdefault("opts", {})[opt] = v
                _write_json(self.lucid_widgets_path, wdoc)

            # 5. lucidmoji + standalone Lucid apps
            installed_lucid_root = self.home / ".config" / "quickshell" / "lucid"
            if "moji" in l_store["apps"] and l_store["apps"]["moji"]:
                m_cfg = _read_json(self.lucid_moji_config_path)
                m_st = _read_json(self.lucid_moji_state_path)
                for k, v in l_store["apps"]["moji"].items():
                    if k in MOJI_CONFIG_KEYS:
                        m_cfg[k] = v
                    else:
                        m_st[k] = v
                if m_cfg:
                    _write_json(self.lucid_moji_config_path, m_cfg)
                    if installed_lucid_root.exists():
                        _write_json(installed_lucid_root / "lucidmoji" / "config.json", m_cfg)
                if m_st:
                    _write_json(self.lucid_moji_state_path, m_st)
                    if installed_lucid_root.exists():
                        _write_json(installed_lucid_root / "lucidmoji" / "state.json", m_st)

            for app_name, app_vals in l_store["apps"].items():
                if app_name == "moji" or not app_vals or app_name not in self.lucid_app_paths:
                    continue
                ap = self.lucid_app_paths[app_name]
                cur = _read_json(ap)
                cur.update(app_vals)
                _write_json(ap, cur)
                if app_name == "keys" and installed_lucid_root.exists():
                    _write_json(installed_lucid_root / "lucidkeys" / "state.json", cur)

            # 6. Staged SDDM theme.conf (independent Login Experience configuration)
            login_cfg = self._build_design_tokens_doc()["login_experience"]
            sddm_map = dict(l_store["sddm"])
            if login_cfg.get("background_path"):
                sddm_map.setdefault("background", login_cfg["background_path"])
            sddm_map.setdefault("blurRadius", login_cfg.get("background_blur", 36))
            sddm_map.setdefault("clock24h", login_cfg.get("clock_24h", True))
            sddm_map.setdefault("userListStyle", login_cfg.get("user_list_style", "avatar-cards"))
            sddm_map.setdefault("passwordFieldStyle", login_cfg.get("password_style", "glass-pill"))
            sddm_map.setdefault("avatarRing", login_cfg.get("avatar_ring", True))
            sddm_map.setdefault("showSessionPicker", login_cfg.get("show_session_picker", True))
            sddm_map.setdefault("showPowerActions", login_cfg.get("show_power_actions", True))
            sddm_map.setdefault("loginAnimation", login_cfg.get("login_animation", "smooth-rise"))
            sddm_map.setdefault("highContrast", login_cfg.get("high_contrast", False))
            sddm_map.setdefault("uiScale", login_cfg.get("ui_scale", 1.0))
            lines = ["[General]"] + [
                f"{k}={str(v).lower() if isinstance(v, bool) else v}"
                for k, v in sorted(sddm_map.items())
            ]
            atomic_write_text(self.lucid_sddm_stage_path, "\n".join(lines) + "\n")

            # --- Write ALL Native Mandara Engine Stores ---
            m_store = self.doc["providers"]["mandara"]
            atomic_write_text(
                self.mandara_config_path,
                dumps_toml(m_store["config"], header_comment="Synced by Scy-Shell Unified Core (inactive settings preserved)."),
            )
            if m_store["wallgen"]:
                atomic_write_text(self.mandara_wallgen_path, dumps_toml(m_store["wallgen"]))
            greeter_doc = dict(m_store["greeter"])
            greeter_doc["scy_login"] = login_cfg
            atomic_write_text(self.mandara_greeter_stage_path, dumps_toml(greeter_doc))

            self._save_ledger()
            self.flush_runtime_state()
        except Exception as exc:
            self.log_persistence_error(f"flush_all failed: {exc}")
            raise
