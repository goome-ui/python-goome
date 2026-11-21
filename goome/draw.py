import ctypes
import weakref
from ctypes import byref, c_double, c_uint32

from . import _lib
from ._lib import lib
from .core import EARG, EGONE, OK, GoomeError, Rect, _b, _rect, _s, error_for, pixel_view, u32_buffer

Radii = _lib.RadiiS
"""Per corner radii, `Radii(tl, tr, br, bl)`. Anywhere a radius is wanted you can also pass a number, or a 4 tuple in that order."""

DIR_AUTO, DIR_LTR, DIR_RTL = range(3)
"""Text directions for `text_dir()`: DIR_AUTO reads it from the first strong letter of each line, DIR_LTR and DIR_RTL force one."""
DIR_NAMES = ("auto", "ltr", "rtl")
"""Text direction names you can pass as a string."""


def radius(r):
    """A Radii with the same radius on all four corners."""
    return lib.goome_radius(float(r))


def _radii(r):
    if isinstance(r, Radii):
        return r
    if isinstance(r, (int, float)):
        return lib.goome_radius(float(r))
    tl, tr, br, bl = r
    return Radii(tl, tr, br, bl)


def _c(argb):
    return int(argb) & 0xFFFFFFFF


def set_font(font):
    """Pick one of the built in fonts for plain `text()` calls. See font_count()."""
    lib.goome_set_font(int(font))


def text_dir(dir=DIR_AUTO):
    """Set the paragraph direction for all text, DIR_AUTO / DIR_LTR / DIR_RTL or "auto" / "ltr" / "rtl"."""
    if isinstance(dir, str):
        if dir.lower() not in DIR_NAMES:
            raise ValueError("text direction is one of %s, not %r" % (", ".join(DIR_NAMES), dir))
        dir = DIR_NAMES.index(dir.lower())
    lib.goome_text_dir(int(dir))


def font_count():
    """How many built in fonts there are."""
    return lib.goome_font_count()


def _fh(font):
    if font is None:
        return None
    return font._h()


def measure(text, size, font=None):
    """Size of some text as `(width, height)` in logical px. `font` is a Font, None is the built in one."""
    h = c_double()
    w = lib.goome_text_measure(_fh(font), size, _b(text), byref(h))
    return w, h.value


def line_height(size, font=None):
    """Height of one line of text at this size, in logical px."""
    return lib.goome_text_line_height(_fh(font), size)


class Canvas(object):
    """What you draw on. Get one from `g.begin()` or `ui.begin()`, or make your own pixel buffer with `Canvas.new()`. All coords are logical, the canvas scales them to real px. Colors are plain 0xAARRGGBB ints.

    Read only fields: `w`, `h`, `stride` (real px, stride in pixels), `scale` (real px per logical px), `ox` and `oy` (logical spot of the first pixel) and `mon`.
    """
    def __init__(self, ptr, g=None, own=None):
        self._ptr = ptr
        self._g = g
        self._own = own
        self._hits = []

    @classmethod
    def new(cls, w, h, stride=None, scale=1.0, ox=0.0, oy=0.0):
        """Make a canvas on your own pixel buffer, for drawing to an image with no goome open. Size is in real px, `scale` is real px per logical px."""
        stride = w if stride is None else stride
        if w < 0 or h < 0 or stride < w:
            raise ValueError("bad canvas size %dx%d stride %d" % (w, h, stride))
        s = _lib.CanvasS()
        buf = (c_uint32 * max(1, h * stride))()
        s.px = ctypes.cast(buf, ctypes.POINTER(c_uint32))
        s.w, s.h, s.stride, s.scale, s.ox, s.oy = w, h, stride, scale, ox, oy
        return cls(ctypes.pointer(s), None, (s, buf))

    def _p(self):
        if self._ptr is None:
            raise GoomeError(EGONE, "this canvas got handed back with end(), get a new one from begin()")
        return self._ptr

    def _take(self):
        p = self._p()
        if self._own is None:
            self._ptr = None
        return p

    @property
    def valid(self):
        """False once the canvas was handed back with end()."""
        return self._ptr is not None

    @property
    def raw(self):
        """The ctypes struct under the canvas."""
        return self._p().contents

    w = property(lambda self: self.raw.w, doc="Width in real px.")
    h = property(lambda self: self.raw.h, doc="Height in real px.")
    stride = property(lambda self: self.raw.stride, doc="Pixels per row.")
    scale = property(lambda self: self.raw.scale, doc="Real px per logical px.")
    ox = property(lambda self: self.raw.ox, doc="Logical x of the first pixel.")
    oy = property(lambda self: self.raw.oy, doc="Logical y of the first pixel.")
    mon = property(lambda self: self.raw.mon, doc="Monitor id this canvas is for.")

    @property
    def drawn(self):
        """Rect (real px) that got drawn on since the last clear."""
        r = self.raw
        return Rect(r.dx0, r.dy0, r.dx1 - r.dx0, r.dy1 - r.dy0)

    @property
    def pixels(self):
        """The pixels as a memoryview of premultiplied argb ints."""
        r = self.raw
        return pixel_view(r.px, r.h, r.stride)

    def row(self, y):
        """One row of pixels, `w` long."""
        s = self.stride
        return self.pixels[y * s : y * s + self.w]

    def hit(self, x, y, w, h):
        """Make this rect catch the mouse. Anywhere nothing is marked, clicks go through the overlay."""
        self._hits.append(_rect((x, y, w, h)))

    def damage(self, rect=None):
        """Tell goome this rect (logical) changed because you wrote the pixels yourself. None means everything."""
        r = _rect(rect)
        lib.goome_damage(self._p(), byref(r) if r is not None else None)

    def clear(self):
        """Wipe the whole canvas to see-through."""
        lib.goome_clear(self._p())

    def rect(self, x, y, w, h, argb):
        """Filled rectangle."""
        lib.goome_draw_rect(self._p(), x, y, w, h, _c(argb))

    def round_rect(self, x, y, w, h, radius, argb):
        """Filled rectangle with the same radius on every corner."""
        lib.goome_draw_round_rect(self._p(), x, y, w, h, radius, _c(argb))

    def frame(self, x, y, w, h, width, argb):
        """Rectangle outline, `width` thick."""
        lib.goome_draw_frame(self._p(), x, y, w, h, width, _c(argb))

    def line(self, x0, y0, x1, y1, width, argb):
        """Line from x0, y0 to x1, y1, `width` thick."""
        lib.goome_draw_line(self._p(), x0, y0, x1, y1, width, _c(argb))

    def triangle(self, x0, y0, x1, y1, x2, y2, argb):
        """Filled triangle."""
        lib.goome_draw_triangle(self._p(), x0, y0, x1, y1, x2, y2, _c(argb))

    def image(self, x, y, w, h, pixels, iw, ih):
        """Draw raw pixels (0xAARRGGBB, `iw` x `ih`) stretched into the box x, y, w, h."""
        arr, keep = u32_buffer(pixels, iw * ih)
        lib.goome_draw_image(self._p(), x, y, w, h, ctypes.cast(arr, ctypes.POINTER(c_uint32)), iw, ih)

    def erase(self, x, y, w, h):
        """Cut a see-through hole in the rect."""
        lib.goome_erase(self._p(), x, y, w, h)

    def text(self, x, y, text, argb=0xFFFFFFFF, big=False):
        """Draw text with the built in font and return its width. `y` is the top. `big` picks the larger size."""
        return lib.goome_draw_text(self._p(), x, y, _b(text), int(bool(big)), _c(argb))

    def text_width(self, text, big=False):
        """Width of text in the built in font."""
        return lib.goome_text_width(self._p(), _b(text), int(bool(big)))

    def font_text(self, font, size, x, y, text, argb=0xFFFFFFFF):
        """Draw text with a Font at `size` and return its width. `y` is the top, a font of None is the built in one."""
        return lib.goome_text(self._p(), _fh(font), size, x, y, _b(text), _c(argb))

    def blit(self, src, alpha=1.0, dx=0.0, dy=0.0):
        """Draw another canvas on this one, at an offset and with an alpha (0 to 1)."""
        lib.goome_canvas_blit(self._p(), src._p(), alpha, dx, dy)

    def clip_push(self, x, y, w, h):
        """Clip drawing to this rect (snaps to whole px). Up to 16 deep, `begin()` resets it. Pair with clip_pop()."""
        lib.goome_clip_push(self._p(), x, y, w, h)

    def clip_pop(self):
        """Undo the last clip_push()."""
        lib.goome_clip_pop(self._p())

    def clip(self, x, y, w, h):
        """Clip to a rect for a `with` block, so you dont need clip_pop()."""
        self.clip_push(x, y, w, h)
        return _Pop(self.clip_pop)

    def rrect(self, x, y, w, h, radius, argb):
        """Filled rectangle with per corner radii (a number, or tl, tr, br, bl)."""
        lib.goome_draw_rrect(self._p(), x, y, w, h, _radii(radius), _c(argb))

    def rrect_line(self, x, y, w, h, radius, width, argb):
        """Outline of a rounded rectangle, `width` thick."""
        lib.goome_draw_rrect_line(self._p(), x, y, w, h, _radii(radius), width, _c(argb))

    def rrect_grad(self, x, y, w, h, radius, top, bottom, sideways=False):
        """Rounded rectangle filled with a gradient from `top` to `bottom`, or left to right with `sideways=True`."""
        lib.goome_draw_rrect_grad(self._p(), x, y, w, h, _radii(radius), _c(top), _c(bottom), int(bool(sideways)))

    def shadow(self, x, y, w, h, radius, blur, argb):
        """Soft drop shadow for a rounded rect, `blur` works like css box-shadow."""
        lib.goome_draw_shadow(self._p(), x, y, w, h, radius, blur, _c(argb))

    def circle(self, cx, cy, r, argb):
        """Filled circle around cx, cy."""
        lib.goome_draw_circle(self._p(), cx, cy, r, _c(argb))

    def ring(self, cx, cy, r, width, argb):
        """Circle outline, `r` is the middle of the stroke."""
        lib.goome_draw_ring(self._p(), cx, cy, r, width, _c(argb))

    def arc(self, cx, cy, r, width, a0, a1, argb):
        """Arc of a ring from angle `a0` to `a1` in radians, 0 is 3 oclock and it runs clockwise. Round caps."""
        lib.goome_draw_arc(self._p(), cx, cy, r, width, a0, a1, _c(argb))

    def poly(self, points, argb):
        """Filled polygon from a list of (x, y) points or a flat list of numbers."""
        flat = []
        for p in points:
            if isinstance(p, (int, float)):
                flat.append(float(p))
            else:
                flat.extend((float(p[0]), float(p[1])))
        if len(flat) % 2:
            raise ValueError("poly wants x,y pairs, got an odd number of values")
        arr = (c_double * len(flat))(*flat)
        lib.goome_draw_poly(self._p(), arr, len(flat) // 2, _c(argb))

    def bitmap(self, bmp, x, y, w, h, radius=0, tint=0xFFFFFFFF):
        """Draw a Bitmap into x, y, w, h with optional rounded corners, multiplied by a `tint` color."""
        lib.goome_draw_bitmap(self._p(), bmp._ref(), x, y, w, h, _radii(radius), _c(tint))

    def bitmap_part(self, bmp, sx, sy, sw, sh, x, y, w, h, tint=0xFFFFFFFF):
        """Draw part of a Bitmap, the box sx, sy, sw, sh in bitmap px, into x, y, w, h."""
        lib.goome_draw_bitmap_part(self._p(), bmp._ref(), int(sx), int(sy), int(sw), int(sh), x, y, w, h, _c(tint))

    def bitmap_nine(self, bmp, x, y, w, h, left, top=None, right=None, bottom=None):
        """Draw a Bitmap as a 9 slice so the corners stay sharp. `left`, `top`, `right` and `bottom` are the border sizes in bitmap px, one number is used for all."""
        top = left if top is None else top
        right = left if right is None else right
        bottom = top if bottom is None else bottom
        lib.goome_draw_bitmap_nine(self._p(), bmp._ref(), x, y, w, h, left, top, right, bottom)

    def __repr__(self):
        if self._ptr is None:
            return "Canvas(done)"
        return "Canvas(%dx%d scale %g)" % (self.w, self.h, self.scale)


class _Pop(object):
    def __init__(self, fn):
        self.fn = fn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.fn()
        return False


class Bitmap(object):
    """An image goome can draw, stored as premultiplied argb. Make one with load(), from_bytes(), from_argb() or wrap(). Works as a context manager. `w`, `h`, `stride` and `owned` are read only."""
    def __init__(self):
        self._s = _lib.BitmapS()
        self._keep = None
        self._live = False
        self._themes = weakref.WeakSet()

    @classmethod
    def _loaded(cls, rc, b, what):
        if rc != OK:
            msg = _s(lib.goome_bitmap_error()) or "unknown"
            raise error_for(rc, "cant load %s: %s" % (what, msg))
        b._live = True
        return b

    @classmethod
    def load(cls, path):
        """Load a png, jpeg, bmp, ppm or qoi file. It goes by the content, not the file name."""
        b = cls()
        return cls._loaded(lib.goome_bitmap_load(_b(path), byref(b._s)), b, path)

    @classmethod
    def from_bytes(cls, data):
        """Load an image file that is already in memory, same formats as load()."""
        b = cls()
        data = bytes(data)
        return cls._loaded(lib.goome_bitmap_load_mem(data, len(data), byref(b._s)), b, "the image bytes")

    @classmethod
    def from_argb(cls, pixels, w, h):
        """Make a bitmap from plain 0xAARRGGBB pixels. They get copied."""
        b = cls()
        arr, keep = u32_buffer(pixels, w * h)
        rc = lib.goome_bitmap_from_argb(ctypes.cast(arr, ctypes.POINTER(c_uint32)), w, h, byref(b._s))
        return cls._loaded(rc, b, "the pixels")

    @classmethod
    def wrap(cls, pixels, w, h, stride=None):
        """Use your own premultiplied argb pixels without copying them, so keep them alive. Not freed on close."""
        stride = w if stride is None else stride
        b = cls()
        arr, keep = u32_buffer(pixels, (h - 1) * stride + w if h > 0 else 0)
        b._s.px = ctypes.cast(arr, ctypes.POINTER(c_uint32))
        b._s.w, b._s.h, b._s.stride, b._s.owned = w, h, stride, 0
        b._keep = keep
        b._live = True
        return b

    def _ref(self):
        if not self._live:
            raise GoomeError(EGONE, "this bitmap is closed")
        return byref(self._s)

    w = property(lambda self: self._s.w, doc="Width in px.")
    h = property(lambda self: self._s.h, doc="Height in px.")
    stride = property(lambda self: self._s.stride, doc="Pixels per row.")
    owned = property(lambda self: bool(self._s.owned), doc="True if goome owns the pixels and frees them on close.")

    @property
    def closed(self):
        """True once close() ran."""
        return not self._live

    @property
    def pixels(self):
        """The pixels as a memoryview of premultiplied argb ints."""
        self._ref()
        return pixel_view(self._s.px, self._s.h, self._s.stride)

    def close(self):
        """Free the bitmap. Themes that use it let go of it."""
        if not self._live:
            return
        for t in list(self._themes):
            t._drop_bitmap(self)
        self._live = False
        if self._s.owned:
            lib.goome_bitmap_free(byref(self._s))
        else:
            self._s.px = None
            self._s.w = self._s.h = self._s.stride = 0
        self._keep = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __del__(self):
        if getattr(self, "_live", False) and lib is not None:
            self.close()

    def __repr__(self):
        return "Bitmap(closed)" if not self._live else "Bitmap(%dx%d)" % (self.w, self.h)


class Font(object):
    """A loaded font. Make one with load(), from_bytes() or system(). Works as a context manager."""
    def __init__(self, handle, keep=None, owned=True):
        self._f = handle
        self._keep = keep
        self._owned = owned
        self._themes = weakref.WeakSet()
        self._fallbacks = []
        self._users = weakref.WeakSet()

    @classmethod
    def load(cls, path, index=None):
        """Load a .ttf, .otf or .ttc file. `index` picks the face inside a .ttc."""
        h = lib.goome_font_load(_b(path)) if index is None else lib.goome_font_load_index(_b(path), int(index))
        if not h:
            raise GoomeError(EARG, "cant load the font %s" % path)
        return cls(h)

    @classmethod
    def from_bytes(cls, data, copy=False):
        """Load a font from memory. With `copy=False` goome uses your bytes in place, so goome keeps them alive for you."""
        data = bytes(data)
        if copy:
            h = lib.goome_font_load_mem(data, len(data), 1)
            keep = None
        else:
            keep = ctypes.create_string_buffer(data, len(data))
            h = lib.goome_font_load_mem(keep, len(data), 0)
        if not h:
            raise GoomeError(EARG, "thats not a font goome can read")
        return cls(h, keep)

    @classmethod
    def system(cls, name=None):
        """Find an installed font by name, or the desktops usual ui font with None. Returns None if there isnt one. The emoji font is added as a fallback for you."""
        h = lib.goome_font_system(_b(name))
        return cls(h) if h else None

    def _h(self):
        if self._f is None:
            raise GoomeError(EGONE, "this font is closed")
        return self._f

    @property
    def closed(self):
        """True once close() ran."""
        return self._f is None

    def fallback(self, *fonts):
        """Fonts to try, in order, for characters this font doesnt have. Returns self."""
        for f in fonts:
            if f is self or f in self._fallbacks:
                continue
            lib.goome_font_fallback(self._h(), f._h())
            self._fallbacks.append(f)
            f._users.add(self)
        return self

    @property
    def fallbacks(self):
        """The fallback fonts added so far."""
        return list(self._fallbacks)

    def measure(self, text, size):
        """Size of the text at this size as `(width, height)`."""
        return measure(text, size, self)

    def width(self, text, size):
        """Width of the text at this size."""
        return lib.goome_text_measure(self._h(), size, _b(text), None)

    def line_height(self, size):
        """Height of one line at this size."""
        return line_height(size, self)

    def close(self):
        """Free the font. Raises if it is still the fallback of another open font."""
        if self._f is None:
            return
        busy = [u for u in self._users if u._f is not None]
        if busy:
            raise GoomeError(EARG, "this font is still the fallback of %d open font(s), close those first" % len(busy))
        for t in list(self._themes):
            t._drop_font(self)
        f, self._f = self._f, None
        self._fallbacks = []
        if self._owned:
            lib.goome_font_free(f)
        self._keep = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __del__(self):
        if getattr(self, "_f", None) and lib is not None and not self._themes and not any(u._f for u in self._users):
            self.close()

    def __repr__(self):
        return "Font(closed)" if self._f is None else "Font(%#x)" % self._f
