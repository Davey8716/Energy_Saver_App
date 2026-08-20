import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_energy_saver


class AhkResourceTests(unittest.TestCase):
    def test_exe_builder_script_matches_active_script(self):
        project_root = Path(__file__).parents[1]
        active_script = (project_root / "EnergySaver.ahk").read_text(encoding="utf-8")
        builder_script = (project_root / "Icons" / "EnergySaver.ahk").read_text(
            encoding="utf-8"
        )

        self.assertEqual(builder_script, active_script)


class RunEnergyToggleTests(unittest.TestCase):
    def setUp(self):
        self.ahk_path = Path("C:/Tools/AutoHotkey/v2/AutoHotkey64.exe")
        self.script_path = Path("C:/Tools/EnergySaver.ahk")

    @patch("run_energy_saver.subprocess.run")
    @patch("run_energy_saver.Path.exists", return_value=True)
    def test_returns_success_only_after_automation_exits_cleanly(self, _exists, run):
        run.return_value = subprocess.CompletedProcess([], 0, "", "")
        with patch.object(run_energy_saver, "ahk_exe", self.ahk_path), patch.object(
            run_energy_saver, "script", self.script_path
        ):
            success, message = run_energy_saver.run_energy_toggle()

        self.assertTrue(success)
        self.assertEqual(message, "")
        run.assert_called_once_with(
            [str(self.ahk_path), str(self.script_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

    @patch("run_energy_saver.subprocess.run")
    @patch("run_energy_saver.Path.exists", return_value=True)
    def test_returns_failure_when_quick_settings_is_not_ready(self, _exists, run):
        run.return_value = subprocess.CompletedProcess([], 1, "", "timed out")
        with patch.object(run_energy_saver, "ahk_exe", self.ahk_path), patch.object(
            run_energy_saver, "script", self.script_path
        ):
            success, message = run_energy_saver.run_energy_toggle()

        self.assertFalse(success)
        self.assertIn("not changed", message)
        self.assertIn("timed out", message)

    @patch("run_energy_saver.subprocess.run", side_effect=OSError("launch failed"))
    @patch("run_energy_saver.Path.exists", return_value=True)
    def test_returns_failure_when_automation_cannot_start(self, _exists, _run):
        with patch.object(run_energy_saver, "ahk_exe", self.ahk_path), patch.object(
            run_energy_saver, "script", self.script_path
        ):
            success, message = run_energy_saver.run_energy_toggle()

        self.assertFalse(success)
        self.assertIn("Could not start", message)
        self.assertIn("launch failed", message)


class MissingDependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.ahk_exe = self.base_dir / "AutoHotkey" / "v2" / "AutoHotkey64.exe"
        self.ahk_script = self.base_dir / "EnergySaver.ahk"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_reports_missing_autohotkey_only(self):
        self.ahk_script.touch()

        with patch.object(run_energy_saver, "ahk_exe", None), patch.object(
            run_energy_saver, "find_ahk_exe", return_value=None
        ), patch.object(run_energy_saver, "script", self.ahk_script):
            success, message = run_energy_saver.run_energy_toggle()

        self.assertFalse(success)
        self.assertIn("AutoHotkey v2 could not be found", message)
        self.assertNotIn("EnergySaver.ahk could not be found", message)

    def test_reports_missing_sidecar_with_expected_path(self):
        self.ahk_exe.parent.mkdir(parents=True)
        self.ahk_exe.touch()

        with patch.object(run_energy_saver, "ahk_exe", self.ahk_exe), patch.object(
            run_energy_saver, "script", self.ahk_script
        ):
            success, message = run_energy_saver.run_energy_toggle()

        self.assertFalse(success)
        self.assertNotIn("AutoHotkey v2 could not be found", message)
        self.assertIn("EnergySaver.ahk could not be found", message)
        self.assertIn(str(self.ahk_script), message)
        self.assertIn("same folder", message)

    def test_reports_both_missing_dependencies_together(self):
        with patch.object(run_energy_saver, "ahk_exe", None), patch.object(
            run_energy_saver, "find_ahk_exe", return_value=None
        ), patch.object(run_energy_saver, "script", self.ahk_script):
            success, message = run_energy_saver.run_energy_toggle()

        self.assertFalse(success)
        self.assertIn("AutoHotkey v2 could not be found", message)
        self.assertIn("EnergySaver.ahk could not be found", message)
        self.assertIn(str(self.ahk_script), message)


class FindAhkExeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.ahk_path = self.base_dir / "AutoHotkey" / "v2" / "AutoHotkey64.exe"
        self.ahk_path.parent.mkdir(parents=True)
        self.ahk_path.touch()
        self.config_path = self.base_dir / "config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def read_config(self):
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def test_cached_path_migration_removes_saved_eco_mode(self):
        self.config_path.write_text(
            json.dumps({"eco_mode": True, "ahk_exe": str(self.ahk_path)}),
            encoding="utf-8",
        )

        with patch.object(run_energy_saver, "config_path", self.config_path):
            result = run_energy_saver.find_ahk_exe()

        self.assertEqual(result, self.ahk_path)
        self.assertEqual(self.read_config(), {"ahk_exe": str(self.ahk_path)})

    def test_discovered_path_is_the_only_saved_configuration(self):
        self.config_path.write_text(
            json.dumps({"eco_mode": False, "unused": "value"}), encoding="utf-8"
        )

        with patch.object(
            run_energy_saver, "config_path", self.config_path
        ), patch.object(
            run_energy_saver, "ahk_v2_candidates", return_value=[self.ahk_path]
        ):
            result = run_energy_saver.find_ahk_exe()

        self.assertEqual(result, self.ahk_path.resolve())
        self.assertEqual(
            self.read_config(), {"ahk_exe": str(self.ahk_path.resolve())}
        )

    def test_cache_write_failure_does_not_hide_a_valid_cached_path(self):
        config = {"eco_mode": True, "ahk_exe": str(self.ahk_path)}

        with patch.object(
            run_energy_saver, "load_config", return_value=config
        ), patch.object(
            run_energy_saver, "save_config", side_effect=OSError("read only")
        ):
            result = run_energy_saver.find_ahk_exe()

        self.assertEqual(result, self.ahk_path)


if __name__ == "__main__":
    unittest.main()
