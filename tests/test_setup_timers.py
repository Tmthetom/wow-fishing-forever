"""Timer settings persist without replacing unrelated saved configuration."""

from dataclasses import replace

import pytest

from wowfish.config import load_config, save_config
from wowfish.gui.presenter import Presenter


def test_timer_settings_round_trip_and_preserve_latest_config(tmp_path, monkeypatch):
    monkeypatch.setenv("WOWFISH_HOME", str(tmp_path))
    p = Presenter(find_window=lambda _: None)
    latest = replace(p.cfg, vision=replace(p.cfg.vision, icon_size_px=37))
    save_config(latest)
    p.save_session_helpers(" 1 ", "5.5")
    saved = load_config()[0]
    assert saved.vision == latest.vision
    assert saved.game == latest.game
    assert saved.audio == latest.audio
    assert saved.behavior == replace(latest.behavior, focus_check_minutes=1, jump_every_minutes=5.5)
    p.save_session_helpers("", "5")
    assert p.cfg.behavior.focus_check_minutes == 0
    assert p.cfg.behavior.jump_every_minutes == 5
    p.save_session_helpers("1", "   ")
    assert p.cfg.behavior.focus_check_minutes == 1
    assert p.cfg.behavior.jump_every_minutes == 0


@pytest.mark.parametrize("bad", ["-1", "1441", "nan", "inf", "abc"])
@pytest.mark.parametrize("field", [0, 1])
def test_invalid_timer_does_not_save_either_field(tmp_path, monkeypatch, bad, field):
    monkeypatch.setenv("WOWFISH_HOME", str(tmp_path))
    p = Presenter(find_window=lambda _: None)
    p.save_session_helpers("1", "5")
    before = load_config()[0]
    values = ["2", "6"]
    values[field] = bad
    with pytest.raises(ValueError):
        p.save_session_helpers(*values)
    assert load_config()[0] == before
    assert p.cfg == before
