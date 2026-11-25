import ctypes
import weakref
from collections import namedtuple
from ctypes import byref, c_double, c_int, c_uint32

from . import _lib
from ._lib import lib

AUTO, WAYLAND, GNOME, PORTAL, X11, WIN32, MACOS, TEST, OFFSCREEN = range(9)
"""Backend ids for `backend=`: AUTO picks the best one for the system, the rest force one. The env var GOOME_BACKEND wins over both."""
BACKENDS = {"auto": AUTO, "wayland": WAYLAND, "gnome": GNOME, "portal": PORTAL, "x11": X11, "win32": WIN32, "macos": MACOS, "test": TEST,
            "offscreen": OFFSCREEN}
"""Backend names you can pass as a string, like `backend="x11"`."""

MODE_OVERLAY, MODE_WINDOW, MODE_OFFSCREEN = range(3)
"""What a goome is: a see-through overlay (MODE_OVERLAY), a normal window (MODE_WINDOW) or a pixel buffer with no window (MODE_OFFSCREEN)."""
MODES = {"overlay": MODE_OVERLAY, "window": MODE_WINDOW, "app": MODE_WINDOW, "offscreen": MODE_OFFSCREEN}
"""Mode names you can pass as a string. "app" is the same as "window"."""

WINDOW_RESIZABLE = 1
"""Window flag: the user can resize the window."""
WINDOW_BORDERLESS = 2
"""Window flag: no border or title bar from the os."""
WINDOW_TRANSPARENT = 4
"""Window flag: the window background is see-through where you dont draw."""
WINDOW_ON_TOP = 8
"""Window flag: stay above other windows."""
WINDOW_HIDDEN = 16
"""Window flag: start hidden, call show() when ready."""
WINDOW_CENTER = 32
"""Window flag: open in the middle of the screen."""
WINDOW_NO_TITLEBAR = 64
"""Window flag: leave out the title bar that `ui.app()` draws, so APP_TITLEBAR is ignored."""
WINDOW_NO_CONSOLE = 128
"""Window flag: on Windows, hide the console window."""

OK = 0
"""Return code for success. The errors below are all negative."""
ENOTSUP = -1
"""Error code: this backend cant do that."""
EDENIED = -2
"""Error code: the user or the os said no."""
ENODISPLAY = -3
"""Error code: no display to connect to."""
EGONE = -4
"""Error code: the thing you used is gone, closed or replaced."""
EAGAIN = -5
"""Error code: not ready yet, try again."""
ENOMEM = -6
"""Error code: out of memory."""
EARG = -7
"""Error code: a bad argument."""

CAP_CAPTURE = 1
"""Capability bit: can capture the screen. Check with `g.can(CAP_CAPTURE)`."""
CAP_GLOBAL_POINTER = 2
"""Capability bit: can read the pointer anywhere on screen, not just over your own window."""
CAP_HOTKEYS = 4
"""Capability bit: can register global hotkeys."""
CAP_HIDE_SELF = 8
"""Capability bit: can keep your own overlay out of captures."""
CAP_KEYBOARD = 16
"""Capability bit: can take keyboard input."""
CAP_WINDOW = 32
"""Capability bit: can move, resize and change the window state."""
CAP_CLIPBOARD = 64
"""Capability bit: can read and write the clipboard."""
CAP_CURSOR = 128
"""Capability bit: can change the mouse cursor."""
CAP_GRAB = 256
"""Capability bit: can grab focus and the pointer."""

WANT_MOUSE = 1
"""Bit in `ui.wants`: the ui wants the mouse right now."""
WANT_KEYBOARD = 2
"""Bit in `ui.wants`: the ui wants the keyboard right now."""

FMT_BGRA_PREMUL, FMT_RGBA_PREMUL, FMT_BGRA, FMT_RGBA = range(4)
"""Pixel formats for `frame_copy`, named by byte order in memory. The non premultiplied ones (FMT_BGRA, FMT_RGBA) get converted for you."""

NONE, DOWN, UP, MOTION, SCROLL, KEY, HOTKEY, CONTROL, MONITORS, QUIT, CLOSE, FOCUS, DROP, TEXT, PREEDIT = range(15)
"""Event types, the `type` of an Event. NONE is an empty one, CLOSE is the window close button, FOCUS has `id` 1 when gained and 0 when lost, DROP is a file dropped on the window, TEXT is finished ime or compose text, PREEDIT is text still being composed."""
EVENT_NAMES = ("none", "down", "up", "motion", "scroll", "key", "hotkey", "control", "monitors", "quit", "close", "focus", "drop", "text",
               "preedit")
"""Event type names, in the same order as the type ids."""

(CURSOR_ARROW, CURSOR_IBEAM, CURSOR_HAND, CURSOR_MOVE, CURSOR_RESIZE_EW, CURSOR_RESIZE_NS, CURSOR_RESIZE_NWSE, CURSOR_RESIZE_NESW,
 CURSOR_WAIT, CURSOR_NO, CURSOR_HIDDEN) = range(11)
"""Mouse cursor shapes for `g.cursor`."""
CURSOR_NAMES = ("arrow", "ibeam", "hand", "move", "resize_ew", "resize_ns", "resize_nwse", "resize_nesw", "wait", "no", "hidden")
"""Cursor shape names, in the same order as the ids."""
CURSORS = dict((n, i) for i, n in enumerate(CURSOR_NAMES))
"""Cursor name to id, so `g.cursor = "hand"` works."""

EDGE_LEFT = 1
"""Window edge bit for `drag()`: left."""
EDGE_RIGHT = 2
"""Window edge bit for `drag()`: right."""
EDGE_TOP = 4
"""Window edge bit for `drag()`: top."""
EDGE_BOTTOM = 8
"""Window edge bit for `drag()`: bottom."""

STATE_NORMAL, STATE_MINIMIZED, STATE_MAXIMIZED, STATE_FULLSCREEN = range(4)
"""Window states for `g.state`."""
STATES = {"normal": STATE_NORMAL, "minimized": STATE_MINIMIZED, "maximized": STATE_MAXIMIZED, "fullscreen": STATE_FULLSCREEN}
"""Window state names you can pass as a string."""

K_BACKSPACE = 8
"""Key code: backspace."""
K_TAB = 9
"""Key code: tab."""
K_ENTER = 13
"""Key code: enter."""
K_ESC = 27
"""Key code: escape."""
K_SPACE = 32
"""Key code: space."""
K_DELETE = 127
"""Key code: delete."""
K_F1 = 0x81
"""Key code: F1. F2 to F11 are the codes in between."""
K_F12 = 0x8C
"""Key code: F12."""
K_LEFT, K_RIGHT, K_UP, K_DOWN, K_HOME, K_END, K_PGUP, K_PGDN, K_INSERT = range(0x90, 0x99)
"""Key codes for the arrows, home, end, page up, page down and insert."""

SHIFT = 0x100
"""Modifier bit in `event.mods`: shift."""
CTRL = 0x200
"""Modifier bit in `event.mods`: ctrl."""
ALT = 0x400
"""Modifier bit in `event.mods`: alt."""
SUPER = 0x800
"""Modifier bit in `event.mods`: the super / windows / command key."""

VERSION = "0.5.6"
"""The goome version, like "0.5.6"."""

Rect = namedtuple("Rect", "x y w h")
"""A rectangle in logical coords, `Rect(x, y, w, h)`."""
Pointer = namedtuple("Pointer", "x y buttons")
"""Where the mouse is, `Pointer(x, y, buttons)`."""


class GoomeError(Exception):
    """Base class for every goome error. `code` is the GOOME_E* code and `message` is the text."""
    def __init__(self, code, message=None):
        self.code = code
        self.message = message or strerror(code)
        super().__init__(self.message)


class NotSupported(GoomeError):
    """Raised when this backend cant do what you asked (ENOTSUP)."""
    pass


class Denied(GoomeError):
    """Raised when the user or the os refused (EDENIED)."""
    pass


class NoDisplay(GoomeError):
    """Raised when there is no display to open (ENODISPLAY)."""
    pass


class Gone(GoomeError):
    """Raised when you use something that was closed or replaced (EGONE)."""
    pass


class Again(GoomeError):
    """Raised when something isnt ready yet and you should try again (EAGAIN)."""
    pass


class NoMemory(GoomeError):
    """Raised when goome runs out of memory (ENOMEM)."""
    pass


class BadArg(GoomeError):
    """Raised for a bad argument (EARG)."""
    pass


ERRORS = {ENOTSUP: NotSupported, EDENIED: Denied, ENODISPLAY: NoDisplay, EGONE: Gone, EAGAIN: Again, ENOMEM: NoMemory, EARG: BadArg}
"""Error code to exception class."""


def _s(b):
    if b is None:
        return None
    return b.decode("utf-8", "replace")


def _b(s):
    if s is None:
        return None
    if isinstance(s, bytes):
        return s
    return str(s).encode("utf-8")


def strerror(code):
    """Text for an error code.

    Args:
        code: one of the E* constants.
    """
    return _s(lib.goome_strerror(code)) or "error %d" % code


def error_for(code, message=None):
    """Build the right exception for an error code."""
    return ERRORS.get(code, GoomeError)(code, message)


def _rect(r):
    if r is None:
        return None
    if isinstance(r, _lib.RectS):
        return r
    x, y, w, h = r
    return _lib.RectS(int(x), int(y), int(w), int(h))


def _rect_out(s):
    return Rect(s.x, s.y, s.w, s.h)


class Monitor(object):
    """One screen. `id`, `name`, `area` (a Rect in logical coords), `scale` (real px per logical px), `pw` and `ph` (size in real px) and `rotation` (0, 90, 180 or 270, plus 360 if mirrored)."""
    __slots__ = ("id", "name", "area", "scale", "pw", "ph", "rotation")

    def __init__(self, s):
        self.id = s.id
        self.name = _s(s.name)
        self.area = _rect_out(s.area)
        self.scale = s.scale
        self.pw = s.pw
        self.ph = s.ph
        self.rotation = s.rotation

    def __repr__(self):
        a = self.area
        return "Monitor(%d, %r, %dx%d at %d,%d, scale %g)" % (self.id, self.name, a.w, a.h, a.x, a.y, self.scale)


class Event(object):
    """One input or system event from `poll()` / `events()`.

    Fields: `type` (DOWN, KEY and so on), `x` and `y` (logical), `mon`, `button` (1 left, 2 middle, 3 right), `dy` (scroll notches, +1 is down), `key`, `mods`, `text`, `id`, `msg`, `path` (the file for a DROP) and `caret` (for PREEDIT).
    """
    __slots__ = ("type", "x", "y", "mon", "button", "dy", "key", "mods", "text", "id", "msg", "raw", "path", "caret")

    def __init__(self, s, path=None, full=None):
        self.raw = s
        self.path = path
        self.type = s.type
        self.x = s.x
        self.y = s.y
        self.mon = s.mon
        self.button = s.button
        self.dy = s.dy
        self.key = s.key
        self.mods = s.mods
        self.text = _s(s.text)
        self.id = s.id
        self.msg = _s(s.msg)
        self.caret = 0
        if s.type in (TEXT, PREEDIT):
            self.text = full if full is not None else self.msg
            if s.type == PREEDIT:
                self.caret = _chars(self.text, s.id)

    @classmethod
    def make(cls, type, x=0.0, y=0.0, mon=0, button=0, dy=0, key=0, mods=0, text="", id=0, msg="", caret=None):
        """Build an event by hand, to feed or push.

        Args:
            type: an event type like KEY or DOWN.
            caret: for PREEDIT, the caret position in characters.
        TEXT, PREEDIT and DROP text has to fit in 63 bytes here.
        """
        s = _lib.EventS()
        s.type, s.x, s.y, s.mon, s.button, s.dy = int(type), x, y, int(mon), int(button), int(dy)
        s.key, s.mods, s.id = int(key), int(mods), int(id)
        if type in (TEXT, PREEDIT):
            if text and not msg:
                if len(_b(text)) > 63:
                    raise ValueError("pushed %s events hold 63 bytes at most, thats %d" % (EVENT_NAMES[type], len(_b(text))))
                msg, text = text, ""
            if type == PREEDIT and caret is not None:
                s.id = len(_b(msg[: int(caret)]))
        s.text = _cut(text, 8)
        s.msg = _cut(msg, 64)
        return cls(s, path=msg if type == DROP and msg else None)

    @property
    def name(self):
        """The event type as a word, like "motion"."""
        return EVENT_NAMES[self.type] if 0 <= self.type < len(EVENT_NAMES) else str(self.type)

    def __repr__(self):
        t = self.type
        if t in (DOWN, UP):
            more = " %.0f,%.0f button %d" % (self.x, self.y, self.button)
        elif t == MOTION:
            more = " %.0f,%.0f" % (self.x, self.y)
        elif t == SCROLL:
            more = " %.0f,%.0f dy %d" % (self.x, self.y, self.dy)
        elif t == KEY:
            more = " key %d mods %#x text %r" % (self.key, self.mods, self.text)
        elif t == HOTKEY:
            more = " id %d" % self.id
        elif t == CONTROL:
            more = " %r" % self.msg
        elif t == FOCUS:
            more = " gained" if self.id else " lost"
        elif t == DROP:
            more = " %.0f,%.0f %r" % (self.x, self.y, self.path or self.msg)
        elif t == TEXT:
            more = " %r" % self.text
        elif t == PREEDIT:
            more = " %r caret %d" % (self.text, self.caret)
        else:
            more = ""
        return "Event(%s%s)" % (self.name, more)


def _chars(text, nbytes):
    return len(_b(text)[: max(0, int(nbytes))].decode("utf-8", "ignore"))


def _cut(text, size):
    raw = _b(text or "")
    if len(raw) > size - 1:
        raw = raw[: size - 1].decode("utf-8", "ignore").encode("utf-8")
    return raw


def pixel_view(ptr, h, stride):
    """Wrap a pixel pointer in a memoryview of 32 bit ints, `h * stride` long."""
    n = h * stride
    if not ptr or n <= 0:
        return memoryview(b"").cast("I")
    arr = (c_uint32 * n).from_address(ctypes.addressof(ptr.contents))
    return memoryview(arr).cast("B").cast("I")


class Image(object):
    """A screen grab from `capture()`. `w`, `h` and `stride` are in real px (stride in pixels), `area` is where it came from, `mon` the monitor. `has_self` is True if your overlay is in it, `has_cursor` if the mouse got baked in at `cursor`. The pixels are only good until the next grab of that monitor, `copy()` them to keep them."""
    def __init__(self, g, s, gen):
        self._g = g
        self._s = s
        self._gen = gen
        self.w = s.w
        self.h = s.h
        self.stride = s.stride
        self.area = _rect_out(s.area)
        self.mon = s.mon
        self.has_self = bool(s.has_self)
        self.has_cursor = bool(s.has_cursor)
        self.cursor = _rect_out(s.cursor)

    @property
    def fresh(self):
        """True while the pixels are still valid, False once a newer grab replaced them."""
        g = self._g
        return g._g is not None and g._grabs.get(self.mon) == self._gen

    def _check(self):
        if not self.fresh:
            raise GoomeError(EGONE, "this grab is gone, a newer one replaced it. copy() it to keep the pixels")

    @property
    def pixels(self):
        """The pixels as a memoryview of 0xFFRRGGBB ints. Raises Gone if the grab is stale."""
        self._check()
        return pixel_view(self._s.px, self.h, self.stride)

    def row(self, y):
        """One row of pixels, `w` long."""
        return self.pixels[y * self.stride : y * self.stride + self.w]

    def pixel(self, x, y):
        """The 0xFFRRGGBB pixel at x, y. Raises IndexError outside the image."""
        self._check()
        if not (0 <= x < self.w and 0 <= y < self.h):
            raise IndexError("pixel %d,%d is outside %dx%d" % (x, y, self.w, self.h))
        return self._s.px[y * self.stride + x]

    def tobytes(self):
        """The pixels as bytes, without any row padding."""
        v = self.pixels
        if self.stride == self.w:
            return v.tobytes()
        s, w = self.stride, self.w
        return b"".join(v[y * s : y * s + w].tobytes() for y in range(self.h))

    def copy(self):
        """A copy of the pixels as an `array('I')` that stays valid after the next grab."""
        import array

        a = array.array("I")
        a.frombytes(self.tobytes())
        return a

    def save_ppm(self, path):
        """Write the image to a .ppm file."""
        self._check()
        rc = lib.goome_save_ppm(_b(path), self._s.px, self.w, self.h, self.stride)
        if rc != OK:
            raise error_for(rc, "couldnt write %s" % path)

    def numpy(self):
        """The pixels as a numpy uint32 array shaped (h, w), no copy. Needs numpy."""
        try:
            import numpy
        except ImportError:
            raise ImportError("numpy isnt installed, use .pixels (a memoryview) or .copy() instead")
        a = numpy.frombuffer(self.pixels, dtype=numpy.uint32).reshape(self.h, self.stride)
        return a[:, : self.w]

    def __repr__(self):
        return "Image(%dx%d of monitor %d)" % (self.w, self.h, self.mon)


class Frame(Image):
    """The last frame goome sent, from `last_frame()`. Same fields as Image, but the pixels are premultiplied argb and only good until the next `begin()`."""
    @property
    def fresh(self):
        """True while the pixels are still valid, False once a new frame was begun."""
        g = self._g
        return g._g is not None and g._began == self._gen

    def _check(self):
        if not self.fresh:
            raise GoomeError(EGONE, "this frame is gone, begin() started a new one. copy() it to keep the pixels")

    def __repr__(self):
        return "Frame(%dx%d)" % (self.w, self.h)


class Goome(object):
    """An open goome: an overlay, an app window or an offscreen surface. Use `goome.open()`, `open_app()` or `open_offscreen()` instead of calling this directly. Works as a context manager, `close()` runs at the end.

    Args:
        title: window title.
        backend: AUTO, one of the backend ids, or a name like "x11".
        state_dir: folder for the portal token and the control fifo, None for neither.
        no_capture: overlay only, never ask for screen access.
        capture_fps: capture rate for the gnome and portal streams, 0 means 5.
        hide_self: keep our overlay out of grabs where the os allows it.
        test_frames, test_script, test_shots: only for the test backend.
        mode: MODE_OVERLAY, MODE_WINDOW or MODE_OFFSCREEN (or their names).
        width, height: window or offscreen size in logical px, 0 means 960x640.
        min_width, min_height: smallest window size, 0 means none.
        window_flags: WINDOW_* flags ored together.
        scale: offscreen only, real px per logical px, 0 means 1.
    """
    def __init__(self, title=None, backend=AUTO, state_dir=None, no_capture=False, capture_fps=0, hide_self=False,
                 test_frames=None, test_script=None, test_shots=None, mode=MODE_OVERLAY, width=0, height=0,
                 min_width=0, min_height=0, window_flags=0, scale=0.0, _app=False):
        backend = _pick(backend, BACKENDS, "backend")
        mode = _pick(mode, MODES, "mode")
        self._keep = [_b(v) for v in (title, state_dir, test_frames, test_script, test_shots)]
        o = _lib.Opts()
        o.title, o.state_dir, o.test_frames, o.test_script, o.test_shots = self._keep
        o.backend = int(backend)
        o.no_capture = int(bool(no_capture))
        o.capture_fps = int(capture_fps)
        o.hide_self = int(bool(hide_self))
        o.mode, o.width, o.height = int(mode), int(width), int(height)
        o.min_width, o.min_height = int(min_width), int(min_height)
        o.window_flags, o.scale = int(window_flags), float(scale)
        self._opts = o
        self._grabs = {}
        self._began = 0
        self._uis = weakref.WeakSet()
        self._canvases = set()
        err = c_int(0)
        if _app:
            self._g = lib.goome_open_app(self._keep[0], o.width, o.height, byref(err))
        else:
            self._g = lib.goome_open(byref(o), byref(err))
        if not self._g:
            what = "an offscreen goome" if mode == MODE_OFFSCREEN else "an app window" if _app or mode == MODE_WINDOW else "an overlay"
            raise error_for(err.value or ENODISPLAY, "cant open %s: %s" % (what, strerror(err.value or ENODISPLAY)))

    def _h(self):
        if self._g is None:
            raise GoomeError(EGONE, "goome is already closed")
        return self._g

    def _check(self, rc):
        if rc < 0:
            raise error_for(rc, self.error or strerror(rc))
        return rc

    @property
    def closed(self):
        """True once close() ran."""
        return self._g is None

    def close(self):
        """Close the goome and any ui or canvas made from it. Safe to call twice."""
        if self._g is None:
            return
        for u in list(self._uis):
            u.close()
        for c in list(self._canvases):
            c._ptr = None
        self._canvases.clear()
        g, self._g = self._g, None
        lib.goome_close(g)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __del__(self):
        if getattr(self, "_g", None) is not None and lib is not None:
            self.close()

    @property
    def error(self):
        """Text for the last error goome hit, or None."""
        return _s(lib.goome_error(self._g)) if self._g else None

    @property
    def backend_name(self):
        """Name of the backend that got picked."""
        return _s(lib.goome_backend_name(self._h()))

    @property
    def caps(self):
        """Capability bits (CAP_*) this backend supports."""
        return lib.goome_caps(self._h())

    def can(self, cap):
        """True if the backend has that capability, like `g.can(CAP_CAPTURE)`."""
        return bool(self.caps & cap)

    def monitors(self):
        """List of Monitor objects, one per screen."""
        arr = (_lib.MonitorS * 32)()
        n = self._check(lib.goome_monitors(self._h(), arr, 32))
        return [Monitor(arr[i]) for i in range(min(n, 32))]

    def capture(self, mon=0, rect=None):
        """Grab a screen, or part of it, as an Image.

        Args:
            mon: monitor id.
            rect: (x, y, w, h) in logical coords, None for the whole monitor.
        Raises Again if the first frame isnt in yet, see capture_wait().
        """
        s = _lib.ImageS()
        r = _rect(rect)
        rc = lib.goome_capture(self._h(), mon, byref(r) if r is not None else None, byref(s))
        self._check(rc)
        gen = self._grabs.get(mon, 0) + 1
        self._grabs[mon] = gen
        return Image(self, s, gen)

    def capture_wait(self, mon=0, rect=None, tries=50, wait_ms=100):
        """Like capture(), but keeps retrying while the stream warms up (`tries` times, `wait_ms` apart)."""
        for i in range(tries):
            try:
                return self.capture(mon, rect)
            except Again:
                if i == tries - 1:
                    raise
                self.poll(wait_ms)

    def alpha_at(self, x, y):
        """Alpha of our own overlay at x, y (logical). Use it to mask your overlay out of an Image where `has_self` is set."""
        return lib.goome_alpha_at(self._h(), x, y)

    def begin(self, mon=0):
        """Start a frame and get a Canvas to draw on, or None if there is nothing to draw on (skip the frame). Hand it back with end()."""
        from .draw import Canvas

        p = lib.goome_begin(self._h(), mon)
        self._began += 1
        if not p:
            return None
        c = Canvas(p, self)
        self._canvases.add(c)
        return c

    def end(self, canvas, hits=None):
        """Send the canvas to the screen. `hits` are extra (x, y, w, h) rects that catch the mouse, anything else clicks through."""
        rects = list(canvas._hits)
        if hits:
            rects += [_rect(h) for h in hits]
        arr = (_lib.RectS * len(rects))(*rects) if rects else None
        p = canvas._take()
        self._canvases.discard(canvas)
        return self._check(lib.goome_end(self._h(), p, arr, len(rects)))

    def frame(self, mon=0, hits=None):
        """Context manager for one frame: `with g.frame() as c:` begins it and ends it at the end of the block."""
        return _Frame(self, mon, hits)

    def poll(self, timeout_ms=0):
        """Wait up to `timeout_ms` for the next Event and return it, or None if nothing came."""
        s = _lib.EventS()
        rc = self._check(lib.goome_poll(self._h(), byref(s), int(timeout_ms)))
        if rc <= 0:
            return None
        full = _s(lib.goome_event_text(self._g)) if s.type in (TEXT, PREEDIT) else None
        return Event(s, self.drop_path if s.type == DROP else None, full)

    def events(self, timeout_ms=0):
        """Iterate every event that is waiting, after waiting up to `timeout_ms` for the first one."""
        ev = self.poll(timeout_ms)
        while ev is not None:
            yield ev
            ev = self.poll(0)

    def pointer(self):
        """Where the mouse is as a Pointer(x, y, buttons), or None if unknown."""
        x, y, b = c_double(), c_double(), c_int()
        if not lib.goome_pointer(self._h(), byref(x), byref(y), byref(b)):
            return None
        return Pointer(x.value, y.value, b.value)

    def keyboard(self, on=True):
        """Turn keyboard input on or off."""
        self._check(lib.goome_keyboard(self._h(), int(bool(on))))

    def grab(self, on=True):
        """Overlay: take focus and the pointer until you call grab(False). Window: drags keep going outside the window."""
        self._check(lib.goome_grab(self._h(), int(bool(on))))

    @property
    def grabbed(self):
        """True while grab() is on."""
        return bool(lib.goome_grabbed(self._h()))

    def hotkey(self, combo, id):
        """Register a global hotkey. You get a HOTKEY event with this `id` when it is pressed.

        Args:
            combo: like "ctrl+shift+k".
        """
        self._check(lib.goome_hotkey(self._h(), _b(combo), int(id)))

    @property
    def control_path(self):
        """Path of the control fifo in state_dir, where `send()` writes to. None if there isnt one."""
        return _s(lib.goome_control_path(self._h()))

    def ui(self):
        """Make a Ui for this goome."""
        from .ui import Ui

        return Ui(self)

    @property
    def mode(self):
        """MODE_OVERLAY, MODE_WINDOW or MODE_OFFSCREEN."""
        return lib.goome_mode(self._h())

    def set_title(self, title):
        """Set the window title."""
        self._check(lib.goome_window_title(self._h(), _b(title)))

    title = property(lambda self: self.monitors()[0].name if self.mode != MODE_OVERLAY else None, set_title, doc="Window title. Setting it is the same as set_title().")

    @property
    def size(self):
        """Size of the monitor area as (w, h) in logical px. Set it to resize a window."""
        a = self.monitors()[0].area
        return a.w, a.h

    @size.setter
    def size(self, wh):
        self._check(lib.goome_window_size(self._h(), int(wh[0]), int(wh[1])))
        self._began += 1

    def resize(self, w, h, scale=0.0):
        """Resize an offscreen surface (with a new `scale` if you want) or a window. Size is in logical px."""
        if self.mode == MODE_OFFSCREEN:
            self._check(lib.goome_resize(self._h(), int(w), int(h), float(scale)))
        else:
            self._check(lib.goome_window_size(self._h(), int(w), int(h)))
        self._began += 1

    @property
    def pos(self):
        """Window position as (x, y). Raises NotSupported where the os wont say (wayland)."""
        x, y = c_int(), c_int()
        self._check(lib.goome_window_pos(self._h(), byref(x), byref(y), 0))
        return x.value, y.value

    @pos.setter
    def pos(self, xy):
        x, y = c_int(int(xy[0])), c_int(int(xy[1]))
        self._check(lib.goome_window_pos(self._h(), byref(x), byref(y), 1))

    @property
    def state(self):
        """Window state, one of the STATE_* constants or their names. Set it to change it."""
        return self._check(lib.goome_window_get_state(self._h()))

    @state.setter
    def state(self, st):
        self._check(lib.goome_window_state(self._h(), _pick(st, STATES, "window state")))

    def minimize(self):
        """Minimize the window."""
        self.state = STATE_MINIMIZED

    def maximize(self):
        """Maximize the window, or restore it if it already is."""
        self.state = STATE_NORMAL if self.state == STATE_MAXIMIZED else STATE_MAXIMIZED

    def fullscreen(self, on=True):
        """Go fullscreen, or back to normal with `False`."""
        self.state = STATE_FULLSCREEN if on else STATE_NORMAL

    def drag(self, edges=0):
        """Start a native window move (0) or resize (EDGE_* bits ored together) from the mouse press happening right now."""
        self._check(lib.goome_window_drag(self._h(), int(edges)))

    def show(self, on=True):
        """Show the window, or hide it with `False`."""
        self._check(lib.goome_window_show(self._h(), int(bool(on))))

    def hide(self):
        """Hide the window."""
        self.show(False)

    @property
    def cursor(self):
        """The last cursor shape asked for. Set it to a CURSOR_* id or a name like "hand"."""
        return lib.goome_cursor_shape(self._h())

    @cursor.setter
    def cursor(self, shape):
        self._check(lib.goome_cursor(self._h(), _pick(shape, CURSORS, "cursor")))

    @property
    def clipboard(self):
        """Clipboard text. Reading can block for about 250ms on x11 and wayland."""
        n = self._check(lib.goome_clipboard_get(self._h(), None, 0))
        while True:
            buf = ctypes.create_string_buffer(n + 1)
            m = self._check(lib.goome_clipboard_get(self._h(), buf, n + 1))
            if m <= n:
                return buf.raw[:m].decode("utf-8", "replace")
            n = m

    @clipboard.setter
    def clipboard(self, text):
        self._check(lib.goome_clipboard_set(self._h(), _b(text or "")))

    @property
    def drop_path(self):
        """Full path of the last file dropped on the window, good until the next poll."""
        return _s(lib.goome_drop_path(self._h()))

    def push(self, ev, **fields):
        """Queue an event so poll() hands it back, in any mode. Pass an Event, or a type plus fields like `g.push(KEY, key=13)`."""
        if not isinstance(ev, Event):
            ev = Event.make(ev, **fields)
        elif fields:
            raise TypeError("pass an Event or a type with fields, not both")
        self._check(lib.goome_push(self._h(), byref(ev.raw)))

    def push_text(self, text):
        """Queue key events that type this text."""
        for ch in text:
            k = ord(ch)
            self.push(KEY, key=k if k < 128 else 0, text=ch)

    def push_commit(self, text):
        """Queue a TEXT event, as if an ime finished composing it."""
        self.push(TEXT, text=text)

    def push_preedit(self, text, caret=None):
        """Queue a PREEDIT event, as if an ime is still composing. `caret` is a character index, the end by default."""
        self.push(PREEDIT, text=text, caret=len(text) if caret is None else caret)

    @property
    def event_text(self):
        """Full text of the last TEXT or PREEDIT event, with no length cut."""
        return _s(lib.goome_event_text(self._h()))

    @property
    def preedit_cursor(self):
        """Caret position, in characters, in the last PREEDIT text."""
        return _chars(self.event_text, lib.goome_preedit_cursor(self._h()))

    def text_input(self, on=True, caret=None):
        """Turn ime input on or off. `caret` is an (x, y, w, h) rect in logical coords, where the candidate window goes."""
        r = _rect(caret)
        self._check(lib.goome_text_input(self._h(), int(bool(on)), byref(r) if r is not None else None))

    def push_click(self, x, y, button=1):
        """Queue a mouse move, press and release at x, y. Handy in tests."""
        self.push(MOTION, x=x, y=y)
        self.push(DOWN, x=x, y=y, button=button)
        self.push(UP, x=x, y=y, button=button)

    def last_frame(self):
        """The last frame `end()` sent, as a Frame."""
        s = _lib.ImageS()
        self._check(lib.goome_frame(self._h(), byref(s)))
        return Frame(self, s, self._began)

    def hit(self, x, y):
        """True if x, y (logical) is inside the hit rects of the last frame."""
        return bool(lib.goome_hit(self._h(), x, y))

    def frame_dirty(self):
        """Rect (real px) that changed since the last call, or None if nothing did. The first call after open or resize is the whole frame."""
        r = _lib.RectS()
        if not lib.goome_frame_dirty(self._h(), byref(r)):
            return None
        return _rect_out(r)

    def frame_copy(self, buf=None, stride=None, fmt=FMT_BGRA_PREMUL, rect=None):
        """Copy part of the last frame into a buffer and return it.

        Args:
            buf: a writable bytearray or similar, None makes one.
            stride: bytes per row in buf, defaults to the rect width times 4.
            fmt: one of the FMT_* pixel formats.
            rect: (x, y, w, h) in real px, None for the whole frame.
        """
        if rect is None:
            f = self.last_frame()
            rect = Rect(0, 0, f.w, f.h)
        r = _rect(rect)
        if r.w <= 0 or r.h <= 0:
            raise ValueError("cant copy an empty rect %r" % (tuple(rect),))
        stride = r.w * 4 if stride is None else int(stride)
        if stride < r.w * 4:
            raise ValueError("stride %d is too small for %d px" % (stride, r.w))
        need = (r.h - 1) * stride + r.w * 4
        if buf is None:
            buf = bytearray(r.h * stride)
        mv = memoryview(buf)
        if mv.readonly or not mv.c_contiguous:
            raise ValueError("frame_copy needs a writable contiguous buffer, like a bytearray")
        mv = mv.cast("B")
        if mv.nbytes < need:
            raise ValueError("buffer has %d bytes, %d px x %d rows at stride %d needs %d" % (mv.nbytes, r.w, r.h, stride, need))
        dst = (ctypes.c_char * mv.nbytes).from_buffer(mv)
        self._check(lib.goome_frame_copy(self._h(), dst, stride, int(fmt), byref(r)))
        return buf

    def __repr__(self):
        if self._g is None:
            return "Goome(closed)"
        return "Goome(%s)" % self.backend_name


class _Frame(object):
    def __init__(self, g, mon, hits):
        self.g, self.mon, self.hits, self.c = g, mon, hits, None

    def __enter__(self):
        self.c = self.g.begin(self.mon)
        return self.c

    def __exit__(self, et, ev, tb):
        if self.c is not None and self.c._ptr is not None:
            self.g.end(self.c, self.hits)
        return False


def _pick(v, names, what):
    if isinstance(v, str):
        if v.lower() not in names:
            raise ValueError("no %s called %r, pick one of %s" % (what, v, ", ".join(names)))
        return names[v.lower()]
    return int(v)


def open(title=None, **kw):
    """Open an overlay. Takes the same keyword args as Goome, like `backend=` and `no_capture=`."""
    return Goome(title, **kw)


def open_app(title="goome", width=960, height=640, **kw):
    """Open a normal window, resizable and centered unless you pass `window_flags`."""
    if kw:
        kw.setdefault("window_flags", WINDOW_RESIZABLE | WINDOW_CENTER)
        return Goome(title, mode=MODE_WINDOW, width=width, height=height, **kw)
    return Goome(title, mode=MODE_WINDOW, width=width, height=height, _app=True)


def open_offscreen(width=960, height=640, scale=1.0, title=None, **kw):
    """Open an offscreen surface with no window, for rendering to pixels. `scale` is real px per logical px."""
    return Goome(title, mode=MODE_OFFSCREEN, width=width, height=height, scale=scale, **kw)


def parse_combo(combo):
    """Turn a combo like "ctrl+shift+k" into `(key, mods)`. Raises BadArg if it cant read it."""
    k, m = c_int(), c_int()
    rc = lib.goome_parse_combo(_b(combo), byref(k), byref(m))
    if rc != OK:
        raise error_for(rc, "cant read the combo %r" % combo)
    return k.value, m.value


def send(state_dir, msg):
    """Send a line to the control fifo in `state_dir`, so another goome app can act on it (shows up as a CONTROL event)."""
    rc = lib.goome_send(_b(state_dir), _b(msg))
    if rc != OK:
        raise error_for(rc, "couldnt send %r to %s: %s" % (msg, state_dir, strerror(rc)))


def now_ms():
    """Milliseconds on goome's clock, handy for timing."""
    return lib.goome_now_ms()


class Pacer(object):
    """Frame pacing. Call `wait()` once per loop and use what it returns as the poll timeout, see wait()."""
    def __init__(self, fps=60):
        self.fps = fps
        self._s = _lib.PacerS()

    def wait(self, fps=None):
        """Milliseconds until the next frame is due at `fps` (the pacer's own if not given). Returns 0 when it is time to draw, so pass it to `poll()` and it wont wait longer than that."""
        return lib.goome_pace(byref(self._s), int(fps if fps is not None else self.fps))


def u32_buffer(data, n):
    """Turn pixel data (bytes, array, ctypes array, list of ints or an Image) into a 32 bit buffer of `n` pixels."""
    if isinstance(data, Image):
        data = data.tobytes()
    if isinstance(data, ctypes.Array) and ctypes.sizeof(data) >= n * 4:
        return ctypes.cast(data, ctypes.POINTER(c_uint32)), data
    try:
        mv = memoryview(data)
    except TypeError:
        arr = (c_uint32 * n)(*[int(v) & 0xFFFFFFFF for v in data])
        return arr, arr
    if mv.nbytes < n * 4:
        raise ValueError("need %d pixels, got %d bytes" % (n, mv.nbytes))
    if not mv.c_contiguous:
        mv = memoryview(mv.tobytes())
    if mv.readonly:
        arr = (c_uint32 * n).from_buffer_copy(mv.cast("B")[: n * 4])
    else:
        arr = (c_uint32 * n).from_buffer(mv.cast("B"))
    return arr, (arr, data)


def save_ppm(path, pixels, w, h, stride=None):
    """Write 0xFFRRGGBB pixels to a .ppm file.

    Args:
        stride: pixels per row, defaults to `w`.
    """
    stride = w if stride is None else stride
    arr, keep = u32_buffer(pixels, (h - 1) * stride + w if h > 0 else 0)
    rc = lib.goome_save_ppm(_b(path), ctypes.cast(arr, ctypes.POINTER(c_uint32)), w, h, stride)
    if rc != OK:
        raise error_for(rc, "couldnt write %s" % path)
