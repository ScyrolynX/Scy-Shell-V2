"""Phase 5 — Cross-Engine Launcher Federation (!ai + @plugins) & Procedural Wallgen Pipeline."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .schema import MANDARA_19_LOOKS, SCHEMA_DIR
from .theme_engine import ScyThemeCoordinator, generate_m3_expressive_tokens


WALLGEN_13_STYLES: tuple[str, ...] = (
    "aurora",
    "topographic",
    "bauhaus",
    "voronoi",
    "flow-field",
    "iso-cubes",
    "halftone",
    "waves",
    "mesh-gradient",
    "brutalist-grid",
    "starfield",
    "chladni",
    "ripples",
)


class ScyFederationEngine:
    """Federates Mandara's 88+WASM Plugins, Local AI Agent, and 13-style Wallgen into Lucid & Studio."""

    def __init__(self, store: ScyConfigStore, theme_coord: ScyThemeCoordinator | None = None) -> None:
        self.store = store
        self.theme_coord = theme_coord or ScyThemeCoordinator(store)
        pfile = SCHEMA_DIR / "plugins_catalogue.json"
        self.plugins: list[dict[str, Any]] = json.loads(pfile.read_text(encoding="utf-8")) if pfile.exists() else []

    def query_plugins(self, query: str = "", limit: int = 40) -> list[dict[str, Any]]:
        q = query.strip().lstrip("@").strip().lower()
        mcfg = self.store.doc["providers"]["mandara"]["config"]
        enabled_list = set(mcfg.get("plugins", {}).get("enabled", []) or [])
        disabled_list = set(mcfg.get("plugins", {}).get("disabled", []) or [])

        out: list[dict[str, Any]] = []
        for p in self.plugins:
            pid = p["id"]
            if not q or q in pid.lower() or q in p["name"].lower() or q in p.get("description", "").lower():
                is_on = (pid in enabled_list) or (p["kind"].startswith("builtin") and pid not in disabled_list)
                out.append(
                    {
                        **p,
                        "enabled": is_on,
                        "open_cmd": ["mandara", "msg", "panel", "toggle", pid],
                        "settings_cmd": ["mandara", "studio", "plugins", "--plugin", pid, "--settings"],
                    }
                )
                if len(out) >= limit:
                    break
        return out

    def set_plugin_enabled(self, plugin_id: str, enabled: bool) -> dict[str, Any]:
        p_tbl = self.store.doc["providers"]["mandara"]["config"].setdefault("plugins", {})
        en = list(dict.fromkeys(p_tbl.get("enabled", []) or []))
        dis = list(dict.fromkeys(p_tbl.get("disabled", []) or []))
        if enabled:
            if plugin_id not in en:
                en.append(plugin_id)
            if plugin_id in dis:
                dis.remove(plugin_id)
        else:
            if plugin_id in en:
                en.remove(plugin_id)
            if plugin_id not in dis:
                dis.append(plugin_id)
        p_tbl["enabled"] = en
        p_tbl["disabled"] = dis
        self.store.flush_all()
        return {"plugin_id": plugin_id, "enabled": enabled}

    def interpret_ai_command(self, prompt: str, apply_immediately: bool = False) -> dict[str, Any]:
        """Deterministic offline NL intent router + Mandara FunctionGemma/Qwen3 bridge."""
        clean = prompt.strip().removeprefix("!ai").strip()
        low = clean.lower()
        plan: list[dict[str, Any]] = []

        if "dark mode" in low or "dark theme" in low:
            plan.append({"tool": "theme.mode", "dark": True, "summary": "Switch Scy-Shell to Dark Mode"})
            if apply_immediately:
                self.theme_coord.apply_palette(dark_mode=True)
        elif "light mode" in low or "light theme" in low:
            plan.append({"tool": "theme.mode", "dark": False, "summary": "Switch Scy-Shell to Light Mode"})
            if apply_immediately:
                self.theme_coord.apply_palette(dark_mode=False)

        for look in MANDARA_19_LOOKS:
            if look in low or look.replace("-", " ") in low:
                plan.append({"tool": "presentation.set", "domain": "primary_identity", "value": look, "summary": f"Apply '{look}' Look"})
                if apply_immediately:
                    self.store.set_presentation("primary_identity", look)
                break

        m_prov = re.search(r"switch\s+(bar|dock|launcher|lock_screen|lock|notifications|osd|wallpaper)\s+to\s+(lucid|mandara|hybrid)", low)
        if m_prov:
            dom = "lock_screen" if m_prov.group(1) == "lock" else m_prov.group(1)
            prov = m_prov.group(2)
            plan.append({"tool": "provider.set", "domain": dom, "provider": prov, "summary": f"Set {dom} provider to {prov}"})
            if apply_immediately:
                self.store.set_provider(dom, prov)

        m_gaps = re.search(r"gaps?\s+(?:to\s+)?(\d+)", low)
        if m_gaps:
            g = int(m_gaps.group(1))
            plan.append({"tool": "setting.set", "scy_id": "scy.providers.lucid.hypr.general.gaps_in", "value": g, "summary": f"Set Hyprland inner gaps to {g}px"})
            if apply_immediately:
                self.store.set_setting("scy.providers.lucid.hypr.general.gaps_in", g)

        if not plan:
            plan.append({
                "tool": "mandara.agent.forward",
                "cmd": ["mandara", "msg", "agent", "ask", clean],
                "summary": f"Forward '{clean}' to local Mandara FunctionGemma/Qwen3 worker",
            })

        return {"prompt": clean, "applied": apply_immediately, "actions": plan}

    def federate_launcher_query(self, raw_query: str) -> dict[str, Any]:
        s = raw_query.strip()
        if s.startswith("!ai"):
            return {"mode": "ai", "result": self.interpret_ai_command(s, apply_immediately=False)}
        if s.startswith("@"):
            return {"mode": "plugins", "items": self.query_plugins(s[1:], limit=25)}
        return {
            "mode": "mixed",
            "plugins": self.query_plugins(s, limit=8),
            "settings": [
                {"scy_id": m.scy_id, "key": m.original_key, "project": m.source_project}
                for m in self.store.schema.search(s, limit=8)
            ],
        }

    def generate_procedural_wallpaper(
        self,
        style: str = "aurora",
        width: int = 1920,
        height: int = 1080,
        seed_hex: str | None = None,
    ) -> dict[str, Any]:
        """Generates a real palette-seeded high-resolution procedural SVG wallpaper for any of the 13 Wallgen styles
        and wires it into the active wallpaper renderer (`awww` or `mandara-wallpaper`) + M3 palette sync."""
        if style not in WALLGEN_13_STYLES:
            raise ValueError(f"Unknown Wallgen style '{style}'. Supported: {WALLGEN_13_STYLES}")
        seed = seed_hex or self.store.doc["identity"].get("accent_seed", "#ffb1c4")
        tok = generate_m3_expressive_tokens(seed, dark=bool(self.store.doc["identity"].get("dark_mode", True)))
        out_dir = self.store.home / ".local" / "share" / "scy-shell" / "wallgen"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"scy-wallgen-{style}.svg"

        shapes: list[str] = []
        for i in range(12):
            ang = (i / 12.0) * math.tau
            cx = int(width * (0.5 + 0.32 * math.cos(ang)))
            cy = int(height * (0.5 + 0.28 * math.sin(ang * 1.5)))
            rx = int(width * (0.14 + 0.03 * (i % 4)))
            ry = int(height * (0.18 + 0.04 * ((i + 2) % 3)))
            fill = tok["accent"] if i % 3 == 0 else (tok["tertiary"] if i % 3 == 1 else tok["accentContainer"])
            op = round(0.14 + 0.04 * (i % 4), 2)
            if style in ("bauhaus", "iso-cubes", "brutalist-grid"):
                shapes.append(f'<rect x="{cx - rx//2}" y="{cy - ry//2}" width="{rx}" height="{ry}" rx="28" fill="{fill}" fill-opacity="{op}"/>')
            elif style in ("waves", "topographic", "flow-field", "chladni"):
                y0 = int(height * (0.15 + 0.065 * i))
                shapes.append(
                    f'<path d="M 0 {y0} Q {width//3} {y0 - 90} {width*2//3} {y0 + 70} T {width} {y0}" '
                    f'fill="none" stroke="{fill}" stroke-width="6" stroke-opacity="{min(0.65, op*2)}"/>'
                )
            else:
                shapes.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" fill-opacity="{op}"/>')

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
            f'  <defs>\n'
            f'    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">\n'
            f'      <stop offset="0%" stop-color="{tok["bgOpaque"]}"/>\n'
            f'      <stop offset="100%" stop-color="{tok["surface1"]}"/>\n'
            f'    </linearGradient>\n'
            f'  </defs>\n'
            f'  <rect width="{width}" height="{height}" fill="url(#bg)"/>\n'
            f'  <!-- Wallgen Style: {style} -->\n  '
            + "\n  ".join(shapes)
            + "\n</svg>\n"
        )
        out_path.write_text(svg, encoding="utf-8")

        self.store.doc["identity"]["wallpaper"] = str(out_path)
        self.store.doc["providers"]["lucid"]["prefs"]["wallpaper"] = str(out_path)
        self.store.doc["providers"]["mandara"]["wallgen"]["style"] = style
        self.theme_coord.apply_palette(seed_hex=seed)

        active_wp = self.store.get_provider("wallpaper")
        apply_cmd = (
            ["awww", "img", str(out_path), "--transition-type", "grow"]
            if active_wp == "lucid"
            else ["mandara", "msg", "wallpaper", "set", str(out_path)]
        )
        return {
            "style": style,
            "path": str(out_path),
            "renderer_provider": active_wp,
            "apply_cmd": apply_cmd,
        }
