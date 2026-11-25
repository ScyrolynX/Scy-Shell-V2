"""Scy-Shell v2.0 — Strictly Decoupled Lock Screen (11) & Login Experience (12) Coordinator.

Security invariants:
1. Lock Screen (`11 — Lock Screen`) and Login/Greeter (`12 — Login Experience`) use completely
   independent configuration state (`scy.lock.*` / `lockPreset` vs `scy.login.*` / `login-greeter.json`).
   Editing Lock Screen settings NEVER overwrites Login/Greeter configuration.
2. Both share harmonized visual tokens (`ScyDesignTokens`) while preserving independent layouts,
   wallpapers, blur levels, clock formats, and visibility toggles.
3. Passwords, PAM tokens, or plaintext credentials are NEVER accepted or written to disk.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .theme_engine import generate_m3_expressive_tokens
from .toml_io import atomic_write_text, dumps_toml

LUCID_6_LOCK_PRESETS: tuple[str, ...] = ("centre", "split", "panel", "minimal", "bento", "deck")
MANDARA_6_AUTH_DESIGNS: tuple[str, ...] = (
    "Mandara",
    "MidnightCard",
    "MaterialYou",
    "Ghostline",
    "ChromeHalo",
    "Meridian",
)
FORBIDDEN_CREDENTIAL_KEYS: frozenset[str] = frozenset(
    {"password", "passwd", "passphrase", "pin", "secret", "pam_password", "auth_token"}
)


class ScyPreAuthCoordinator:
    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store

    @staticmethod
    def assert_no_credentials(payload: dict[str, Any]) -> None:
        for k, v in payload.items():
            if k.strip().lower() in FORBIDDEN_CREDENTIAL_KEYS:
                raise ValueError(f"Security violation: credential field '{k}' may never be stored in shell configuration.")
            if isinstance(v, dict):
                ScyPreAuthCoordinator.assert_no_credentials(v)

    def set_lock_design(self, provider: str, design_or_preset: str) -> dict[str, Any]:
        """Updates ONLY Section 11 (Session Lock Screen) — never touches Section 12 Login/Greeter."""
        if provider == "lucid":
            if design_or_preset not in LUCID_6_LOCK_PRESETS:
                raise ValueError(f"Unknown Lucid lock preset: {design_or_preset}")
            self.store.set_provider("lock_screen", "lucid")
            self.store.set_setting("scy.providers.lucid.prefs.lockPreset", design_or_preset)
            return {"section": "11-lock-screen", "provider": "lucid", "preset": design_or_preset}
        if provider == "mandara":
            if design_or_preset not in MANDARA_6_AUTH_DESIGNS:
                raise ValueError(f"Unknown Mandara AuthDesign: {design_or_preset}")
            self.store.set_provider("lock_screen", "mandara")
            self.store.doc["providers"]["mandara"]["config"].setdefault("lock", {})["design"] = design_or_preset
            self.store.flush_all()
            return {"section": "11-lock-screen", "provider": "mandara", "design": design_or_preset}
        raise ValueError(f"Invalid lock provider: {provider}")

    def set_login_design(self, greeter_target: str, user_list_style: str = "avatar-cards", design: str | None = None) -> dict[str, Any]:
        """Updates ONLY Section 12 (Pre-Session Login Experience) — never touches Section 11 Lock Screen."""
        target_map = {
            "sddm-scy": "scy-sddm",
            "scy-sddm": "scy-sddm",
            "greetd-mandara": "scy-greetd",
            "scy-greetd": "scy-greetd",
            "preserve": "preserve",
            "external": "preserve",
        }
        if greeter_target not in target_map:
            raise ValueError(f"Unknown greeter target: {greeter_target}")
        norm_target = target_map[greeter_target]
        self.store.set_setting("scy.login.greeter_target", norm_target, flush=False)
        if user_list_style in ("avatar-cards", "carousel", "compact-dropdown"):
            self.store.set_setting("scy.login.user_list_style", user_list_style, flush=False)
        if design:
            self.store.doc["providers"]["mandara"]["greeter"]["design"] = design
        self.store.flush_all()
        self.stage_display_manager_configs()
        return {"section": "12-login-experience", "greeter_target": norm_target, "user_list_style": user_list_style, "design": design}

    def copy_visual_tokens_lock_to_login_once(self) -> dict[str, Any]:
        """Explicit user-invoked one-shot copy of wallpaper/blur from Lock (11) to Login (12) without persistent coupling."""
        lock_wp = str(self.store.get_setting("scy.lock.wallpaper_override") or "")
        lock_blur = int(self.store.get_setting("scy.providers.lucid.prefs.lockBlur") or 36)
        if lock_wp:
            self.store.set_setting("scy.login.background_path", lock_wp, flush=False)
        self.store.set_setting("scy.login.background_blur", min(80, max(0, lock_blur)), flush=False)
        # Keep lockLoginSync and mirror_lock_layout strictly False so future edits stay decoupled!
        self.store.set_setting("scy.providers.lucid.prefs.lockLoginSync", False, flush=False)
        self.store.set_setting("scy.login.mirror_lock_layout", False, flush=True)
        paths = self.stage_display_manager_configs()
        return {"ok": True, "copied_blur": lock_blur, "staged": {k: str(v) for k, v in paths.items()}}

    def stage_display_manager_configs(self) -> dict[str, Path]:
        """Generates ready-to-install staged configs for BOTH SDDM (`scy-sddm`) and `greetd` (`scy-greetd`)
        exclusively from Section 12 Login Experience settings + shared `ScyDesignTokens`."""
        ident = self.store.doc["identity"]
        tok = generate_m3_expressive_tokens(
            ident.get("accent_seed", "#7aa2f7"),
            dark=bool(ident.get("dark_mode", True)),
        )
        login_cfg = self.store._build_design_tokens_doc()["login_experience"]
        self.assert_no_credentials(login_cfg)

        # 1. Stage SDDM theme.conf (reads ONLY Section 12 `login_cfg`, NEVER `lockPreset`!)
        sddm_lines = [
            "[General]",
            "# Generated by Scy-Shell v2.0 Section 12 — Login Experience (Decoupled from Lock Screen)",
            f"isLight={'false' if ident.get('dark_mode', True) else 'true'}",
            f"userListStyle={login_cfg['user_list_style']}",
            f"passwordFieldStyle={login_cfg['password_style']}",
            f"background={login_cfg['background_path']}",
            f"blurRadius={login_cfg['background_blur']}",
            f"avatarRing={'true' if login_cfg['avatar_ring'] else 'false'}",
            f"showSessionPicker={'true' if login_cfg['show_session_picker'] else 'false'}",
            f"showPowerActions={'true' if login_cfg['show_power_actions'] else 'false'}",
            f"clock24h={'true' if login_cfg['clock_24h'] else 'false'}",
            f"loginAnimation={login_cfg['login_animation']}",
            f"highContrast={'true' if login_cfg['high_contrast'] else 'false'}",
            f"uiScale={login_cfg['ui_scale']}",
            f"accent={tok['accent']}",
            f"accentHover={tok['accentHover']}",
            f"fgAccent={tok['fgAccent']}",
            f"accentMuted={tok['accentMuted']}",
            f"accentContainer={tok['accentContainer']}",
            f"fgAccentContainer={tok['fgAccentContainer']}",
            f"bgOpaque={tok['bgOpaque']}",
            f"bgHigh={tok['bgHigh']}",
            f"text={tok['text']}",
            f"subtext={tok['subtext']}",
            f"outline={tok['outline']}",
            f"fontFamily={ident.get('font_family', 'Google Sans')}",
        ]
        atomic_write_text(self.store.lucid_sddm_stage_path, "\n".join(sddm_lines) + "\n")

        # 2. Stage Mandara /etc/mandara/greeter.toml
        greeter_doc = dict(self.store.doc["providers"]["mandara"]["greeter"])
        self.assert_no_credentials(greeter_doc)
        greeter_doc["font"] = ident.get("font_family", "Google Sans")
        greeter_doc["show_power_buttons"] = bool(login_cfg["show_power_actions"])
        greeter_doc["show_session_selector"] = bool(login_cfg["show_session_picker"])
        if login_cfg["background_path"]:
            greeter_doc["wallpaper"] = login_cfg["background_path"]
        greeter_doc["scy_login"] = login_cfg
        t_sec = dict(greeter_doc.get("theme") or {})
        t_sec["accent"] = tok["accent"]
        t_sec["light"] = not bool(ident.get("dark_mode", True))
        greeter_doc["theme"] = t_sec
        atomic_write_text(self.store.mandara_greeter_stage_path, dumps_toml(greeter_doc))

        # 3. Also keep JSON mirror up to date
        atomic_write_text(self.store.login_greeter_path, json.dumps(login_cfg, indent=2) + "\n")

        return {
            "lucid_sddm_theme_conf": self.store.lucid_sddm_stage_path,
            "mandara_greeter_toml": self.store.mandara_greeter_stage_path,
            "login_greeter_json": self.store.login_greeter_path,
        }
