# Instructions for Codex

This is a Windows fork of [WoW Fishing Forever](https://github.com/rsamf/wow-fishing-forever), licensed under MIT. Work from the repository root. Keep user-facing instructions in concise English and consistent with [README.md](README.md).

## Documentation maintenance

- Document every significant feature, behavior change, configuration option, workaround, and known limitation in README as part of the same change. Keep the GUI instructions and this file consistent; use concise, grammatical English.
- Distinguish implemented behavior, automated checks, user-verified behavior, and planned work. Do not describe proposals or untested builds as working releases. Preserve the stable recovery reference.
- A portable Windows x64 ZIP with bundled Python and dependencies is an agreed future sharing option, not an implemented packaging workflow. Prepare it when requested, from a selected commit with clean defaults and license notices; exclude personal state and logs. Verify relocation and startup on a clean PC before calling it portable. Do not distribute the current virtual environment or machine-specific shortcuts as a ready-made package.
- Use the connected GitHub MCP for publishing changes. Do not trigger a separate Git Credential Manager sign-in or use `git push` for this workflow.

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
- The lure timer is shared across GUI Stop/Start runs in the same app, not persisted to disk. Preserve this behavior and document its limits: no buff verification, reset on app restart or lure settings/game window changes, and reopen after switching characters or poles.
- The launcher is `RiverDesk.cmd`, its Python entry point is `scripts/river_desk.py`, and key mappings are in `src/wowfish/input/keys.py`.
- The Windows launcher generates a new `River-<random>` window and executable name on every launch. Keep using `RiverDesk.cmd` or the existing taskbar shortcut through `.local/launch_taskbar.py`; never pin the temporary executable. The helper removes the executable after exit; settings remain in `.local/state`.
- Preserve the immutable recovery reference in STABLE.md. New session helpers are separate from that user-verified baseline: `behavior.focus_check_minutes` and `behavior.jump_every_minutes` default to 0. The user selected 1 and 5 minutes respectively for this PC. Do not replace the stable configuration snapshot with the experimental settings.

## Session workflow

Always include these steps when explaining startup:

1. Prepare the game settings and icon commands listed in README.
2. Calibrate and save the gear icon before every session. Move River Desk to the side so it cannot cover the bobber or icon; minimizing alone may not be enough.
3. Catch a few fish manually at the start of every session, even with Bright Baubles enabled. Several catches may be needed before starting the bot. This is the user's required startup workflow, not sound training.
4. Start the bot, minimize the app after positioning it to the side, and keep WoW in the foreground.
5. After stopping, restore the game settings changed for the session; keep the key bindings.
