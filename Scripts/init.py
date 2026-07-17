import pygame
from pygame import *
import os.path
import configparser
import random
from Scripts.camera_calibration import load_camera_settings


#initialise timer for game
clock = pygame.time.Clock()
old_timer = pygame.time.get_ticks()
game_timer = pygame.time.get_ticks()

channel1 = pygame.mixer.Channel(0)
channel2 = pygame.mixer.Channel(1)
channel2.set_volume(0.1)
channel3 = pygame.mixer.Channel(2)
channel4 = pygame.mixer.Channel(3)  # voix de Fanny (répliques)
channel4.set_volume(0.9)
channel5 = pygame.mixer.Channel(4)  # hymne national du pays courant (piste A, crossfade)
channel5.set_volume(0.18)  # abaissé depuis 0.5 : trop fort par rapport aux voix (retour utilisateur)
channel6 = pygame.mixer.Channel(5)  # hymne national du pays courant (piste B, crossfade)
channel6.set_volume(0.18)
channel7 = pygame.mixer.Channel(6)  # narration audio du quizz (question/choix/explication, TTS)
channel7.set_volume(0.9)

cibleencours = 2
score = 0
high_score = 0
gamestate = 0
oldcibleencours = cibleencours
continuer = True
current_time = 0
old_current_time = 0
affichage = True
cam_fps = 5


def save_high_score(new_score):
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    if "Score" not in cfg:
        cfg["Score"] = {}
    cfg["Score"]["high_score"] = str(new_score)
    with open("config.ini", "w") as f:
        cfg.write(f)


def save_high_score_hardcore(new_score):
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    if "Hardcore" not in cfg:
        cfg["Hardcore"] = {}
    cfg["Hardcore"]["high_score"] = str(new_score)
    with open("config.ini", "w") as f:
        cfg.write(f)


def save_high_score_quizz(new_score):
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    if "Quizz" not in cfg:
        cfg["Quizz"] = {}
    cfg["Quizz"]["high_score"] = str(new_score)
    with open("config.ini", "w") as f:
        cfg.write(f)


# parse config.ini and create if not exist
if not os.path.exists("config.ini"):
    f = open("config.ini", "w")
    f.write("[TimeSetting]\n")
    f.write("intro_length = 10\n")
    f.write("game_length = 60\n")
    f.write("ending_length = 10\n")
    f.write("splash_length = 7\n")
    f.write("\n")
    f.write("[BonusTime]\n")
    f.write("time = 5\n")
    f.write("country_change_time = 30\n")
    f.write("\n")
    f.write("[WorldTour]\n")
    f.write("hits_per_country = 5\n")
    f.write("\n")
    f.write("[CamActivation]\n")
    f.write("Webcam = True\n")
    f.write("\n")
    f.write("[Screen]\n")
    f.write("Fullscreen = True\n")
    f.write("CRT = False\n")
    f.write("\n")
    f.write("[Audio]\n")
    f.write("Music = True\n")
    f.write("Effects = True\n")
    f.write("FadeoutTime = 1000\n")
    f.write("\n")
    f.write("[Resolution]\n")
    f.write("#resolution value 1080 720 360 240 if empty resolution will be set to 1024x768\n")
    f.write("Resolution = 1080\n")
    f.write("\n")
    f.write("[Debug]\n")
    f.write("DebugLine = False\n")
    f.write("FPS = 20\n")
    f.write("ShowFps = False\n")
    f.write("DebugCam = False\n")
    f.write("Credit = 1\n")
    f.write("FreePlay = False\n")
    f.write("\n")
    f.write("[Score]\n")
    f.write("high_score = 0\n")
    f.write("\n")
    f.write("[Hardcore]\n")
    f.write("high_score = 0\n")
    f.write("hits_per_country = 5\n")
    f.write("\n")
    f.write("[Quizz]\n")
    f.write("high_score = 0\n")
    f.write("\n")
    f.write("[RoundTheClock]\n")
    f.write("targets = 7\n")
    f.write("default_players = 2\n")
    f.write("min_players = 1\n")
    f.write("max_players = 6\n")
    f.write("default_rounds = 3\n")
    f.write("min_rounds = 3\n")
    f.write("max_rounds = 12\n")
    f.write("shots_per_turn = 3\n")
    f.write("hit_cooldown_ms = 2000\n")
    f.write("menu_cooldown_ms = 200\n")
    f.write("banner_duration_s = 5\n")
    f.close()


if os.path.exists("config.ini"):
    try:
        with open("config.ini", "r") as f:
            config = configparser.ConfigParser()
            config.read_file(f)
            intro_length = int(config["TimeSetting"]["intro_length"])
            game_length = int(config["TimeSetting"]["game_length"])
            ending_length = int(config["TimeSetting"]["ending_length"])
            splash_length = int(config["TimeSetting"].get("splash_length", "7"))
            bonus_time = int(config["BonusTime"]["time"])
            country_change_bonus_time = int(config["BonusTime"].get("country_change_time", "30"))
            hits_per_country = int(config["WorldTour"].get("hits_per_country", "5")) if "WorldTour" in config else 5
            active_webcam = config.getboolean("CamActivation", "Webcam")
            # Résolution, zone de tir, cadence d'analyse : propres à CHAQUE
            # caméra, donc dans camera_calibration.json (pas config.ini) -
            # voir Scripts/camera_calibration.py et calibrate_camera.py.
            _cam_settings = load_camera_settings()
            cam_fps = _cam_settings["CamFPS"]
            camera_index = _cam_settings["CameraIndex"]
            capture_width = _cam_settings["CaptureWidth"]
            capture_height = _cam_settings["CaptureHeight"]
            zone_width_percent = _cam_settings["ZoneWidthPercent"]
            zone_height_percent = _cam_settings["ZoneHeightPercent"]
            zone_offset_x_percent = _cam_settings["ZoneOffsetXPercent"]
            zone_offset_y_percent = _cam_settings["ZoneOffsetYPercent"]
            Fullscreen = config.getboolean("Screen", "Fullscreen")
            crt = config.getboolean("Screen", "CRT", fallback=False)
            background_music = config.getboolean("Audio", "Music")
            sound_effects = config.getboolean("Audio", "Effects")
            FadeoutTime = int(config["Audio"]["FadeoutTime"])
            debug_line = config.getboolean("Debug", "DebugLine")
            resolution = int(config["Resolution"]["Resolution"])
            FPS = int(config["Debug"]["FPS"])
            ShowFPS = config.getboolean("Debug", "ShowFps")
            DebugCam = config.getboolean("Debug", "DebugCam")
            credit_left = int(config["Debug"]["Credit"])
            free_play = config.getboolean("Debug", "FreePlay", fallback=False)
            if "Score" in config and "high_score" in config["Score"]:
                high_score = int(config["Score"]["high_score"])
            hardcore_high_score = int(config["Hardcore"]["high_score"]) if "Hardcore" in config and "high_score" in config["Hardcore"] else 0
            hardcore_hits_per_country = int(config["Hardcore"]["hits_per_country"]) if "Hardcore" in config and "hits_per_country" in config["Hardcore"] else 5
            quizz_high_score = int(config["Quizz"]["high_score"]) if "Quizz" in config and "high_score" in config["Quizz"] else 0
    except (KeyError, ValueError, configparser.Error) as e:
        print(f"Erreur dans config.ini : {e}. Supprimez le fichier pour le régénérer.")
        raise SystemExit(1)

time_left = intro_length

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

Fontsize = round(HAUTEUR_ECRAN/10)
Fontsize2 = round(HAUTEUR_ECRAN/20)
# Alfa Slab One (assets/fonts/AlfaSlabOne-Regular.ttf, licence OFL) remplace
# "Neon Glow" depuis le 2026-07-16 - choisie avec l'utilisateur (esprit
# affiche de voyage vintage) pour gérer les caractères accentués
# ("Amérique", "Océanie"...), que Neon Glow n'avait pas. Une seule graisse
# (pas de variante "hollow" comme Neon Glow) : FontDel2/FontDel4 pointent
# sur la même police que FontDel1/FontDel3, draw_text() simule un ombre
# portée plutôt qu'un halo pour le rendu à deux calques.
FontDel1 = pygame.font.Font("./assets/fonts/AlfaSlabOne-Regular.ttf", Fontsize)
FontDel2 = FontDel1
FontDel3 = pygame.font.Font("./assets/fonts/AlfaSlabOne-Regular.ttf", Fontsize2)
FontDel4 = FontDel3

# Palette "warm_muted" (2026-07-16, choisie avec l'utilisateur parmi 3
# options) : les couleurs néon d'origine (calibrées pour Neon Glow)
# détonnaient avec la police Alfa Slab One / l'esthétique affiche de
# voyage vintage (voir draw_text() dans main.py). Désaturées et
# réchauffées vers les tons sépia/terracotta de l'illustration, tout en
# gardant assez de saturation pour rester lisibles sur les fonds de pays
# très variés (jungle, désert, ciel...) du jeu.
red = (150, 40, 35)
redlight = (206, 96, 72)
orange = (168, 110, 40)
orangelight = (224, 164, 80)
yellow = (172, 140, 50)
yellowlight = (230, 196, 120)
blue = (50, 90, 110)
bluelight = (108, 160, 182)
green = (70, 100, 50)
greenlight = (138, 168, 96)
