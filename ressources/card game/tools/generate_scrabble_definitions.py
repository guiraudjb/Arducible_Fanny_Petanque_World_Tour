#!/usr/bin/env python3
"""Construit assets/scrabble/definitions.csv (mot,définition) à partir du
dictionnaire français de kaikki.org (extraction du Wiktionnaire français,
licence CC BY-SA / GFDL comme le Wiktionnaire lui-même).

Source : https://kaikki.org/frwiktionary/Fran%C3%A7ais/kaikki.org-dictionary-Fran%C3%A7ais.jsonl
(~2,65M sens, un objet JSON par ligne). Le Scrabble français se joue sans
accents (les lettres du tirage n'en portent pas) : mots.txt est donc tout en
majuscules sans accents, alors que le Wiktionnaire liste les mots avec leurs
accents habituels - la correspondance se fait en normalisant les deux côtés
(majuscules + accents retirés) avant comparaison.

Usage:
    python3 tools/generate_scrabble_definitions.py <chemin_vers_jsonl_téléchargé>

Sortie: assets/scrabble/definitions.csv - une ligne par mot de mots.txt qui a
trouvé au moins une définition dans le Wiktionnaire (le premier sens
rencontré est gardé, pas de fusion de plusieurs sens : suffisant pour une
infobulle de jeu, pas pour une encyclopédie). Les mots sans correspondance
ne sont pas dans le fichier - le jeu doit prévoir un message "définition non
disponible" pour ce cas plutôt que de dépendre d'une entrée pour chaque mot.
"""
import csv
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS_PATH = ROOT / "assets" / "scrabble" / "mots.txt"
OUT_PATH = ROOT / "assets" / "scrabble" / "definitions.csv"


def normalize(word):
    """Majuscules + accents retirés, pour faire correspondre le Wiktionnaire
    (accentué) aux mots du tirage Scrabble (jamais accentués)."""
    decomposed = unicodedata.normalize("NFD", word)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return stripped.upper()


def clean_gloss(gloss):
    return " ".join(gloss.split())


def main():
    if len(sys.argv) != 2:
        print("Usage: generate_scrabble_definitions.py <chemin_vers_jsonl>")
        sys.exit(1)
    jsonl_path = Path(sys.argv[1])

    target_words = {
        normalize(w): w
        for w in WORDS_PATH.read_text(encoding="utf-8").split()
    }
    print(f"{len(target_words)} mots cible dans mots.txt")

    found = {}  # mot normalisé -> (mot original mots.txt, définition)
    line_count = 0
    match_count = 0

    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            line_count += 1
            if line_count % 500_000 == 0:
                print(f"  ... {line_count} lignes lues, {len(found)} définitions trouvées")
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            word = entry.get("word")
            if not word or " " in word or "-" in word:
                continue  # les mots composés/locutions ne correspondent à aucune entrée de mots.txt (mots simples uniquement)

            key = normalize(word)
            if key not in target_words or key in found:
                continue

            senses = entry.get("senses") or []
            gloss_text = None
            for sense in senses:
                glosses = sense.get("glosses") or []
                if glosses:
                    gloss_text = clean_gloss(glosses[0])
                    break
            if not gloss_text:
                continue

            found[key] = (target_words[key], gloss_text)
            match_count += 1

    print(f"Terminé : {line_count} lignes lues, {match_count} définitions retenues sur {len(target_words)} mots cible ({100 * match_count / len(target_words):.1f}%)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["mot", "definition"])
        for word_original, definition in sorted(found.values()):
            writer.writerow([word_original, definition])

    print(f"Écrit : {OUT_PATH}")


if __name__ == "__main__":
    main()
