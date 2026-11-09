# -*- coding: utf-8 -*-
"""Éléments d'interface réutilisables : écran final (QR + numéro), téléphone, bulles, etc."""
import functools
import math

from PIL import Image, ImageChops, ImageDraw

import config
from brand import lockup
from engine import *  # noqa: F401,F403
from engine import _mask, _with_glow, _with_shadow  # noqa: F401

# ---------------------------------------------------------------- thèmes
THEMES = {
    "neon":   dict(card="#ffffff", qr="#0a0a12", accent="#b6ff3b", accent2="#ff2d95", fg="#ffffff", soft="#b8bccf",
                   pill="#b6ff3b", pill_fg="#0a0a12", conf=("#b6ff3b", "#ff2d95", "#ffffff", "#5ef2ff")),
    "code":   dict(card="#ffffff", qr="#0f1020", accent="#5ef2ff", accent2="#a78bfa", fg="#ffffff", soft="#aab0d0",
                   pill="#5ef2ff", pill_fg="#0b1020", conf=("#5ef2ff", "#a78bfa", "#ffffff", "#ff79c6")),
    "paper":  dict(card="#ffffff", qr="#16213e", accent="#e11d48", accent2="#1f4fd8", fg="#16213e", soft="#5b6478",
                   pill="#16213e", pill_fg="#ffffff", conf=("#e11d48", "#1f4fd8", "#f59e0b", "#16a34a")),
    "yellow": dict(card="#ffffff", qr="#111111", accent="#111111", accent2="#e11d48", fg="#111111", soft="#3b3b3b",
                   pill="#111111", pill_fg="#ffd60a", conf=("#111111", "#e11d48", "#ffffff", "#ff8a00")),
    "night":  dict(card="#ffffff", qr="#1a1038", accent="#ffb347", accent2="#ff5e7e", fg="#ffffff", soft="#d8cff5",
                   pill="#ffb347", pill_fg="#1a1038", conf=("#ffb347", "#ff5e7e", "#ffffff", "#9b8cff")),
    "violet": dict(card="#ffffff", qr="#1e1b4b", accent="#ffffff", accent2="#f0abfc", fg="#ffffff", soft="#ddd6fe",
                   pill="#ffffff", pill_fg="#4c1d95", conf=("#f0abfc", "#fde047", "#ffffff", "#67e8f9")),
    "teal":   dict(card="#ffffff", qr="#06302d", accent="#0d9488", accent2="#f59e0b", fg="#06302d", soft="#2f6f6a",
                   pill="#0d9488", pill_fg="#ffffff", conf=("#0d9488", "#f59e0b", "#06302d", "#fb7185")),
    "wa":     dict(card="#ffffff", qr="#06281d", accent="#4ade80", accent2="#fde047", fg="#ffffff", soft="#b7f0d9",
                   pill="#25d366", pill_fg="#04281c", conf=("#4ade80", "#fde047", "#ffffff", "#22d3ee")),
    "cyber":  dict(card="#ffffff", qr="#04101c", accent="#00e5ff", accent2="#2dff9a", fg="#ffffff", soft="#9bb4c9",
                   pill="#00e5ff", pill_fg="#04101c", conf=("#00e5ff", "#2dff9a", "#ffffff", "#ff2d95")),
    "ci":     dict(card="#ffffff", qr="#101010", accent="#f77f00", accent2="#009e60", fg="#ffffff", soft="#c9c9c9",
                   pill="#f77f00", pill_fg="#101010", conf=("#f77f00", "#009e60", "#ffffff", "#ffd60a")),
    "quiz":   dict(card="#ffffff", qr="#0f2a6b", accent="#ffd60a", accent2="#ff3b6b", fg="#ffffff", soft="#c7d6ff",
                   pill="#ffd60a", pill_fg="#0f2a6b", conf=("#ffd60a", "#ff3b6b", "#ffffff", "#34d399")),
}


def tag_line():
    """Ligne affichée en haut de l'écran final : nom + @ si renseignés dans config.py, sinon le métier."""
    who = (config.BRAND + "  •  " + config.HANDLE) if (config.BRAND and config.HANDLE) else (config.BRAND or config.HANDLE or "")
    return "💻 " + (who or config.TAGLINE)


@functools.lru_cache(maxsize=64)
def glow_shape(w, h, r, color, radius, strength=1.0):
    return _with_glow(rrect(w, h, r, fill=color), color, radius, strength)


@functools.lru_cache(maxsize=16)
def bracket(length, thick, color):
    ss = 4
    m = Image.new("L", (length * ss, length * ss), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, length * ss, thick * ss), radius=thick * ss // 2, fill=255)
    d.rounded_rectangle((0, 0, thick * ss, length * ss), radius=thick * ss // 2, fill=255)
    m = m.resize((length, length), BOX)
    spr = Image.new("RGBA", (length, length), col(color)[:3] + (0,))
    spr.putalpha(m)
    return spr


def brackets(img, cx, cy, hw, hh, color, length=76, thick=10, margin=26, alpha=1.0):
    b = bracket(length, thick, color)
    T = Image.Transpose
    put(img, b, cx - hw - margin, cy - hh - margin, alpha)
    put(img, b.transpose(T.FLIP_LEFT_RIGHT), cx + hw + margin - length, cy - hh - margin, alpha)
    put(img, b.transpose(T.FLIP_TOP_BOTTOM), cx - hw - margin, cy + hh + margin - length, alpha)
    put(img, b.transpose(T.ROTATE_180), cx + hw + margin - length, cy + hh + margin - length, alpha)


@functools.lru_cache(maxsize=32)
def _scan_line(w, color):
    return _with_glow(rrect(w, 7, 3, fill=color), color, 9, 1.4)


def pill_tag(txt, fg, bg, size=34, padx=30, pady=14, fk="semi", alpha=255):
    t = text(txt, fk, size, fg)
    return t, rrect(t.width + 2 * padx, t.height + 2 * pady - 8, (t.height + 2 * pady) // 2, fill=bg, alpha=alpha)


def put_pill(img, txt, cx, cy, fg, bg, size=34, fk="semi", alpha=1.0, s=1.0, padx=30, pady=14, bg_alpha=255):
    t, bgs = pill_tag(txt, fg, bg, size, padx, pady, fk, bg_alpha)
    place(img, bgs, cx, cy, s=s, alpha=alpha)
    place(img, t, cx, cy - 2 * s, s=s, alpha=alpha)
    return bgs.width


def put_headline(img, t, th, headline, sub=None, room=(284, 530), size=78):
    """Titre (+ sous-titre) centré verticalement dans l'espace libre entre la signature et la carte QR."""
    hs = text(headline, "black", size, th["fg"], hl=th["accent"], max_w=940, ls=1.06)
    sb = text(sub, "semi", 40, th["soft"], max_w=900) if sub else None
    gap = 10
    gh = hs.height + ((gap + sb.height) if sb else 0)
    top = room[0] + (room[1] - room[0] - gh) / 2
    p = e_out(prog(t, 0.05, 0.55))
    place(img, hs, W // 2, top + hs.height / 2 + (1 - p) * 50, s=lerp(0.85, 1, p), alpha=p)
    if sb:
        p = e_out(prog(t, 0.3, 0.5))
        place(img, sb, W // 2, top + hs.height + gap + sb.height / 2 + (1 - p) * 30, alpha=p)


def endcard(img, t, th, headline="On en parle ?", sub="Devis gratuit • Réponse rapide",
            qr=None, label=("Scanne-moi 📲", "pour écrire sur WhatsApp"), number=None,
            foot="💬 WhatsApp   •   📞 Appel", burst=True, tag=True):
    """Écran final : titre, QR code, numéro et appels à l'action. t = secondes depuis le début de l'écran."""
    qr = qr or config.WHATSAPP_URL
    number = number or config.PHONE_DISPLAY
    acc, acc2, fg, soft = th["accent"], th["accent2"], th["fg"], th["soft"]

    # --- signature « qui je suis » en haut : logo + métier (ou simple ligne de texte s'il n'y a pas de logo)
    if tag and not lockup(img, t, th):
        place(img, text(tag_line(), "semi", 32, soft), W // 2, 212, alpha=prog(t, 0.0, 0.4))

    # --- titre + sous-titre
    put_headline(img, t, th, headline, sub)

    # --- carte QR
    cw, ch = 640, 580
    cx, cy = W // 2, 860
    pc = prog(t, 0.4, 0.7)
    sc = lerp(0.55, 1.0, e_back(pc)) * (1 + 0.012 * math.sin(t * 3.1)) if pc > 0 else 0
    if sc > 0:
        def P(y):                       # position verticale qui suit l'échelle de la carte (effet « pop »)
            return cy + (y - cy) * sc
        gl = glow_shape(cw, ch, 48, acc, 46, 0.85 + 0.2 * math.sin(t * 3.1))
        place(img, gl, cx, cy, s=sc, alpha=min(1, pc * 1.6) * 0.75)
        card = rrect(cw, ch, 46, fill=th["card"], shadow=(0, 14, 26, "#000000", 0.35))
        place(img, card, cx, cy, s=sc, alpha=min(1, pc * 2))
        q = qr_sprite(qr, 440, fg=th["qr"], bg=th["card"], quiet=1)   # modules de 11 px ; la marge blanche de la carte fait office de zone de silence
        qy = cy - ch / 2 + 26 + q.height / 2
        place(img, q, cx, P(qy), s=sc, alpha=min(1, pc * 2))
        # ligne de scan
        if t > 1.0:
            ph = ((t - 1.0) / 2.2) % 1.0
            sl = _scan_line(q.width - 20, acc if acc != "#ffffff" else acc2)
            fade = min(1, ph * 6, (1 - ph) * 6)
            place(img, sl, cx, P(qy - q.height / 2 + 10 + ph * (q.height - 20)), s=sc, alpha=0.9 * fade)
        # légende
        l1 = text(label[0], "black", 44, th["qr"])
        l2 = text(label[1], "semi", 31, "#4b5563")
        place(img, l1, cx, P(cy + ch / 2 - 84), s=sc, alpha=min(1, pc * 2))
        place(img, l2, cx, P(cy + ch / 2 - 38), s=sc, alpha=min(1, pc * 2))
        # viseur
        pulse = 5 * math.sin(t * 4.0)
        brackets(img, cx, cy, int(cw / 2 * sc), int(ch / 2 * sc), acc if acc != th["card"] else acc2, margin=int(24 + pulse), alpha=min(1, pc * 1.5))

    # --- numéro
    p = e_out(prog(t, 1.0, 0.55))
    if p > 0:
        ts = text("📞 " + number, "black", 62, th["pill_fg"])
        pw, ph_ = ts.width + 80, 124
        pill = rrect(pw, ph_, ph_ // 2, fill=th["pill"], shadow=(0, 10, 22, "#000000", 0.28))
        ypos = 1262 + (1 - p) * 70
        sc2 = 1 + 0.018 * math.sin(t * 5.2 + 1.0)
        # onde
        rp = ((t - 1.2) / 1.3) % 1.0 if t > 1.2 else 1.0
        ring = rrect(pw, ph_, ph_ // 2, outline=th["pill"], ow=5)
        place(img, ring, W // 2, ypos, s=1 + rp * 0.22, alpha=(1 - rp) * 0.7 * p)
        place(img, pill, W // 2, ypos, s=sc2, alpha=p)
        place(img, ts, W // 2, ypos - 3, s=sc2, alpha=p)

    # --- pied
    if foot:
        p = e_out(prog(t, 1.4, 0.5))
        place(img, text(foot, "semi", 36, soft), W // 2, 1382 + (1 - p) * 20, alpha=p)

    if burst:
        confetti(img, t, 0.55, n=72, seed=7, origin=(W // 2, cy), colors=th["conf"], life=2.8)
    return img
