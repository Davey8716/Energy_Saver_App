
import os
import subprocess
from pathlib import Path
from shutil import which

from state_management import base_dir, load_config, save_config

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


def save_cached_ahk_path(exe_path):
    """Best-effort persistence of the only supported configuration value."""
    config = {"ahk_exe": str(exe_path)} if exe_path is not None else {}
    try:
        save_config(config_path, config)
    except OSError:
        pass


def find_ahk_exe():
    config = load_config(config_path)
    cached_path = config.get("ahk_exe")
    if isinstance(cached_path, str) and cached_path:
        cached_exe = Path(cached_path)
        if cached_exe.exists() and is_ahk_v2_path(cached_exe):
            if config != {"ahk_exe": cached_path}:
                save_cached_ahk_path(cached_exe)
            return cached_exe

    for exe_path in existing_paths(ahk_v2_candidates()):
        save_cached_ahk_path(exe_path)
        return exe_path

    if winreg is None:
        if config:
            save_cached_ahk_path(None)
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
        save_cached_ahk_path(exe_path)
        return exe_path

    if config:
        save_cached_ahk_path(None)
    return None


def run_energy_toggle():
    """Run the Quick Settings automation and return ``(success, message)``.

    AutoHotkey does the UI work, so its exit code tells the caller whether the
    automation completed successfully.
    """
    global ahk_exe

    if ahk_exe is None:
        ahk_exe = find_ahk_exe()

    missing_dependencies = []
    if ahk_exe is None or not ahk_exe.exists():
        missing_dependencies.append(
            "AutoHotkey v2 could not be found. Install AutoHotkey v2, then run "
            "Energy Saver again."
        )

    if not script.exists():
        missing_dependencies.append(
            "EnergySaver.ahk could not be found.\n\n"
            f"Expected location:\n{script}\n\n"
            "Keep EnergySaver.ahk in the same folder as the Energy Saver application."
        )

    if missing_dependencies:
        return False, "\n\n".join(missing_dependencies)

    try:
        result = subprocess.run(
            [
                str(ahk_exe),
                str(script),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return True, ""

        details = (result.stderr or result.stdout or "").strip()
        message = "Quick Settings was not ready, so Energy Saver was not changed."
        if details:
            message = f"{message}\n\n{details}"
        return False, message

    except Exception as e:
        return False, f"Could not start the Energy Saver automation: {e}"
