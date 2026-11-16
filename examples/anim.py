import sys

import goome

ROWS = [("linear", goome.EASE_LINEAR, 0xFF7C8CFF), ("in", goome.EASE_IN, 0xFF4FB3F7), ("out", goome.EASE_OUT, 0xFF3FC8B4),
        ("in out", goome.EASE_IN_OUT, 0xFF6FDC5F), ("smooth", goome.EASE_SMOOTH, 0xFFE8D85A), ("back", goome.EASE_BACK, 0xFFFFB443),
        ("spring", goome.EASE_SPRING, 0xFFFF7A59), ("bounce", goome.EASE_BOUNCE, 0xFFFF6FA8)]
MOODS = [(0xFF2D6CDF, "blue"), (0xFFE0483E, "red"), (0xFF21A66B, "green"), (0xFFF2B33D, "gold"), (0x00000000, "see through")]


def fade(c, k):
    k = 0 if k < 0 else 1 if k > 1 else k
    return int(((c >> 24) & 255) * k + 0.5) << 24 | (c & 0xFFFFFF)


def text_at(c, font, size, x, cy, s, col, center=False):
    w, h = goome.measure(s, size, font)
    if h <= 0:
        h = goome.line_height(size, font)
    c.font_text(font, size, x - w / 2 if center else x, int(cy - h / 2 + 0.5), s, col)


class Demo(object):
    def __init__(self, g, u):
        self.g, self.u = g, u
        self.side, self.autoplay, self.mood, self.on, self.count, self.kick = 0, True, 0, False, 0, False

    def ease_rows(self):
        u, th = self.u, self.u.theme
        for name, ease, color in ROWS:
            it = u.custom(name, 0, 30, goome.ITEM_NO_HIT)
            k = u.anim(name, self.side, 900, ease)
            c = u.canvas
            if c is None:
                continue
            tx, tw, bw = it.x + 86, it.w - 96, 46
            run = (tw - bw) * 0.76
            left = tx + (tw - bw - run) / 2
            text_at(c, th.font, 13, it.x + 4, it.y + 15, name, th.text_dim)
            c.rrect(tx, it.y + 3, tw, 24, 12, 0x14FFFFFF)
            c.rect(left + bw / 2, it.y + 14, 1, 2, 0x30FFFFFF)
            c.rect(left + run + bw / 2, it.y + 14, 1, 2, 0x30FFFFFF)
            x = left + k * run
            c.shadow(x, it.y + 8, bw, 16, 8, 8, fade(color, 0.45))
            c.rrect(x, it.y + 6, bw, 18, 9, color)

    def color_card(self):
        u, th = self.u, self.u.theme
        it = u.custom("mood", 0, 92)
        if it.clicked:
            self.mood = (self.mood + 1) % len(MOODS)
        u.tooltip("click for the next color")
        want, name = MOODS[self.mood]
        col = u.anim_color("mood", want, 600, goome.EASE_IN_OUT)
        lift = u.anim("mood lift", 1 if it.hovered else 0, 160, goome.EASE_OUT)
        c = u.canvas
        if c is None:
            return
        y = it.y - lift * 2
        for i in range(12):
            c.rect(it.x + i * it.w / 12, it.y + 8, it.w / 24, 76, 0x10FFFFFF)
        c.shadow(it.x, y + 6, it.w, 84, 14, 18, fade(col, 0.4 + lift * 0.2))
        c.rrect(it.x, y, it.w, 84, 14, col)
        c.ring(it.x + 30, y + 42, 12, 2, 0x50FFFFFF)
        text_at(c, th.font, 15, it.x + 54, y + 42, "%s  #%08X" % (name, col), th.text)

    def spring_toggle(self):
        u, th = self.u, self.u.theme
        it = u.custom("springy", 64, 36, goome.ITEM_FOCUSABLE)
        key = it.key & 0xFF
        if it.clicked or key in (ord(" "), goome.K_ENTER):
            self.on = not self.on
        k = u.anim("springy", 1 if self.on else 0, 520, goome.EASE_SPRING)
        squish = u.anim("squish", 1 if it.held else 0, 220, goome.EASE_SPRING)
        track = u.anim_color("springy", th.accent if self.on else 0xFF3A3F49, 260, goome.EASE_OUT)
        c = u.canvas
        if c is None:
            return
        x, y, w, h, r = it.x + 2, it.y + 4, 60, 28, 11
        kw = 2 * r + squish * 8
        if it.focused:
            c.rrect(x - 3, y - 3, w + 6, h + 6, 17, fade(th.focus or th.accent, 0.6))
        c.rrect(x, y, w, h, 14, track)
        kx = x + 3 + k * (w - 6 - kw)
        c.shadow(kx, y + 5, kw, 2 * r, r, 6, 0x60000000)
        c.rrect(kx, y + 3, kw, 2 * r, r, 0xFFF4F5F7)

    def bell(self):
        u, th = self.u, self.u.theme
        it = u.custom("bell", 140, 64)
        if it.clicked:
            self.count += 1
            self.kick = True
        drop = u.anim("drop", -46 if self.kick else 0, 0 if self.kick else 900, goome.EASE_BOUNCE)
        pop = u.anim("pop", 0.4 if self.kick else 1, 0 if self.kick else 500, goome.EASE_SPRING)
        shown = u.anim("shown", 1 if self.count > 0 else 0, 200, goome.EASE_OUT)
        self.kick = False
        c = u.canvas
        if c is None:
            return
        bg = u.anim_color("bell bg", 0xFF2E333C if it.hovered else 0xFF262A31, 140, goome.EASE_OUT)
        c.rrect(it.x, it.y + 8, 120, 52, 12, bg)
        text_at(c, th.font, 14, it.x + 60, it.y + 34, "notify me", th.text, True)
        if shown <= 0.01:
            return
        r, cx, cy = 13 * pop, it.x + 116, it.y + 10 + drop
        c.shadow(cx - r, cy - r + 3, 2 * r, 2 * r, r, 8, fade(0x90000000, shown))
        c.circle(cx, cy, r, fade(0xFFE0483E, shown))
        if pop > 0.6:
            text_at(c, th.font, 12 * pop, cx, cy, str(self.count), fade(0xFFFFFFFF, shown), True)

    def draw(self, now):
        u = self.u
        with u.app("Animations", goome.APP_STATUSBAR):
            u.heading("Every ease, same 900 ms")
            if u.button("Swap sides"):
                self.side, self.flipped = 1 - self.side, now
            u.same_line()
            self.autoplay = u.toggle("Play by itself", self.autoplay)
            u.space(4)
            self.ease_rows()
            u.space(8)
            u.heading("Color fade")
            self.color_card()
            u.space(8)
            u.heading("Spring and bounce")
            self.spring_toggle()
            u.same_line()
            u.label("on, and it wobbled a bit" if self.on else "off")
            u.same_line()
            u.space(40)
            u.same_line()
            self.bell()
            u.statusbar("moving" if u.animating else "still")

    def run(self):
        g, u = self.g, self.u
        test = g.backend_name.split()[0] == "test"
        pace = goome.Pacer(60)
        running, frames, moving = True, 0, 0
        self.flipped = 0
        while running:
            wait = pace.wait() if test or self.autoplay or u.animating else 500
            for ev in g.events(wait):
                if ev.type in (goome.QUIT, goome.CLOSE):
                    running = False
                u.feed(ev)
            if not running:
                break
            now = frames * 16 if test else goome.now_ms()
            frames += 1
            if self.autoplay and now - self.flipped >= 1500:
                self.flipped, self.side = now, 1 - self.side
                if self.side:
                    self.mood = (self.mood + 1) % len(MOODS)
                    self.on = not self.on
                    self.count += 1
                    self.kick = True
            if u.begin(0) is None:
                continue
            self.draw(now)
            u.end()
            moving += u.animating
        print("%d frames, %d moving, side %d, mood %s, bell %d" % (frames, moving, self.side, MOODS[self.mood][1], self.count))


def main():
    try:
        g = goome.open("Animations", mode="window", width=880, height=760, min_width=620, min_height=700,
                       window_flags=goome.WINDOW_RESIZABLE | goome.WINDOW_CENTER)
    except goome.GoomeError as e:
        print("cant open a window: %s" % e, file=sys.stderr)
        return 1
    with g, g.ui() as u:
        Demo(g, u).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
