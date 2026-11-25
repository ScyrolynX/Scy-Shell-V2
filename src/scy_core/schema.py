"""Scy-Shell Unified Type-Aware Schema Registry — All 1,875 Settings, Validation, Ranges & Choices."""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .scy_native_settings import (
    SCY_NATIVE_SETTINGS,
    UNIFIED_STUDIO_15_SECTIONS,
    classify_studio_section,
)

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schema"

PROVIDER_DOMAINS: dict[str, tuple[str, ...]] = {
    "bar": ("lucid", "mandara", "hybrid"),
    "dock": ("lucid", "mandara", "none"),
    "launcher": ("lucid", "mandara"),
    "quick_settings": ("lucid", "mandara"),
    "notifications": ("lucid", "mandara"),
    "osd": ("lucid", "mandara"),
    "wallpaper": ("lucid", "mandara"),
    "desktop_widgets": ("lucid", "mandara", "hybrid"),
    "desktop_icons": ("lucid", "none"),
    "lock_screen": ("lucid", "mandara"),
    "polkit": ("lucid", "mandara"),
    "night_light": ("lucid", "mandara"),
    "bt_agent": ("lucid", "mandara"),
    "idle": ("lucid", "mandara"),
    "clipboard": ("lucid", "mandara"),
    "capture": ("lucid", "mandara"),
    "overview": ("lucid", "mandara"),
    "switcher": ("lucid", "mandara"),
    "display_manager": ("preserve", "lucid-sddm", "mandara-greetd"),
}

DEFAULT_ACTIVE_PROVIDERS: dict[str, str] = {
    domain: ("preserve" if domain == "display_manager" else "lucid")
    for domain in PROVIDER_DOMAINS
}

MANDARA_19_LOOKS: tuple[str, ...] = (
    "scy-m3-expressive",
    "corniche-dusk",
    "pharos-ink",
    "montaza-crimson",
    "qaitbay-forest",
    "anfushi-wave",
    "night-frame",
    "redmond",
    "cupertino",
    "corniche-frame",
    "raml-line",
    "lighthouse-rail",
    "phosphor",
    "pharos-lantern",
    "stanley-arches",
    "souk-tiles",
    "sea-glass",
    "library-desk",
    "ink-rush",
    "zen",
)

PRESENTATION_DOMAINS: dict[str, tuple[str, ...]] = {
    "primary_identity": MANDARA_19_LOOKS,
    "toasts": ("lucid", "mandara"),
    "osd_style": ("lucid-jelly", "mandara"),
    "mandara_surface_look": MANDARA_19_LOOKS,
    "launcher_federation": ("enabled", "disabled"),
    "lucid_bar_plugin_pill": ("enabled", "disabled"),
}

DEFAULT_PRESENTATIONS: dict[str, str] = {
    "primary_identity": "scy-m3-expressive",
    "toasts": "lucid",
    "osd_style": "lucid-jelly",
    "mandara_surface_look": "scy-m3-expressive",
    "launcher_federation": "enabled",
    "lucid_bar_plugin_pill": "enabled",
}

HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
TIME_HHMM_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def parse_qml_default(raw: Any, qml_type: str) -> Any:
    if isinstance(raw, (bool, int, float, list, dict)):
        return raw
    s = str(raw or "").strip().rstrip(";")
    if not s or s.startswith("("):
        if qml_type == "bool":
            return False
        if qml_type in ("int",):
            return 0
        if qml_type in ("real", "double", "float"):
            return 0.0
        if qml_type == "list":
            return []
        if qml_type in ("json", "table"):
            return {}
        return ""
    if s == "true":
        return True
    if s == "false":
        return False
    if qml_type == "int":
        try:
            return int(float(s))
        except ValueError:
            return 0
    if qml_type in ("real", "double", "float"):
        try:
            return float(s)
        except ValueError:
            return 0.0
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        try:
            return json.loads(s) if s.startswith('"') else s[1:-1]
        except Exception:
            return s[1:-1]
    if s.startswith("[") or s.startswith("{"):
        try:
            return json.loads(s)
        except Exception:
            return s
    return s


@dataclass(frozen=True)
class SettingMeta:
    scy_id: str
    original_key: str
    source_project: str
    source_file: str
    storage: str
    category: str
    value_type: str
    default_value: Any
    label: str = ""
    help_text: str = ""
    ui_widget: str = "text"
    concrete_type: str = "string"
    min_val: float | None = None
    max_val: float | None = None
    step: float | None = None
    unit: str = ""
    choices: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    nullable: bool = False
    live_preview: str = "engine_sync"
    special_default: dict[str, Any] | None = None
    studio_section: str = "15-advanced"


class ScySchema:
    def __init__(self, catalogue_path: Path | None = None) -> None:
        p = catalogue_path or (SCHEMA_DIR / "settings_catalogue.json")
        raw = json.loads(p.read_text(encoding="utf-8"))
        self.by_id: dict[str, SettingMeta] = {}
        self.by_orig: dict[tuple[str, str], SettingMeta] = {}
        self.lucid_count = len(raw["lucid_settings"])
        self.mandara_count = len(raw["mandara_settings"])
        self.engine_total_count = self.lucid_count + self.mandara_count
        raw_scy = raw.get("scy_settings") if "scy_settings" in raw else list(SCY_NATIVE_SETTINGS)
        self.scy_native_count = len(raw_scy)
        self.total_count = self.engine_total_count + self.scy_native_count
        self.studio_sections = tuple(raw.get("studio_sections") or UNIFIED_STUDIO_15_SECTIONS)

        all_m_keys = [e["original_key"] for e in raw["mandara_settings"]]
        parent_tables = {
            k for k in all_m_keys
            if any(other != k and other.startswith((k + "/") if k.startswith("/") else (k + ".")) for other in all_m_keys)
        }

        for entry in raw["lucid_settings"]:
            ctype = entry.get("concrete_type") or entry.get("type", "string")
            dval = entry.get("default_value") if "default_value" in entry else parse_qml_default(entry.get("default", ""), entry["type"])
            sec = entry.get("studio_section") or classify_studio_section(entry["scy_id"], entry["category"], entry["original_key"])
            meta = SettingMeta(
                scy_id=entry["scy_id"],
                original_key=entry["original_key"],
                source_project="lucid",
                source_file=entry["source_file"],
                storage=entry["storage"],
                category=entry["category"],
                value_type=entry["type"],
                default_value=dval,
                label=entry.get("label") or entry["original_key"],
                help_text=entry.get("help", ""),
                ui_widget=entry.get("ui_widget", "text"),
                concrete_type=ctype,
                min_val=entry.get("min"),
                max_val=entry.get("max"),
                step=entry.get("step"),
                unit=entry.get("unit", ""),
                choices=tuple(entry.get("choices", [])),
                nullable=bool(entry.get("nullable", False)),
                live_preview=entry.get("live_preview", "lucid_prefs"),
                special_default=entry.get("special_default"),
                studio_section=sec,
            )
            self.by_id[meta.scy_id] = meta
            self.by_orig[("lucid", meta.original_key)] = meta

        for entry in raw["mandara_settings"]:
            okey = entry["original_key"]
            is_tbl = okey in parent_tables or entry.get("concrete_type") == "table"
            vtype = "table" if is_tbl else entry.get("type", "config_field")
            ctype = "table" if is_tbl else entry.get("concrete_type", "string")
            dval = {} if is_tbl else entry.get("default_value", "")
            sec = entry.get("studio_section") or classify_studio_section(entry["scy_id"], entry["category"], okey)
            meta = SettingMeta(
                scy_id=entry["scy_id"],
                original_key=okey,
                source_project="mandara",
                source_file=entry["source_file"],
                storage=entry["storage"],
                category=entry["category"],
                value_type=vtype,
                default_value=dval,
                label=entry.get("label") or okey,
                help_text=entry.get("help", ""),
                ui_widget="section_table" if is_tbl else entry.get("ui_widget", "text"),
                concrete_type=ctype,
                min_val=entry.get("min"),
                max_val=entry.get("max"),
                step=entry.get("step"),
                unit=entry.get("unit", ""),
                choices=tuple(entry.get("choices", [])),
                nullable=bool(entry.get("nullable", False)),
                live_preview="section" if is_tbl else entry.get("live_preview", "mandara_ipc"),
                special_default=entry.get("special_default"),
                studio_section=sec,
            )
            self.by_id[meta.scy_id] = meta
            self.by_orig[("mandara", meta.original_key)] = meta

        for entry in raw_scy:
            sec = entry.get("studio_section") or classify_studio_section(entry["scy_id"], entry["category"], entry["original_key"])
            meta = SettingMeta(
                scy_id=entry["scy_id"],
                original_key=entry["original_key"],
                source_project="scy",
                source_file=entry.get("source_file", "config.toml"),
                storage=entry.get("storage", "scy_native"),
                category=entry.get("category", sec),
                value_type=entry.get("type", entry["concrete_type"]),
                default_value=entry["default_value"],
                label=entry.get("label") or entry["original_key"],
                help_text=entry.get("help", ""),
                ui_widget=entry.get("ui_widget", "text"),
                concrete_type=entry["concrete_type"],
                min_val=entry.get("min"),
                max_val=entry.get("max"),
                step=entry.get("step"),
                unit=entry.get("unit", ""),
                choices=tuple(entry.get("choices", [])),
                nullable=bool(entry.get("nullable", False)),
                live_preview=entry.get("live_preview", "scy_tokens"),
                special_default=entry.get("special_default"),
                studio_section=sec,
            )
            self.by_id[meta.scy_id] = meta
            self.by_orig[("scy", meta.original_key)] = meta

    def validate_and_coerce(self, scy_id: str, value: Any) -> Any:
        """Type-aware validation & coercion enforcing concrete types, min/max ranges, enums, colors, springs, and lists."""
        meta = self.by_id.get(scy_id)
        if meta is None:
            raise KeyError(f"Unknown setting ID: {scy_id}")

        if value is None and meta.nullable:
            return None

        ctype = meta.concrete_type

        if ctype == "table":
            if not isinstance(value, dict):
                raise ValueError(f"{scy_id} is a TOML section table; expected object/dict, got {type(value).__name__}")
            return value

        if ctype == "bool":
            if isinstance(value, bool):
                return value
            if isinstance(value, str) and value.strip().lower() in ("true", "false", "1", "0"):
                return value.strip().lower() in ("true", "1")
            raise ValueError(f"{scy_id} expects boolean (true/false), got {value!r}")

        if ctype == "enum" and meta.choices:
            allowed = [c["key"] for c in meta.choices]
            if value in allowed:
                return value
            s_val = str(value)
            for k in allowed:
                if str(k) == s_val:
                    return k
            raise ValueError(f"{scy_id} value {value!r} not in allowed choices {allowed}")

        if ctype in ("int", "float"):
            if isinstance(value, bool):
                raise ValueError(f"{scy_id} expects {ctype}, got bool")
            if meta.choices:
                allowed = [c["key"] for c in meta.choices]
                for k in allowed:
                    if k == value or str(k) == str(value):
                        return int(k) if ctype == "int" else float(k)
            try:
                num = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{scy_id} expects {ctype}, got {value!r}") from exc
            if not math.isfinite(num):
                raise ValueError(f"{scy_id} requires a finite number")
            if meta.special_default is not None and "value" in meta.special_default:
                sentinel = meta.special_default["value"]
                if abs(num - float(sentinel)) <= 1e-9:
                    return int(sentinel) if isinstance(sentinel, int) and not isinstance(sentinel, bool) else float(sentinel)
            if meta.min_val is not None and num < meta.min_val - 1e-9:
                raise ValueError(f"{scy_id}={num} below minimum {meta.min_val}")
            if meta.max_val is not None and num > meta.max_val + 1e-9:
                raise ValueError(f"{scy_id}={num} above maximum {meta.max_val}")
            return int(round(num)) if ctype == "int" else float(num)

        if ctype == "color":
            if not isinstance(value, str) or not HEX_COLOR_RE.match(value.strip()):
                raise ValueError(f"{scy_id} expects hex color (#RRGGBB or #AARRGGBB), got {value!r}")
            return value.strip()

        if ctype == "time":
            if not isinstance(value, str) or not TIME_HHMM_RE.match(value.strip()):
                raise ValueError(f"{scy_id} expects 24h time 'HH:MM', got {value!r}")
            return value.strip()

        if ctype == "spring":
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except Exception as exc:
                    raise ValueError(f"{scy_id} expects Spring JSON object {{stiffness, damping}}") from exc
            if not isinstance(value, dict) or "stiffness" not in value or "damping" not in value:
                raise ValueError(f"{scy_id} expects Spring dict with 'stiffness' and 'damping'")
            stiff = float(value["stiffness"])
            damp = float(value["damping"])
            if not (1.0 <= stiff <= 5000.0 and 0.1 <= damp <= 500.0):
                raise ValueError(f"{scy_id} spring out of bounds: stiffness={stiff}, damping={damp}")
            out = {"stiffness": stiff, "damping": damp}
            if "mass" in value:
                out["mass"] = float(value["mass"])
            return out

        if ctype == "list":
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                s = value.strip()
                if s.startswith("["):
                    parsed = json.loads(s)
                    if not isinstance(parsed, list):
                        raise ValueError(f"{scy_id} expected JSON array")
                    return parsed
                return [item.strip() for item in s.split(",") if item.strip()] if s else []
            raise ValueError(f"{scy_id} expects list/array, got {type(value).__name__}")

        if ctype == "json":
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                s = value.strip()
                if not s:
                    return {}
                parsed = json.loads(s)
                if not isinstance(parsed, dict):
                    raise ValueError(f"{scy_id} expects JSON object")
                return parsed
            raise ValueError(f"{scy_id} expects JSON object, got {type(value).__name__}")

        # string / font
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def by_section(self, section_id: str) -> list[SettingMeta]:
        return [m for m in self.by_id.values() if m.studio_section == section_id]

    def search(
        self,
        query: str,
        project: str | None = None,
        section: str | None = None,
        limit: int | None = None,
    ) -> list[SettingMeta]:
        q = query.strip().lower()
        out: list[SettingMeta] = []
        for m in self.by_id.values():
            if project and m.source_project != project:
                continue
            if section and m.studio_section != section:
                continue
            if (
                not q
                or q in m.scy_id.lower()
                or q in m.original_key.lower()
                or q in m.category.lower()
                or q in m.label.lower()
                or q in m.studio_section.lower()
            ):
                out.append(m)
                if limit is not None and len(out) >= limit:
                    break
        return out

    def validate_provider(self, domain: str, provider: str | dict[str, str]) -> tuple[bool, str]:
        if domain not in PROVIDER_DOMAINS:
            return False, f"Unknown provider domain: '{domain}'"
        allowed = PROVIDER_DOMAINS[domain]
        if isinstance(provider, dict):
            if "hybrid" not in allowed:
                return False, f"Domain '{domain}' does not support per-monitor hybrid maps"
            for mon, p in provider.items():
                if p not in ("lucid", "mandara", "none"):
                    return False, f"Invalid monitor provider '{p}' on '{mon}'"
            return True, "ok"
        if provider not in allowed:
            return False, f"Provider '{provider}' not allowed for '{domain}'; expected one of {allowed}"
        return True, "ok"

    def validate_presentation(self, slot: str, value: str) -> tuple[bool, str]:
        if slot not in PRESENTATION_DOMAINS:
            return False, f"Unknown presentation slot: '{slot}'"
        if value not in PRESENTATION_DOMAINS[slot]:
            return False, f"Invalid presentation '{value}' for '{slot}'"
        return True, "ok"
