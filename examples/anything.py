import sys

import goome

RETRO, SOFT, HUD, DENSE, NLOOK = range(5)
TABS = ["Play", "Stats", "Gear"]
MODES = ["Story", "Arena", "Sandbox"]
STARTS = ["theme_make", "Dark", "Light", "Midnight", "Paper", "Mint", "High contrast", "Rose"]
CODE = ["t = ui.theme.copy()", "t.make(0xFF8B5CF6, dark=True, radius=12)", "ui.push_theme(t)"]
NAMES = ["guest_01", "Mia", "NOVA-7", "render_pass_b"]


class Card(object):
    def __init__(self, i):
        self.sound, self.online, self.level = True, i != DENSE, 1 + (i & 1)
        self.volume, self.mode, self.tab = 35 + i * 12, i % 3, i % 3
        self.name = NAMES[i] if i < NLOOK else "sev"


def sprite(w, h, draw):
    c = goome.Canvas.new(w, h)
    draw(c)
    return goome.Bitmap.wrap(c.pixels.tobytes(), w, h)


def diamond(c, cx, cy, r, col):
    c.poly([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], col)


def term_icons():
    def arrow_down(c):
        c.rect(1, 3, 10, 2, 0xFFFFFFFF)
        c.rect(3, 5, 6, 2, 0xFFFFFFFF)
        c.rect(5, 7, 2, 2, 0xFFFFFFFF)

    def arrow_right(c):
        c.rect(3, 1, 2, 10, 0xFFFFFFFF)
        c.rect(5, 3, 2, 6, 0xFFFFFFFF)
        c.rect(7, 5, 2, 2, 0xFFFFFFFF)

    def hollow(c):
        c.rect(0, 0, 12, 12, 0xFFFFFFFF)
        c.rect(3, 3, 6, 6, 0xFF000000)

    def box(c):
        c.rect(0, 0, 12, 12, 0xFF1FA64C)
        c.rect(1, 1, 10, 10, 0xFF031408)

    return [
        sprite(12, 12, lambda c: c.rect(2, 2, 8, 8, 0xFFFFFFFF)),
        sprite(10, 10, lambda c: c.rect(2, 2, 6, 6, 0xFFFFFFFF)),
        sprite(12, 12, lambda c: c.rect(0, 0, 12, 12, 0xFFFFFFFF)),
        sprite(12, 12, arrow_down),
        sprite(12, 12, arrow_right),
        sprite(12, 12, hollow),
        sprite(12, 12, box),
    ]


def hud_art():
    def ring(c):
        diamond(c, 10, 10, 9, 0xFFFFFFFF)
        diamond(c, 10, 10, 5.5, 0xFF0A1A24)

    def cross(c):
        c.line(2, 2, 10, 10, 1.6, 0xFFFFFFFF)
        c.line(10, 2, 2, 10, 1.6, 0xFFFFFFFF)

    def check_box(c):
        c.rect(0, 0, 18, 18, 0xC0081C28)
        c.frame(0.5, 0.5, 17, 17, 1.2, 0xFF39E1FF)

    def radio_box(c):
        diamond(c, 9, 9, 8.6, 0xFF39E1FF)
        diamond(c, 9, 9, 7.2, 0xF0081C28)

    def frame(c):
        c.rect(0, 0, 24, 24, 0xA00A1622)
        c.frame(0.5, 0.5, 23, 23, 1, 0x5539E1FF)
        c.rect(0, 0, 8, 2, 0xFF39E1FF)
        c.rect(0, 0, 2, 8, 0xFF39E1FF)
        c.rect(16, 22, 8, 2, 0xFF39E1FF)
        c.rect(22, 16, 2, 8, 0xFF39E1FF)

    def plate(c):
        c.poly([6, 0, 24, 0, 24, 18, 18, 24, 0, 24, 0, 6], 0xC0103346)
        c.poly([6.8, 1, 23, 1, 23, 17.6, 17.6, 23, 1, 23, 1, 6.8], 0xFF0D2533)
        c.line(6, 0.5, 23.5, 0.5, 1, 0xFF39E1FF)
        c.line(0.5, 6, 0.5, 23.5, 1, 0x9939E1FF)
        c.line(0.5, 6, 6, 0.5, 1, 0xFF39E1FF)

    art = [
        sprite(16, 16, lambda c: diamond(c, 8, 8, 6, 0xFFFFFFFF)),
        sprite(16, 16, lambda c: diamond(c, 8, 8, 5, 0xFFFFFFFF)),
        sprite(20, 20, ring),
        sprite(12, 12, lambda c: c.triangle(1, 3, 11, 3, 6, 10, 0xFFFFFFFF)),
        sprite(12, 12, lambda c: c.triangle(3, 1, 10, 6, 3, 11, 0xFFFFFFFF)),
        sprite(12, 12, cross),
        sprite(18, 18, check_box),
        sprite(18, 18, radio_box),
    ]
    tab = sprite(24, 24, lambda c: c.poly([5, 0, 24, 0, 24, 19, 19, 24, 0, 24, 0, 5], 0xFF39E1FF))
    return art, sprite(24, 24, frame), sprite(24, 24, plate), tab


def retro(w):
    t = goome.Theme.preset("dark")
    t.update(bg=0xFF000000, panel=0xFF020A04, border=0xFF1F7A3A, text=0xFF3DFF7A, text_dim=0xFF1FA64C,
             accent=0xFF3DFF7A, accent_text=0xFF001A08, hover=0xFF0A2A14, active=0xFF124422, input_bg=0xFF031408,
             shadow=0x5533FF77, shadow_blur=18, shadow_y=0,
             radius=0, check_radius=0, tip_radius=0, border_width=1, anim_ms=0, ease="linear",
             font=w.mono, font_mono=w.mono, font_heading=w.mono, font_size=15, heading_size=17,
             caret_w=9, caret=0xB03DFF7A, select=0x663DFF7A, knob=0xFF3DFF7A, focus_w=1, focus_gap=2,
             toggle_w=34, toggle_h=18, slider_track=2, knob_size=6)
    term = w.term
    t.icon["check"], t.icon["radio_dot"] = term[0], term[1]
    t.icon["slider_knob"], t.icon["toggle_knob"] = term[2], term[5]
    t.icon["arrow_down"], t.icon["arrow_right"] = term[3], term[4]
    t.skin_checkbox = t.skin_radio = t.skin_toggle = (term[6], 3)
    return t


def soft():
    t = goome.Theme.make(0xFF2F7BF6, dark=False, radius=20)
    t.update(bg=0xFFF2F4F8, panel=0xFFFFFFFF, border=0x14000000, input_bg=0xFFEEF1F6, hover=0xFFE3E8F0,
             font_size=17, heading_size=22, pad=14, gap=10, item_h=44, tab_h=42, win_title_h=48,
             check_size=22, check_radius=11, toggle_w=46, toggle_h=28, slider_h=28, knob_size=12, slider_track=8,
             shadow=0x22203060, shadow_blur=34, shadow_y=10, focus_w=3, focus_gap=4,
             anim_ms=260, hover_ms=200, press_ms=160, popup_ms=320, ease="back")
    return t


def hud(w):
    t = goome.Theme.preset("dark")
    t.update(bg=0x00000000, panel=0x8A06121C, border=0x6639E1FF, text=0xFFE6FBFF, text_dim=0xFF7FC4D6,
             accent=0xFF39E1FF, accent_text=0xFF041820, hover=0xFF12384A, active=0xFF1A4C63, input_bg=0xB0081C28,
             shadow=0x5539E1FF, shadow_blur=26, shadow_y=0, radius=0, check_radius=0, tip_radius=0,
             font_size=16, heading_size=22, item_h=38, win_title_h=42,
             knob=0xFF39E1FF, knob_size=9, slider_track=4, check_size=18, ease="out", anim_ms=160)
    if w.bold is not None:
        t.font = w.bold
    t.skin_panel = (w.frame, 8)
    t.skin_button = (w.plate, 8)
    t.skin_input = (w.plate, 8)
    t.skin_tab = (w.tab, 7)
    t.skin_checkbox = (w.hud[6], 3)
    t.skin_radio = (w.hud[7], 0)
    t.icon["check"], t.icon["radio_dot"] = w.hud[0], w.hud[1]
    t.icon["slider_knob"] = t.icon["toggle_knob"] = w.hud[2]
    t.icon["arrow_down"], t.icon["arrow_right"], t.icon["close"] = w.hud[3], w.hud[4], w.hud[5]
    return t


def dense():
    t = goome.Theme.preset("dark")
    t.update(bg=0xFF1B1C1F, panel=0xFF232428, border=0xFF34363C, text=0xFFD5D7DC, text_dim=0xFF8A8F98,
             accent=0xFF4C8DF6, accent_text=0xFFFFFFFF, hover=0xFF2E3036, active=0xFF383B42, input_bg=0xFF1A1B1E,
             shadow=0x66000000, shadow_blur=10, shadow_y=3, radius=3, check_radius=2, tip_radius=3,
             font_size=12, heading_size=13, pad=6, gap=6, item_h=24, tab_h=24, win_title_h=26,
             check_size=13, toggle_w=26, toggle_h=14, slider_h=14, knob_size=5, slider_track=3,
             scroll_w=3, focus_w=1, focus_gap=1, anim_ms=70, tip_pad_x=6, tip_pad_y=4)
    return t


def widgets(u, c, big, focus):
    c.tab = u.tabs("tabs", TABS, c.tab)
    u.heading("Player one")
    if focus:
        u.set_focus()
    c.name = u.input("Name", c.name, 48)
    c.volume = u.slider("Volume", c.volume, 0, 100, "%.0f")
    u.row(2)
    c.sound = u.checkbox("Sound", c.sound)
    c.online = u.toggle("Online", c.online)
    c.level = u.radio("Easy", c.level, 0)
    u.same_line()
    c.level = u.radio("Normal", c.level, 1)
    u.same_line()
    c.level = u.radio("Hard", c.level, 2)
    if not big:
        c.mode = u.combo("Mode", c.mode, MODES)
        u.progress(c.volume / 100, "loading")
    u.row(2)
    u.button("Start")
    u.button("Quit")


def scene(u, x, y, w, h):
    c = u.canvas
    if c is None:
        return
    c.rrect_grad(x, y, w, h, 14, 0xFF1B2747, 0xFFE0794F)
    c.circle(x + w * 0.72, y + h * 0.62, 46, 0xFFFFC27A)
    c.poly([x, y + h, x, y + h * 0.7, x + w * 0.22, y + h * 0.56, x + w * 0.45, y + h * 0.74, x + w * 0.7, y + h * 0.6,
            x + w, y + h * 0.72, x + w, y + h], 0xFF1A1F38)
    c.poly([x, y + h, x, y + h * 0.86, x + w * 0.3, y + h * 0.8, x + w * 0.62, y + h * 0.9, x + w, y + h * 0.82, x + w, y + h],
           0xFF0D1022)


class World(object):
    def __init__(self, u):
        self.mono = goome.Font.system("monospace")
        self.bold = goome.Font.system("sans-serif:bold")
        self.zoom, self.focus_once, self.start = 1.0, True, 0
        self.password, self.code, self.server = "hunter22", "", "eu-west-2"
        self.term = term_icons()
        self.hud, self.frame, self.plate, self.tab = hud_art()
        self.look = [retro(self), soft(), hud(self), dense()]
        for t in self.look:
            if t.font is None:
                t.font = u.theme.font
        self.cards = [Card(i) for i in range(NLOOK + 1)]

    def close(self):
        for f in (self.mono, self.bold):
            if f is not None:
                f.close()


def look(u, w, k, title, x, y, ww, hh):
    u.push_theme(w.look[k])
    u.scale(w.zoom)
    with u.id(title):
        with u.window(title, goome.Window(x, y, ww, hh), 0) as shown:
            if shown:
                widgets(u, w.cards[k], k in (SOFT, HUD), k == RETRO and w.focus_once)
                if k == RETRO:
                    w.focus_once = False
    u.pop(1)


def simple(u, w, x, y, ww, hh):
    t = u.theme.copy()
    if w.start == 0:
        t.make(0xFF8B5CF6, dark=True, radius=12)
    else:
        t.preset(w.start - 1)
    u.push_theme(t)
    u.scale(w.zoom)
    with u.window("The simple path", goome.Window(x, y, ww, hh), 0) as shown:
        if shown:
            u.wrapped("three lines, one accent color, dark or light and a corner radius:")
            with u.style(font=w.mono, font_size=12):
                for line in CODE:
                    u.label(line)
            u.space(4)
            w.start = u.combo("Start from", w.start, STARTS)
            w.zoom = u.slider("UI size", w.zoom, 0.8, 1.3, "%.2fx")
            u.separator()
            c = w.cards[NLOOK]
            u.row(2)
            c.name = u.input("Name", c.name, 48)
            w.password = u.password("Password", w.password, "8 letters or more", goome.INPUT_ENTER_RETURNS, 32)
            if u.entered:
                u.toast("logged in", 1500)
            u.row(2)
            w.code = u.input_ex("Room code", w.code, goome.INPUT_NUMBER, "numbers only", 8)
            w.server = u.input_ex("Server", w.server, goome.INPUT_READONLY, None, 16)
            u.row(2)
            c.sound = u.checkbox("Sound", c.sound)
            c.online = u.toggle("Online", c.online)
            u.separator()
            u.label("one push changes one widget")
            u.row(3)
            with u.style(radius=0):
                u.button("Square")
            with u.style(radius=99, align="left"):
                u.button("Pill")
            with u.style(accent=0xFFF59E0B, check_size=24, check_radius=12):
                c.sound = u.checkbox("Big", c.sound)
            u.separator()
            u.label("every preset, same widgets")
            for i in range(goome.PRESET_COUNT):
                p = u.theme.copy().preset(i)
                with u.style(p), u.id(STARTS[i + 1]):
                    u.row(3)
                    u.badge(STARTS[i + 1], 0)
                    u.button("Open")
                    u.toggle("##t", i & 1)
    u.pop(1)


def main():
    try:
        g = goome.open("goome can look like anything", mode="window", width=1320, height=940, min_width=900, min_height=600,
                       window_flags=goome.WINDOW_RESIZABLE | goome.WINDOW_CENTER)
    except goome.GoomeError as e:
        print("cant open a window: %s" % e, file=sys.stderr)
        return 1
    with g, g.ui() as u:
        w = World(u)
        u.config.tip_delay_ms = 300
        u.config.cursor["button"] = "hand"
        u.config.bind("select_all", "ctrl+a super+a ctrl+l")
        test = g.backend_name.split()[0] == "test"
        pace = goome.Pacer(60)
        running = True
        while running:
            for ev in g.events(pace.wait() if test or u.animating else 500):
                if ev.type in (goome.QUIT, goome.CLOSE):
                    running = False
                u.feed(ev)
            if not running:
                break
            if u.begin(0) is None:
                continue
            with u.app("anything", goome.APP_NO_PAD):
                scene(u, 452, 496, 420, 428)
            look(u, w, RETRO, "> retro terminal_", 16, 16, 420, 0)
            look(u, w, SOFT, "Soft and round", 452, 16, 420, 0)
            look(u, w, HUD, "GAME HUD", 476, 520, 372, 0)
            look(u, w, DENSE, "dense pro tool", 16, 456, 420, 0)
            simple(u, w, 888, 16, 416, 908)
            u.end()
        w.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
