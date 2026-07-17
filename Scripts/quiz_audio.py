# -*- coding: utf-8 -*-
"""Chemin des fichiers audio TTS (gTTS) du quizz : un mp3 par texte unique
(question, choix ou explication), nommé d'après un hash du texte lui-même
- permet de retrouver le bon fichier à partir du texte affiché, sans table
de correspondance séparée à maintenir/synchroniser.

Généré par ressources/utils/generate_quiz_audio.py, à lancer avec le venv
gTTS dédié (pas le venv du jeu, gTTS n'y est pas installé) :
    /home/adm1/iatools/gtts/venv/bin/python3 ressources/utils/generate_quiz_audio.py

Module volontairement sans dépendance (stdlib uniquement) : importé à la
fois par le générateur (venv gTTS) et par main_quizz.py (venv du jeu).
"""
import hashlib
import os

QUIZ_AUDIO_DIR = "assets/Sounds/QuizzTTS"


def quiz_audio_hash(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:20]


def quiz_audio_path(text):
    return os.path.join(QUIZ_AUDIO_DIR, f"{quiz_audio_hash(text)}.mp3")
