#include <stdio.h>
#include <stddef.h>

#include "goome.h"

#define S(t) printf("%s %d\n", #t, (int)sizeof(t))
#define F(t, f) printf("%s.%s %d %d\n", #t, #f, (int)offsetof(t, f), (int)sizeof(((t *)0)->f))

int main(void)
{
    S(goome_opts);
    F(goome_opts, title);
    F(goome_opts, backend);
    F(goome_opts, state_dir);
    F(goome_opts, no_capture);
    F(goome_opts, capture_fps);
    F(goome_opts, hide_self);
    F(goome_opts, test_frames);
    F(goome_opts, test_script);
    F(goome_opts, test_shots);
    S(goome_rect);
    F(goome_rect, x);
    F(goome_rect, y);
    F(goome_rect, w);
    F(goome_rect, h);
    S(goome_monitor);
    F(goome_monitor, id);
    F(goome_monitor, name);
    F(goome_monitor, area);
    F(goome_monitor, scale);
    F(goome_monitor, pw);
    F(goome_monitor, ph);
    F(goome_monitor, rotation);
    S(goome_image);
    F(goome_image, px);
    F(goome_image, w);
    F(goome_image, h);
    F(goome_image, stride);
    F(goome_image, area);
    F(goome_image, mon);
    F(goome_image, has_self);
    F(goome_image, has_cursor);
    F(goome_image, cursor);
    S(goome_canvas);
    F(goome_canvas, px);
    F(goome_canvas, w);
    F(goome_canvas, h);
    F(goome_canvas, stride);
    F(goome_canvas, ox);
    F(goome_canvas, oy);
    F(goome_canvas, scale);
    F(goome_canvas, mon);
    F(goome_canvas, dx0);
    F(goome_canvas, dy0);
    F(goome_canvas, dx1);
    F(goome_canvas, dy1);
    F(goome_canvas, cx0);
    F(goome_canvas, cy0);
    F(goome_canvas, cx1);
    F(goome_canvas, cy1);
    F(goome_canvas, kx0);
    F(goome_canvas, ky0);
    F(goome_canvas, kx1);
    F(goome_canvas, ky1);
    F(goome_canvas, nclip);
    F(goome_canvas, clips);
    S(goome_event);
    F(goome_event, type);
    F(goome_event, x);
    F(goome_event, y);
    F(goome_event, mon);
    F(goome_event, button);
    F(goome_event, dy);
    F(goome_event, key);
    F(goome_event, mods);
    F(goome_event, text);
    F(goome_event, id);
    F(goome_event, msg);
    S(goome_pacer);
    F(goome_pacer, next);
    F(goome_pacer, fps);
    S(goome_radii);
    F(goome_radii, tl);
    F(goome_radii, tr);
    F(goome_radii, br);
    F(goome_radii, bl);
    S(goome_bitmap);
    F(goome_bitmap, px);
    F(goome_bitmap, w);
    F(goome_bitmap, h);
    F(goome_bitmap, stride);
    F(goome_bitmap, owned);
    S(goome_theme);
    F(goome_theme, bg);
    F(goome_theme, panel);
    F(goome_theme, border);
    F(goome_theme, text);
    F(goome_theme, text_dim);
    F(goome_theme, accent);
    F(goome_theme, accent_text);
    F(goome_theme, hover);
    F(goome_theme, active);
    F(goome_theme, input_bg);
    F(goome_theme, shadow);
    F(goome_theme, radius);
    F(goome_theme, pad);
    F(goome_theme, gap);
    F(goome_theme, border_width);
    F(goome_theme, font_size);
    F(goome_theme, shadow_blur);
    F(goome_theme, anim_ms);
    F(goome_theme, font);
    return 0;
}
