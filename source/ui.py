# -*- coding: utf-8 -*-
"""Éléments visuels : effets, téléphone, faux site web, bulles de chat, notifications, coches, tampons."""
import functools
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from components import *  # noqa: F401,F403
from engine import _mask, _with_glow, _with_shadow  # noqa: F401


# ----------------------------------------------------------------- effets
def slam(img, spr, cx, cy, t, t0, dur=0.22, s0=2.6, amp=10.0, alpha=1.0):
    """Le sprite « s'écrase » à l'écran avec une petite secousse."""
    if t < t0:
        return img
    p = prog(t, t0, dur)
    s = lerp(s0, 1.0, e_out(p, 4))
    a = min(1.0, p * 3.0) * alpha
    k = 1 - prog(t, t0 + dur, 0.28)
    dx, dy = shake(t, amp * k) if k > 0 else (0, 0)
    place(img, spr, cx + dx, cy + dy, s=s, alpha=a)
    return img


def flash(img, t, t0, dur=0.14, color="#ffffff", a=0.22):
    if t0 <= t < t0 + dur:
        return overlay(img, color, a * (1 - (t - t0) / dur))
    return img


def glitch(img, k, seed=0):
    if k <= 0.02:
        return img
    rnd = random.Random(seed)
    out = rgb_split(img, int(26 * k))
    for _ in range(int(2 + 5 * k)):
        y = rnd.randrange(0, H - 140)
        h = rnd.randrange(20, 150)
        dx = int(rnd.uniform(-100, 100) * k)
        out.paste(out.crop((0, y, W, y + h)), (dx, y))
    return out


def near(t, b, w=0.2):
    """1 -> 0 autour d'un instant b (pour déclencher glitchs/flashs aux transitions)."""
    return clamp(1 - abs(t - b) / w)


@functools.lru_cache(maxsize=8)
def grid_sprite(color="#7c8cff", alpha=26, step=90):
    im = Image.new("RGBA", (W, H + step), col(color)[:3] + (0,))
    d = ImageDraw.Draw(im)
    c = col(color)[:3] + (alpha,)
    for x in range(0, W + 1, step):
        d.line([(x, 0), (x, H + step)], fill=c, width=2)
    for y in range(0, H + step + 1, step):
        d.line([(0, y), (W, y)], fill=c, width=2)
    return im


def draw_grid(img, t, speed=70, color="#7c8cff", alpha=26, step=90):
    put(img, grid_sprite(color, alpha, step), 0, -((t * speed) % step))


def chip(txt, fg, bg, size=40, fk="bold", px=34, py=16, outline=None, ow=0, bg_alpha=255):
    t = text(txt, fk, size, fg)
    w, h = t.width + 2 * px, t.height + 2 * py - 10
    spr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    spr.alpha_composite(rrect(w, h, h // 2, fill=bg if bg else None, outline=outline, ow=ow, alpha=bg_alpha))
    spr.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 - 1))
    return spr


@functools.lru_cache(maxsize=256)
def check_sprite(size, color, width, p):
    p = clamp(p)
    ss = 4
    S = size * ss
    pts = [(0.17 * S, 0.54 * S), (0.41 * S, 0.77 * S), (0.85 * S, 0.27 * S)]
    l1 = math.dist(pts[0], pts[1])
    l2 = math.dist(pts[1], pts[2])
    dist = p * (l1 + l2)
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    w = int(width * ss)
    path = [pts[0]]
    if dist <= l1:
        f = dist / l1
        path.append((pts[0][0] + (pts[1][0] - pts[0][0]) * f, pts[0][1] + (pts[1][1] - pts[0][1]) * f))
    else:
        f = (dist - l1) / l2
        path += [pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * f, pts[1][1] + (pts[2][1] - pts[1][1]) * f)]
    if len(path) >= 2 and p > 0:
        d.line(path, fill=255, width=w, joint="curve")
        for (x, y) in (path[0], path[-1]):
            d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=255)
    m = m.resize((size, size), BOX)
    spr = Image.new("RGBA", (size, size), col(color)[:3] + (0,))
    spr.putalpha(m)
    return spr


def cross_sprite(size, color, width):
    ss = 4
    S = size * ss
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    w = int(width * ss)
    a, b = 0.2 * S, 0.8 * S
    d.line([(a, a), (b, b)], fill=255, width=w)
    d.line([(a, b), (b, a)], fill=255, width=w)
    for (x, y) in ((a, a), (b, b), (a, b), (b, a)):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=255)
    m = m.resize((size, size), BOX)
    spr = Image.new("RGBA", (size, size), col(color)[:3] + (0,))
    spr.putalpha(m)
    return spr


@functools.lru_cache(maxsize=32)
def stamp(txt, color, size=96, ow=10, padx=40, pady=14, fill=None):
    t = text(txt, "black", size, color)
    w, h = t.width + 2 * padx, t.height + 2 * pady - 14
    spr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    spr.alpha_composite(rrect(w, h, 26, outline=color, ow=ow, fill=fill))
    spr.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 - 2))
    return spr


def ripple(img, cx, cy, p, color="#ffffff", d=120, ow=8):
    if p <= 0 or p >= 1:
        return
    place(img, circle(d, outline=color, ow=ow), cx, cy, s=0.4 + p * 1.3, alpha=(1 - p) * 0.9)


def place_xy(img, spr, cx, cy, sx=1.0, sy=1.0, alpha=1.0):
    """Comme place() mais avec une échelle différente en x et en y (effet « carte qui se retourne »)."""
    if sx <= 0.02 or sy <= 0.02 or alpha <= 0.003:
        return
    spr = spr.resize((max(1, round(spr.width * sx)), max(1, round(spr.height * sy))), BICUBIC)
    put(img, spr, cx - spr.width / 2, cy - spr.height / 2, alpha)


# --------------------------------------------------------------- téléphone
@functools.lru_cache(maxsize=8)
def _phone_parts(sw, sh, bezel, radius):
    w, h = sw + 2 * bezel, sh + 2 * bezel
    ss = 2
    outer = _mask("rrect", w, h, radius, ss)
    inner = Image.new("L", (w, h), 0)
    inner.paste(_mask("rrect", sw, sh, max(1, radius - bezel), ss), (bezel, bezel))
    ring = ImageChops.subtract(outer, inner)
    iw, ih = int(sw * 0.30), 32
    isl = Image.new("L", (w, h), 0)
    isl.paste(_mask("rrect", iw, ih, ih // 2, 4), ((w - iw) // 2, bezel + 14))
    fr = Image.new("RGBA", (w, h), (14, 14, 20, 0))
    fr.putalpha(ImageChops.lighter(ring, isl))
    rim_in = Image.new("L", (w, h), 0)
    rim_in.paste(_mask("rrect", w - 6, h - 6, radius - 3, ss), (3, 3))
    rim = ImageChops.subtract(outer, rim_in)
    rimimg = Image.new("RGBA", (w, h), (92, 92, 108, 0))
    rimimg.putalpha(rim.point([int(v * 0.9) for v in range(256)]))
    fr = Image.alpha_composite(fr, rimimg)
    return fr, outer


def phone_img(screen, bezel=16, radius=64):
    sw, sh = screen.size
    fr, outer = _phone_parts(sw, sh, bezel, radius)
    base = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    base.paste(screen.convert("RGBA"), (bezel, bezel))
    base.alpha_composite(fr)
    base.putalpha(ImageChops.multiply(base.getchannel("A"), outer))
    return base


@functools.lru_cache(maxsize=8)
def phone_shadow(w, h, radius=64, blur=38, op=0.5):
    pad = blur * 3
    a = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    a.paste(rrect(w, h, radius, fill="#000000").getchannel("A"), (pad, pad))
    a = a.filter(ImageFilter.GaussianBlur(blur)).point([int(v * op) for v in range(256)])
    im = Image.new("RGBA", a.size, (0, 0, 0, 0))
    im.putalpha(a)
    return im


def put_phone(img, screen, cx, cy, s=1.0, rot=0.0, alpha=1.0, bezel=16, radius=64):
    ph = phone_img(screen, bezel, radius)
    sh = phone_shadow(ph.width, ph.height, radius)
    place(img, sh, cx, cy + 34 * s, s=s, rot=rot, alpha=alpha * 0.9)
    place(img, ph, cx, cy, s=s, rot=rot, alpha=alpha)


# ------------------------------------------------------------ faux site web
@functools.lru_cache(maxsize=64)
def product_card(emoji, name, price, bg, accent):
    spr = rrect(188, 236, 24, fill="#ffffff", shadow=(0, 6, 12, "#000000", 0.14)).copy()
    pad = (spr.width - 188) // 2
    inner = rrect(164, 150, 18, fill=bg)
    spr.alpha_composite(inner, (pad + 12, pad + 12))
    spr.alpha_composite(text(emoji, "bold", 76), (pad + 12 + (164 - text(emoji, "bold", 76).width) // 2, pad + 40))
    spr.alpha_composite(text(name, "semi", 22, "#1f2937"), (pad + 14, pad + 168))
    spr.alpha_composite(text(price, "black", 22, accent), (pad + 14, pad + 196))
    return spr


@functools.lru_cache(maxsize=16)
def _hero_img(sw, h, c1, c2):
    return gradient(sw, h, (c1, c2), 125).convert("RGB")


PRODUCTS = [("👗", "Robe wax", "15 000 F", "#fde7f3"), ("👟", "Sneakers", "25 000 F", "#e0f2fe"),
            ("👜", "Sac cuir", "18 000 F", "#fef3c7"), ("⌚", "Montre", "30 000 F", "#dcfce7"),
            ("🎧", "Casque", "12 000 F", "#ede9fe"), ("🕶️", "Lunettes", "8 000 F", "#ffedd5")]


def site_screen(t=0.0, scroll=0.0, c1="#7c3aed", c2="#ec4899", sw=440, sh=900, name="Ma Boutique",
                tagline="Les meilleurs produits, chez toi", btn="Commander", press=0.0):
    img = Image.new("RGB", (sw, sh), "#f6f5fa")
    sc = int(scroll)
    TOP, hero_h = 122, 372
    img.paste(_hero_img(sw, hero_h, c1, c2), (0, TOP - sc))
    place(img, text("🛍️", "bold", 92), sw / 2, TOP - sc + 112)
    place(img, text(name, "black", 46, "#ffffff"), sw / 2, TOP - sc + 206)
    place(img, fit(tagline, "reg", 22, sw - 50, fill="#f5f3ff"), sw / 2, TOP - sc + 256)
    bs = 1 - 0.06 * press
    place(img, rrect(200, 62, 31, fill="#ffffff", shadow=(0, 6, 12, "#000000", 0.2)), sw / 2, TOP - sc + 328, s=bs)
    place(img, text(btn, "bold", 27, c1), sw / 2, TOP - sc + 327, s=bs)
    y = TOP + hero_h + 28 - sc
    put(img, text("Nos produits", "black", 30, "#1f2937"), 24, y)
    y += 62
    for i, (e, n, p_, bg) in enumerate(PRODUCTS):
        cx = 24 if i % 2 == 0 else 228
        cy = y + (i // 2) * 258
        put(img, product_card(e, n, p_, bg, c1), cx - 6, cy - 6)
    # barre du haut fixe : statut + en-tête
    img.paste(Image.new("RGB", (sw, TOP), "#ffffff"), (0, 0))
    put(img, text("9:41", "bold", 22, "#111827"), 30, 10)
    for k in range(4):
        img.paste(Image.new("RGB", (6, 6 + k * 4), "#111827"), (sw - 118 + k * 10, 34 - k * 4))
    place(img, rrect(36, 18, 5, fill="#111827"), sw - 48, 28)
    place(img, rrect(4, 8, 2, fill="#111827"), sw - 28, 28)
    place(img, circle(46, grad=((c1, c2), 90)), 46, 88)
    place(img, text("M", "black", 26, "#ffffff"), 46, 88)
    put(img, text(name, "bold", 28, "#111827"), 84, 68)
    for k in range(3):
        img.paste(Image.new("RGB", (30, 4), "#111827"), (sw - 62, 76 + k * 11))
    img.paste(Image.new("RGB", (sw, 2), "#e5e7eb"), (0, TOP))
    # bouton discussion flottant
    pulse = 1 + 0.06 * math.sin(t * 5)
    place(img, circle(74, fill="#25d366", shadow=(0, 5, 10, "#000000", 0.3)), sw - 58, sh - 66, s=pulse)
    place(img, text("💬", "bold", 38), sw - 58, sh - 68, s=pulse)
    return img


# ---------------------------------------------------------------- chat
@functools.lru_cache(maxsize=256)
def bubble(txt, side="left", size=29, max_w=290, fill="#ffffff", fg="#111b21", emo=0.92):
    t = text(txt, "reg", size, fg, max_w=max_w, align="left", ls=1.2, em=emo)
    px, py = 20, 13
    w, h = t.width + 2 * px - 8, t.height + 2 * py - 12
    body = rrect(w, h, 22, fill=fill, shadow=(0, 2, 3, "#000000", 0.16))
    pad = (body.width - w) // 2
    ss = 4
    tail = Image.new("L", (30 * ss, 30 * ss), 0)
    d = ImageDraw.Draw(tail)
    if side == "left":
        d.polygon([(0, 0), (30 * ss, 0), (30 * ss, 30 * ss)], fill=255)
    else:
        d.polygon([(0, 0), (30 * ss, 0), (0, 30 * ss)], fill=255)
    tail = tail.resize((30, 30), BOX)
    tl = Image.new("RGBA", (30, 30), col(fill)[:3] + (0,))
    tl.putalpha(tail)
    spr = Image.new("RGBA", (body.width + 24, body.height), (0, 0, 0, 0))
    ox = 12 if side == "left" else 0
    spr.alpha_composite(body, (ox, 0))
    spr.alpha_composite(tl, (ox + pad - 14 if side == "left" else ox + pad + w - 16, pad + 2))
    spr.alpha_composite(t, (ox + pad + px - 4, pad + py - 8))
    return spr


def typing_dots(t, fg="#8696a0"):
    spr = rrect(110, 56, 28, fill="#ffffff", shadow=(0, 2, 3, "#000000", 0.16)).copy()
    for i in range(3):
        a = 0.35 + 0.65 * max(0, math.sin(t * 7 - i * 0.9))
        d = circle(13, fill=fg)
        place(spr, d, spr.width / 2 - 24 + i * 24, spr.height / 2 - 1, alpha=a)
    return spr


# ------------------------------------------------------------- notification
@functools.lru_cache(maxsize=64)
def notif(icon, title, body, when="maintenant", w=920, accent="#34c759", dark=False):
    px = 28
    ic = rrect(108, 108, 28, fill=accent)
    tt = text(title, "bold", 38, "#ffffff" if dark else "#111111")
    bt = text(body, "reg", 33, "#d1d5db" if dark else "#3f3f46", max_w=w - 108 - 3 * px - 24, align="left", ls=1.15)
    wt = text(when, "reg", 26, "#9ca3af")
    h = max(108, tt.height + bt.height) + 2 * 22
    bg = (30, 30, 38, 225) if dark else (255, 255, 255, 232)
    spr = rrect(w, h, 40, fill=bg, shadow=(0, 12, 24, "#000000", 0.3)).copy()
    pad = (spr.width - w) // 2
    spr.alpha_composite(ic, (pad + px, pad + (h - 108) // 2))
    ie = text(icon, "bold", 62)
    spr.alpha_composite(ie, (pad + px + (108 - ie.width) // 2, pad + (h - 108) // 2 + 16))
    spr.alpha_composite(tt, (pad + px + 108 + 22, pad + 14))
    spr.alpha_composite(bt, (pad + px + 108 + 22, pad + 14 + tt.height - 8))
    spr.alpha_composite(wt, (pad + w - px - wt.width, pad + 20))
    return spr
