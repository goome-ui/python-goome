import importlib.util
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

from tests.util import ROOT


def run(name, script, *args, **env):
    e = dict(os.environ, GOOME_BACKEND="test", GOOME_TEST_SCRIPT=script, PYTHONPATH=ROOT)
    e.update(env)
    return subprocess.run([sys.executable, os.path.join(ROOT, "examples", name)] + list(args), env=e, cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)


class Examples(unittest.TestCase):
    def test_hello(self):
        r = run("hello.py", "screen 800x600 1; 2 click 100,100; 3 click 100,180; 4 key hi; 5 hotkey alt+h; 6 hotkey alt+h; 7 key \\e; end 20")
        out = r.stdout.decode()
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        self.assertIn("backend: test", out)
        self.assertIn("click 100,100", out)
        self.assertIn("text 'h'", out)

    def test_grab(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.ppm")
            r = run("grab.py", "screen 320x200 1; end 5", "0", "10", "10", "40", "30", p)
            self.assertEqual(r.returncode, 0, r.stderr.decode())
            self.assertIn("40x30 px", r.stdout.decode())
            with open(p, "rb") as f:
                self.assertEqual(f.read(2), b"P6")
            r = run("grab.py", "end 1")
            self.assertEqual(r.returncode, 2)

    def test_ui_demo(self):
        r = run("ui_demo.py", "screen 1280x720 1; 3 click 60,62; 6 click 130,62; 9 click 200,62; 12 click 270,62; 15 click 600,52; end 30")
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        self.assertIn("frames", r.stdout.decode())

    def test_app(self):
        code = ("import runpy, sys; m = runpy.run_path(%r); app = m['app']; "
                "app.on_start(lambda: app.ui.theme.update(font=None)); sys.exit(m['main']())" % os.path.join(ROOT, "examples", "app.py"))
        e = dict(os.environ, GOOME_BACKEND="test", PYTHONPATH=ROOT)
        outs = []
        for script in ("screen 1x1 1; 3 click 67,160; 5 click 900,560; 6 key hi; 10 close; end 20",
                       "screen 1x1 1; 3 click 60,268; 6 key hi; 10 close; end 20"):
            e["GOOME_TEST_SCRIPT"] = script
            r = subprocess.run([sys.executable, "-c", code], env=e, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr.decode())
            outs.append(r.stdout.decode())
        self.assertIn("5 notes, on 'Workout'", outs[0])
        self.assertIn("fri pullhi'", outs[0])
        self.assertIn("6 notes, on 'Untitled'", outs[1])

    def test_offscreen(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "off.png")
            e = dict(os.environ, PYTHONPATH=ROOT)
            e.pop("GOOME_BACKEND", None)
            r = subprocess.run([sys.executable, os.path.join(ROOT, "examples", "offscreen.py"), p], env=e, cwd=ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr.decode())
            self.assertIn("check 1 volume", r.stdout.decode())
            with open(p, "rb") as f:
                png = f.read()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        w, h = struct.unpack(">II", png[16:24])
        self.assertEqual((w, h), (720, 660))
        n = struct.unpack(">I", png[33:37])[0]
        self.assertEqual(png[37:41], b"IDAT")
        self.assertEqual(len(zlib.decompress(png[41 : 41 + n])), h * (w * 3 + 1))

    def test_pygame(self):
        if importlib.util.find_spec("pygame") is None:
            self.skipTest("no pygame, its optional")
        e = dict(os.environ, PYTHONPATH=ROOT, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        e.pop("GOOME_BACKEND", None)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "examples", "pygame_embed.py"), "10"], env=e, cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        self.assertIn("ran 10 frames", r.stdout.decode())


if __name__ == "__main__":
    unittest.main()
