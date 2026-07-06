#!/usr/bin/env python3
"""Régénère la version ANGLAISE du Fanny World Tour : les 112 cartes
postales puis le diaporama vidéo, avec exactement les mêmes caractéristiques
que la version française (mise en page, décors, cartes, portraits de Fanny,
musique, écran-titre/fin, durée calée sur la musique) — seul le texte
affiché (nom du pays + réplique) change.

Ce script ne fait que piloter, avec les bons paramètres, les deux scripts
génériques déjà utilisés pour la version française :
  - build_world_tour_postcards.py  (--pays-names / --speach / --out-dir)
  - build_world_tour_slideshow.py  (--postcards-dir / --out)
Les noms de pays et répliques anglais viennent de "pays_index_en.txt" et
"speach_en.txt" (mêmes index/ordre que les fichiers français ; les noms de
fichiers d'assets, eux, restent toujours dérivés du "pays_index.txt"
français, cf. build_world_tour_postcards.py).

Usage :
    python3 build_world_tour_english.py [--force]
"""
import argparse
import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TOUR_DIR = os.path.join(PROJECT_ROOT, "fanny wold tour")

PAYS_NAMES_EN = os.path.join(TOUR_DIR, "pays_index_en.txt")
SPEACH_EN = os.path.join(TOUR_DIR, "speach_en.txt")
POSTCARDS_EN_DIR = os.path.join(TOUR_DIR, "postcards_en")
VIDEO_EN_OUT = os.path.join(TOUR_DIR, "fanny_world_tour_slideshow_en.mp4")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="Regénérer même les cartes/la vidéo déjà présentes")
    args = parser.parse_args()

    postcards_cmd = [
        "python3", os.path.join(PROJECT_ROOT, "build_world_tour_postcards.py"),
        "--pays-names", PAYS_NAMES_EN,
        "--speach", SPEACH_EN,
        "--out-dir", POSTCARDS_EN_DIR,
    ]
    if args.force:
        postcards_cmd.append("--force")
    subprocess.run(postcards_cmd, check=True)

    slideshow_cmd = [
        "python3", os.path.join(PROJECT_ROOT, "build_world_tour_slideshow.py"),
        "--postcards-dir", POSTCARDS_EN_DIR,
        "--out", VIDEO_EN_OUT,
    ]
    subprocess.run(slideshow_cmd, check=True)

    print(f"\nVersion anglaise terminée : {POSTCARDS_EN_DIR} + {VIDEO_EN_OUT}")


if __name__ == "__main__":
    main()
