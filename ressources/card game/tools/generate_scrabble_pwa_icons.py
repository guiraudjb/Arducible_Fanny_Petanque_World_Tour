# -*- coding: utf-8 -*-
"""Génère les icônes PWA du Scrabble (games/scrabble/icons/) : même fond en
dégradé radial que la Belote (palette --felt-1/--felt-2/--table-bg,
partagée par les deux jeux), avec un jeton de Scrabble (lettre "S", valeur
1 point - lettre la plus emblématique du nom du jeu) reprenant le style du
jeton en jeu (.tile de style.css : dégradé crème/or, coins arrondis).

Usage : python3 "ressources/card game/tools/generate_scrabble_pwa_icons.py"
(Pillow + la police DejaVu Sans du système, pas besoin du venv gTTS.)

Écrit :
  games/scrabble/icons/icon-192.png            (any)
  games/scrabble/icons/icon-512.png            (any)
  games/scrabble/icons/icon-512-maskable.png   (maskable)
  games/scrabble/icons/apple-touch-icon.png    (180x180, opaque)
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CARD_GAME_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
OUT_DIR = os.path.join(_CARD_GAME_ROOT, "games", "scrabble", "icons")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FELT_1 = (0x2F, 0x6E, 0x3F)   # centre du tapis
FELT_2 = (0x1C, 0x4E, 0x28)   # bord du tapis
TABLE_BG = (0x1C, 0x13, 0x0B)  # coins, assombri (vignette)
TILE_TOP = (0xF4, 0xE4, 0xBC)
TILE_BOTTOM = (0xE2, 0xC9, 0x8F)
INK = (0x24, 0x1C, 0x13)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def felt_background(size):
    """Dégradé radial felt-1 -> felt-2 -> table-bg (identique à la Belote,
    même palette de tapis partagée entre les jeux du casino)."""
    grid = 64
    base = Image.new("RGB", (grid, grid))
    px = base.load()
    cx = cy = (grid - 1) / 2
    max_dist = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(grid):
        for x in range(grid):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / max_dist
            if d <= 0.55:
                color = lerp(FELT_1, FELT_2, d / 0.55)
            else:
                color = lerp(FELT_2, TABLE_BG, min(1.0, (d - 0.55) / 0.45))
            px[x, y] = color
    return base.resize((size, size), Image.BICUBIC)


def tile_gradient(w, h, radius):
    """Jeton crème->or (comme .tile en jeu), coins arrondis, sur fond
    transparent."""
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        grad.putpixel((0, y), lerp(TILE_TOP, TILE_BOTTOM, y / max(1, h - 1)))
    grad = grad.resize((w, h))

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)

    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tile.paste(grad, (0, 0), mask)
    return tile, mask


def tile_layer(size, scale, shadow, show_value=True):
    w = h = round(size * scale)
    radius = round(w * 0.14)
    tile, mask = tile_gradient(w, h, radius)

    draw = ImageDraw.Draw(tile)
    letter_font = ImageFont.truetype(FONT_BOLD_PATH, round(h * 0.62))
    draw.text((w / 2, h * 0.44), "S", font=letter_font, fill=INK, anchor="mm")
    if show_value:
        value_font = ImageFont.truetype(FONT_BOLD_PATH, round(h * 0.16))
        draw.text((w * 0.82, h * 0.82), "1", font=value_font, fill=INK, anchor="mm")

    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx = (size - w) // 2
    cy = (size - h) // 2

    if shadow:
        shadow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        shadow_mask = Image.new("L", (size, size), 0)
        offset = max(2, size // 60)
        shadow_mask.paste(mask, (cx + offset, cy + offset * 2))
        shadow_rgba = Image.new("RGBA", (size, size), (0, 0, 0, 140))
        shadow_rgba.putalpha(shadow_mask)
        shadow_layer = Image.alpha_composite(shadow_layer, shadow_rgba)
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(size * 0.018))
        layer = Image.alpha_composite(layer, shadow_layer)

    layer.paste(tile, (cx, cy), tile)
    return layer


def make_icon(size, scale, shadow, opaque=False, show_value=True):
    bg = felt_background(size).convert("RGBA")
    icon = Image.alpha_composite(bg, tile_layer(size, scale, shadow, show_value))
    if opaque:
        icon = icon.convert("RGB")
    return icon


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    make_icon(192, 0.62, shadow=True).save(os.path.join(OUT_DIR, "icon-192.png"))
    make_icon(512, 0.62, shadow=True).save(os.path.join(OUT_DIR, "icon-512.png"))
    # Maskable : contenu dans la zone de sécurité centrale, sans ombre
    # débordante, pour ne jamais être rogné par le masque de l'OS.
    make_icon(512, 0.44, shadow=False).save(os.path.join(OUT_DIR, "icon-512-maskable.png"))
    make_icon(180, 0.62, shadow=True, opaque=True).save(os.path.join(OUT_DIR, "apple-touch-icon.png"))

    print("Icônes générées dans", OUT_DIR)


if __name__ == "__main__":
    main()
