"""Regression coverage for calibration blocking acquisition past its deadline."""

import numpy as np
import pytest

from test_wowfish import _Pond
from wowfish.config import AudioConfig, Config, GameConfig, VisionConfig
from wowfish.engine.engine import FishingEngine
from wowfish.engine.state import State
from wowfish.vision import calibrate
from wowfish.vision.matcher import IconMatch
from wowfish.vision.template import load_icon_templates


def make_engine(pond, **kwargs):
    return FishingEngine(
        Config(GameConfig(), VisionConfig(), AudioConfig()),
        pond.window,
        capturer=pond,
        input_device=pond,
        audio_source=pond,
        detector=pond,
        matcher=pond,
        clock=pond.clock,
        sleep=pond.sleep,
        **kwargs,
    )


def test_saved_size_waits_for_icon_without_immediate_calibration():
    pond = _Pond()
    calls = []
    engine = make_engine(pond, calibrate=lambda *a, **kw: calls.append(1))
    engine.step()
    pond.bobber = False  # icon not visible yet
    engine.step()
    assert not calls
    assert engine.state == State.CASTING
    pond.bobber = True
    engine.step()
    assert engine.state == State.WAIT_BITE


def test_slow_match_is_not_accepted_after_deadline():
    pond = _Pond()
    engine = make_engine(pond)
    engine.step()

    def slow_match(*args, **kwargs):
        pond.t += 5
        return IconMatch(0.99, 20, 20, 32, 0.5)

    pond.match = slow_match
    engine.step()
    assert engine.state != State.WAIT_BITE
    assert engine._icon_timeouts == 1


@pytest.mark.parametrize("stop", [False, True])
def test_fallback_honors_deadline_and_stop(stop):
    pond = _Pond()

    def fallback(frame, *, match_width, should_stop):
        while not should_stop():
            pond.t += 0.1
            if stop:
                engine.stop()
        assert pond.t < 4.5  # before the normal pause between casts
        raise calibrate.CalibrationInterrupted

    engine = make_engine(pond, calibrate=fallback)
    engine.step()
    pond.bobber = False
    engine._sweeping = True
    engine.step()
    assert engine._icon_timeouts == (0 if stop else 1)
    assert engine.state != State.WAIT_BITE


def test_calibration_checks_budget_between_matches(monkeypatch):
    calls = []

    def match(self, frame, region=None):
        calls.append(1)
        return IconMatch(0.9, 30, 30, 32, 0.5)

    monkeypatch.setattr(calibrate.IconMatcher, "match", match)
    with pytest.raises(calibrate.CalibrationInterrupted):
        calibrate.calibrate_icon_scale(
            np.zeros((80, 80, 3), dtype=np.uint8),
            load_icon_templates(),
            should_stop=lambda: len(calls) >= 2,
        )
    assert len(calls) == 2


def test_no_gold_candidates_skip_dense_sweep(monkeypatch):
    calls = []

    def match(self, frame, region=None):
        calls.append(1)
        return IconMatch(0.9, 30, 30, 32, 0.0)

    monkeypatch.setattr(calibrate.IconMatcher, "match", match)
    result = calibrate.calibrate_icon_scale(
        np.zeros((80, 80, 3), dtype=np.uint8), load_icon_templates()
    )
    assert not result.valid
    assert len(calls) == len(calibrate.PROBE_SIZES)
