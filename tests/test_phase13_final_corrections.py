"""Targeted Regression Suite for Final V1.0.0 Corrections:
1. Safe, validated, atomic `scy-shell backup restore` CLI & midway-failure cleanup recovery.
2. Special `-1` ("Auto") default preservation, range validation, persistence & GUI representation
   for `surfaceDarkness` and `surfaceTint`.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scy_core.config_store import ScyConfigStore
from scy_core.schema import ScySchema

SCY_CLI = str(ROOT / "bin" / "scy-shell")
LUCID = Path(os.environ.get("SCY_LUCID_DIR") or str(ROOT / "engines" / "lucid"))


class TestPhase13FinalCorrections(unittest.TestCase):
    # ------------------------------------------------------------------
    # ISSUE 1: BACKUP RESTORE (CLI, path validation, rollback, live trap)
    # ------------------------------------------------------------------
    def test_01_cli_backup_restore_success_by_path_and_by_name_and_post_backup_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
            cli = [sys.executable, SCY_CLI, "--home", str(home)]

            # Establish known baseline configuration
            subprocess.check_call(cli + ["config", "set", "scy.providers.lucid.prefs.barSpacing", "14"], env=env, stdout=subprocess.DEVNULL)
            subprocess.check_call(cli + ["config", "set", "scy.providers.mandara.config.bar.height", "40"], env=env, stdout=subprocess.DEVNULL)
            subprocess.check_call(cli + ["provider", "bar", "lucid"], env=env, stdout=subprocess.DEVNULL)

            bpath_str = subprocess.check_output(cli + ["backup", "create", "golden"], env=env, text=True).strip()
            bpath = Path(bpath_str)
            self.assertTrue((bpath / "manifest.json").is_file())

            listed = json.loads(subprocess.check_output(cli + ["backup", "list"], env=env, text=True))
            self.assertIn(bpath.name, listed)

            # Mutate settings, switch providers, and create a new post-backup file (wallgen.toml)
            subprocess.check_call(cli + ["config", "set", "scy.providers.lucid.prefs.barSpacing", "22"], env=env, stdout=subprocess.DEVNULL)
            subprocess.check_call(cli + ["config", "set", "scy.providers.lucid.prefs.surfaceDarkness", "0.45"], env=env, stdout=subprocess.DEVNULL)
            subprocess.check_call(cli + ["provider", "bar", "mandara"], env=env, stdout=subprocess.DEVNULL)
            subprocess.check_call(cli + ["config", "set", "scy.providers.mandara.wallgen.schedule.enabled", "true"], env=env, stdout=subprocess.DEVNULL)
            wallgen_toml = home / ".config" / "mandara" / "wallgen.toml"
            self.assertTrue(wallgen_toml.exists())

            # 1A: Restore by full directory path via CLI
            res_out = subprocess.check_output(cli + ["backup", "restore", str(bpath)], env=env, text=True)
            res = json.loads(res_out)
            self.assertTrue(res["ok"])
            self.assertEqual(Path(res["backup_dir"]).resolve(), bpath.resolve())

            self.assertEqual(json.loads(subprocess.check_output(cli + ["config", "get", "scy.providers.lucid.prefs.barSpacing"], env=env, text=True)), 14)
            self.assertEqual(json.loads(subprocess.check_output(cli + ["config", "get", "scy.providers.lucid.prefs.surfaceDarkness"], env=env, text=True)), -1)
            self.assertEqual(subprocess.check_output(cli + ["provider", "bar"], env=env, text=True).strip(), "lucid")
            self.assertFalse(wallgen_toml.exists(), "Post-backup wallgen.toml should be removed on restore")

            # 1B: Corrupt live config.toml completely and restore by snapshot name alone
            (home / ".config" / "scy-shell" / "config.toml").write_text("[[[corrupt_toml\n", encoding="utf-8")
            res2 = json.loads(subprocess.check_output(cli + ["backup", "restore", bpath.name], env=env, text=True))
            self.assertTrue(res2["ok"])
            self.assertEqual(json.loads(subprocess.check_output(cli + ["config", "get", "scy.providers.lucid.prefs.barSpacing"], env=env, text=True)), 14)

    def test_02_backup_restore_rejects_invalid_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            home = Path(tmp)
            outside = Path(outside_tmp)
            env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
            cli = [sys.executable, SCY_CLI, "--home", str(home)]

            store = ScyConfigStore(home_dir=home)
            store.set_setting("scy.providers.lucid.prefs.barSpacing", 16)
            good_backup = store.create_backup("valid")

            # 1. Missing target argument on CLI
            p_missing = subprocess.run(cli + ["backup", "restore"], env=env, capture_output=True, text=True)
            self.assertNotEqual(p_missing.returncode, 0)
            self.assertIn("requires a backup directory", p_missing.stderr)

            # 2. Non-existent directory
            p_noexist = subprocess.run(cli + ["backup", "restore", str(home / "does-not-exist")], env=env, capture_output=True, text=True)
            self.assertNotEqual(p_noexist.returncode, 0)

            # 3. Regular file instead of directory
            regular_file = home / "not-a-dir.txt"
            regular_file.write_text("hello", encoding="utf-8")
            p_file = subprocess.run(cli + ["backup", "restore", str(regular_file)], env=env, capture_output=True, text=True)
            self.assertNotEqual(p_file.returncode, 0)

            # 4. Symlinked backup path
            sym_dir = home / "symlink-backup"
            sym_dir.symlink_to(good_backup)
            with self.assertRaises(ValueError):
                store.restore_backup(sym_dir)

            # 5. Directory without manifest.json
            empty_dir = outside / "empty-backup"
            empty_dir.mkdir()
            with self.assertRaises(FileNotFoundError):
                store.restore_backup(empty_dir)

            # 6. Malformed JSON in manifest.json
            bad_json_dir = outside / "bad-json"
            bad_json_dir.mkdir()
            (bad_json_dir / "manifest.json").write_text("{broken json", encoding="utf-8")
            with self.assertRaises(ValueError):
                store.restore_backup(bad_json_dir)

            # 7. Path traversal alias (`../evil`) in manifest
            trav_dir = outside / "traversal-alias"
            trav_dir.mkdir()
            (outside / "evil").write_text("pwned", encoding="utf-8")
            (trav_dir / "manifest.json").write_text(
                json.dumps({"files": {"../evil": str(store.config_path)}}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                store.restore_backup(trav_dir)

            # 8. Destination path outside user's managed directories
            escape_target = outside / "escaped-target.toml"
            escape_dir = outside / "escape-dest"
            escape_dir.mkdir()
            (escape_dir / "scy_config.toml").write_text("schema_version = 1\n", encoding="utf-8")
            (escape_dir / "manifest.json").write_text(
                json.dumps({"files": {"scy_config.toml": str(escape_target)}}),
                encoding="utf-8",
            )
            p_escape = subprocess.run(cli + ["backup", "restore", str(escape_dir)], env=env, capture_output=True, text=True)
            self.assertNotEqual(p_escape.returncode, 0)
            self.assertFalse(escape_target.exists())

            # 9. Missing payload file referenced in manifest (must fail before touching any file)
            missing_payload_dir = outside / "missing-payload"
            missing_payload_dir.mkdir()
            (missing_payload_dir / "manifest.json").write_text(
                json.dumps({"files": {"scy_config.toml": str(store.config_path)}}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                store.restore_backup(missing_payload_dir)
            self.assertEqual(store.get_setting("scy.providers.lucid.prefs.barSpacing"), 16)

    def test_03_backup_restore_failed_midway_rolls_back_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)
            store.set_setting("scy.providers.lucid.prefs.barSpacing", 10)
            store.set_setting("scy.providers.mandara.config.bar.height", 36)
            bdir = store.create_backup("before-edit")

            # Advance live state so both files differ from backup
            store.set_setting("scy.providers.lucid.prefs.barSpacing", 24)
            store.set_setting("scy.providers.mandara.config.bar.height", 52)
            pre_scy_bytes = store.config_path.read_bytes()
            pre_lucid_bytes = store.lucid_prefs_path.read_bytes()
            pre_mandara_bytes = store.mandara_config_path.read_bytes()

            real_copy = ScyConfigStore._atomic_copy_file
            call_count = {"n": 0}

            def fail_on_second_copy(src: Path, dst: Path) -> None:
                call_count["n"] += 1
                if call_count["n"] == 2:
                    raise OSError("Simulated mid-restore I/O failure after first file overwritten")
                real_copy(src, dst)

            with mock.patch.object(ScyConfigStore, "_atomic_copy_file", side_effect=fail_on_second_copy):
                with self.assertRaises(OSError):
                    store.restore_backup(bdir)

            # Verify first file (already overwritten before the failure) rolled back cleanly!
            self.assertEqual(store.config_path.read_bytes(), pre_scy_bytes)
            self.assertEqual(store.lucid_prefs_path.read_bytes(), pre_lucid_bytes)
            self.assertEqual(store.mandara_config_path.read_bytes(), pre_mandara_bytes)
            self.assertEqual(store.get_setting("scy.providers.lucid.prefs.barSpacing"), 24)
            self.assertEqual(store.get_setting("scy.providers.mandara.config.bar.height"), 52)

    def test_04_live_verification_cleanup_restores_config_on_midway_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            env = dict(os.environ, HOME=str(home), PYTHONPATH=str(ROOT / "src"))
            store = ScyConfigStore(home_dir=home)
            store.set_setting("scy.providers.lucid.prefs.barSpacing", 12)
            store.set_setting("scy.providers.lucid.prefs.surfaceDarkness", -1)
            store.set_provider("bar", "lucid")

            def digest_state() -> str:
                s = ScyConfigStore(home_dir=home)
                payload = {
                    "providers": s.doc["active_providers"],
                    "values": s.get_all_values(),
                }
                return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

            before_hash = digest_state()

            # Verify verify-cachyos-live.sh contains the hardened backup create + trap + backup restore pattern
            live_sh = (ROOT / "scripts" / "verify-cachyos-live.sh").read_text(encoding="utf-8")
            self.assertIn('backup create live-verify', live_sh)
            self.assertIn('backup restore "$BACKUP_PATH"', live_sh)
            self.assertIn('trap cleanup_live EXIT INT TERM', live_sh)

            # Execute the exact cleanup_live trap pattern from verify-cachyos-live.sh with a forced midway failure (exit 42)
            midway_script = f"""
set -euo pipefail
ROOT_DIR="{ROOT}"
EPHEMERAL_DAEMON_PID=""
QS_BIN=""
WAYLAND_DISPLAY=""
BACKUP_PATH="$(python3 "${{ROOT_DIR}}/bin/scy-shell" backup create live-verify)"

cleanup_live() {{
  local exit_rc=$?
  set +e
  if [[ -n "${{BACKUP_PATH:-}}" && -d "${{BACKUP_PATH}}" ]]; then
    if ! python3 "${{ROOT_DIR}}/bin/scy-shell" backup restore "$BACKUP_PATH" >/dev/null; then
      exit_rc=1
    fi
  fi
  exit "$exit_rc"
}}
trap cleanup_live EXIT INT TERM

# Mutate providers and settings midway through verification, then fail!
python3 "${{ROOT_DIR}}/bin/scy-shell" provider bar mandara >/dev/null
python3 "${{ROOT_DIR}}/bin/scy-shell" config set scy.providers.lucid.prefs.barSpacing 20 >/dev/null
python3 "${{ROOT_DIR}}/bin/scy-shell" config set scy.providers.lucid.prefs.surfaceDarkness 0.5 >/dev/null
exit 42
"""
            proc = subprocess.run(["bash", "-c", midway_script], env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 42, f"Expected midway failure exit code 42, got {proc.returncode}: {proc.stderr}")
            self.assertEqual(digest_state(), before_hash, "Midway failure cleanup failed to restore exact pre-test configuration!")

    # ------------------------------------------------------------------
    # ISSUE 2: SLIDER SPECIAL DEFAULTS (`surfaceDarkness` & `surfaceTint`)
    # ------------------------------------------------------------------
    def test_05_surface_darkness_and_surface_tint_preserve_minus_one_and_enforce_ranges(self):
        schema = ScySchema()
        dark_id = "scy.providers.lucid.prefs.surfaceDarkness"
        tint_id = "scy.providers.lucid.prefs.surfaceTint"

        dark_meta = schema.by_id[dark_id]
        tint_meta = schema.by_id[tint_id]

        # 1. Upstream -1 defaults preserved alongside normal bounded slider ranges
        self.assertEqual(dark_meta.default_value, -1)
        self.assertEqual(dark_meta.ui_widget, "slider")
        self.assertEqual(dark_meta.min_val, 0.0)
        self.assertEqual(dark_meta.max_val, 0.8)
        self.assertEqual(dark_meta.step, 0.05)
        self.assertIsNotNone(dark_meta.special_default)
        self.assertEqual(dark_meta.special_default["value"], -1)
        self.assertEqual(dark_meta.special_default["label"], "Auto")

        self.assertEqual(tint_meta.default_value, -1)
        self.assertEqual(tint_meta.ui_widget, "slider")
        self.assertEqual(tint_meta.min_val, 0.0)
        self.assertEqual(tint_meta.max_val, 1.0)
        self.assertEqual(tint_meta.step, 0.05)
        self.assertIsNotNone(tint_meta.special_default)
        self.assertEqual(tint_meta.special_default["value"], -1)
        self.assertEqual(tint_meta.special_default["label"], "Auto")

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
            cli = [sys.executable, SCY_CLI, "--home", str(home)]
            store = ScyConfigStore(home_dir=home)

            # 2. Fresh store returns -1 (never silently replaced with 0)
            self.assertEqual(store.get_setting(dark_id), -1)
            self.assertEqual(store.get_setting(tint_id), -1)
            live_initial = json.loads(store.live_values_path.read_text(encoding="utf-8"))["values"]
            self.assertNotIn(dark_id, live_initial)
            self.assertNotIn(tint_id, live_initial)

            # 3. Explicit 0.0 is valid, stored as 0.0, and treated as distinct from -1!
            store.set_setting(dark_id, 0.0)
            store.set_setting(tint_id, 0.0)
            self.assertEqual(store.get_setting(dark_id), 0.0)
            self.assertEqual(store.get_setting(tint_id), 0.0)
            prefs_zero = json.loads(store.lucid_prefs_path.read_text(encoding="utf-8"))
            self.assertEqual(prefs_zero["surfaceDarkness"], 0.0)
            self.assertEqual(prefs_zero["surfaceTint"], 0.0)
            live_zero = json.loads(store.live_values_path.read_text(encoding="utf-8"))["values"]
            self.assertEqual(live_zero[dark_id], 0.0)
            self.assertEqual(live_zero[tint_id], 0.0)

            # 4. Bounded manual slider values persist across provider switches
            subprocess.check_call(cli + ["config", "set-json", dark_id, "0.45"], env=env, stdout=subprocess.DEVNULL)
            subprocess.check_call(cli + ["config", "set-json", tint_id, "0.75"], env=env, stdout=subprocess.DEVNULL)
            for mode in ("mandara", "hybrid", "lucid"):
                subprocess.check_call(cli + ["provider", "bar", mode], env=env, stdout=subprocess.DEVNULL)

            reloaded = ScyConfigStore(home_dir=home)
            self.assertAlmostEqual(reloaded.get_setting(dark_id), 0.45)
            self.assertAlmostEqual(reloaded.get_setting(tint_id), 0.75)
            prefs_manual = json.loads(reloaded.lucid_prefs_path.read_text(encoding="utf-8"))
            self.assertAlmostEqual(prefs_manual["surfaceDarkness"], 0.45)
            self.assertAlmostEqual(prefs_manual["surfaceTint"], 0.75)

            # 5. Restoring -1 via set-json (GUI Auto button) AND via reset (GUI Reset button) stores exact -1
            subprocess.check_call(cli + ["config", "set-json", dark_id, "-1"], env=env, stdout=subprocess.DEVNULL)
            subprocess.check_call(cli + ["config", "reset", tint_id], env=env, stdout=subprocess.DEVNULL)

            restored = ScyConfigStore(home_dir=home)
            self.assertEqual(restored.get_setting(dark_id), -1)
            self.assertEqual(restored.get_setting(tint_id), -1)
            prefs_auto = json.loads(restored.lucid_prefs_path.read_text(encoding="utf-8"))
            self.assertEqual(prefs_auto["surfaceDarkness"], -1)
            self.assertEqual(prefs_auto["surfaceTint"], -1)
            live_after = json.loads(restored.live_values_path.read_text(encoding="utf-8"))["values"]
            self.assertNotIn(dark_id, live_after)
            self.assertNotIn(tint_id, live_after)

            # 6. Arbitrary out-of-range values other than sentinel -1 are strictly rejected
            for bad_dark in (-0.5, -2, 0.85, 2.0):
                with self.assertRaises(ValueError, msg=f"Expected {bad_dark} to be rejected for surfaceDarkness"):
                    restored.set_setting(dark_id, bad_dark)
            for bad_tint in (-0.25, -3, 1.05, 5.0):
                with self.assertRaises(ValueError, msg=f"Expected {bad_tint} to be rejected for surfaceTint"):
                    restored.set_setting(tint_id, bad_tint)

    def test_06_gui_special_slider_representation_and_qml_lint(self):
        studio_vault = (ROOT / "studio" / "ScyVaultPage.qml").read_text(encoding="utf-8")
        lucid_vault = (LUCID / "lucidprefs" / "ScyVaultPage.qml").read_text(encoding="utf-8")
        self.assertEqual(studio_vault, lucid_vault, "studio/ScyVaultPage.qml and lucidprefs/ScyVaultPage.qml drifted!")

        for token in (
            "hasSpecialDefault",
            "specialSentinel",
            "specialLabel",
            "specialManualInitial",
            "isSpecialActive",
            "enabled: !rowCard.isSpecialActive",
            "const nextVal = rowCard.isSpecialActive ? rowCard.specialManualInitial : rowCard.specialSentinel;",
        ):
            self.assertIn(token, studio_vault)

        cat_root = (ROOT / "schema" / "settings_catalogue.json").read_text(encoding="utf-8")
        cat_lucid = (LUCID / "scy-schema" / "settings_catalogue.json").read_text(encoding="utf-8")
        self.assertEqual(cat_root, cat_lucid, "Root and Lucid settings_catalogue.json drifted!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
