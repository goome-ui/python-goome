import ctypes
import os
import sys
from ctypes import (
    POINTER,
    Structure,
    c_char,
    c_char_p,
    c_double,
    c_int,
    c_long,
    c_size_t,
    c_uint32,
    c_void_p,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def lib_name():
    if sys.platform == "win32":
        return "goome.dll"
    if sys.platform == "darwin":
        return "libgoome.dylib"
    return "libgoome.so"


class Opts(Structure):
    _fields_ = [
        ("title", c_char_p),
        ("backend", c_int),
        ("state_dir", c_char_p),
        ("no_capture", c_int),
        ("capture_fps", c_int),
        ("hide_self", c_int),
        ("test_frames", c_char_p),
        ("test_script", c_char_p),
        ("test_shots", c_char_p),
    ]


class RectS(Structure):
    _fields_ = [("x", c_int), ("y", c_int), ("w", c_int), ("h", c_int)]


class MonitorS(Structure):
    _fields_ = [
        ("id", c_int),
        ("name", c_char * 64),
        ("area", RectS),
        ("scale", c_double),
        ("pw", c_int),
        ("ph", c_int),
        ("rotation", c_int),
    ]


class ImageS(Structure):
    _fields_ = [
        ("px", POINTER(c_uint32)),
        ("w", c_int),
        ("h", c_int),
        ("stride", c_int),
        ("area", RectS),
        ("mon", c_int),
        ("has_self", c_int),
        ("has_cursor", c_int),
        ("cursor", RectS),
    ]


class CanvasS(Structure):
    _fields_ = [
        ("px", POINTER(c_uint32)),
        ("w", c_int),
        ("h", c_int),
        ("stride", c_int),
        ("ox", c_double),
        ("oy", c_double),
        ("scale", c_double),
        ("mon", c_int),
        ("dx0", c_int),
        ("dy0", c_int),
        ("dx1", c_int),
        ("dy1", c_int),
        ("cx0", c_int),
        ("cy0", c_int),
        ("cx1", c_int),
        ("cy1", c_int),
        ("kx0", c_int),
        ("ky0", c_int),
        ("kx1", c_int),
        ("ky1", c_int),
        ("nclip", c_int),
        ("clips", (c_int * 4) * 16),
    ]


class EventS(Structure):
    _fields_ = [
        ("type", c_int),
        ("x", c_double),
        ("y", c_double),
        ("mon", c_int),
        ("button", c_int),
        ("dy", c_int),
        ("key", c_int),
        ("mods", c_int),
        ("text", c_char * 8),
        ("id", c_int),
        ("msg", c_char * 64),
    ]


class PacerS(Structure):
    _fields_ = [("next", c_long), ("fps", c_int)]


class RadiiS(Structure):
    _fields_ = [("tl", c_double), ("tr", c_double), ("br", c_double), ("bl", c_double)]


class BitmapS(Structure):
    _fields_ = [
        ("px", POINTER(c_uint32)),
        ("w", c_int),
        ("h", c_int),
        ("stride", c_int),
        ("owned", c_int),
    ]


THEME_COLORS = ("bg", "panel", "border", "text", "text_dim", "accent", "accent_text", "hover", "active", "input_bg", "shadow")
THEME_SIZES = ("radius", "pad", "gap", "border_width", "font_size", "shadow_blur", "anim_ms")


class ThemeS(Structure):
    _fields_ = [(n, c_uint32) for n in THEME_COLORS] + [(n, c_double) for n in THEME_SIZES] + [("font", c_void_p)]


STRUCTS = {
    "goome_opts": Opts,
    "goome_rect": RectS,
    "goome_monitor": MonitorS,
    "goome_image": ImageS,
    "goome_canvas": CanvasS,
    "goome_event": EventS,
    "goome_pacer": PacerS,
    "goome_radii": RadiiS,
    "goome_bitmap": BitmapS,
    "goome_theme": ThemeS,
}

P = c_void_p
CP = POINTER(CanvasS)
D = c_double
I = c_int
S = c_char_p
U = c_uint32
PD = POINTER(c_double)
PI = POINTER(c_int)
PU = POINTER(c_uint32)

PROTOS = {
    "goome_open": (P, [POINTER(Opts), PI]),
    "goome_close": (None, [P]),
    "goome_error": (S, [P]),
    "goome_strerror": (S, [I]),
    "goome_backend_name": (S, [P]),
    "goome_caps": (I, [P]),
    "goome_monitors": (I, [P, POINTER(MonitorS), I]),
    "goome_capture": (I, [P, I, POINTER(RectS), POINTER(ImageS)]),
    "goome_alpha_at": (I, [P, D, D]),
    "goome_begin": (CP, [P, I]),
    "goome_end": (I, [P, CP, POINTER(RectS), I]),
    "goome_damage": (None, [CP, POINTER(RectS)]),
    "goome_poll": (I, [P, POINTER(EventS), I]),
    "goome_pointer": (I, [P, PD, PD, PI]),
    "goome_keyboard": (I, [P, I]),
    "goome_hotkey": (I, [P, S, I]),
    "goome_parse_combo": (I, [S, PI, PI]),
    "goome_control_path": (S, [P]),
    "goome_send": (I, [S, S]),
    "goome_pace": (I, [POINTER(PacerS), I]),
    "goome_now_ms": (c_long, []),
    "goome_save_ppm": (I, [S, PU, I, I, I]),
    "goome_clear": (None, [CP]),
    "goome_draw_rect": (None, [CP, D, D, D, D, U]),
    "goome_draw_round_rect": (None, [CP, D, D, D, D, D, U]),
    "goome_draw_frame": (None, [CP, D, D, D, D, D, U]),
    "goome_draw_line": (None, [CP, D, D, D, D, D, U]),
    "goome_draw_triangle": (None, [CP, D, D, D, D, D, D, U]),
    "goome_draw_image": (None, [CP, D, D, D, D, PU, I, I]),
    "goome_erase": (None, [CP, D, D, D, D]),
    "goome_draw_text": (D, [CP, D, D, S, I, U]),
    "goome_text_width": (D, [CP, S, I]),
    "goome_set_font": (None, [I]),
    "goome_font_count": (I, []),
    "goome_canvas_blit": (None, [CP, CP, D, D, D]),
    "goome_radius": (RadiiS, [D]),
    "goome_clip_push": (None, [CP, D, D, D, D]),
    "goome_clip_pop": (None, [CP]),
    "goome_draw_rrect": (None, [CP, D, D, D, D, RadiiS, U]),
    "goome_draw_rrect_line": (None, [CP, D, D, D, D, RadiiS, D, U]),
    "goome_draw_rrect_grad": (None, [CP, D, D, D, D, RadiiS, U, U, I]),
    "goome_draw_shadow": (None, [CP, D, D, D, D, D, D, U]),
    "goome_draw_circle": (None, [CP, D, D, D, U]),
    "goome_draw_ring": (None, [CP, D, D, D, D, U]),
    "goome_draw_arc": (None, [CP, D, D, D, D, D, D, U]),
    "goome_draw_poly": (None, [CP, PD, I, U]),
    "goome_bitmap_load": (I, [S, POINTER(BitmapS)]),
    "goome_bitmap_load_mem": (I, [c_void_p, c_size_t, POINTER(BitmapS)]),
    "goome_bitmap_error": (S, []),
    "goome_bitmap_from_argb": (I, [PU, I, I, POINTER(BitmapS)]),
    "goome_bitmap_free": (None, [POINTER(BitmapS)]),
    "goome_draw_bitmap": (None, [CP, POINTER(BitmapS), D, D, D, D, RadiiS, U]),
    "goome_draw_bitmap_part": (None, [CP, POINTER(BitmapS), I, I, I, I, D, D, D, D, U]),
    "goome_font_load": (P, [S]),
    "goome_font_load_index": (P, [S, I]),
    "goome_font_load_mem": (P, [c_void_p, c_size_t, I]),
    "goome_font_system": (P, [S]),
    "goome_font_free": (None, [P]),
    "goome_text": (D, [CP, P, D, D, D, S, U]),
    "goome_text_measure": (D, [P, D, S, PD]),
    "goome_text_line_height": (D, [P, D]),
    "goome_ui_new": (P, [P]),
    "goome_ui_free": (None, [P]),
    "goome_ui_theme": (POINTER(ThemeS), [P]),
    "goome_ui_theme_dark": (None, [POINTER(ThemeS)]),
    "goome_ui_theme_light": (None, [POINTER(ThemeS)]),
    "goome_ui_feed": (I, [P, POINTER(EventS)]),
    "goome_ui_begin": (CP, [P, I]),
    "goome_ui_end": (None, [P]),
    "goome_ui_hit": (None, [P, D, D, D, D]),
    "goome_ui_animating": (I, [P]),
    "goome_ui_window": (I, [P, S, PD, PD, PD, PD, I, PI]),
    "goome_ui_window_end": (None, [P]),
    "goome_ui_row": (None, [P, I]),
    "goome_ui_same_line": (None, [P]),
    "goome_ui_space": (None, [P, D]),
    "goome_ui_separator": (None, [P]),
    "goome_ui_width": (None, [P, D]),
    "goome_ui_label": (None, [P, S]),
    "goome_ui_heading": (None, [P, S]),
    "goome_ui_wrapped": (None, [P, S]),
    "goome_ui_button": (I, [P, S]),
    "goome_ui_image_button": (I, [P, S, POINTER(BitmapS), D, D]),
    "goome_ui_image": (None, [P, POINTER(BitmapS), D, D, D]),
    "goome_ui_checkbox": (I, [P, S, PI]),
    "goome_ui_toggle": (I, [P, S, PI]),
    "goome_ui_radio": (I, [P, S, PI, I]),
    "goome_ui_slider": (I, [P, S, PD, D, D, S]),
    "goome_ui_slider_int": (I, [P, S, PI, I, I]),
    "goome_ui_input": (I, [P, S, c_char_p, I]),
    "goome_ui_combo": (I, [P, S, PI, POINTER(c_char_p), I]),
    "goome_ui_selectable": (I, [P, S, I]),
    "goome_ui_tabs": (I, [P, S, POINTER(c_char_p), I, PI]),
    "goome_ui_collapsing": (I, [P, S, PI]),
    "goome_ui_progress": (None, [P, D, S]),
    "goome_ui_color": (I, [P, S, PU]),
    "goome_ui_tooltip": (None, [P, S]),
    "goome_ui_hovered": (I, [P]),
    "goome_ui_scroll_begin": (I, [P, S, D]),
    "goome_ui_scroll_end": (None, [P]),
    "goome_ui_push_id": (None, [P, S]),
    "goome_ui_pop_id": (None, [P]),
}


def candidates():
    env = os.environ.get("GOOME_LIB")
    if env:
        return [env]
    return [os.path.join(HERE, "_native", lib_name())]


def load():
    tried = []
    for path in candidates():
        if not os.path.isfile(path):
            tried.append(path + " (not there)")
            continue
        try:
            return ctypes.CDLL(path), path
        except OSError as e:
            tried.append("%s (%s)" % (path, e))
    raise OSError(
        "cant find the goome native library, tried: %s. reinstall the package so it builds one, "
        "run ./build.sh in the repo, or point GOOME_LIB at a libgoome you built" % "; ".join(tried)
    )


def bind(lib):
    missing = []
    for name, (res, args) in PROTOS.items():
        try:
            f = getattr(lib, name)
        except AttributeError:
            missing.append(name)
            continue
        f.restype = res
        f.argtypes = args
    if missing:
        raise OSError("this goome library is missing %s, its probably too old" % ", ".join(missing))
    return lib


lib, path = load()
bind(lib)
