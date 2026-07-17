# -*- coding: utf-8 -*-
"""Fabrique des sprites TEMPORAIRES pour un pays qui n'a pas encore ses
vrais portraits/fonds (générés à la main par l'utilisateur, hors dépôt -
aucun outil de génération d'image disponible ici). Copie les fichiers
existants de la France (assets/*/013_france.*) vers le tier demandé, en
tamponnant un filigrane "TODO" bien visible en diagonale, pour qu'il soit
impossible de confondre un vrai portrait avec un placeholder.

Concerne les 4 fichiers par pays qui n'ont pas de fallback silencieux côté
jeu (contrairement à la voix/l'hymne, cf. Scripts/Sprites.py) :
  - assets/Images/FannyWorldTour/{tier}_{slug}.png (portrait)
  - assets/Images/BackgroundWorldTour/{tier}_{slug}.jpg (fond sans trou webcam)
  - assets/Images/BackgroundWorldTour/{tier}_{slug}.png (fond trou webcam, main.py)
  - assets/Images/BackgroundWorldTourHardcore/{tier}_{slug}.png (fond trou webcam, Hardcore)

Usage :
    python3 ressources/utils/build_placeholder_assets.py bresil israel liban
    python3 ressources/utils/build_placeholder_assets.py 112 113 114
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
sys.path.insert(0, ROOT)
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402

SOURCE_TIER = 12  # France
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

ASSET_SPECS = [
    ("assets/Images/FannyWorldTour", "png"),
    ("assets/Images/BackgroundWorldTour", "jpg"),
    ("assets/Images/BackgroundWorldTour", "png"),
    ("assets/Images/BackgroundWorldTourHardcore", "png"),
]


def resolve_tier(arg):
    if arg.isdigit():
        return int(arg)
    needle = arg.strip().lower()
    for tier, (pays, slug, _texte) in enumerate(WORLD_TOUR_COUNTRIES):
        if needle in (pays.lower(), slug.lower()):
            return tier
    raise SystemExit(f"Pays introuvable : {arg!r}")


def stamp_todo(img):
    """Filigrane "TODO" répété en diagonale, rouge vif semi-transparent,
    assez dense pour être visible sur n'importe quelle zone de l'image."""
    img = img.convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(28, w // 10)
    font = ImageFont.truetype(FONT_BOLD, font_size)
    text = "TODO"
    text_w = draw.textlength(text, font=font)
    step_x = int(text_w * 1.8)
    step_y = font_size * 3

    for y in range(-step_y, h + step_y, step_y):
        offset = (y // step_y % 2) * (step_x // 2)
        for x in range(-step_x, w + step_x, step_x):
            draw.text((x + offset, y), text, font=font, fill=(220, 30, 20, 150))

    rotated = overlay.rotate(28, resample=Image.BICUBIC)
    rw, rh = rotated.size
    crop_box = ((rw - w) // 2, (rh - h) // 2, (rw - w) // 2 + w, (rh - h) // 2 + h)
    rotated = rotated.crop(crop_box)

    band_h = max(60, h // 12)
    band = Image.new("RGBA", (w, band_h), (220, 30, 20, 210))
    band_draw = ImageDraw.Draw(band)
    banner_text = "PLACEHOLDER TEMPORAIRE - À REMPLACER"
    banner_size = int(band_h * 0.55)
    while banner_size > 10:
        banner_font = ImageFont.truetype(FONT_BOLD, banner_size)
        if band_draw.textlength(banner_text, font=banner_font) <= w * 0.92:
            break
        banner_size -= 2
    banner_w = band_draw.textlength(banner_text, font=banner_font)
    band_draw.text(((w - banner_w) / 2, (band_h - banner_size) / 2), banner_text, font=banner_font, fill=(255, 255, 255, 255))

    combined = Image.alpha_composite(img, rotated)
    combined.alpha_composite(band, (0, (h - band_h) // 2))
    return combined


def build_placeholders_for(tier):
    pays, slug, _texte = WORLD_TOUR_COUNTRIES[tier]
    src_pays, src_slug, _t = WORLD_TOUR_COUNTRIES[SOURCE_TIER]
    generated = []
    for folder, ext in ASSET_SPECS:
        src_path = f"{ROOT}/{folder}/{SOURCE_TIER + 1:03d}_{src_slug}.{ext}"
        dst_path = f"{ROOT}/{folder}/{tier + 1:03d}_{slug}.{ext}"
        if not os.path.isfile(src_path):
            print(f"  (source manquante, ignorée : {src_path})")
            continue
        img = Image.open(src_path)
        stamped = stamp_todo(img)
        if ext == "jpg":
            stamped = stamped.convert("RGB")
            stamped.save(dst_path, quality=90)
        else:
            stamped.save(dst_path)
        generated.append(dst_path)
        print(f"{dst_path}  <-  {src_path} (+ filigrane TODO)")
    return generated


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        tier = resolve_tier(arg)
        pays = WORLD_TOUR_COUNTRIES[tier][0]
        print(f"=== {pays} (tier {tier}) ===")
        build_placeholders_for(tier)


if __name__ == "__main__":
    main()
