import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scy_core.provenance import (
    ScyProvenanceVerifier,
    parse_patch_touched_files,
    parse_sha256_manifest,
)


class TestPhase1ProvenanceAndBaseline(unittest.TestCase):
    def test_01_provenance_metadata_and_3708_sha256_manifests_complete(self):
        prov_json = json.loads((ROOT / "provenance" / "PROVENANCE.json").read_text(encoding="utf-8"))
        self.assertEqual(prov_json["upstreams"]["lucid"]["pinned_commit"], "15f13429bc59b4a97223bcfe5592735cb1eb92be")
        self.assertEqual(prov_json["upstreams"]["mandara"]["pinned_commit"], "8a50e16af3a59cd8745df36e5656d825e5284641")
        self.assertIn("GPL-3.0-or-later", prov_json["combined_license"])

        lucid_m = parse_sha256_manifest(ROOT / "provenance" / "lucid-v1.21.1-sha256sums.txt")
        mandara_m = parse_sha256_manifest(ROOT / "provenance" / "mandara-v0.38.2-sha256sums.txt")
        self.assertEqual(len(lucid_m), 920)
        self.assertEqual(len(mandara_m), 2788)
        self.assertEqual(len(lucid_m) + len(mandara_m), 3708)

    def test_02_adapter_patches_capture_both_modified_and_added_files(self):
        l_mod, l_add = parse_patch_touched_files(ROOT / "adapters" / "lucid" / "lucid-scy-adapter.patch")
        self.assertIn("shell.qml", l_mod)
        self.assertIn("Prefs.qml", l_mod)
        self.assertIn("luciddocks/Dock.qml", l_mod)
        self.assertIn("ScyBridge.qml", l_add)
        self.assertIn("lucidbar/ScyPluginPill.qml", l_add)

        m_mod, m_add = parse_patch_touched_files(ROOT / "adapters" / "mandara" / "mandara-scy-adapter.patch")
        self.assertIn("crates/mandara-config/src/looks.rs", m_mod)
        self.assertIn("crates/mandara-config/src/scy_gates.rs", m_add)

    def test_03_live_reverse_patch_reconstructs_exact_upstream_sha256_baseline(self):
        verifier = ScyProvenanceVerifier(
            prov_dir=ROOT / "provenance",
            adap_dir=ROOT / "adapters",
            lucid_dir=ROOT / "engines" / "lucid",
            mandara_dir=ROOT / "engines" / "mandara",
        )
        rep = verifier.verify_all()
        self.assertTrue(rep["ok"], json.dumps(rep, indent=2))
        self.assertEqual(rep["lucid"]["hash_mismatches"], [])
        self.assertEqual(rep["lucid"]["reverse_errors"], [])
        self.assertEqual(rep["mandara"]["hash_mismatches"], [])
        self.assertEqual(rep["mandara"]["reverse_errors"], [])
        self.assertGreaterEqual(len(rep["lucid"]["reverse_patch_verified_files"]), 4)
        self.assertGreaterEqual(len(rep["mandara"]["reverse_patch_verified_files"]), 4)

    def test_04_cli_provenance_subcommand_succeeds(self):
        out = subprocess.check_output(
            [sys.executable, str(ROOT / "bin" / "scy-shell"), "provenance"],
            env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"},
            text=True,
        )
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["upstream_manifest_counts"]["total"], 3708)


if __name__ == "__main__":
    unittest.main(verbosity=2)
