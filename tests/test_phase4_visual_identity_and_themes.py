import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scy_core.config_store import ScyConfigStore
from scy_core.theme_engine import (
    APP_THEME_TARGETS,
    ScyThemeCoordinator,
    contrast_ratio,
    generate_m3_expressive_tokens,
)
from scy_core.toml_io import load_toml


class TestPhase4VisualIdentityAndThemes(unittest.TestCase):
    def test_01_wcag_aa_contrast_dark_and_light_across_diverse_seeds(self):
        for seed in ("#ffb1c4", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"):
            for dark in (True, False):
                tok = generate_m3_expressive_tokens(seed, dark=dark)
                cr_text = contrast_ratio(tok["text"], tok["bg"])
                cr_accent = contrast_ratio(tok["fgAccent"], tok["accent"])
                cr_container = contrast_ratio(tok["fgAccentContainer"], tok["accentContainer"])
                self.assertGreaterEqual(cr_text, 7.0, f"Low text contrast for {seed} dark={dark}: {cr_text}")
                self.assertGreaterEqual(cr_accent, 4.5, f"Low accent contrast for {seed} dark={dark}: {cr_accent}")
                self.assertGreaterEqual(cr_container, 4.5, f"Low container contrast for {seed} dark={dark}: {cr_container}")

    def test_02_28_app_sha256_tamper_safe_ledger_never_clobbers_user_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)
            coord = ScyThemeCoordinator(store)

            # First apply writes all 28 app targets cleanly
            res1 = coord.apply_palette(seed_hex="#ffb1c4", dark_mode=True)
            self.assertEqual(len(res1["written_apps"]), 28)
            self.assertEqual(len(res1["skipped_user_modified_apps"]), 0)

            # Simulate user manually editing kitty & gtk4 configs!
            kitty_p = home / APP_THEME_TARGETS["kitty"]
            gtk4_p = home / APP_THEME_TARGETS["gtk4"]
            kitty_p.write_text("# My custom user kitty config\nbackground #000000\n")
            gtk4_p.write_text("/* User custom GTK4 override */\n")

            # Second apply with new seed MUST skip kitty & gtk4 while updating the other 26!
            res2 = coord.apply_palette(seed_hex="#3b82f6", dark_mode=False, adopt_modified=False)
            self.assertEqual(set(res2["skipped_user_modified_apps"]), {"kitty", "gtk4"})
            self.assertEqual(len(res2["written_apps"]), 26)
            self.assertIn("My custom user kitty config", kitty_p.read_text())

            # Explicit user opt-in (`adopt_modified=True`) backs up user files first, then updates!
            res3 = coord.apply_palette(seed_hex="#10b981", dark_mode=True, adopt_modified=True)
            self.assertEqual(len(res3["written_apps"]), 28)
            backups = list((store.backup_root / "app-themes").glob("*.bak"))
            self.assertGreaterEqual(len(backups), 2)

            # Verify portable Mandara user Look file was emitted in valid user_looks.rs format = 1
            look_toml = load_toml(home / ".config" / "mandara" / "looks" / "scy-m3-expressive.toml")
            self.assertEqual(look_toml["format"], 1)
            self.assertEqual(look_toml["id"], "scy-m3-expressive")
            self.assertEqual(look_toml["settings"]["typography"]["ui_font"], "Google Sans")

    def test_03_all_20_looks_preserved_in_mandara_working(self):
        looks_rs = (ROOT / "engines" / "mandara" / "crates" / "mandara-config" / "src" / "looks.rs").read_text()
        self.assertIn("pub const LOOKS: [LookDef; 20]", looks_rs)
        for id_str in ("corniche-dusk", "pharos-ink", "phosphor", "library-desk", "ink-rush", "zen", "scy-m3-expressive"):
            self.assertIn(f'id: "{id_str}"', looks_rs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
