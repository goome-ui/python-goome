import sys

import goome


def main(argv):
    if len(argv) < 2:
        print("usage: grab.py [monitor] [x y w h] out.ppm", file=sys.stderr)
        return 2
    nums = []
    for a in argv[1:-1][:5]:
        try:
            nums.append(int(a))
        except ValueError:
            nums.append(0)
    try:
        g = goome.open("goome grab")
    except goome.GoomeError as e:
        print("cant open: %s" % e, file=sys.stderr)
        return 1
    with g:
        mon = nums[0] if len(nums) in (1, 5) else 0
        rect = nums[-4:] if len(nums) >= 4 else None
        try:
            img = g.capture_wait(mon, rect)
            img.save_ppm(argv[-1])
        except goome.GoomeError as e:
            print("grab failed: %s (%s)" % (goome.strerror(e.code), g.error), file=sys.stderr)
            return 1
        a = img.area
        print("%dx%d px of %d,%d %dx%d on monitor %d%s%s" % (img.w, img.h, a.x, a.y, a.w, a.h, mon,
              ", has our overlay" if img.has_self else "", ", has the cursor" if img.has_cursor else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
