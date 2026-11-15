#include <stdio.h>
#include <stddef.h>

#include "goome.h"

#define S(t) printf("%s %d\n", #t, (int)sizeof(t))
#define F(t, f) printf("%s.%s %d %d\n", #t, #f, (int)offsetof(t, f), (int)sizeof(((t *)0)->f))

int main(void)
{
    S(goome_opts);
    F(goome_opts, title); F(goome_opts, backend); F(goome_opts, state_dir); F(goome_opts, no_capture);
    F(goome_opts, capture_fps); F(goome_opts, hide_self); F(goome_opts, test_frames); F(goome_opts, test_script);
    F(goome_opts, test_shots); F(goome_opts, mode); F(goome_opts, width); F(goome_opts, height);
    F(goome_opts, min_width); F(goome_opts, min_height); F(goome_opts, window_flags); F(goome_opts, scale);
    S(goome_rect);
    F(goome_rect, x); F(goome_rect, y); F(goome_rect, w); F(goome_rect, h);
    S(goome_monitor);
    F(goome_monitor, id); F(goome_monitor, name); F(goome_monitor, area); F(goome_monitor, scale); F(goome_monitor, pw);
    F(goome_monitor, ph); F(goome_monitor, rotation);
    S(goome_image);
    F(goome_image, px); F(goome_image, w); F(goome_image, h); F(goome_image, stride); F(goome_image, area);
    F(goome_image, mon); F(goome_image, has_self); F(goome_image, has_cursor); F(goome_image, cursor);
    S(goome_canvas);
    F(goome_canvas, px); F(goome_canvas, w); F(goome_canvas, h); F(goome_canvas, stride); F(goome_canvas, ox);
    F(goome_canvas, oy); F(goome_canvas, scale); F(goome_canvas, mon); F(goome_canvas, dx0); F(goome_canvas, dy0);
    F(goome_canvas, dx1); F(goome_canvas, dy1); F(goome_canvas, cx0); F(goome_canvas, cy0); F(goome_canvas, cx1);
    F(goome_canvas, cy1); F(goome_canvas, kx0); F(goome_canvas, ky0); F(goome_canvas, kx1); F(goome_canvas, ky1);
    F(goome_canvas, nclip); F(goome_canvas, clips);
    S(goome_event);
    F(goome_event, type); F(goome_event, x); F(goome_event, y); F(goome_event, mon); F(goome_event, button);
    F(goome_event, dy); F(goome_event, key); F(goome_event, mods); F(goome_event, text); F(goome_event, id);
    F(goome_event, msg);
    S(goome_pacer);
    F(goome_pacer, next); F(goome_pacer, fps);
    S(goome_radii);
    F(goome_radii, tl); F(goome_radii, tr); F(goome_radii, br); F(goome_radii, bl);
    S(goome_bitmap);
    F(goome_bitmap, px); F(goome_bitmap, w); F(goome_bitmap, h); F(goome_bitmap, stride); F(goome_bitmap, owned);
    S(goome_theme);
    F(goome_theme, bg); F(goome_theme, panel); F(goome_theme, border); F(goome_theme, text); F(goome_theme, text_dim);
    F(goome_theme, accent); F(goome_theme, accent_text); F(goome_theme, hover); F(goome_theme, active);
    F(goome_theme, input_bg); F(goome_theme, shadow); F(goome_theme, radius); F(goome_theme, pad); F(goome_theme, gap);
    F(goome_theme, border_width); F(goome_theme, font_size); F(goome_theme, shadow_blur); F(goome_theme, anim_ms);
    F(goome_theme, font); F(goome_theme, skin_button); F(goome_theme, skin_panel); F(goome_theme, skin_input);
    F(goome_theme, icon); F(goome_theme, icon_tint); F(goome_theme, skin_checkbox); F(goome_theme, skin_radio);
    F(goome_theme, skin_toggle); F(goome_theme, skin_slider); F(goome_theme, skin_slider_fill); F(goome_theme, skin_scrollbar);
    F(goome_theme, skin_tab); F(goome_theme, skin_titlebar); F(goome_theme, skin_tooltip); F(goome_theme, skin_menu);
    F(goome_theme, skin_popup);
    F(goome_theme, focus); F(goome_theme, select); F(goome_theme, caret); F(goome_theme, link); F(goome_theme, badge);
    F(goome_theme, toast); F(goome_theme, tooltip); F(goome_theme, danger); F(goome_theme, knob); F(goome_theme, dim);
    F(goome_theme, check_size); F(goome_theme, check_radius); F(goome_theme, toggle_w); F(goome_theme, toggle_h); F(goome_theme, slider_h);
    F(goome_theme, slider_track); F(goome_theme, knob_size); F(goome_theme, scroll_w); F(goome_theme, scroll_min); F(goome_theme, item_h);
    F(goome_theme, menu_item_h); F(goome_theme, tab_h); F(goome_theme, win_title_h); F(goome_theme, app_title_h); F(goome_theme, menubar_h);
    F(goome_theme, statusbar_h); F(goome_theme, focus_w); F(goome_theme, focus_gap); F(goome_theme, sep_w); F(goome_theme, grip);
    F(goome_theme, indent); F(goome_theme, plot_w); F(goome_theme, spinner); F(goome_theme, caret_w); F(goome_theme, win_min_w);
    F(goome_theme, win_min_h); F(goome_theme, pop_gap); F(goome_theme, menu_gap); F(goome_theme, tip_pad_x); F(goome_theme, tip_pad_y);
    F(goome_theme, tip_x); F(goome_theme, tip_y); F(goome_theme, tip_radius); F(goome_theme, shadow_x); F(goome_theme, shadow_y);
    F(goome_theme, align); F(goome_theme, heading_size); F(goome_theme, small_size); F(goome_theme, ease); F(goome_theme, hover_ms);
    F(goome_theme, press_ms); F(goome_theme, popup_ms); F(goome_theme, collapse_ms); F(goome_theme, toast_fade_ms); F(goome_theme, font_heading);
    F(goome_theme, font_mono); F(goome_theme, font_small);
    S(goome_skin);
    F(goome_skin, bm); F(goome_skin, l); F(goome_skin, t); F(goome_skin, r); F(goome_skin, b);
    S(goome_ui_item);
    F(goome_ui_item, x); F(goome_ui_item, y); F(goome_ui_item, w); F(goome_ui_item, h); F(goome_ui_item, hovered);
    F(goome_ui_item, pressed); F(goome_ui_item, held); F(goome_ui_item, released); F(goome_ui_item, clicked);
    F(goome_ui_item, double_clicked); F(goome_ui_item, right_clicked); F(goome_ui_item, focused); F(goome_ui_item, mx);
    F(goome_ui_item, my); F(goome_ui_item, dx); F(goome_ui_item, dy); F(goome_ui_item, drag_x); F(goome_ui_item, drag_y);
    F(goome_ui_item, key);
    S(goome_combo);
    F(goome_combo, key); F(goome_combo, mods);
    S(goome_ui_config);
    F(goome_ui_config, tip_delay_ms); F(goome_ui_config, dbl_click_ms); F(goome_ui_config, dbl_click_px); F(goome_ui_config, drag_px); F(goome_ui_config, repeat_delay_ms);
    F(goome_ui_config, repeat_ms); F(goome_ui_config, blink_ms); F(goome_ui_config, menu_delay_ms); F(goome_ui_config, toast_ms); F(goome_ui_config, scroll_lines);
    F(goome_ui_config, raise_on_click); F(goome_ui_config, esc_closes); F(goome_ui_config, tab_nav); F(goome_ui_config, focus_on_mouse); F(goome_ui_config, cursor);
    F(goome_ui_config, keys); F(goome_ui_config, ease); F(goome_ui_config, ease_user); F(goome_ui_config, mask);
    return 0;
}
