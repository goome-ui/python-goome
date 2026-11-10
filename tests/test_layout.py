import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.util import HERE, ROOT

from goome import _lib


def compiler():
    for c in (os.environ.get("CC"), "cc", "gcc", "clang"):
        if c and shutil.which(c):
            return c
    return None


def c_layout():
    pre = os.environ.get("GOOME_LAYOUT")
    if pre:
        return subprocess.check_output([pre]).decode()
    cc = compiler()
    if not cc:
        return None
    with tempfile.TemporaryDirectory() as d:
        exe = os.path.join(d, "layout.exe" if sys.platform == "win32" else "layout")
        subprocess.check_call([cc, "-std=c99", "-I" + os.path.join(ROOT, "native"), "-o", exe, os.path.join(HERE, "layout.c")])
        return subprocess.check_output([exe]).decode()


class Layout(unittest.TestCase):
    def test_matches_c(self):
        out = c_layout()
        if out is None:
            if os.environ.get("GOOME_STRICT"):
                self.fail("no C compiler to check the layout with")
            self.skipTest("no C compiler, set CC or GOOME_LAYOUT")
        seen = 0
        for line in out.splitlines():
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            if "." in name:
                st, field = name.split(".")
                cls = _lib.STRUCTS[st]
                desc = getattr(cls, field)
                self.assertEqual((desc.offset, desc.size), (int(parts[1]), int(parts[2])), name)
            else:
                self.assertEqual(ctypes.sizeof(_lib.STRUCTS[name]), int(parts[1]), name)
            seen += 1
        want = sum(1 + len(c._fields_) for c in _lib.STRUCTS.values())
        self.assertEqual(seen, want)


if __name__ == "__main__":
    unittest.main()
