"""A new fishing run reuses the lure timer without sending real game input."""

from dataclasses import replace

from test_wowfish import _Pond
from wowfish.config import AudioConfig, Config, GameConfig, VisionConfig
from wowfish.engine.engine import FishingEngine, LureState
from wowfish.gui.presenter import Presenter


def engine(pond, state, key="'", sleep=None):
    return FishingEngine(
        Config(GameConfig(lure_key=key, lure_minutes=10), VisionConfig(), AudioConfig()),
        pond.window,
        capturer=pond,
        input_device=pond,
        audio_source=pond,
        detector=pond,
        matcher=pond,
        clock=pond.clock,
        sleep=sleep or pond.sleep,
        lure_state=state,
    )


def test_restart_reuses_timer_and_renews_only_after_expiry():
    pond, state = _Pond(), LureState()
    first = engine(pond, state)
    first.step()
    assert [p[1] for p in pond.pressed] == ["'"]
    applied = state.applied_at
    assert applied is not None
    first.stop()
    pond.t = applied + 120
    second = engine(pond, state)
    second.step()
    assert [p[1] for p in pond.pressed] == ["'", "1"]
    second.stop()
    pond.t = applied + 601
    third = engine(pond, state)
    third.step()
    assert [p[1] for p in pond.pressed] == ["'", "1", "'"]


def test_interrupted_application_is_not_remembered():
    pond, state = _Pond(), LureState()

    def stop_during_wait(seconds):
        pond.sleep(seconds)
        first.stop()

    first = engine(pond, state, sleep=stop_during_wait)
    first.step()
    assert state.applied_at is None
    engine(pond, state).step()
    assert [p[1] for p in pond.pressed] == ["'", "'"]


def test_changed_macro_or_game_and_new_app_reset_timer():
    pond, state = _Pond(), LureState()
    engine(pond, state).step()
    engine(pond, state, key="f2").step()
    assert pond.pressed[-1][1] == "f2"
    pond.window = replace(pond.window, pid=123)
    engine(pond, state, key="f2").step()
    assert [p[1] for p in pond.pressed] == ["'", "f2", "f2"]
    engine(pond, LureState(), key="f2").step()
    assert len(pond.pressed) == 4


def test_presenter_passes_same_state_after_thread_is_gone(tmp_path, monkeypatch):
    monkeypatch.setenv("WOWFISH_HOME", str(tmp_path))
    states = []

    def build(cfg, *, session_s, lure_state):
        states.append(lure_state)
        raise RuntimeError("no real game in test")

    p = Presenter(build_engine=build)
    p.start()
    p.start()
    assert states[0] is states[1]
