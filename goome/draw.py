import ctypes
import weakref
from ctypes import byref, c_double, c_uint32

from . import _lib
from ._lib import lib
from .core import EARG, EGONE, OK, GoomeError, Rect, _b, _rect, _s, error_for, pixel_view, u32_buffer

Radii = _lib.RadiiS


def radius(r):
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
    lib.goome_set_font(int(font))


def font_count():
    return lib.goome_font_count()


def _fh(font):
    if font is None:
        return None
    return font._h()


def measure(text, size, font=None):
    h = c_double()
    w = lib.goome_text_measure(_fh(font), size, _b(text), byref(h))
    return w, h.value


def line_height(size, font=None):
    return lib.goome_text_line_height(_fh(font), size)


class Canvas(object):
    def __init__(self, ptr, g=None, own=None):
        self._ptr = ptr
        self._g = g
        self._own = own
        self._hits = []

    @classmethod
    def new(cls, w, h, stride=None, scale=1.0, ox=0.0, oy=0.0):
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
        return self._ptr is not None

    @property
    def raw(self):
        return self._p().contents

    w = property(lambda self: self.raw.w)
    h = property(lambda self: self.raw.h)
    stride = property(lambda self: self.raw.stride)
    scale = property(lambda self: self.raw.scale)
    ox = property(lambda self: self.raw.ox)
    oy = property(lambda self: self.raw.oy)
    mon = property(lambda self: self.raw.mon)

    @property
    def drawn(self):
        r = self.raw
        return Rect(r.dx0, r.dy0, r.dx1 - r.dx0, r.dy1 - r.dy0)

    @property
    def pixels(self):
        r = self.raw
        return pixel_view(r.px, r.h, r.stride)

    def row(self, y):
        s = self.stride
        return self.pixels[y * s : y * s + self.w]

    def hit(self, x, y, w, h):
        self._hits.append(_rect((x, y, w, h)))

    def damage(self, rect=None):
        r = _rect(rect)
        lib.goome_damage(self._p(), byref(r) if r is not None else None)

    def clear(self):
        lib.goome_clear(self._p())

    def rect(self, x, y, w, h, argb):
        lib.goome_draw_rect(self._p(), x, y, w, h, _c(argb))

    def round_rect(self, x, y, w, h, radius, argb):
        lib.goome_draw_round_rect(self._p(), x, y, w, h, radius, _c(argb))

    def frame(self, x, y, w, h, width, argb):
        lib.goome_draw_frame(self._p(), x, y, w, h, width, _c(argb))

    def line(self, x0, y0, x1, y1, width, argb):
        lib.goome_draw_line(self._p(), x0, y0, x1, y1, width, _c(argb))

    def triangle(self, x0, y0, x1, y1, x2, y2, argb):
        lib.goome_draw_triangle(self._p(), x0, y0, x1, y1, x2, y2, _c(argb))

    def image(self, x, y, w, h, pixels, iw, ih):
        arr, keep = u32_buffer(pixels, iw * ih)
        lib.goome_draw_image(self._p(), x, y, w, h, ctypes.cast(arr, ctypes.POINTER(c_uint32)), iw, ih)

    def erase(self, x, y, w, h):
        lib.goome_erase(self._p(), x, y, w, h)

    def text(self, x, y, text, argb=0xFFFFFFFF, big=False):
        return lib.goome_draw_text(self._p(), x, y, _b(text), int(bool(big)), _c(argb))

    def text_width(self, text, big=False):
        return lib.goome_text_width(self._p(), _b(text), int(bool(big)))

    def font_text(self, font, size, x, y, text, argb=0xFFFFFFFF):
        return lib.goome_text(self._p(), _fh(font), size, x, y, _b(text), _c(argb))

    def blit(self, src, alpha=1.0, dx=0.0, dy=0.0):
        lib.goome_canvas_blit(self._p(), src._p(), alpha, dx, dy)

    def clip_push(self, x, y, w, h):
        lib.goome_clip_push(self._p(), x, y, w, h)

    def clip_pop(self):
        lib.goome_clip_pop(self._p())

    def clip(self, x, y, w, h):
        self.clip_push(x, y, w, h)
        return _Pop(self.clip_pop)

    def rrect(self, x, y, w, h, radius, argb):
        lib.goome_draw_rrect(self._p(), x, y, w, h, _radii(radius), _c(argb))

    def rrect_line(self, x, y, w, h, radius, width, argb):
        lib.goome_draw_rrect_line(self._p(), x, y, w, h, _radii(radius), width, _c(argb))

    def rrect_grad(self, x, y, w, h, radius, top, bottom, sideways=False):
        lib.goome_draw_rrect_grad(self._p(), x, y, w, h, _radii(radius), _c(top), _c(bottom), int(bool(sideways)))

    def shadow(self, x, y, w, h, radius, blur, argb):
        lib.goome_draw_shadow(self._p(), x, y, w, h, radius, blur, _c(argb))

    def circle(self, cx, cy, r, argb):
        lib.goome_draw_circle(self._p(), cx, cy, r, _c(argb))

    def ring(self, cx, cy, r, width, argb):
        lib.goome_draw_ring(self._p(), cx, cy, r, width, _c(argb))

    def arc(self, cx, cy, r, width, a0, a1, argb):
        lib.goome_draw_arc(self._p(), cx, cy, r, width, a0, a1, _c(argb))

    def poly(self, points, argb):
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
        lib.goome_draw_bitmap(self._p(), bmp._ref(), x, y, w, h, _radii(radius), _c(tint))

    def bitmap_part(self, bmp, sx, sy, sw, sh, x, y, w, h, tint=0xFFFFFFFF):
        lib.goome_draw_bitmap_part(self._p(), bmp._ref(), int(sx), int(sy), int(sw), int(sh), x, y, w, h, _c(tint))

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
    def __init__(self):
        self._s = _lib.BitmapS()
        self._keep = None
        self._live = False

    @classmethod
    def _loaded(cls, rc, b, what):
        if rc != OK:
            msg = _s(lib.goome_bitmap_error()) or "unknown"
            raise error_for(rc, "cant load %s: %s" % (what, msg))
        b._live = True
        return b

    @classmethod
    def load(cls, path):
        b = cls()
        return cls._loaded(lib.goome_bitmap_load(_b(path), byref(b._s)), b, path)

    @classmethod
    def from_bytes(cls, data):
        b = cls()
        data = bytes(data)
        return cls._loaded(lib.goome_bitmap_load_mem(data, len(data), byref(b._s)), b, "the image bytes")

    @classmethod
    def from_argb(cls, pixels, w, h):
        b = cls()
        arr, keep = u32_buffer(pixels, w * h)
        rc = lib.goome_bitmap_from_argb(ctypes.cast(arr, ctypes.POINTER(c_uint32)), w, h, byref(b._s))
        return cls._loaded(rc, b, "the pixels")

    @classmethod
    def wrap(cls, pixels, w, h, stride=None):
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

    w = property(lambda self: self._s.w)
    h = property(lambda self: self._s.h)
    stride = property(lambda self: self._s.stride)
    owned = property(lambda self: bool(self._s.owned))

    @property
    def closed(self):
        return not self._live

    @property
    def pixels(self):
        self._ref()
        return pixel_view(self._s.px, self._s.h, self._s.stride)

    def close(self):
        if not self._live:
            return
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
        try:
            self.close()
        except Exception:
            pass

    def __repr__(self):
        return "Bitmap(closed)" if not self._live else "Bitmap(%dx%d)" % (self.w, self.h)


class Font(object):
    def __init__(self, handle, keep=None, owned=True):
        self._f = handle
        self._keep = keep
        self._owned = owned
        self._themes = weakref.WeakSet()

    @classmethod
    def load(cls, path, index=None):
        h = lib.goome_font_load(_b(path)) if index is None else lib.goome_font_load_index(_b(path), int(index))
        if not h:
            raise GoomeError(EARG, "cant load the font %s" % path)
        return cls(h)

    @classmethod
    def from_bytes(cls, data, copy=False):
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
        h = lib.goome_font_system(_b(name))
        return cls(h) if h else None

    def _h(self):
        if self._f is None:
            raise GoomeError(EGONE, "this font is closed")
        return self._f

    @property
    def closed(self):
        return self._f is None

    def measure(self, text, size):
        return measure(text, size, self)

    def width(self, text, size):
        return lib.goome_text_measure(self._h(), size, _b(text), None)

    def line_height(self, size):
        return line_height(size, self)

    def close(self):
        if self._f is None:
            return
        for t in list(self._themes):
            if t._font is self:
                t.font = None
        f, self._f = self._f, None
        if self._owned:
            lib.goome_font_free(f)
        self._keep = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __del__(self):
        try:
            if not self._themes:
                self.close()
        except Exception:
            pass

    def __repr__(self):
        return "Font(closed)" if self._f is None else "Font(%#x)" % self._f
