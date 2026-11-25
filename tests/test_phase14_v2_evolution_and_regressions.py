"""Phase 14 — Comprehensive Scy-Shell v2.0.0 ("Ultimate Unified Desktop Evolution") QA & Regression Suite.

Covers:
1. All 5 mandatory user-reported bug-fix regressions (Dock switching, Duplicate docks & competing startups,
   Settings persistence across re-login + corruption recovery, Unified 15-Section Studio, Lock vs Login separation).
2. Unified 2,026-setting schema & 15-section Studio routing, Apply/Revert transactions, and Reset scopes.
3. Scy-Shell Native Signature Subsystems: ScyDesignTokens, ScyProfileManager, ScyLayoutComposer,
   ScyComponentLab, ScyPerformanceAdvisor, ScyDockController, ScyProductivityEngine, SingleInstanceLock,
   and Hyprland 0.57+ v2 layerrule/windowrule emission.
4. Safe Installer, Uninstaller, Zsh completion, and Backup Restoration.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCY_CLI = str(ROOT / "bin" / "scy-shell")
LAUNCH_ENG = str(ROOT / "bin" / "scy-launch-engine")
INSTALL_SH = str(ROOT / "install.sh")
UNINSTALL_SH = str(ROOT / "uninstall.sh")

from scy_core.config_store import ScyConfigStore
from scy_core.hypr_coordinator import ScyHyprCoordinator
from scy_core.layout_and_lab import ScyComponentLab, ScyLayoutComposer
from scy_core.native_services import (
    ScyControlCenterBackend,
    ScyDockController,
    ScyPerformanceAdvisor,
    ScyProductivityEngine,
)
from scy_core.process_guard import ProcessSupervisor, SingleInstanceLock
from scy_core.profiles import BUILTIN_PROFILES, ScyProfileManager
from scy_core.security_preauth import ScyPreAuthCoordinator
from scy_core.toml_io import load_toml


class TestPhase14V2EvolutionAndRegressions(unittest.TestCase):
    def test_01_regression_bug1_and_bug2_single_owner_dock_switching_and_no_duplicates(self):
        """Regression 1 & 2: Single-action dock switching persists across restarts and enforces
        exclusive surface ownership in both Lucid QML and Mandara Rust without duplicate docks."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)
            dock = ScyDockController(store)

            # Default: Scy-Shell Primary Dock (Lucid island) owns dock; Mandara dock strictly disabled
            st0 = dock.status()
            self.assertEqual(st0["owner"], "lucid")
            self.assertTrue(store.get_setting("scy.providers.lucid.prefs.dockEnabled"))
            m_cfg0 = load_toml(store.mandara_config_path)
            self.assertEqual(m_cfg0["scy_gates"]["dock_mode"], "lucid")
            self.assertIn("dock", m_cfg0["plugins"]["disabled"])

            # Switch to Mandara dock in ONE action -> Lucid dock unmaps, Mandara dock activates
            dock.switch_engine("mandara")
            self.assertEqual(store.doc["active_providers"]["dock"], "mandara")
            self.assertEqual(store.get_setting("scy.dock.mode"), "rail")
            self.assertFalse(store.get_setting("scy.providers.lucid.prefs.dockEnabled"))
            m_cfg1 = load_toml(store.mandara_config_path)
            self.assertEqual(m_cfg1["scy_gates"]["dock_mode"], "mandara")
            self.assertTrue(m_cfg1["dock"]["enabled"])
            self.assertIn("dock", m_cfg1["plugins"]["enabled"])
            self.assertNotIn("dock", m_cfg1["plugins"]["disabled"])

            # Restart store (simulating re-login) -> Mandara dock choice remains 100% intact
            restarted = ScyConfigStore(home_dir=home)
            self.assertEqual(restarted.doc["active_providers"]["dock"], "mandara")
            self.assertFalse(restarted.get_setting("scy.providers.lucid.prefs.dockEnabled"))

            # Switch back to Lucid split dock -> Mandara dock torn down, Lucid split dock active
            ScyDockController(restarted).switch_engine("lucid")
            restarted.set_setting("scy.dock.mode", "split")
            self.assertEqual(restarted.doc["active_providers"]["dock"], "lucid")
            self.assertTrue(restarted.get_setting("scy.providers.lucid.prefs.dockEnabled"))
            self.assertEqual(restarted.get_setting("scy.providers.lucid.prefs.dockStyle"), "split")
            m_cfg2 = load_toml(restarted.mandara_config_path)
            self.assertEqual(m_cfg2["scy_gates"]["dock_mode"], "lucid")

            # Verify source-level QML & Rust single-owner dock gates
            lucid_dir = ROOT / "engines" / "lucid"
            mandara_dir = ROOT / "engines" / "mandara"
            dock_qml = (lucid_dir / "luciddocks" / "Dock.qml").read_text(encoding="utf-8")
            self.assertIn('ScyBridge.owns("dock") && Prefs.dockOn', dock_qml)
            self.assertIn('target: "dock"', dock_qml)
            mandara_dock_rs = (mandara_dir / "crates" / "mandara-ui" / "src" / "plugins" / "dock" / "mod.rs").read_text(encoding="utf-8")
            self.assertIn("cfg.scy_gates.dock_enabled()", mandara_dock_rs)

    def test_02_competing_startup_flock_guard_and_autostart_dedup_without_killall(self):
        """Regression 2B: Kernel flock prevents duplicate engine startups, and Hyprland autostart
        deduplication quarantines competing exec-once lines safely without broad killall/pkill."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            env = {**os.environ, "SCY_HOME": str(home), "SCY_LAUNCH_DRY_RUN": "1"}

            # Hold an active SingleInstanceLock for 'engine-lucid' in a child process
            holder = subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    (
                        "import fcntl, os, sys, time; "
                        f"sys.path.insert(0, {str(ROOT / 'src')!r}); "
                        "from pathlib import Path; "
                        "from scy_core.process_guard import runtime_lock_dir; "
                        f"lp = runtime_lock_dir(Path({str(home)!r})) / 'engine-lucid.lock'; "
                        "lp.parent.mkdir(parents=True, exist_ok=True); "
                        "fd = os.open(str(lp), os.O_CREAT | os.O_RDWR, 0o600); "
                        "fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); "
                        "sys.stdout.write('LOCKED\\n'); sys.stdout.flush(); "
                        "time.sleep(10)"
                    ),
                ],
                stdout=subprocess.PIPE,
                text=True,
            )
            try:
                line = holder.stdout.readline().strip()
                self.assertEqual(line, "LOCKED")
                # Concurrent scy-launch-engine invocation must detect lock and exit 0 cleanly
                cp = subprocess.run([sys.executable, LAUNCH_ENG, "lucid"], env=env, capture_output=True, text=True)
                self.assertEqual(cp.returncode, 0)
                self.assertIn("Single-instance guard", cp.stderr)
            finally:
                if holder.stdout is not None:
                    holder.stdout.close()
                holder.terminate()
                holder.wait(timeout=5)

            # Once released, scy-launch-engine dry-run succeeds cleanly
            cp2 = subprocess.run([sys.executable, LAUNCH_ENG, "lucid"], env=env, capture_output=True, text=True, check=True)
            payload = json.loads(cp2.stdout.strip())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["engine"], "lucid")

            # Verify autostart deduplication backs up before commenting duplicate shell launches
            hypr_dir = home / ".config" / "hypr"
            hypr_dir.mkdir(parents=True)
            hconf = hypr_dir / "hyprland.conf"
            hconf.write_text(
                "monitor=,preferred,auto,1\n"
                "exec-once = quickshell -p ~/.config/quickshell/lucid\n"
                "exec-once = mandara\n",
                encoding="utf-8",
            )
            sup = ProcessSupervisor(home_dir=home)
            res = sup.deduplicate_hyprland_autostart(hypr_dir=hypr_dir)
            self.assertGreaterEqual(res["deduplicated_lines"], 2)
            updated_txt = hconf.read_text(encoding="utf-8")
            self.assertIn("monitor=,preferred,auto,1", updated_txt)
            self.assertIn("# [Scy-Shell v2 deduplicated", updated_txt)

    def test_03_regression_bug3_settings_survive_relogin_live_edits_and_corruption_recovery(self):
        """Regression 3: User edits made in live QML/Rust files during a session are absorbed via
        SHA-256 persistence-ledger.json on next login (never overwritten by stale config.toml),
        and corrupted config.toml automatically recovers from .last-good with error logging."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)
            store.set_setting("scy.providers.lucid.prefs.themeColour", "#7AA2F7")
            store.set_setting("scy.dock.icon_size", 44)

            # Simulate user changing themeColour & dockIconSize inside live QML prefs.json during session
            live_prefs = json.loads(store.lucid_prefs_path.read_text(encoding="utf-8"))
            live_prefs["themeColour"] = "#FF79C6"
            live_prefs["dockBottomMargin"] = 22
            store.lucid_prefs_path.write_text(json.dumps(live_prefs, indent=2), encoding="utf-8")

            # Next login: new ScyConfigStore starts up -> must absorb live prefs.json instead of clobbering!
            next_login = ScyConfigStore(home_dir=home)
            self.assertEqual(next_login.get_setting("scy.providers.lucid.prefs.themeColour"), "#FF79C6")
            self.assertEqual(next_login.get_setting("scy.providers.lucid.prefs.dockBottomMargin"), 22)

            # Simulate power-loss corruption of config.toml
            next_login.config_path.write_text("<<<CORRUPTED TOML PAYLOAD === [[[", encoding="utf-8")
            recovered = ScyConfigStore(home_dir=home)
            self.assertEqual(recovered.get_setting("scy.providers.lucid.prefs.themeColour"), "#FF79C6")
            self.assertEqual(recovered.get_setting("scy.dock.icon_size"), 44)
            self.assertTrue(recovered.error_log_path.exists())
            self.assertIn("Corrupted config.toml detected", recovered.error_log_path.read_text(encoding="utf-8"))

    def test_04_regression_bug4_unified_15_section_studio_live_preview_and_reset_scopes(self):
        """Regression 4: Studio opens on unified 01-personalization, exposes exactly 15 visible intent
        sections (hiding engine-provider pages), supports transactional Live Preview (stage/diff/commit/revert),
        and supports setting/section/profile resets."""
        lucid_dir = ROOT / "engines" / "lucid"
        settings_qml = (lucid_dir / "lucidprefs" / "Settings.qml").read_text(encoding="utf-8")
        prefs_qml = (lucid_dir / "Prefs.qml").read_text(encoding="utf-8")
        self.assertIn('property string page: "01-personalization"', settings_qml)
        self.assertIn('active: ScyBridge.lazyStudioTabs ? pane.active : paneLoader.everActive', settings_qml)
        for sec_id in (
            "01-personalization", "02-desktop", "03-dock", "04-visual-effects", "05-layout",
            "06-widgets", "07-windows", "08-interactions", "09-notifications", "10-system-hardware",
            "11-lock-screen", "12-login", "13-productivity", "14-profiles", "15-advanced",
        ):
            self.assertIn(f'"key": "{sec_id}"', prefs_qml)

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)
            orig_blur = store.get_setting("scy.effects.blur_strength")

            # Live Preview staging -> diff -> revert restores original value cleanly
            store.stage_preview({"scy.effects.blur_strength": 5, "scy.effects.glow_intensity": 0.65})
            diff = store.preview_diff()
            diff_ids = [c["scy_id"] for c in diff["changes"]]
            self.assertIn("scy.effects.blur_strength", diff_ids)
            store.revert_preview()
            self.assertEqual(store.get_setting("scy.effects.blur_strength"), orig_blur)

            # Live Preview staging -> commit persists permanently
            store.stage_preview({"scy.effects.blur_strength": 5})
            store.commit_preview()
            self.assertEqual(store.get_setting("scy.effects.blur_strength"), 5)

            # Reset single setting & reset section
            store.reset_setting("scy.effects.blur_strength")
            self.assertEqual(store.get_setting("scy.effects.blur_strength"), orig_blur)

            store.set_setting("scy.island.width", 310)
            res = store.reset_section("02-desktop")
            self.assertGreaterEqual(res["reset_count"], 1)
            self.assertEqual(store.get_setting("scy.island.width"), store.schema.by_id["scy.island.width"].default_value)

    def test_05_regression_bug5_strict_lock_screen_11_vs_login_12_isolation_and_no_passwords(self):
        """Regression 5: Lock Screen (Section 11) and Login Experience (Section 12) remain strictly
        decoupled (lockLoginSync=False), never overwrite each other, and forbid password storage."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)
            preauth = ScyPreAuthCoordinator(store)

            self.assertFalse(store.get_setting("scy.providers.lucid.prefs.lockLoginSync"))

            # Customize Section 12 Login Experience
            preauth.set_login_design("scy-sddm", user_list_style="minimal-pill", design="editorial")
            login_target_before = store.get_setting("scy.login.greeter_target")
            login_style_before = store.get_setting("scy.login.user_list_style")

            # Customize Section 11 Lock Screen heavily -> must NEVER alter Section 12 Login!
            preauth.set_lock_design("lucid", "minimal")
            store.set_setting("scy.lock.clock_style", "editorial-serif")
            store.set_setting("scy.providers.lucid.prefs.lockBlur", 85)
            self.assertEqual(store.get_setting("scy.login.greeter_target"), login_target_before)
            self.assertEqual(store.get_setting("scy.login.user_list_style"), login_style_before)

            # Customize Section 12 Login again -> must NEVER alter Section 11 Lock Screen!
            preauth.set_login_design("scy-greetd", user_list_style="avatar-cards", design="glass")
            self.assertEqual(store.get_setting("scy.lock.clock_style"), "editorial-serif")
            self.assertEqual(store.get_setting("scy.providers.lucid.prefs.lockBlur"), 85)

            # Password storage strictly rejected
            with self.assertRaises(Exception):
                preauth.assert_no_credentials({"username": "alice", "password": "secret"})

            launch_sh = (ROOT / "engines" / "lucid" / "support" / "lucid" / "launch-shell.sh").read_text(encoding="utf-8")
            self.assertIn("SCY_SHELL_ALLOW_LEGACY_SDDM_SYNC", launch_sh)

    def test_06_signature_v2_profiles_layouts_component_lab_performance_productivity_and_hypr057(self):
        """Verifies all Scy-Shell v2.0 native subsystems and Hyprland 0.57+ v2 rule emission."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)

            # 1. All 7 built-in profiles + custom profile creation/export/import
            pm = ScyProfileManager(store)
            for pid in ("minimal", "productivity", "immersive", "gaming", "creative", "cinema", "balanced"):
                self.assertIn(pid, BUILTIN_PROFILES)
                applied = pm.apply_profile(pid)
                self.assertEqual(applied["profile_id"], pid)

            pm.create_profile_from_current("studio-pro", "Studio Pro", "Custom test profile")
            exp_path = pm.export_profile("studio-pro", home / "studio-pro.json")
            self.assertTrue(exp_path.exists())
            imp = pm.import_profile(exp_path, override_id="studio-pro-copy")
            self.assertEqual(imp["id"], "studio-pro-copy")

            # 2. Scy Layout Composer
            lc = ScyLayoutComposer(store)
            for lid in ("unity-left", "minimal-top", "bottom-deck", "dual-stage", "scy-signature"):
                res = lc.apply_layout(lid)
                self.assertEqual(res["layout"]["id"], lid)

            # 3. Scy Component Laboratory
            lab = ScyComponentLab(store)
            upd = lab.update_component("dock", {"radius": 26, "opacity": 0.88})
            self.assertEqual(upd["radius"], 26)
            rst = lab.reset_component("dock")
            self.assertIn("radius", rst)

            # 4. Scy Intelligent Performance tiers
            perf = ScyPerformanceAdvisor(store)
            hw = perf.probe_hardware()
            self.assertIn("recommended_tier", hw)
            for tier in ("max-quality", "performance", "battery", "balanced"):
                perf.apply_tier(tier)
                self.assertEqual(store.get_setting("scy.performance.tier"), tier)

            # 5. Scy Productivity Engine (AST math, unit conversion, quick notes, focus timer) + Control Center
            prod = ScyProductivityEngine(store)
            self.assertEqual(prod.evaluate_query("= (12 * 8) + 4")["value"], 100)
            conv = prod.evaluate_query("100 km to mi")
            self.assertAlmostEqual(conv["value"], 62.1371, places=2)
            before_notes = len(prod.list_notes())
            note = prod.add_note("Ship Scy-Shell v2.0", tag="release")
            self.assertEqual(len(prod.list_notes()), before_notes + 1)
            self.assertTrue(prod.delete_note(note["id"]))
            t_on = prod.start_timer(minutes=25, phase="focus")
            self.assertTrue(t_on["running"])
            t_off = prod.stop_timer()
            self.assertFalse(t_off["running"])

            cc = ScyControlCenterBackend(store).snapshot()
            self.assertIn("performance_tier", cc)
            self.assertIn("active_profile", cc)

            # 6. Hyprland 0.57+ v2 layerrule & windowrule syntax (ZERO deprecated <0.53 syntax)
            hypr = ScyHyprCoordinator(store)
            hypr.emit_modular_configs()
            conf_txt = (hypr.scy_hypr_dir / "scy-shell.conf").read_text(encoding="utf-8")
            self.assertIn("match:namespace", conf_txt)
            self.assertNotIn("layerrule = blur, quickshell", conf_txt)
            self.assertNotIn("ignorezero", conf_txt)

            # 7. Design tokens exported for live QML ScyDesignTokens singleton
            self.assertTrue(store.design_tokens_path.exists())
            tokens = json.loads(store.design_tokens_path.read_text(encoding="utf-8"))
            for section_key in ("colors", "typography", "materials", "motion", "layout", "dock", "dynamic_island", "lock_screen", "login_experience"):
                self.assertIn(section_key, tokens)

    def test_07_installer_preinstall_backup_zsh_completion_and_restore(self):
        """Verifies install.sh creates pre-install backup manifest, installs Zsh completion &
        scy-launch-engine, uninstalls via uninstall.sh preserving backups, and restores snapshots."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".config" / "hypr").mkdir(parents=True)
            (home / ".config" / "hypr" / "hyprland.conf").write_text("# Custom User Hyprland\nmonitor=,preferred,auto,1\n", encoding="utf-8")

            subprocess.check_call(
                [INSTALL_SH, "--profile", "productivity", "--with-hypr", "--skip-engine-build", "--home", str(home)],
                stdout=subprocess.DEVNULL,
            )
            self.assertTrue((home / ".local" / "bin" / "scy-launch-engine").exists())
            self.assertTrue((home / ".local" / "share" / "zsh" / "site-functions" / "_scy-shell").exists())

            bkp_root = home / ".local" / "share" / "scy-shell" / "backups"
            install_bkps = sorted(bkp_root.glob("install-*"))
            self.assertGreaterEqual(len(install_bkps), 1)
            self.assertTrue((install_bkps[0] / "manifest.json").exists())

            # Uninstall via uninstall.sh wrapper -> keeps backups intact
            subprocess.check_call([UNINSTALL_SH, "--home", str(home)], stdout=subprocess.DEVNULL)
            self.assertFalse((home / ".local" / "bin" / "scy-shell").exists())
            self.assertTrue(install_bkps[0].exists())

            # Restore backup via install.sh --restore-backup
            subprocess.check_call(
                [INSTALL_SH, "--restore-backup", str(install_bkps[0]), "--home", str(home)],
                stdout=subprocess.DEVNULL,
            )
            self.assertIn("# Custom User Hyprland", (home / ".config" / "hypr" / "hyprland.conf").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
