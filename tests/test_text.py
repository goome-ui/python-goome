import unittest

from tests.util import data, fnv

import goome

L, R, H, E, S = goome.K_LEFT, goome.K_RIGHT, goome.K_HOME, goome.K_END, goome.SHIFT
HEB = "אבג"
SMILE = "\U0001F600"
TONE = "\U0001F3FB"
CAT = "\U0001F431"
ARAB = "بلام ببب لم"


def font(name):
    return goome.Font.from_bytes(data(name))


def txt_hash(f, size, s, argb, dir, w, h):
    c = goome.Canvas.new(400, 120)
    px = c.pixels
    c.raw.w, c.raw.h, c.raw.kx1, c.raw.ky1 = w, h, w, h
    goome.text_dir(dir)
    try:
        c.font_text(f, size, 4, 4, s, argb)
    finally:
        goome.text_dir(goome.DIR_AUTO)
    return fnv(px, 400, 120)


def near(a, b):
    return abs(a - b) < 0.01


class EmojiRtl(unittest.TestCase):
    def test_hashes_match_c(self):
        f, cb, sb, d = font("colr.ttf"), font("cbdt.ttf"), font("sbix.ttf"), font("dejavu-sub.ttf")
        self.assertTrue(near(f.width(SMILE + TONE, 30), 24))
        self.assertTrue(near(f.width(SMILE + "‍" + SMILE, 30), 24))
        self.assertTrue(near(f.width("❤", 30), 18) and near(f.width("❤️", 30), 24))
        got = [txt_hash(f, 30, "ab %s %s%s %s‍%s ❤ ❤️" % (SMILE, SMILE, TONE, SMILE, SMILE), 0xFF2040A0, 0, 400, 60)]
        c = goome.Canvas.new(400, 120)
        c.font_text(cb, 16, 4, 4, CAT, 0xFFFFFFFF)
        c.font_text(cb, 64, 30, 4, CAT, 0xFFFFFFFF)
        c.font_text(sb, 40, 120, 4, CAT + CAT, 0x80FFFFFF)
        mid = c.pixels[(4 + 40) * 400 + 30 + 35]
        self.assertTrue(mid >> 24 == 255 and (mid >> 16 & 255) > 200 and 100 < (mid >> 8 & 255) < 210 and (mid & 255) < 120)
        got.append(fnv(c.pixels, 400, 120))
        self.assertIs(d.fallback(f, d), d)
        self.assertEqual(d.fallbacks, [f])
        self.assertTrue(near(d.width("goome! " + SMILE, 20), d.width("goome! ", 20) + 16))
        got.append(txt_hash(d, 20, "goome! %s Hi" % SMILE, 0xFFFFFFFF, 0, 400, 40))
        mixed = "ab %s (12) c" % HEB
        got.append(txt_hash(f, 24, mixed, 0xFFFFFFFF, 0, 400, 40))
        self.assertNotEqual(got[3], txt_hash(f, 24, mixed, 0xFFFFFFFF, goome.DIR_RTL, 400, 40))
        self.assertEqual(got[3], txt_hash(f, 24, mixed, 0xFFFFFFFF, "ltr", 400, 40))
        got.append(txt_hash(f, 24, mixed, 0xFFFFFFFF, "rtl", 400, 40))
        self.assertTrue(near(f.width(ARAB, 20), 93.2))
        got.append(txt_hash(f, 30, ARAB + " بَب", 0xFFFFFFFF, 0, 400, 50))
        split = "ب لام ب ب ب لم"
        self.assertNotEqual(got[5], txt_hash(f, 30, split, 0xFFFFFFFF, 0, 400, 50))
        self.assertEqual(["%08x" % h for h in got], ["3bab3875", "85fe883a", "d3add387", "b79518dd", "49a72d7d", "469719e1"])
        with self.assertRaises(goome.GoomeError):
            f.close()
        d.close()
        f.close()
        for x in (cb, sb):
            x.close()

    def test_text_dir_names(self):
        goome.text_dir("rtl")
        goome.text_dir("auto")
        with self.assertRaises(ValueError):
            goome.text_dir("up")


def bd_run(f, edit, text, keys):
    g = goome.Goome(backend=goome.TEST, mode=goome.MODE_WINDOW, width=300, height=200, test_script="end 100000")
    u = g.ui()
    u.theme.update(font=f, font_size=14, anim_ms=0)
    u.config.blink_ms = 0
    st = {"in": "" if edit else text, "ed": text if edit else "", "hash": 0}

    def frame(focus):
        for ev in g.events(0):
            u.feed(ev)
        c = u.begin(0)
        if c is None:
            return
        px, w, h, stride = c.pixels, c.w, c.h, c.stride
        if focus == 1:
            u.set_focus()
        st["in"] = u.input_ex("in", st["in"], goome.INPUT_NO_SELECT_ON_FOCUS, None, 64)
        if focus == 2:
            u.set_focus()
        st["ed"] = u.text_edit("ed", st["ed"], 80, 0, 96)
        u.end()
        st["hash"] = fnv(px, w, h, stride)

    frame(2 if edit else 1)
    frame(0)
    for key, mods in keys:
        t = chr(key) if 32 <= key < 127 and not mods & goome.CTRL else ""
        g.push(goome.KEY, key=key, mods=mods, text=t)
        frame(0)
    frame(0)
    u.close()
    g.close()
    return st["ed" if edit else "in"], st["hash"]


def k(*keys):
    return [(x, 0) if isinstance(x, int) else x for x in keys]


class BidiCaret(unittest.TestCase):
    def test_caret_matches_c(self):
        f = font("colr.ttf")
        hs = []
        t, h = bd_run(f, 0, HEB, k(H, L, ord("a")))
        self.assertEqual(t, "אaבג")
        hs.append(h)
        self.assertEqual(bd_run(f, 0, HEB, k(E, R, ord("b")))[0], "אבbג")
        self.assertEqual(bd_run(f, 0, HEB, k(H, R, ord("c")))[0], "c" + HEB)
        self.assertEqual(bd_run(f, 0, "abc " + HEB, k(E, L, ord("z")))[0], "abcz " + HEB)
        self.assertEqual(bd_run(f, 0, "ab אב cd", k(H, R, R, R, R, ord("x")))[0], "ab אxב cd")
        hs.append(bd_run(f, 0, "ab %s cd" % HEB, k(H, R, R, R, (R, S), (R, S)))[1])
        self.assertEqual(bd_run(f, 0, SMILE + TONE + "a", k(H, R, ord("q")))[0], SMILE + TONE + "qa")
        t, h = bd_run(f, 1, HEB + "\nabc", k(H, L, ord("x")))
        self.assertEqual(t, "אxבג\nabc")
        hs.append(h)
        self.assertEqual(bd_run(f, 1, HEB + "\nabc", k(H, L, L, L, L, ord("y")))[0], HEB + "\nyabc")
        hs.append(bd_run(f, 1, "אב ab ג\nبب", k(H, (L, S), (L, S), (L, S)))[1])
        hs.append(bd_run(f, 0, "بلام 12", k(E, (L, S)))[1])
        hs.append(bd_run(f, 0, "بلام 12", k(E, (R, S)))[1])
        self.assertNotEqual(hs[4], hs[5])
        self.assertEqual(["%08x" % h for h in hs], ["f96a8023", "8c422f63", "eb1c9776", "fb019b26", "31cd9204", "e15c011a"])
        f.close()


if __name__ == "__main__":
    unittest.main()
