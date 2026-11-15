import ctypes
import os
import re
import subprocess
import sys
import tempfile
import unittest

from tests.util import HERE, ROOT, compiler

import goome
from goome import _lib


def enum_names():
    with open(os.path.join(ROOT, "native", "goome.h")) as f:
        head = f.read().split("#ifdef GOOME_IMPLEMENTATION")[0]
    names = []
    for body in re.findall(r"enum\s*\{(.*?)\}", head, re.S):
        body = re.sub(r"//[^\n]*", "", body)
        names += re.findall(r"^\s*(GOOME_[A-Z0-9_]+)", body.replace(",", "\n"), re.M)
    return names


def c_consts(names):
    cc = compiler()
    if not cc:
        return None
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "consts.c")
        exe = os.path.join(d, "consts.exe" if sys.platform == "win32" else "consts")
        with open(src, "w") as f:
            f.write('#include <stdio.h>\n#include "goome.h"\nint main(void)\n{\n')
            for n in names:
                f.write('    printf("%%s %%d\\n", "%s", (int)%s);\n' % (n, n))
            f.write("    return 0;\n}\n")
        subprocess.check_call([cc, "-std=c99", "-I" + os.path.join(ROOT, "native"), "-o", exe, src])
        return subprocess.check_output([exe]).decode()


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

    def test_constants(self):
        names = enum_names()
        self.assertGreater(len(names), 100)
        out = c_consts(names)
        if out is None:
            if os.environ.get("GOOME_STRICT"):
                self.fail("no C compiler to check the constants with")
            self.skipTest("no C compiler, set CC")
        for line in out.splitlines():
            name, value = line.split()
            short = name[len("GOOME_"):]
            self.assertTrue(hasattr(goome, short), "goome.%s is missing" % short)
            self.assertEqual(getattr(goome, short), int(value), name)

    def test_every_function(self):
        with open(os.path.join(ROOT, "native", "goome.h")) as f:
            head = f.read().split("#ifdef GOOME_IMPLEMENTATION")[0]
        names = set(re.findall(r"\b(goome_[a-z0-9_]+)\s*\(", head))
        self.assertEqual(sorted(names - set(_lib.PROTOS)), [])


if __name__ == "__main__":
    unittest.main()
