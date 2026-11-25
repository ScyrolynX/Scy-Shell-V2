"""Scy-Shell Unified Visual Identity & Theme Coordinator (OKLCH / M3 Expressive + 28-App SHA-256 Ledger)."""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .toml_io import atomic_write_text, dumps_toml


# --- Perceptual OKLab / OKLCH Color Math (Zero external deps) ---
def _hex_to_srgb(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return (1.0, 0.69, 0.77)
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055


def hex_to_oklch(hex_str: str) -> tuple[float, float, float]:
    r, g, b = [_srgb_to_linear(x) for x in _hex_to_srgb(hex_str)]
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1.0 / 3.0)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1.0 / 3.0)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1.0 / 3.0)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_val = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    C = math.hypot(a, b_val)
    H = math.degrees(math.atan2(b_val, a)) % 360.0
    return (L, C, H)


def oklch_to_hex(L: float, C: float, H_deg: float) -> str:
    h_rad = math.radians(H_deg)
    a = C * math.cos(h_rad)
    b = C * math.sin(h_rad)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l3, m3, s3 = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3
    sr, sg, sb = [round(_linear_to_srgb(x) * 255) for x in (r, g, bl)]
    return f"#{sr:02x}{sg:02x}{sb:02x}"


def relative_luminance(hex_str: str) -> float:
    r, g, b = [_srgb_to_linear(x) for x in _hex_to_srgb(hex_str)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1: str, hex2: str) -> float:
    l1, l2 = relative_luminance(hex1), relative_luminance(hex2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def generate_m3_expressive_tokens(seed_hex: str, dark: bool = True, expressive_shift: bool = True) -> dict[str, str]:
    """Generates full Material 3 Expressive semantic tokens harmonized across Lucid QML & Mandara GPUI."""
    _, seed_c, h = hex_to_oklch(seed_hex)
    c_primary = max(0.11, min(0.20, seed_c if seed_c > 0.03 else 0.14))
    c_neutral = min(0.022, c_primary * 0.14)
    h_tert = (h + (48.0 if expressive_shift else 60.0)) % 360.0

    if dark:
        return {
            "mode": "dark",
            "seed": seed_hex,
            "bg": oklch_to_hex(0.15, c_neutral, h),
            "bgOpaque": oklch_to_hex(0.13, c_neutral, h),
            "bgTile": oklch_to_hex(0.20, c_neutral, h),
            "bgHigh": oklch_to_hex(0.26, c_neutral, h),
            "surface0": oklch_to_hex(0.17, c_neutral, h),
            "surface1": oklch_to_hex(0.21, c_neutral, h),
            "surface2": oklch_to_hex(0.25, c_neutral, h),
            "surface3": oklch_to_hex(0.30, c_neutral, h),
            "accent": oklch_to_hex(0.80, c_primary, h),
            "accentHover": oklch_to_hex(0.85, c_primary, h),
            "fgAccent": oklch_to_hex(0.22, c_primary * 0.75, h),
            "accentMuted": oklch_to_hex(0.76, c_primary * 0.45, h),
            "accentContainer": oklch_to_hex(0.34, c_primary * 0.85, h),
            "fgAccentContainer": oklch_to_hex(0.91, c_primary * 0.55, h),
            "tertiary": oklch_to_hex(0.81, c_primary * 0.85, h_tert),
            "tertiaryContainer": oklch_to_hex(0.34, c_primary * 0.75, h_tert),
            "text": oklch_to_hex(0.93, c_neutral * 0.8, h),
            "subtext": oklch_to_hex(0.80, c_neutral * 1.1, h),
            "subtextDim": oklch_to_hex(0.66, c_neutral, h),
            "outline": oklch_to_hex(0.42, c_neutral * 1.3, h),
            "outlineStrong": oklch_to_hex(0.62, c_neutral * 1.2, h),
            "error": "#ffb4ab",
            "fgError": "#690005",
            "success": "#36e27e",
            "fgSuccess": "#06381b",
            "warning": "#eec13a",
            "scrim": "#000000",
        }
    return {
        "mode": "light",
        "seed": seed_hex,
        "bg": oklch_to_hex(0.97, c_neutral * 0.6, h),
        "bgOpaque": oklch_to_hex(0.98, c_neutral * 0.5, h),
        "bgTile": oklch_to_hex(0.93, c_neutral * 0.8, h),
        "bgHigh": oklch_to_hex(0.89, c_neutral * 0.9, h),
        "surface0": oklch_to_hex(0.96, c_neutral * 0.6, h),
        "surface1": oklch_to_hex(0.93, c_neutral * 0.7, h),
        "surface2": oklch_to_hex(0.90, c_neutral * 0.8, h),
        "surface3": oklch_to_hex(0.86, c_neutral * 0.9, h),
        "accent": oklch_to_hex(0.45, c_primary, h),
        "accentHover": oklch_to_hex(0.40, c_primary, h),
        "fgAccent": "#ffffff",
        "accentMuted": oklch_to_hex(0.52, c_primary * 0.45, h),
        "accentContainer": oklch_to_hex(0.90, c_primary * 0.55, h),
        "fgAccentContainer": oklch_to_hex(0.22, c_primary * 0.85, h),
        "tertiary": oklch_to_hex(0.46, c_primary * 0.85, h_tert),
        "tertiaryContainer": oklch_to_hex(0.90, c_primary * 0.50, h_tert),
        "text": oklch_to_hex(0.18, c_neutral, h),
        "subtext": oklch_to_hex(0.36, c_neutral * 1.1, h),
        "subtextDim": oklch_to_hex(0.50, c_neutral, h),
        "outline": oklch_to_hex(0.72, c_neutral * 1.2, h),
        "outlineStrong": oklch_to_hex(0.52, c_neutral * 1.2, h),
        "error": "#ba1a1a",
        "fgError": "#ffffff",
        "success": "#146c2e",
        "fgSuccess": "#ffffff",
        "warning": "#7c5800",
        "scrim": "#000000",
    }


# All 28 External App-Theming Targets (Lucid Matugen union + Mandara 24-App Ledger)
APP_THEME_TARGETS: dict[str, str] = {
    "gtk3": ".config/gtk-3.0/scy-colors.css",
    "gtk4": ".config/gtk-4.0/scy-colors.css",
    "qt5ct": ".config/qt5ct/colors/scy-shell.conf",
    "qt6ct": ".config/qt6ct/colors/scy-shell.conf",
    "kitty": ".config/kitty/scy-theme.conf",
    "foot": ".config/foot/scy-theme.ini",
    "ghostty": ".config/ghostty/themes/scy-shell",
    "alacritty": ".config/alacritty/scy-theme.toml",
    "wezterm": ".config/wezterm/scy-colors.lua",
    "zed": ".config/zed/themes/scy-shell.json",
    "helix": ".config/helix/themes/scy-shell.toml",
    "neovim": ".config/nvim/lua/scy_palette.lua",
    "vscode": ".config/Code/User/scy-theme.json",
    "yazi": ".config/yazi/scy-theme.toml",
    "btop": ".config/btop/themes/scy-shell.theme",
    "cava": ".config/cava/scy-colors",
    "fuzzel": ".config/fuzzel/scy-colors.ini",
    "rofi": ".config/rofi/scy-colors.rasi",
    "vesktop": ".config/vesktop/themes/scy-shell.theme.css",
    "tmux": ".config/tmux/scy-theme.conf",
    "zellij": ".config/zellij/themes/scy-shell.kdl",
    "lazygit": ".config/lazygit/scy-theme.yml",
    "starship": ".config/starship-scy-palette.toml",
    "bat": ".config/bat/themes/scy-shell.tmTheme",
    "delta": ".config/git/scy-delta.gitconfig",
    "obsidian": ".config/scy-shell/exports/obsidian-snippet.css",
    "zen_browser": ".config/scy-shell/exports/zen-userChrome.css",
    "hyprland_colors": ".config/hypr/scy-shell/colors.lua",
}


def _render_app_template(app_id: str, t: dict[str, str]) -> str:
    if app_id in ("gtk3", "gtk4"):
        return (
            f"/* Generated by Scy-Shell Theme Coordinator */\n"
            f"@define-color accent_bg_color {t['accent']};\n"
            f"@define-color accent_fg_color {t['fgAccent']};\n"
            f"@define-color window_bg_color {t['bg']};\n"
            f"@define-color window_fg_color {t['text']};\n"
            f"@define-color card_bg_color {t['bgTile']};\n"
        )
    if app_id == "kitty":
        return (
            f"# Generated by Scy-Shell\nbackground {t['bg']}\nforeground {t['text']}\n"
            f"cursor {t['accent']}\nselection_background {t['accentContainer']}\n"
            f"selection_foreground {t['fgAccentContainer']}\n"
        )
    if app_id == "ghostty":
        return f"background = {t['bg']}\nforeground = {t['text']}\ncursor-color = {t['accent']}\n"
    if app_id == "hyprland_colors":
        return (
            "-- Generated by Scy-Shell Unified Theme Coordinator\n"
            "return {\n"
            f'  bg = "{t["bg"]}",\n'
            f'  accent = "{t["accent"]}",\n'
            f'  accent_container = "{t["accentContainer"]}",\n'
            f'  text = "{t["text"]}",\n'
            f'  outline = "{t["outline"]}",\n'
            f'  error = "{t["error"]}",\n'
            "}\n"
        )
    return (
        f"# Scy-Shell M3 Expressive Palette ({app_id})\n"
        f"# bg={t['bg']} fg={t['text']} accent={t['accent']} container={t['accentContainer']}\n"
    )


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ScyThemeCoordinator:
    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store
        self.ledger_path = self.store.state_dir / "theme-ledger.json"
        self.tokens_path = self.store.state_dir / "palette-tokens.json"

    def _load_ledger(self) -> dict[str, dict[str, str]]:
        if not self.ledger_path.exists():
            return {}
        try:
            return json.loads(self.ledger_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_ledger(self, ledger: dict[str, dict[str, str]]) -> None:
        atomic_write_text(self.ledger_path, json.dumps(ledger, indent=2) + "\n")

    def write_mandara_portable_m3_look(self) -> Path:
        """Writes `~/.config/mandara/looks/scy-m3-expressive.toml` (compatible with stock Mandara `user_looks.rs`!)."""
        look_path = self.store.home / ".config" / "mandara" / "looks" / "scy-m3-expressive.toml"
        look_doc = {
            "format": 1,
            "id": "scy-m3-expressive",
            "name": "Scy-Shell · Material 3 Expressive",
            "author": "Scy-Shell",
            "parent": "corniche-dusk",
            "created": "2026-11-24",
            "wallpaper_colors": True,
            "unset": [],
            "settings": {
                "typography": {
                    "ui_font": self.store.doc["identity"].get("font_family", "Google Sans"),
                    "display_font": self.store.doc["identity"].get("font_family", "Google Sans"),
                },
                "style": {
                    "radius_scale": 1.25,
                },
            },
        }
        atomic_write_text(look_path, dumps_toml(look_doc))
        return look_path

    def apply_palette(
        self,
        seed_hex: str | None = None,
        dark_mode: bool | None = None,
        enabled_apps: list[str] | None = None,
        adopt_modified: bool = False,
    ) -> dict[str, Any]:
        ident = self.store.doc["identity"]
        if seed_hex is not None:
            ident["accent_seed"] = seed_hex
        if dark_mode is not None:
            ident["dark_mode"] = dark_mode

        tokens = generate_m3_expressive_tokens(
            ident.get("accent_seed", "#ffb1c4"),
            dark=bool(ident.get("dark_mode", True)),
        )
        atomic_write_text(self.tokens_path, json.dumps(tokens, indent=2) + "\n")

        # Sync Lucid theme mode & Mandara theme mode
        self.store.doc["providers"]["lucid"]["prefs"]["themeDark"] = bool(ident["dark_mode"])
        self.store.doc["providers"]["mandara"]["config"].setdefault("theme", {})["mode"] = (
            "dark" if ident["dark_mode"] else "light"
        )
        self.write_mandara_portable_m3_look()
        self.store.flush_all()

        # Apply to enabled external apps with SHA-256 tamper protection!
        targets = enabled_apps if enabled_apps is not None else list(APP_THEME_TARGETS.keys())
        ledger = self._load_ledger()
        written: list[str] = []
        skipped_tampered: list[str] = []

        for app_id in targets:
            rel = APP_THEME_TARGETS.get(app_id)
            if not rel:
                continue
            target_file = self.store.home / rel
            rendered = _render_app_template(app_id, tokens)
            new_hash = _sha256_text(rendered)

            if target_file.exists():
                disk_text = target_file.read_text(encoding="utf-8", errors="replace")
                disk_hash = _sha256_text(disk_text)
                recorded_hash = ledger.get(app_id, {}).get("sha256")
                if recorded_hash != disk_hash:
                    if not adopt_modified:
                        skipped_tampered.append(app_id)
                        continue
                    # Backup user-modified file before adopting!
                    bdir = self.store.backup_root / "app-themes"
                    bdir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target_file, bdir / f"{app_id}-{int(time.time())}.bak")

            atomic_write_text(target_file, rendered)
            ledger[app_id] = {"path": str(target_file), "sha256": new_hash}
            written.append(app_id)

        self._save_ledger(ledger)
        return {
            "tokens": tokens,
            "written_apps": written,
            "skipped_user_modified_apps": skipped_tampered,
        }
