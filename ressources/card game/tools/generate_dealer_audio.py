# -*- coding: utf-8 -*-
"""Génère les fichiers audio (gTTS, français) des répliques de la
croupière (Fanny) pour le Blackjack et le Vidéo Poker, à partir de
src/dealer/dealer-dialogue.json (seule source de vérité des textes -
ne pas dupliquer les répliques ailleurs, éditer uniquement ce JSON).

Ce script utilise le paquet gTTS, installé UNIQUEMENT dans le venv dédié
/home/adm1/iatools/gtts/venv (pas dans un venv du jeu) - il faut le lancer
avec cet interpréteur, depuis n'importe quel dossier :

    /home/adm1/iatools/gtts/venv/bin/python3 \\
        "ressources/card game/tools/generate_dealer_audio.py"

Chaque réplique est écrite dans
assets/dealer_audio/{game}/{event}_{index}.mp3 (index = position de la
réplique dans le tableau du JSON pour cet event) - convention lue à
l'identique par src/dealer/dealerVoice.js pour retrouver le bon fichier.

Idempotent : un fichier déjà présent (de taille valide) n'est pas
régénéré, donc relancer ce script après une interruption (quota, coupure
réseau) ne refait que le travail manquant.
"""
import json
import os
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CARD_GAME_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))

DIALOGUE_PATH = os.path.join(_CARD_GAME_ROOT, "src", "dealer", "dealer-dialogue.json")
AUDIO_ROOT = os.path.join(_CARD_GAME_ROOT, "assets", "dealer_audio")

MAX_RETRIES = 4
MIN_VALID_SIZE = 1024  # un mp3 gTTS valide fait toujours plus que ça


def synthesize(text, path):
    from gtts import gTTS

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
    with open(DIALOGUE_PATH, encoding="utf-8") as f:
        dialogue = json.load(f)

    jobs = []
    for game, events in dialogue.items():
        game_dir = os.path.join(AUDIO_ROOT, game)
        os.makedirs(game_dir, exist_ok=True)
        for event, lines in events.items():
            for index, text in enumerate(lines):
                path = os.path.join(game_dir, f"{event}_{index}.mp3")
                jobs.append((text, path))

    print(f"{len(jobs)} répliques à synthétiser (Blackjack + Vidéo Poker)")

    counts = {"generated": 0, "skipped": 0, "failed": 0}
    for i, (text, path) in enumerate(jobs, start=1):
        result = synthesize(text, path)
        counts[result] += 1
        print(f"[{i}/{len(jobs)}] {result:9s} {os.path.relpath(path, AUDIO_ROOT)}")

    print("Terminé :", counts)


if __name__ == "__main__":
    main()
