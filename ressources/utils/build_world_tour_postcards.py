#!/usr/bin/env python3
"""Génère une image "carte postale" par pays du Fanny World Tour, à partir
des assets déjà générés pour ce pays :
  - le décor ("fanny wold tour/Fanny Wold Tour Game/assets/Images/BackgroundWorldTour/{i:03d}_{slug}.jpg")
  - sa réplique ("fanny wold tour/speach.txt", ligne i)
  - la mini-carte du monde avec flèche ("...CountryMapsWorldTour/{i:03d}_{slug}.png")
  - le portrait de Fanny dans sa tenue typique du pays ("...FannyWorldTour/{i:03d}_{slug}.png")

Composition : décor en plein cadre (1920x1080), titre "FANNY PÉTANQUE WORLD
TOUR" en haut, bandeau de légende en bas avec le nom du pays + la réplique
de Fanny, mini-carte du monde encartée en haut à droite et Fanny (tenue du
pays) en bas à droite, façon "carte postale".

Sortie : "fanny wold tour/postcards/{i:03d}_{slug}.png" (un fichier par
pays, nommé comme tous les autres assets du pipeline World Tour).

Autres langues (ex. anglais, cf. build_world_tour_postcards_en.py) : le
NOM DE FICHIER des assets (décor/carte/Fanny) est toujours dérivé de
"pays_index.txt" (français, la clé stable du pipeline) via --pays-index ;
seul le TEXTE AFFICHÉ (titre du pays + réplique) change, via --pays-names
et --speach, qui peuvent pointer vers des fichiers traduits de même
longueur/ordre.

Usage :
    python3 build_world_tour_postcards.py [--force] [--limit N] [--only I,I,...]
        [--pays-index PATH] [--pays-names PATH] [--speach PATH] [--out-dir PATH]
"""
import argparse
import os
import re

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TOUR_DIR = os.path.join(PROJECT_ROOT, "fanny wold tour")
GAME_DIR = os.path.join(TOUR_DIR, "Fanny Wold Tour Game")
IMAGES_DIR = os.path.join(GAME_DIR, "assets", "Images")
PAYS_INDEX = os.path.join(TOUR_DIR, "pays_index.txt")
SPEACH_TXT = os.path.join(TOUR_DIR, "speach.txt")
BACKGROUND_DIR = os.path.join(IMAGES_DIR, "BackgroundWorldTour")
MAP_DIR = os.path.join(IMAGES_DIR, "CountryMapsWorldTour")
FANNY_DIR = os.path.join(IMAGES_DIR, "FannyWorldTour")
OUT_DIR = os.path.join(TOUR_DIR, "postcards")

CANVAS_W, CANVAS_H = 1920, 1080

BAND_HEIGHT = 300
BAND_COLOR = (255, 250, 240, 235)
TITLE_COLOR = (140, 30, 30, 255)
TEXT_COLOR = (35, 30, 25, 255)

HEADER_HEIGHT = 150
HEADER_TITLE = "FANNY PÉTANQUE WORLD TOUR"

MAP_MARGIN_X = 44
MAP_MARGIN_TOP = HEADER_HEIGHT + 24
CARD_PADDING = 10
CARD_COLOR = (255, 255, 255, 245)
SHADOW_COLOR = (0, 0, 0, 90)
CARD_GAP = 20

# Colonne de droite : la mini-carte du monde et le portrait de Fanny ont la
# MÊME largeur de carton (CORNER_CARD_WIDTH) et sont empilés l'un au-dessus
# de l'autre (carte en haut, Fanny en dessous) plutôt que placés
# indépendamment — sinon, à largeurs différentes, les deux cartons ne
# s'alignent pas et peuvent se chevaucher (retour utilisateur 2026-07-06).
# Portrait Fanny non détouré en sticker flottant : présenté comme une carte
# photo encadrée, le fond studio du portrait étant conservé à dessein (cf.
# `round_corners` dans remove_background.py : choix déjà fait par
# l'utilisateur le 2026-07-05 de garder ce fond plutôt que détourer le
# personnage).
CORNER_CARD_WIDTH = 400

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
TITLE_FONT_PATH = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
TEXT_FONT_PATH = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
HEADER_FONT_PATH = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")


def slugify(name: str) -> str:
    name = name.lower()
    repl = {"é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "î": "i",
            "ô": "o", "û": "u", "ù": "u", "ç": "c", "ï": "i", "ë": "e"}
    for a, b in repl.items():
        name = name.replace(a, b)
    name = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
    return name


def load_pays(path=PAYS_INDEX):
    pays_by_index = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            i, name = line.rstrip("\n").split("\t", 1)
            pays_by_index[int(i)] = name
    return pays_by_index


def load_speach(path=SPEACH_TXT):
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_header(canvas):
    """Bandeau titre "FANNY PÉTANQUE WORLD TOUR" en haut : dégradé sombre
    (pour rester lisible quel que soit le décor derrière) + texte blanc
    centré avec une légère ombre portée."""
    # Dégradé vertical (1px de large, étiré horizontalement : bien plus
    # rapide qu'une écriture pixel par pixel sur toute la largeur).
    grad = Image.new("L", (1, HEADER_HEIGHT))
    for y in range(HEADER_HEIGHT):
        grad.putpixel((0, y), round(150 * (1 - y / HEADER_HEIGHT)))
    grad = grad.resize((CANVAS_W, HEADER_HEIGHT))
    scrim = Image.merge("RGBA", (
        Image.new("L", (CANVAS_W, HEADER_HEIGHT), 0),
        Image.new("L", (CANVAS_W, HEADER_HEIGHT), 0),
        Image.new("L", (CANVAS_W, HEADER_HEIGHT), 0),
        grad,
    ))
    canvas.alpha_composite(scrim, (0, 0))

    draw = ImageDraw.Draw(canvas)
    header_font = ImageFont.truetype(HEADER_FONT_PATH, 46)
    text_w = draw.textlength(HEADER_TITLE, font=header_font)
    x = (CANVAS_W - text_w) / 2
    y = 42
    draw.text((x + 2, y + 2), HEADER_TITLE, font=header_font, fill=(0, 0, 0, 140))
    draw.text((x, y), HEADER_TITLE, font=header_font, fill=(255, 255, 255, 255))


def paste_card(canvas, content_img, card_x, card_y, padding=CARD_PADDING, radius=14):
    """Colle `content_img` sur un petit carton blanc arrondi avec ombre
    portée (coin supérieur-gauche du carton en (card_x, card_y)), façon
    encart de carte postale. Réutilisé pour la mini-carte du monde et le
    portrait de Fanny, pour un traitement visuel identique aux deux coins."""
    card_w = content_img.width + 2 * padding
    card_h = content_img.height + 2 * padding

    shadow = Image.new("RGBA", (card_w + 16, card_h + 16), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (8, 10, card_w + 8, card_h + 10), radius=radius, fill=SHADOW_COLOR
    )
    canvas.alpha_composite(shadow, (card_x - 8, card_y - 8))

    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card_w, card_h), radius=radius, fill=CARD_COLOR)
    card.alpha_composite(content_img, (padding, padding))
    canvas.alpha_composite(card, (card_x, card_y))
    return card_w, card_h


def build_postcard(pays, text, background_path, map_path, fanny_path):
    bg = Image.open(background_path).convert("RGB").resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    canvas = bg.convert("RGBA")

    # Bandeau de légende en bas
    band = Image.new("RGBA", (CANVAS_W, BAND_HEIGHT), BAND_COLOR)
    canvas.alpha_composite(band, (0, CANVAS_H - BAND_HEIGHT))

    draw = ImageDraw.Draw(canvas)
    pad_x = 56
    text_top = CANVAS_H - BAND_HEIGHT + 28

    title_font = ImageFont.truetype(TITLE_FONT_PATH, 54)
    draw.text((pad_x, text_top), pays.upper(), font=title_font, fill=TITLE_COLOR)

    body_font = ImageFont.truetype(TEXT_FONT_PATH, 30)
    max_text_width = CANVAS_W - 2 * pad_x - (CORNER_CARD_WIDTH + MAP_MARGIN_X)
    lines = wrap_text(draw, text, body_font, max_text_width)
    line_height = body_font.size + 10
    body_top = text_top + 70
    # Si trop de lignes pour la hauteur du bandeau, réduire la taille de police.
    max_lines = (BAND_HEIGHT - (body_top - (CANVAS_H - BAND_HEIGHT))) // line_height
    if len(lines) > max_lines:
        body_font = ImageFont.truetype(TEXT_FONT_PATH, 25)
        line_height = body_font.size + 8
        lines = wrap_text(draw, text, body_font, max_text_width)

    y = body_top
    for line in lines:
        draw.text((pad_x, y), line, font=body_font, fill=TEXT_COLOR)
        y += line_height

    # Colonne de droite : mini-carte du monde en haut, portrait de Fanny
    # juste en dessous — même largeur de carton pour les deux, donc alignés
    # dans la même colonne sans jamais se chevaucher.
    card_x = CANVAS_W - MAP_MARGIN_X - (CORNER_CARD_WIDTH + 2 * CARD_PADDING)
    next_card_y = MAP_MARGIN_TOP

    if map_path and os.path.isfile(map_path):
        map_img = Image.open(map_path).convert("RGBA")
        ratio = CORNER_CARD_WIDTH / map_img.width
        map_img = map_img.resize((CORNER_CARD_WIDTH, round(map_img.height * ratio)), Image.LANCZOS)
        _, card_h = paste_card(canvas, map_img, card_x, next_card_y)
        next_card_y += card_h + CARD_GAP

    # Portrait de Fanny en tenue typique du pays, juste sous la carte du monde.
    if fanny_path and os.path.isfile(fanny_path):
        fanny_img = Image.open(fanny_path).convert("RGBA")
        ratio = CORNER_CARD_WIDTH / fanny_img.width
        fanny_img = fanny_img.resize((CORNER_CARD_WIDTH, round(fanny_img.height * ratio)), Image.LANCZOS)
        paste_card(canvas, fanny_img, card_x, next_card_y)

    draw_header(canvas)

    return canvas.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="Regénérer même les cartes postales déjà présentes")
    parser.add_argument("--limit", type=int, default=None, help="Limiter aux N premiers pays (test)")
    parser.add_argument("--only", type=str, default=None, help="Liste d'index séparés par des virgules (ex: 1,13,112)")
    parser.add_argument("--pays-index", default=PAYS_INDEX,
                         help="Fichier index->pays utilisé pour retrouver les assets (slug) — ne pas traduire")
    parser.add_argument("--pays-names", default=None,
                         help="Fichier index->nom AFFICHÉ (titre de la carte) ; par défaut, même fichier que --pays-index")
    parser.add_argument("--speach", default=SPEACH_TXT, help="Fichier des répliques affichées (une par ligne)")
    parser.add_argument("--out-dir", default=OUT_DIR)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    pays_by_index = load_pays(args.pays_index)
    names_by_index = load_pays(args.pays_names) if args.pays_names else pays_by_index
    speach_lines = load_speach(args.speach)
    assert len(speach_lines) == len(pays_by_index), (
        f"{args.speach} a {len(speach_lines)} lignes mais {args.pays_index} en a {len(pays_by_index)}"
    )
    assert names_by_index.keys() == pays_by_index.keys(), (
        f"{args.pays_names} n'a pas les mêmes index que {args.pays_index}"
    )

    indices = sorted(pays_by_index)
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        indices = [i for i in indices if i in wanted]
    elif args.limit:
        indices = indices[: args.limit]

    done = skipped = missing_bg = 0
    for i in indices:
        pays = pays_by_index[i]  # nom français : clé des assets (slug), jamais traduit
        display_name = names_by_index[i]  # nom affiché sur la carte (français ou traduit)
        slug = slugify(pays)
        text = speach_lines[i - 1]
        out_path = os.path.join(args.out_dir, f"{i:03d}_{slug}.png")
        if os.path.isfile(out_path) and not args.force:
            skipped += 1
            continue

        background_path = os.path.join(BACKGROUND_DIR, f"{i:03d}_{slug}.jpg")
        if not os.path.isfile(background_path):
            print(f"[{i:03d}] {pays} : décor introuvable ({background_path}), ignoré")
            missing_bg += 1
            continue
        map_path = os.path.join(MAP_DIR, f"{i:03d}_{slug}.png")
        fanny_path = os.path.join(FANNY_DIR, f"{i:03d}_{slug}.png")

        postcard = build_postcard(display_name, text, background_path, map_path, fanny_path)
        postcard.save(out_path)
        done += 1
        print(f"[{i:03d}] {display_name} -> {out_path}")

    print(f"\nTerminé : {done} créée(s), {skipped} déjà présente(s) (ignorée(s)), {missing_bg} décor(s) manquant(s).")
    print(f"Dossier : {args.out_dir}")


if __name__ == "__main__":
    main()
