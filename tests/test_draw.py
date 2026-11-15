import os
import tempfile
import unittest
from array import array

from tests.util import data, fnv, zero_rows

import goome

STAR = [80, 5, 98, 85, 40, 35, 120, 35, 62, 85]

SHAPES = [
    [0xA7B3B4C5, 0x0FB29A82, 0x1A98CF16, 0x1E7B729F, 0x21FD3B05, 0x241CE7FD, 0x6910B0D5, 0x7180B28E, 0x6F33AC30, 0xB48ADFA3, 0x796B9105, 0x2D93DC92, 0x1F908FAD, 0x23A6CF0C],
    [0x73429A18, 0xD9BD97AB, 0xD031F56C, 0xD2D9FA9A, 0xD639A1A7, 0xA77C3E9E, 0x7BD3FEAD, 0xAC76561E, 0x5BD0648D, 0xD0AC70E1, 0x0BB5DDA0, 0xE7C304C7, 0xCCEF8860, 0xEFC1F212],
    [0x9175788F, 0x6E99EA87, 0x935CC8E1, 0x0B73F68D, 0x23891BE5, 0xA28476C1, 0xEA64F655, 0x87DC9430, 0x909D11B5, 0x0550BB7A, 0x6455EE86, 0xD8C08E2B, 0xFD0DD1FD, 0x28C27977],
]

IMAGES = [
    ("png-gray-1-bit.png", 9, 3, 0x01975AD8),
    ("png-palette-4-bit-trns-interlaced.png", 6, 6, 0xAF77E7E2),
    ("png-rgb-16-bit.png", 5, 4, 0xDD60C23E),
    ("png-gray-alpha-stored-interlaced.png", 5, 5, 0x52D68985),
    ("png-rgba-fixed-huffman-split.png", 8, 6, 0x66DB9DCD),
    ("png-gray-key.png", 7, 4, 0x843ED605),
    ("png-rgba-16-bit-interlaced.png", 9, 9, 0xDC2F91D5),
    ("jpeg-420.jpg", 16, 16, 0x32E2C9CE),
    ("jpeg-422-restarts.jpg", 13, 9, 0x0E230BAF),
    ("jpeg-444.jpg", 10, 10, 0x34FC5275),
    ("jpeg-progressive-420-restarts.jpg", 14, 11, 0x5BCEE932),
    ("jpeg-gray.jpg", 9, 7, 0xF010B3C8),
    ("jpeg-exif-rotated.jpg", 6, 10, 0x65909E25),
    ("bmp-4-bit.bmp", 5, 3, 0x9256D097),
    ("bmp-32-bit-alpha-top-down.bmp", 3, 2, 0x6BDB3A29),
    ("bmp-24-bit.bmp", 5, 3, 0x09D94C56),
    ("ppm.ppm", 3, 2, 0xC6FDF725),
    ("pgm-16-bit.pgm", 3, 1, 0x35029201),
    ("qoi.qoi", 6, 4, 0x23AF45AD),
]


def shape(c, k, b):
    if k == 0:
        c.rrect(10.3, 8.6, 120, 70.2, (4, 20, 0, 33), 0xE02060C0)
    elif k == 1:
        c.rrect_line(10.3, 8.6, 120, 70.2, goome.radius(18), 2.5, 0xFF20A060)
    elif k == 2:
        c.rrect_grad(10, 10, 130, 70, 12, 0xFF102040, 0x8080C0FF)
    elif k == 3:
        c.rrect_grad(10, 10, 130, 70, 35, 0xFFFF4080, 0x004080FF, sideways=True)
    elif k == 4:
        c.shadow(30, 20, 90, 50, 10, 16, 0x80000000)
    elif k == 5:
        c.circle(50.5, 50.2, 30.7, 0xFFFFC020)
        c.circle(120, 30, 1.3, 0xFF000000)
    elif k == 6:
        c.ring(80, 50, 30, 5, 0xC0208080)
    elif k == 7:
        c.arc(50, 50, 30, 6, 0.3, 4.5, 0xFF3060E0)
        c.arc(120, 50, 20, 30, 2, 2.5, 0xFF905020)
    elif k == 8:
        c.poly(STAR, 0xFF2040A0)
    elif k == 9:
        c.bitmap(b, 10, 10, 100.5, 75.3, 20)
    elif k == 10:
        c.bitmap(b, 10, 10, 24, 16, 0, 0x80FF8080)
    elif k == 11:
        c.bitmap(b, 10, 10, 9, 5, 2)
    elif k == 12:
        c.bitmap_part(b, 4, 2, 8, 8, 100, 10, 40, 40)
    else:
        with c.clip(20, 15, 80, 50):
            c.rrect(0, 0, 160, 100, 30, 0xFF4080FF)
            with c.clip(50, 0, 100, 40):
                c.circle(70, 40, 30, 0xFFFF4040)
                c.text(30, 30, "clip", 0xFF000000, big=True)
                c.shadow(40, 20, 60, 30, 8, 10, 0xFF000000)
                c.bitmap(b, 40, 10, 48, 32, 6)
            c.line(0, 0, 160, 100, 3, 0xFF00A000)
            c.poly(list(zip(STAR[0::2], STAR[1::2])), 0x80000000)
        c.frame(20, 15, 80, 50, 1, 0x80000000)


def make_bitmap():
    bp = array("I", [0] * (27 * 16))
    for y in range(16):
        for x in range(24):
            a = x * 255 // 23
            v = 0xFFFFFF if (x // 4 + y // 4) & 1 else 0x2050C0
            bp[y * 27 + x] = a << 24 | ((v >> 16 & 255) * a // 255) << 16 | ((v >> 8 & 255) * a // 255) << 8 | (v & 255) * a // 255
    return goome.Bitmap.wrap(bp, 24, 16, 27)


class Drawing(unittest.TestCase):
    def test_basic(self):
        c = goome.Canvas.new(160, 100, stride=200, scale=1.5)
        c.round_rect(5, 5, 60, 40, 8, 0xC0203040)
        c.line(0, 0, 100, 60, 3, 0xFFFF0000)
        c.triangle(10, 50, 60, 50, 35, 10, 0x8000FF00)
        c.text(8, 8, "goome!", 0xFFFFFFFF, big=True)
        c.frame(70, 10, 30, 30, 2, 0xFF00FFFF)
        px = c.pixels
        self.assertTrue(all(px[y * 200 + 170] == 0 for y in range(100)))
        r = c.raw
        self.assertTrue(r.dx1 > r.dx0 and r.dy1 > r.dy0)
        self.assertEqual(fnv(px, 200, 100), 0xB93B60CF)
        c.clear()
        self.assertEqual(fnv(px, 200, 100), fnv(memoryview(bytes(200 * 100 * 4)).cast("I"), 200, 100))
        self.assertGreater(c.text_width("abc"), 0)

    def test_shapes(self):
        b = make_bitmap()
        for s, sc in enumerate((1, 1.25, 2)):
            got = []
            for k in range(14):
                w, h = int(160 * sc), int(100 * sc)
                c = goome.Canvas.new(w, h, stride=w + 3, scale=sc)
                shape(c, k, b)
                px = c.pixels
                got.append(fnv(px, w + 3, h))
                self.assertGreater(c.raw.dx1, c.raw.dx0)
                self.assertTrue(zero_rows(px, w + 3, h, w, w + 3))
                for p in px:
                    a = p >> 24
                    if (p >> 16 & 255) > a or (p >> 8 & 255) > a or (p & 255) > a:
                        self.fail("not premultiplied")
                if k == 13:
                    x0, y0 = int(20 * sc + 0.5), int(15 * sc + 0.5)
                    x1, y1 = int(100 * sc + 0.5), int(65 * sc + 0.5)
                    c = goome.Canvas.new(w, h, stride=w + 3, scale=sc)
                    c.clip_push(20, 15, 80, 50)
                    shape(c, 8, b)
                    shape(c, 4, b)
                    shape(c, 9, b)
                    c.text(0, 20, "outside", 0xFFFFFFFF, big=True)
                    r = c.raw
                    self.assertTrue(r.dx0 >= x0 and r.dy0 >= y0 and r.dx1 <= x1 and r.dy1 <= y1 and r.dx1 > r.dx0)
                    px = c.pixels
                    for y in range(h):
                        for x in range(w):
                            if (x < x0 or x >= x1 or y < y0 or y >= y1) and px[y * (w + 3) + x]:
                                self.fail("drew outside the clip")
                    c.clip_pop()
                    self.assertEqual(c.raw.nclip, 0)
            self.assertEqual(["%08x" % v for v in got], ["%08x" % v for v in SHAPES[s]], "scale %g" % sc)
        b.close()

    def test_image_and_blit(self):
        src = goome.Canvas.new(20, 20)
        src.image(0, 0, 20, 20, array("I", [0xFF00FF00] * 16), 4, 4)
        self.assertEqual(src.pixels[0], 0xFF00FF00)
        dst = goome.Canvas.new(40, 40)
        dst.blit(src, 1.0, 10, 10)
        self.assertEqual(dst.pixels[10 * 40 + 10], 0xFF00FF00)
        self.assertEqual(dst.pixels[0], 0)
        dst.erase(0, 0, 40, 40)
        self.assertEqual(dst.pixels[10 * 40 + 10], 0)
        dst.image(0, 0, 2, 1, bytes([0, 0, 255, 255, 255, 0, 0, 255]), 2, 1)
        self.assertEqual(dst.row(0)[0], 0xFFFF0000)
        self.assertEqual(dst.row(0)[1], 0xFF0000FF)


class Fonts(unittest.TestCase):
    def test_fonts(self):
        ttf, otf = data("dejavu-sub.ttf"), data("dejavu-sub.otf")
        with self.assertRaises(goome.GoomeError):
            goome.Font.from_bytes(b"nope, not a font", copy=True)
        with self.assertRaises(goome.GoomeError):
            goome.Font.from_bytes(ttf[:40])
        f, o = goome.Font.from_bytes(ttf), goome.Font.from_bytes(otf, copy=True)
        w, h = f.measure("goome!", 20)
        self.assertTrue(76.97 < w < 76.98 and 23.2 < h < 23.3)
        for font in (f, o):
            self.assertLess(font.width("AV", 20), font.width("A", 20) + font.width("V", 20) - 1)
        w, h = f.measure("a\nbb\n", 20)
        self.assertTrue(3 * 23.2 < h < 3 * 23.3)
        self.assertGreater(f.width(b"\xff\xc3(\xed\xa0\x80\xf4\x90\x80\x80", 20), 0)
        self.assertGreater(f.line_height(20), 0)
        want = [0x412C299F, 0xBCD42095]
        bufs = []
        for k, font in enumerate((f, o)):
            c = goome.Canvas.new(200, 120, stride=240, scale=1.5)
            c.raw.kx1, c.raw.ky1 = 200, 120
            c.font_text(font, 13, 4, 2, "goome! Hié\nAVAWAY Ty.@ ☃")
            c.font_text(font, 30, 2.3, 24, "Hig", 0xC0FF8040)
            r = c.raw
            r.kx0, r.ky0, r.kx1, r.ky1, r.nclip = 30, 60, 90, 100, 1
            c.font_text(font, 40, 10, 50, "WoW", 0xFF2080FF)
            px = c.pixels
            self.assertTrue(zero_rows(px, 240, 120, 200, 240))
            self.assertFalse(any(px[100 * 240 :].tolist()))
            self.assertTrue(r.dx0 >= 0 and r.dx1 <= 200 and r.dy1 <= 100 and r.dx1 > r.dx0)
            self.assertEqual("%08x" % fnv(px, 240, 120), "%08x" % want[k])
            c = goome.Canvas.new(240, 120)
            c.raw.kx1, c.raw.ky1 = 240, 120
            c.font_text(font, 31, 3, 3, "goome Hi\nmoge")
            bufs.append(c.pixels)
        ink = sum(p >> 24 for p in bufs[0])
        diff = sum(abs((a >> 24) - (b >> 24)) for a, b in zip(bufs[0], bufs[1]))
        self.assertTrue(ink > 0 and diff * 50 < ink)
        c = goome.Canvas.new(200, 120, stride=240)
        c.raw.kx1, c.raw.ky1 = 200, 120
        for cut in range(0, len(otf), 7):
            bad = bytearray(otf)
            bad[cut] ^= 0x5A
            try:
                b = goome.Font.from_bytes(bytes(bad) if cut & 1 else bytes(bad[: cut + 12]))
            except goome.GoomeError:
                b = None
            c.font_text(b, 20, 0, 0, "goome! AV")
            if b:
                b.close()
        c = goome.Canvas.new(200, 120, stride=240)
        self.assertEqual(c.font_text(None, 12, 0, 0, "ab\nabc"), goome.measure("abc", 12)[0])
        f.close()
        f.close()
        o.close()
        with self.assertRaises(goome.GoomeError):
            f.measure("x", 10)

    def test_builtin(self):
        self.assertGreaterEqual(goome.font_count(), 1)
        goome.set_font(0)
        self.assertGreater(goome.line_height(12), 0)

    def test_load_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "f.ttf")
            with open(p, "wb") as fh:
                fh.write(data("dejavu-sub.ttf"))
            with goome.Font.load(p) as f:
                self.assertGreater(f.width("goome", 12), 0)
            with goome.Font.load(p, 0) as f:
                self.assertGreater(f.width("goome", 12), 0)
        with self.assertRaises(goome.GoomeError):
            goome.Font.load(os.path.join(d, "gone.ttf"))


class Bitmaps(unittest.TestCase):
    def test_cases(self):
        for name, w, h, hv in IMAGES:
            raw = data(name)
            b = goome.Bitmap.from_bytes(raw)
            self.assertEqual((b.w, b.h, b.owned), (w, h, True), name)
            self.assertEqual("%08x" % fnv(b.pixels, b.w, b.h, b.stride), "%08x" % hv, name)
            b.close()
            self.assertTrue(b.closed)
            b.close()
            try:
                half = goome.Bitmap.from_bytes(raw[: len(raw) // 2])
            except goome.GoomeError:
                half = None
            if half:
                self.assertGreater(half.w, 0)
                half.close()

    def test_errors(self):
        with self.assertRaises(goome.NotSupported) as e:
            goome.Bitmap.from_bytes(data("jpeg-arithmetic.jpg"))
        self.assertIn("arithmetic", str(e.exception))
        with self.assertRaises(goome.NotSupported):
            goome.Bitmap.from_bytes(b"GIF89a......")
        with self.assertRaises(goome.GoomeError):
            goome.Bitmap.from_bytes(b"\x89PNG\r\n\x1a\n")
        with self.assertRaises(goome.GoomeError):
            goome.Bitmap.load("no/such/file.png")

    def test_from_argb(self):
        with goome.Bitmap.from_argb([0xFFFF0000, 0x80FFFFFF, 0x00123456, 0x40804020], 2, 2) as b:
            self.assertEqual(list(b.pixels), [0xFFFF0000, 0x80808080, 0, 0x40201008])
        with self.assertRaises(goome.GoomeError):
            b.pixels
        with self.assertRaises(ValueError):
            goome.Bitmap.from_argb(array("I", [1, 2]), 2, 2)

    def test_load_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.qoi")
            with open(p, "wb") as fh:
                fh.write(data("qoi.qoi"))
            with goome.Bitmap.load(p) as b:
                self.assertEqual((b.w, b.h), (6, 4))


if __name__ == "__main__":
    unittest.main()
