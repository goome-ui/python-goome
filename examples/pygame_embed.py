import math
import sys

try:
    import pygame
except ImportError:
    print("this one needs pygame: pip install pygame (or pygame-ce)", file=sys.stderr)
    sys.exit(2)

import goome

KEYS = {
    pygame.K_BACKSPACE: goome.K_BACKSPACE, pygame.K_TAB: goome.K_TAB, pygame.K_RETURN: goome.K_ENTER, pygame.K_ESCAPE: goome.K_ESC,
    pygame.K_DELETE: goome.K_DELETE, pygame.K_LEFT: goome.K_LEFT, pygame.K_RIGHT: goome.K_RIGHT, pygame.K_UP: goome.K_UP,
    pygame.K_DOWN: goome.K_DOWN, pygame.K_HOME: goome.K_HOME, pygame.K_END: goome.K_END,
}
CURSORS = {
    goome.CURSOR_IBEAM: pygame.SYSTEM_CURSOR_IBEAM, goome.CURSOR_HAND: pygame.SYSTEM_CURSOR_HAND,
    goome.CURSOR_RESIZE_EW: pygame.SYSTEM_CURSOR_SIZEWE, goome.CURSOR_RESIZE_NS: pygame.SYSTEM_CURSOR_SIZENS,
}


def mods():
    m = pygame.key.get_mods()
    return (goome.SHIFT if m & pygame.KMOD_SHIFT else 0) | (goome.CTRL if m & pygame.KMOD_CTRL else 0) | (goome.ALT if m & pygame.KMOD_ALT else 0)


def forward(g, e):
    if e.type == pygame.MOUSEMOTION:
        g.push(goome.MOTION, x=e.pos[0], y=e.pos[1])
    elif e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and e.button in (1, 2, 3):
        g.push(goome.DOWN if e.type == pygame.MOUSEBUTTONDOWN else goome.UP, x=e.pos[0], y=e.pos[1], button=e.button)
    elif e.type == pygame.MOUSEWHEEL:
        x, y = pygame.mouse.get_pos()
        g.push(goome.SCROLL, x=x, y=y, dy=-e.y)
    elif e.type == pygame.TEXTINPUT:
        g.push_text(e.text)
    elif e.type == pygame.KEYDOWN:
        if e.key in KEYS:
            g.push(goome.KEY, key=KEYS[e.key], mods=mods())
        elif mods() & goome.CTRL and 0 < e.key < 128:
            g.push(goome.KEY, key=e.key, mods=mods())


def main():
    frames = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("goome inside pygame")
    clock = pygame.time.Clock()
    g = goome.open_offscreen(800, 600)
    ui = g.ui()
    stride = 800 * 4
    pixels = bytearray(stride * 600)
    overlay = pygame.image.frombuffer(pixels, (800, 600), "BGRA")
    copied = 0
    win = goome.Window(24, 24, 260, 0)
    speed, size, color, cursor = 1.0, 40, 0xFF6FDC5F, -1
    t, n, running, paused = 0.0, 0, True, False
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not ui.wants_mouse:
                paused = not paused
            forward(g, e)
        for ev in g.events(0):
            ui.feed(ev)

        if not paused:
            t += speed / 60
        screen.fill((24, 28, 36))
        x = 400 + math.cos(t) * 220
        y = 330 + math.sin(t * 2) * 120
        pygame.draw.circle(screen, ((color >> 16) & 255, (color >> 8) & 255, color & 255), (int(x), int(y)), size)

        with ui.frame(0) as c:
            if c is not None:
                with ui.window("game settings", win, goome.WIN_MOVE | goome.WIN_COLLAPSE):
                    ui.label("fps %.0f" % clock.get_fps())
                    speed = ui.slider("Speed", speed, 0, 4, "%.1f")
                    size = ui.slider_int("Size", size, 5, 120)
                    color = ui.color("Color", color)
                    if ui.button("Quit"):
                        running = False
        r = g.frame_dirty()
        if r is not None:
            g.frame_copy(memoryview(pixels)[r.y * stride + r.x * 4 :], stride, goome.FMT_BGRA_PREMUL, r)
            copied += r.w * r.h
        screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        if g.cursor != cursor:
            cursor = g.cursor
            try:
                pygame.mouse.set_system_cursor(CURSORS.get(cursor, pygame.SYSTEM_CURSOR_ARROW))
            except pygame.error:
                pass
        pygame.display.flip()
        clock.tick(60)
        n += 1
        if frames and n >= frames:
            running = False
    ui.close()
    g.close()
    pygame.quit()
    print("ran %d frames, copied %.1f screens of pixels" % (n, copied / (800.0 * 600)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
