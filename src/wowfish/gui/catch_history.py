"""Persistent local-day catch totals for the Fishing dashboard."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

HISTORY_DAYS = 14


class CatchHistory:
    def __init__(self, path: Path) -> None:
        self.path = path

    def record(self, day: date) -> None:
        with closing(sqlite3.connect(self.path, timeout=0.25)) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS daily_catches (day TEXT PRIMARY KEY, catches INTEGER)"
            )
            db.execute(
                "INSERT INTO daily_catches VALUES (?, 1) "
                "ON CONFLICT(day) DO UPDATE SET catches = catches + 1",
                (day.isoformat(),),
            )

    def recent(self, today: date) -> tuple[tuple[date, int], ...]:
        first = today - timedelta(days=HISTORY_DAYS - 1)
        totals = {}
        if self.path.exists():
            with closing(sqlite3.connect(self.path, timeout=0.25)) as db:
                totals = dict(
                    db.execute(
                        "SELECT day, catches FROM daily_catches WHERE day BETWEEN ? AND ?",
                        (first.isoformat(), today.isoformat()),
                    )
                )
        days = (first + timedelta(days=offset) for offset in range(HISTORY_DAYS))
        return tuple((day, totals.get(day.isoformat(), 0)) for day in days)
