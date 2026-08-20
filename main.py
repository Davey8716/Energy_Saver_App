"""Headless launcher for toggling Windows Energy Saver once per invocation."""

import ctypes

from run_energy_saver import run_energy_toggle


def show_error_dialog(message: str) -> None:
    """Display a native Windows error dialog, falling back to console output."""
    try:
        ctypes.windll.user32.MessageBoxW(
            None,
            message,
            "Energy Saver Error",
            0x10,  # MB_OK | MB_ICONERROR
        )
    except Exception:
        try:
            print(f"Energy Saver Error: {message}")
        except Exception:
            pass


def main() -> int:
    """Toggle Energy Saver once and return a process exit code."""
    try:
        success, message = run_energy_toggle()
    except Exception as error:
        success = False
        message = f"Energy Saver could not start.\n\n{error}"

    if success:
        return 0

    show_error_dialog(message or "Energy Saver could not be changed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
