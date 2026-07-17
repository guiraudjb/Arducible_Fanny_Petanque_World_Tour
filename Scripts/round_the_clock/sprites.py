"""Sprites et éléments visuels pour Round the Clock.

Disposition des 7 cibles = étoile de David (6 boules sur les pointes de
l'étoile, cochonet au centre), coordonnées reprises telles quelles de
main/collections/InGame.collection du jeu Defold d'origine, puis
normalisées et remappées à l'écran courant."""
import os
import pygame
from Scripts.round_the_clock.state import LARGEUR_ECRAN, HAUTEUR_ECRAN

_IMG = "./assets/Images"
_RTC_IMG = "./assets/RoundTheClock/Images"

# (nx, ny) en fraction du canvas ENTIER 1920x1080 (celui de game.project),
# recopiées telles quelles des positions absolues de Target1..Target7 dans
# main/collections/InGame.collection (Target7 = cochonet, au centre exact
# du losange formé par les 6 autres cibles). Defold utilise un repère Y
# ASCENDANT (origine en bas), Pygame un repère Y DESCENDANT (origine en
# haut) : on inverse donc ny = 1 - y_defold/1080 pour que "devant" (proche
# du joueur, y_defold faible) reste bien en BAS de l'écran Pygame, et
# "derrière" (y_defold élevé) reste en HAUT - sans ça, les deux rangées de
# cibles se retrouvent inversées à l'écran.
TARGET_LAYOUT = [
    (300 / 1920, 1 - 360 / 1080),   # Target1
    (640 / 1920, 1 - 150 / 1080),   # Target2 (rangée avant)
    (980 / 1920, 1 - 360 / 1080),   # Target3
    (300 / 1920, 1 - 700 / 1080),   # Target4
    (980 / 1920, 1 - 700 / 1080),   # Target5 (rangée arrière)
    (640 / 1920, 1 - 910 / 1080),   # Target6
    (640 / 1920, 1 - 530 / 1080),   # Target7 = cochonet, au centre
]
COCHONET_INDEX = 6

# Positions du HUD (score, Touche/Rate, tirs restants, manche), en fraction
# du même canvas 1920x1080, reprises de main/IngameMenu.gui (le panneau de
# score occupe le tiers droit de l'écran, sur 2 colonnes x 3 lignes pour les
# 6 joueurs).
HUD_SCORE_COLUMNS_NX = (1336 / 1920, 1736 / 1920)
HUD_SCORE_ROWS_NY = (
    (1 - 964 / 1080, 1 - 864 / 1080),  # ligne J1/J2 : (label, score)
    (1 - 748 / 1080, 1 - 648 / 1080),  # ligne J3/J4
    (1 - 532 / 1080, 1 - 432 / 1080),  # ligne J5/J6
)
HUD_RESTE_NXY = (1536 / 1920, 1 - 128 / 1080)
HUD_TOUR_NXY = (1596 / 1920, 1 - 1036 / 1080)
HUD_CENTER_BANNER_NXY = (0.5, 1 - 623 / 1080)


def compute_target_centers(largeur_ecran, hauteur_ecran):
    """Retourne les 7 centres (x, y) à l'écran, simple mise à l'échelle des
    fractions absolues de TARGET_LAYOUT sur la résolution courante."""
    return [(nx * largeur_ecran, ny * hauteur_ecran) for nx, ny in TARGET_LAYOUT]


def hud_point(nxy, largeur_ecran, hauteur_ecran):
    nx, ny = nxy
    return nx * largeur_ecran, ny * hauteur_ecran


class Target(pygame.sprite.Sprite):
    """Une des 7 cibles physiques. États : idle (Boule), active (BouleG,
    la cible actuellement désignée), explosion (courte animation au
    moment du tir, hit ou raté), reprise de main.py::animate_cible."""

    EXPLOSION_FRAME_MS = 70

    def __init__(self, is_cochonet=False):
        pygame.sprite.Sprite.__init__(self)
        size = int(HAUTEUR_ECRAN * (0.08 if is_cochonet else 0.24))
        self.idle_image = pygame.transform.smoothscale(
            pygame.image.load(f"{_IMG}/Boule.png").convert_alpha(), (size, size))
        self.active_image = pygame.transform.smoothscale(
            pygame.image.load(f"{_IMG}/BouleG.png").convert_alpha(), (size, size))
        self.explosion_frames = [
            pygame.transform.smoothscale(
                pygame.image.load(f"{_RTC_IMG}/Explosion{i}.png").convert_alpha(), (size, size))
            for i in (1, 2, 3)
        ]
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.is_active = False
        self._exploding_until = 0
        self._explosion_start = 0

    def set_center(self, x, y):
        self.rect.center = (x, y)

    def set_active(self, active):
        self.is_active = active
        if not self._is_exploding():
            self.image = self.active_image if active else self.idle_image

    def trigger_explosion(self, now_ms):
        self._explosion_start = now_ms
        self._exploding_until = now_ms + self.EXPLOSION_FRAME_MS * len(self.explosion_frames)

    def _is_exploding(self):
        return self._exploding_until != 0

    def update(self, now_ms):
        if self._exploding_until == 0:
            return
        if now_ms >= self._exploding_until:
            self._exploding_until = 0
            self.image = self.active_image if self.is_active else self.idle_image
            return
        elapsed = now_ms - self._explosion_start
        frame = min(elapsed // self.EXPLOSION_FRAME_MS, len(self.explosion_frames) - 1)
        self.image = self.explosion_frames[int(frame)]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


_OUTLINE_COLOR = (10, 10, 10)


def draw_text(surface, text, x, y, center, font_pair, color_pair, blink=False, visible=True):
    """Texte plein (font_pair[0]/color_pair[0]) cerné d'un contour sombre
    (font_pair[1] en gras, dessiné à plusieurs offsets) pour rester lisible
    sur le fond en planches de bois, quelle que soit la couleur du texte -
    le principe "police décorative + variante creuse" de Fanny World Tour
    ne fonctionne pas avec DejaVu Sans (pas de variante creuse), remplacé
    ici par un contour classique jeu vidéo."""
    if blink and not visible:
        return
    font1, font2 = font_pair
    color1, _ = color_pair
    main_img = font1.render(str(text), True, color1)
    outline_img = font2.render(str(text), True, _OUTLINE_COLOR)
    w, h = main_img.get_rect().size
    ow, oh = outline_img.get_rect().size
    if center:
        base = (x - w / 2, y - h / 2)
        obase = (x - ow / 2, y - oh / 2)
    else:
        base = (x, y)
        obase = (x, y)
    offset = max(2, font1.get_height() // 14)
    for dx, dy in ((-offset, 0), (offset, 0), (0, -offset), (0, offset),
                   (-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)):
        surface.blit(outline_img, (obase[0] + dx, obase[1] + dy))
    surface.blit(main_img, base)


class ColoredRing(pygame.sprite.Sprite):
    """Indicateur de zone de tir webcam (rouge = hors zone, vert = zone
    correcte), même principe que ColoredRing dans Scripts/Sprites.py mais
    autonome (pas de dépendance à Scripts.init/dialogues.py de Fanny)."""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        size = (int(LARGEUR_ECRAN * 0.134), int(HAUTEUR_ECRAN * 0.366))
        self.images = [
            pygame.transform.scale(pygame.image.load(f"{_IMG}/Background/redring.png").convert_alpha(), size),
            pygame.transform.scale(pygame.image.load(f"{_IMG}/Background/greenring.png").convert_alpha(), size),
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.zone_interdite = True

    def set_zone_interdite(self, value):
        self.zone_interdite = value
        self.image = self.images[0] if value else self.images[1]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class WaitBanner:
    """Bandeau 'WAIT' plein écran affiché pendant l'anti-rebond en jeu :
    une image (assets/RoundTheClock/Images/bigcase.png, même texture que
    les boutons Touche/Rate) étirée sur toute la largeur, qui masque le
    plateau de jeu derrière elle le temps du cooldown - bien plus visible
    qu'un simple texte au milieu de l'écran."""

    def __init__(self):
        height = int(HAUTEUR_ECRAN * 0.24)
        img = pygame.image.load(f"{_RTC_IMG}/bigcase.png").convert_alpha()
        self.image = pygame.transform.smoothscale(img, (LARGEUR_ECRAN, height))
        self.rect = self.image.get_rect()

    def draw(self, surface, center_y, font_pair, color_pair):
        rect = self.image.get_rect(midtop=(LARGEUR_ECRAN / 2, center_y - self.rect.height / 2))
        surface.blit(self.image, rect)
        draw_text(surface, "WAIT", LARGEUR_ECRAN / 2, center_y, True, font_pair, color_pair)


class ShotsLeftBanner:
    """Bandeau 'tirs restants' (assets/RoundTheClock/Images/reste{1,2,3}.png),
    repris de IngameMenu.gui_script::updateShotLeft."""

    def __init__(self):
        width = int(LARGEUR_ECRAN * 0.16)
        self.images = {}
        for n in (1, 2, 3):
            img = pygame.image.load(f"{_RTC_IMG}/reste{n}.png").convert_alpha()
            w, h = img.get_rect().size
            height = int(width * h / w)
            self.images[n] = pygame.transform.smoothscale(img, (width, height))
        self.rect = self.images[3].get_rect()

    def draw(self, surface, reste, midtop):
        reste = max(1, min(3, reste))
        image = self.images[reste]
        rect = image.get_rect(midtop=midtop)
        surface.blit(image, rect)
