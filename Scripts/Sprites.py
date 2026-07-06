import os
import random
import pygame
from pygame import *
from Scripts.init import *
from Scripts.dialogues import WORLD_TOUR_COUNTRIES, get_country_tier

class Cible(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(pygame.image.load('./assets/Images/Boule.png'))
        self.images.append(pygame.image.load('./assets/Images/BouleG.png'))
        self.images.append(pygame.image.load('./assets/Images/BouleGold.png'))
        for i in range(len(self.images)):
            self.images[i] = pygame.transform.scale(self.images[i], (LARGEUR_ECRAN*0.25, HAUTEUR_ECRAN*0.44))
        self.image = self.images[0]
        self.rect = self.image.get_rect()


class ColoredRing(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(pygame.image.load('./assets/Images/Background/redring.png'))
        self.images.append(pygame.image.load('./assets/Images/Background/greenring.png'))
        for i in range(len(self.images)):
            self.images[i] = pygame.transform.scale(self.images[i], (258 * LARGEUR_ECRAN/1920, 395 * HAUTEUR_ECRAN/1080))
        self.image = self.images[0]
        self.rect = self.image.get_rect()


class WorldTourBackground(pygame.sprite.Sprite):
    """Fond de jeu "World Tour" : un par pays (WORLD_TOUR_COUNTRIES), suit
    fanny_companion.country_tier au lieu du cycle par score de `Background`.
    La banque (assets/Images/BackgroundWorldTour/) peut être incomplète tant
    que le batch Krea2 tourne : un pays sans fond conserve simplement le
    dernier fond affiché, comme les portraits de FannyCompanion. Le trou
    webcam ovale de la variante .png est découpé aux mêmes coordonnées que
    les 9 fonds du jeu de base (cf. build_world_tour_backgrounds.py)."""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.no_webcam_images = {}
        self.webcam_images = {}
        for tier, (_pays, slug, _text) in enumerate(WORLD_TOUR_COUNTRIES):
            jpg_path = f'./assets/Images/BackgroundWorldTour/{tier + 1:03d}_{slug}.jpg'
            png_path = f'./assets/Images/BackgroundWorldTour/{tier + 1:03d}_{slug}.png'
            if os.path.isfile(jpg_path):
                jpg = pygame.image.load(jpg_path)
                jpg = pygame.transform.scale(jpg, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
                self.no_webcam_images[tier] = jpg
            if os.path.isfile(png_path):
                png = pygame.image.load(png_path)
                png = pygame.transform.scale(png, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
                self.webcam_images[tier] = png
        self.tier = 0
        self.image = None
        self.rect = None
        self._resolve(0, False)

    def _resolve(self, tier, webcam_compatibility):
        images = self.webcam_images if webcam_compatibility else self.no_webcam_images
        if tier in images:
            self.image = images[tier]
        elif self.image is None:
            # aucun fond dispo pour l'instant (même pas le premier pays) :
            # couleur de secours plutôt qu'un crash au tout premier lancement
            self.image = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
            self.image.fill((20, 20, 20))
        # sinon : pays sans fond généré, on garde le fond précédent
        self.rect = self.image.get_rect()

    def update_for_tier(self, tier, webcam_compatibility):
        """À appeler chaque frame en jeu (gamestate==1) : choisit le fond
        correspondant au pays courant, dans la variante webcam ou non."""
        self.tier = tier
        self._resolve(tier, webcam_compatibility)

    def freeze_for_ending(self):
        """Écran de fin : toujours la variante SANS webcam, du fond qui
        était affiché au dernier coup de la manche."""
        self._resolve(self.tier, False)

    def reset(self, webcam_compatibility):
        self.tier = 0
        self._resolve(0, webcam_compatibility)


class FannySpinner(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        original = pygame.image.load('./assets/Images/fanny_10x10cm.png').convert_alpha()
        target_size = int(HAUTEUR_ECRAN * 0.22)
        self._original = pygame.transform.smoothscale(original, (target_size, target_size))
        self._angle = 0
        self.image = self._original
        self.rect = self.image.get_rect()

    def update(self, speed=2):
        self._angle = (self._angle - speed) % 360
        cx, cy = self.rect.center
        self.image = pygame.transform.rotate(self._original, self._angle)
        self.rect = self.image.get_rect(center=(cx, cy))

    def draw(self, surface, cx, cy):
        self.rect.center = (cx, cy)
        surface.blit(self.image, self.rect)


_dialogue_font = pygame.font.SysFont("Arial", max(14, round(HAUTEUR_ECRAN / 42)))
_BUBBLE_BG = (255, 255, 255, 235)
_BUBBLE_BORDER = (40, 40, 40)
_BUBBLE_TEXT = (20, 20, 20)
_BUBBLE_PADDING = 12


def _wrap_text(text, font, max_width):
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


def build_bubble_surface(text, width):
    """Construit la surface de la bulle de dialogue à une LARGEUR FIXE
    (indépendante du texte, pour que la position de Fanny ne bouge pas
    quand la réplique change) ; seule la hauteur varie selon le nombre de
    lignes. À appeler uniquement quand le texte change, pas à chaque frame."""
    available_width = width - 2 * _BUBBLE_PADDING
    lines = _wrap_text(text, _dialogue_font, available_width)
    line_surfaces = [_dialogue_font.render(line, True, _BUBBLE_TEXT) for line in lines]
    # Un mot isolé trop long pour available_width (résolutions très basses,
    # mots français longs) ne peut pas être coupé par _wrap_text : on le
    # réduit pour qu'il ne déborde jamais du cadre fixe de la bulle.
    for i, line_surf in enumerate(line_surfaces):
        if line_surf.get_width() > available_width:
            line_surfaces[i] = pygame.transform.smoothscale(
                line_surf, (available_width, line_surf.get_height())
            )
    line_height = _dialogue_font.get_linesize()
    height = line_height * len(line_surfaces) + 2 * _BUBBLE_PADDING

    bubble = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(bubble, _BUBBLE_BG, bubble.get_rect(), border_radius=14)
    pygame.draw.rect(bubble, _BUBBLE_BORDER, bubble.get_rect(), width=2, border_radius=14)
    for i, line_surf in enumerate(line_surfaces):
        bubble.blit(line_surf, (_BUBBLE_PADDING, _BUBBLE_PADDING + i * line_height))
    return bubble


class ShuffleBag:
    """Pioche des indices 0..n-1 sans répétition jusqu'à épuisement du sac,
    puis remélange et recommence. Garantit qu'une pose ou une réplique
    n'est jamais réutilisée avant que toutes les autres du même palier
    soient passées."""

    def __init__(self, size):
        self._size = size
        self._bag = []

    def draw(self):
        if not self._bag:
            self._bag = list(range(self._size))
            random.shuffle(self._bag)
        return self._bag.pop()

    def reset(self):
        self._bag = []


class FannyCompanion(pygame.sprite.Sprite):
    """Compagnon in-game de Fanny, ancré dans le coin supérieur droit de
    l'écran : bulle de dialogue à gauche, personnage à droite de la bulle.
    Version "World Tour" : un nouveau PAYS toutes les COUNTRY_SCORE_SEUIL
    points (get_country_tier, cf. Scripts/dialogues.py, généré depuis
    fanny wold tour/speach.txt + pays_index.txt) — le portrait de Fanny et
    sa réplique changent ensemble, contrairement à l'ancien système à deux
    progressions découplées (pose/dialogue) du jeu de base. La banque de
    portraits (assets/Images/FannyWorldTour/) peut être incomplète tant que
    le batch Krea2 tourne : un pays sans image conserve simplement le
    dernier portrait affiché plutôt que de planter. La surface de la bulle
    et l'image du personnage ne sont recalculées que lorsque le pays change
    réellement (pas à chaque frame) ; le dimensionnement (taille du
    sprite, largeur de bulle, marges) est proportionnel à
    LARGEUR_ECRAN/HAUTEUR_ECRAN, donc cohérent quelle que soit la
    résolution choisie dans config.ini (1920x1080, 1280x720, 640x360,
    426x240, ou 1024x768 par défaut)."""

    ENDING_INVITE_TEXT = "Retente ta chance, je ne demande que ça."
    ENDING_VOICE_PATH = './assets/Sounds/VoicesFanny/ending_invite.wav'
    ANTHEM_CROSSFADE_MS = 1500

    def __init__(self, country_max_tier=None):
        pygame.sprite.Sprite.__init__(self)
        self.country_max_tier = (
            len(WORLD_TOUR_COUNTRIES) - 1 if country_max_tier is None else country_max_tier
        )
        self.gap = int(LARGEUR_ECRAN * 0.015)
        self.bubble_width = int(LARGEUR_ECRAN * 0.22)

        target_height = int(HAUTEUR_ECRAN * 0.45)
        self.tier_images = {}
        for tier, (pays, slug, _text) in enumerate(WORLD_TOUR_COUNTRIES):
            path = f'./assets/Images/FannyWorldTour/{tier + 1:03d}_{slug}.png'
            if os.path.isfile(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_rect().size
                ratio = target_height / h
                self.tier_images[tier] = pygame.transform.smoothscale(img, (int(w * ratio), target_height))

        fallback = pygame.image.load('./assets/Images/fanny_10x10cm.png').convert_alpha()
        fw, fh = fallback.get_rect().size
        ratio = target_height / fh
        self._fallback_image = pygame.transform.smoothscale(fallback, (int(fw * ratio), target_height))

        map_height = int(HAUTEUR_ECRAN * 0.25)
        self.map_images = {}
        for tier, (_pays, slug, _text) in enumerate(WORLD_TOUR_COUNTRIES):
            path = f'./assets/Images/CountryMapsWorldTour/{tier + 1:03d}_{slug}.png'
            if os.path.isfile(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_rect().size
                ratio = map_height / h
                self.map_images[tier] = pygame.transform.smoothscale(img, (int(w * ratio), map_height))
        self.map_image = self.map_images.get(0)

        self.ending_bubble = build_bubble_surface(self.ENDING_INVITE_TEXT, self.bubble_width)
        self._ending_played = False

        self._anthem_channels = (channel5, channel6)
        self._anthem_active = 0

        # État initial (menu/attract) : pose + texte du premier pays préparés
        # pour l'affichage, mais SANS jouer sa voix ni son hymne — ceux-ci ne
        # doivent démarrer qu'au vrai début de manche, via reset().
        self.country_tier = 0
        self._ending_played = False
        self._set_pose(0)
        self._set_dialogue(0, play_audio=False)

    def _play_anthem(self, tier):
        """Bascule vers l'hymne du pays `tier`, en fondu croisé avec celui
        qui jouait déjà (fade-out de l'ancien + fade-in du nouveau sur
        l'autre canal, joués en boucle tant que le pays reste affiché).
        Certains pays n'ont pas d'hymne dans le téléchargement Navy Band
        (cf. build_world_tour_anthems.py) : dans ce cas on fait juste
        silence (fade-out de l'ancien, rien ne redémarre)."""
        _pays, slug, _text = WORLD_TOUR_COUNTRIES[tier]
        old_channel = self._anthem_channels[self._anthem_active]
        new_index = 1 - self._anthem_active
        new_channel = self._anthem_channels[new_index]

        old_channel.fadeout(self.ANTHEM_CROSSFADE_MS)

        anthem_path = f'./assets/Sounds/AnthemsWorldTour/{tier + 1:03d}_{slug}.mp3'
        if os.path.isfile(anthem_path):
            try:
                new_channel.play(pygame.mixer.Sound(anthem_path), loops=-1, fade_ms=self.ANTHEM_CROSSFADE_MS)
                self._anthem_active = new_index
            except pygame.error:
                pass  # pas d'hymne lisible pour ce pays, on garde juste le silence

    def stop_anthem(self):
        """Coupe l'hymne en cours (fin de manche) : à appeler quand on
        quitte l'écran de jeu, pour ne pas le laisser jouer sur l'écran de
        fin/le menu."""
        for ch in self._anthem_channels:
            ch.fadeout(self.ANTHEM_CROSSFADE_MS)

    def _set_dialogue(self, tier, play_audio=True):
        _pays, slug, text = WORLD_TOUR_COUNTRIES[tier]
        self.dialogue = text
        self.bubble_surface = build_bubble_surface(text, self.bubble_width)

        if not play_audio:
            return  # affichage initial (menu) : texte préparé mais pas encore "prononcé"

        voice_path = f'./assets/Sounds/VoicesFannyWorldTour/{tier + 1:03d}_{slug}.wav'
        if os.path.isfile(voice_path):
            try:
                channel4.play(pygame.mixer.Sound(voice_path))
            except pygame.error:
                pass  # pas de voix générée pour cette réplique, on garde juste le texte

    def _set_pose(self, tier):
        if tier in self.tier_images:
            self.image = self.tier_images[tier]
        elif not hasattr(self, "image"):
            self.image = self._fallback_image
        # sinon : portrait pas encore généré pour ce pays, on garde l'image précédente
        self.rect = self.image.get_rect()

        if tier in self.map_images:
            self.map_image = self.map_images[tier]
        # sinon : carte pas encore générée pour ce pays, on garde la précédente

    def reset(self):
        self.country_tier = 0
        self._ending_played = False
        self._set_pose(0)
        self._set_dialogue(0)
        self._play_anthem(0)

    def on_score_update(self, score):
        """Retourne True si ce coup vient de faire changer de pays (pour
        que main.py puisse accorder le bonus de temps correspondant)."""
        new_tier = min(get_country_tier(score, score_seuil=hits_per_country), self.country_max_tier)
        if new_tier != self.country_tier:
            self.country_tier = new_tier
            self._set_pose(new_tier)
            self._set_dialogue(new_tier)
            self._play_anthem(new_tier)
            return True
        return False

    def draw(self, surface, right_x, y):
        """(right_x, y) est le coin supérieur DROIT du personnage, destiné
        à rester dans le coin supérieur droit de l'écran. La bulle de
        dialogue est placée à gauche du personnage (largeur fixe, donc le
        personnage ne bouge pas horizontalement quand le texte change), et
        la mini-carte du pays courant sous la bulle, dans la même colonne
        (jamais collée à la bulle même si le texte fait plusieurs lignes) —
        elle se retrouve ainsi naturellement à côté des pieds de Fanny,
        celle-ci étant bien plus haute que la bulle."""
        self.rect.topright = (right_x, y)
        bubble_x = self.rect.left - self.gap - self.bubble_width
        bubble_rect = self.bubble_surface.get_rect(topleft=(bubble_x, y))
        surface.blit(self.bubble_surface, bubble_rect)
        surface.blit(self.image, self.rect)

        if self.map_image:
            map_rect = self.map_image.get_rect()
            map_rect.left = bubble_x
            map_rect.top = bubble_rect.bottom + self.gap
            surface.blit(self.map_image, map_rect)

    def draw_ending(self, surface, cx, top_y):
        """Écran de fin de manche (score > 0) : affiche la dernière pose
        débloquée (self.image, déjà à jour depuis la partie) avec une
        invitation à retenter sa chance, dans une bulle au-dessus."""
        bubble_rect = self.ending_bubble.get_rect(midtop=(cx, top_y))
        surface.blit(self.ending_bubble, bubble_rect)
        self.rect.midtop = (cx, bubble_rect.bottom + self.gap)
        surface.blit(self.image, self.rect)
        if not self._ending_played:
            self._ending_played = True
            if os.path.isfile(self.ENDING_VOICE_PATH):
                try:
                    channel4.play(pygame.mixer.Sound(self.ENDING_VOICE_PATH))
                except pygame.error:
                    pass
