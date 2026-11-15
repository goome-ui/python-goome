import unittest

import tests.util

import goome

D, U, M = goome.DOWN, goome.UP, goome.MOTION


class Api(unittest.TestCase):
    def test_constants(self):
        self.assertEqual((goome.WANT_MOUSE, goome.WANT_KEYBOARD, goome.CAP_GRAB), (1, 2, 256))

    def test_grab_flag(self):
        with goome.open_offscreen(200, 100) as g:
            self.assertFalse(g.grabbed)
            g.grab(True)
            self.assertTrue(g.grabbed)
            g.grab(False)
            self.assertFalse(g.grabbed)
            self.assertFalse(g.can(goome.CAP_GRAB))

    def test_ui_defaults(self):
        with goome.open_offscreen(200, 100) as g:
            with g.ui() as u:
                self.assertEqual(u.wants, 0)
                self.assertFalse(u.wants_mouse or u.wants_keyboard)
                self.assertEqual(u.auto_grab, goome.WANT_MOUSE | goome.WANT_KEYBOARD)
                u.auto_grab = 0
                self.assertEqual(u.auto_grab, 0)
            with self.assertRaises(goome.GoomeError):
                u.wants


class Drag(unittest.TestCase):
    def run_drag(self, auto):
        g = goome.open_offscreen(400, 300, 1, "drag")
        u = g.ui()
        u.theme.update(anim_ms=0, font=None, font_size=14)
        if auto is not None:
            u.auto_grab = auto
        win = goome.Window(20, 20, 240, 0)
        modal = goome.Flag(False)
        st = dict(val=0.0, name="")
        steps = {
            1: lambda: g.push(M, x=SLIDER[0], y=SLIDER[1]),
            2: lambda: g.push(D, x=SLIDER[0], y=SLIDER[1], button=1),
            3: lambda: g.push(M, x=380, y=280),
            4: lambda: g.push(U, x=380, y=280, button=1),
            5: lambda: g.push(M, x=390, y=290),
            6: lambda: g.push_click(*FIELD),
            7: lambda: (g.push(M, x=390, y=290), g.push(goome.KEY, key=goome.K_ESC)),
            8: lambda: setattr(modal, "value", True),
        }
        seen = {}
        for f in range(10):
            if f in steps:
                steps[f]()
            for ev in g.events(0):
                u.feed(ev)
            with u.frame(0) as c:
                if c is None:
                    continue
                with u.window("drag", win, goome.WIN_MOVE):
                    st["val"] = u.slider("Val", st["val"], 0, 1, "%.2f")
                    st["name"] = u.input("Name", st["name"], 32)
                with u.modal("Sure", modal) as shown:
                    if shown:
                        u.label("really?")
            seen[f] = (u.wants, g.grabbed)
        u.close()
        g.close()
        return seen, st

    def test_drag(self):
        seen, st = self.run_drag(None)
        W, K = goome.WANT_MOUSE, goome.WANT_KEYBOARD
        self.assertEqual(seen[0], (0, False))
        self.assertEqual(seen[1], (W, False))
        self.assertEqual(seen[2], (W, True))
        self.assertEqual(seen[3], (W, True))
        self.assertEqual(st["val"], 1.0)
        self.assertEqual(seen[4], (0, False))
        self.assertEqual(seen[5], (0, False))
        self.assertTrue(seen[6][0] & K)
        self.assertFalse(seen[6][1])
        self.assertEqual(seen[7], (0, False))
        self.assertEqual(seen[8][0] & (W | K), W | K)

    def test_no_auto_grab(self):
        seen, st = self.run_drag(0)
        self.assertEqual(seen[2], (goome.WANT_MOUSE, False))
        self.assertEqual(seen[3], (goome.WANT_MOUSE, False))
        self.assertEqual(st["val"], 1.0)


SLIDER = (140, 95)
FIELD = (140, 152)


if __name__ == "__main__":
    unittest.main()
