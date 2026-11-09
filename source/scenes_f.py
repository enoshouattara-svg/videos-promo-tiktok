# -*- coding: utf-8 -*-
"""Vidéos 11 et 12."""
import functools
import math

import config
from ui import *  # noqa: F401,F403
from brand import lockup
from components import THEMES, endcard, glow_shape, brackets, tag_line, put_headline
from engine import _with_glow

SCENES = []

# ====================================================================== 11
# « Scanne-moi » : QR code, détection, message WhatsApp déjà écrit, puis 2 QR (WhatsApp / appel)
CY, GC = "#00e5ff", "#2dff9a"
CARD = 640


@functools.lru_cache(maxsize=2)
def qr_full(url, target):
    return qr_sprite(url, target, fg="#04101c", bg="#ffffff", quiet=2)


@functools.lru_cache(maxsize=2)
def laser_line(w):
    return _with_glow(rrect(w, 8, 4, fill=CY), CY, 10, 1.2)


@functools.lru_cache(maxsize=2)
def screen_laser():
    return _with_glow(rrect(W, 6, 3, fill=CY), CY, 16, 1.0)


@functools.lru_cache(maxsize=1)
def composer_base():
    w, h = 900, 440
    spr = rrect(w, h, 40, fill="#ece5dd", shadow=(0, 18, 30, "#000000", 0.5)).copy()
    pad = (spr.width - w) // 2
    spr.alpha_composite(rrect(w, 104, 40, fill="#128c7e"), (pad, pad))
    spr.alpha_composite(Image.new("RGBA", (w, 52), col("#128c7e") + (255,)), (pad, pad + 52))
    spr.alpha_composite(text("💬  WhatsApp", "bold", 42, "#ffffff"), (pad + 32, pad + 26))
    spr.alpha_composite(text("Nouvelle discussion", "reg", 26, "#b7f0d9"), (pad + w - 32 - text("Nouvelle discussion", "reg", 26, "#b7f0d9").width, pad + 36))
    spr.alpha_composite(rrect(w - 170, 78, 39, fill="#ffffff"), (pad + 24, pad + h - 104))
    spr.alpha_composite(circle(78, fill="#16a34a"), (pad + w - 24 - 78, pad + h - 104))
    spr.alpha_composite(text("➤", "bold", 34, "#ffffff"), (pad + w - 24 - 78 + 22, pad + h - 104 + 16))
    return spr, pad


def composer(t):
    base, pad = composer_base()
    spr = base.copy()
    msg = "Bonjour, je veux un devis"
    sent = t >= 6.55
    q = typed(msg, prog(t, 5.0, 1.1))
    if not sent:
        spr.alpha_composite(text(q + ("|" if int(t * 3) % 2 == 0 else ""), "reg", 36, "#111b21", align="left"), (pad + 52, pad + 440 - 104 + 18))
    else:
        p = e_back(prog(t, 6.55, 0.4))
        b = bubble(msg, "right", size=40, max_w=620, fill="#d9fdd3")
        spr.alpha_composite(b.resize((int(b.width * p), int(b.height * p))) if p < 1 else b, (pad + 900 - 30 - b.width, pad + 140))
        spr.alpha_composite(text("✓✓", "bold", 30, "#34b7f1"), (pad + 900 - 50 - b.width // 2, pad + 140 + b.height - 6))
    return spr


def endcard_dual(img, t, th):
    acc, acc2, fg, soft = th["accent"], th["accent2"], th["fg"], th["soft"]
    if not lockup(img, t, th):
        place(img, text(tag_line(), "semi", 32, soft), W // 2, 212, alpha=prog(t, 0.0, 0.4))
    put_headline(img, t, th, "Scanne **ou appelle**", "Devis gratuit • Réponse rapide", room=(286, 520), size=90)
    for cx, lab, cap, url, c, t0 in [(290, "💬 WhatsApp", "Message déjà écrit", config.WHATSAPP_URL, "#25d366", 0.45),
                                      (790, "📞 Appel direct", "Un clic pour appeler", config.TEL_URL, "#38bdf8", 0.75)]:
        pc = prog(t, t0, 0.65)
        if pc <= 0:
            continue
        sc = lerp(0.55, 1.0, e_back(pc)) * (1 + 0.012 * math.sin(t * 3.1 + cx))
        place(img, glow_shape(480, 600, 44, c, 34, 0.7), cx, 830, s=sc, alpha=min(1, pc * 1.6) * 0.7)
        card = rrect(480, 600, 44, fill="#ffffff", shadow=(0, 14, 26, "#000000", 0.35)).copy()
        pad = (card.width - 480) // 2
        rib = Image.new("RGBA", (480, 92), col(c)[:3] + (255,))
        rib.putalpha(card.getchannel("A").crop((pad, pad, pad + 480, pad + 92)))
        card.alpha_composite(rib, (pad, pad))
        lb = text(lab, "black", 42, "#ffffff")
        card.alpha_composite(lb, (pad + (480 - lb.width) // 2, pad + (92 - lb.height) // 2 - 2))
        q = qr_full(url, 372)
        card.alpha_composite(q, (pad + (480 - q.width) // 2, pad + 112))
        cp = text(cap, "semi", 30, "#4b5563")
        card.alpha_composite(cp, (pad + (480 - cp.width) // 2, pad + 600 - 70))
        place(img, card, cx, 830, s=sc, alpha=min(1, pc * 2))
    p = e_out(prog(t, 1.1, 0.55))
    if p > 0:
        ts = text("📞 " + config.PHONE_DISPLAY, "black", 62, th["pill_fg"])
        pw, ph = ts.width + 80, 124
        y = 1262 + (1 - p) * 70
        sc2 = 1 + 0.018 * math.sin(t * 5.2 + 1.0)
        rp = ((t - 1.3) / 1.3) % 1.0 if t > 1.3 else 1.0
        place(img, rrect(pw, ph, ph // 2, outline=th["pill"], ow=5), W // 2, y, s=1 + rp * 0.22, alpha=(1 - rp) * 0.7 * p)
        place(img, rrect(pw, ph, ph // 2, fill=th["pill"], shadow=(0, 10, 22, "#000000", 0.28)), W // 2, y, s=sc2, alpha=p)
        place(img, ts, W // 2, y - 3, s=sc2, alpha=p)
    p = e_out(prog(t, 1.5, 0.5))
    place(img, text("💬 WhatsApp   •   📞 Appel", "semi", 36, soft), W // 2, 1382 + (1 - p) * 20, alpha=p)
    confetti(img, t, 0.6, n=70, seed=5, origin=(W // 2, 830), colors=th["conf"], life=2.6)


def v11(t):
    img = blobs_bg(t, "#04060c", [("#00e5ff", .85, .12, .5, .06, .04, .6, 0, .30), ("#ff2d95", .1, .9, .55, .06, .05, .5, 2, .22),
                                  ("#2dff9a", .5, .5, .4, .1, .05, .4, 4, .08)])
    draw_grid(img, t, speed=40, color="#00e5ff", alpha=24)
    put(img, screen_laser(), 0, (t % 3.2) / 3.2 * (H + 200) - 100, 0.3)
    BD = 8.2
    cx, cy = 540, 860
    if t < BD:
        ex = e_in(prog(t, 7.6, 0.55))
        a = e_out(prog(t, 4.6, 0.5))
        shrink = e_io(prog(t, 4.5, 0.6))
        # titres
        if t < 4.5:
            slam(img, fit("SCANNE 📲", "black", 160, 940, fill="#ffffff", glow=(CY, 16, 0.7)), 540, 300, t, 0.1, alpha=1 - prog(t, 4.2, 0.3))
            place(img, text("pour discuter de ton projet", "semi", 46, "#9bb4c9"), 540, 430, alpha=prog(t, 0.7, 0.4) * (1 - prog(t, 4.2, 0.3)))
        else:
            place(img, text("Ça ouvre **WhatsApp** direct 💬", "black", 62, "#ffffff", hl=GC, max_w=940, ls=1.1), 540, 290, alpha=a * (1 - ex))
        # carte QR
        pc = pop(t, 0.5, 0.55)
        sc = lerp(1.0, 0.5, shrink) * lerp(0.6, 1.0, pc)
        qy = lerp(cy, 620, shrink) - ex * 1100
        reveal = prog(t, 0.9, 1.4)
        if pc > 0:
            place(img, glow_shape(CARD, CARD, 46, CY, 46, 0.7), cx, qy, s=sc, alpha=min(1, pc * 1.5) * 0.6)
            place(img, rrect(CARD, CARD, 46, fill="#ffffff", shadow=(0, 14, 28, "#000000", 0.45)), cx, qy, s=sc, alpha=min(1, pc * 2))
            q = qr_full(config.WHATSAPP_URL, 540) if reveal >= 1 else qr_sprite(config.WHATSAPP_URL, 540, fg="#04101c", bg="#ffffff", quiet=2, reveal=reveal)
            place(img, q, cx, qy, s=sc, alpha=min(1, pc * 2))
            if 2.2 <= t < 4.1:
                ph = ((t - 2.2) / 0.9) % 1.0
                place(img, laser_line(540), cx, qy - 270 * sc + ph * 540 * sc, s=sc, alpha=0.95)
        # viseur + détection
        det = t >= 4.0
        if 2.2 <= t < 5.4:
            k = e_out(prog(t, 2.2, 0.7))
            colr = GC if det else CY
            brackets(img, cx, int(qy), int(CARD / 2 * sc), int(CARD / 2 * sc), colr, length=96, thick=13,
                     margin=int(30 + (1 - k) * 90 + (6 * math.sin(t * 8) if not det else 0)), alpha=min(1, k * 2) * (1 - prog(t, 5.0, 0.4)))
        if det:
            ripple(img, cx, qy, prog(t, 4.0, 0.7), GC, d=640, ow=14)
        if 2.4 <= t < 4.6:
            if not det:
                place(img, text("Scan en cours" + "." * (int(t * 3) % 4), "bold", 50, CY), 540, 1250)
                w_ = int(560 * prog(t, 2.4, 1.6))
                place(img, rrect(560, 16, 8, fill=(255, 255, 255, 50)), 540, 1320)
                if w_ > 8:
                    put(img, rrect(w_, 16, 8, fill=CY), 540 - 280, 1312)
            else:
                place(img, text("✅ Détecté !", "black", 64, GC, glow=(GC, 12, 0.6)), 540, 1260, s=pop(t, 4.0, 0.4), alpha=1 - prog(t, 4.3, 0.3))
        # composeur de message
        if t >= 4.8:
            pcm = e_out(prog(t, 4.8, 0.5))
            place(img, composer(t), 540, 1070 + (1 - pcm) * 520 + ex * 800, alpha=min(1, pcm * 2))
            if t > 6.6:
                place(img, text("Le message est déjà prêt 😉", "bold", 48, "#ffffff"), 540, 1370, alpha=prog(t, 6.9, 0.4) * (1 - ex))
        if det and t < 5.2:
            img = flash(img, t, 4.0, 0.25, GC, 0.18)
    else:
        endcard_dual(img, t - BD, THEMES["cyber"])
    return img


_s11 = [(0.1, "slam"), (0.5, "pop")] + [(0.9 + i * 0.12, "tick", 0.3) for i in range(11)] + [(2.2, "scan", 0.8)]
SFX11 = _s11 + [(2.9, "scan", 0.6), (4.0, "success", 0.8), (4.8, "whoosh", 0.6), (5.0, "pop")] + [(5.1 + i * 0.07, "type", 0.4) for i in range(15)] \
    + [(6.55, "msg_out", 0.9), (6.9, "pop", 0.7), (7.55, "whoosh", 0.9), (8.15, "impact", 0.7), (8.2, "whoosh"), (8.65, "pop"), (9.0, "pop"), (9.4, "ding", 0.8)]
VOICE11 = [dict(text="Scanne ce QR code avec ton téléphone.", at=0.25, end=2.65),
           dict(text="Ton appareil photo le détecte,", at=2.75, end=4.6),
           dict(text="et WhatsApp s'ouvre avec un message déjà écrit !", at=4.7, end=7.9),
           dict(text="Tu peux aussi nous appeler directement.", at=8.4, end=11.0),
           dict(text="Devis gratuit : scanne ou appelle !", at=11.3, end=14.2)]
SCENES.append(dict(id=11, slug="scanne-moi-qr-code", dur=15.0, end=8.2, frame=v11, sfx=SFX11, voice=VOICE11,
                   music=dict(style="chip", bpm=118, root=57, prog="minor", lv=[(0, 2), (4.0, 3)], seed=31),
                   caption="Scanne ce QR code 📲 Ça ouvre WhatsApp avec un message déjà écrit pour demander ton devis. Tu peux aussi nous appeler directement !"))


# ====================================================================== 12
# « Vrai ou Faux ? » : 4 idées reçues sur le site web
BLU, YEL = "#1d4ed8", "#ffd60a"
STM = [("Un site web, c'est seulement pour les grandes entreprises.", "FAUX ❌", "#ff3b30", "Les petits commerces en profitent aussi 💪", 1.9),
       ("C'est trop compliqué, je ne saurais pas m'en occuper.", "FAUX ❌", "#ff3b30", "On s'occupe de tout, de A à Z 🛠️", 5.1),
       ("WhatsApp et Instagram suffisent pour vendre.", "PAS ASSEZ ⚠️", "#ff9f0a", "Utiles, mais ton site, c'est TA vitrine à toi 🏪", 8.3),
       ("On peut discuter du prix avant de se décider.", "VRAI ✅", "#22c55e", "Devis gratuit : écris-nous 💬", 11.5)]
SLEN = 3.2
BE12 = 14.7


@functools.lru_cache(maxsize=96)
def ring(d, w, color, p):
    ss = 4
    S = d * ss
    m = Image.new("L", (S, S), 0)
    dr = ImageDraw.Draw(m)
    if p >= 0.999:
        dr.ellipse((w * ss // 2, w * ss // 2, S - w * ss // 2, S - w * ss // 2), outline=255, width=w * ss)
    elif p > 0:
        dr.arc((w * ss // 2, w * ss // 2, S - w * ss // 2, S - w * ss // 2), start=-90, end=-90 + 360 * p, fill=255, width=w * ss)
    m = m.resize((d, d), BOX)
    spr = Image.new("RGBA", (d, d), col(color)[:3] + (0,))
    spr.putalpha(m)
    return spr


@functools.lru_cache(maxsize=8)
def st_card(txt):
    spr = rrect(940, 420, 52, fill="#ffffff", shadow=(0, 16, 28, "#06123a", 0.45)).copy()
    pad = (spr.width - 940) // 2
    t_ = text(txt, "black", 60, "#0f172a", max_w=820, ls=1.12)
    spr.alpha_composite(t_, (pad + (940 - t_.width) // 2, pad + (420 - t_.height) // 2))
    return spr


def v12(t):
    img = new_frame(["#2557e8", "#14287f"], 90)
    put(img, dots_layer12(), -64 + (t * 20) % 64, -64 + (t * 20) % 64)
    vis = 1 - prog(t, BE12 - 0.5, 0.4)
    if vis > 0.01:
        # titre d'intro
        if t < 2.2:
            k = 1 - prog(t, 1.85, 0.3)
            slam(img, fit("VRAI", "black", 190, 940, fill="#ffffff"), 540, 600, t, 0.1, alpha=k)
            slam(img, fit("ou", "bold", 80, 940, fill=YEL), 540, 750, t, 0.5, alpha=k)
            slam(img, fit("FAUX ?", "black", 190, 940, fill=YEL, glow=(YEL, 14, 0.5)), 540, 910, t, 0.8, alpha=k)
        # progression
        if t >= 1.9:
            for i in range(4):
                done = t >= STM[i][4] + 2.0
                cur = STM[i][4] <= t < STM[i][4] + SLEN + 0.2
                place(img, circle(26 if cur else 20, fill=YEL if (done or cur) else (255, 255, 255, 90)), 540 - 90 + i * 60, 214, alpha=vis)
        for i, (st, stamp_txt, sc_, expl, t0) in enumerate(STM):
            lt = t - t0
            if lt < 0 or lt > SLEN + 0.15:
                continue
            pin = e_out(prog(lt, 0.0, 0.4))
            pout = e_in(prog(lt, SLEN - 0.25, 0.3))
            dx = (1 - pin) * 1100 - pout * 1200
            place(img, chip(f"AFFIRMATION {i + 1}/4", "#0f172a", YEL, size=36, fk="black", px=32, py=15), 540 + dx, 330)
            place(img, st_card(st), 540 + dx, 700)
            # compte à rebours
            if lt < 1.75:
                n = 3 - int(prog(lt, 0.45, 1.2) * 3 - 1e-6) if lt >= 0.45 else 3
                p = prog(lt, 0.45, 1.2)
                place(img, ring(200, 17, "#ffffff", 1 - p), 540 + dx, 1130, alpha=0.95)
                place(img, ring(200, 17, "#ffffff", 1.0), 540 + dx, 1130, alpha=0.18)
                place(img, text(str(max(1, min(3, n))), "black", 106, "#ffffff"), 540 + dx, 1132, s=1 + 0.12 * max(0, 1 - ((p * 3) % 1) * 4))
            # tampon : la carte s'estompe pour que le tampon reste lisible
            if lt >= 1.75:
                ps = prog(lt, 1.75, 0.2)
                place(img, rrect(940, 420, 52, fill=(255, 255, 255, 215)), 540 + dx, 700, alpha=min(1, ps * 3))
                s_ = lerp(2.8, 1.0, e_out(ps, 4))
                k = 1 - prog(lt, 1.95, 0.3)
                dx2, dy2 = shake(lt, 12 * k) if k > 0 else (0, 0)
                place(img, stamp(stamp_txt, sc_, size=132, ow=15, padx=48, pady=20), 540 + dx + dx2, 700 + dy2, s=s_, rot=-8, alpha=min(1, ps * 3))
                pe = prog(lt, 2.1, 0.35)
                place(img, text(expl, "black", 60, "#ffffff", max_w=900, ls=1.1, shadow=(0, 4, 10, "#06123a", 0.5)), 540 + dx, 1130 + (1 - pe) * 30, alpha=pe)
    if t >= BE12:
        endcard(img, t - BE12, THEMES["quiz"], headline="Dernière question :\non **en parle** ?", sub="Devis gratuit • Écris-nous")
    return img


@functools.lru_cache(maxsize=1)
def dots_layer12():
    step, ss, r = 64, 2, 8
    big = Image.new("L", ((W + 2 * step) * ss, (H + 2 * step) * ss), 0)
    d = ImageDraw.Draw(big)
    for yy in range(0, H + 2 * step, step):
        for xx in range(0, W + 2 * step, step):
            ox = step // 2 if (yy // step) % 2 else 0
            cx, cy = (xx + ox) * ss, yy * ss
            d.ellipse((cx - r * ss, cy - r * ss, cx + r * ss, cy + r * ss), fill=255)
    m = big.resize((W + 2 * step, H + 2 * step), BOX).point([int(v * 0.14) for v in range(256)])
    im = Image.new("RGBA", m.size, (255, 255, 255, 0))
    im.putalpha(m)
    return im


_s12 = [(0.1, "slam"), (0.5, "pop"), (0.8, "slam"), (0.85, "impact", 0.6)]
for _i, (_s, _st, _c, _e, _t0) in enumerate(STM):
    _s12 += [(_t0, "swipe", 0.6), (_t0 + 0.5, "tick", 0.7), (_t0 + 0.95, "tick", 0.7), (_t0 + 1.4, "tick", 0.7), (_t0 + 1.75, "stamp", 0.9),
             (_t0 + 1.75, "success" if "VRAI" in _st else "buzz", 0.6), (_t0 + 2.1, "pop", 0.7)]
SFX12 = _s12 + [(14.65, "impact", 0.7), (14.7, "whoosh"), (15.1, "pop"), (15.7, "ding", 0.8)]
# Variante « voix off » : chaque carte dure 4,4 s au lieu de 3,2 s (la voix a besoin de temps) ;
# les animations et les bruitages sont étirés en proportion (voir warp12 / unwarp12).
SLEN_V, N_ST = 4.4, 4


def warp12(t):
    """Temps de la variante voix off -> temps de la vidéo d'origine."""
    if t < 1.9:
        return t
    if t < 1.9 + N_ST * SLEN_V:
        i = int((t - 1.9) // SLEN_V)
        return 1.9 + i * SLEN + (t - 1.9 - i * SLEN_V) * SLEN / SLEN_V
    return t - N_ST * (SLEN_V - SLEN)


def unwarp12(t):
    """Temps de la vidéo d'origine -> temps de la variante voix off."""
    if t < 1.9:
        return t
    if t < 1.9 + N_ST * SLEN:
        i = int((t - 1.9) // SLEN)
        return 1.9 + i * SLEN_V + (t - 1.9 - i * SLEN) * SLEN_V / SLEN
    return t + N_ST * (SLEN_V - SLEN)


def v12v(t):
    return v12(warp12(t))


SFX12V = [(unwarp12(ev[0]),) + tuple(ev[1:]) for ev in SFX12]
# cartes à 1,9 / 6,3 / 10,7 / 15,1 s ; le tampon tombe 2,41 s après le début de chaque carte
VOICE12 = [dict(text="Vrai ou faux ?", at=0.2, end=1.8),
           dict(text="Réservé aux grandes entreprises ?", at=2.2, end=4.25),
           dict(text="Faux ! Pour tous les commerces.", at=4.35, end=6.45),
           dict(text="C'est trop compliqué ?", at=6.6, end=8.65),
           dict(text="Faux ! On s'occupe de tout.", at=8.75, end=10.85),
           dict(text="WhatsApp et Instagram suffisent ?", at=11.0, end=13.05),
           dict(text="Pas assez ! Ton propre site.", at=13.15, end=15.25),
           dict(text="On peut discuter du prix ?", at=15.4, end=17.45),
           dict(text="Vrai ! Devis gratuit.", at=17.55, end=19.65),
           dict(text="Dernière question : on en parle ? Devis gratuit, écris-nous !", at=20.0, end=24.3)]
SCENES.append(dict(id=12, slug="vrai-ou-faux-site-web", dur=19.7, end=14.7, frame=v12, sfx=SFX12, voice=VOICE12,
                   voice_variant=dict(dur=24.5, end=19.5, frame=v12v, sfx=SFX12V),
                   music=dict(style="funk", bpm=108, root=50, prog="minor", lv=[(0, 2), (1.9, 3)], seed=41),
                   caption="Vrai ou faux ? 🤔 4 idées reçues sur les sites web… et la dernière est VRAIE : on peut discuter du prix avant ! Devis gratuit 👇"))
