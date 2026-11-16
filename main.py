#!/usr/bin/env python3
"""Neon Koi Ascending - deterministic generative art for make.fun ai-excited-01.

Draws one vivid scene: an orange-and-white koi leaping through a ring of
gold fire over a moonlit ocean, under aurora ribbons and a full moon, with
cherry-blossom petals drifting through the air.

Pure Pillow + numpy + stdlib. Fixed seed, no network, no clock, no reading
of any input file: every run writes byte-identical pixels.

Usage:  python3 main.py [output_path]     (default: output/entry.png)
"""

import math
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

W = H = 1024
SEED = 20261116
HORIZON = 560  # y where the ocean meets the sky

rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- helpers

def lerp(a, b, t):
    return a + (b - a) * t


def vgrad(top, bottom, height, width=W):
    """Vertical RGB gradient as a float array of shape (height, width, 3)."""
    t = np.linspace(0.0, 1.0, height, dtype=np.float64)[:, None, None]
    top = np.asarray(top, dtype=np.float64)[None, None, :]
    bottom = np.asarray(bottom, dtype=np.float64)[None, None, :]
    band = top + (bottom - top) * t
    return np.repeat(band, width, axis=1)


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def stamp_ellipse(base, center, rx, ry, angle_deg, fill):
    """Paste a rotated filled ellipse onto an RGBA image."""
    pad = int(max(rx, ry)) + 4
    tile = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.ellipse([pad - rx, pad - ry, pad + rx, pad + ry], fill=fill)
    tile = tile.rotate(angle_deg, resample=Image.BICUBIC, center=(pad, pad))
    base.alpha_composite(tile, (int(center[0]) - pad, int(center[1]) - pad))


def bezier(p0, p1, p2, p3, t):
    mt = 1.0 - t
    x = (mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
         + 3 * mt * t * t * p2[0] + t ** 3 * p3[0])
    y = (mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
         + 3 * mt * t * t * p2[1] + t ** 3 * p3[1])
    return (x, y)


def bezier_tangent(p0, p1, p2, p3, t):
    mt = 1.0 - t
    dx = (3 * mt * mt * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0])
          + 3 * t * t * (p3[0] - p2[0]))
    dy = (3 * mt * mt * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1])
          + 3 * t * t * (p3[1] - p2[1]))
    n = math.hypot(dx, dy) or 1.0
    return (dx / n, dy / n)


def perp_up(tangent):
    """Unit perpendicular with a negative y component (the sky side)."""
    tx, ty = tangent
    a = (ty, -tx)
    b = (-ty, tx)
    return a if a[1] < b[1] else b


def rot_point(px, py, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (cx + (px - cx) * c - (py - cy) * s,
            cy + (px - cx) * s + (py - cy) * c)


# ---------------------------------------------------------------- sky & sea

def paint_background():
    sky = vgrad((8, 7, 42), (46, 30, 96), HORIZON)
    sea = vgrad((18, 22, 68), (5, 7, 28), H - HORIZON)
    arr = np.vstack([sky, sea]).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def paint_aurora(base):
    aur = layer()
    d = ImageDraw.Draw(aur)
    ribbons = [
        # (base_y, amp1, amp2, thickness, colour)
        (150, 46, 20, 64, (64, 255, 190, 110)),
        (235, 60, 26, 84, (0, 220, 200, 95)),
        (330, 38, 16, 52, (150, 110, 255, 85)),
    ]
    for base_y, a1, a2, thick, colour in ribbons:
        phase1 = rng.uniform(0, 6.28)
        phase2 = rng.uniform(0, 6.28)
        top_pts, bot_pts = [], []
        for x in range(-20, W + 21, 16):
            yc = (base_y + a1 * math.sin(x * 0.0042 + phase1)
                  + a2 * math.sin(x * 0.011 + phase2))
            th = thick * (0.75 + 0.25 * math.sin(x * 0.006 + phase2))
            top_pts.append((x, yc - th / 2))
            bot_pts.append((x, yc + th / 2))
        d.polygon(top_pts + bot_pts[::-1], fill=colour)
    aur = aur.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(aur)


def paint_stars(base):
    st = layer()
    d = ImageDraw.Draw(st)
    moon_c, moon_r = (770, 195), 95
    for _ in range(230):
        x = float(rng.uniform(0, W))
        y = float(rng.uniform(0, HORIZON - 30))
        if math.hypot(x - moon_c[0], y - moon_c[1]) < moon_r + 45:
            continue
        r = float(rng.uniform(0.7, 2.4))
        b = int(rng.uniform(150, 255))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, 255, 235))
        if r > 1.9:  # a few bright stars get a sparkle cross
            arm = r * 3.2
            d.line([x - arm, y, x + arm, y], fill=(b, b, 255, 150), width=1)
            d.line([x, y - arm, x, y + arm], fill=(b, b, 255, 150), width=1)
    base.alpha_composite(st)


def paint_moon(base):
    glow = layer()
    d = ImageDraw.Draw(glow)
    cx, cy, r = 770, 195, 95
    d.ellipse([cx - 165, cy - 165, cx + 165, cy + 165],
              fill=(255, 238, 190, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    base.alpha_composite(glow)

    disc = layer()
    d = ImageDraw.Draw(disc)
    for rr in range(r, 0, -2):  # radial shading, bright core
        t = rr / r
        col = (int(lerp(255, 244, t)), int(lerp(250, 228, t)),
               int(lerp(224, 186, t)))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col + (255,))
    # craters on their own layer, for the same blending reason as the
    # koi's belly: drawn straight on the disc they would punch holes
    crat = layer()
    cd = ImageDraw.Draw(crat)
    for _ in range(9):  # craters
        a = float(rng.uniform(0, 6.28))
        dist = float(rng.uniform(0, r * 0.72))
        cr = float(rng.uniform(6, 20))
        px, py = cx + dist * math.cos(a), cy + dist * math.sin(a)
        cd.ellipse([px - cr, py - cr, px + cr, py + cr],
                   fill=(222, 210, 172, 130))
    disc.alpha_composite(crat)
    base.alpha_composite(disc)


def paint_sea(base):
    sea = layer()
    d = ImageDraw.Draw(sea)
    # horizontal wave streaks, denser and brighter near the horizon
    for _ in range(170):
        y = float(rng.uniform(HORIZON + 6, H - 8))
        depth = (y - HORIZON) / (H - HORIZON)
        x = float(rng.uniform(0, W - 120))
        ln = float(rng.uniform(24, 130)) * (1.0 - depth * 0.45)
        alpha = int(lerp(64, 16, depth) * rng.uniform(0.5, 1.0))
        d.line([x, y, x + ln, y], fill=(130, 160, 230, alpha), width=2)
    # moon reflection: shimmering gold dashes in a column under the moon
    for _ in range(110):
        y = float(rng.uniform(HORIZON + 10, H - 14))
        depth = (y - HORIZON) / (H - HORIZON)
        spread = 46 + depth * 95
        x = 770 + float(rng.uniform(-spread, spread))
        ln = float(rng.uniform(12, 84)) * (1.0 - depth * 0.5)
        alpha = int(lerp(190, 45, depth) * rng.uniform(0.4, 1.0))
        d.line([x, y, x + ln, y], fill=(255, 216, 130, alpha), width=3)
    # ripples where the koi bursts out of the water
    rcx, rcy = 430, 668
    for i in range(6):
        rx = 46 + i * 42
        ry = rx * 0.26
        alpha = int(lerp(150, 30, i / 5))
        d.ellipse([rcx - rx, rcy - ry, rcx + rx, rcy + ry],
                  outline=(185, 205, 255, alpha), width=3)
    base.alpha_composite(sea)


# ---------------------------------------------------------------- fire ring

RING_C = (512, 468)
RING_RX, RING_RY = 258, 152
RING_TILT = math.radians(-16)


def ring_point(theta):
    x = RING_RX * math.cos(theta)
    y = RING_RY * math.sin(theta)
    rx, ry = rot_point(x, y, 0, 0, RING_TILT)
    return (rx + RING_C[0], ry + RING_C[1])


def ring_outward(theta):
    px, py = ring_point(theta)
    dx, dy = px - RING_C[0], py - RING_C[1]
    n = math.hypot(dx, dy) or 1.0
    return (dx / n, dy / n)


def paint_flames(base, front):
    """Flames around the ring. front=False draws the far (upper) half first,
    front=True the near (lower) half, so the koi passes *through* the ring."""
    glow = layer()
    fl = layer()
    dg = ImageDraw.Draw(glow)
    df = ImageDraw.Draw(fl)
    palette = [(255, 196, 64), (255, 138, 30), (232, 84, 22), (255, 214, 110)]
    n = 132
    for i in range(n):
        theta = 2 * math.pi * i / n
        px, py = ring_point(theta)
        is_front = py > RING_C[1]
        if is_front != front:
            continue
        ox, oy = ring_outward(theta)
        # flame length: slow waves plus wide jitter, so the ring reads as
        # uneven fire rather than a uniform spiky saw blade
        length = (30 + 26 * math.sin(theta * 3.0 + 0.7)
                  + 18 * math.sin(theta * 7.0 + 2.1)
                  + float(rng.uniform(-10, 26)))
        length = max(18.0, length)
        half_w = 10.0 + float(rng.uniform(-2, 4))
        tip = (px + ox * length, py + oy * length)
        side = (-oy, ox)
        base_pt = (px - ox * 6, py - oy * 6)
        col = palette[i % len(palette)]
        poly = [(base_pt[0] + side[0] * half_w, base_pt[1] + side[1] * half_w),
                (base_pt[0] - side[0] * half_w, base_pt[1] - side[1] * half_w),
                tip]
        df.polygon(poly, fill=col + (235,))
        dg.polygon(poly, fill=(255, 120, 20, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    base.alpha_composite(glow)
    base.alpha_composite(fl)
    if front:
        # bright core of the ring itself, drawn over the front flames
        core = layer()
        d = ImageDraw.Draw(core)
        pts = [ring_point(2 * math.pi * i / 220) for i in range(221)]
        d.line(pts, fill=(255, 214, 96, 255), width=9, joint="curve")
        d.line(pts, fill=(255, 244, 190, 255), width=3, joint="curve")
        base.alpha_composite(core)
        # embers bursting off the ring
        emb = layer()
        d = ImageDraw.Draw(emb)
        for _ in range(42):
            theta = float(rng.uniform(0, 6.28))
            px, py = ring_point(theta)
            ox, oy = ring_outward(theta)
            dist = float(rng.uniform(8, 66))
            ex, ey = px + ox * dist, py + oy * dist
            r = float(rng.uniform(1.5, 4.2))
            d.ellipse([ex - r, ey - r, ex + r, ey + r],
                      fill=(255, 210, 90, 230))
        emb = emb.filter(ImageFilter.GaussianBlur(1.2))
        base.alpha_composite(emb)


# ---------------------------------------------------------------- the koi

# Spine of the leap: tail low-left in the water, head high-right in the sky.
P0 = (296, 712)
P1 = (372, 470)
P2 = (566, 372)
P3 = (706, 296)


def koi_width(t):
    return 15.0 + 56.0 * (math.sin(math.pi * t ** 0.92) ** 0.9)


def paint_koi(base):
    koi = layer()
    d = ImageDraw.Draw(koi)

    # --- tail: two flowing lobes trailing behind the body
    tail_base = bezier(P0, P1, P2, P3, 0.0)
    tan0 = bezier_tangent(P0, P1, P2, P3, 0.0)
    back = (-tan0[0], -tan0[1])
    for sgn, ln, spread in ((1, 128, 58), (-1, 104, 46)):
        up = perp_up(tan0)
        side = up if sgn > 0 else (-up[0], -up[1])
        tip = (tail_base[0] + back[0] * ln + side[0] * spread * 0.4,
               tail_base[1] + back[1] * ln + side[1] * spread * 0.4)
        mid = (tail_base[0] + back[0] * ln * 0.55 + side[0] * spread,
               tail_base[1] + back[1] * ln * 0.55 + side[1] * spread)
        poly = [tail_base,
                (tail_base[0] + side[0] * 14, tail_base[1] + side[1] * 14),
                mid, tip,
                (tail_base[0] - side[0] * 12, tail_base[1] - side[1] * 12)]
        d.polygon(poly, fill=(255, 122, 36, 215))
        d.line([tail_base, mid, tip], fill=(255, 200, 130, 200), width=3)

    # --- body: overlapping discs along the spine, bright orange
    steps = 64
    spine = [bezier(P0, P1, P2, P3, i / steps) for i in range(steps + 1)]
    for i, (x, y) in enumerate(spine):
        wdt = koi_width(i / steps)
        d.ellipse([x - wdt, y - wdt * 0.92, x + wdt, y + wdt * 0.92],
                  fill=(255, 122, 26, 255))

    # --- pale belly stripe along the underside, on its own layer.
    # Pillow's ImageDraw replaces pixels instead of blending them, so a
    # translucent fill drawn straight over the orange body would punch a
    # see-through hole (the belly rendered grey, showing the sky through).
    # A separate layer composited on top blends it properly instead.
    ov = layer()
    od = ImageDraw.Draw(ov)
    for i in range(8, steps - 6):
        t = i / steps
        x, y = spine[i]
        tan = bezier_tangent(P0, P1, P2, P3, t)
        down = (-perp_up(tan)[0], -perp_up(tan)[1])
        wdt = koi_width(t)
        cx, cy = x + down[0] * wdt * 0.30, y + down[1] * wdt * 0.30
        od.ellipse([cx - wdt * 0.52, cy - wdt * 0.42,
                    cx + wdt * 0.52, cy + wdt * 0.42],
                   fill=(255, 236, 208, 110))

    # --- white patches (koi pattern), rotated to the spine's angle.
    # Kept smaller than the body width so the orange flank stays dominant.
    for t, scale in ((0.22, 0.8), (0.48, 0.9), (0.72, 0.75)):
        x, y = bezier(P0, P1, P2, P3, t)
        tan = bezier_tangent(P0, P1, P2, P3, t)
        up = perp_up(tan)
        cx, cy = x - up[0] * koi_width(t) * 0.12, y - up[1] * koi_width(t) * 0.12
        ang = math.degrees(math.atan2(tan[1], tan[0]))
        stamp_ellipse(koi, (cx, cy), koi_width(t) * 0.62 * scale,
                      koi_width(t) * 0.40 * scale, ang, (255, 250, 244, 238))

    # --- a few ink-black spots
    for t, off in ((0.30, 0.30), (0.68, -0.34)):
        x, y = bezier(P0, P1, P2, P3, t)
        tan = bezier_tangent(P0, P1, P2, P3, t)
        up = perp_up(tan)
        cx, cy = x + up[0] * koi_width(t) * off, y + up[1] * koi_width(t) * off
        ang = math.degrees(math.atan2(tan[1], tan[0]))
        stamp_ellipse(koi, (cx, cy), 13, 8, ang, (28, 18, 14, 225))

    # --- scale hints: small arcs over the orange flank, kept off the
    # white patches so they read as scales, not markings on the patches
    patch_ts = (0.22, 0.48, 0.72)
    for i in range(10, steps - 4, 3):
        t = i / steps
        if min(abs(t - p) for p in patch_ts) < 0.08:
            continue
        x, y = spine[i]
        tan = bezier_tangent(P0, P1, P2, P3, t)
        up = perp_up(tan)
        cx, cy = x + up[0] * koi_width(t) * 0.18, y + up[1] * koi_width(t) * 0.18
        r = koi_width(t) * 0.30
        od.arc([cx - r, cy - r, cx + r, cy + r], 200, 340,
               fill=(205, 88, 18, 45), width=2)

    # --- dorsal fin along the top of the mid-body
    top_pts, tip_pts = [], []
    for i in range(20, 37):
        t = i / steps
        x, y = spine[i]
        tan = bezier_tangent(P0, P1, P2, P3, t)
        up = perp_up(tan)
        wdt = koi_width(t)
        top_pts.append((x + up[0] * wdt * 0.9, y + up[1] * wdt * 0.9))
        lift = 30 * math.sin(math.pi * (i - 20) / 16)
        tip_pts.append((x + up[0] * (wdt * 0.9 + lift),
                        y + up[1] * (wdt * 0.9 + lift)))
    od.polygon(top_pts + tip_pts[::-1], fill=(255, 110, 30, 205))

    # --- pectoral fin near the head, sweeping down-back
    t = 0.84
    hx, hy = bezier(P0, P1, P2, P3, t)
    tan = bezier_tangent(P0, P1, P2, P3, t)
    down = (-perp_up(tan)[0], -perp_up(tan)[1])
    fin = [(hx + down[0] * 18, hy + down[1] * 18),
           (hx + down[0] * 62 + tan[0] * 26, hy + down[1] * 62 + tan[1] * 26),
           (hx + down[0] * 74 - tan[0] * 34, hy + down[1] * 74 - tan[1] * 34),
           (hx + down[0] * 30 - tan[0] * 30, hy + down[1] * 30 - tan[1] * 30)]
    od.polygon(fin, fill=(255, 168, 88, 200))
    od.line(fin + [fin[0]], fill=(255, 220, 170, 220), width=2)
    koi.alpha_composite(ov)

    # --- head: a slightly wider cap, white blaze, and the eye
    ht = 0.97
    hx, hy = bezier(P0, P1, P2, P3, ht)
    tan = bezier_tangent(P0, P1, P2, P3, ht)
    up = perp_up(tan)
    ang = math.degrees(math.atan2(tan[1], tan[0]))
    stamp_ellipse(koi, (hx, hy), 46, 38, ang, (255, 250, 244, 255))
    stamp_ellipse(koi, (hx + tan[0] * 22, hy + tan[1] * 22), 24, 20, ang,
                  (255, 122, 26, 255))
    # whiskers from the snout, kept short so they stay clear of the moon
    snout = (hx + tan[0] * 46, hy + tan[1] * 46)
    for sgn in (1, -1):
        pts = []
        for k in range(9):
            u = k / 8
            pts.append((snout[0] + tan[0] * u * 30 + up[0] * sgn * u * u * 18,
                        snout[1] + tan[1] * u * 30 + up[1] * sgn * u * u * 18))
        d.line(pts, fill=(120, 50, 10, 230), width=3)
    # the eye: white, black pupil, bright catchlight - the focal point
    ex, ey = hx + up[0] * 20 - tan[0] * 6, hy + up[1] * 20 - tan[1] * 6
    d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=(255, 255, 255, 255))
    d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], outline=(40, 20, 8, 255),
              width=2)
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(12, 8, 6, 255))
    d.ellipse([ex - 6, ey - 9, ex - 1, ey - 4], fill=(255, 255, 255, 255))
    # mouth: a small dark curve at the snout
    d.arc([snout[0] - 14, snout[1] - 8, snout[0] + 14, snout[1] + 14],
          20, 130, fill=(120, 50, 10, 230), width=3)

    base.alpha_composite(koi)


# ---------------------------------------------------------------- petals

def paint_petals(base):
    pet = layer()
    for _ in range(48):
        x = float(rng.uniform(10, W - 10))
        y = float(rng.uniform(10, H - 10))
        size = float(rng.uniform(9, 20))
        ang = float(rng.uniform(0, 360))
        pink = int(rng.uniform(225, 255))
        tile = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        # a cherry petal: rounded lobes with a notch at the top
        td.polygon([(24, 4), (32, 8), (38, 16), (36, 28), (28, 40),
                    (24, 44), (20, 40), (12, 28), (10, 16), (16, 8)],
                   fill=(255, pink - 40, 198, 225),
                   outline=(228, 120, 152, 235))
        tile = tile.resize((int(size * 2), int(size * 2)),
                           resample=Image.LANCZOS)
        tile = tile.rotate(ang, resample=Image.BICUBIC, expand=True)
        pet.alpha_composite(tile, (int(x - tile.width / 2),
                                   int(y - tile.height / 2)))
    base.alpha_composite(pet)


# ---------------------------------------------------------------- finish

def paint_finish(img):
    # soft bloom: a blurred copy screened back over the picture
    bloom = img.filter(ImageFilter.GaussianBlur(6))
    img = ImageChops.screen(img, Image.blend(img, bloom, 0.22))
    # gentle vignette so the centre - koi, ring, moon - holds the eye
    arr = np.asarray(img.convert("RGB")).astype(np.float64)
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx - W / 2) / (W / 2)
    dy = (yy - H / 2) / (H / 2)
    r2 = np.clip(dx * dx + dy * dy, 0, 2)
    arr *= (1.0 - 0.20 * r2 / 2.0)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def main(argv):
    out = argv[1] if len(argv) > 1 else os.path.join("output", "entry.png")
    img = paint_background()
    paint_aurora(img)
    paint_stars(img)
    paint_moon(img)
    paint_sea(img)
    paint_flames(img, front=False)   # far half of the fire ring
    paint_koi(img)                   # the koi leaps through it
    paint_flames(img, front=True)    # near half overlaps the koi
    paint_petals(img)
    img = paint_finish(img)
    folder = os.path.dirname(out)
    if folder:
        os.makedirs(folder, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main(sys.argv)
