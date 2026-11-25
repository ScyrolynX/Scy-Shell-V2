import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scy_core.config_store import ScyConfigStore
from scy_core.desktop_canvas import ScyDesktopCoordinator, WidgetBox
from scy_core.federation import WALLGEN_13_STYLES, ScyFederationEngine
from scy_core.security_preauth import (
    LUCID_6_LOCK_PRESETS,
    MANDARA_6_AUTH_DESIGNS,
    ScyPreAuthCoordinator,
)
from scy_core.toml_io import load_toml


class TestPhases567(unittest.TestCase):
    def test_phase5_plugin_federation_ai_agent_and_wallgen_13_styles(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            fed = ScyFederationEngine(store)

            # Verify all 88+ Mandara plugins are searchable via `@` federation
            all_plugins = fed.query_plugins("", limit=200)
            self.assertGreaterEqual(len(all_plugins), 88)
            fed_at = fed.federate_launcher_query("@weather")
            self.assertEqual(fed_at["mode"], "plugins")
            self.assertTrue(any(p["id"] == "weather" for p in fed_at["items"]))

            # Toggle plugin enablement and verify persistence in Mandara config.toml
            fed.set_plugin_enabled("tailscale", True)
            self.assertIn("tailscale", load_toml(store.mandara_config_path)["plugins"]["enabled"])
            fed.set_plugin_enabled("tailscale", False)
            self.assertIn("tailscale", load_toml(store.mandara_config_path)["plugins"]["disabled"])

            # Verify `!ai` natural-language command federation executes real changes
            ai_res = fed.interpret_ai_command("!ai switch bar to mandara and set gaps to 14 and apply sea-glass", apply_immediately=True)
            self.assertEqual(len(ai_res["actions"]), 3)
            self.assertEqual(store.get_provider("bar"), "mandara")
            self.assertEqual(store.get_setting("scy.providers.lucid.hypr.general.gaps_in"), 14)
            self.assertEqual(store.doc["presentations"]["primary_identity"], "sea-glass")

            # Verify all 13 Wallgen procedural styles generate valid SVG wallpapers & route to active provider!
            store.set_provider("wallpaper", "lucid")
            for st in WALLGEN_13_STYLES:
                wres = fed.generate_procedural_wallpaper(style=st, width=1280, height=720, seed_hex="#3b82f6")
                self.assertEqual(wres["renderer_provider"], "lucid")
                self.assertEqual(wres["apply_cmd"][0], "awww")
                self.assertTrue(Path(wres["path"]).exists())
                self.assertIn("<svg", Path(wres["path"]).read_text())

    def test_phase6_hybrid_widget_bounding_box_resolver_portals_and_agenda_bridge(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            desk = ScyDesktopCoordinator(store)

            lucid_w = [WidgetBox("lucid", "clock-hero", 100, 100, 320, 220)]
            # Colliding Mandara WASM widget placed right on top of Lucid clock!
            mandara_w = [WidgetBox("mandara", "wasm-pomodoro", 120, 120, 260, 180)]
            resolved = desk.resolve_hybrid_widget_boxes(lucid_w, mandara_w)
            self.assertFalse(resolved[0].overlaps(lucid_w[0]), "Colliding widget was not moved out of Lucid bounding box!")

            pconf = desk.write_portal_config(use_lumen_filechooser=True).read_text()
            self.assertIn("org.freedesktop.impl.portal.FileChooser=lumen;gtk", pconf)
            self.assertIn("org.freedesktop.impl.portal.ScreenCast=hyprland", pconf)

            agenda_p = desk.publish_synced_agenda([{"title": "Scy-Shell Review", "start": "2026-11-24T15:00:00Z"}])
            self.assertEqual(json.loads(agenda_p.read_text())["events"][0]["title"], "Scy-Shell Review")

    def test_phase7_lock_presets_auth_designs_and_dm_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            sec = ScyPreAuthCoordinator(store)

            for preset in LUCID_6_LOCK_PRESETS:
                res = sec.set_lock_design("lucid", preset)
                self.assertEqual(res["preset"], preset)
                self.assertEqual(store.get_provider("lock_screen"), "lucid")

            for design in MANDARA_6_AUTH_DESIGNS:
                res = sec.set_lock_design("mandara", design)
                self.assertEqual(res["design"], design)
                self.assertEqual(store.get_provider("lock_screen"), "mandara")

            staged = sec.stage_display_manager_configs()
            self.assertIn("fontFamily=Google Sans", staged["lucid_sddm_theme_conf"].read_text())
            gtoml = load_toml(staged["mandara_greeter_toml"])
            self.assertEqual(gtoml["font"], "Google Sans")


if __name__ == "__main__":
    unittest.main(verbosity=2)
