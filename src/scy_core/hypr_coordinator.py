"""Phase 8 — Safe, Version-Validated Hyprland Coordinator (0.55+ Lua & .conf) + Complete Shortcut Ledger."""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .paths import lucid_keybinds_template, schema_dir
from .process_guard import ProcessSupervisor
from .toml_io import atomic_write_text

MANDARA_UNIQUE_BINDS: list[dict[str, Any]] = [
    {
        "id": "scy-ai-agent",
        "keys": "SUPER + SHIFT + A",
        "desc": "Local AI Command Agent (Mandara FunctionGemma / Qwen3)",
        "category": "Scy-Shell",
        "type": "exec",
        "cmd": "scy-shell-ipc agent toggle",
    },
    {
        "id": "scy-sidebar",
        "keys": "SUPER + SHIFT + B",
        "desc": "Toggle Mandara Sidebar / Edge Drawer",
        "category": "Scy-Shell",
        "type": "exec",
        "cmd": "scy-shell-ipc sidebar toggle",
    },
    {
        "id": "scy-look-switcher",
        "keys": "SUPER + ALT + T",
        "desc": "Switch Visual Look / Theme Preset (20 Looks)",
        "category": "Scy-Shell",
        "type": "exec",
        "cmd": "scy-shell-ipc look picker",
    },
    {
        "id": "scy-plugins-drawer",
        "keys": "SUPER + SHIFT + P",
        "desc": "Open 89 Built-in & WASM Plugins Studio",
        "category": "Scy-Shell",
        "type": "exec",
        "cmd": "scy-shell-ipc plugins",
    },
    {
        "id": "scy-game-shelf",
        "keys": "SUPER + SHIFT + G",
        "desc": "Open 3D Steam / Lutris / Heroic Game Shelf",
        "category": "Scy-Shell",
        "type": "exec",
        "cmd": "scy-shell-ipc games",
    },
    {
        "id": "scy-wallgen",
        "keys": "SUPER + SHIFT + W",
        "desc": "Open Wallgen Procedural Wallpaper Generator (13 Styles)",
        "category": "Scy-Shell",
        "type": "exec",
        "cmd": "scy-shell-ipc wallgen",
    },
]

# Exact shared IPC targets rewritten in Lucid's keybinds.json so active_providers routing works seamlessly!
SHARED_CMD_REWRITES: dict[str, str] = {
    "qs ipc call launcher toggle": "scy-shell-ipc launcher toggle",
    "qs ipc call launcher wallpaper": "scy-shell-ipc wallpaper picker",
    "qs ipc call launcher clipboard": "scy-shell-ipc clipboard toggle",
    "qs ipc call lock lock": "scy-shell-ipc lock",
    "qs ipc call controlcentre toggle": "scy-shell-ipc quick toggle",
    "qs ipc call snap toggle": "scy-shell-ipc shot region",
    "qs ipc call screenshot full": "scy-shell-ipc shot screen",
    "qs ipc call workspaces toggle": "scy-shell-ipc overview toggle",
    "qs ipc call session toggle": "scy-shell-ipc power toggle",
    "qs ipc call settings toggle": "scy-shell-ipc studio",
    "qs ipc call switcher next": "scy-shell-ipc switcher next",
    "qs ipc call switcher prev": "scy-shell-ipc switcher prev",
}


def _lua_literal(val: Any) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return repr(val)
    s = str(val).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


def normalize_chord(keys_str: str, opts: dict[str, Any] | None = None) -> str:
    parts = [p.strip().upper() for p in keys_str.split("+") if p.strip()]
    if not parts:
        return ""
    mods = sorted("CTRL" if p == "CONTROL" else p for p in parts[:-1])
    key = parts[-1]
    rel = ":RELEASE" if (opts or {}).get("release") else ""
    return "+".join(mods + [key]) + rel


class ScyHyprCoordinator:
    def __init__(self, store: ScyConfigStore, keybinds_source: Path | None = None) -> None:
        self.store = store
        self.hypr_dir = self.store.home / ".config" / "hypr"
        self.scy_hypr_dir = self.hypr_dir / "scy-shell"
        self.lucid_settings_lua = self.hypr_dir / "lucid-settings.lua"
        self.lucid_keybinds_json = self.store.home / ".config" / "lucid" / "keybinds.json"
        self.trial_state_path = self.store.state_dir / "hypr-trial.json"
        self.keybinds_source = keybinds_source or lucid_keybinds_template()
        self.keybindings_catalogue_path = schema_dir() / "keybindings_catalogue.json"

        self.allowed_hypr_keys: set[str] = {
            m.original_key
            for m in self.store.schema.by_id.values()
            if m.scy_id.startswith("scy.providers.lucid.hypr.")
        }

    def validate_options(self, options: dict[str, Any]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        for k in options:
            if k not in self.allowed_hypr_keys:
                errors.append(f"Rejected unverified/invented Hyprland directive: '{k}'")
        return (len(errors) == 0, errors)

    def backup_hypr_dir(self, tag: str = "hypr-apply") -> Path:
        ts = time.strftime("%Y%m%d-%H%M%S")
        bdir = self.store.backup_root / f"{ts}-{tag}-{int(time.time_ns() % 100000)}"
        bdir.mkdir(parents=True, exist_ok=True)
        if self.hypr_dir.exists():
            shutil.copytree(self.hypr_dir, bdir / "hypr", dirs_exist_ok=True)
        if self.lucid_keybinds_json.exists():
            shutil.copy2(self.lucid_keybinds_json, bdir / "keybinds.json")
        return bdir

    def restore_hypr_backup(self, bdir: Path) -> None:
        saved_hypr = bdir / "hypr"
        if saved_hypr.exists():
            if self.hypr_dir.exists():
                shutil.rmtree(self.hypr_dir)
            shutil.copytree(saved_hypr, self.hypr_dir)
        saved_kb = bdir / "keybinds.json"
        if saved_kb.exists():
            self.lucid_keybinds_json.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(saved_kb, self.lucid_keybinds_json)

    def build_unified_keybinds(self, enable_bare_fn_media_keys: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        base_doc = json.loads(self.keybinds_source.read_text(encoding="utf-8"))
        binds: list[dict[str, Any]] = []
        seen_chords: dict[str, str] = {}
        collisions: list[dict[str, str]] = []

        for entry in base_doc.get("binds", []):
            item = dict(entry)
            if item.get("type") == "exec" and item.get("cmd") in SHARED_CMD_REWRITES:
                item["cmd"] = SHARED_CMD_REWRITES[item["cmd"]]
            # Bare F1..F12 ("Function keys" category) duplicate XF86* media keys and globally shadow
            # DesktopIcons.qml F2 (Rename) & F5 (Refresh) unless explicitly enabled for non-XF86 keyboards.
            if item.get("category") == "Function keys" and "enabled" not in item and not enable_bare_fn_media_keys:
                item["enabled"] = False
            if item.get("enabled", True) is not False:
                chord = normalize_chord(item.get("keys", ""), item.get("opts"))
                if chord in seen_chords:
                    collisions.append({"chord": chord, "first": seen_chords[chord], "second": item["id"]})
                else:
                    seen_chords[chord] = item["id"]
            binds.append(item)

        existing_ids = {b["id"] for b in binds}
        for mbind in MANDARA_UNIQUE_BINDS:
            if mbind["id"] in existing_ids:
                continue
            chord = normalize_chord(mbind["keys"])
            if chord in seen_chords:
                collisions.append({"chord": chord, "first": seen_chords[chord], "second": mbind["id"]})
                continue
            seen_chords[chord] = mbind["id"]
            binds.append(dict(mbind))

        return binds, collisions

    def build_desktop_icons_shortcuts(self) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        """Resolves all 22 DesktopIcons.qml keyActions (19 default-bound + 3 user-bindable) with live Prefs.desktopKeys overrides."""
        cat = json.loads(self.keybindings_catalogue_path.read_text(encoding="utf-8"))
        raw_overrides = self.store.doc["providers"]["lucid"]["prefs"].get("desktopKeys", "{}")
        try:
            overrides = json.loads(raw_overrides) if isinstance(raw_overrides, str) else dict(raw_overrides or {})
        except Exception:
            overrides = {}

        resolved: list[dict[str, Any]] = []
        seen_local: dict[str, str] = {}
        clashes: list[dict[str, str]] = []

        for action in cat["desktop_icons_qml_key_actions"]:
            aid = action["id"]
            active_keys = overrides.get(aid, action["default_keys"])
            norm = normalize_chord(active_keys) if active_keys else ""
            if norm:
                if norm in seen_local:
                    clashes.append({"chord": norm, "first": seen_local[norm], "second": aid})
                else:
                    seen_local[norm] = aid
            resolved.append({
                **action,
                "active_keys": active_keys,
                "overridden": aid in overrides,
            })

        return resolved, clashes

    def build_complete_shortcut_ledger(self, enable_bare_fn_media_keys: bool = False) -> dict[str, Any]:
        """Full accounting across Lucid compositor (61), Mandara added (6 -> 67), DesktopIcons (17 grouped / 22 QML slots + 6 board nav), and Mandara default_keybinds (25)."""
        cat = json.loads(self.keybindings_catalogue_path.read_text(encoding="utf-8"))
        comp_binds, comp_collisions = self.build_unified_keybinds(enable_bare_fn_media_keys=enable_bare_fn_media_keys)
        desktop_actions, desktop_clashes = self.build_desktop_icons_shortcuts()

        comp_chords = {
            normalize_chord(b["keys"], b.get("opts")): b["id"]
            for b in comp_binds
            if b.get("enabled", True) is not False
        }
        cross_scope_overlaps: list[dict[str, str]] = []
        for da in desktop_actions:
            norm = normalize_chord(da["active_keys"]) if da["active_keys"] else ""
            if norm and norm in comp_chords:
                cross_scope_overlaps.append({
                    "chord": norm,
                    "compositor_bind": comp_chords[norm],
                    "desktop_icons_action": da["id"],
                })

        return {
            "counts": {
                "lucid_compositor_original": 61,
                "mandara_unique_added": len(MANDARA_UNIQUE_BINDS),
                "compositor_unified_total": len(comp_binds),
                "desktop_icons_stage0_grouped": len(cat["stage0_17_desktop_icons_shortcuts"]),
                "desktop_icons_qml_key_actions_total": len(desktop_actions),
                "desktop_icons_qml_active_bound": sum(1 for d in desktop_actions if d["active_keys"]),
                "desktop_icons_qml_unbound_slots": sum(1 for d in desktop_actions if not d["active_keys"]),
                "icon_board_navigation_handlers": len(cat["icon_board_navigation_handlers"]),
                "mandara_default_keybinds_accounted": len(cat["mandara_25_default_keybinds_accounting"]),
            },
            "compositor_collisions": comp_collisions,
            "desktop_icons_intra_clashes": desktop_clashes,
            "cross_scope_compositor_overlaps": cross_scope_overlaps,
            "compositor_binds": comp_binds,
            "stage0_17_desktop_icons_shortcuts": cat["stage0_17_desktop_icons_shortcuts"],
            "desktop_icons_qml_key_actions": desktop_actions,
            "icon_board_navigation_handlers": cat["icon_board_navigation_handlers"],
            "mandara_25_default_keybinds_accounting": cat["mandara_25_default_keybinds_accounting"],
        }

    def emit_modular_configs(self, extra_options: dict[str, Any] | None = None) -> dict[str, Any]:
        merged_opts = dict(self.store.doc["providers"]["lucid"]["hypr"])
        if extra_options:
            merged_opts.update(extra_options)

        ok, errors = self.validate_options(merged_opts)
        if not ok:
            raise ValueError("; ".join(errors))

        backup_dir = self.backup_hypr_dir("before-emit")
        self.scy_hypr_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write ~/.config/hypr/lucid-settings.lua
        opt_lines = ["return {", "  options = {"]
        for k in sorted(merged_opts):
            opt_lines.append(f"    [{_lua_literal(k)}] = {_lua_literal(merged_opts[k])},")
        opt_lines.extend(["  }", "}"])
        atomic_write_text(self.lucid_settings_lua, "\n".join(opt_lines) + "\n")

        # 2. Write ~/.config/hypr/scy-shell/init.lua (Hyprland 0.57+ Lua layer rules)
        lua_init = (
            "-- Generated by Scy-Shell v2.0 Hyprland Coordinator (Hyprland 0.57+ Lua)\n"
            "-- Applies harmonized frosted glass blur rules to Lucid Quickshell & Mandara GPUI surfaces\n"
            'pcall(function()\n'
            '  hl.layer_rule({ match = { namespace = "quickshell" }, blur = true, ignore_alpha = 0.2 })\n'
            '  hl.layer_rule({ match = { namespace = "mandara-bar" }, blur = true, ignore_alpha = 0.2 })\n'
            '  hl.layer_rule({ match = { namespace = "mandara-dock" }, blur = true, ignore_alpha = 0.2 })\n'
            '  hl.layer_rule({ match = { namespace = "mandara-panel" }, blur = true, ignore_alpha = 0.2 })\n'
            '  hl.layer_rule({ match = { namespace = "mandara-sidebar" }, blur = true, ignore_alpha = 0.2 })\n'
            'end)\n'
        )
        atomic_write_text(self.scy_hypr_dir / "init.lua", lua_init)

        # 3. Write ~/.config/lucid/keybinds.json
        binds, collisions = self.build_unified_keybinds()
        atomic_write_text(
            self.lucid_keybinds_json,
            json.dumps({"version": 1, "binds": binds}, indent=2, ensure_ascii=False) + "\n",
        )

        # 4. Write ~/.config/hypr/scy-shell/scy-shell.conf (Hyprland 0.57+ drop-in syntax)
        vrr_policy = str(self.store.get_setting("scy.performance.vrr_policy") or "off")
        vrr_num = 2 if vrr_policy == "fullscreen-only" else (1 if vrr_policy == "always" else 0)
        conf_lines = [
            "# Generated by Scy-Shell v2.0 Hyprland Coordinator (Hyprland 0.57+ syntax)",
            "# Never edit directly; managed safely via Scy-Shell Studio.",
            "exec-once = test -x ~/.local/bin/scy-shell && exec ~/.local/bin/scy-shell start",
            "",
            "# Hyprland 0.57+ named-property layerrule syntax for Scy-Shell surfaces",
            "layerrule = blur on, match:namespace quickshell",
            "layerrule = ignore_alpha 0.2, match:namespace quickshell",
            "layerrule = blur on, match:namespace mandara-bar",
            "layerrule = ignore_alpha 0.2, match:namespace mandara-bar",
            "layerrule = blur on, match:namespace mandara-dock",
            "layerrule = ignore_alpha 0.2, match:namespace mandara-dock",
            "layerrule = blur on, match:namespace mandara-panel",
            "layerrule = ignore_alpha 0.2, match:namespace mandara-panel",
            f"misc:vrr = {vrr_num}",
            "",
        ]
        for k in sorted(merged_opts):
            if k.startswith("lucid."):
                continue
            colon_key = k.replace(".", ":")
            v = merged_opts[k]
            v_str = ("true" if v else "false") if isinstance(v, bool) else str(v)
            conf_lines.append(f"{colon_key} = {v_str}")

        conf_lines.append("")
        for b in binds:
            if b.get("enabled", True) is False or b.get("type") != "exec":
                continue
            parts = [p.strip() for p in b["keys"].split("+") if p.strip()]
            mods = " ".join(parts[:-1])
            key = parts[-1] if parts else ""
            bind_kw = "bindr" if (b.get("opts") or {}).get("release") else ("bindl" if (b.get("opts") or {}).get("locked") else "bind")
            conf_lines.append(f"{bind_kw} = {mods}, {key}, exec, {b['cmd']}")

        atomic_write_text(self.scy_hypr_dir / "scy-shell.conf", "\n".join(conf_lines) + "\n")
        dedup_report = ProcessSupervisor().deduplicate_hyprland_autostart(self.hypr_dir)
        self._inject_non_destructive_include()

        return {
            "backup_dir": str(backup_dir),
            "binds_count": len(binds),
            "collisions": collisions,
            "autostart_deduplication": dedup_report,
            "lua_init": str(self.scy_hypr_dir / "init.lua"),
            "conf_dropin": str(self.scy_hypr_dir / "scy-shell.conf"),
        }

    def _inject_non_destructive_include(self) -> None:
        lua_main = self.hypr_dir / "hyprland.lua"
        conf_main = self.hypr_dir / "hyprland.conf"

        if lua_main.exists():
            txt = lua_main.read_text(encoding="utf-8")
            marker = 'pcall(require, "scy-shell.init")'
            if marker not in txt:
                if "hypr-user" in txt:
                    idx = txt.find("hypr-user")
                    line_start = txt.rfind("\n", 0, idx) + 1
                    txt = txt[:line_start] + f"-- Scy-Shell modular hook\n{marker}\n" + txt[line_start:]
                else:
                    txt = txt.rstrip() + f"\n\n-- Scy-Shell modular hook\n{marker}\n"
                atomic_write_text(lua_main, txt)
        elif conf_main.exists():
            txt = conf_main.read_text(encoding="utf-8")
            marker = "source = ~/.config/hypr/scy-shell/scy-shell.conf"
            if marker not in txt:
                txt = txt.rstrip() + f"\n\n# Scy-Shell modular drop-in\n{marker}\n"
                atomic_write_text(conf_main, txt)

    def begin_trial(self, proposed_options: dict[str, Any], timeout_s: int = 15) -> dict[str, Any]:
        res = self.emit_modular_configs(extra_options=proposed_options)
        trial = {
            "active": True,
            "backup_dir": res["backup_dir"],
            "expires_at": time.time() + timeout_s,
            "proposed_options": proposed_options,
        }
        atomic_write_text(self.trial_state_path, json.dumps(trial, indent=2) + "\n")
        return trial

    def confirm_trial(self) -> dict[str, Any]:
        if not self.trial_state_path.exists():
            return {"ok": False, "error": "No active Hyprland trial"}
        trial = json.loads(self.trial_state_path.read_text(encoding="utf-8"))
        for k, v in trial.get("proposed_options", {}).items():
            self.store.set_setting(f"scy.providers.lucid.hypr.{k}", v, flush=False)
        self.store.flush_all()
        self.trial_state_path.unlink()
        return {"ok": True, "confirmed": True}

    def revert_trial(self) -> dict[str, Any]:
        if not self.trial_state_path.exists():
            return {"ok": False, "error": "No active Hyprland trial"}
        trial = json.loads(self.trial_state_path.read_text(encoding="utf-8"))
        self.restore_hypr_backup(Path(trial["backup_dir"]))
        self.trial_state_path.unlink()
        return {"ok": True, "reverted_to": trial["backup_dir"]}
