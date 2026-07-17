# -*- coding: utf-8 -*-
"""Génère un titre + une liste de hashtags par pays pour les 112 vidéos
"réseaux sociaux" du quizz, à partir des données déjà présentes dans le
projet (WORLD_TOUR_COUNTRIES, quiz_country_facts.py, quiz_monuments_facts.py)
- pas de fait inventé, seulement des hashtags dérivés de noms déjà réels
(pays, continent, monument/spécialité mis en avant dans le quizz).

Écrit ressources/social_videos/titres_hashtags.md (table pays -> titre +
hashtags), à consulter au moment de publier chaque vidéo sur TikTok.

Usage : python3 ressources/utils/generate_social_captions.py
"""
import re
import sys
import unicodedata

sys.path.insert(0, "/home/adm1/Fanny_P-tanque_World_Tour")
sys.path.insert(0, "/home/adm1/Fanny_P-tanque_World_Tour/ressources/utils")
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from quiz_country_facts import COUNTRY_FACTS  # noqa: E402
from quiz_monuments_facts import MONUMENTS  # noqa: E402

ARTICLES = ["les ", "des ", "aux ", "du ", "le ", "la ", "l'", "un ", "une "]


def to_hashtag(text):
    t = text.strip()
    low = t.lower()
    for art in ARTICLES:
        if low.startswith(art):
            t = t[len(art):]
            break
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[A-Za-z0-9]+", t)
    return "#" + "".join(w.capitalize() for w in words)


CORE_TAGS = ["#Petanque", "#Quiz", "#QuizTime", "#CultureGenerale", "#Geographie",
             "#ApprendreSurTiktok", "#TourDuMonde", "#FannyPetanque"]

N = len(WORLD_TOUR_COUNTRIES)
rows = []
for tier in range(N):
    pays = WORLD_TOUR_COUNTRIES[tier][0]
    continent = COUNTRY_FACTS[tier][1]
    monument_name = MONUMENTS[tier][0]

    title = f"Quiz Pétanque : {pays} — Tu relèves le défi ?"

    tags = list(CORE_TAGS)
    tags.append(to_hashtag(pays))
    continent_tag = to_hashtag(continent)
    if continent_tag not in tags:
        tags.append(continent_tag)
    monument_tag = to_hashtag(monument_name)
    if monument_tag not in tags and len(monument_tag) > 1:
        tags.append(monument_tag)

    rows.append((tier, pays, title, " ".join(tags)))

OUT = "/home/adm1/Fanny_P-tanque_World_Tour/ressources/social_videos/titres_hashtags.md"
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# Titres et hashtags — Fanny Pétanque World Tour Quizz (TikTok)\n\n")
    f.write("Généré par `ressources/utils/generate_social_captions.py`. "
            "Titre commun à toute la série + hashtags fixes (#Petanque, #Quiz, ...), "
            "hashtag pays, hashtag continent, hashtag du monument/spécialité mis en avant "
            "dans la vidéo (Question 2 du quizz).\n\n")
    f.write("| # | Pays | Titre | Hashtags |\n")
    f.write("|---|------|-------|----------|\n")
    for tier, pays, title, tags in rows:
        f.write(f"| {tier + 1} | {pays} | {title} | {tags} |\n")

print("écrit :", OUT, "-", len(rows), "pays")
