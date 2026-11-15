import array
import ctypes
from collections import namedtuple
from ctypes import byref, c_char_p, c_double, c_float, c_int, c_uint32

from . import _lib
from ._lib import lib
from .core import CURSORS, EGONE, ENOMEM, OK, WANT_KEYBOARD, WANT_MOUSE, GoomeError, _b, _cut, _s, error_for
from .draw import Canvas, Font, _radii

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

INPUT_PASSWORD = 1
INPUT_READONLY = 2
INPUT_NUMBER = 4
INPUT_NO_SELECT_ON_FOCUS = 8
INPUT_ENTER_RETURNS = 16

(S_BG, S_PANEL, S_BORDER, S_TEXT, S_TEXT_DIM, S_ACCENT, S_ACCENT_TEXT, S_HOVER, S_ACTIVE, S_INPUT_BG, S_SHADOW,
 S_RADIUS, S_PAD, S_GAP, S_BORDER_WIDTH, S_FONT_SIZE, S_SHADOW_BLUR, S_ANIM_MS,
 S_FOCUS, S_SELECT, S_CARET, S_LINK, S_BADGE, S_TOAST, S_TOOLTIP, S_DANGER, S_KNOB, S_DIM,
 S_CHECK_SIZE, S_CHECK_RADIUS, S_TOGGLE_W, S_TOGGLE_H, S_SLIDER_H, S_SLIDER_TRACK, S_KNOB_SIZE,
 S_SCROLL_W, S_SCROLL_MIN, S_ITEM_H, S_MENU_ITEM_H, S_TAB_H, S_WIN_TITLE_H, S_APP_TITLE_H, S_MENUBAR_H, S_STATUSBAR_H,
 S_FOCUS_W, S_FOCUS_GAP, S_SEP_W, S_GRIP, S_INDENT, S_PLOT_W, S_SPINNER, S_CARET_W,
 S_WIN_MIN_W, S_WIN_MIN_H, S_POP_GAP, S_MENU_GAP, S_TIP_PAD_X, S_TIP_PAD_Y, S_TIP_X, S_TIP_Y, S_TIP_RADIUS,
 S_SHADOW_X, S_SHADOW_Y, S_ALIGN, S_HEADING_SIZE, S_SMALL_SIZE, S_EASE,
 S_HOVER_MS, S_PRESS_MS, S_POPUP_MS, S_COLLAPSE_MS, S_TOAST_FADE_MS, S_COUNT) = range(len(_lib.STYLE_NAMES) + 1)
STYLE_NAMES = _lib.STYLE_NAMES
STYLE_COLORS = frozenset(STYLE_NAMES.index(n) for n in _lib.THEME_COLORS)
STYLE_NUMS = frozenset(STYLE_NAMES.index(n) for n in _lib.THEME_SIZES)

ALIGN_NAMES = ("auto", "left", "center", "right")
ALIGN_AUTO, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = range(4)
EASE_NAMES = ("smooth", "linear", "out", "in_out", "back", "custom")
EASE_SMOOTH, EASE_LINEAR, EASE_OUT, EASE_IN_OUT, EASE_BACK, EASE_CUSTOM = range(6)
PRESET_NAMES = ("dark", "light", "midnight", "paper", "mint", "high_contrast", "rose")
PRESET_DARK, PRESET_LIGHT, PRESET_MIDNIGHT, PRESET_PAPER, PRESET_MINT, PRESET_HIGH_CONTRAST, PRESET_ROSE, PRESET_COUNT = range(8)
ACT_NAMES = ("copy", "cut", "paste", "undo", "redo", "select_all", "word_left", "word_right", "del_word_left", "del_word_right",
             "doc_start", "doc_end")
(ACT_COPY, ACT_CUT, ACT_PASTE, ACT_UNDO, ACT_REDO, ACT_SELECT_ALL, ACT_WORD_LEFT, ACT_WORD_RIGHT, ACT_DEL_WORD_LEFT,
 ACT_DEL_WORD_RIGHT, ACT_DOC_START, ACT_DOC_END, ACT_COUNT) = range(_lib.ACT_COUNT + 1)
CUR_NAMES = ("button", "input", "link", "drag_value", "split_x", "split_y", "grip", "column", "drag_drop", "custom_x", "custom_y",
             "custom_xy")
(CUR_BUTTON, CUR_INPUT, CUR_LINK, CUR_DRAG_VALUE, CUR_SPLIT_X, CUR_SPLIT_Y, CUR_GRIP, CUR_COLUMN, CUR_DRAG_DROP, CUR_CUSTOM_X,
 CUR_CUSTOM_Y, CUR_CUSTOM_XY, CUR_COUNT) = range(_lib.CUR_COUNT + 1)

(SKIN_BUTTON, SKIN_PANEL, SKIN_INPUT, SKIN_CHECKBOX, SKIN_RADIO, SKIN_TOGGLE, SKIN_SLIDER_TRACK, SKIN_SLIDER_FILL, SKIN_SCROLLBAR,
 SKIN_TAB, SKIN_TITLEBAR, SKIN_TOOLTIP, SKIN_MENU, SKIN_POPUP, SKIN_COUNT) = range(15)
SKIN_KINDS = {"button": SKIN_BUTTON, "panel": SKIN_PANEL, "input": SKIN_INPUT, "checkbox": SKIN_CHECKBOX, "radio": SKIN_RADIO,
              "toggle": SKIN_TOGGLE, "slider_track": SKIN_SLIDER_TRACK, "slider_fill": SKIN_SLIDER_FILL, "scrollbar": SKIN_SCROLLBAR,
              "tab": SKIN_TAB, "titlebar": SKIN_TITLEBAR, "tooltip": SKIN_TOOLTIP, "menu": SKIN_MENU, "popup": SKIN_POPUP}

ICON_NAMES = ("arrow_down", "arrow_right", "arrow_up", "arrow_left", "check", "radio_dot", "close", "minimize", "maximize", "restore",
              "resize", "sort_up", "sort_down", "plus", "minus", "slider_knob", "toggle_knob", "collapse", "expand", "drag_handle",
              "toast", "picker")
(ICON_ARROW_DOWN, ICON_ARROW_RIGHT, ICON_ARROW_UP, ICON_ARROW_LEFT, ICON_CHECK, ICON_RADIO_DOT, ICON_CLOSE, ICON_MINIMIZE,
 ICON_MAXIMIZE, ICON_RESTORE, ICON_RESIZE, ICON_SORT_UP, ICON_SORT_DOWN, ICON_PLUS, ICON_MINUS, ICON_SLIDER_KNOB, ICON_TOGGLE_KNOB,
 ICON_COLLAPSE, ICON_EXPAND, ICON_DRAG_HANDLE, ICON_TOAST, ICON_PICKER, ICON_COUNT) = range(_lib.ICON_COUNT + 1)

ITEM_DRAG_X = 1
ITEM_DRAG_Y = 2
ITEM_FOCUSABLE = 4
ITEM_NO_HIT = 8
ITEM_REPEAT = 16

Sort = namedtuple("Sort", "changed col desc")
Skin = namedtuple("Skin", "bitmap left top right bottom")


def _named(v, names, what):
    if isinstance(v, str):
        k = v.lower().replace(" ", "_").replace("-", "_")
        if k not in names:
            raise ValueError("theres no %s called %r, its one of %s" % (what, v, ", ".join(names)))
        return names.index(k)
    return v


def _style_value(name, v):
    if name in _lib.THEME_COLORS:
        return int(v) & 0xFFFFFFFF
    if name == "align":
        return float(_named(v, ALIGN_NAMES, "align"))
    if name == "ease":
        return float(_named(v, EASE_NAMES, "ease"))
    return float(v)


def _theme_prop(name):
    def get(self):
        return getattr(self._t(), name)

    def put(self, v):
        setattr(self._t(), name, _style_value(name, v))

    return property(get, put)


def _font_prop(name):
    def get(self):
        p = getattr(self._t(), name)
        if not p:
            return None
        f = self._fonts.get(name)
        if f is not None and f._f == p:
            return f
        w = self._own_fonts.get(name)
        if w is None or w._f != p:
            w = self._own_fonts[name] = Font(p, owned=False)
        return w

    def put(self, f):
        self._set_font(name, f)

    return property(get, put)


class _Either(object):
    def __init__(self, fn):
        self.fn = fn

    def __get__(self, obj, cls):
        if obj is None:
            return lambda *a, **kw: self.fn(cls(None, _lib.ThemeS()), *a, **kw)
        return lambda *a, **kw: self.fn(obj, *a, **kw)


def _skin_edges(v):
    bmp, edges = v[0], list(v[1:])
    if not edges:
        raise ValueError("a skin needs a bitmap and its border size, like (bmp, 8) or (bmp, l, t, r, b)")
    if len(edges) == 1:
        edges *= 4
    elif len(edges) != 4:
        raise ValueError("give one border size or four (left, top, right, bottom)")
    return Skin(bmp, *[float(e) for e in edges])


def _icon_id(i):
    if isinstance(i, str):
        if i not in ICON_NAMES:
            raise ValueError("theres no icon called %r" % i)
        return ICON_NAMES.index(i)
    i = int(i)
    if not 0 <= i < ICON_COUNT:
        raise IndexError("icon has to be 0 to %d (goome.ICON_*), not %d" % (ICON_COUNT - 1, i))
    return i


class Icons(object):
    def __init__(self, theme):
        self._theme = theme

    def __len__(self):
        return ICON_COUNT

    def __getitem__(self, i):
        i = _icon_id(i)
        b = self._theme._icons.get(i)
        if b is None or b.closed or not self._theme._t().icon[i]:
            return None
        return b

    def __setitem__(self, i, bmp):
        self._theme._set_icon(_icon_id(i), bmp)

    def __delitem__(self, i):
        self._theme._set_icon(_icon_id(i), None)

    def __iter__(self):
        return iter([self[i] for i in range(ICON_COUNT)])

    def clear(self):
        for i in range(ICON_COUNT):
            self._theme._set_icon(i, None)

    def __repr__(self):
        return "Icons(%s)" % ", ".join(ICON_NAMES[i] for i in range(ICON_COUNT) if self[i] is not None)


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
    def __init__(self, ui, own=None):
        self._ui = ui
        self._own = own
        self._fonts = {}
        self._own_fonts = {}
        self._skins = {}
        self._icons = {}

    def _uses(self, bmp):
        return any(k.bitmap is bmp for k in self._skins.values()) or any(b is bmp for b in self._icons.values())

    def _hold(self, bmp):
        if self._ui is not None and not self._ui.closed:
            self._ui._spent.append(bmp)

    def _set_icon(self, i, bmp):
        old = self._icons.pop(i, None)
        if old is not None:
            self._hold(old)
            if not self._uses(old):
                old._themes.discard(self)
        if bmp is None:
            self._t().icon[i] = None
            return
        bmp._ref()
        self._t().icon[i] = ctypes.pointer(bmp._s)
        self._icons[i] = bmp
        bmp._themes.add(self)

    @property
    def icon(self):
        return Icons(self)

    @property
    def icon_tint(self):
        return self._t().icon_tint

    @icon_tint.setter
    def icon_tint(self, v):
        self._t().icon_tint = int(v) & 0xFFFFFFFF

    def _set_skin(self, name, v):
        old = self._skins.pop(name, None)
        if old is not None:
            self._hold(old.bitmap)
            if not self._uses(old.bitmap):
                old.bitmap._themes.discard(self)
        s = getattr(self._t(), name)
        if v is None:
            s.bm, s.l, s.t, s.r, s.b = None, 0, 0, 0, 0
            return
        k = _skin_edges(v)
        bmp = k.bitmap
        bmp._ref()
        s.bm = ctypes.pointer(bmp._s)
        s.l, s.t, s.r, s.b = k.left, k.top, k.right, k.bottom
        self._skins[name] = k
        bmp._themes.add(self)

    def _drop_bitmap(self, bmp):
        for name, k in list(self._skins.items()):
            if k.bitmap is bmp:
                self._set_skin(name, None)
        for i, b in list(self._icons.items()):
            if b is bmp:
                self._set_icon(i, None)

    def _ptr(self):
        if self._own is not None:
            return ctypes.pointer(self._own)
        return self._ui._theme_ptr()

    def _t(self):
        return self._ptr().contents

    def dark(self):
        lib.goome_ui_theme_dark(self._ptr())

    def light(self):
        lib.goome_ui_theme_light(self._ptr())

    @_Either
    def make(self, accent, dark=True, radius=10):
        lib.goome_ui_theme_make(self._ptr(), int(accent) & 0xFFFFFFFF, int(bool(dark)), float(radius))
        return self

    @_Either
    def preset(self, name):
        i = _named(name, PRESET_NAMES, "preset")
        if lib.goome_ui_theme_preset(self._ptr(), int(i)) != OK:
            raise ValueError("preset has to be one of %s (or goome.PRESET_*), not %r" % (", ".join(PRESET_NAMES), name))
        return self

    def copy(self):
        t = Theme(self._ui, _lib.ThemeS())
        ctypes.pointer(t._own)[0] = self._t()
        t._fonts = dict(self._fonts)
        for f in t._fonts.values():
            f._themes.add(t)
        t._skins = dict(self._skins)
        for k in t._skins.values():
            k.bitmap._themes.add(t)
        t._icons = dict(self._icons)
        for b in t._icons.values():
            b._themes.add(t)
        return t

    def _set_font(self, name, f):
        old = self._fonts.pop(name, None)
        if old is not None and not any(o is old for o in self._fonts.values()):
            old._themes.discard(self)
        if f is None:
            setattr(self._t(), name, None)
            return
        setattr(self._t(), name, f._h())
        if any(f is w for w in self._own_fonts.values()):
            return
        self._fonts[name] = f
        f._themes.add(self)

    def _drop_font(self, f):
        for name, o in list(self._fonts.items()):
            if o is f:
                self._set_font(name, None)

    def _forget(self):
        for f in self._fonts.values():
            f._themes.discard(self)
        self._fonts.clear()
        for k in self._skins.values():
            k.bitmap._themes.discard(self)
        self._skins.clear()
        for b in self._icons.values():
            b._themes.discard(self)
        self._icons.clear()

    def as_dict(self):
        t = self._t()
        return dict((n, getattr(t, n)) for n in _lib.THEME_COLORS + _lib.THEME_SIZES)

    def update(self, **kw):
        for k, v in kw.items():
            if k == "icons":
                for i, b in v.items():
                    self.icon[i] = b
                continue
            if k not in _lib.THEME_COLORS + _lib.THEME_SIZES + _lib.THEME_SKINS + _lib.THEME_FONTS + ("icon_tint",):
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
for _n in _lib.THEME_FONTS:
    setattr(Theme, _n, _font_prop(_n))


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


class Item(object):
    __slots__ = [n for n, _ in _lib.ItemS._fields_] + ["changed"]

    def __init__(self, s, changed):
        for n, t in _lib.ItemS._fields_:
            v = getattr(s, n)
            setattr(self, n, bool(v) if t is c_int and n != "key" else v)
        self.changed = bool(changed)

    def __bool__(self):
        return self.changed

    def __repr__(self):
        on = [n for n in ("hovered", "pressed", "held", "released", "clicked", "double_clicked", "right_clicked", "focused") if getattr(self, n)]
        return "Item(%g, %g, %g, %g%s)" % (self.x, self.y, self.w, self.h, "".join(", " + n for n in on))


class _Style(object):
    def __init__(self, ui, n):
        self._ui, self.n = ui, n

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self._ui.pop(self.n)
        return False


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
        self.config = Config(self)
        self.entered = False
        self._canvas = None
        self._panes = {}
        self._edits = {}
        self._scope = []
        self._wins = []
        self._used = set()
        self._frames = 0
        self._auto_grab = WANT_MOUSE | WANT_KEYBOARD
        self._pins = []
        self._spent = []
        self._layers = []

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
        self.theme._forget()
        self.config._drop()
        u, self._u = self._u, None
        if self._canvas is not None:
            self._canvas._ptr = None
        self._drop_layers()
        self._pins = []
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
        self._wins = []
        self._used = set()
        self._pins = []
        self._spent = []
        if not p:
            self._canvas = None
            return None
        self._canvas = Canvas(p, self._g)
        return self._canvas

    def end(self):
        lib.goome_ui_end(self._h())
        self._wins = []
        old = [k for k, e in self._edits.items() if e[2] < self._frames - 600]
        for k in old:
            del self._edits[k]
        if self._canvas is not None:
            self._canvas._ptr = None
            self._canvas = None
        self._pins = []
        self._spent = []
        self._drop_layers()

    def _drop_layers(self):
        for c in self._layers:
            c._ptr = None
        self._layers = []

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
        self._wins.append(win)
        return Shown(r, self.window_end)

    def window_end(self):
        lib.goome_ui_window_end(self._h())
        if self._scope:
            self._scope.pop()
        if self._wins:
            self._wins.pop()

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
        self.entered = False
        return _s(buf.value)

    def input_ex(self, label, text, flags=0, hint=None, cap=256):
        buf = ctypes.create_string_buffer(_cut(text, cap), cap)
        r = lib.goome_ui_input_ex(self._h(), _b(label), buf, cap, int(flags), _b(hint))
        self.changed = r != 0
        self.entered = r == 2
        return _s(buf.value)

    def password(self, label, text, hint=None, flags=0, cap=256):
        return self.input_ex(label, text, INPUT_PASSWORD | int(flags), hint, cap)

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

    @property
    def wants(self):
        return lib.goome_ui_wants(self._h())

    @property
    def wants_mouse(self):
        return bool(self.wants & WANT_MOUSE)

    @property
    def wants_keyboard(self):
        return bool(self.wants & WANT_KEYBOARD)

    @property
    def auto_grab(self):
        return self._auto_grab

    @auto_grab.setter
    def auto_grab(self, wants):
        lib.goome_ui_auto_grab(self._h(), int(wants))
        self._auto_grab = int(wants)

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


    def pos(self, x, y):
        lib.goome_ui_pos(self._h(), x, y)

    def size(self, w=0, h=0):
        lib.goome_ui_size(self._h(), w, h)

    def _style_id(self, what, kinds):
        if isinstance(what, str):
            if what not in STYLE_NAMES:
                raise ValueError("theres no style called %r" % what)
            what = STYLE_NAMES.index(what)
        what = int(what)
        if what not in kinds:
            raise ValueError("style %d isnt a %s" % (what, "color" if kinds is STYLE_COLORS else "number"))
        return what

    def _pin(self, keep=None):
        self._pins.append(keep)

    def push_color(self, what, argb):
        what = self._style_id(what, STYLE_COLORS)
        lib.goome_ui_push_color(self._h(), what, int(argb) & 0xFFFFFFFF)
        self._pin()

    def push_num(self, what, v):
        what = self._style_id(what, STYLE_NUMS)
        lib.goome_ui_push_num(self._h(), what, _style_value(STYLE_NAMES[what], v))
        self._pin()

    def push_radii(self, r):
        lib.goome_ui_push_radii(self._h(), _radii(r))
        self._pin()

    def push_font(self, font):
        lib.goome_ui_push_font(self._h(), None if font is None else font._h())
        self._pin(font)

    def push_skin(self, kind, skin):
        kind = SKIN_KINDS.get(kind, kind) if isinstance(kind, str) else int(kind)
        if not 0 <= kind < SKIN_COUNT:
            raise ValueError("skin kind has to be one of the goome.SKIN_* ones, not %r" % kind)
        if skin is None:
            lib.goome_ui_push_skin(self._h(), kind, None)
            self._pin()
            return
        k = _skin_edges(skin)
        k.bitmap._ref()
        s = _lib.SkinS(ctypes.pointer(k.bitmap._s), k.left, k.top, k.right, k.bottom)
        lib.goome_ui_push_skin(self._h(), kind, byref(s))
        self._pin(k.bitmap)

    def push_icon(self, icon, bmp):
        icon = _icon_id(icon)
        if bmp is None:
            lib.goome_ui_push_icon(self._h(), icon, None)
            self._pin()
            return
        bmp._ref()
        lib.goome_ui_push_icon(self._h(), icon, ctypes.pointer(bmp._s))
        self._pin(bmp)

    def push_theme(self, theme):
        if not isinstance(theme, Theme):
            raise TypeError("push_theme needs a Theme, like ui.theme.copy(), not %r" % theme)
        lib.goome_ui_push_theme(self._h(), theme._ptr())
        self._pin(theme)

    def pop(self, n=1):
        n = int(n)
        lib.goome_ui_pop(self._h(), n)
        if n > 0:
            cut = max(0, len(self._pins) - n)
            self._spent += self._pins[cut:]
            del self._pins[cut:]

    def style(self, theme=None, **kw):
        n = 0
        try:
            if theme is not None:
                self.push_theme(theme)
                n += 1
            for k, v in kw.items():
                if k in _lib.THEME_COLORS:
                    self.push_color(k, v)
                elif k in _lib.THEME_SIZES:
                    self.push_num(k, v)
                elif k == "radii":
                    self.push_radii(v)
                elif k == "font":
                    self.push_font(v)
                elif k == "skin":
                    self.push_skin(*v)
                elif k == "icon":
                    self.push_icon(*v)
                elif k == "icons":
                    for i, b in v.items():
                        self.push_icon(i, b)
                        n += 1
                    continue
                else:
                    raise TypeError("style() has no %r" % k)
                n += 1
        except Exception:
            self.pop(n)
            raise
        return _Style(self, n)

    def scale(self, s):
        lib.goome_ui_scale(self._h(), float(s))

    def custom(self, id, w=0, h=0, flags=0):
        s = _lib.ItemS()
        r = lib.goome_ui_custom(self._h(), _b(id), w, h, int(flags), byref(s))
        it = Item(s, r)
        self.changed = it.changed
        return it

    @property
    def canvas(self):
        p = lib.goome_ui_canvas(self._h())
        if not p:
            return None
        c = Canvas(p, self._g)
        self._layers.append(c)
        return c

    def store(self, id, n):
        n = int(n)
        if n <= 0:
            raise ValueError("store needs at least 1 slot, got %d" % n)
        p = lib.goome_ui_store(self._h(), _b(id), n)
        if not p:
            raise GoomeError(ENOMEM, "no memory for the store %r" % id)
        arr = (c_double * n).from_address(ctypes.addressof(p.contents))
        return memoryview(arr).cast("B").cast("d")


def _combo_list(combos):
    if combos is None:
        return None
    if isinstance(combos, (str, bytes)):
        return _b(combos)
    return _b(" ".join(c if isinstance(c, str) else c.decode() for c in combos))


class Cursors(object):
    def __init__(self, cfg):
        self._cfg = cfg

    def __len__(self):
        return CUR_COUNT

    def __getitem__(self, what):
        return self._cfg._c().cursor[_named_id(what, CUR_NAMES, CUR_COUNT, "widget cursor")]

    def __setitem__(self, what, shape):
        shape = CURSORS[shape] if isinstance(shape, str) and shape in CURSORS else shape
        if isinstance(shape, str):
            raise ValueError("theres no cursor called %r" % shape)
        self._cfg._c().cursor[_named_id(what, CUR_NAMES, CUR_COUNT, "widget cursor")] = int(shape)

    def __iter__(self):
        return iter([self[i] for i in range(CUR_COUNT)])

    def __repr__(self):
        return "Cursors(%s)" % ", ".join("%s=%d" % (CUR_NAMES[i], self[i]) for i in range(CUR_COUNT))


def _named_id(what, names, count, kind):
    i = _named(what, names, kind)
    i = int(i)
    if not 0 <= i < count:
        raise IndexError("%s has to be 0 to %d, not %d" % (kind, count - 1, i))
    return i


def _cfg_prop(name, cast):
    def get(self):
        v = getattr(self._c(), name)
        return bool(v) if cast is bool else v

    def put(self, v):
        setattr(self._c(), name, int(bool(v)) if cast is bool else cast(v))

    return property(get, put)


class Config(object):
    def __init__(self, ui):
        self._ui = ui
        self._ease = None
        self._ease_fn = None
        self._mask = None

    def _c(self):
        return lib.goome_ui_cfg(self._ui._h()).contents

    def _drop(self):
        self._ease = self._ease_fn = self._mask = None

    @property
    def cursor(self):
        return Cursors(self)

    def keys(self, action):
        row = self._c().keys[_named_id(action, ACT_NAMES, ACT_COUNT, "action")]
        return [(k.key, k.mods) for k in row if k.key]

    def bind(self, action, combos):
        i = _named_id(action, ACT_NAMES, ACT_COUNT, "action")
        raw = _combo_list(combos)
        rc = lib.goome_ui_bind(self._ui._h(), i, raw)
        if rc != OK:
            raise error_for(rc, "cant read the keys %r" % combos)

    def reset(self):
        lib.goome_ui_config_default(ctypes.pointer(self._c()))
        self._drop()

    @property
    def ease(self):
        return self._ease

    @ease.setter
    def ease(self, fn):
        c = self._c()
        if fn is None:
            c.ease = _lib.EASE_FN()
            self._ease = self._ease_fn = None
            return
        if not callable(fn):
            raise TypeError("ease needs a function that takes t (0 to 1) and gives back a number, not %r" % fn)

        def call(t, user):
            return float(fn(t))

        f = _lib.EASE_FN(call)
        c.ease = f
        c.ease_user = None
        self._ease, self._ease_fn = fn, f

    @property
    def mask(self):
        return _s(self._c().mask)

    @mask.setter
    def mask(self, text):
        self._mask = _b(text)
        self._c().mask = self._mask

    def __setattr__(self, k, v):
        if not k.startswith("_") and not hasattr(type(self), k):
            raise AttributeError("config has no %r" % k)
        object.__setattr__(self, k, v)


for _n in _lib.CONFIG_INTS:
    setattr(Config, _n, _cfg_prop(_n, int))
for _n in _lib.CONFIG_TOGGLES:
    setattr(Config, _n, _cfg_prop(_n, bool))
Config.scroll_lines = _cfg_prop("scroll_lines", float)


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
