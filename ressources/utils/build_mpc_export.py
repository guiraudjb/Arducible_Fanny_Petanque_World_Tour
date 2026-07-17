# -*- coding: utf-8 -*-
"""Prépare l'export des deux jeux de cartes "Fanny Pétanque World Tour" pour
impression professionnelle chez MakePlayingCards.com (produit "Custom Game
Cards 63 x 88mm").

Rendu délégué à ressources/utils/card_render.py (profil "mpc" : toile pleine
page avec fond perdu 1/8" + marge de sécurité 1/8", coins NON découpés dans
le fichier - c'est MakePlayingCards qui s'en charge à partir d'un fichier
plein cadre) - le même moteur que l'éditeur web card_studio et les autres
exports, pour éviter toute divergence entre les différentes sorties.

Usage : python3 ressources/utils/build_mpc_export.py
Sortie : ressources/playing_cards/mpc_export/deck_1/ et deck_2/
         (fronts/*.png numérotés dans l'ordre d'upload, back.png, deck_X.zip,
         LISEZ-MOI.txt avec la marche à suivre côté site MPC).
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from ressources.utils.card_render import (  # noqa: E402
    RANKS, SUITS, SUIT_COLORS, SUIT_SYMBOLS, portrait_path as _portrait_path, render_back, render_card,
)

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
OUT_DIR = f"{ROOT}/ressources/playing_cards/mpc_export"
DPI = 300


def portrait_path(tier):
    pays, slug, _texte = WORLD_TOUR_COUNTRIES[tier]
    return _portrait_path(tier, slug), pays


def build_deck(tiers, out_dir, deck_label):
    fronts_dir = f"{out_dir}/fronts"
    os.makedirs(fronts_dir, exist_ok=True)
    cards = [(rank, suit) for suit in SUITS for rank in RANKS]  # 52
    joker_tiers = tiers[52:]
    assert len(joker_tiers) % 2 == 0 and len(joker_tiers) >= 2

    seq = 1
    front_files = []
    for (rank, suit), tier in zip(cards, tiers[:52]):
        image_path, pays = portrait_path(tier)
        card_img = render_card("mpc", image_path, pays, rank, SUIT_SYMBOLS[suit], SUIT_COLORS[suit])
        out_path = f"{fronts_dir}/{seq:02d}_{rank}-{suit}.png"
        card_img.save(out_path, dpi=(DPI, DPI))
        front_files.append(out_path)
        seq += 1

    for i, tier in enumerate(joker_tiers):
        is_red = i % 2 == 0
        color = SUIT_COLORS["hearts"] if is_red else SUIT_COLORS["clubs"]
        image_path, pays = portrait_path(tier)
        card_img = render_card("mpc", image_path, pays, "JOKER", "", color, is_joker=True)
        out_path = f"{fronts_dir}/{seq:02d}_joker-{'red' if is_red else 'black'}.png"
        card_img.save(out_path, dpi=(DPI, DPI))
        front_files.append(out_path)
        seq += 1

    back_img = render_back("mpc")
    back_path = f"{out_dir}/back.png"
    back_img.save(back_path, dpi=(DPI, DPI))

    zip_path = f"{out_dir}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in front_files:
            zf.write(f, arcname=f"fronts/{os.path.basename(f)}")
        zf.write(back_path, arcname="back.png")

    readme = f"""Fanny Pétanque World Tour — {deck_label}
Export pour MakePlayingCards.com

1. Aller sur makeplayingcards.com -> Design & Print -> Game / Custom Cards
   -> choisir le produit "Custom Game Cards (63 x 88mm)".
2. Quantité : {len(front_files)} cartes uniques, 1 exemplaire de chaque (1 jeu).
3. Verso ("Card Back") : choisir l'option "same image for all cards" /
   "one card back for the whole deck" et uploader back.png.
4. Recto ("Card Front") : uploader les {len(front_files)} fichiers du
   dossier fronts/ EN GARDANT L'ORDRE NUMÉRIQUE du préfixe (01_, 02_, ...) -
   c'est l'ordre A,2,3...K de Coeur, Carreau, Trèfle, Pique puis les Jokers.
5. Les fichiers sont déjà au bon format (fond perdu + marge de sécurité
   inclus, 300 dpi) : ne pas les recadrer ni les redimensionner sur le site.

Fichiers : {len(front_files)} images dans fronts/ + back.png (verso unique).
Tout est aussi disponible pré-zippé : {os.path.basename(zip_path)}
"""
    with open(f"{out_dir}/LISEZ-MOI.txt", "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"{out_dir} : {len(front_files)} rectos + 1 verso -> {zip_path}")


def main():
    all_tiers = list(range(112))
    deck_1_tiers = all_tiers[0:54]
    deck_2_tiers = all_tiers[54:112]

    build_deck(deck_1_tiers, f"{OUT_DIR}/deck_1", "Volume 1 (54 cartes)")
    build_deck(deck_2_tiers, f"{OUT_DIR}/deck_2", "Volume 2 (58 cartes)")


if __name__ == "__main__":
    main()
