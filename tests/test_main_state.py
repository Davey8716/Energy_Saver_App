import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox

import main


class MainStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        Path(self.temp_dir.name, "config.json").write_text(
            json.dumps({"eco_mode": False}), encoding="utf-8"
        )
        self.base_dir = Path(self.temp_dir.name)
        with patch("main.get_base_dir", return_value=self.base_dir):
            self.window = main.windows11energysaverswitch()

    def tearDown(self):
        self.window.server.close()
        self.window.deleteLater()
        self.temp_dir.cleanup()

    def test_failed_switch_restores_confirmed_mode_without_saving(self):
        self.window.pending_eco = True
        self.window.button.blockSignals(True)
        self.window.button.setChecked(True)
        self.window.button.blockSignals(False)

        with patch("main.save_config") as save, patch.object(QMessageBox, "warning"):
            self.window.on_toggle_complete(False, "Quick Settings timed out")

        save.assert_not_called()
        self.assertFalse(self.window.button.isChecked())
        self.assertFalse(self.window.config["eco_mode"])

    def test_successful_switch_saves_confirmed_mode_then_quits(self):
        self.window.pending_eco = True
        self.window.button.blockSignals(True)
        self.window.button.setChecked(True)
        self.window.button.blockSignals(False)

        with patch("main.save_config") as save, patch.object(
            QApplication.instance(), "quit"
        ) as quit_app:
            self.window.on_toggle_complete(True, "")

        save.assert_called_once_with(self.window.config_path, self.window.config)
        self.assertTrue(self.window.config["eco_mode"])
        quit_app.assert_called_once()


if __name__ == "__main__":
    unittest.main()
