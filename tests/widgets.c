#define GOOME_IMPLEMENTATION
#include "goome.h"

#include <stdio.h>
#include <string.h>

static goome *g;

static void ev(int type, double x, double y, int key, const char *text, int dy)
{
    goome_event e;
    memset(&e, 0, sizeof(e));
    e.type = type, e.x = x, e.y = y, e.key = key, e.dy = dy;
    e.button = type == GOOME_DOWN || type == GOOME_UP ? 1 : 0;
    if (text) snprintf(e.text, sizeof(e.text), "%s", text);
    goome_push(g, &e);
}

static void click(double x, double y)
{
    ev(GOOME_MOTION, x, y, 0, NULL, 0);
    ev(GOOME_DOWN, x, y, 0, NULL, 0);
    ev(GOOME_UP, x, y, 0, NULL, 0);
}

static void script(int f)
{
    switch (f) {
    case 1: case 5: click(28, 14); break;
    case 3: click(60, 77); break;
    case 7: click(60, 50); break;
    case 9: click(330, 93); break;
    case 10: ev(GOOME_KEY, 0, 0, '!', "!", 0); break;
    case 11: ev(GOOME_KEY, 0, 0, GOOME_K_ENTER, NULL, 0); break;
    case 12: ev(GOOME_KEY, 0, 0, 'x', "x", 0); break;
    case 14: click(240, 158); break;
    case 16: click(70, 67); break;
    case 18: ev(GOOME_MOTION, 407, 279, 0, NULL, 0), ev(GOOME_DOWN, 407, 279, 0, NULL, 0); break;
    case 19: ev(GOOME_MOTION, 447, 279, 0, NULL, 0); break;
    case 20: ev(GOOME_UP, 447, 279, 0, NULL, 0); break;
    case 22: click(590, 339); break;
    case 24: click(250, 430); break;
    case 30: ev(GOOME_MOTION, 100, 160, 0, NULL, 0), ev(GOOME_SCROLL, 100, 160, 0, NULL, 3); break;
    case 28: ev(GOOME_KEY, 0, 0, GOOME_K_ESC, NULL, 0); break;
    }
}

static uint32_t fnv(const goome_image *f)
{
    uint32_t v = 2166136261u;
    for (int y = 0; y < f->h; y++) {
        const unsigned char *p = (const unsigned char *)(f->px + (size_t)y * f->stride);
        for (int i = 0; i < f->w * 4; i++) v = (v ^ p[i]) * 16777619u;
    }
    return v;
}

int main(void)
{
    int err;
    g = goome_open(&(goome_opts){.mode = GOOME_MODE_OFFSCREEN, .title = "scene", .width = 640, .height = 520, .scale = 1}, &err);
    if (!g) return 1;
    goome_ui *u = goome_ui_new(g);
    goome_theme *th = goome_ui_theme(u);
    th->anim_ms = 0, th->font = NULL, th->font_size = 14;
    int wrap = 0, tree = 1, modal = 0, news = 0, sorted = 0, col = 0, desc = 0, modal_seen = 0, first = 0, last = 0;
    double frac = 0.3, speed = 1.5, count = 2;
    char text[256] = "hello\nworld";
    float fps[] = {1, 3, 2, 5, 4};
    uint32_t mid = 0;
    for (int f = 0; f < 34; f++) {
        script(f);
        goome_event e;
        while (goome_poll(g, &e, 0) > 0) goome_ui_feed(u, &e);
        if (!goome_ui_begin(u, 0)) continue;
        goome_ui_app(u, "Scene", GOOME_APP_MENUBAR | GOOME_APP_STATUSBAR);
        if (goome_ui_menubar_begin(u)) {
            if (goome_ui_menu_begin(u, "File")) {
                if (goome_ui_menu_item(u, "New", "Ctrl+N", NULL)) news++;
                goome_ui_menu_item(u, "Wrap", NULL, &wrap);
                goome_ui_menu_end(u);
            }
            goome_ui_menubar_end(u);
        }
        goome_ui_split_begin(u, "main", 0, &frac);
        if (goome_ui_tree(u, "Folder", &tree)) {
            goome_ui_label(u, "%s", "a.txt");
            goome_ui_label(u, "%s", "b.txt");
            goome_ui_tree_end(u);
        }
        goome_ui_scroll_begin(u, "list", 120);
        goome_ui_list_clip(u, 100, 0, &first, &last);
        for (int k = first; k < last; k++) {
            char row[32];
            snprintf(row, sizeof(row), "row %d", k);
            goome_ui_selectable(u, row, 0);
        }
        goome_ui_scroll_end(u);
        goome_ui_split_next(u);
        goome_ui_text_edit(u, "body", text, sizeof(text), 80, GOOME_EDIT_LINE_NUMBERS);
        goome_ui_table_begin(u, "files", 2, 90, GOOME_TABLE_SORTABLE | GOOME_TABLE_STRIPES);
        goome_ui_table_column(u, "Name", 0);
        goome_ui_table_column(u, "Size", 80);
        if (goome_ui_table_sort(u, &col, &desc)) sorted++;
        for (int k = 0; k < 3; k++) {
            char a[32], b[32];
            snprintf(a, sizeof(a), "file %d", k);
            snprintf(b, sizeof(b), "%d kb", k);
            goome_ui_table_row(u);
            goome_ui_label(u, "%s", a);
            goome_ui_table_next(u);
            goome_ui_label(u, "%s", b);
        }
        goome_ui_table_end(u);
        goome_ui_drag_float(u, "Speed", &speed, 0.1, 0, 10, "%.1f");
        goome_ui_number(u, "Count", &count, 1, "%.0f");
        goome_ui_plot_lines(u, "fps", fps, 5, 0, 5, 30);
        if (goome_ui_link(u, "open about")) modal = 1;
        goome_ui_badge(u, "new", 0xFF6FDC5F);
        goome_ui_split_end(u);
        if (goome_ui_modal_begin(u, "About", &modal)) {
            modal_seen++;
            goome_ui_label(u, "%s", "about box");
            if (goome_ui_button(u, "Close")) modal = 0;
            goome_ui_modal_end(u);
        }
        goome_ui_statusbar(u, "ready");
        goome_ui_app_end(u);
        goome_ui_end(u);
        goome_image fr;
        if (f == 25 && goome_frame(g, &fr) == GOOME_OK) mid = fnv(&fr);
    }
    goome_image fr;
    if (goome_frame(g, &fr) != GOOME_OK) return 1;
    printf("mid %08x\nend %08x\n", mid, fnv(&fr));
    printf("state wrap=%d tree=%d modal=%d seen=%d news=%d sorted=%d col=%d desc=%d speed=%.1f count=%.0f rows=%d,%d frac=%.2f\n", wrap, tree,
           modal, modal_seen > 0, news, sorted, col, desc, speed, count, first, last, frac);
    printf("text %s\n", text);
    goome_ui_free(u);
    goome_close(g);
    return 0;
}
