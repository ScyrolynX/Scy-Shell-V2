"""Scy-Shell v2.0 — Intelligent Performance, Dock Intelligence, Control Center & Productivity Layer."""
from __future__ import annotations

import ast
import json
import math
import operator
import os
import re
import shutil
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore
from .toml_io import atomic_write_text

PERFORMANCE_TIERS: dict[str, dict[str, Any]] = {
    "max-quality": {
        "id": "max-quality",
        "label": "Maximum Visual Quality",
        "tradeoff_summary": "Enables 4-pass Kawase glass blur (size 10), soft multi-layer drop shadows, accent edge glow, full spring animations, and live dock previews. Highest GPU shader cost (~3–5% GPU on modern dGPU/iGPU).",
        "settings": {
            "scy.performance.tier": "max-quality",
            "scy.effects.blur_strength": 4,
            "scy.effects.blur_radius": 10,
            "scy.effects.shadow_softness": 36,
            "scy.effects.glow_intensity": 0.32,
            "scy.effects.motion_preset": "expressive-spring",
            "scy.providers.lucid.prefs.reduceMotion": False,
        },
    },
    "balanced": {
        "id": "balanced",
        "label": "Balanced (Recommended)",
        "tradeoff_summary": "Uses 3-pass optimized frosted glass (radius 8), clean medium shadows, responsive spring transitions, and lazy offscreen Studio tab unloading. Ideal daily balance of beauty and low GPU/CPU overhead.",
        "settings": {
            "scy.performance.tier": "balanced",
            "scy.effects.blur_strength": 3,
            "scy.effects.blur_radius": 8,
            "scy.effects.shadow_softness": 24,
            "scy.effects.glow_intensity": 0.18,
            "scy.effects.motion_preset": "expressive-spring",
            "scy.performance.lazy_studio_tabs": True,
            "scy.providers.lucid.prefs.reduceMotion": False,
        },
    },
    "performance": {
        "id": "performance",
        "label": "Performance (High Refresh / Low Latency)",
        "tradeoff_summary": "Reduces compositor blur to 1 fast pass (radius 4), disables outer shadows and glow shaders, switches animations to crisp short curves, and enables fullscreen VRR. Maximizes frame pacing for 144Hz–360Hz displays and gaming.",
        "settings": {
            "scy.performance.tier": "performance",
            "scy.effects.blur_strength": 1,
            "scy.effects.blur_radius": 4,
            "scy.effects.shadow_softness": 0,
            "scy.effects.glow_intensity": 0.0,
            "scy.effects.motion_preset": "crisp-snappy",
            "scy.performance.vrr_policy": "fullscreen-only",
        },
    },
    "battery": {
        "id": "battery",
        "label": "Battery Efficiency",
        "tradeoff_summary": "Replaces live multi-pass backdrop blur with opaque Obsidian Matte tinted surfaces (0 blur passes), disables decorative animations/glow, and minimizes wakeups to extend laptop battery life.",
        "settings": {
            "scy.performance.tier": "battery",
            "scy.effects.material_preset": "obsidian-matte",
            "scy.effects.blur_strength": 0,
            "scy.effects.blur_radius": 0,
            "scy.effects.shadow_softness": 0,
            "scy.effects.glow_intensity": 0.0,
            "scy.effects.motion_preset": "minimal",
            "scy.providers.lucid.prefs.reduceMotion": True,
        },
    },
}


class ScyPerformanceAdvisor:
    """Hardware capability detector and transparent performance tier controller."""

    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store

    def probe_hardware(self) -> dict[str, Any]:
        cpu_cores = os.cpu_count() or 4
        cpu_model = "Generic CPU"
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.lower().startswith("model name"):
                    cpu_model = line.split(":", 1)[1].strip()
                    break
        except OSError:
            pass

        mem_gib = 8.0
        try:
            for line in Path("/proc/meminfo").read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    mem_gib = round(kb / (1024 * 1024), 2)
                    break
        except (OSError, ValueError, IndexError):
            pass

        batteries = list(Path("/sys/class/power_supply").glob("BAT*")) if Path("/sys/class/power_supply").exists() else []
        on_battery = False
        battery_percent: int | None = None
        for bat in batteries:
            try:
                status = (bat / "status").read_text(encoding="utf-8").strip().lower()
                if status == "discharging":
                    on_battery = True
                cap = (bat / "capacity").read_text(encoding="utf-8").strip()
                battery_percent = int(cap)
            except (OSError, ValueError):
                pass

        drm_cards: list[str] = []
        if Path("/sys/class/drm").exists():
            for card in sorted(Path("/sys/class/drm").glob("card[0-9]")):
                drm_cards.append(card.name)

        is_software_gl = any(
            k in cpu_model.lower() for k in ("qemu", "kvm", "virtual")
        ) and not drm_cards

        if on_battery and (battery_percent is not None and battery_percent <= 25):
            recommended = "battery"
            reason = f"Laptop is discharging at {battery_percent}% battery; Battery Efficiency minimizes GPU shader & timer wakeups."
        elif is_software_gl or mem_gib < 4.5 or cpu_cores <= 2:
            recommended = "performance"
            reason = f"Detected constrained/virtualized hardware ({cpu_cores} threads, {mem_gib} GiB RAM); Performance tier avoids costly multi-pass blur."
        elif cpu_cores >= 12 and mem_gib >= 15.0 and not on_battery:
            recommended = "max-quality"
            reason = f"High-headroom system ({cpu_cores} threads, {mem_gib} GiB RAM on AC power) comfortably sustains 4-pass Kawase glass and full spring physics."
        else:
            recommended = "balanced"
            reason = f"System ({cpu_cores} threads, {mem_gib} GiB RAM) suits Balanced 3-pass frosted glass with lazy Studio tab loading."

        active_tier = str(self.store.get_setting("scy.performance.tier") or "balanced")
        return {
            "cpu_model": cpu_model,
            "cpu_threads": cpu_cores,
            "memory_gib": mem_gib,
            "has_battery": bool(batteries),
            "on_battery": on_battery,
            "battery_percent": battery_percent,
            "drm_cards": drm_cards,
            "active_tier": active_tier,
            "active_tier_details": PERFORMANCE_TIERS.get(active_tier, PERFORMANCE_TIERS["balanced"]),
            "recommended_tier": recommended,
            "recommendation_reason": reason,
            "tiers": PERFORMANCE_TIERS,
        }

    def apply_tier(self, tier_id: str) -> dict[str, Any]:
        if tier_id not in PERFORMANCE_TIERS:
            raise ValueError(f"Unknown performance tier '{tier_id}'. Expected one of {list(PERFORMANCE_TIERS)}")
        tdef = PERFORMANCE_TIERS[tier_id]
        for sid, val in tdef["settings"].items():
            if sid in self.store.schema.by_id:
                self.store.set_setting(sid, val, flush=False, validate=True)
        self.store.flush_all()
        return {
            "ok": True,
            "tier": tier_id,
            "label": tdef["label"],
            "tradeoff_summary": tdef["tradeoff_summary"],
            "applied_settings": tdef["settings"],
        }


class ScyDockController:
    """Single-owner dock controller + intelligent app pinning, groups, separators, recents & frequents."""

    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store
        self.dock_items_file = self.store.config_dir / "dock-items.json"
        self._items = self._load_items()
        self._save_items()

    def _load_items(self) -> dict[str, Any]:
        default_doc = {
            "pinned": [
                {"type": "app", "id": "kitty.desktop", "label": "Terminal", "group": "system"},
                {"type": "app", "id": "org.kde.dolphin.desktop", "label": "Files", "group": "system"},
                {"type": "separator", "id": "sep-main"},
                {"type": "app", "id": "firefox.desktop", "label": "Browser", "group": "web"},
                {"type": "app", "id": "code.desktop", "label": "Code Editor", "group": "dev"},
                {"type": "separator", "id": "sep-studio"},
                {"type": "action", "id": "scy-studio", "label": "Scy-Shell Studio", "exec": "scy-shell studio"},
            ],
            "groups": {
                "system": {"label": "System & Utilities", "icon": "folder-system"},
                "web": {"label": "Web & Communication", "icon": "applications-internet"},
                "dev": {"label": "Development", "icon": "applications-development"},
            },
            "recent": [],
            "launch_counts": {},
        }
        if self.dock_items_file.exists():
            try:
                loaded = json.loads(self.dock_items_file.read_text(encoding="utf-8"))
                if isinstance(loaded, dict) and "pinned" in loaded:
                    default_doc.update(loaded)
            except Exception:
                pass
        return default_doc

    def _save_items(self) -> None:
        atomic_write_text(self.dock_items_file, json.dumps(self._items, indent=2) + "\n")

    def status(self) -> dict[str, Any]:
        dock_cfg = self.store._build_design_tokens_doc()["dock"]
        freq = sorted(
            self._items.get("launch_counts", {}).items(),
            key=lambda kv: kv[1],
            reverse=True,
        )[:3]
        return {
            **dock_cfg,
            "enabled": dock_cfg.get("mode") != "disabled" and bool(self.store.get_setting("scy.providers.lucid.prefs.dockEnabled") or dock_cfg.get("owner") == "mandara"),
            "pinned": self._items["pinned"],
            "groups": self._items["groups"],
            "recent": self._items["recent"][: int(dock_cfg.get("recent_limit") or 3)],
            "frequent": [{"id": k, "launches": v} for k, v in freq],
        }

    def switch_engine(self, engine: str) -> dict[str, Any]:
        eng = engine.strip().lower()
        if eng not in ("lucid", "mandara", "off", "none"):
            raise ValueError("Dock engine must be 'lucid', 'mandara', or 'off'")
        if eng in ("off", "none"):
            self.store.set_provider("dock", "none")
            return self.status()
        self.store.set_provider("dock", eng)
        return self.status()

    def pin_app(self, desktop_id: str, label: str | None = None, group: str | None = None) -> dict[str, Any]:
        did = desktop_id.strip()
        if not any(it.get("id") == did for it in self._items["pinned"]):
            entry: dict[str, Any] = {"type": "app", "id": did, "label": label or did.replace(".desktop", "").title()}
            if group:
                entry["group"] = group
            self._items["pinned"].append(entry)
            self._save_items()
        return self.status()

    def unpin_item(self, item_id: str) -> dict[str, Any]:
        self._items["pinned"] = [it for it in self._items["pinned"] if it.get("id") != item_id]
        self._save_items()
        return self.status()

    def add_separator(self, sep_id: str | None = None) -> dict[str, Any]:
        sid = sep_id or f"sep-{int(time.time())}"
        self._items["pinned"].append({"type": "separator", "id": sid})
        self._save_items()
        return self.status()

    def record_launch(self, desktop_id: str) -> dict[str, Any]:
        did = desktop_id.strip()
        counts = self._items.setdefault("launch_counts", {})
        counts[did] = int(counts.get(did, 0)) + 1
        rec = [x for x in self._items.get("recent", []) if x != did]
        rec.insert(0, did)
        self._items["recent"] = rec[:12]
        self._save_items()
        return self.status()


class ScyControlCenterBackend:
    """Real Linux/Wayland system integration for Section 09 & Section 10 Control Center."""

    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store

    @staticmethod
    def _run_quiet(cmd: list[str], timeout: float = 2.5) -> tuple[int, str]:
        if not shutil.which(cmd[0]):
            return (127, "")
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
            return (cp.returncode, (cp.stdout or "").strip())
        except Exception:
            return (1, "")

    def snapshot(self) -> dict[str, Any]:
        # Audio via wpctl or pactl
        vol_pct: int | None = None
        muted = False
        rc, out = self._run_quiet(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
        if rc == 0 and out:
            muted = "MUTED" in out.upper()
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)", out)
            if m:
                vol_pct = int(round(float(m.group(1)) * 100))

        # Brightness via /sys/class/backlight
        brightness_pct: int | None = None
        bl_root = Path("/sys/class/backlight")
        if bl_root.exists():
            for dev in bl_root.iterdir():
                try:
                    cur = int((dev / "brightness").read_text().strip())
                    mx = int((dev / "max_brightness").read_text().strip())
                    if mx > 0:
                        brightness_pct = int(round((cur / mx) * 100))
                        break
                except Exception:
                    continue

        # Network via nmcli
        wifi_enabled: bool | None = None
        active_ssid: str | None = None
        rc, out = self._run_quiet(["nmcli", "-t", "-f", "WIFI", "general"])
        if rc == 0 and out:
            wifi_enabled = out.strip().lower() == "enabled"
        rc, out = self._run_quiet(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"])
        if rc == 0 and out:
            for line in out.splitlines():
                if line.startswith("yes:"):
                    active_ssid = line.split(":", 1)[1]
                    break

        # Power profile
        rc, pprof = self._run_quiet(["powerprofilesctl", "get"])
        power_profile = pprof if rc == 0 and pprof else str(self.store.get_setting("scy.performance.tier") or "balanced")

        # Media via playerctl
        media: dict[str, Any] = {"playing": False, "title": "", "artist": ""}
        rc, mstatus = self._run_quiet(["playerctl", "status"])
        if rc == 0 and mstatus:
            media["playing"] = mstatus.lower() == "playing"
            _, title = self._run_quiet(["playerctl", "metadata", "title"])
            _, artist = self._run_quiet(["playerctl", "metadata", "artist"])
            media["title"] = title
            media["artist"] = artist

        dnd_val = False
        if "scy.providers.lucid.prefs.notifDnd" in self.store.schema.by_id:
            dnd_val = bool(self.store.get_setting("scy.providers.lucid.prefs.notifDnd"))

        return {
            "dnd": dnd_val,
            "caffeine": bool(self.store.get_setting("scy.control_center.show_caffeine")),
            "night_light": {
                "enabled": bool(self.store.get_setting("scy.control_center.show_night_light")),
                "kelvin": 4200,
            },
            "audio": {
                "available": shutil.which("wpctl") is not None or shutil.which("pactl") is not None,
                "volume_percent": vol_pct,
                "muted": muted,
            },
            "brightness": {
                "available": brightness_pct is not None or shutil.which("brightnessctl") is not None,
                "percent": brightness_pct,
            },
            "network": {
                "nmcli_available": shutil.which("nmcli") is not None,
                "wifi_enabled": wifi_enabled,
                "ssid": active_ssid,
            },
            "bluetooth": {
                "available": shutil.which("bluetoothctl") is not None,
            },
            "power_profile": power_profile,
            "performance_tier": self.store.get_setting("scy.performance.tier"),
            "active_profile": self.store.get_setting("scy.profiles.active"),
            "media": media,
        }


# Safe AST math evaluator (no eval!)
_SAFE_OPS: dict[type[Any], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}
_SAFE_FUNCS: dict[str, Any] = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "abs": abs,
    "round": round,
    "pi": math.pi,
    "e": math.e,
}

_UNIT_FACTORS_TO_BASE: dict[str, tuple[str, float]] = {
    "mm": ("len", 0.001),
    "cm": ("len", 0.01),
    "m": ("len", 1.0),
    "km": ("len", 1000.0),
    "in": ("len", 0.0254),
    "ft": ("len", 0.3048),
    "mi": ("len", 1609.344),
    "g": ("mass", 1.0),
    "kg": ("mass", 1000.0),
    "oz": ("mass", 28.349523125),
    "lb": ("mass", 453.59237),
    "b": ("data", 1.0),
    "kb": ("data", 1000.0),
    "mb": ("data", 1_000_000.0),
    "gb": ("data", 1_000_000_000.0),
    "kib": ("data", 1024.0),
    "mib": ("data", 1024.0 ** 2),
    "gib": ("data", 1024.0 ** 3),
    "px": ("css", 1.0),
    "rem": ("css", 16.0),
    "ms": ("time", 0.001),
    "s": ("time", 1.0),
    "min": ("time", 60.0),
    "hr": ("time", 3600.0),
}

_SEARCH_ENGINES: dict[str, str] = {
    "duckduckgo": "https://duckduckgo.com/?q={q}",
    "brave": "https://search.brave.com/search?q={q}",
    "kagi": "https://kagi.com/search?q={q}",
    "google": "https://www.google.com/search?q={q}",
    "archwiki": "https://wiki.archlinux.org/index.php?search={q}",
}


class ScyProductivityEngine:
    """Section 9.8 Scy Productivity Layer: Calculator, Unit Converter, Notes, Focus Timer & Search."""

    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store
        self.data_dir = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "scy-shell"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.notes_file = self.data_dir / "notes.json"
        self.timer_file = self.store.state_dir / "focus-timer.json"

    def evaluate_query(self, query: str) -> dict[str, Any]:
        q = query.strip()
        # 1. `?` Web Search prefix (Serpantinum-inspired)
        if q.startswith("?"):
            term = q[1:].strip()
            engine = str(self.store.get_setting("scy.productivity.web_search_provider") or "duckduckgo")
            tpl = _SEARCH_ENGINES.get(engine, _SEARCH_ENGINES["duckduckgo"])
            return {
                "kind": "web_search",
                "engine": engine,
                "query": term,
                "url": tpl.format(q=urllib.parse.quote_plus(term)),
            }

        # 2. Unit conversion (`100 km to mi`, `72 f in c`, `32 px to rem`)
        m = re.match(r"^\s*([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(?:to|in|->)\s+([a-zA-Z]+)\s*$", q)
        if m:
            val = float(m.group(1))
            src_u = m.group(2).lower()
            dst_u = m.group(3).lower()
            conv = self._convert_units(val, src_u, dst_u)
            if conv is not None:
                return {
                    "kind": "unit_conversion",
                    "input": q,
                    "value": round(conv, 6),
                    "formatted": f"{conv:.4g} {dst_u}",
                }

        # 3. Safe AST Calculator (`= 2 + 2` or direct math expression)
        expr = q[1:].strip() if q.startswith("=") else q
        try:
            result = self._eval_ast(ast.parse(expr, mode="eval").body)
            return {
                "kind": "calculator",
                "expression": expr,
                "value": result,
                "formatted": str(round(result, 10) if isinstance(result, float) else result),
            }
        except Exception as exc:
            return {"kind": "unmatched", "query": q, "reason": str(exc)}

    @staticmethod
    def _convert_units(val: float, src: str, dst: str) -> float | None:
        if src in ("c", "f", "k") and dst in ("c", "f", "k"):
            c = val if src == "c" else ((val - 32.0) * 5.0 / 9.0 if src == "f" else val - 273.15)
            return c if dst == "c" else (c * 9.0 / 5.0 + 32.0 if dst == "f" else c + 273.15)
        if src in _UNIT_FACTORS_TO_BASE and dst in _UNIT_FACTORS_TO_BASE:
            cat_s, f_s = _UNIT_FACTORS_TO_BASE[src]
            cat_d, f_d = _UNIT_FACTORS_TO_BASE[dst]
            if cat_s == cat_d:
                return (val * f_s) / f_d
        return None

    def _eval_ast(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name) and node.id in _SAFE_FUNCS and isinstance(_SAFE_FUNCS[node.id], (int, float)):
            return _SAFE_FUNCS[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent out of safe range")
            return _SAFE_OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](self._eval_ast(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _SAFE_FUNCS:
            fn = _SAFE_FUNCS[node.func.id]
            if callable(fn) and len(node.args) == 1:
                return fn(self._eval_ast(node.args[0]))
        raise ValueError("Unsupported mathematical expression")

    # Quick Notes
    def list_notes(self) -> list[dict[str, Any]]:
        if not self.notes_file.exists():
            return []
        try:
            data = json.loads(self.notes_file.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def add_note(self, text: str, tag: str = "quick") -> dict[str, Any]:
        notes = self.list_notes()
        entry = {
            "id": f"note-{int(time.time() * 1000)}",
            "text": text.strip(),
            "tag": tag,
            "created_at": int(time.time()),
        }
        notes.insert(0, entry)
        atomic_write_text(self.notes_file, json.dumps(notes, indent=2, ensure_ascii=False) + "\n")
        return entry

    def delete_note(self, note_id: str) -> bool:
        notes = self.list_notes()
        filtered = [n for n in notes if n.get("id") != note_id]
        if len(filtered) != len(notes):
            atomic_write_text(self.notes_file, json.dumps(filtered, indent=2, ensure_ascii=False) + "\n")
            return True
        return False

    # Focus / Pomodoro Timer (syncs with Dynamic Island!)
    def timer_status(self) -> dict[str, Any]:
        if self.timer_file.exists():
            try:
                doc = json.loads(self.timer_file.read_text(encoding="utf-8"))
                if doc.get("running") and doc.get("ends_at"):
                    rem = max(0, int(doc["ends_at"] - time.time()))
                    doc["remaining_seconds"] = rem
                    if rem == 0:
                        doc["running"] = False
                        doc["completed"] = True
                return doc
            except Exception:
                pass
        mins = int(self.store.get_setting("scy.productivity.focus_minutes") or 25)
        return {"running": False, "phase": "focus", "remaining_seconds": mins * 60, "duration_seconds": mins * 60}

    def start_timer(self, minutes: int | None = None, phase: str = "focus") -> dict[str, Any]:
        dur_min = minutes if minutes is not None else int(
            self.store.get_setting("scy.productivity.focus_minutes") or (25 if phase == "focus" else 5)
        )
        now = time.time()
        doc = {
            "running": True,
            "completed": False,
            "phase": phase,
            "duration_seconds": int(dur_min * 60),
            "started_at": int(now),
            "ends_at": int(now + dur_min * 60),
            "remaining_seconds": int(dur_min * 60),
        }
        atomic_write_text(self.timer_file, json.dumps(doc, indent=2) + "\n")
        return doc

    def stop_timer(self) -> dict[str, Any]:
        doc = self.timer_status()
        doc["running"] = False
        atomic_write_text(self.timer_file, json.dumps(doc, indent=2) + "\n")
        return doc
