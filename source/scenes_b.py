# -*- coding: utf-8 -*-
"""Vidéos 3 et 4."""
import functools
import math

import numpy as np

from ui import *  # noqa: F401,F403
from components import THEMES, endcard
from engine import _with_glow

SCENES = []


# ====================================================================== 03
# « Avant / Après » : WhatsApp qui déborde -> site web propre (balayage sur le téléphone)
CHAT = [("L", "C'est combien ?", 0.6), ("L", "Dispo ?", 1.0), ("R", "Oui dispo", 1.4), ("L", "Tu as la taille M ?", 1.85),
        ("L", "Envoie les photos", 2.3), ("R", "Attends, je cherche…", 2.75), ("L", "Tu livres où ?", 3.2), ("L", "Allô ?? 😡", 3.65),
        ("L", "J'attends toujours…", 4.1), ("L", "C'est combien ??", 4.5)]


def chat_screen(t, sw=440, sh=900):
    img = Image.new("RGB", (sw, sh), "#e9e1d6")
    top, bot = 122, sh - 86
    cum, items = 0.0, []
    for side, txt, ti in CHAT:
        p = e_out(prog(t, ti, 0.3))
        if p <= 0:
            break
        b = bubble(txt, "left" if side == "L" else "right", fill="#ffffff" if side == "L" else "#d9fdd3", size=27, max_w=270)
        items.append((side, b, p, cum))
        cum += (b.height - 8) * p
    off = max(0.0, cum - (bot - top - 16))
    for side, b, p, c in items:
        y = top + 8 + c - off + (1 - p) * 14
        put(img, b, 8 if side == "L" else sw - 8 - b.width, y, p)
    img.paste(Image.new("RGB", (sw, 122), "#0f766e"), (0, 0))
    put(img, text("9:41", "bold", 22, "#ffffff"), 30, 10)
    place(img, rrect(36, 18, 5, fill="#ffffff"), sw - 48, 28)
    place(img, circle(60, fill="#cbd5e1"), 46, 84)
    place(img, text("👥", "bold", 34), 46, 84)
    put(img, text("Mes clients", "bold", 30, "#ffffff"), 90, 54)
    put(img, text("en ligne", "reg", 21, "#a7f3d0"), 90, 90)
    n = int(lerp(2, 99, e_out(prog(t, 0.6, 4.2))))
    if t > 0.6:
        pulse = 1 + 0.08 * math.sin(t * 9)
        place(img, circle(52, fill="#ef4444"), sw - 52, 84, s=pulse)
        place(img, text("99+" if n >= 99 else str(n), "black", 22 if n >= 99 else 26, "#ffffff"), sw - 52, 84, s=pulse)
    img.paste(Image.new("RGB", (sw, 86), "#f0f2f5"), (0, sh - 86))
    place(img, rrect(sw - 40, 52, 26, fill="#ffffff"), sw / 2, sh - 43)
    put(img, text("Message", "reg", 24, "#9ca3af"), 40, sh - 58)
    return img


@functools.lru_cache(maxsize=2)
def wipe_bar(h):
    return _with_glow(rrect(8, h, 4, fill="#ffffff"), "#ffffff", 14, 1.2)


def v03(t):
    BW, BEND = 6.2, 12.6
    pw = e_io(prog(t, BW, 0.9))
    img = blobs_bg(t, "#12141c", [("#ff3b5c", .2, .2, .5, .06, .04, .6, 0, .20), ("#64748b", .85, .8, .5, .05, .04, .5, 2, .22)])
    if pw > 0:
        bgb = blobs_bg(t, "#06142e", [("#22e07a", .85, .15, .55, .06, .04, .6, 1, .30), ("#38bdf8", .12, .85, .6, .06, .04, .5, 3, .30),
                                       ("#a78bfa", .5, .5, .5, .1, .05, .4, 5, .15)])
        img = Image.blend(img, bgb, pw)
    vis = 1 - prog(t, BEND - 0.5, 0.4)          # le contenu s'efface avant l'écran final
    if vis > 0.01:
        if t < BW + 0.4:
            slam(img, text("AVANT", "black", 128, "#ff3b5c", glow=("#ff3b5c", 14, 0.55)), 540, 290, t, 0.1)
            place(img, text("Sur WhatsApp, ça déborde 😩", "bold", 46, "#ffffff"), 540, 410, alpha=prog(t, 0.5, 0.4))
        else:
            slam(img, text("APRÈS", "black", 128, "#22e07a", glow=("#22e07a", 14, 0.55)), 540, 290, t, BW + 0.4, alpha=vis)
            place(img, text("Avec ton site, tout est clair 😍", "bold", 46, "#ffffff"), 540, 410, alpha=prog(t, BW + 0.8, 0.4) * vis)
        scr = chat_screen(t)
        if pw > 0:
            after = site_screen(t, e_io(prog(t, BW + 1.2, 4.6)) * 380, c1="#0ea5e9", c2="#22c55e")
            sw_, sh_ = scr.size
            xw = int(pw * (sw_ + 30)) - 10
            comp = scr.copy()
            comp.paste(after.crop((0, 0, max(1, min(xw, sw_)), sh_)), (0, 0))
            if 0 < xw < sw_ and pw < 1:
                place(comp, wipe_bar(sh_), xw, sh_ / 2)
            scr = comp
        pe = pop(t, 0.0, 0.6)
        put_phone(img, scr, 540, 950 + math.sin(t * 1.8) * 6, s=lerp(0.85, 1.08, pe), rot=lerp(-3, 0, pw), alpha=min(1, pe * 2) * vis)
        if t > BW + 1.6:
            for i, (lab, x, y, rr) in enumerate([("💰 Prix visibles", 230, 690, -5), ("🛒 Commande en 1 clic", 830, 980, 4),
                                                 ("🔗 Un seul lien à partager", 340, 1270, -3)]):
                place(img, chip(lab, "#06302d", "#eafff4", size=36), x, y + math.sin(t * 2 + i) * 8, s=pop(t, BW + 1.8 + i * 0.8, 0.45),
                      rot=rr, alpha=vis)
    if t >= BEND:
        endcard(img, t - BEND, THEMES["ci"], headline="Prêt pour\nl'**après** ?", sub="Ton site web pro • Devis gratuit")
    img = glitch(img, near(t, BW + 0.1, 0.12) * 0.6, seed=int(t * 30))
    return img


_chat_sfx = [(ti, "msg_in" if s == "L" else "msg_out", 0.7) for s, _, ti in CHAT]
SFX03 = ([(0.1, "slam"), (0.3, "pop")] + _chat_sfx + [(4.8, "riser", 0.8), (6.2, "whoosh"), (6.6, "slam"), (7.0, "success", 0.7),
         (7.8, "pop"), (8.6, "pop"), (9.4, "pop"), (12.5, "impact", 0.8), (12.6, "whoosh"), (13.0, "pop"), (13.6, "ding", 0.8)])
VOICE03 = [dict(text="Avant : les mêmes questions, cent fois par jour.", at=0.4, end=3.7),
           dict(text="Tu réponds à tout, tout le temps !", at=3.85, end=6.1),
           dict(text="Après : un site clair, avec tes prix et un seul lien !", at=6.5, end=10.3),
           dict(text="Ils voient tout, ils commandent.", at=10.5, end=12.5),
           dict(text="Prêt pour l'après ? Devis gratuit, écris-nous !", at=13.0, end=17.2)]
SCENES.append(dict(id=3, slug="avant-apres-ton-site", dur=17.6, end=12.6, frame=v03, sfx=SFX03, voice=VOICE03,
                   music=dict(style="afro", bpm=104, root=55, prog="major2", lv=[(0, 1), (1.0, 2), (6.2, 3)], seed=5),
                   caption="Avant : WhatsApp qui déborde 😩 Après : un site web clair, pro, avec tes prix et un seul lien 🔗 Écris-nous pour un devis !"))


# ====================================================================== 04
# « Un site web, ça coûte combien ? » : machine à sous
CELL_W, CELL_H = 250, 330
REELS = [("TYPE", [("🌐", "Site\nvitrine"), ("🛒", "Boutique\nen ligne"), ("📱", "App\nmobile"), ("📊", "Logiciel\nde gestion")], 1, 5.6),
         ("OPTIONS", [("✨", "Design\npro"), ("🔒", "Sécurité\nrenforcée"), ("📈", "Suivi des\nstatistiques"), ("🎨", "Sur\nmesure")], 0, 6.6),
         ("DÉLAI", [("⚡", "Livraison\nexpress"), ("📅", "Délai\nnormal"), ("🕒", "Délai\nflexible"), ("🚀", "Lancement\nrapide")], 0, 7.6)]
SPIN_START, SPIN_V = 3.6, 14.0


@functools.lru_cache(maxsize=8)
def reel_strip(items):
    n = len(items)
    strip = Image.new("RGBA", (CELL_W, CELL_H * n * 2), (255, 255, 255, 255))
    for k in range(2 * n):
        e, lab = items[k % n]
        place(strip, text(e, "bold", 112), CELL_W / 2, k * CELL_H + 112)
        place(strip, text(lab, "bold", 34, "#111111", ls=1.1), CELL_W / 2, k * CELL_H + 246)
        strip.paste(Image.new("RGBA", (CELL_W, 3), (0, 0, 0, 40)), (0, k * CELL_H))
    return strip


@functools.lru_cache(maxsize=2)
def reel_shade():
    y = np.linspace(0, 1, CELL_H)[:, None]
    a = np.clip((0.26 - y) / 0.26, 0, 1) * 150 + np.clip((y - 0.74) / 0.26, 0, 1) * 150
    arr = np.zeros((CELL_H, CELL_W, 4), np.uint8)
    arr[..., 3] = np.repeat(a, CELL_W, axis=1).astype(np.uint8)
    return Image.fromarray(arr)


@functools.lru_cache(maxsize=2)
def reel_mask():
    return rrect(CELL_W, CELL_H, 28, fill="#ffffff").getchannel("A")


def reel_pos(t, final, n, t_stop):
    t_dec = t_stop - 0.75
    if t < SPIN_START:
        return float(final), 0.0
    if t < t_dec:
        return ((t - SPIN_START) * SPIN_V) % n, SPIN_V
    p0 = (t_dec - SPIN_START) * SPIN_V
    target = math.ceil(p0 + 2.6)
    while target % n != final:
        target += 1
    p = prog(t, t_dec, 0.75)
    pos = lerp(p0, target, e_back(p, 0.9) if p < 1 else 1.0)
    return pos % n, (1 - p) * SPIN_V * 0.6


def reel_window(items, pos, vel):
    n = len(items)
    strip = reel_strip(items)
    y0 = int((pos % n) * CELL_H)
    win = strip.crop((0, y0, CELL_W, y0 + CELL_H))
    if vel > 5:
        win = win.resize((CELL_W, max(2, CELL_H // 7)), BILINEAR).resize((CELL_W, CELL_H), BICUBIC)
    win.alpha_composite(reel_shade())
    win.putalpha(reel_mask())
    return win


@functools.lru_cache(maxsize=2)
def machine_base():
    body = rrect(900, 740, 64, fill="#161616", outline="#ff3b30", ow=9, shadow=(0, 26, 40, "#000000", 0.5)).copy()
    pad = (body.width - 900) // 2
    body.alpha_composite(rrect(640, 92, 32, fill="#ffd60a"), (pad + 130, pad + 62))
    tt = text("🎰 TON DEVIS", "black", 58, "#161616")
    body.alpha_composite(tt, (pad + (900 - tt.width) // 2, pad + 62 + (92 - tt.height) // 2 - 2))
    for i, (lab, *_r) in enumerate(REELS):
        l = text(lab, "black", 30, "#ffd60a")
        body.alpha_composite(l, (pad + 51 + i * 274 + (CELL_W - l.width) // 2, pad + 176))
        body.alpha_composite(rrect(CELL_W + 20, CELL_H + 20, 36, fill="#000000"), (pad + 41 + i * 274, pad + 212))
    body.alpha_composite(rrect(780, 132, 30, fill="#0a0a0a", outline="#2a2a2a", ow=3), (pad + 60, pad + 596))
    return body, pad


@functools.lru_cache(maxsize=4)
def bulb(color, on):
    s = circle(30, fill=color if on else mix(color, "#000000", 0.7))
    return _with_glow(s, color, 12, 1.1) if on else s


@functools.lru_cache(maxsize=1)
def dots_layer():
    step, ss, r = 64, 2, 9
    big = Image.new("L", ((W + 2 * step) * ss, (H + 2 * step) * ss), 0)
    d = ImageDraw.Draw(big)
    for yy in range(0, H + 2 * step, step):
        for xx in range(0, W + 2 * step, step):
            ox = step // 2 if (yy // step) % 2 else 0
            cx, cy = (xx + ox) * ss, yy * ss
            d.ellipse((cx - r * ss, cy - r * ss, cx + r * ss, cy + r * ss), fill=255)
    m = big.resize((W + 2 * step, H + 2 * step), BOX).point([int(v * 0.5) for v in range(256)])
    im = Image.new("RGBA", m.size, (214, 160, 0, 0))
    im.putalpha(m)
    return im


def v04(t):
    BX, BEND4 = 10.5, 12.3
    img = new_frame(["#ffd60a", "#ffc400"], 90)
    put(img, dots_layer(), -64 + (t * 26) % 64, -64 + (t * 26) % 64)
    INK = "#111111"
    # accroche
    if t < 2.7:
        k = prog(t, 2.35, 0.35)
        for txt, sz, t0, y in [("UN SITE WEB,", 124, 0.1, 560), ("ÇA COÛTE", 150, 0.5, 740), ("COMBIEN ?", 170, 0.9, 940)]:
            spr = fit(txt, "black", sz, 940, fill=INK)
            if k < 1:
                slam(img, spr, 540, y - k * 200, t, t0, alpha=1 - k)
        if t > 1.4:
            place(img, text("💸", "bold", 190), 540, 1170 + abs(math.sin((t - 1.4) * 5)) * -40, s=pop(t, 1.4, 0.5), alpha=1 - k)
        for i in range(5):
            qa = prog(t, 1.0 + i * 0.12, 0.3)
            place(img, text("?", "black", 110 + i * 14, "#e11d48"), 120 + i * 210, 1380 - (i % 2) * 60 + math.sin(t * 3 + i) * 12,
                  alpha=qa * (1 - k), rot=(-12 + i * 6))
    if 2.6 <= t < BX + 0.8:
        a = e_out(prog(t, 2.7, 0.4)) * (1 - prog(t, BX, 0.3))
        place(img, text("Voici la vraie réponse ⬇️", "black", 62, INK), 540, 300 - (1 - a) * 40, alpha=a)
        pm = e_back(prog(t, 2.9, 0.7))
        mb, pad = machine_base()
        mcx, mcy = 540, 830
        ex = e_in(prog(t, BX - 0.2, 0.7))
        s_ = lerp(0.6, 1.0, pm)
        cy_ = mcy + ex * 800
        place(img, mb, mcx, cy_, s=s_, alpha=min(1, pm * 2))
        if pm >= 0.99 or t > 3.4:
            for i, (lab, items, final, tstop) in enumerate(REELS):
                pos, vel = reel_pos(t, final, len(items), tstop)
                win = reel_window(tuple(items), pos, vel)
                wx = mcx - 450 + 51 + i * 274 + CELL_W / 2
                wy = mcy - 370 + 222 + CELL_H / 2
                place(img, win, mcx + (wx - mcx) * s_, cy_ + (wy - mcy) * s_, s=s_)
            jack = t > 7.7
            for i in range(11):
                on = ((int(t * (14 if jack else 6)) + i) % 2 == 0)
                bx = mcx - 450 + 50 + i * 80
                place(img, bulb("#ff3b30" if i % 2 else "#ffffff", on), mcx + (bx - mcx) * s_, cy_ + (-370 + 28) * s_ + 4, s=s_)
            if t > 7.7:
                txt = "💰 DEVIS SUR MESURE" if int(t * 4) % 2 == 0 else "💰 DEVIS SUR MESURE ✨"
                place(img, fit(txt, "black", 46, 740, fill="#ffd60a"), mcx, cy_ + (-370 + 662) * s_, s=s_)
            else:
                place(img, text("? ? ?", "monob", 60, "#555555"), mcx, cy_ + (-370 + 662) * s_, s=s_)
            pull = prog(t, 3.4, 0.35) - prog(t, 3.9, 0.45)
            lx = mcx + 450 * s_ + 44
            place(img, rrect(22, 190, 11, fill="#c9c9c9"), lx, cy_ - 80 * s_ + pull * 10, s=s_)
            place(img, circle(78, fill="#ff3b30", shadow=(0, 6, 10, "#000000", 0.4)), lx, cy_ - 190 * s_ + pull * 130 * s_, s=s_)
        if 7.7 <= t < 8.0:
            img = flash(img, t, 7.7, 0.3, "#ffffff", 0.45)
        confetti(img, t, 7.7, n=90, seed=11, origin=(540, 830), colors=("#e11d48", "#ffffff", "#111111", "#ff8a00", "#34d399"), life=2.8)
        if t > 8.4:
            a = e_out(prog(t, 8.4, 0.45)) * (1 - ex)
            place(img, text("Le prix dépend de **ton projet**", "black", 58, INK, hl="#e11d48", max_w=940, ls=1.08), 540, 1262 - (1 - a) * 30, alpha=a)
            place(img, text("Type  +  Options  +  Délai", "semi", 40, "#3a2f00"), 540, 1342, alpha=prog(t, 9.0, 0.4) * (1 - ex))
    if BX <= t < BEND4:
        lt = t - BX
        k = 1 - prog(t, BEND4 - 0.55, 0.4)
        if k > 0.01:
            slam(img, fit("DIS-NOUS", "black", 130, 940, fill=INK), 540, 620, lt, 0.5, alpha=k)
            slam(img, fit("TON BESOIN", "black", 140, 940, fill=INK), 540, 790, lt, 0.8, alpha=k)
            slam(img, fit("ON FAIT LE **DEVIS**", "black", 96, 940, fill=INK, hl="#e11d48"), 540, 975, lt, 1.1, alpha=k)
            if lt > 1.4:
                place(img, text("⬇️", "bold", 170), 540, 1190 + abs(math.sin(lt * 6)) * -30, s=pop(lt, 1.4, 0.4), alpha=k)
    if t >= BEND4:
        endcard(img, t - BEND4, THEMES["yellow"], headline="Parlons **prix** !", sub="Devis gratuit • Dis-nous ton budget")
    return img


def _slot_ticks():
    ev, tt = [], SPIN_START
    while tt < 7.55:
        ev.append((tt, "tick", 0.3))
        tt += 0.065 if tt < 5.6 else 0.09 if tt < 6.6 else 0.13
    return ev


SFX04 = ([(0.1, "slam"), (0.5, "slam"), (0.9, "slam"), (1.4, "pop"), (2.35, "whoosh"), (2.9, "pop"), (3.4, "whoosh", 0.5), (3.55, "click")]
         + _slot_ticks() + [(5.6, "thunk"), (6.6, "thunk"), (7.6, "thunk"), (7.7, "jackpot"), (7.9, "coin", 0.7), (8.1, "coin", 0.7),
                            (8.3, "coin", 0.7), (8.45, "pop"), (10.3, "whoosh"), (11.0, "slam"), (11.3, "slam"), (11.6, "slam"),
                            (12.25, "impact", 0.8), (12.3, "whoosh"), (12.7, "pop"), (13.3, "ding", 0.8)])
VOICE04 = [dict(text="Un site web, ça coûte combien ?", at=0.2, end=2.5),
           dict(text="Voici la vraie réponse !", at=2.85, end=4.5),
           dict(text="Ça dépend du type de projet,", at=4.7, end=6.2),
           dict(text="des options,", at=6.3, end=7.2),
           dict(text="et du délai.", at=7.25, end=8.0),
           dict(text="Résultat : un devis sur mesure, rien que pour toi.", at=8.1, end=10.9),
           dict(text="Dis-nous ton besoin, on s'occupe du devis !", at=11.0, end=13.2),
           dict(text="Devis gratuit ! Parlons de ton budget.", at=13.5, end=16.8)]
SCENES.append(dict(id=4, slug="combien-coute-un-site-web", dur=17.3, end=12.3, frame=v04, sfx=SFX04, voice=VOICE04,
                   music=dict(style="funk", bpm=112, root=52, prog="minor2", lv=[(0, 2), (2.9, 3)], seed=7),
                   caption="Un site web, ça coûte combien ? 💸 Ça dépend de ton projet, de tes options et de ton délai. Écris-nous, le devis est gratuit 🎰"))
