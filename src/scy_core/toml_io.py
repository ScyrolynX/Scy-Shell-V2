"""Deterministic, dependency-free TOML serializer & atomic JSON-pointer reader/writer (Python 3.11+ tomllib)."""
from __future__ import annotations

import math
import os
import tempfile
import tomllib
from pathlib import Path
from typing import Any


def _escape_toml_str(s: str) -> str:
    out = ['"']
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _bare_key_ok(k: str) -> bool:
    return bool(k) and all(c.isalnum() or c in "-_" for c in k)


def _fmt_key(k: str) -> str:
    return k if _bare_key_ok(k) else _escape_toml_str(k)


def _fmt_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return "0.0"
        s = repr(v)
        if "." not in s and "e" not in s and "E" not in s:
            s += ".0"
        return s
    if isinstance(v, str):
        return _escape_toml_str(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_fmt_value(x) for x in v) + "]"
    if isinstance(v, dict):
        items = [f"{_fmt_key(str(k))} = {_fmt_value(val)}" for k, val in v.items() if val is not None]
        return "{ " + ", ".join(items) + " }"
    return _escape_toml_str(str(v))


def dumps_toml(data: dict[str, Any], header_comment: str = "") -> str:
    lines: list[str] = []
    if header_comment:
        for hl in header_comment.splitlines():
            lines.append(f"# {hl}" if hl else "#")
        lines.append("")

    def emit_table(prefix: list[str], tbl: dict[str, Any]) -> None:
        scalars: list[tuple[str, Any]] = []
        subtables: list[tuple[str, dict[str, Any]]] = []
        array_tables: list[tuple[str, list[dict[str, Any]]]] = []

        for k, v in tbl.items():
            if v is None:
                continue
            if isinstance(v, dict):
                subtables.append((k, v))
            elif isinstance(v, list) and v and all(isinstance(item, dict) for item in v):
                array_tables.append((k, v))
            else:
                scalars.append((k, v))

        if prefix and (scalars or not subtables and not array_tables):
            hdr = ".".join(_fmt_key(p) for p in prefix)
            lines.append(f"[{hdr}]")
        for k, v in scalars:
            lines.append(f"{_fmt_key(k)} = {_fmt_value(v)}")
        if prefix and (scalars or not subtables and not array_tables):
            lines.append("")
        elif not prefix and scalars:
            lines.append("")

        for k, sub in subtables:
            emit_table(prefix + [k], sub)

        for k, arr in array_tables:
            hdr = ".".join(_fmt_key(p) for p in (prefix + [k]))
            for item in arr:
                lines.append(f"[[{hdr}]]")
                for ik, iv in item.items():
                    if iv is not None:
                        lines.append(f"{_fmt_key(ik)} = {_fmt_value(iv)}")
                lines.append("")

    emit_table([], data)
    return "\n".join(lines).rstrip() + "\n"


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def atomic_write_text(path: Path, content: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_name, mode)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def get_pointer(doc: dict[str, Any], pointer: str, default: Any = None) -> Any:
    parts = [p for p in pointer.strip("/").split("/") if p]
    cur: Any = doc
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur


def set_pointer(doc: dict[str, Any], pointer: str, value: Any) -> None:
    parts = [p for p in pointer.strip("/").split("/") if p]
    if not parts:
        return
    cur = doc
    for p in parts[:-1]:
        nxt = cur.get(p)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[p] = nxt
        cur = nxt
    cur[parts[-1]] = value
