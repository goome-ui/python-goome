import ctypes
import weakref
from collections import namedtuple
from ctypes import byref, c_double, c_int, c_uint32

from . import _lib
from ._lib import lib

AUTO, WAYLAND, GNOME, PORTAL, X11, WIN32, MACOS, TEST = range(8)
BACKENDS = {"auto": AUTO, "wayland": WAYLAND, "gnome": GNOME, "portal": PORTAL, "x11": X11, "win32": WIN32, "macos": MACOS, "test": TEST}

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

NONE, DOWN, UP, MOTION, SCROLL, KEY, HOTKEY, CONTROL, MONITORS, QUIT = range(10)
EVENT_NAMES = ("none", "down", "up", "motion", "scroll", "key", "hotkey", "control", "monitors", "quit")

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

VERSION = "0.1.0"

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
    __slots__ = ("type", "x", "y", "mon", "button", "dy", "key", "mods", "text", "id", "msg", "raw")

    def __init__(self, s):
        self.raw = s
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
        else:
            more = ""
        return "Event(%s%s)" % (self.name, more)


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
            raise GoomeError(EGONE, "this grab got replaced by a newer one of the same monitor (or goome got closed), use copy() to keep pixels")

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

    def __repr__(self):
        return "Image(%dx%d of monitor %d)" % (self.w, self.h, self.mon)


class Goome(object):
    def __init__(self, title=None, backend=AUTO, state_dir=None, no_capture=False, capture_fps=0, hide_self=False,
                 test_frames=None, test_script=None, test_shots=None):
        if isinstance(backend, str):
            if backend.lower() not in BACKENDS:
                raise ValueError("no backend called %r, pick one of %s" % (backend, ", ".join(BACKENDS)))
            backend = BACKENDS[backend.lower()]
        self._keep = [_b(v) for v in (title, state_dir, test_frames, test_script, test_shots)]
        o = _lib.Opts()
        o.title, o.state_dir, o.test_frames, o.test_script, o.test_shots = self._keep
        o.backend = int(backend)
        o.no_capture = int(bool(no_capture))
        o.capture_fps = int(capture_fps)
        o.hide_self = int(bool(hide_self))
        self._opts = o
        self._grabs = {}
        self._uis = weakref.WeakSet()
        self._canvases = set()
        err = c_int(0)
        self._g = lib.goome_open(byref(o), byref(err))
        if not self._g:
            raise error_for(err.value or ENODISPLAY, "cant open an overlay: %s" % strerror(err.value or ENODISPLAY))

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
        try:
            self.close()
        except Exception:
            pass

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
        return Event(s) if rc > 0 else None

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

    def hotkey(self, combo, id):
        self._check(lib.goome_hotkey(self._h(), _b(combo), int(id)))

    @property
    def control_path(self):
        return _s(lib.goome_control_path(self._h()))

    def ui(self):
        from .ui import Ui

        return Ui(self)

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


def open(title=None, **kw):
    return Goome(title, **kw)


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

    __call__ = wait


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
