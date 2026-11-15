#define GOOME_IMPLEMENTATION
#include "goome.h"

#include <stdio.h>
#include <string.h>

static goome *g;
static goome_ui *u;

static uint32_t fnv(const goome_image *f)
{
    uint32_t v = 2166136261u;
    for (int y = 0; y < f->h; y++) {
        const unsigned char *p = (const unsigned char *)(f->px + (size_t)y * f->stride);
        for (int i = 0; i < f->w * 4; i++) v = (v ^ p[i]) * 16777619u;
    }
    return v;
}

static void key(int k, int mods)
{
    goome_event e;
    memset(&e, 0, sizeof(e));
    e.type = GOOME_KEY, e.key = k, e.mods = mods;
    if (k >= 32 && k < 127 && !(mods & GOOME_CTRL)) e.text[0] = (char)k;
    goome_push(g, &e);
}

static void feed(void)
{
    goome_event e;
    while (goome_poll(g, &e, 0) > 0) goome_ui_feed(u, &e);
}

static void widgets(void)
{
    static const char *const tabs[] = {"Play", "Stats", "Gear"};
    static const char *const modes[] = {"Story", "Arena", "Sandbox"};
    char name[32] = "sev", pass[32] = "hunter22";
    int tab = 1, sound = 1, online = 0, level = 2, mode = 1;
    double vol = 40;
    goome_ui_tabs(u, "tabs", tabs, 3, &tab);
    goome_ui_heading(u, "Player one");
    goome_ui_input(u, "Name", name, sizeof(name));
    goome_ui_input_ex(u, "Password", pass, sizeof(pass), GOOME_INPUT_PASSWORD, "8 or more");
    goome_ui_row(u, 2);
    goome_ui_checkbox(u, "Sound", &sound);
    goome_ui_toggle(u, "Online", &online);
    goome_ui_radio(u, "Easy", &level, 0);
    goome_ui_same_line(u);
    goome_ui_radio(u, "Hard", &level, 2);
    goome_ui_slider(u, "Volume", &vol, 0, 100, "%.0f");
    goome_ui_combo(u, "Mode", &mode, modes, 3);
    goome_ui_progress(u, 0.6, "loading");
    goome_ui_row(u, 2);
    goome_ui_button(u, "Start");
    goome_ui_badge(u, "new", 0);
}

static uint32_t look(const goome_theme *t, double zoom)
{
    for (int f = 0; f < 3; f++) {
        feed();
        if (!goome_ui_begin(u, 0)) continue;
        goome_ui_push_theme(u, t);
        if (zoom != 1) goome_ui_scale(u, zoom);
        double x = 6, y = 6, w = 340, h = 0;
        if (goome_ui_window(u, "look", &x, &y, &w, &h, 0, NULL)) widgets();
        goome_ui_window_end(u);
        goome_ui_pop(u, 1);
        goome_ui_end(u);
    }
    goome_image fr;
    if (goome_frame(g, &fr) != GOOME_OK) return 0;
    return fnv(&fr);
}

static uint32_t typed(int flags, const char *start, const char *type, char *out, int *ret)
{
    char buf[32];
    snprintf(buf, sizeof(buf), "%s", start);
    int focus = 1, n = 0, ks[16], ms[16];
    *ret = 0;
    for (const char *p = type; *p && n < 16; p++, n++) {
        if (*p == '^') ks[n] = p[1], ms[n] = GOOME_CTRL, p++;
        else if (*p == '\n') ks[n] = GOOME_K_ENTER, ms[n] = 0;
        else ks[n] = (unsigned char)*p, ms[n] = 0;
    }
    for (int f = 0; f < n + 3; f++) {
        if (f >= 1 && f - 1 < n) key(ks[f - 1], ms[f - 1]);
        feed();
        if (!goome_ui_begin(u, 0)) continue;
        double x = 6, y = 6, w = 300, h = 0;
        if (goome_ui_window(u, "typing", &x, &y, &w, &h, 0, NULL)) {
            goome_ui_button(u, "Hi");
            if (focus) goome_ui_set_focus(u), focus = 0;
            int r = goome_ui_input_ex(u, "in", buf, sizeof(buf), flags | GOOME_INPUT_NO_SELECT_ON_FOCUS, "hint here");
            if (r) *ret = r;
        }
        goome_ui_window_end(u);
        goome_ui_end(u);
    }
    snprintf(out, 32, "%s", buf);
    goome_image fr;
    if (goome_frame(g, &fr) != GOOME_OK) return 0;
    return fnv(&fr);
}

int main(void)
{
    int err;
    g = goome_open(&(goome_opts){.mode = GOOME_MODE_OFFSCREEN, .title = "looks", .width = 360, .height = 420, .scale = 1}, &err);
    if (!g) return 1;
    u = goome_ui_new(g);
    goome_theme *th = goome_ui_theme(u);
    th->anim_ms = 0, th->font = NULL, th->font_size = 14;
    goome_ui_cfg(u)->blink_ms = 0;
    for (int i = 0; i < GOOME_PRESET_COUNT; i++) {
        goome_theme t = *th;
        goome_ui_theme_preset(&t, i);
        t.anim_ms = 0;
        printf("preset%d %08x\n", i, look(&t, 1));
    }
    goome_theme t;
    memset(&t, 0, sizeof(t));
    goome_ui_theme_make(&t, 0xFF8B5CF6, 1, 12);
    t.anim_ms = 0;
    printf("make_dark %08x\n", look(&t, 1));
    printf("make_dark_big %08x\n", look(&t, 1.25));
    memset(&t, 0, sizeof(t));
    goome_ui_theme_make(&t, 0xFFF2D04A, 0, 20);
    t.anim_ms = 0;
    printf("make_light %08x\n", look(&t, 1));
    printf("make_light_small %08x\n", look(&t, 0.8));

    char out[32];
    int ret;
    uint32_t hv = typed(0, "abc", "", out, &ret);
    printf("plain %08x %s %d\n", hv, out, ret);
    hv = typed(GOOME_INPUT_PASSWORD, "abc", "", out, &ret);
    printf("pass_abc %08x %s %d\n", hv, out, ret);
    hv = typed(GOOME_INPUT_PASSWORD, "xyz", "", out, &ret);
    printf("pass_xyz %08x %s %d\n", hv, out, ret);
    goome_ui_cfg(u)->mask = "#";
    hv = typed(GOOME_INPUT_PASSWORD, "abc", "d", out, &ret);
    printf("pass_mask %08x %s %d\n", hv, out, ret);
    goome_ui_cfg(u)->mask = NULL;
    hv = typed(GOOME_INPUT_PASSWORD | GOOME_INPUT_ENTER_RETURNS, "abc", "\n", out, &ret);
    printf("pass_enter %08x %s %d\n", hv, out, ret);
    hv = typed(GOOME_INPUT_NUMBER, "12", "3a4", out, &ret);
    printf("number %08x %s %d\n", hv, out, ret);
    hv = typed(GOOME_INPUT_READONLY, "eu-west", "xy", out, &ret);
    printf("readonly %08x %s %d\n", hv, out, ret);

    hv = typed(0, "hello", "^qx", out, &ret);
    printf("before_bind %08x %s %d\n", hv, out, ret);
    goome_ui_bind(u, GOOME_ACT_SELECT_ALL, "alt+l, ctrl+q");
    hv = typed(0, "hello", "^qx", out, &ret);
    printf("after_bind %08x %s %d\n", hv, out, ret);
    goome_ui_bind(u, GOOME_ACT_SELECT_ALL, NULL);
    hv = typed(0, "hello", "^ax", out, &ret);
    printf("unbound %08x %s %d\n", hv, out, ret);

    goome_ui_free(u);
    goome_close(g);
    return 0;
}
