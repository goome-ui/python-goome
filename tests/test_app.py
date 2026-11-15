import os
import unittest

import goome

LONG = "/home/someone/a/really/long/folder/name/that/goes/past/63/bytes/file.txt"
SCRIPT = ("screen 1x1 2; 1 click 250,150; 1 click 350,150; 2 resize 400x300; 3 close; 4 focus 0; 5 key a; 6 focus 1; 7 key b; "
          "8 drop 10,20 " + LONG + "; 9 resize 100x100; end 11")


class WindowMode(unittest.TestCase):
    def test_scripted(self):
        g = goome.open("notes", backend="test", mode="window", width=300, height=200, min_width=250, min_height=120, test_script=SCRIPT)
        with g:
            self.assertEqual(g.mode, goome.MODE_WINDOW)
            self.assertTrue(g.can(goome.CAP_WINDOW))
            m = g.monitors()[0]
            self.assertEqual((m.area.w, m.area.h, m.scale, m.pw, m.name), (300, 200, 2, 600, "notes"))
            n = dict(down=0, mons=0, close=0)
            focus, keys, drops, cw, quit, frames = [], "", [], 0, False, 0
            while not quit and frames < 100:
                with g.frame(0) as c:
                    if frames == 3:
                        cw = c.w
                    c.rect(0, 0, 300, 200, 0xFF202830)
                frames += 1
                for ev in g.events(1):
                    if ev.type == goome.DOWN:
                        n["down"] += 1
                    elif ev.type == goome.MONITORS:
                        n["mons"] += 1
                    elif ev.type == goome.CLOSE:
                        n["close"] += 1
                    elif ev.type == goome.FOCUS:
                        focus.append(ev.id)
                    elif ev.type == goome.KEY:
                        keys += ev.text
                    elif ev.type == goome.DROP:
                        drops.append((ev.x, ev.y, ev.msg, ev.path, g.drop_path))
                    elif ev.type == goome.QUIT:
                        quit = True
                    repr(ev)
            self.assertEqual((n["down"], n["mons"], n["close"], focus, keys, cw), (1, 2, 1, [0, 1], "b", 800))
            self.assertEqual(len(drops), 1)
            x, y, msg, path, now = drops[0]
            self.assertEqual((x, y, path, now), (10, 20, LONG, LONG))
            self.assertEqual(msg, LONG[:63])
            self.assertEqual(g.size, (250, 120))
            f = g.last_frame()
            self.assertEqual((f.w, f.pixel(0, 0)), (500, 0xFF202830))
            self.assertFalse(g.hit(5, 5))

            g.title = "renamed"
            self.assertEqual(g.title, "renamed")
            g.size = (500, 400)
            self.assertEqual((g.size, g.monitors()[0].pw), ((500, 400), 1000))
            g.pos = (30, 40)
            self.assertEqual(g.pos, (30, 40))
            g.maximize()
            self.assertEqual(g.state, goome.STATE_MAXIMIZED)
            g.maximize()
            self.assertEqual(g.state, goome.STATE_NORMAL)
            g.state = "fullscreen"
            self.assertEqual(g.state, goome.STATE_FULLSCREEN)
            with self.assertRaises(goome.BadArg):
                g.state = 9
            with self.assertRaises(ValueError):
                g.state = "huge"
            g.drag(goome.EDGE_LEFT)
            g.show()
            g.clipboard = "copied"
            self.assertEqual(g.clipboard, "copied")
            g.cursor = goome.CURSOR_RESIZE_EW
            self.assertEqual(g.cursor, goome.CURSOR_RESIZE_EW)
            g.resize(320, 200)
            self.assertEqual(g.size, (320, 200))

    def test_open_app(self):
        old = os.environ.get("GOOME_BACKEND")
        os.environ["GOOME_BACKEND"] = "test"
        try:
            with goome.open_app("app", 640, 480) as g:
                self.assertEqual(g.mode, goome.MODE_WINDOW)
                self.assertEqual((g.size, g.title), ((640, 480), "app"))
            with goome.open_app() as g:
                self.assertEqual((g.size, g.title), ((960, 640), "goome"))
            with goome.open_app("min", 500, 300, min_width=400) as g:
                self.assertEqual((g.size, g.title), ((500, 300), "min"))
        finally:
            if old is None:
                del os.environ["GOOME_BACKEND"]
            else:
                os.environ["GOOME_BACKEND"] = old

    def test_overlay(self):
        with goome.open(backend="test", test_script="end 1") as g:
            self.assertEqual(g.mode, goome.MODE_OVERLAY)
            self.assertFalse(g.can(goome.CAP_WINDOW))
            self.assertIsNone(g.title)
            with self.assertRaises(goome.NotSupported):
                g.title = "x"
            with self.assertRaises(goome.NotSupported):
                g.state
            self.assertIsNone(g.drop_path)
        with self.assertRaises(goome.BadArg):
            goome.open(mode=7)
        with self.assertRaises(ValueError):
            goome.open(mode="sideways")


class AppHelper(unittest.TestCase):
    def test_scripted(self):
        app = goome.App("Notes", 400, 300, flags=goome.APP_MENUBAR | goome.APP_STATUSBAR, backend="test",
                        test_script="screen 1x1 1; 2 resize 500x320; 4 focus 0; 5 drop 3,4 " + LONG + "; 6 close; 8 close; end 30")
        seen = dict(close=0, drops=[], focus=[], sizes=set(), started=False)

        @app.on_start
        def started():
            seen["started"] = app.g is not None

        @app.event
        def on(ev):
            if ev.type == goome.DROP:
                seen["drops"].append(ev.path)
            if ev.type == goome.FOCUS:
                seen["focus"].append(ev.id)

        @app.on_close
        def closing():
            seen["close"] += 1
            return seen["close"] > 1

        @app.frame
        def draw(ui):
            seen["sizes"].add(app.g.size)
            with ui.menubar():
                with ui.menu("File") as shown:
                    if shown:
                        ui.menu_item("Quit")
            ui.label("hello")
            ui.statusbar("ready")

        app.run()
        self.assertTrue(seen["started"])
        self.assertEqual(seen["close"], 2)
        self.assertEqual(seen["drops"], [LONG])
        self.assertEqual(seen["focus"], [0])
        self.assertIn((500, 320), seen["sizes"])
        self.assertTrue(8 <= app.frames <= 10, app.frames)
        self.assertIsNone(app.g)
        self.assertFalse(app.running)

    def test_idle(self):
        app = goome.App("idle", 300, 200, backend="offscreen", idle_ms=0)
        drawn = []
        app.frame(lambda ui: drawn.append(app.frames))
        app.start()
        try:
            self.assertEqual(app.g.backend_name, "offscreen")
            for _ in range(5):
                app.step()
            self.assertEqual(len(drawn), 2)
            app.g.push(goome.MOTION, x=5, y=5)
            for _ in range(5):
                app.step()
            self.assertEqual(len(drawn), 4)
            app.animate = True
            for _ in range(3):
                app.step(wait=False)
            self.assertEqual(len(drawn), 7)
            app.animate = False
            app.step()
            app.redraw()
            app.step()
            self.assertEqual(len(drawn), 8)
            app.g.push(goome.CLOSE)
            self.assertFalse(app.step())
        finally:
            app.stop()
        self.assertIsNone(app.ui)

    def test_quit(self):
        app = goome.App("q", backend="offscreen")
        app.on_start(lambda: setattr(app, "animate", True))
        app.run(lambda ui: app.quit() if app.frames >= 3 else None)
        self.assertEqual(app.frames, 4)


if __name__ == "__main__":
    unittest.main()
