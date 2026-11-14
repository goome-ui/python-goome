import os
import re
import shutil
import subprocess
import sys

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution

try:
    from setuptools.command.bdist_wheel import bdist_wheel
except ImportError:
    try:
        from wheel.bdist_wheel import bdist_wheel
    except ImportError:
        bdist_wheel = None

HERE = os.path.dirname(os.path.abspath(__file__))
NATIVE = os.path.join(HERE, "native")


def lib_name():
    if sys.platform == "win32":
        return "goome.dll"
    if sys.platform == "darwin":
        return "libgoome.dylib"
    return "libgoome.so"


def find_cc():
    names = [os.environ.get("CC")] + (["gcc", "clang", "cl"] if sys.platform == "win32" else ["cc", "gcc", "clang"])
    for n in names:
        if n and shutil.which(n.split()[0]):
            return n
    return None


def write_def(path):
    with open(os.path.join(NATIVE, "goome.h"), encoding="utf-8") as f:
        text = f.read()
    names = sorted(set(re.findall(r"^(?!static)[A-Za-z][\w \*]*?\b(goome_\w+)\s*\(", text, re.M)))
    with open(path, "w") as f:
        f.write("EXPORTS\n" + "".join("    %s\n" % n for n in names))


def build_native(out_dir, tmp_dir):
    cc = find_cc()
    if not cc:
        raise SystemExit(
            "goome: theres no prebuilt native library for this computer and i couldnt find a C compiler to build one.\n"
            "install one (build-essential on debian/ubuntu, xcode-select --install on mac, mingw-w64 or visual studio on windows) "
            "or set CC, then install again."
        )
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    src = os.path.join(NATIVE, "goome_lib.c")
    out = os.path.join(out_dir, lib_name())
    exe = os.path.basename(cc.split()[0]).lower()
    if exe in ("cl", "cl.exe"):
        d = os.path.join(tmp_dir, "goome.def")
        write_def(d)
        cmd = cc.split() + ["/nologo", "/O2", "/LD", "/I" + NATIVE, src, "/Fo" + tmp_dir + os.sep, "/Fe" + out, "/link", "/DEF:" + d]
    elif sys.platform == "win32":
        cmd = cc.split() + ["-O2", "-std=c99", "-shared", "-static-libgcc", "-Wl,--export-all-symbols", "-o", out, src]
    elif sys.platform == "darwin":
        cmd = cc.split() + ["-O2", "-std=c99", "-fPIC", "-dynamiclib", "-mmacosx-version-min=11.0", "-o", out, src]
    else:
        cmd = cc.split() + ["-O2", "-std=c99", "-fPIC", "-shared", "-o", out, src]
    print("goome: building the native library: " + " ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except (OSError, subprocess.CalledProcessError) as e:
        raise SystemExit("goome: building the native library with %s failed (%s)" % (cc, e))
    return out


class BuildPy(build_py):
    def run(self):
        build_py.run(self)
        out_dir = os.path.join(self.build_lib, "goome", "_native")
        if os.path.isfile(os.path.join(out_dir, lib_name())) and not os.environ.get("GOOME_REBUILD"):
            return
        build_native(out_dir, os.path.join(self.build_lib, "goome-native"))


class PlatformDist(Distribution):
    def has_ext_modules(self):
        return True


cmds = {"build_py": BuildPy}

if bdist_wheel is not None:

    class Wheel(bdist_wheel):
        def finalize_options(self):
            bdist_wheel.finalize_options(self)
            self.root_is_pure = False

        def get_tag(self):
            plat = bdist_wheel.get_tag(self)[2]
            if sys.platform == "darwin":
                import platform

                plat = "macosx_11_0_" + platform.machine()
            return "py3", "none", plat

    cmds["bdist_wheel"] = Wheel

setup(cmdclass=cmds, distclass=PlatformDist, license="GPL-3.0-only")
