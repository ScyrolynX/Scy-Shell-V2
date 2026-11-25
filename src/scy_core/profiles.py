"""Scy-Shell v2.0 — Complete Desktop Profile System (Create, Apply, Duplicate, Import, Export)."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .theme_engine import ScyThemeCoordinator
from .toml_io import atomic_write_text

BUILTIN_PROFILES: dict[str, dict[str, Any]] = {
    "balanced": {
        "id": "balanced",
        "name": "Balanced (Scy Default)",
        "builtin": True,
        "description": "Signature Scy-Shell experience: top floating island bar, bottom Lucid-inspired dock, Dynamic Island, frosted glass, and balanced spring physics.",
        "look": "scy-m3-expressive",
        "seed": "#7aa2f7",
        "dark_mode": True,
        "settings": {
            "scy.providers.lucid.prefs.barEnabled": True,
            "scy.providers.lucid.prefs.barPosition": "top",
            "scy.providers.lucid.prefs.barStyle": "island",
            "scy.providers.lucid.prefs.barSpacing": 8,
            "scy.dock.mode": "island",
            "scy.dock.placement": "bottom",
            "scy.dock.icon_size": 42,
            "scy.dock.magnify_enabled": True,
            "scy.dock.auto_hide_mode": "dodge-windows",
            "scy.island.enabled": True,
            "scy.effects.material_preset": "scy-frosted",
            "scy.effects.motion_preset": "expressive-spring",
            "scy.performance.tier": "balanced",
            "scy.providers.lucid.hypr.general.gaps_in": 6,
            "scy.providers.lucid.hypr.general.gaps_out": 12,
            "scy.providers.lucid.hypr.decoration.rounding": 14,
            "scy.widgets.board_preset": "balanced-glance",
        },
    },
    "minimal": {
        "id": "minimal",
        "name": "Minimal Zen",
        "builtin": True,
        "description": "Distraction-free workspace: compact single top bar, auto-hidden dock, zero desktop widgets, tight tiling gaps, and calm subtle motion.",
        "look": "zen",
        "seed": "#c0caf5",
        "dark_mode": True,
        "settings": {
            "scy.providers.lucid.prefs.barEnabled": True,
            "scy.providers.lucid.prefs.barPosition": "top",
            "scy.providers.lucid.prefs.barStyle": "full",
            "scy.providers.lucid.prefs.barSpacing": 4,
            "scy.dock.mode": "island",
            "scy.dock.icon_size": 36,
            "scy.dock.magnify_enabled": False,
            "scy.dock.auto_hide_mode": "always-hide",
            "scy.island.enabled": False,
            "scy.effects.material_preset": "obsidian-matte",
            "scy.effects.motion_preset": "minimal",
            "scy.performance.tier": "balanced",
            "scy.providers.lucid.hypr.general.gaps_in": 3,
            "scy.providers.lucid.hypr.general.gaps_out": 6,
            "scy.providers.lucid.hypr.decoration.rounding": 8,
            "scy.widgets.board_preset": "clean-slate",
        },
    },
    "productivity": {
        "id": "productivity",
        "name": "Productivity Focus",
        "builtin": True,
        "description": "High-density multi-window workflow: left studio rail dock, top status strip, active Focus Timer in Dynamic Island, and agenda/notes widgets.",
        "look": "library-desk",
        "seed": "#e0af68",
        "dark_mode": True,
        "settings": {
            "scy.providers.lucid.prefs.barEnabled": True,
            "scy.providers.lucid.prefs.barPosition": "top",
            "scy.providers.lucid.prefs.barStyle": "notch",
            "scy.dock.mode": "island",
            "scy.dock.placement": "left",
            "scy.dock.icon_size": 38,
            "scy.dock.magnify_enabled": False,
            "scy.dock.auto_hide_mode": "dodge-maximized",
            "scy.island.enabled": True,
            "scy.island.show_timer": True,
            "scy.effects.material_preset": "tinted-acrylic",
            "scy.effects.motion_preset": "crisp-snappy",
            "scy.providers.lucid.hypr.general.gaps_in": 4,
            "scy.providers.lucid.hypr.general.gaps_out": 8,
            "scy.providers.lucid.hypr.decoration.rounding": 10,
            "scy.widgets.board_preset": "productivity-hub",
        },
    },
    "immersive": {
        "id": "immersive",
        "name": "Immersive Liquid Glass",
        "builtin": True,
        "description": "Rich showcase visuals: Liquid Crystal deep blur, split floating dock with magnification wave, generous gaps, and fluid spring animations.",
        "look": "corniche-dusk",
        "seed": "#f28fad",
        "dark_mode": True,
        "settings": {
            "scy.providers.lucid.prefs.barEnabled": True,
            "scy.providers.lucid.prefs.barPosition": "top",
            "scy.providers.lucid.prefs.barStyle": "island",
            "scy.providers.lucid.prefs.barSpacing": 10,
            "scy.dock.mode": "split",
            "scy.dock.placement": "bottom",
            "scy.dock.icon_size": 48,
            "scy.dock.magnify_enabled": True,
            "scy.dock.magnify_scale": 1.50,
            "scy.dock.auto_hide_mode": "never",
            "scy.island.enabled": True,
            "scy.effects.material_preset": "liquid-crystal",
            "scy.effects.motion_preset": "fluid-silk",
            "scy.performance.tier": "max-quality",
            "scy.providers.lucid.hypr.general.gaps_in": 10,
            "scy.providers.lucid.hypr.general.gaps_out": 20,
            "scy.providers.lucid.hypr.decoration.rounding": 20,
            "scy.widgets.board_preset": "balanced-glance",
        },
    },
    "gaming": {
        "id": "gaming",
        "name": "Gaming Low-Latency",
        "builtin": True,
        "description": "Zero-overhead competitive mode: VRR enabled, dock & bar auto-dodge fullscreen, minimal blur passes, snappy 0-lag transitions, DND ready.",
        "look": "phosphor",
        "seed": "#a6e3a1",
        "dark_mode": True,
        "settings": {
            "scy.providers.lucid.prefs.barAutoHide": True,
            "scy.dock.mode": "island",
            "scy.dock.auto_hide_mode": "always-hide",
            "scy.island.enabled": False,
            "scy.effects.material_preset": "minimal-flat",
            "scy.effects.motion_preset": "crisp-snappy",
            "scy.performance.tier": "performance",
            "scy.performance.vrr_policy": "fullscreen-only",
            "scy.providers.lucid.hypr.general.gaps_in": 2,
            "scy.providers.lucid.hypr.general.gaps_out": 4,
            "scy.providers.lucid.hypr.decoration.rounding": 6,
            "scy.widgets.board_preset": "clean-slate",
        },
    },
    "creative": {
        "id": "creative",
        "name": "Creative Studio",
        "builtin": True,
        "description": "Color-accurate neutral chrome for design, photography, and editing: neutral OKLCH surfaces, carved bottom notch dock, telemetry widgets.",
        "look": "pharos-ink",
        "seed": "#89b4fa",
        "dark_mode": True,
        "settings": {
            "scy.design.palette_harmony": "neutral",
            "scy.design.accent_intensity": 0.85,
            "scy.dock.mode": "notch",
            "scy.dock.placement": "bottom",
            "scy.dock.icon_size": 44,
            "scy.dock.auto_hide_mode": "dodge-windows",
            "scy.island.enabled": True,
            "scy.effects.material_preset": "scy-frosted",
            "scy.providers.lucid.hypr.general.gaps_in": 6,
            "scy.providers.lucid.hypr.general.gaps_out": 12,
            "scy.widgets.board_preset": "telemetry-pro",
        },
    },
    "cinema": {
        "id": "cinema",
        "name": "Cinema OLED",
        "builtin": True,
        "description": "Deep pitch-dark surfaces for media & OLED panels: auto-hiding bar and dock, warm cinema accents, dim inactive windows, zero glare.",
        "look": "night-frame",
        "seed": "#cba6f7",
        "dark_mode": True,
        "settings": {
            "scy.providers.lucid.prefs.barAutoHide": True,
            "scy.providers.lucid.prefs.surfaceDarkness": 0.75,
            "scy.dock.mode": "island",
            "scy.dock.auto_hide_mode": "always-hide",
            "scy.island.enabled": True,
            "scy.island.expand_on_media": True,
            "scy.windows.dim_inactive": True,
            "scy.windows.dim_strength": 0.24,
            "scy.effects.shader_preset": "warm-cinema",
            "scy.widgets.board_preset": "minimal-zen",
        },
    },
}


class ScyProfileManager:
    """Manages built-in and custom user desktop profiles (`~/.config/scy-shell/profiles/*.scyprofile.json`)."""

    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store
        self.profiles_dir = self.store.config_dir / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _slugify(raw: str) -> str:
        s = re.sub(r"[^a-z0-9_-]+", "-", raw.strip().lower()).strip("-")
        if not s:
            raise ValueError("Profile ID must contain alphanumeric characters")
        return s

    def list_profiles(self) -> list[dict[str, Any]]:
        active_id = str(self.store.get_setting("scy.profiles.active") or "balanced")
        out: list[dict[str, Any]] = []
        for pid, pdef in BUILTIN_PROFILES.items():
            out.append({**pdef, "active": pid == active_id})
        for f in sorted(self.profiles_dir.glob("*.scyprofile.json")):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
                pid = doc["id"]
                if pid not in BUILTIN_PROFILES:
                    out.append({**doc, "builtin": False, "active": pid == active_id, "path": str(f)})
            except Exception:
                continue
        return out

    def get_profile(self, profile_id: str) -> dict[str, Any]:
        if profile_id in BUILTIN_PROFILES:
            return dict(BUILTIN_PROFILES[profile_id])
        fpath = self.profiles_dir / f"{self._slugify(profile_id)}.scyprofile.json"
        if not fpath.exists():
            raise FileNotFoundError(f"Profile not found: {profile_id}")
        return json.loads(fpath.read_text(encoding="utf-8"))

    def apply_profile(self, profile_id: str) -> dict[str, Any]:
        pdoc = self.get_profile(profile_id)
        if bool(self.store.get_setting("scy.profiles.auto_backup_on_switch")):
            self.store.create_backup(tag=f"pre-profile-{pdoc['id']}")

        if pdoc.get("look"):
            self.store.set_presentation("primary_identity", str(pdoc["look"]))
            self.store.set_presentation("mandara_surface_look", str(pdoc["look"]))

        applied_keys: list[str] = []
        for sid, val in (pdoc.get("settings") or {}).items():
            if sid in self.store.schema.by_id:
                self.store.set_setting(sid, val, flush=False, validate=True)
                applied_keys.append(sid)

        target_choice = pdoc["id"] if pdoc["id"] in BUILTIN_PROFILES else "custom"
        self.store.set_setting("scy.profiles.active", target_choice, flush=False, validate=True)
        self.store.doc["identity"]["active_custom_profile_id"] = pdoc["id"]

        thm = ScyThemeCoordinator(self.store)
        thm.apply_palette(
            seed_hex=pdoc.get("seed") or self.store.doc["identity"].get("accent_seed", "#7aa2f7"),
            dark_mode=pdoc.get("dark_mode", True),
        )
        return {
            "ok": True,
            "profile_id": pdoc["id"],
            "name": pdoc.get("name", pdoc["id"]),
            "applied_settings_count": len(applied_keys),
        }

    def create_profile_from_current(self, profile_id: str, name: str, description: str = "") -> dict[str, Any]:
        pid = self._slugify(profile_id)
        if pid in BUILTIN_PROFILES:
            raise ValueError(f"Cannot overwrite built-in profile '{pid}'; choose a custom ID or duplicate it.")
        overrides = self.store._collect_override_values()
        doc = {
            "format": "scy-profile-v2",
            "id": pid,
            "name": name.strip() or pid,
            "builtin": False,
            "created_at": int(time.time()),
            "description": description.strip() or "User-saved complete Scy-Shell desktop profile.",
            "look": self.store.doc["presentations"].get("primary_identity", "scy-m3-expressive"),
            "seed": self.store.doc["identity"].get("accent_seed", "#7aa2f7"),
            "dark_mode": bool(self.store.doc["identity"].get("dark_mode", True)),
            "settings": overrides,
        }
        out_path = self.profiles_dir / f"{pid}.scyprofile.json"
        atomic_write_text(out_path, json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        return {**doc, "path": str(out_path)}

    def duplicate_profile(self, source_id: str, new_id: str, new_name: str | None = None) -> dict[str, Any]:
        src = self.get_profile(source_id)
        pid = self._slugify(new_id)
        if pid in BUILTIN_PROFILES:
            raise ValueError(f"Cannot overwrite built-in profile '{pid}'")
        dup = {
            "format": "scy-profile-v2",
            "id": pid,
            "name": (new_name or f"{src.get('name', source_id)} Copy").strip(),
            "builtin": False,
            "created_at": int(time.time()),
            "description": src.get("description", ""),
            "look": src.get("look", "scy-m3-expressive"),
            "seed": src.get("seed", "#7aa2f7"),
            "dark_mode": bool(src.get("dark_mode", True)),
            "settings": dict(src.get("settings") or {}),
        }
        out_path = self.profiles_dir / f"{pid}.scyprofile.json"
        atomic_write_text(out_path, json.dumps(dup, indent=2, ensure_ascii=False) + "\n")
        return {**dup, "path": str(out_path)}

    def export_profile(self, profile_id: str, destination: Path) -> Path:
        pdoc = self.get_profile(profile_id)
        destination = destination.expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(destination, json.dumps(pdoc, indent=2, ensure_ascii=False) + "\n")
        return destination

    def import_profile(self, source_path: Path, override_id: str | None = None) -> dict[str, Any]:
        src = Path(source_path).expanduser().resolve()
        if not src.exists() or not src.is_file():
            raise FileNotFoundError(f"Profile file not found: {src}")
        raw = json.loads(src.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or "settings" not in raw or not isinstance(raw["settings"], dict):
            raise ValueError(f"Invalid Scy-Shell profile JSON in {src}")
        pid = self._slugify(override_id or raw.get("id") or src.stem)
        if pid in BUILTIN_PROFILES:
            pid = f"{pid}-imported"
        # Validate every setting key/value before importing!
        clean_settings: dict[str, Any] = {}
        for sid, val in raw["settings"].items():
            if sid in self.store.schema.by_id:
                clean_settings[sid] = self.store.schema.validate_and_coerce(sid, val)
        doc = {
            "format": "scy-profile-v2",
            "id": pid,
            "name": str(raw.get("name") or pid),
            "builtin": False,
            "created_at": int(time.time()),
            "description": str(raw.get("description") or f"Imported from {src.name}"),
            "look": str(raw.get("look") or "scy-m3-expressive"),
            "seed": str(raw.get("seed") or "#7aa2f7"),
            "dark_mode": bool(raw.get("dark_mode", True)),
            "settings": clean_settings,
        }
        out_path = self.profiles_dir / f"{pid}.scyprofile.json"
        atomic_write_text(out_path, json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        return {**doc, "path": str(out_path)}

    def delete_profile(self, profile_id: str) -> bool:
        if profile_id in BUILTIN_PROFILES:
            raise ValueError(f"Built-in profile '{profile_id}' cannot be deleted")
        fpath = self.profiles_dir / f"{self._slugify(profile_id)}.scyprofile.json"
        if fpath.exists():
            fpath.unlink()
            return True
        return False
