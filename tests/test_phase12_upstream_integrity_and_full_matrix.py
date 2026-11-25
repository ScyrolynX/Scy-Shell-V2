import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPhase12UpstreamIntegrityAndFullMatrix(unittest.TestCase):
    def test_01_zero_hardcoded_workspace_paths_anywhere_in_code_scripts_or_tests(self):
        forbidden = "/" + "home" + "/" + "user"
        scan_dirs = ["src", "bin", "scripts", "tests", "studio", "packaging"]
        offenders: list[str] = []
        for d in scan_dirs:
            base = ROOT / d
            if not base.exists():
                continue
            for p in base.rglob("*"):
                if not p.is_file() or "__pycache__" in p.parts or p.suffix in (".pyc", ".so") or p.name == "scy-shell-ipc":
                    continue
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if forbidden in txt:
                    offenders.append(str(p.relative_to(ROOT)))
        for top in ["install.sh", "Makefile", "README.md"]:
            p = ROOT / top
            if p.exists() and forbidden in p.read_text(encoding="utf-8", errors="ignore"):
                offenders.append(top)
        self.assertEqual(offenders, [], f"Hard-coded workspace path found in: {offenders}")

    def test_02_mandara_rust_workspace_340_compile_time_assets_and_struct_literals_intact(self):
        mandara = ROOT / "engines" / "mandara"
        self.assertTrue((mandara / "Cargo.toml").exists())
        self.assertTrue((mandara / "Cargo.lock").exists())

        direct_re = re.compile(r'include_(?:bytes|str)!\s*\(\s*"([^"]+)"\s*,?\s*\)', re.DOTALL)
        concat_re = re.compile(r'include_(?:bytes|str)!\s*\(\s*concat!\s*\(\s*env!\("CARGO_MANIFEST_DIR"\)\s*,\s*"([^"]+)"\s*\)\s*\)', re.DOTALL)
        macro_total = 0
        checked_includes = 0
        missing_includes: list[str] = []
        bad_shell_literals: list[str] = []

        for rs in (mandara / "crates").rglob("*.rs"):
            txt = rs.read_text(encoding="utf-8", errors="ignore")
            macro_total += len(re.findall(r"include_(?:bytes|str)!", txt))
            for m in direct_re.finditer(txt):
                rel = m.group(1)
                if "$" in rel:
                    continue
                checked_includes += 1
                if not (rs.parent / rel).resolve().exists():
                    missing_includes.append(f"{rs.relative_to(mandara)} -> {rel}")
            crate_dir = rs
            while crate_dir != mandara and not (crate_dir / "Cargo.toml").exists():
                crate_dir = crate_dir.parent
            for m in concat_re.finditer(txt):
                rel = m.group(1).lstrip("/")
                checked_includes += 1
                if not (crate_dir / rel).resolve().exists():
                    missing_includes.append(f"{rs.relative_to(mandara)} -> CARGO_MANIFEST_DIR/{rel}")

            for m in re.finditer(r"\bShellConfig\s*\{", txt):
                idx = m.end()
                depth = 1
                while idx < len(txt) and depth > 0:
                    if txt[idx] == "{":
                        depth += 1
                    elif txt[idx] == "}":
                        depth -= 1
                    idx += 1
                body = txt[m.end():idx - 1]
                if "appearance:" in body and "bar:" in body and ".." not in body and "scy_gates:" not in body:
                    bad_shell_literals.append(str(rs.relative_to(mandara)))

        self.assertGreaterEqual(macro_total, 340)
        self.assertGreaterEqual(checked_includes, 76)
        self.assertEqual(missing_includes, [], f"Missing Rust include_bytes!/include_str! files: {missing_includes}")
        self.assertEqual(bad_shell_literals, [], f"Exhaustive ShellConfig literal missing scy_gates/..: {bad_shell_literals}")

    def test_03_all_catalogues_patches_looks_and_licenses_verified(self):
        feat = json.loads((ROOT / "schema" / "feature_inventory.json").read_text(encoding="utf-8"))
        subs = feat["subsystems"] if isinstance(feat, dict) and "subsystems" in feat else feat
        self.assertEqual(len(subs), 41)

        cat = json.loads((ROOT / "schema" / "settings_catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cat["lucid_settings"]), 643)
        self.assertEqual(len(cat["mandara_settings"]), 1232)
        self.assertEqual(len(cat["lucid_settings"]) + len(cat["mandara_settings"]), 1875)

        plugs = json.loads((ROOT / "schema" / "plugins_catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(len(plugs), 89)

        looks_rs = (ROOT / "engines" / "mandara" / "crates" / "mandara-config" / "src" / "looks.rs").read_text(encoding="utf-8")
        self.assertIn("pub const LOOKS: [LookDef; 20]", looks_rs)
        self.assertIn('id: "scy-m3-expressive"', looks_rs)

        for patch_rel in ["adapters/lucid/lucid-scy-adapter.patch", "adapters/mandara/mandara-scy-adapter.patch"]:
            p = ROOT / patch_rel
            self.assertTrue(p.exists() and p.stat().st_size > 200, f"Missing or empty patch: {p}")

        self.assertTrue((ROOT / "LICENSE").exists())
        self.assertTrue((ROOT / "THIRD_PARTY_NOTICES.md").exists())
        self.assertTrue((ROOT / "bin" / "scy-shell-ipc").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
