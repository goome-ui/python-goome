import gc
import os
import subprocess
import sys
import tempfile
import unittest

from tests.util import HERE, ROOT, compiler, fnv, fnv_bytes

import goome

SCRIPT = "screen 980x680 1; 3 click 200,300; 5 hover 400,200; 7 click 150,160; end 12"

SKIN_PX = [0xFF7B4FD0 if x < 3 or x > 8 else 0xFFF0E8FF for x in list(range(12)) * 12]


def ring(i):
    px = []
    for y in range(16):
        for x in range(16):
            d = (x - 8) ** 2 + (y - 8) ** 2
            a = 255 if d < 40 + i else 120 if (x + y + i) % 5 == 0 else 0
            v = (x * 7 + y * 13 + i * 29) & 255
            px.append(a << 24 | v << 16 | (255 - v) << 8 | (i * 11 & 255))
    return px


def shots(cmd, d):
    e = dict(os.environ, GOOME_BACKEND="test", GOOME_TEST_SCRIPT=SCRIPT, GOOME_TEST_SHOTS=d, PYTHONPATH=ROOT)
    r = subprocess.run(cmd, env=e, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr.decode())
    out = {}
    for n in sorted(os.listdir(d)):
        with open(os.path.join(d, n), "rb") as f:
            out[n] = f.read()
    return out


def dress_theme(t, keep, on):
    for i in range(goome.ICON_COUNT):
        t.icon[i] = keep["icons"][i] if on else None
    for name in goome._lib.THEME_SKINS[3:]:
        setattr(t, name, (keep["skin"], 3) if on else None)


def scene(u, mode, keep):
    win = keep["win"]
    with u.window("icons", win, goome.WIN_MOVE | goome.WIN_RESIZE | goome.WIN_COLLAPSE | goome.WIN_CLOSE) as shown:
        if shown:
            if mode == "pushed":
                with u.style(icons={goome.ICON_CHECK: keep["heart"]}, skin=(goome.SKIN_CHECKBOX, (keep["skin"], 3))):
                    u.checkbox("Check", True)
            elif mode == "nested":
                u.push_icon("check", keep["heart"])
                u.push_icon(goome.ICON_CHECK, None)
                u.pop()
                u.checkbox("Check", True)
                u.pop()
            else:
                u.checkbox("Check", True)
            scene_rest(u)


def frames(u, g, dress, mode, keep):
    if dress is not None:
        dress_theme(u.theme, keep, dress)
    for _ in range(3):
        with u.frame(0) as c:
            if c is None:
                continue
            scene(u, mode, keep)
    f = g.last_frame()
    return "%08x" % fnv(f.pixels, f.w, f.h, f.stride)


class Skinned(unittest.TestCase):
    def setUp(self):
        self.g = goome.open_offscreen(300, 260, 1, "icons")
        self.u = self.g.ui()
        self.u.theme.update(anim_ms=0, font=None, font_size=14)
        self.keep = {
            "icons": [goome.Bitmap.from_argb(ring(i), 16, 16) for i in range(goome.ICON_COUNT)],
            "heart": goome.Bitmap.from_argb(ring(40), 16, 16),
            "skin": goome.Bitmap.from_argb(SKIN_PX, 12, 12),
            "win": goome.Window(6, 6, 288, 248),
        }

    def tearDown(self):
        self.u.close()
        self.g.close()

    def run_scene(self, dress, mode=None):
        return frames(self.u, self.g, dress, mode, self.keep)

    def test_matches_c(self):
        cc = compiler()
        if not cc:
            if os.environ.get("GOOME_STRICT"):
                self.fail("no C compiler to build tests/skinned.c")
            self.skipTest("no C compiler")
        with tempfile.TemporaryDirectory() as d:
            exe = os.path.join(d, "skinned.exe" if sys.platform == "win32" else "skinned")
            subprocess.check_call([cc, "-O2", "-std=c99", "-I" + os.path.join(ROOT, "native"), "-o", exe, os.path.join(HERE, "skinned.c"),
                                   os.path.join(ROOT, "native", "goome_lib.c")] + ([] if sys.platform == "win32" else ["-lm"]))
            os.makedirs(os.path.join(d, "c"))
            os.makedirs(os.path.join(d, "py"))
            want = shots([exe], os.path.join(d, "c"))
            got = shots([sys.executable, os.path.join(ROOT, "examples", "skinned.py")], os.path.join(d, "py"))
        self.assertGreater(len(want), 5)
        self.assertEqual(sorted(got), sorted(want))
        for n in sorted(want):
            self.assertEqual("%08x" % fnv_bytes(got[n]), "%08x" % fnv_bytes(want[n]), n)

    def test_icons_change_pixels(self):
        base = self.run_scene(False)
        dressed = self.run_scene(True)
        self.u.theme.icon_tint = 1
        as_is = self.run_scene(True)
        self.u.theme.icon_tint = 0
        self.assertNotEqual(base, dressed)
        self.assertNotEqual(dressed, as_is)
        self.assertEqual(self.run_scene(False), base)

    def test_push_pop_restores(self):
        base = self.run_scene(False)
        pushed = self.run_scene(False, "pushed")
        self.assertNotEqual(base, pushed)
        self.assertEqual(self.run_scene(False, "nested"), self.nested_want())
        self.assertEqual(self.run_scene(False), base)
        for i in range(goome.ICON_COUNT):
            self.assertIsNone(self.u.theme.icon[i])
        self.assertIsNone(self.u.theme.skin_checkbox)

    def nested_want(self):
        dress_theme(self.u.theme, self.keep, False)
        self.u.theme.icon[goome.ICON_CHECK] = self.keep["heart"]
        h = self.run_scene(None)
        self.u.theme.icon[goome.ICON_CHECK] = None
        return h

    def test_theme_icons(self):
        t = self.u.theme
        bmp = goome.Bitmap.from_argb(ring(3), 16, 16)
        self.assertEqual(len(t.icon), goome.ICON_COUNT)
        self.assertEqual(goome.ICON_PICKER, 21)
        self.assertIsNone(t.icon[goome.ICON_CLOSE])
        t.icon[goome.ICON_CLOSE] = bmp
        t.icon["resize"] = bmp
        t.skin_popup = (bmp, 4)
        self.assertIs(t.icon[goome.ICON_CLOSE], bmp)
        self.assertIs(t.icon[goome.ICON_RESIZE], bmp)
        self.assertTrue(t._t().icon[goome.ICON_CLOSE])
        t.icon_tint = 1
        self.assertEqual(t.icon_tint, 1)
        c = t.copy()
        self.assertIs(c.icon[goome.ICON_CLOSE], bmp)
        self.assertEqual(c.icon_tint, 1)
        del t.icon[goome.ICON_RESIZE]
        self.assertIsNone(t.icon[goome.ICON_RESIZE])
        self.assertIs(t.icon[goome.ICON_CLOSE], bmp)
        self.assertRaises(IndexError, lambda: t.icon[goome.ICON_COUNT])
        self.assertRaises(ValueError, lambda: t.icon["nope"])
        self.assertRaises(ValueError, lambda: self.u.push_skin(goome.SKIN_COUNT, None))
        bmp.close()
        self.assertIsNone(t.icon[goome.ICON_CLOSE])
        self.assertFalse(t._t().icon[goome.ICON_CLOSE])
        self.assertIsNone(t.skin_popup)
        self.assertIsNone(c.icon[goome.ICON_CLOSE])
        t.update(icons={goome.ICON_PLUS: self.keep["heart"]}, icon_tint=0)
        self.assertIs(t.icon[goome.ICON_PLUS], self.keep["heart"])
        t.icon.clear()
        self.assertEqual(list(t.icon), [None] * goome.ICON_COUNT)

    def test_gc_keeps_bitmaps(self):
        want = self.run_scene(True)
        t = self.u.theme
        for i in range(goome.ICON_COUNT):
            t.icon[i] = goome.Bitmap.from_argb(ring(i), 16, 16)
        gc.collect()
        for i in range(goome.ICON_COUNT):
            self.assertFalse(t.icon[i].closed)
        self.assertEqual(self.run_scene(None), want)

        base = self.run_scene(False, "pushed")
        u, g = self.u, self.g
        for _ in range(3):
            with u.frame(0) as c:
                if c is None:
                    continue
                with u.window("icons", self.keep["win"], goome.WIN_MOVE | goome.WIN_RESIZE | goome.WIN_COLLAPSE | goome.WIN_CLOSE) as shown:
                    if shown:
                        u.push_icon(goome.ICON_CHECK, goome.Bitmap.from_argb(ring(40), 16, 16))
                        u.push_skin(goome.SKIN_CHECKBOX, (goome.Bitmap.from_argb(SKIN_PX, 12, 12), 3))
                        gc.collect()
                        u.checkbox("Check", True)
                        u.pop(2)
                        scene_rest(u)
        f = g.last_frame()
        self.assertEqual("%08x" % fnv(f.pixels, f.w, f.h, f.stride), base)


def scene_rest(u):
    u.checkbox("Other", False)
    u.radio("A", 1, 0)
    u.same_line()
    u.radio("B", 1, 1)
    u.toggle("On", True)
    u.slider("Val", 0.4, 0, 1, "%.2f")
    u.combo("Pick", 1, ["one", "two", "three"])
    u.tabs("t", ["One", "Two"], 0)
    u.number("N", 3, 1, "%.0f")
    if u.collapsing("More", True):
        u.label("inside")


if __name__ == "__main__":
    unittest.main()
