import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import run_energy_saver


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
            success, message = run_energy_saver.run_energy_toggle(True)

        self.assertTrue(success)
        self.assertEqual(message, "")
        run.assert_called_once_with(
            [str(self.ahk_path), str(self.script_path), "1"],
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
            success, message = run_energy_saver.run_energy_toggle(False)

        self.assertFalse(success)
        self.assertIn("not changed", message)
        self.assertIn("timed out", message)


if __name__ == "__main__":
    unittest.main()
