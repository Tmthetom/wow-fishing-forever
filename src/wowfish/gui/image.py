"""BGR frames -> PNG bytes -> Tk images, without Pillow."""

from __future__ import annotations

import base64
from typing import Any

import cv2
import numpy as np

from wowfish.capture import Box

GREEN = (0, 200, 0)
THUMB_WIDTH = 480


def thumbnail(frame: np.ndarray, width: int = THUMB_WIDTH) -> tuple[np.ndarray, float]:
    """Downscale to at most `width` px wide; returns (thumb, scale)."""
    h, w = frame.shape[:2]
    scale = min(1.0, width / w)
    if scale < 1.0:
        return cv2.resize(frame, (round(w * scale), round(h * scale)), cv2.INTER_AREA), scale
    return frame.copy(), 1.0


def with_box(frame: np.ndarray, box: Box, color=GREEN) -> np.ndarray:
    out = frame.copy()
    x, y, w, h = box
    cv2.rectangle(out, (x - 2, y - 2), (x + w + 2, y + h + 2), color, 2)
    return out


def bgr_to_png_bytes(frame: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", frame)
    if not ok:
        raise ValueError("cannot encode frame as PNG")
    return buf.tobytes()


def png_base64(png: bytes) -> str:
    return base64.b64encode(png).decode("ascii")


def photo_from_png(png: bytes):  # -> tkinter.PhotoImage; imported lazily so tests stay Tk-free
    import tkinter

    return tkinter.PhotoImage(data=png_base64(png))


class Preview:
    """Fit a preview inside its panel, even when the window is narrow."""

    def __init__(self, parent: Any, height: int = 200) -> None:
        import ttkbootstrap as tb

        self.frame = tb.Frame(parent, height=height)
        self.frame.pack_propagate(False)
        self.label = tb.Label(self.frame, anchor="center")
        self.label.pack(fill="both", expand=True)
        self._png: bytes | None = None
        self._photo: Any = None
        self.frame.bind("<Configure>", lambda _event: self._fit())

    def show(self, png: bytes | None) -> None:
        if png is not self._png:
            self._png = png
            self._fit()

    def _fit(self) -> None:
        if self._png is None:
            self.label.configure(image="")
            self._photo = None
            return
        view_width, view_height = self.frame.winfo_width(), self.frame.winfo_height()
        if min(view_width, view_height) <= 1:
            return
        pixels = cv2.imdecode(np.frombuffer(self._png, dtype=np.uint8), cv2.IMREAD_COLOR)
        height, width = pixels.shape[:2]
        limit = min(view_width, int(view_height * width / height))
        rendered = (
            bgr_to_png_bytes(thumbnail(pixels, max(1, limit))[0]) if limit < width else self._png
        )
        self._photo = photo_from_png(rendered)
        self.label.configure(image=self._photo)
