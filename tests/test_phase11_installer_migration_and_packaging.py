import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = str(ROOT / "install.sh")


class TestPhase11InstallerMigrationAndPackaging(unittest.TestCase):
    def test_01_dry_run_leaves_target_home_completely_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            out = subprocess.check_output([INSTALL_SH, "--dry-run", "--with-hypr", "--home", str(home)], text=True)
            self.assertIn("[DRY-RUN]", out)
            self.assertEqual(list(home.iterdir()), [])

    def test_02_install_migrates_standalone_lucid_and_mandara_configs_and_uninstalls_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".config" / "lucid").mkdir(parents=True)
            (home / ".config" / "lucid" / "settings.json").write_text(json.dumps({"barHeight": 46, "themeColour": "#FF6B8B"}))
            (home / ".config" / "mandara").mkdir(parents=True)
            (home / ".config" / "mandara" / "config.toml").write_text("[bar]\nheight = 42\n")
            (home / ".config" / "hypr").mkdir(parents=True)
            (home / ".config" / "hypr" / "hyprland.conf").write_text("# User Hyprland Config\nmonitor=,preferred,auto,1\n")

            out = subprocess.check_output([INSTALL_SH, "--profile", "full", "--with-hypr", "--skip-engine-build", "--home", str(home)], text=True)
            self.assertIn("Migrated standalone keys: Lucid=2, Mandara=1", out)

            installed_cli = home / ".local" / "bin" / "scy-shell"
            self.assertTrue(installed_cli.exists())
            bh = json.loads(subprocess.check_output([str(installed_cli), "--home", str(home), "config", "get", "scy.providers.lucid.prefs.barHeight"], text=True))
            mbh = json.loads(subprocess.check_output([str(installed_cli), "--home", str(home), "config", "get", "scy.providers.mandara.config.bar.height"], text=True))
            self.assertEqual(bh, 46)
            self.assertEqual(mbh, 42)

            hconf = (home / ".config" / "hypr" / "hyprland.conf").read_text()
            self.assertIn("# User Hyprland Config", hconf)
            self.assertIn("source = ~/.config/hypr/scy-shell/scy-shell.conf", hconf)

            subprocess.check_call([INSTALL_SH, "--uninstall", "--home", str(home)], stdout=subprocess.DEVNULL)
            self.assertFalse(installed_cli.exists())
            hconf_after = (home / ".config" / "hypr" / "hyprland.conf").read_text()
            self.assertIn("# User Hyprland Config", hconf_after)
            self.assertNotIn("scy-shell.conf", hconf_after)
            self.assertTrue((home / ".local" / "share" / "scy-shell" / "backups").exists())

    def test_03_pkgbuild_and_systemd_units_valid(self):
        pkgb = (ROOT / "packaging" / "arch" / "PKGBUILD").read_text(encoding="utf-8")
        self.assertIn("pkgname=scy-shell", pkgb)
        self.assertIn("'hyprland>=0.57.0'", pkgb)
        self.assertIn("cargo build --release", pkgb)
        for unit in ["scy-daemon.service", "scy-lucid.service", "scy-mandara.service"]:
            p = ROOT / "packaging" / "systemd" / unit
            self.assertTrue(p.exists())
            self.assertIn("[Service]", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
