import unittest

from tests.util import fnv

import goome


class Anim(object):
    def __init__(self):
        self.g = goome.Goome(backend=goome.TEST, mode=goome.MODE_WINDOW, width=300, height=200, test_script="end 100000")
        self.u = self.g.ui()
        self.on = False
        self.dropped = False
        self.box = self.sp = self.last = 0.0
        self.col = 0
        self.shot = None

    def frame(self):
        u = self.u
        for ev in self.g.events(0):
            u.feed(ev)
        c = u.begin(0)
        if c is None:
            return
        px, w, h, stride = c.pixels, c.w, c.h, c.stride
        r = u.canvas
        self.box = u.anim("box", 200 if self.on else 10, 160, goome.EASE_OUT)
        self.sp = u.anim("spring", 1 if self.on else 0, 320, "spring")
        self.col = u.anim_color("col", 0xFF20D060 if self.on else 0, 200, goome.EASE_LINEAR)
        if not self.dropped:
            self.last = u.anim("gone", 5 if self.on else 0, 100, goome.EASE_LINEAR)
        if r is not None:
            r.rect(self.box, 20, 60, 40, 0xFFE0A030)
            r.rrect(20 + self.sp * 180, 90, 50, 30, goome.radius(15), 0xFF4FB3F7)
            r.rect(20, 140, 260, 40, self.col)
        u.end()
        self.shot = (px, w, h, stride)

    @property
    def hash(self):
        return fnv(*self.shot)

    def close(self):
        self.u.close()
        self.g.close()


class Anims(unittest.TestCase):
    def test_ease(self):
        e = goome.ease
        self.assertEqual(e(goome.EASE_LINEAR, 0.25), 0.25)
        self.assertEqual(e("in", 0.5), 0.125)
        self.assertEqual(e(goome.EASE_OUT, 0.5), 0.875)
        self.assertEqual(e(goome.EASE_IN_OUT, 0.25), 0.0625)
        self.assertEqual(e(goome.EASE_IN_OUT, 0.75), 0.9375)
        self.assertEqual(e(goome.EASE_SMOOTH, 0.5), 0.5)
        self.assertEqual(e("bounce", 0.25), 0.47265625)
        self.assertEqual((e(goome.EASE_OUT, -3), e(goome.EASE_IN, 7)), (0, 1))
        for k in range(goome.EASE_SMOOTH, goome.EASE_BOUNCE + 1):
            if k not in (goome.EASE_CUSTOM, goome.EASE_BACK):
                self.assertEqual((e(k, 0), e(k, 1)), (0, 1), goome.EASE_NAMES[k])
        spring = [e(goome.EASE_SPRING, i / 100.0) for i in range(1, 100)]
        bounce = [e(goome.EASE_BOUNCE, i / 100.0) for i in range(1, 100)]
        self.assertTrue(1.1 < max(spring) < 1.25)
        self.assertTrue(0.9 < min(spring[30:]) < 1)
        self.assertTrue(max(bounce) <= 1 and min(bounce) >= 0)
        self.assertTrue(0.95 < e(goome.EASE_SPRING, 0.5) < 1.05)
        with self.assertRaises(ValueError):
            e("wobbly", 0.5)

    def test_frames_match_c(self):
        k = Anim()
        try:
            k.frame()
            self.assertEqual((k.box, k.sp, k.col, k.last), (10, 0, 0, 0))
            k.frame()
            self.assertFalse(k.u.animating)
            hs = []
            k.on = True
            prev, over, mid, moving = k.box, 0, -1, 0
            for f in range(60):
                k.frame()
                if f in (1, 4, 8):
                    hs.append(k.hash)
                self.assertGreaterEqual(k.box, prev)
                prev = k.box
                over = max(over, k.sp)
                if f == 6:
                    mid = k.col
                if k.u.animating:
                    moving = f + 1
            hs.append(k.hash)
            self.assertEqual((k.box, k.sp, k.col, k.last), (200, 1, 0xFF20D060, 5))
            self.assertTrue(over > 1.05 and 19 <= moving <= 22 and not k.u.animating)
            self.assertTrue(0x70 < (mid >> 24) < 0x90 and (mid >> 8) & 255 == 0xD0 and (mid >> 16) & 255 == 0x20)
            k.on = False
            k.frame()
            self.assertTrue(k.u.animating and k.box == 200)
            k.frame()
            self.assertTrue(10 < k.box < 200)
            k.on = True
            k.frame()
            self.assertTrue(k.box < 200 and k.u.animating)
            k.dropped = True
            for _ in range(1600):
                k.frame()
            k.dropped, k.on = False, False
            k.frame()
            self.assertEqual(k.last, 0)
            self.assertEqual(["%08x" % h for h in hs], ["0226f2f5", "906d3ce5", "db5848ad", "12bea72d"])
        finally:
            k.close()


if __name__ == "__main__":
    unittest.main()
