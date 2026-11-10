import unittest

from tests.util import data, fnv

import goome

SCRIPT = ("screen 400x360 1; 1 click 35,71; 2 click 29,106; 3 hold 40,157 6; 4 hover 120,157; "
          "7 click 100,213; 8 key ab; 9 key \\n; 10 key zz; 11 click 120,273; 13 click 120,206; "
          "15 click 300,20; 16 hold 100,20 20; 18 hover 150,40; end 22")


class Kit(unittest.TestCase):
    def test_scripted(self):
        g = goome.open(backend=goome.TEST, test_script=SCRIPT)
        u = goome.Ui(g)
        u.theme.font = None
        u.theme.font_size = 14
        win = goome.Window(10, 10, 220, 0)
        val, check, pick, text = 0.0, False, 0, ""
        quit, frames, clicks, downs, keys_off, kb_seen = False, 0, 0, 0, 0, False
        hs = {}
        while not quit and frames < 100:
            for ev in g.events(0):
                if ev.type == goome.QUIT:
                    quit = True
                if ev.type == goome.DOWN:
                    downs += 1
                if ev.type == goome.KEY and frames > 10:
                    keys_off += 1
                u.feed(ev)
            c = u.begin(0)
            self.assertIsNotNone(c)
            p = c._ptr
            if u.window("test", win, goome.WIN_MOVE):
                if u.button("Go"):
                    clicks += 1
                check = u.checkbox("Check", check)
                val = u.slider("Val", val, 0, 1)
                text = u.input("Text", text, 16)
                pick = u.combo("Pick", pick, ["one", "two", "three"])
            u.window_end()
            u.end()
            self.assertFalse(c.valid)
            if frames == 8:
                kb_seen = text != ""
            if frames in (0, 12, 21):
                r = p.contents
                hs[frames] = "%08x" % fnv(goome.core.pixel_view(r.px, r.h, r.stride), r.w, r.h, r.stride)
            frames += 1
        self.assertEqual(clicks, 1)
        self.assertTrue(check)
        self.assertTrue(0.45 < val < 0.55, val)
        self.assertTrue(kb_seen)
        self.assertEqual(text, "ab")
        self.assertEqual(keys_off, 0)
        self.assertEqual(pick, 1)
        self.assertEqual((win.x, win.y), (60, 30))
        self.assertEqual(downs, 7)
        self.assertEqual(hs, {0: "51713294", 12: "b52f16c5", 21: "ea01692c"})
        u.close()
        g.close()

    def test_widgets(self):
        with goome.open(backend="test", test_script="screen 800x600 1; 2 click 60,80; end 6") as g, g.ui() as u:
            u.theme.font = None
            t = u.theme
            t.light()
            self.assertGreater(t.text >> 24, 0)
            t.dark()
            t.accent = 0xFF6FDC5F
            self.assertEqual(t.accent, 0xFF6FDC5F)
            t.radius = 4
            t.update(pad=8, anim_ms=0)
            self.assertEqual((t.radius, t.pad, t.anim_ms), (4, 8, 0))
            with self.assertRaises(AttributeError):
                t.nope = 1
            self.assertIn("panel", t.as_dict())
            win = goome.Window(20, 20, 400, 0)
            stats = goome.Window(500, 20, 200, 0)
            logo = goome.Bitmap.from_argb([0xFF2A409A] * 64, 8, 8)
            tab, vol, n, color, mode, on, more, name = 0, 0.5, 3, 0xFF4FA3FF, 1, False, True, "hi"
            for i in range(8):
                for ev in g.events(0):
                    u.feed(ev)
                with u.frame(0) as c:
                    if c is None:
                        continue
                    with u.window("main", win, goome.WIN_MOVE | goome.WIN_RESIZE | goome.WIN_COLLAPSE) as shown:
                        if shown:
                            tab = u.tabs("tabs", ["A", "B"], tab)
                            with u.id(tab):
                                with u.scroll_begin("page"):
                                    u.heading("Head")
                                    u.row(2)
                                    u.button("One")
                                    u.button("Two")
                                    u.tooltip("tip")
                                    u.hovered
                                    u.label("100% sure %s %d")
                                    u.wrapped("some long text that wraps around a bit")
                                    u.separator()
                                    u.space(4)
                                    u.width(120)
                                    on = u.toggle("Toggle", on)
                                    mode = u.radio("Small", mode, 0)
                                    u.same_line()
                                    mode = u.radio("Big", mode, 1)
                                    vol = u.slider("Vol", vol, 0, 1, "%.2f")
                                    n = u.slider_int("N", n, 0, 10)
                                    u.progress(vol, "%d%%" % (vol * 100))
                                    u.progress(-1)
                                    color = u.color("Color", color)
                                    name = u.input("Name", name)
                                    more = u.collapsing("More", more)
                                    if more:
                                        for k in range(3):
                                            u.selectable("Item %d" % k, k == 1)
                                    u.collapsing("Self kept")
                                    u.image(logo, 32, 32, 6)
                                    u.image_button("img", logo, 24, 24)
                    with u.window("Stats", stats, goome.WIN_MOVE | goome.WIN_CLOSE):
                        u.label("stats")
                    u.hit(0, 0, 4, 4)
                    u.animating
            self.assertTrue(stats.open)
            stats.open = False
            with u.frame(0) as c:
                self.assertFalse(u.window("Stats", stats, goome.WIN_CLOSE))
                u.window_end()
            logo.close()

    def test_label_varargs(self):
        def draw(fn):
            with goome.open(backend="test", test_script="screen 300x200 1; end 3") as g, g.ui() as u:
                u.theme.font = None
                win = goome.Window(10, 10, 200, 0)
                c = u.begin(0)
                p = c._ptr
                with u.window("w", win, 0):
                    fn(u)
                u.end()
                r = p.contents
                return fnv(goome.core.pixel_view(r.px, r.h, r.stride), r.w, r.h, r.stride)

        plain = draw(lambda u: goome._lib.lib.goome_ui_label(u._u, b"100%% sure %%s"))
        self.assertEqual(draw(lambda u: u.label("100% sure %s")), plain)

    def test_font_lifetime(self):
        with goome.open(backend="test", test_script="end 3") as g:
            u = g.ui()
            f = goome.Font.from_bytes(data("dejavu-sub.ttf"))
            u.theme.font = f
            self.assertIs(u.theme.font, f)
            f.close()
            self.assertIsNone(u.theme.font)
            sysf = goome.Font.system()
            if sysf:
                u.theme.font = sysf
                with u.frame(0):
                    with u.window("w", goome.Window()):
                        u.label("hi")
                u.theme.font = None
                sysf.close()
            u.close()
            u.close()
            with self.assertRaises(goome.GoomeError):
                u.button("x")


if __name__ == "__main__":
    unittest.main()
