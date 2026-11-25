"""Scy-Shell v2.0 — Scy Layout Composer & Scy Component Laboratory."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .toml_io import atomic_write_text

LAYOUT_PRESETS: dict[str, dict[str, Any]] = {
    "scy-signature": {
        "id": "scy-signature",
        "name": "Scy Signature (Top Island + Bottom Dock)",
        "description": "Classic Scy-Shell spatial balance: floating top island bar, Dynamic Island center pill, and bottom Lucid-inspired glass dock.",
        "surfaces": {
            "top_bar": {"enabled": True, "edge": "top", "anchor": "top-stretch", "height": 38, "margin_outer": 8, "padding_x": 14, "layer": "top", "monitor": "all"},
            "dynamic_island": {"enabled": True, "edge": "top", "anchor": "top-center", "width": 220, "height": 34, "margin_outer": 8, "layer": "overlay", "monitor": "primary"},
            "dock": {"enabled": True, "edge": "bottom", "anchor": "bottom-center", "icon_size": 42, "margin_outer": 8, "padding_x": 12, "layer": "top", "monitor": "primary"},
            "notifications": {"enabled": True, "anchor": "top-right", "width": 360, "margin_outer": 14, "layer": "overlay", "monitor": "active"},
            "control_center": {"enabled": True, "anchor": "top-right", "width": 410, "margin_outer": 12, "layer": "overlay", "monitor": "active"},
            "osd": {"enabled": True, "anchor": "bottom-center", "width": 240, "margin_outer": 96, "layer": "overlay", "monitor": "active"},
        },
        "settings_sync": {
            "scy.layout.active_preset": "scy-signature",
            "scy.providers.lucid.prefs.barEnabled": True,
            "scy.providers.lucid.prefs.barPosition": "top",
            "scy.providers.lucid.prefs.barStyle": "island",
            "scy.dock.placement": "bottom",
            "scy.dock.mode": "island",
            "scy.island.enabled": True,
        },
    },
    "unity-left": {
        "id": "unity-left",
        "name": "Unity Left Rail + Top Strip",
        "description": "Ultrawide & productivity favorite: vertical left application rail with full vertical screen height for code and browsers.",
        "surfaces": {
            "top_bar": {"enabled": True, "edge": "top", "anchor": "top-stretch", "height": 32, "margin_outer": 4, "padding_x": 12, "layer": "top", "monitor": "all"},
            "dynamic_island": {"enabled": True, "edge": "top", "anchor": "top-center", "width": 210, "height": 30, "margin_outer": 4, "layer": "overlay", "monitor": "primary"},
            "dock": {"enabled": True, "edge": "left", "anchor": "left-center", "icon_size": 38, "margin_outer": 6, "padding_x": 8, "layer": "top", "monitor": "primary"},
            "notifications": {"enabled": True, "anchor": "top-right", "width": 350, "margin_outer": 12, "layer": "overlay", "monitor": "active"},
            "control_center": {"enabled": True, "anchor": "top-right", "width": 400, "margin_outer": 12, "layer": "overlay", "monitor": "active"},
            "osd": {"enabled": True, "anchor": "bottom-center", "width": 230, "margin_outer": 48, "layer": "overlay", "monitor": "active"},
        },
        "settings_sync": {
            "scy.layout.active_preset": "unity-left",
            "scy.providers.lucid.prefs.barEnabled": True,
            "scy.providers.lucid.prefs.barPosition": "top",
            "scy.providers.lucid.prefs.barStyle": "full",
            "scy.dock.placement": "left",
            "scy.dock.mode": "island",
        },
    },
    "bottom-deck": {
        "id": "bottom-deck",
        "name": "Unified Bottom Deck",
        "description": "Clean top edge with bottom status bar and auto-dodging floating dock.",
        "surfaces": {
            "top_bar": {"enabled": True, "edge": "bottom", "anchor": "bottom-stretch", "height": 38, "margin_outer": 6, "padding_x": 14, "layer": "top", "monitor": "all"},
            "dynamic_island": {"enabled": True, "edge": "top", "anchor": "top-center", "width": 220, "height": 34, "margin_outer": 8, "layer": "overlay", "monitor": "primary"},
            "dock": {"enabled": True, "edge": "left", "anchor": "left-center", "icon_size": 40, "margin_outer": 8, "padding_x": 10, "layer": "top", "monitor": "primary"},
            "notifications": {"enabled": True, "anchor": "bottom-right", "width": 360, "margin_outer": 56, "layer": "overlay", "monitor": "active"},
            "control_center": {"enabled": True, "anchor": "bottom-right", "width": 410, "margin_outer": 54, "layer": "overlay", "monitor": "active"},
            "osd": {"enabled": True, "anchor": "top-center", "width": 230, "margin_outer": 54, "layer": "overlay", "monitor": "active"},
        },
        "settings_sync": {
            "scy.layout.active_preset": "bottom-deck",
            "scy.providers.lucid.prefs.barEnabled": True,
            "scy.providers.lucid.prefs.barPosition": "bottom",
            "scy.dock.placement": "left",
        },
    },
    "minimal-top": {
        "id": "minimal-top",
        "name": "Minimal Single Top Bar",
        "description": "Zero permanent bottom chrome: ultra-slim top bar with auto-hidden reveal dock.",
        "surfaces": {
            "top_bar": {"enabled": True, "edge": "top", "anchor": "top-stretch", "height": 30, "margin_outer": 0, "padding_x": 12, "layer": "top", "monitor": "all"},
            "dynamic_island": {"enabled": False, "edge": "top", "anchor": "top-center", "width": 200, "height": 30, "margin_outer": 4, "layer": "overlay", "monitor": "primary"},
            "dock": {"enabled": True, "edge": "bottom", "anchor": "bottom-center", "icon_size": 38, "margin_outer": 6, "padding_x": 10, "layer": "overlay", "monitor": "primary"},
            "notifications": {"enabled": True, "anchor": "top-right", "width": 340, "margin_outer": 10, "layer": "overlay", "monitor": "active"},
            "control_center": {"enabled": True, "anchor": "top-right", "width": 390, "margin_outer": 10, "layer": "overlay", "monitor": "active"},
            "osd": {"enabled": True, "anchor": "bottom-center", "width": 220, "margin_outer": 40, "layer": "overlay", "monitor": "active"},
        },
        "settings_sync": {
            "scy.layout.active_preset": "minimal-top",
            "scy.providers.lucid.prefs.barPosition": "top",
            "scy.providers.lucid.prefs.barStyle": "full",
            "scy.dock.auto_hide_mode": "always-hide",
            "scy.island.enabled": False,
        },
    },
    "dual-stage": {
        "id": "dual-stage",
        "name": "Creator Dual-Edge Stage",
        "description": "Carved top notch bar + carved bottom notch dock + full Dynamic Island telemetry.",
        "surfaces": {
            "top_bar": {"enabled": True, "edge": "top", "anchor": "top-stretch", "height": 38, "margin_outer": 0, "padding_x": 16, "layer": "top", "monitor": "all"},
            "dynamic_island": {"enabled": True, "edge": "top", "anchor": "top-center", "width": 260, "height": 36, "margin_outer": 6, "layer": "overlay", "monitor": "primary"},
            "dock": {"enabled": True, "edge": "bottom", "anchor": "bottom-center", "icon_size": 46, "margin_outer": 0, "padding_x": 14, "layer": "top", "monitor": "all"},
            "notifications": {"enabled": True, "anchor": "top-right", "width": 380, "margin_outer": 14, "layer": "overlay", "monitor": "active"},
            "control_center": {"enabled": True, "anchor": "top-right", "width": 420, "margin_outer": 14, "layer": "overlay", "monitor": "active"},
            "osd": {"enabled": True, "anchor": "bottom-center", "width": 250, "margin_outer": 96, "layer": "overlay", "monitor": "active"},
        },
        "settings_sync": {
            "scy.layout.active_preset": "dual-stage",
            "scy.providers.lucid.prefs.barStyle": "notch",
            "scy.dock.mode": "notch",
            "scy.dock.placement": "bottom",
            "scy.dock.monitor_policy": "all",
            "scy.island.enabled": True,
        },
    },
}


DEFAULT_COMPONENTS: dict[str, dict[str, Any]] = {
    "top_bar": {
        "id": "top_bar",
        "label": "Top / Edge Bar",
        "visible": True,
        "material": "scy-frosted",
        "opacity": 0.84,
        "radius": 18,
        "border_width": 1,
        "border_opacity": 0.16,
        "shadow_elevation": 2,
        "glow_accent": False,
        "padding_x": 14,
        "padding_y": 6,
        "animation_curve": "expressive-spring",
        "hover_action": "highlight-pill",
        "click_action": "module-default",
    },
    "dock": {
        "id": "dock",
        "label": "Primary Application Dock",
        "visible": True,
        "material": "scy-frosted",
        "opacity": 0.88,
        "radius": 24,
        "border_width": 1,
        "border_opacity": 0.20,
        "shadow_elevation": 3,
        "glow_accent": True,
        "padding_x": 12,
        "padding_y": 8,
        "animation_curve": "expressive-spring",
        "hover_action": "magnify-and-preview",
        "click_action": "launch-or-focus-cycle",
    },
    "dynamic_island": {
        "id": "dynamic_island",
        "label": "Scy Dynamic Island",
        "visible": True,
        "material": "obsidian-matte",
        "opacity": 0.94,
        "radius": 22,
        "border_width": 1,
        "border_opacity": 0.22,
        "shadow_elevation": 3,
        "glow_accent": True,
        "padding_x": 14,
        "padding_y": 6,
        "animation_curve": "expressive-spring",
        "hover_action": "expand-capsule",
        "click_action": "toggle-media-or-dashboard",
    },
    "control_center": {
        "id": "control_center",
        "label": "Quick Settings & Control Center",
        "visible": True,
        "material": "scy-frosted",
        "opacity": 0.90,
        "radius": 24,
        "border_width": 1,
        "border_opacity": 0.18,
        "shadow_elevation": 4,
        "glow_accent": False,
        "padding_x": 18,
        "padding_y": 18,
        "animation_curve": "expressive-spring",
        "hover_action": "tile-elevation",
        "click_action": "toggle-tile",
    },
    "notification_card": {
        "id": "notification_card",
        "label": "Notification Toast Card",
        "visible": True,
        "material": "scy-frosted",
        "opacity": 0.92,
        "radius": 18,
        "border_width": 1,
        "border_opacity": 0.16,
        "shadow_elevation": 3,
        "glow_accent": False,
        "padding_x": 14,
        "padding_y": 12,
        "animation_curve": "crisp-snappy",
        "hover_action": "pause-timeout",
        "click_action": "invoke-default-action",
    },
    "launcher": {
        "id": "launcher",
        "label": "Unified Command & App Launcher",
        "visible": True,
        "material": "liquid-crystal",
        "opacity": 0.90,
        "radius": 26,
        "border_width": 1,
        "border_opacity": 0.22,
        "shadow_elevation": 4,
        "glow_accent": True,
        "padding_x": 20,
        "padding_y": 18,
        "animation_curve": "expressive-spring",
        "hover_action": "select-row",
        "click_action": "execute-entry",
    },
    "workspace_switcher": {
        "id": "workspace_switcher",
        "label": "Workspace Pill & Overview",
        "visible": True,
        "material": "tinted-acrylic",
        "opacity": 0.86,
        "radius": 16,
        "border_width": 1,
        "border_opacity": 0.14,
        "shadow_elevation": 1,
        "glow_accent": True,
        "padding_x": 10,
        "padding_y": 4,
        "animation_curve": "expressive-spring",
        "hover_action": "preview-workspace",
        "click_action": "switch-workspace",
    },
    "desktop_widgets": {
        "id": "desktop_widgets",
        "label": "Desktop Ambient Widgets (Clock, Weather, Media, Telemetry)",
        "visible": True,
        "material": "scy-frosted",
        "opacity": 0.80,
        "radius": 22,
        "border_width": 1,
        "border_opacity": 0.14,
        "shadow_elevation": 2,
        "glow_accent": False,
        "padding_x": 16,
        "padding_y": 14,
        "animation_curve": "fluid-silk",
        "hover_action": "reveal-controls",
        "click_action": "open-detail-sheet",
    },
}


class ScyLayoutComposer:
    """Manages spatial shell layouts (`~/.config/scy-shell/layouts/*.json`) and syncs live state."""

    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store
        self.layouts_dir = self.store.config_dir / "layouts"
        self.layouts_dir.mkdir(parents=True, exist_ok=True)
        self.active_layout_file = self.store.state_dir / "active-layout.json"

    def list_layouts(self) -> list[dict[str, Any]]:
        active_id = str(self.store.get_setting("scy.layout.active_preset") or "scy-signature")
        out: list[dict[str, Any]] = []
        for lid, ldef in LAYOUT_PRESETS.items():
            out.append({**ldef, "builtin": True, "active": lid == active_id})
        for f in sorted(self.layouts_dir.glob("*.json")):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
                out.append({**doc, "builtin": False, "active": doc.get("id") == active_id, "path": str(f)})
            except Exception:
                continue
        return out

    def get_active_layout(self) -> dict[str, Any]:
        if self.active_layout_file.exists():
            try:
                return json.loads(self.active_layout_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        preset_id = str(self.store.get_setting("scy.layout.active_preset") or "scy-signature")
        return copy.deepcopy(LAYOUT_PRESETS.get(preset_id, LAYOUT_PRESETS["scy-signature"]))

    def apply_layout(self, layout_id: str) -> dict[str, Any]:
        if layout_id in LAYOUT_PRESETS:
            ldoc = copy.deepcopy(LAYOUT_PRESETS[layout_id])
        else:
            custom_path = self.layouts_dir / f"{layout_id}.json"
            if not custom_path.exists():
                raise FileNotFoundError(f"Layout '{layout_id}' not found")
            ldoc = json.loads(custom_path.read_text(encoding="utf-8"))

        for sid, val in (ldoc.get("settings_sync") or {}).items():
            if sid in self.store.schema.by_id:
                self.store.set_setting(sid, val, flush=False, validate=True)

        # Also sync surface dimensions directly to relevant settings
        surfaces = ldoc.get("surfaces") or {}
        if "dock" in surfaces and "icon_size" in surfaces["dock"]:
            self.store.set_setting("scy.dock.icon_size", int(surfaces["dock"]["icon_size"]), flush=False)
        if "dynamic_island" in surfaces and "width" in surfaces["dynamic_island"]:
            self.store.set_setting("scy.island.width", int(surfaces["dynamic_island"]["width"]), flush=False)

        self.store.flush_all()
        atomic_write_text(self.active_layout_file, json.dumps(ldoc, indent=2) + "\n")
        return {"ok": True, "layout": ldoc}

    def update_surface(self, surface_id: str, patch: dict[str, Any], save_as: str | None = None) -> dict[str, Any]:
        current = self.get_active_layout()
        surfaces = current.setdefault("surfaces", {})
        if surface_id not in surfaces:
            surfaces[surface_id] = {}
        surfaces[surface_id].update(patch)
        grid = max(1, int(self.store.get_setting("scy.desktop.edit_grid_px") or 8))
        for dim_key in ("x", "y", "margin_outer"):
            if dim_key in surfaces[surface_id] and isinstance(surfaces[surface_id][dim_key], (int, float)):
                surfaces[surface_id][dim_key] = int(round(surfaces[surface_id][dim_key] / grid) * grid)

        # Propagate edge/size edits to live shell settings
        if surface_id == "dock":
            if "edge" in patch and patch["edge"] in ("bottom", "left", "right", "floating"):
                self.store.set_setting("scy.dock.placement", patch["edge"], flush=False)
            if "icon_size" in patch:
                self.store.set_setting("scy.dock.icon_size", int(patch["icon_size"]), flush=False)
        elif surface_id == "top_bar":
            if "edge" in patch and patch["edge"] in ("top", "bottom", "left", "right"):
                self.store.set_setting("scy.providers.lucid.prefs.barPosition", patch["edge"], flush=False)
            if "enabled" in patch:
                self.store.set_setting("scy.providers.lucid.prefs.barEnabled", bool(patch["enabled"]), flush=False)
        elif surface_id == "dynamic_island":
            if "enabled" in patch:
                self.store.set_setting("scy.island.enabled", bool(patch["enabled"]), flush=False)
            if "width" in patch:
                self.store.set_setting("scy.island.width", int(patch["width"]), flush=False)

        if save_as:
            slug = re.sub(r"[^a-z0-9_-]+", "-", save_as.strip().lower()).strip("-") or "custom-layout"
            current["id"] = slug
            current["name"] = save_as.strip()
            atomic_write_text(self.layouts_dir / f"{slug}.json", json.dumps(current, indent=2) + "\n")

        self.store.flush_all()
        atomic_write_text(self.active_layout_file, json.dumps(current, indent=2) + "\n")
        return {"ok": True, "surface": surface_id, "layout": current}


class ScyComponentLab:
    """Per-component appearance, material, geometry, border, glow, and interaction customizer."""

    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store
        self.config_file = self.store.config_dir / "components.json"
        self.live_file = self.store.state_dir / "components-live.json"
        self._state = self._load()
        self._sync_live()

    def _load(self) -> dict[str, dict[str, Any]]:
        base = copy.deepcopy(DEFAULT_COMPONENTS)
        if self.config_file.exists():
            try:
                user_doc = json.loads(self.config_file.read_text(encoding="utf-8"))
                if isinstance(user_doc, dict):
                    for cid, patch in user_doc.items():
                        if cid in base and isinstance(patch, dict):
                            base[cid].update(patch)
                        elif isinstance(patch, dict):
                            base[cid] = patch
            except Exception:
                pass
        return base

    def _sync_live(self) -> None:
        atomic_write_text(self.config_file, json.dumps(self._state, indent=2) + "\n")
        atomic_write_text(self.live_file, json.dumps(self._state, indent=2) + "\n")

    def list_components(self) -> dict[str, dict[str, Any]]:
        return copy.deepcopy(self._state)

    def update_component(self, component_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        if component_id not in self._state:
            raise KeyError(f"Unknown shell component: {component_id}")
        allowed = {
            "visible", "material", "opacity", "radius", "border_width",
            "border_opacity", "shadow_elevation", "glow_accent",
            "padding_x", "padding_y", "animation_curve", "hover_action", "click_action",
        }
        for k, v in patch.items():
            if k in allowed:
                self._state[component_id][k] = v

        # Mirror to global settings where linked
        if component_id == "dock" and "visible" in patch:
            self.store.set_setting("scy.providers.lucid.prefs.dockEnabled", bool(patch["visible"]), flush=True)
        elif component_id == "top_bar" and "visible" in patch:
            self.store.set_setting("scy.providers.lucid.prefs.barEnabled", bool(patch["visible"]), flush=True)
        elif component_id == "dynamic_island" and "visible" in patch:
            self.store.set_setting("scy.island.enabled", bool(patch["visible"]), flush=True)

        self._sync_live()
        return copy.deepcopy(self._state[component_id])

    def reset_component(self, component_id: str) -> dict[str, Any]:
        if component_id not in DEFAULT_COMPONENTS:
            raise KeyError(f"Unknown default shell component: {component_id}")
        self._state[component_id] = copy.deepcopy(DEFAULT_COMPONENTS[component_id])
        self._sync_live()
        return copy.deepcopy(self._state[component_id])
