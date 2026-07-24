# -*- coding: utf-8 -*-
"""Génère un fichier audio (gTTS, français) annonçant chaque carte du jeu de
belote (32 cartes : 7 à As, 4 enseignes) - utilisé quand la carte retournée
est révélée après la donne (voir announceCardVoice/pauseOnTurnedCard dans
games/belote/main.js). Distinct de generate_dealer_audio.py : ce ne sont pas
des répliques de Fanny mais de simples noms de carte, donc pas de source
dans dealer-dialogue.json.

Même venv gTTS dédié que generate_dealer_audio.py, à lancer depuis
n'importe quel dossier :

    /home/adm1/iatools/gtts/venv/bin/python3 \\
        "ressources/card game/tools/generate_card_audio.py"

Écrit dans assets/cards_audio/belote/{rank}-{suit}.mp3 - convention d'id de
carte identique à src/games/belote/engine.js:makeCard (donc lue à
l'identique par announceCardVoice). Idempotent : un fichier déjà présent
de taille valide n'est pas régénéré.
"""
import os
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CARD_GAME_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
OUT_DIR = os.path.join(_CARD_GAME_ROOT, "assets", "cards_audio", "belote")

RANKS = ["7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["coeur", "carreau", "trefle", "pique"]
RANK_NAMES = {
    "7": "Sept", "8": "Huit", "9": "Neuf", "10": "Dix",
    "J": "Valet", "Q": "Dame", "K": "Roi", "A": "As",
}
SUIT_NAMES = {"coeur": "Cœur", "carreau": "Carreau", "trefle": "Trèfle", "pique": "Pique"}

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
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = []
    for suit in SUITS:
        for rank in RANKS:
            text = f"{RANK_NAMES[rank]} de {SUIT_NAMES[suit]}"
            path = os.path.join(OUT_DIR, f"{rank}-{suit}.mp3")
            jobs.append((text, path))

    print(f"{len(jobs)} cartes à synthétiser")
    counts = {"generated": 0, "skipped": 0, "failed": 0}
    for i, (text, path) in enumerate(jobs, start=1):
        result = synthesize(text, path)
        counts[result] += 1
        print(f"[{i}/{len(jobs)}] {result:9s} {text}")

    print("Terminé :", counts)


if __name__ == "__main__":
    main()
