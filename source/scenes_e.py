# -*- coding: utf-8 -*-
"""Vidéos 9 et 10."""
import functools
import math

from ui import *  # noqa: F401,F403
from components import THEMES, endcard
from engine import _with_glow

SCENES = []

# ====================================================================== 09
# « POV : un client te demande ton site » : mini-scénario en conversation de chat
MSGS = [("L", "Bonsoir ! Vous avez un site web pour voir vos produits ?", 1.5),
        ("R", "Euh… non. Je mets tout dans mon statut WhatsApp 😅", 3.4),
        ("L", "Ah ok… Tu peux m'envoyer le catalogue avec les prix ?", 5.3),
        ("R", "Attends, je cherche les photos…", 7.2),
        ("S", "⏳  10 minutes plus tard…", 8.6),
        ("L", "Pas de souci, je vais voir chez un autre vendeur 👋", 9.9),
        ("X", "🚪  Le client a quitté la discussion", 11.1)]
WW, WH = 940, 1040
BE9 = 16.2


@functools.lru_cache(maxsize=64)
def msg_sprite(kind, txt):
    if kind == "L":
        return bubble(txt, "left", size=36, max_w=600, fill="#ffffff")
    if kind == "R":
        return bubble(txt, "right", size=36, max_w=600, fill="#d9fdd3")
    if kind == "S":
        return chip(txt, "#5b4a14", "#fdf0b5", size=30, fk="semi", px=26, py=14)
    return chip(txt, "#7f1d1d", "#fee2e2", size=30, fk="semi", px=26, py=14)


@functools.lru_cache(maxsize=1)
def win_mask():
    return rrect(WW, WH, 46, fill="#ffffff").getchannel("A")


@functools.lru_cache(maxsize=1)
def win_shadow():
    return rrect(WW, WH, 46, fill="#000000", shadow=(0, 22, 36, "#000000", 0.45))


def chat_win(t):
    img = Image.new("RGB", (WW, WH), "#e9e1d6")
    top, bot = 140, WH - 104
    cum, items = 0.0, []
    typing = None
    for kind, txt, ti in MSGS:
        if kind == "L" and ti - 1.0 <= t < ti:
            typing = ti
        p = e_out(prog(t, ti, 0.3))
        if p <= 0:
            continue
        s = msg_sprite(kind, txt)
        items.append((kind, s, p, cum))
        cum += (s.height + (10 if kind in "LR" else 22)) * p - (8 if kind in "LR" else 0) * p
    if typing:
        tp = typing_dots(t)
        items.append(("T", tp, 1.0, cum))
        cum += tp.height
    off = max(0.0, cum - (bot - top - 24))
    for kind, s, p, c in items:
        y = top + 12 + c - off + (1 - p) * 16
        if kind == "L" or kind == "T":
            x = 14
        elif kind == "R":
            x = WW - 14 - s.width
        else:
            x = (WW - s.width) // 2
        put(img, s, x, y, p)
    left = t >= 11.1
    img.paste(Image.new("RGB", (WW, 128), "#0f766e"), (0, 0))
    place(img, circle(76, fill="#94a3b8" if left else "#cbd5e1"), 70, 70)
    place(img, text("🙋", "bold", 44), 70, 72, alpha=0.5 if left else 1.0)
    put(img, text("Nouveau client", "bold", 38, "#ffffff"), 126, 26)
    status_ = "hors ligne" if left else ("en train d'écrire…" if typing else "en ligne")
    put(img, text(status_, "reg", 26, "#a7f3d0"), 128, 74)
    img.paste(Image.new("RGB", (WW, 104), "#f0f2f5"), (0, WH - 104))
    place(img, rrect(WW - 150, 64, 32, fill="#ffffff"), (WW - 110) / 2 + 10, WH - 52)
    put(img, text("Écris un message", "reg", 28, "#9ca3af"), 52, WH - 70)
    place(img, circle(70, fill="#16a34a"), WW - 62, WH - 52)
    place(img, text("➤", "bold", 30, "#ffffff"), WW - 60, WH - 54)
    return img


def v09(t):
    img = blobs_bg(t, "#0a2f2b", [("#14b8a6", .15, .15, .5, .06, .04, .5, 0, .35), ("#22c55e", .9, .85, .55, .05, .05, .4, 2, .28),
                                  ("#0ea5e9", .85, .1, .4, .05, .05, .6, 4, .2)])
    vis = 1 - prog(t, BE9 - 0.5, 0.4)
    ex = e_in(prog(t, 11.8, 0.6))
    a = e_out(prog(t, 0.1, 0.5))
    if t < 11.5:
        place(img, text("POV : un client te demande\nton **site web** 😅", "black", 54, "#ffffff", hl="#fde047", ls=1.1, shadow=(0, 4, 10, "#000000", 0.35)),
              540, 262 - (1 - a) * 30, alpha=a * (1 - prog(t, 11.3, 0.3)))
    if t < 12.5:
        pw_ = e_back(prog(t, 0.3, 0.6))
        win = chat_win(t).convert("RGBA")
        win.putalpha(win_mask())
        cy = 880 + ex * 900
        sc = lerp(0.9, 1.0, pw_)
        place(img, win_shadow(), 540, cy, s=sc, alpha=min(1, pw_ * 2))
        place(img, win, 540, cy, s=sc, alpha=min(1, pw_ * 2))
    if 12.5 <= t < 13.8:
        slam(img, text("Ça t'est déjà\n**arrivé** ? 😬", "black", 104, "#ffffff", hl="#fde047", ls=1.08, shadow=(0, 6, 14, "#000000", 0.4)), 540, 760, t, 12.5,
             alpha=1 - prog(t, 13.5, 0.3))
    if 13.8 <= t < BE9:
        lt = t - 13.8
        k = vis
        place(img, text("Avec un site pro,\ntout est **dans un seul lien** 🔗", "black", 64, "#ffffff", hl="#fde047", ls=1.12, max_w=940,
                        shadow=(0, 4, 10, "#000000", 0.35)), 540, 470, s=lerp(0.9, 1, e_out(prog(lt, 0, 0.4))), alpha=prog(lt, 0, 0.3) * k)
        for i, lab in enumerate(["📖  Ton catalogue", "💰  Tes prix", "🛒  La commande en ligne"]):
            p = pop(lt, 0.5 + i * 0.4, 0.45)
            place(img, chip(lab, "#ffffff", "#16a34a", size=54, px=46, py=22), 540, 760 + i * 150, s=p, alpha=k)
        place(img, text("Ton client n'attend plus ✅", "black", 56, "#ffffff", shadow=(0, 4, 10, "#000000", 0.35)), 540, 1230,
              alpha=prog(lt, 1.8, 0.4) * k)
    if t >= BE9:
        endcard(img, t - BE9, THEMES["wa"], headline="Évite de perdre\ndes **clients**", sub="Devis gratuit • Écris-nous")
    return img


_s9 = []
for _k, _tx, _ti in MSGS:
    if _k == "L":
        _s9 += [(_ti - 0.95, "tick", 0.3), (_ti, "msg_in", 0.8)]
    elif _k == "R":
        _s9 += [(_ti, "msg_out", 0.8)]
    elif _k == "S":
        _s9 += [(_ti, "pop", 0.8)]
    else:
        _s9 += [(_ti, "buzz", 0.6)]
SFX09 = _s9 + [(0.3, "whoosh", 0.4), (11.8, "whoosh", 0.8), (12.5, "slam", 0.9), (12.55, "impact", 0.5), (13.8, "whoosh", 0.5),
               (14.3, "pop"), (14.7, "pop"), (15.1, "pop"), (15.6, "success", 0.6), (16.15, "impact", 0.7), (16.2, "whoosh"), (16.6, "pop"), (17.2, "ding", 0.8)]
VOICE09 = [dict(text="Un client te demande si tu as un site web.", at=0.3, end=3.3),
           dict(text="Toi, tu mets tout dans ton statut WhatsApp,", at=3.5, end=6.3),
           dict(text="il veut le catalogue, tu cherches les photos,", at=6.5, end=9.5),
           dict(text="résultat : il va voir ailleurs.", at=9.9, end=11.9),
           dict(text="Ça t'est déjà arrivé ?", at=12.55, end=13.8),
           dict(text="Avec un site pro, tout est dans un seul lien.", at=13.9, end=16.5),
           dict(text="Évite de perdre des clients : devis gratuit, écris-nous !", at=16.9, end=20.7)]
SCENES.append(dict(id=9, slug="pov-un-client-te-demande-ton-site", dur=21.2, end=16.2, frame=v09, sfx=SFX09, voice=VOICE09, music_vol=0.55,
                   music=dict(style="lofi", bpm=96, root=55, prog="major", lv=[(0, 1), (1.2, 2)], seed=17),
                   caption="POV : un client te demande ton site web 😅 Ne perds plus de ventes ! Un seul lien avec ton catalogue, tes prix et la commande. Devis gratuit 👇"))


# ====================================================================== 10
# « Tout ce qu'on peut créer pour toi » : grille de services (couleurs orange / blanc / vert)
OR, GR = "#f77f00", "#009e60"
TILES = [("🌐", "Site\nvitrine", OR, "#111111"), ("🛒", "Boutique\nen ligne", "#ffffff", "#111111"),
         ("📱", "Application\nmobile", GR, "#ffffff"), ("📊", "Logiciel de\ngestion", OR, "#111111"),
         ("🤖", "Chatbot &\nautomatisation", "#ffffff", "#111111"), ("🛠️", "Maintenance &\nhébergement", GR, "#ffffff")]
TW, TH = 470, 270
POS = [(290, 640), (790, 640), (290, 930), (790, 930), (290, 1220), (790, 1220)]
BE10 = 11.6


@functools.lru_cache(maxsize=8)
def tile(i):
    emo, lab, bg, fg = TILES[i]
    spr = rrect(TW, TH, 42, fill=bg, shadow=(0, 12, 22, "#000000", 0.4)).copy()
    pad = (spr.width - TW) // 2
    spr.alpha_composite(text(emo, "bold", 104), (pad + 32, pad + 22))
    spr.alpha_composite(text(lab, "black", 42, fg, align="left", ls=1.08), (pad + 36, pad + TH - 36 - text(lab, "black", 42, fg, align="left", ls=1.08).height + 10))
    n = text(f"0{i + 1}", "black", 40, fg)
    spr.alpha_composite(n, (pad + TW - 30 - n.width, pad + 24))
    return spr


def v10(t):
    img = blobs_bg(t, "#0e1013", [("#f77f00", .1, .12, .5, .06, .04, .5, 0, .32), ("#009e60", .9, .9, .55, .06, .05, .4, 2, .3)])
    vis = 1 - prog(t, BE10 - 0.5, 0.4)
    if vis > 0.01:
        a = e_out(prog(t, 0.1, 0.5))
        if t < 7.7:
            place(img, text("Tout ce qu'on peut\n**créer** pour toi", "black", 78, "#ffffff", hl=OR, ls=1.08), 540, 300 - (1 - a) * 30, alpha=a * (1 - prog(t, 7.4, 0.3)))
            bw = int(380 * e_out(prog(t, 0.5, 0.6)))
            if bw > 6:
                for k, c in enumerate((OR, "#ffffff", GR)):
                    put(img, rrect(max(2, bw // 3), 14, 4, fill=c), 540 - bw // 2 + k * (bw // 3), 418, 1 - prog(t, 7.4, 0.3))
            active = int((t - 4.4) / 0.42) % 6 if 4.4 <= t < 7.4 else -1
            for i in range(6):
                ts = 1.0 + i * 0.4
                p = prog(t, ts, 0.45)
                if p <= 0:
                    continue
                sx = e_out(p)
                s_ = 1.07 if i == active else 1.0
                ex = e_in(prog(t, 7.4 + i * 0.05, 0.35))
                cx, cy = POS[i]
                place_xy(img, tile(i), cx, cy + ex * 120, sx * s_, s_, alpha=min(1, p * 2) * (1 - ex))
                if i == active:
                    place(img, rrect(TW + 14, TH + 14, 46, outline="#ffffff", ow=7), cx, cy, s=1.07, alpha=0.95)
            if t > 5.0:
                place(img, text("…et bien plus encore ✨", "bold", 52, "#ffffff"), 540, 1400, alpha=prog(t, 5.0, 0.4) * (1 - prog(t, 7.4, 0.3)))
        if t >= 7.8:
            lt = t - 7.8
            slam(img, fit("UNE IDÉE ?", "black", 134, 940, fill="#ffffff"), 540, 640, lt, 0.0, alpha=vis)
            slam(img, fit("On la transforme en", "bold", 70, 940, fill="#ffffff"), 540, 790, lt, 0.45, alpha=vis)
            slam(img, fit("RÉALITÉ 🚀", "black", 150, 940, fill=OR, glow=(OR, 14, 0.5)), 540, 960, lt, 0.9, alpha=vis)
            bw = int(560 * e_out(prog(lt, 1.3, 0.5)))
            if bw > 6:
                for k, c in enumerate((OR, "#ffffff", GR)):
                    put(img, rrect(max(2, bw // 3), 16, 5, fill=c), 540 - bw // 2 + k * (bw // 3), 1090, vis)
    if t >= BE10:
        endcard(img, t - BE10, THEMES["ci"], headline="Parlons de\nton **projet** !", sub="Devis gratuit • Réponse rapide")
    return img


SFX10 = ([(0.2, "pop"), (0.5, "whoosh", 0.4)] + [(1.0 + i * 0.4, "pop", 0.8) for i in range(6)]
         + [(4.4 + i * 0.42, "tick", 0.5) for i in range(7)] + [(5.0, "pop", 0.6), (7.0, "riser", 0.7), (7.4, "whoosh", 0.7), (7.8, "slam"),
            (8.25, "slam"), (8.7, "slam"), (8.75, "impact", 0.6), (9.2, "sparkle", 0.7), (11.55, "impact", 0.7), (11.6, "whoosh"), (12.0, "pop"), (12.6, "ding", 0.8)])
VOICE10 = [dict(text="Tout ce qu'on peut créer pour toi !", at=0.3, end=2.5),
           dict(text="Un site vitrine, une boutique en ligne, une application mobile, et bien plus encore !", at=2.6, end=7.2),
           dict(text="Une idée ? On la transforme en réalité !", at=7.8, end=10.9),
           dict(text="Parlons de ton projet : devis gratuit !", at=11.9, end=15.0)]
SCENES.append(dict(id=10, slug="tout-ce-qu-on-peut-creer-pour-toi", dur=16.6, end=11.6, frame=v10, sfx=SFX10, voice=VOICE10,
                   music=dict(style="afro", bpm=108, root=50, prog="minor2", lv=[(0, 2), (1.0, 3)], seed=23),
                   caption="Site vitrine, boutique en ligne, application mobile, logiciel de gestion, chatbot, maintenance… On crée tout pour toi 🇨🇮 Une idée ? Écris-nous !"))
