import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class HeadlessToggleTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.config_path = self.base_dir / "config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_config(self, eco_mode):
        self.config_path.write_text(
            json.dumps({"eco_mode": eco_mode}), encoding="utf-8"
        )

    def test_launch_toggles_off_to_on_and_saves_state(self):
        self.write_config(False)

        with patch("main.get_base_dir", return_value=self.base_dir), patch(
            "main.run_energy_toggle", return_value=(True, "")
        ) as toggle:
            exit_code = main.main()

        self.assertEqual(exit_code, 0)
        toggle.assert_called_once_with(True)
        self.assertTrue(json.loads(self.config_path.read_text(encoding="utf-8"))["eco_mode"])

    def test_second_launch_toggles_on_to_off_and_saves_state(self):
        self.write_config(True)

        with patch("main.get_base_dir", return_value=self.base_dir), patch(
            "main.run_energy_toggle", return_value=(True, "")
        ) as toggle:
            exit_code = main.main()

        self.assertEqual(exit_code, 0)
        toggle.assert_called_once_with(False)
        self.assertFalse(json.loads(self.config_path.read_text(encoding="utf-8"))["eco_mode"])

    def test_failed_toggle_keeps_saved_state_and_returns_failure(self):
        self.write_config(False)

        with patch("main.get_base_dir", return_value=self.base_dir), patch(
            "main.run_energy_toggle", return_value=(False, "Timed out")
        ) as toggle:
            exit_code = main.main()

        self.assertEqual(exit_code, 1)
        toggle.assert_called_once_with(True)
        self.assertFalse(json.loads(self.config_path.read_text(encoding="utf-8"))["eco_mode"])


if __name__ == "__main__":
    unittest.main()
