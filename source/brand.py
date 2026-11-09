# -*- coding: utf-8 -*-
"""Logo de la marque : badge rond, filigrane pendant la vidéo et signature sur l'écran final."""
import functools
import os

import numpy as np
from PIL import Image, ImageDraw

import config
from engine import *  # noqa: F401,F403
from engine import _with_shadow

_HERE = os.path.dirname(os.path.abspath(__file__))


def logo_file():
    p = (getattr(config, "LOGO_PATH", "") or "").strip()
    if not p:
        return None
    p = p if os.path.isabs(p) else os.path.join(_HERE, p)
    return p if os.path.exists(p) else None


@functools.lru_cache(maxsize=1)
def _disc():
    """Logo découpé en disque : le cercle est détecté automatiquement (tout ce qui diffère du fond d'angle)."""
    f = logo_file()
    if not f:
        return None
    im = Image.open(f).convert("RGBA")
    rgb = np.asarray(im.convert("RGB")).astype(int)
    diff = np.abs(rgb - rgb[2, 2]).sum(axis=2) > 40
    ys, xs = np.nonzero(diff)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2 + 2.0
    size = int(round(2 * r))
    x0, y0 = int(round(cx - r)), int(round(cy - r))
    crop = im.crop((x0, y0, x0 + size, y0 + size))
    ss = 4
    m = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * ss - 1, size * ss - 1), fill=255)
    crop.putalpha(m.resize((size, size), BOX))
    return crop


@functools.lru_cache(maxsize=16)
def logo_badge(d, shadow=True):
    """Sprite rond du logo, de diamètre d (avec ombre douce). None si aucun logo n'est configuré."""
    disc = _disc()
    if disc is None:
        return None
    spr = disc.resize((d, d), LANCZOS)
    if shadow:
        spr = _with_shadow(spr, 0, max(2, d // 22), max(3, d // 10), "#000000", 0.38)
    return spr


def watermark(img, t, scene):
    """Petit logo en filigrane pendant toute la vidéo ; il s'efface quand l'écran final (avec sa propre signature) arrive."""
    if not scene.get("logo", True) or not getattr(config, "LOGO_WATERMARK", True):
        return img
    d = scene.get("logo_d", 84)
    spr = logo_badge(d)
    if spr is None:
        return img
    a = prog(t, 0.3, 0.4)
    end = scene.get("end")
    if end:
        a *= 1 - prog(t, end - 0.35, 0.3)
    if a <= 0.01:
        return img
    margin, cy = 58, 226
    cx = (W - margin - d / 2) if scene.get("logo_pos", "tr") == "tr" else (margin + d / 2)
    place(img, spr, cx, cy, s=lerp(0.7, 1.0, e_back(prog(t, 0.3, 0.5))), alpha=a * 0.96)
    return img


def brand_lines():
    b, h = (config.BRAND or "").strip(), (config.HANDLE or "").strip()
    if b and h:
        return b, h
    if b:
        return b, config.TAGLINE
    if h:
        return h, config.TAGLINE
    return config.TAGLINE, ""


def lockup(img, t, th, y=226, d=90):
    """Signature de l'écran final : logo + métier (ou nom de marque et @). Renvoie False s'il n'y a pas de logo."""
    spr = logo_badge(d)
    if spr is None:
        return False
    l1, l2 = brand_lines()
    t1 = fit(l1, "bold", 40, 620, fill=th["fg"])
    t2 = fit(l2, "semi", 30, 620, fill=th["soft"]) if l2 else None
    tw = max(t1.width, t2.width if t2 else 0) - 12
    gap = 20
    x0 = W / 2 - (d + gap + tw) / 2
    p = prog(t, 0.0, 0.55)
    place(img, spr, x0 + d / 2, y, s=lerp(0.6, 1.0, e_back(p)), alpha=min(1, p * 2))
    ta = e_out(prog(t, 0.15, 0.45))
    xt = x0 + d + gap - 6
    if t2:
        place(img, t1, xt, y - 17, ax=0.0, alpha=ta)
        place(img, t2, xt, y + 23, ax=0.0, alpha=ta)
    else:
        place(img, t1, xt, y, ax=0.0, alpha=ta)
    return True
