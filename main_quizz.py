"""Fanny Pétanque World Tour - Quizz.

Version quizz seul : pas de tir, pas de cibles physiques, pas de chrono de
partie (mais un chrono PAR QUESTION, voir plus bas). À l'insertion d'un
crédit, le joueur enchaîne directement les 115 quizz (5 questions chacun,
pétanque + culture générale) de tous les pays du tour, dans l'ordre, en
répondant avec les touches E/R/T (choix gauche/centre/droite). Le score
final est le nombre total de bonnes réponses sur l'ensemble du tour.

Différences avec main.py (dont ce fork est issu) :
- Aucun tir, aucune webcam, aucun chrono de partie : `gamestate == 1`
  (la scène de tir) est entièrement supprimée. Après l'écran d'accueil
  (crédit/freeplay, inchangé), on entre directement dans `gamestate == 3`
  ("quizz") pour le pays 0, puis on enchaîne automatiquement les pays
  suivants après chaque récap (voir `quiz_advance()`), jusqu'au dernier
  (tier 114), puis écran de fin. Les sprites des 3 cibles (boules) du jeu
  de base sont réaffichés sous chaque choix de réponse
  (`init_quiz_cibles()`/`draw_quiz_cibles()`), sans étiquette E/R/T -
  purement visuel, sans détection de tir : la bonne réponse s'illumine en
  doré pendant le feedback, comme un tir réussi dans le jeu de base.
  Après le feedback (couleurs sur les choix), une phase "explanation"
  affiche un speech qui explique la bonne réponse à la place de l'énoncé,
  au moins QUIZ_EXPLANATION_MS mais jamais moins longtemps que l'audio de
  l'explication (la durée réelle du fichier gTTS est vérifiée pour ne
  jamais couper le son en passant à la question suivante trop tôt), ou
  jusqu'à ce que le joueur appuie sur E/R/T pour passer directement à la
  question suivante.
- Le décor, l'hymne et le portrait de Fanny par pays sont toujours pilotés
  par `FannyCompanion`/`WorldTourBackground`, mais en avançant directement
  de pays en pays (`fanny_companion.on_score_update(tier, score_seuil=1)`)
  plutôt qu'en fonction d'un score de tir.
- Questions dans Scripts/quiz_questions.py (généré depuis
  Scripts/dialogues.py + une table de métadonnées pays : capitale,
  continent, langue, monnaie). Chaque question/choix/explication est aussi
  narré en français par synthèse vocale (gTTS, voix Google) : un mp3 par
  texte unique dans assets/Sounds/QuizzTTS/, généré hors-ligne par
  ressources/utils/generate_quiz_audio.py (venv gTTS dédié, pas celui du
  jeu), retrouvé à l'exécution via Scripts/quiz_audio.py (hash du texte,
  pas de table de correspondance séparée) et joué en file d'attente sur
  channel7 (`queue_quiz_audio()`/`update_quiz_audio()`). Silencieux si un
  fichier manque (génération incomplète) plutôt que de planter.
- Texte du quizz (question + choix) rendu avec sa propre police
  (assets/RoundTheClock/Fonts/DejaVuSans.ttf) et ses propres panneaux de
  fond unis (draw_quiz_text/draw_panel), pas draw_text() : le texte du
  quizz défile par-dessus un fond de pays variable (contrairement au HUD,
  posé sur les écrans titre/fin fixes) et doit rester lisible dans tous les
  cas, plus retourner à la ligne (draw_quiz_text_wrapped) - draw_text()
  utilise Alfa Slab One depuis le 2026-07-16 (accents complets), mais reste
  pensée pour un texte court sur fond fixe.
- `high_score` propre à Quizz, dans sa propre section `[Quizz]` de
  `config.ini`, indépendant des autres jeux (`quizz_high_score`,
  `save_high_score_quizz()`, cf. Scripts/init.py).
- Portrait de Fanny en tenue traditionnelle du pays courant
  (`FannyCompanion.image`) dans le coin supérieur droit, réduit
  (QUIZ_FANNY_HEIGHT) pour ne jamais chevaucher la question - juste la
  photo, pas la bulle de dialogue ni la mini-carte du jeu de base (voir
  `get_quiz_fanny_portrait()`/`draw_quiz_fanny_and_timer()`). Juste
  en-dessous, pendant la phase "asking" : un compte à rebours de
  QUIZ_ANSWER_TIME_MS (60s) pour répondre, en vert/orange/rouge selon le
  temps restant ; passé ce délai sans réponse, `quiz_timeout()` bascule en
  feedback sans sélection (comme un choix manqué, sans score).

Tout le reste (écran d'accueil, CRT, debug, crédits/freeplay) est repris
tel quel de Scripts/init.py, partagé avec le jeu de base.
"""
#---------------------------------IMPORTS-------------------------------
import os
os.environ['GLOG_minloglevel'] = '2'  # supprime les logs verbeux de MediaPipe/TFLite
import pygame
from pygame import *
pygame.init()
from Scripts.init import *  # noqa: F401,F403 (config.ini, polices, couleurs, canaux audio)
from Scripts.Sprites import *  # noqa: F401,F403 (WorldTourBackground, FannyCompanion, FannySpinner, ...)
from Scripts.dialogues import COUNTRY_MAX_TIER, WORLD_TOUR_COUNTRIES, WORLD_TOUR_MODES
from Scripts.quiz_questions import QUIZ_QUESTIONS
from Scripts.quiz_audio import quiz_audio_path

TARGET_KEYS = [pygame.K_e, pygame.K_r, pygame.K_t]
CONTINENT_SELECT_TIMEOUT = 60  # secondes avant lancement auto de la partie sur le mode affiché
QUIZ_FEEDBACK_MS = 1500
QUIZ_EXPLANATION_MS = 4500
QUIZ_RECAP_MS = 2500
QUIZ_ANSWER_TIME_MS = 60000  # temps max pour répondre à une question
QUIZ_CHOICE_X = [LARGEUR_ECRAN * 3 / 20, LARGEUR_ECRAN * 10 / 20, LARGEUR_ECRAN * 17 / 20]
QUIZ_CHOICE_MAX_WIDTH = LARGEUR_ECRAN * 0.3
QUIZ_TOTAL_QUESTIONS = len(QUIZ_QUESTIONS) * 5

# Modes de jeu proposés à l'écran de sélection (gamestate 4, voir
# start_mode_select/draw_mode_select) : le tour complet (115 pays, très
# long) ou un tour limité à un seul continent - demande utilisateur du
# 2026-07-15 ("le jeu est trop long, il faut proposer plusieurs modes, un
# par continent", élargie le même jour à "l'ensemble des variantes du
# jeu"). Table PARTAGÉE avec main.py/main_hardcore.py, cf.
# Scripts.dialogues.WORLD_TOUR_MODES - ne pas redéfinir ici. Seul le mode
# "Tour complet" (index 0) alimente le high score (quizz_high_score,
# calibré sur QUIZ_TOTAL_QUESTIONS) - un score sur un continent n'est pas
# comparable, voir quiz_is_full_tour.
QUIZ_MODES = WORLD_TOUR_MODES

# Portrait de Fanny (tenue traditionnelle du pays courant, FannyCompanion)
# dans le coin supérieur droit, réduit par rapport à sa taille d'origine
# (prévue pour le jeu de base) pour ne jamais chevaucher la question,
# affichée juste en dessous.
QUIZ_FANNY_HEIGHT = HAUTEUR_ECRAN * 0.14
QUIZ_FANNY_TOPRIGHT = (LARGEUR_ECRAN * 0.98, HAUTEUR_ECRAN * 0.02)

# Police dédiée (pas draw_text()/Alfa Slab One du reste du jeu) pour tout
# le texte du quizz : question, choix, récap - voir la note en tête de
# fichier (panneaux de fond + retour à la ligne nécessaires ici).
QUIZ_FONT_PATH = "./assets/RoundTheClock/Fonts/DejaVuSans.ttf"
QUIZ_FONT_TITLE = pygame.font.Font(QUIZ_FONT_PATH, round(HAUTEUR_ECRAN * 0.055))
QUIZ_FONT_QUESTION = pygame.font.Font(QUIZ_FONT_PATH, round(HAUTEUR_ECRAN * 0.042))
QUIZ_FONT_CHOICE = pygame.font.Font(QUIZ_FONT_PATH, round(HAUTEUR_ECRAN * 0.038))
QUIZ_FONT_RECAP = pygame.font.Font(QUIZ_FONT_PATH, round(HAUTEUR_ECRAN * 0.06))
QUIZ_FONT_TIMER = pygame.font.Font(QUIZ_FONT_PATH, round(HAUTEUR_ECRAN * 0.045))
#---------------------Procedures et fonctions---------------------------

def next_gamestate():
    global time_left
    global gamestate
    global intro_length
    if gamestate == 2:
        gamestate = 0
        time_left = intro_length

def countdown():
    global old_timer
    global game_timer
    global time_left
    game_timer = pygame.time.get_ticks()
    if game_timer - old_timer >= 1000:
        time_left = time_left - 1
        old_timer = game_timer

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

# Couleurs de texte propres au quizz (pas les couleurs "néon" du reste du
# jeu, prévues pour un fond noir) : tons foncés et saturés choisis pour
# rester lisibles sur le panneau clair ci-dessous.
QUIZ_COLORS = {
    1: (150, 15, 15),   # rouge sombre : mauvaise réponse sélectionnée
    2: (170, 80, 0),     # orange sombre
    3: (100, 70, 10),    # brun/ocre : choix non sélectionné pendant le feedback
    4: (15, 25, 70),     # bleu marine : texte par défaut (question, titre, labels)
    5: (10, 110, 30),    # vert foncé : bonne réponse
}
QUIZ_PANEL_COLOR = (245, 240, 222)
QUIZ_PANEL_ALPHA = 225
QUIZ_PANEL_PAD_X = 14
QUIZ_PANEL_PAD_Y = 8

def draw_panel(x, y, w, h, center=True):
    """Rectangle de couleur unie semi-opaque, pour que le texte du quizz
    reste lisible par-dessus n'importe quel fond de pays."""
    w, h = max(1, int(w)), max(1, int(h))
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((*QUIZ_PANEL_COLOR, QUIZ_PANEL_ALPHA))
    if center:
        ecran.blit(panel, (x - w / 2, y - h / 2))
    else:
        ecran.blit(panel, (x, y))

def _blit_quiz_text(text, x, y, center, font, color):
    text_img = font.render(str(text), True, color)
    w, h = text_img.get_rect().size
    if center:
        ecran.blit(text_img, (x - w/2, y - h/2))
    else:
        ecran.blit(text_img, (x, y))

def draw_quiz_text(text, x, y, center, font, col):
    """Rendu plein (pas de double calque néon) avec une police à
    accentuation complète, sur un panneau de fond uni pour rester lisible
    - utilisé uniquement par l'écran de quizz."""
    color = QUIZ_COLORS[col]
    text_img = font.render(str(text), True, color)
    w, h = text_img.get_rect().size
    draw_panel(x, y, w + 2 * QUIZ_PANEL_PAD_X, h + 2 * QUIZ_PANEL_PAD_Y, center=center)
    _blit_quiz_text(text, x, y, center, font, color)

def wrap_text(text, font, max_width):
    """Découpe `text` en lignes tenant dans `max_width` pixels pour `font`
    (mesure au mot près)."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if font.size(trial)[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_quiz_text_wrapped(text, x, y, center, font, col, max_width, line_height):
    """Comme draw_quiz_text(), mais retourne à la ligne pour respecter
    max_width - un seul panneau de fond derrière tout le bloc de texte.
    Renvoie la hauteur totale occupée."""
    color = QUIZ_COLORS[col]
    lines = wrap_text(str(text), font, max_width)
    if not lines:
        return 0
    block_width = max(font.size(line)[0] for line in lines)
    block_height = len(lines) * line_height
    block_center_y = y + (block_height - line_height) / 2
    draw_panel(
        x, block_center_y,
        block_width + 2 * QUIZ_PANEL_PAD_X, block_height + 2 * QUIZ_PANEL_PAD_Y,
        center=center,
    )
    for i, line in enumerate(lines):
        _blit_quiz_text(line, x, y + i * line_height, center, font, color)
    return block_height

QUIZ_CIBLE_Y = HAUTEUR_ECRAN * 0.70
QUIZ_CIBLE_SIZE = (LARGEUR_ECRAN * 0.14, HAUTEUR_ECRAN * 0.25)

def init_quiz_cibles():
    """Réaffiche les sprites des 3 cibles (boules) du jeu de base au-dessus
    des touches E/R/T, une par choix de réponse - repris tel quel de Cible
    (Scripts/Sprites.py), simplement repositionné et réduit pour ne pas
    empiéter sur le texte des choix."""
    global quiz_cibles
    quiz_cibles = []
    for x in QUIZ_CHOICE_X:
        cible = Cible(size=QUIZ_CIBLE_SIZE)
        cible.rect.center = (x, QUIZ_CIBLE_Y)
        quiz_cibles.append(cible)

MODE_SELECT_CIBLE_SIZE = (LARGEUR_ECRAN * 0.07, HAUTEUR_ECRAN * 0.10)

def init_mode_select_cibles():
    """Trois boules (gauche=E, centre=R, droite=T) affichées sur l'écran de
    choix du continent : le joueur n'a que le socle physique devant lui
    (pas de clavier), il faut donc montrer les boules plutôt que des
    flèches/lettres pour indiquer précédent/valider/suivant - demande
    utilisateur du 2026-07-16, même principe que init_quiz_cibles()
    ci-dessus."""
    global mode_select_cibles
    mode_select_cibles = [Cible(size=MODE_SELECT_CIBLE_SIZE) for _ in range(3)]
    mode_select_cibles[0].rect.center = (LARGEUR_ECRAN * 0.12, HAUTEUR_ECRAN * 0.5)
    mode_select_cibles[1].rect.center = (LARGEUR_ECRAN * 0.5, HAUTEUR_ECRAN * 0.72)
    mode_select_cibles[2].rect.center = (LARGEUR_ECRAN * 0.88, HAUTEUR_ECRAN * 0.5)

def draw_quiz_cibles(quiz_phase, correct_index):
    """Boule dorée (images[2], comme un tir réussi dans le jeu de base) sur
    la bonne réponse pendant le feedback et l'explication de Fanny, boule
    normale (images[0]) sinon."""
    for i, cible in enumerate(quiz_cibles):
        if quiz_phase in ("feedback", "explanation") and i == correct_index:
            cible.image = cible.images[2]
        else:
            cible.image = cible.images[0]
        ecran.blit(cible.image, cible.rect)

_quiz_fanny_cache = {"tier": None, "image": None}

def get_quiz_fanny_portrait():
    """Version réduite du portrait de Fanny (FannyCompanion.image, tenue
    traditionnelle du pays courant), pour le coin supérieur droit de
    l'écran de quizz - recalculée seulement quand le pays change (pas à
    chaque frame)."""
    tier = fanny_companion.country_tier
    if _quiz_fanny_cache["tier"] != tier:
        img = fanny_companion.image
        w, h = img.get_rect().size
        ratio = QUIZ_FANNY_HEIGHT / h
        _quiz_fanny_cache["image"] = pygame.transform.smoothscale(img, (round(w * ratio), round(QUIZ_FANNY_HEIGHT)))
        _quiz_fanny_cache["tier"] = tier
    return _quiz_fanny_cache["image"]

def draw_quiz_fanny_and_timer(quiz_phase, quiz_phase_start):
    """Portrait de Fanny dans le coin supérieur droit, et juste en dessous,
    pendant la phase "asking" seulement, le compte à rebours (60 secondes
    max pour répondre - QUIZ_ANSWER_TIME_MS), en vert/orange/rouge selon le
    temps restant (même convention que le jeu de base : draw_text pour
    time_left dans main.py)."""
    portrait = get_quiz_fanny_portrait()
    portrait_rect = portrait.get_rect(topright=QUIZ_FANNY_TOPRIGHT)
    ecran.blit(portrait, portrait_rect)

    if quiz_phase != "asking":
        return
    remaining_ms = max(0, QUIZ_ANSWER_TIME_MS - (pygame.time.get_ticks() - quiz_phase_start))
    remaining_s = (remaining_ms + 999) // 1000
    if remaining_s <= 10:
        col = 1
    elif remaining_s <= 20:
        col = 2
    else:
        col = 5
    draw_quiz_text(str(remaining_s), portrait_rect.centerx, portrait_rect.bottom + HAUTEUR_ECRAN * 0.035,
                    True, QUIZ_FONT_TIMER, col)

quiz_audio_cache = {}
quiz_audio_queue = []

def get_quiz_audio(text):
    """Charge (avec cache) le mp3 TTS correspondant à `text`, généré par
    ressources/utils/generate_quiz_audio.py. Renvoie None si le fichier est
    introuvable (génération incomplète) - la narration saute alors ce
    texte silencieusement plutôt que de planter."""
    path = quiz_audio_path(text)
    if path not in quiz_audio_cache:
        try:
            quiz_audio_cache[path] = pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            quiz_audio_cache[path] = None
    return quiz_audio_cache[path]

def queue_quiz_audio(texts):
    """Remplace la file de narration du quizz par `texts` (dans l'ordre)
    et coupe immédiatement ce qui était en train de jouer."""
    global quiz_audio_queue
    channel7.stop()
    quiz_audio_queue = list(texts)

def update_quiz_audio():
    """À appeler chaque frame pendant gamestate == 3 : dès que le canal de
    narration est libre, joue le texte suivant de la file (silencieux si
    l'audio manque, sans bloquer la file)."""
    if channel7.get_busy():
        return
    while quiz_audio_queue:
        sound = get_quiz_audio(quiz_audio_queue.pop(0))
        if sound is not None:
            channel7.play(sound)
            return

def debug_lines():
    for i in range(1, 20):
        pygame.draw.line(ecran, red, (LARGEUR_ECRAN*i/20, 0), (LARGEUR_ECRAN*i/20, HAUTEUR_ECRAN), 1)
        pygame.draw.line(ecran, red, (0, HAUTEUR_ECRAN*i/20), (LARGEUR_ECRAN, HAUTEUR_ECRAN*i/20), 1)

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
    draw_text(f"{quizz_high_score} / {QUIZ_TOTAL_QUESTIONS}",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*3/20,False,True,1,4)
    # Bloc "GAME START IN" + décompte centré verticalement sur l'écran :
    # "IN" (ligne du milieu) posé au centre exact (10/20), les 3 lignes
    # gardant le même espacement (2/20) qu'avant - demande utilisateur du
    # 2026-07-16, alignée sur main_hardcore.py/main.py.
    draw_text("GAME START",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*8/20,False,True,1,5)
    draw_text("IN",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*10/20,False,True,1,5)
    draw_text(str(time_left),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*12/20,False,True,1,5)
    draw_credit_display()

def draw_intro_insertCoin():
    draw_text("HIGH SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/20,False,True,1,4)
    draw_text(f"{quizz_high_score} / {QUIZ_TOTAL_QUESTIONS}",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*3/20,False,True,1,4)
    draw_credit_display()

def draw_ending_text():
    """Le HIGH SCORE affiché (et la comparaison "New record") n'a de sens
    que pour le mode "Tour complet" (quizz_high_score y est calibré, cf.
    QUIZ_TOTAL_QUESTIONS = 115 pays x 5) - un score sur un seul continent
    utilise son propre dénominateur (nombre de pays du mode x 5) et
    n'affiche pas de comparaison au record, incomparable."""
    max_score = QUIZ_TOTAL_QUESTIONS if quiz_is_full_tour else len(quiz_mode_tiers) * 5

    if quiz_is_full_tour:
        draw_text("HIGH SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/20,False,True,1,4)
        draw_text(f"{quizz_high_score} / {QUIZ_TOTAL_QUESTIONS}",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*3/20,False,True,1,4)
    else:
        draw_text(QUIZ_MODES[mode_select_index][0].upper(),LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*1/20,False,True,1,4)

    if quiz_is_full_tour and score >= quizz_high_score:
        draw_text("YOUR SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*11/20,True,True,1,5)
        draw_text(f"{score} / {max_score}",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*13/20,True,True,1,5)
        draw_text("New record !!!",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*9/20,True,True,2,5)
    else:
        draw_text("YOUR SCORE",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*11/20,False,True,1,3)
        draw_text(f"{score} / {max_score}",LARGEUR_ECRAN*10/20,HAUTEUR_ECRAN*13/20,False,True,1,3)

    draw_credit_display()

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

#-------------------------QUIZZ--------------------------------------

def goto_country(tier):
    """Met à jour décor/hymne/portrait pour `tier`, en appelant directement
    les méthodes internes de FannyCompanion plutôt que reset()/
    on_score_update() (pas de score de tir dans ce fork) - surtout, pour
    couper sa voix à l'ouverture de chaque pays (play_audio=False) : dans
    ce mode quizz-only, l'enchaînement est trop rapide/répétitif pour
    laisser la voix démarrer à chaque pays. L'hymne national continue de
    jouer normalement, lui, comme dans le jeu de base."""
    fanny_companion.country_tier = tier
    fanny_companion._ending_played = False
    fanny_companion._set_pose(tier)
    fanny_companion._set_dialogue(tier, play_audio=False)
    fanny_companion._play_anthem(tier)
    ingamebackground.update_for_tier(tier, False)

def start_quiz(tier):
    global gamestate, quiz_tier, quiz_index, quiz_score, quiz_phase, quiz_selected, quiz_phase_start
    gamestate = 3
    quiz_tier = tier
    quiz_index = 0
    quiz_score = 0
    quiz_phase = "asking"
    quiz_selected = None
    quiz_phase_start = pygame.time.get_ticks()
    goto_country(tier)
    question, choices, _correct_index, _explanation = QUIZ_QUESTIONS[tier][0]
    queue_quiz_audio([question] + choices)

def start_mode_select():
    """Dès qu'un crédit est disponible (gamestate 0) : écran de choix du
    continent (voir QUIZ_MODES), affiché AVANT le décompte "GAME START IN"
    (désormais dans start_pregame_countdown(), gamestate 5) - demande
    utilisateur du 2026-07-15 : l'écran de choix du continent doit se
    situer entre l'accueil et le countdown, pas après. Navigation
    carrousel E (précédent) / R (valider) / T (suivant) - seuls boutons
    physiques disponibles sur la borne (3 cibles, pas de clavier ni de
    flèches). time_left amorce le timeout de CONTINENT_SELECT_TIMEOUT
    secondes (voir gamestate 4 dans la boucle principale) : au bout de ce
    délai sans choix du joueur, la partie se lance sur le mode
    actuellement affiché par le carrousel, comme un appui sur R - demande
    utilisateur du 2026-07-16."""
    global gamestate, mode_select_index, time_left
    gamestate = 4
    mode_select_index = 0
    time_left = CONTINENT_SELECT_TIMEOUT

def start_pregame_countdown():
    """Après validation du continent (gamestate 4, touche R ou timeout de
    CONTINENT_SELECT_TIMEOUT) : décompte "GAME START IN" repris de
    l'ancien gamestate 0 (avant l'ajout de la sélection de continent),
    déplacé après le choix plutôt qu'avant. La musique de menu, laissée
    intacte pendant tout l'écran de sélection du continent (demande
    utilisateur du 2026-07-16), ne commence à s'éteindre qu'à partir d'ici."""
    global gamestate, time_left
    channel1.fadeout(9000)
    gamestate = 5
    time_left = intro_length

def start_quiz_mode(mode_index):
    """Lance le mode choisi à l'écran de sélection : remet le total à zéro
    et démarre le premier pays de la liste de tiers du mode (continent ou
    tour complet, cf. QUIZ_MODES)."""
    global quiz_mode_tiers, quiz_position, quiz_total_correct, quiz_is_full_tour
    _name, tiers = QUIZ_MODES[mode_index]
    quiz_mode_tiers = tiers
    quiz_position = 0
    quiz_is_full_tour = (mode_index == 0)
    quiz_total_correct = 0
    ingamebackground.reset(False)
    start_quiz(quiz_mode_tiers[0])

def quiz_answer(choice_index):
    """Appelée quand le joueur répond (E/R/T = choix 0/1/2). Ignorée hors
    phase "asking" (pas de double-validation pendant le feedback)."""
    global quiz_phase, quiz_selected, quiz_score, quiz_phase_start, quiz_total_correct
    if quiz_phase != "asking":
        return
    quiz_selected = choice_index
    _question, _choices, correct_index, _explanation = QUIZ_QUESTIONS[quiz_tier][quiz_index]
    if choice_index == correct_index:
        quiz_score += 1
        quiz_total_correct += 1
        if sound_effects:
            channel2.play(sfx_hit)
    quiz_phase = "feedback"
    quiz_phase_start = pygame.time.get_ticks()
    queue_quiz_audio([])  # coupe la narration des choix restants

def quiz_timeout():
    """Le joueur n'a pas répondu dans les QUIZ_ANSWER_TIME_MS (60s)
    impartis : bascule en feedback sans sélection (comme un choix manqué),
    sans incrémenter le score - le compte à rebours affiché doit
    correspondre à une vraie limite, pas être décoratif."""
    global quiz_phase, quiz_phase_start
    quiz_phase = "feedback"
    quiz_phase_start = pygame.time.get_ticks()
    queue_quiz_audio([])

def finish_quiz_tour():
    """Dernier pays du mode choisi terminé : bascule vers l'écran de fin,
    score = total de bonnes réponses sur le mode joué. N'alimente
    quizz_high_score que pour le mode "Tour complet" (voir
    quiz_is_full_tour) - un score sur un seul continent n'est pas
    comparable au score max calibré sur les 115 pays."""
    global gamestate, score, time_left, quizz_high_score
    score = quiz_total_correct
    # Vérifié une seule fois ici, au moment où le score devient définitif
    # (pas à chaque frame de l'écran de fin comme avant :
    # save_high_score_quizz() réécrivait config.ini plusieurs centaines de
    # fois sur les ~10s de l'écran de fin, sans changer le résultat
    # affiché) - trouvé en vérifiant la correspondance score final/high
    # score, demande utilisateur du 2026-07-16.
    if quiz_is_full_tour and score >= quizz_high_score:
        quizz_high_score = score
        save_high_score_quizz(quizz_high_score)
    time_left = ending_length
    ingamebackground.freeze_for_ending()
    fanny_companion.stop_anthem()
    queue_quiz_audio([])
    gamestate = 2

def quiz_next_question():
    """Question suivante (ou récap après la 5e) - appelée soit après le
    délai d'explication (QUIZ_EXPLANATION_MS), soit immédiatement si le
    joueur appuie sur une touche pour passer l'explication de Fanny."""
    global quiz_index, quiz_phase, quiz_selected, quiz_phase_start
    now = pygame.time.get_ticks()
    if quiz_index < 4:
        quiz_index += 1
        quiz_selected = None
        quiz_phase = "asking"
        quiz_phase_start = now
        question, choices, _correct_index, _explanation = QUIZ_QUESTIONS[quiz_tier][quiz_index]
        queue_quiz_audio([question] + choices)
    else:
        quiz_phase = "recap"
        quiz_phase_start = now
        queue_quiz_audio([])

def quiz_advance():
    """Avance le quizz : asking (60s max) -> feedback -> explication de
    Fanny -> question suivante (ou récap après la 5e) -> pays suivant (ou
    écran de fin si c'était le dernier)."""
    global quiz_phase, quiz_phase_start, quiz_explanation_ms, quiz_position
    now = pygame.time.get_ticks()
    elapsed = now - quiz_phase_start
    if quiz_phase == "asking" and elapsed >= QUIZ_ANSWER_TIME_MS:
        quiz_timeout()
    elif quiz_phase == "feedback" and elapsed >= QUIZ_FEEDBACK_MS:
        quiz_phase = "explanation"
        quiz_phase_start = now
        _question, _choices, _correct_index, explanation = QUIZ_QUESTIONS[quiz_tier][quiz_index]
        queue_quiz_audio([explanation])
        # Le passage à la question suivante ne doit jamais couper le son de
        # l'explication en cours : si le fichier audio dure plus longtemps
        # que QUIZ_EXPLANATION_MS, on attend la fin du son (+ marge) avant
        # d'avancer. Sans audio (fichier manquant), on garde le délai de
        # lecture par défaut.
        explanation_sound = get_quiz_audio(explanation)
        if explanation_sound is not None:
            quiz_explanation_ms = max(QUIZ_EXPLANATION_MS, round(explanation_sound.get_length() * 1000) + 300)
        else:
            quiz_explanation_ms = QUIZ_EXPLANATION_MS
    elif quiz_phase == "explanation" and elapsed >= quiz_explanation_ms:
        quiz_next_question()
    elif quiz_phase == "recap" and elapsed >= QUIZ_RECAP_MS:
        if quiz_position + 1 < len(quiz_mode_tiers):
            quiz_position += 1
            start_quiz(quiz_mode_tiers[quiz_position])
        else:
            finish_quiz_tour()

def draw_mode_select():
    """Écran de choix du mode (gamestate 4) : un mode affiché à la fois au
    centre (carrousel), avec le nombre de pays qu'il contient - navigation
    E (précédent) / R (valider) / T (suivant), matérialisée par les boules
    du socle physique (gauche/centre/droite, voir
    init_mode_select_cibles) plutôt que des flèches/lettres, le joueur
    n'ayant pas de clavier sous les yeux - demande utilisateur du
    2026-07-16."""
    ecran.blit(title_screen_image, (0, 0))
    name, tiers = QUIZ_MODES[mode_select_index]

    draw_quiz_text("Choisis ton mode de jeu", LARGEUR_ECRAN/2, HAUTEUR_ECRAN*0.16, True, QUIZ_FONT_TITLE, 4)
    ecran.blit(mode_select_cibles[0].image, mode_select_cibles[0].rect)
    ecran.blit(mode_select_cibles[2].image, mode_select_cibles[2].rect)
    draw_quiz_text(name, LARGEUR_ECRAN/2, HAUTEUR_ECRAN/2, True, QUIZ_FONT_RECAP, 5)
    draw_quiz_text(f"{len(tiers)} pays", LARGEUR_ECRAN/2, HAUTEUR_ECRAN*0.62, True, QUIZ_FONT_QUESTION, 4)
    ecran.blit(mode_select_cibles[1].image, mode_select_cibles[1].rect)
    draw_quiz_text("Valider", LARGEUR_ECRAN/2, HAUTEUR_ECRAN*0.82, True, QUIZ_FONT_CHOICE, 4)

def draw_quiz():
    pays = WORLD_TOUR_COUNTRIES[quiz_tier][0]
    ecran.blit(ingamebackground.image, ingamebackground.rect)

    draw_quiz_text(f"QUIZZ — {pays} ({quiz_position + 1}/{len(quiz_mode_tiers)})",
                    LARGEUR_ECRAN/2, HAUTEUR_ECRAN*0.08, True, QUIZ_FONT_TITLE, 4)

    draw_quiz_fanny_and_timer(quiz_phase, quiz_phase_start)

    if quiz_phase == "recap":
        draw_quiz_text(f"{quiz_score} / 5 bonnes réponses", LARGEUR_ECRAN/2, HAUTEUR_ECRAN/2, True, QUIZ_FONT_RECAP, 5)
        draw_crt()
        pygame.display.flip()
        return

    question, choices, correct_index, explanation = QUIZ_QUESTIONS[quiz_tier][quiz_index]

    if quiz_phase == "explanation":
        # Fanny explique la bonne réponse, à la place de l'énoncé de la
        # question (les choix restent affichés et coloriés en dessous).
        draw_quiz_text_wrapped(
            f"« {explanation} »",
            LARGEUR_ECRAN/2, HAUTEUR_ECRAN*0.2, True, QUIZ_FONT_QUESTION, 5,
            LARGEUR_ECRAN*0.85, HAUTEUR_ECRAN*0.058,
        )
    else:
        draw_quiz_text_wrapped(
            f"Question {quiz_index + 1}/5 : {question}",
            LARGEUR_ECRAN/2, HAUTEUR_ECRAN*0.2, True, QUIZ_FONT_QUESTION, 4,
            LARGEUR_ECRAN*0.85, HAUTEUR_ECRAN*0.058,
        )

    for i, choice in enumerate(choices):
        col = 4  # bleu par défaut (pas encore répondu)
        if quiz_phase in ("feedback", "explanation"):
            if i == correct_index:
                col = 5  # vert : bonne réponse
            elif i == quiz_selected:
                col = 1  # rouge : ce que le joueur a choisi (et qui était faux)
            else:
                col = 3
        draw_quiz_text_wrapped(
            choice, QUIZ_CHOICE_X[i], HAUTEUR_ECRAN*0.48, True, QUIZ_FONT_CHOICE, col,
            QUIZ_CHOICE_MAX_WIDTH, HAUTEUR_ECRAN*0.052,
        )

    draw_quiz_cibles(quiz_phase, correct_index)

    if debug_line == True:
        debug_lines()
    draw_fps()
    draw_crt()
    pygame.display.flip()

#-------------------------DEBUT DU Programme ---------------------------
print("loading sprites")
ingamebackground = WorldTourBackground()

try:
    sfx_hit    = pygame.mixer.Sound('./assets/Sounds/Son3.wav')
    music_intro = pygame.mixer.Sound('./assets/Sounds/intro.wav')
    music_menu  = pygame.mixer.Sound('./assets/Sounds/Arducible vibe.mp3')
except pygame.error as e:
    print(f"Erreur chargement audio : {e}")
    raise SystemExit(1)

pygame.display.set_caption("Fanny Pétanque World Tour Quizz - An #ARDUCIBLE pétanque game")
icon = pygame.image.load("assets/icons/192x192.png")
pygame.display.set_icon(icon)

if Fullscreen:
    ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SCALED | pygame.FULLSCREEN, vsync=1)
else:
    ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SCALED)

fanny = FannySpinner()
fanny_companion = FannyCompanion()
init_quiz_cibles()
init_mode_select_cibles()

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

# état du quizz (voir start_quiz/quiz_answer/quiz_advance/draw_quiz)
quiz_tier = 0
quiz_index = 0
quiz_score = 0
quiz_phase = "asking"
quiz_selected = None
quiz_phase_start = 0
quiz_explanation_ms = QUIZ_EXPLANATION_MS
quiz_total_correct = 0
score = 0

# état du mode choisi (voir start_mode_select/start_quiz_mode/QUIZ_MODES)
quiz_mode_tiers = QUIZ_MODES[0][1]
quiz_position = 0
quiz_is_full_tour = True
mode_select_index = 0


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
                # En freeplay, presser une touche de quizz équivaut à
                # insérer un crédit fictif.
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
            # choix du continent (gamestate 5, voir start_pregame_countdown)
            # - demande utilisateur du 2026-07-15. La musique de menu
            # continue de jouer pendant tout l'écran de sélection du
            # continent (demande utilisateur du 2026-07-16) : son fondu
            # est déclenché plus tard, dans start_pregame_countdown().
            credit_left = credit_left - 1
            start_mode_select()

        draw_crt()
        pygame.display.flip()

    #-----------------------Continent select scene------------------------
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
                if event.key == pygame.K_e:
                    mode_select_index = (mode_select_index - 1) % len(QUIZ_MODES)
                elif event.key == pygame.K_t:
                    mode_select_index = (mode_select_index + 1) % len(QUIZ_MODES)
                elif event.key == pygame.K_r:
                    start_pregame_countdown()

        countdown()
        draw_mode_select()
        draw_crt()
        pygame.display.flip()
        if time_left <= 0:
            start_pregame_countdown()

    #-----------------------Pregame countdown scene------------------------
    if gamestate == 5:
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
            start_quiz_mode(mode_select_index)

        draw_crt()
        pygame.display.flip()

    #-----------------------Quizz scene----------------------------------
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
                if quiz_phase == "explanation" and event.key in TARGET_KEYS:
                    # Passer directement à la question suivante sans
                    # attendre la fin du délai d'explication (choix
                    # explicite du joueur - contrairement au délai
                    # automatique, ça peut couper le son en cours).
                    quiz_next_question()
                elif event.key == pygame.K_e:
                    quiz_answer(0)
                elif event.key == pygame.K_r:
                    quiz_answer(1)
                elif event.key == pygame.K_t:
                    quiz_answer(2)

        quiz_advance()
        update_quiz_audio()
        draw_quiz()

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
