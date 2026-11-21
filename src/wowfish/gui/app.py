"""The River Desk window and its Fishing, Setup, and Activity tabs."""

from __future__ import annotations

import gc
import os
import sys

from wowfish import __version__
from wowfish.assets import asset_dir
from wowfish.gui.activity_page import ActivityPage
from wowfish.gui.fish_page import FishPage
from wowfish.gui.presenter import Presenter
from wowfish.gui.setup_page import SetupPage

POLL_MS = 50


class App:
    def __init__(self, presenter: Presenter | None = None) -> None:
        import ttkbootstrap as tb

        self.p = presenter or Presenter()
        title = os.environ.get("WOWFISH_WINDOW_TITLE") or "River Desk"
        icon = asset_dir() / ("river-desk.ico" if sys.platform == "win32" else "river-desk.png")
        self.root = tb.Window(
            themename="bootstrap-dark",
            title=f"{title} {__version__}",
            size=(820, 680),
            minsize=(420, 390),
            iconphoto=str(icon),
        )
        style = self.root.style
        style.configure("TNotebook", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 9))
        style.configure("Dashboard.TFrame", background="#192a35")
        style.configure("Metric.TLabel", background="#192a35", foreground="#eaf4f8")
        style.configure("MetricCaption.TLabel", background="#192a35", foreground="#adc3ce")
        nb = tb.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=12, pady=12)
        nb.enable_traversal()
        self.setup = SetupPage(nb, self.p)
        self.fish = FishPage(nb, self.p)
        self.activity = ActivityPage(nb, self.p)
        nb.add(self.fish.frame, text="Fishing", underline=0)
        nb.add(self.setup.frame, text="Setup", underline=0)
        nb.add(self.activity.frame, text="Activity", underline=0)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._after = self.root.after(POLL_MS, self._tick)

    def tick(self) -> None:
        view = self.p.poll()
        self.fish.render(view)
        self.setup.render(view)
        self.activity.render(view)

    def _tick(self) -> None:
        try:
            self.tick()
        finally:
            self._after = self.root.after(POLL_MS, self._tick)

    def run(self) -> None:
        try:
            self.root.mainloop()
        finally:
            self.close()

    def close(self) -> None:
        """Stop everything and free the Tk interpreter on this thread.

        Tcl panics (an Illegal-instruction trap) if its interpreter is deleted from another
        thread, which is what happens when a later garbage collection on a worker thread frees
        a window that was merely destroyed. So drop every reference and collect here.
        """
        if self.root is None:
            return
        if self._after is not None:
            self.root.after_cancel(self._after)
            self._after = None
        self.p.shutdown()
        self.root.destroy()
        self.setup = self.fish = self.activity = None  # type: ignore[assignment]
        self.root = None  # type: ignore[assignment]
        gc.collect()


def run() -> None:
    App().run()
