import ctypes
import weakref
from collections import namedtuple
from ctypes import byref, c_double, c_int, c_uint32

from . import _lib
from ._lib import lib

AUTO, WAYLAND, GNOME, PORTAL, X11, WIN32, MACOS, TEST, OFFSCREEN = range(9)
BACKENDS = {"auto": AUTO, "wayland": WAYLAND, "gnome": GNOME, "portal": PORTAL, "x11": X11, "win32": WIN32, "macos": MACOS, "test": TEST,
            "offscreen": OFFSCREEN}

MODE_OVERLAY, MODE_WINDOW, MODE_OFFSCREEN = range(3)
MODES = {"overlay": MODE_OVERLAY, "window": MODE_WINDOW, "app": MODE_WINDOW, "offscreen": MODE_OFFSCREEN}

WINDOW_RESIZABLE = 1
WINDOW_BORDERLESS = 2
WINDOW_TRANSPARENT = 4
WINDOW_ON_TOP = 8
WINDOW_HIDDEN = 16
WINDOW_CENTER = 32
WINDOW_NO_TITLEBAR = 64
WINDOW_NO_CONSOLE = 128

OK = 0
ENOTSUP = -1
EDENIED = -2
ENODISPLAY = -3
EGONE = -4
EAGAIN = -5
ENOMEM = -6
EARG = -7

CAP_CAPTURE = 1
CAP_GLOBAL_POINTER = 2
CAP_HOTKEYS = 4
CAP_HIDE_SELF = 8
CAP_KEYBOARD = 16
CAP_WINDOW = 32
CAP_CLIPBOARD = 64
CAP_CURSOR = 128
CAP_GRAB = 256

WANT_MOUSE = 1
WANT_KEYBOARD = 2

FMT_BGRA_PREMUL, FMT_RGBA_PREMUL, FMT_BGRA, FMT_RGBA = range(4)

NONE, DOWN, UP, MOTION, SCROLL, KEY, HOTKEY, CONTROL, MONITORS, QUIT, CLOSE, FOCUS, DROP, TEXT, PREEDIT = range(15)
EVENT_NAMES = ("none", "down", "up", "motion", "scroll", "key", "hotkey", "control", "monitors", "quit", "close", "focus", "drop", "text",
               "preedit")

(CURSOR_ARROW, CURSOR_IBEAM, CURSOR_HAND, CURSOR_MOVE, CURSOR_RESIZE_EW, CURSOR_RESIZE_NS, CURSOR_RESIZE_NWSE, CURSOR_RESIZE_NESW,
 CURSOR_WAIT, CURSOR_NO, CURSOR_HIDDEN) = range(11)
CURSOR_NAMES = ("arrow", "ibeam", "hand", "move", "resize_ew", "resize_ns", "resize_nwse", "resize_nesw", "wait", "no", "hidden")
CURSORS = dict((n, i) for i, n in enumerate(CURSOR_NAMES))

EDGE_LEFT = 1
EDGE_RIGHT = 2
EDGE_TOP = 4
EDGE_BOTTOM = 8

STATE_NORMAL, STATE_MINIMIZED, STATE_MAXIMIZED, STATE_FULLSCREEN = range(4)
STATES = {"normal": STATE_NORMAL, "minimized": STATE_MINIMIZED, "maximized": STATE_MAXIMIZED, "fullscreen": STATE_FULLSCREEN}

K_BACKSPACE = 8
K_TAB = 9
K_ENTER = 13
K_ESC = 27
K_SPACE = 32
K_DELETE = 127
K_F1 = 0x81
K_F12 = 0x8C
K_LEFT, K_RIGHT, K_UP, K_DOWN, K_HOME, K_END, K_PGUP, K_PGDN, K_INSERT = range(0x90, 0x99)

SHIFT = 0x100
CTRL = 0x200
ALT = 0x400
SUPER = 0x800

VERSION = "0.5.5"

Rect = namedtuple("Rect", "x y w h")
Pointer = namedtuple("Pointer", "x y buttons")


class GoomeError(Exception):
    def __init__(self, code, message=None):
        self.code = code
        self.message = message or strerror(code)
        super().__init__(self.message)


class NotSupported(GoomeError):
    pass


class Denied(GoomeError):
    pass


class NoDisplay(GoomeError):
    pass


class Gone(GoomeError):
    pass


class Again(GoomeError):
    pass


class NoMemory(GoomeError):
    pass


class BadArg(GoomeError):
    pass


ERRORS = {ENOTSUP: NotSupported, EDENIED: Denied, ENODISPLAY: NoDisplay, EGONE: Gone, EAGAIN: Again, ENOMEM: NoMemory, EARG: BadArg}


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
    return _s(lib.goome_strerror(code)) or "error %d" % code


def error_for(code, message=None):
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
    n = h * stride
    if not ptr or n <= 0:
        return memoryview(b"").cast("I")
    arr = (c_uint32 * n).from_address(ctypes.addressof(ptr.contents))
    return memoryview(arr).cast("B").cast("I")


class Image(object):
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
        g = self._g
        return g._g is not None and g._grabs.get(self.mon) == self._gen

    def _check(self):
        if not self.fresh:
            raise GoomeError(EGONE, "this grab is gone, a newer one replaced it. copy() it to keep the pixels")

    @property
    def pixels(self):
        self._check()
        return pixel_view(self._s.px, self.h, self.stride)

    def row(self, y):
        return self.pixels[y * self.stride : y * self.stride + self.w]

    def pixel(self, x, y):
        self._check()
        if not (0 <= x < self.w and 0 <= y < self.h):
            raise IndexError("pixel %d,%d is outside %dx%d" % (x, y, self.w, self.h))
        return self._s.px[y * self.stride + x]

    def tobytes(self):
        v = self.pixels
        if self.stride == self.w:
            return v.tobytes()
        s, w = self.stride, self.w
        return b"".join(v[y * s : y * s + w].tobytes() for y in range(self.h))

    def copy(self):
        import array

        a = array.array("I")
        a.frombytes(self.tobytes())
        return a

    def save_ppm(self, path):
        self._check()
        rc = lib.goome_save_ppm(_b(path), self._s.px, self.w, self.h, self.stride)
        if rc != OK:
            raise error_for(rc, "couldnt write %s" % path)

    def numpy(self):
        try:
            import numpy
        except ImportError:
            raise ImportError("numpy isnt installed, use .pixels (a memoryview) or .copy() instead")
        a = numpy.frombuffer(self.pixels, dtype=numpy.uint32).reshape(self.h, self.stride)
        return a[:, : self.w]

    def __repr__(self):
        return "Image(%dx%d of monitor %d)" % (self.w, self.h, self.mon)


class Frame(Image):
    @property
    def fresh(self):
        g = self._g
        return g._g is not None and g._began == self._gen

    def _check(self):
        if not self.fresh:
            raise GoomeError(EGONE, "this frame is gone, begin() started a new one. copy() it to keep the pixels")

    def __repr__(self):
        return "Frame(%dx%d)" % (self.w, self.h)


class Goome(object):
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
        return self._g is None

    def close(self):
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
        return _s(lib.goome_error(self._g)) if self._g else None

    @property
    def backend_name(self):
        return _s(lib.goome_backend_name(self._h()))

    @property
    def caps(self):
        return lib.goome_caps(self._h())

    def can(self, cap):
        return bool(self.caps & cap)

    def monitors(self):
        arr = (_lib.MonitorS * 32)()
        n = self._check(lib.goome_monitors(self._h(), arr, 32))
        return [Monitor(arr[i]) for i in range(min(n, 32))]

    def capture(self, mon=0, rect=None):
        s = _lib.ImageS()
        r = _rect(rect)
        rc = lib.goome_capture(self._h(), mon, byref(r) if r is not None else None, byref(s))
        self._check(rc)
        gen = self._grabs.get(mon, 0) + 1
        self._grabs[mon] = gen
        return Image(self, s, gen)

    def capture_wait(self, mon=0, rect=None, tries=50, wait_ms=100):
        for i in range(tries):
            try:
                return self.capture(mon, rect)
            except Again:
                if i == tries - 1:
                    raise
                self.poll(wait_ms)

    def alpha_at(self, x, y):
        return lib.goome_alpha_at(self._h(), x, y)

    def begin(self, mon=0):
        from .draw import Canvas

        p = lib.goome_begin(self._h(), mon)
        self._began += 1
        if not p:
            return None
        c = Canvas(p, self)
        self._canvases.add(c)
        return c

    def end(self, canvas, hits=None):
        rects = list(canvas._hits)
        if hits:
            rects += [_rect(h) for h in hits]
        arr = (_lib.RectS * len(rects))(*rects) if rects else None
        p = canvas._take()
        self._canvases.discard(canvas)
        return self._check(lib.goome_end(self._h(), p, arr, len(rects)))

    def frame(self, mon=0, hits=None):
        return _Frame(self, mon, hits)

    def poll(self, timeout_ms=0):
        s = _lib.EventS()
        rc = self._check(lib.goome_poll(self._h(), byref(s), int(timeout_ms)))
        if rc <= 0:
            return None
        full = _s(lib.goome_event_text(self._g)) if s.type in (TEXT, PREEDIT) else None
        return Event(s, self.drop_path if s.type == DROP else None, full)

    def events(self, timeout_ms=0):
        ev = self.poll(timeout_ms)
        while ev is not None:
            yield ev
            ev = self.poll(0)

    def pointer(self):
        x, y, b = c_double(), c_double(), c_int()
        if not lib.goome_pointer(self._h(), byref(x), byref(y), byref(b)):
            return None
        return Pointer(x.value, y.value, b.value)

    def keyboard(self, on=True):
        self._check(lib.goome_keyboard(self._h(), int(bool(on))))

    def grab(self, on=True):
        self._check(lib.goome_grab(self._h(), int(bool(on))))

    @property
    def grabbed(self):
        return bool(lib.goome_grabbed(self._h()))

    def hotkey(self, combo, id):
        self._check(lib.goome_hotkey(self._h(), _b(combo), int(id)))

    @property
    def control_path(self):
        return _s(lib.goome_control_path(self._h()))

    def ui(self):
        from .ui import Ui

        return Ui(self)

    @property
    def mode(self):
        return lib.goome_mode(self._h())

    def set_title(self, title):
        self._check(lib.goome_window_title(self._h(), _b(title)))

    title = property(lambda self: self.monitors()[0].name if self.mode != MODE_OVERLAY else None, set_title)

    @property
    def size(self):
        a = self.monitors()[0].area
        return a.w, a.h

    @size.setter
    def size(self, wh):
        self._check(lib.goome_window_size(self._h(), int(wh[0]), int(wh[1])))

    def resize(self, w, h, scale=0.0):
        if self.mode == MODE_OFFSCREEN:
            self._check(lib.goome_resize(self._h(), int(w), int(h), float(scale)))
        else:
            self._check(lib.goome_window_size(self._h(), int(w), int(h)))

    @property
    def pos(self):
        x, y = c_int(), c_int()
        self._check(lib.goome_window_pos(self._h(), byref(x), byref(y), 0))
        return x.value, y.value

    @pos.setter
    def pos(self, xy):
        x, y = c_int(int(xy[0])), c_int(int(xy[1]))
        self._check(lib.goome_window_pos(self._h(), byref(x), byref(y), 1))

    @property
    def state(self):
        return self._check(lib.goome_window_get_state(self._h()))

    @state.setter
    def state(self, st):
        self._check(lib.goome_window_state(self._h(), _pick(st, STATES, "window state")))

    def minimize(self):
        self.state = STATE_MINIMIZED

    def maximize(self):
        self.state = STATE_NORMAL if self.state == STATE_MAXIMIZED else STATE_MAXIMIZED

    def fullscreen(self, on=True):
        self.state = STATE_FULLSCREEN if on else STATE_NORMAL

    def drag(self, edges=0):
        self._check(lib.goome_window_drag(self._h(), int(edges)))

    def show(self, on=True):
        self._check(lib.goome_window_show(self._h(), int(bool(on))))

    def hide(self):
        self.show(False)

    @property
    def cursor(self):
        return lib.goome_cursor_shape(self._h())

    @cursor.setter
    def cursor(self, shape):
        self._check(lib.goome_cursor(self._h(), _pick(shape, CURSORS, "cursor")))

    @property
    def clipboard(self):
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
        return _s(lib.goome_drop_path(self._h()))

    def push(self, ev, **fields):
        if not isinstance(ev, Event):
            ev = Event.make(ev, **fields)
        elif fields:
            raise TypeError("pass an Event or a type with fields, not both")
        self._check(lib.goome_push(self._h(), byref(ev.raw)))

    def push_text(self, text):
        for ch in text:
            k = ord(ch)
            self.push(KEY, key=k if k < 128 else 0, text=ch)

    def push_commit(self, text):
        self.push(TEXT, text=text)

    def push_preedit(self, text, caret=None):
        self.push(PREEDIT, text=text, caret=len(text) if caret is None else caret)

    @property
    def event_text(self):
        return _s(lib.goome_event_text(self._h()))

    @property
    def preedit_cursor(self):
        return _chars(self.event_text, lib.goome_preedit_cursor(self._h()))

    def text_input(self, on=True, caret=None):
        r = _rect(caret)
        self._check(lib.goome_text_input(self._h(), int(bool(on)), byref(r) if r is not None else None))

    def push_click(self, x, y, button=1):
        self.push(MOTION, x=x, y=y)
        self.push(DOWN, x=x, y=y, button=button)
        self.push(UP, x=x, y=y, button=button)

    def last_frame(self):
        s = _lib.ImageS()
        self._check(lib.goome_frame(self._h(), byref(s)))
        return Frame(self, s, self._began)

    def hit(self, x, y):
        return bool(lib.goome_hit(self._h(), x, y))

    def frame_dirty(self):
        r = _lib.RectS()
        if not lib.goome_frame_dirty(self._h(), byref(r)):
            return None
        return _rect_out(r)

    def frame_copy(self, buf=None, stride=None, fmt=FMT_BGRA_PREMUL, rect=None):
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
    return Goome(title, **kw)


def open_app(title="goome", width=960, height=640, **kw):
    if kw:
        kw.setdefault("window_flags", WINDOW_RESIZABLE | WINDOW_CENTER)
        return Goome(title, mode=MODE_WINDOW, width=width, height=height, **kw)
    return Goome(title, mode=MODE_WINDOW, width=width, height=height, _app=True)


def open_offscreen(width=960, height=640, scale=1.0, title=None, **kw):
    return Goome(title, mode=MODE_OFFSCREEN, width=width, height=height, scale=scale, **kw)


def parse_combo(combo):
    k, m = c_int(), c_int()
    rc = lib.goome_parse_combo(_b(combo), byref(k), byref(m))
    if rc != OK:
        raise error_for(rc, "cant read the combo %r" % combo)
    return k.value, m.value


def send(state_dir, msg):
    rc = lib.goome_send(_b(state_dir), _b(msg))
    if rc != OK:
        raise error_for(rc, "couldnt send %r to %s: %s" % (msg, state_dir, strerror(rc)))


def now_ms():
    return lib.goome_now_ms()


class Pacer(object):
    def __init__(self, fps=60):
        self.fps = fps
        self._s = _lib.PacerS()

    def wait(self, fps=None):
        return lib.goome_pace(byref(self._s), int(fps if fps is not None else self.fps))


def u32_buffer(data, n):
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
    stride = w if stride is None else stride
    arr, keep = u32_buffer(pixels, (h - 1) * stride + w if h > 0 else 0)
    rc = lib.goome_save_ppm(_b(path), ctypes.cast(arr, ctypes.POINTER(c_uint32)), w, h, stride)
    if rc != OK:
        raise error_for(rc, "couldnt write %s" % path)
