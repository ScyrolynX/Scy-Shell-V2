import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scy_core.config_store import ScyConfigStore
from scy_core.hypr_coordinator import ScyHyprCoordinator


class TestPhase8HyprlandAndKeybinds(unittest.TestCase):
    def test_01_invented_hyprland_directives_strictly_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            hypr = ScyHyprCoordinator(store)

            ok, errs = hypr.validate_options({"general.gaps_in": 8, "lucid.solo": True})
            self.assertTrue(ok, errs)

            with self.assertRaises(ValueError):
                hypr.emit_modular_configs(extra_options={"decoration.fake_invented_blur_magic": 99})

    def test_02_unified_67_compositor_keybinds_zero_collisions_and_shared_ipc_routing(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            hypr = ScyHyprCoordinator(store)
            binds, collisions = hypr.build_unified_keybinds()
            self.assertEqual(len(binds), 67)  # 61 Lucid + 6 Mandara unique chords
            self.assertEqual(collisions, [], f"Unexpected keybind chord collisions: {collisions}")

            by_id = {b["id"]: b for b in binds}
            self.assertEqual(by_id["snap-text"]["keys"], "SUPER + SHIFT + T")
            self.assertEqual(by_id["scy-look-switcher"]["keys"], "SUPER + ALT + T")
            self.assertEqual(by_id["scy-ai-agent"]["keys"], "SUPER + SHIFT + A")
            self.assertEqual(by_id["launcher"]["cmd"], "scy-shell-ipc launcher toggle")
            self.assertEqual(by_id["clipboard"]["cmd"], "scy-shell-ipc clipboard toggle")
            self.assertEqual(by_id["snap-region"]["cmd"], "scy-shell-ipc shot region")
            self.assertEqual(by_id["snap-full"]["cmd"], "scy-shell-ipc shot screen")
            self.assertEqual(by_id["overview"]["cmd"], "scy-shell-ipc overview toggle")
            self.assertEqual(by_id["wallpaper"]["cmd"], "scy-shell-ipc wallpaper picker")

    def test_03_all_17_stage0_and_22_qml_desktop_icons_shortcuts_plus_25_mandara_keybinds_accounted(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            hypr = ScyHyprCoordinator(store)
            ledger = hypr.build_complete_shortcut_ledger()
            counts = ledger["counts"]

            # Verify exact counts across every single scope!
            self.assertEqual(counts["lucid_compositor_original"], 61)
            self.assertEqual(counts["mandara_unique_added"], 6)
            self.assertEqual(counts["compositor_unified_total"], 67)
            self.assertEqual(counts["desktop_icons_stage0_grouped"], 17)
            self.assertEqual(counts["desktop_icons_qml_key_actions_total"], 22)
            self.assertEqual(counts["desktop_icons_qml_active_bound"], 19)
            self.assertEqual(counts["desktop_icons_qml_unbound_slots"], 3)
            self.assertEqual(counts["icon_board_navigation_handlers"], 6)
            self.assertEqual(counts["mandara_default_keybinds_accounted"], 25)

            self.assertEqual(ledger["compositor_collisions"], [])
            self.assertEqual(ledger["desktop_icons_intra_clashes"], [])
            self.assertEqual(ledger["cross_scope_compositor_overlaps"], [])
            # If a user opts into bare F1..F12 media keys, ledger explicitly flags F2 (rename) & F5 (refresh) shadowing!
            ledger_fn = hypr.build_complete_shortcut_ledger(enable_bare_fn_media_keys=True)
            fn_chords = {x["chord"] for x in ledger_fn["cross_scope_compositor_overlaps"]}
            self.assertEqual(fn_chords, {"F2", "F5"})

            # Verify live user remapping via Prefs.desktopKeys (`scy.providers.lucid.prefs.desktopKeys`)
            store.set_setting(
                "scy.providers.lucid.prefs.desktopKeys",
                json.dumps({"compress": "Ctrl+Shift+Z", "arrange": "Ctrl+Alt+A"}),
            )
            ledger2 = hypr.build_complete_shortcut_ledger()
            self.assertEqual(ledger2["counts"]["desktop_icons_qml_active_bound"], 21)
            self.assertEqual(ledger2["counts"]["desktop_icons_qml_unbound_slots"], 1)
            self.assertEqual(ledger2["desktop_icons_intra_clashes"], [])
            self.assertEqual(ledger2["cross_scope_compositor_overlaps"], [])

            # Verify cross-scope warning triggers if user binds a DesktopIcons slot onto a SUPER compositor chord!
            store.set_setting(
                "scy.providers.lucid.prefs.desktopKeys",
                json.dumps({"compress": "SUPER + SHIFT + A"}),
            )
            ledger3 = hypr.build_complete_shortcut_ledger()
            self.assertEqual(len(ledger3["cross_scope_compositor_overlaps"]), 1)
            self.assertEqual(ledger3["cross_scope_compositor_overlaps"][0]["compositor_bind"], "scy-ai-agent")

    def test_04_non_destructive_user_config_include_and_15s_trial_revert(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            hypr_dir = home / ".config" / "hypr"
            hypr_dir.mkdir(parents=True)
            user_lua = hypr_dir / "hyprland.lua"
            user_lua.write_text('-- My custom Hyprland Lua\nrequire("modules.settings")\nrequire("hypr-user")\n')

            store = ScyConfigStore(home_dir=home)
            hypr = ScyHyprCoordinator(store)
            hypr.emit_modular_configs({"general.gaps_in": 6})

            updated_lua = user_lua.read_text()
            self.assertIn("-- My custom Hyprland Lua", updated_lua)
            self.assertLess(updated_lua.index('pcall(require, "scy-shell.init")'), updated_lua.index('require("hypr-user")'))

            hypr.begin_trial({"general.gaps_in": 24}, timeout_s=15)
            self.assertIn('["general.gaps_in"] = 24', hypr.lucid_settings_lua.read_text())

            rev = hypr.revert_trial()
            self.assertTrue(rev["ok"])
            self.assertIn('["general.gaps_in"] = 6', hypr.lucid_settings_lua.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
