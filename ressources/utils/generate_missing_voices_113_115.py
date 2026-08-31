#!/usr/bin/env python3
"""Génère les 3 lignes de voix manquantes pour Brésil/Israël/Liban (tiers
112/113/114, cf. Scripts/dialogues.py) dans assets/Sounds/VoicesFannyWorldTour/.

Adapté de ~/story/generate_fanny_world_tour_voices.py : l'original lisait
"fanny wold tour/speach.txt" + "pays_index.txt", un dossier de travail qui
n'existe plus sur le disque. Le texte réellement prononcé en jeu est celui
de Scripts.dialogues.WORLD_TOUR_COUNTRIES (3e champ, cf. Scripts/Sprites.py
_set_dialogue) - on le lit donc directement depuis le module courant du
dépôt plutôt que de le retaper à la main.

Même voix de référence et mêmes réglages XTTS-v2 (par défaut) que
l'original, à exécuter avec l'environnement XTTS dédié :
    /home/adm1/RAID/xtts-test/.venv/bin/python3 \
        ressources/utils/generate_missing_voices_113_115.py
"""
import os
import re
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "assets", "Sounds", "VoicesFannyWorldTour")
REFERENCE_VOICE = os.path.expanduser(
    "~/story/index-tts/examples/fanny_voice_candidates/cv_fr_39809558.wav"
)

TIERS = [112, 113, 114]  # Brésil, Israël, Liban


def slugify(name: str) -> str:
    name = name.lower()
    repl = {"é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "î": "i",
            "ô": "o", "û": "u", "ù": "u", "ç": "c", "ï": "i", "ë": "e"}
    for a, b in repl.items():
        name = name.replace(a, b)
    name = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
    return name


def main():
    os.environ["COQUI_TOS_AGREED"] = "1"
    from TTS.api import TTS

    os.makedirs(OUT_DIR, exist_ok=True)

    t0 = time.time()
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
    print(f"Modèle XTTS-v2 chargé en {time.time()-t0:.1f}s")

    for tier in TIERS:
        pays, slug, text = WORLD_TOUR_COUNTRIES[tier]
        expected_slug = slugify(pays)
        assert slug == expected_slug, f"slug incohérent pour {pays} : {slug!r} vs {expected_slug!r}"
        filename = f"{tier + 1:03d}_{slug}.wav"
        out_path = os.path.join(OUT_DIR, filename)
        t0 = time.time()
        tts.tts_to_file(
            text=text,
            speaker_wav=REFERENCE_VOICE,
            language="fr",
            file_path=out_path,
        )
        print(f"[{tier + 1:03d}] {pays} -> {out_path}  ({time.time()-t0:.1f}s)")

    print("Terminé.")


if __name__ == "__main__":
    main()
