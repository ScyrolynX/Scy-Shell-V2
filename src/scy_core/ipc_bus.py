"""Scy-Shell v2.0 — Async Unix-Socket JSON-RPC 2.0 Server, Event Broker & Unified Action Router."""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

from .config_store import ScyConfigStore
from .layout_and_lab import ScyComponentLab, ScyLayoutComposer
from .native_services import (
    ScyControlCenterBackend,
    ScyDockController,
    ScyPerformanceAdvisor,
    ScyProductivityEngine,
)
from .profiles import ScyProfileManager
from .security_preauth import ScyPreAuthCoordinator


def default_socket_path() -> Path:
    override = os.environ.get("SCY_SHELL_SOCK")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        return Path(xdg) / "scy-shell.sock"
    return Path(f"/tmp/scy-shell-{os.getuid()}.sock")


class ScyIpcServer:
    def __init__(
        self,
        store: ScyConfigStore,
        sock_path: Path | None = None,
        dry_exec: bool = False,
    ) -> None:
        self.store = store
        self.sock_path = sock_path or default_socket_path()
        self.dry_exec = dry_exec
        self._server: asyncio.AbstractServer | None = None
        self.started_at = time.monotonic()
        self.dispatch_log: list[dict[str, Any]] = []
        self.toast_log: list[dict[str, Any]] = []
        self.osd_log: list[dict[str, Any]] = []
        self.extra_handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}

        self.profiles = ScyProfileManager(self.store)
        self.layouts = ScyLayoutComposer(self.store)
        self.components = ScyComponentLab(self.store)
        self.performance = ScyPerformanceAdvisor(self.store)
        self.dock = ScyDockController(self.store)
        self.control_center = ScyControlCenterBackend(self.store)
        self.productivity = ScyProductivityEngine(self.store)
        self.preauth = ScyPreAuthCoordinator(self.store)

    def register_handler(self, method: str, fn: Callable[[dict[str, Any]], Any]) -> None:
        self.extra_handlers[method] = fn

    async def start(self) -> None:
        self.sock_path.parent.mkdir(parents=True, exist_ok=True)
        if self.sock_path.exists():
            self.sock_path.unlink()
        self._server = await asyncio.start_unix_server(self._handle_client, path=str(self.sock_path))
        os.chmod(self.sock_path, 0o600)

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        if self.sock_path.exists():
            self.sock_path.unlink()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            raw = await reader.readline()
            if not raw:
                return
            req = json.loads(raw.decode("utf-8"))
            req_id = req.get("id", 1)
            method = req.get("method", "")
            params = req.get("params") or {}
            try:
                result = await self._dispatch_rpc(method, params)
                resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
            except Exception as exc:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(exc)}}
            writer.write((json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8"))
            await writer.drain()
        except Exception as exc:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
            writer.write((json.dumps(err) + "\n").encode("utf-8"))
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    def _notify_dock_reload(self) -> None:
        """Signals running Wayland shell runtimes to immediately reconcile single-owner dock surfaces."""
        if self.dry_exec or not os.environ.get("WAYLAND_DISPLAY"):
            return
        for cmd in (
            ["qs", "ipc", "call", "dock", "reload"],
            ["mandara", "msg", "config", "reload"],
        ):
            if shutil.which(cmd[0]):
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2, check=False)

    async def _dispatch_rpc(self, method: str, params: dict[str, Any]) -> Any:
        if method == "ping":
            return {
                "ok": True,
                "version": "2.0.0",
                "uptime_s": round(time.monotonic() - self.started_at, 3),
                "settings_count": self.store.schema.total_count,
                "engine_settings_count": self.store.schema.engine_total_count,
                "scy_native_settings_count": self.store.schema.scy_native_count,
                "studio_sections_count": len(self.store.schema.studio_sections),
                "active_providers": self.store.doc["active_providers"],
                "presentations": self.store.doc["presentations"],
            }
        if method == "studio.sections":
            return [
                {
                    **sec,
                    "count": len(self.store.schema.by_section(sec["id"])),
                }
                for sec in self.store.schema.studio_sections
            ]
        if method == "provider.get":
            domain = params.get("domain")
            return (
                self.store.get_provider(domain)
                if domain
                else dict(self.store.doc["active_providers"])
            )
        if method == "provider.set":
            ok, msg = self.store.set_provider(params["domain"], params["provider"])
            if not ok:
                raise ValueError(msg)
            if params["domain"] == "dock":
                self._notify_dock_reload()
            return {"ok": True, "message": msg, "active_providers": self.store.doc["active_providers"]}
        if method == "presentation.set":
            ok, msg = self.store.set_presentation(params["domain"], params["value"])
            if not ok:
                raise ValueError(msg)
            return {"ok": True, "message": msg}
        if method == "setting.get":
            sid = params["scy_id"]
            return {"scy_id": sid, "value": self.store.get_setting(sid)}
        if method == "setting.set":
            meta = self.store.set_setting(params["scy_id"], params["value"])
            if params["scy_id"] in ("scy.dock.engine", "scy.providers.lucid.prefs.dockEnabled"):
                self._notify_dock_reload()
            if params["scy_id"].startswith("scy.login."):
                self.preauth.stage_display_manager_configs()
            return {"scy_id": meta.scy_id, "value": self.store.get_setting(meta.scy_id), "project": meta.source_project}
        if method == "setting.reset":
            val = self.store.reset_setting(params["scy_id"])
            return {"ok": True, "scy_id": params["scy_id"], "value": val}
        if method == "section.reset":
            return self.store.reset_section(params["section_id"])
        if method == "setting.search":
            matches = self.store.schema.search(
                params.get("query", ""),
                project=params.get("project"),
                section=params.get("section"),
                limit=int(params.get("limit", 100)),
            )
            return [
                {
                    "scy_id": m.scy_id,
                    "original_key": m.original_key,
                    "project": m.source_project,
                    "studio_section": m.studio_section,
                    "category": m.category,
                    "type": m.value_type,
                    "ui_widget": m.ui_widget,
                    "value": self.store._read_meta_value(m),
                    "label": m.label,
                }
                for m in matches
            ]
        # Live Preview Engine RPCs
        if method == "preview.stage":
            return self.store.stage_preview(dict(params.get("changes") or {}))
        if method == "preview.diff":
            return self.store.get_preview_diff()
        if method == "preview.commit":
            return self.store.commit_preview()
        if method == "preview.revert":
            return self.store.revert_preview()

        # Dock Studio RPCs
        if method == "dock.status":
            return self.dock.status()
        if method == "dock.switch":
            res = self.dock.switch_engine(str(params["engine"]))
            self._notify_dock_reload()
            return res
        if method == "dock.pin":
            return self.dock.pin_app(params["id"], label=params.get("label"), group=params.get("group"))
        if method == "dock.unpin":
            return self.dock.unpin_item(params["id"])
        if method == "dock.separator":
            return self.dock.add_separator(params.get("id"))

        # Profile System RPCs
        if method == "profile.list":
            return self.profiles.list_profiles()
        if method == "profile.apply":
            res = self.profiles.apply_profile(params["id"])
            self._notify_dock_reload()
            return res
        if method == "profile.create":
            return self.profiles.create_profile_from_current(
                params["id"], params.get("name", params["id"]), params.get("description", "")
            )
        if method == "profile.duplicate":
            return self.profiles.duplicate_profile(params["source_id"], params["new_id"], params.get("new_name"))
        if method == "profile.export":
            out = self.profiles.export_profile(params["id"], Path(params["path"]))
            return {"ok": True, "path": str(out)}
        if method == "profile.import":
            return self.profiles.import_profile(Path(params["path"]), params.get("override_id"))
        if method == "profile.delete":
            return {"ok": self.profiles.delete_profile(params["id"])}

        # Layout Composer & Component Lab RPCs
        if method == "layout.list":
            return self.layouts.list_layouts()
        if method == "layout.get":
            return self.layouts.get_active_layout()
        if method == "layout.apply":
            return self.layouts.apply_layout(params["id"])
        if method == "layout.update_surface":
            return self.layouts.update_surface(params["surface_id"], dict(params.get("patch") or {}), params.get("save_as"))
        if method == "component.list":
            return self.components.list_components()
        if method == "component.update":
            return self.components.update_component(params["id"], dict(params.get("patch") or {}))
        if method == "component.reset":
            return self.components.reset_component(params["id"])

        # Intelligent Performance, Control Center & Productivity RPCs
        if method == "performance.probe":
            return self.performance.probe_hardware()
        if method == "performance.apply":
            return self.performance.apply_tier(params["tier"])
        if method == "control_center.snapshot":
            return self.control_center.snapshot()
        if method == "productivity.eval":
            return self.productivity.evaluate_query(str(params.get("query", "")))
        if method == "productivity.notes":
            act = params.get("action", "list")
            if act == "add":
                return self.productivity.add_note(params["text"], params.get("tag", "quick"))
            if act == "delete":
                return {"ok": self.productivity.delete_note(params["id"])}
            return self.productivity.list_notes()
        if method == "productivity.timer":
            act = params.get("action", "status")
            if act == "start":
                return self.productivity.start_timer(params.get("minutes"), params.get("phase", "focus"))
            if act == "stop":
                return self.productivity.stop_timer()
            return self.productivity.timer_status()

        if method == "toast.emit":
            renderer = self.store.doc["presentations"].get("toasts", "lucid")
            ev = {"renderer": renderer, **params, "ts": time.time()}
            self.toast_log.append(ev)
            return self._route_engine_cmd(
                renderer,
                lucid_cmd=["qs", "ipc", "call", "toast", "notify", params.get("title", ""), params.get("body", "")],
                mandara_cmd=["mandara", "msg", "notifications", "send", params.get("title", ""), params.get("body", "")],
            )
        if method == "osd.emit":
            osd_prov = self.store.doc["active_providers"].get("osd", "lucid")
            ev = {"provider": osd_prov, **params, "ts": time.time()}
            self.osd_log.append(ev)
            kind = params.get("kind", "volume")
            val = str(params.get("value", 50))
            return self._route_engine_cmd(
                osd_prov,
                lucid_cmd=["qs", "ipc", "call", "osd", "show", kind, val],
                mandara_cmd=["mandara", "msg", "osd", kind, val],
            )
        if method == "ipc.dispatch":
            return self._route_cli_args(list(params.get("args", [])))
        if method in self.extra_handlers:
            res = self.extra_handlers[method](params)
            if asyncio.iscoroutine(res):
                return await res
            return res
        raise ValueError(f"Unknown RPC method: {method}")

    def _route_cli_args(self, args: list[str]) -> dict[str, Any]:
        """Routes unified hotkey/CLI commands (`scy-shell-ipc <domain> [action...]`) to the single active owner!"""
        if not args:
            raise ValueError("Empty ipc.dispatch args")
        head = args[0]
        rest = args[1:]
        ap = self.store.doc["active_providers"]

        if head == "ping":
            return {"ok": True, "version": "2.0.0", "providers": ap}
        if head in ("studio", "settings", "prefs"):
            page = rest[0] if rest else ""
            return self._exec(["qs", "ipc", "call", "settings", "show" if page else "toggle", *([page] if page else [])], "studio")
        if head == "dock":
            if len(rest) >= 2 and rest[0] == "switch":
                res = self.dock.switch_engine(rest[1])
                self._notify_dock_reload()
                return {"ok": True, "dock": res}
            act = rest[0] if rest else "toggle"
            return self._route_engine_cmd(
                ap.get("dock", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "dock", act],
                mandara_cmd=["mandara", "msg", "dock", act],
            )
        if head == "launcher":
            act = rest[0] if rest else "toggle"
            return self._route_engine_cmd(
                ap.get("launcher", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "launcher", act, *rest[1:]],
                mandara_cmd=["mandara", "msg", "launcher", act, *rest[1:]],
            )
        if head == "lock":
            return self._route_engine_cmd(
                ap.get("lock_screen", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "lock", "lock"],
                mandara_cmd=["mandara", "lock"],
            )
        if head == "bar":
            act = rest[0] if rest else "toggle"
            prov = ap.get("bar", "lucid")
            target_prov = "lucid" if isinstance(prov, dict) else prov
            return self._route_engine_cmd(
                "lucid" if target_prov == "hybrid" else target_prov,
                lucid_cmd=["qs", "ipc", "call", "bar", act],
                mandara_cmd=["mandara", "msg", "bar", act],
            )
        if head in ("quick", "controlcentre", "control-center"):
            act = rest[0] if rest else "toggle"
            return self._route_engine_cmd(
                ap.get("quick_settings", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "controlcentre", act],
                mandara_cmd=["mandara", "msg", "panel", act, "control-center"],
            )
        if head in ("notifications", "notifs"):
            act = rest[0] if rest else "toggle"
            return self._route_engine_cmd(
                ap.get("notifications", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "notifs", act],
                mandara_cmd=["mandara", "msg", "notifications", act],
            )
        if head in ("shot", "screenshot", "capture"):
            mode = rest[0] if rest else "region"
            lucid_shot = (
                ["qs", "ipc", "call", "snap", "toggle"]
                if mode == "region"
                else (["qs", "ipc", "call", "screenshot", "full"] if mode == "screen" else ["qs", "ipc", "call", "snap", mode, *rest[1:]])
            )
            return self._route_engine_cmd(
                ap.get("capture", "lucid"),
                lucid_cmd=lucid_shot,
                mandara_cmd=["mandara", "msg", "screenshot", mode, *rest[1:]],
            )
        if head == "wallpaper":
            return self._route_engine_cmd(
                ap.get("wallpaper", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "launcher", "wallpaper"],
                mandara_cmd=["mandara", "msg", "wallpaper", "picker", "toggle"],
            )
        if head == "clipboard":
            return self._route_engine_cmd(
                ap.get("clipboard", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "launcher", "clipboard"],
                mandara_cmd=["mandara", "msg", "panel", "toggle", "clipboard"],
            )
        if head in ("emoji", "moji"):
            return self._exec(["qs", "ipc", "call", "moji", "toggle"], "lucid")
        if head == "switcher":
            direction = rest[0] if rest else "next"
            return self._route_engine_cmd(
                ap.get("switcher", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "switcher", direction],
                mandara_cmd=["mandara", "msg", "switcher", direction],
            )
        if head == "overview":
            return self._route_engine_cmd(
                ap.get("overview", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "workspaces", "toggle"],
                mandara_cmd=["mandara", "msg", "overview", "toggle"],
            )
        if head == "power":
            return self._exec(["qs", "ipc", "call", "session", "toggle"], "lucid")
        if head == "audio":
            sub = rest[0] if rest else "mute-toggle"
            return self._route_engine_cmd(
                ap.get("osd", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "audio", sub, *rest[1:]],
                mandara_cmd=["mandara", "msg", "audio", sub, *rest[1:]],
            )
        if head == "brightness":
            sub = rest[0] if rest else "up"
            return self._route_engine_cmd(
                ap.get("osd", "lucid"),
                lucid_cmd=["qs", "ipc", "call", "brightness", sub, *rest[1:]],
                mandara_cmd=["mandara", "msg", "brightness", sub, *rest[1:]],
            )
        if head == "agent":
            return self._exec(["mandara", "msg", "agent", *(rest or ["toggle"])], "mandara")
        if head == "sidebar":
            return self._exec(["mandara", "msg", "sidebar", *(rest or ["toggle"])], "mandara")
        if head == "plugins":
            return self._exec(["mandara", "studio", "plugins", *rest], "mandara")
        if head == "games":
            return self._exec(["mandara", "msg", "panel", "toggle", "games"], "mandara")
        if head == "wallgen":
            return self._exec(["mandara", "studio", "wallpaper", "--tab", "generator"], "mandara")
        if head == "look":
            if len(rest) >= 2 and rest[0] == "set":
                ok, msg = self.store.set_presentation("primary_identity", rest[1])
                if not ok:
                    raise ValueError(msg)
                return {"ok": True, "look": rest[1], "message": msg}
            return self._exec(["qs", "ipc", "call", "settings", "show", "01-personalization"], "studio")

        raise ValueError(f"Unknown IPC dispatch domain: {head}")

    def _route_engine_cmd(self, provider: str, lucid_cmd: list[str], mandara_cmd: list[str]) -> dict[str, Any]:
        if provider == "mandara":
            return self._exec(mandara_cmd, "mandara")
        return self._exec(lucid_cmd, "lucid")

    def _exec(self, cmd: list[str], target_engine: str) -> dict[str, Any]:
        entry = {"engine": target_engine, "cmd": cmd, "ts": time.time()}
        self.dispatch_log.append(entry)
        if self.dry_exec or shutil.which(cmd[0]) is None:
            return {"ok": True, "routed_to": target_engine, "cmd": cmd, "executed": False}
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return {
            "ok": proc.returncode == 0,
            "routed_to": target_engine,
            "cmd": cmd,
            "executed": True,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
