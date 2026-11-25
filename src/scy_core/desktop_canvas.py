"""Phase 6 — Hybrid Desktop Widget Bounding-Box Coordinator, Calendar Bridge & Safe Portals."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .toml_io import atomic_write_text


@dataclass
class WidgetBox:
    engine: str   # "lucid" | "mandara"
    widget_id: str
    x: float
    y: float
    width: float
    height: float

    def overlaps(self, other: "WidgetBox", margin: float = 12.0) -> bool:
        return not (
            self.x + self.width + margin <= other.x
            or other.x + other.width + margin <= self.x
            or self.y + self.height + margin <= other.y
            or other.y + other.height + margin <= self.y
        )


class ScyDesktopCoordinator:
    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store
        self.portal_conf_path = self.store.home / ".config" / "xdg-desktop-portal" / "hyprland-portals.conf"
        self.agenda_bridge_path = self.store.state_dir / "synced-agenda.json"

    def resolve_hybrid_widget_boxes(
        self,
        lucid_boxes: list[WidgetBox],
        mandara_boxes: list[WidgetBox],
        screen_w: float = 1920.0,
        screen_h: float = 1080.0,
    ) -> list[WidgetBox]:
        """Places Lucid M3 widgets first (priority default), nudging any colliding Mandara/WASM
        widgets onto free grid coordinates so both engines coexist on LAYER_BOTTOM cleanly."""
        placed: list[WidgetBox] = [WidgetBox(**vars(b)) for b in lucid_boxes]
        resolved_mandara: list[WidgetBox] = []

        for mb in mandara_boxes:
            cand = WidgetBox(**vars(mb))
            step = 32.0
            attempts = 0
            while any(cand.overlaps(p) for p in placed) and attempts < 200:
                cand.x += step
                if cand.x + cand.width > screen_w - 24.0:
                    cand.x = 24.0
                    cand.y += step
                    if cand.y + cand.height > screen_h - 24.0:
                        cand.y = 48.0
                attempts += 1
            placed.append(cand)
            resolved_mandara.append(cand)
        return resolved_mandara

    def write_portal_config(self, use_lumen_filechooser: bool = True) -> Path:
        """Writes safe Hyprland XDG Desktop Portal routing so ScreenCast/Screenshot stay on
        xdg-desktop-portal-hyprland while FileChooser optionally routes to Lucid Lumen (`lumend.py`)."""
        fc_value = "lumen;gtk" if use_lumen_filechooser else "gtk"
        content = (
            "# Managed by Scy-Shell Desktop & Portal Coordinator\n"
            "[preferred]\n"
            "default=hyprland;gtk\n"
            f"org.freedesktop.impl.portal.FileChooser={fc_value}\n"
            "org.freedesktop.impl.portal.ScreenCast=hyprland\n"
            "org.freedesktop.impl.portal.Screenshot=hyprland\n"
        )
        atomic_write_text(self.portal_conf_path, content)
        return self.portal_conf_path

    def publish_synced_agenda(self, events: list[dict[str, Any]]) -> Path:
        """Bridges Mandara CalDAV/Google/Outlook events to Lucid `lucidcalendar` & `LockAgenda.qml`."""
        payload = {"version": 1, "source": "mandara-calendar-sync", "events": events}
        atomic_write_text(self.agenda_bridge_path, json.dumps(payload, indent=2) + "\n")
        return self.agenda_bridge_path
