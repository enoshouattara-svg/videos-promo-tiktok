# -*- coding: utf-8 -*-
"""Vidéos 7 et 8."""
import functools
import math
import random

from ui import *  # noqa: F401,F403
from components import THEMES, endcard
from engine import _with_glow

SCENES = []


# ====================================================================== 07
# « Ton app mobile » : une vraie application à ton nom (écrans animés dans un téléphone)
PUR, PNK, GRN = "#7c3aed", "#ec4899", "#16a34a"
SW7, SH7 = 440, 900
T_HOME, T_CART, T_DONE = 2.5, 5.7, 8.0
HOME_ROWS = [("👗", "Robe wax", "15 000 F", "#fde7f3"), ("👟", "Sneakers", "18 000 F", "#e0f2fe"), ("👜", "Sac cuir", "18 000 F", "#fef3c7")]


def status(img, fg="#ffffff"):
    sw = img.width
    put(img, text("9:41", "bold", 22, fg), 30, 10)
    for k in range(4):
        img.paste(Image.new("RGB", (6, 6 + k * 4), fg), (sw - 118 + k * 10, 34 - k * 4))
    place(img, rrect(36, 18, 5, fill=fg), sw - 48, 28)
    place(img, rrect(4, 8, 2, fill=fg), sw - 28, 28)


@functools.lru_cache(maxsize=32)
def prow(emoji, name, price, bg, state):
    w, h = 392, 124
    spr = rrect(w, h, 26, fill="#ffffff", shadow=(0, 6, 12, "#000000", 0.13)).copy()
    pad = (spr.width - w) // 2
    spr.alpha_composite(rrect(92, 92, 22, fill=bg), (pad + 16, pad + 16))
    e = text(emoji, "bold", 54)
    spr.alpha_composite(e, (pad + 16 + (92 - e.width) // 2, pad + 30))
    spr.alpha_composite(text(name, "bold", 28, "#1f2937"), (pad + 124, pad + 14))
    spr.alpha_composite(text(price, "black", 26, PUR), (pad + 124, pad + 54))
    btn = chip("+ Ajouter", "#ffffff", PUR, size=22, px=16, py=10) if state == 0 else chip("✓ Ajouté", "#ffffff", GRN, size=22, px=16, py=10)
    spr.alpha_composite(btn, (pad + w - 14 - btn.width, pad + h - 14 - btn.height))
    return spr


def add_count(t):
    return int(t >= 4.3) + int(t >= 5.0)


def nav_bar(img):
    img.paste(Image.new("RGB", (SW7, 84), "#ffffff"), (0, SH7 - 84))
    img.paste(Image.new("RGB", (SW7, 2), "#ede9fe"), (0, SH7 - 84))
    for i, e in enumerate(["🏠", "🔍", "🛒", "👤"]):
        place(img, text(e, "bold", 36), 55 + i * 110, SH7 - 44, alpha=1.0 if i == 0 else 0.45)
    place(img, circle(8, fill=PUR), 55, SH7 - 12)


def s_splash(t):
    img = gradient(SW7, SH7, (PUR, PNK), 120).convert("RGB")
    status(img)
    p = e_back(prog(t, 1.0, 0.6))
    place(img, circle(170, fill="#ffffff", shadow=(0, 10, 20, "#000000", 0.25)), 220, 380, s=p)
    place(img, text("M", "black", 104, PUR), 220, 384, s=p)
    place(img, text("MonApp", "black", 50, "#ffffff"), 220, 524, alpha=prog(t, 1.3, 0.4))
    place(img, text("Ta boutique dans ta poche", "reg", 23, "#f3e8ff"), 220, 574, alpha=prog(t, 1.4, 0.4))
    place(img, rrect(220, 10, 5, fill=(255, 255, 255, 80)), 220, 700)
    w = int(220 * prog(t, 1.4, 1.0))
    if w > 8:
        put(img, rrect(w, 10, 5, fill="#ffffff"), 110, 695)
    return img


def s_home(t):
    img = Image.new("RGB", (SW7, SH7), "#f5f3ff")
    img.paste(gradient(SW7, 214, (PUR, PNK), 120).convert("RGB"), (0, 0))
    status(img)
    put(img, text("Bonjour 👋", "black", 36, "#ffffff"), 22, 50)
    put(img, text("Que veux-tu acheter ?", "reg", 22, "#f3e8ff"), 24, 102)
    place(img, rrect(392, 56, 28, fill="#ffffff"), 220, 172)
    put(img, text("🔍  Rechercher…", "reg", 24, "#9ca3af"), 44, 154)
    n = add_count(t)
    place(img, text("🛒", "bold", 40), 396, 86)
    if n:
        place(img, circle(30, fill="#ef4444"), 418, 64, s=1 + 0.25 * max(0, 1 - (t - (4.3 if n == 1 else 5.0)) * 5))
        place(img, text(str(n), "black", 20, "#ffffff"), 418, 64)
    x = 24
    for i, lab in enumerate(["Tout", "Mode", "Chaussures", "Sacs"]):
        c = chip(lab, "#ffffff" if i == 0 else "#6b7280", PUR if i == 0 else "#ffffff", size=22, px=18, py=10)
        put(img, c, x, 250)
        x += c.width + 10
    for i, row in enumerate(HOME_ROWS):
        place(img, prow(*row, int(n > i)), 220, 372 + i * 142)
    nav_bar(img)
    return img


def s_cart(t):
    img = Image.new("RGB", (SW7, SH7), "#f5f3ff")
    img.paste(Image.new("RGB", (SW7, 128), "#ffffff"), (0, 0))
    status(img, "#111827")
    put(img, text("←  Mon panier", "black", 32, "#1f2937"), 22, 62)
    for i, row in enumerate(HOME_ROWS[:2]):
        place(img, prow(*row, 1), 220, 220 + i * 142)
    place(img, rrect(392, 190, 26, fill="#ffffff", shadow=(0, 6, 12, "#000000", 0.12)), 220, 570)
    for i, (a, b, bold) in enumerate([("Sous-total", "33 000 F", 0), ("Livraison", "Offerte", 0), ("Total", "33 000 F", 1)]):
        put(img, text(a, "bold" if bold else "reg", 28, "#1f2937"), 44, 498 + i * 54)
        r = text(b, "black" if bold else "semi", 28, PUR if bold else "#1f2937")
        put(img, r, 396 - r.width, 498 + i * 54)
    press = max(0.0, 1 - abs(t - 7.2) * 6)
    place(img, rrect(392, 76, 38, fill=GRN, shadow=(0, 8, 14, "#000000", 0.25)), 220, 746, s=1 - 0.05 * press)
    place(img, text("Payer maintenant", "black", 30, "#ffffff"), 220, 744, s=1 - 0.05 * press)
    return img


def s_done(t):
    img = gradient(SW7, SH7, ("#16a34a", "#bbf7d0", "#f0fdf4"), 90).convert("RGB")
    status(img, "#ffffff")
    p = e_back(prog(t, T_DONE + 0.15, 0.55))
    place(img, circle(190, fill="#ffffff", shadow=(0, 12, 22, "#000000", 0.22)), 220, 330, s=p)
    place(img, check_sprite(120, GRN, 18, round(prog(t, T_DONE + 0.5, 0.4) * 12) / 12), 220, 330)
    a = prog(t, T_DONE + 0.7, 0.4)
    place(img, text("Commande\nconfirmée !", "black", 46, "#14532d", ls=1.05), 220, 520, alpha=a)
    place(img, text("Tu recevras une notification\ndès l'expédition 🔔", "reg", 25, "#166534", ls=1.2), 220, 640, alpha=a)
    return img


def app_screen(t):
    def slide(prev, nxt, t0):
        a = prog(t, t0, 0.42)
        if a >= 1:
            return nxt(t)
        base = prev(t).copy()
        base.paste(nxt(t), (int((1 - e_out(a)) * SW7), 0))
        return base
    if t < T_HOME:
        return s_splash(t)
    if t < T_CART:
        return slide(s_splash, s_home, T_HOME)
    if t < T_DONE:
        return slide(s_home, s_cart, T_CART)
    return slide(s_cart, s_done, T_DONE)


_r7 = random.Random(7)
ORBS = [(_r7.uniform(0, W), _r7.uniform(0, H + 300), _r7.uniform(60, 220), _r7.uniform(14, 40), _r7.uniform(0.06, 0.14)) for _ in range(9)]


def v07(t):
    img = blobs_bg(t, "#1e1b4b", [("#7c3aed", .2, .2, .6, .06, .04, .5, 0, .55), ("#ec4899", .85, .75, .6, .06, .05, .4, 2, .50),
                                  ("#38bdf8", .8, .1, .45, .05, .04, .6, 4, .30)])
    for (x, y0, d, sp, a) in ORBS:
        place(img, circle(int(d), fill="#ffffff"), x, (y0 - sp * t) % (H + 400) - 200, alpha=a)
    BE7 = 13.0
    vis = 1 - prog(t, BE7 - 0.5, 0.4)
    if vis > 0.01:
        a = e_out(prog(t, 0.1, 0.5))
        if t < 9.3:
            place(img, text("Ton business dans\nla poche de tes **clients** 📲", "black", 64, "#ffffff", hl="#f0abfc", ls=1.1, shadow=(0, 4, 12, "#000000", 0.35)),
                  540, 280 - (1 - a) * 40, alpha=a * (1 - prog(t, 8.9, 0.35)))
        else:
            place(img, text("Une vraie application\nà **ton nom** ✨", "black", 64, "#ffffff", hl="#f0abfc", ls=1.1, shadow=(0, 4, 12, "#000000", 0.35)),
                  540, 280, alpha=prog(t, 9.3, 0.4) * vis)
        pp = e_back(prog(t, 0.3, 0.9), 1.1)
        scr = app_screen(t)
        sc = scr.copy()
        # doigt + ondulation sur les actions
        taps = [(4.3, 338, 398), (5.0, 338, 540), (7.2, 220, 748)]
        for (tt, fx, fy) in taps:
            dt = t - (tt - 0.5)
            if 0 <= dt < 0.5 + 0.55:
                k = prog(dt, 0, 0.5)
                px = lerp(fx + 90, fx, e_out(k))
                py = lerp(fy + 160, fy, e_out(k))
                ripple(sc, fx, fy, prog(t, tt, 0.5), "#ffffff", d=90, ow=7)
                if t < tt + 0.5:
                    place(sc, text("👆", "bold", 84), px + 6, py + 36, s=1 - 0.1 * max(0, 1 - abs(t - tt) * 7), alpha=min(1, k * 2) * (1 - prog(t, tt + 0.25, 0.25)))
        cy = lerp(2250, 940, pp) + math.sin(t * 1.6) * 8
        put_phone(img, sc, 540, cy, s=1.13, rot=lerp(6, 0, e_out(prog(t, 0.3, 0.9))), alpha=vis)
        if T_DONE <= t:
            confetti(img, t, T_DONE + 0.2, n=80, seed=3, origin=(540, 760), colors=("#f0abfc", "#fde047", "#ffffff", "#67e8f9", "#86efac"), life=2.6)
        for i, (lab, x, y, rr) in enumerate([("🎨 Ton logo", 230, 640, -6), ("🌈 Tes couleurs", 840, 960, 5), ("🔔 Notifications clients", 330, 1290, -3)]):
            if t > 9.7:
                place(img, chip(lab, "#3b0764", "#fdf4ff", size=36), x, y + math.sin(t * 2 + i) * 8, s=pop(t, 9.8 + i * 0.6, 0.45), rot=rr, alpha=vis)
    if t >= BE7:
        endcard(img, t - BE7, THEMES["violet"], headline="Ton app,\nà **ton nom** !", sub="Parlons de ton projet • Devis gratuit")
    return img


SFX07 = ([(0.3, "whoosh", 0.7), (1.0, "pop"), (1.5, "pop", 0.6), (2.5, "swipe"), (3.8, "whoosh", 0.3), (4.3, "click"), (4.35, "pop"),
          (5.0, "click"), (5.05, "pop"), (5.7, "swipe"), (7.2, "click"), (8.0, "success", 0.8), (8.05, "sparkle", 0.7),
          (9.8, "pop"), (10.4, "pop"), (11.0, "pop"), (11.6, "riser", 0.6), (12.95, "impact", 0.7), (13.0, "whoosh"), (13.4, "pop"), (14.0, "ding", 0.8)])
# Voix off (variante « voix-off » de la vidéo : python source/build.py voice 7 hortense paul)
# at = instant de départ voulu, end = fin à ne pas dépasser (la ligne est accélérée au besoin pour tenir dedans)
VOICE07 = [dict(text="Ton business dans la poche de tes clients !", at=0.45, end=3.75),
           dict(text="Ils choisissent, ils ajoutent au panier,", at=3.95, end=6.9),
           dict(text="et commandent en un clic !", at=7.05, end=9.25),
           dict(text="Une vraie application, à ton nom, avec ton logo et tes couleurs.", at=9.4, end=13.15),
           dict(text="Devis gratuit ! Scanne le QR code, ou écris-nous sur WhatsApp.", at=13.65, end=17.85)]
SCENES.append(dict(id=7, slug="ton-app-mobile-a-ton-nom", dur=18.0, end=13.0, frame=v07, sfx=SFX07, voice=VOICE07,
                   music=dict(style="edm", bpm=124, root=55, prog="major", lv=[(0, 1), (2.4, 2), (8.0, 3)], seed=14),
                   caption="Une vraie application mobile, à ton nom, avec ton logo et tes couleurs 📲✨ On la crée pour toi. Devis gratuit !"))


# ====================================================================== 08
# « Comment ça marche ? » : 3 étapes, frise verticale + fusée
TEAL, TEAL_D = "#0d9488", "#06302d"
STEPS = [("📞", "Tu nous contactes", "On discute de ton projet\net de ton budget.", 1.6),
         ("🎨", "On crée ta maquette", "Tu vois le design\net tu valides.", 4.3),
         ("🚀", "Ton site est en ligne", "Prêt à accueillir\ntes premiers clients !", 7.0)]
NODE_Y = [590, 890, 1190]
LINE_X = 140


@functools.lru_cache(maxsize=8)
def step_card(emoji, title, desc, w=750, h=240):
    spr = rrect(w, h, 38, fill="#ffffff", shadow=(0, 12, 24, "#06302d", 0.16)).copy()
    pad = (spr.width - w) // 2
    e = text(emoji, "bold", 92)
    spr.alpha_composite(e, (pad + 26, pad + (h - e.height) // 2 + 4))
    spr.alpha_composite(text(title, "black", 46, TEAL_D), (pad + 152, pad + 28))
    spr.alpha_composite(text(desc, "reg", 34, "#3f6f6a", align="left", ls=1.15), (pad + 152, pad + 98))
    return spr


def v08(t):
    img = blobs_bg(t, "#effaf7", [("#5eead4", .1, .15, .5, .06, .04, .5, 0, .55), ("#fde68a", .9, .55, .5, .05, .05, .4, 2, .55),
                                  ("#a5f3fc", .2, .95, .55, .06, .04, .5, 4, .5)])
    BE8 = 12.2
    vis = 1 - prog(t, BE8 - 0.5, 0.4)
    if vis > 0.01:
        a = e_out(prog(t, 0.1, 0.5))
        place(img, text("Comment ça marche ?", "black", 84, TEAL_D), 540, 322 - (1 - a) * 30, alpha=a * vis)
        place(img, text("Seulement 3 étapes", "semi", 46, "#2f6f6a"), 540, 424, alpha=prog(t, 0.4, 0.5) * vis)
        # ligne verticale
        ys = NODE_Y
        for i in range(2):
            seg0 = STEPS[i][3] + 0.4
            h_full = ys[i + 1] - ys[i]
            hp = int(h_full * e_io(prog(t, seg0, 1.5)))
            if hp > 4:
                put(img, rrect(14, hp, 7, fill="#99e0d6"), LINE_X - 7, ys[i], vis)
        for i, (emo, ti, de, t0) in enumerate(STEPS):
            pn = pop(t, t0, 0.5)
            if pn <= 0:
                continue
            place(img, circle(112, fill=TEAL, shadow=(0, 8, 16, "#06302d", 0.3)), LINE_X, ys[i], s=pn, alpha=vis)
            place(img, text(str(i + 1), "black", 62, "#ffffff"), LINE_X, ys[i] - 2, s=pn, alpha=vis)
            pc = e_out(prog(t, t0 + 0.15, 0.5))
            place(img, step_card(emo, ti, de), 255 + 375 + (1 - pc) * 500, ys[i], alpha=min(1, pc * 2) * vis)
        # fusée
        if t > 9.0:
            k = e_in(prog(t, 9.0, 1.2))
            place(img, text("🚀", "bold", 120), LINE_X, ys[2] - k * 1300, rot=45, alpha=vis * (1 - prog(t, 10.1, 0.3)))
        if t > 8.9:
            a = e_out(prog(t, 9.1, 0.4))
            place(img, text("Simple. Rapide. **Pro.**", "black", 80, TEAL_D, hl=TEAL), 540, 1372 - (1 - a) * 30, alpha=a * vis)
    if t >= BE8:
        endcard(img, t - BE8, THEMES["teal"], headline="Lance ton\n**projet** !", sub="Devis gratuit • Écris-nous")
    return img


SFX08 = ([(0.15, "pop"), (0.5, "whoosh", 0.4)] + [(s[3], "pop") for s in STEPS] + [(s[3] + 0.2, "whoosh", 0.4) for s in STEPS]
         + [(STEPS[0][3] + 0.45, "ding", 0.5), (STEPS[1][3] + 0.45, "ding", 0.5), (STEPS[2][3] + 0.45, "success", 0.7),
            (8.8, "riser", 0.6), (9.0, "whoosh", 0.9), (9.15, "pop"), (12.15, "impact", 0.7), (12.2, "whoosh"), (12.6, "pop"), (13.2, "ding", 0.8)])
VOICE08 = [dict(text="Comment ça marche ?", at=0.25, end=1.55),
           dict(text="Un : tu nous contactes, on parle de ton projet.", at=1.7, end=4.25),
           dict(text="Deux : on crée ta maquette, et tu valides le design.", at=4.4, end=6.95),
           dict(text="Trois : ton site est en ligne !", at=7.1, end=8.95),
           dict(text="Simple, rapide, pro !", at=9.15, end=11.0),
           dict(text="Lance ton projet : devis gratuit, écris-nous !", at=12.7, end=16.3)]
SCENES.append(dict(id=8, slug="comment-ca-marche-3-etapes", dur=17.2, end=12.2, frame=v08, sfx=SFX08, voice=VOICE08,
                   music=dict(style="edm", bpm=116, root=57, prog="major2", lv=[(0, 1), (1.4, 2), (8.8, 3)], seed=21),
                   caption="Comment ça marche ? 1️⃣ Tu nous contactes 2️⃣ On crée ta maquette 3️⃣ Ton site est en ligne 🚀 Simple, rapide, pro. Devis gratuit !"))
