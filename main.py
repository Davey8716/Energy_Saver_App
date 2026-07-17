"""Headless launcher for toggling Windows Energy Saver.

Each invocation switches to the opposite of the last successfully saved mode
and exits when the AutoHotkey automation finishes.
"""

from state_management import get_base_dir, load_config, save_config
from run_energy_saver import run_energy_toggle


def main() -> int:
    """Toggle Energy Saver once and return a process exit code."""
    config_path = (get_base_dir().resolve() / "config.json").resolve()
    config = load_config(config_path)
    target_eco_mode = not bool(config.get("eco_mode", False))

    success, _message = run_energy_toggle(target_eco_mode)
    if not success:
        return 1

    config["eco_mode"] = target_eco_mode
    try:
        save_config(config_path, config)
    except OSError:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
