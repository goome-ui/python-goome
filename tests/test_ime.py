import re
import unittest

from tests.util import fnv

import goome

NIHON = "にほん"


class Im(object):
    def __init__(self, script, text_in, text_ed, focus):
        self.g = goome.Goome(backend=goome.TEST, mode=goome.MODE_WINDOW, width=300, height=200, test_script=script)
        self.u = self.g.ui()
        self.u.theme.update(font=None, font_size=14, anim_ms=0)
        self.u.config.blink_ms = 0
        self.text_in, self.text_ed, self.flags, self.ctl, self.hash = text_in, text_ed, 0, "", 0
        self.frame(focus)
        self.frame(0)

    def frame(self, focus=0):
        u = self.u
        for ev in self.g.events(0):
            if ev.type == goome.CONTROL and ev.msg.startswith("ime "):
                self.ctl = ev.msg
            u.feed(ev)
        c = u.begin(0)
        if c is None:
            return
        px, w, h, stride = c.pixels, c.w, c.h, c.stride
        if focus == 1:
            u.set_focus()
        self.text_in = u.input_ex("in", self.text_in, goome.INPUT_NO_SELECT_ON_FOCUS | self.flags, None, 64)
        if focus == 2:
            u.set_focus()
        self.text_ed = u.text_edit("ed", self.text_ed, 80, 0, 96)
        u.end()
        self.hash = fnv(px, w, h, stride)

    def preedit(self, text, caret):
        self.g.push_preedit(text, caret)
        self.frame()

    def commit(self, text):
        self.g.push_commit(text)
        self.frame()

    def key(self, key, mods=0):
        t = chr(key) if 32 <= key < 127 and not mods & goome.CTRL else ""
        self.g.push(goome.KEY, key=key, mods=mods, text=t)
        self.frame()

    def close(self):
        self.u.close()
        self.g.close()


class Ime(unittest.TestCase):
    def test_events(self):
        longt = "q" * 80
        sc = "1 text %s;2 preedit %s 3;3 preedit abc;4 preedit;end 10" % (longt, NIHON)
        with goome.Goome(backend=goome.TEST, mode=goome.MODE_WINDOW, width=100, height=100, test_script=sc) as g:
            g.push(goome.TEXT, text="hi")
            ev = g.poll(0)
            self.assertEqual((ev.type, ev.name, ev.msg, ev.text, g.event_text), (goome.TEXT, "text", "hi", "hi", "hi"))
            g.text_input(True, (10, 20, 1, 16))
            g.text_input(False)
            got, quit = 0, False
            for _ in range(20):
                if quit:
                    break
                for ev in g.events(0):
                    if ev.type == goome.QUIT:
                        quit = True
                    if ev.type == goome.TEXT:
                        got |= 1
                        self.assertEqual((len(ev.msg), ev.text), (63, longt))
                    if ev.type == goome.PREEDIT and ev.text == NIHON:
                        got |= 2
                        self.assertEqual((ev.id, ev.caret, g.preedit_cursor), (3, 1, 1))
                    if ev.type == goome.PREEDIT and ev.text == "abc":
                        got |= 4
                        self.assertEqual(ev.caret, 3)
                    if ev.type == goome.PREEDIT and ev.text == "":
                        got |= 8
                        self.assertEqual((ev.caret, g.preedit_cursor, g.event_text), (0, 0, ""))
                with g.frame(0):
                    pass
            self.assertEqual(got, 15)
            self.assertIn("preedit", repr(goome.Event.make(goome.PREEDIT, text="ab", caret=1)))
            with self.assertRaises(ValueError):
                g.push_commit("x" * 64)

    def test_preedit_hashes_match_c(self):
        k = Im("end 100000", "ab", "", 1)
        try:
            h0 = k.hash
            k.preedit("xyz", 1)
            h1 = k.hash
            k.preedit("xyz", 3)
            h2 = k.hash
            self.assertTrue(h0 != h1 != h2 and k.text_in == "ab")
            k.preedit("", 0)
            self.assertEqual(k.hash, h0)
            self.assertEqual(("%08x" % h1, "%08x" % h2), ("2e20540f", "ceafcbad"))
        finally:
            k.close()
        k = Im("end 100000", "", "line", 2)
        try:
            h3 = k.hash
            k.preedit("kana", 2)
            self.assertNotEqual(k.hash, h3)
            self.assertEqual("%08x" % k.hash, "c9c1add5")
        finally:
            k.close()

    def test_commit_into_input(self):
        k = Im("end 100000", "ab", "", 1)
        try:
            k.commit("日本")
            self.assertEqual(k.text_in, "ab日本")
            k.key(ord("c"))
            self.assertEqual(k.text_in, "ab日本c")
            k.key(ord("z"), goome.CTRL)
            self.assertEqual(k.text_in, "ab日本")
            k.key(ord("z"), goome.CTRL)
            self.assertEqual(k.text_in, "ab日本c")
            k.key(ord("a"), goome.CTRL)
            k.commit("é")
            self.assertEqual(k.text_in, "é")
            k.key(ord("z"), goome.CTRL)
            self.assertEqual(k.text_in, "ab日本c")
        finally:
            k.close()
        k = Im("end 100000", "", "line", 2)
        try:
            k.preedit("kana", 2)
            k.preedit("", 0)
            k.commit("かな\n")
            self.assertEqual((k.text_ed, k.text_in), ("かな\nline", ""))
            k.key(ord("z"), goome.CTRL)
            self.assertEqual(k.text_ed, "line")
        finally:
            k.close()
        k = Im("end 100000", "", "", 1)
        try:
            k.flags = goome.INPUT_NUMBER
            k.commit("1a2.5")
            self.assertEqual(k.text_in, "12.5")
        finally:
            k.close()

    def test_script_text_and_caret_rect(self):
        longt = "w" * 90
        k = Im("4 text %s;6 ime;end 100000" % longt, "", "", 1)
        try:
            for _ in range(8):
                k.frame()
            self.assertEqual(k.text_in, longt[:63])
            m = re.match(r"ime (\d+) (-?\d+),(-?\d+) (\d+)x(\d+)", k.ctl)
            self.assertIsNotNone(m, k.ctl)
            on, x, y, w, h = map(int, m.groups())
            self.assertTrue(on == 1 and x > 0 and y > 0 and h >= 14)
        finally:
            k.close()
        k = Im("3 ime;end 100000", "", "", 0)
        try:
            for _ in range(5):
                k.frame()
            self.assertTrue(k.ctl.startswith("ime 0 "), k.ctl)
        finally:
            k.close()


if __name__ == "__main__":
    unittest.main()
