# Instructions for Codex

This is a Windows fork of [WoW Fishing Forever](https://github.com/rsamf/wow-fishing-forever), licensed under MIT. Work from the repository root. Keep user-facing instructions in concise English and consistent with [README.md](README.md).

## Install on Windows x64

If `uv` is unavailable, download `uv-x86_64-pc-windows-msvc.zip` from the official [Astral uv releases](https://github.com/astral-sh/uv/releases/latest) and extract `uv.exe` into `.local/uv`. Run in PowerShell:

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.local\cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PWD '.local\python'
$env:UV_NO_REGISTRY = '1'
.\.local\uv\uv.exe sync --locked --python 3.13 --managed-python --no-dev
.\RiverDesk.cmd doctor
```

Use `uv` instead of `.\.local\uv\uv.exe` if it is already on PATH. Launch `.\RiverDesk.cmd` and verify that the GUI opens. Missing game warnings are expected when WoW is closed; diagnostics and GUI startup are sufficient to check installation.

## Preserve local settings

- Read `.local/state/config/config.toml` before making changes. Preserve working keys, calibration, and all unrelated values. Copy this file directly when transferring settings between PCs.
- The working setup uses **Cast key** `[`, **Interact key** `]`, and **Lure key** `'` (a single apostrophe). The corresponding Czech WoW fishing and interaction bindings are `ú` and `)`. The lure key triggers the Bright Baubles macro documented in README; verify its physical key in WoW.
- `config/forever-working.toml` is the user's approved configuration snapshot. For a new installation, copy it to `.local/state/config/config.toml` before opening the GUI. For an existing installation, preserve its settings unless the user requests replacement. Recalibrate for the current display; the snapshot's detection settings are not universal defaults.
- Keep `.local/`, `.venv/`, logs, and machine-specific shortcuts out of Git.
- The launcher is `RiverDesk.cmd`, its Python entry point is `scripts/river_desk.py`, and key mappings are in `src/wowfish/input/keys.py`.

## Session workflow

Always include these steps when explaining startup:

1. Prepare the game settings and icon commands listed in README.
2. Calibrate and save the gear icon before every session. Move River Desk to the side so it cannot cover the bobber or icon; minimizing alone may not be enough.
3. Catch the first fish manually. Several manual catches may be needed before detection works reliably.
4. Start the bot, minimize the app after positioning it to the side, and keep WoW in the foreground.
5. After stopping, restore the game settings changed for the session; keep the key bindings.
