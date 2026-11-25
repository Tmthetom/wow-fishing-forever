# Contributing

## Setup

Install [uv](https://docs.astral.sh/uv/) and optionally [just](https://github.com/casey/just).

    uv sync --group dev
    uv run pre-commit install   # optional: ruff on every commit

## Everyday commands

| just | without just |
|---|---|
| `just test` | `uv run pytest` |
| `just lint` | `uv run ruff check . && uv run ruff format --check .` |
| `just fmt` | `uv run ruff check --fix . && uv run ruff format .` |
| `just build` | `uv run pyinstaller --clean --noconfirm packaging/wowfish.spec` |
| `just smoke` | run the built executable: `--version`, `doctor`, `listen --list`, `calibrate` on the fixture |

Unit tests never touch the network, the display, or audio hardware: `soundcard`, `mss`, and
`Xlib` are imported lazily and the tests stub them. The X11 capture tests run only when
`DISPLAY` is set. Set `WOWFISH_HOME` to redirect config, cache, and logs; the test suite does
this automatically.

## Layout

    src/wowfish/
      cli.py        typer app; registers the commands below
      commands/     calibrate, watch, listen, verify-bite, run, gui (one module each)
      config.py     TOML config: defaults, validation, save; adds new settings to old files at launch
      paths.py      config / cache / log locations (WOWFISH_HOME override)
      doctor.py     environment probes
      assets/       interact-icon sprites (PNG) and splash clips (WAV) shipped in the package
      vision/       templates, regions, masked matcher, acquire/track search, calibration, annotate
      audio/        WAV I/O, log-mel features, fingerprints, bite detector, loopback devices
      capture/      window lookup and capture: X11 (ctypes XGetImage), Hyprland (IPC + grim),
                    Windows (user32 + mss), macOS (CoreGraphics window list + mss), stub
      input/        key presses: XTest (python-xlib) or a Wayland virtual keyboard on Linux,
                    SendInput on Windows, Quartz events on macOS, stub elsewhere
      engine/       the fishing loop: states, events, FishingEngine (injectable collaborators),
                    optional behavior variations, thread
      gui/          Tk-free Presenter (engine thread + setup workers), ttkbootstrap window and pages
    scripts/        release preflight, clip conversion (ffmpeg, dev only)
    packaging/      PyInstaller spec (console `wowfish` and windowed `wowfish-gui`)
    tests/          unit tests, synthetic frame/audio helpers, tests/fixtures/

## Branches and releases

Follow the approval and publication conventions in [AGENTS.md](AGENTS.md). `main` is this
fork's publication branch. The tagged stable builds and recovery instructions are in
[STABLE.md](STABLE.md).

1. Run the relevant checks before publishing the release commit. For a user-facing change,
   confirm the user's approval and record which behavior was verified in the game.
2. Update the stable release links in README and STABLE, preserving earlier recovery points.
   Publish the approved commit through GitHub MCP and verify the remote branch head.
3. Create the GitHub Release from that exact commit using a `v`-prefixed version such as
   `v1.2.1`. Use a patch version for small fixes and a minor version for new functionality.
   Verify that GitHub marks the approved release as **Latest** and shows the expected commit.

Hatch-vcs derives the installed version from Git tags. A tagged checkout gets the tag's
version and intervening commits get a development version. Check it with `wowfish --version`.

The [release workflow](.github/workflows/release.yml) is configured to build executables and
attach them to a draft for version tags when the workflow runs successfully. Check the actual
release assets before advertising a compiled download. GitHub also provides source archives.

## Updating the bundled clips or sprites

The splash clips are converted once from the game's Vorbis files with
`uv run python scripts/convert_clips.py <dir-with-ogg-files>` (needs `ffmpeg`) and committed
as 16-bit mono 22050 Hz WAV. The gear sprites are cropped from the client's 2x crosshair
sheet. Neither step runs at install or build time.

## Pull requests

CI runs lint, unit tests, and a PyInstaller smoke build on Linux, Windows, and macOS. Keep
PRs green on all three. Add tests for behavior changes.
