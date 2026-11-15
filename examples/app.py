import sys

import goome

COLORS = ["None", "Blue", "Green", "Yellow", "Red"]
SORTS = ["Recently edited", "Title", "Created"]

app = goome.App("Notes", 980, 640, flags=goome.APP_MENUBAR | goome.APP_STATUSBAR | goome.APP_NO_PAD, min_width=560, min_height=380)
notes = []
settings, about, confirm = goome.Flag(), goome.Flag(), goome.Flag()
sidebar, statusbar, wrap = goome.Flag(True), goome.Flag(True), goome.Flag(True)
side = goome.Split(0.27)
state = dict(sel=0, search="", light=False, accent=0xFF6FDC5F, size=15.0, save=False, autosave=True, sort=0, made=0, typed=0)


def add(title, tags="", body="", pinned=False, color=0):
    state["made"] += 1
    notes.append(dict(title=title, tags=tags, body=body, pinned=pinned, color=color, made=state["made"], edited=state["made"], changed=False))
    state["sel"] = len(notes) - 1


def touch(note):
    state["made"] += 1
    note["edited"] = state["made"]
    note["changed"] = True
    state["typed"] = goome.now_ms()


def order():
    by = state["sort"]
    if by == 1:
        key = lambda i: (not notes[i]["pinned"], notes[i]["title"], notes[i]["made"])
    elif by == 2:
        key = lambda i: (not notes[i]["pinned"], notes[i]["made"])
    else:
        key = lambda i: (not notes[i]["pinned"], -notes[i]["edited"])
    return sorted(range(len(notes)), key=key)


def theme(ui):
    font = ui.theme.font
    ui.theme.light() if state["light"] else ui.theme.dark()
    ui.theme.update(font=font, accent=state["accent"], font_size=round(state["size"]))


def save(ui, note, quiet=False):
    note["changed"] = False
    if not quiet:
        ui.toast('Saved "%s"' % note["title"], 2500)


add("Groceries", "home", "milk\neggs\ncoffee\nrice\ncat food", True, 2)
add("Release checklist", "work", "bump the version\nrun the tests\nwrite the changelog\ntag it", color=1)
add("Books", "reading", "finish the one on the nightstand first", color=3)
add("Workout", "health", "mon legs, wed push, fri pull")
add("Trip", "travel", "train at 8:10, book the hotel", color=4)
state["sel"] = 0


@app.event
def keys(ev):
    if ev.type == goome.KEY and ev.mods & goome.CTRL:
        if ev.key == ord("s"):
            state["save"] = True
        elif ev.key == ord("n"):
            add("Untitled")
        elif ev.key == ord("q"):
            app.quit()
        elif ev.key == ord("b"):
            sidebar.toggle()
        app.redraw()


def menus(ui, note):
    with ui.menubar() as bar:
        if not bar:
            return
        with ui.menu("File") as shown:
            if shown:
                if ui.menu_item("New note", "Ctrl+N"):
                    add("Untitled")
                with ui.menu("Open recent") as recent:
                    if recent:
                        for i, n in enumerate(notes[:4]):
                            if ui.menu_item(n["title"] or "Untitled"):
                                state["sel"] = i
                if ui.menu_item("Save", "Ctrl+S") and note:
                    save(ui, note)
                ui.menu_separator()
                if ui.menu_item("Settings", "Ctrl+,"):
                    settings.value = True
                ui.menu_separator()
                if ui.menu_item("Quit", "Ctrl+Q"):
                    app.quit()
        with ui.menu("Edit") as shown:
            if shown:
                if ui.menu_item("Copy note") and note:
                    app.g.clipboard = note["body"]
                    ui.toast("Copied", 1500)
                if ui.menu_item("Paste at the end") and note:
                    text = app.g.clipboard
                    if text:
                        note["body"] = (note["body"] + text)[:4095]
                        touch(note)
                ui.menu_separator()
                if ui.menu_item("Delete note", "Del") and note:
                    confirm.value = True
        with ui.menu("View") as shown:
            if shown:
                ui.menu_item("Sidebar", "Ctrl+B", sidebar)
                ui.menu_item("Status bar", None, statusbar)
                ui.menu_item("Wrap text", None, wrap)
                ui.menu_separator()
                with ui.menu("Sort by") as sorts:
                    if sorts:
                        for i, name in enumerate(SORTS):
                            if ui.menu_item(name, None, goome.Flag(state["sort"] == i)):
                                state["sort"] = i
        with ui.menu("Help") as shown:
            if shown and ui.menu_item("About Notes"):
                about.value = True


def note_list(ui):
    state["search"] = ui.input("##search", state["search"], 64)
    ui.tooltip("filter notes by title")
    for i in order():
        n = notes[i]
        if state["search"] not in n["title"]:
            continue
        if ui.selectable("%s%s##%d" % ("* " if n["pinned"] else "", n["title"] or "Untitled", i), i == state["sel"]):
            state["sel"] = i
        with ui.context("note%d" % i) as shown:
            if shown:
                if ui.menu_item("Open"):
                    state["sel"] = i
                if ui.menu_item("Duplicate"):
                    add(n["title"], n["tags"], n["body"], False, n["color"])
                ui.menu_separator()
                if ui.menu_item("Delete"):
                    state["sel"] = i
                    confirm.value = True
    ui.space(4)
    if ui.button("New note"):
        add("Untitled")


def editor(ui, note):
    if note is None:
        ui.label("no note picked")
        return
    ui.heading(note["title"] or "Untitled")
    changed = False
    ui.row(2)
    note["title"] = ui.input("Title", note["title"], 64)
    changed |= ui.changed
    note["tags"] = ui.input("Tags", note["tags"], 64)
    changed |= ui.changed
    ui.row(2)
    note["color"] = ui.combo("Label", note["color"], COLORS)
    changed |= ui.changed
    state["sort"] = ui.combo("Sort notes by", state["sort"], SORTS)
    note["pinned"] = ui.toggle("Pinned", note["pinned"])
    changed |= ui.changed
    if ui.button("Save"):
        save(ui, note)
    ui.same_line()
    if ui.button("Delete"):
        confirm.value = True
    ui.same_line()
    if ui.button("More..."):
        ui.popup_open("more")
    with ui.popup("more") as shown:
        if shown:
            ui.label("%d words" % len(note["body"].split()))
            state["autosave"] = ui.toggle("Autosave", state["autosave"])
            if ui.button("Duplicate"):
                add(note["title"], note["tags"], note["body"], False, note["color"])
            if ui.button("Close"):
                ui.popup_close()
    with ui.id("note%d" % state["sel"]):
        note["body"] = ui.text_edit("body", note["body"], 0, goome.EDIT_WRAP if wrap else 0)
    changed |= ui.changed
    if changed:
        touch(note)


def dialogs(ui, note):
    with ui.modal("Settings", settings) as shown:
        if shown:
            light = ui.radio("Dark", int(state["light"]), 0)
            ui.same_line()
            light = ui.radio("Light", light, 1)
            changed = bool(light) != state["light"]
            state["light"] = bool(light)
            state["accent"] = ui.color("Accent color", state["accent"])
            changed |= ui.changed
            state["size"] = ui.slider("Text size", state["size"], 12, 20, "%.0f px")
            changed |= ui.changed
            if changed:
                theme(ui)
            ui.separator()
            state["autosave"] = ui.toggle("Save while typing", state["autosave"])
            ui.space(6)
            if ui.button("Done"):
                ui.popup_close()
    with ui.modal("Delete this note?", confirm) as shown:
        if shown:
            ui.wrapped("it goes away for good, theres no trash folder yet.")
            if ui.button("Delete") and note:
                notes.remove(note)
                state["sel"] = min(state["sel"], len(notes) - 1)
                ui.toast("Note deleted", 2000)
                ui.popup_close()
            ui.same_line()
            if ui.button("Keep it"):
                ui.popup_close()
    with ui.modal("About Notes", about) as shown:
        if shown:
            ui.label("Notes, a goome %s demo in Python" % goome.VERSION)
            ui.wrapped("everything in here is drawn by goome: the menus, the editor, this dialog.")
            if ui.button("Nice"):
                ui.popup_close()


@app.frame
def draw(ui):
    app.flags = goome.APP_MENUBAR | (goome.APP_STATUSBAR if statusbar else 0) | (goome.APP_NO_PAD if sidebar else 0)
    note = notes[state["sel"]] if 0 <= state["sel"] < len(notes) else None
    if state["save"]:
        state["save"] = False
        if note:
            save(ui, note)
    menus(ui, note)
    if sidebar:
        with ui.split("panes", side) as panes:
            note_list(ui)
            panes.next()
            editor(ui, note)
    else:
        with ui.scroll_begin("main"):
            editor(ui, note)
    dialogs(ui, note)
    if state["autosave"] and state["typed"] and goome.now_ms() - state["typed"] > 1500:
        for n in notes:
            save(ui, n, True)
        state["typed"] = 0
    app.animate = bool(state["typed"])
    words = len(note["body"].split()) if note else 0
    left = any(n["changed"] for n in notes)
    ui.statusbar("%d notes   %d words   %s" % (len(notes), words, "unsaved changes" if left else "all saved"))


def main():
    try:
        app.run()
    except goome.GoomeError as e:
        print("cant open the app: %s" % e, file=sys.stderr)
        return 1
    note = notes[state["sel"]] if notes else None
    print("closed after %d frames, %d notes, on %r" % (app.frames, len(notes), note and note["title"]))
    if note:
        print("body ends with %r" % note["body"][-20:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
