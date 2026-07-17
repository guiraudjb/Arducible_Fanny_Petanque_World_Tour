# -*- coding: utf-8 -*-
"""Génère les fichiers audio (gTTS, français) pour toutes les questions,
choix et explications du quizz (Scripts/quiz_questions.py).

Ce script utilise le paquet gTTS, installé UNIQUEMENT dans le venv dédié
/home/adm1/iatools/gtts/venv (pas dans le venv du jeu) - il faut le lancer
avec cet interpréteur :

    cd /home/adm1/Fanny_P-tanque_World_Tour
    /home/adm1/iatools/gtts/venv/bin/python3 ressources/utils/generate_quiz_audio.py

Chaque texte unique (question, choix ou explication - un même choix peut
apparaître comme bonne réponse dans un pays et comme distracteur dans un
autre : on ne le synthétise qu'une fois) est écrit dans
assets/Sounds/QuizzTTS/{hash_du_texte}.mp3 (voir Scripts/quiz_audio.py
pour le calcul du hash - le jeu retrouve le fichier de la même façon à
l'exécution, sans table de correspondance séparée).

Idempotent : un fichier déjà présent n'est pas régénéré, donc relancer ce
script après une interruption (quota, coupure réseau) ne refait que le
travail manquant.
"""
import concurrent.futures
import os
import sys
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, _REPO_ROOT)
os.chdir(_REPO_ROOT)

from Scripts.quiz_questions import QUIZ_QUESTIONS  # noqa: E402
from Scripts.quiz_audio import QUIZ_AUDIO_DIR, quiz_audio_path  # noqa: E402

from gtts import gTTS  # noqa: E402

MAX_WORKERS = 1
MAX_RETRIES = 4
MIN_VALID_SIZE = 1024  # un mp3 gTTS valide fait toujours plus que ça


def collect_texts():
    texts = set()
    for questions in QUIZ_QUESTIONS:
        for question, choices, _correct_index, explanation in questions:
            texts.add(question)
            texts.update(choices)
            texts.add(explanation)
    return sorted(texts)


def synthesize(text):
    path = quiz_audio_path(text)
    if os.path.exists(path) and os.path.getsize(path) >= MIN_VALID_SIZE:
        return "skipped"
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            gTTS(text=text, lang="fr").save(path)
            if os.path.getsize(path) >= MIN_VALID_SIZE:
                return "generated"
            last_error = "fichier généré mais anormalement petit"
        except Exception as e:  # réseau/quota : on retente avant d'abandonner
            last_error = e
        if os.path.exists(path):
            os.remove(path)  # ne pas laisser un fichier tronqué être pris pour "déjà présent"
        time.sleep(3 * attempt)  # backoff croissant, utile contre le 429 (rate limit)
    print(f"ÉCHEC après {MAX_RETRIES} essais : {text!r} ({last_error})")
    return "failed"


def main():
    os.makedirs(QUIZ_AUDIO_DIR, exist_ok=True)
    texts = collect_texts()
    print(f"{len(texts)} textes uniques à synthétiser (questions + choix + explications)")

    counts = {"generated": 0, "skipped": 0, "failed": 0}
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(synthesize, text): text for text in texts}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            counts[result] += 1
            done += 1
            if done % 50 == 0 or done == len(texts):
                print(f"[{done}/{len(texts)}] générés={counts['generated']} "
                      f"déjà présents={counts['skipped']} échecs={counts['failed']}")

    print("Terminé :", counts)


if __name__ == "__main__":
    main()
