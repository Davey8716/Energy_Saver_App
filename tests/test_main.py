import unittest
from unittest.mock import patch

import main


class StatelessToggleTests(unittest.TestCase):
    def test_successful_toggle_returns_success(self):
        with patch("main.run_energy_toggle", return_value=(True, "")) as toggle, patch(
            "main.show_error_dialog"
        ) as show_error:
            exit_code = main.main()

        self.assertEqual(exit_code, 0)
        toggle.assert_called_once_with()
        show_error.assert_not_called()

    def test_failed_toggle_returns_failure(self):
        with patch(
            "main.run_energy_toggle", return_value=(False, "Timed out")
        ) as toggle, patch("main.show_error_dialog") as show_error:
            exit_code = main.main()

        self.assertEqual(exit_code, 1)
        toggle.assert_called_once_with()
        show_error.assert_called_once_with("Timed out")

    def test_failure_without_details_uses_a_fallback_message(self):
        with patch("main.run_energy_toggle", return_value=(False, "")), patch(
            "main.show_error_dialog"
        ) as show_error:
            exit_code = main.main()

        self.assertEqual(exit_code, 1)
        show_error.assert_called_once_with("Energy Saver could not be changed.")

    def test_unexpected_launcher_error_is_displayed(self):
        with patch(
            "main.run_energy_toggle", side_effect=OSError("unexpected failure")
        ), patch("main.show_error_dialog") as show_error:
            exit_code = main.main()

        self.assertEqual(exit_code, 1)
        show_error.assert_called_once_with(
            "Energy Saver could not start.\n\nunexpected failure"
        )


class ErrorDialogTests(unittest.TestCase):
    def test_uses_native_windows_error_dialog(self):
        with patch.object(
            main.ctypes.windll.user32, "MessageBoxW"
        ) as message_box:
            main.show_error_dialog("Something went wrong")

        message_box.assert_called_once_with(
            None,
            "Something went wrong",
            "Energy Saver Error",
            0x10,
        )

    def test_prints_message_if_native_dialog_fails(self):
        with patch.object(
            main.ctypes.windll.user32,
            "MessageBoxW",
            side_effect=OSError("dialog unavailable"),
        ), patch("builtins.print") as print_message:
            main.show_error_dialog("Something went wrong")

        print_message.assert_called_once_with(
            "Energy Saver Error: Something went wrong"
        )

    def test_does_not_raise_if_dialog_and_console_output_both_fail(self):
        with patch.object(
            main.ctypes.windll.user32,
            "MessageBoxW",
            side_effect=OSError("dialog unavailable"),
        ), patch("builtins.print", side_effect=OSError("console unavailable")):
            main.show_error_dialog("Something went wrong")


if __name__ == "__main__":
    unittest.main()
