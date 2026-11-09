# -*- coding: utf-8 -*-
"""Vidéos 1 à 4."""
import functools
import math
import random
import re

from ui import *  # noqa: F401,F403
from components import THEMES, endcard

LIME, PINK, RED = "#b6ff3b", "#ff2d95", "#ff3b5c"
SCENES = []


# ====================================================================== 01
# « Sans site, tu rates des clients » : typographie cinétique néon
@functools.lru_cache(maxsize=32)
def result_card(title, url, rating, color, letter, bad=False):
    w, h = 940, 152
    if bad:
        spr = rrect(w, h, 34, fill="#2b0d19", outline=RED, ow=5, shadow=(0, 10, 22, "#000000", 0.35)).copy()
    else:
        spr = rrect(w, h, 34, fill="#ffffff", shadow=(0, 10, 22, "#000000", 0.35)).copy()
    pad = (spr.width - w) // 2
    spr.alpha_composite(circle(84, fill=color), (pad + 28, pad + (h - 84) // 2))
    lt_ = text(letter, "black", 46, "#ffffff")
    spr.alpha_composite(lt_, (pad + 28 + (84 - lt_.width) // 2, pad + (h - lt_.height) // 2 - 2))
    spr.alpha_composite(text(title, "bold", 42, "#ffffff" if bad else "#111827"), (pad + 140, pad + 20))
    spr.alpha_composite(text(url, "reg", 30, "#ff8fa3" if bad else "#0f9d58"), (pad + 140, pad + 82))
    r = text(rating, "semi", 34, "#ff8fa3" if bad else "#6b7280")
    spr.alpha_composite(r, (pad + w - 28 - r.width, pad + (h - r.height) // 2))
    return spr


def v01(t):
    img = blobs_bg(t, "#07070d", [("#b6ff3b", .88, .10, .50, .05, .03, .7, .0, .20),
                                  ("#ff2d95", .08, .92, .60, .06, .03, .6, 2.0, .26),
                                  ("#5b3bff", .50, .52, .55, .10, .05, .4, 4.0, .13)])
    draw_grid(img, t, speed=70, color="#8a7bff", alpha=22)
    B2, B3, B4, B5, BE = 2.4, 6.0, 8.6, 11.4, 13.6

    if t < B2:                                                         # accroche
        L = [("TU VENDS", 150, "#ffffff", 0.15, 600), ("SUR **WHATSAPP**", 112, "#ffffff", 0.65, 782),
             ("OU INSTAGRAM ?", 100, "#ffffff", 1.2, 926)]
        for txt, sz, c, t0, y in L:
            spr = fit(txt, "black", sz, 940, fill=c, hl=LIME, glow=(LIME, 12, 0.5) if "WHATS" in txt else None)
            slam(img, spr, 540, y, t, t0)
            img = flash(img, t, t0, 0.12, "#ffffff", 0.16)
        if t > 1.7:
            p = pop(t, 1.7, 0.5)
            place(img, text("🤔", "bold", 210), 540, 1150 - abs(math.sin((t - 1.7) * 5.5)) * 34, s=p)
    elif t < B3:                                                       # recherche Google
        lt = t - B2
        a = prog(lt, 0.05, 0.4)
        swap = prog(lt, 2.55, 0.25)
        place(img, text("Tes clients te cherchent sur **Google**…", "black", 60, "#ffffff", hl=LIME, max_w=740, ls=1.12),
              540 - (1 - e_out(a)) * 120, 300, alpha=a * (1 - swap))
        place(img, text("…et ils trouvent tes **concurrents** 😬", "black", 60, "#ffffff", hl=PINK, max_w=740, ls=1.12),
              540, 300, alpha=swap)
        pb = pop(lt, 0.2, 0.45)
        place(img, rrect(920, 112, 56, fill="#ffffff", shadow=(0, 10, 24, "#000000", 0.35)), 540, 520, s=pb)
        if pb > 0.2:
            q = typed("meilleure boutique en ligne", prog(lt, 0.55, 1.1))
            caret = "|" if (int(lt * 2.5) % 2 == 0 and lt < 2.2) else ""
            place(img, text("🔍", "bold", 50), 118, 520)
            place(img, text(q + caret, "reg", 42, "#111827", align="left"), 172, 520, ax=0.0)
        R = [("Concurrent n°1", "www.concurrent1.ci", "⭐ 4,8", "#ff7a59", "A", 1.75),
             ("Concurrent n°2", "www.concurrent2.ci", "⭐ 4,6", "#3b82f6", "B", 2.0),
             ("Concurrent n°3", "www.concurrent3.ci", "⭐ 4,9", "#10b981", "C", 2.25)]
        for i, (ti, ur, ra, co, le, tt) in enumerate(R):
            p = e_out(prog(lt, tt, 0.4))
            if p > 0:
                place(img, result_card(ti, ur, ra, co, le), 540 + (1 - p) * 950, 700 + i * 172, alpha=min(1, p * 2))
        p = prog(lt, 2.7, 0.35)
        if p > 0:
            k = 1 - prog(lt, 2.95, 0.6)
            dx, dy = shake(lt, 14 * k) if k > 0 else (0, 0)
            place(img, result_card("Ta boutique", "Introuvable sur Google", "❌ 0 visite", "#6b7280", "?", True),
                  540 + dx, 1228 + dy, s=lerp(1.3, 1, e_out(p)), alpha=min(1, p * 3))
    elif t < B4:                                                       # pas de site = ...
        lt = t - B3
        for txt, sz, c, t0, y, h in [("PAS DE SITE", 146, "#ffffff", 0.1, 600, None), ("= PAS DE CONFIANCE", 92, "#ffffff", 0.7, 790, None),
                                     ("= PAS DE VENTES", 104, RED, 1.3, 960, RED)]:
            spr = fit(txt, "black", sz, 940, fill=c, glow=(h, 14, 0.6) if h else None)
            slam(img, spr, 540, y, lt, t0)
        img = flash(img, lt, 1.3, 0.16, RED, 0.3)
        if lt > 1.6:
            place(img, text("📉", "bold", 200), 540, 1180 + math.sin(lt * 4) * 10, s=pop(lt, 1.6, 0.5))
    elif t < B5:                                                       # la solution
        lt = t - B4
        img = flash(img, lt, 0.0, 0.18, "#ffffff", 0.5)
        slam(img, fit("ON CRÉE", "black", 120, 940, fill="#ffffff"), 540, 520, lt, 0.05)
        slam(img, fit("TON SITE WEB", "black", 132, 940, fill=LIME, glow=(LIME, 14, 0.6)), 540, 690, lt, 0.35)
        slam(img, fit("PRO", "black", 250, 940, fill="#ffffff"), 540, 930, lt, 0.7)
        pu = e_out(prog(lt, 1.05, 0.35))
        if pu > 0:
            place(img, rrect(int(440 * pu) + 4, 14, 7, fill=LIME), 540, 1068)
        chs = [chip(lab, "#ffffff", None, size=40, outline=c, ow=4) for lab, c in
               [("⚡ Rapide", LIME), ("🎨 Moderne", PINK), ("🎯 Sur mesure", "#5ef2ff")]]
        gap = 24
        x = 540 - (sum(c.width for c in chs) + 2 * gap) / 2
        for i, ch in enumerate(chs):
            place(img, ch, x + ch.width / 2, 1240, s=pop(lt, 1.4 + i * 0.2, 0.4))
            x += ch.width + gap
    elif t < BE:                                                       # bénéfices
        lt = t - B5
        place(img, text("Avec un site web :", "black", 64, "#ffffff"), 540, 330, alpha=prog(lt, 0, 0.3))
        for i, lab in enumerate(["✅ Visible 24h/24", "✅ Image professionnelle", "✅ Clients qui te font confiance", "✅ Plus de ventes 💰"]):
            p = pop(lt, 0.25 + i * 0.4, 0.4)
            card = rrect(900, 118, 36, fill=(255, 255, 255, 22), outline=LIME, ow=3)
            place(img, card, 540 - (1 - e_out(prog(lt, 0.25 + i * 0.4, 0.3))) * 700, 520 + i * 150, alpha=min(1, p * 2))
            place(img, fit(lab, "bold", 48, 820, fill="#ffffff"), 540 - (1 - e_out(prog(lt, 0.25 + i * 0.4, 0.3))) * 700, 520 + i * 150, alpha=min(1, p * 2))
    else:
        endcard(img, t - BE, THEMES["neon"], headline="Ton site web, **maintenant** ?", sub="Devis gratuit • Réponse rapide")
    for b in (B2, B3, B5):
        img = glitch(img, near(t, b, 0.14), seed=int(t * 30))
    return img


SFX01 = ([(0.15, "slam"), (0.65, "slam"), (1.2, "slam"), (1.7, "pop"), (2.3, "glitch"), (2.45, "whoosh", 0.7)]
         + [(2.95 + i * 0.075, "type", 0.5) for i in range(14)]
         + [(4.15, "pop"), (4.4, "pop"), (4.65, "pop"), (5.1, "buzz"), (5.9, "glitch", 0.7), (6.1, "slam"), (6.7, "slam"),
            (7.3, "slam"), (7.35, "impact", 0.7), (7.0, "riser", 0.8), (8.6, "impact"), (8.65, "slam"), (8.95, "slam"), (9.3, "slam"),
            (10.0, "pop"), (10.2, "pop"), (10.4, "pop"), (11.3, "whoosh"), (11.7, "ding", 0.6), (12.1, "ding", 0.6),
            (12.5, "ding", 0.6), (12.9, "ding", 0.6), (13.55, "impact", 0.9), (13.6, "whoosh"), (14.0, "pop"), (14.55, "ding", 0.8)])
# Voix off (at = départ voulu, end = fin à ne pas dépasser ; la ligne est accélérée au besoin) : python source/build.py voice 1 hortense
VOICE01 = [dict(text="Tu vends sur WhatsApp ou Instagram ?", at=0.2, end=2.4),
           dict(text="Tes clients te cherchent sur Google,", at=2.5, end=4.7),
           dict(text="et trouvent tes concurrents.", at=4.8, end=6.1),
           dict(text="Pas de site, pas de confiance, pas de ventes.", at=6.15, end=8.55),
           dict(text="On crée ton site web pro.", at=8.7, end=10.2),
           dict(text="Rapide, moderne, sur mesure.", at=10.25, end=12.4),
           dict(text="Plus de clients, plus de ventes !", at=12.5, end=14.3),
           dict(text="Devis gratuit ! Scanne le QR code, ou écris-nous.", at=14.45, end=18.3)]
SCENES.append(dict(id=1, slug="sans-site-tu-rates-des-clients", dur=18.6, end=13.6, frame=v01, sfx=SFX01, voice=VOICE01,
                   music=dict(style="trap", bpm=140, root=57, prog="minor", lv=[(0, 2), (8.6, 3)], seed=2),
                   caption="Tu vends sur WhatsApp ? Sans site web, tu rates des clients chaque jour 📉 On crée ton site pro. Devis gratuit, écris-nous 👇"))


# ====================================================================== 02
# « Du code à ton site » : éditeur de code -> site sur téléphone
CODE = ['<header>',
        '  <img src="logo.png" />',
        '  <nav>Accueil · Boutique · Contact</nav>',
        '</header>',
        '<section class="hero">',
        '  <h1>Ma Boutique</h1>',
        '  <p>Les meilleurs produits, chez toi</p>',
        '  <button>Commander</button>',
        '</section>']
C_PUNC, C_TAG, C_ATTR, C_STR, C_TXT = "#8b93c9", "#ff79c6", "#50fa7b", "#f1fa8c", "#e8eaff"
CFS = 34                                  # taille du code
CW = font("mono", CFS).getlength("M")
LHT = 56


def tokenize(line):
    out, i, n = [], 0, len(line)
    while i < n:
        if line[i] == "<":
            j = i + 1
            if j < n and line[j] == "/":
                j += 1
            k = j
            while k < n and (line[k].isalnum() or line[k] == "-"):
                k += 1
            out += [(line[i:j], C_PUNC), (line[j:k], C_TAG)]
            i = k
            while i < n and line[i] != ">" and line[i:i + 2] != "/>":
                if line[i] == " ":
                    out.append((" ", C_PUNC))
                    i += 1
                    continue
                m = re.match(r'([\w-]+)(=)("[^"]*")', line[i:])
                if m:
                    out += [(m.group(1), C_ATTR), ("=", C_PUNC), (m.group(3), C_STR)]
                    i += len(m.group(0))
                else:
                    out.append((line[i], C_PUNC))
                    i += 1
            if line[i:i + 2] == "/>":
                out.append(("/>", C_PUNC))
                i += 2
            elif i < n:
                out.append((">", C_PUNC))
                i += 1
        else:
            j = line.find("<", i)
            j = n if j < 0 else j
            out.append((line[i:j], C_TXT))
            i = j
    return out


@functools.lru_cache(maxsize=2)
def editor_base():
    spr = rrect(940, 830, 30, fill="#14162b", outline="#2c3163", ow=3, shadow=(0, 22, 40, "#000000", 0.55)).copy()
    pad = (spr.width - 940) // 2
    spr.alpha_composite(rrect(934, 72, 27, fill="#1c2042"), (pad + 3, pad + 3))
    spr.alpha_composite(Image.new("RGBA", (934, 34), col("#1c2042") + (255,)), (pad + 3, pad + 41))
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        spr.alpha_composite(circle(22, fill=c), (pad + 30 + i * 36, pad + 27))
    tb = text("index.html", "mono", 28, "#c9d1ff")
    spr.alpha_composite(tb, (pad + (940 - tb.width) // 2, pad + 22))
    for i in range(len(CODE)):
        n = text(str(i + 1), "mono", 30, "#5b628f", align="right")
        spr.alpha_composite(n, (pad + 78 - n.width, pad + 98 + i * LHT))
    spr.alpha_composite(Image.new("RGBA", (2, 560), col("#262b57") + (255,)), (pad + 92, pad + 90))
    return spr, pad


def draw_code(ed, pad, nchars, t):
    x0, y0 = pad + 112, pad + 100
    rem = nchars
    caret = (0, 0)
    for li, line in enumerate(CODE):
        n = min(len(line), rem)
        ci = 0
        for tok, c in tokenize(line):
            if ci >= n:
                break
            seg = tok[: n - ci]
            body = seg.strip(" ")
            if body:
                lead = len(seg) - len(seg.lstrip(" "))
                put(ed, text(body, "mono", CFS, c, align="left"), x0 + (ci + lead) * CW - 6, y0 + li * LHT - 6)
            ci += len(seg)
        caret = (li, n)
        rem -= len(line) + 1
        if rem < 0:
            break
    if int(t * 2.2) % 2 == 0 or nchars < sum(len(l) + 1 for l in CODE):
        put(ed, rrect(5, 44, 2, fill="#5ef2ff"), x0 + caret[1] * CW - 2, y0 + caret[0] * LHT + 2)


def draw_terminal(ed, pad, lt):
    p = e_out(prog(lt, 0, 0.35))
    if p <= 0:
        return
    base = pad + 640
    place(ed, rrect(900, 164, 22, fill="#080913", outline="#2c3163", ow=2), pad + 470, base + 82 + (1 - p) * 40, alpha=p)
    y = base + 14 + (1 - p) * 40
    cmd = typed("npm run build", prog(lt, 0.15, 0.8))
    put(ed, text("$", "monob", 30, "#50fa7b", align="left"), pad + 50, y - 4, p)
    put(ed, text(cmd, "mono", 30, "#ffffff", align="left"), pad + 90, y - 4, p)
    if lt > 1.1:
        put(ed, text("✅ Compilé en 1,2 s", "mono", 30, "#9ef0b8", align="left"), pad + 50, y + 44, prog(lt, 1.1, 0.2))
    if lt > 1.6:
        put(ed, text("✅ En ligne : www.maboutique.ci", "mono", 30, "#5ef2ff", align="left"), pad + 50, y + 88, prog(lt, 1.6, 0.2))


SYMS = [("{ }", 96), ("</>", 84), ("=>", 90), ("( )", 84), ("#", 96), ("<div>", 58), ("fn()", 60), ("&&", 86), ("[ ]", 90),
        ("const", 56), ("npm", 56), (";", 110), ("<p>", 64), ("//", 90)]
_rs = random.Random(4)
SYM_POS = [(_rs.uniform(40, 1000), _rs.uniform(0, H + 200), _rs.uniform(24, 56), _rs.uniform(0.07, 0.15),
            _rs.choice(["#7c8cff", "#5ef2ff", "#a78bfa"])) for _ in SYMS]


def v02(t):
    img = new_frame(["#0a0d1f", "#1b1747"], 100)
    for (s, sz), (x, y0, sp, a, c) in zip(SYMS, SYM_POS):
        y = (y0 - sp * t) % (H + 260) - 130
        place(img, text(s, "monob", sz, c), x, y, alpha=a)
    BP, BE = 9.0, 14.0
    if t < BP:
        a = prog(t, 0.1, 0.5)
        place(img, text("Ton idée → ton **site web** 🚀", "black", 68, "#ffffff", hl="#5ef2ff", max_w=940, ls=1.1),
              540, 300 + (1 - e_out(a)) * 40, alpha=a * (1 - prog(t, 8.55, 0.4)))
    elif t < BE:
        a = prog(t, BP + 0.2, 0.4)
        place(img, text("Ton site, **sur mobile** 📱", "black", 68, "#ffffff", hl="#5ef2ff", max_w=940, ls=1.1),
              540, 296 + (1 - e_out(a)) * 30, alpha=a * (1 - prog(t, 13.5, 0.4)))
    # éditeur
    ex = e_in(prog(t, 8.9, 0.6))
    if t < BP + 0.7:
        ed, pad = editor_base()
        ed = ed.copy()
        total = sum(len(l) + 1 for l in CODE) - 1
        draw_code(ed, pad, int(total * e_io(prog(t, 1.5, 5.4))), t)
        draw_terminal(ed, pad, t - 7.0)
        pe = pop(t, 0.5, 0.5)
        place(img, ed, 540, 840 - ex * 560, s=lerp(0.88, 1, pe), alpha=min(1, pe * 1.5) * (1 - ex))
    # téléphone
    if BP <= t < BE + 0.5:
        pp = e_back(prog(t, BP + 0.1, 0.85), 1.2)
        ps = prog(t, BP + 1.2, 3.4)
        scr = site_screen(t, e_io(ps) * 420)
        ph_cy = lerp(2100, 880, pp) + math.sin(t * 1.7) * 7
        out = prog(t, 13.5, 0.4)
        put_phone(img, scr, 540, ph_cy, s=1.0, rot=lerp(-9, 0, e_out(prog(t, BP + 0.1, 0.9))), alpha=1 - out)
        if t > 10.1:
            p = pop(t, 10.1, 0.4)
            place(img, chip("🟢  En ligne • www.maboutique.ci", "#eafff1", "#14532d", size=32, fk="semi"), 540, 372, s=p, alpha=1 - out)
        for i, (lab, bg, x, y, rr) in enumerate([("⚡ Rapide", "#5ef2ff", 230, 640, -6), ("📱 Adapté mobile", "#a78bfa", 810, 930, 5),
                                              ("🎨 Sur mesure", "#ff79c6", 250, 1200, -4)]):
            p = pop(t, 11.2 + i * 0.4, 0.45)
            place(img, chip(lab, "#0b1020", bg, size=36), x, y + math.sin(t * 2 + i) * 9, s=p, rot=rr, alpha=1 - out)
    if t >= BE:
        endcard(img, t - BE, THEMES["code"], headline="Ton idée mérite\nun **vrai site**", sub="Parlons de ton projet • Devis gratuit")
    img = glitch(img, near(t, BP, 0.1) * 0.5, seed=int(t * 30))
    return img


SFX02 = ([(0.2, "pop"), (0.5, "whoosh", 0.5)] + [(1.5 + i * 0.09, "type", 0.5) for i in range(60)]
         + [(6.95, "swipe"), (7.15, "click", 0.7)] + [(7.2 + i * 0.07, "type", 0.5) for i in range(10)]
         + [(8.15, "success", 0.7), (8.85, "whoosh", 0.8), (9.05, "pop"), (9.6, "impact", 0.5), (10.15, "pop"), (11.2, "pop"),
            (11.6, "pop"), (12.0, "pop"), (13.85, "impact", 0.8), (14.0, "whoosh"), (14.4, "pop"), (15.0, "ding", 0.8)])
VOICE02 = [dict(text="Tu as une idée ? On la transforme en site web !", at=0.3, end=3.5),
           dict(text="On écrit le code, ligne après ligne,", at=3.7, end=6.2),
           dict(text="on vérifie que tout fonctionne,", at=6.3, end=8.4),
           dict(text="et ton site est en ligne !", at=8.5, end=10.4),
           dict(text="Rapide, adapté au mobile, et fait sur mesure.", at=10.8, end=13.7),
           dict(text="Ton idée mérite un vrai site. Devis gratuit, écris-nous !", at=14.4, end=18.8)]
SCENES.append(dict(id=2, slug="du-code-a-ton-site", dur=19.5, end=14.0, frame=v02, sfx=SFX02, voice=VOICE02,
                   music=dict(style="chip", bpm=124, root=60, prog="major", lv=[(0, 1), (1.4, 2), (9.0, 3)], seed=3),
                   caption="De l'idée au site web en ligne 💻➡️📱 On code ton projet de A à Z. Devis gratuit, contacte-nous !"))
