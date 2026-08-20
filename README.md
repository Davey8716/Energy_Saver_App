# Energy Saver App

A very simple Windows utility designed to save a few clicks when toggling
Energy Saver. It is intended to be built as a small executable that runs once,
toggles the Energy Saver tile in Quick Settings, and exits.

## Requirements

- Windows with the Energy Saver tile available in Quick Settings
- [AutoHotkey v2](https://www.autohotkey.com/)
- Python 3 when running from source

## Run from source

```powershell
python main.py
```

## Use as an executable

Build `main.py` with your preferred Python-to-EXE tool. Keep
`EnergySaver.ahk` beside the resulting executable:

```text
Energy_Saver_App/
├── Energy_Saver_App.exe
└── EnergySaver.ahk
```

AutoHotkey v2 must remain installed. The app locates it automatically and
caches its installation path in `config.json`.

## How it works

Each launch runs `EnergySaver.ahk`, which opens Windows Quick Settings and uses
keyboard navigation to toggle the Energy Saver tile. The app does not store or
infer the current Energy Saver state; Windows remains the source of truth.

Because the automation relies on the Quick Settings layout and timing, changes
to that layout may require updating the AutoHotkey script.

## License

This project is available under the [MIT License](LICENSE).
