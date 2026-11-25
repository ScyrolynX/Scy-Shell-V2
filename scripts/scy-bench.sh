#!/usr/bin/env bash
# Scy-Shell Honest Resource & Latency Benchmark Harness
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_JSON="${1:-$ROOT_DIR/docs/stage1/benchmark-results.json}"
mkdir -p "$(dirname "$OUT_JSON")"

python3 - "$ROOT_DIR" "$OUT_JSON" <<'PY'
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
import sys

root = Path(sys.argv[1])
out_json = Path(sys.argv[2])
sys.path.insert(0, str(root / "src"))

from scy_core.config_store import ScyConfigStore

with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp)
    sock = home / "bench.sock"

    # 1. Measure cold 1,875-setting load + full sync time
    t0 = time.perf_counter()
    store = ScyConfigStore(home_dir=home)
    load_ms = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    store.flush_all()
    flush_ms = (time.perf_counter() - t1) * 1000.0

    # 2. Launch real scy-daemon process and measure startup + VmRSS + C11 IPC latency!
    t_start = time.perf_counter()
    proc = subprocess.Popen(
        [str(root / "bin" / "scy-daemon"), "--home", str(home), "--socket", str(sock)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        while not sock.exists():
            if time.perf_counter() - t_start > 10.0:
                raise RuntimeError("scy-daemon failed to bind socket within 10s")
            time.sleep(0.01)
        daemon_ready_ms = (time.perf_counter() - t_start) * 1000.0

        # Read real RSS from /proc/<pid>/status
        rss_kb = 0
        status_file = Path(f"/proc/{proc.pid}/status")
        if status_file.exists():
            for line in status_file.read_text().splitlines():
                if line.startswith("VmRSS:"):
                    rss_kb = int(line.split()[1])
                    break

        # 3. Measure 50 sequential C11 scy-shell-ipc round-trips over Unix socket
        ipc_bin = root / "bin" / "scy-shell-ipc"
        env = dict(os.environ, SCY_SHELL_SOCK=str(sock))
        latencies_ms = []
        for _ in range(50):
            ti = time.perf_counter()
            r = subprocess.run([str(ipc_bin), "--json", "ping"], env=env, capture_output=True, text=True, check=True)
            assert json.loads(r.stdout)["result"]["ok"] is True
            latencies_ms.append((time.perf_counter() - ti) * 1000.0)

        latencies_ms.sort()
        p50_ms = latencies_ms[len(latencies_ms) // 2]
        p95_ms = latencies_ms[int(len(latencies_ms) * 0.95)]
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    results = {
        "environment": {
            "measured_in_sandbox": not bool(os.environ.get("WAYLAND_DISPLAY")),
            "wayland_display_present": bool(os.environ.get("WAYLAND_DISPLAY")),
            "honesty_note": (
                "scy-daemon RSS, 1,875-setting sync latency, and C11 Unix-socket IPC round-trip times "
                "are real measurements executed in this Linux environment. Live Wayland GPU/VRAM/frame-time "
                "metrics require running this identical script inside an active CachyOS Hyprland session."
            ),
        },
        "measured_metrics": {
            "catalogue_load_1875_settings_ms": round(load_ms, 2),
            "full_dual_engine_sync_flush_ms": round(flush_ms, 2),
            "scy_daemon_cold_ready_ms": round(daemon_ready_ms, 2),
            "scy_daemon_vmrss_mb": round(rss_kb / 1024.0, 2),
            "c11_ipc_roundtrip_p50_ms": round(p50_ms, 3),
            "c11_ipc_roundtrip_p95_ms": round(p95_ms, 3),
        },
    }
    out_json.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
PY
