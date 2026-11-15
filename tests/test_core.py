import os
import tempfile
import unittest

from tests.util import ROOT

import goome


class Combos(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(goome.parse_combo("alt+h"), (ord("h"), goome.ALT))
        self.assertEqual(goome.parse_combo("Ctrl+Shift+F5"), (goome.K_F1 + 4, goome.CTRL | goome.SHIFT))
        self.assertEqual(goome.parse_combo("alt+?"), (ord("/"), goome.ALT | goome.SHIFT))
        self.assertEqual(goome.parse_combo("super+space"), (ord(" "), goome.SUPER))
        self.assertEqual(goome.parse_combo("cmd+left"), (goome.K_LEFT, goome.SUPER))
        self.assertEqual(goome.parse_combo("H"), (ord("h"), goome.SHIFT))

    def test_bad(self):
        for c in ("alt+", "alt+f13", ""):
            with self.assertRaises(goome.GoomeError):
                goome.parse_combo(c)

    def test_pacer(self):
        p = goome.Pacer(50)
        self.assertEqual(p.wait(), 0)
        w = p.wait()
        self.assertTrue(0 < w <= 20, w)
        t = goome.now_ms()
        self.assertGreaterEqual(t, 0)
        self.assertGreaterEqual(goome.now_ms(), t)


SCRIPT = "screen 640x360 2; 1 click 20,20; 1 click 300,300; 2 hotkey alt+j; 3 key Hi\\b; 4 send ping; 5 scroll 30,30 -1; 6 hold 25,25 8; end 10"


class Scripted(unittest.TestCase):
    def test_run(self):
        with goome.open("t", backend=goome.TEST, test_script=SCRIPT) as g:
            self.assertEqual(g.backend_name.split()[0], "test")
            mons = g.monitors()
            self.assertEqual(len(mons), 1)
            m = mons[0]
            self.assertEqual((m.area.w, m.scale, m.pw), (640, 2, 1280))
            g.hotkey("alt+j", 7)
            g.keyboard(True)
            n = dict(down=0, up=0, hot=0, keys=0, ctl=0, scroll=0, held=0)
            text, quit, frames = "", False, 0
            while not quit and frames < 100:
                c = g.begin(0)
                self.assertIsNotNone(c)
                self.assertEqual((c.scale, c.w), (2, 1280))
                c.rect(10, 10, 40, 40, 0xFF336699)
                c.hit(10, 10, 40, 40)
                g.end(c)
                self.assertFalse(c.valid)
                frames += 1
                p = g.pointer()
                if p and p.buttons:
                    n["held"] += 1
                for ev in g.events(1):
                    if ev.type == goome.DOWN:
                        n["down"] += 1
                    elif ev.type == goome.UP:
                        n["up"] += 1
                    elif ev.type == goome.HOTKEY and ev.id == 7:
                        n["hot"] += 1
                    elif ev.type == goome.KEY:
                        n["keys"] += 1
                        text += ev.text
                    elif ev.type == goome.CONTROL and ev.msg == "ping":
                        n["ctl"] += 1
                    elif ev.type == goome.SCROLL and ev.dy == -1:
                        n["scroll"] += 1
                    elif ev.type == goome.QUIT:
                        quit = True
                    repr(ev)
            self.assertEqual((n["down"], n["up"]), (2, 2))
            self.assertEqual((n["hot"], n["keys"], text, n["ctl"], n["scroll"]), (1, 3, "Hi", 1, 1))
            self.assertTrue(quit)
            self.assertGreaterEqual(n["held"], 1)

            img = g.capture(0, (10, 10, 40, 40))
            self.assertEqual((img.w, img.h, img.has_self), (80, 80, True))
            self.assertEqual(img.pixel(0, 0), 0xFF336699)
            self.assertEqual(img.pixels[0], 0xFF336699)
            self.assertEqual(len(img.pixels), 80 * img.stride)
            self.assertEqual(img.row(79)[79], img.pixel(79, 79))
            kept = img.copy()
            self.assertEqual(len(kept), 80 * 80)
            self.assertEqual(kept[0], 0xFF336699)
            self.assertEqual(g.alpha_at(20, 20), 255)
            self.assertEqual(g.alpha_at(200, 200), 0)

            again = g.capture(0)
            self.assertFalse(img.fresh)
            with self.assertRaises(goome.GoomeError):
                img.pixels
            self.assertEqual((again.w, again.h), (1280, 720))
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "grab.ppm")
                again.save_ppm(p)
                with open(p, "rb") as f:
                    self.assertTrue(f.read(2) == b"P6")
        self.assertTrue(g.closed)
        with self.assertRaises(goome.GoomeError):
            g.monitors()
        self.assertFalse(again.fresh)


class Errors(unittest.TestCase):
    def test_bad_backend(self):
        with self.assertRaises(ValueError):
            goome.open(backend="nope")

    def test_frames_missing(self):
        with self.assertRaises(goome.GoomeError) as e:
            goome.open(backend="test", test_frames=os.path.join(ROOT, "no", "such", "frames"))
        self.assertEqual(e.exception.code, goome.ENODISPLAY)
        self.assertIsInstance(e.exception, goome.NoDisplay)

    def test_close_twice(self):
        g = goome.open(backend="test", test_script="end 3")
        c = g.begin(0)
        g.close()
        g.close()
        self.assertFalse(c.valid)
        with self.assertRaises(goome.GoomeError):
            c.rect(0, 0, 1, 1, 0xFFFFFFFF)
        with self.assertRaises(goome.GoomeError):
            g.poll()

    def test_frame_and_no_state_dir(self):
        with goome.open(backend="test", test_script="end 3") as g:
            self.assertIsNone(g.control_path)
            with g.frame(0, hits=[(0, 0, 10, 10)]) as c:
                c.rect(0, 0, 10, 10, 0xFFFF0000)
            self.assertFalse(c.valid)
            self.assertEqual(g.alpha_at(5, 5), 255)

    def test_strerror(self):
        self.assertTrue(goome.strerror(goome.ENOTSUP))
        self.assertTrue(issubclass(goome.Again, goome.GoomeError))


class Control(unittest.TestCase):
    def test_send(self):
        with tempfile.TemporaryDirectory() as d:
            try:
                g = goome.open(backend="test", state_dir=d, test_script="end 50")
            except goome.GoomeError as e:
                self.skipTest("no state dir here: %s" % e)
            with g:
                if not g.control_path:
                    self.skipTest("no control fifo on this os")
                goome.send(d, "hello there")
                got = None
                for _ in range(40):
                    with g.frame(0):
                        pass
                    for ev in g.events(5):
                        if ev.type == goome.CONTROL:
                            got = ev.msg
                    if got:
                        break
                self.assertEqual(got, "hello there")


if __name__ == "__main__":
    unittest.main()
