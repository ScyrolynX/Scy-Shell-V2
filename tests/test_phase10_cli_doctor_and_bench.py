import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCY_CLI = str(ROOT / "bin" / "scy-shell")


class TestPhase10CliDoctorAndBench(unittest.TestCase):
    def test_01_cli_status_doctor_provider_config_wallgen_plugins_and_keybinds(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = [sys.executable, SCY_CLI, "--home", tmp]

            st = json.loads(subprocess.check_output(base + ["status"], text=True))
            self.assertEqual(st["engine_settings_total"], 1875)
            self.assertEqual(st["scy_native_settings_total"], 151)
            self.assertEqual(st["settings_total"], 2026)
            self.assertEqual(len(st["studio_sections"]), 15)
            self.assertEqual(st["active_providers"]["bar"], "lucid")

            doc = json.loads(subprocess.check_output(base + ["doctor", "--json"], text=True))
            self.assertTrue(doc["resource_discipline"]["mandara_zero_swapchain_dormant_mode"])

            subprocess.check_call(base + ["provider", "bar", "mandara"], stdout=subprocess.DEVNULL)
            doc2 = json.loads(subprocess.check_output(base + ["doctor", "--json"], text=True))
            self.assertFalse(doc2["resource_discipline"]["mandara_zero_swapchain_dormant_mode"])

            hits = json.loads(subprocess.check_output(base + ["config", "search", "jellyAmount"], text=True))
            self.assertGreaterEqual(len(hits), 1)
            subprocess.check_call(base + ["config", "set", "scy.providers.lucid.prefs.jellyAmount", "0.75"], stdout=subprocess.DEVNULL)
            val = json.loads(subprocess.check_output(base + ["config", "get", "scy.providers.lucid.prefs.jellyAmount"], text=True))
            self.assertAlmostEqual(val, 0.75)

            wg = json.loads(subprocess.check_output(base + ["wallgen", "voronoi", "--seed", "#7AA2F7"], text=True))
            self.assertTrue(Path(wg["path"]).exists())

            pls = json.loads(subprocess.check_output(base + ["plugins", "pomodoro"], text=True))
            self.assertGreaterEqual(pls["count"], 1)

            kb = json.loads(subprocess.check_output(base + ["hypr", "keybinds", "--full"], text=True))
            self.assertEqual(kb["counts"]["compositor_unified_total"], 67)
            self.assertEqual(kb["counts"]["desktop_icons_stage0_grouped"], 17)
            self.assertEqual(kb["counts"]["desktop_icons_qml_key_actions_total"], 22)
            self.assertEqual(kb["counts"]["mandara_default_keybinds_accounted"], 25)

    def test_02_benchmark_results_json_recorded_real_metrics(self):
        bench = json.loads((ROOT / "docs" / "stage1" / "benchmark-results.json").read_text(encoding="utf-8"))
        m = bench["measured_metrics"]
        self.assertGreater(m["scy_daemon_vmrss_mb"], 1.0)
        self.assertLess(m["scy_daemon_vmrss_mb"], 80.0)
        self.assertLess(m["c11_ipc_roundtrip_p50_ms"], 25.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
