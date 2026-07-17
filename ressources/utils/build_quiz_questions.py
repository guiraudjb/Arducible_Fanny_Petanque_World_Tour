# -*- coding: utf-8 -*-
"""Génère Scripts/quiz_questions.py à partir de WORLD_TOUR_COUNTRIES +
quiz_country_facts.py + quiz_petanque_researched_facts.py +
quiz_monuments_facts.py + quiz_second_facts.py + quiz_monument_categories.py
+ quiz_pre_euro_currencies.py + quiz_second_monuments_facts.py +
quiz_petanque_facts_2.py + quiz_petanque_athletes.py +
quiz_petanque_facts_3.py (tous dans ce même dossier).
Chaque option de réponse, correcte ou non, est toujours un vrai fait réel
rattaché à un pays réel de la liste (jamais une donnée inventée). Les
distracteurs sont choisis dans le même continent quand c'est possible, et
pour les deux questions monument/spécialité dans la même CATÉGORIE en plus
(un château face à d'autres châteaux, jamais face à un casino ou un
navire), pour rester plausibles (éviter qu'un choix soit "évidemment" faux
par simple élimination de type ou de continent).

Pour MAXIMISER la part de questions sur la pétanque elle-même (demande
utilisateur du 2026-07-12, réitérée le même jour : "il faut plus de
question sur la pétanque", à partir des recherches de
RECHERCHE_ATHLETES_PETANQUE.md) :
- Q3 (capitale) est remplacée par un TROISIÈME fait pétanque réel et sourcé
  (quiz_petanque_facts_3.py), pour les quelques pays les plus riches en
  faits distincts (Madagascar, Maroc, Tunisie). Sinon la capitale comme
  avant.
- Q4 (monnaie) est remplacée par un DEUXIÈME fait pétanque réel et sourcé
  (quiz_petanque_facts_2.py), distinct de celui de Q1, quand disponible.
  Sinon : pour les 19 pays de la zone euro, la monnaie D'AVANT l'euro
  (sinon les 19 partageraient tous la même réponse "l'euro") ; sinon la
  monnaie actuelle.
- Q5 (second monument/spécialité) est remplacée par une question sur une
  personnalité de pétanque réelle associée au pays (quiz_petanque_athletes.py
  - joueur/joueuse, mais aussi président(e) de fédération ou entraîneur(e)
  quand c'est la seule personnalité réelle trouvée), quand disponible.
  Sinon un second monument/site/spécialité différent de celui de la
  question 2 (quiz_second_monuments_facts.py), phrasé sans jamais dire
  "monument" ni "spécialité".

Les répliques de Fanny (Scripts/dialogues.py) ne sont PAS utilisées comme
question de quizz (retiré sur demande) - seulement comme fait pétanque
narratif affiché ailleurs dans le jeu.

Sources des faits : voir RECHERCHE_PETANQUE_PAYS.md,
RECHERCHE_ATHLETES_PETANQUE.md, RECHERCHE_MONUMENTS_SPECIALITES.md et
RECHERCHE_2E_MONUMENT_SPECIALITE.md dans ce même dossier. À relancer avec :
    cd /home/adm1/Fanny_P-tanque_World_Tour
    python3 ressources/utils/build_quiz_questions.py
"""

import os
import random
import re
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _THIS_DIR)

from Scripts.dialogues import WORLD_TOUR_COUNTRIES
from quiz_country_facts import COUNTRY_FACTS
from quiz_petanque_researched_facts import RESEARCHED_FACTS
from quiz_monuments_facts import MONUMENTS
from quiz_second_facts import SECOND_FACTS
from quiz_monument_categories import MONUMENT_CATEGORIES, SECOND_MONUMENT_CATEGORIES
from quiz_pre_euro_currencies import PRE_EURO_CURRENCIES
from quiz_second_monuments_facts import SECOND_MONUMENTS
from quiz_petanque_facts_2 import SECOND_PETANQUE_FACTS
from quiz_petanque_athletes import PETANQUE_ATHLETES
from quiz_petanque_facts_3 import THIRD_PETANQUE_FACTS

random.seed(42)  # sortie reproductible

N = len(WORLD_TOUR_COUNTRIES)
assert len(COUNTRY_FACTS) == N
assert len(MONUMENTS) == N
assert len(MONUMENT_CATEGORIES) == N
assert len(SECOND_MONUMENTS) == N
assert len(SECOND_MONUMENT_CATEGORIES) == N
for t in range(N):
    assert t in RESEARCHED_FACTS or t in SECOND_FACTS, t

CAPITALS = [f[0] for f in COUNTRY_FACTS]
CONTINENTS = [f[1] for f in COUNTRY_FACTS]
CURRENCIES = [f[3] for f in COUNTRY_FACTS]
MONUMENT_NAMES = [MONUMENTS[t][0] for t in range(N)]
SECOND_MONUMENT_NAMES = [SECOND_MONUMENTS[t][0] for t in range(N)]


def pick_distractors(values, tier, k=2, same_continent_pool=None, priority_pools=None):
    """k valeurs distinctes de values[tier], jamais la bonne réponse ni
    entre elles. `priority_pools`, si fourni (liste de listes d'index),
    est essayé dans l'ordre AVANT same_continent_pool puis le pool global -
    permet de préférer par ex. même catégorie ET même continent avant de
    retomber sur juste même continent, pour des distracteurs plus
    difficiles à écarter par simple élimination de type."""
    correct_value = values[tier]
    ordered_pools = []
    if priority_pools:
        ordered_pools.extend(priority_pools)
    if same_continent_pool is not None:
        ordered_pools.append(same_continent_pool)
    ordered_pools.append([i for i in range(len(values)) if i != tier])

    chosen = []
    seen = {correct_value}
    for pool in ordered_pools:
        pool = [i for i in pool if i != tier]
        random.shuffle(pool)
        for i in pool:
            if values[i] in seen:
                continue
            chosen.append(values[i])
            seen.add(values[i])
            if len(chosen) == k:
                return chosen
    return chosen


def same_continent_indices(tier):
    return [i for i in range(N) if i != tier and CONTINENTS[i] == CONTINENTS[tier]]


def same_category_indices(tier):
    category = MONUMENT_CATEGORIES[tier]
    return [i for i in range(N) if i != tier and MONUMENT_CATEGORIES[i] == category]


def same_second_category_indices(tier):
    category = SECOND_MONUMENT_CATEGORIES[tier]
    return [i for i in range(N) if i != tier and SECOND_MONUMENT_CATEGORIES[i] == category]


def make_qcm(question, correct_value, distractors, explanation=None):
    """`explanation` est le texte que Fanny affiche après le feedback pour
    expliquer la bonne réponse, avant de passer à la question suivante -
    par défaut une confirmation neutre de la valeur correcte (toujours
    vraie, jamais inventée), enrichie d'une description réelle quand on en
    a une (monument, second fait...)."""
    options = [correct_value] + distractors
    order = list(range(len(options)))
    random.shuffle(order)
    shuffled = [options[i] for i in order]
    correct_index = shuffled.index(correct_value)
    if explanation is None:
        explanation = f"La bonne réponse était {correct_value}."
    return (question, shuffled, correct_index, explanation)


# "en Allemagne" / "au Maroc" / "aux Pays-Bas" / "à Monaco" : chaque phrase de
# Fanny (Scripts/dialogues.py) commence déjà par la bonne préposition + le bon
# pays - on la récupère telle quelle (garantit un accord grammatical correct,
# cohérent avec le reste du jeu) plutôt que de re-déterminer le genre nous-mêmes.
# On dérive ensuite la forme génitive ("la capitale de/du/des X") à partir de
# cette même préposition : en->de, au->du, aux->des, à->de.
_LIEU_PATTERN = re.compile(r"^(En|Au|Aux|À)\s+([^,!]+)[,!]")
_LIEU_OVERRIDES = {
    0: ("en", "Allemagne"),
    1: ("en", "Andorre"),
    12: ("en", "France"),
    13: ("à", "Guernesey"),
    17: ("à", "Jersey"),
}
_GENITIF = {"en": "de", "au": "du", "aux": "des", "à": "de"}
VOWELS = tuple("AEIOUÉÀÂÄÎÏÔÖÙÛÜ")


def build_lieu_tables():
    lieux, genitifs = [], []
    for i, (_pays, _slug, text) in enumerate(WORLD_TOUR_COUNTRIES):
        if i in _LIEU_OVERRIDES:
            prep, lieu_pays = _LIEU_OVERRIDES[i]
        else:
            m = _LIEU_PATTERN.match(text)
            assert m, (i, text[:60])
            prep, lieu_pays = m.group(1).lower(), m.group(2)
        lieux.append(f"{prep} {lieu_pays}")
        genitif_prep = _GENITIF[prep]
        if genitif_prep == "de" and lieu_pays.startswith(VOWELS):
            genitifs.append(f"d'{lieu_pays}")
        else:
            genitifs.append(f"{genitif_prep} {lieu_pays}")
    return lieux, genitifs


LIEUX, GENITIFS = build_lieu_tables()


def make_researched_question(tier):
    """Question basée sur un fait pétanque réel et sourcé (recherche web),
    trouvé pour ce pays. Distracteurs = vraies réponses (années/faits)
    d'AUTRES pays de RESEARCHED_FACTS - jamais une valeur inventée."""
    question, answer = RESEARCHED_FACTS[tier]
    pool_tiers = [t for t in RESEARCHED_FACTS if t != tier]
    random.shuffle(pool_tiers)
    distractors = []
    seen = {answer}
    for t in pool_tiers:
        _q, a = RESEARCHED_FACTS[t]
        if a in seen:
            continue
        distractors.append(a)
        seen.add(a)
        if len(distractors) == 2:
            break
    return make_qcm(question, answer, distractors)


def make_second_fact_question(pays, tier):
    """Pour les 12 pays sans fait pétanque sourcé : question sur un
    deuxième fait notable (ressource, tradition...), distincte du
    monument/spécialité déjà utilisé en Q2. Distracteurs pris parmi les
    autres pays de SECOND_FACTS (mêmes garanties que les autres
    catégories : jamais une valeur inventée)."""
    name, description = SECOND_FACTS[tier]
    pool_tiers = [t for t in SECOND_FACTS if t != tier]
    random.shuffle(pool_tiers)
    distractors = []
    seen = {name}
    for t in pool_tiers:
        other_name, _d = SECOND_FACTS[t]
        if other_name in seen:
            continue
        distractors.append(other_name)
        seen.add(other_name)
        if len(distractors) == 2:
            break
    question = f"Quel fait notable est associé à {pays} ({description}) ?"
    return make_qcm(question, name, distractors, explanation=f"La bonne réponse était {name} : {description}.")


def make_second_petanque_question(tier):
    """Deuxième question pétanque (remplace la monnaie, Q4, quand
    disponible) : un fait réel distinct de celui de Q1, tiré de
    SECOND_PETANQUE_FACTS. Distracteurs = vraies années d'AUTRES pays de ce
    même dict - jamais une valeur inventée, jamais mélangées avec le pool
    de RESEARCHED_FACTS (Q1) pour ne pas répéter deux fois le même
    distracteur au même joueur dans la même manche."""
    question, answer = SECOND_PETANQUE_FACTS[tier]
    pool_tiers = [t for t in SECOND_PETANQUE_FACTS if t != tier]
    random.shuffle(pool_tiers)
    distractors = []
    seen = {answer}
    for t in pool_tiers:
        _q, a = SECOND_PETANQUE_FACTS[t]
        if a in seen:
            continue
        distractors.append(a)
        seen.add(a)
        if len(distractors) == 2:
            break
    return make_qcm(question, answer, distractors)


def make_third_petanque_question(tier):
    """Troisième question pétanque (remplace la capitale, Q3, uniquement
    pour les quelques pays les plus riches en faits pétanque distincts) :
    un fait réel tiré de THIRD_PETANQUE_FACTS, distinct de Q1 et Q4.
    Distracteurs = vraies années d'AUTRES pays de ce même dict."""
    question, answer = THIRD_PETANQUE_FACTS[tier]
    pool_tiers = [t for t in THIRD_PETANQUE_FACTS if t != tier]
    random.shuffle(pool_tiers)
    distractors = []
    seen = {answer}
    for t in pool_tiers:
        _q, a = THIRD_PETANQUE_FACTS[t]
        if a in seen:
            continue
        distractors.append(a)
        seen.add(a)
        if len(distractors) == 2:
            break
    return make_qcm(question, answer, distractors)


def make_petanque_athlete_question(pays, tier):
    """Question sur un(e) athlète de pétanque réel(le) associé(e) au pays
    (remplace le second monument/spécialité, Q5, quand disponible), tirée
    de PETANQUE_ATHLETES. Distracteurs = vrais noms d'athlètes d'AUTRES
    pays de ce même dict - jamais un nom inventé."""
    name, description = PETANQUE_ATHLETES[tier]
    pool_tiers = [t for t in PETANQUE_ATHLETES if t != tier]
    random.shuffle(pool_tiers)
    distractors = []
    seen = {name}
    for t in pool_tiers:
        other_name, _d = PETANQUE_ATHLETES[t]
        if other_name in seen:
            continue
        distractors.append(other_name)
        seen.add(other_name)
        if len(distractors) == 2:
            break
    question = f"Quel joueur ou quelle joueuse de pétanque est associé(e) à {pays} ({description}) ?"
    return make_qcm(question, name, distractors, explanation=f"La bonne réponse était {name} : {description}.")


QUIZ_QUESTIONS = []
for tier in range(N):
    pays = WORLD_TOUR_COUNTRIES[tier][0]
    same_cont = same_continent_indices(tier)

    # Q1 : fait pétanque précis et sourcé si dispo, sinon un deuxième fait
    # notable (ressource/tradition...), jamais une réplique de Fanny.
    if tier in RESEARCHED_FACTS:
        q1 = make_researched_question(tier)
    else:
        q1 = make_second_fact_question(pays, tier)

    # Q2 : monument / site touristique / spécialité locale. Distracteurs
    # pris en priorité parmi d'AUTRES monuments de la MÊME CATÉGORIE (un
    # château face à d'autres châteaux, jamais face à un casino ou un
    # navire) - même continent d'abord, puis même catégorie ailleurs, puis
    # même continent toute catégorie, puis global en dernier recours.
    same_cat = same_category_indices(tier)
    same_cat_and_cont = [i for i in same_cat if i in set(same_cont)]
    q2 = make_qcm(
        f"Quel monument ou quelle spécialité est associé à {pays} ({MONUMENTS[tier][1]}) ?",
        MONUMENT_NAMES[tier],
        pick_distractors(
            MONUMENT_NAMES, tier,
            priority_pools=[same_cat_and_cont, same_cat],
            same_continent_pool=same_cont,
        ),
        explanation=f"La bonne réponse était {MONUMENT_NAMES[tier]} : {MONUMENTS[tier][1]}.",
    )

    # Q3 : TROISIÈME question pétanque quand un fait distinct de Q1/Q4 a été
    # trouvé (THIRD_PETANQUE_FACTS - demande utilisateur du 2026-07-12 de
    # maximiser encore la part de pétanque), sinon capitale comme avant.
    if tier in THIRD_PETANQUE_FACTS:
        q3 = make_third_petanque_question(tier)
    else:
        q3 = make_qcm(
            f"Quelle est la capitale {GENITIFS[tier]} ?",
            CAPITALS[tier],
            pick_distractors(CAPITALS, tier, same_continent_pool=same_cont),
        )

    # Q4 : DEUXIÈME question pétanque quand un fait distinct de Q1 a été
    # trouvé (SECOND_PETANQUE_FACTS - demande utilisateur du 2026-07-12 de
    # maximiser la part de questions sur la pétanque), sinon monnaie comme
    # avant. Les 19 pays de la zone euro partagent tous "l'euro" - une
    # question triviale et répétitive - donc pour ceux-là (sans 2e fait
    # pétanque) on interroge plutôt sur la monnaie utilisée AVANT l'euro.
    if tier in SECOND_PETANQUE_FACTS:
        q4 = make_second_petanque_question(tier)
    elif tier in PRE_EURO_CURRENCIES:
        pre_euro_tiers = [t for t in PRE_EURO_CURRENCIES if t != tier]
        random.shuffle(pre_euro_tiers)
        distractors = []
        seen = {PRE_EURO_CURRENCIES[tier]}
        for t in pre_euro_tiers:
            val = PRE_EURO_CURRENCIES[t]
            if val in seen:
                continue
            distractors.append(val)
            seen.add(val)
            if len(distractors) == 2:
                break
        q4 = make_qcm(
            f"Quelle monnaie était utilisée {LIEUX[tier]} avant l'euro ?",
            PRE_EURO_CURRENCIES[tier],
            distractors,
        )
    else:
        q4 = make_qcm(
            f"Quelle est la monnaie utilisée {LIEUX[tier]} ?",
            CURRENCIES[tier],
            pick_distractors(CURRENCIES, tier, same_continent_pool=same_cont),
        )

    # Q5 : question sur un(e) athlète de pétanque réel(le) quand disponible
    # (PETANQUE_ATHLETES - même demande de maximisation), sinon un second
    # monument/site/spécialité différent de celui de Q2 comme avant.
    # Phrasée SANS jamais dire "monument" ni "spécialité" (contrairement à
    # Q2), pour ne pas donner d'indice sur la nature de la réponse.
    if tier in PETANQUE_ATHLETES:
        q5 = make_petanque_athlete_question(pays, tier)
    else:
        same_second_cat = same_second_category_indices(tier)
        same_second_cat_and_cont = [i for i in same_second_cat if i in set(same_cont)]
        q5 = make_qcm(
            f"À quoi d'autre est associé {pays} ({SECOND_MONUMENTS[tier][1]}) ?",
            SECOND_MONUMENT_NAMES[tier],
            pick_distractors(
                SECOND_MONUMENT_NAMES, tier,
                priority_pools=[same_second_cat_and_cont, same_second_cat],
                same_continent_pool=same_cont,
            ),
            explanation=f"La bonne réponse était {SECOND_MONUMENT_NAMES[tier]} : {SECOND_MONUMENTS[tier][1]}.",
        )

    QUIZ_QUESTIONS.append([q1, q2, q3, q4, q5])

# --- validation structurelle ---
assert len(QUIZ_QUESTIONS) == N
for tier, qs in enumerate(QUIZ_QUESTIONS):
    assert len(qs) == 5, tier
    for q in qs:
        question, choices, correct_index, explanation = q
        assert isinstance(question, str) and question
        assert len(choices) == 3, (tier, q)
        assert 0 <= correct_index < 3
        assert len(set(choices)) == 3, (tier, q)  # pas de doublon parmi les 3 choix
        assert isinstance(explanation, str) and explanation
        assert choices[correct_index] in explanation, (tier, q)  # l'explication cite bien la bonne réponse

# --- écriture du fichier final ---
OUT = os.path.join(_REPO_ROOT, "Scripts", "quiz_questions.py")

HEADER = '''"""Questions de quizz du fork Fanny Pétanque World Tour Quizz.

QUIZ_QUESTIONS est parallèle à WORLD_TOUR_COUNTRIES (Scripts/dialogues.py) :
même longueur, même ordre, même index de pays (tier). Chaque élément est une
liste de 5 questions (une par cible dans main_quizz.py), chaque question un
tuple (texte, [choix_a, choix_b, choix_c], index_bonne_reponse, explication).
L'explication est le texte que Fanny affiche après le feedback (bonne/
mauvaise réponse en couleur) pour expliquer la bonne réponse, avant de
passer à la question suivante - toujours au moins une confirmation de la
valeur correcte, enrichie de la description réelle du fait quand il y en a
une (monument, second fait...), jamais une donnée inventée.

Généré par ressources/utils/build_quiz_questions.py à partir de :
- ressources/utils/quiz_country_facts.py (capitale, continent, monnaie)
- ressources/utils/quiz_petanque_researched_facts.py (faits pétanque réels
  et sourcés, recherchés sur le web pour 100/112 pays — voir
  ressources/utils/RECHERCHE_PETANQUE_PAYS.md)
- ressources/utils/quiz_monuments_facts.py (monument/site touristique/
  spécialité locale par pays, recherché pour les 112 pays — voir
  ressources/utils/RECHERCHE_MONUMENTS_SPECIALITES.md)
- ressources/utils/quiz_second_facts.py (deuxième fait notable, pour les
  12 pays sans fait pétanque sourcé)
- ressources/utils/quiz_monument_categories.py (catégorie de chaque
  monument/spécialité des questions 2 et 5, pour des distracteurs du même
  type)
- ressources/utils/quiz_pre_euro_currencies.py (monnaie nationale d'avant
  l'euro, pour les 19 pays de la zone euro)
- ressources/utils/quiz_second_monuments_facts.py (2e monument/site/
  spécialité par pays, différent de celui de la question 2 — voir
  ressources/utils/RECHERCHE_2E_MONUMENT_SPECIALITE.md)
- ressources/utils/quiz_petanque_facts_2.py (2e fait pétanque réel et
  sourcé, distinct de celui de la question 1, quand disponible — remplace
  la monnaie en question 4)
- ressources/utils/quiz_petanque_athletes.py (personnalité de pétanque
  réelle associée au pays, quand disponible — remplace le second monument
  en question 5)
- ressources/utils/quiz_petanque_facts_3.py (3e fait pétanque réel et
  sourcé, distinct des questions 1 et 4, pour 3 pays seulement — remplace
  la capitale en question 3) — ces trois derniers voir
  ressources/utils/RECHERCHE_ATHLETES_PETANQUE.md

Principe de contenu : chaque option de réponse, correcte ou non, est
toujours un vrai fait rattaché à un pays réel de la liste — les mauvaises
réponses sont uniquement de vrais faits d'AUTRES pays (jamais une donnée
inventée). Elles sont choisies en priorité dans le MÊME CONTINENT que la
bonne réponse pour rester plausibles (éviter qu'un choix soit "évidemment"
faux), et pour les questions monument/spécialité, en plus dans la MÊME
CATÉGORIE (un château face à d'autres châteaux, jamais face à un casino ou
un navire). Les répliques de Fanny (Scripts/dialogues.py) ne sont PAS
utilisées comme question de quizz.

Les 5 questions de chaque pays (maximisant la part de pétanque quand les
recherches le permettent — jusqu'à 4/5 questions pétanque pour Madagascar,
le Maroc et la Tunisie ; jusqu'à 3/5 pour les autres) :
1. Fait pétanque précis et sourcé (année de fondation de fédération,
   résultat en championnat...) si trouvé en recherche, sinon un deuxième
   fait notable (ressource, tradition...).
2. Monument, site touristique ou spécialité locale (distracteurs de même
   catégorie).
3. Un TROISIÈME fait pétanque réel, distinct des questions 1 et 4, pour
   les quelques pays qui en ont un ; sinon la capitale.
4. Un DEUXIÈME fait pétanque réel, distinct du premier, quand disponible ;
   sinon la monnaie (ou la monnaie d'avant l'euro pour les 19 pays de la
   zone euro, "l'euro" étant une réponse trop répétitive).
5. Une personnalité de pétanque réelle associée au pays (joueur/joueuse,
   ou président(e)/entraîneur(e) quand c'est la seule trouvée), quand
   disponible ; sinon un second monument/site/spécialité, différent de
   celui de la question 2 (distracteurs de même catégorie) — cette
   dernière ne dit jamais explicitement "monument" ni "spécialité".
"""

QUIZ_QUESTIONS = [
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(HEADER)
    for tier, qs in enumerate(QUIZ_QUESTIONS):
        pays = WORLD_TOUR_COUNTRIES[tier][0]
        f.write(f"    # {tier} {pays}\n    [\n")
        for question, choices, correct_index, explanation in qs:
            f.write(f"        ({question!r}, {choices!r}, {correct_index}, {explanation!r}),\n")
        f.write("    ],\n")
    f.write("]\n")

print("OK, written", OUT, "-", len(QUIZ_QUESTIONS), "countries")
