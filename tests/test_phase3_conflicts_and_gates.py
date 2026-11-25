import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scy_core.config_store import ScyConfigStore
from scy_core.conflicts import ScyConflictScanner
from scy_core.provenance import ScyProvenanceVerifier


class TestPhase3ConflictsAndGates(unittest.TestCase):
    def test_01_upstream_sha256_integrity_preserved_across_both_engines(self):
        rep = ScyProvenanceVerifier().verify_all()
        self.assertTrue(rep["ok"])

    def test_02_external_daemon_and_cross_provider_conflict_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            scanner = ScyConflictScanner(store)

            mock_procs = [
                (1001, "mako", "/usr/bin/mako"),
                (1002, "waybar", "/usr/bin/waybar"),
                (1003, "hyprpolkitagent", "/usr/lib/hyprpolkitagent"),
                (1004, "hyprsunset", "hyprsunset -t 4200"),
            ]
            items = scanner.scan_all(mock_processes=mock_procs)
            domains = [c.domain for c in items]
            self.assertIn("notifications", domains)
            self.assertIn("bar", domains)
            self.assertIn("polkit", domains)
            self.assertNotIn("night_light", domains)

            items_nl = scanner.scan_all(
                mock_processes=mock_procs,
                proposed_domain="night_light",
                proposed_provider="mandara",
            )
            self.assertTrue(any(c.domain == "night_light" and c.severity == "critical" for c in items_nl))

    def test_03_display_manager_sddm_vs_greetd_conflict_and_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            scanner = ScyConflictScanner(store)
            store.set_provider("display_manager", "mandara-greetd")
            items = scanner.scan_all(mock_processes=[], mock_dm_target="sddm.service")
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].domain, "display_manager")

            res = scanner.resolve({"action": "keep_dm"})
            self.assertTrue(res["ok"])
            self.assertEqual(store.get_provider("display_manager"), "preserve")

    def test_04_internal_gate_drift_detected_and_repaired(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            scanner = ScyConflictScanner(store)
            store.doc["providers"]["mandara"]["config"]["scy_gates"]["owns_notifications"] = True
            items = scanner.scan_all(mock_processes=[])
            self.assertTrue(any(c.kind == "internal_gate" and c.domain == "notifications" for c in items))

            scanner.resolve({"action": "resync_gates"})
            items_after = scanner.scan_all(mock_processes=[])
            self.assertEqual(len(items_after), 0)

    def test_05_bundled_engine_adapters_mounted_in_shell_dock_and_mandara(self):
        lucid = ROOT / "engines" / "lucid"
        mandara = ROOT / "engines" / "mandara"
        self.assertTrue((lucid / "ScyBridge.qml").exists())
        shell_txt = (lucid / "shell.qml").read_text(encoding="utf-8")
        self.assertIn('ScyBridge.owns("notifications")', shell_txt)
        self.assertIn("ScyPluginPill {", shell_txt)

        dock_txt = (lucid / "luciddocks" / "Dock.qml").read_text(encoding="utf-8")
        self.assertIn('"scy-ai"', dock_txt)
        self.assertIn('"scy-plugin"', dock_txt)
        self.assertIn("scy-schema/plugins_catalogue.json", dock_txt)

        self.assertTrue((mandara / "crates" / "mandara-config" / "src" / "scy_gates.rs").exists())
        self.assertIn(
            "scy_gates.notifications_enabled()",
            (mandara / "crates" / "mandara-ui" / "src" / "hub.rs").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "gates.needs_shell_surface()",
            (mandara / "crates" / "mandara-app" / "src" / "surfaces.rs").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
