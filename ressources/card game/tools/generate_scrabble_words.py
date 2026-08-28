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

     La catégorie brute est bruitée. words_from_argot() en retire :
       - les titres capitalisés : noms propres (Bercy, Pantruche...) et
         sigles (BDR, DZ...), que Morphalou exclut déjà de son côté ;
       - les fragments trop courts ou sans voyelle : SMS / phonétique
         ("br", "vrm", "wsh", "teh"...) - on exige >= 4 lettres ET une
         voyelle, sauf poignée de mono/dissyllabes d'argot vérifiés
         (_SHORT_ARGOT_KEEP : TAF, RIF, ZOB...) ;
       - une liste noire manuelle versionnée, argot-exclude.txt : mots
         non français (anglais internet, translittérations) que rien de
         structurel ne distingue - à éditer à la main, la source étant
         figée.
     Rafraîchir l'instantané (nouvelle capture de la catégorie) : via
     PetScan (https://petscan.wmcloud.org) sur frwiktionary, catégorie
     "Termes argotiques en français", profondeur 0, sortie "Wiki" ou
     "CSV" titres seuls ; ou l'API MediaWiki :
       https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers
         &cmtitle=Cat%C3%A9gorie:Termes_argotiques_en_fran%C3%A7ais
         &cmlimit=max&cmnamespace=0&format=json  (paginer sur cmcontinue)
     Écraser argot-wiktionary-fr.txt (un titre par ligne) et mettre à
     jour la date de capture ci-dessus.

Mêmes filtres qu'avant : replié en majuscules SANS accent (une lettre du
jeu = un jeton, "ÉTÉ" se pose avec les jetons E, T, E), longueur 2 à 15,
une seule chaîne de lettres (rejette espaces, apostrophes, tirets,
chiffres - donc les locutions et mots composés).

Le plafond est 15 (largeur du plateau) et non 7 (taille du chevalet) : le
mini-jeu permet de PROLONGER un mot déjà posé en n'ajoutant qu'un ou deux
jetons, donc un coup légal peut former un mot de 8 à 15 lettres
("STIPULA" + I -> "STIPULAI"). Se limiter à 7 rendait toute cette bande
injouable.

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
ARGOT_EXCLUDE_PATH = os.path.join(_THIS_DIR, "argot-exclude.txt")
OUTPUT_PATH = os.path.join(_CARD_GAME_ROOT, "assets", "scrabble", "mots.txt")

SHORT_WORD_MAX_LEN = 3  # longueur à partir de laquelle le bruit "Nom commun" de Morphalou disparaît

# Mono/dissyllabes d'argot vérifiés, gardés malgré la règle ">= 4 lettres
# ET une voyelle" appliquée au reste de la catégorie (voir words_from_argot).
_SHORT_ARGOT_KEEP = {"TAF", "RIF", "SAP", "ZOB", "ZIG", "DAB", "NIB", "MEC"}

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
    return 2 <= len(normalized) <= 15 and ASCII_LETTERS_RE.match(normalized)


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
    print(f"Morphalou : {total_rows} formes fléchies lues, {len(words)} mots de 2 à 15 lettres retenus "
          f"({skipped_short_noms} noms communs courts écartés, non confirmés par le dictionnaire système)")
    return words


def load_argot_exclude(path):
    """Liste noire manuelle (un mot par ligne, '#' = commentaire) des titres
    argot non français que rien de structurel ne distingue - anglais
    internet (CREW, WEED, POOKIE...), translittérations (KONNICHIWA...),
    variantes orthographiques parasites. Normalisée pour comparer à
    normalize(titre). Absente = pas de liste noire (rien retiré)."""
    excluded = set()
    if not os.path.exists(path):
        return excluded
    with open(path, encoding="utf-8") as f:
        for line in f:
            entry = line.split("#", 1)[0].strip()
            if entry:
                excluded.add(normalize(entry))
    return excluded


def words_from_argot(path, exclude_path=ARGOT_EXCLUDE_PATH):
    """Titres à un seul mot de la catégorie argot du Wiktionnaire, nettoyés
    (voir le point 2 du docstring du module). On écarte :
      - l'en-tête "argot" et tout titre capitalisé : noms propres (Bercy,
        Pantruche...) et sigles (BDR, DZ...) - Morphalou les exclut déjà ;
      - les fragments < 4 lettres ou sans voyelle : SMS / phonétique
        ("br", "vrm", "wsh"...), SAUF _SHORT_ARGOT_KEEP (TAF, RIF, ZOB...) ;
      - argot-exclude.txt : liste noire manuelle des mots non français.
    Instantané figé : si le fichier manque, on avertit et on renvoie un
    ensemble vide (comme words_from_morphalou) plutôt que de planter."""
    if not os.path.exists(path):
        print(f"ATTENTION : instantané argot introuvable à {path} - voir le point 2 du "
              "docstring pour le recapturer. Génération poursuivie sans l'apport argot.")
        return set()

    excluded = load_argot_exclude(exclude_path)
    words = set()
    skipped_propres = skipped_courts = skipped_liste = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            title = line.strip()
            if not title or not VALID_SOURCE_RE.match(title):
                continue
            if title == "argot" or title[0].isupper():
                skipped_propres += 1
                continue
            if not keep(title):
                continue
            normalized = normalize(title)
            if normalized in excluded:
                skipped_liste += 1
                continue
            if normalized not in _SHORT_ARGOT_KEEP and (
                    len(normalized) < 4 or not VOWEL_RE.search(normalized)):
                skipped_courts += 1
                continue
            words.add(normalized)
    print(f"Argot (Wiktionnaire) : {len(words)} mots retenus "
          f"({skipped_propres} noms propres/sigles, {skipped_courts} fragments courts, "
          f"{skipped_liste} sur liste noire écartés)")
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
