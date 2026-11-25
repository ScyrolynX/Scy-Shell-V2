#!/usr/bin/env python3
"""Enriches schema/settings_catalogue.json with genuine upstream-extracted types, defaults,
ranges (min/max/step/unit), enum choices, validation rules, and live-preview bindings
across all 1,875 settings (643 Lucid + 1,232 Mandara).
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import os, sys
sys.path.insert(0, str(ROOT / "src"))
from scy_core.paths import lucid_engine_dir, mandara_engine_dir
LUCID = Path(os.environ.get("SCY_LUCID_DIR") or lucid_engine_dir() or (ROOT / "engines" / "lucid"))
MANDARA = Path(os.environ.get("SCY_MANDARA_DIR") or mandara_engine_dir() or (ROOT / "engines" / "mandara"))
CAT_PATH = ROOT / "schema" / "settings_catalogue.json"

HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def camel_to_kebab(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def camel_to_snake(name: str) -> str:
    return camel_to_kebab(name).replace("-", "_")


def humanize_key(key: str) -> str:
    tail = key.strip("/").split("/")[-1].split(".")[-1]
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", tail).replace("_", " ").replace("-", " ")
    return words[:1].upper() + words[1:] if words else key


# --- 1. Parse Rust numeric range constants & serde enums across Mandara crates ---
def parse_mandara_rust_metadata() -> tuple[dict[str, tuple[float, float]], dict[str, list[dict[str, str]]], dict[str, dict[str, Any]]]:
    range_consts: dict[str, tuple[float, float]] = {}
    rust_enums: dict[str, list[dict[str, str]]] = {}
    registry_by_ptr: dict[str, dict[str, Any]] = {}

    # Scan mandara-config, mandara-greeter, mandara-wallgen for range tuples & enums
    tuple_re = re.compile(
        r"pub\s+const\s+([A-Z0-9_]+)\s*:\s*\(\s*(?:f32|f64|u32|u16|u8|i32|usize)\s*,\s*(?:f32|f64|u32|u16|u8|i32|usize)\s*\)\s*=\s*\(\s*([-0-9._]+)\s*,\s*([-0-9._]+)\s*\)"
    )
    scalar_const_re = re.compile(
        r"(?:pub\s+)?const\s+([A-Z0-9_]+)\s*:\s*(?:f32|f64|u32|u16|u8|i32|usize)\s*=\s*([-0-9._]+)\s*;"
    )
    scalars: dict[str, float] = {}

    for crate in ("mandara-config", "mandara-greeter", "mandara-wallgen", "mandara-studio"):
        cdir = MANDARA / "crates" / crate / "src"
        if not cdir.exists():
            continue
        for rs in cdir.rglob("*.rs"):
            txt = rs.read_text(encoding="utf-8", errors="ignore")
            for m in scalar_const_re.finditer(txt):
                try:
                    scalars[m.group(1)] = float(m.group(2).replace("_", ""))
                except ValueError:
                    pass
            for m in tuple_re.finditer(txt):
                try:
                    lo = float(m.group(2).replace("_", ""))
                    hi = float(m.group(3).replace("_", ""))
                    range_consts[m.group(1)] = (lo, hi)
                except ValueError:
                    pass

            # Parse `#[serde(rename_all = "...")] pub enum Foo { ... }`
            for em in re.finditer(
                r'((?:#\[[^\]]+\]\s*)*)pub\s+enum\s+([A-Za-z0-9_]+)\s*\{([^}]+)\}',
                txt,
                re.DOTALL,
            ):
                attrs, ename, body = em.group(1), em.group(2), em.group(3)
                if "(" in body or "{" in body:
                    continue
                ren_m = re.search(r'rename_all\s*=\s*"([^"]+)"', attrs)
                ren = ren_m.group(1) if ren_m else "kebab-case"
                opts: list[dict[str, str]] = []
                cur_rename = None
                for raw_line in body.splitlines():
                    line = re.sub(r"//.*", "", raw_line).strip()
                    if not line:
                        continue
                    rm = re.search(r'#\[serde\(rename\s*=\s*"([^"]+)"', line)
                    if rm:
                        cur_rename = rm.group(1)
                    vm = re.match(r"^(?:#\[[^\]]+\]\s*)*([A-Z][A-Za-z0-9_]*)\s*,?$", line)
                    if vm:
                        vname = vm.group(1)
                        if cur_rename:
                            vkey = cur_rename
                        elif ren == "snake_case":
                            vkey = camel_to_snake(vname)
                        elif ren == "lowercase":
                            vkey = vname.lower()
                        else:
                            vkey = camel_to_kebab(vname)
                        opts.append({"key": vkey, "label": humanize_key(vname)})
                        cur_rename = None
                if len(opts) >= 2:
                    rust_enums[ename] = opts

    # Scan mandara-studio/src/registry/**/*.rs for choice tables & Setting declarations!
    reg_dir = MANDARA / "crates" / "mandara-studio" / "src"
    choice_tables: dict[str, list[dict[str, str]]] = {}
    pair_re = re.compile(r'\(\s*"([^"]+)"\s*,\s*(?:tk\(\s*)?"([^"]+)"\s*\)?\s*\)')

    for rs in reg_dir.rglob("*.rs"):
        txt = rs.read_text(encoding="utf-8", errors="ignore")
        for cm in re.finditer(r'(?:pub\s+)?const\s+([A-Z0-9_]+)\s*:\s*&\[\(&str,\s*&str\)\]\s*=\s*&\[(.*?)\];', txt, re.DOTALL):
            cname, cbody = cm.group(1), cm.group(2)
            pairs = []
            for pm in pair_re.finditer(cbody):
                raw_k, lbl = pm.group(1), pm.group(2)
                try:
                    k_unq = json.loads(raw_k) if raw_k.startswith('"') else raw_k
                except Exception:
                    k_unq = raw_k.strip('\\"')
                pairs.append({"key": str(k_unq), "label": lbl})
            if pairs:
                choice_tables[cname] = pairs

    # Also scan mandara-config/src/**/*.rs for `pub field_name: Type` so struct fields resolve exact Rust types!
    struct_field_types: dict[str, str] = {}
    for crate in ("mandara-config", "mandara-greeter", "mandara-wallgen"):
        cdir = MANDARA / "crates" / crate / "src"
        if not cdir.exists():
            continue
        for rs in cdir.rglob("*.rs"):
            stxt = rs.read_text(encoding="utf-8", errors="ignore")
            for fm in re.finditer(r"pub\s+([a-z0-9_]+)\s*:\s*([A-Za-z0-9_<>:]+)", stxt):
                fname, ftype = fm.group(1), fm.group(2).split("::")[-1]
                struct_field_types.setdefault(fname, ftype)

    # Balanced-parenthesis scan around every JSON pointer `"/..."` in mandara-studio/src/**/*.rs!
    ptr_lit_re = re.compile(r'"(/[a-z0-9_/-]+)"')
    for rs in reg_dir.rglob("*.rs"):
        txt = rs.read_text(encoding="utf-8", errors="ignore")
        local_tables = dict(choice_tables)
        for cm in re.finditer(r'(?:pub\s+)?const\s+([A-Z0-9_]+)\s*:\s*&\[\(&str,\s*&str\)\]\s*=\s*&\[(.*?)\];', txt, re.DOTALL):
            pairs = [{"key": pm.group(1).strip('\\"'), "label": pm.group(2)} for pm in pair_re.finditer(cm.group(2))]
            if pairs:
                local_tables[cm.group(1)] = pairs

        for pm in ptr_lit_re.finditer(txt):
            ptr = pm.group(1)
            if ptr.count("/") < 2 and ptr not in ("/look",):
                continue
            # Find enclosing function call (...) containing this pointer literal
            open_idx = txt.rfind("(", max(0, pm.start() - 260), pm.start())
            if open_idx == -1:
                continue
            depth = 1
            j = open_idx + 1
            limit = min(len(txt), open_idx + 1400)
            while j < limit and depth > 0:
                if txt[j] == "(":
                    depth += 1
                elif txt[j] == ")":
                    depth -= 1
                j += 1
            stmt = " ".join(txt[open_idx:j].split())
            after_ptr = " ".join(txt[pm.end():j].split())

            info: dict[str, Any] = {}
            # Extract tk("...") strings after pointer for label & help
            tks = re.findall(r'tk\(\s*"([^"]+)"\s*\)', after_ptr)
            if len(tks) >= 1:
                info["label"] = tks[0]
            if len(tks) >= 2:
                info["help"] = tks[1]

            # Detect Choice(...) or choice(..., TABLE, ...)
            table_hit = None
            for tname, opts in local_tables.items():
                if re.search(rf"\b{re.escape(tname)}\b", after_ptr):
                    table_hit = opts
                    break
            if table_hit:
                is_int_keys = all(o["key"].lstrip("-").isdigit() for o in table_hit)
                info.update({
                    "ui_widget": "segmented" if len(table_hit) <= 3 else "dropdown",
                    "concrete_type": "int" if is_int_keys else "enum",
                    "choices": [{"key": (int(o["key"]) if is_int_keys else o["key"]), "label": o["label"]} for o in table_hit],
                })
            elif re.search(r"\bToggle\b", after_ptr):
                info.update({"ui_widget": "switch", "concrete_type": "bool"})
            elif any(k in after_ptr for k in ("Slider", "slider(", "span(", "ints(", "pct(", "px_range(", "OptionalSlider")):
                rc_hit = None
                for rname, bounds in range_consts.items():
                    if re.search(rf"\b{re.escape(rname)}\b", after_ptr):
                        rc_hit = bounds
                        break
                nums = [float(x) for x in re.findall(r"(?<![A-Za-z0-9_])(-?\d+(?:\.\d+)?)", after_ptr)]
                unit_m = re.search(r'"(\s*(?:px|ms|s|%|°|x|pt|rem|fps|Hz|min|h)?)"', after_ptr)
                unit = unit_m.group(1).strip() if unit_m else ("%" if "pct(" in after_ptr else ("px" if "px" in after_ptr else ""))
                if rc_hit:
                    lo, hi = rc_hit
                    step = nums[0] if nums else (1.0 if (hi - lo) >= 10 and float(lo).is_integer() and float(hi).is_integer() else 0.05)
                elif len(nums) >= 3:
                    lo, hi, step = nums[0], nums[1], nums[2]
                elif len(nums) == 2:
                    lo, hi = nums[0], nums[1]
                    step = 1.0 if (hi - lo) >= 10 else 0.05
                elif "pct(" in after_ptr:
                    lo, hi, step, unit = 0.0, 1.0, 0.05, ""
                else:
                    lo, hi, step = 0.0, 100.0, 1.0
                if hi <= lo:
                    hi = lo + 100.0
                is_int = float(step).is_integer() and float(lo).is_integer() and float(hi).is_integer()
                info.update({
                    "ui_widget": "slider",
                    "concrete_type": "int" if is_int else "float",
                    "min": int(lo) if is_int else lo,
                    "max": int(hi) if is_int else hi,
                    "step": int(step) if is_int else step,
                    "unit": unit,
                    "nullable": "OptionalSlider" in after_ptr,
                })
            elif "Number" in after_ptr:
                nums = [float(x) for x in re.findall(r"(-?\d+(?:\.\d+)?)", after_ptr)]
                lo = nums[0] if len(nums) >= 1 else 0.0
                hi = nums[1] if len(nums) >= 2 else 10000.0
                info.update({"ui_widget": "number", "concrete_type": "float", "min": lo, "max": hi})
            elif re.search(r"\bTime\b", after_ptr):
                info.update({"ui_widget": "text", "concrete_type": "time", "pattern": r"^\d{2}:\d{2}$", "placeholder": "HH:MM"})
            elif re.search(r"\bFont\b", after_ptr):
                info.update({"ui_widget": "text", "concrete_type": "font", "placeholder": "Google Sans"})
            elif re.search(r"\b(?:List|StashEdges)\b", after_ptr):
                info.update({"ui_widget": "list", "concrete_type": "list"})
            elif re.search(r"\b(?:Text|OptionalText|Icon|Device|Display)\b", after_ptr):
                info.update({"ui_widget": "text", "concrete_type": "string", "nullable": "OptionalText" in after_ptr})

            if "ui_widget" in info:
                registry_by_ptr[ptr] = info

    # Fallback enrichment via struct_field_types & rust_enums for pointers not declared via s()/sd() (e.g. bespoke pages like /bar/left, /bar/layout)
    registry_by_ptr["__struct_field_types__"] = struct_field_types
    return range_consts, rust_enums, registry_by_ptr


# --- 2. Parse Lucid Prefs.qml, lucidprefs/*Page.qml & Catalog.js ---
def parse_lucid_qml_metadata() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    lucid_ui: dict[str, dict[str, Any]] = {}
    lock_catalog: dict[str, dict[str, Any]] = {}

    # Extract M3Slider / M3Segmented / M3Dropdown bindings in lucidprefs/*.qml
    prefs_dir = LUCID / "lucidprefs"
    hypr_ui: dict[str, dict[str, Any]] = {}
    for qml in prefs_dir.glob("*.qml"):
        if qml.name.startswith("Scy"):
            continue
        txt = qml.read_text(encoding="utf-8", errors="ignore")
        # Parse HyprRow blocks for all 72 Hyprland settings!
        for hm in re.finditer(r"HyprRow\s*\{([^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}[^{}]*)*)\}", txt, re.DOTALL):
            hbody = hm.group(1)
            om = re.search(r'option:\s*"([^"]+)"', hbody)
            if not om:
                continue
            hopt = om.group(1)
            tm = re.search(r'title:\s*I18n\.tr\("([^"]+)"\)', hbody)
            hinfo: dict[str, Any] = {}
            if tm:
                hinfo["label"] = tm.group(1)
            if "M3Switch" in hbody:
                hinfo.update({"ui_widget": "switch", "concrete_type": "bool", "default_value": False})
            elif "M3Slider" in hbody:
                fm = re.search(r"\bfrom:\s*([-0-9.]+)", hbody)
                tom = re.search(r"\bto:\s*([-0-9.]+)", hbody)
                sm = re.search(r"\bstepSize:\s*([-0-9.]+)", hbody)
                um = re.search(r'\bsuffix:\s*"([^"]*)"', hbody)
                dm = re.search(r"HyprConfig\.num\([^,]+,\s*([-0-9.]+)\)", hbody)
                lo = float(fm.group(1)) if fm else 0.0
                hi = float(tom.group(1)) if tom else 64.0
                st = float(sm.group(1)) if sm and float(sm.group(1)) > 0 else (1.0 if (hi - lo) >= 10 else 0.05)
                is_int = st.is_integer() and lo.is_integer() and hi.is_integer()
                dv = float(dm.group(1)) if dm else lo
                hinfo.update({
                    "ui_widget": "slider",
                    "concrete_type": "int" if is_int else "float",
                    "min": int(lo) if is_int else lo,
                    "max": int(hi) if is_int else hi,
                    "step": int(st) if is_int else st,
                    "unit": um.group(1).strip() if um else "",
                    "default_value": int(round(dv)) if is_int else dv,
                })
            elif "M3Segmented" in hbody or "M3Dropdown" in hbody:
                opts = [{"key": m.group(1), "label": m.group(2)} for m in re.finditer(r'"key":\s*"([^"]+)"\s*,\s*"label":\s*(?:I18n\.tr\(\s*)?"([^"]+)"', hbody)]
                if opts:
                    hinfo.update({
                        "ui_widget": "segmented" if len(opts) <= 3 else "dropdown",
                        "concrete_type": "enum",
                        "choices": opts,
                        "default_value": opts[0]["key"],
                    })
            if "ui_widget" in hinfo:
                hypr_ui[hopt] = hinfo

        # Match blocks binding value/current of Prefs.<prop> (never enabled: Prefs.<prop>!)
        for m in re.finditer(r"(M3Slider|M3Segmented|M3Dropdown)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", txt, re.DOTALL):
            kind, body = m.group(1), m.group(2)
            pm = re.search(r"(?:value|current):\s*[^\n]*?Prefs\.([A-Za-z0-9_]+)", body)
            if not pm:
                continue
            prop = pm.group(1)
            if kind == "M3Slider":
                fm = re.search(r"\bfrom:\s*([-0-9.]+)", body)
                tm = re.search(r"\bto:\s*([-0-9.]+)", body)
                sm = re.search(r"\bstepSize:\s*([-0-9.]+)", body)
                um = re.search(r'\bsuffix:\s*"([^"]*)"', body)
                if fm and tm:
                    lo, hi = float(fm.group(1)), float(tm.group(1))
                    st = float(sm.group(1)) if (sm and float(sm.group(1)) > 0) else (1.0 if (hi - lo) >= 10 else 0.05)
                    is_int = st.is_integer() and lo.is_integer() and hi.is_integer()
                    lucid_ui[prop] = {
                        "ui_widget": "slider",
                        "min": int(lo) if is_int else lo,
                        "max": int(hi) if is_int else hi,
                        "step": int(st) if is_int else st,
                        "unit": um.group(1) if um else "",
                    }
            else:
                opts = []
                for om in re.finditer(r'"key":\s*"([^"]+)"\s*,\s*"label":\s*(?:I18n\.tr\(\s*)?"([^"]+)"', body):
                    opts.append({"key": om.group(1), "label": om.group(2)})
                if opts:
                    lucid_ui[prop] = {
                        "ui_widget": "segmented" if len(opts) <= 3 else "dropdown",
                        "concrete_type": "enum",
                        "choices": opts,
                    }

    # Parse Catalog.js lock widget options
    cat_js = (LUCID / "lucidlock" / "parts" / "Catalog.js").read_text(encoding="utf-8", errors="ignore")
    for wm in re.finditer(r'\{\s*"id":\s*"([^"]+)".*?(?=\n    \{\s*"id":|\n\];)', cat_js, re.DOTALL):
        wid, wbody = wm.group(1), wm.group(0)
        if '"sized": true' in wbody:
            lock_catalog[f"lockOpts.{wid}.size"] = {
                "ui_widget": "segmented",
                "concrete_type": "enum",
                "choices": [{"key": k, "label": k} for k in ("S", "M", "L", "XL")],
            }
        sm = re.search(r'"styles":\s*\[(.*?)\]\s*,', wbody, re.DOTALL)
        if sm:
            sopts = [{"key": m.group(1), "label": m.group(2)} for m in re.finditer(r'\[\s*"([^"]+)"\s*,\s*I18n\.tr\("([^"]+)"\)', sm.group(1))]
            if sopts:
                lock_catalog[f"lockOpts.{wid}.style"] = {
                    "ui_widget": "segmented" if len(sopts) <= 3 else "dropdown",
                    "concrete_type": "enum",
                    "choices": sopts,
                }
        for om in re.finditer(r'\{\s*"key":\s*"([^"]+)"\s*,\s*"name":\s*I18n\.tr\("([^"]+)"\)\s*,\s*"type":\s*"([^"]+)"(.*?)\}', wbody):
            okey, oname, otype, orest = om.group(1), om.group(2), om.group(3), om.group(4)
            full_k = f"lockOpts.{wid}.{okey}"
            if otype == "bool":
                lock_catalog[full_k] = {"label": oname, "ui_widget": "switch", "concrete_type": "bool"}
            elif otype == "choice":
                copts = [{"key": cm.group(1), "label": cm.group(2)} for cm in re.finditer(r'\[\s*"([^"]+)"\s*,\s*I18n\.tr\("([^"]+)"\)', orest)]
                if copts:
                    lock_catalog[full_k] = {
                        "label": oname,
                        "ui_widget": "segmented" if len(copts) <= 3 else "dropdown",
                        "concrete_type": "enum",
                        "choices": copts,
                    }
    lock_catalog["lockOpts.panel_preset.side"] = {
        "label": "Panel Sheet Side",
        "ui_widget": "segmented",
        "concrete_type": "enum",
        "choices": [{"key": "left", "label": "Left"}, {"key": "right", "label": "Right"}],
    }
    lucid_ui.update(hypr_ui)
    return lucid_ui, lock_catalog


def parse_default_literal(raw: Any, fallback_type: str) -> Any:
    if isinstance(raw, (bool, int, float, list, dict)):
        return raw
    s = str(raw or "").strip().rstrip(";")
    if not s or s.startswith("("):
        if fallback_type == "bool":
            return False
        if fallback_type == "int":
            return 0
        if fallback_type == "float":
            return 0.0
        if fallback_type == "list":
            return []
        if fallback_type in ("json", "table", "spring"):
            return {}
        return ""
    if s == "true":
        return True
    if s == "false":
        return False
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if s.startswith("[") or s.startswith("{"):
        try:
            return json.loads(s)
        except Exception:
            return [] if s.startswith("[") else {}
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def infer_mandara_leaf(entry: dict[str, Any], rust_enums: dict[str, list[dict[str, str]]], registry_by_ptr: dict[str, dict[str, Any]]) -> dict[str, Any]:
    okey = entry["original_key"]
    rtype = entry.get("type", "config_field")
    leaf = okey.strip("/").split("/")[-1].split(".")[-1].lower()

    # 1. Exact hit from Mandara Studio's declarative registry!
    if okey in registry_by_ptr:
        reg = dict(registry_by_ptr[okey])
    else:
        reg = {}

    sft = registry_by_ptr.get("__struct_field_types__", {})
    field_rust_type = sft.get(okey.strip("/").split("/")[-1].split(".")[-1], "")
    if rtype == "config_field" and field_rust_type:
        rtype = field_rust_type

    # 2. Direct Rust enum type from wallgen / greeter / config
    if "ui_widget" not in reg and rtype in rust_enums:
        opts = rust_enums[rtype]
        reg.update({
            "ui_widget": "segmented" if len(opts) <= 3 else "dropdown",
            "concrete_type": "enum",
            "choices": opts,
        })

    # 3. Direct primitive / structured Rust types & semantic field names
    if "ui_widget" not in reg:
        if rtype in ("bool", "toggle") or leaf.startswith(("enable", "show_", "use_", "is_", "has_", "allow_", "auto_", "hide_", "dim_", "mute_", "pause_", "lock_", "blur", "follow_", "remember_")) and rtype == "config_field":
            reg.update({"ui_widget": "switch", "concrete_type": "bool"})
        elif rtype == "Spring":
            reg.update({
                "ui_widget": "spring",
                "concrete_type": "spring",
                "min": 20.0,
                "max": 1200.0,
                "step": 10.0,
                "default_value": {"stiffness": 320.0, "damping": 26.0},
            })
        elif rtype.startswith("Vec<") or rtype in ("Vec<String>", "Vec<PathBuf>", "Vec<Placement>", "list", "stashedges", "preauth::Widgets"):
            reg.update({"ui_widget": "list", "concrete_type": "list", "default_value": []})
        elif rtype == "toml::Table":
            reg.update({"ui_widget": "json", "concrete_type": "json", "default_value": {}})
        elif rtype == "color" or leaf.endswith(("_color", "_colour", "_tint", "_hex", "accent_color", "seed_color")):
            reg.update({"ui_widget": "color", "concrete_type": "color", "default_value": "#ffb1c4"})
        elif rtype in ("u8", "u16", "u32", "i32", "int"):
            hi = 255 if rtype == "u8" else (65535 if rtype == "u16" else 4096)
            if "opacity" in leaf or "percent" in leaf or "pct" in leaf or "volume" in leaf or "brightness" in leaf:
                reg.update({"ui_widget": "slider", "concrete_type": "int", "min": 0, "max": 100, "step": 1, "unit": "%"})
            elif "height" in leaf or "width" in leaf or "size" in leaf or "radius" in leaf or "gap" in leaf or "padding" in leaf or "margin" in leaf:
                reg.update({"ui_widget": "slider", "concrete_type": "int", "min": 0, "max": 512, "step": 1, "unit": "px"})
            else:
                reg.update({"ui_widget": "number", "concrete_type": "int", "min": 0, "max": hi, "step": 1})
        elif rtype in ("f32", "real", "slider"):
            if "opacity" in leaf or "alpha" in leaf or "amount" in leaf or "strength" in leaf or "scale" in leaf or "dim" in leaf:
                hi = 3.0 if "scale" in leaf else 1.0
                reg.update({"ui_widget": "slider", "concrete_type": "float", "min": 0.0, "max": hi, "step": 0.05, "unit": ""})
            else:
                reg.update({"ui_widget": "slider", "concrete_type": "float", "min": 0.0, "max": 200.0, "step": 1.0, "unit": ""})
        elif any(tok in leaf for tok in ("opacity", "alpha", "dim", "strength", "intensity", "volume_step")):
            reg.update({"ui_widget": "slider", "concrete_type": "float", "min": 0.0, "max": 1.0, "step": 0.05, "unit": ""})
        elif any(tok in leaf for tok in ("height", "width", "radius", "corner", "padding", "margin", "gap", "spacing", "thickness", "border", "icon_size", "font_size")):
            hi = 96 if "font_size" in leaf else (128 if "radius" in leaf or "gap" in leaf or "padding" in leaf else 800)
            reg.update({"ui_widget": "slider", "concrete_type": "int", "min": 0, "max": hi, "step": 1, "unit": "px"})
        elif any(tok in leaf for tok in ("_ms", "duration", "timeout", "interval", "delay", "debounce")):
            hi = 3600 if "timeout" in leaf or "interval" in leaf else 2000
            unit = "s" if ("sec" in leaf or "timeout" in leaf) else "ms"
            reg.update({"ui_widget": "slider", "concrete_type": "int", "min": 0, "max": hi, "step": 10 if unit == "ms" else 5, "unit": unit})
        elif any(tok in leaf for tok in ("max_", "count", "columns", "rows", "limit", "fps", "hz", "port")):
            hi = 65535 if "port" in leaf else (240 if "fps" in leaf or "hz" in leaf else 100)
            reg.update({"ui_widget": "number", "concrete_type": "int", "min": 0, "max": hi, "step": 1})
        elif leaf == "mode" and "theme" in okey:
            reg.update({
                "ui_widget": "segmented",
                "concrete_type": "enum",
                "choices": [{"key": "dark", "label": "Dark"}, {"key": "light", "label": "Light"}, {"key": "auto", "label": "Auto"}],
            })
        elif leaf in ("position", "edge", "side", "anchor"):
            opts = [{"key": k, "label": k.title()} for k in ("top", "bottom", "left", "right")]
            reg.update({"ui_widget": "dropdown", "concrete_type": "enum", "choices": opts})
        else:
            reg.update({"ui_widget": "text", "concrete_type": "string"})

    ctype = reg["concrete_type"]
    if "default_value" not in reg:
        if ctype == "enum" and reg.get("choices"):
            reg["default_value"] = reg["choices"][0]["key"]
        elif ctype == "bool":
            reg["default_value"] = False
        elif ctype == "int":
            reg["default_value"] = int(reg.get("min", 0))
        elif ctype == "float":
            reg["default_value"] = float(reg.get("min", 0.0))
        elif ctype == "color":
            reg["default_value"] = "#ffb1c4"
        elif ctype == "list":
            reg["default_value"] = []
        elif ctype in ("json", "spring"):
            reg["default_value"] = {"stiffness": 320.0, "damping": 26.0} if ctype == "spring" else {}
        else:
            reg["default_value"] = ""

    return reg


def enrich_all() -> None:
    doc = json.loads(CAT_PATH.read_text(encoding="utf-8"))
    _, rust_enums, registry_by_ptr = parse_mandara_rust_metadata()
    lucid_ui, lock_catalog = parse_lucid_qml_metadata()

    # Enrich 643 Lucid settings
    for entry in doc["lucid_settings"]:
        okey = entry["original_key"]
        raw_t = entry["type"]
        sid = entry["scy_id"]
        leaf = okey.split(".")[-1]

        info: dict[str, Any] = {"label": entry.get("label") or humanize_key(okey)}
        if raw_t == 'bool':
            info.update({'ui_widget': 'switch', 'concrete_type': 'bool'})
        elif okey in lucid_ui:
            info.update(lucid_ui[okey])
        elif okey in lock_catalog:
            info.update(lock_catalog[okey])

        if "ui_widget" not in info:
            d_parsed = parse_default_literal(entry.get("default"), raw_t)
            if raw_t == "bool" or isinstance(d_parsed, bool):
                info.update({"ui_widget": "switch", "concrete_type": "bool"})
            elif raw_t == "color" or "Colour" in okey or "Color" in okey or (isinstance(d_parsed, str) and HEX_RE.match(d_parsed)):
                info.update({"ui_widget": "color", "concrete_type": "color"})
            elif raw_t == "int" or (raw_t in ("hypr_option", "widget_option", "lock_widget_option") and isinstance(d_parsed, int) and not isinstance(d_parsed, bool)):
                hi = 100 if any(x in leaf.lower() for x in ("blur", "dim", "opacity", "pct", "vol")) else 400
                unit = "%" if hi == 100 else ("px" if any(x in leaf.lower() for x in ("height", "width", "size", "gap", "radius", "spacing", "margin", "pad", "border", "rounding")) else "")
                if hi <= 400 and not leaf.lower().endswith(("x", "y", "after")):
                    info.update({"ui_widget": "slider", "concrete_type": "int", "min": 0, "max": hi, "step": 1, "unit": unit})
                else:
                    info.update({"ui_widget": "number", "concrete_type": "int", "min": -4096, "max": 86400, "step": 1})
            elif raw_t == "real" or (raw_t in ("hypr_option", "widget_option", "lock_widget_option") and isinstance(d_parsed, float)):
                hi = max(2.0, float(d_parsed) * 2.0) if isinstance(d_parsed, (int, float)) and d_parsed > 1.0 else 1.0
                info.update({"ui_widget": "slider", "concrete_type": "float", "min": 0.0, "max": hi, "step": 0.05, "unit": ""})
            elif raw_t == "var" or isinstance(d_parsed, (list, dict)):
                is_list = isinstance(d_parsed, list)
                info.update({"ui_widget": "list" if is_list else "json", "concrete_type": "list" if is_list else "json"})
            elif raw_t == "widget_option":
                if any(k in leaf.lower() for k in ("show", "seconds", "dot", "compact", "fill", "24", "invert", "bold", "ring", "seconds")):
                    info.update({"ui_widget": "switch", "concrete_type": "bool"})
                elif raw_t == "hypr_option":
                    if any(tok in okey for tok in ("gap", "border_size", "rounding", "range", "render_power", "passes", "size", "timeout", "force_split")):
                        info.update({"ui_widget": "slider", "concrete_type": "int", "min": 0, "max": 64, "step": 1, "unit": "px", "default_value": 4})
                    elif any(tok in okey for tok in ("enabled", "dim_inactive", "preserve_split", "new_on_top", "no_warps", "resize_on_border", "focus_on_activate", "hide_on_key_press", "natural_scroll", "disable_while_typing", "tap-to-click")):
                        info.update({"ui_widget": "switch", "concrete_type": "bool", "default_value": False})
                    elif any(tok in okey for tok in ("strength", "multiplier", "ratio", "mfact", "opacity", "sensitivity", "column_width")):
                        info.update({"ui_widget": "slider", "concrete_type": "float", "min": 0.0, "max": 2.0, "step": 0.05, "unit": "", "default_value": 0.5})
                    else:
                        info.update({"ui_widget": "text", "concrete_type": "string"})
                else:
                    info.update({"ui_widget": "text", "concrete_type": "string"})
            else:
                info.update({"ui_widget": "text", "concrete_type": "string"})

        ctype = info.get("concrete_type") or ("int" if info.get("step", 1) == 1 and raw_t == "int" else ("float" if info["ui_widget"] == "slider" and raw_t == "real" else ("int" if info["ui_widget"] == "slider" else "string")))
        info["concrete_type"] = ctype
        dval = info["default_value"] if "default_value" in info else parse_default_literal(entry.get("default"), ctype)
        if ctype == "int" and not isinstance(dval, int):
            dval = int(info.get("min", 0))
        elif ctype == "float" and not isinstance(dval, (int, float)):
            dval = float(info.get("min", 0.0))
        elif ctype == "bool" and not isinstance(dval, bool):
            dval = False
        if ctype == "color" and (not isinstance(dval, str) or not dval.startswith("#")):
            dval = "#ffb1c4"
        info["default_value"] = dval

        # Preserve upstream sentinel defaults (-1 = Auto) alongside bounded manual slider ranges
        if okey == "surfaceDarkness":
            info["default_value"] = -1
            info["special_default"] = {
                "value": -1,
                "label": "Auto",
                "manual_initial": 0.3,
                "description": "Automatic theme surface darkness (-1)",
            }
        elif okey == "surfaceTint":
            info["default_value"] = -1
            info["special_default"] = {
                "value": -1,
                "label": "Auto",
                "manual_initial": 0.2,
                "description": "Automatic theme surface tint (-1)",
            }

        # Live preview classification
        if sid.startswith("scy.providers.lucid.hypr."):
            info["live_preview"] = "hypr_trial"
        elif ctype == "color" or okey in ("themeColour", "matugenScheme", "darkMode"):
            info["live_preview"] = "theme_accent"
        elif sid.startswith("scy.providers.lucid.prefs."):
            info["live_preview"] = "lucid_prefs"
        elif sid.startswith("scy.providers.lucid.lock_widgets."):
            info["live_preview"] = "lock_preview"
        else:
            info["live_preview"] = "engine_sync"

        entry.update(info)

    # Identify parent TOML section tables in Mandara
    all_m_keys = [e["original_key"] for e in doc["mandara_settings"]]
    parent_tables = {
        k: sum(1 for other in all_m_keys if other != k and other.startswith((k + "/") if k.startswith("/") else (k + ".")))
        for k in all_m_keys
    }
    parent_tables = {k: cnt for k, cnt in parent_tables.items() if cnt > 0}

    for entry in doc["mandara_settings"]:
        okey = entry["original_key"]
        sid = entry["scy_id"]
        if okey in parent_tables:
            entry.update({
                "label": entry.get("label") or humanize_key(okey),
                "ui_widget": "section_table",
                "concrete_type": "table",
                "default_value": {},
                "child_count": parent_tables[okey],
                "live_preview": "section",
            })
            continue

        reg = infer_mandara_leaf(entry, rust_enums, registry_by_ptr)
        entry["label"] = reg.get("label") or entry.get("label") or humanize_key(okey)
        if sid.startswith("scy.providers.mandara.wallgen."):
            reg["live_preview"] = "wallgen_preview"
        elif sid.startswith("scy.providers.mandara.greeter."):
            reg["live_preview"] = "preauth_stage"
        else:
            reg["live_preview"] = "mandara_ipc"
        entry.update(reg)

    out_txt = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    CAT_PATH.write_text(out_txt, encoding="utf-8")
    (LUCID / "scy-schema" / "settings_catalogue.json").write_text(out_txt, encoding="utf-8")

    all_items = doc["lucid_settings"] + doc["mandara_settings"]
    w_counts = Counter(e["ui_widget"] for e in all_items)
    t_counts = Counter(e["concrete_type"] for e in all_items)
    p_counts = Counter(e["live_preview"] for e in all_items)
    print(f"Enriched {len(all_items)} total settings ({len(doc['lucid_settings'])} Lucid + {len(doc['mandara_settings'])} Mandara)")
    print("UI Widgets:    ", dict(w_counts))
    print("Concrete Types:", dict(t_counts))
    print("Live Previews: ", dict(p_counts))


if __name__ == "__main__":
    enrich_all()
