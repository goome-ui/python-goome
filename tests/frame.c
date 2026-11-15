#define GOOME_IMPLEMENTATION
#include "goome.h"

#include <stdio.h>
#include <string.h>

static uint32_t fnv(const goome_image *f)
{
    uint32_t v = 2166136261u;
    for (int y = 0; y < f->h; y++) {
        const unsigned char *p = (const unsigned char *)(f->px + (size_t)y * f->stride);
        for (int i = 0; i < f->w * 4; i++) v = (v ^ p[i]) * 16777619u;
    }
    return v;
}

static void push(goome *g, int type, double x, double y, int key, const char *text)
{
    goome_event e;
    memset(&e, 0, sizeof(e));
    e.type = type, e.x = x, e.y = y, e.button = type == GOOME_DOWN || type == GOOME_UP ? 1 : 0, e.key = key;
    if (text) snprintf(e.text, sizeof(e.text), "%s", text);
    goome_push(g, &e);
}

int main(void)
{
    int err;
    goome *g = goome_open(&(goome_opts){.mode = GOOME_MODE_OFFSCREEN, .title = "engine", .width = 200, .height = 200, .scale = 2}, &err);
    if (!g) return 1;
    goome_canvas *c = goome_begin(g, 0);
    goome_draw_rect(c, 10, 10, 20, 20, 0x80FF0000);
    goome_draw_circle(c, 120, 50, 30, 0xFF3A7AFE);
    goome_draw_rrect(c, 40, 60, 70, 30, goome_radius(8), 0xCC20C060);
    goome_draw_text(c, 44, 66, "offscreen", 0, 0xFFFFFFFF);
    goome_rect hit = {10, 10, 20, 20};
    goome_end(g, c, &hit, 1);
    goome_image f;
    if (goome_frame(g, &f) != GOOME_OK) return 1;
    printf("draw %08x\n", fnv(&f));

    goome_ui *u = goome_ui_new(g);
    goome_ui_theme(u)->anim_ms = 0;
    goome_ui_theme(u)->font = NULL;
    goome_ui_theme(u)->font_size = 14;
    double wx = 6, wy = 6, ww = 180, wh = 0, val = 0.25;
    int check = 0;
    char name[32] = "hi";
    for (int frame = 0; frame < 6; frame++) {
        if (frame == 1) push(g, GOOME_MOTION, 25, 64, 0, NULL), push(g, GOOME_DOWN, 25, 64, 0, NULL), push(g, GOOME_UP, 25, 64, 0, NULL);
        if (frame == 2) push(g, GOOME_DOWN, 90, 168, 0, NULL), push(g, GOOME_UP, 90, 168, 0, NULL);
        if (frame == 3) push(g, GOOME_KEY, 0, 0, 'z', "z");
        goome_event ev;
        while (goome_poll(g, &ev, 0) > 0) goome_ui_feed(u, &ev);
        if (!goome_ui_begin(u, 0)) continue;
        if (goome_ui_window(u, "engine", &wx, &wy, &ww, &wh, GOOME_WIN_MOVE, NULL)) {
            goome_ui_checkbox(u, "Check", &check);
            goome_ui_slider(u, "Val", &val, 0, 1, "%.2f");
            goome_ui_input(u, "Name", name, sizeof(name));
        }
        goome_ui_window_end(u);
        goome_ui_end(u);
    }
    if (goome_frame(g, &f) != GOOME_OK) return 1;
    printf("ui %08x %d %s %d\n", fnv(&f), check, name, goome_hit(g, 10, 10));
    goome_ui_free(u);
    goome_close(g);
    return 0;
}
