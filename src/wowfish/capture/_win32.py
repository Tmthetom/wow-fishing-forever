"""Windows window lookup and direct client-area capture."""

from __future__ import annotations

import contextlib
import ctypes
import sys
from ctypes import wintypes
from functools import cache
from typing import Any

import numpy as np

from wowfish.capture import Box, WindowRef

INVALID_GDI_OBJECT = ctypes.c_void_p(-1).value


def client_rect_to_box(left: int, top: int, right: int, bottom: int, sx: int, sy: int) -> Box:
    """GetClientRect (0, 0, right, bottom) plus the client origin on screen (sx, sy) -> a Box."""
    return sx + left, sy + top, right - left, bottom - top


def set_dpi_aware() -> None:
    """Ask for per-monitor DPI awareness so client rectangles are in physical pixels."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # PER_MONITOR_V2
    except Exception:
        with contextlib.suppress(Exception):
            ctypes.windll.shcore.SetProcessDpiAwareness(2)


def find_window_win32(title_substring: str) -> WindowRef | None:
    if sys.platform != "win32":
        return None
    set_dpi_aware()
    user32: Any = ctypes.windll.user32
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    wanted = title_substring.lower()
    found: list[WindowRef] = []
    proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        if n <= 0:
            return True
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)
        title = buf.value
        if wanted not in title.lower():
            return True
        rect = wintypes.RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            return True
        origin = wintypes.POINT(0, 0)
        user32.ClientToScreen(hwnd, ctypes.byref(origin))
        x, y, w, h = client_rect_to_box(
            rect.left, rect.top, rect.right, rect.bottom, origin.x, origin.y
        )
        pid = wintypes.DWORD(0)
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        found.append(WindowRef(title, int(pid.value) or None, x, y, w, h, handle=int(hwnd)))
        return True

    user32.EnumWindows(proto(visit), 0)
    found = [f for f in found if f.width > 0 and f.height > 0]
    if not found:
        return None
    return max(found, key=lambda r: r.width * r.height)


class _BitmapInfoHeader(ctypes.Structure):
    _fields_ = [
        ("size", wintypes.DWORD),
        ("width", wintypes.LONG),
        ("height", wintypes.LONG),
        ("planes", wintypes.WORD),
        ("bits", wintypes.WORD),
        ("compression", wintypes.DWORD),
        ("image_size", wintypes.DWORD),
        ("x_pixels_per_meter", wintypes.LONG),
        ("y_pixels_per_meter", wintypes.LONG),
        ("colors_used", wintypes.DWORD),
        ("colors_important", wintypes.DWORD),
    ]


@cache
def _capture_api() -> tuple[Any, Any]:
    user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
    pointer = ctypes.c_void_p
    for function, arguments, result in (
        (user32.IsIconic, [wintypes.HWND], wintypes.BOOL),
        (user32.GetClientRect, [wintypes.HWND, ctypes.POINTER(wintypes.RECT)], wintypes.BOOL),
        (user32.PrintWindow, [wintypes.HWND, pointer, wintypes.UINT], wintypes.BOOL),
        (gdi32.CreateCompatibleDC, [pointer], pointer),
        (gdi32.CreateDIBSection, [pointer, pointer, wintypes.UINT, ctypes.POINTER(pointer),
                                pointer, wintypes.DWORD], pointer),
        (gdi32.SelectObject, [pointer, pointer], pointer),
        (gdi32.GdiFlush, [], wintypes.BOOL),
        (gdi32.DeleteObject, [pointer], wintypes.BOOL),
        (gdi32.DeleteDC, [pointer], wintypes.BOOL),
    ):  # fmt: skip
        function.argtypes, function.restype = arguments, result
    return user32, gdi32


def _capture_client(hwnd: int) -> np.ndarray:
    """Read client pixels using PrintWindow, as in the upstream background capture."""
    user32, gdi32 = _capture_api()
    rect = wintypes.RECT()
    if user32.IsIconic(hwnd) or not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError("Cannot capture the WoW window. Keep it open and unminimized.")
    width, height = rect.right - rect.left, rect.bottom - rect.top
    if width <= 0 or height <= 0:
        raise RuntimeError("The WoW window has no visible client area.")

    dc = gdi32.CreateCompatibleDC(None)
    if not dc:
        raise RuntimeError("Could not create a Windows capture context.")
    bitmap = previous = None
    try:
        header = _BitmapInfoHeader(ctypes.sizeof(_BitmapInfoHeader), width, -height, 1, 32)
        pixels = ctypes.c_void_p()
        bitmap = gdi32.CreateDIBSection(dc, ctypes.byref(header), 0, ctypes.byref(pixels), None, 0)
        if not bitmap or not pixels.value:
            raise RuntimeError("Could not allocate a Windows capture frame.")
        selected = gdi32.SelectObject(dc, bitmap)
        if not selected or selected == INVALID_GDI_OBJECT:
            raise RuntimeError("Could not select the Windows capture frame.")
        previous = selected
        if not user32.PrintWindow(hwnd, dc, 1 | 2):  # client area, full content
            raise RuntimeError("Direct capture failed. Turn it off in Setup and restart fishing.")
        gdi32.GdiFlush()
        bgra = (ctypes.c_uint8 * (width * height * 4)).from_address(pixels.value)
        bgr = np.ctypeslib.as_array(bgra).reshape(height, width, 4)[:, :, :3].copy()
        if not bgr.any():
            raise RuntimeError("Direct capture returned a black frame. Turn it off in Setup.")
        return bgr
    finally:
        if previous:
            gdi32.SelectObject(dc, previous)
        if bitmap:
            gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(dc)


class Win32WindowCapturer:
    def __init__(self) -> None:
        self._handle: int | None = None

    def open(self, window: WindowRef) -> None:
        if not window.handle:
            raise RuntimeError("Direct capture requires a Windows window handle.")
        self._handle = window.handle

    def grab(self, box: Box | None = None) -> np.ndarray:
        if self._handle is None:
            raise RuntimeError("capturer is not open")
        frame = _capture_client(self._handle)
        if box is None:
            return frame
        x, y, width, height = box
        return np.ascontiguousarray(frame[y : y + height, x : x + width])

    def close(self) -> None:
        self._handle = None
