# Vidéos promo TikTok : création de sites web

12 vidéos verticales (1080x1920) pour promouvoir la création de sites web et d'applications,
avec QR code vers WhatsApp. Chaque vidéo existe aussi en version avec voix off.

| Dossier | Contenu |
|---|---|
| `videos/` | vidéos finales, couvertures, légendes TikTok, textes des voix off, page d'aperçu |
| `source/` | scripts Python qui génèrent les vidéos |

## Régénérer les vidéos

```bash
pip install -r source/requirements.txt
python source/build.py render
```

Les textes, le numéro et le QR code se règlent dans `source/config.py`.
Les autres commandes (couvertures, légendes, voix off) sont décrites en haut de `source/build.py`.
