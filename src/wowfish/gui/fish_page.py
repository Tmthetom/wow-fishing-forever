"""Fishing controls and a dashboard for the current session."""

from __future__ import annotations

import math
from tkinter import Canvas
from typing import Any

import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledFrame

from wowfish.gui.presenter import Presenter, View

SURFACE = "#192a35"
MUTED = "#adc3ce"
GRID = "#39505d"
ACCENT = "#63dac6"
STATE_LABELS = {
    "CASTING": "Finding the bobber",
    "WAIT_BITE": "Waiting for a bite",
    "INTERACT": "Reeling in",
}


def _duration(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


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
        for label in ("Catches", "Casts", "Misses", "Session time"):
            card = tb.Frame(self.metrics, style="Dashboard.TFrame", padding=(12, 9))
            tb.Label(card, text=label, style="MetricCaption.TLabel").pack(anchor="w")
            value = tb.Label(card, style="Metric.TLabel", font=("TkDefaultFont", 21, "bold"))
            value.pack(anchor="w")
            self._cards.append(card)
            self._values.append(value)
        self.metrics.bind("<Configure>", lambda event: self._layout_metrics(event.width))
        self._layout_metrics(420)

        chart_card = tb.Frame(body, style="Dashboard.TFrame", padding=12)
        chart_card.pack(fill="x", pady=(12, 0))
        tb.Label(
            chart_card, text="Catches over time", style="Metric.TLabel",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w")  # fmt: skip
        self.chart = Canvas(chart_card, background=SURFACE, highlightthickness=0, height=156)
        self.chart.pack(fill="x", pady=(6, 0))
        self.chart.bind("<Configure>", lambda _event: self._draw_history())
        self._history: tuple[float, ...] = ()
        self._elapsed = 0.0

    def _layout_metrics(self, width: int) -> None:
        columns = 4 if width >= 620 else 2
        if columns == self._columns:
            return
        self._columns = columns
        for col in range(4):
            self.metrics.columnconfigure(
                col, weight=int(col < columns), uniform="metrics" if col < columns else ""
            )
        for index, card in enumerate(self._cards):
            row, column = divmod(index, columns)
            card.grid(
                row=row, column=column, sticky="nsew",
                padx=(0, 8 if column < columns - 1 else 0), pady=(0, 8 if row == 0 else 0),
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
        values = (stats.catches, stats.casts, stats.misses, _duration(stats.elapsed_s))
        for label, value in zip(self._values, values, strict=True):
            label.configure(text=str(value))
        if self._history is not view.catch_times or self._elapsed != stats.elapsed_s:
            self._history = view.catch_times
            self._elapsed = stats.elapsed_s
            self._draw_history()

    def _draw_history(self) -> None:
        chart = self.chart
        chart.delete("all")
        width, height = chart.winfo_width(), chart.winfo_height()
        if width < 120 or height < 70:
            return
        if not self._history:
            chart.create_text(
                width / 2, height / 2, text="Your catches will appear here", fill=MUTED
            )
            return

        left, right, top, bottom = 36, width - 12, 12, height - 28
        span = max(1.0, self._elapsed, self._history[-1])
        step = max(1, math.ceil(len(self._history) / 4))
        ceiling = math.ceil(len(self._history) / step) * step
        for count in range(0, ceiling + 1, step):
            y = bottom - (bottom - top) * count / ceiling
            chart.create_line(left, y, right, y, fill=GRID)
            chart.create_text(left - 6, y, text=str(count), anchor="e", fill=MUTED)
        points = [float(left), float(bottom)]
        y = float(bottom)
        for count, elapsed in enumerate(self._history, start=1):
            x = left + (right - left) * elapsed / span
            next_y = bottom - (bottom - top) * count / ceiling
            points.extend((x, y, x, next_y))
            y = next_y
        points.extend((right, y))
        chart.create_line(*points, fill=ACCENT, width=2)
        chart.create_text(left, bottom + 9, text="00:00", anchor="nw", fill=MUTED)
        chart.create_text(right, bottom + 9, text=_duration(span), anchor="ne", fill=MUTED)
