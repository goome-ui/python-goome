import array
import ctypes
from collections import namedtuple
from ctypes import byref, c_char_p, c_double, c_float, c_int, c_uint32

from . import _lib
from ._lib import lib
from .core import EGONE, ENOMEM, GoomeError, _b, _cut, _s
from .draw import Canvas, Font

WIN_MOVE = 1
WIN_RESIZE = 2
WIN_COLLAPSE = 4
WIN_NO_TITLE = 8
WIN_CLOSE = 16

APP_TITLEBAR = 1
APP_MENUBAR = 2
APP_STATUSBAR = 4
APP_NO_PAD = 8

EDIT_READONLY = 1
EDIT_LINE_NUMBERS = 2
EDIT_WRAP = 4
EDIT_MONO = 8

TABLE_SORTABLE = 1
TABLE_RESIZABLE = 2
TABLE_STRIPES = 4
TABLE_BORDERS = 8

Sort = namedtuple("Sort", "changed col desc")
Skin = namedtuple("Skin", "bitmap left top right bottom")


def _theme_prop(name):
    def get(self):
        return getattr(self._t(), name)

    def put(self, v):
        if name in _lib.THEME_COLORS:
            v = int(v) & 0xFFFFFFFF
        setattr(self._t(), name, v)

    return property(get, put)


def _skin_prop(name):
    def get(self):
        k = self._skins.get(name)
        if k is None or not getattr(self._t(), name).bm or k.bitmap.closed:
            return None
        return k

    def put(self, v):
        self._set_skin(name, v)

    return property(get, put)


class Theme(object):
    def __init__(self, ui):
        self._ui = ui
        self._font = None
        self._own_font = None
        self._skins = {}

    def _set_skin(self, name, v):
        old = self._skins.pop(name, None)
        if old is not None and old.bitmap not in [k.bitmap for k in self._skins.values()]:
            old.bitmap._themes.discard(self)
        s = getattr(self._t(), name)
        if v is None:
            s.bm, s.l, s.t, s.r, s.b = None, 0, 0, 0, 0
            return
        bmp, edges = v[0], list(v[1:])
        if not edges:
            raise ValueError("a skin needs a bitmap and its border size, like (bmp, 8) or (bmp, l, t, r, b)")
        if len(edges) == 1:
            edges *= 4
        elif len(edges) != 4:
            raise ValueError("give one border size or four (left, top, right, bottom)")
        bmp._ref()
        k = Skin(bmp, *[float(e) for e in edges])
        s.bm = ctypes.pointer(bmp._s)
        s.l, s.t, s.r, s.b = k.left, k.top, k.right, k.bottom
        self._skins[name] = k
        bmp._themes.add(self)

    def _drop_bitmap(self, bmp):
        for name, k in list(self._skins.items()):
            if k.bitmap is bmp:
                self._set_skin(name, None)

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
            if k not in _lib.THEME_COLORS + _lib.THEME_SIZES + _lib.THEME_SKINS + ("font",):
                raise AttributeError("theme has no %r" % k)
            setattr(self, k, v)

    def __setattr__(self, k, v):
        if not k.startswith("_") and not hasattr(type(self), k):
            raise AttributeError("theme has no %r" % k)
        object.__setattr__(self, k, v)


for _n in _lib.THEME_COLORS + _lib.THEME_SIZES:
    setattr(Theme, _n, _theme_prop(_n))
for _n in _lib.THEME_SKINS:
    setattr(Theme, _n, _skin_prop(_n))


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


class Flag(object):
    def __init__(self, value=False):
        self._v = c_int(int(bool(value)))

    value = property(lambda s: bool(s._v.value), lambda s, v: setattr(s._v, "value", int(bool(v))))

    def __bool__(self):
        return bool(self._v.value)

    def toggle(self):
        self.value = not self.value

    def __repr__(self):
        return "Flag(%s)" % self.value


class Split(object):
    def __init__(self, frac=0.5, vertical=False):
        self._f = c_double(frac)
        self.vertical = vertical

    frac = property(lambda s: s._f.value, lambda s, v: setattr(s._f, "value", v))

    def __repr__(self):
        return "Split(%g%s)" % (self.frac, ", vertical" if self.vertical else "")


def _ref(flag, what):
    if flag is None:
        return None
    if isinstance(flag, Flag):
        return byref(flag._v)
    raise TypeError("%s needs a goome.Flag (or None) so goome can flip it, not %r" % (what, flag))


class Shown(object):
    def __init__(self, shown, end, always=True):
        self.shown = bool(shown)
        self._end = end
        self._always = always

    def __bool__(self):
        return self.shown

    def __enter__(self):
        return self.shown

    def __exit__(self, *a):
        if self._always or self.shown:
            self._end()
        return False


class Table(Shown):
    def __init__(self, ui, shown):
        Shown.__init__(self, shown, ui.table_end)
        self._ui = ui

    def __enter__(self):
        return self

    def column(self, name, width=0):
        self._ui.table_column(name, width)

    def sort(self, col=0, desc=False):
        return self._ui.table_sort(col, desc)

    def row(self):
        self._ui.table_row()

    def next(self):
        self._ui.table_next()


class Panes(Shown):
    def __init__(self, ui, shown):
        Shown.__init__(self, shown, ui.split_end)
        self._ui = ui

    def __enter__(self):
        return self

    def next(self):
        self._ui.split_next()


def _floats(values):
    if isinstance(values, ctypes.Array) and values._type_ is c_float:
        return values, len(values), values
    try:
        mv = memoryview(values)
    except TypeError:
        mv = None
    if mv is not None and mv.format == "f" and mv.c_contiguous and not mv.readonly:
        n = mv.nbytes // 4
        arr = (c_float * max(1, n)).from_buffer(mv.cast("B")) if n else (c_float * 1)()
        return arr, n, (arr, values)
    vals = array.array("f", [float(v) for v in values])
    n = len(vals)
    arr = (c_float * max(1, n)).from_buffer(vals) if n else (c_float * 1)()
    return arr, n, (arr, vals)


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
        self._panes = {}
        self._edits = {}
        self._scope = []
        self._used = set()
        self._frames = 0

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
        for k in self.theme._skins.values():
            k.bitmap._themes.discard(self.theme)
        self.theme._skins.clear()
        u, self._u = self._u, None
        if self._canvas is not None:
            self._canvas._ptr = None
        lib.goome_ui_free(u)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __del__(self):
        if getattr(self, "_u", None) is not None and self._g._g is not None and lib is not None:
            self.close()

    def feed(self, ev):
        return bool(lib.goome_ui_feed(self._h(), byref(ev.raw)))

    def begin(self, mon=0):
        p = lib.goome_ui_begin(self._h(), mon)
        self._g._began += 1
        self._frames += 1
        self._scope = []
        self._used = set()
        if not p:
            self._canvas = None
            return None
        self._canvas = Canvas(p, self._g)
        return self._canvas

    def end(self):
        lib.goome_ui_end(self._h())
        old = [k for k, e in self._edits.items() if e[2] < self._frames - 600]
        for k in old:
            del self._edits[k]
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
        self._scope.append(("window", title))
        return Shown(r, self.window_end)

    def window_end(self):
        lib.goome_ui_window_end(self._h())
        if self._scope:
            self._scope.pop()

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
        buf = ctypes.create_string_buffer(_cut(text, cap), cap)
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
        self._scope.append(("id", id))

    def pop_id(self):
        lib.goome_ui_pop_id(self._h())
        if self._scope:
            self._scope.pop()

    def id(self, id):
        self.push_id(id)
        return Shown(True, self.pop_id)

    def app(self, title=None, flags=0):
        return Shown(lib.goome_ui_app(self._h(), _b(title), int(flags)), self.app_end)

    def app_end(self):
        lib.goome_ui_app_end(self._h())

    def menubar(self):
        return Shown(lib.goome_ui_menubar_begin(self._h()), self.menubar_end, always=False)

    def menubar_end(self):
        lib.goome_ui_menubar_end(self._h())

    def menu(self, label):
        return Shown(lib.goome_ui_menu_begin(self._h(), _b(label)), self.menu_end, always=False)

    def menu_end(self):
        lib.goome_ui_menu_end(self._h())

    def menu_item(self, label, shortcut=None, checked=None):
        r = bool(lib.goome_ui_menu_item(self._h(), _b(label), _b(shortcut), _ref(checked, "menu_item checked")))
        self.changed = r
        return r

    def menu_separator(self):
        lib.goome_ui_menu_separator(self._h())

    def context(self, id):
        return Shown(lib.goome_ui_context_begin(self._h(), _b(id)), self.context_end, always=False)

    def context_end(self):
        lib.goome_ui_context_end(self._h())

    def popup_open(self, id):
        lib.goome_ui_popup_open(self._h(), _b(id))

    def popup(self, id):
        return Shown(lib.goome_ui_popup_begin(self._h(), _b(id)), self.popup_end, always=False)

    def popup_end(self):
        lib.goome_ui_popup_end(self._h())

    def popup_close(self):
        lib.goome_ui_popup_close(self._h())

    def modal(self, title, open=None):
        return Shown(lib.goome_ui_modal_begin(self._h(), _b(title), _ref(open, "modal open")), self.modal_end, always=False)

    def modal_end(self):
        lib.goome_ui_modal_end(self._h())

    def toast(self, text, ms=2500):
        lib.goome_ui_toast(self._h(), _b(text), int(ms))

    def statusbar(self, text):
        lib.goome_ui_statusbar(self._h(), _b(text))

    @property
    def focused(self):
        return bool(lib.goome_ui_focused(self._h()))

    def set_focus(self):
        lib.goome_ui_set_focus(self._h())

    def text_edit(self, id, text, h=0, flags=0, cap=None):
        raw = _b(text or "") if cap is None else _cut(text, int(cap))
        key = (tuple(self._scope), id)
        n = 0
        while key + (n,) in self._used:
            n += 1
        key += (n,)
        self._used.add(key)
        e = self._edits.get(key)
        if cap is not None:
            size = int(cap)
            fresh = e is None or e[1] != size
        else:
            size = max(65536, len(raw) * 4)
            fresh = e is None or len(raw) * 4 > e[1] * 3
        if fresh:
            e = self._edits[key] = [ctypes.create_string_buffer(size), size, 0]
        buf = e[0]
        e[2] = self._frames
        if buf.value != raw:
            ctypes.memmove(buf, raw + b"\0", len(raw) + 1)
        self.changed = bool(lib.goome_ui_text_edit(self._h(), _b(id), buf, e[1], h, int(flags)))
        return _s(buf.value)

    def table(self, id, cols, h=0, flags=0):
        return Table(self, lib.goome_ui_table_begin(self._h(), _b(id), int(cols), h, int(flags)))

    def table_column(self, name, width=0):
        lib.goome_ui_table_column(self._h(), _b(name), width)

    def table_sort(self, col=0, desc=False):
        c, d = c_int(int(col)), c_int(int(bool(desc)))
        r = bool(lib.goome_ui_table_sort(self._h(), byref(c), byref(d)))
        return Sort(r, c.value, bool(d.value))

    def table_row(self):
        lib.goome_ui_table_row(self._h())

    def table_next(self):
        lib.goome_ui_table_next(self._h())

    def table_end(self):
        lib.goome_ui_table_end(self._h())

    def tree(self, label, open=None):
        return Shown(lib.goome_ui_tree(self._h(), _b(label), _ref(open, "tree open")), self.tree_end, always=False)

    def tree_end(self):
        lib.goome_ui_tree_end(self._h())

    def list_clip(self, count, row_h=0):
        first, last = c_int(0), c_int(0)
        lib.goome_ui_list_clip(self._h(), int(count), row_h, byref(first), byref(last))
        return range(first.value, last.value)

    def drag_float(self, label, value, speed=1.0, lo=0.0, hi=0.0, fmt=None):
        v = c_double(value)
        self.changed = bool(lib.goome_ui_drag_float(self._h(), _b(label), byref(v), speed, lo, hi, _b(fmt)))
        return v.value

    def drag_int(self, label, value, speed=1.0, lo=0, hi=0):
        v = c_int(int(value))
        self.changed = bool(lib.goome_ui_drag_int(self._h(), _b(label), byref(v), speed, int(lo), int(hi)))
        return v.value

    def number(self, label, value, step=1.0, fmt=None):
        v = c_double(value)
        self.changed = bool(lib.goome_ui_number(self._h(), _b(label), byref(v), step, _b(fmt)))
        return v.value

    def _plot(self, fn, label, values, lo, hi, h):
        arr, n, keep = _floats(values)
        if lo is None or hi is None:
            vals = arr[:n]
            lo = (min(vals) if vals else 0.0) if lo is None else lo
            hi = (max(vals) if vals else 1.0) if hi is None else hi
        fn(self._h(), _b(label), arr, n, lo, hi, h)

    def plot_lines(self, label, values, lo=None, hi=None, h=60):
        self._plot(lib.goome_ui_plot_lines, label, values, lo, hi, h)

    def plot_bars(self, label, values, lo=None, hi=None, h=60):
        self._plot(lib.goome_ui_plot_bars, label, values, lo, hi, h)

    def split(self, id, pane=None, vertical=None):
        if pane is None:
            pane = self._panes.get(id)
            if pane is None:
                pane = self._panes[id] = Split()
        v = pane.vertical if vertical is None else vertical
        return Panes(self, lib.goome_ui_split_begin(self._h(), _b(id), int(bool(v)), byref(pane._f)))

    def split_next(self):
        lib.goome_ui_split_next(self._h())

    def split_end(self):
        lib.goome_ui_split_end(self._h())

    def drag_source(self, type, data):
        raw = _b(data) if isinstance(data, str) else bytes(data)
        return bool(lib.goome_ui_drag_source(self._h(), _b(type), raw, len(raw)))

    def drop_target(self, type, cap=4096):
        buf = ctypes.create_string_buffer(int(cap))
        n = lib.goome_ui_drop_target(self._h(), _b(type), buf, int(cap))
        return buf.raw[: min(n, int(cap))] if n > 0 else None

    def spinner(self, size=16):
        lib.goome_ui_spinner(self._h(), size)

    def link(self, text):
        r = bool(lib.goome_ui_link(self._h(), _b(text)))
        self.changed = r
        return r

    def badge(self, text, argb=None):
        lib.goome_ui_badge(self._h(), _b(text), int(self.theme.accent if argb is None else argb) & 0xFFFFFFFF)


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
