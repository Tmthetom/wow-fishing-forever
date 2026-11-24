"""Fishing controls and a dashboard for the current session."""

from __future__ import annotations

import math
from datetime import date, datetime
from tkinter import Canvas
from typing import Any

import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledFrame

from wowfish.gui.catch_history import HISTORY_DAYS
from wowfish.gui.presenter import Presenter, View

SURFACE = "#192a35"
MUTED = "#adc3ce"
GRID = "#39505d"
ACCENT = "#63dac6"
PAST_DAY = "#498c86"
CHART_LEFT, CHART_RIGHT = 44, 12
STATE_LABELS = {
    "CASTING": "Finding the bobber",
    "WAIT_BITE": "Waiting for a bite",
    "INTERACT": "Reeling in",
}


def _duration(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def _session_time(stamp: datetime | None) -> str:
    if stamp is None:
        return "—"
    return stamp.strftime("%H:%M:%S" if stamp.date() == date.today() else "%d %b %H:%M:%S")


def _catch_rate(catches: int, elapsed_s: float) -> str:
    return f"{catches * 3600 / elapsed_s:,.1f}" if elapsed_s >= 60 else "—"


def _since_last_catch(caught_at: datetime | None, until: datetime) -> str:
    if caught_at is None:
        return "—"
    return _duration(max(0, until.timestamp() - caught_at.timestamp()))


class FishPage:
    def __init__(self, parent: Any, presenter: Presenter) -> None:
        self.p = presenter
        self.frame = tb.Frame(parent)
        controls = tb.Frame(self.frame, padding=(12, 12, 12, 5))
        controls.pack(fill="x")
        self.start = tb.Button(
            controls, text="Start", command=self._start, bootstyle="success", width=10
        )
        self.start.pack(side="left")
        self.stop = tb.Button(
            controls, text="Stop", command=self.p.stop, bootstyle="secondary", width=8
        )
        self.stop.pack(side="left", padx=(8, 12))
        self.status = tb.Label(controls, font=("TkDefaultFont", 12, "bold"))
        self.status.pack(side="left", fill="x", expand=True)
        self.status.bind("<Configure>", lambda e: self.status.configure(wraplength=e.width))
        self._blocker = ""

        body = ScrolledFrame(self.frame, padding=(12, 4, 12, 12), auto_hide=True)
        body.pack(fill="both", expand=True)
        self.detail = tb.Label(body, justify="left", bootstyle="secondary")
        self.detail.pack(fill="x", pady=(0, 14))
        self.detail.bind("<Configure>", lambda e: self.detail.configure(wraplength=e.width))

        self.metrics = tb.Frame(body)
        self.metrics.pack(fill="x")
        self._cards: list[tb.Frame] = []
        self._values: list[tb.Label] = []
        self._columns = 0
        for label in (
            "Catches",
            "Casts",
            "Misses",
            "Catches / hour",
            "Since last catch",
            "Session time",
        ):
            card = tb.Frame(self.metrics, style="Dashboard.TFrame", padding=(12, 9))
            tb.Label(card, text=label, style="MetricCaption.TLabel").pack(anchor="w")
            value = tb.Label(card, style="Metric.TLabel", font=("TkDefaultFont", 21, "bold"))
            value.pack(anchor="w")
            self._cards.append(card)
            self._values.append(value)
        self.metrics.bind("<Configure>", lambda event: self._layout_metrics(event.width))
        self._layout_metrics(420)

        self.session_times = tb.Label(body, justify="left", bootstyle="secondary")
        self.session_times.pack(fill="x", pady=(2, 0))
        self.session_times.bind(
            "<Configure>", lambda e: self.session_times.configure(wraplength=e.width)
        )
        chart_card = tb.Frame(body, style="Dashboard.TFrame", padding=12)
        chart_card.pack(fill="x", pady=(12, 0))
        tb.Label(
            chart_card, text="Catches by day", style="Metric.TLabel",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w")  # fmt: skip
        self.summary = tb.Label(chart_card, style="MetricCaption.TLabel")
        self.summary.pack(anchor="w", pady=(3, 0))
        self.chart = Canvas(chart_card, background=SURFACE, highlightthickness=0, height=174)
        self.chart.pack(fill="x", pady=(6, 0))
        self.chart.bind("<Configure>", lambda _event: self._draw_history())
        self.chart.bind("<Motion>", self._show_day)
        self.chart.bind("<Leave>", lambda _event: self.summary.configure(text=self._summary))
        self._history: tuple[tuple[date, int], ...] = ()
        self._summary = f"Last {HISTORY_DAYS} days"
        self.summary.configure(text=self._summary)

    def _layout_metrics(self, width: int) -> None:
        columns = 3 if width >= 620 else 2
        if columns == self._columns:
            return
        self._columns = columns
        for col in range(3):
            self.metrics.columnconfigure(
                col, weight=int(col < columns), uniform="metrics" if col < columns else ""
            )
        for index, card in enumerate(self._cards):
            row, column = divmod(index, columns)
            card.grid(
                row=row, column=column, sticky="nsew",
                padx=(0, 8 if column < columns - 1 else 0), pady=(0, 8),
            )  # fmt: skip

    def _start(self) -> None:
        reasons = self.p.prerequisites(request=True)
        self._blocker = "\n".join(reasons)
        if not reasons:
            self.p.start()

    def render(self, view: View) -> None:
        if self._blocker or view.did.startswith("Error:"):
            status, detail, color = "Needs attention", self._blocker or view.did, "warning"
        elif view.state == "PAUSED":
            status, detail, color = "Paused", view.did.removeprefix("Paused: "), "warning"
        elif view.running:
            status, detail, color = STATE_LABELS.get(view.state, "Fishing"), view.next, "success"
        elif view.state == "STOPPED":
            status, detail, color = "Stopped", view.did, "secondary"
        else:
            status, detail, color = "Ready to start", "Calibrate in Setup before fishing.", "info"
        self.status.configure(text=status, bootstyle=color)
        self.detail.configure(text=detail)
        self.start.configure(state="disabled" if view.running else "normal")
        self.stop.configure(state="normal" if view.running else "disabled")
        stats = view.stats
        values = (
            stats.catches,
            stats.casts,
            stats.misses,
            _catch_rate(stats.catches, stats.elapsed_s),
            _since_last_catch(view.last_catch_at, view.stopped_at or datetime.now()),
            _duration(stats.elapsed_s),
        )
        for label, value in zip(self._values, values, strict=True):
            label.configure(text=str(value))
        started = _session_time(view.started_at)
        stopped = "In progress" if view.running else _session_time(view.stopped_at)
        self.session_times.configure(text=f"Started  {started}     ·     Stopped  {stopped}")
        if self._history != view.daily_catches:
            self._history = view.daily_catches
            recent = sum(count for _, count in self._history)
            today = self._history[-1][1] if self._history else 0
            self._summary = f"Today  {today:,}     ·     Last {HISTORY_DAYS} days  {recent:,}"
            self.summary.configure(text=self._summary)
            self._draw_history()

    def _draw_history(self) -> None:
        chart = self.chart
        chart.delete("all")
        width, height = chart.winfo_width(), chart.winfo_height()
        if width < 120 or height < 70:
            return
        peak = max((count for _, count in self._history), default=0)
        if peak == 0:
            chart.create_text(
                width / 2, height / 2, text="Your catches will appear here", fill=MUTED
            )
            return

        left, right, top, bottom = CHART_LEFT, width - CHART_RIGHT, 14, height - 27
        step = max(1, math.ceil(peak / 4))
        ceiling = math.ceil(peak / step) * step
        for count in range(0, ceiling + 1, step):
            y = bottom - (bottom - top) * count / ceiling
            chart.create_line(left, y, right, y, fill=GRID)
            chart.create_text(left - 6, y, text=f"{count:,}", anchor="e", fill=MUTED)
        slot = (right - left) / len(self._history)
        label_every = max(1, math.ceil(54 / slot))
        last = len(self._history) - 1
        for index, (day, count) in enumerate(self._history):
            x = left + slot * (index + 0.5)
            bar_height = max(2, (bottom - top) * count / ceiling)
            half = min(16, slot * 0.33)
            color = ACCENT if index == last else PAST_DAY
            chart.create_rectangle(
                x - half, bottom - bar_height, x + half, bottom, fill=color, outline=""
            )
            if (last - index) % label_every == 0:
                chart.create_text(
                    min(x, width - 28), bottom + 8, text=day.strftime("%d %b"),
                    anchor="n", fill=MUTED,
                )  # fmt: skip

    def _show_day(self, event: Any) -> None:
        width = self.chart.winfo_width() - CHART_LEFT - CHART_RIGHT
        offset = event.x - CHART_LEFT
        if self._history and width > 0 and 0 <= offset < width:
            index = int(offset * len(self._history) / width)
            day, count = self._history[index]
            self.summary.configure(text=f"{day:%d %b %Y}     ·     {count:,} catches")
        else:
            self.summary.configure(text=self._summary)
