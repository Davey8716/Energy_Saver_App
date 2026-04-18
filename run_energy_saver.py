
import subprocess 
import os
from state_management import base_dir, load_config, save_config
from pathlib import Path
from shutil import which

try:
    import winreg
except ImportError:
    winreg = None

script = (base_dir / "EnergySaver.ahk").resolve()
config_path = (base_dir / "config.json").resolve()
ahk_exe = None

def is_ahk_v2_path(exe_path):
    return any(part.lower().startswith("v2") for part in exe_path.parts)

def existing_paths(paths):
    seen = set()
    for path in paths:
        if path is None:
            continue

        exe_path = Path(path).resolve()
        if exe_path in seen or not exe_path.exists():
            continue

        seen.add(exe_path)
        yield exe_path

def ahk_install_dirs():
    for env_name in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)", "LocalAppData"):
        base_path = os.environ.get(env_name)
        if base_path:
            yield Path(base_path) / "AutoHotkey"

def ahk_v2_candidates():
    for exe_name in ("AutoHotkey64.exe", "AutoHotkey.exe"):
        exe_path = which(exe_name)
        if exe_path and is_ahk_v2_path(Path(exe_path)):
            yield exe_path

    for install_dir in ahk_install_dirs():
        yield install_dir / "v2" / "AutoHotkey64.exe"
        yield install_dir / "v2" / "AutoHotkey.exe"

        for version_dir in install_dir.glob("v2*"):
            yield version_dir / "AutoHotkey64.exe"
            yield version_dir / "AutoHotkey.exe"

def find_ahk_exe():
    config = load_config(config_path)
    cached_path = config.get("ahk_exe")
    if cached_path:
        cached_exe = Path(cached_path)
        if cached_exe.exists() and is_ahk_v2_path(cached_exe):
            return cached_exe

    for exe_path in existing_paths(ahk_v2_candidates()):
        config["ahk_exe"] = str(exe_path)
        save_config(config_path, config)
        return exe_path

    if winreg is None:
        return None

    app_paths_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
    registry_candidates = []
    for root_key in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for exe_name in ("AutoHotkey64.exe", "AutoHotkey.exe"):
            try:
                with winreg.OpenKey(root_key, fr"{app_paths_key}\{exe_name}") as key:
                    exe_path, _ = winreg.QueryValueEx(key, "")
                    if is_ahk_v2_path(Path(exe_path)):
                        registry_candidates.append(exe_path)
            except OSError:
                pass

    for exe_path in existing_paths(registry_candidates):
        config["ahk_exe"] = str(exe_path)
        save_config(config_path, config)
        return exe_path

    return None

def run_energy_toggle(eco_mode: bool):
    global ahk_exe

    if ahk_exe is None:
        ahk_exe = find_ahk_exe()

    if ahk_exe is None or not ahk_exe.exists():
        print("AutoHotkey executable not found.")
        return

    if not script.exists():
        print("AHK script not found.")
        return

    try:
        subprocess.Popen(
            [
                str(ahk_exe),
                str(script),
                "1" if eco_mode else "0"
            ]
        )

    except Exception as e:
        print(f"Failed to launch script: {e}")

