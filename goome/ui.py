import ctypes
from ctypes import byref, c_char_p, c_double, c_int, c_uint32

from . import _lib
from ._lib import lib
from .core import EGONE, ENOMEM, GoomeError, _b, _s
from .draw import Canvas, Font

WIN_MOVE = 1
WIN_RESIZE = 2
WIN_COLLAPSE = 4
WIN_NO_TITLE = 8
WIN_CLOSE = 16


def _theme_prop(name):
    def get(self):
        return getattr(self._t(), name)

    def put(self, v):
        if name in _lib.THEME_COLORS:
            v = int(v) & 0xFFFFFFFF
        setattr(self._t(), name, v)

    return property(get, put)


class Theme(object):
    def __init__(self, ui):
        self._ui = ui
        self._font = None
        self._own_font = None

    def _t(self):
        return self._ui._theme_ptr().contents

    def dark(self):
        lib.goome_ui_theme_dark(self._ui._theme_ptr())

    def light(self):
        lib.goome_ui_theme_light(self._ui._theme_ptr())

    @property
    def font(self):
        p = self._t().font
        if not p:
            return None
        if self._font is not None and self._font._f == p:
            return self._font
        if self._own_font is None or self._own_font._f != p:
            self._own_font = Font(p, owned=False)
        return self._own_font

    @font.setter
    def font(self, f):
        if self._font is not None:
            self._font._themes.discard(self)
        if f is None:
            self._t().font = None
            self._font = None
            return
        if f is self._own_font:
            self._t().font = f._h()
            self._font = None
            return
        self._t().font = f._h()
        self._font = f
        f._themes.add(self)

    def as_dict(self):
        t = self._t()
        return dict((n, getattr(t, n)) for n in _lib.THEME_COLORS + _lib.THEME_SIZES)

    def update(self, **kw):
        for k, v in kw.items():
            if k not in _lib.THEME_COLORS + _lib.THEME_SIZES + ("font",):
                raise AttributeError("theme has no %r" % k)
            setattr(self, k, v)

    def __setattr__(self, k, v):
        if not k.startswith("_") and not hasattr(type(self), k):
            raise AttributeError("theme has no %r" % k)
        object.__setattr__(self, k, v)


for _n in _lib.THEME_COLORS + _lib.THEME_SIZES:
    setattr(Theme, _n, _theme_prop(_n))


class Window(object):
    def __init__(self, x=40, y=40, w=300, h=0, open=True):
        self._x, self._y, self._w, self._h = c_double(x), c_double(y), c_double(w), c_double(h)
        self._open = c_int(int(bool(open)))

    x = property(lambda s: s._x.value, lambda s, v: setattr(s._x, "value", v))
    y = property(lambda s: s._y.value, lambda s, v: setattr(s._y, "value", v))
    w = property(lambda s: s._w.value, lambda s, v: setattr(s._w, "value", v))
    h = property(lambda s: s._h.value, lambda s, v: setattr(s._h, "value", v))
    open = property(lambda s: bool(s._open.value), lambda s, v: setattr(s._open, "value", int(bool(v))))

    def __repr__(self):
        return "Window(%g, %g, %g, %g%s)" % (self.x, self.y, self.w, self.h, "" if self.open else ", closed")


class Shown(object):
    def __init__(self, shown, end):
        self.shown = bool(shown)
        self._end = end

    def __bool__(self):
        return self.shown

    def __enter__(self):
        return self.shown

    def __exit__(self, *a):
        self._end()
        return False


def _strs(items):
    bs = [_b(i) for i in items]
    return (c_char_p * max(1, len(bs)))(*bs), len(bs)


class Ui(object):
    def __init__(self, g):
        self._g = g
        self._u = lib.goome_ui_new(g._h())
        if not self._u:
            raise GoomeError(ENOMEM, "no memory for the ui")
        g._uis.add(self)
        self.changed = False
        self.theme = Theme(self)
        self._canvas = None

    def _h(self):
        if self._u is None:
            raise GoomeError(EGONE, "this ui is closed")
        return self._u

    def _theme_ptr(self):
        return lib.goome_ui_theme(self._h())

    @property
    def closed(self):
        return self._u is None

    def close(self):
        if self._u is None:
            return
        if self.theme._font is not None:
            self.theme._font._themes.discard(self.theme)
            self.theme._font = None
        u, self._u = self._u, None
        if self._canvas is not None:
            self._canvas._ptr = None
        lib.goome_ui_free(u)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __del__(self):
        try:
            if self._g._g is not None:
                self.close()
        except Exception:
            pass

    def feed(self, ev):
        return bool(lib.goome_ui_feed(self._h(), byref(ev.raw)))

    def begin(self, mon=0):
        p = lib.goome_ui_begin(self._h(), mon)
        if not p:
            self._canvas = None
            return None
        self._canvas = Canvas(p, self._g)
        return self._canvas

    def end(self):
        lib.goome_ui_end(self._h())
        if self._canvas is not None:
            self._canvas._ptr = None
            self._canvas = None

    def frame(self, mon=0):
        return _UiFrame(self, mon)

    def hit(self, x, y, w, h):
        lib.goome_ui_hit(self._h(), x, y, w, h)

    @property
    def animating(self):
        return bool(lib.goome_ui_animating(self._h()))

    def window(self, title, win, flags=WIN_MOVE | WIN_COLLAPSE):
        r = lib.goome_ui_window(self._h(), _b(title), byref(win._x), byref(win._y), byref(win._w), byref(win._h), int(flags), byref(win._open))
        return Shown(r, self.window_end)

    def window_end(self):
        lib.goome_ui_window_end(self._h())

    def row(self, cols):
        lib.goome_ui_row(self._h(), int(cols))

    def same_line(self):
        lib.goome_ui_same_line(self._h())

    def space(self, px):
        lib.goome_ui_space(self._h(), px)

    def separator(self):
        lib.goome_ui_separator(self._h())

    def width(self, w):
        lib.goome_ui_width(self._h(), w)

    def label(self, text):
        lib.goome_ui_label(self._h(), b"%s", c_char_p(_b(text)))

    def heading(self, text):
        lib.goome_ui_heading(self._h(), _b(text))

    def wrapped(self, text):
        lib.goome_ui_wrapped(self._h(), _b(text))

    def button(self, label):
        r = bool(lib.goome_ui_button(self._h(), _b(label)))
        self.changed = r
        return r

    def image_button(self, id, bmp, w, h):
        r = bool(lib.goome_ui_image_button(self._h(), _b(id), bmp._ref(), w, h))
        self.changed = r
        return r

    def image(self, bmp, w, h, radius=0):
        lib.goome_ui_image(self._h(), bmp._ref(), w, h, radius)

    def _flag(self, fn, label, value):
        v = c_int(int(bool(value)))
        self.changed = bool(fn(self._h(), _b(label), byref(v)))
        return bool(v.value)

    def checkbox(self, label, value):
        return self._flag(lib.goome_ui_checkbox, label, value)

    def toggle(self, label, value):
        return self._flag(lib.goome_ui_toggle, label, value)

    def radio(self, label, value, option):
        v = c_int(int(value))
        self.changed = bool(lib.goome_ui_radio(self._h(), _b(label), byref(v), int(option)))
        return v.value

    def slider(self, label, value, lo=0.0, hi=1.0, fmt=None):
        v = c_double(value)
        self.changed = bool(lib.goome_ui_slider(self._h(), _b(label), byref(v), lo, hi, _b(fmt)))
        return v.value

    def slider_int(self, label, value, lo=0, hi=100):
        v = c_int(int(value))
        self.changed = bool(lib.goome_ui_slider_int(self._h(), _b(label), byref(v), int(lo), int(hi)))
        return v.value

    def input(self, label, text, cap=256):
        raw = _b(text or "")
        if len(raw) > cap - 1:
            raw = raw[: cap - 1].decode("utf-8", "ignore").encode("utf-8")
        buf = ctypes.create_string_buffer(raw, cap)
        self.changed = bool(lib.goome_ui_input(self._h(), _b(label), buf, cap))
        return _s(buf.value)

    def combo(self, label, sel, items):
        arr, n = _strs(items)
        v = c_int(int(sel))
        self.changed = bool(lib.goome_ui_combo(self._h(), _b(label), byref(v), arr, n))
        return v.value

    def selectable(self, label, selected=False):
        r = bool(lib.goome_ui_selectable(self._h(), _b(label), int(bool(selected))))
        self.changed = r
        return r

    def tabs(self, id, names, sel):
        arr, n = _strs(names)
        v = c_int(int(sel))
        self.changed = bool(lib.goome_ui_tabs(self._h(), _b(id), arr, n, byref(v)))
        return v.value

    def collapsing(self, label, open=None):
        if open is None:
            r = bool(lib.goome_ui_collapsing(self._h(), _b(label), None))
            self.changed = False
            return r
        v = c_int(int(bool(open)))
        r = bool(lib.goome_ui_collapsing(self._h(), _b(label), byref(v)))
        self.changed = bool(v.value) != bool(open)
        return r

    def progress(self, frac, text=None):
        lib.goome_ui_progress(self._h(), frac, _b(text))

    def color(self, label, argb):
        v = c_uint32(int(argb) & 0xFFFFFFFF)
        self.changed = bool(lib.goome_ui_color(self._h(), _b(label), byref(v)))
        return v.value

    def tooltip(self, text):
        lib.goome_ui_tooltip(self._h(), _b(text))

    @property
    def hovered(self):
        return bool(lib.goome_ui_hovered(self._h()))

    def scroll_begin(self, id, h=0):
        return Shown(lib.goome_ui_scroll_begin(self._h(), _b(id), h), self.scroll_end)

    def scroll_end(self):
        lib.goome_ui_scroll_end(self._h())

    def push_id(self, id):
        lib.goome_ui_push_id(self._h(), _b(str(id) if not isinstance(id, (str, bytes)) else id))

    def pop_id(self):
        lib.goome_ui_pop_id(self._h())

    def id(self, id):
        self.push_id(id)
        return Shown(True, self.pop_id)


class _UiFrame(object):
    def __init__(self, ui, mon):
        self.ui, self.mon, self.c = ui, mon, None

    def __enter__(self):
        self.c = self.ui.begin(self.mon)
        return self.c

    def __exit__(self, et, ev, tb):
        if self.c is not None:
            self.ui.end()
        return False
