"""Tier 2 — Native Rust Toolchain, Fatal QML Lint, and Live CachyOS + Hyprland Compositor Tests.

Executes every native Rust, C11, and Qt6 QML verification step supported by the host's
installed toolchains and physical resources, while cleanly reporting SKIPPED (never
fabricated or disguised as passed) for:
  - linking `mandara-app` (`tract-core` ONNX + `wasmtime` + `gpui`) when host RAM < 4 GiB
  - live Wayland/Hyprland layer-surface & Quickshell session assertions when headless
"""
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANDARA_DIR = Path(os.environ.get("SCY_MANDARA_DIR") or str(ROOT / "engines" / "mandara"))
LUCID_DIR = Path(os.environ.get("SCY_LUCID_DIR") or str(ROOT / "engines" / "lucid"))

CARGO_BIN = shutil.which("cargo")
RUSTC_BIN = shutil.which("rustc")
HAS_CARGO = bool(CARGO_BIN and RUSTC_BIN and (MANDARA_DIR / "Cargo.toml").exists())
HAS_QMLLINT = bool(shutil.which("qmllint") or Path("/usr/lib/qt6/bin/qmllint").exists())
HAS_QUICKSHELL = bool(shutil.which("quickshell") or shutil.which("qs"))
HAS_LIVE_HYPRLAND = bool(
    os.environ.get("WAYLAND_DISPLAY")
    and os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    and shutil.which("hyprctl")
)


def _host_mem_kb() -> int:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    except Exception:
        pass
    return 8_000_000


HAS_4GB_RAM = _host_mem_kb() >= 4_000_000


def _cargo_env() -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("CARGO_TARGET_DIR", os.environ.get("CARGO_TARGET_DIR", str(MANDARA_DIR / "target")))
    env.setdefault("GIT_CEILING_DIRECTORIES", str(MANDARA_DIR.parent))
    if not HAS_4GB_RAM:
        env.setdefault("CARGO_BUILD_JOBS", "1")
        env.setdefault("RUSTFLAGS", "-C link-arg=-Wl,--no-keep-memory")
    return env


class TestCachyOsHostIntegration(unittest.TestCase):
    @unittest.skipUnless(HAS_CARGO, "Requires native Rust toolchain (cargo + rustc) on host")
    def test_host_01_native_rust_837_unit_tests_config_theme_i18n_version(self):
        cmd = [
            CARGO_BIN,
            "test",
            "--locked",
            "-p", "mandara-config",
            "-p", "mandara-theme",
            "-p", "mandara-i18n",
            "-p", "mandara-version",
            "--manifest-path",
            str(MANDARA_DIR / "Cargo.toml"),
        ]
        if not HAS_4GB_RAM:
            cmd[3:3] = [
                "-j", "1",
                "--config", "profile.test.codegen-units=32",
            ]
        proc = subprocess.run(cmd, env=_cargo_env(), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn("test result: ok.", proc.stdout)

    @unittest.skipUnless(HAS_CARGO, "Requires native Rust toolchain (cargo + rustc) on host")
    def test_host_02_native_rust_release_fat_lto_binary_mandara_delta(self):
        env = _cargo_env()
        cmd = [
            CARGO_BIN,
            "build",
            "--release",
            "--locked",
            "-p", "mandara-delta",
            "--manifest-path",
            str(MANDARA_DIR / "Cargo.toml"),
        ]
        if not HAS_4GB_RAM:
            cmd[3:3] = ["-j", "1"]
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        bin_path = Path(env["CARGO_TARGET_DIR"]) / "release" / "mandara-delta"
        self.assertTrue(bin_path.exists() and os.access(bin_path, os.X_OK))

    @unittest.skipUnless(HAS_QMLLINT, "Requires Qt6 qmllint on host")
    def test_host_03_fatal_qml_lint_zero_warnings(self):
        env = dict(os.environ, SCY_LUCID_DIR=str(LUCID_DIR))
        proc = subprocess.run(
            [str(ROOT / "scripts" / "lint-qml.sh")],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertEqual(proc.stderr.strip(), "")

    @unittest.skipUnless(
        HAS_CARGO and HAS_4GB_RAM,
        f"Requires >= 4.0 GiB host RAM to compile tract-core ONNX + wasmtime + gpui into mandara-app (current host MemTotal={_host_mem_kb() / 1048576:.2f} GiB, 0B swap)",
    )
    def test_host_04_mandara_app_full_release_binary(self):
        env = _cargo_env()
        proc = subprocess.run(
            [
                CARGO_BIN,
                "build",
                "--release",
                "--locked",
                "-p",
                "mandara-app",
                "--manifest-path",
                str(MANDARA_DIR / "Cargo.toml"),
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        ver = subprocess.run(
            [str(Path(env["CARGO_TARGET_DIR"]) / "release" / "mandara"), "--version"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(ver.returncode, 0, ver.stderr or ver.stdout)

    @unittest.skipUnless(
        HAS_LIVE_HYPRLAND and HAS_QUICKSHELL,
        "Requires active CachyOS Wayland + Hyprland + Quickshell session (WAYLAND_DISPLAY & HYPRLAND_INSTANCE_SIGNATURE)",
    )
    def test_host_05_live_layer_surfaces_ipc_arbitration_and_provider_switching(self):
        proc = subprocess.run(
            [str(ROOT / "scripts" / "verify-cachyos-live.sh")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn("All 7 Live CachyOS + Hyprland Verification Stages PASSED", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
