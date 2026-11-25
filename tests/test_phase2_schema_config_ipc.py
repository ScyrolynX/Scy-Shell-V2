import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scy_core.config_store import ScyConfigStore, _parse_ini_general
from scy_core.ipc_bus import ScyIpcServer
from scy_core.schema import MANDARA_19_LOOKS, PROVIDER_DOMAINS, ScySchema
from scy_core.toml_io import get_pointer, load_toml


def _make_valid_test_value(sid: str, meta, idx: int):
    if sid == "scy.providers.lucid.prefs.hyprOptions":
        return json.dumps({"general.gaps_in": 9})
    if sid == "scy.providers.lucid.prefs.lockWidgetOpts":
        return json.dumps({"clock": {"tone": "mono"}})
    ctype = meta.concrete_type
    if ctype == "table":
        return {"_scy_section_marker": idx}
    if ctype == "bool":
        return not bool(meta.default_value)
    if ctype == "enum" and meta.choices:
        keys = [c["key"] for c in meta.choices]
        for k in keys:
            if k != meta.default_value:
                return k
        return keys[0]
    if ctype == "int":
        if meta.choices:
            return int(meta.choices[-1]["key"])
        lo = int(meta.min_val) if meta.min_val is not None else 0
        hi = int(meta.max_val) if meta.max_val is not None else 100
        cand = min(hi, max(lo, lo + ((idx % 7) + 1) * int(meta.step or 1)))
        if cand == meta.default_value and cand < hi:
            cand = min(hi, cand + int(meta.step or 1))
        return cand
    if ctype == "float":
        lo = float(meta.min_val) if meta.min_val is not None else 0.0
        hi = float(meta.max_val) if meta.max_val is not None else 1.0
        step = float(meta.step) if meta.step else 0.05
        cand = round(min(hi, max(lo, lo + step * 2.0)), 4)
        if cand == meta.default_value and cand + step <= hi:
            cand = round(cand + step, 4)
        return cand
    if ctype == "color":
        palette = ["#7aa2f7", "#10b981", "#f59e0b", "#a855f7", "#ef4444", "#06b6d4"]
        pick = palette[idx % len(palette)]
        return "#3b82f6" if pick == meta.default_value else pick
    if ctype == "time":
        return "21:45" if meta.default_value != "21:45" else "07:30"
    if ctype == "spring":
        return {"stiffness": 410.0, "damping": 31.0}
    if ctype == "list":
        return [f"item_{idx}_a", f"item_{idx}_b"]
    if ctype == "json":
        return {"k": f"v_{idx}"}
    return f"scy_val_{idx}"


class TestPhase2SchemaConfigIpc(unittest.TestCase):
    def test_01_all_1875_settings_type_enriched_zero_generic_config_field(self):
        schema = ScySchema()
        self.assertEqual(schema.lucid_count, 643)
        self.assertEqual(schema.mandara_count, 1232)
        self.assertEqual(schema.engine_total_count, 1875)
        self.assertEqual(schema.scy_native_count, 151)
        self.assertEqual(schema.total_count, 2026)
        self.assertEqual(len(schema.studio_sections), 15)
        self.assertEqual(len(MANDARA_19_LOOKS), 20)
        self.assertGreaterEqual(len(PROVIDER_DOMAINS), 18)

        # Assert ZERO settings have generic concrete_type "config_field"
        generic = [m.scy_id for m in schema.by_id.values() if m.concrete_type == "config_field"]
        self.assertEqual(generic, [])

        widgets = {m.ui_widget for m in schema.by_id.values()}
        for expected_w in ("switch", "slider", "segmented", "dropdown", "color", "number", "spring", "list", "text"):
            self.assertIn(expected_w, widgets)

    def test_02_all_1875_settings_persist_to_all_14_native_engine_stores_and_survive_provider_switches(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            # Pre-seed a live Lucid widget instance to verify live instance opts also update!
            wpath = home / ".config" / "quickshell" / "lucidwidgets" / "widgets.json"
            wpath.parent.mkdir(parents=True, exist_ok=True)
            wpath.write_text(json.dumps({
                "nextId": 2,
                "instances": [{"id": "w1", "type": "clock", "opts": {"seconds": False}}],
            }))

            store = ScyConfigStore(home_dir=home)

            written = {}
            # Set macro preset triggers first, then non-embedded prefs, then specific hypr/lock_widgets/leaf overrides
            macro_triggers = {
                "scy.profiles.active",
                "scy.layout.active_preset",
                "scy.dock.preset",
                "scy.performance.tier",
                "scy.effects.material_preset",
                "scy.effects.motion_preset",
            }
            ordered_items = sorted(
                store.schema.by_id.items(),
                key=lambda kv: (
                    0 if kv[0] in macro_triggers else (
                        2 if kv[0].startswith(("scy.providers.lucid.hypr.", "scy.providers.lucid.lock_widgets.")) else 1
                    ),
                    kv[0],
                ),
            )
            for idx, (sid, meta) in enumerate(ordered_items):
                val = _make_valid_test_value(sid, meta, idx)
                store.set_setting(sid, val, flush=False, validate=True)
                written[sid] = store.get_setting(sid)

            store.flush_all()

            # Switch EVERY provider across ALL domains (`lucid -> mandara -> hybrid -> none -> lucid`)
            for domain, allowed in PROVIDER_DOMAINS.items():
                for choice in (*allowed, allowed[0]):
                    ok, msg = store.set_provider(domain, choice)
                    self.assertTrue(ok, msg)
            # Single-owner dock arbitration deterministically synchronizes dock ownership gates
            dock_gate_keys = {
                "scy.dock.mode",
                "scy.providers.lucid.prefs.dockEnabled",
                "scy.providers.mandara.config.dock.enabled",
                "scy.providers.mandara.config.plugins.enabled",
                "scy.providers.mandara.config.plugins.disabled",
            }
            for gk in dock_gate_keys:
                if gk in written:
                    written[gk] = store.get_setting(gk)

            # Verify ALL 14 native original-engine files on disk contain the exact persisted settings!
            lucid_prefs = json.loads(store.lucid_prefs_path.read_text(encoding="utf-8"))
            self.assertEqual(lucid_prefs["barEnabled"], written["scy.providers.lucid.prefs.barEnabled"])
            hypr_embedded = json.loads(lucid_prefs["hyprOptions"])
            self.assertEqual(hypr_embedded["general.gaps_in"], written["scy.providers.lucid.hypr.general.gaps_in"])
            lock_embedded = json.loads(lucid_prefs["lockWidgetOpts"])
            self.assertEqual(lock_embedded["clock"]["style"], written["scy.providers.lucid.lock_widgets.clock.style"])

            lua_txt = store.lucid_hypr_lua_path.read_text(encoding="utf-8")
            self.assertIn('["general.gaps_in"]', lua_txt)

            blur_doc = json.loads(store.lucid_blur_path.read_text(encoding="utf-8"))
            self.assertAlmostEqual(blur_doc["value"], written["scy.providers.lucid.glass.blurValue"])

            widgets_doc = json.loads(store.lucid_widgets_path.read_text(encoding="utf-8"))
            self.assertIn("clock", widgets_doc["scyWidgetDefaults"])
            self.assertEqual(
                widgets_doc["instances"][0]["opts"]["seconds"],
                written["scy.providers.lucid.widget_opts.clock.seconds"],
            )

            moji_cfg = json.loads(store.lucid_moji_config_path.read_text(encoding="utf-8"))
            moji_st = json.loads(store.lucid_moji_state_path.read_text(encoding="utf-8"))
            self.assertEqual(moji_cfg["giphyKey"], written["scy.providers.lucid.moji.giphyKey"])
            self.assertEqual(moji_st["skinTone"], written["scy.providers.lucid.moji.skinTone"])

            for app_k in ("lumen", "lens", "clock_app", "shot_state", "keys"):
                self.assertTrue(store.lucid_app_paths[app_k].exists(), f"Missing native app store {app_k}")

            sddm_ini = _parse_ini_general(store.lucid_sddm_stage_path)
            self.assertGreaterEqual(len(sddm_ini), 20)

            m_cfg = load_toml(store.mandara_config_path)
            self.assertIn("scy_gates", m_cfg)
            self.assertEqual(get_pointer(m_cfg, "/bar/capsule_fill"), written["scy.providers.mandara.config.bar.capsule_fill"])

            m_wall = load_toml(store.mandara_wallgen_path)
            self.assertTrue(len(m_wall) > 0)
            m_greet = load_toml(store.mandara_greeter_stage_path)
            self.assertTrue(len(m_greet) > 0)

            live_vals = json.loads(store.live_values_path.read_text(encoding="utf-8"))
            self.assertGreater(len(live_vals["values"]), 1500)

            # Test 2A: Reload from ScyConfigStore (`scy-shell/config.toml`)
            reloaded = ScyConfigStore(home_dir=home)
            for sid, expected in written.items():
                if sid in ("scy.providers.lucid.prefs.hyprOptions", "scy.providers.lucid.prefs.lockWidgetOpts"):
                    continue
                actual = reloaded.get_setting(sid)
                if reloaded.schema.by_id[sid].value_type == "table":
                    self.assertEqual(actual.get("_scy_section_marker"), expected["_scy_section_marker"])
                else:
                    self.assertEqual(actual, expected, f"Mismatch after provider switches on {sid}")

            # Test 2B: Delete scy-shell/config.toml (+ .last-good) completely and reload EXCLUSIVELY from the 14 native original-engine files!
            store.config_path.unlink()
            store.last_good_config_path.unlink(missing_ok=True)
            from_native_only = ScyConfigStore(home_dir=home)
            for sid, expected in written.items():
                if sid in ("scy.providers.lucid.prefs.hyprOptions", "scy.providers.lucid.prefs.lockWidgetOpts"):
                    continue
                if from_native_only.schema.by_id[sid].source_project == "scy":
                    continue
                actual = from_native_only.get_setting(sid)
                if from_native_only.schema.by_id[sid].value_type == "table":
                    self.assertEqual(actual.get("_scy_section_marker"), expected["_scy_section_marker"])
                else:
                    self.assertEqual(actual, expected, f"Native-only reload mismatch on {sid}")

    def test_03_type_aware_validation_and_range_enforcement(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            with self.assertRaises(ValueError):
                store.set_setting("scy.providers.lucid.prefs.barEnabled", "not-a-boolean")
            with self.assertRaises(ValueError):
                store.set_setting("scy.providers.mandara.config.bar.capsule_fill", "nonexistent-enum-option")
            with self.assertRaises(ValueError):
                store.set_setting("scy.providers.lucid.prefs.themeColour", "not-a-hex-color")
            with self.assertRaises(ValueError):
                store.set_setting("scy.providers.lucid.prefs.barSpacing", -99999)
            with self.assertRaises(ValueError):
                store.set_setting("scy.providers.lucid.prefs.barSpacing", 999999)
            with self.assertRaises(ValueError):
                store.set_setting("scy.providers.mandara.config.theme", "cannot-overwrite-table-with-string")

    def test_04_pinned_apps_sync_and_backup_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            store = ScyConfigStore(home_dir=home)
            store.set_setting("scy.providers.lucid.prefs.barSpacing", 14)
            apps = store.sync_pinned_apps(["org.kde.dolphin.desktop", "kitty.desktop", "zen.desktop"])
            self.assertEqual(len(apps), 3)
            self.assertEqual(json.loads(store.lucid_pinned_path.read_text()), apps)

            bdir = store.create_backup("unit-test")
            store.set_setting("scy.providers.lucid.prefs.barSpacing", 20)
            self.assertEqual(store.get_setting("scy.providers.lucid.prefs.barSpacing"), 20)

            store.restore_backup(bdir)
            self.assertEqual(store.get_setting("scy.providers.lucid.prefs.barSpacing"), 14)

    def test_05_live_unix_socket_c_binary_ipc_and_provider_switch_arbitration(self):
        async def run_ipc():
            with tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                sock = home / "scy.sock"
                store = ScyConfigStore(home_dir=home)
                srv = ScyIpcServer(store, sock_path=sock, dry_exec=True)
                await srv.start()
                try:
                    env = dict(os.environ, SCY_SHELL_SOCK=str(sock))
                    c_bin = str(ROOT / "bin" / "scy-shell-ipc")

                    t0 = time.perf_counter()
                    p1 = await asyncio.create_subprocess_exec(
                        c_bin, "--json", "lock", env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    out1, err1 = await p1.communicate()
                    dt_ms = (time.perf_counter() - t0) * 1000.0
                    self.assertEqual(p1.returncode, 0, err1.decode())
                    resp = json.loads(out1.decode())
                    self.assertEqual(resp["result"]["routed_to"], "lucid")
                    self.assertEqual(resp["result"]["cmd"], ["qs", "ipc", "call", "lock", "lock"])
                    self.assertLess(dt_ms, 50.0)

                    # Switch lock_screen + notifications to Mandara via JSON-RPC over Unix socket and verify exclusive gates!
                    reader, writer = await asyncio.open_unix_connection(str(sock))
                    writer.write(b'{"jsonrpc":"2.0","id":2,"method":"provider.set","params":{"domain":"lock_screen","provider":"mandara"}}\n')
                    await writer.drain()
                    rline = await reader.readline()
                    writer.close()
                    await writer.wait_closed()
                    self.assertTrue(json.loads(rline.decode())["result"]["ok"])

                    m_cfg = load_toml(store.mandara_config_path)
                    self.assertTrue(m_cfg["scy_gates"]["owns_lock"])
                    self.assertFalse(m_cfg["scy_gates"]["owns_notifications"])

                    p2 = await asyncio.create_subprocess_exec(
                        c_bin, "--json", "lock", env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    out2, err2 = await p2.communicate()
                    self.assertEqual(p2.returncode, 0, err2.decode())
                    resp2 = json.loads(out2.decode())
                    self.assertEqual(resp2["result"]["routed_to"], "mandara")
                    self.assertEqual(resp2["result"]["cmd"], ["mandara", "lock"])

                    store.set_presentation("toasts", "lucid")
                    reader, writer = await asyncio.open_unix_connection(str(sock))
                    writer.write(b'{"jsonrpc":"2.0","id":7,"method":"toast.emit","params":{"title":"Hello","body":"M3 Toast"}}\n')
                    await writer.drain()
                    line = await reader.readline()
                    writer.close()
                    await writer.wait_closed()
                    t_resp = json.loads(line.decode())
                    self.assertEqual(t_resp["result"]["routed_to"], "lucid")
                finally:
                    await srv.stop()

        asyncio.run(run_ipc())


if __name__ == "__main__":
    unittest.main(verbosity=2)
