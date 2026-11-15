#define GOOME_IMPLEMENTATION
#include "goome.h"

#include <stdio.h>
#include <string.h>

static goome *g;

static void ev(int type, double x, double y)
{
    goome_event e;
    memset(&e, 0, sizeof(e));
    e.type = type, e.x = x, e.y = y;
    e.button = type == GOOME_DOWN || type == GOOME_UP ? 1 : 0;
    goome_push(g, &e);
}

static void script(int f)
{
    switch (f) {
    case 2: ev(GOOME_MOTION, 250, 25), ev(GOOME_DOWN, 250, 25); break;
    case 3: ev(GOOME_MOTION, 280, 47); break;
    case 4: ev(GOOME_MOTION, 291, 60); break;
    case 5: ev(GOOME_UP, 291, 60); break;
    case 7: ev(GOOME_MOTION, 250, 275), ev(GOOME_DOWN, 250, 275); break;
    case 8: ev(GOOME_MOTION, 262, 284); break;
    case 9: ev(GOOME_UP, 262, 284); break;
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

static void show(const char *name, const goome_ui_item *it)
{
    printf("%s %.1f %.1f %.1f %.1f %d%d%d%d%d %.1f %.1f %.1f %.1f\n", name, it->x, it->y, it->w, it->h, it->hovered, it->pressed, it->held,
           it->released, it->clicked, it->dx, it->dy, it->drag_x, it->drag_y);
}

int main(void)
{
    int err;
    g = goome_open(&(goome_opts){.mode = GOOME_MODE_OFFSCREEN, .title = "style", .width = 400, .height = 300, .scale = 1}, &err);
    if (!g) return 1;
    goome_ui *u = goome_ui_new(g);
    goome_theme *th = goome_ui_theme(u);
    th->anim_ms = 0, th->font = NULL, th->font_size = 14;
    uint32_t px[64];
    for (int i = 0; i < 64; i++) px[i] = (i % 9) ? 0xFF3050A0 : 0xFFF0C040;
    goome_bitmap bmp;
    if (goome_bitmap_from_argb(px, 8, 8, &bmp) != GOOME_OK) return 1;
    int chk = 1;
    double amt = 0.4;
    for (int f = 0; f < 12; f++) {
        script(f);
        goome_event e;
        while (goome_poll(g, &e, 0) > 0) goome_ui_feed(u, &e);
        if (!goome_ui_begin(u, 0)) continue;
        goome_ui_button(u, "Plain");
        goome_ui_same_line(u);
        goome_ui_push_num(u, GOOME_S_RADIUS, 0);
        goome_ui_button(u, "Square");
        goome_ui_pop(u, 1);
        goome_ui_same_line(u);
        goome_ui_push_radii(u, (goome_radii){16, 3, 16, 3});
        goome_ui_button(u, "Leaf");
        goome_ui_pop(u, 1);
        goome_ui_push_color(u, GOOME_S_ACCENT, 0xFFFF6FA8);
        goome_ui_push_color(u, GOOME_S_ACCENT_TEXT, 0xFF2A0614);
        goome_ui_push_num(u, GOOME_S_PAD, 9);
        goome_ui_checkbox(u, "Pink", &chk);
        goome_ui_slider(u, "Amount", &amt, 0, 1, "%.2f");
        goome_ui_pop(u, 3);
        goome_skin sk = {&bmp, 3, 3, 3, 3};
        goome_ui_push_skin(u, GOOME_SKIN_BUTTON, &sk);
        goome_ui_push_font(u, NULL);
        goome_ui_button(u, "Skinned");
        goome_ui_pop(u, 2);
        goome_theme t = *goome_ui_theme(u);
        goome_ui_theme_light(&t);
        t.radius = 2, t.font = NULL, t.font_size = 14, t.anim_ms = 0;
        goome_ui_push_theme(u, &t);
        goome_ui_button(u, "Light");
        goome_ui_pop(u, 1);
        goome_ui_size(u, 120, 0);
        goome_ui_button(u, "Wide");

        double *v = goome_ui_store(u, "pos", 3);
        goome_ui_item a, b, c;
        goome_ui_pos(u, 220, 10);
        goome_ui_custom(u, "lock", 60, 30, GOOME_ITEM_DRAG_X, &a);
        if (a.held) v[0] += a.dx;
        if (a.released) v[2] += 1;
        goome_ui_pos(u, 220 + v[1], 250);
        goome_ui_custom(u, "free", 40, 40, GOOME_ITEM_DRAG_X | GOOME_ITEM_DRAG_Y, &b);
        if (b.held) v[1] += b.dx;
        goome_ui_custom(u, "after", 50, 20, 0, &c);
        goome_canvas *k = goome_ui_canvas(u);
        if (k) {
            goome_draw_rrect(k, a.x + v[0], a.y, a.w, a.h, goome_radius(6), a.held ? 0xFFFF7A59 : 0xFF4FB3F7);
            goome_draw_circle(k, b.x + b.w / 2, b.y + b.h / 2, 18, b.held ? 0xFFE8D85A : 0xFF6FDC5F);
        }
        goome_ui_push_num(u, GOOME_S_GAP, 3);
        goome_ui_end(u);
        if (f >= 2 && f <= 9) {
            char n[16];
            snprintf(n, sizeof(n), "lock%d", f);
            show(n, &a);
            snprintf(n, sizeof(n), "free%d", f);
            show(n, &b);
        }
        if (f == 11) show("after", &c);
    }
    double *v = goome_ui_store(u, "pos", 3);
    goome_image fr;
    if (goome_frame(g, &fr) != GOOME_OK) return 1;
    printf("store %.1f %.1f %.1f\n", v[0], v[1], v[2]);
    printf("end %08x\n", fnv(&fr));
    goome_bitmap_free(&bmp);
    goome_ui_free(u);
    goome_close(g);
    return 0;
}
