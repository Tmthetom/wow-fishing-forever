from datetime import date, datetime, timedelta

from wowfish.engine import events
from wowfish.gui.catch_history import HISTORY_DAYS, CatchHistory
from wowfish.gui.fish_page import _catch_rate, _since_last_catch
from wowfish.gui.presenter import Presenter


def test_history_keeps_counts_across_reopens_and_rolls_over(tmp_path):
    path = tmp_path / "catches.sqlite3"
    today = date(2026, 11, 24)
    yesterday = today - timedelta(days=1)
    older = today - timedelta(days=HISTORY_DAYS)
    history = CatchHistory(path)
    assert dict(history.recent(today))[today] == 0
    history.record(older)
    history.record(yesterday)
    history.record(today)
    CatchHistory(path).record(today)

    recent = CatchHistory(path).recent(today)
    assert len(recent) == HISTORY_DAYS
    assert recent[-3:] == ((today - timedelta(days=2), 0), (yesterday, 1), (today, 2))
    assert older not in dict(recent)
    assert dict(history.recent(older))[older] == 1
    assert history.recent(today + timedelta(days=1))[-2:] == (
        (today, 2),
        (today + timedelta(days=1), 0),
    )


def test_presenter_uses_event_time_for_days_and_stop_reason(tmp_path, monkeypatch):
    monkeypatch.setenv("WOWFISH_HOME", str(tmp_path))
    presenter = Presenter()
    now = datetime.now()
    previous_day = now - timedelta(days=1)
    presenter._apply(events.Caught(10, at=previous_day))
    presenter._apply(events.Caught(11, at=now))
    presenter._apply(events.Error(12, "capture failed"))
    presenter._apply(events.Stopped(12, "error", at=now))

    view = presenter.poll()
    assert view.daily_catches[-2:] == ((previous_day.date(), 1), (now.date(), 1))
    assert view.stopped_at == now
    assert view.last_catch_at == now
    assert view.did == "Error: capture failed"
    assert Presenter().poll().daily_catches == view.daily_catches


def test_session_rate_and_time_since_last_catch():
    caught = datetime(2026, 11, 24, 12)
    assert _catch_rate(1, 59) == "—"
    assert _catch_rate(0, 60) == "0.0"
    assert _catch_rate(3, 120) == "90.0"
    assert _since_last_catch(None, caught) == "—"
    assert _since_last_catch(caught, caught + timedelta(seconds=83)) == "01:23"
