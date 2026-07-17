# -*- coding: utf-8 -*-
"""Génère deux jeux de 54 cartes (52 + 2 jokers) façon souvenir/merchandise
"Fanny Pétanque World Tour", à partir des 112 portraits de Fanny en tenue
traditionnelle (assets/Images/FannyWorldTour/). Chaque carte affiche en petit
le nom du pays du portrait utilisé.

Rendu délégué à ressources/utils/card_render.py (profil "home" : coins
arrondis découpés dans le fichier, cf. build_playing_cards_pdf.py pour
l'impression maison à la découpeuse/ciseaux) - le même moteur que l'éditeur
web card_studio et les exports MPC/Print Europe, pour éviter toute
divergence entre les différentes sorties.

Répartition : les 112 pays sont pris dans l'ordre du tour du monde (Europe ->
Afrique -> Asie -> Amériques/Océanie, cf. WORLD_TOUR_COUNTRIES) ; les 54
premiers vont dans le jeu 1, les 54 suivants dans le jeu 2. Les 4 derniers
pays du tour (Nouvelle-Zélande, Tahiti, Vanuatu, Wallis-et-Futuna) ne sont
utilisés dans aucun des deux jeux à 54 cartes.

Usage : python3 ressources/utils/build_world_tour_playing_cards.py
Sortie : ressources/playing_cards/deck_1/*.png, ressources/playing_cards/deck_2/*.png
         + une planche de contact par jeu pour relecture rapide.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from ressources.utils.card_render import (  # noqa: E402
    RANKS, SUITS, SUIT_COLORS, SUIT_SYMBOLS, portrait_path as _portrait_path, render_back, render_card,
)

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
OUT_DIR = f"{ROOT}/ressources/playing_cards"


def portrait_path(tier):
    pays, slug, _texte = WORLD_TOUR_COUNTRIES[tier]
    return _portrait_path(tier, slug), pays


def build_contact_sheet(card_paths, out_path, cols=9):
    thumb_w, thumb_h = 150, 210
    rows = -(-len(card_paths) // cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (30, 26, 20))
    for i, p in enumerate(card_paths):
        img = Image.open(p).convert("RGBA")
        thumb = img.resize((thumb_w - 4, thumb_h - 4), Image.LANCZOS)
        x = (i % cols) * thumb_w + 2
        y = (i // cols) * thumb_h + 2
        sheet.paste(thumb, (x, y), thumb)
    sheet.save(out_path)


def build_deck(tiers, out_dir, volume_label):
    """tiers = 52 pays pour les cartes A..K des 4 couleurs, suivis d'un
    nombre pair de pays supplémentaires pour les jokers (2 au minimum :
    joker-red/joker-black ; au-delà, joker-red-2/joker-black-2, etc.) - permet
    d'écouler tous les pays du tour même quand ça ne tombe pas rond sur 54."""
    os.makedirs(out_dir, exist_ok=True)
    cards = [(rank, suit) for suit in SUITS for rank in RANKS]  # 52
    joker_tiers = tiers[52:]
    assert len(tiers) == 52 + len(joker_tiers) and len(joker_tiers) % 2 == 0 and len(joker_tiers) >= 2

    generated = []
    for (rank, suit), tier in zip(cards, tiers[:52]):
        image_path, pays = portrait_path(tier)
        color = SUIT_COLORS[suit]
        symbol = SUIT_SYMBOLS[suit]
        card_img = render_card("home", image_path, pays, rank, symbol, color)
        out_path = f"{out_dir}/{rank}-{suit}.png"
        card_img.save(out_path)
        generated.append(out_path)
        print(f"{out_path}  <-  {pays}")

    for i, tier in enumerate(joker_tiers):
        is_red = i % 2 == 0
        color = SUIT_COLORS["hearts"] if is_red else SUIT_COLORS["clubs"]
        suffix = "" if i < 2 else f"-{i // 2 + 1}"
        label = "red" if is_red else "black"
        image_path, pays = portrait_path(tier)
        joker_img = render_card("home", image_path, pays, "JOKER", "", color, is_joker=True)
        out_path = f"{out_dir}/joker-{label}{suffix}.png"
        joker_img.save(out_path)
        generated.append(out_path)
        print(f"{out_path}  <-  {pays}")

    back_img = render_back("home", subtitle=f"WORLD TOUR — {volume_label}")
    back_img.save(f"{out_dir}/back.png")
    print(f"{out_dir}/back.png  <-  (généré, motif géométrique)")

    build_contact_sheet(generated, f"{out_dir}/_planche_apercu.png")
    print(f"{out_dir}/_planche_apercu.png  <-  (planche de contact, {len(generated)} cartes)")


def main():
    all_tiers = list(range(112))
    deck_1_tiers = all_tiers[0:54]   # 52 cartes + 2 jokers
    deck_2_tiers = all_tiers[54:112]  # 52 cartes + 6 jokers (inclut les 4 pays restants)

    build_deck(deck_1_tiers, f"{OUT_DIR}/deck_1", "Vol. 1")
    build_deck(deck_2_tiers, f"{OUT_DIR}/deck_2", "Vol. 2")

    print(f"\n{len(deck_1_tiers) + len(deck_2_tiers)} portraits utilisés sur 112 "
          f"(deck 1 : {len(deck_1_tiers)} cartes, deck 2 : {len(deck_2_tiers)} cartes).")


if __name__ == "__main__":
    main()
