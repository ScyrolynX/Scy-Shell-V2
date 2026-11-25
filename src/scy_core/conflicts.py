"""Scy-Shell Pre-Activation Conflict Detector & User-Controlled Resolution Engine."""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config_store import ScyConfigStore


@dataclass
class ConflictItem:
    domain: str
    severity: str  # "critical" | "warning" | "info"
    resource: str
    owner: str
    kind: str      # "external_process" | "dbus_owner" | "display_manager" | "keybind" | "internal_gate"
    summary: str
    resolutions: list[dict[str, str]] = field(default_factory=list)


EXTERNAL_DAEMON_MAP: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "notifications": (
        "org.freedesktop.Notifications",
        "critical",
        ("mako", "dunst", "swaync", "fnott", "wired", "xfce4-notifyd"),
    ),
    "bar": (
        "wlr-layer-shell:LAYER_TOP",
        "warning",
        ("waybar", "ironbar", "polybar", "yambar", "ags"),
    ),
    "wallpaper": (
        "wlr-layer-shell:LAYER_BACKGROUND",
        "warning",
        ("hyprpaper", "mpvpaper", "swaybg", "wbg", "swww-daemon"),
    ),
    "polkit": (
        "org.freedesktop.PolicyKit1.AuthenticationAgent",
        "critical",
        (
            "hyprpolkitagent",
            "polkit-kde-authentication-agent-1",
            "lxqt-policykit-agent",
            "polkit-gnome-authentication-agent-1",
            "mate-polkit",
        ),
    ),
    "night_light": (
        "zwlr_gamma_control_manager_v1",
        "critical",
        ("wlsunset", "gammastep", "redshift"),
    ),
    "idle": (
        "ext_idle_notifier_v1",
        "warning",
        ("swayidle",),
    ),
    "clipboard": (
        "zwlr_data_control_manager_v1",
        "warning",
        ("copyq", "clipvault"),
    ),
}


def list_running_processes() -> list[tuple[int, str, str]]:
    """Returns [(pid, comm, cmdline)] from /proc without spawning `ps`."""
    out: list[tuple[int, str, str]] = []
    proc_root = Path("/proc")
    if not proc_root.exists():
        return out
    my_uid = os.getuid()
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            st = entry.stat()
            if st.st_uid != my_uid:
                continue
            comm = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
            raw_cmd = (entry / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", errors="replace").strip()
            out.append((int(entry.name), comm, raw_cmd))
        except Exception:
            continue
    return out


class ScyConflictScanner:
    def __init__(self, store: ScyConfigStore) -> None:
        self.store = store

    def scan_all(
        self,
        mock_processes: list[tuple[int, str, str]] | None = None,
        mock_dm_target: str | None = None,
        proposed_domain: str | None = None,
        proposed_provider: str | None = None,
    ) -> list[ConflictItem]:
        procs = mock_processes if mock_processes is not None else list_running_processes()
        ap = dict(self.store.doc["active_providers"])
        if proposed_domain and proposed_provider:
            ap[proposed_domain] = proposed_provider

        conflicts: list[ConflictItem] = []

        # 1. External process conflicts across exclusive Wayland/D-Bus domains
        for domain, (resource, severity, names) in EXTERNAL_DAEMON_MAP.items():
            if ap.get(domain) == "none":
                continue
            for pid, comm, cmdline in procs:
                exe = Path(cmdline.split()[0]).name if cmdline else comm
                if comm in names or exe in names:
                    conflicts.append(
                        ConflictItem(
                            domain=domain,
                            severity=severity,
                            resource=resource,
                            owner=f"{comm} (PID {pid})",
                            kind="external_process",
                            summary=(
                                f"External daemon '{comm}' (PID {pid}) is already claiming {resource}, "
                                f"which conflicts with Scy-Shell's '{ap.get(domain)}' {domain} provider."
                            ),
                            resolutions=[
                                {
                                    "action": "stop_external",
                                    "pid": str(pid),
                                    "label": f"Stop '{comm}' for this session (SIGTERM)",
                                },
                                {
                                    "action": "comment_autostart_backup",
                                    "daemon": comm,
                                    "label": f"Disable '{comm}' in Hyprland autostart (creates backup first)",
                                },
                                {
                                    "action": "keep_external",
                                    "domain": domain,
                                    "label": f"Keep '{comm}' and yield Scy-Shell {domain} control",
                                },
                            ],
                        )
                    )

        # Special cross-helper checks: hyprsunset & hypridle when Mandara owns night_light / idle
        for pid, comm, _ in procs:
            if comm == "hyprsunset" and ap.get("night_light") == "mandara":
                conflicts.append(
                    ConflictItem(
                        domain="night_light",
                        severity="critical",
                        resource="zwlr_gamma_control_manager_v1",
                        owner=f"hyprsunset (PID {pid})",
                        kind="external_process",
                        summary="hyprsunset holds Wayland gamma control while Mandara Night Light is selected.",
                        resolutions=[
                            {"action": "stop_external", "pid": str(pid), "label": "Stop hyprsunset before activating Mandara Night Light"},
                            {"action": "switch_provider", "domain": "night_light", "provider": "lucid", "label": "Keep Lucid (hyprsunset) as Night Light provider"},
                        ],
                    )
                )
            if comm == "hypridle" and ap.get("idle") == "mandara":
                conflicts.append(
                    ConflictItem(
                        domain="idle",
                        severity="warning",
                        resource="ext_idle_notifier_v1",
                        owner=f"hypridle (PID {pid})",
                        kind="external_process",
                        summary="hypridle is running alongside Mandara's native idle manager (`idle.rs`).",
                        resolutions=[
                            {"action": "stop_external", "pid": str(pid), "label": "Stop hypridle for this session"},
                            {"action": "switch_provider", "domain": "idle", "provider": "lucid", "label": "Use Lucid (hypridle) as Idle provider"},
                        ],
                    )
                )

        # 2. Internal Lucid <-> Mandara gate consistency verification
        gates = self.store.doc["providers"]["mandara"]["config"].get("scy_gates", {})
        gate_checks = [
            ("notifications", "owns_notifications", "org.freedesktop.Notifications"),
            ("polkit", "owns_polkit", "org.freedesktop.PolicyKit1.AuthenticationAgent"),
            ("lock_screen", "owns_lock", "ext_session_lock_manager_v1"),
            ("night_light", "owns_night_light", "zwlr_gamma_control_manager_v1"),
            ("bt_agent", "owns_bt_agent", "org.bluez.Agent1"),
            ("idle", "owns_idle", "ext_idle_notifier_v1"),
            ("clipboard", "owns_clipboard", "zwlr_data_control_manager_v1"),
            ("wallpaper", "owns_wallpaper", "wlr-layer-shell:LAYER_BACKGROUND"),
        ]
        for domain, gate_key, res_name in gate_checks:
            expected_mandara = ap.get(domain) == "mandara"
            if gates.get("managed_by_scy_shell") and gates.get(gate_key) != expected_mandara and proposed_domain != domain:
                conflicts.append(
                    ConflictItem(
                        domain=domain,
                        severity="critical",
                        resource=res_name,
                        owner="internal_gate_drift",
                        kind="internal_gate",
                        summary=f"Internal gate mismatch for {domain}: active={ap.get(domain)} vs gate={gates.get(gate_key)}.",
                        resolutions=[{"action": "resync_gates", "label": "Re-synchronize Scy-Shell engine gates immediately"}],
                    )
                )

        # 3. Display Manager mutual exclusion check (SDDM vs greetd)
        dm_choice = ap.get("display_manager", "preserve")
        dm_link = Path("/etc/systemd/system/display-manager.service")
        current_dm = mock_dm_target
        if current_dm is None and dm_link.is_symlink():
            try:
                current_dm = Path(os.readlink(dm_link)).name
            except Exception:
                current_dm = None
        if dm_choice == "lucid-sddm" and current_dm and current_dm != "sddm.service":
            conflicts.append(
                ConflictItem(
                    domain="display_manager",
                    severity="warning",
                    resource="display-manager.service",
                    owner=current_dm,
                    kind="display_manager",
                    summary=f"System currently uses {current_dm}, while 'lucid-sddm' is selected.",
                    resolutions=[
                        {"action": "keep_dm", "label": f"Keep {current_dm} active (preserve)"},
                        {"action": "stage_sddm", "label": "Generate Polkit-confirmed systemctl switch command for SDDM"},
                    ],
                )
            )
        elif dm_choice == "mandara-greetd" and current_dm and current_dm != "greetd.service":
            conflicts.append(
                ConflictItem(
                    domain="display_manager",
                    severity="warning",
                    resource="display-manager.service",
                    owner=current_dm,
                    kind="display_manager",
                    summary=f"System currently uses {current_dm}, while 'mandara-greetd' is selected.",
                    resolutions=[
                        {"action": "keep_dm", "label": f"Keep {current_dm} active (preserve)"},
                        {"action": "stage_greetd", "label": "Generate Polkit-confirmed systemctl switch command for greetd"},
                    ],
                )
            )

        return conflicts

    def resolve(self, action_spec: dict[str, str], dry_run: bool = False) -> dict[str, Any]:
        act = action_spec.get("action", "")
        if act == "resync_gates":
            self.store.flush_all()
            return {"ok": True, "action": act, "detail": "Engine gates synchronized"}
        if act == "switch_provider":
            ok, msg = self.store.set_provider(action_spec["domain"], action_spec["provider"])
            return {"ok": ok, "action": act, "detail": msg}
        if act == "keep_external":
            dom = action_spec["domain"]
            if dom in ("dock", "desktop_icons"):
                ok, msg = self.store.set_provider(dom, "none")
                return {"ok": ok, "action": act, "detail": msg}
            return {"ok": True, "action": act, "detail": f"External owner retained for {dom}"}
        if act == "stop_external":
            pid = int(action_spec["pid"])
            if not dry_run:
                os.kill(pid, 15)
            return {"ok": True, "action": act, "pid": pid, "dry_run": dry_run}
        if act == "keep_dm":
            ok, msg = self.store.set_provider("display_manager", "preserve")
            return {"ok": ok, "action": act, "detail": msg}
        return {"ok": False, "error": f"Unsupported resolution action: {act}"}

    def to_json_report(self, **kwargs: Any) -> dict[str, Any]:
        items = self.scan_all(**kwargs)
        return {
            "conflict_count": len(items),
            "critical_count": sum(1 for c in items if c.severity == "critical"),
            "items": [asdict(c) for c in items],
        }
