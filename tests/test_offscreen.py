import array
import ctypes
import os
import unittest

from tests.util import HERE, fnv, run_c

import goome

DRAW_HASH = "5858302d"


def frame_hash(f):
    return "%08x" % fnv(f.pixels, f.w, f.h, f.stride)


def draw(g):
    c = g.begin(0)
    c.rect(10, 10, 20, 20, 0x80FF0000)
    c.circle(120, 50, 30, 0xFF3A7AFE)
    c.rrect(40, 60, 70, 30, 8, 0xCC20C060)
    c.text(44, 66, "offscreen", 0xFFFFFFFF)
    c.hit(10, 10, 20, 20)
    g.end(c)


def ui_run(g):
    u = g.ui()
    u.theme.update(anim_ms=0, font=None, font_size=14)
    win = goome.Window(6, 6, 180, 0)
    check, val, name = False, 0.25, "hi"
    for frame in range(6):
        if frame == 1:
            g.push_click(25, 64)
        if frame == 2:
            g.push(goome.DOWN, x=90, y=168, button=1)
            g.push(goome.UP, x=90, y=168, button=1)
        if frame == 3:
            g.push_text("z")
        for ev in g.events(0):
            u.feed(ev)
        with u.frame(0) as c:
            if c is None:
                continue
            with u.window("engine", win, goome.WIN_MOVE):
                check = u.checkbox("Check", check)
                val = u.slider("Val", val, 0, 1, "%.2f")
                name = u.input("Name", name, 32)
    u.close()
    return check, name


class Offscreen(unittest.TestCase):
    def open(self):
        return goome.open_offscreen(200, 200, 2, "engine")

    def test_basics(self):
        with self.open() as g:
            self.assertEqual(g.backend_name, "offscreen")
            self.assertEqual(g.mode, goome.MODE_OFFSCREEN)
            self.assertTrue(g.can(goome.CAP_CLIPBOARD) and g.can(goome.CAP_CURSOR) and not g.can(goome.CAP_WINDOW))
            m = g.monitors()[0]
            self.assertEqual((m.area.w, m.area.h, m.scale, m.pw, m.name), (200, 200, 2, 400, "engine"))
            with self.assertRaises(goome.Again):
                g.last_frame()
            draw(g)
            f = g.last_frame()
            self.assertEqual((f.w, f.h, f.stride, f.area.w), (400, 400, 400, 200))
            self.assertEqual(f.pixel(25, 25), 0x80800000)
            self.assertEqual(f.pixels[0], 0)
            self.assertEqual(g.alpha_at(15, 15), 0x80)
            kept = f.copy()
            g.begin(0)
            self.assertFalse(f.fresh)
            with self.assertRaises(goome.GoomeError):
                f.pixels
            self.assertEqual(kept[25 * 400 + 25], 0x80800000)

    def test_hash(self):
        with self.open() as g:
            draw(g)
            got = frame_hash(g.last_frame())
            check, name = ui_run(g)
            ui = frame_hash(g.last_frame())
            hit = g.hit(10, 10)
        self.assertEqual(got, DRAW_HASH)
        self.assertEqual((check, name, hit), (True, "hiz", True))
        out = run_c(os.path.join(HERE, "frame.c"))
        if out is None:
            if os.environ.get("GOOME_STRICT"):
                self.fail("no C compiler to check the frame hash with")
            return
        lines = dict(line.split(" ", 1) for line in out.splitlines())
        self.assertEqual(lines["draw"], got)
        self.assertEqual(lines["ui"], "%s 1 hiz 1" % ui)

    def test_hit(self):
        with self.open() as g:
            draw(g)
            self.assertTrue(g.hit(15, 15))
            self.assertTrue(g.hit(10, 10))
            self.assertFalse(g.hit(9.5, 15))
            self.assertFalse(g.hit(30, 30))
            with g.frame(0, hits=[(100, 100, 5, 5)]) as c:
                c.hit(0, 0, 4, 4)
            self.assertTrue(g.hit(102, 102) and g.hit(1, 1))
            self.assertFalse(g.hit(15, 15))

    def test_push(self):
        with self.open() as g:
            g.push(goome.DOWN, x=12, y=13, button=1)
            g.push(goome.Event.make(goome.KEY, key=ord("q"), text="q"))
            evs = list(g.events(0))
            self.assertEqual([e.type for e in evs], [goome.DOWN, goome.KEY])
            self.assertEqual((evs[0].x, evs[0].y, evs[1].text), (12, 13, "q"))
            t = goome.now_ms()
            self.assertIsNone(g.poll(200))
            self.assertLess(goome.now_ms() - t, 100)
            with self.assertRaises(TypeError):
                g.push(goome.Event.make(goome.KEY), key=1)
            g.resize(300, 150)
            self.assertEqual(g.poll(0).type, goome.MONITORS)
            self.assertEqual(g.size, (300, 150))
            c = g.begin(0)
            self.assertEqual((c.w, c.h), (600, 300))
            g.end(c)
            f = g.last_frame()
            g.resize(300, 150, 1)
            self.assertFalse(f.fresh)
            with self.assertRaises(goome.GoomeError):
                f.pixels
            self.assertEqual(g.monitors()[0].pw, 300)
            with self.assertRaises(goome.BadArg):
                g.resize(0, 10, 1)
            with self.assertRaises(goome.NotSupported):
                g.pos
            with self.assertRaises(goome.NotSupported):
                g.capture(0, (0, 0, 10, 10))

    def test_clipboard_cursor(self):
        with self.open() as g:
            self.assertEqual(g.clipboard, "")
            g.clipboard = "hello clipboard, héllo"
            self.assertEqual(g.clipboard, "hello clipboard, héllo")
            self.assertEqual(g.cursor, goome.CURSOR_ARROW)
            g.cursor = goome.CURSOR_IBEAM
            self.assertEqual(g.cursor, goome.CURSOR_IBEAM)
            g.cursor = "hand"
            self.assertEqual(g.cursor, goome.CURSOR_HAND)
            with self.assertRaises(goome.BadArg):
                g.cursor = 99
            with self.assertRaises(ValueError):
                g.cursor = "nope"
            g.title = "renamed"
            self.assertEqual(g.title, "renamed")

    def test_numpy(self):
        try:
            import numpy
        except ImportError:
            self.skipTest("no numpy, thats fine")
        with self.open() as g:
            draw(g)
            a = g.last_frame().numpy()
            self.assertEqual(a.shape, (400, 400))
            self.assertEqual(int(a[25, 25]), 0x80800000)
            self.assertEqual(a.dtype, numpy.uint32)

    def test_two(self):
        with self.open() as a, goome.open(backend="offscreen") as b:
            self.assertEqual(b.size, (960, 640))
            ca = a.begin(0)
            cb = b.begin(0)
            self.assertNotEqual(ctypes.addressof(ca.raw.px.contents), ctypes.addressof(cb.raw.px.contents))
            a.end(ca)
            b.end(cb)
            self.assertEqual(len(array.array("I", b.last_frame().tobytes())), 960 * 640)


if __name__ == "__main__":
    unittest.main()
