# -*- coding: utf-8 -*-
"""Moteur de rendu vidéo : texte (avec emojis couleur), formes lissées, dégradés,
QR codes, animations et export MP4 via ffmpeg.  Pillow + numpy uniquement."""
import functools
import math
import os
import random
import re
import subprocess

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
_R = Image.Resampling
BOX, BICUBIC, LANCZOS, NEAREST, BILINEAR = _R.BOX, _R.BICUBIC, _R.LANCZOS, _R.NEAREST, _R.BILINEAR


# ----------------------------------------------------------------- couleurs
def col(c, a=None):
    if isinstance(c, str):
        s = c.lstrip("#")
        if len(s) in (3, 4):
            s = "".join(ch * 2 for ch in s)
        v = tuple(int(s[i:i + 2], 16) for i in range(0, len(s), 2))
    else:
        v = tuple(int(x) for x in c)
    if a is not None:
        v = v[:3] + (int(a),)
    return v


def mix(c1, c2, t):
    a, b = col(c1), col(c2)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ---------------------------------------------------------------- animation
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, t0, d):
    if d <= 0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / d)


def e_out(p, n=3):
    return 1 - (1 - p) ** n


def e_in(p, n=3):
    return p ** n


def e_io(p):
    return p * p * (3 - 2 * p)


def e_back(p, s=1.70158):
    p -= 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def e_spring(p):
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0
    return 1 - math.exp(-6.5 * p) * math.cos(12 * p)


def pop(t, t0, d=0.45):
    """0 -> 1 avec petit dépassement (effet « pop »)."""
    return e_back(prog(t, t0, d))


def shake(t, amp=8.0, f=37.0):
    return amp * math.sin(t * f), amp * math.cos(t * f * 1.37)


# ------------------------------------------------------------------ polices
_FD = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
_FILES = dict(black="seguibl.ttf", bold="segoeuib.ttf", semi="seguisb.ttf", reg="segoeui.ttf",
              light="segoeuil.ttf", impact="impact.ttf", mono="consola.ttf", monob="consolab.ttf",
              hand="Inkfree.ttf", print="segoepr.ttf", printb="segoeprb.ttf", emoji="seguiemj.ttf",
              bahn="bahnschrift.ttf")


@functools.lru_cache(maxsize=512)
def font(key, size):
    f = ImageFont.truetype(os.path.join(_FD, _FILES[key]), int(size))
    if key == "bahn":
        f.set_variation_by_name("Bold")
    return f


_TOK = re.compile(r"\n| +|[^ \n]+")


def _is_emoji(ch):
    o = ord(ch)
    return (0x1F000 <= o <= 0x1FAFF or 0x2600 <= o <= 0x27BF or 0x2B00 <= o <= 0x2BFF
            or 0x2300 <= o <= 0x23FF)


def _runs(s):
    out = []
    for ch in s:
        e = _is_emoji(ch)
        if out and out[-1][1] == e:
            out[-1][0] += ch
        else:
            out.append([ch, e])
    return out


def _wlen(word, fk, size, em, track):
    n = 0.0
    for run, e in _runs(word):
        if e:
            n += font("emoji", int(size * em)).getlength(run)
        else:
            n += font(fk, size).getlength(run) + track * len(run)
    return n


def _draw_word(d, x, by, word, fk, size, fill, em, stroke, stroke_fill, track):
    for run, e in _runs(word):
        if e:
            f = font("emoji", int(size * em))
            d.text((x, by), run, font=f, embedded_color=True, anchor="ls")
            x += f.getlength(run)
        else:
            f = font(fk, size)
            if track:
                for ch in run:
                    d.text((x, by), ch, font=f, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=stroke_fill)
                    x += f.getlength(ch) + track
            else:
                d.text((x, by), run, font=f, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=stroke_fill)
                x += f.getlength(run)
    return x


def _with_shadow(spr, dx, dy, blur, color, opacity):
    pad = int(blur * 2.5 + max(abs(dx), abs(dy)) + 2)
    w2, h2 = spr.width + 2 * pad, spr.height + 2 * pad
    a = Image.new("L", (w2, h2), 0)
    a.paste(spr.getchannel("A"), (pad + int(dx), pad + int(dy)))
    if blur > 0:
        a = a.filter(ImageFilter.GaussianBlur(blur))
    lut = [min(255, int(v * opacity)) for v in range(256)]
    a = a.point(lut)
    sh = Image.new("RGBA", (w2, h2), col(color)[:3] + (0,))
    sh.putalpha(a)
    sh.alpha_composite(spr, (pad, pad))
    return sh


def _with_glow(spr, color, radius, strength=1.0):
    pad = int(radius * 3) + 2
    w2, h2 = spr.width + 2 * pad, spr.height + 2 * pad
    a = Image.new("L", (w2, h2), 0)
    a.paste(spr.getchannel("A"), (pad, pad))
    a = a.filter(ImageFilter.GaussianBlur(radius))
    lut = [min(255, int(v * strength)) for v in range(256)]
    a = a.point(lut)
    g = Image.new("RGBA", (w2, h2), col(color)[:3] + (0,))
    g.putalpha(a)
    g.alpha_composite(spr, (pad, pad))
    return g


@functools.lru_cache(maxsize=700)
def text(txt, fk="bold", size=60, fill="#ffffff", hl=None, max_w=None, align="center", ls=1.18,
         stroke=0, stroke_fill="#000000", glow=None, shadow=None, em=0.92, track=0):
    """Sprite RGBA de texte. Supporte \\n, **mot en surbrillance**, emojis couleur,
    retour à la ligne auto (max_w), contour, halo (glow) et ombre."""
    size = int(size)
    fillc = col(fill)
    hlc = col(hl) if hl else fillc
    strc = col(stroke_fill)
    f = font(fk, size)
    asc, desc = f.getmetrics()
    space = f.getlength(" ") + track

    # un \u00AB mot \u00BB = suite de morceaux (texte, surlign\u00E9?) sans espace entre eux
    lines_words, cur = [[]], []
    for i, seg in enumerate(txt.replace("\uFE0F", "").replace("\u200d", "").split("**")):
        on = (i % 2 == 1)
        for m in _TOK.finditer(seg):
            tok = m.group()
            if tok == "\n":
                if cur:
                    lines_words[-1].append(cur)
                    cur = []
                lines_words.append([])
            elif tok[0] == " ":
                if cur:
                    lines_words[-1].append(cur)
                    cur = []
            else:
                cur.append((tok, on))
    if cur:
        lines_words[-1].append(cur)

    def wl(word):
        return sum(_wlen(p, fk, size, em, track) for p, _ in word)

    lines = []
    for words in lines_words:
        if not max_w:
            lines.append(words)
            continue
        cur, cw = [], 0.0
        for word in words:
            ww = wl(word)
            if cur and cw + space + ww > max_w:
                lines.append(cur)
                cur, cw = [], 0.0
            cw += (space if cur else 0) + ww
            cur.append(word)
        lines.append(cur)

    widths = [sum(wl(w) for w in ln) + space * (len(ln) - 1) if ln else 0 for ln in lines]
    maxw = max(widths) if widths else 0
    pad = stroke + 6
    lh = int(size * ls)
    sw = int(maxw + 2 * pad) + 2
    sh = int(lh * (len(lines) - 1) + asc + desc + 2 * pad) + 2
    base = (strc if stroke else fillc)[:3]
    layer = Image.new("RGBA", (max(sw, 2), max(sh, 2)), base + (0,))
    d = ImageDraw.Draw(layer)
    for i, (ln, wd) in enumerate(zip(lines, widths)):
        if align == "left":
            x = pad
        elif align == "right":
            x = pad + maxw - wd
        else:
            x = pad + (maxw - wd) / 2
        by = pad + asc + i * lh
        for word in ln:
            for piece, on in word:
                x = _draw_word(d, x, by, piece, fk, size, hlc if on else fillc, em, stroke, strc, track)
            x += space
    if glow:
        layer = _with_glow(layer, *glow)
    if shadow:
        layer = _with_shadow(layer, *shadow)
    return layer


def text_width(txt, fk="bold", size=60, **kw):
    return text(txt, fk, size, **kw).width


def fit(txt, fk, size, max_w, **kw):
    """Comme text() mais réduit la taille jusqu'à tenir dans max_w."""
    size = int(size)
    spr = text(txt, fk, size, **kw)
    while spr.width > max_w and size > 14:
        size -= 4
        spr = text(txt, fk, size, **kw)
    return spr


def typed(s, p):
    return s[:int(len(s) * clamp(p))]


# ------------------------------------------------------------------ dégradés
@functools.lru_cache(maxsize=48)
def gradient(w, h, stops, angle=90):
    cols = [col(c) for c in stops]
    cols = [c if len(c) == 4 else c + (255,) for c in cols]
    pos = np.linspace(0, 1, len(cols))
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    proj = (xs - w / 2) * dx + (ys - h / 2) * dy
    half = (abs(w * dx) + abs(h * dy)) / 2 or 1
    t = np.clip((proj / half + 1) / 2, 0, 1)
    out = np.empty((h, w, 4), np.uint8)
    for i in range(4):
        out[..., i] = np.interp(t, pos, [c[i] for c in cols]).astype(np.uint8)
    return Image.fromarray(out)


def new_frame(stops, angle=90):
    return gradient(W, H, tuple(stops), angle).convert("RGB")


_GRID = {}


def _grid(w, h):
    if (w, h) not in _GRID:
        _GRID[(w, h)] = np.mgrid[0:h, 0:w].astype(np.float32)
    return _GRID[(w, h)]


def blobs_bg(t, base, blobs, scale=8):
    """Fond « mesh gradient » animé. blobs = [(couleur, cx, cy, rayon, ax, ay, vitesse, phase, alpha)]"""
    w, h = W // scale, H // scale
    ys, xs = _grid(w, h)
    img = np.empty((h, w, 3), np.float32)
    img[:] = col(base)[:3]
    for (color, cx, cy, r, ax, ay, sp, ph, alpha) in blobs:
        x = (cx + ax * math.sin(t * sp + ph)) * w
        y = (cy + ay * math.cos(t * sp * 0.8 + ph * 1.7)) * h
        d2 = ((xs - x) ** 2 + (ys - y) ** 2) / ((r * w) ** 2)
        a = (alpha * np.exp(-d2))[..., None]
        img = img * (1 - a) + np.array(col(color)[:3], np.float32) * a
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), BICUBIC)


# ------------------------------------------------------------------- formes
def _mask(kind, w, h, r, ss):
    m = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    if kind == "ellipse":
        d.ellipse((0, 0, w * ss - 1, h * ss - 1), fill=255)
    else:
        d.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=r * ss, fill=255)
    return m.resize((w, h), BOX)


def _fill_layer(w, h, fill, grad):
    if grad:
        return gradient(w, h, tuple(grad[0]), grad[1]).copy()
    return Image.new("RGBA", (w, h), col(fill)[:3] + (255,))


@functools.lru_cache(maxsize=900)
def shape(kind, w, h, r=0, fill=None, grad=None, outline=None, ow=0, shadow=None, alpha=255):
    w, h = max(int(w), 2), max(int(h), 2)
    r = int(min(r, w // 2, h // 2))
    ss = 4 if w * h < 120_000 else 3 if w * h < 450_000 else 2
    mo = _mask(kind, w, h, r, ss)
    fa = col(fill)[3] if (fill is not None and len(col(fill)) == 4) else 255
    k = alpha / 255.0 * fa / 255.0
    if k < 1:
        mo = mo.point([int(v * k) for v in range(256)])
    if outline and ow:
        wi, hi = w - 2 * ow, h - 2 * ow
        mi = Image.new("L", (w, h), 0)
        if wi > 0 and hi > 0:
            mi.paste(_mask(kind, wi, hi, max(0, r - ow), ss), (ow, ow))
        ring = ImageChops.subtract(_mask(kind, w, h, r, ss), mi)
        spr = Image.new("RGBA", (w, h), col(outline)[:3] + (0,))
        spr.putalpha(ring)
        if fill is not None or grad:
            inner = _fill_layer(w, h, fill, grad)
            inner.putalpha(mi.point([int(v * k) for v in range(256)]) if k < 1 else mi)
            spr = Image.alpha_composite(inner, spr)
    else:
        spr = _fill_layer(w, h, fill, grad)
        spr.putalpha(mo)
    if shadow:
        spr = _with_shadow(spr, *shadow)
    return spr


def rrect(w, h, r, fill=None, **kw):
    return shape("rrect", w, h, r, fill=fill, **kw)


def circle(d, fill=None, **kw):
    return shape("ellipse", d, d, 0, fill=fill, **kw)


def ellipse(w, h, fill=None, **kw):
    return shape("ellipse", w, h, 0, fill=fill, **kw)


# ------------------------------------------------------------- composition
def _lut(alpha):
    return [int(v * alpha) for v in range(256)]


def put(dst, spr, x, y, alpha=1.0):
    if alpha <= 0.003:
        return
    x, y = int(round(x)), int(round(y))
    if alpha >= 0.997:
        dst.paste(spr, (x, y), spr)
    else:
        dst.paste(spr, (x, y), spr.getchannel("A").point(_lut(alpha)))


def place(dst, spr, cx, cy, s=1.0, rot=0.0, alpha=1.0, ax=0.5, ay=0.5):
    """Dépose un sprite centré (ou ancré par ax, ay) avec échelle, rotation, opacité."""
    if s <= 0.01 or alpha <= 0.003:
        return
    if s != 1.0:
        spr = spr.resize((max(1, round(spr.width * s)), max(1, round(spr.height * s))), BICUBIC)
    if rot:
        # rotation autour du point d'ancrage = centre ; ancre non centrée : approximation
        spr = spr.rotate(rot, BICUBIC, expand=True)
    put(dst, spr, cx - spr.width * ax, cy - spr.height * ay, alpha)


def crop_w(spr, p):
    """Révèle un sprite de gauche à droite (effet écriture / wipe)."""
    p = clamp(p)
    if p >= 1:
        return spr
    w = max(1, int(spr.width * p))
    return spr.crop((0, 0, w, spr.height))


def fast_blur(img, r):
    if r <= 0.5:
        return img
    s = max(2, int(r // 3) + 1)
    small = img.resize((img.width // s, img.height // s), BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(max(0.6, r / s)))
    return small.resize(img.size, BICUBIC)


def rgb_split(img, dx):
    dx = int(dx)
    if dx == 0:
        return img
    r, g, b = img.split()
    r = ImageChops.offset(r, dx, 0)
    b = ImageChops.offset(b, -dx, 0)
    return Image.merge("RGB", (r, g, b))


def overlay(img, color, alpha):
    """Voile de couleur sur toute l'image."""
    if alpha <= 0.003:
        return img
    return Image.blend(img, Image.new("RGB", img.size, col(color)[:3]), clamp(alpha))


# ----------------------------------------------------------------- confettis
@functools.lru_cache(maxsize=256)
def _confetti_sprite(color, w, h):
    return rrect(w, h, 2, fill=color)


def confetti(img, t, t0=0.0, n=60, seed=1, origin=(W // 2, 760), colors=("#ff3b6b", "#ffd60a", "#2ee6a6", "#4cc9ff", "#ffffff"),
             power=(450, 1150), g=1500.0, life=2.6, size=(12, 24), up=True):
    p = t - t0
    if p < 0 or p > life:
        return
    rnd = random.Random(seed)
    for _ in range(n):
        ang = rnd.uniform(-math.pi * 0.97, -math.pi * 0.03) if up else rnd.uniform(0, math.pi * 2)
        sp = rnd.uniform(*power)
        vx, vy = math.cos(ang) * sp, math.sin(ang) * sp
        c = rnd.choice(colors)
        w = int(rnd.uniform(*size))
        h = max(4, int(w * rnd.uniform(0.35, 0.6)))
        spin = rnd.uniform(-540, 540)
        r0 = rnd.uniform(0, 360)
        k = 1.6
        x = origin[0] + vx * (1 - math.exp(-k * p)) / k
        y = origin[1] + vy * (1 - math.exp(-k * p)) / k + 0.5 * g * p * p * 0.55
        fade = clamp((life - p) / 0.6)
        place(img, _confetti_sprite(c, w, h), x, y, rot=r0 + spin * p, alpha=fade)


# --------------------------------------------------------------------- QR
@functools.lru_cache(maxsize=16)
def qr_modules(data, ecc="M"):
    import segno
    q = segno.make(data, error=ecc.lower(), boost_error=False)
    return np.array([list(r) for r in q.matrix], dtype=np.uint8)


def qr_sprite(data, target, fg="#0b1020", bg="#ffffff", quiet=3, ecc="M", reveal=None, seed=3):
    """QR code net (modules entiers). reveal = 0..1 : apparition progressive des modules."""
    m = qr_modules(data, ecc)
    n = m.shape[0]
    px = max(2, target // (n + 2 * quiet))
    if reveal is not None and reveal < 1:
        rnd = np.random.RandomState(seed)
        yy, xx = np.mgrid[0:n, 0:n]
        dist = np.hypot(yy - n / 2, xx - n / 2) / (n * 0.72)
        delay = np.clip(dist * 0.7 + rnd.rand(n, n) * 0.3, 0, 1)
        m = (m & (delay <= reveal * 1.02)).astype(np.uint8)
    arr = np.pad(m, quiet)
    mask = Image.fromarray((arr * 255).astype(np.uint8), "L").resize(((n + 2 * quiet) * px,) * 2, NEAREST)
    img = Image.new("RGBA", mask.size, col(bg)[:3] + (255,))
    img.paste(Image.new("RGBA", mask.size, col(fg)[:3] + (255,)), (0, 0), mask)
    return img


# --------------------------------------------------------------------- vidéo
def ffmpeg_exe():
    exe = os.environ.get("FFMPEG")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


class VideoWriter:
    def __init__(self, path, audio=None, crf=19, fps=FPS):
        cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
        if audio:
            cmd += ["-i", audio]
        cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-profile:v", "high",
                "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-movflags", "+faststart", "-r", str(fps)]
        if audio:
            cmd += ["-af", "loudnorm=I=-15:TP=-2:LRA=11,alimiter=limit=0.8:level=0", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest"]
        cmd += [path]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def write(self, img):
        if img.mode != "RGB":
            img = img.convert("RGB")
        self.p.stdin.write(img.tobytes())

    def close(self):
        self.p.stdin.close()
        return self.p.wait()
