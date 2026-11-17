"""Run the GUI from source using the project's local Windows interpreter."""

import runpy
import site
import sys
from pathlib import Path

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    site.addsitedir(str(root / ".venv" / "Lib" / "site-packages"))
    sys.argv[:] = ["river-desk", "gui"]
    runpy.run_module("wowfish", run_name="__main__", alter_sys=True)
