# -*- coding: utf-8 -*-
"""Génère les vidéos TikTok (1080x1920, 30 fps, MP4 H.264 + AAC).

Utilisation (depuis le dossier du projet) :
    python source/build.py render            -> rend toutes les vidéos dans ./videos
    python source/build.py render 1 4 7      -> rend seulement les vidéos 1, 4 et 7
    python source/build.py preview 3 out.png -> planche-contact de la vidéo 3 (vérification visuelle)
    python source/build.py frame 3 5.2 f.png -> image pleine résolution de la vidéo 3 à t=5.2 s
    python source/build.py covers            -> une image de couverture par vidéo (videos/couvertures)
    python source/build.py captions          -> légendes + hashtags TikTok (videos/legendes_tiktok.txt)
    python source/build.py voice 7 hortense paul -> variantes avec voix off de la vidéo 7 (voix Windows locales)
Les textes, le numéro et le QR code se règlent dans source/config.py.
"""
import concurrent.futures as cf
import importlib
import os
import subprocess
import sys
import tempfile
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "videos")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def load_scenes():
    scenes = []
    for mod in ("scenes_a", "scenes_b", "scenes_c", "scenes_d", "scenes_e", "scenes_f"):
        try:
            m = importlib.import_module(mod)
        except ModuleNotFoundError as e:
            if e.name != mod:
                raise
            continue
        scenes += m.SCENES
    from brand import watermark
    out = []
    for s in sorted(scenes, key=lambda s: s["id"]):
        s = dict(s)       # copie : le filigrane du logo est ajouté sur chaque image, sans toucher aux scènes
        s["frame"] = (lambda t, raw=s["frame"], sc=s: watermark(raw(t), t, sc))
        if s.get("voice_variant"):      # montage légèrement différent pour la version avec voix off
            vv = dict(s["voice_variant"])
            merged = {**s, **vv}
            vv["frame"] = (lambda t, raw=vv["frame"], sc=merged: watermark(raw(t), t, sc))
            s["voice_variant"] = vv
        out.append(s)
    return out


def get(sid):
    for s in load_scenes():
        if s["id"] == sid:
            return s
    raise SystemExit(f"scène {sid} introuvable")


def preview(sid, out, times=None, cols=6):
    from PIL import Image
    s = get(sid)
    d = s["dur"]
    if times is None:
        n = 12
        times = [min(d - 0.05, d * (i + 0.5) / n) for i in range(n)]
    tw, th = 300, 533
    rows = (len(times) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (40, 40, 40))
    tot = 0.0
    for i, t in enumerate(times):
        t0 = time.time()
        img = s["frame"](t)
        tot += time.time() - t0
        sheet.paste(img.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    sheet.save(out)
    print(f"video {sid}: {len(times)} images, {tot / len(times) * 1000:.0f} ms/image -> {out}")


def render_one(sid, voix=None):
    """Rend une vidéo. voix = nom d'une voix Windows (hortense, julie, paul) pour la variante avec voix off."""
    from audio import render_audio
    from engine import FPS, VideoWriter
    s = get(sid)
    if voix and s.get("voice_variant"):
        s = {**s, **s["voice_variant"]}
    os.makedirs(OUT, exist_ok=True)
    vlines, suffix = (), ""
    if voix:
        import voice as vo
        if not s.get("voice"):
            raise SystemExit(f"la vidéo {sid} n'a pas de texte de voix off (clé voice dans sa scène)")
        vlines = vo.build(s["voice"], voix.capitalize(), s["dur"])
        suffix = "_voix-off-" + vo.LABELS.get(voix.lower(), voix.lower())
    out = os.path.join(OUT, f"{s['id']:02d}_{s['slug']}{suffix}.mp4")
    t0 = time.time()
    wav = os.path.join(tempfile.gettempdir(), f"promo_{sid}_{os.getpid()}.wav")
    render_audio(wav, s["dur"], s.get("music"), s.get("sfx", []), music_vol=s.get("music_vol", 1.0), voice=vlines)
    w = VideoWriter(out, audio=wav)
    n = int(round(s["dur"] * FPS))
    try:
        for i in range(n):
            w.write(s["frame"](i / FPS))
    except Exception:
        traceback.print_exc()
        w.close()
        raise
    rc = w.close()
    try:
        os.remove(wav)
    except OSError:
        pass
    return sid, out, time.time() - t0, rc


BASE_TAGS = "#siteweb #creationsiteweb #developpeur #webdesign #entrepreneur #cotedivoire #business #devis"
EXTRA_TAGS = {1: "#whatsappbusiness #vendreenligne", 2: "#code #programmation", 3: "#avantapres #transformation", 4: "#devisgratuit #prix",
              5: "#astuce #conseil", 6: "#ecommerce #ventesenligne", 7: "#applicationmobile #app", 8: "#projetweb #etapes",
              9: "#pov #humour", 10: "#services #freelance", 11: "#qrcode #whatsapp", 12: "#vraioufaux #ideesrecues"}


def write_captions():
    import config
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "legendes_tiktok.txt")
    lines = ["LÉGENDES TIKTOK (à copier-coller au moment de publier)", "",
             f"Contact affiché dans les vidéos : {config.PHONE_DISPLAY}",
             "Astuce : mets ce lien dans ta bio TikTok, les clients t'écrivent en 1 clic :",
             config.WHATSAPP_URL,
             "Astuce : à la publication, choisis comme couverture une image où le texte d'accroche est visible.", ""]
    for s in load_scenes():
        lines += [f"--- {s['id']:02d} · {s['slug']}.mp4 ---", s["caption"], f"{BASE_TAGS} {EXTRA_TAGS.get(s['id'], '')}".strip(), ""]
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))
    print("légendes écrites :", path)


# instant de chaque vidéo où l'accroche est bien visible (sert de couverture TikTok et d'image d'aperçu)
COVER_TIMES = {1: 2.0, 2: 12.0, 3: 10.2, 4: 9.4, 5: 13.3, 6: 6.4, 7: 11.3, 8: 9.3, 9: 10.9, 10: 5.6, 11: 3.4, 12: 4.4}


def write_covers():
    folder = os.path.join(OUT, "couvertures")
    os.makedirs(folder, exist_ok=True)
    for s in load_scenes():
        img = s["frame"](COVER_TIMES.get(s["id"], s["dur"] * 0.4))
        img.save(os.path.join(folder, f"{s['id']:02d}.jpg"), quality=90, optimize=True)
    print("couvertures écrites dans", folder)


def write_voice_scripts():
    path = os.path.join(OUT, "textes_voix_off.txt")
    lines = ["TEXTES DES VOIX OFF (voix de femme : Microsoft Hortense, installée sur ton ordinateur)",
             "Chaque phrase est dite à l'instant indiqué (en secondes).",
             "Pour changer un texte : modifie la liste VOICExx dans source/scenes_*.py, puis relance :",
             "    python source/build.py voice all hortense --force", ""]
    for s in load_scenes():
        if not s.get("voice"):
            continue
        v = {**s, **s.get("voice_variant", {})}
        lines.append(f"--- Vidéo {s['id']:02d} · {s['slug']} ({v['dur']:.1f} s) ---")
        lines += [f"  {ln['at']:5.2f} s   {ln['text']}" for ln in v["voice"]]
        lines.append("")
    with open(path, "w", encoding="utf-8-sig") as f:      # avec signature : le Bloc-notes affiche bien les accents
        f.write("\n".join(lines))
    print("textes écrits :", path)


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    if a[0] == "captions":
        write_captions()
        return
    if a[0] == "covers":
        write_covers()
        return
    if a[0] == "scripts":
        write_voice_scripts()
        return
    if a[0] == "voice":                      # voice 7 hortense paul  |  voice 1,2,3 hortense  |  voice all hortense [--force]
        import voice as vo
        scenes = {s["id"]: s for s in load_scenes()}
        ids = [i for i, s in scenes.items() if s.get("voice")] if a[1] == "all" else [int(x) for x in a[1].split(",")]
        force = "--force" in a
        voices = [v for v in a[2:] if not v.startswith("--")] or ["hortense", "paul"]
        tasks = []
        for i in ids:
            for v in voices:
                outp = os.path.join(OUT, f"{i:02d}_{scenes[i]['slug']}_voix-off-{vo.LABELS.get(v.lower(), v.lower())}.mp4")
                if os.path.exists(outp) and not force:
                    print("  (déjà présent, ignoré)", os.path.basename(outp))
                    continue
                tasks.append((i, v))
        if not tasks:
            return
        workers = max(1, min(len(tasks), (os.cpu_count() or 4) // 2))
        print(f"rendu de {len(tasks)} vidéo(s) avec voix off, {workers} processus...")
        with cf.ProcessPoolExecutor(max_workers=workers) as ex:
            for f in [ex.submit(render_one, i, v) for i, v in tasks]:
                _, out, dt, rc = f.result()
                print(f"  [{'OK' if rc == 0 else 'ERREUR'}] {os.path.basename(out)}  ({dt:.0f}s)", flush=True)
        return
    if a[0] == "preview":
        sid = int(a[1])
        out = a[2]
        times = [float(x) for x in a[3].split(",")] if len(a) > 3 else None
        preview(sid, out, times)
    elif a[0] == "frame":
        s = get(int(a[1]))
        s["frame"](float(a[2])).save(a[3])
    elif a[0] == "render":
        ids = [int(x) for x in a[1:]] or [s["id"] for s in load_scenes()]
        workers = max(1, min(len(ids), (os.cpu_count() or 4) // 2))
        print(f"rendu de {len(ids)} vidéo(s) avec {workers} processus...")
        with cf.ProcessPoolExecutor(max_workers=workers) as ex:
            for sid, out, dt, rc in ex.map(render_one, ids):
                print(f"  [{'OK' if rc == 0 else 'ERREUR'}] {os.path.basename(out)}  ({dt:.0f}s)", flush=True)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
