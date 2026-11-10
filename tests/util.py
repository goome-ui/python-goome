import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
ROOT = os.path.dirname(HERE)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def data(name):
    with open(os.path.join(DATA, name), "rb") as f:
        return f.read()


def fnv_bytes(b, v=2166136261):
    for c in b:
        v = ((v ^ c) * 16777619) & 0xFFFFFFFF
    return v


def fnv(view, w, h, stride=None):
    stride = w if stride is None else stride
    v = 2166136261
    if sys.byteorder == "little":
        for y in range(h):
            v = fnv_bytes(view[y * stride : y * stride + w].tobytes(), v)
        return v
    for y in range(h):
        row = view[y * stride : y * stride + w]
        for x in range(w):
            p = row[x]
            for k in range(4):
                v = ((v ^ ((p >> (k * 8)) & 255)) * 16777619) & 0xFFFFFFFF
    return v


def zero_rows(view, stride, h, x0, x1):
    for y in range(h):
        if any(view[y * stride + x0 : y * stride + x1].tolist()):
            return False
    return True
