"""Run the GUI from source using the project's local Windows interpreter."""

import os
import runpy
import secrets
import shutil
import site
import subprocess
import sys
from pathlib import Path


def launch_randomized() -> int:
    """Keep the Python DLLs beside the copied interpreter; remove it after the GUI exits."""
    name = f"River-{secrets.token_hex(6)}"
    interpreter = Path(sys.executable).resolve()
    executable = interpreter.with_name(f"{name}.exe")
    env = dict(os.environ, WOWFISH_WINDOW_TITLE=name)
    try:
        # Exclusive creation avoids overwriting a file, even in the unlikely event of a collision.
        with executable.open("xb") as target, interpreter.open("rb") as source:
            shutil.copyfileobj(source, target)
    except FileExistsError:
        return launch_randomized()
    try:
        return subprocess.run(
            [str(executable), "-I", str(Path(__file__).resolve()), "--gui-child"],
            env=env,
            check=False,
        ).returncode
    finally:
        executable.unlink(missing_ok=True)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    if "--gui-child" not in sys.argv:
        try:
            raise SystemExit(launch_randomized())
        except Exception:
            import traceback

            log = root / ".local" / "state" / "log" / "launcher-error.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(traceback.format_exc(), encoding="utf-8")
            raise
    site.addsitedir(str(root / ".venv" / "Lib" / "site-packages"))
    sys.argv[:] = ["river-desk", "gui"]
    runpy.run_module("wowfish", run_name="__main__", alter_sys=True)
