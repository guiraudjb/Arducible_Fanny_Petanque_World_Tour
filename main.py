#---------------------------------IMPORTS-------------------------------
import os
os.environ['GLOG_minloglevel'] = '2'  # supprime les logs verbeux de MediaPipe/TFLite
import pygame
from pygame import *
pygame.init()
from Scripts.init import * # load config.ini and some variables
from Scripts.Sprites import *# load sprites
from Scripts.dialogues import is_tour_complete, WORLD_TOUR_MODES
import cv2

TARGET_KEYS = [pygame.K_e, pygame.K_r, pygame.K_t]
CONTINENT_SELECT_TIMEOUT = 60  # secondes avant lancement auto de la partie sur le mode affiché
#---------------------Procedures et fonctions---------------------------

def init_cibles():
    global cible1
    global cible2
    global cible3
    cible1 = Cible()
    cible1.rect.x = LARGEUR_ECRAN * 3/20 - LARGEUR_ECRAN*0.25/2
    cible1.rect.y = HAUTEUR_ECRAN * 16/20 - HAUTEUR_ECRAN*0.44/2

    cible2 = Cible()
    cible2.rect.x = LARGEUR_ECRAN *10/20 - LARGEUR_ECRAN*0.25/2
    cible2.rect.y = HAUTEUR_ECRAN * 16/20 - HAUTEUR_ECRAN*0.44/2

    cible3 = Cible()
    cible3.rect.x = LARGEUR_ECRAN * 17/20 - LARGEUR_ECRAN*0.25/2
    cible3.rect.y = HAUTEUR_ECRAN * 16/20 - HAUTEUR_ECRAN*0.44/2

def init_mode_select_cibles():
    """Trois boules (gauche=E, centre=R, droite=T) affichées sur l'écran de
    choix du continent : le joueur n'a que le socle physique devant lui
    (pas de clavier), il faut donc montrer les boules plutôt que des
    lettres pour indiquer précédent/valider/suivant - demande utilisateur
    du 2026-07-16, même principe que les cibles du quizz
    (init_quiz_cibles/main_quizz.py)."""
    global mode_select_cibles
    size = (LARGEUR_ECRAN * 0.07, HAUTEUR_ECRAN * 0.10)
    mode_select_cibles = [Cible(size=size) for _ in range(3)]
    mode_select_cibles[0].rect.center = (LARGEUR_ECRAN * 4/20, HAUTEUR_ECRAN * 14/20)
    mode_select_cibles[1].rect.center = (LARGEUR_ECRAN * 10/20, HAUTEUR_ECRAN * 14/20)
    mode_select_cibles[2].rect.center = (LARGEUR_ECRAN * 17/20, HAUTEUR_ECRAN * 14/20)


def next_gamestate():
    """Gère les transitions 1->2 (fin de manche) et 2->0 (retour à
    l'accueil). La transition 0->(mode select)->(countdown)->1 passe par
    start_mode_select()/start_pregame_countdown()/start_game_with_mode()
    plutôt que par ici, depuis l'ajout des modes par continent le
    2026-07-15."""
    global time_left
    global gamestate
    global score
    global intro_length
    global ending_length
    global ingamebackground
    global high_score
    if gamestate == 1:
        gamestate = 2
        ingamebackground.freeze_for_ending()
        score = score + max(time_left, 0)  # score final = points + temps restant
        # Vérifié une seule fois ici, au moment où le score devient
        # définitif (pas à chaque frame de l'écran de fin comme avant :
        # save_high_score() réécrivait config.ini plusieurs centaines de
        # fois sur les ~10s de l'écran de fin, sans changer le résultat
        # affiché puisque score et high_score restent fixes une fois
        # l'écran de fin atteint) - trouvé en vérifiant la correspondance
        # score final/high score, demande utilisateur du 2026-07-16.
        if mode_is_full_tour and score >= high_score:
            high_score = score
            save_high_score(high_score)
        time_left = ending_length
        fanny_companion.stop_anthem()
    elif gamestate == 2:
        gamestate = 0
        time_left = intro_length

def start_mode_select():
    """Dès qu'un crédit est disponible (gamestate 0) : écran de choix du
    continent (voir Scripts.dialogues.WORLD_TOUR_MODES), affiché AVANT le
    décompte "GAME START IN" (désormais dans start_pregame_countdown(),
    gamestate 4) - demande utilisateur du 2026-07-15 : l'écran de choix du
    continent doit se situer entre l'accueil et le countdown, pas après.
    Navigation carrousel E (précédent) / R (valider) / T (suivant) - seuls
    boutons physiques disponibles sur la borne. time_left amorce le
    timeout de CONTINENT_SELECT_TIMEOUT secondes (voir gamestate 3 dans la
    boucle principale) : au bout de ce délai sans choix du joueur, la
    partie se lance sur le mode actuellement affiché par le carrousel,
    comme un appui sur R - demande utilisateur du 2026-07-16."""
    global gamestate, mode_select_index, time_left
    gamestate = 3
    mode_select_index = 0
    time_left = CONTINENT_SELECT_TIMEOUT

def start_pregame_countdown():
    """Après validation du continent (gamestate 3, touche R ou timeout de
    CONTINENT_SELECT_TIMEOUT) : décompte "GAME START IN" repris de
    l'ancien gamestate 0 (avant l'ajout de la sélection de continent),
    déplacé après le choix plutôt qu'avant. La musique de menu, laissée
    intacte pendant tout l'écran de sélection du continent (demande
    utilisateur du 2026-07-16), ne commence à s'éteindre qu'à partir d'ici
    - les hymnes nationaux (FannyCompanion) prennent le relai pendant la
    partie."""
    global gamestate, time_left
    channel1.fadeout(9000)
    gamestate = 4
    time_left = intro_length

def start_game_with_mode(mode_index):
    """Lance la manche de tir avec le mode choisi à l'écran de sélection :
    reprend ce que faisait next_gamestate() pour la transition 0->1, en
    bornant en plus la progression pays à la liste de tiers du mode
    (fanny_companion.set_mode)."""
    global gamestate, time_left, score, game_length, ingamebackground, webcam_compatibility, mode_is_full_tour
    _name, tiers = WORLD_TOUR_MODES[mode_index]
    mode_is_full_tour = (mode_index == 0)
    fanny_companion.set_mode(tiers)
    gamestate = 1
    ingamebackground.reset(webcam_compatibility)
    time_left = game_length
    score = 0
    fanny_companion.reset()

def ciblealeatoire():
    global cibleencours
    global oldcibleencours
    while cibleencours == oldcibleencours:
        cibleencours = random.randint(1, 3)
    oldcibleencours = cibleencours
    if sound_effects == True:
        if cibleencours == 1:
            channel3.play(sfx_gauche)
        if cibleencours == 2:
            channel3.play(sfx_centre)
        if cibleencours == 3:
            channel3.play(sfx_droite)

def showcam():
    ecran.blit(mycam.image, (LARGEUR_ECRAN/2-mycam.width/2, 0))

def countdown():
    global old_timer
    global game_timer
    global time_left
    game_timer = pygame.time.get_ticks()
    if game_timer - old_timer >= 1000:
        time_left = time_left - 1
        old_timer = game_timer

def update_score():
    global score
    global time_left
    global channel2
    if sound_effects == True:
        channel2.play(sfx_hit)
    score = score + 1
    time_left = time_left + bonus_time
    if fanny_companion.on_score_update(score):
        time_left = time_left + country_change_bonus_time

def draw_camring():
    global ecran
    global camring
    if mycam.zoneinterdite == True:
        draw_go_to_shooting_zone()
        camring.image = camring.images[0]
        ecran.blit(camring.image, camring.rect)
    else:
        camring.image = camring.images[1]
        ecran.blit(camring.image, camring.rect)

def draw_text(text,x,y,blink,center,fnt,col):
    if fnt == 1:
        font1=FontDel1.render
        font2=FontDel2.render
    if fnt == 2:
        font1=FontDel3.render
        font2=FontDel4.render

    if col == 1:
        color1=red
        color2=redlight
    if col == 2:
        color1=orange
        color2=orangelight
    if col == 3:
        color1=yellow
        color2=yellowlight
    if col == 4:
        color1=blue
        color2=bluelight
    if col == 5:
        color1=green
        color2=greenlight

    text_img = font1(str(text),True,color1)
    text_img2 = font2(str(text),True,color2)

    if blink and not affichage:
        return

    # Alfa Slab One n'a pas de variante "hollow" comme Neon Glow : au lieu
    # d'un halo superposé à la même position, text_img (color1, plus
    # sombre) sert d'ombre portée légèrement décalée derrière text_img2
    # (color2, plus clair) - effet lettrage d'affiche vintage.
    w2, h2 = text_img2.get_rect().size
    offset = max(2, round(h2 * 0.05))
    if center:
        ecran.blit(text_img,  (x - w2/2 + offset, y - h2/2 + offset))
        ecran.blit(text_img2, (x - w2/2, y - h2/2))
    else:
        ecran.blit(text_img,  (x + offset, y + offset))
        ecran.blit(text_img2, (x, y))

def debug_lines():
    for i in range(1, 20):
        pygame.draw.line(ecran, red, (LARGEUR_ECRAN*i/20, 0), (LARGEUR_ECRAN*i/20, HAUTEUR_ECRAN), 1)
        pygame.draw.line(ecran, red, (0, HAUTEUR_ECRAN*i/20), (LARGEUR_ECRAN, HAUTEUR_ECRAN*i/20), 1)

def draw_go_to_shooting_zone():
    draw_text("Go to the shooting zone",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*11/20,False,True,1,1)

def draw_credit_display():
    """Mention crédits en bas à droite, remplacée par "FREEPLAY" quand
    [Debug] FreePlay=True dans config.ini (aucun crédit à afficher/gérer)."""
    if free_play:
        draw_text("FREEPLAY",LARGEUR_ECRAN*18/20,HAUTEUR_ECRAN*19/20,False,True,2,3)
    else:
        draw_text("CREDIT  : ",LARGEUR_ECRAN*17/20,HAUTEUR_ECRAN*19/20,False,True,2,3)
        draw_text(str(credit_left),LARGEUR_ECRAN*19/20,HAUTEUR_ECRAN*19/20,False,True,2,3)

def draw_intro_text():
    draw_text("HIGH SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/20,False,True,1,4)
    draw_text(str(high_score),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*3/20,False,True,1,4)
    # Bloc "GAME START IN" + décompte centré verticalement sur l'écran :
    # "IN" (ligne du milieu) posé au centre exact (10/20), les 3 lignes
    # gardant le même espacement (2/20) qu'avant - demande utilisateur du
    # 2026-07-16, alignée sur main_hardcore.py.
    draw_text("GAME START",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*8/20,False,True,1,5)
    draw_text("IN",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*10/20,False,True,1,5)
    draw_text(str(time_left),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*12/20,False,True,1,5)
    draw_credit_display()

def draw_intro_insertCoin():
    draw_text("HIGH SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/20,False,True,1,4)
    draw_text(str(high_score),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*3/20,False,True,1,4)
    draw_credit_display()

def draw_mode_select():
    """Écran de choix du continent (gamestate 3) : un mode affiché à la
    fois au centre (carrousel), avec le nombre de pays qu'il contient -
    navigation E (précédent) / R (valider) / T (suivant), matérialisée par
    les boules du socle physique (gauche/centre/droite, voir
    init_mode_select_cibles) plutôt que des lettres, le joueur n'ayant pas
    de clavier sous les yeux - demande utilisateur du 2026-07-16.
    draw_text() utilise Alfa Slab One depuis le 2026-07-16 (accents
    complets), plus besoin d'une police dédiée ici comme du temps de Neon
    Glow."""
    ecran.blit(title_screen_image, (0, 0))
    name, tiers = WORLD_TOUR_MODES[mode_select_index]
    draw_text("CHOISIS TON MODE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*2/20,False,True,1,4)
    draw_text(name.upper(),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*9/20,True,True,2,5)
    draw_text(f"{len(tiers)} PAYS",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*12/20,False,True,1,4)
    for cible in mode_select_cibles:
        ecran.blit(cible.image, cible.rect)
    draw_text("PRÉCÉDENT",LARGEUR_ECRAN*4/20,HAUTEUR_ECRAN*15.6/20,False,True,2,3)
    draw_text("VALIDER",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*15.6/20,False,True,2,3)
    draw_text("SUIVANT",LARGEUR_ECRAN*17/20,HAUTEUR_ECRAN*15.6/20,False,True,2,3)
    draw_credit_display()

def draw_ingame_text():
    if time_left <= 15:
        draw_text(str(time_left),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*9/20,True,True,1,1)
    elif time_left <= 30:
        draw_text(str(time_left),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*9/20,False,True,1,2)
    elif time_left <= 45:
        draw_text(str(time_left),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*9/20,False,True,1,3)
    else:
        draw_text(str(time_left),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*9/20,False,True,1,5)

    draw_text("POINTS",LARGEUR_ECRAN*4/20,HAUTEUR_ECRAN*1/20,False,True,1,4)
    draw_text(str(score),LARGEUR_ECRAN*4/20,HAUTEUR_ECRAN*3/20,False,True,1,4)
    draw_credit_display()

def draw_ending_text():
    """Le HIGH SCORE affiché (et la comparaison "New record") n'a de sens
    que pour le mode "Tour complet" (mode_is_full_tour) : un score sur un
    seul continent atteint un plafond de tirs plus bas (moins de pays à
    parcourir), donc pas comparable au record établi sur les 115 pays."""
    if mode_is_full_tour:
        draw_text("HIGH SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/20,False,True,1,4)
        draw_text(str(high_score),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*3/20,False,True,1,4)
    else:
        draw_text(WORLD_TOUR_MODES[mode_select_index][0].upper(),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/20,False,True,1,4)
    draw_text(str(time_left),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/3,False,True,1,3)

    if mode_is_full_tour and score >= high_score:
        draw_text("YOUR SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*11/20,True,True,1,5)
        draw_text(str(score),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*13/20,True,True,1,5)
        draw_text("New record !!!",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*9/20,True,True,2,5)
    else:
        draw_text("YOUR SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*11/20,False,True,1,3)
        draw_text(str(score),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*13/20,False,True,1,3)

    draw_credit_display()

def draw_cibles():
    global ecran
    global cible1
    global cible2
    global cible3
    global cibleencours
    if cibleencours == 1:
        cible1.image = cible1.images[1]
        cible2.image = cible1.images[0]
        cible3.image = cible1.images[0]
    elif cibleencours == 2:
        cible1.image = cible1.images[0]
        cible2.image = cible1.images[1]
        cible3.image = cible1.images[0]
    elif cibleencours == 3:
        cible1.image = cible1.images[0]
        cible2.image = cible1.images[0]
        cible3.image = cible1.images[1]
    ecran.blit(cible1.image, cible1.rect)
    ecran.blit(cible2.image, cible2.rect)
    ecran.blit(cible3.image, cible3.rect)

def animate_cible():
    global oldcibleencours
    if oldcibleencours == 1:
        cible1.image = cible1.images[2]
    if oldcibleencours == 2:
        cible2.image = cible2.images[2]
    if oldcibleencours == 3:
        cible3.image = cible3.images[2]
    for i in range(3):
        ecran.blit(ingamebackground.image, ingamebackground.rect)
        ecran.blit(cible1.image, cible1.rect)
        ecran.blit(cible2.image, cible2.rect)
        ecran.blit(cible3.image, cible3.rect)
        ingamedraw()
        clock.tick(9)

def draw_fps():
    if ShowFPS:
        fps = str(int(clock.get_fps()))
        FPS1 = FontDel1.render(fps, True, blue)
        FPS2 = FontDel2.render(fps, True, bluelight)
        ecran.blit(FPS1, (0, 0))
        ecran.blit(FPS2, (0, 0))

def draw_crt():
    if crt_surface:
        ecran.blit(crt_surface, (0, 0))

def ingamedraw():
    draw_ingame_text()
    if debug_line == True:
        debug_lines()
    draw_fps()
    draw_crt()
    pygame.display.flip()

def handle_common_keys(event):
    global credit_left, sound_effects
    if event.key == pygame.K_c:
        credit_left += 1
    elif event.key == pygame.K_m:
        if channel1.get_busy():
            channel1.fadeout(FadeoutTime)
        else:
            channel1.play(music, loops=-1)
    elif event.key == pygame.K_s:
        if sound_effects:
            if channel1.get_busy():
                channel1.fadeout(FadeoutTime)
            sound_effects = False
        else:
            sound_effects = True
            channel1.play(music, loops=-1)

#-------------------------DEBUT DU Programme ---------------------------
print("loading sprites")
ingamebackground = WorldTourBackground()
camring = ColoredRing()
camring_width, camring_height = camring.image.get_rect().size
camring.rect.x = LARGEUR_ECRAN/2 - camring_width/2

try:
    sfx_hit    = pygame.mixer.Sound('./assets/Sounds/Son3.wav')
    sfx_gauche = pygame.mixer.Sound('./assets/Sounds/VoicesAI/gauche.wav')
    sfx_centre = pygame.mixer.Sound('./assets/Sounds/VoicesAI/centre.wav')
    sfx_droite = pygame.mixer.Sound('./assets/Sounds/VoicesAI/droite.wav')
    music_intro = pygame.mixer.Sound('./assets/Sounds/intro.wav')
    music_menu  = pygame.mixer.Sound('./assets/Sounds/Arducible vibe.mp3')
except pygame.error as e:
    print(f"Erreur chargement audio : {e}")
    raise SystemExit(1)

#initialise webcam if actived in config.ini
if active_webcam:
    try:
        from Scripts.opencvcam import Cam
        print("activating webcam")
        mycam = Cam()
        mycam.update()

        if mycam.webcam_compatibility == True:
            webcam_compatibility = True
        else:
            webcam_compatibility = False

        if webcam_compatibility == False:
            webcam_zone_interdite = False
        ingamebackground.reset(webcam_compatibility)
    except Exception as e:
        print(f"Webcam/MediaPipe error: {e}")
        webcam_compatibility = False
        webcam_zone_interdite = False
        ingamebackground.reset(webcam_compatibility)
else:
    webcam_compatibility = False
    webcam_zone_interdite = False
    ingamebackground.reset(webcam_compatibility)

pygame.display.set_caption("Fanny Pétanque World Tour - An #ARDUCIBLE pétanque game")
icon = pygame.image.load("assets/icons/192x192.png")
pygame.display.set_icon(icon)

if Fullscreen:
    ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SCALED | pygame.FULLSCREEN, vsync=1)
else:
    ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SCALED)

fanny = FannySpinner()
fanny_companion = FannyCompanion()

title_screen_image = pygame.transform.scale(
    pygame.image.load('./assets/Images/TitleScreenWorldTour.jpg'), (LARGEUR_ECRAN, HAUTEUR_ECRAN))
ending_screen_image = pygame.transform.scale(
    pygame.image.load('./assets/Images/EndingScreenWorldTour.jpg'), (LARGEUR_ECRAN, HAUTEUR_ECRAN))

crt_surface = None
if crt:
    import numpy as np
    crt_surface = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SRCALPHA)
    if HAUTEUR_ECRAN >= 1080:
        sl_step, sl_alpha = 6, 30
    elif HAUTEUR_ECRAN >= 720:
        sl_step, sl_alpha = 4, 25
    else:
        sl_step, sl_alpha = 3, 20
    for _y in range(0, HAUTEUR_ECRAN, sl_step):
        pygame.draw.line(crt_surface, (0, 0, 0, sl_alpha), (0, _y), (LARGEUR_ECRAN, _y))
    _alpha = pygame.surfarray.pixels_alpha(crt_surface)
    _cx, _cy = LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2
    _X, _Y = np.ogrid[:LARGEUR_ECRAN, :HAUTEUR_ECRAN]
    _dist = np.sqrt(((_X - _cx) / _cx) ** 2 + ((_Y - _cy) / _cy) ** 2)
    _vignette = np.clip(_dist ** 2 * 180, 0, 160).astype(np.uint8)
    _alpha[:] = np.maximum(_alpha, _vignette)
    del _alpha

time_left = splash_length
if background_music == True:
    music = music_intro
    channel1.play(music)

while time_left >= 0:
    ecran.blit(title_screen_image, (0, 0))
    countdown()
    fanny.update()
    fanny.draw(ecran, LARGEUR_ECRAN - int(HAUTEUR_ECRAN * 0.12), int(HAUTEUR_ECRAN * 0.12))
    draw_crt()
    pygame.display.flip()
    clock.tick(FPS)
time_left = intro_length

if background_music == True:
    print("Turn on music")
    music = music_menu
    channel1.play(music, loops=-1)


init_cibles()
init_mode_select_cibles()

# état du mode choisi (voir start_mode_select/start_game_with_mode,
# Scripts.dialogues.WORLD_TOUR_MODES) - demande utilisateur du 2026-07-15 :
# "le jeu est trop long, il faut proposer plusieurs modes, un par
# continent", élargie le même jour à toutes les variantes du jeu.
mode_select_index = 0
mode_is_full_tour = True


#---------------------------main game loop------------------------------

while continuer:
    current_time = pygame.time.get_ticks()
    if current_time - old_current_time > 500:
        old_current_time = current_time
        affichage = not affichage

    #-----------------------begining scene------------------------------
    if gamestate == 0:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
                print("exit game")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    continuer = False
                    print("exit game")
            elif event.type == pygame.KEYUP:
                handle_common_keys(event)
                # En freeplay, presser une cible équivaut à insérer un
                # crédit fictif : ça lance le même décompte qu'un vrai
                # crédit, le temps que le joueur rejoigne la zone de tir.
                if free_play and credit_left < 1 and event.key in TARGET_KEYS:
                    credit_left += 1

        ecran.blit(title_screen_image, (0, 0))

        if debug_line == True:
            debug_lines()

        draw_fps()

        fanny.update()
        fanny.draw(ecran, LARGEUR_ECRAN - int(HAUTEUR_ECRAN * 0.12), int(HAUTEUR_ECRAN * 0.12))

        if credit_left < 1:
            if free_play:
                draw_text("press a target to play", LARGEUR_ECRAN/2, HAUTEUR_ECRAN*3/4, True, True, 1, 3)
            else:
                draw_text("insert coin", LARGEUR_ECRAN/2, HAUTEUR_ECRAN*3/4, True, True, 1, 3)
            draw_intro_insertCoin()
        else:
            # Le décompte "GAME START IN" n'a plus lieu ici mais après le
            # choix du continent (gamestate 4, voir start_pregame_countdown)
            # - demande utilisateur du 2026-07-15. La musique de menu
            # continue de jouer pendant tout l'écran de sélection du
            # continent (demande utilisateur du 2026-07-16) : son fondu
            # est déclenché plus tard, dans start_pregame_countdown().
            credit_left = credit_left - 1
            start_mode_select()

        draw_crt()
        pygame.display.flip()

    #-----------------------Continent select scene------------------------
    if gamestate == 3:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
                print("exit game")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    continuer = False
                    print("exit game")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    mode_select_index = (mode_select_index - 1) % len(WORLD_TOUR_MODES)
                elif event.key == pygame.K_t:
                    mode_select_index = (mode_select_index + 1) % len(WORLD_TOUR_MODES)
                elif event.key == pygame.K_r:
                    start_pregame_countdown()

        countdown()
        draw_mode_select()
        draw_crt()
        pygame.display.flip()
        if time_left <= 0:
            start_pregame_countdown()

    #-----------------------Pregame countdown scene------------------------
    if gamestate == 4:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
                print("exit game")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    continuer = False
                    print("exit game")
            elif event.type == pygame.KEYUP:
                handle_common_keys(event)

        ecran.blit(title_screen_image, (0, 0))

        if debug_line == True:
            debug_lines()

        draw_fps()

        fanny.update()
        fanny.draw(ecran, LARGEUR_ECRAN - int(HAUTEUR_ECRAN * 0.12), int(HAUTEUR_ECRAN * 0.12))

        countdown()
        draw_intro_text()
        if time_left <= 0:
            start_game_with_mode(mode_select_index)

        draw_crt()
        pygame.display.flip()

    #-----------------------Game scene----------------------------------
    if gamestate == 1:
        countdown()
        ingamebackground.update_for_tier(fanny_companion.country_tier, webcam_compatibility)

        if webcam_compatibility == True:
            mycam.update()
            showcam()
            webcam_zone_interdite = mycam.zoneinterdite
            ecran.blit(ingamebackground.image, ingamebackground.rect)
            draw_camring()
        else:
            ecran.blit(ingamebackground.image, ingamebackground.rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
                print("exit game")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    continuer = False
                    print("exit game")
            elif event.type == pygame.KEYUP:
                if webcam_zone_interdite == False:
                    handle_common_keys(event)
                    if event.key == pygame.K_e:
                        if cibleencours == 1:
                            animate_cible()
                            update_score()
                            ciblealeatoire()
                    if event.key == pygame.K_r:
                        if cibleencours == 2:
                            animate_cible()
                            update_score()
                            ciblealeatoire()
                    if event.key == pygame.K_t:
                        if cibleencours == 3:
                            animate_cible()
                            update_score()
                            ciblealeatoire()

        draw_cibles()
        fanny_companion.draw(ecran, LARGEUR_ECRAN - int(LARGEUR_ECRAN * 0.01), int(HAUTEUR_ECRAN * 0.02))
        ingamedraw()

        tour_complete_score = len(fanny_companion.mode_tiers) * hits_per_country - 1
        if time_left <= 0 or is_tour_complete(score, tour_complete_score):
            if background_music == True:
                music = music_menu
                channel1.play(music, loops=-1)
            next_gamestate()

    #-----------------------ending scene--------------------------------
    if gamestate == 2:

        countdown()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
                print("exit game")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    continuer = False
                    print("exit game")
            elif event.type == pygame.KEYUP:
                handle_common_keys(event)

        ecran.blit(ending_screen_image, (0, 0))
        draw_ending_text()

        if debug_line == True:
            debug_lines()

        draw_fps()
        draw_crt()

        pygame.display.flip()

        if time_left <= 0:
            next_gamestate()

    clock.tick(FPS)


pygame.quit()
