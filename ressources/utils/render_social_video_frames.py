# -*- coding: utf-8 -*-
"""Rend les frames statiques nécessaires aux vidéos "réseaux sociaux" du
quizz (une par pays) : intro (hook - écran d'accueil + texte annonçant le
pays et le format quizz+pétanque), question x5 (asking/feedback/
explanation), récap, outro (pays suivant + CTA like/abonnement).

Réutilise le vrai code de rendu de main_quizz.py (title_screen_image,
draw_quiz(), draw_quiz_text_wrapped(), start_quiz()...) en exécutant son
code source dans un dict globals qu'on contrôle depuis l'extérieur (voir
mémoire feedback_headless_testing_technique) - pas de duplication de la
logique d'affichage.

Le logo Fanny qui tourne (intro/outro) N'EST PAS pré-rendu ici : il est
composité et animé ensuite par ffmpeg (filtre `rotate`) dans
build_social_videos.py, pour éviter de produire des centaines de PNG par
pays (le disque `/tmp` de la sandbox est une tmpfs limitée à quelques Go -
on a fait déborder cet espace une première fois en pré-rendant les frames
d'animation ; toutes les images de ce script vont donc directement sur le
disque du projet, pas /tmp).

IMPORTANT : à lancer avec le venv du JEU (pygame), pas un venv générique :
    /home/adm1/pythonvenv/bin/python3 ressources/utils/render_social_video_frames.py [tier1 tier2 ...]

Sans argument : rend les 112 pays. Le manifest existant (s'il y en a un)
est complété/mis à jour pour les tiers demandés, jamais écrasé en entier -
relancer pour quelques pays seulement ne perd pas le travail déjà fait sur
les autres.
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['GLOG_minloglevel'] = '2'
import sys
import json

sys.path.insert(0, "/home/adm1/Fanny_P-tanque_World_Tour")
os.chdir("/home/adm1/Fanny_P-tanque_World_Tour")

import pygame
pygame.init()

OUT_DIR = "/home/adm1/Fanny_P-tanque_World_Tour/ressources/social_videos/_work/frames"
MANIFEST_PATH = "/home/adm1/Fanny_P-tanque_World_Tour/ressources/social_videos/_work/manifest.json"
os.makedirs(OUT_DIR, exist_ok=True)

TIERS = [int(a) for a in sys.argv[1:]] or list(range(112))

jumped = [False]
done = [False]
my_globals = {"__name__": "__main__", "__file__": "main_quizz.py"}
orig_flip = pygame.display.flip


def audio_len(text, quiz_audio_path):
    path = quiz_audio_path(text)
    try:
        return pygame.mixer.Sound(path).get_length()
    except (pygame.error, FileNotFoundError):
        return None


def render_hook_background(tier, lines, out_path):
    """Fond statique de l'écran d'accueil + texte (sans le logo qui
    tourne, composité ensuite par ffmpeg)."""
    ecran = my_globals["ecran"]
    title_screen_image = my_globals["title_screen_image"]
    draw_quiz_text_wrapped = my_globals["draw_quiz_text_wrapped"]
    draw_crt = my_globals["draw_crt"]
    LARGEUR_ECRAN = my_globals["LARGEUR_ECRAN"]
    HAUTEUR_ECRAN = my_globals["HAUTEUR_ECRAN"]

    ecran.blit(title_screen_image, (0, 0))
    for text, y_frac, col, font in lines:
        draw_quiz_text_wrapped(
            text, LARGEUR_ECRAN / 2, HAUTEUR_ECRAN * y_frac, True, font, col,
            LARGEUR_ECRAN * 0.82, HAUTEUR_ECRAN * 0.075,
        )
    draw_crt()
    pygame.image.save(ecran, out_path)


def render_all():
    quiz_audio_path = my_globals["quiz_audio_path"]
    QUIZ_QUESTIONS = my_globals["QUIZ_QUESTIONS"]
    WORLD_TOUR_COUNTRIES = my_globals["WORLD_TOUR_COUNTRIES"]
    draw_quiz = my_globals["draw_quiz"]
    start_quiz = my_globals["start_quiz"]
    QUIZ_FONT_PATH = my_globals["QUIZ_FONT_PATH"]
    HAUTEUR_ECRAN = my_globals["HAUTEUR_ECRAN"]
    N = len(WORLD_TOUR_COUNTRIES)

    hook_font_title = pygame.font.Font(QUIZ_FONT_PATH, round(HAUTEUR_ECRAN * 0.075))
    hook_font_cta = pygame.font.Font(QUIZ_FONT_PATH, round(HAUTEUR_ECRAN * 0.042))

    manifest = {}
    if os.path.isfile(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)

    for tier in TIERS:
        pays = WORLD_TOUR_COUNTRIES[tier][0]

        intro_bg = f"{OUT_DIR}/{tier:03d}_intro_bg.png"
        render_hook_background(
            tier,
            [
                (f"Aujourd'hui : {pays} !", 0.42, 4, hook_font_title),
                ("Teste tes connaissances sur ce pays et sa pétanque !", 0.62, 5, hook_font_cta),
            ],
            intro_bg,
        )

        start_quiz(tier)
        country_manifest = []
        for qi in range(5):
            my_globals["quiz_index"] = qi
            question, choices, correct_index, explanation = QUIZ_QUESTIONS[tier][qi]

            my_globals["quiz_phase"] = "asking"
            my_globals["quiz_selected"] = None
            draw_quiz()
            asking_path = f"{OUT_DIR}/{tier:03d}_q{qi}_asking.png"
            pygame.image.save(pygame.display.get_surface(), asking_path)
            asking_audio = [quiz_audio_path(t) for t in [question] + choices]

            my_globals["quiz_selected"] = correct_index
            my_globals["quiz_phase"] = "feedback"
            draw_quiz()
            feedback_path = f"{OUT_DIR}/{tier:03d}_q{qi}_feedback.png"
            pygame.image.save(pygame.display.get_surface(), feedback_path)

            my_globals["quiz_phase"] = "explanation"
            draw_quiz()
            explanation_path = f"{OUT_DIR}/{tier:03d}_q{qi}_explanation.png"
            pygame.image.save(pygame.display.get_surface(), explanation_path)
            explanation_audio = quiz_audio_path(explanation)
            explanation_duration = audio_len(explanation, quiz_audio_path)

            country_manifest.append({
                "asking_image": asking_path,
                "asking_audio": asking_audio,
                "feedback_image": feedback_path,
                "explanation_image": explanation_path,
                "explanation_audio": explanation_audio,
                "explanation_duration": explanation_duration,
            })

        my_globals["quiz_phase"] = "recap"
        my_globals["quiz_score"] = 5
        draw_quiz()
        recap_path = f"{OUT_DIR}/{tier:03d}_recap.png"
        pygame.image.save(pygame.display.get_surface(), recap_path)

        next_tier = (tier + 1) % N
        next_pays = WORLD_TOUR_COUNTRIES[next_tier][0]
        outro_bg = f"{OUT_DIR}/{tier:03d}_outro_bg.png"
        render_hook_background(
            tier,
            [
                (f"Prochain pays : {next_pays} !", 0.42, 4, hook_font_title),
                ("Like & abonne-toi pour suivre le tour du monde !", 0.62, 5, hook_font_cta),
            ],
            outro_bg,
        )

        manifest[str(tier)] = {
            "pays": pays,
            "next_pays": next_pays,
            "intro_bg": intro_bg,
            "questions": country_manifest,
            "recap_image": recap_path,
            "outro_bg": outro_bg,
        }
        print(f"tier {tier} ({pays}) : frames rendues (intro/outro inclus)", flush=True)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"manifest écrit ({len(manifest)} pays au total)")


def flip_hook():
    orig_flip()
    if not jumped[0] and "quiz_total_correct" in my_globals:
        jumped[0] = True
        try:
            render_all()
        finally:
            done[0] = True
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))


pygame.display.flip = flip_hook

with open("main_quizz.py", encoding="utf-8") as f:
    source = f.read()
code = compile(source, "main_quizz.py", "exec")

try:
    exec(code, my_globals)
except SystemExit:
    pass

print("OK, done:", done[0])
