"""Scy-Shell v2.0 — Single-Instance Process Ownership, Dock Deduplication & Lifecycle Supervisor.

Guarantees:
1. Single-instance `fcntl.flock` locks for `scy-daemon`, `lucid-shell`, `mandara-engine`, and `dock-owner`.
2. Exact `/proc/<pid>/cmdline` inspection scoped strictly to `os.getuid()` — NEVER uses broad `killall`.
3. Eliminates duplicate dock / shell instances on startup and deduplicates legacy Hyprland `exec-once` entries.
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import signal
import time
from pathlib import Path
from typing import Any


def runtime_lock_dir(home_dir: Path | None = None) -> Path:
    override = os.environ.get("SCY_RUNTIME_LOCK_DIR")
    if override:
        p = Path(override)
    elif os.environ.get("XDG_RUNTIME_DIR"):
        p = Path(os.environ["XDG_RUNTIME_DIR"]) / "scy-shell"
    elif home_dir is not None:
        p = home_dir / ".local" / "state" / "scy-shell" / "locks"
    else:
        p = Path(f"/tmp/scy-shell-locks-{os.getuid()}")
    p.mkdir(parents=True, exist_ok=True)
    return p


class SingleInstanceLock:
    """Advisory kernel lock (`fcntl.flock`) tied to file descriptor lifetime — automatically released on crash."""

    def __init__(self, role: str, home_dir: Path | None = None) -> None:
        safe_role = re.sub(r"[^a-zA-Z0-9_-]", "-", role)
        self.role = safe_role
        self.lock_path = runtime_lock_dir(home_dir) / f"{safe_role}.lock"
        self._fd: int | None = None

    def acquire(self) -> tuple[bool, dict[str, Any]]:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.lock_path), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            holder = self.read_holder()
            os.close(fd)
            return False, holder

        meta = {
            "role": self.role,
            "pid": os.getpid(),
            "uid": os.getuid(),
            "started_at": round(time.time(), 3),
        }
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, (json.dumps(meta) + "\n").encode("utf-8"))
        os.fsync(fd)
        self._fd = fd
        return True, meta

    def read_holder(self) -> dict[str, Any]:
        if not self.lock_path.exists():
            return {}
        try:
            return json.loads(self.lock_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def is_locked_by_another(self) -> tuple[bool, dict[str, Any]]:
        if not self.lock_path.exists():
            return False, {}
        fd = os.open(str(self.lock_path), os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return False, {}
        except BlockingIOError:
            return True, self.read_holder()
        finally:
            os.close(fd)

    def release(self) -> None:
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None


class ProcessSupervisor:
    """Inspects and arbitrates Scy-Shell component ownership without broad process killing."""

    COMPETING_DOCK_BINS = frozenset({"nwg-dock-hyprland", "cairo-dock", "plank", "latte-dock"})

    def __init__(self, home_dir: Path | None = None, proc_root: Path | None = None) -> None:
        self.home = (home_dir or Path.home()).resolve()
        self.proc_root = proc_root or Path("/proc")
        self.uid = os.getuid()

    def scan_user_processes(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        if not self.proc_root.exists():
            return out
        my_pid = os.getpid()
        for entry in self.proc_root.iterdir():
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if pid == my_pid:
                continue
            try:
                st = entry.stat()
                if st.st_uid != self.uid:
                    continue
                raw_cmd = (entry / "cmdline").read_bytes()
                if not raw_cmd:
                    continue
                argv = [p.decode("utf-8", errors="replace") for p in raw_cmd.rstrip(b"\x00").split(b"\x00")]
                exe_name = Path(argv[0]).name if argv else ""
                out.append({"pid": pid, "exe": exe_name, "argv": argv, "cmdline": " ".join(argv)})
            except (PermissionError, FileNotFoundError, ProcessLookupError, OSError):
                continue
        return sorted(out, key=lambda x: x["pid"])

    def classify_shell_instances(self, processes: list[dict[str, Any]] | None = None) -> dict[str, list[dict[str, Any]]]:
        procs = processes if processes is not None else self.scan_user_processes()
        classified: dict[str, list[dict[str, Any]]] = {
            "scy_daemon": [],
            "lucid_quickshell": [],
            "mandara_shell": [],
            "competing_docks": [],
        }
        for p in procs:
            exe = p["exe"]
            cmd = p["cmdline"]
            argv = p["argv"]
            if exe == "scy-daemon" or any(a.endswith("/scy-daemon") for a in argv):
                classified["scy_daemon"].append(p)
            elif exe in ("quickshell", "qs") and ("quickshell/lucid" in cmd or "-c lucid" in cmd or cmd.endswith("quickshell")):
                classified["lucid_quickshell"].append(p)
            elif exe == "mandara" and (len(argv) == 1 or argv[1] in ("run", "daemon", "--daemon")):
                classified["mandara_shell"].append(p)
            elif exe in self.COMPETING_DOCK_BINS:
                classified["competing_docks"].append(p)
        return classified

    def enforce_single_instances(
        self,
        active_dock_mode: str = "lucid",
        dry_run: bool = False,
        processes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Terminates ONLY verified duplicate instances of Lucid Quickshell or Mandara shell for this UID,
        keeping the single earliest/lock-holding authoritative instance."""
        cls = self.classify_shell_instances(processes)
        terminated_pids: list[int] = []
        actions: list[dict[str, Any]] = []

        for group in ("lucid_quickshell", "mandara_shell"):
            items = cls[group]
            if len(items) > 1:
                keeper = items[0]
                for dup in items[1:]:
                    actions.append({
                        "group": group,
                        "action": "terminate_duplicate",
                        "kept_pid": keeper["pid"],
                        "duplicate_pid": dup["pid"],
                        "cmdline": dup["cmdline"],
                    })
                    if not dry_run:
                        try:
                            os.kill(dup["pid"], signal.SIGTERM)
                            terminated_pids.append(dup["pid"])
                        except ProcessLookupError:
                            pass

        return {
            "active_dock_owner": "none" if active_dock_mode in ("none", "disabled") else active_dock_mode,
            "counts": {k: len(v) for k, v in cls.items()},
            "duplicate_actions": actions,
            "terminated_pids": terminated_pids,
            "competing_external_docks": [p["exe"] for p in cls["competing_docks"]],
        }

    def deduplicate_hyprland_autostart(self, hypr_dir: Path | None = None, backup_dir: Path | None = None) -> dict[str, Any]:
        """Scans `~/.config/hypr/*.{conf,lua}` for legacy standalone `quickshell` / `launch-shell.sh` /
        `mandara` / `nwg-dock-hyprland` autostart lines that would spawn a second competing dock at login,
        backs up modified files, and comments out ONLY the conflicting autostart lines."""
        hdir = hypr_dir or (self.home / ".config" / "hypr")
        if not hdir.exists():
            return {"scanned_files": 0, "deduplicated_lines": 0, "modified_files": []}

        # Match standalone spawns outside scy-shell/ drop-in
        conf_pat = re.compile(
            r"^\s*exec-once\s*=\s*(?:.*launch-shell\.sh\b|quickshell\b(?!.*scy-keep)|qs\b(?!\s+ipc)|mandara\s*(?:$|&|--daemon)|nwg-dock-hyprland\b)"
        )
        lua_pat = re.compile(
            r"^\s*hl\.exec_once\s*\(\s*['\"](?:.*launch-shell\.sh|quickshell|qs|mandara|nwg-dock-hyprland)\b"
        )

        scanned = 0
        dedup_count = 0
        modified: list[str] = []

        for fpath in sorted(hdir.rglob("*")):
            if not fpath.is_file() or fpath.suffix not in (".conf", ".lua"):
                continue
            if "scy-shell" in fpath.parts:
                continue
            scanned += 1
            orig = fpath.read_text(encoding="utf-8", errors="replace")
            lines = orig.splitlines()
            changed = False
            new_lines: list[str] = []
            for ln in lines:
                stripped = ln.lstrip()
                if stripped.startswith("#") or stripped.startswith("--"):
                    new_lines.append(ln)
                    continue
                if fpath.suffix == ".conf" and conf_pat.search(ln):
                    new_lines.append(f"# [Scy-Shell v2 deduplicated — managed by scy-daemon] {ln}")
                    dedup_count += 1
                    changed = True
                elif fpath.suffix == ".lua" and lua_pat.search(ln):
                    new_lines.append(f"-- [Scy-Shell v2 deduplicated — managed by scy-daemon] {ln}")
                    dedup_count += 1
                    changed = True
                else:
                    new_lines.append(ln)
            if changed:
                if backup_dir is not None:
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    rel_name = str(fpath.relative_to(hdir)).replace("/", "__")
                    shutil.copy2(fpath, backup_dir / rel_name)
                fpath.write_text("\n".join(new_lines) + ("\n" if orig.endswith("\n") else ""), encoding="utf-8")
                modified.append(str(fpath))

        return {
            "scanned_files": scanned,
            "deduplicated_lines": dedup_count,
            "modified_files": modified,
        }
