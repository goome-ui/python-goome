import math
import sys

import goome

SWATCHES = [0xFF6FDC5F, 0xFF3FC8B4, 0xFF4FB3F7, 0xFF7C8CFF, 0xFFB57CFF, 0xFFFF6FA8, 0xFFFF7A59, 0xFFFFB443, 0xFFE8D85A]
NODES = [("Noise", "seed 42", 0xFFB57CFF, 20, 40), ("Blur", "radius 6", 0xFF4FB3F7, 240, 120), ("Output", "1280x720", 0xFFFF7A59, 460, 40)]
HZ = ["60", "150", "400", "1k", "2.4k", "6k", "15k"]
EQ = [0.7, 0.62, 0.45, 0.5, 0.58, 0.68, 0.74]
KEYS = [1.2, 2.6, 5.0, 6.4, 7.7]


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def snap(v, step):
    return math.floor(v / step + 0.5) * step


def fade(c, k):
    return int(((c >> 24) & 255) * clamp(k, 0, 1) + 0.5) << 24 | (c & 0xFFFFFF)


def mix(a, b, t):
    out = 0
    for s in (0, 8, 16, 24):
        x, y = (a >> s) & 255, (b >> s) & 255
        out |= int(x + (y - x) * clamp(t, 0, 1) + 0.5) << s
    return out


def text_at(c, font, size, x, cy, s, col, center=False):
    w, h = goome.measure(s, size, font)
    if h <= 0:
        h = goome.line_height(size, font)
    c.font_text(font, size, x - w / 2 if center else x, int(cy - h / 2 + 0.5), s, col)


def knob(u, name, start, scale, fmt):
    v = u.store(name, 2)
    if not v[1]:
        v[0], v[1] = start, 1
    it = u.custom(name, 92, 112, goome.ITEM_DRAG_Y | goome.ITEM_FOCUSABLE)
    key = it.key & 0xFF
    if it.held:
        v[0] = clamp(v[0] - it.dy / 180, 0, 1)
    if key in (goome.K_UP, goome.K_RIGHT):
        v[0] = clamp(v[0] + 0.05, 0, 1)
    if key in (goome.K_DOWN, goome.K_LEFT):
        v[0] = clamp(v[0] - 0.05, 0, 1)
    if it.double_clicked:
        v[0] = start
    u.tooltip("drag up or down, arrows work too, double click resets it")

    th = u.theme
    c = u.canvas
    if c is None:
        return
    cx, cy, r, ri = it.x + it.w / 2, it.y + 40, 31, 21
    a0, a1 = 2.35619449, 7.06858347
    at = a0 + (a1 - a0) * v[0]
    on = it.hovered or it.held
    if on:
        c.circle(cx, cy, r + 9, fade(th.accent, 0.16 if it.held else 0.09))
    c.arc(cx, cy, r, 6, a0, a1, fade(th.text, 0.09))
    if v[0] > 0.004:
        c.arc(cx, cy, r, 6, a0, at, th.accent)
    c.shadow(cx - ri, cy - ri + 4, 2 * ri, 2 * ri, ri, 10, 0x70000000)
    c.rrect_grad(cx - ri, cy - ri, 2 * ri, 2 * ri, ri, 0xFF3A3F49, 0xFF24272E)
    c.ring(cx, cy, ri - 0.5, 1, 0x1AFFFFFF)
    px, py = cx + math.cos(at) * (ri - 7), cy + math.sin(at) * (ri - 7)
    c.line(cx + math.cos(at) * (ri - 15), cy + math.sin(at) * (ri - 15), px, py, 2.6, th.text if on else mix(th.text_dim, th.text, 0.5))
    text_at(c, th.font, 14, cx, it.y + 84, fmt % (v[0] * scale), th.text, True)
    text_at(c, th.font, 12.5, cx, it.y + 103, name, th.text_dim, True)


def timeline(u, ox, oy):
    t = u.store("playhead", 2)
    if not t[1]:
        t[0], t[1] = 2.4, 1
    th = u.theme
    tr = u.custom("track", 0, 92, goome.ITEM_NO_HIT)
    x0, x1, secs = tr.x + 14, tr.x + tr.w - 14, 10
    per = (x1 - x0) / secs
    ly0, ly1 = tr.y + 34, tr.y + 61
    c = u.canvas
    if c is None:
        return
    c.rrect(tr.x, tr.y, tr.w, tr.h, 10, 0xFF1E2127)
    c.rrect_line(tr.x, tr.y, tr.w, tr.h, 10, 1, th.border)
    for i in range(21):
        x = x0 + i * per / 2
        c.rect(x - 0.5, tr.y + (18 if i % 2 else 12), 1, 5 if i % 2 else 11, fade(th.text, 0.14 if i % 2 else 0.28))
        if not i % 2 and i < 20:
            c.font_text(th.font, 11, x + 4, tr.y + 9, "%ds" % (i // 2), th.text_dim)
    for start, length, y, col, name, ink in ((0.4, 3.6, ly0, 0xFFB57CFF, "intro.wav", 0xFFE6DAFF), (3.1, 5.3, ly1, 0xFF4FB3F7, "drums.wav", 0xFFD6EEFF)):
        c.rrect(x0 + start * per, y, length * per, 22, 6, fade(col, 0.3))
        c.rrect_line(x0 + start * per, y, length * per, 22, 6, 1, fade(col, 0.62))
        c.font_text(th.font, 12, x0 + start * per + 9, y + 4, name, ink)

    u.pos(x0 + t[0] * per - 9 - ox, tr.y + 4 - oy)
    with u.style(radius=6):
        hd = u.custom("handle", 18, tr.h - 8, goome.ITEM_DRAG_X | goome.ITEM_FOCUSABLE)
    key = hd.key & 0xFF
    if hd.held and per > 0:
        t[0] = clamp(t[0] + hd.dx / per, 0, secs)
    if key in (goome.K_LEFT, goome.K_RIGHT):
        t[0] = clamp(snap(t[0], 0.5) + (0.5 if key == goome.K_RIGHT else -0.5), 0, secs)
    if hd.released:
        t[0] = snap(t[0], 0.1)
    u.tooltip("this one only moves sideways")
    hx = x0 + t[0] * per

    c = u.canvas
    if c is None:
        return
    for k in KEYS:
        kx, ky, d = x0 + k * per, ly1 + 11, 4.5
        c.poly([(kx, ky - d), (kx + d, ky), (kx, ky + d), (kx - d, ky)], th.accent if k <= t[0] else 0xFFD6EEFF)
    c.rect(x0, tr.y + tr.h - 5, hx - x0, 2, fade(th.accent, 0.7))
    on = hd.hovered or hd.held
    c.rect(hx - 1, tr.y + 20, 2, tr.h - 25, th.accent)
    hc = mix(th.accent, 0xFFFFFFFF, 0.25) if on else th.accent
    c.shadow(hx - 8, tr.y + 7, 16, 13, 4, 6, 0x60000000)
    c.rrect(hx - 8, tr.y + 5, 16, 13, 4, hc)
    c.triangle(hx - 6, tr.y + 17, hx + 6, tr.y + 17, hx, tr.y + 23, hc)
    s = "%.1fs" % t[0]
    w = goome.measure(s, 11.5, th.font)[0]
    bx = clamp(hx + 12, tr.x + 6, tr.x + tr.w - w - 18)
    c.rrect(bx, tr.y + 4, w + 10, 16, 5, fade(th.accent, 0.18))
    c.font_text(th.font, 11.5, bx + 5, tr.y + 5, s, th.accent)


def swatch_strip(u, sel):
    for i, col in enumerate(SWATCHES):
        if i:
            u.same_line()
        it = u.custom("sw%d" % i, 34, 34, goome.ITEM_FOCUSABLE)
        if it.clicked:
            sel = i
        c = u.canvas
        if c is None:
            continue
        lift = 2 if it.hovered and not it.held else 0
        if i == sel:
            c.rrect_line(it.x - 4, it.y - 4 - lift, it.w + 8, it.h + 8, 13, 2, 0xFFFFFFFF)
        c.shadow(it.x, it.y + 3 - lift, it.w, it.h, 9, 8 + lift * 2, 0x66000000)
        c.rrect_grad(it.x, it.y - lift, it.w, it.h, 9, mix(col, 0xFFFFFFFF, 0.12), mix(col, 0xFF000000, 0.12))
        c.rrect_line(it.x, it.y - lift, it.w, it.h, 9, 1, 0x26FFFFFF)
        if i == sel:
            cx, cy = it.x + it.w / 2, it.y + it.h / 2 - lift
            c.line(cx - 6, cy, cx - 2, cy + 4, 2.4, 0xE0141618)
            c.line(cx - 2, cy + 4, cx + 6.5, cy - 5, 2.4, 0xE0141618)
    return sel


def faders(u):
    v = u.store("eq", 8)
    if not v[7]:
        for i, e in enumerate(EQ):
            v[i] = e
        v[7] = 1
    for i, hz in enumerate(HZ):
        if i:
            u.same_line()
        it = u.custom("eq%d" % i, 28, 138, goome.ITEM_DRAG_Y | goome.ITEM_FOCUSABLE)
        top, bot = it.y + 8, it.y + it.h - 26
        size = bot - top
        key = it.key & 0xFF
        knob_y = top + (1 - v[i]) * size
        if it.pressed and not knob_y - 8 <= it.my <= knob_y + 8:
            v[i] = clamp(1 - (it.my - top) / size, 0, 1)
        elif it.held:
            v[i] = clamp(v[i] - it.dy / size, 0, 1)
        if key in (goome.K_UP, goome.K_DOWN):
            v[i] = clamp(v[i] + (0.05 if key == goome.K_UP else -0.05), 0, 1)
        if it.double_clicked:
            v[i] = 0.5
        th = u.theme
        c = u.canvas
        if c is None:
            continue
        cx, ty, mid = it.x + it.w / 2, top + (1 - v[i]) * size, top + size / 2
        c.rrect(cx - 2, top, 4, size, 2, fade(th.text, 0.09))
        c.rect(cx - 6, mid - 0.5, 12, 1, fade(th.text, 0.2))
        c.rrect(cx - 2, min(ty, mid), 4, abs(mid - ty), 2, th.accent)
        on = it.hovered or it.held
        c.shadow(cx - 11, ty - 3, 22, 10, 5, 6, 0x70000000)
        c.rrect_grad(cx - 11, ty - 5, 22, 10, 5, 0xFFFFFFFF if on else 0xFFE4E7EC, 0xFFDDE1E7 if on else 0xFFB9BEC7)
        c.rect(cx - 5, ty - 0.5, 10, 1, fade(th.accent, 0.9))
        text_at(c, th.font, 11, cx, it.y + it.h - 9, hz, th.text if on else th.text_dim, True)


def xy_pad(u):
    v = u.store("xy", 3)
    if not v[2]:
        v[0], v[1], v[2] = 0.62, 0.38, 1
    it = u.custom("xy", 0, 138, goome.ITEM_DRAG_X | goome.ITEM_DRAG_Y)
    if it.held:
        v[0] = clamp((it.mx - it.x - 8) / (it.w - 16), 0, 1)
        v[1] = clamp((it.my - it.y - 8) / (it.h - 16), 0, 1)
    th = u.theme
    c = u.canvas
    if c is None:
        return
    px, py = it.x + 8 + v[0] * (it.w - 16), it.y + 8 + v[1] * (it.h - 16)
    c.rrect(it.x, it.y, it.w, it.h, 12, 0xFF1B1E23)
    c.rrect_grad(it.x, it.y, it.w, it.h, 12, fade(th.accent, 0), fade(th.accent, 0.1), True)
    for i in (1, 2, 3):
        c.rect(it.x + it.w * i / 4, it.y + 6, 1, it.h - 12, 0x0FFFFFFF)
        c.rect(it.x + 6, it.y + it.h * i / 4, it.w - 12, 1, 0x0FFFFFFF)
    c.rect(px - 0.5, it.y + 4, 1, it.h - 8, fade(th.accent, 0.35))
    c.rect(it.x + 4, py - 0.5, it.w - 8, 1, fade(th.accent, 0.35))
    c.circle(px, py, 18 if it.held else 14, fade(th.accent, 0.22 if it.held else 0.14))
    c.circle(px, py, 7, th.accent)
    c.ring(px, py, 7, 2, 0xFFFFFFFF)
    c.font_text(th.font, 11.5, it.x + 12, it.y + 9, "cutoff %.2f  res %.2f" % (v[0], 1 - v[1]), th.text_dim)
    c.rrect_line(it.x, it.y, it.w, it.h, 12, 1, fade(th.accent, 0.6) if it.hovered or it.held else th.border)


def node_box(c, th, node, it, x, y, top):
    name, info, col = node[:3]
    w, h = it.w, it.h
    c.shadow(x, y + (10 if top else 5), w, h, 12, 22 if top else 12, 0x90000000 if top else 0x70000000)
    c.rrect(x, y, w, h, 12, 0xFF2A2E36)
    c.rrect_grad(x, y, w, 26, (12, 12, 0, 0), mix(col, 0xFF2A2E36, 0.25), mix(col, 0xFF2A2E36, 0.55), True)
    c.circle(x + 15, y + 13, 4, 0xFFFFFFFF)
    c.font_text(th.font, 13.5, x + 26, y + 5, name, 0xFFFFFFFF)
    c.font_text(th.font, 12, x + 12, y + 35, info, th.text_dim)
    on = it.held or it.hovered
    edge = mix(th.accent, 0xFFFFFFFF, 0.2 if it.held else 0) if on else 0x22FFFFFF
    c.rrect_line(x, y, w, h, 12, 1.5 if on else 1, edge)
    for ex in (x, x + w):
        c.circle(ex, y + 41, 5.5, 0xFF1A1C21)
        c.ring(ex, y + 41, 5, 2, col)


def wire(c, ax, ay, bx, by, start, end):
    px, py, pull = ax, ay, clamp((bx - ax) * 0.5, 40, 200)
    for i in range(1, 33):
        t = i / 32.0
        s = 1 - t
        x = s * s * s * ax + 3 * s * s * t * (ax + pull) + 3 * s * t * t * (bx - pull) + t * t * t * bx
        y = s * s * s * ay + 3 * s * s * t * ay + 3 * s * t * t * by + t * t * t * by
        c.line(px, py, x, y, 2.5, mix(start, end, t - 1 / 64.0))
        px, py = x, y


def node_area(u, ox, oy):
    ar = u.custom("area", 0, 232, goome.ITEM_NO_HIT)
    pos, its, top = [], [], -1
    for i, node in enumerate(NODES):
        p = u.store(node[0], 3)
        if not p[2]:
            p[0], p[1], p[2] = node[3], node[4], 1
        u.pos(ar.x - ox + p[0], ar.y - oy + p[1])
        it = u.custom(node[0], 150, 58, goome.ITEM_DRAG_X | goome.ITEM_DRAG_Y)
        if it.held:
            p[0] += it.dx
            p[1] += it.dy
            top = i
        p[0] = clamp(p[0], 8, ar.w - it.w - 8)
        p[1] = clamp(p[1], 8, ar.h - it.h - 8)
        if it.released:
            p[0] = clamp(snap(p[0], 20), 0, ar.w - it.w)
            p[1] = clamp(snap(p[1], 20), 0, ar.h - it.h)
        pos.append(p)
        its.append(it)
    th = u.theme
    c = u.canvas
    if c is None:
        return
    c.rrect(ar.x, ar.y, ar.w, ar.h, 12, 0xFF17191E)
    with c.clip(ar.x + 1, ar.y + 1, ar.w - 2, ar.h - 2):
        y = ar.y + 20
        while y < ar.y + ar.h:
            x = ar.x + 20
            while x < ar.x + ar.w:
                c.rect(x - 1, y - 1, 2, 2, 0x16FFFFFF)
                x += 20
            y += 20
        if top >= 0:
            it = its[top]
            sx = clamp(snap(pos[top][0], 20), 0, ar.w - it.w)
            sy = clamp(snap(pos[top][1], 20), 0, ar.h - it.h)
            c.rrect(ar.x + sx, ar.y + sy, it.w, it.h, 12, fade(th.accent, 0.08))
            c.rrect_line(ar.x + sx, ar.y + sy, it.w, it.h, 12, 1.5, fade(th.accent, 0.45))
        for i in range(len(NODES) - 1):
            wire(c, ar.x + pos[i][0] + its[i].w, ar.y + pos[i][1] + 41, ar.x + pos[i + 1][0], ar.y + pos[i + 1][1] + 41, NODES[i][2], NODES[i + 1][2])
        order = [i for i in range(len(NODES)) if i != top] + ([top] if top >= 0 else [])
        for i in order:
            node_box(c, th, NODES[i], its[i], ar.x + pos[i][0], ar.y + pos[i][1], i == top)
        c.font_text(th.font, 12, ar.x + 14, ar.y + ar.h - 24, "drag the boxes, they snap to the grid when you let go", fade(th.text_dim, 0.8))
    c.rrect_line(ar.x, ar.y, ar.w, ar.h, 12, 1, th.border)


class Demo(object):
    def __init__(self, g, u):
        self.g, self.u = g, u
        self.seg, self.tab, self.sel, self.wifi, self.pick, self.pink = 1, 0, 0, True, 1, True
        self.frac, self.vol, self.amt = goome.Split(0.4), 0.62, 0.7
        self.name, self.find = "living room", "search, but round"
        self.gain, self.playhead = 0.0, 0.0

    def buttons(self):
        u = self.u
        u.heading("Buttons your way")
        u.wrapped("push a radius, a color or per corner radii, then pop it. only the widgets in between change.")
        u.button("Normal")
        u.same_line()
        with u.style(radius=0):
            u.button("Square")
        u.same_line()
        with u.style(radius=999):
            u.button("Pill")
        u.same_line()
        with u.style(radii=(16, 3, 16, 3)):
            u.button("Leaf")

        with u.style(gap=1):
            for i, name in enumerate(["Day", "Week", "Month", "Year"]):
                if i:
                    u.same_line()
                r = (9 if i == 0 else 2, 9 if i == 3 else 2, 9 if i == 3 else 2, 9 if i == 0 else 2)
                if self.seg == i:
                    look = dict(input_bg=0xFF3B4250, border=0x40FFFFFF)
                else:
                    look = dict(text=0xFF969CA6, border=0x00000000)
                with u.style(radii=r, **look):
                    u.size(74, 0)
                    if u.button(name):
                        self.seg = i
        u.space(8)

        with u.style(input_bg=0xFF6FDC5F, hover=0xFF86E878, active=0xFF58C24A, text=0xFF0F1D0C, border=0, radius=999):
            u.button("Save it")
        u.same_line()
        with u.style(input_bg=0, hover=0x24E5534B, active=0x40E5534B, text=0xFFFF7A72, border=0x80E5534B, border_width=1.5):
            u.button("Delete")
        u.same_line()
        with u.style(font_size=19, pad=14, radii=(4, 18, 4, 18)):
            u.button("Big one")

        with u.style(radii=(12, 12, 0, 0), gap=2):
            for i, name in enumerate(["Files", "Search", "Git"]):
                if i:
                    u.same_line()
                on = self.tab == i
                with u.style(input_bg=0xFF2F333C if on else 0xFF1F2228, border=0x30FFFFFF if on else 0, text=0xFFE9EBEE if on else 0xFF8C929C):
                    if u.button(name):
                        self.tab = i

    def more(self):
        u = self.u
        u.heading("Every widget reads it")
        with u.style(accent=0xFFFF6FA8, accent_text=0xFF2A0614):
            u.row(2)
            self.pink = u.checkbox("Pink", self.pink)
            self.pink = u.toggle("Also pink", self.pink)
            self.amt = u.slider("Amount", self.amt, 0, 1, "%.2f")
        with u.style(radius=999):
            self.find = u.input("##find", self.find, 64)
        with u.style(radius=0, accent=0xFF4FB3F7, accent_text=0xFF06202E):
            u.progress(self.amt, "square corners")

    def light_card(self):
        u = self.u
        at = u.custom("light-spot", 0, 262, goome.ITEM_NO_HIT)
        t = u.theme.copy()
        t.light()
        t.update(radius=8, shadow=0x60000000)
        with u.style(t):
            with u.window("A whole other theme", goome.Window(at.x, at.y, at.w, at.h), 0) as shown:
                if shown:
                    self.wifi = u.toggle("Wifi", self.wifi)
                    self.vol = u.slider("Volume", self.vol, 0, 1, "%.2f")
                    u.row(2)
                    self.pick = u.radio("Small", self.pick, 0)
                    self.pick = u.radio("Large", self.pick, 1)
                    self.name = u.input("##name", self.name, 64)
                    with u.style(radius=999):
                        u.button("Cancel")
                        u.same_line()
                        with u.style(input_bg=t.accent, hover=0xFF55C944, active=0xFF3AA12B, text=0xFFFFFFFF, border=0):
                            u.button("Apply")

    def draw(self):
        u = self.u
        with u.app("Custom", goome.APP_STATUSBAR | goome.APP_NO_PAD):
            with u.split("main", self.frac) as panes:
                self.buttons()
                u.space(4)
                self.more()
                u.space(6)
                self.light_card()
                panes.next()

                u.pos(0, 0)
                o = u.custom("##origin", 1, 1, goome.ITEM_NO_HIT)
                with u.style(accent=SWATCHES[self.sel]):
                    u.heading("Custom widgets")
                    u.pos(176, 3)
                    u.badge("pinned with ui.pos", 0x26FFFFFF)
                    u.space(2)
                    for i, k in enumerate((("Gain", 0.62, 12, "%.1f dB"), ("Tone", 0.35, 100, "%.0f%%"), ("Mix", 0.8, 100, "%.0f%%"), ("Width", 0.5, 200, "%.0f%%"))):
                        if i:
                            u.same_line()
                        knob(u, *k)
                    u.space(4)
                    timeline(u, o.x, o.y)
                    u.space(4)
                    self.sel = swatch_strip(u, self.sel)
                    u.space(4)
                    node_area(u, o.x, o.y)
                    u.space(4)
                    faders(u)
                    u.same_line()
                    xy_pad(u)
                    self.gain, self.playhead = u.store("Gain", 2)[0] * 12, u.store("playhead", 2)[0]
            u.statusbar("gain %.1f dB   playhead %.1fs" % (self.gain, self.playhead))

    def run(self):
        g, u = self.g, self.u
        test = g.backend_name.split()[0] == "test"
        pace = goome.Pacer(60)
        running, frames = True, 0
        while running:
            for ev in g.events(pace.wait() if test or u.animating else 500):
                if ev.type in (goome.QUIT, goome.CLOSE):
                    running = False
                u.feed(ev)
            if not running:
                break
            if u.begin(0) is None:
                continue
            self.draw()
            u.end()
            frames += 1
        print("%d frames, gain %.1f dB, playhead %.1fs, swatch %d, seg %d" % (frames, self.gain, self.playhead, self.sel, self.seg))


def main():
    try:
        g = goome.open("Custom", mode="window", width=1120, height=800, min_width=800, min_height=560,
                       window_flags=goome.WINDOW_RESIZABLE | goome.WINDOW_CENTER)
    except goome.GoomeError as e:
        print("cant open a window: %s" % e, file=sys.stderr)
        return 1
    with g, g.ui() as u:
        Demo(g, u).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
