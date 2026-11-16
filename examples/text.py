import array
import sys

import goome

LINES = [
    "goome \U0001F600 \U0001F389 \U0001F44D\U0001F3FD \U0001F468‍\U0001F469‍\U0001F467 \U0001F1E9\U0001F1EA #️⃣ ❤️ \U0001F431",
    "السلام عليكم، كيف حالك؟",
    "שלום עולם, מה שלומך?",
    "goome says مرحبا (123) to שלום \U0001F44B",
    "لا لأن محمد كتب 2024 [ok]",
]


def save(g, path):
    f = g.last_frame()
    out = array.array("I", bytes(f.w * f.h * 4))
    for y in range(f.h):
        row = f.row(y)
        for x in range(f.w):
            s = row[x]
            add = 0x20 * (255 - (s >> 24)) // 255
            out[y * f.w + x] = 0xFF000000 | sum((((s >> k) & 255) + add) << k for k in (0, 8, 16))
    goome.save_ppm(path, out, f.w, f.h)


def main():
    shot = sys.argv[1] if len(sys.argv) > 1 else None
    font_path = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        if shot:
            g = goome.open_offscreen(560, 600, scale=2, title="goome text")
        else:
            g = goome.open("goome text", mode="window", width=560, height=600, window_flags=goome.WINDOW_RESIZABLE | goome.WINDOW_CENTER)
    except goome.GoomeError as e:
        print("cant open: %s" % e, file=sys.stderr)
        return 1
    font = emoji = None
    with g, g.ui() as u:
        if font_path:
            font = goome.Font.load(font_path)
            emoji = goome.Font.system("Noto Color Emoji") or goome.Font.system("Segoe UI Emoji") or goome.Font.system("Apple Color Emoji")
            if emoji is not None:
                font.fallback(emoji)
            u.theme.font = font
        if shot:
            u.theme.anim_ms = 0
            u.config.blink_ms = 0
        dir, frame, run = goome.DIR_AUTO, 0, True
        name = "العربية abc \U0001F600"
        notes = ("שלום! this line starts in hebrew\nmixed: abc عربي 42 \U0001F44D\U0001F3FD\n"
                 "مرحبا بكم")
        while run:
            if shot and frame == 3:
                g.push(goome.KEY, key=goome.K_END)
                for _ in range(6):
                    g.push(goome.KEY, key=goome.K_RIGHT, mods=goome.SHIFT)
            for ev in g.events(0 if shot else 16):
                if ev.type in (goome.CLOSE, goome.QUIT):
                    run = False
                u.feed(ev)
            if u.begin(0) is None:
                continue
            goome.text_dir(dir)
            with u.app("goome text") as shown:
                if shown:
                    u.heading("Emoji, Arabic, Hebrew")
                    for line in LINES:
                        u.label(line)
                    u.separator()
                    u.row(3)
                    dir = u.radio("Auto", dir, goome.DIR_AUTO)
                    dir = u.radio("Left to right", dir, goome.DIR_LTR)
                    dir = u.radio("Right to left", dir, goome.DIR_RTL)
                    u.row(1)
                    if shot and frame == 2:
                        u.set_focus()
                    name = u.input("Name", name, 128)
                    notes = u.text_edit("notes", notes, 120, goome.EDIT_WRAP, 1024)
            u.end()
            goome.text_dir(goome.DIR_AUTO)
            frame += 1
            if shot and frame == 6:
                run = False
        if shot:
            save(g, shot)
            print("saved %s, name has %d chars" % (shot, len(name)))
    for f in (font, emoji):
        if f is not None:
            f.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
