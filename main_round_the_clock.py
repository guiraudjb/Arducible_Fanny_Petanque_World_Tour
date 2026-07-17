"""Petanque Challenge 2 - Round the Clock.

Point d'entrée indépendant de Fanny World Tour (main.py), pour le chassis à
7 cibles physiques disposées en étoile de David (6 boules sur les pointes,
un cochonet au centre). Port fidèle du jeu Lua/Defold d'origine, voir
ressources/Petanque-challenge-Round-the-clock/petanquechallengeV2Sourcecode/.

Règles reprises telles quelles de l'original :
- 1 à 6 joueurs, 3 à 12 manches, 3 tirs par passage.
- La cible imposée suit l'ordre 1..7 tant que le joueur courant a moins de
  7 REUSSITES (pas 7 tirs) ; au-delà, cible aléatoire (jamais deux fois la
  même de suite).
- Toucher la touche de la cible active = hit. Toucher la touche d'une autre
  cible = raté (c'est aussi le mécanisme prévu pour comptabiliser un tir qui
  n'a touché aucune des 7 cibles).
- Anti-rebond de 2 s après chaque tir.
- Pas de crédits/insert-coin, pas de high-score persistant (absents de
  l'original).
"""
import os
os.environ['GLOG_minloglevel'] = '2'
import glob
import random
import pygame
pygame.init()

import Scripts.round_the_clock.state as st
from Scripts.round_the_clock.sprites import (
    Target, ColoredRing, ShotsLeftBanner, WaitBanner, compute_target_centers,
    hud_point, draw_text, wrap_text, COCHONET_INDEX,
    HUD_SCORE_COLUMNS_NX, HUD_SCORE_ROWS_NY, HUD_RESTE_NXY, HUD_TOUR_NXY,
    HUD_CENTER_BANNER_NXY,
)

MENU, OPTIONS, HELP, INGAME, ENDING = range(5)

HELP_TEXT = """1. Objectif du jeu
Le but est simple : viser et toucher la cible désignée par le système. Chaque bonne cible touchée vous rapproche de la victoire.

2. Déroulement d'un tour
Lancers par tour : chaque joueur dispose de trois lancers par tour pour tenter de toucher la cible active.
Cible désignée : l'écran affiche clairement la cible à viser à chaque instant. Soyez attentif aux indications !

3. Comptabilisation des points et des lancers
Tir réussi : si vous touchez la cible désignée, un point est automatiquement comptabilisé.
Tir manqué (mauvaise cible) : si votre boule frappe une cible différente de celle désignée, un tir manqué est comptabilisé.
Tir manqué (aucune cible) : si votre boule ne touche aucune cible, actionnez manuellement une cible (n'importe laquelle, sauf celle désignée) pour valider le tir manqué.

4. Touches
E / T : diminuer / augmenter (joueurs, manches) - Y : options - U : aide - O : valider / retour - R : son (dans Options)
Flèche GAUCHE / DROITE : simuler un tir réussi / raté sur la cible active (jeu sans matériel physique)"""


def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Erreur chargement audio : {e}")
        return None


sfx_clic = load_sound('./assets/RoundTheClock/Sounds/clic.wav')
sfx_hit = load_sound('./assets/Sounds/Son3.wav')
sfx_miss = load_sound('./assets/Sounds/Son2.wav')
voix_joueur = [load_sound(f'./assets/RoundTheClock/Sounds/joueur{n}.wav') for n in range(1, 7)]

mycam = None
webcam_compatibility = False
webcam_zone_interdite = False
if st.active_webcam:
    try:
        from Scripts.opencvcam import Cam
        mycam = Cam(cam_fps=st.cam_fps, debug_cam=st.DebugCam,
                    largeur_ecran=st.LARGEUR_ECRAN, hauteur_ecran=st.HAUTEUR_ECRAN,
                    camera_index=st.camera_index, capture_width=st.capture_width,
                    capture_height=st.capture_height, zone_width_percent=st.zone_width_percent,
                    zone_height_percent=st.zone_height_percent,
                    zone_offset_x_percent=st.zone_offset_x_percent,
                    zone_offset_y_percent=st.zone_offset_y_percent)
        mycam.update()
        webcam_compatibility = mycam.webcam_compatibility
    except Exception as e:
        print(f"Webcam/MediaPipe error: {e}")
        webcam_compatibility = False

pygame.display.set_caption("Petanque Challenge 2 - Round the Clock - An #ARDUCIBLE pétanque game")
icon = pygame.image.load("assets/icons/192x192.png")
pygame.display.set_icon(icon)

if st.Fullscreen:
    ecran = pygame.display.set_mode((st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN), pygame.SCALED | pygame.FULLSCREEN, vsync=1)
else:
    ecran = pygame.display.set_mode((st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN), pygame.SCALED)

background_image = pygame.transform.scale(
    pygame.image.load('./assets/RoundTheClock/Images/background.png').convert(),
    (st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN))

# Fond du menu et de l'écran de fin (scores) : image de fin de Fanny World
# Tour, déjà pensée pour ces deux moments (accueil / bilan de partie).
menu_ending_background = pygame.transform.scale(
    pygame.image.load('./assets/Images/EndingScreenWorldTour.jpg').convert(),
    (st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN))

# Fond d'écran EN JEU (pas au menu) : fonds "Tour du Monde" de Fanny
# Pétanque World Tour (assets/Images/BackgroundWorldTour/, 111 pays, mêmes
# fichiers que ceux utilisés par Scripts/Sprites.py::WorldTourBackground),
# réutilisés ici pour faire découvrir un décor de pays différent après
# chaque tir réussi. Même système de "double fond" que Fanny : variante
# .jpg (pleine) si pas de webcam, variante .png (avec découpe ovale
# transparente) si webcam active - la webcam est alors dessinée EN DESSOUS
# du fond, visible à travers la découpe (cf. run_ingame). Pas de voile
# assombrissant ici : ça casserait la transparence de la découpe.
COUNTRY_BACKGROUNDS_DIR = './assets/Images/BackgroundWorldTour'
_country_slugs = sorted({
    os.path.splitext(os.path.basename(p))[0]
    for p in glob.glob(f'{COUNTRY_BACKGROUNDS_DIR}/*.jpg')
})
_ingame_background = None


def _load_random_country_background():
    if not _country_slugs:
        return background_image
    ext = 'png' if webcam_compatibility else 'jpg'
    slug = random.choice(_country_slugs)
    path = f'{COUNTRY_BACKGROUNDS_DIR}/{slug}.{ext}'
    try:
        img = pygame.image.load(path).convert_alpha() if webcam_compatibility else pygame.image.load(path).convert()
        return pygame.transform.smoothscale(img, (st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN))
    except pygame.error as e:
        print(f"Erreur chargement fond de pays : {e}")
        return background_image


def roll_ingame_background():
    """Tire un nouveau décor de pays au hasard - appelée au lancement
    d'une partie et après chaque tir réussi (pas les ratés)."""
    global _ingame_background
    _ingame_background = _load_random_country_background()


def get_ingame_background():
    if _ingame_background is None:
        roll_ingame_background()
    return _ingame_background

targets = [Target(is_cochonet=(i == COCHONET_INDEX)) for i in range(st.TARGET_COUNT)]
for _t, (_x, _y) in zip(targets, compute_target_centers(st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN)):
    _t.set_center(_x, _y)

shots_left_banner = ShotsLeftBanner()
wait_banner = WaitBanner()
# Même position que Fanny World Tour (main.py::showcam/draw_camring) :
# caméra et anneau centrés horizontalement, collés en haut de l'écran.
camring = ColoredRing() if webcam_compatibility else None
if camring:
    camring_width, camring_height = camring.image.get_rect().size
    camring.rect.x = st.LARGEUR_ECRAN / 2 - camring_width / 2
    camring.rect.y = 0

TARGET_KEYS = [pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o]

gamestate = MENU
continuer = True
clock = st.clock


def now_ms():
    return pygame.time.get_ticks()


def refresh_cooldown():
    """A appeler une fois par frame, indépendamment des événements clavier :
    sans ça, l'anti-rebond ne se lève que quand une touche est pressée, et
    le HUD affiche 'WAIT' en continu tant que le joueur n'a rien pressé.

    Cooldown plus court dans les menus (juste de quoi absorber un éventuel
    rebond du capteur physique) que pendant la partie, où les 2s servent
    aussi à laisser le temps à l'animation d'impact de se jouer - reprendre
    ce délai long pour la navigation menu le rendait pénible à utiliser."""
    cooldown = st.HIT_COOLDOWN_MS if gamestate == INGAME else st.MENU_COOLDOWN_MS
    if now_ms() - st.lasthit >= cooldown:
        st.activekeyboard = True


def input_ready():
    return st.activekeyboard


def consume_input():
    st.activekeyboard = False
    st.lasthit = now_ms()


def play(sound):
    if sound and st.SoundVolume:
        sound.play()


def announce_player():
    play(voix_joueur[st.joueur_en_cours])


def determiner_cible():
    st.determiner_cible_a_toucher()


def gerer_interruptions():
    global gamestate
    dernier_joueur = st.joueur_en_cours == st.NumberPlayer - 1
    if dernier_joueur and st.tour == st.NombreDeTours and st.reste == 0:
        gamestate = ENDING
    elif dernier_joueur and st.reste == 0:
        st.tour += 1
        st.reste = st.SHOTS_PER_TURN
        st.joueur_en_cours = 0
        st.lastchange = now_ms()
        announce_player()
        determiner_cible()
    elif st.reste == 0:
        st.joueur_en_cours = (st.joueur_en_cours + 1) % st.NumberPlayer
        st.reste = st.SHOTS_PER_TURN
        st.lastchange = now_ms()
        announce_player()
        determiner_cible()
    else:
        determiner_cible()


def register_hit():
    st.scorejoueurs[st.joueur_en_cours] += 1
    st.hitcount[st.joueur_en_cours] += 1
    st.reste -= 1
    play(sfx_hit)
    roll_ingame_background()
    gerer_interruptions()


def register_miss():
    st.misscount[st.joueur_en_cours] += 1
    st.reste -= 1
    play(sfx_miss)
    gerer_interruptions()


def start_game():
    global gamestate
    st.reset_game()
    st.lastchange = now_ms()
    announce_player()
    roll_ingame_background()
    gamestate = INGAME


def draw_star_menu(active_indices, labels):
    """Affiche les 7 boules à leur position physique exacte (même étoile de
    David que pendant la partie) et les utilise comme boutons de menu : le
    joueur retrouve toujours les mêmes 7 positions/touches à l'écran, qu'il
    soit en jeu ou dans un menu - meilleure lisibilité pour une borne où
    seules ces 7 touches existent physiquement."""
    now = now_ms()
    for i, t in enumerate(targets):
        t.set_active(i in active_indices)
        t.update(now)
        t.draw(ecran)
    for i, (label, key_hint) in labels.items():
        cx, cy = targets[i].rect.center
        color = (st.green, st.greenlight) if i in active_indices else (st.white, st.whitelight)
        draw_text(ecran, label, cx, cy - st.HAUTEUR_ECRAN * 0.075, True, (st.FontDel5, st.FontDel6), color)
        draw_text(ecran, f"({key_hint})", cx, cy + st.HAUTEUR_ECRAN * 0.075, True, (st.FontDel5, st.FontDel6), color)


def draw_credit_display(nx=0.78, ny=0.24):
    """Mention crédits, alignée avec Fanny World Tour / Hardcore :
    remplacée par "FREEPLAY" quand [Debug] FreePlay=True dans config.ini."""
    x, y = st.LARGEUR_ECRAN * nx, st.HAUTEUR_ECRAN * ny
    if st.free_play:
        draw_text(ecran, "FREEPLAY", x, y, True, (st.FontDel5, st.FontDel6), (st.yellow, st.yellowlight))
    else:
        draw_text(ecran, f"CREDIT : {st.credit_left}", x, y, True, (st.FontDel5, st.FontDel6), (st.yellow, st.yellowlight))


def draw_waiting_for_credit(events):
    """Écran affiché tant qu'aucun crédit n'est disponible : "INSERT COIN"
    par défaut, ou "PRESS A TARGET TO PLAY" en freeplay - presser une cible
    y équivaut alors à insérer un crédit fictif (même principe que Fanny
    World Tour / Hardcore)."""
    msg = "PRESS A TARGET TO PLAY" if st.free_play else "INSERT COIN"
    visible = (now_ms() // 500) % 2 == 0
    draw_text(ecran, msg, st.LARGEUR_ECRAN / 2, st.HAUTEUR_ECRAN * 0.5, True,
               (st.FontDel3, st.FontDel4), (st.red, st.redlight), blink=True, visible=visible)
    for event in events:
        if event.type == pygame.KEYDOWN and input_ready() and st.free_play and event.key in TARGET_KEYS:
            consume_input()
            play(sfx_clic)
            st.credit_left += 1


def draw_menu(events):
    global gamestate
    ecran.blit(menu_ending_background, (0, 0))
    # Titre placé dans la zone libre à droite de l'étoile (jamais occupée en
    # jeu que par le panneau de score) : avec des cibles agrandies, l'étoile
    # remplit presque toute la hauteur à gauche, plus assez de place au-
    # dessus d'elle pour un titre sans le chevaucher.
    draw_text(ecran, "PETANQUE CHALLENGE", st.LARGEUR_ECRAN * 0.78, st.HAUTEUR_ECRAN * 0.10, True,
               (st.FontDel3, st.FontDel4), (st.blue, st.bluelight))
    draw_text(ecran, "ROUND THE CLOCK", st.LARGEUR_ECRAN * 0.78, st.HAUTEUR_ECRAN * 0.16, True,
               (st.FontDel5, st.FontDel6), (st.orange, st.orangelight))
    draw_credit_display()

    if st.credit_left < 1:
        draw_waiting_for_credit(events)
        return

    draw_star_menu(
        active_indices={0, 2, 3, 4, 6},
        labels={
            0: ("- JOUEURS", "E"),
            2: ("+ JOUEURS", "T"),
            3: ("OPTIONS", "Y"),
            4: ("AIDE", "U"),
            6: ("DEMARRER", "O"),
        },
    )
    # Target6 (touche I) n'a pas d'action dans ce menu : on y affiche le
    # nombre de joueurs choisi, à titre informatif, sous la boule (pas
    # dessus, pour ne pas chevaucher le titre au-dessus).
    info_x, info_y = targets[5].rect.center
    draw_text(ecran, f"JOUEURS : {st.NumberPlayer}", info_x, info_y + st.HAUTEUR_ECRAN * 0.075, True,
               (st.FontDel3, st.FontDel4), (st.yellow, st.yellowlight))

    for event in events:
        if event.type == pygame.KEYDOWN and input_ready():
            if event.key == pygame.K_e:
                consume_input()
                play(sfx_clic)
                st.NumberPlayer = max(st.MIN_PLAYERS, st.NumberPlayer - 1)
            elif event.key == pygame.K_t:
                consume_input()
                play(sfx_clic)
                st.NumberPlayer = min(st.MAX_PLAYERS, st.NumberPlayer + 1)
            elif event.key == pygame.K_o:
                consume_input()
                play(sfx_clic)
                st.credit_left -= 1
                start_game()
            elif event.key == pygame.K_y:
                consume_input()
                play(sfx_clic)
                gamestate = OPTIONS
            elif event.key == pygame.K_u:
                consume_input()
                play(sfx_clic)
                gamestate = HELP


def draw_options(events):
    global gamestate
    ecran.blit(background_image, (0, 0))
    draw_text(ecran, "OPTIONS", st.LARGEUR_ECRAN * 0.78, st.HAUTEUR_ECRAN * 0.10, True,
               (st.FontDel3, st.FontDel4), (st.orange, st.orangelight))

    son_txt = "SON : ACTIVE" if st.SoundVolume else "SON : COUPE"
    draw_star_menu(
        active_indices={0, 1, 2, 6},
        labels={
            0: ("- MANCHES", "E"),
            1: (son_txt, "R"),
            2: ("+ MANCHES", "T"),
            6: ("RETOUR", "O"),
        },
    )
    # Target6 (touche I) n'a pas d'action dans Options : nombre de manches,
    # sous la boule (pas dessus, pour ne pas chevaucher le titre au-dessus).
    info_x, info_y = targets[5].rect.center
    draw_text(ecran, f"MANCHES : {st.NombreDeTours}", info_x, info_y + st.HAUTEUR_ECRAN * 0.075, True,
               (st.FontDel3, st.FontDel4), (st.yellow, st.yellowlight))

    for event in events:
        if event.type == pygame.KEYDOWN and input_ready():
            if event.key == pygame.K_e:
                consume_input()
                play(sfx_clic)
                st.NombreDeTours = max(st.MIN_ROUNDS, st.NombreDeTours - 1)
            elif event.key == pygame.K_t:
                consume_input()
                play(sfx_clic)
                st.NombreDeTours = min(st.MAX_ROUNDS, st.NombreDeTours + 1)
            elif event.key == pygame.K_r:
                consume_input()
                st.SoundVolume = not st.SoundVolume
                play(sfx_clic)
            elif event.key == pygame.K_o:
                consume_input()
                play(sfx_clic)
                gamestate = MENU


def draw_help(events):
    global gamestate
    ecran.blit(background_image, (0, 0))
    draw_text(ecran, "AIDE", st.LARGEUR_ECRAN / 2, st.HAUTEUR_ECRAN * 0.06, True,
               (st.FontDel1, st.FontDel2), (st.orange, st.orangelight))

    max_width = int(st.LARGEUR_ECRAN * 0.86)
    y = st.HAUTEUR_ECRAN * 0.16
    line_height = st.FontDel5.get_linesize()
    for paragraph in HELP_TEXT.split("\n"):
        if not paragraph:
            y += line_height * 0.6
            continue
        for line in wrap_text(paragraph, st.FontDel5, max_width):
            draw_text(ecran, line, st.LARGEUR_ECRAN * 0.07, y, False,
                       (st.FontDel5, st.FontDel6), (st.white, st.whitelight))
            y += line_height

    draw_text(ecran, "O : RETOUR", st.LARGEUR_ECRAN / 2, st.HAUTEUR_ECRAN * 0.97, True,
               (st.FontDel3, st.FontDel4), (st.white, st.whitelight))

    for event in events:
        if event.type == pygame.KEYDOWN and input_ready():
            if event.key == pygame.K_o:
                consume_input()
                play(sfx_clic)
                gamestate = MENU


def draw_ingame_hud():
    # Panneau de score : 2 colonnes (J1/J3/J5 à gauche, J2/J4/J6 à droite) x
    # 3 lignes, sur le tiers droit de l'écran - reprend la disposition exacte
    # de main/IngameMenu.gui (voir HUD_SCORE_COLUMNS_NX/HUD_SCORE_ROWS_NY).
    for i in range(st.NumberPlayer):
        col = i % 2
        row = i // 2
        if row >= len(HUD_SCORE_ROWS_NY):
            break
        actif = i == st.joueur_en_cours
        color = (st.blue, st.bluelight) if actif else (st.white, st.whitelight)
        nx = HUD_SCORE_COLUMNS_NX[col]
        label_ny, score_ny = HUD_SCORE_ROWS_NY[row]
        lx, ly = hud_point((nx, label_ny), st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN)
        sx, sy = hud_point((nx, score_ny), st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN)
        draw_text(ecran, f"JOUEUR {i + 1}", lx, ly, True, (st.FontDel5, st.FontDel6), color)
        draw_text(ecran, st.scorejoueurs[i], sx, sy, True, (st.FontDel3, st.FontDel4), color)

    # Sous le panneau de score, au-dessus du bandeau "tirs restants" - même
    # colonne, seul espace libre du HUD (dense sur ce tiers droit de l'écran).
    draw_credit_display(nx=0.8, ny=0.72)

    shots_left_banner.draw(ecran, st.reste, hud_point(HUD_RESTE_NXY, st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN))

    tx, ty = hud_point(HUD_TOUR_NXY, st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN)
    draw_text(ecran, f"MANCHE {st.tour} / {st.NombreDeTours}", tx, ty, True,
               (st.FontDel5, st.FontDel6), (st.white, st.whitelight))

    bx, by = hud_point(HUD_CENTER_BANNER_NXY, st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN)
    if now_ms() - st.lastchange < st.BANNER_DURATION_S * 1000:
        draw_text(ecran, f"JOUEUR {st.joueur_en_cours + 1}", bx, by - st.HAUTEUR_ECRAN * 0.20, True,
                   (st.FontDel3, st.FontDel4), (st.yellow, st.yellowlight))
    # Bandeau plein écran, sur toute la largeur, qui masque le plateau
    # pendant l'anti-rebond (bien plus visible qu'un simple texte au milieu
    # de l'écran, notamment sur une grande borne vue de loin).
    if not st.activekeyboard:
        wait_banner.draw(ecran, by, (st.FontWait1, st.FontWait2), (st.red, st.redlight))

    if webcam_zone_interdite:
        # Même position que Fanny World Tour (draw_go_to_shooting_zone) :
        # centré à l'écran.
        draw_text(ecran, "RETOURNEZ DANS LA ZONE DE TIR", st.LARGEUR_ECRAN / 2, st.HAUTEUR_ECRAN * 0.55, True,
                   (st.FontDel5, st.FontDel6), (st.red, st.redlight))


def run_ingame(events):
    global gamestate, webcam_zone_interdite

    if webcam_compatibility:
        mycam.update()
        webcam_zone_interdite = mycam.zoneinterdite

    for t in targets:
        t.set_active(False)
    targets[st.cible_en_cours].set_active(True)
    for t in targets:
        t.update(now_ms())

    if webcam_compatibility:
        # Même ordre de dessin que Fanny World Tour (main.py, gamestate==1) :
        # la caméra est dessinée D'ABORD, puis le fond (variante .png à
        # découpe ovale transparente) par-dessus - la caméra apparaît à
        # travers la découpe - puis l'anneau coloré (zone de tir) par-dessus.
        ecran.blit(mycam.image, (st.LARGEUR_ECRAN / 2 - mycam.width / 2, 0))
        ecran.blit(get_ingame_background(), (0, 0))
        camring.set_zone_interdite(webcam_zone_interdite)
        camring.draw(ecran)
    else:
        ecran.blit(get_ingame_background(), (0, 0))

    for t in targets:
        t.draw(ecran)
    draw_ingame_hud()

    for event in events:
        if event.type != pygame.KEYDOWN:
            continue
        if not input_ready() or webcam_zone_interdite:
            continue
        if event.key in TARGET_KEYS:
            # Une cible physique vraiment frappée par une boule explose
            # toujours (retour visuel d'impact), que ce soit un hit ou un
            # raté - seul le score dépend de si c'était la cible désignée.
            idx = TARGET_KEYS.index(event.key)
            consume_input()
            targets[idx].trigger_explosion(now_ms())
            if idx == st.cible_en_cours:
                register_hit()
            else:
                register_miss()
        elif event.key == pygame.K_LEFT:
            # Fallback clavier "Touche" (sans matériel physique) : valide un
            # hit sur la cible active, avec son explosion.
            consume_input()
            targets[st.cible_en_cours].trigger_explosion(now_ms())
            register_hit()
        elif event.key == pygame.K_RIGHT:
            # Fallback clavier "Raté" : aucune cible n'a été frappée, donc
            # pas d'explosion (fidèle à l'original).
            consume_input()
            register_miss()


def draw_ending(events):
    global gamestate
    ecran.blit(menu_ending_background, (0, 0))
    draw_text(ecran, "FIN DE PARTIE", st.LARGEUR_ECRAN / 2, st.HAUTEUR_ECRAN * 0.08, True,
               (st.FontDel1, st.FontDel2), (st.orange, st.orangelight))

    classement = sorted(range(st.NumberPlayer), key=lambda i: st.scorejoueurs[i], reverse=True)
    meilleur_score = st.scorejoueurs[classement[0]] if classement else 0

    for rang, i in enumerate(classement):
        tirs = st.hitcount[i] + st.misscount[i]
        taux = (st.hitcount[i] * 100 / tirs) if tirs else 0.0
        est_premier = st.scorejoueurs[i] == meilleur_score
        color = (st.yellow, st.yellowlight) if est_premier else (st.white, st.whitelight)
        y = st.HAUTEUR_ECRAN * (0.24 + rang * 0.11)
        draw_text(ecran, f"J{i + 1}", st.LARGEUR_ECRAN * 0.10, y, False, (st.FontDel3, st.FontDel4), color)
        draw_text(ecran, f"{st.scorejoueurs[i]} pts", st.LARGEUR_ECRAN * 0.30, y, False, (st.FontDel3, st.FontDel4), color)
        draw_text(ecran, f"{st.hitcount[i]} touches / {st.misscount[i]} ratés", st.LARGEUR_ECRAN * 0.52, y, False,
                   (st.FontDel5, st.FontDel6), color)
        draw_text(ecran, f"{taux:.0f} %", st.LARGEUR_ECRAN * 0.86, y, False, (st.FontDel5, st.FontDel6), color)

    draw_text(ecran, "O : RETOUR AU MENU", st.LARGEUR_ECRAN / 2, st.HAUTEUR_ECRAN * 0.95, True,
               (st.FontDel3, st.FontDel4), (st.white, st.whitelight))

    for event in events:
        if event.type == pygame.KEYDOWN and input_ready():
            if event.key == pygame.K_o:
                consume_input()
                play(sfx_clic)
                gamestate = MENU


while continuer:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            continuer = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            continuer = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            # Touche crédit globale, alignée sur Fanny World Tour / Hardcore
            # (borne réelle : pièce détectée par l'Arduino). Les 7 touches de
            # cible E R T Y U I O étant toutes prises par le chassis étoile,
            # C reste libre pour ce rôle sur les 3 jeux.
            st.credit_left += 1

    if not continuer:
        break

    refresh_cooldown()

    if gamestate == MENU:
        draw_menu(events)
    elif gamestate == OPTIONS:
        draw_options(events)
    elif gamestate == HELP:
        draw_help(events)
    elif gamestate == INGAME:
        run_ingame(events)
    elif gamestate == ENDING:
        draw_ending(events)

    if st.debug_line:
        for i in range(1, 20):
            pygame.draw.line(ecran, st.red, (st.LARGEUR_ECRAN * i / 20, 0), (st.LARGEUR_ECRAN * i / 20, st.HAUTEUR_ECRAN), 1)
            pygame.draw.line(ecran, st.red, (0, st.HAUTEUR_ECRAN * i / 20), (st.LARGEUR_ECRAN, st.HAUTEUR_ECRAN * i / 20), 1)
    if st.ShowFPS:
        fps_img = st.FontDel3.render(str(int(clock.get_fps())), True, st.blue)
        ecran.blit(fps_img, (0, 0))

    pygame.display.flip()
    clock.tick(st.FPS)

pygame.quit()
