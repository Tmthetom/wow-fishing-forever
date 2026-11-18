"""Test the Windows launcher without opening a GUI or sending game input."""

import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def launcher(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[1] / "scripts" / "river_desk.py"
    module = runpy.run_path(str(script))
    interpreter = tmp_path / "pythonw.exe"
    interpreter.write_bytes(b"test interpreter")
    monkeypatch.setattr(module["sys"], "executable", str(interpreter))
    monkeypatch.setenv("WOWFISH_HOME", str(tmp_path / "state"))
    return module, interpreter


def test_each_launch_has_matching_unique_names_and_cleans_up(launcher, monkeypatch):
    module, interpreter = launcher
    names = []

    def run(args, *, env, check):
        executable = Path(args[0])
        assert executable.read_bytes() == interpreter.read_bytes()
        assert executable.parent == interpreter.parent
        assert args[1] == "-I" and args[-1] == "--gui-child"
        assert env["WOWFISH_WINDOW_TITLE"] == executable.stem
        assert env["WOWFISH_HOME"] == str(interpreter.parent / "state")
        names.append(executable)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(module["subprocess"], "run", run)
    for _ in range(2):
        assert module["launch_randomized"]() == 0
    assert names[0] != names[1]
    assert all(not path.exists() for path in names)
    assert interpreter.exists()


def test_failed_start_removes_temporary_executable(launcher, monkeypatch):
    module, interpreter = launcher

    def fail(*args, **kwargs):
        raise OSError("cannot start")

    monkeypatch.setattr(module["subprocess"], "run", fail)
    with pytest.raises(OSError, match="cannot start"):
        module["launch_randomized"]()
    assert list(interpreter.parent.glob("*.exe")) == [interpreter]
