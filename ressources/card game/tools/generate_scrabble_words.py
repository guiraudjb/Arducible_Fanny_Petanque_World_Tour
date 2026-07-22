# -*- coding: utf-8 -*-
"""Génère la liste de mots valides du Scrabble Fanny (mini-jeu du Casino).

Deux sources, toutes deux bien plus fiables qu'un simple dictionnaire de
correcteur orthographique (l'ancienne source, /usr/share/dict/french,
laissait passer des abréviations comme "KM" ou "CC") :

  1. Morphalou 3.1 (ATILF/CNRS, licence LGPL-LR, écosystème CNRTL/TLFi) -
     lexique de 159 271 lemmes / 976 570 formes fléchies du français
     moderne, avec catégorie grammaticale par forme (aucun nom propre,
     aucune locution multi-mots dans ce lexique). Fichier trop volumineux
     (~106 Mo) pour être versionné dans le dépôt : à télécharger une fois
     depuis https://huggingface.co/datasets/datasets-CNRS/Morphalou
     (fichier Morphalou3.1_formatCSV_toutEnUn.zip, ne dézipper que
     Morphalou3.1_CSV.csv) et placer dans MORPHALOU_CSV_PATH ci-dessous -
     même logique que le venv gTTS : une ressource externe documentée,
     pas un fichier du dépôt.

  2. Argot : les ~3860 titres de la catégorie Wiktionnaire "Termes
     argotiques en français", capturés le 2026-07-22 dans
     argot-wiktionary-fr.txt (petit fichier, versionné - contrairement à
     Morphalou, source authentique mais pas rejouable sans réseau, donc
     un instantané figé plutôt qu'un appel API à chaque génération).
     Couvre des mots comme MEUF, KEUF, SEUM, KIFFER (acceptés à l'Officiel
     du Scrabble - ODS) mais aussi énormément d'argot que l'ODS refuse :
     comme pour Morphalou, ceci n'est PAS l'ODS (dictionnaire propriétaire
     non distribuable), juste un enrichissement assumé, pas une
     prétention d'exactitude compétition.

Mêmes filtres qu'avant : replié en majuscules SANS accent (une lettre du
jeu = un jeton, "ÉTÉ" se pose avec les jetons E, T, E), longueur 2 à 7
(le chevalet ne contient que 7 lettres), une seule chaîne de lettres
(rejette espaces, apostrophes, tirets, chiffres - donc les locutions et
mots composés).

Sortie : assets/scrabble/mots.txt (un mot par ligne, trié) - lu tel quel
par src/games/scrabble/engine.js via fetch + split('\\n').

ATTENTION - bruit residuel sur les mots courts (2-3 lettres) : Morphalou
est une fusion de plusieurs lexiques (dont Dicollecte et Lefff), qui
incluent tous deux des ABRÉVIATIONS taguées comme si c'étaient de vrais
mots fléchis - ex. "kW", "MW", "cm", "km" étiquetés "Nom commun" (le
lemme "W" y récupère des dizaines de préfixes SI comme flexions !), ou
"pr", "qd", "qq", "bcp" (abréviations SMS pour "pour", "quand", "quelque",
"beaucoup") avec une vraie catégorie grammaticale. Ce n'est PAS un
problème pour les mots de 4+ lettres (les abréviations sont
quasi-systématiquement courtes). Pour les mots de 2-3 lettres, on
n'accepte donc une entrée Morphalou de catégorie "Nom commun" que si elle
est également confirmée par le dictionnaire système (/usr/share/dict/french,
l'ancienne source) - ça élimine l'essentiel du bruit "Nom commun" (les
abréviations d'unités) tout en gardant les vrais mots courts usuels
(AMI, ARC, BAL...). Il reste malgré tout quelques abréviations SMS
taguées avec d'autres catégories (ex. "pr", "qd") qui passent au travers
- accepté comme compromis, pas une prétention d'exactitude ODS.

Usage : python3 "ressources/card game/tools/generate_scrabble_words.py"
(aucune dépendance externe).
"""
import csv
import os
import re
import unicodedata

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CARD_GAME_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))

MORPHALOU_CSV_PATH = os.path.expanduser("~/iatools/morphalou/Morphalou3.1_CSV.csv")
SYSTEM_DICT_PATH = "/usr/share/dict/french"
ARGOT_TITLES_PATH = os.path.join(_THIS_DIR, "argot-wiktionary-fr.txt")
OUTPUT_PATH = os.path.join(_CARD_GAME_ROOT, "assets", "scrabble", "mots.txt")

SHORT_WORD_MAX_LEN = 3  # longueur à partir de laquelle le bruit "Nom commun" de Morphalou disparaît

# Une seule chaîne de lettres (accentuées ou non) : rejette d'entrée les
# locutions ("à la bien"), mots composés ("croque-mitaine"), formes avec
# apostrophe, chiffres, etc.
VALID_SOURCE_RE = re.compile(r"^[a-zàâäéèêëîïôöùûüçœæÿ]+$", re.IGNORECASE)
ASCII_LETTERS_RE = re.compile(r"^[A-Z]+$")
VOWEL_RE = re.compile(r"[AEIOUY]")


def normalize(word):
    folded = word.replace("œ", "oe").replace("æ", "ae").replace("Œ", "OE").replace("Æ", "AE")
    decomposed = unicodedata.normalize("NFKD", folded)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.upper()


def keep(word):
    normalized = normalize(word)
    return 2 <= len(normalized) <= 7 and ASCII_LETTERS_RE.match(normalized)


def trusted_short_words(path):
    """Mots de 2-3 lettres du dictionnaire système - sert de garde-fou
    pour la catégorie "Nom commun" de Morphalou (voir docstring du
    module) : un spell-checker classique ne référence pas les
    abréviations d'unités (kW, cm...) comme des mots à part entière."""
    words = set()
    if not os.path.exists(path):
        return words
    with open(path, encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if not w or not VALID_SOURCE_RE.match(w):
                continue
            normalized = normalize(w)
            if 2 <= len(normalized) <= SHORT_WORD_MAX_LEN and VOWEL_RE.search(normalized):
                words.add(normalized)
    return words


def words_from_morphalou(path, trusted_short):
    if not os.path.exists(path):
        print(f"ATTENTION : Morphalou introuvable à {path} - voir le docstring pour le télécharger. "
              "Génération poursuivie avec l'argot seul.")
        return set()

    words = set()
    total_rows = 0
    skipped_short_noms = 0
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            # Le fichier commence par ~16 lignes de préambule (licence,
            # description) avant la vraie ligne d'en-têtes de colonnes.
            if line.startswith("GRAPHIE;ID;CAT"):
                break
        reader = csv.reader(f, delimiter=";")
        current_category = None
        for row in reader:
            if len(row) < 10:
                continue
            if row[0].strip():  # nouvelle ligne de lemme : la catégorie est mise à jour
                current_category = row[2].strip()
            flexion = row[9].strip()
            if not flexion or not VALID_SOURCE_RE.match(flexion):
                continue
            total_rows += 1
            if not keep(flexion):
                continue
            normalized = normalize(flexion)
            if len(normalized) <= SHORT_WORD_MAX_LEN and current_category == "Nom commun" \
                    and normalized not in trusted_short:
                skipped_short_noms += 1
                continue
            words.add(normalized)
    print(f"Morphalou : {total_rows} formes fléchies lues, {len(words)} mots de 2 à 7 lettres retenus "
          f"({skipped_short_noms} noms communs courts écartés, non confirmés par le dictionnaire système)")
    return words


def words_from_argot(path):
    words = set()
    total = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            title = line.strip()
            if not title or not VALID_SOURCE_RE.match(title):
                continue
            total += 1
            if keep(title):
                words.add(normalize(title))
    print(f"Argot (Wiktionnaire) : {total} titres à un seul mot lus, {len(words)} mots de 2 à 7 lettres retenus")
    return words


def main():
    words = set()
    trusted_short = trusted_short_words(SYSTEM_DICT_PATH)
    words |= words_from_morphalou(MORPHALOU_CSV_PATH, trusted_short)
    words |= words_from_argot(ARGOT_TITLES_PATH)

    if not words:
        raise SystemExit("Aucun mot généré - vérifier les chemins des sources.")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(words)))

    print(f"Total : {len(words)} mots écrits dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
