# -*- coding: utf-8 -*-
"""Synthé audio (numpy/scipy) : musique originale + effets sonores synchronisés.
Tout est généré par le code -> aucun droit d'auteur, aucun fichier audio externe."""
import functools
import wave

import numpy as np
from scipy import signal as sg

SR = 44100


def _t(n):
    return np.arange(n, dtype=np.float64) / SR


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


@functools.lru_cache(maxsize=128)
def _sos(kind, fc, order):
    fc = fc if isinstance(fc, tuple) else min(fc, SR * 0.45)
    return sg.butter(order, fc if not isinstance(fc, tuple) else list(fc), kind, fs=SR, output="sos")


def lp(x, fc, order=2):
    return sg.sosfilt(_sos("low", float(fc), order), x)


def hp(x, fc, order=2):
    return sg.sosfilt(_sos("high", float(fc), order), x)


def bp(x, lo, hi, order=2):
    return sg.sosfilt(_sos("band", (float(lo), float(min(hi, SR * 0.45))), order), x)


def soft(x, drive=1.0):
    return np.tanh(x * drive)


def _freeze(a):
    a = a.astype(np.float64)
    a.setflags(write=False)
    return a


def ad(n, a, tau):
    env = np.exp(-_t(n) / tau)
    na = int(a * SR)
    if na > 0:
        env[:na] *= np.linspace(0, 1, na)
    return env


def ar(n, a, r):
    env = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        env[:na] = np.linspace(0, 1, min(na, n))
    if nr and nr <= n:
        env[-nr:] *= np.linspace(1, 0, nr)
    return env


def saw(freq, n, maxh=24):
    t = _t(n)
    k = int(max(1, min(maxh, 10000 // max(freq, 20))))
    out = np.zeros(n)
    for h in range(1, k + 1):
        out += np.sin(2 * np.pi * freq * h * t) / h
    return out * (2 / np.pi)


def square(freq, n, maxh=20):
    t = _t(n)
    k = int(max(1, min(maxh, 10000 // max(freq, 20))))
    out = np.zeros(n)
    for h in range(1, 2 * k, 2):
        out += np.sin(2 * np.pi * freq * h * t) / h
    return out * (4 / np.pi) * 0.5


def tri(freq, n):
    t = _t(n)
    return (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * freq * t))


# ---------------------------------------------------------------- percussions
@functools.lru_cache(maxsize=32)
def kick(f0=150, f1=48, decay=0.17, dur=0.5, click=0.3):
    n = int(dur * SR)
    t = _t(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    clk = hp(np.random.RandomState(11).randn(n), 2000) * np.exp(-t / 0.003) * click
    out = soft((body + clk) * 1.3)
    out[-400:] *= np.linspace(1, 0, 400)
    return _freeze(out)


@functools.lru_cache(maxsize=16)
def snare(dur=0.3, tone=190):
    n = int(dur * SR)
    t = _t(n)
    noise = hp(np.random.RandomState(2).randn(n), 1600) * np.exp(-t / 0.085)
    body = np.sin(2 * np.pi * tone * t) * np.exp(-t / 0.05) * 0.7
    return _freeze(soft((noise * 0.9 + body) * 1.1))


@functools.lru_cache(maxsize=16)
def clap(dur=0.4):
    n = int(dur * SR)
    t = _t(n)
    rng = np.random.RandomState(3)
    base = bp(rng.randn(n), 900, 3200)
    env = np.zeros(n)
    for k in (0.0, 0.012, 0.024):
        env += np.exp(-np.maximum(t - k, 0) / 0.008) * (t >= k)
    env = env * 0.7 + np.exp(-t / 0.11) * 0.5
    return _freeze(soft(base * env * 1.4))


@functools.lru_cache(maxsize=16)
def hat(open_=False, dur=0.25):
    n = int(dur * SR)
    t = _t(n)
    x = hp(np.random.RandomState(4).randn(n), 7000) * np.exp(-t / (0.09 if open_ else 0.022))
    return _freeze(x * 0.8)


@functools.lru_cache(maxsize=16)
def shaker(dur=0.12):
    n = int(dur * SR)
    t = _t(n)
    x = bp(np.random.RandomState(5).randn(n), 5000, 12000)
    env = np.minimum(t / 0.012, 1) * np.exp(-t / 0.035)
    return _freeze(x * env * 0.9)


@functools.lru_cache(maxsize=32)
def conga(f=230, dur=0.3):
    n = int(dur * SR)
    t = _t(n)
    fr = f * (1 + 0.25 * np.exp(-t / 0.02))
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.09)
    slap = bp(np.random.RandomState(6).randn(n), 1500, 4000) * np.exp(-t / 0.008) * 0.35
    return _freeze(soft((body + slap) * 1.2))


@functools.lru_cache(maxsize=16)
def tom(f=110, dur=0.4):
    n = int(dur * SR)
    t = _t(n)
    fr = f * (1 + 0.5 * np.exp(-t / 0.05))
    return _freeze(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.16))


# ------------------------------------------------------------------- tonales
@functools.lru_cache(maxsize=256)
def bass(freq, dur=0.3, kind="sine"):
    n = int((dur + 0.06) * SR)
    t = _t(n)
    if kind == "808":
        f = freq * (1 + 0.7 * np.exp(-t / 0.03))
        w = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / max(dur * 0.9, 0.2))
        w = soft(w * 2.2) * 0.8
        return _freeze(w * ar(n, 0.002, 0.04))
    if kind == "saw":
        w = lp(saw(freq, n), 700) * 1.2
    elif kind == "tri":
        w = tri(freq, n)
    elif kind == "slap":
        w = (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t / 0.08)
             + 0.3 * lp(saw(freq, n), 1800)) * np.exp(-t / 0.22)
    else:
        w = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t / 0.2)
    return _freeze(soft(w * 1.1) * ar(n, 0.004, 0.05))


@functools.lru_cache(maxsize=256)
def pluck(freq, dur=0.5):
    n = int(dur * SR)
    t = _t(n)
    w = (np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.2) + 0.35 * np.sin(2 * np.pi * 4 * freq * t) * np.exp(-t / 0.05)
         + 0.12 * np.sin(2 * np.pi * 10 * freq * t) * np.exp(-t / 0.02))
    return _freeze(w * ar(n, 0.002, 0.03))


@functools.lru_cache(maxsize=256)
def bell(freq, dur=1.0):
    n = int(dur * SR)
    t = _t(n)
    parts = [(1, 1.0, 0.7), (2.0, 0.5, 0.45), (3.0, 0.3, 0.3), (4.2, 0.2, 0.22), (5.4, 0.12, 0.14)]
    w = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / tau) for r, a, tau in parts)
    return _freeze(w * 0.6 * ar(n, 0.001, 0.05))


@functools.lru_cache(maxsize=256)
def epiano(freq, dur=0.9):
    n = int(dur * SR)
    t = _t(n)
    mod = np.sin(2 * np.pi * freq * t) * 1.6 * np.exp(-t / 0.22)
    w = np.sin(2 * np.pi * freq * t + mod) * np.exp(-t / 0.7) + 0.2 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t / 0.1)
    return _freeze(w * 0.8 * ar(n, 0.003, 0.08))


@functools.lru_cache(maxsize=256)
def sqlead(freq, dur=0.2):
    n = int(dur * SR)
    return _freeze(square(freq, n) * ad(n, 0.002, 0.18) * 0.7 * ar(n, 0.002, 0.02))


@functools.lru_cache(maxsize=256)
def stab(freq, dur=0.25):
    n = int(dur * SR)
    w = lp(saw(freq, n) + saw(freq * 1.006, n), 3200) * np.exp(-_t(n) / 0.12)
    return _freeze(w * 0.7 * ar(n, 0.003, 0.03))


@functools.lru_cache(maxsize=64)
def pad(freqs, dur=2.0, bright=1800):
    n = int(dur * SR)
    w = np.zeros(n)
    for f in freqs:
        for cents in (-8, 0, 8):
            w += saw(f * 2 ** (cents / 1200.0), n, maxh=8)
    w = lp(w, bright) / (len(freqs) * 2.2)
    return _freeze(w * ar(n, min(0.35, dur * 0.3), min(0.5, dur * 0.4)))


@functools.lru_cache(maxsize=64)
def supersaw(freq, dur=0.5):
    n = int(dur * SR)
    w = np.zeros(n)
    for cents in (-14, -7, 0, 7, 14):
        w += saw(freq * 2 ** (cents / 1200.0), n, maxh=10)
    return _freeze(lp(w, 4500) * 0.22 * ar(n, 0.01, 0.1))


# ------------------------------------------------------------------- effets
def _noise(n, seed=0):
    return np.random.RandomState(seed).randn(n)


@functools.lru_cache(maxsize=32)
def sweep_noise(dur, f0, f1, seed=0):
    n = int(dur * SR)
    noise = _noise(n, seed)
    cuts = np.geomspace(200, 12000, 10)
    bank = np.stack([lp(noise, c) for c in cuts])
    fc = f0 * (f1 / f0) ** np.linspace(0, 1, n)
    idx = np.interp(np.log(fc), np.log(cuts), np.arange(len(cuts)))
    i0 = np.clip(np.floor(idx).astype(int), 0, len(cuts) - 2)
    fr = idx - i0
    ar_ = np.arange(n)
    return _freeze(bank[i0, ar_] * (1 - fr) + bank[i0 + 1, ar_] * fr)


def fx_whoosh(dur=0.55, up=True):
    n = int(dur * SR)
    x = sweep_noise(dur, 300 if up else 6000, 6000 if up else 300)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6
    return x * env * 0.7


def fx_swipe():
    return fx_whoosh(0.28, True) * 0.8


def fx_riser(dur=1.6):
    n = int(dur * SR)
    x = sweep_noise(dur, 250, 11000, seed=3)
    t = _t(n)
    tone = np.sin(2 * np.pi * np.cumsum(200 * 2 ** (np.linspace(0, 3, n))) / SR) * 0.15
    env = np.linspace(0, 1, n) ** 2.2
    out = (x * 0.9 + tone) * env
    out[-300:] *= np.linspace(1, 0, 300)
    return out


def fx_impact(dur=1.3):
    n = int(dur * SR)
    t = _t(n)
    boom = np.sin(2 * np.pi * 52 * t * (1 + 0.5 * np.exp(-t / 0.08))) * np.exp(-t / 0.45)
    crash = lp(_noise(n, 5), 2500) * np.exp(-t / 0.22) * 0.5
    return soft((boom * 1.2 + crash) * 1.3) * 0.9


def fx_slam():
    n = int(0.5 * SR)
    t = _t(n)
    boom = np.sin(2 * np.pi * 85 * t * (1 + 0.6 * np.exp(-t / 0.04))) * np.exp(-t / 0.14)
    hit = hp(_noise(n, 8), 800) * np.exp(-t / 0.03) * 0.6
    return soft((boom + hit) * 1.4) * 0.85


def fx_pop(f_end=1000, f_start=420):
    n = int(0.16 * SR)
    t = _t(n)
    f = f_end - (f_end - f_start) * np.exp(-t / 0.025)
    w = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.045)
    return w * 0.8 * ar(n, 0.001, 0.02)


def fx_tick(f=2400):
    n = int(0.04 * SR)
    t = _t(n)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) + bp(_noise(n, 9), 1500, 6000) * np.exp(-t / 0.004) * 0.6) * 0.8


def fx_type(seed=0):
    rng = np.random.RandomState(seed)
    n = int(0.05 * SR)
    t = _t(n)
    f = rng.uniform(1800, 3200)
    return (bp(rng.randn(n), 1800, 6000) * np.exp(-t / 0.006) * 0.9 + np.sin(2 * np.pi * f * t) * np.exp(-t / 0.003) * 0.4) * 0.8


def fx_ding(f=1568.0, dur=1.0):
    return bell(f, dur) * 0.9


def fx_coin():
    n1, n2 = int(0.07 * SR), int(0.45 * SR)
    a = square(988, n1) * ad(n1, 0.001, 0.1) * 0.6
    b = square(1319, n2) * ad(n2, 0.001, 0.2) * 0.6
    return np.concatenate([a, b])


def fx_success():
    out = np.zeros(int(1.2 * SR))
    for i, m in enumerate((72, 76, 79, 84)):
        w = bell(mtof(m), 0.8) * 0.8
        s = int(i * 0.075 * SR)
        out[s:s + len(w)] += w[:len(out) - s]
    return out


def fx_buzz():
    n = int(0.36 * SR)
    t = _t(n)
    w = lp(saw(110, n), 1100) * (0.65 + 0.35 * np.sign(np.sin(2 * np.pi * 28 * t)))
    return soft(w * 1.4) * 0.75 * ar(n, 0.004, 0.05)


def fx_stamp():
    n = int(0.55 * SR)
    t = _t(n)
    thump = np.sin(2 * np.pi * 70 * t * (1 + 0.5 * np.exp(-t / 0.05))) * np.exp(-t / 0.16)
    crack = lp(_noise(n, 12), 3500) * np.exp(-t / 0.025) * 0.7
    return soft((thump * 1.3 + crack) * 1.3) * 0.9


def fx_msg_in():
    a, b = bell(mtof(88), 0.35) * 0.6, bell(mtof(83), 0.5) * 0.6
    out = np.zeros(int(0.65 * SR))
    out[:len(a)] += a
    s = int(0.09 * SR)
    out[s:s + len(b)] += b[:len(out) - s]
    return out


def fx_msg_out():
    n = int(0.22 * SR)
    t = _t(n)
    pop = np.sin(2 * np.pi * np.cumsum(500 + 700 * (1 - np.exp(-t / 0.03))) / SR) * np.exp(-t / 0.06)
    sw = fx_whoosh(0.18, True)[:n] * 0.4
    return pop * 0.7 + np.pad(sw, (0, max(0, n - len(sw))))[:n]


def fx_notif():
    out = np.zeros(int(0.9 * SR))
    for i, m in enumerate((88, 93)):
        w = bell(mtof(m), 0.6) * 0.65
        s = int(i * 0.11 * SR)
        out[s:s + len(w)] += w[:len(out) - s]
    return out


def fx_scan():
    n = int(0.5 * SR)
    t = _t(n)
    f = 600 + 1400 * np.linspace(0, 1, n) ** 1.4
    w = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 22 * t))
    return w * 0.45 * ar(n, 0.01, 0.1)


def fx_glitch():
    n = int(0.3 * SR)
    rng = np.random.RandomState(14)
    x = hp(rng.randn(n), 900)
    gate = np.zeros(n)
    i = 0
    while i < n:
        seg = int(rng.uniform(0.01, 0.05) * SR)
        if rng.rand() < 0.6:
            gate[i:i + seg] = 1
        i += seg
    return soft(x * gate * 1.2) * 0.55 * ar(n, 0.001, 0.05)


def fx_click():
    return fx_tick(1700) * 0.8


def fx_thunk():
    n = int(0.18 * SR)
    t = _t(n)
    return soft((np.sin(2 * np.pi * 130 * t) * np.exp(-t / 0.05) + lp(_noise(n, 15), 900) * np.exp(-t / 0.03)) * 1.3) * 0.8


def fx_sparkle():
    out = np.zeros(int(1.0 * SR))
    rng = np.random.RandomState(21)
    for i in range(9):
        w = bell(mtof(rng.choice([84, 88, 91, 96, 100])), 0.5) * 0.35
        s = int(rng.uniform(0, 0.55) * SR)
        out[s:s + len(w)] += w[:len(out) - s]
    return out


def fx_jackpot():
    out = np.zeros(int(1.8 * SR))
    for i, m in enumerate((72, 76, 79, 84, 88, 91, 96)):
        w = bell(mtof(m), 0.9) * 0.7
        s = int(i * 0.06 * SR)
        out[s:s + len(w)] += w[:len(out) - s]
    sp = fx_sparkle()
    out[int(0.4 * SR):int(0.4 * SR) + len(sp)] += sp[:len(out) - int(0.4 * SR)] * 0.8
    return out


SFX = {
    "whoosh": fx_whoosh, "swipe": fx_swipe, "riser": fx_riser, "impact": fx_impact, "slam": fx_slam,
    "pop": fx_pop, "tick": fx_tick, "type": fx_type, "ding": fx_ding, "coin": fx_coin, "success": fx_success,
    "buzz": fx_buzz, "stamp": fx_stamp, "msg_in": fx_msg_in, "msg_out": fx_msg_out, "notif": fx_notif,
    "scan": fx_scan, "glitch": fx_glitch, "click": fx_click, "thunk": fx_thunk, "sparkle": fx_sparkle,
    "jackpot": fx_jackpot,
}


# ---------------------------------------------------------------- mélange
class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR)
        self.bus = {k: np.zeros((2, self.n)) for k in ("drums", "bass", "pad", "mel", "sfx")}
        self.kicks = []

    def add(self, bus, buf, t, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i < 0 or i >= self.n:
            return
        j = min(self.n, i + len(buf))
        seg = buf[:j - i]
        gl = gain * np.cos((pan + 1) * np.pi / 4)
        gr = gain * np.sin((pan + 1) * np.pi / 4)
        self.bus[bus][0, i:j] += seg * gl
        self.bus[bus][1, i:j] += seg * gr


@functools.lru_cache(maxsize=4)
def _reverb_ir(decay, seed):
    n = int(decay * SR)
    t = _t(n)
    irs = []
    for ch in range(2):
        r = np.random.RandomState(seed + ch).randn(n) * np.exp(-t / (decay / 4.2))
        r = lp(r, 5500)
        r[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
        irs.append(r / np.sqrt(np.sum(r ** 2)))
    return np.stack(irs)


def reverb(x, wet=0.2, decay=1.6):
    ir = _reverb_ir(decay, 31)
    out = np.stack([sg.fftconvolve(x[c], ir[c], mode="full")[:x.shape[1]] for c in range(2)])
    return x * (1 - wet * 0.5) + out * wet * 2.2


# --------------------------------------------------------------- musique
PROGS = dict(
    minor=[(0, "m"), (8, "M"), (3, "M"), (10, "M")],
    minor2=[(0, "m"), (5, "m"), (8, "M"), (7, "M")],
    major=[(0, "M"), (7, "M"), (9, "m"), (5, "M")],
    major2=[(0, "M"), (5, "M"), (9, "m"), (7, "M")],
)
TRI = dict(M=(0, 4, 7), m=(0, 3, 7))

STYLES = dict(
    trap=dict(kick=[0, 10, 11], snare=[], clap=[8], hat=[0, 2, 4, 6, 8, 10, 12, 14, 15], ohat=[6], bass=("808", [0, 10]),
              mel=("bell", [0, 3, 6, 10, 13]), pad=True, bassvol=0.8, padvol=0.8, droppad=False),
    afro=dict(kick=[0, 7, 10], clap=[4, 12], shaker=[0, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15], conga=[3, 6, 11, 14],
              bass=("sine", [0, 3, 6, 10, 13]), mel=("pluck", [0, 3, 6, 8, 11, 14]), pad=True),
    chip=dict(kick=[0, 8], snare=[4, 12], hat=[0, 2, 4, 6, 8, 10, 12, 14], bass=("tri", [0, 2, 4, 6, 8, 10, 12, 14]),
              mel=("sq", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]), pad=False, melvol=0.75),
    lofi=dict(kick=[0, 10], snare=[4, 12], hat=[0, 2, 4, 6, 8, 10, 12, 14], bass=("sine", [0, 10]),
              mel=("epiano", [0, 6]), pad=False, chordmel=True, swing=0.18),
    edm=dict(kick=[0, 4, 8, 12], clap=[4, 12], ohat=[2, 6, 10, 14], hat=[0, 2, 4, 6, 8, 10, 12, 14],
             bass=("saw", [2, 3, 6, 7, 10, 11, 14, 15]), mel=("pluck", [0, 3, 6, 9, 12, 14]), pad=True, stabs=[0, 6, 10]),
    ambient=dict(kick=[0], bass=("sine", [0]), mel=("bell", [0, 6, 10]), pad=True, padvol=1.3, soft=True),
    funk=dict(kick=[0, 3, 10], snare=[4, 12], hat=list(range(16)), bass=("slap", [0, 3, 6, 7, 10, 12, 14]),
              mel=("pluck", [2, 6, 11, 15]), pad=False, stabs=[2, 6, 11, 14]),
)


def play_music(mix, style, dur, bpm, root, lv, prog="minor", seed=1):
    S = STYLES[style]
    rng = np.random.RandomState(seed)
    step = 60.0 / bpm / 4
    ns = int(dur / step) + 2
    chords = PROGS[prog]
    swing = S.get("swing", 0.0)
    bar_len = step * 16

    def level(t):
        cur = 0
        for tt, l in lv:
            if t >= tt:
                cur = l
        return cur

    mel_i = 0
    for s in range(ns):
        pos, bar = s % 16, s // 16
        t = s * step + (swing * step if s % 2 else 0.0)
        if t >= dur:
            break
        L = level(t)
        if L <= 0:
            continue
        off, q = chords[bar % len(chords)]
        triad = [root + off + i for i in TRI[q]]
        soft_ = S.get("soft", False)
        if pos in S.get("kick", ()) and (not soft_ or bar % 2 == 0):
            mix.add("drums", kick(), t, 0.8 if not soft_ else 0.35)
            mix.kicks.append(t)
        if L >= 2:
            if pos in S.get("snare", ()):
                mix.add("drums", snare(), t, 0.5)
            if pos in S.get("clap", ()):
                mix.add("drums", clap(), t, 0.55)
            if pos in S.get("hat", ()):
                vel = (0.34 if pos % 4 == 2 else 0.22) * (0.8 if style == "lofi" else 1)
                mix.add("drums", hat(), t, vel * rng.uniform(0.85, 1.0), 0.25)
            if pos in S.get("shaker", ()):
                mix.add("drums", shaker(), t, (0.34 if pos % 4 in (2, 3) else 0.2), -0.2)
            if pos in S.get("conga", ()):
                mix.add("drums", conga(230 if pos % 2 else 300), t, 0.45, 0.35)
        if L >= 3 and pos in S.get("ohat", ()):
            mix.add("drums", hat(True), t, 0.3, -0.3)
        # basse
        bk, bpat = S["bass"]
        if pos in bpat:
            n_ = triad[0] - 24 if bk != "tri" else triad[0] - 12
            if style in ("afro", "funk") and pos in (6, 13):
                n_ = triad[2] - 24
            mix.add("bass", bass(round(mtof(n_), 2), step * (3 if bk != "808" else 5), bk), t, 0.8 if bk != "808" else 0.9)
        # nappes
        if S.get("pad") and pos == 0:
            fr = tuple(round(mtof(x + 12), 2) for x in triad)
            mix.add("pad", pad(fr, bar_len * 1.02), t, 0.6, 0.0)
        # accords (lofi / stabs)
        if S.get("chordmel") and pos in S["mel"][1]:
            for k, x in enumerate(triad):
                mix.add("mel", epiano(round(mtof(x + 12 + (12 if k == 2 and pos else 0)), 2), 1.0), t + k * 0.012, 0.28, -0.3 + 0.3 * k)
        elif L >= 2:
            mk, mpat = S.get("mel", (None, ()))
            if mk and pos in mpat:
                arp = [triad[0] + 12, triad[1] + 12, triad[2] + 12, triad[0] + 24, triad[2] + 12, triad[1] + 12]
                note = arp[mel_i % len(arp)]
                if mk == "sq":
                    note = arp[(s) % len(arp)] + (12 if L >= 3 else 0)
                mel_i += 1
                fq = round(mtof(note), 2)
                mv = S.get("melvol", 1.0)
                if mk == "pluck":
                    mix.add("mel", pluck(fq, 0.45), t, 0.5 * mv, rng.uniform(-0.4, 0.4))
                elif mk == "bell":
                    mix.add("mel", bell(fq, 0.9), t, 0.38 * mv, rng.uniform(-0.4, 0.4))
                elif mk == "sq":
                    mix.add("mel", sqlead(fq, step * 1.6), t, 0.22 * mv, rng.uniform(-0.3, 0.3))
        if L >= 2 and pos in S.get("stabs", ()):
            for k, x in enumerate(triad):
                mix.add("mel", stab(round(mtof(x + 12), 2), 0.22) if style == "funk" else supersaw(round(mtof(x + 12), 2), 0.3), t, 0.16, -0.25 + 0.25 * k)
    return mix


def _sidechain(mix, depth=0.55, rel=0.14):
    duck = np.ones(mix.n)
    L = int(0.5 * SR)
    curve = 1 - depth * np.exp(-np.arange(L) / SR / rel)
    for tk in mix.kicks:
        i = int(tk * SR)
        j = min(mix.n, i + L)
        duck[i:j] = np.minimum(duck[i:j], curve[:j - i])
    return duck


def _voice_duck(vb, hold=0.30):
    """Courbe 0..1 : 1 pendant que la voix parle (avec maintien sur les petites pauses), transitions douces."""
    from scipy.ndimage import maximum_filter1d
    act = (lp(np.abs(vb), 20) > 0.015).astype(np.float64)
    held = maximum_filter1d(act, size=max(1, int(hold * SR)))
    return np.clip(lp(held, 4), 0.0, 1.0)


def render_audio(path, dur, spec, sfx=(), music_vol=1.0, voice=()):
    """spec = dict(style, bpm, root, lv=[(t, niveau)], prog, seed) ; sfx = [(t, nom, gain)] ;
    voice = [(t, tableau mono 44,1 kHz)] : voix off, la musique et les effets baissent pendant qu'elle parle."""
    mix = Mix(dur)
    if spec:
        play_music(mix, spec["style"], dur, spec["bpm"], spec["root"], spec["lv"], spec.get("prog", "minor"), spec.get("seed", 1))
    rng = np.random.RandomState(99)
    for ev in sfx:
        t, name = ev[0], ev[1]
        g = ev[2] if len(ev) > 2 else 1.0
        fn = SFX[name]
        buf = fn(seed=int(rng.randint(0, 1000))) if name == "type" else fn()
        pk_ = float(np.max(np.abs(buf))) or 1.0
        if pk_ > 0.9:
            buf = buf * (0.9 / pk_)
        mix.add("sfx", buf, t, 0.9 * g, rng.uniform(-0.15, 0.15))
    duck = _sidechain(mix) if mix.kicks else np.ones(mix.n)
    b = mix.bus
    st = STYLES[spec["style"]] if spec else {}
    music = (b["drums"] * 0.62 + b["bass"] * duck * 0.55 * st.get("bassvol", 1) + b["pad"] * duck * 0.30 * st.get("padvol", 1)
             + reverb(b["mel"], 0.18, 1.5) * 0.45) * music_vol
    sfxb = reverb(b["sfx"], 0.14, 1.2) * 1.0
    vb = None
    if voice:
        vb = np.zeros(mix.n)
        for tv, arr in voice:
            i = int(tv * SR)
            if 0 <= i < mix.n:
                j = min(mix.n, i + len(arr))
                vb[i:j] += arr[:j - i]
        sm = _voice_duck(vb)
        music = music * (1 - 0.62 * sm)        # la musique baisse d'environ 8 dB sous la voix
        sfxb = sfxb * (1 - 0.30 * sm)          # les effets baissent un peu moins
    out = music * 0.55 + sfxb * 0.95
    if vb is not None:
        out = out + np.stack([vb, vb]) * 1.0
    out = np.tanh(out * 1.05)
    pk = np.max(np.abs(out)) or 1.0
    out = out / pk * 0.89
    fi, fo = int(0.02 * SR), int(0.45 * SR)
    out[:, :fi] *= np.linspace(0, 1, fi)
    out[:, -fo:] *= np.linspace(1, 0, fo)
    data = (np.clip(out.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    return path
