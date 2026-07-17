"""Configuration et état de jeu pour Petanque Challenge 2 - Round the Clock.

Port fidèle du jeu Lua/Defold d'origine (voir
ressources/Petanque-challenge-Round-the-clock/petanquechallengeV2Sourcecode/).
Entrée dédiée (main_round_the_clock.py), indépendante de Fanny World Tour,
mais qui lit/complète le même config.ini partagé à la racine du dépôt.
"""
import os.path
import configparser
import random

import pygame

from Scripts.camera_calibration import load_camera_settings

clock = pygame.time.Clock()

channel_click = pygame.mixer.Channel(0)
channel_hit = pygame.mixer.Channel(1)
channel_miss = pygame.mixer.Channel(2)
channel_voice = pygame.mixer.Channel(3)

_DEFAULT_SECTIONS = {
    "Screen": {
        "Fullscreen": "True",
        "CRT": "False",
    },
    "Audio": {
        "Music": "True",
        "Effects": "True",
        "FadeoutTime": "1000",
    },
    "CamActivation": {
        "Webcam": "True",
    },
    "Resolution": {
        "Resolution": "1080",
    },
    "Debug": {
        "DebugLine": "False",
        "FPS": "30",
        "ShowFps": "False",
        "DebugCam": "False",
        "Credit": "1",
        "FreePlay": "False",
    },
    "RoundTheClock": {
        "targets": "7",
        "default_players": "2",
        "min_players": "1",
        "max_players": "6",
        "default_rounds": "3",
        "min_rounds": "3",
        "max_rounds": "12",
        "shots_per_turn": "3",
        "hit_cooldown_ms": "2000",
        "menu_cooldown_ms": "200",
        "banner_duration_s": "5",
    },
}


def _ensure_config():
    """Crée config.ini s'il n'existe pas, ou complète les sections
    manquantes (ex : config.ini généré par Fanny World Tour sans
    [RoundTheClock], ou l'inverse). Les sections propres à Fanny
    (TimeSetting, BonusTime, WorldTour, Score) ne sont ni touchées ni
    requises ici."""
    cfg = configparser.ConfigParser()
    if os.path.exists("config.ini"):
        cfg.read("config.ini")

    changed = not os.path.exists("config.ini")
    for section, keys in _DEFAULT_SECTIONS.items():
        if section not in cfg:
            cfg[section] = {}
            changed = True
        for key, value in keys.items():
            if key not in cfg[section]:
                cfg[section][key] = value
                changed = True

    if changed:
        with open("config.ini", "w") as f:
            cfg.write(f)

    return cfg


config = _ensure_config()

try:
    Fullscreen = config.getboolean("Screen", "Fullscreen")
    crt = config.getboolean("Screen", "CRT", fallback=False)
    background_music = config.getboolean("Audio", "Music")
    sound_effects_enabled = config.getboolean("Audio", "Effects")
    FadeoutTime = int(config["Audio"]["FadeoutTime"])
    active_webcam = config.getboolean("CamActivation", "Webcam")
    # Résolution, zone de tir, cadence d'analyse : propres à CHAQUE caméra,
    # donc dans camera_calibration.json (pas config.ini) - voir
    # Scripts/camera_calibration.py et calibrate_camera.py.
    _cam_settings = load_camera_settings()
    cam_fps = _cam_settings["CamFPS"]
    camera_index = _cam_settings["CameraIndex"]
    capture_width = _cam_settings["CaptureWidth"]
    capture_height = _cam_settings["CaptureHeight"]
    zone_width_percent = _cam_settings["ZoneWidthPercent"]
    zone_height_percent = _cam_settings["ZoneHeightPercent"]
    zone_offset_x_percent = _cam_settings["ZoneOffsetXPercent"]
    zone_offset_y_percent = _cam_settings["ZoneOffsetYPercent"]
    resolution = int(config["Resolution"]["Resolution"])
    debug_line = config.getboolean("Debug", "DebugLine")
    FPS = int(config["Debug"]["FPS"])
    ShowFPS = config.getboolean("Debug", "ShowFps")
    DebugCam = config.getboolean("Debug", "DebugCam")
    credit_left = int(config["Debug"].get("Credit", "1"))
    free_play = config.getboolean("Debug", "FreePlay", fallback=False)

    TARGET_COUNT = int(config["RoundTheClock"]["targets"])
    DEFAULT_PLAYERS = int(config["RoundTheClock"]["default_players"])
    MIN_PLAYERS = int(config["RoundTheClock"]["min_players"])
    MAX_PLAYERS = int(config["RoundTheClock"]["max_players"])
    DEFAULT_ROUNDS = int(config["RoundTheClock"]["default_rounds"])
    MIN_ROUNDS = int(config["RoundTheClock"]["min_rounds"])
    MAX_ROUNDS = int(config["RoundTheClock"]["max_rounds"])
    SHOTS_PER_TURN = int(config["RoundTheClock"]["shots_per_turn"])
    HIT_COOLDOWN_MS = int(config["RoundTheClock"]["hit_cooldown_ms"])
    MENU_COOLDOWN_MS = int(config["RoundTheClock"]["menu_cooldown_ms"])
    BANNER_DURATION_S = int(config["RoundTheClock"]["banner_duration_s"])
except (KeyError, ValueError, configparser.Error) as e:
    print(f"Erreur dans config.ini : {e}. Supprimez le fichier pour le régénérer.")
    raise SystemExit(1)

if resolution == 1080:
    LARGEUR_ECRAN = 1920
    HAUTEUR_ECRAN = 1080
elif resolution == 720:
    LARGEUR_ECRAN = 1280
    HAUTEUR_ECRAN = 720
elif resolution == 360:
    LARGEUR_ECRAN = 640
    HAUTEUR_ECRAN = 360
elif resolution == 240:
    LARGEUR_ECRAN = 426
    HAUTEUR_ECRAN = 240
else:
    LARGEUR_ECRAN = 1024
    HAUTEUR_ECRAN = 768

print("résolution " + str(LARGEUR_ECRAN) + " X " + str(HAUTEUR_ECRAN))

# DejaVu Sans (portée du jeu Defold d'origine, assets/font/DejaVuSans.ttf) :
# police très lisible à toutes tailles, préférée à la police décorative
# "NEON GLOW" de Fanny World Tour pour ce jeu où le texte porte des
# informations de jeu (scores, règles) à lire vite, pas juste un logo.
# FontDelN = remplissage plein ; FontDelN+1 = même police en gras, utilisée
# par draw_text() pour dessiner un contour sombre qui détache le texte du
# fond (planches de bois chargées visuellement).
_DEJAVU = "./assets/RoundTheClock/Fonts/DejaVuSans.ttf"
Fontsize = round(HAUTEUR_ECRAN / 9)
Fontsize2 = round(HAUTEUR_ECRAN / 18)
Fontsize3 = round(HAUTEUR_ECRAN / 26)
FontsizeWait = round(HAUTEUR_ECRAN / 5.5)


def _bold_font(path, size):
    f = pygame.font.Font(path, size)
    f.set_bold(True)
    return f


FontDel1 = pygame.font.Font(_DEJAVU, Fontsize)
FontDel2 = _bold_font(_DEJAVU, Fontsize)
FontDel3 = pygame.font.Font(_DEJAVU, Fontsize2)
FontDel4 = _bold_font(_DEJAVU, Fontsize2)
FontDel5 = pygame.font.Font(_DEJAVU, Fontsize3)
FontDel6 = _bold_font(_DEJAVU, Fontsize3)
FontWait1 = _bold_font(_DEJAVU, FontsizeWait)
FontWait2 = _bold_font(_DEJAVU, FontsizeWait)

red = (204, 0, 0)
redlight = (239, 41, 41)
orange = (245, 121, 0)
orangelight = (252, 175, 62)
yellow = (237, 212, 0)
yellowlight = (255, 255, 79)
blue = (66, 0, 255)
bluelight = (66, 236, 255)
green = (0, 255, 0)
greenlight = (0, 200, 0)
white = (255, 255, 255)
whitelight = (230, 230, 230)

# ---------------------------------------------------------------------
# État de partie mutable (équivalent des globales Lua partagées entre
# main.script/ingame.script/Target1-7.script dans la source Defold).
# Joueurs indexés 0..5 en interne (joueur 1 = index 0).
# ---------------------------------------------------------------------

NumberPlayer = DEFAULT_PLAYERS
NombreDeTours = DEFAULT_ROUNDS
SoundVolume = background_music or sound_effects_enabled

tour = 1
joueur_en_cours = 0
reste = SHOTS_PER_TURN
cible_en_cours = 0
old_cible_en_cours = None

scorejoueurs = [0] * MAX_PLAYERS
hitcount = [0] * MAX_PLAYERS
misscount = [0] * MAX_PLAYERS

activekeyboard = True
lasthit = -10 ** 9
lastchange = -10 ** 9


def reset_game():
    """Ne touche PAS à activekeyboard/lasthit : ces deux variables portent
    le cooldown démarré par la touche (ex : O pour "démarrer") qui vient
    d'appeler cette fonction depuis le menu. Les réinitialiser ici annulait
    ce cooldown et laissait un éventuel rebond du capteur physique (ou
    l'événement clavier suivant) être aussitôt interprété comme un tir sur
    la cible 7 (cochonet) alors que la cible désignée est la cible 1 - d'où
    un raté enregistré immédiatement pour le joueur 1 au lancement."""
    global tour, joueur_en_cours, reste, cible_en_cours, old_cible_en_cours
    global scorejoueurs, hitcount, misscount, lastchange
    tour = 1
    joueur_en_cours = 0
    reste = SHOTS_PER_TURN
    cible_en_cours = 0
    old_cible_en_cours = None
    scorejoueurs = [0] * MAX_PLAYERS
    hitcount = [0] * MAX_PLAYERS
    misscount = [0] * MAX_PLAYERS
    lastchange = -10 ** 9
    determiner_cible_a_toucher()


def determiner_cible_a_toucher():
    """Reproduit ingame.script::determinerCibleAToucherPourLeJoueur : tant
    que le joueur courant a moins de TARGET_COUNT hits, la cible imposée
    suit l'ordre hitcount+1 (basé sur les REUSSITES, pas les tirs). Au-delà,
    cible aléatoire, jamais deux fois la même de suite."""
    global cible_en_cours, old_cible_en_cours
    if hitcount[joueur_en_cours] < TARGET_COUNT:
        cible_en_cours = hitcount[joueur_en_cours]
    else:
        old = cible_en_cours
        new = old
        while new == old:
            new = random.randint(0, TARGET_COUNT - 1)
        cible_en_cours = new
    old_cible_en_cours = cible_en_cours
