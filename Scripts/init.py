import pygame
from pygame import *
import os.path
import configparser
import random


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
channel5.set_volume(0.5)
channel6 = pygame.mixer.Channel(5)  # hymne national du pays courant (piste B, crossfade)
channel6.set_volume(0.5)

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
music_fadeout_started = False


def save_high_score(new_score):
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    if "Score" not in cfg:
        cfg["Score"] = {}
    cfg["Score"]["high_score"] = str(new_score)
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
    f.write("CamFPS = 5\n")
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
    f.write("\n")
    f.write("[Score]\n")
    f.write("high_score = 0\n")
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
            cam_fps = int(config["CamActivation"].get("CamFPS", "5"))
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
            if "Score" in config and "high_score" in config["Score"]:
                high_score = int(config["Score"]["high_score"])
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
FontDel1 = pygame.font.Font("./assets/fonts/NEON GLOW.otf", Fontsize)
FontDel2 = pygame.font.Font("./assets/fonts/NEON GLOW-Hollow.otf", Fontsize)
FontDel3 = pygame.font.Font("./assets/fonts/NEON GLOW.otf", Fontsize2)
FontDel4 = pygame.font.Font("./assets/fonts/NEON GLOW-Hollow.otf", Fontsize2)

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
