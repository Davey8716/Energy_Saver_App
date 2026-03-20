
import subprocess 
from state_management import base_dir
from pathlib import Path

script = (base_dir / "EnergySaver.ahk").resolve()
ahk_exe = Path(r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe")

def run_energy_toggle(eco_mode: bool):
    if not ahk_exe.exists():
        print("AutoHotkey executable not found.")
        return

    if not script.exists():
        print("AHK script not found.")
        return

    try:
        # Kill any existing AHK instance (prevents silent ignore)
        subprocess.call(
            ["taskkill", "/f", "/im", "AutoHotkey64.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        subprocess.Popen(
            [
                str(ahk_exe),
                str(script),
                "1" if eco_mode else "0"
            ]
        )

    except Exception as e:
        print(f"Failed to launch script: {e}")