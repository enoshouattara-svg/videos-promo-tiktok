# -*- coding: utf-8 -*-
"""Voix off : synthèse vocale locale avec les voix Windows déjà installées (rien n'est envoyé sur Internet).

Chaque scène peut définir  voice=[dict(text="...", at=<instant de départ voulu>, end=<fin à ne pas dépasser>), ...].
Les lignes sont synthétisées, accélérées au besoin pour tenir dans leur créneau, traitées (aigus, nivellement)
puis mélangées dans audio.render_audio, qui baisse automatiquement la musique pendant que la voix parle."""
import hashlib
import json
import os
import subprocess
import tempfile
import wave

import numpy as np
from scipy import signal as sg

from audio import SR, bp, hp, lp

HERE = os.path.dirname(os.path.abspath(__file__))
PS_SCRIPT = os.path.join(HERE, "voice_synth.ps1")
CACHE = os.path.join(tempfile.gettempdir(), "promo_voix")
LABELS = {"hortense": "femme", "julie": "femme2", "paul": "homme"}      # suffixe du nom de fichier


def _path(voice, rate, pitch, text):
    h = hashlib.sha1(f"{voice}|{rate:.3f}|{pitch:.3f}|{text}".encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE, f"{voice.lower()}_{h}.wav")


def synth(jobs):
    """jobs = [(voix, débit, hauteur, texte)] -> chemins des WAV (mis en cache)."""
    os.makedirs(CACHE, exist_ok=True)
    paths, todo, final = [], [], {}
    for voice, rate, pitch, text in jobs:
        out = _path(voice, rate, pitch, text)
        paths.append(out)
        if not os.path.exists(out) and out not in final:
            part = f"{out}.{os.getpid()}.part"
            final[out] = part
            todo.append(dict(voice=voice, rate=rate, pitch=pitch, text=text, out=part.replace("\\", "/")))
    if todo:
        jf = os.path.join(CACHE, f"jobs_{os.getpid()}.json")
        with open(jf, "w", encoding="utf-8") as f:
            json.dump(todo, f, ensure_ascii=False)
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS_SCRIPT, "-JobFile", jf],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError("synthèse vocale impossible : " + (r.stderr or r.stdout)[-600:])
        for out, part in final.items():
            os.replace(part, out)          # écriture atomique : plusieurs rendus en parallèle peuvent partager le cache
    return paths


def _load(path):
    with wave.open(path) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def _process(x, sr, target_rms=0.2):
    """Coupe les silences, passe à 44,1 kHz, ajoute de la présence, nivelle et limite."""
    idx = np.nonzero(np.abs(x) > 0.012)[0]
    if len(idx):
        x = x[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.05 * sr)]
    g = int(np.gcd(SR, sr))
    x = sg.resample_poly(x, SR // g, sr // g)
    x = hp(x, 85)
    x = x + 0.30 * bp(x, 2200, 5200) + 0.12 * bp(x, 5200, 7600)          # présence : la voix perce au-dessus de la musique
    env = np.maximum(lp(np.abs(x), 10), 0.0) + 2e-3                      # nivellement doux (le filtre peut osciller sous 0)
    x = x * lp(np.clip((0.10 / env) ** 0.5, 0.5, 2.5), 15)
    act = np.abs(x) > 0.02
    rms = float(np.sqrt(np.mean(x[act] ** 2))) if act.any() else 1.0
    x = x * (target_rms / rms)
    x = np.tanh(x * 1.1) / 1.1                                           # limiteur doux
    fi, fo = int(0.01 * SR), int(0.04 * SR)
    x[:fi] *= np.linspace(0, 1, fi)
    x[-fo:] *= np.linspace(1, 0, fo)
    return x.astype(np.float32)


def build(lines, voice, total_dur, base_rate=1.08, pitch=1.0, gap=0.12, max_speedup=1.4, verbose=True):
    """Renvoie [(instant de départ, tableau mono 44,1 kHz)] pour les lignes de voix off d'une scène."""
    rates = [ln.get("rate", base_rate) for ln in lines]
    arrs = [_process(*_load(p)) for p in synth([(voice, r, pitch, ln["text"]) for r, ln in zip(rates, lines)])]
    out, t_prev = [], 0.0
    for i, ln in enumerate(lines):
        arr = arrs[i]
        d = len(arr) / SR
        start = max(ln["at"], t_prev + gap)
        lim = ln.get("end", total_dur - 0.1)
        if start + d > lim:
            f = min(max_speedup, d / max(0.5, lim - start))
            if f > 1.02:       # on réécrit la ligne plus vite pour qu'elle tienne dans son créneau
                rates[i] *= f
                arr = _process(*_load(synth([(voice, rates[i], pitch, ln["text"])])[0]))
                d = len(arr) / SR
        out.append((start, arr))
        t_prev = start + d
        if verbose:
            flag = "" if t_prev <= lim + 0.05 else "   <-- DÉPASSE le créneau (%.2f s)" % lim
            print("  [%s] %5.2f -> %5.2f s  (%.2f s, débit %.2f)  %s%s" % (voice, start, t_prev, d, rates[i], ln["text"], flag))
    return out
