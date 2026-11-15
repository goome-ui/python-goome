import array
import os
import unittest

from tests.util import HERE, fnv, run_c

import goome

D, U, M = goome.DOWN, goome.UP, goome.MOTION

SCRIPT = {
    2: ((M, 250, 25), (D, 250, 25)), 3: ((M, 280, 47),), 4: ((M, 291, 60),), 5: ((U, 291, 60),),
    7: ((M, 250, 275), (D, 250, 275)), 8: ((M, 262, 284),), 9: ((U, 262, 284),),
}


def show(name, it):
    flags = "".join(str(int(getattr(it, n))) for n in ("hovered", "pressed", "held", "released", "clicked"))
    return "%s %.1f %.1f %.1f %.1f %s %.1f %.1f %.1f %.1f" % (name, it.x, it.y, it.w, it.h, flags, it.dx, it.dy, it.drag_x, it.drag_y)


def frame_hash(g):
    f = g.last_frame()
    return "%08x" % fnv(f.pixels, f.w, f.h, f.stride)


def styled():
    g = goome.open_offscreen(400, 300, 1, "style")
    u = g.ui()
    u.theme.update(anim_ms=0, font=None, font_size=14)
    bmp = goome.Bitmap.from_argb([0xFF3050A0 if i % 9 else 0xFFF0C040 for i in range(64)], 8, 8)
    out, chk, amt = [], True, 0.4
    for f in range(12):
        for e in SCRIPT.get(f, ()):
            g.push(e[0], x=e[1], y=e[2], button=1 if e[0] != M else 0)
        for ev in g.events(0):
            u.feed(ev)
        with u.frame(0) as c:
            if c is None:
                continue
            u.button("Plain")
            u.same_line()
            with u.style(radius=0):
                u.button("Square")
            u.same_line()
            with u.style(radii=(16, 3, 16, 3)):
                u.button("Leaf")
            with u.style(accent=0xFFFF6FA8, accent_text=0xFF2A0614, pad=9):
                chk = u.checkbox("Pink", chk)
                amt = u.slider("Amount", amt, 0, 1, "%.2f")
            u.push_skin(goome.SKIN_BUTTON, (bmp, 3))
            u.push_font(None)
            u.button("Skinned")
            u.pop(2)
            t = u.theme.copy()
            t.light()
            t.update(radius=2, font=None, font_size=14, anim_ms=0)
            with u.style(t):
                u.button("Light")
            u.size(120, 0)
            u.button("Wide")

            v = u.store("pos", 3)
            u.pos(220, 10)
            a = u.custom("lock", 60, 30, goome.ITEM_DRAG_X)
            if a.held:
                v[0] += a.dx
            if a.released:
                v[2] += 1
            u.pos(220 + v[1], 250)
            b = u.custom("free", 40, 40, goome.ITEM_DRAG_X | goome.ITEM_DRAG_Y)
            if b.held:
                v[1] += b.dx
            after = u.custom("after", 50, 20)
            k = u.canvas
            if k is not None:
                k.rrect(a.x + v[0], a.y, a.w, a.h, 6, 0xFFFF7A59 if a.held else 0xFF4FB3F7)
                k.circle(b.x + b.w / 2, b.y + b.h / 2, 18, 0xFFE8D85A if b.held else 0xFF6FDC5F)
            u.push_num(goome.S_GAP, 3)
        if 2 <= f <= 9:
            out += [show("lock%d" % f, a), show("free%d" % f, b)]
        if f == 11:
            out.append(show("after", after))
    v = u.store("pos", 3)
    out.append("store %.1f %.1f %.1f" % tuple(v))
    out.append("end " + frame_hash(g))
    err = g.error
    bmp.close()
    u.close()
    g.close()
    return out, err


def one_frame(build, w=300, h=160):
    g = goome.open_offscreen(w, h, 1, "one")
    u = g.ui()
    u.theme.update(anim_ms=0, font=None, font_size=14)
    got = []
    for _ in range(2):
        with u.frame(0):
            got = build(u)
    h = frame_hash(g)
    u.close()
    g.close()
    return h, got


class Custom(unittest.TestCase):
    def test_matches_c(self):
        lines, err = styled()
        self.assertIn("style stack", err or "")
        self.assertIn("lock3 230.0 20.0 60.0 30.0 10100 30.0 0.0 30.0 0.0", lines)
        self.assertIn("free8 230.0 260.0 40.0 40.0 10100 12.0 9.0 12.0 9.0", lines)
        self.assertEqual(lines[-2], "store 41.0 12.0 1.0")
        out = run_c(os.path.join(HERE, "style.c"))
        if out is None:
            if os.environ.get("GOOME_STRICT"):
                self.fail("no C compiler to run tests/style.c")
            self.skipTest("no C compiler")
        self.assertEqual(lines, out.splitlines())

    def test_push_pop_restores(self):
        def plain(u):
            u.button("One")
            u.button("Two")

        def pushed(u):
            u.button("One")
            with u.style(radius=0, accent=0xFFFF0000, border_width=3, radii=(9, 0, 9, 0), font=None):
                pass
            u.push_color("text", 0xFF00FF00)
            u.pop()
            u.button("Two")

        def square(u):
            u.button("One")
            with u.style(radius=0, border=0xFFFF0000):
                u.button("Two")

        base = one_frame(plain)[0]
        self.assertEqual(one_frame(pushed)[0], base)
        self.assertNotEqual(one_frame(square)[0], base)

    def test_style_errors(self):
        def bad(u):
            errs = []
            for fn in (lambda: u.style(nope=1), lambda: u.push_color(goome.S_RADIUS, 1), lambda: u.push_num("accent", 1),
                       lambda: u.push_skin(99, None), lambda: u.style(radius=0, skin=(goome.SKIN_BUTTON, ("x",)))):
                try:
                    fn()
                except (TypeError, ValueError) as e:
                    errs.append(type(e).__name__)
            u.button("One")
            return errs

        h, errs = one_frame(bad)
        self.assertEqual(errs, ["TypeError", "ValueError", "ValueError", "ValueError", "ValueError"])
        self.assertEqual(h, one_frame(lambda u: u.button("One"))[0])

    def test_pos(self):
        def build(u):
            first = u.custom("a", 30, 20)
            u.pos(123, 40)
            pinned = u.custom("p", 20, 20, goome.ITEM_NO_HIT)
            u.pos(0, 0)
            corner = u.custom("c", 5, 5, goome.ITEM_NO_HIT)
            u.size(77, 33)
            sized = u.custom("s", 0, 0)
            return first, pinned, corner, sized

        _, (first, pinned, corner, sized) = one_frame(build)
        self.assertEqual((pinned.x - corner.x, pinned.y - corner.y), (123, 40))
        self.assertEqual((corner.x, corner.y), (first.x, first.y))
        self.assertEqual((sized.w, sized.h), (77, 33))
        self.assertGreater(sized.y, first.y + first.h - 1)
        self.assertLess(sized.y, pinned.y)

    def test_drag_lock_and_store(self):
        g = goome.open_offscreen(300, 200, 1, "drag")
        u = g.ui()
        u.theme.update(anim_ms=0, font=None)
        moves = {1: [(M, 40, 30), (D, 40, 30)], 2: [(M, 55, 70)], 3: [(M, 70, 90)], 4: [(U, 70, 90)]}
        seen = []
        with g, u:
            for f in range(7):
                for t, x, y in moves.get(f, []):
                    g.push(t, x=x, y=y, button=0 if t == M else 1)
                for ev in g.events(0):
                    u.feed(ev)
                with u.frame(0):
                    v = u.store("ys", 2)
                    it = u.custom("bar", 60, 40, goome.ITEM_DRAG_Y | goome.ITEM_FOCUSABLE)
                    v[0] += it.dy
                    v[1] += 1
                    seen.append(it)
            self.assertTrue(seen[1].pressed and seen[1].held and seen[1].focused and seen[1].changed)
            self.assertEqual((seen[2].dx, seen[2].dy, seen[2].drag_x), (0, 40, 0))
            self.assertEqual((seen[3].drag_x, seen[3].drag_y), (0, 60))
            self.assertTrue(seen[4].released and not seen[4].held)
            self.assertFalse(seen[6].changed)
            self.assertIn("Item(", repr(seen[1]))
            v = u.store("ys", 2)
            self.assertEqual(list(v), [60, 7])
            self.assertEqual(u.store("ys", 4).tolist(), [60, 7, 0, 0])
            self.assertEqual(u.store("other", 1).tolist(), [0])
            with self.assertRaises(ValueError):
                u.store("ys", 0)

    def test_canvas_lifetime(self):
        g = goome.open_offscreen(100, 60, 1, "cv")
        u = g.ui()
        with g, u:
            with u.frame(0):
                u.custom("x", 20, 20)
                c = u.canvas
                c.rect(0, 0, 10, 10, 0xFFFF0000)
            self.assertFalse(c.valid)
            with self.assertRaises(goome.GoomeError):
                c.rect(0, 0, 1, 1, 0xFF000000)
            self.assertIsNone(u.canvas)


class FrameCopy(unittest.TestCase):
    def setUp(self):
        self.g = goome.open_offscreen(64, 40, 1, "copy")
        c = self.g.begin(0)
        c.rect(0, 0, 64, 40, 0xC0102030)
        c.rect(10, 5, 20, 10, 0x80402010)
        c.rect(40, 20, 8, 8, 0x00000000)
        c.erase(40, 20, 8, 8)
        self.g.end(c)

    def tearDown(self):
        self.g.close()

    def test_dirty(self):
        r = self.g.frame_dirty()
        self.assertEqual(r, goome.Rect(0, 0, 64, 40))
        self.assertIsNone(self.g.frame_dirty())
        for _ in range(2):
            c = self.g.begin(0)
            c.rect(5, 6, 7, 8, 0xFFFFFFFF)
            self.g.end(c)
            r = self.g.frame_dirty()
        self.assertIsNotNone(r)
        self.assertTrue(r.x <= 5 and r.y <= 6 and r.x + r.w >= 12 and r.y + r.h >= 14)
        self.assertTrue(r.w < 64 or r.h < 40)

    def test_partial_copies_add_up(self):
        g = goome.open_offscreen(320, 200, 1, "partial")
        u = g.ui()
        u.theme.update(anim_ms=0, font=None)
        win = goome.Window(20, 20, 200, 0)
        stride = 320 * 4
        buf = bytearray(stride * 200)
        sizes = []
        with g, u:
            for i in range(6):
                with u.frame(0):
                    with u.window("w", win):
                        u.label("frame %d" % i)
                        u.button("Same")
                r = g.frame_dirty()
                sizes.append(r.w * r.h)
                g.frame_copy(memoryview(buf)[r.y * stride + r.x * 4 :], stride, goome.FMT_BGRA_PREMUL, r)
                self.assertEqual(bytes(buf), g.last_frame().tobytes())
        self.assertEqual(sizes[0], 320 * 200)
        self.assertLess(max(sizes[2:]), 320 * 200 * 3 // 4)

    def test_formats(self):
        f = self.g.last_frame()
        px = f.pixel(15, 8)
        a = px >> 24
        self.assertTrue(0 < a < 255)
        whole = self.g.frame_copy()
        self.assertEqual(bytes(whole), f.tobytes())
        rect = (12, 6, 30, 20)
        stride = 30 * 4 + 12
        for fmt in (goome.FMT_BGRA_PREMUL, goome.FMT_RGBA_PREMUL, goome.FMT_BGRA, goome.FMT_RGBA):
            buf = bytearray(b"\xee" * (stride * 20))
            self.assertIs(self.g.frame_copy(buf, stride, fmt, rect), buf)
            for x, y in ((15, 8), (0 + 12, 6), (41, 25), (40, 20)):
                p = f.pixel(x, y)
                al, r, gr, b = p >> 24, (p >> 16) & 255, (p >> 8) & 255, p & 255
                if fmt in (goome.FMT_BGRA, goome.FMT_RGBA):
                    if al == 0:
                        r = gr = b = 0
                    elif al < 255:
                        r, gr, b = [min(255, (v * 255 + al // 2) // al) for v in (r, gr, b)]
                want = bytes((r, gr, b, al) if fmt in (goome.FMT_RGBA_PREMUL, goome.FMT_RGBA) else (b, gr, r, al))
                o = (y - 6) * stride + (x - 12) * 4
                self.assertEqual(bytes(buf[o : o + 4]), want, (fmt, x, y))
            self.assertEqual(bytes(buf[30 * 4 : stride]), b"\xee" * 12)
        arr = array.array("I", [0] * (8 * 4))
        self.g.frame_copy(arr, 32, goome.FMT_BGRA_PREMUL, (10, 5, 8, 4))
        self.assertEqual(arr[0], f.pixel(10, 5))

    def test_bad_args(self):
        with self.assertRaises(ValueError):
            self.g.frame_copy(bytearray(10), None, goome.FMT_RGBA, (0, 0, 4, 4))
        with self.assertRaises(ValueError):
            self.g.frame_copy(bytes(64), None, goome.FMT_RGBA, (0, 0, 4, 4))
        with self.assertRaises(ValueError):
            self.g.frame_copy(bytearray(64), 8, goome.FMT_RGBA, (0, 0, 4, 4))
        with self.assertRaises(goome.BadArg):
            self.g.frame_copy(bytearray(64 * 4 * 40), None, goome.FMT_RGBA, (60, 0, 8, 2))
        with self.assertRaises(goome.BadArg):
            self.g.frame_copy(bytearray(64), None, 9, (0, 0, 4, 4))


if __name__ == "__main__":
    unittest.main()
