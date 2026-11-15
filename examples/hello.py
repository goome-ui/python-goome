import sys

import goome


def main():
    try:
        g = goome.open("goome hello")
    except goome.GoomeError as e:
        print("cant open an overlay: %s" % e, file=sys.stderr)
        return 1
    with g:
        mons = g.monitors()
        print("backend: %s" % g.backend_name)
        for i, m in enumerate(mons):
            a = m.area
            print("monitor %d: %s %dx%d at %d,%d scale %.2f" % (i, m.name, a.w, a.h, a.x, a.y, m.scale))
        try:
            g.hotkey("alt+h", 1)
        except goome.GoomeError:
            print("no global hotkeys here: %s" % g.error)
        sys.stdout.flush()

        bx, by = mons[0].area.x + 80, mons[0].area.y + 80
        clicks, hidden, typing, running = 0, False, False, True
        typed = ""
        pace = goome.Pacer(30)
        while running:
            wait = pace.wait()
            while True:
                ev = g.poll(wait)
                if ev is None:
                    break
                if ev.type == goome.QUIT:
                    running = False
                if ev.type == goome.DOWN:
                    print("click %.0f,%.0f" % (ev.x, ev.y))
                    if ev.x > bx + 250 and ev.y < by + 30:
                        running = False
                    elif ev.y > by + 80:
                        typing = not typing
                        g.keyboard(typing)
                    else:
                        clicks += 1
                if ev.type == goome.KEY:
                    print("key %d mods %x text '%s'" % (ev.key, ev.mods, ev.text))
                    if ev.key == goome.K_ESC:
                        running = False
                    elif ev.key == goome.K_BACKSPACE and typed:
                        typed = typed[:-1]
                    elif ev.text and len((typed + ev.text).encode()) < 40:
                        typed += ev.text
                if ev.type == goome.HOTKEY or (ev.type == goome.CONTROL and ev.msg == "hide"):
                    hidden = not hidden
                if ev.type == goome.SCROLL:
                    by += ev.dy * 10
                sys.stdout.flush()
                wait = pace.wait()
            c = g.begin(0)
            if c is None:
                continue
            if not hidden:
                c.round_rect(bx, by, 280, 120, 14, 0xE0202838)
                c.frame(bx, by, 280, 120, 2, 0xFF6FDC5F if clicks & 1 else 0xFF8090A0)
                c.text(bx + 16, by + 12, "hello from goome", 0xFFFFFFFF, big=True)
                c.line(bx + 256, by + 10, bx + 268, by + 22, 2, 0xFFFF6B8B)
                c.line(bx + 268, by + 10, bx + 256, by + 22, 2, 0xFFFF6B8B)
                c.text(bx + 16, by + 46, "clicks: %d" % clicks, 0xFFC0C8D0)
                c.round_rect(bx + 12, by + 80, 256, 28, 8, 0xFF2E4A30 if typing else 0xFF303848)
                c.text(bx + 22, by + 86, (typed or "type something...") if typing else "click here to type", 0xFFFFFFFF)
                c.hit(bx, by, 280, 120)
            g.end(c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
