# -*- coding: utf-8 -*-
"""Réglages communs à toutes les vidéos. Modifie ici puis relance build.py."""

# --- Contact affiché dans les vidéos -------------------------------------
PHONE_DISPLAY = "+225 01 60 67 42 17"
PHONE_DIGITS = "2250160674217"          # format international sans le +

# QR code principal : ouvre WhatsApp avec un message déjà écrit.
# (Le numéro doit avoir WhatsApp. Sinon remplace par TEL_URL dans components.py)
WHATSAPP_URL = f"https://wa.me/{PHONE_DIGITS}?text=Bonjour%2C%20je%20veux%20un%20devis"
# QR code secondaire : lance directement un appel.
TEL_URL = f"tel:+{PHONE_DIGITS}"

# --- Identité (facultatif) -----------------------------------------------
BRAND = ""                  # ex. "MonStudio"  -> affiché sur l'écran final si rempli
HANDLE = ""                 # ex. "@moncompte" -> affiché sur l'écran final si rempli
TAGLINE = "Développeur web & mobile"

# --- Logo ------------------------------------------------------------------
LOGO_PATH = "assets/logo.png"   # chemin relatif au dossier source ; "" pour désactiver le logo
LOGO_WATERMARK = True           # petit logo en coin pendant toute la vidéo (en plus de l'écran final)
