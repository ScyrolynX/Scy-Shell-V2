import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUCID = Path(
    __import__("os").environ.get("SCY_LUCID_DIR")
    or str(ROOT / "engines" / "lucid")
)
LUCID_PATCH = ROOT / "adapters" / "lucid" / "lucid-scy-adapter.patch"


class TestPhase9StudioCoverage(unittest.TestCase):
    def test_01_all_studio_and_modified_qml_files_have_balanced_delimiters(self):
        new_qml_files = list((LUCID / "lucidprefs").glob("Scy*.qml")) + [
            LUCID / "ScyBridge.qml",
            LUCID / "ScyDesignTokens.qml",
            LUCID / "lucidbar" / "ScyPluginPill.qml",
            LUCID / "lucidbar" / "ScyDynamicIsland.qml",
        ]
        self.assertEqual(len(new_qml_files), 28)

        for qf in new_qml_files:
            txt = qf.read_text(encoding="utf-8")
            no_comments = re.sub(r"//.*", "", txt)
            no_strings = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '""', no_comments)
            self.assertEqual(no_strings.count("{"), no_strings.count("}"), f"Unbalanced {{}} in {qf.name}")
            self.assertEqual(no_strings.count("["), no_strings.count("]"), f"Unbalanced [] in {qf.name}")
            self.assertEqual(no_strings.count("("), no_strings.count(")"), f"Unbalanced () in {qf.name}")

        modified_rels = ["Prefs.qml", "LockStyle.qml", "shell.qml", "lucidprefs/Settings.qml", "luciddocks/Dock.qml"]
        extra_patch_rels = ["support/lucid/launch-shell.sh"]
        with tempfile.TemporaryDirectory() as tmp:
            troot = Path(tmp)
            for qf in new_qml_files:
                dst = troot / qf.relative_to(LUCID)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(qf, dst)
            for rel in ["scy-schema/settings_catalogue.json", "scy-schema/plugins_catalogue.json", "scy-schema/keybindings_catalogue.json", *modified_rels, *extra_patch_rels]:
                src = LUCID / rel
                dst = troot / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

            subprocess.check_call(
                ["patch", "-p1", "-R", "--batch", "--silent", "-i", str(LUCID_PATCH)],
                cwd=troot,
            )
            for rel in modified_rels:
                up = (troot / rel).read_text(encoding="utf-8")
                wk = (LUCID / rel).read_text(encoding="utf-8")
                self.assertEqual(wk.count("{") - wk.count("}"), up.count("{") - up.count("}"), f"Brace drift in {rel}")
                self.assertEqual(wk.count("[") - wk.count("]"), up.count("[") - up.count("]"), f"Bracket drift in {rel}")
                self.assertEqual(wk.count("(") - wk.count(")"), up.count("(") - up.count(")"), f"Paren drift in {rel}")

    def test_02_every_settings_page_key_maps_to_real_qml_file(self):
        prefs_txt = (LUCID / "Prefs.qml").read_text(encoding="utf-8")
        settings_txt = (LUCID / "lucidprefs" / "Settings.qml").read_text(encoding="utf-8")
        page_keys = re.findall(
            r'\{\s*"key":\s*"([^"]+)"',
            prefs_txt[prefs_txt.find("settingsPages: ["):prefs_txt.find("function settingsPage")],
        )
        self.assertEqual(len(page_keys), 53)

        for k in page_keys:
            if k == "about":
                self.assertIn('default:\n                                return "AboutPage.qml";', settings_txt)
                qml_file = "AboutPage.qml"
            else:
                m = re.search(rf'case "{re.escape(k)}":\s*return "([^"]+\.qml)";', settings_txt)
                self.assertIsNotNone(m, f"Page key '{k}' missing from Settings.qml paneLoader switch!")
                qml_file = m.group(1)
            qml_path = LUCID / "lucidprefs" / qml_file
            self.assertTrue(qml_path.exists(), f"Missing QML file for '{k}': {qml_path}")

    def test_03_type_aware_1875_studio_controls_live_loading_validation_and_preview(self):
        cat = json.loads((LUCID / "scy-schema" / "settings_catalogue.json").read_text(encoding="utf-8"))
        all_entries = cat["lucid_settings"] + cat["mandara_settings"]
        self.assertEqual(len(all_entries), 1875)
        for item in all_entries:
            self.assertIn("ui_widget", item)
            self.assertIn("concrete_type", item)
            self.assertNotEqual(item["concrete_type"], "config_field")
            self.assertIn("default_value", item)
            self.assertIn("live_preview", item)

        vault_qml = (LUCID / "lucidprefs" / "ScyVaultPage.qml").read_text(encoding="utf-8")
        for control_token in ("M3Switch", "M3Slider", "M3Segmented", "M3Dropdown", "M3TextField", "isValidHexColor", "ScyBridge.getValue", "ScyBridge.setSetting", "ScyBridge.resetSetting"):
            self.assertIn(control_token, vault_qml)

        bridge_qml = (LUCID / "ScyBridge.qml").read_text(encoding="utf-8")
        self.assertIn("live-values.json", bridge_qml)
        self.assertIn('"config", "set-json"', bridge_qml)
        self.assertIn('"provider", domain, provider', bridge_qml)
        self.assertIn('"presentation", domain, val', bridge_qml)

        plugs = json.loads((LUCID / "scy-schema" / "plugins_catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(len(plugs), 89)
        kb = json.loads((LUCID / "scy-schema" / "keybindings_catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(kb["summary"]["unified_compositor_binds_total"], 67)

    @unittest.skipUnless(
        shutil.which("qmllint") or Path("/usr/lib/qt6/bin/qmllint").exists(),
        "Requires Qt6 qmllint binary on host",
    )
    def test_04_fatal_qmllint_passes_cleanly_and_fails_on_invalid_qml(self):
        env = dict(__import__("os").environ, SCY_LUCID_DIR=str(LUCID))
        lint_script = str(ROOT / "scripts" / "lint-qml.sh")
        ok_proc = subprocess.run([lint_script], env=env, capture_output=True, text=True)
        self.assertEqual(ok_proc.returncode, 0, ok_proc.stderr or ok_proc.stdout)
        self.assertEqual(ok_proc.stderr.strip(), "", f"Unexpected qmllint warnings:\n{ok_proc.stderr}")

        # Negative test: broken QML MUST fail fatally (non-zero exit code, never swallowed!)
        with tempfile.NamedTemporaryFile("w", suffix=".qml", delete=False) as bad:
            bad.write("import QtQuick\nItem { nonExistentProp: 42; UnresolvedBogusWidget {} }\n")
            bad_path = bad.name
        try:
            bad_proc = subprocess.run([lint_script, bad_path], env=env, capture_output=True, text=True)
            self.assertNotEqual(bad_proc.returncode, 0, "lint-qml.sh failed to exit non-zero on broken QML!")
        finally:
            Path(bad_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
