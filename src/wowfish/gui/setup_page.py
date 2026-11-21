"""Setup tab: prerequisites, keys, audio device with a live meter, calibration, bite check."""

from __future__ import annotations

import sys
from tkinter import BooleanVar
from typing import Any

from wowfish.gui import image
from wowfish.gui.presenter import (
    CALIBRATE_WATCH_S,
    CalibrateDone,
    Presenter,
    VerifyDone,
    View,
    WorkerFailed,
)

CHECKLIST = (
    "1. Enable Interact Key and Auto Loot. Keep Sound Effects on and mute Music and Ambience.\n"
    "2. Enter each command separately in the game chat:\n"
    "    /console SoftTargetIconInteract 1\n"
    "    /console SoftTargetIconGameObject 1\n"
    "3. Move River Desk clear of the bobber. Calibrate and save the result.\n"
    "4. Catch a few fish manually, even with Bright Baubles enabled.\n"
    "5. Choose Fishing → Start. Minimize River Desk and keep WoW in the foreground.\n"
    "Czech keyboard: use [ and ] here. Bind Fishing to ú and Interact to ) "
    "in WoW. After stopping, restore the game settings you changed. Keep the key bindings."
)
LURE_HINT = (
    "Optional. Use /use Bright Baubles + /use 16 in a macro. Stop/Start keeps the lure timer; "
    "closing the app resets it. The active buff is not checked. Empty = no lure."
)
VERIFY_HINT = "Click, then fish by hand in the game until a fish bites (it records for 60 s)."
CALIBRATE_HINT = (
    f"Click, then cast in the game: it watches for the gold gear for up to {CALIBRATE_WATCH_S:g} s."
)


class SetupPage:
    def __init__(self, parent: Any, presenter: Presenter) -> None:
        import ttkbootstrap as tb
        from ttkbootstrap.widgets.scrolled import ScrolledFrame

        self.p = presenter
        content = ScrolledFrame(parent, padding=12, auto_hide=True)
        self.frame = content.container
        self._wrapped: list[Any] = []

        cal = tb.Labelframe(content, text="Calibration", padding=12)
        cal.pack(fill="x", pady=(0, 10))
        size = presenter.cfg.vision.icon_size_px
        current = f"Saved size: {size} px. " if size > 0 else ""
        self.cal_note = self._note(cal, current + CALIBRATE_HINT)
        row = tb.Frame(cal)
        row.pack(fill="x", pady=(8, 0))
        self.cal_button = tb.Button(
            row, text="Calibrate the gear icon", command=self._calibrate, bootstyle="info"
        )
        self.cal_button.pack(side="left")
        self.save_cal = tb.Button(
            row, text="Save calibration", command=self._save_cal, bootstyle="success",
            state="disabled",
        )  # fmt: skip
        self.save_cal.pack(side="left", padx=(8, 0))
        self.preview = image.Preview(cal, height=246)

        checklist = tb.Labelframe(content, text="Before fishing", padding=12)
        checklist.pack(fill="x", pady=(0, 10))
        instructions = self._note(checklist, CHECKLIST)
        instructions.pack_forget()

        def toggle_checklist() -> None:
            is_visible = instructions.winfo_manager() == "pack"
            if is_visible:
                instructions.pack_forget()
            else:
                instructions.pack(fill="x", pady=(8, 0))
            checklist_button.configure(text="Show checklist" if is_visible else "Hide checklist")

        checklist_button = tb.Button(
            checklist, text="Show checklist", command=toggle_checklist, bootstyle="secondary"
        )
        checklist_button.pack(anchor="w")

        bindings = tb.Labelframe(content, text="Key bindings", padding=12)
        bindings.pack(fill="x", pady=(0, 10))
        keys = tb.Frame(bindings)
        keys.pack(fill="x")
        game = presenter.cfg.game
        self.cast = self._entry(keys, 0, "Cast key", game.cast_key)
        self.interact = self._entry(keys, 1, "Interact key", game.interact_key)
        self.lure = self._entry(keys, 2, "Lure key (optional)", game.lure_key)
        self.quit = self._entry(keys, 3, "Quit key (optional)", game.quit_key)
        self._note(bindings, LURE_HINT, pady=6)
        tb.Button(bindings, text="Save keys", command=self._save_keys, bootstyle="secondary").pack(
            anchor="w"
        )
        self.keys_note = self._note(bindings, "")

        helpers = tb.Labelframe(content, text="Session helpers (optional)", padding=12)
        helpers.pack(fill="x", pady=(0, 10))
        timers = tb.Frame(helpers)
        timers.pack(fill="x")
        behavior = presenter.cfg.behavior
        self.focus_minutes = self._entry(
            timers, 0, "Check foreground (min)",
            f"{behavior.focus_check_minutes:g}" if behavior.focus_check_minutes else "",
        )  # fmt: skip
        self.jump_minutes = self._entry(
            timers, 1, "Jump every (min)",
            f"{behavior.jump_every_minutes:g}" if behavior.jump_every_minutes else "",
        )  # fmt: skip
        for entry in (self.focus_minutes, self.jump_minutes):
            entry.bind("<Return>", lambda _event: self._save_helpers())
        tb.Button(helpers, text="Save timers", command=self._save_helpers).pack(anchor="w", pady=4)
        self.helpers_note = self._note(helpers, "Empty or 0 turns a timer off. Applies on Start.")

        limit = tb.Frame(helpers)
        limit.pack(fill="x", pady=(10, 0))
        tb.Label(limit, text="Stop after (min)").grid(row=0, column=0, sticky="w")
        self.minutes = tb.Spinbox(limit, from_=0, to=1440, increment=15, width=6)
        self.minutes.set(game.session_minutes)
        self.minutes.grid(row=0, column=1, padx=8)
        self.minutes.bind("<Return>", lambda _event: self._save_limit())
        tb.Button(limit, text="Save limit", command=self._save_limit, bootstyle="secondary").grid(
            row=0, column=2
        )
        self.limit_note = self._note(helpers, "0 keeps fishing until you press Stop.")

        if sys.platform == "win32":
            self.window_capture = BooleanVar(master=content, value=presenter.cfg.run.window_capture)
            tb.Checkbutton(
                helpers,
                text="Capture the WoW window directly",
                variable=self.window_capture,
                command=lambda: self.p.save_window_capture(self.window_capture.get()),
            ).pack(anchor="w", pady=(10, 0))

        audio = tb.Labelframe(content, text="Audio diagnostics", padding=12)
        audio.pack(fill="x")
        self.devices = presenter.audio_devices()
        self.device = tb.Combobox(
            audio, values=[device.name for device in self.devices], state="readonly", width=18
        )
        self.device.pack(fill="x")
        current = presenter.cfg.audio.device
        pick = (
            next(
                (i for i, device in enumerate(self.devices) if current in (device.id, device.name)),
                None,
            )
            if current
            else None
        )
        if pick is None:
            default = presenter.default_device()
            pick = self.devices.index(default) if default in self.devices else None
        if pick is not None:
            self.device.current(pick)
        tb.Button(
            audio, text="Use this and listen", command=self._save_device, bootstyle="secondary"
        ).pack(anchor="w", pady=6)
        self.meter = tb.Progressbar(audio, maximum=100, value=0, bootstyle="info")
        self.meter.pack(fill="x")
        self.level_text = self._note(audio, "")
        self._meter_error = ""
        self.verify_button = tb.Button(
            audio, text="Record 60 s and check the bite", command=self._verify, bootstyle="info"
        )
        self.verify_button.pack(anchor="w", pady=(10, 4))
        self._meter_was_on = False
        self.verify_note = self._note(audio, VERIFY_HINT)
        bite_row = tb.Frame(audio)
        bite_row.pack(fill="x", pady=(10, 4))
        self.bite = self._entry(
            bite_row, 0, "Bite threshold", f"{presenter.cfg.audio.bite_threshold:.2f}"
        )
        self.bite.bind("<Return>", lambda _event: self._save_bite())
        tb.Button(bite_row, text="Save", command=self._save_bite, bootstyle="secondary").grid(
            row=0, column=2
        )
        self.bite_note = self._note(audio, "Minimum audio score required to detect a bite.")

        content.bind("<Configure>", self._reflow, add="+")

    def _note(self, parent: Any, text: str, pady: int = 0) -> Any:
        import ttkbootstrap as tb

        label = tb.Label(parent, text=text, justify="left", wraplength=315)
        label.pack(fill="x", pady=pady)
        self._wrapped.append(label)
        return label

    def _reflow(self, event: Any) -> None:
        width = max(100, event.width - 58)
        for label in self._wrapped:
            if int(label.cget("wraplength")) != width:
                label.configure(wraplength=width)

    @staticmethod
    def _entry(parent: Any, row: int, text: str, value: str) -> Any:
        import ttkbootstrap as tb

        tb.Label(parent, text=text).grid(row=row, column=0, sticky="w", pady=3)
        entry = tb.Entry(parent, width=7)
        entry.insert(0, value)
        entry.grid(row=row, column=1, padx=8, pady=3, sticky="w")
        return entry

    # -- actions ----------------------------------------------------------------------------

    def _save_keys(self) -> None:
        try:
            self.p.save_keys(self.cast.get(), self.interact.get(), self.quit.get(), self.lure.get())
            self.keys_note.configure(text="saved")
        except ValueError as e:
            self.keys_note.configure(text=str(e))

    def _save_limit(self) -> None:
        try:
            self.p.save_session_minutes(int(self.minutes.get()))
        except ValueError:
            self.limit_note.configure(text="enter whole minutes, 0 for never")
            return
        quit_key = self.p.cfg.game.quit_key
        then = f"; then the bot presses {quit_key} to quit the game" if quit_key else ""
        self.limit_note.configure(text=f"saved; used from the next Start{then}")

    def _save_helpers(self) -> None:
        try:
            self.p.save_session_helpers(self.focus_minutes.get(), self.jump_minutes.get())
        except ValueError as e:
            self.helpers_note.configure(text=str(e))
            return
        for entry, value in (
            (self.focus_minutes, self.p.cfg.behavior.focus_check_minutes),
            (self.jump_minutes, self.p.cfg.behavior.jump_every_minutes),
        ):
            entry.delete(0, "end")
            if value:
                entry.insert(0, f"{value:g}")
        self.helpers_note.configure(text="Saved; used from the next Start. Empty = off.")

    def _selected_device(self) -> str | None:
        i = self.device.current()
        return self.devices[i].id if 0 <= i < len(self.devices) else None

    def _save_device(self) -> None:
        sel = self._selected_device()
        if sel is not None:
            self.p.save_audio_device(sel)
            self._meter_error = ""
            self.p.start_meter(sel)

    def _verify(self) -> None:
        self._meter_was_on = self.p.meter_running
        self.p.stop_meter()  # the recording shows its own level on the meter
        self.verify_button.configure(state="disabled")
        self.verify_note.configure(text="Starting the recording...")
        self.p.record_and_verify(60.0, self._selected_device())

    def _calibrate(self) -> None:
        self.cal_button.configure(state="disabled")
        self.save_cal.configure(state="disabled")
        self.cal_note.configure(text="Starting...")
        self.preview.frame.pack_forget()
        self.preview.show(None)
        self.p.grab_and_calibrate()

    def _save_bite(self) -> None:
        try:
            saved = self.p.save_bite_threshold(self.bite.get())
        except ValueError as e:
            self.bite_note.configure(text=str(e))
            return
        self.bite_note.configure(text=f"saved {saved:.2f}; used from the next Start")

    def _save_cal(self) -> None:
        self.p.save_calibration()
        self.cal_note.configure(text=f"Calibration saved at {self.p.cfg.vision.icon_size_px} px.")
        self.save_cal.configure(state="disabled")

    # -- rendering --------------------------------------------------------------------------

    def render(self, view: View) -> None:
        pct = max(0.0, min(100.0, (view.level_dbfs + 60.0) / 60.0 * 100.0))
        self.meter.configure(value=pct)
        if not view.listening:
            self.level_text.configure(
                text=self._meter_error or "not listening (press Use this and listen)"
            )
        else:
            level = "silent" if view.level_dbfs <= -60 else f"{view.level_dbfs:5.1f} dBFS"
            best = max(view.last_scores.values(), default=None)
            score = f"   bite score {best:.2f}" if best is not None and best > -1.0 else ""
            self.level_text.configure(text=level + score)
        if view.verify_status:
            self.verify_note.configure(text=view.verify_status)
        if view.calibrate_status:
            self.cal_note.configure(text=view.calibrate_status)
        for item, line in zip(view.log_events, view.new_lines, strict=True):
            match item:
                case CalibrateDone(calibration=cal):
                    self.preview.frame.pack(fill="x", pady=(8, 0))
                    self.preview.show(item.thumbnail_png)
                    if cal.valid:
                        self.cal_note.configure(
                            text=f"Found it: {cal.icon_size_px} px, score {cal.score:.2f}. "
                            "Save calibration to keep it."
                        )
                        self.save_cal.configure(state="normal")
                    else:
                        self.cal_note.configure(
                            text=f"No gold gear icon seen in {CALIBRATE_WATCH_S:g} s. "
                            "Is SoftTargetIconGameObject on "
                            "and the bobber close enough to interact with? Try again."
                        )
                    self.cal_button.configure(state="normal")
                case VerifyDone(report=report):
                    self.verify_note.configure(text=line)
                    if report.stands_out:  # suggest, but only Save changes the config
                        self.bite.delete(0, "end")
                        self.bite.insert(0, f"{report.threshold:.2f}")
                        self.bite_note.configure(text="suggested by the bite check; Save to use it")
                    self._verify_finished()
                case WorkerFailed(what="verify the bite"):
                    self.verify_note.configure(text=line)
                    self._verify_finished()
                case WorkerFailed(what="calibrate"):
                    self.cal_note.configure(text=line)
                    self.cal_button.configure(state="normal")
                case WorkerFailed():
                    self._meter_error = line

    def _verify_finished(self) -> None:
        self.verify_button.configure(state="normal")
        if self._meter_was_on:
            self._meter_was_on = False
            self.p.start_meter(self._selected_device())
