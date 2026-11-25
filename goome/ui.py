import array
import ctypes
import re
from collections import namedtuple
from ctypes import byref, c_char_p, c_double, c_float, c_int, c_uint32

from . import _lib
from ._lib import lib
from .core import CONTROL, CURSORS, EGONE, ENOMEM, OK, WANT_KEYBOARD, WANT_MOUSE, GoomeError, _b, _cut, _s, error_for
from .draw import Canvas, Font, _radii

WIN_MOVE = 1
"""Flag for `ui.window()`: the title bar drags it around."""
WIN_RESIZE = 2
"""Flag for `ui.window()`: the user can resize it from the corner."""
WIN_COLLAPSE = 4
"""Flag for `ui.window()`: clicking the title folds it up."""
WIN_NO_TITLE = 8
"""Flag for `ui.window()`: no title bar."""
WIN_CLOSE = 16
"""Flag for `ui.window()`: a close button that sets the Window's `open` to False."""

APP_TITLEBAR = 1
"""Flag for `ui.app()`: draw goome's own title bar. Ignored if the window has WINDOW_NO_TITLEBAR."""
APP_MENUBAR = 2
"""Flag for `ui.app()`: reserve room for a menu bar."""
APP_STATUSBAR = 4
"""Flag for `ui.app()`: reserve room for a status bar at the bottom."""
APP_NO_PAD = 8
"""Flag for `ui.app()`: no padding around the content."""

EDIT_READONLY = 1
"""Flag for `ui.text_edit()`: can be selected and copied but not changed."""
EDIT_LINE_NUMBERS = 2
"""Flag for `ui.text_edit()`: show line numbers."""
EDIT_WRAP = 4
"""Flag for `ui.text_edit()`: wrap long lines."""
EDIT_MONO = 8
"""Flag for `ui.text_edit()`: use the monospace font."""

TABLE_SORTABLE = 1
"""Flag for `ui.table()`: clicking a header sorts, see table_sort()."""
TABLE_RESIZABLE = 2
"""Flag for `ui.table()`: columns can be dragged wider or narrower."""
TABLE_STRIPES = 4
"""Flag for `ui.table()`: every other row is shaded."""
TABLE_BORDERS = 8
"""Flag for `ui.table()`: lines between cells."""

INPUT_PASSWORD = 1
"""Flag for `ui.input_ex()`: show dots instead of the text."""
INPUT_READONLY = 2
"""Flag for `ui.input_ex()`: can be selected and copied but not changed."""
INPUT_NUMBER = 4
"""Flag for `ui.input_ex()`: only accept number characters."""
INPUT_NO_SELECT_ON_FOCUS = 8
"""Flag for `ui.input_ex()`: dont select everything when it gets focus."""
INPUT_ENTER_RETURNS = 16
"""Flag for `ui.input_ex()`: pressing enter sets `ui.entered`."""

(S_BG, S_PANEL, S_BORDER, S_TEXT, S_TEXT_DIM, S_ACCENT, S_ACCENT_TEXT, S_HOVER, S_ACTIVE, S_INPUT_BG, S_SHADOW,
 S_RADIUS, S_PAD, S_GAP, S_BORDER_WIDTH, S_FONT_SIZE, S_SHADOW_BLUR, S_ANIM_MS,
 S_FOCUS, S_SELECT, S_CARET, S_LINK, S_BADGE, S_TOAST, S_TOOLTIP, S_DANGER, S_KNOB, S_DIM,
 S_CHECK_SIZE, S_CHECK_RADIUS, S_TOGGLE_W, S_TOGGLE_H, S_SLIDER_H, S_SLIDER_TRACK, S_KNOB_SIZE,
 S_SCROLL_W, S_SCROLL_MIN, S_ITEM_H, S_MENU_ITEM_H, S_TAB_H, S_WIN_TITLE_H, S_APP_TITLE_H, S_MENUBAR_H, S_STATUSBAR_H,
 S_FOCUS_W, S_FOCUS_GAP, S_SEP_W, S_GRIP, S_INDENT, S_PLOT_W, S_SPINNER, S_CARET_W,
 S_WIN_MIN_W, S_WIN_MIN_H, S_POP_GAP, S_MENU_GAP, S_TIP_PAD_X, S_TIP_PAD_Y, S_TIP_X, S_TIP_Y, S_TIP_RADIUS,
 S_SHADOW_X, S_SHADOW_Y, S_ALIGN, S_HEADING_SIZE, S_SMALL_SIZE, S_EASE,
 S_HOVER_MS, S_PRESS_MS, S_POPUP_MS, S_COLLAPSE_MS, S_TOAST_FADE_MS, S_COUNT) = range(len(_lib.STYLE_NAMES) + 1)
"""Style ids for `ui.push_color()` and `ui.push_num()`, one per theme field (S_BG is the theme's `bg`, S_RADIUS is `radius`, and so on). You can also pass the field name as a string. S_COUNT is how many there are."""
STYLE_NAMES = _lib.STYLE_NAMES
"""Theme field names, in the same order as the S_* ids."""
STYLE_COLORS = frozenset(STYLE_NAMES.index(n) for n in _lib.THEME_COLORS)
"""The S_* ids that are colors."""
STYLE_NUMS = frozenset(STYLE_NAMES.index(n) for n in _lib.THEME_SIZES)
"""The S_* ids that are numbers."""

ALIGN_NAMES = ("auto", "left", "center", "right")
"""Text align names, in the same order as the ALIGN_* ids."""
ALIGN_AUTO, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = range(4)
"""Values for the theme's `align`: AUTO picks per widget, then left, center or right."""
EASE_NAMES = ("smooth", "linear", "out", "in_out", "back", "custom", "in", "spring", "bounce")
"""Easing curve names, in the same order as the EASE_* ids."""
EASE_SMOOTH, EASE_LINEAR, EASE_OUT, EASE_IN_OUT, EASE_BACK, EASE_CUSTOM, EASE_IN, EASE_SPRING, EASE_BOUNCE = range(9)
"""Easing curves for animations. EASE_CUSTOM calls the function set as `ui.config.ease`."""
PRESET_NAMES = ("dark", "light", "midnight", "paper", "mint", "high_contrast", "rose")
"""Theme preset names, in the same order as the PRESET_* ids."""
PRESET_DARK, PRESET_LIGHT, PRESET_MIDNIGHT, PRESET_PAPER, PRESET_MINT, PRESET_HIGH_CONTRAST, PRESET_ROSE, PRESET_COUNT = range(8)
"""Theme presets for `theme.preset()`. PRESET_COUNT is how many there are."""
ACT_NAMES = ("copy", "cut", "paste", "undo", "redo", "select_all", "word_left", "word_right", "del_word_left", "del_word_right",
             "doc_start", "doc_end")
"""Editing action names, in the same order as the ACT_* ids."""
(ACT_COPY, ACT_CUT, ACT_PASTE, ACT_UNDO, ACT_REDO, ACT_SELECT_ALL, ACT_WORD_LEFT, ACT_WORD_RIGHT, ACT_DEL_WORD_LEFT,
 ACT_DEL_WORD_RIGHT, ACT_DOC_START, ACT_DOC_END, ACT_COUNT) = range(_lib.ACT_COUNT + 1)
"""Editing actions you can rebind with `ui.config.bind()`, like copy, paste, undo or jump a word. ACT_COUNT is how many there are."""
CUR_NAMES = ("button", "input", "link", "drag_value", "split_x", "split_y", "grip", "column", "drag_drop", "custom_x", "custom_y",
             "custom_xy")
"""Widget names for `ui.config.cursor`, in the same order as the CUR_* ids."""
(CUR_BUTTON, CUR_INPUT, CUR_LINK, CUR_DRAG_VALUE, CUR_SPLIT_X, CUR_SPLIT_Y, CUR_GRIP, CUR_COLUMN, CUR_DRAG_DROP, CUR_CUSTOM_X,
 CUR_CUSTOM_Y, CUR_CUSTOM_XY, CUR_COUNT) = range(_lib.CUR_COUNT + 1)
"""Widgets whose mouse cursor you can change through `ui.config.cursor`. CUR_COUNT is how many there are."""

(SKIN_BUTTON, SKIN_PANEL, SKIN_INPUT, SKIN_CHECKBOX, SKIN_RADIO, SKIN_TOGGLE, SKIN_SLIDER_TRACK, SKIN_SLIDER_FILL, SKIN_SCROLLBAR,
 SKIN_TAB, SKIN_TITLEBAR, SKIN_TOOLTIP, SKIN_MENU, SKIN_POPUP, SKIN_COUNT) = range(15)
"""Skin kinds for `theme.skin_*` and `ui.push_skin()`, one per widget part. SKIN_COUNT is how many there are."""
SKIN_KINDS = {"button": SKIN_BUTTON, "panel": SKIN_PANEL, "input": SKIN_INPUT, "checkbox": SKIN_CHECKBOX, "radio": SKIN_RADIO,
              "toggle": SKIN_TOGGLE, "slider_track": SKIN_SLIDER_TRACK, "slider_fill": SKIN_SLIDER_FILL, "scrollbar": SKIN_SCROLLBAR,
              "tab": SKIN_TAB, "titlebar": SKIN_TITLEBAR, "tooltip": SKIN_TOOLTIP, "menu": SKIN_MENU, "popup": SKIN_POPUP}
"""Skin kind names you can pass as a string, like "button"."""

ICON_NAMES = ("arrow_down", "arrow_right", "arrow_up", "arrow_left", "check", "radio_dot", "close", "minimize", "maximize", "restore",
              "resize", "sort_up", "sort_down", "plus", "minus", "slider_knob", "toggle_knob", "collapse", "expand", "drag_handle",
              "toast", "picker")
"""Icon names, in the same order as the ICON_* ids."""
(ICON_ARROW_DOWN, ICON_ARROW_RIGHT, ICON_ARROW_UP, ICON_ARROW_LEFT, ICON_CHECK, ICON_RADIO_DOT, ICON_CLOSE, ICON_MINIMIZE,
 ICON_MAXIMIZE, ICON_RESTORE, ICON_RESIZE, ICON_SORT_UP, ICON_SORT_DOWN, ICON_PLUS, ICON_MINUS, ICON_SLIDER_KNOB, ICON_TOGGLE_KNOB,
 ICON_COLLAPSE, ICON_EXPAND, ICON_DRAG_HANDLE, ICON_TOAST, ICON_PICKER, ICON_COUNT) = range(_lib.ICON_COUNT + 1)
"""Icon ids for `theme.icon` and `ui.push_icon()`, the little pictures widgets draw. ICON_COUNT is how many there are."""

ROLE_NAMES = ("none", "window", "button", "checkbox", "radio", "slider", "text", "input", "combo", "list", "item", "tab", "menu",
              "menuitem", "table", "tree", "progress", "image", "group", "dialog")
"""Accessibility role names, in the same order as the ROLE_* ids."""
(ROLE_NONE, ROLE_WINDOW, ROLE_BUTTON, ROLE_CHECKBOX, ROLE_RADIO, ROLE_SLIDER, ROLE_TEXT, ROLE_INPUT, ROLE_COMBO, ROLE_LIST, ROLE_ITEM,
 ROLE_TAB, ROLE_MENU, ROLE_MENUITEM, ROLE_TABLE, ROLE_TREE, ROLE_PROGRESS, ROLE_IMAGE, ROLE_GROUP, ROLE_DIALOG) = range(20)
"""Accessibility roles for `ui.a11y_role()` and `A11yNode.role`."""

A11Y_FOCUSED = 1
"""Accessibility state bit: the node has keyboard focus."""
A11Y_CHECKED = 2
"""Accessibility state bit: checked or on."""
A11Y_DISABLED = 4
"""Accessibility state bit: disabled."""
A11Y_EXPANDED = 8
"""Accessibility state bit: expanded."""
A11Y_SELECTED = 16
"""Accessibility state bit: selected."""
A11Y_ACTIONS = ("press", "set", "expand", "focus")
"""Actions you can send with `ui.a11y_action()`."""

ITEM_DRAG_X = 1
"""Flag for `ui.custom()`: dragging works on the x axis. With only one of the two the drag locks to that axis."""
ITEM_DRAG_Y = 2
"""Flag for `ui.custom()`: dragging works on the y axis."""
ITEM_FOCUSABLE = 4
"""Flag for `ui.custom()`: tab and clicks can give it keyboard focus."""
ITEM_NO_HIT = 8
"""Flag for `ui.custom()`: dont add its area to the mouse catching rects, so clicks pass through to whatever is behind."""
ITEM_REPEAT = 16
"""Flag for `ui.custom()`: holding the mouse down keeps firing clicks, like a scrollbar arrow."""

Sort = namedtuple("Sort", "changed col desc")
"""What `table_sort()` returns, `Sort(changed, col, desc)`."""
Skin = namedtuple("Skin", "bitmap left top right bottom")
"""A bitmap plus its 9 slice borders, `Skin(bitmap, left, top, right, bottom)`. Set it like `theme.skin_button = (bmp, 8)` where one number is used for every border."""


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
    """The theme's icons, indexed by ICON_* id or name like `theme.icon["check"] = bmp`. Set one to None, or `del` it, to go back to the built in one."""
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
        """Reset every icon to the built in one."""
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
    """The colors, sizes, fonts, skins and icons a Ui draws with, at `ui.theme`. The fields are plain attributes: colors (`bg`, `panel`, `border`, `text`, `text_dim`, `accent`, `accent_text`, `hover`, `active`, `input_bg`, `shadow` and more) are 0xAARRGGBB ints, sizes (`radius`, `pad`, `gap`, `font_size`, `item_h` and more) are logical px, `font` and the other fonts take a Font, and `skin_*` take a Skin or (bitmap, border). `theme.copy()` makes a standalone one you can edit and hand to `ui.push_theme()`."""
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
        """The icons, see Icons."""
        return Icons(self)

    @property
    def icon_tint(self):
        """Color multiplied into every icon, 0xAARRGGBB."""
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
        """Switch to the built in dark colors. Leaves the font alone."""
        lib.goome_ui_theme_dark(self._ptr())

    def light(self):
        """Switch to the built in light colors. Leaves the font alone."""
        lib.goome_ui_theme_light(self._ptr())

    @_Either
    def make(self, accent, dark=True, radius=10):
        """Build a whole theme from one accent color. `dark` picks dark or light and `radius` is the corner size. Returns the theme. Also works as `Theme.make(...)` for a new standalone one."""
        lib.goome_ui_theme_make(self._ptr(), int(accent) & 0xFFFFFFFF, int(bool(dark)), float(radius))
        return self

    @_Either
    def preset(self, name):
        """Apply a preset by name ("dark", "light", "midnight", "paper", "mint", "high_contrast", "rose") or PRESET_* id. Returns the theme."""
        i = _named(name, PRESET_NAMES, "preset")
        if lib.goome_ui_theme_preset(self._ptr(), int(i)) != OK:
            raise ValueError("preset has to be one of %s (or goome.PRESET_*), not %r" % (", ".join(PRESET_NAMES), name))
        return self

    def copy(self):
        """A standalone copy you can change and pass to `ui.push_theme()` or `ui.style()`."""
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
        """Every color and size as a dict."""
        t = self._t()
        return dict((n, getattr(t, n)) for n in _lib.THEME_COLORS + _lib.THEME_SIZES)

    def update(self, **kw):
        """Set several fields at once, like `theme.update(accent=0xFF3366FF, radius=6)`. `icons=` takes a dict of icon to Bitmap."""
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
    """State for a `ui.window()`: `x`, `y`, `w`, `h` in logical px (h of 0 fits the content) and `open`. goome moves and resizes it for you, so keep the same Window between frames."""
    def __init__(self, x=40, y=40, w=300, h=0, open=True):
        self._x, self._y, self._w, self._h = c_double(x), c_double(y), c_double(w), c_double(h)
        self._open = c_int(int(bool(open)))

    x = property(lambda s: s._x.value, lambda s, v: setattr(s._x, "value", v), doc="Left edge in logical px.")
    y = property(lambda s: s._y.value, lambda s, v: setattr(s._y, "value", v), doc="Top edge in logical px.")
    w = property(lambda s: s._w.value, lambda s, v: setattr(s._w, "value", v), doc="Width in logical px.")
    h = property(lambda s: s._h.value, lambda s, v: setattr(s._h, "value", v), doc="Height in logical px, 0 fits the content.")
    open = property(lambda s: bool(s._open.value), lambda s, v: setattr(s._open, "value", int(bool(v))), doc="False once the user closed it with the close button. Set it to True to bring it back.")

    def __repr__(self):
        return "Window(%g, %g, %g, %g%s)" % (self.x, self.y, self.w, self.h, "" if self.open else ", closed")


class Flag(object):
    """A boolean goome can flip for you, for `menu_item(checked=)`, `tree(open=)`, `modal(open=)` and `collapsing(open=)`. Read or set `.value`, or just use it in an `if`."""
    def __init__(self, value=False):
        self._v = c_int(int(bool(value)))

    value = property(lambda s: bool(s._v.value), lambda s, v: setattr(s._v, "value", int(bool(v))), doc="The current bool.")

    def __bool__(self):
        return bool(self._v.value)

    def toggle(self):
        """Flip the value."""
        self.value = not self.value

    def __repr__(self):
        return "Flag(%s)" % self.value


class Split(object):
    """State for a `ui.split()`: `frac` is the first pane's share (0 to 1) and `vertical` picks the direction. goome updates it when the divider is dragged."""
    def __init__(self, frac=0.5, vertical=False):
        self._f = c_double(frac)
        self.vertical = vertical

    frac = property(lambda s: s._f.value, lambda s, v: setattr(s._f, "value", v), doc="The first pane's share, 0 to 1.")

    def __repr__(self):
        return "Split(%g%s)" % (self.frac, ", vertical" if self.vertical else "")


class Item(object):
    """What `ui.custom()` hands back for your own widget. Truthy when something happened (`changed`).

    Fields: `x`, `y`, `w`, `h` (logical), `hovered`, `pressed`, `held`, `released`, `clicked`, `double_clicked`, `right_clicked`, `focused`, `mx`, `my` (pointer), `dx`, `dy` (moved this frame while held), `drag_x`, `drag_y` (since the press) and `key` (key pressed this frame while focused, with the mods ored in, 0 for none).
    """
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


def ease(kind, t):
    """Run the easing curve `kind` (a name like "out" or an EASE_* id) on `t` from 0 to 1 and get the eased value."""
    return lib.goome_ease(_named(kind, EASE_NAMES, "ease"), float(t))


class A11yNode(object):
    """One node of the accessibility tree from `ui.a11y_tree()`: `role`, `parent` (index, -1 for none), `states` (A11Y_* bits), `x`, `y`, `w`, `h`, `label`, `value`, `id`, `num`, `min`, `max` and `caret`."""
    __slots__ = ("index", "role", "parent", "states", "x", "y", "w", "h", "label", "value", "id", "num", "min", "max", "caret")

    def __init__(self, s, index):
        self.index = index
        self.role = s.role
        self.parent = s.parent
        self.states = s.states
        self.x, self.y, self.w, self.h = s.x, s.y, s.w, s.h
        self.label = _s(s.label)
        self.value = _s(s.value)
        self.id = s.id
        self.num, self.min, self.max = s.num, s.min, s.max
        self.caret = s.caret

    @property
    def role_name(self):
        """The role as a word, like "button"."""
        return ROLE_NAMES[self.role] if 0 <= self.role < len(ROLE_NAMES) else str(self.role)

    @property
    def rect(self):
        """Position and size as (x, y, w, h)."""
        return (self.x, self.y, self.w, self.h)

    focused = property(lambda self: bool(self.states & A11Y_FOCUSED), doc="True if it has keyboard focus.")
    checked = property(lambda self: bool(self.states & A11Y_CHECKED), doc="True if checked or on.")
    disabled = property(lambda self: bool(self.states & A11Y_DISABLED), doc="True if disabled.")
    expanded = property(lambda self: bool(self.states & A11Y_EXPANDED), doc="True if expanded.")
    selected = property(lambda self: bool(self.states & A11Y_SELECTED), doc="True if selected.")

    def __repr__(self):
        more = " = %r" % self.value if self.value else ""
        return "A11yNode(%d %s %r%s, parent %d)" % (self.index, self.role_name, self.label, more, self.parent)


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
    """What the begin style calls return (`window`, `menu`, `popup` and so on). Truthy when the content is open, and as a `with` block it calls the matching end for you."""
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
    """What `ui.table()` returns. Use it as a `with` block and call its `column()`, `row()` and `next()`."""
    def __init__(self, ui, shown):
        Shown.__init__(self, shown, ui.table_end)
        self._ui = ui

    def __enter__(self):
        return self

    def column(self, name, width=0):
        """Add a column. `width` 0 shares what is left."""
        self._ui.table_column(name, width)

    def sort(self, col=0, desc=False):
        """Check the sort state, returns a Sort. Call it after the columns."""
        return self._ui.table_sort(col, desc)

    def row(self):
        """Start a row."""
        self._ui.table_row()

    def next(self):
        """Move to the next cell."""
        self._ui.table_next()


class Panes(Shown):
    """What `ui.split()` returns. Use it as a `with` block and call `next()` between the two panes."""
    def __init__(self, ui, shown):
        Shown.__init__(self, shown, ui.split_end)
        self._ui = ui

    def __enter__(self):
        return self

    def next(self):
        """Move on to the second pane."""
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


_NUM_FMT = re.compile(rb"(?:[^%]|%%)*(?:%[-+ #0]*\d*(?:\.\d+)?[eEfFgG](?:[^%]|%%)*)?")


def _num_fmt(fmt):
    raw = _b(fmt)
    if raw is not None and not _NUM_FMT.fullmatch(raw):
        raise ValueError("%r isnt a number format, use something like \"%%.2f\"" % (fmt,))
    return raw


def _strs(items):
    bs = [_b(i) for i in items]
    return (c_char_p * max(1, len(bs)))(*bs), len(bs)


class Ui(object):
    """The immediate mode ui. Make one with `g.ui()`. Each frame: `ui.begin()`, call widgets, `ui.end()` (or `with ui.frame():`). Widgets that hold a value take it and return the new one, like `x = ui.slider("Size", x)`, and `ui.changed` says if the last widget changed. Sizes are logical px. Begin calls like `window()` return a Shown you can use in a `with` block.

    Attributes: `theme` (a Theme), `config` (a Config), `changed` (True if the last widget changed its value or was clicked) and `entered` (True if the last `input_ex()` ended with enter, needs INPUT_ENTER_RETURNS)."""
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
        """True once close() ran."""
        return self._u is None

    def close(self):
        """Free the ui. Closing the goome does it too."""
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
        """Give the ui an event. Returns True if it used it, so you can skip your own handling."""
        return bool(lib.goome_ui_feed(self._h(), byref(ev.raw)))

    def begin(self, mon=0):
        """Start a frame on a monitor and return its Canvas, or None if there is nothing to draw on (skip the frame, but still call `end()` only if this wasnt None)."""
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
        """Finish the frame and send it, with every widget's area catching the mouse."""
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
        """Context manager for a frame: `with ui.frame() as canvas:` calls begin and end."""
        return _UiFrame(self, mon)

    def hit(self, x, y, w, h):
        """Make this rect (logical) catch the mouse, for things you drew yourself."""
        lib.goome_ui_hit(self._h(), x, y, w, h)

    @property
    def animating(self):
        """True while something is still moving, so draw again soon."""
        return bool(lib.goome_ui_animating(self._h()))

    def window(self, title, win, flags=WIN_MOVE | WIN_COLLAPSE):
        """A floating window. `win` is a Window kept between frames, `flags` is WIN_* ored together. Draw the contents if it returns true.

        Use as `with ui.window("Title", win):`.
        """
        r = lib.goome_ui_window(self._h(), _b(title), byref(win._x), byref(win._y), byref(win._w), byref(win._h), int(flags), byref(win._open))
        self._scope.append(("window", title))
        self._wins.append(win)
        return Shown(r, self.window_end)

    def window_end(self):
        """End a window by hand, only needed if you didnt use `with`."""
        lib.goome_ui_window_end(self._h())
        if self._scope:
            self._scope.pop()
        if self._wins:
            self._wins.pop()

    def row(self, cols):
        """Lay the next `cols` widgets out side by side in equal columns."""
        lib.goome_ui_row(self._h(), int(cols))

    def same_line(self):
        """Put the next widget on the same line as the last one."""
        lib.goome_ui_same_line(self._h())

    def space(self, px):
        """Empty gap of `px`."""
        lib.goome_ui_space(self._h(), px)

    def separator(self):
        """A thin line across."""
        lib.goome_ui_separator(self._h())

    def width(self, w):
        """Width of the next widget only, 0 fills."""
        lib.goome_ui_width(self._h(), w)

    def label(self, text):
        """A line of text."""
        lib.goome_ui_label(self._h(), b"%s", c_char_p(_b(text)))

    def heading(self, text):
        """A bigger line of text."""
        lib.goome_ui_heading(self._h(), _b(text))

    def wrapped(self, text):
        """Text that wraps to the width."""
        lib.goome_ui_wrapped(self._h(), _b(text))

    def button(self, label):
        """A button. Returns True the frame it is clicked."""
        r = bool(lib.goome_ui_button(self._h(), _b(label)))
        self.changed = r
        return r

    def image_button(self, id, bmp, w, h):
        """A button with a Bitmap on it, `id` tells it apart from other buttons. Returns True when clicked."""
        r = bool(lib.goome_ui_image_button(self._h(), _b(id), bmp._ref(), w, h))
        self.changed = r
        return r

    def image(self, bmp, w, h, radius=0):
        """Show a Bitmap at w by h, with optional rounded corners."""
        lib.goome_ui_image(self._h(), bmp._ref(), w, h, radius)

    def _flag(self, fn, label, value):
        v = c_int(int(bool(value)))
        self.changed = bool(fn(self._h(), _b(label), byref(v)))
        return bool(v.value)

    def checkbox(self, label, value):
        """A checkbox. Pass the current bool and get the new one back."""
        return self._flag(lib.goome_ui_checkbox, label, value)

    def toggle(self, label, value):
        """A switch. Pass the current bool and get the new one back."""
        return self._flag(lib.goome_ui_toggle, label, value)

    def radio(self, label, value, option):
        """A radio button. `value` is the currently picked option and `option` is the one this button stands for, returns the new picked one."""
        v = c_int(int(value))
        self.changed = bool(lib.goome_ui_radio(self._h(), _b(label), byref(v), int(option)))
        return v.value

    def slider(self, label, value, lo=0.0, hi=1.0, fmt=None):
        """A float slider from `lo` to `hi`. `fmt` is a printf format for the shown number, like "%.1f". Returns the new value."""
        v = c_double(value)
        self.changed = bool(lib.goome_ui_slider(self._h(), _b(label), byref(v), lo, hi, _num_fmt(fmt)))
        return v.value

    def slider_int(self, label, value, lo=0, hi=100):
        """An int slider from `lo` to `hi`. Returns the new value."""
        v = c_int(int(value))
        self.changed = bool(lib.goome_ui_slider_int(self._h(), _b(label), byref(v), int(lo), int(hi)))
        return v.value

    def input(self, label, text, cap=256):
        """A one line text box. Returns the text, `cap` is the most bytes it can hold."""
        buf = ctypes.create_string_buffer(_cut(text, cap), cap)
        self.changed = bool(lib.goome_ui_input(self._h(), _b(label), buf, cap))
        self.entered = False
        return _s(buf.value)

    def input_ex(self, label, text, flags=0, hint=None, cap=256):
        """A text box with INPUT_* flags and a `hint` shown while empty. Returns the text, and `ui.entered` says if enter was pressed."""
        buf = ctypes.create_string_buffer(_cut(text, cap), cap)
        r = lib.goome_ui_input_ex(self._h(), _b(label), buf, cap, int(flags), _b(hint))
        self.changed = r != 0
        self.entered = r == 2
        return _s(buf.value)

    def password(self, label, text, hint=None, flags=0, cap=256):
        """A text box that shows dots, same as `input_ex()` with INPUT_PASSWORD."""
        return self.input_ex(label, text, INPUT_PASSWORD | int(flags), hint, cap)

    def combo(self, label, sel, items):
        """A dropdown. `sel` is the picked index, `items` the strings. Returns the new index."""
        arr, n = _strs(items)
        v = c_int(int(sel))
        self.changed = bool(lib.goome_ui_combo(self._h(), _b(label), byref(v), arr, n))
        return v.value

    def selectable(self, label, selected=False):
        """A row that can be picked, drawn highlighted when `selected`. Returns True when clicked."""
        r = bool(lib.goome_ui_selectable(self._h(), _b(label), int(bool(selected))))
        self.changed = r
        return r

    def tabs(self, id, names, sel):
        """A tab strip. `id` tells it apart from other ones, `names` are the tabs, `sel` the picked index. Returns the new index."""
        arr, n = _strs(names)
        v = c_int(int(sel))
        self.changed = bool(lib.goome_ui_tabs(self._h(), _b(id), arr, n, byref(v)))
        return v.value

    def collapsing(self, label, open=None):
        """A header that folds its content. Returns True while open, so draw the content then. Pass a Flag as `open` to keep the state yourself."""
        if open is None:
            r = bool(lib.goome_ui_collapsing(self._h(), _b(label), None))
            self.changed = False
            return r
        v = c_int(int(bool(open)))
        r = bool(lib.goome_ui_collapsing(self._h(), _b(label), byref(v)))
        self.changed = bool(v.value) != bool(open)
        return r

    def progress(self, frac, text=None):
        """A progress bar, `frac` from 0 to 1, with optional text on it."""
        lib.goome_ui_progress(self._h(), frac, _b(text))

    def color(self, label, argb):
        """A color picker. Takes and returns 0xAARRGGBB."""
        v = c_uint32(int(argb) & 0xFFFFFFFF)
        self.changed = bool(lib.goome_ui_color(self._h(), _b(label), byref(v)))
        return v.value

    def tooltip(self, text):
        """Show a tooltip when the widget right before this call is hovered."""
        lib.goome_ui_tooltip(self._h(), _b(text))

    @property
    def hovered(self):
        """True if the mouse is over the widget right before it."""
        return bool(lib.goome_ui_hovered(self._h()))

    def scroll_begin(self, id, h=0):
        """A scroll area `h` tall (0 fills the rest). Draw the contents if it returns true, and end it with `scroll_end()` (or use `with`)."""
        return Shown(lib.goome_ui_scroll_begin(self._h(), _b(id), h), self.scroll_end)

    def scroll_end(self):
        """End a scroll area by hand."""
        lib.goome_ui_scroll_end(self._h())

    def push_id(self, id):
        """Add to the id of the widgets after it. Use it when a loop makes widgets with the same label, push the index first. Pair with pop_id()."""
        lib.goome_ui_push_id(self._h(), _b(str(id) if not isinstance(id, (str, bytes)) else id))
        self._scope.append(("id", id))

    def pop_id(self):
        """Undo the last push_id()."""
        lib.goome_ui_pop_id(self._h())
        if self._scope:
            self._scope.pop()

    def id(self, id):
        """`with ui.id(i):` is push_id and pop_id in one."""
        self.push_id(id)
        return Shown(True, self.pop_id)

    def app(self, title=None, flags=0):
        """A root panel that fills the monitor, call it right after `begin()`. `flags` is APP_* ored together. What App uses under the hood."""
        return Shown(lib.goome_ui_app(self._h(), _b(title), int(flags)), self.app_end)

    def app_end(self):
        """End the app panel by hand."""
        lib.goome_ui_app_end(self._h())

    def menubar(self):
        """The menu bar of the app panel (needs APP_MENUBAR). Draw menus inside if it returns true."""
        return Shown(lib.goome_ui_menubar_begin(self._h()), self.menubar_end, always=False)

    def menubar_end(self):
        """End the menu bar by hand."""
        lib.goome_ui_menubar_end(self._h())

    def menu(self, label):
        """A menu in the menu bar. Draw items if it returns true. Menus can nest for submenus."""
        return Shown(lib.goome_ui_menu_begin(self._h(), _b(label)), self.menu_end, always=False)

    def menu_end(self):
        """End a menu by hand."""
        lib.goome_ui_menu_end(self._h())

    def menu_item(self, label, shortcut=None, checked=None):
        """An item in a menu. `shortcut` is just text shown on the right, `checked` is an optional Flag for a tick. Returns True when clicked."""
        r = bool(lib.goome_ui_menu_item(self._h(), _b(label), _b(shortcut), _ref(checked, "menu_item checked")))
        self.changed = r
        return r

    def menu_separator(self):
        """A line between menu items."""
        lib.goome_ui_menu_separator(self._h())

    def context(self, id):
        """A right click menu for the widget right before it (or empty space). Draw its items if it returns true."""
        return Shown(lib.goome_ui_context_begin(self._h(), _b(id)), self.context_end, always=False)

    def context_end(self):
        """End a context menu by hand."""
        lib.goome_ui_context_end(self._h())

    def popup_open(self, id):
        """Open the popup with this id."""
        lib.goome_ui_popup_open(self._h(), _b(id))

    def popup(self, id):
        """A popup that stays open until closed. Draw its content if it returns true."""
        return Shown(lib.goome_ui_popup_begin(self._h(), _b(id)), self.popup_end, always=False)

    def popup_end(self):
        """End a popup by hand."""
        lib.goome_ui_popup_end(self._h())

    def popup_close(self):
        """Close the innermost open popup, menu or modal."""
        lib.goome_ui_popup_close(self._h())

    def modal(self, title, open=None):
        """A centered dialog that dims everything else, esc closes it. `open` is a Flag that holds whether it shows."""
        return Shown(lib.goome_ui_modal_begin(self._h(), _b(title), _ref(open, "modal open")), self.modal_end, always=False)

    def modal_end(self):
        """End a modal by hand."""
        lib.goome_ui_modal_end(self._h())

    def toast(self, text, ms=2500):
        """A message that pops up and fades after `ms`."""
        lib.goome_ui_toast(self._h(), _b(text), int(ms))

    def statusbar(self, text):
        """Text for the status bar, needs APP_STATUSBAR."""
        lib.goome_ui_statusbar(self._h(), _b(text))

    @property
    def focused(self):
        """True if the widget right before it has keyboard focus."""
        return bool(lib.goome_ui_focused(self._h()))

    def set_focus(self):
        """Give keyboard focus to the next widget."""
        lib.goome_ui_set_focus(self._h())

    @property
    def wants(self):
        """WANT_* bits for what the ui wants from the os right now. Good after `feed()` and `end()`."""
        return lib.goome_ui_wants(self._h())

    @property
    def wants_mouse(self):
        """True if the ui wants the mouse right now."""
        return bool(self.wants & WANT_MOUSE)

    @property
    def wants_keyboard(self):
        """True if the ui wants the keyboard right now."""
        return bool(self.wants & WANT_KEYBOARD)

    @property
    def auto_grab(self):
        """WANT_* bits the ui takes from the os by itself, both by default. Set 0 if the app does the grabbing."""
        return self._auto_grab

    @auto_grab.setter
    def auto_grab(self, wants):
        lib.goome_ui_auto_grab(self._h(), int(wants))
        self._auto_grab = int(wants)

    def text_edit(self, id, text, h=0, flags=0, cap=None):
        """A multi line text editor. Returns the text. `h` is the height, `flags` is EDIT_* ored together, `cap` the most bytes it can hold (it grows by default)."""
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
        """A table with `cols` columns, `h` tall. Returns a Table, use it in a `with` block."""
        return Table(self, lib.goome_ui_table_begin(self._h(), _b(id), int(cols), h, int(flags)))

    def table_column(self, name, width=0):
        """Add a column to the table, `width` 0 shares what is left."""
        lib.goome_ui_table_column(self._h(), _b(name), width)

    def table_sort(self, col=0, desc=False):
        """A Sort telling if a header was clicked this frame and which column and direction. Call it after the columns."""
        c, d = c_int(int(col)), c_int(int(bool(desc)))
        r = bool(lib.goome_ui_table_sort(self._h(), byref(c), byref(d)))
        return Sort(r, c.value, bool(d.value))

    def table_row(self):
        """Start a table row."""
        lib.goome_ui_table_row(self._h())

    def table_next(self):
        """Move to the next cell."""
        lib.goome_ui_table_next(self._h())

    def table_end(self):
        """End the table by hand."""
        lib.goome_ui_table_end(self._h())

    def tree(self, label, open=None):
        """A tree node. Draw its children if it returns true. A Flag as `open` keeps the state yourself."""
        return Shown(lib.goome_ui_tree(self._h(), _b(label), _ref(open, "tree open")), self.tree_end, always=False)

    def tree_end(self):
        """End a tree node by hand."""
        lib.goome_ui_tree_end(self._h())

    def list_clip(self, count, row_h=0):
        """For long lists inside a scroll area: returns a range of the rows that are visible, so you only draw those."""
        first, last = c_int(0), c_int(0)
        lib.goome_ui_list_clip(self._h(), int(count), row_h, byref(first), byref(last))
        return range(first.value, last.value)

    def drag_float(self, label, value, speed=1.0, lo=0.0, hi=0.0, fmt=None):
        """A number you drag left and right to change. `speed` is the change per px, `lo` and `hi` limit it (both 0 means no limit). Returns the new value."""
        v = c_double(value)
        self.changed = bool(lib.goome_ui_drag_float(self._h(), _b(label), byref(v), speed, lo, hi, _num_fmt(fmt)))
        return v.value

    def drag_int(self, label, value, speed=1.0, lo=0, hi=0):
        """Same as `drag_float()` but whole numbers."""
        v = c_int(int(value))
        self.changed = bool(lib.goome_ui_drag_int(self._h(), _b(label), byref(v), speed, int(lo), int(hi)))
        return v.value

    def number(self, label, value, step=1.0, fmt=None):
        """A number box with minus and plus buttons, `step` is how much they add. Returns the new value."""
        v = c_double(value)
        self.changed = bool(lib.goome_ui_number(self._h(), _b(label), byref(v), step, _num_fmt(fmt)))
        return v.value

    def _plot(self, fn, label, values, lo, hi, h):
        arr, n, keep = _floats(values)
        if lo is None or hi is None:
            vals = arr[:n]
            lo = (min(vals) if vals else 0.0) if lo is None else lo
            hi = (max(vals) if vals else 1.0) if hi is None else hi
        fn(self._h(), _b(label), arr, n, lo, hi, h)

    def plot_lines(self, label, values, lo=None, hi=None, h=60):
        """Line graph of a list of numbers. `lo` and `hi` are the range, fitted to the data by default."""
        self._plot(lib.goome_ui_plot_lines, label, values, lo, hi, h)

    def plot_bars(self, label, values, lo=None, hi=None, h=60):
        """Bar graph of a list of numbers. `lo` and `hi` are the range, fitted to the data by default."""
        self._plot(lib.goome_ui_plot_bars, label, values, lo, hi, h)

    def split(self, id, pane=None, vertical=None):
        """Two panes with a draggable divider. Pass your own Split to keep the state, `vertical` stacks them top and bottom. Returns Panes, use it in a `with` block."""
        if pane is None:
            pane = self._panes.get(id)
            if pane is None:
                pane = self._panes[id] = Split()
        v = pane.vertical if vertical is None else vertical
        return Panes(self, lib.goome_ui_split_begin(self._h(), _b(id), int(bool(v)), byref(pane._f)))

    def split_next(self):
        """Move on to the second pane."""
        lib.goome_ui_split_next(self._h())

    def split_end(self):
        """End the split by hand."""
        lib.goome_ui_split_end(self._h())

    def drag_source(self, type, data):
        """Make the widget right before it draggable and carry `data` of this `type`. Returns True while it is being dragged."""
        raw = _b(data) if isinstance(data, str) else bytes(data)
        return bool(lib.goome_ui_drag_source(self._h(), _b(type), raw, len(raw)))

    def drop_target(self, type, cap=4096):
        """Make the widget right before it accept drops of this `type`. Returns the dropped bytes, or None."""
        buf = ctypes.create_string_buffer(int(cap))
        n = lib.goome_ui_drop_target(self._h(), _b(type), buf, int(cap))
        return buf.raw[: min(n, int(cap))] if n > 0 else None

    def spinner(self, size=16):
        """A loading spinner."""
        lib.goome_ui_spinner(self._h(), size)

    def link(self, text):
        """Clickable link text. Returns True when clicked."""
        r = bool(lib.goome_ui_link(self._h(), _b(text)))
        self.changed = r
        return r

    def badge(self, text, argb=None):
        """A small colored label, in the accent color unless you give `argb`."""
        lib.goome_ui_badge(self._h(), _b(text), int(self.theme.accent if argb is None else argb) & 0xFFFFFFFF)


    def pos(self, x, y):
        """Put the next widget at x, y from the content's top left (scroll included) without moving the layout."""
        lib.goome_ui_pos(self._h(), x, y)

    def size(self, w=0, h=0):
        """Size of the next widget, 0 keeps its own size on that side."""
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
        """Change a color for everything after this, until `pop()`. `what` is an S_* id or a field name like "accent"."""
        what = self._style_id(what, STYLE_COLORS)
        lib.goome_ui_push_color(self._h(), what, int(argb) & 0xFFFFFFFF)
        self._pin()

    def push_num(self, what, v):
        """Change a number (radius, pad, gap and so on) until `pop()`. `what` is an S_* id or a field name."""
        what = self._style_id(what, STYLE_NUMS)
        lib.goome_ui_push_num(self._h(), what, _style_value(STYLE_NAMES[what], v))
        self._pin()

    def push_radii(self, r):
        """Per corner radii until `pop()`, beats the radius setting."""
        lib.goome_ui_push_radii(self._h(), _radii(r))
        self._pin()

    def push_font(self, font):
        """Change the font until `pop()`. None is the built in one."""
        lib.goome_ui_push_font(self._h(), None if font is None else font._h())
        self._pin(font)

    def push_skin(self, kind, skin):
        """Change a widget skin until `pop()`. `kind` is a SKIN_* id or name, `skin` is (bitmap, border) or (bitmap, l, t, r, b), None removes it."""
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
        """Change an icon until `pop()`. `icon` is an ICON_* id or name, `bmp` None goes back to the built in one."""
        icon = _icon_id(icon)
        if bmp is None:
            lib.goome_ui_push_icon(self._h(), icon, None)
            self._pin()
            return
        bmp._ref()
        lib.goome_ui_push_icon(self._h(), icon, ctypes.pointer(bmp._s))
        self._pin(bmp)

    def push_theme(self, theme):
        """Swap the whole theme, in one push, until `pop()`."""
        if not isinstance(theme, Theme):
            raise TypeError("push_theme needs a Theme, like ui.theme.copy(), not %r" % theme)
        lib.goome_ui_push_theme(self._h(), theme._ptr())
        self._pin(theme)

    def pop(self, n=1):
        """Undo the last `n` pushes, of any kind."""
        n = int(n)
        lib.goome_ui_pop(self._h(), n)
        if n > 0:
            cut = max(0, len(self._pins) - n)
            self._spent += self._pins[cut:]
            del self._pins[cut:]

    def style(self, theme=None, **kw):
        """Push several style changes at once and pop them when the `with` block ends, like `with ui.style(accent=0xFF00AA00, radius=4):`. Takes a Theme, theme field names, `radii`, `font`, `skin`, `icon` and `icons`."""
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
        """Scale the whole ui, 2 is twice as big."""
        lib.goome_ui_scale(self._h(), float(s))

    def anim(self, id, target, ms=200, ease=EASE_OUT):
        """Animate toward `target`. Call it every frame with the same `id` and it eases the number over `ms`. Returns the current value."""
        return lib.goome_ui_anim(self._h(), _b(id), float(target), float(ms), _named(ease, EASE_NAMES, "ease"))

    def anim_color(self, id, target, ms=200, ease=EASE_OUT):
        """Same as `anim()` but for a 0xAARRGGBB color."""
        return lib.goome_ui_anim_color(self._h(), _b(id), int(target) & 0xFFFFFFFF, float(ms), _named(ease, EASE_NAMES, "ease"))

    def a11y(self, on=True):
        """Turn the accessibility tree on or off."""
        lib.goome_ui_a11y(self._h(), int(bool(on)))

    def a11y_role(self, role, label=None):
        """Set the accessibility role and label of the next widget."""
        lib.goome_ui_a11y_role(self._h(), _named(role, ROLE_NAMES, "role"), _b(label))

    def a11y_value(self, value):
        """Set the accessibility value text of the next widget."""
        lib.goome_ui_a11y_value(self._h(), _b(value))

    def a11y_tree(self):
        """The accessibility tree of the last frame as a list of A11yNode."""
        n = lib.goome_a11y_tree(self._h(), None, 0)
        while n > 0:
            arr = (_lib.A11yNodeS * n)()
            m = lib.goome_a11y_tree(self._h(), arr, n)
            if m <= n:
                return [A11yNode(arr[i], i) for i in range(m)]
            n = m
        return []

    def a11y_action(self, action, node, text=None):
        """Do an accessibility action on a node (A11yNode or its id): "press", "set" (with `text`), "expand" or "focus"."""
        if action not in A11Y_ACTIONS:
            raise ValueError("a11y action is one of %s, not %r" % (", ".join(A11Y_ACTIONS), action))
        nid = node.id if isinstance(node, A11yNode) else int(node)
        msg = "a11y %s %d" % (action, nid) + ("" if text is None else " %s" % text)
        self._g.push(CONTROL, msg=msg)

    def custom(self, id, w=0, h=0, flags=0):
        """Reserve a w by h spot for your own widget and get an Item back with the mouse and focus state. Draw it yourself on `ui.canvas`. `flags` is ITEM_* ored together."""
        s = _lib.ItemS()
        r = lib.goome_ui_custom(self._h(), _b(id), w, h, int(flags), byref(s))
        it = Item(s, r)
        self.changed = it.changed
        return it

    @property
    def canvas(self):
        """A Canvas that draws right here in the ui, clipped like the widgets. Use it after `custom()`. None if nothing is being drawn."""
        p = lib.goome_ui_canvas(self._h())
        if not p:
            return None
        c = Canvas(p, self._g)
        self._layers.append(c)
        return c

    def store(self, id, n):
        """`n` floats (a memoryview of doubles) kept for this `id` between frames, zero the first time."""
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
    """The mouse cursor each widget uses, indexed by CUR_* id or name, like `ui.config.cursor["button"] = "hand"`. Values are CURSOR_* ids or names."""
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
    """Behavior settings at `ui.config`: delays in ms (`tip_delay_ms`, `dbl_click_ms`, `repeat_delay_ms`, `repeat_ms`, `blink_ms`, `menu_delay_ms`, `toast_ms`), `dbl_click_px`, `drag_px`, `scroll_lines`, the toggles `raise_on_click`, `esc_closes`, `tab_nav` and `focus_on_mouse`, and `cursor`, `keys()`, `bind()`, `ease` and `mask`."""
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
        """Cursor per widget, see Cursors."""
        return Cursors(self)

    def keys(self, action):
        """The key combos bound to an action (ACT_* id or name) as a list of (key, mods)."""
        row = self._c().keys[_named_id(action, ACT_NAMES, ACT_COUNT, "action")]
        return [(k.key, k.mods) for k in row if k.key]

    def bind(self, action, combos):
        """Rebind an action to key combos, a string like "ctrl+c ctrl+insert" or a list of them. Raises BadArg if it cant read them."""
        i = _named_id(action, ACT_NAMES, ACT_COUNT, "action")
        raw = _combo_list(combos)
        rc = lib.goome_ui_bind(self._ui._h(), i, raw)
        if rc != OK:
            raise error_for(rc, "cant read the keys %r" % combos)

    def reset(self):
        """Put every setting back to the default."""
        lib.goome_ui_config_default(ctypes.pointer(self._c()))
        self._drop()

    @property
    def ease(self):
        """A function taking t (0 to 1) and returning a number, used by EASE_CUSTOM. None to remove."""
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
        """The character shown instead of the text in password inputs, "*" by default."""
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
