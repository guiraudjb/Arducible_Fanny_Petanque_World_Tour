# -*- coding: utf-8 -*-
"""Génère la liste de mots valides du Scrabble Fanny (mini-jeu du Casino)
à partir du dictionnaire système français (paquet Debian "wfrench",
/usr/share/dict/french - liste de mots réels, pas la liste officielle
ODS du Scrabble : quelques abréviations résiduelles peuvent donc se
glisser dans les mots de 2-3 lettres, c'est un compromis assumé pour un
mini-jeu de casino, pas une résolution disponible en compétition).

Chaque mot est replié en majuscules SANS accent (ce qui correspond aux
lettres réellement gravées sur les jetons - "ÉTÉ" se pose avec les
lettres E, T, E), dédupliqué, et filtré :
  - longueur 2 à 7 (le chevalet ne contient que 7 lettres, inutile de
    garder des mots plus longs qu'il est impossible de poser)
  - au moins une voyelle (A E I O U Y) pour écarter la plupart des
    abréviations à consonnes seules (KM, CC, DG...) présentes dans le
    dictionnaire système

Sortie : assets/scrabble/mots.txt (un mot par ligne, trié) - lu tel
quel par src/games/scrabble/engine.js via fetch + split('\\n'), donc
pas de commentaire ni de ligne vide dans ce fichier.

Usage : python3 "ressources/card game/tools/generate_scrabble_words.py"
(aucune dépendance externe, contrairement à generate_dealer_audio.py).
"""
import os
import re
import unicodedata

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CARD_GAME_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))

SOURCE_DICT = "/usr/share/dict/french"
OUTPUT_PATH = os.path.join(_CARD_GAME_ROOT, "assets", "scrabble", "mots.txt")

VALID_SOURCE_RE = re.compile(r"^[a-zàâäéèêëîïôöùûüçœæÿ]+$")
ASCII_LETTERS_RE = re.compile(r"^[A-Z]+$")
VOWEL_RE = re.compile(r"[AEIOUY]")


def normalize(word):
    folded = word.replace("œ", "oe").replace("æ", "ae")
    decomposed = unicodedata.normalize("NFKD", folded)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.upper()


def main():
    words = set()
    with open(SOURCE_DICT, encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or not VALID_SOURCE_RE.match(raw):
                continue
            word = normalize(raw)
            if not (2 <= len(word) <= 7):
                continue
            if not ASCII_LETTERS_RE.match(word):
                continue
            if not VOWEL_RE.search(word):
                continue
            words.add(word)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(words)))

    print(f"{len(words)} mots écrits dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
