import os
import sys

import goome

SKINS = [
    ("skin_button", "button", 8, 8, 8, 8),
    ("skin_input", "input", 8, 8, 8, 8),
    ("skin_checkbox", "checkbox", 18, 18, 18, 18),
    ("skin_radio", "radio", 18, 18, 18, 18),
    ("skin_toggle", "toggle", 38, 22, 38, 22),
    ("skin_slider", "slider", 3, 3, 3, 3),
    ("skin_slider_fill", "slider_fill", 3, 3, 3, 3),
    ("skin_scrollbar", "scrollbar", 3, 3, 3, 3),
    ("skin_tab", "tab", 8, 8, 8, 8),
    ("skin_titlebar", "titlebar", 12, 12, 12, 3),
    ("skin_tooltip", "tooltip", 8, 8, 8, 8),
    ("skin_menu", "menu", 10, 10, 10, 10),
    ("skin_popup", "menu", 10, 10, 10, 10),
]

FILES = [("sketch.png", "image", 482), ("notes.txt", "text", 12), ("palette.gpl", "colors", 3), ("cover.jpg", "image", 1210),
         ("draft.psd", "layers", 8840), ("todo.md", "text", 4), ("brushes.zip", "archive", 2304)]
TABS = ["General", "Sound", "About"]
BRUSHES = ["Round", "Pencil", "Ink pen", "Marker", "Charcoal"]


def find_assets():
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    for d in (here, "examples/assets", "assets"):
        if os.path.isfile(os.path.join(d, "arrow_down.png")):
            return d
    return None


def load(folder, name):
    path = os.path.join(folder, name + ".png")
    try:
        return goome.Bitmap.load(path)
    except goome.GoomeError as e:
        print("cant load %s: %s" % (path, e), file=sys.stderr)
        return None


def paper(t):
    t.update(bg=0xFFEFE8DD, panel=0xFFFAF6F0, border=0x2E2B1E35, text=0xFF2B2233, text_dim=0xFF85798C, accent=0xFF7B4FD0,
             accent_text=0xFFFFFFFF, hover=0xFFE7DEF0, active=0xFFDACDEA, input_bg=0xFFEDE6DE, shadow=0x3A281838,
             radius=9, pad=10, gap=9, border_width=1, shadow_blur=24, anim_ms=120)


def by_col(x, y, col):
    if col == 2:
        return x[2] - y[2]
    p, q = (x[1], y[1]) if col == 1 else (x[0], y[0])
    return (p > q) - (p < q)


class Skinned(object):
    def __init__(self, g, u):
        self.g, self.u = g, u
        self.tab, self.snap, self.hints, self.fav, self.size, self.corners, self.autosave = 0, True, False, True, 1, True, False
        self.brush, self.sort_col, self.sort_desc, self.layers = 0, 2, True, True
        self.grid, self.outline, self.inspector = goome.Flag(True), goome.Flag(False), goome.Flag(True)
        self.bg_open, self.sketch_open = goome.Flag(True), goome.Flag(False)
        self.volume, self.copies, self.opacity, self.zoom = 64.0, 3.0, 0.8, 1.0
        self.split = goome.Split(0.5)
        self.win = goome.Window(610, 300, 330, 268)
        self.tint = 0xFFE0567A
        self.name = "cozy cat sketch"
        self.heart = self.app_bar = None
        self.running = True

    def dress(self):
        folder = find_assets()
        if folder is None:
            print("cant find examples/assets, run it from the repo folder", file=sys.stderr)
            return False
        t = self.u.theme
        paper(t)
        for i, name in enumerate(goome.ICON_NAMES):
            b = load(folder, name)
            if b is not None:
                t.icon[i] = b
        for field, name, l, top, r, bottom in SKINS:
            b = load(folder, name)
            if b is not None:
                setattr(t, field, (b, l, top, r, bottom))
        self.heart = load(folder, "heart")
        self.app_bar = load(folder, "titlebar_app")
        return True

    def menus(self):
        u = self.u
        with u.menubar() as shown:
            if not shown:
                return
            with u.menu("File") as m:
                if m:
                    u.menu_item("New", "Ctrl+N")
                    u.menu_item("Open", "Ctrl+O")
                    u.menu_separator()
                    if u.menu_item("Quit", "Ctrl+Q"):
                        self.running = False
            with u.menu("View") as m:
                if m:
                    u.menu_item("Grid", None, self.grid)
                    u.menu_item("Outline", None, self.outline)
                    with u.menu("Zoom") as z:
                        if z:
                            for label, v in (("50%", 0.5), ("100%", 1.0), ("200%", 2.0)):
                                if u.menu_item(label):
                                    self.zoom = v
                    if u.menu_item("Inspector", None, self.inspector):
                        self.win.h = self.win.h if self.win.h > 0 else 300

    def left_pane(self):
        u = self.u
        u.heading("Look")
        self.tab = u.tabs("tabs", TABS, self.tab)
        u.space(2)
        u.row(2)
        self.snap = u.checkbox("Snap to grid", self.snap)
        self.hints = u.checkbox("Show hints", self.hints)
        icons = {goome.ICON_CHECK: self.heart} if self.heart else {}
        with u.style(icons=icons, accent=0xFFE0567A):
            self.fav = u.checkbox("Favorite", self.fav)
        u.tooltip("this one gets a heart, pushed with goome_ui_push_icon")
        self.size = u.radio("Small", self.size, 0)
        u.same_line()
        self.size = u.radio("Medium", self.size, 1)
        u.same_line()
        self.size = u.radio("Large", self.size, 2)
        u.row(2)
        self.corners = u.toggle("Soft corners", self.corners)
        self.autosave = u.toggle("Autosave", self.autosave)
        self.volume = u.slider("Volume", self.volume, 0, 100, "%.0f%%")
        u.row(2)
        self.brush = u.combo("Brush", self.brush, BRUSHES)
        self.tint = u.color("Tint", self.tint)
        u.row(2)
        self.copies = u.number("Copies", self.copies, 1, "%.0f")
        self.opacity = u.drag_float("Opacity", self.opacity, 0.005, 0, 1, "%.2f")
        shown = u.collapsing("Layers", self.layers)
        if u.changed:
            self.layers = not self.layers
        if shown:
            with u.tree("Background", self.bg_open) as t:
                if t:
                    u.label("paper texture")
                    u.label("warm fill")
            with u.tree("Sketch", self.sketch_open) as t:
                if t:
                    u.label("lines")

    def right_pane(self):
        u = self.u
        u.heading("Files")
        order = list(range(len(FILES)))
        with u.table("files", 3, 0, goome.TABLE_SORTABLE | goome.TABLE_STRIPES) as t:
            if t:
                t.column("Name", 0)
                t.column("Kind", 90)
                t.column("KB", 70)
                s = t.sort(self.sort_col, self.sort_desc)
                self.sort_col, self.sort_desc = s.col, s.desc
                for i in range(1, len(order)):
                    for j in range(i, 0, -1):
                        c = by_col(FILES[order[j - 1]], FILES[order[j]], self.sort_col) if self.sort_col >= 0 else 0
                        if (c >= 0) if self.sort_desc else (c <= 0):
                            break
                        order[j], order[j - 1] = order[j - 1], order[j]
                for i in order:
                    name, kind, size = FILES[i]
                    t.row()
                    u.label(name)
                    t.next()
                    u.label(kind)
                    t.next()
                    u.label(str(size))
        u.space(4)
        self.name = u.input("Name", self.name, 64)
        u.progress(self.volume / 100, "exporting")
        u.row(3)
        if u.button("Export"):
            u.toast("exported, check your folder", 2500)
        u.tooltip("saves every layer as its own png")
        u.button("Share")
        if u.button("Inspector"):
            self.inspector.value = True

    def inspector_window(self):
        u = self.u
        self.win.open = self.inspector.value
        flags = goome.WIN_MOVE | goome.WIN_RESIZE | goome.WIN_COLLAPSE | goome.WIN_CLOSE
        with u.window("Inspector", self.win, flags) as shown:
            if shown:
                u.label("Brush settings")
                self.opacity = u.slider("Flow", self.opacity, 0, 1, "%.2f")
                self.snap = u.checkbox("Pressure", self.snap)
                u.separator()
                for i in range(14):
                    u.label("stroke %d, %d px" % (i + 1, 2 + i * 3))
        self.inspector.value = self.win.open

    def draw(self, first):
        u = self.u
        if first:
            u.toast("skin loaded, every icon is a png now", 4000)
        if self.app_bar:
            u.push_skin(goome.SKIN_TITLEBAR, (self.app_bar, 4, 4, 4, 3))
        u.app("Skinned", goome.APP_TITLEBAR | goome.APP_MENUBAR | goome.APP_STATUSBAR | goome.APP_NO_PAD)
        if self.app_bar:
            u.pop()
        self.menus()
        u.split("main", self.split)
        self.left_pane()
        u.split_next()
        self.right_pane()
        u.split_end()
        u.statusbar("%d files, zoom %.0f%%, every glyph and part here is a png from examples/assets" % (len(FILES), self.zoom * 100))
        u.app_end()
        if self.inspector:
            self.inspector_window()

    def run(self):
        g, u = self.g, self.u
        test = g.backend_name.startswith("test")
        pace = goome.Pacer(60)
        first = True
        while self.running:
            for ev in g.events(pace.wait() if test or u.animating else 500):
                if ev.type in (goome.QUIT, goome.CLOSE):
                    self.running = False
                u.feed(ev)
            if not self.running:
                break
            if u.begin(0) is None:
                continue
            self.draw(first)
            first = False
            u.end()


def main():
    try:
        g = goome.open("Skinned", mode="window", width=980, height=680, min_width=760, min_height=520,
                       window_flags=goome.WINDOW_RESIZABLE | goome.WINDOW_CENTER)
    except goome.GoomeError as e:
        print("cant open a window: %s" % e, file=sys.stderr)
        return 1
    with g, g.ui() as u:
        s = Skinned(g, u)
        if not s.dress():
            return 1
        s.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
