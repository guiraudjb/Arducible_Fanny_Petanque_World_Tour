# -*- coding: utf-8 -*-
"""Génère les icônes PWA de la Belote (games/belote/icons/) : un fond en
dégradé radial reprenant la palette du tapis (--felt-1/--felt-2/--table-bg
de games/belote/style.css) avec un pique doré centré. Un simple symbole
d'enseigne plutôt qu'une face de carte illustrée : ça reste lisible à
16-48px (barre des tâches, favicon) là où une illustration détaillée
deviendrait un bouillie de pixels.

Usage : python3 "ressources/card game/tools/generate_belote_pwa_icons.py"
(Pillow + la police DejaVu Sans du système, pas besoin du venv gTTS.)

Écrit :
  games/belote/icons/icon-192.png            (any)
  games/belote/icons/icon-512.png            (any)
  games/belote/icons/icon-512-maskable.png   (maskable : contenu dans la
                                               zone de sécurité centrale)
  games/belote/icons/apple-touch-icon.png    (180x180, opaque)
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CARD_GAME_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
OUT_DIR = os.path.join(_CARD_GAME_ROOT, "games", "belote", "icons")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

FELT_1 = (0x2F, 0x6E, 0x3F)   # centre du tapis
FELT_2 = (0x1C, 0x4E, 0x28)   # bord du tapis
TABLE_BG = (0x1C, 0x13, 0x0B)  # coins, assombri (vignette)
GOLD = (0xFF, 0xD5, 0x4F)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def felt_background(size):
    """Dégradé radial felt-1 -> felt-2 -> table-bg, calculé sur une petite
    grille puis agrandi (lissage par le redimensionnement bicubique)."""
    grid = 64
    base = Image.new("RGB", (grid, grid))
    px = base.load()
    cx = cy = (grid - 1) / 2
    max_dist = (cx ** 2 + cy ** 2) ** 0.5  # coin le plus loin du centre
    for y in range(grid):
        for x in range(grid):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / max_dist
            if d <= 0.55:
                color = lerp(FELT_1, FELT_2, d / 0.55)
            else:
                color = lerp(FELT_2, TABLE_BG, min(1.0, (d - 0.55) / 0.45))
            px[x, y] = color
    return base.resize((size, size), Image.BICUBIC)


def spade_layer(size, scale, shadow):
    """Rendu du glyphe ♠ (DejaVu Sans) sur un calque transparent, avec une
    ombre portée douce optionnelle (désactivée pour la version maskable,
    où le contenu doit rester net dans la zone de sécurité)."""
    # DejaVu dessine le glyphe avec une bonne marge interne : on sur-dimensionne
    # la police puis on recadre sur le rendu réel (bbox) pour que `scale`
    # corresponde à la taille visuelle du pique, pas à sa boîte de police.
    probe_size = size * 2
    font = ImageFont.truetype(FONT_PATH, probe_size)
    probe = Image.new("L", (probe_size * 2, probe_size * 2), 0)
    d = ImageDraw.Draw(probe)
    d.text((probe_size // 2, probe_size // 2), "♠", font=font, fill=255, anchor="mm")
    bbox = probe.getbbox()
    glyph_h = bbox[3] - bbox[1]

    target_h = size * scale
    font_size = round(probe_size * (target_h / glyph_h))
    font = ImageFont.truetype(FONT_PATH, font_size)

    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text((size / 2, size / 2), "♠", font=font, fill=GOLD, anchor="mm")

    if shadow:
        shadow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow_layer)
        offset = max(2, size // 70)
        sd.text((size / 2 + offset, size / 2 + offset * 1.4), "♠", font=font, fill=(0, 0, 0, 150), anchor="mm")
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(size * 0.015))
        base = Image.alpha_composite(shadow_layer, layer)
        return base
    return layer


def make_icon(size, scale, shadow, opaque=False):
    bg = felt_background(size).convert("RGBA")
    icon = Image.alpha_composite(bg, spade_layer(size, scale, shadow))
    if opaque:
        icon = icon.convert("RGB")
    return icon


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    make_icon(192, 0.62, shadow=True).save(os.path.join(OUT_DIR, "icon-192.png"))
    make_icon(512, 0.62, shadow=True).save(os.path.join(OUT_DIR, "icon-512.png"))
    # Maskable : contenu dans la zone de sécurité (cercle central ~80%),
    # donc plus petit et sans ombre débordante, pour ne jamais être rogné
    # par le masque (rond, arrondi...) que l'OS applique par-dessus.
    make_icon(512, 0.42, shadow=False).save(os.path.join(OUT_DIR, "icon-512-maskable.png"))
    # apple-touch-icon : iOS ignore la transparence et arrondit lui-même les
    # coins, donc un fond plein convient tel quel.
    make_icon(180, 0.62, shadow=True, opaque=True).save(os.path.join(OUT_DIR, "apple-touch-icon.png"))

    print("Icônes générées dans", OUT_DIR)


if __name__ == "__main__":
    main()
