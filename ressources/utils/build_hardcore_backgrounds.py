#!/usr/bin/env python3
"""Génère la variante Hardcore des fonds "World Tour" avec trou webcam.

main.py (3 cibles en ligne) et main_hardcore.py (7 cibles en étoile de
David) partagent les mêmes décors par pays
(assets/Images/BackgroundWorldTour/{i:03d}_{slug}.jpg), mais pas la même
variante .png à trou webcam : sur le chassis étoile, la position haut-centre
héritée de main.py fait chevaucher la cible U par la caméra/l'anneau coloré
(cf. main_hardcore.py, camring déplacé en bas-droite). Ce script recopie
donc chaque .jpg en découpant un trou elliptique transparent à la NOUVELLE
position (bas-droite), dans un dossier séparé : les .jpg (sans webcam)
restent partagés, seule cette variante .png diffère entre les deux jeux.

Géométrie du trou : ellipse de mêmes rayons que l'originale de
BackgroundWorldTour/*.png (rx=106, ry=189 à la résolution de référence
1920x1080, mesurés par échantillonnage sur 001_allemagne.png), recentrée
sur la nouvelle position de camring dans main_hardcore.py (marge droite
40px, marge basse 90px -> centre (1751, 792)).

Usage :
    python3 build_hardcore_backgrounds.py [--force] [--limit N] [--only I,I,...]
"""
import argparse
import os

from PIL import Image, ImageDraw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGES_DIR = os.path.join(PROJECT_ROOT, "assets", "Images")
SRC_DIR = os.path.join(IMAGES_DIR, "BackgroundWorldTour")
OUT_DIR = os.path.join(IMAGES_DIR, "BackgroundWorldTourHardcore")

CANVAS_W, CANVAS_H = 1920, 1080

# Reprend exactement le calcul de camring.rect dans main_hardcore.py.
RING_WIDTH, RING_HEIGHT = 258, 395
RING_RIGHT_MARGIN, RING_BOTTOM_MARGIN = 40, 90
RING_RIGHT = CANVAS_W - RING_RIGHT_MARGIN
RING_BOTTOM = CANVAS_H - RING_BOTTOM_MARGIN
RING_LEFT = RING_RIGHT - RING_WIDTH
RING_TOP = RING_BOTTOM - RING_HEIGHT

HOLE_CENTER = ((RING_LEFT + RING_RIGHT) // 2, (RING_TOP + RING_BOTTOM) // 2)
HOLE_RX, HOLE_RY = 106, 189


def cut_hole(jpg_path, out_path):
    img = Image.open(jpg_path).convert("RGBA")
    if img.size != (CANVAS_W, CANVAS_H):
        img = img.resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    mask = Image.new("L", (CANVAS_W, CANVAS_H), 255)
    cx, cy = HOLE_CENTER
    ImageDraw.Draw(mask).ellipse(
        (cx - HOLE_RX, cy - HOLE_RY, cx + HOLE_RX, cy + HOLE_RY), fill=0
    )
    img.putalpha(mask)
    img.save(out_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="Regénérer même les PNG déjà présents")
    parser.add_argument("--limit", type=int, default=None, help="Limiter aux N premiers fichiers (test)")
    parser.add_argument("--only", type=str, default=None, help="Liste d'index séparés par des virgules (ex: 1,13,112)")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    jpgs = sorted(f for f in os.listdir(SRC_DIR) if f.endswith(".jpg"))
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        jpgs = [f for f in jpgs if int(f.split("_", 1)[0]) in wanted]
    elif args.limit:
        jpgs = jpgs[: args.limit]

    done = skipped = 0
    for fname in jpgs:
        out_name = fname[:-4] + ".png"
        out_path = os.path.join(OUT_DIR, out_name)
        if os.path.isfile(out_path) and not args.force:
            skipped += 1
            continue
        cut_hole(os.path.join(SRC_DIR, fname), out_path)
        done += 1
        print(f"{fname} -> {out_name}")

    print(f"\nTerminé : {done} créé(s), {skipped} déjà présent(s) (ignoré(s)).")
    print(f"Dossier : {OUT_DIR}")


if __name__ == "__main__":
    main()
