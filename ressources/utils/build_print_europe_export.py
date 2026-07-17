# -*- coding: utf-8 -*-
"""Prépare l'export des deux jeux de cartes "Fanny Pétanque World Tour" pour
impression professionnelle chez Print Europe (jeuxdecartes.printeurope.fr).

Rendu délégué à ressources/utils/card_render.py (profil "printeurope" : fond
perdu 2mm + zone tranquille 3mm autour du format fini, coins NON découpés
dans le fichier - c'est Print Europe qui s'en charge) - le même moteur que
l'éditeur web card_studio et les autres exports, pour éviter toute
divergence entre les différentes sorties.

Spécifications tirées de leur guide PAO officiel
(https://docs.printeurope.fr/PRINTEUROPE_GUIDE_PAO.pdf, section "Jeux de
cartes", p.17-32) :
  - Fichier PDF CMJN 300 dpi, 1 carte par page.
  - Fond perdu : au moins 2mm tout autour du format fini (63x88mm -> toile
    de 67x92mm).
  - Zone tranquille : marge de 3mm à l'intérieur du format fini - aucun
    texte/élément important dedans.
  - Coins arrondis (rayon 4mm) découpés par leurs soins : ne pas les
    matérialiser dans le fichier, juste laisser la zone libre d'éléments.
  - Dos identique pour tout le jeu (notre cas) -> structure du PDF :
    page 1 = dos, pages 2 à N+1 = les N rectos, dans l'ordre.

Usage : python3 ressources/utils/build_print_europe_export.py
Sortie : ressources/playing_cards/print_europe_export/deck_1.pdf,
         deck_2.pdf (+ LISEZ-MOI.txt commun).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from ressources.utils.card_render import (  # noqa: E402
    RANKS, SUITS, SUIT_COLORS, SUIT_SYMBOLS, portrait_path as _portrait_path, render_back, render_card,
)

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
OUT_DIR = f"{ROOT}/ressources/playing_cards/print_europe_export"
DPI = 300


def portrait_path(tier):
    pays, slug, _texte = WORLD_TOUR_COUNTRIES[tier]
    return _portrait_path(tier, slug), pays


def build_deck_pdf(tiers, out_path):
    cards = [(rank, suit) for suit in SUITS for rank in RANKS]  # 52
    joker_tiers = tiers[52:]
    assert len(joker_tiers) % 2 == 0 and len(joker_tiers) >= 2

    fronts = []
    for (rank, suit), tier in zip(cards, tiers[:52]):
        image_path, pays = portrait_path(tier)
        fronts.append(render_card("printeurope", image_path, pays, rank, SUIT_SYMBOLS[suit], SUIT_COLORS[suit]))

    for i, tier in enumerate(joker_tiers):
        is_red = i % 2 == 0
        color = SUIT_COLORS["hearts"] if is_red else SUIT_COLORS["clubs"]
        image_path, pays = portrait_path(tier)
        fronts.append(render_card("printeurope", image_path, pays, "JOKER", "", color, is_joker=True))

    back = render_back("printeurope")

    # Structure imposée par le guide PAO Print Europe pour un dos unique :
    # page 1 = dos, pages suivantes = les rectos dans l'ordre. Conversion
    # CMJN car leur export attendu est "Fichier PDF CMJN 300 dpi" - c'est une
    # conversion RVB->CMJN basique (pas de profil ICC) : demander une épreuve
    # numérique avant lancement de l'impression finale (cf. LISEZ-MOI.txt).
    pages = [back.convert("CMYK")] + [f.convert("CMYK") for f in fronts]
    pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=DPI)
    print(f"{out_path}  <-  1 dos + {len(fronts)} rectos ({len(pages)} pages)")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    all_tiers = list(range(112))
    deck_1_tiers = all_tiers[0:54]
    deck_2_tiers = all_tiers[54:112]

    build_deck_pdf(deck_1_tiers, f"{OUT_DIR}/deck_1.pdf")
    build_deck_pdf(deck_2_tiers, f"{OUT_DIR}/deck_2.pdf")

    readme = """Fanny Pétanque World Tour — Export pour Print Europe
(jeuxdecartes.printeurope.fr)

Fichiers : deck_1.pdf (54 cartes), deck_2.pdf (58 cartes).

Structure de chaque PDF (conforme au guide PAO Print Europe, "Option 1 :
dos identique pour toutes les cartes") : page 1 = dos, pages suivantes =
les rectos dans l'ordre A,2,3...K de Coeur, Carreau, Trèfle, Pique puis
les Jokers.

Format : CMJN 300 dpi, 1 carte par page, page = format fini (63x88mm) +
2mm de fond perdu de chaque côté (toile 67x92mm). Marge de sécurité de 3mm
respectée pour tous les textes/badges. Coins arrondis (rayon 4mm) non
matérialisés dans le fichier : c'est Print Europe qui les découpe.

À faire côté site : jeuxdecartes.printeurope.fr -> configurer un jeu de
54 (ou 58) cartes au format Poker 63x88mm, dos identique pour tout le jeu,
uploader le PDF correspondant.

Point d'attention : la conversion RVB->CMJN de ce fichier est une
conversion basique (sans profil ICC calibré). Avant un tirage en quantité,
il est recommandé de commander une épreuve numérique ou papier (proposée
par Print Europe) pour valider les couleurs.
"""
    with open(f"{OUT_DIR}/LISEZ-MOI.txt", "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
