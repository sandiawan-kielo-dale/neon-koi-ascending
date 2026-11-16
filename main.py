#!/usr/bin/env python3
"""Make the AI judge excited — entry generator (make.fun bounty ai-excited-01).

Writes one 1024x1024 PNG to /output/entry.png (or sys.argv[1] if given).

The image is "Neon Koi Ascending": a vivid orange-and-white koi leaping
through a ring of gold fire over a moonlit ocean, under aurora ribbons and a
full moon, with drifting cherry-blossom petals. Built to excite a vision
judge: one unmistakable focal subject with a visible eye, extreme warm/cool
colour contrast, glow, and dense but organised detail.

Deterministic: fixed seed, no network, no clock, no file input. Two runs
write byte-identical output.
"""

import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = H = 1024
SEED = 20261116
OUT = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(w, h, stops):
    """stops: list of (y_fraction, (r, g, b)). Returns RGB array."""
    ys = np.linspace(0, 1, h)
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = ys[y]
        for i in range(len(stops) - 1):
            y0, c0 = stops[i]
            y1, c1 = stops[i + 1]
            if y0 <= t <= y1:
                f = 0.0 if y1 == y0 else (t - y0) / (y1 - y0)
                arr[y, :, :] = lerp(c0, c1, f)
                break
        else:
            arr[y, :, :] = stops[-1][1]
    return arr


def bezier(p0, p1, p2, n=120):
    """Quadratic Bezier points."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def fish_polygon(spine, widths):
    """Silhouette polygon from a spine polyline and half-widths."""
    left, right = [], []
    n = len(spine)
    for i, (x, y) in enumerate(spine):
        x2, y2 = spine[min(i + 1, n - 1)]
        x1, y1 = spine[max(i - 1, 0)]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = widths[i]
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))

    def smooth(pts):
        for _ in range(3):
            pts = [(0.25 * pts[max(i - 1, 0)][0] + 0.5 * pts[i][0] + 0.25 * pts[min(i + 1, len(pts) - 1)][0],
                    0.25 * pts[max(i - 1, 0)][1] + 0.5 * pts[i][1] + 0.25 * pts[min(i + 1, len(pts) - 1)][1])
                   for i in range(len(pts))]
        return pts

    return smooth(left) + smooth(right)[::-1]


def curved_lobe(base, tip, spread, bulge):
    """A flowing fin lobe: bezier out along `spread`, back via `bulge`."""
    # outward edge: base -> tip (control pulled sideways)
    out = bezier(base, (base[0] - 90, base[1] + spread * 0.7),
                 tip, n=24)
    # return edge: tip -> base (control pulled the other way)
    back = bezier(tip, (base[0] - 110, base[1] + bulge),
                  base, n=24)
    return out + back[1:]


def main():
    rng = random.Random(SEED)

    # ---- Background: deep indigo sky melting into a dark ocean ----
    base = vertical_gradient(W, H, [
        (0.00, (9, 12, 46)),
        (0.35, (16, 32, 84)),
        (0.62, (10, 58, 74)),   # horizon glow band
        (0.64, (6, 34, 52)),
        (1.00, (3, 12, 26)),
    ])
    img = Image.fromarray(base, "RGB").convert("RGBA")

    # ---- Aurora ribbons (blurred sinusoidal bands, upper sky) ----
    aur = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    da = ImageDraw.Draw(aur)
    for color, amp, phase, base_y, width in [
        ((57, 255, 136, 70), 46, 0.0, 180, 26),
        ((41, 216, 255, 64), 60, 1.4, 250, 34),
        ((255, 79, 216, 52), 38, 2.6, 130, 20),
    ]:
        pts = []
        for x in range(0, W + 8, 8):
            y = base_y + amp * math.sin(x / 170.0 + phase) + 18 * math.sin(x / 61.0 + phase * 2)
            pts.append((x, y))
        da.line(pts, fill=color, width=width, joint="curve")
    aur = aur.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(aur)

    # ---- Stars ----
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(st)
    for _ in range(190):
        x = rng.uniform(0, W)
        y = rng.uniform(0, 600)
        r = rng.choice([1, 1, 1, 2, 2, 3])
        a = rng.randint(90, 235)
        ds.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 225, a))
        if r == 3:
            ds.line([x - 7, y, x + 7, y], fill=(255, 250, 225, 110), width=1)
            ds.line([x, y - 7, x, y + 7], fill=(255, 250, 225, 110), width=1)
    img.alpha_composite(st)

    # ---- Full moon with halo (top right) ----
    moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dm = ImageDraw.Draw(moon)
    mx, my, mr = 798, 208, 92
    for r, a in [(150, 26), (128, 40), (108, 60)]:
        dm.ellipse([mx - r, my - r, mx + r, my + r], fill=(255, 232, 168, a))
    dm.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 244, 205, 255))
    for cx, cy, cr, shade in [(760, 180, 16, 235), (820, 240, 12, 238),
                               (800, 160, 9, 240), (770, 240, 10, 232)]:
        dm.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 233, 168, shade))
    moon = moon.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(moon)

    # ---- Moon reflection: shimmering column on the water ----
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(refl)
    for i in range(46):
        y = 660 + i * 8
        wdt = rng.uniform(26, 110) * (1 - i / 70.0)
        x0 = mx + rng.uniform(-38, 38)
        dr.line([x0 - wdt / 2, y, x0 + wdt / 2, y],
                fill=(255, 226, 150, rng.randint(50, 150)), width=3)
    refl = refl.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(refl)

    # ---- Water ripples ----
    rip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    drp = ImageDraw.Draw(rip)
    for _ in range(70):
        x = rng.uniform(0, W)
        y = rng.uniform(660, 1000)
        wdt = rng.uniform(40, 220)
        hgt = rng.uniform(5, 12)
        a = rng.randint(28, 90)
        col = (64, 220, 255, a) if rng.random() < 0.6 else (255, 200, 120, a)
        drp.arc([x - wdt / 2, y - hgt, x + wdt / 2, y + hgt],
                start=200, end=340, fill=col, width=2)
    img.alpha_composite(rip)

    # ---- Golden ring the koi leaps through ----
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(ring)
    cx, cy = 512, 545
    for r, a, wdt in [(238, 40, 26), (228, 90, 12), (222, 220, 5)]:
        dg.ellipse([cx - r, cy - r * 0.82, cx + r, cy + r * 0.82],
                   outline=(255, 176, 32, a), width=wdt)
    ring = ring.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(ring)
    # ring sparks
    sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dsp = ImageDraw.Draw(sp)
    for _ in range(26):
        ang = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(210, 245)
        x = cx + r * math.cos(ang)
        y = cy + r * 0.82 * math.sin(ang)
        s = rng.uniform(2, 6)
        dsp.ellipse([x - s, y - s, x + s, y + s], fill=(255, 214, 90, rng.randint(140, 255)))
    img.alpha_composite(sp)

    # ---- The koi ----
    # Spine: tail low-left -> head high-right (leaping up-right).
    spine = bezier((330, 800), (470, 660), (706, 402), n=140)
    n = len(spine)
    widths = []
    for i in range(n):
        t = i / (n - 1)  # 0 = tail, 1 = head
        # fat near the head third, tapering to a thin tail stalk
        w = 118 * math.sin(math.pi * (0.12 + 0.78 * t)) ** 0.9
        w *= (0.25 + 0.75 * min(1.0, t * 3.0)) if t < 0.35 else 1.0
        widths.append(max(w, 7))
    body = fish_polygon(spine, widths)

    koi = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dk = ImageDraw.Draw(koi)

    # Tail: two flowing translucent lobes behind the tail stalk.
    tail_base = spine[0]
    for tip, spread, bulge, alpha in [
        ((tail_base[0] - 225, tail_base[1] + 165), 1, 40, 205),
        ((tail_base[0] - 225, tail_base[1] - 135), -1, -30, 195),
    ]:
        lobe = curved_lobe(tail_base, tip, spread * 120, bulge)
        dk.polygon(lobe, fill=(255, 150, 60, alpha))
    # Tail fin rays
    for k in range(5):
        t = k / 4.0
        x0 = tail_base[0] - 30 - t * 150
        y0 = tail_base[1] + (t - 0.5) * 210
        dk.line([tail_base[0] - 10, tail_base[1], x0, y0],
                fill=(255, 190, 110, 130), width=3)

    # Body: orange base, then white belly, orange patches, black spots.
    dk.polygon(body, fill=(255, 107, 26, 255))
    # Rounded head cap so the snout is not flat-cut.
    hx, hy = spine[-1]
    dk.ellipse([hx - 52, hy - 48, hx + 52, hy + 48], fill=(255, 107, 26, 255))
    # Belly highlight along the lower edge of the body
    belly = []
    for i in range(0, n, 4):
        x, y = spine[i]
        x2, y2 = spine[min(i + 1, n - 1)]
        x1, y1 = spine[max(i - 1, 0)]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        belly.append((x - nx * widths[i] * 0.95, y - ny * widths[i] * 0.95))
    dk.line(belly, fill=(255, 246, 232, 140), width=18, joint="curve")
    # White patches on the back
    for (px, py, pr) in [(560, 560, 52), (640, 470, 40), (470, 690, 46)]:
        dk.ellipse([px - pr, py - pr * 0.7, px + pr, py + pr * 0.7],
                   fill=(255, 246, 232, 235))
    # Black spots
    for (px, py, pr) in [(600, 520, 26), (520, 640, 20), (680, 440, 15), (430, 720, 14)]:
        dk.ellipse([px - pr, py - pr * 0.7, px + pr, py + pr * 0.7],
                   fill=(20, 14, 10, 255))
    # Scale arcs: rows of small arcs along the body
    for i in range(8, n - 8, 10):
        x, y = spine[i]
        r = widths[i] * 0.55
        dk.arc([x - r, y - r * 0.7, x + r, y + r * 0.7],
               start=300, end=60, fill=(200, 80, 20, 90), width=2)
    # Dorsal fin: a curved hump along the top edge, mid-body.
    mid = spine[n // 2]
    fin = bezier((mid[0] - 78, mid[1] - 58), (mid[0] + 10, mid[1] - 128),
                 (mid[0] + 92, mid[1] - 52), n=20)
    fin += bezier((mid[0] + 92, mid[1] - 52), (mid[0] + 20, mid[1] - 28),
                  (mid[0] - 78, mid[1] - 58), n=12)[1:]
    dk.polygon(fin, fill=(255, 140, 40, 170))
    # Pectoral fin
    pect = spine[int(n * 0.72)]
    dk.polygon([(pect[0] - 18, pect[1] + 30), (pect[0] + 55, pect[1] + 95),
                (pect[0] + 105, pect[1] + 60), (pect[0] + 30, pect[1] + 8)],
               fill=(255, 160, 70, 200))

    # Eye: the focal point — sits on the head, just back from the snout.
    ex, ey = hx - 28, hy + 6
    dk.ellipse([ex - 14, ey - 14, ex + 14, ey + 14], fill=(255, 250, 240, 255))
    dk.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(12, 8, 6, 255))
    dk.ellipse([ex - 1, ey - 9, ex + 5, ey - 2], fill=(255, 255, 255, 255))
    # Mouth line + whiskers
    dk.arc([hx + 6, hy + 8, hx + 48, hy + 38],
           start=10, end=140, fill=(120, 40, 8, 220), width=4)
    for (wx, wy, wdx, wdy) in [(hx + 8, hy + 22, 44, 24), (hx + 8, hy + 22, 50, -8)]:
        dk.line([wx, wy, wx + wdx, wy + wdy], fill=(255, 220, 170, 200), width=3)

    # Soft glow under the koi, then the koi itself.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dglow = ImageDraw.Draw(glow)
    dglow.polygon(body, fill=(255, 122, 26, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow)
    img.alpha_composite(koi)

    # ---- Cherry-blossom petals drifting ----
    pet = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dp = ImageDraw.Draw(pet)
    for _ in range(42):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H)
        s = rng.uniform(7, 16)
        a = rng.randint(120, 220)
        col = (255, 170, 205, a) if rng.random() < 0.7 else (255, 210, 225, a)
        dp.ellipse([x - s, y - s * 0.6, x + s, y + s * 0.6], fill=col)
    img.alpha_composite(pet)

    # ---- Vignette: darken the corners so the centre pops ----
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx - W / 2) / (W / 2)
    dy = (yy - H / 2) / (H / 2)
    dist = np.sqrt(dx * dx + dy * dy)
    vig = np.clip(1.0 - 0.34 * np.clip(dist - 0.62, 0, None) ** 1.6, 0, 1)
    arr = np.array(img.convert("RGB")).astype(np.float32)
    arr *= vig[:, :, None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
