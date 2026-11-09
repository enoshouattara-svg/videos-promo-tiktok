# -*- coding: utf-8 -*-
"""Vidéos 5 et 6."""
import functools
import math
import random

import numpy as np

from ui import *  # noqa: F401,F403
from components import THEMES, endcard
from engine import _with_glow

SCENES = []


# ====================================================================== 05
# « Tu as besoin d'un site web si… » : liste à cocher sur un cahier
INK, BLUE, GREEN, RED5 = "#1e293b", "#1d4ed8", "#16a34a", "#e11d48"


@functools.lru_cache(maxsize=1)
def paper_bg():
    img = Image.new("RGB", (W, H), "#fbf6e9")
    d = ImageDraw.Draw(img)
    for y in range(230, H, 80):
        d.line([(0, y), (W, y)], fill="#c9dbf2", width=3)
    d.line([(152, 0), (152, H)], fill="#f2a7a7", width=4)
    for y in range(110, H, 170):
        img.paste(circle(46, fill="#cfc7b2"), (30, y - 23), circle(46, fill="#cfc7b2"))
        img.paste(circle(30, fill="#6f6955"), (38, y - 15), circle(30, fill="#6f6955"))
    return img


@functools.lru_cache(maxsize=64)
def wavy(w, p, color, amp=7, wl=64, th=10):
    ss = 3
    im = Image.new("L", (w * ss, 40 * ss), 0)
    d = ImageDraw.Draw(im)
    pts = [(x * ss, (20 + amp * math.sin(x / wl * 2 * math.pi)) * ss) for x in range(0, int(w * p) + 1, 4)]
    if len(pts) > 1:
        d.line(pts, fill=255, width=th * ss, joint="curve")
    im = im.resize((w, 40), BOX)
    spr = Image.new("RGBA", (w, 40), col(color)[:3] + (0,))
    spr.putalpha(im)
    return spr


def hand_lines(img, lines, x, y, size, color, p, fk="hand", lh=None, alpha=1.0, hl=None):
    """Écriture manuscrite : révèle les lignes l'une après l'autre. Renvoie la position du stylo."""
    lh = lh or int(size * 1.2)
    n = len(lines)
    tip = None
    for i, ln in enumerate(lines):
        pi = clamp(p * n - i)
        if pi <= 0:
            break
        spr = text(ln, fk, size, color, hl=hl, align="left")
        put(img, crop_w(spr, pi), x - 6, y + i * lh - spr.height / 2, alpha)
        tip = (x + spr.width * pi - 6, y + i * lh)
        if pi < 1:
            break
    return tip


ITEMS5 = [(["On me demande", "« t'as un site ? »"], 2.2), (["Je répète mes prix", "100 fois par jour"], 4.2),
          (["Mes concurrents sont", "déjà sur Google"], 6.2), (["Je veux vendre", "même la nuit 🌙"], 8.2),
          (["Je veux que les clients", "me fassent confiance"], 10.2)]


@functools.lru_cache(maxsize=2)
def sticky(w, h):
    base = rrect(w, h, 14, fill="#ffe66d", shadow=(0, 16, 26, "#000000", 0.28)).copy()
    pad = (base.width - w) // 2
    base.alpha_composite(rrect(w, 34, 14, fill="#f5d33f"), (pad, pad + h - 34))
    tape = rrect(220, 62, 6, fill=(255, 255, 255, 150))
    base.alpha_composite(tape, (pad + w // 2 - 110, pad - 26))
    return base


def v05(t):
    BN, BE = 12.2, 14.6
    img = paper_bg().copy()
    vis = 1 - prog(t, BE - 0.5, 0.4)
    if vis > 0.01:
        la = 1 - 0.92 * e_out(prog(t, BN, 0.35))          # la liste s'estompe sous le post-it
        la *= vis
        tip = hand_lines(img, ["Tu as besoin", "d'un site web si…"], 90, 296, 92, BLUE, prog(t, 0.2, 1.5), fk="printb", lh=104, alpha=vis)
        if t > 1.7:
            put(img, wavy(780, round(prog(t, 1.75, 0.45) * 24) / 24, RED5), 96, 430, vis)
        for i, (lines, t0) in enumerate(ITEMS5):
            y = 600 + i * 176
            pb = pop(t, t0 - 0.2, 0.35)
            if pb <= 0:
                continue
            place(img, rrect(80, 80, 15, outline="#334155", ow=6), 238, y, s=pb, rot=(-3 if i % 2 else 2), alpha=la)
            p = prog(t, t0, 0.95)
            tp = hand_lines(img, lines, 300, y, 62, INK, p, fk="hand", lh=72, alpha=la)
            if tp and p < 1:
                place(img, text("✏️", "bold", 70), tp[0] + 28, tp[1] + 12, rot=-15, alpha=la)
            pc = prog(t, t0 + 1.0, 0.35)
            if pc > 0:
                place(img, check_sprite(124, GREEN, 16, round(pc * 12) / 12), 250, y - 16, alpha=la)
        if tip and t < 1.8:
            place(img, text("✏️", "bold", 70), tip[0] + 28, tip[1] + 12, rot=-15, alpha=vis)
    if BN <= t < BE:
        pn = prog(t, BN, 0.28)
        s_ = lerp(1.7, 1.0, e_out(pn, 4))
        note = sticky(780, 540)
        place(img, note, 540, 860, s=s_, rot=-3, alpha=min(1, pn * 3) * vis)
        if pn >= 1 or t > BN + 0.2:
            place(img, text("Tu as coché\n**2 cases** ?", "printb", 74, INK, hl=RED5, ls=1.15), 540, 770, rot=-3, alpha=prog(t, BN + 0.2, 0.25) * vis)
            place(img, text("Alors il te faut\nun **site web** 😉", "printb", 66, INK, hl=BLUE, ls=1.15), 540, 985, rot=-3, alpha=prog(t, BN + 0.7, 0.25) * vis)
    if t >= BE:
        endcard(img, t - BE, THEMES["paper"], headline="Un **site web**,\nça te dit ?", sub="Devis gratuit • Écris-nous")
    return img


_s5 = [(0.4, "swipe", 0.35), (0.9, "swipe", 0.3), (1.75, "swipe", 0.3)]
for _, t0 in ITEMS5:
    _s5 += [(t0, "swipe", 0.3), (t0 + 0.45, "swipe", 0.3), (t0 + 1.02, "ding", 0.55), (t0 + 1.02, "tick", 0.5)]
SFX05 = _s5 + [(12.2, "stamp"), (12.45, "sparkle", 0.8), (14.55, "impact", 0.6), (14.6, "whoosh"), (15.0, "pop"), (15.6, "ding", 0.8)]
VOICE05 = [dict(text="Tu as besoin d'un site web si,", at=0.3, end=2.2),
           dict(text="on te demande : t'as un site ?", at=2.25, end=4.15),
           dict(text="Tu répètes tes prix cent fois par jour.", at=4.25, end=6.15),
           dict(text="Tes concurrents sont déjà sur Google.", at=6.25, end=8.15),
           dict(text="Tu veux vendre même la nuit.", at=8.25, end=10.1),
           dict(text="Tu veux que les clients te fassent confiance.", at=10.25, end=12.15),
           dict(text="Deux cases cochées ? Il te faut un site web !", at=12.4, end=15.0),
           dict(text="Devis gratuit, écris-nous !", at=15.3, end=18.0)]
SCENES.append(dict(id=5, slug="tu-as-besoin-d-un-site-si", dur=19.4, end=14.6, frame=v05, sfx=SFX05, voice=VOICE05,
                   music=dict(style="lofi", bpm=84, root=57, prog="minor2", lv=[(0, 1), (2.0, 2)], seed=9),
                   caption="Tu coches 2 cases ou plus ? Alors il te faut un site web ✅ On s'occupe de tout, devis gratuit 👇"))


# ====================================================================== 06
# « Ton site vend pendant que tu dors » : écran verrouillé, commandes la nuit, lever du soleil
_r6 = random.Random(6)
STARS = [(_r6.uniform(30, 1050), _r6.uniform(150, 1100), _r6.choice([4, 6, 8]), _r6.uniform(1.5, 4), _r6.uniform(0, 6.3)) for _ in range(90)]


def vgrad(c1, c2):
    a, b = np.array(col(c1)[:3], np.float32), np.array(col(c2)[:3], np.float32)
    ty = np.linspace(0, 1, 192, dtype=np.float32)[:, None, None]
    arr = (a + (b - a) * ty).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, 2, axis=1)).resize((W, H), BICUBIC)


@functools.lru_cache(maxsize=4)
def moon_sprite():
    m = circle(250, grad=(("#fffbe6", "#e9deb0"), 90)).copy()
    for (x, y, d) in ((60, 70, 54), (150, 130, 40), (90, 160, 30)):
        m.alpha_composite(circle(d, fill=(214, 203, 160, 160)), (x, y))
    return _with_glow(m, "#fff3c4", 40, 0.9)


@functools.lru_cache(maxsize=2)
def sun_sprite():
    return _with_glow(circle(380, grad=(("#fff7c9", "#ffb13b"), 90)), "#ffcf6b", 70, 1.1)


NOTIFS = [(1.8, "🛒", "Nouvelle commande", "Robe wax × 2 — 15 000 F", "#34c759"),
          (3.2, "💬", "Nouveau message", "Vous livrez aussi le week-end ?", "#0a84ff"),
          (4.6, "✅", "Paiement reçu", "Commande n°1042 payée", "#34c759"),
          (6.0, "🛒", "Nouvelle commande", "Sneakers — taille 42", "#ff9500"),
          (7.4, "⭐", "Nouvel avis 5/5", "« Super boutique, livraison rapide ! »", "#ffb800")]
CLOCK = [(0.0, "02:14"), (3.2, "02:47"), (4.6, "03:30"), (6.0, "04:12"), (7.4, "05:05"), (8.7, "06:30")]


def v06(t):
    dawn = e_io(prog(t, 8.3, 3.2))
    img = vgrad(mix("#0a0f2e", "#7b2d8e", dawn), mix("#2d1b69", "#ff9a5c", dawn))
    BE6 = 13.4
    vis = 1 - prog(t, BE6 - 0.5, 0.4)
    ns = 1 - prog(t, 8.3, 2.2)
    if ns > 0.01:
        for (x, y, d, sp, ph) in STARS:
            put(img, circle(d, fill="#ffffff"), x, y, (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * sp + ph))) * ns)
        mp = prog(t, 0.0, 0.8)
        place(img, moon_sprite(), 925, 350 + math.sin(t * 0.6) * 8, s=0.68, alpha=mp * ns)
    if dawn > 0.01:
        place(img, sun_sprite(), 540, lerp(1760, 1360, e_out(prog(t, 8.5, 3.0))), alpha=min(1, dawn * 1.6) * vis)
    if vis > 0.01:
        # en-tête + heure
        head = "Pendant que tu dors… 😴" if t < 8.7 else "Au réveil… ☀️"
        place(img, text(head, "bold", 54, "#e0e6ff" if t < 8.7 else "#ffffff", shadow=(0, 4, 8, "#000000", 0.4)), 540, 232,
              alpha=min(1, prog(t, 0.1, 0.5)) * vis)
        cur = [c for c in CLOCK if t >= c[0]][-1]
        ts_ = prog(t, cur[0], 0.3) if cur[0] > 0 else 1.0
        place(img, text(cur[1], "light", 210, "#ffffff", shadow=(0, 6, 14, "#000000", 0.35)), 520, 390, s=lerp(0.92, 1, e_out(ts_)),
              alpha=min(1, 0.2 + ts_) * prog(t, 0.0, 0.5) * vis)
        # notifications
        ex = e_in(prog(t, 8.6, 0.7))
        n_ = len(NOTIFS)
        for i, (ta, ic, ti, bo, ac) in enumerate(NOTIFS):
            pi = prog(t, ta, 0.45)
            if pi <= 0:
                continue
            slot = sum(e_out(prog(t, NOTIFS[j][0], 0.45)) for j in range(i + 1, n_))
            y = 640 + slot * 178 - ex * 780
            card = notif(ic, ti, bo, "maintenant" if slot < 0.5 else f"il y a {int(slot) + 1} min", w=940, accent=ac, dark=True)
            place(img, card, 540, y - (1 - e_out(pi)) * 60, s=lerp(0.92, 1, e_back(pi)), alpha=min(1, pi * 2.5) * (1 - ex) * vis)
        if t > 9.3:
            slam(img, text("Un site web =\nun vendeur qui\n**ne dort jamais** 💪", "black", 88, "#ffffff", hl="#ffe066", ls=1.12,
                           shadow=(0, 6, 16, "#3a1030", 0.6)), 540, 840, t, 9.3, alpha=1 - prog(t, 11.1, 0.3))
        if t > 11.3:
            a = e_out(prog(t, 11.3, 0.4))
            place(img, text("Tu te réveilles…\net les commandes\nsont **déjà là** ☀️", "black", 84, "#ffffff", hl="#ffe066", ls=1.12,
                            shadow=(0, 6, 16, "#3a1030", 0.6)), 540, 840, s=lerp(0.9, 1, a), alpha=a * vis)
    if t >= BE6:
        endcard(img, t - BE6, THEMES["night"], headline="Ton site vend\n**24h/24**", sub="Devis gratuit • Écris-nous")
    return img


SFX06 = ([(n[0], "notif", 0.8) for n in NOTIFS] + [(n[0] + 0.05, "tick", 0.4) for n in NOTIFS] + [(0.3, "whoosh", 0.4)]
         + [(7.4, "riser", 0.8), (8.7, "sparkle", 0.7), (9.3, "slam", 0.8), (9.3, "impact", 0.5), (11.3, "whoosh"), (11.4, "pop"),
            (13.35, "impact", 0.8), (13.4, "whoosh"), (13.8, "pop"), (14.4, "ding", 0.8)])
VOICE06 = [dict(text="Pendant que tu dors,", at=0.3, end=1.9),
           dict(text="une commande !", at=1.95, end=3.15),
           dict(text="Un message !", at=3.35, end=4.55),
           dict(text="Un paiement !", at=4.75, end=5.95),
           dict(text="Une autre commande !", at=6.1, end=7.35),
           dict(text="Et un avis cinq étoiles !", at=7.5, end=9.2),
           dict(text="Ton site, un vendeur qui ne dort jamais !", at=9.3, end=11.3),
           dict(text="Tu te réveilles, et les commandes sont déjà là !", at=11.4, end=14.4),
           dict(text="Devis gratuit : écris-nous !", at=14.7, end=17.5)]
SCENES.append(dict(id=6, slug="ton-site-vend-pendant-que-tu-dors", dur=18.4, end=13.4, logo_pos="tl", frame=v06, sfx=SFX06, voice=VOICE06,
                   music=dict(style="ambient", bpm=90, root=57, prog="minor", lv=[(0, 1), (1.5, 2)], seed=12),
                   caption="Pendant que tu dors, ton site web vend à ta place 😴➡️💰 Un vendeur qui ne dort jamais ! Devis gratuit, écris-nous."))
