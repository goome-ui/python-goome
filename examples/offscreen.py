import struct
import sys
import zlib

import goome

SCRIPT = {
    2: [(goome.DOWN, 40, 109), (goome.UP, 40, 109)],
    3: [(goome.DOWN, 60, 163)],
    4: [(goome.MOTION, 250, 163)],
    5: [(goome.UP, 250, 163)],
    6: [(goome.DOWN, 150, 223), (goome.UP, 150, 223)],
    7: [("type", " from an engine")],
    8: [(goome.MOTION, 80, 279)],
}


def write_png(path, frame):
    w, h = frame.w, frame.h
    over = []
    for bg in (0xFF2E3C4A, 0xFF3A4A5A):
        over.append([tuple(((bg >> k) & 255) * (255 - a) // 255 for k in (16, 8, 0)) for a in range(256)])
    rows = bytearray()
    for y in range(h):
        rows.append(0)
        row = frame.row(y)
        for x in range(w):
            s = row[x]
            add = over[(x // 16 + y // 16) & 1][s >> 24]
            rows += bytes(((s >> 16 & 255) + add[0], (s >> 8 & 255) + add[1], (s & 255) + add[2]))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(rows), 9)))
        f.write(chunk(b"IEND", b""))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "offscreen.png"
    with goome.open_offscreen(360, 330, scale=2) as g, g.ui() as ui:
        ui.theme.anim_ms = 0
        win = goome.Window(20, 20, 320, 0)
        check, volume, name = False, 0.25, "goome"
        for frame in range(10):
            for step in SCRIPT.get(frame, []):
                if step[0] == "type":
                    g.push_text(step[1])
                else:
                    g.push(step[0], x=step[1], y=step[2], button=1)
            for ev in g.events(0):
                ui.feed(ev)
            with ui.frame(0) as c:
                if c is None:
                    continue
                with ui.window("offscreen", win, goome.WIN_MOVE):
                    ui.label("no window, the engine owns the screen")
                    check = ui.checkbox("Pushed a click", check)
                    volume = ui.slider("Volume", volume, 0, 1, "%.2f")
                    name = ui.input("Name", name, 64)
                    ui.progress(volume)
                    ui.button("Hover me")
        write_png(path, g.last_frame())
        print("check %d volume %.2f name '%s' cursor %s -> %s" % (check, volume, name, goome.CURSOR_NAMES[g.cursor], path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
