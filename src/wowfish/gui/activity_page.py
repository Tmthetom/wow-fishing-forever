"""Session logs and optional audio diagnostics."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledFrame, ScrolledText

from wowfish.gui.image import Preview
from wowfish.gui.presenter import Presenter, View
from wowfish.gui.score_graph import ScoreGraph

LOG_LIMIT = 800


class ActivityPage:
    def __init__(self, parent: Any, presenter: Presenter) -> None:
        self.p = presenter
        self.frame = tb.Frame(parent, padding=10)
        tabs = tb.Notebook(self.frame)
        tabs.pack(fill="both", expand=True)
        logs = tb.Frame(tabs, padding=(0, 8, 0, 0))
        tabs.add(logs, text="Logs")
        tb.Button(logs, text="Copy log", command=self._copy_log, bootstyle="secondary").pack(
            anchor="e", pady=(0, 8)
        )
        self.log = ScrolledText(logs, height=5, width=24, wrap="word", padding=0)
        self.log.pack(fill="both", expand=True)
        self.log.text.configure(state="disabled")
        self._line_count = 0

        diagnostics = ScrolledFrame(tabs, padding=10, auto_hide=True)
        tabs.add(diagnostics.container, text="Bite diagnostics")
        hint = tb.Label(
            diagnostics,
            text="Lines show how closely the sound matches each splash. The dashed line is "
            "the score needed to detect a bite.",
            justify="left",
        )
        hint.pack(fill="x", pady=(0, 8))
        hint.bind("<Configure>", lambda event: hint.configure(wraplength=event.width))
        self.graph = ScoreGraph(diagnostics)
        self.graph.canvas.pack(fill="x")
        self.preview = Preview(diagnostics, height=165)
        self.preview.frame.pack(fill="x", pady=(8, 0))
        self._tabs = tabs
        self._diagnostics = diagnostics.container

    def _copy_log(self) -> None:
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self.log.text.get("1.0", "end-1c"))

    def render(self, view: View) -> None:
        if view.new_lines:
            log = self.log.text
            follow = log.yview()[1] >= 0.99
            log.configure(state="normal")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_text = "".join(f"[{timestamp}] {line}\n" for line in view.new_lines)
            self._line_count += new_text.count("\n")
            log.insert("end", new_text)
            if self._line_count > LOG_LIMIT:
                log.delete("1.0", f"{self._line_count - LOG_LIMIT + 1}.0")
                self._line_count = LOG_LIMIT
            if follow:
                log.see("end")
            log.configure(state="disabled")
        if self.frame.winfo_ismapped() and self._tabs.select() == str(self._diagnostics):
            self.graph.show(view.trace, self.p.cfg.run.cast_timeout_s)
            self.preview.show(view.thumbnail_png)
