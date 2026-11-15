import gc
import os
import unittest

from tests.util import HERE, fnv, run_c

import goome

TABS = ["Play", "Stats", "Gear"]
MODES = ["Story", "Arena", "Sandbox"]


def frame_hash(g):
    f = g.last_frame()
    return "%08x" % fnv(f.pixels, f.w, f.h, f.stride)


def widgets(u):
    u.tabs("tabs", TABS, 1)
    u.heading("Player one")
    u.input("Name", "sev", 32)
    u.password("Password", "hunter22", "8 or more", cap=32)
    u.row(2)
    u.checkbox("Sound", True)
    u.toggle("Online", False)
    u.radio("Easy", 2, 0)
    u.same_line()
    u.radio("Hard", 2, 2)
    u.slider("Volume", 40, 0, 100, "%.0f")
    u.combo("Mode", 1, MODES)
    u.progress(0.6, "loading")
    u.row(2)
    u.button("Start")
    u.badge("new", 0)


class Kit(object):
    def __init__(self):
        self.g = goome.open_offscreen(360, 420, 1, "looks")
        self.u = self.g.ui()
        self.u.theme.update(anim_ms=0, font=None, font_size=14)
        self.u.config.blink_ms = 0

    def close(self):
        self.u.close()
        self.g.close()

    def feed(self):
        for ev in self.g.events(0):
            self.u.feed(ev)

    def look(self, t, zoom=1):
        u = self.u
        for _ in range(3):
            self.feed()
            with u.frame(0) as c:
                if c is None:
                    continue
                with u.style(t):
                    if zoom != 1:
                        u.scale(zoom)
                    with u.window("look", goome.Window(6, 6, 340, 0), 0) as shown:
                        if shown:
                            widgets(u)
        return frame_hash(self.g)

    def typed(self, flags, start, keys):
        u, g = self.u, self.g
        text, got, focus = start, 0, True
        evs = []
        i = 0
        while i < len(keys):
            if keys[i] == "^":
                evs.append((ord(keys[i + 1]), goome.CTRL, ""))
                i += 2
                continue
            if keys[i] == "\n":
                evs.append((goome.K_ENTER, 0, ""))
            else:
                evs.append((ord(keys[i]), 0, keys[i]))
            i += 1
        for f in range(len(evs) + 3):
            if 1 <= f <= len(evs):
                k, m, t = evs[f - 1]
                g.push(goome.KEY, key=k, mods=m, text=t)
            self.feed()
            with u.frame(0) as c:
                if c is None:
                    continue
                with u.window("typing", goome.Window(6, 6, 300, 0), 0) as shown:
                    if shown:
                        u.button("Hi")
                        if focus:
                            u.set_focus()
                            focus = False
                        text = u.input_ex("in", text, flags | goome.INPUT_NO_SELECT_ON_FOCUS, "hint here", 32)
                        if u.changed:
                            got = 2 if u.entered else 1
        return "%s %s %d" % (frame_hash(g), text, got)


def lines():
    k = Kit()
    out = []
    try:
        u = k.u
        for i, name in enumerate(goome.PRESET_NAMES):
            t = u.theme.copy().preset(name if i % 2 else i)
            t.anim_ms = 0
            out.append("preset%d %s" % (i, k.look(t)))
        t = goome.Theme.make(0xFF8B5CF6, True, 12)
        t.anim_ms = 0
        out.append("make_dark " + k.look(t))
        out.append("make_dark_big " + k.look(t, 1.25))
        t = goome.Theme.make(0xFFF2D04A, dark=False, radius=20)
        t.anim_ms = 0
        out.append("make_light " + k.look(t))
        out.append("make_light_small " + k.look(t, 0.8))

        out.append("plain " + k.typed(0, "abc", ""))
        out.append("pass_abc " + k.typed(goome.INPUT_PASSWORD, "abc", ""))
        out.append("pass_xyz " + k.typed(goome.INPUT_PASSWORD, "xyz", ""))
        u.config.mask = "#"
        out.append("pass_mask " + k.typed(goome.INPUT_PASSWORD, "abc", "d"))
        u.config.mask = None
        out.append("pass_enter " + k.typed(goome.INPUT_PASSWORD | goome.INPUT_ENTER_RETURNS, "abc", "\n"))
        out.append("number " + k.typed(goome.INPUT_NUMBER, "12", "3a4"))
        out.append("readonly " + k.typed(goome.INPUT_READONLY, "eu-west", "xy"))

        out.append("before_bind " + k.typed(0, "hello", "^qx"))
        u.config.bind("select_all", "alt+l, ctrl+q")
        out.append("after_bind " + k.typed(0, "hello", "^qx"))
        u.config.bind(goome.ACT_SELECT_ALL, None)
        out.append("unbound " + k.typed(0, "hello", "^ax"))
    finally:
        k.close()
    return out


class Looks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = lines()

    def test_matches_c(self):
        got = self.lines
        want = run_c(os.path.join(HERE, "looks.c"))
        if want is None:
            if os.environ.get("GOOME_STRICT"):
                self.fail("no C compiler to run tests/looks.c")
            self.skipTest("no C compiler")
        self.assertEqual(got, want.splitlines())

    def test_typing(self):
        got = dict(l.split(" ", 1) for l in self.lines)
        h = dict((k, v.split()[0]) for k, v in got.items())
        self.assertEqual(len(set(h[k] for k in got if k.startswith("preset"))), goome.PRESET_COUNT)
        self.assertEqual(h["pass_abc"], h["pass_xyz"])
        self.assertNotEqual(h["pass_abc"], h["plain"])
        self.assertEqual(got["pass_mask"].split()[1:], ["abcd", "1"])
        self.assertEqual(got["pass_enter"].split()[1:], ["abc", "2"])
        self.assertEqual(got["number"].split()[1], "1234")
        self.assertEqual(got["readonly"].split()[1:], ["eu-west", "0"])
        self.assertEqual(got["before_bind"].split()[1], "hellox")
        self.assertEqual(got["after_bind"].split()[1], "x")
        self.assertEqual(got["unbound"].split()[1], "hellox")
        self.assertNotEqual(h["make_dark"], h["make_dark_big"])


class Config(unittest.TestCase):
    def setUp(self):
        self.k = Kit()
        self.u = self.k.u

    def tearDown(self):
        self.k.close()

    def test_defaults_and_fields(self):
        c = self.u.config
        self.assertEqual((c.tip_delay_ms, c.dbl_click_ms, c.scroll_lines), (500, 450, 3.0))
        self.assertTrue(c.tab_nav and c.esc_closes and c.raise_on_click)
        self.assertFalse(c.focus_on_mouse)
        self.assertEqual(c.cursor["input"], goome.CURSOR_IBEAM)
        self.assertEqual(len(list(c.cursor)), goome.CUR_COUNT)
        c.cursor["button"] = "hand"
        self.assertEqual(c.cursor[goome.CUR_BUTTON], goome.CURSOR_HAND)
        c.cursor[goome.CUR_LINK] = goome.CURSOR_ARROW
        self.assertEqual(c.cursor["link"], goome.CURSOR_ARROW)
        c.tip_delay_ms = 200
        c.focus_on_mouse = True
        c.scroll_lines = 1.5
        self.assertEqual((c.tip_delay_ms, c.focus_on_mouse, c.scroll_lines), (200, True, 1.5))
        self.assertEqual(c.keys("copy"), [(ord("c"), goome.CTRL), (ord("c"), goome.SUPER)])
        self.assertEqual(len(c.keys("redo")), 4)
        c.bind("copy", ["ctrl+k", "alt+c"])
        self.assertEqual(c.keys(goome.ACT_COPY), [(ord("k"), goome.CTRL), (ord("c"), goome.ALT)])
        c.bind("paste", "")
        self.assertEqual(c.keys("paste"), [])
        self.assertRaises(goome.BadArg, c.bind, "undo", "ctrl+nope")
        self.assertRaises(ValueError, c.bind, "nope", "ctrl+k")
        self.assertRaises(IndexError, c.bind, goome.ACT_COUNT, "ctrl+k")
        self.assertRaises(ValueError, c.cursor.__setitem__, "button", "nope")
        self.assertRaises(AttributeError, setattr, c, "tip_delay", 3)
        c.mask = "*"
        self.assertEqual(c.mask, "*")
        c.reset()
        self.assertEqual((c.tip_delay_ms, c.mask, c.cursor["button"]), (500, None, goome.CURSOR_ARROW))
        self.assertEqual(c.keys("paste"), [(ord("v"), goome.CTRL), (ord("v"), goome.SUPER)])

    def test_custom_ease(self):
        u, g = self.u, self.k.g
        seen = []

        def bounce(t):
            seen.append(t)
            return t * t

        u.theme.update(anim_ms=200, ease="custom")
        u.config.ease = bounce
        del bounce
        gc.collect()
        self.assertEqual(u.theme.ease, goome.EASE_CUSTOM)
        for f in range(8):
            if f == 1:
                g.push(goome.MOTION, x=40, y=40)
            self.k.feed()
            with u.frame(0) as c:
                if c is None:
                    continue
                with u.window("ease", goome.Window(6, 6, 200, 0), 0):
                    u.button("Hover me")
        self.assertTrue(seen)
        self.assertTrue(all(0 <= t <= 1 for t in seen))
        u.config.ease = None
        self.assertIsNone(u.config.ease)
        self.assertRaises(TypeError, setattr, u.config, "ease", 3)


class Themes(unittest.TestCase):
    def setUp(self):
        self.k = Kit()
        self.u = self.k.u

    def tearDown(self):
        self.k.close()

    def test_new_fields(self):
        t = self.u.theme
        for n in goome._lib.MORE_COLORS + goome._lib.MORE_SIZES:
            self.assertTrue(hasattr(t, n), n)
        self.assertEqual(len(goome.STYLE_NAMES), goome.S_COUNT)
        self.assertEqual(goome.STYLE_NAMES[goome.S_TOAST_FADE_MS], "toast_fade_ms")
        t.check_size = 24
        t.knob = 0x1FF00FF00
        t.align = "center"
        t.ease = "back"
        self.assertEqual((t.check_size, t.knob, t.align, t.ease), (24, 0xFF00FF00, goome.ALIGN_CENTER, goome.EASE_BACK))
        self.assertRaises(ValueError, setattr, t, "ease", "wobbly")
        d = t.as_dict()
        self.assertEqual(d["check_size"], 24)
        self.assertIn("toast_fade_ms", d)

    def test_fonts(self):
        t = self.u.theme
        f = goome.Font.system("monospace")
        if f is None:
            self.skipTest("no system font")
        t.font_mono = f
        t.font_heading = f
        self.assertIs(t.font_mono, f)
        c = t.copy()
        self.assertIs(c.font_heading, f)
        f.close()
        self.assertIsNone(t.font_mono)
        self.assertIsNone(t.font_heading)
        self.assertIsNone(c.font_mono)

    def test_make_and_preset(self):
        t = goome.Theme.make(0xFF8B5CF6)
        self.assertEqual(t.accent, 0xFF8B5CF6)
        self.assertEqual(t.radius, 10)
        self.assertIsNone(t.font)
        u = self.u
        before = u.theme.font_size
        r = u.theme.make(0x8B5CF6, dark=False, radius=4)
        self.assertIs(r, u.theme)
        self.assertEqual((u.theme.accent, u.theme.radius, u.theme.font_size), (0xFF8B5CF6, 4, 15))
        self.assertNotEqual(before, 15)
        a = goome.Theme.preset("high contrast")
        b = u.theme.copy().preset(goome.PRESET_HIGH_CONTRAST)
        self.assertEqual(a.as_dict(), b.as_dict())
        self.assertEqual(a.border_width, 2)
        self.assertRaises(ValueError, goome.Theme.preset, "nope")
        self.assertRaises(ValueError, goome.Theme.preset, 99)

    def test_scale(self):
        u = self.u
        u.theme.update(check_size=18, check_radius=5, font_size=14, item_h=0)
        u.scale(2)
        self.assertEqual((u.theme.font_size, u.theme.check_size, u.theme.check_radius), (28, 18, 10))
        u.scale(0)
        u.scale(-1)
        self.assertEqual(u.theme.font_size, 28)
        u.scale(0.5)
        self.assertEqual(u.theme.font_size, 14)

    def test_style_takes_new_fields(self):
        k = self.k
        u = k.u

        def draw(**kw):
            for _ in range(2):
                with u.frame(0):
                    with u.window("s", goome.Window(6, 6, 300, 0), 0):
                        with u.style(**kw):
                            u.checkbox("Big", True)
                            u.size(200, 0)
                            u.button("Left")
            return frame_hash(k.g)

        base = draw()
        self.assertNotEqual(draw(check_size=26, check_radius=13, knob=0xFFF59E0B), base)
        self.assertNotEqual(draw(align="left"), base)
        self.assertEqual(draw(align=goome.ALIGN_AUTO, ease="smooth"), base)
        self.assertEqual(draw(), base)
        self.assertRaises(ValueError, u.push_color, "check_size", 1)
        self.assertRaises(ValueError, u.push_num, "knob", 1)


if __name__ == "__main__":
    unittest.main()
