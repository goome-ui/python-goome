import array
import ctypes
import os
import unittest

from tests.util import HERE, fnv, run_c

import goome
from goome import ui as uimod

D, U, M = goome.DOWN, goome.UP, goome.MOTION


def click(g, x, y):
    g.push_click(x, y)


SCRIPT = {
    1: lambda g: click(g, 28, 14), 5: lambda g: click(g, 28, 14), 3: lambda g: click(g, 60, 77), 7: lambda g: click(g, 60, 50),
    9: lambda g: click(g, 330, 93), 10: lambda g: g.push_text("!"), 11: lambda g: g.push(goome.KEY, key=goome.K_ENTER),
    12: lambda g: g.push_text("x"), 14: lambda g: click(g, 240, 158), 16: lambda g: click(g, 70, 67),
    18: lambda g: (g.push(M, x=407, y=279), g.push(D, x=407, y=279, button=1)), 19: lambda g: g.push(M, x=447, y=279),
    20: lambda g: g.push(U, x=447, y=279, button=1), 22: lambda g: click(g, 590, 339), 24: lambda g: click(g, 250, 430),
    28: lambda g: g.push(goome.KEY, key=goome.K_ESC),
    30: lambda g: (g.push(M, x=100, y=160), g.push(goome.SCROLL, x=100, y=160, dy=3)),
}


def scene():
    g = goome.open_offscreen(640, 520, 1, "scene")
    u = g.ui()
    u.theme.update(anim_ms=0, font=None, font_size=14)
    wrap, tree, modal, pane = goome.Flag(False), goome.Flag(True), goome.Flag(False), goome.Split(0.3)
    st = dict(text="hello\nworld", speed=1.5, count=2.0, news=0, sorted=0, sort=None, seen=0, rows=None, mid=None)
    for f in range(34):
        if f in SCRIPT:
            SCRIPT[f](g)
        for ev in g.events(0):
            u.feed(ev)
        with u.frame(0) as c:
            if c is None:
                continue
            with u.app("Scene", goome.APP_MENUBAR | goome.APP_STATUSBAR):
                with u.menubar() as bar:
                    if bar:
                        with u.menu("File") as shown:
                            if shown:
                                if u.menu_item("New", "Ctrl+N"):
                                    st["news"] += 1
                                u.menu_item("Wrap", None, wrap)
                with u.split("main", pane) as panes:
                    with u.tree("Folder", tree) as shown:
                        if shown:
                            u.label("a.txt")
                            u.label("b.txt")
                    with u.scroll_begin("list", 120):
                        rows = u.list_clip(100)
                        st["rows"] = rows
                        for k in rows:
                            u.selectable("row %d" % k)
                    panes.next()
                    st["text"] = u.text_edit("body", st["text"], 80, goome.EDIT_LINE_NUMBERS)
                    with u.table("files", 2, 90, goome.TABLE_SORTABLE | goome.TABLE_STRIPES) as t:
                        t.column("Name")
                        t.column("Size", 80)
                        st["sort"] = t.sort(0, False)
                        st["sorted"] += st["sort"].changed
                        for k in range(3):
                            t.row()
                            u.label("file %d" % k)
                            t.next()
                            u.label("%d kb" % k)
                    st["speed"] = u.drag_float("Speed", st["speed"], 0.1, 0, 10, "%.1f")
                    st["count"] = u.number("Count", st["count"], 1, "%.0f")
                    u.plot_lines("fps", array.array("f", [1, 3, 2, 5, 4]), 0, 5, 30)
                    if u.link("open about"):
                        modal.value = True
                    u.badge("new", 0xFF6FDC5F)
                with u.modal("About", modal) as shown:
                    if shown:
                        st["seen"] += 1
                        u.label("about box")
                        if u.button("Close"):
                            modal.value = False
                u.statusbar("ready")
        if f == 25:
            fr = g.last_frame()
            st["mid"] = "%08x" % fnv(fr.pixels, fr.w, fr.h, fr.stride)
    fr = g.last_frame()
    st["end"] = "%08x" % fnv(fr.pixels, fr.w, fr.h, fr.stride)
    st.update(wrap=wrap.value, tree=tree.value, modal=modal.value, frac=pane.frac)
    u.close()
    g.close()
    return st


class Spy(object):
    def __init__(self, real, force=None, fake=()):
        self._real = real
        self.force = force or {}
        self.fake = set(fake)
        self.calls = []
        self.floats = None

    def __getattr__(self, name):
        f = getattr(self._real, name)
        if not name.startswith("goome_ui_") or name in ("goome_ui_new", "goome_ui_free", "goome_ui_theme"):
            return f

        def call(*a):
            self.calls.append(name[len("goome_ui_"):])
            if name.startswith("goome_ui_plot_"):
                self.floats = [a[2][i] for i in range(a[3])], a[4], a[5]
            short = name[len("goome_ui_"):]
            if short in self.fake:
                return self.force.get(short)
            return self.force.get(short, f(*a))

        return call


def run(fn, script="screen 640x480 1; end 4", frames=3, force=None, fake=()):
    real = uimod.lib
    spy = Spy(real, force, fake)
    uimod.lib = spy
    try:
        with goome.open(backend="test", test_script=script) as g, g.ui() as u:
            u.theme.update(font=None, anim_ms=0)
            out = None
            for i in range(frames):
                for ev in g.events(0):
                    u.feed(ev)
                with u.frame(0) as c:
                    if c is not None:
                        out = fn(u, i)
            return spy, out
    finally:
        uimod.lib = real


def between(calls, start, stop):
    return calls[calls.index(start) : len(calls) - calls[::-1].index(stop)]


class Widgets(unittest.TestCase):
    def test_scripted(self):
        st = scene()
        self.assertEqual(st["news"], 1)
        self.assertTrue(st["wrap"])
        self.assertFalse(st["tree"])
        self.assertEqual(st["text"], "hello\nworld!\nx")
        self.assertEqual((st["sorted"], st["sort"]), (1, goome.Sort(False, 0, True)))
        self.assertAlmostEqual(st["speed"], 5.5)
        self.assertEqual(st["count"], 3)
        self.assertTrue(st["seen"] > 0 and not st["modal"])
        self.assertEqual(st["rows"], range(4, 9))
        self.assertAlmostEqual(st["frac"], 0.3)
        out = run_c(os.path.join(HERE, "widgets.c"))
        if out is None:
            if os.environ.get("GOOME_STRICT"):
                self.fail("no C compiler to check the widget hashes with")
            return
        lines = out.splitlines()
        self.assertEqual(lines[0], "mid " + st["mid"])
        self.assertEqual(lines[1], "end " + st["end"])
        self.assertEqual(lines[2], "state wrap=1 tree=0 modal=0 seen=1 news=1 sorted=1 col=0 desc=1 speed=5.5 count=3 rows=4,9 frac=0.30")
        self.assertEqual("\n".join(lines[3:]), "text " + st["text"])

    def test_popups(self):
        g = goome.open_offscreen(400, 300, 1, "s2")
        u = g.ui()
        u.theme.update(anim_ms=0, font=None, font_size=14)
        st = dict(n=5, name="", ctx=0, pop=[], dropped=None, focused=False)

        def at(*evs):
            return lambda: [g.push(e[0], x=e[1], y=e[2], button=e[3] if len(e) > 3 else 1) for e in evs]

        script = {
            1: lambda: g.push_text("hi"),
            3: at((M, 56, 24), (D, 56, 24)), 4: at((M, 60, 40)), 5: at((M, 63, 62)), 6: at((U, 63, 62)),
            8: at((M, 56, 24), (D, 56, 24, 3), (U, 56, 24, 3)), 10: at((M, 100, 44), (D, 100, 44), (U, 100, 44)),
            12: at((M, 200, 182), (D, 200, 182)), 13: at((M, 230, 182)), 14: at((U, 230, 182)),
            16: at((M, 37, 280), (D, 37, 280), (U, 37, 280)), 19: lambda: g.push(goome.KEY, key=goome.K_ESC),
        }
        with g, u:
            for i in range(22):
                if i in script:
                    script[i]()
                for ev in g.events(0):
                    u.feed(ev)
                with u.frame(0):
                    u.button("Drag me")
                    u.drag_source("note", b"hello there")
                    with u.context("ctx") as shown:
                        if shown:
                            if u.menu_item("Rename"):
                                st["ctx"] += 1
                            u.menu_separator()
                            u.menu_item("Delete")
                    u.button("Drop here")
                    d = u.drop_target("note")
                    if d:
                        st["dropped"] = d
                    if i == 0:
                        u.set_focus()
                    st["name"] = u.input("Name", st["name"])
                    st["focused"] = st["focused"] or u.focused
                    st["n"] = u.drag_int("N", st["n"], 1, 0, 100)
                    u.plot_bars("bars", [1, 2, 3], 0, 3, 30)
                    if u.button("Pop"):
                        u.popup_open("pop")
                        u.toast("toasted", 5000)
                    with u.popup("pop") as shown:
                        if shown:
                            st["pop"].append(i)
                            u.label("in a popup")
                    u.spinner(12)
        self.assertEqual(st["name"], "hi")
        self.assertTrue(st["focused"])
        self.assertEqual(st["dropped"], b"hello there")
        self.assertEqual(st["ctx"], 1)
        self.assertEqual(st["n"], 35)
        self.assertTrue(st["pop"] and min(st["pop"]) == 16 and max(st["pop"]) < 20, st["pop"])

    def test_skins(self):
        def hash_with(skin):
            with goome.open_offscreen(200, 80) as g, g.ui() as u:
                u.theme.update(anim_ms=0, font=None)
                if skin is not None:
                    u.theme.skin_button = skin
                with u.frame(0):
                    u.button("Skinned")
                f = g.last_frame()
                return fnv(f.pixels, f.w, f.h, f.stride), u.theme.skin_button

        px = [0xFF2040A0] * 256
        for i in range(16):
            px[i] = px[255 - i] = px[i * 16] = px[i * 16 + 15] = 0xFFFFFFFF
        bmp = goome.Bitmap.from_argb(px, 16, 16)
        plain, none = hash_with(None)
        skinned, got = hash_with((bmp, 4))
        self.assertIsNone(none)
        self.assertNotEqual(plain, skinned)
        self.assertEqual(got, goome.Skin(bmp, 4.0, 4.0, 4.0, 4.0))
        with goome.open_offscreen(100, 50) as g, g.ui() as u:
            u.theme.skin_panel = (bmp, 1, 2, 3, 4)
            self.assertEqual(u.theme.skin_panel[1:], (1, 2, 3, 4))
            with self.assertRaises(ValueError):
                u.theme.skin_input = (bmp,)
            bmp.close()
            self.assertIsNone(u.theme.skin_panel)
            self.assertFalse(u.theme._t().skin_panel.bm)
            u.theme.skin_panel = None

    def test_pairs(self):
        def draw(u, i):
            with u.menubar():
                with u.menu("File"):
                    pass
            with u.context("c"):
                pass
            with u.popup("p"):
                pass
            with u.modal("m", goome.Flag(True)):
                pass
            with u.tree("t"):
                pass
            with u.table("t", 2) as t:
                if t:
                    t.column("a")
                    sorts.append(t.sort(1, True))
                    t.row()
                    t.next()
            with u.split("s") as s:
                s.next()
            with u.app():
                pass

        sorts = []
        names = ("menubar", "menu", "context", "popup", "modal", "tree", "table", "split", "app")
        fake = [n + "_begin" for n in names] + [n + "_end" for n in names] + ["tree", "app", "table_column", "table_sort", "table_row",
                                                                             "table_next", "split_next"]
        shut = run(draw, frames=1, force=dict((n, 0) for n in fake), fake=fake)[0].calls
        for end in ("menubar_end", "menu_end", "context_end", "popup_end", "modal_end", "tree_end"):
            self.assertNotIn(end, shut)
        for end in ("table_end", "split_end", "app_end"):
            self.assertEqual(shut.count(end), 1, end)
        opened = run(draw, frames=1, force=dict((n, 1) for n in fake), fake=fake)[0].calls
        for end in ("menubar_end", "menu_end", "context_end", "popup_end", "modal_end", "tree_end", "table_end", "split_end", "app_end"):
            self.assertEqual(opened.count(end), 1, end)
        self.assertEqual(between(opened, "menubar_begin", "menubar_end"), ["menubar_begin", "menu_begin", "menu_end", "menubar_end"])
        self.assertEqual(between(opened, "table_begin", "table_end"),
                         ["table_begin", "table_column", "table_sort", "table_row", "table_next", "table_end"])
        self.assertEqual(sorts, [goome.Sort(True, 1, True)])

    def test_raise(self):
        def draw(u, i):
            with u.modal("m"):
                raise KeyError("boom")

        with self.assertRaises(KeyError):
            run(draw, frames=1, force=dict(modal_begin=1, modal_end=None), fake=["modal_begin", "modal_end"])

    def test_plots(self):
        got = []

        def draw(u, i):
            u.plot_lines("a", values)

        for values in ([1, 2, 3], (1.0, 2.0, 3.0), array.array("f", [1, 2, 3]), (ctypes.c_float * 3)(1, 2, 3), range(1, 4)):
            spy, _ = run(draw, frames=1)
            got.append(spy.floats)
        try:
            import numpy
        except ImportError:
            numpy = None
        if numpy is not None:
            for values in (numpy.array([1, 2, 3], dtype=numpy.float32), numpy.array([1, 2, 3], dtype=numpy.float64)):
                spy, _ = run(draw, frames=1)
                got.append(spy.floats)
        for g in got:
            self.assertEqual(g, ([1.0, 2.0, 3.0], 1.0, 3.0))
        values = []
        spy, _ = run(draw, frames=1)
        self.assertEqual(spy.floats, ([], 0.0, 1.0))

    def test_holders(self):
        f = goome.Flag()
        self.assertFalse(f)
        f.toggle()
        self.assertTrue(f.value)
        s = goome.Split(0.25, vertical=True)
        s.frac = 0.4
        self.assertEqual((s.frac, s.vertical), (0.4, True))

        def draw(u, i):
            u.menu_item("x", checked=True)

        with self.assertRaises(TypeError):
            run(draw, frames=1)

    def test_long_text(self):
        big = "x" * 10000

        def draw(u, i):
            return u.text_edit("e", big, 100, goome.EDIT_READONLY | goome.EDIT_MONO)

        self.assertEqual(run(draw, frames=1)[1], big)

        def small(u, i):
            return u.text_edit("e", "héllo wörld", 100, cap=4)

        self.assertEqual(run(small, frames=1)[1], "hé")


class Nine(unittest.TestCase):
    def test_bitmap_nine(self):
        c = goome.Canvas.new(64, 64)
        bmp = goome.Bitmap.from_argb([0xFFFFFFFF] * 64, 8, 8)
        c.bitmap_nine(bmp, 0, 0, 64, 64, 2)
        c.bitmap_nine(bmp, 0, 0, 64, 64, 1, 2, 3, 4)
        bmp.close()


if __name__ == "__main__":
    unittest.main()
