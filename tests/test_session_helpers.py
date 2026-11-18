"""Session helpers never send real input in these tests."""

import ctypes
from types import SimpleNamespace

import pytest

from test_wowfish import _fish, _Pond
from wowfish.capture import WindowRef
from wowfish.config import AudioConfig, BehaviorConfig, Config, GameConfig, VisionConfig
from wowfish.engine.engine import FishingEngine
from wowfish.engine.state import State
from wowfish.input._win32 import Win32InputDevice


class FocusPond(_Pond):
    def __init__(self, succeeds=True):
        super().__init__()
        self.focused = False
        self.succeeds = succeeds
        self.focus_calls = []

    def focus_game(self, window):
        self.focus_calls.append(self.t)
        self.focused = self.succeeds
        return self.succeeds


def test_focus_recovery_is_opt_in_and_rate_limited():
    pond, _ = _fish(BehaviorConfig(), 2, pond=FocusPond())
    assert not pond.focus_calls and not pond.pressed
    pond, _ = _fish(BehaviorConfig(focus_check_minutes=1), 2.1, pond=FocusPond(False))
    assert len(pond.focus_calls) == 2
    assert pond.focus_calls[0] >= 60
    assert pond.focus_calls[1] - pond.focus_calls[0] >= 60
    assert not pond.pressed


def test_successful_recovery_resumes_fishing():
    pond, _ = _fish(BehaviorConfig(focus_check_minutes=1), 1.1, pond=FocusPond())
    assert len(pond.focus_calls) == 1
    assert pond.pressed and pond.pressed[0][1] == "1"
    assert pond.pressed[0][0] >= 60


def test_periodic_jump_waits_for_cast_to_finish_and_landing():
    pond, _ = _fish(BehaviorConfig(jump_every_minutes=0.1), 0.6, pond=_Pond(bite_after_s=8))
    jumps = [(i, p) for i, p in enumerate(pond.pressed) if p[1] == "space"]
    assert jumps
    for i, (t, _, _) in jumps:
        assert t >= 6
        assert pond.pressed[i - 1][1] == "f"  # fish was reeled in first
        if i + 1 < len(pond.pressed):
            assert pond.pressed[i + 1][1] == "1"
            assert pond.pressed[i + 1][0] - t >= 1


def test_stop_prevents_due_focus_and_jump():
    pond = FocusPond()
    cfg = Config(
        GameConfig(),
        VisionConfig(),
        AudioConfig(),
        behavior=BehaviorConfig(focus_check_minutes=1, jump_every_minutes=1),
    )
    engine = FishingEngine(
        cfg,
        pond.window,
        capturer=pond,
        input_device=pond,
        audio_source=pond,
        detector=pond,
        matcher=pond,
        clock=pond.clock,
        sleep=pond.sleep,
    )
    engine.step()
    pond.t = 61
    engine.stop()
    engine.step()
    assert engine.state == State.STOPPED
    assert not pond.focus_calls and not pond.pressed


@pytest.mark.parametrize("actual_pid,expected", [(42, True), (99, False)])
def test_windows_focus_checks_process_identity(actual_pid, expected):
    calls = []

    def pid_for_window(hwnd, pointer):
        ctypes.cast(pointer, ctypes.POINTER(ctypes.wintypes.DWORD))[0] = actual_pid

    device = Win32InputDevice.__new__(Win32InputDevice)
    device._u = SimpleNamespace(
        IsWindow=lambda hwnd: True,
        IsIconic=lambda hwnd: True,
        GetWindowThreadProcessId=pid_for_window,
        ShowWindowAsync=lambda hwnd, mode: calls.append(("restore", hwnd, mode)),
        SetForegroundWindow=lambda hwnd: calls.append(("focus", hwnd)) or True,
    )
    window = WindowRef("World of Warcraft", 42, 0, 0, 10, 10, handle=123)
    assert device.focus_game(window) is expected
    assert bool(calls) is expected
    if expected:
        assert calls == [("restore", 123, 9), ("focus", 123)]
