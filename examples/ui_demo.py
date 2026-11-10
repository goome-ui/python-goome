import os
import sys
from array import array

import goome

HERE = os.path.dirname(os.path.abspath(__file__))
FRUITS = ["Mango", "Banana", "Cherry", "Kiwi", "Apple", "Lemon", "Grape", "Fig", "Dragonfruit", "Pear"]
TABS = ["Widgets", "Images", "Theme", "About"]


def make_gradient():
    px = array("I", [0] * (128 * 128))
    for y in range(128):
        for x in range(128):
            r = 0x2A + x * (0x6F - 0x2A) // 127
            g = 0x40 + y * (0xDC - 0x40) // 127
            b = 0x9A - (x + y) * 0x50 // 254
            px[y * 128 + x] = 0xFF000000 | r << 16 | g << 8 | b
    return goome.Bitmap.from_argb(px, 128, 128)


def load_logo():
    for p in ("docs/logo.png", os.path.join(HERE, "..", "docs", "logo.png")):
        try:
            return goome.Bitmap.load(p), True
        except goome.GoomeError:
            pass
    return make_gradient(), False


def plural(n, none, one, many):
    return none if n == 0 else one if n == 1 else many % n


class Demo(object):
    def __init__(self, g, u):
        self.g, self.u = g, u
        m = g.monitors()
        a = m[0].area if m else goome.Rect(0, 0, 1280, 720)
        self.logo, self.have_logo = load_logo()
        self.main = goome.Window(a.x + 40, a.y + 40, 440, 620)
        self.stats = goome.Window(a.x + 500, a.y + 40, 280, 0)
        self.tab, self.clicks, self.grid, self.wifi, self.notify, self.mode = 0, 0, True, True, False, 1
        self.count, self.fruit, self.picked, self.more = 42, 2, -1, True
        self.light, self.own_accent, self.solid, self.always, self.img_clicks = 0, False, False, False, 0
        self.volume, self.radius, self.anim = 0.65, 10.0, 120.0
        self.highlight, self.accent = 0xFF4FA3FF, 0xFF6FDC5F
        self.name, self.search = "goome", ""
        self.fps, self.frame_ms = 0.0, 0.0
        self.running = True

    def set_theme(self):
        t = self.u.theme
        t.light() if self.light else t.dark()
        if self.own_accent:
            t.accent = self.accent
        t.radius, t.anim_ms = self.radius, self.anim
        if self.solid:
            t.panel = t.panel | 0xFF000000

    def widgets(self):
        u = self.u
        u.heading("Buttons")
        u.row(3)
        if u.button("Click me"):
            self.clicks += 1
        if u.button("Reset"):
            self.clicks = 0
        u.button("Hover me")
        u.tooltip("hi :)")
        u.label(plural(self.clicks, "not clicked yet", "clicked once", "clicked %d times"))
        u.separator()
        u.heading("Switches")
        self.grid = u.checkbox("Show grid", self.grid)
        u.same_line()
        self.notify = u.checkbox("Notifications", self.notify)
        self.wifi = u.toggle("Wi-Fi", self.wifi)
        for i, name in enumerate(("Small", "Medium", "Large")):
            if i:
                u.same_line()
            self.mode = u.radio(name, self.mode, i)
        u.separator()
        u.heading("Values")
        self.volume = u.slider("Volume", self.volume, 0, 1, "%.2f")
        self.count = u.slider_int("Count", self.count, 0, 100)
        u.progress(self.volume, "%d%%" % int(self.volume * 100 + 0.5))
        u.progress(-1)
        u.row(2)
        self.name = u.input("Name", self.name, 64)
        self.search = u.input("Search", self.search, 64)
        self.fruit = u.combo("Fruit", self.fruit, FRUITS)
        self.highlight = u.color("Highlight", self.highlight)
        self.more = u.collapsing("More stuff", self.more)
        if self.more:
            u.wrapped("a long list so theres something to scroll. pick one, it shows up under it.")
            with u.scroll_begin("list", 150):
                for i in range(30):
                    if u.selectable("Item %d" % (i + 1), self.picked == i):
                        self.picked = i
            u.label("picked item %d" % (self.picked + 1) if self.picked >= 0 else "nothing picked")

    def images(self):
        u = self.u
        u.heading("docs/logo.png" if self.have_logo else "Generated gradient")
        for i, r in enumerate((18, 60, 0)):
            if i:
                u.same_line()
            u.image(self.logo, 120, 120, r)
        u.label("image buttons")
        for i in range(4):
            if i:
                u.same_line()
            if u.image_button("img%d" % i, self.logo, 56, 56):
                self.img_clicks += 1
        u.label(plural(self.img_clicks, "no image clicks yet", "one image click", "%d image clicks"))
        u.image(self.logo, 0, 90, 10)

    def theme(self):
        u = self.u
        u.heading("Theme")
        was = self.light
        self.light = u.radio("Dark", self.light, 0)
        u.same_line()
        self.light = u.radio("Light", self.light, 1)
        ch = self.light != was
        self.accent = u.color("Accent", self.accent)
        if u.changed:
            self.own_accent = ch = True
        self.radius = u.slider("Corner radius", self.radius, 0, 20, "%.0f px")
        ch |= u.changed
        self.anim = u.slider("Animation", self.anim, 0, 400, "%.0f ms")
        ch |= u.changed
        self.solid = u.toggle("Solid panels", self.solid)
        ch |= u.changed
        if u.button("Reset theme"):
            self.light, self.own_accent, self.radius, self.anim, self.solid, self.accent = 0, False, 10.0, 120.0, False, 0xFF6FDC5F
            ch = True
        if ch:
            self.set_theme()
        if not self.own_accent:
            self.accent = u.theme.accent

    def about(self):
        u = self.u
        u.heading("About")
        u.wrapped("made with goome. try clicking next to this window, your desktop still gets it.")
        u.label("goome %s on %s" % (goome.VERSION, self.g.backend_name))
        u.label("%.0f fps, %.2f ms a frame" % (self.fps, self.frame_ms))
        if not self.stats.open and u.button("Show stats"):
            self.stats.open = True

    def draw(self):
        u = self.u
        flags = goome.WIN_MOVE | goome.WIN_RESIZE | goome.WIN_COLLAPSE
        with u.window("goome ui", self.main, flags) as shown:
            if shown:
                self.tab = u.tabs("tabs", TABS, self.tab)
                with u.id(TABS[self.tab]), u.scroll_begin("page"):
                    (self.widgets, self.images, self.theme, self.about)[self.tab]()
        with u.window("Stats", self.stats, flags | goome.WIN_CLOSE) as shown:
            if shown:
                u.label("%.0f fps" % self.fps)
                u.label("%.2f ms a frame" % self.frame_ms)
                u.progress(self.frame_ms / 16.7, "%d%% of a 60 fps frame" % int(self.frame_ms * 100 / 16.7 + 0.5))
                self.always = u.toggle("Redraw every frame", self.always)
                if u.button("Quit"):
                    self.running = False

    def run(self):
        g, u = self.g, self.u
        test = g.backend_name.split()[0] == "test"
        spent = tframes = 0
        acc_ms, acc_n, fps_n = 0.0, 0, 0
        fps_t = goome.now_ms()
        pace = goome.Pacer(60)
        dirty = True
        while self.running:
            busy = dirty or self.always or test or u.animating
            for ev in g.events(pace.wait() if busy else 500):
                if ev.type == goome.QUIT:
                    self.running = False
                u.feed(ev)
                dirty = True
            if not self.running:
                break
            if not (dirty or self.always or test or u.animating):
                continue
            dirty = False
            t0 = goome.now_ms()
            if u.begin(0) is None:
                continue
            self.draw()
            u.end()
            t1 = goome.now_ms()
            spent += t1 - t0
            tframes += 1
            acc_ms += t1 - t0
            acc_n += 1
            fps_n += 1
            if t1 - fps_t >= 500:
                self.fps = fps_n * 1000.0 / (t1 - fps_t)
                self.frame_ms = acc_ms / acc_n
                fps_t, fps_n, acc_ms, acc_n = t1, 0, 0.0, 0
        if tframes:
            print("%d frames, %.2f ms a frame" % (tframes, spent / float(tframes)))
        self.logo.close()


def main():
    try:
        g = goome.open("goome ui", no_capture=True)
    except goome.GoomeError as e:
        print("cant open an overlay: %s" % e, file=sys.stderr)
        return 1
    with g, g.ui() as u:
        Demo(g, u).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
