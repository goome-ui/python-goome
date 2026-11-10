import os
import subprocess
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
