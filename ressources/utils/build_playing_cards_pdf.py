# -*- coding: utf-8 -*-
"""Met en page les cartes déjà générées par build_world_tour_playing_cards.py
(ressources/playing_cards/deck_1, deck_2) en PDF imprimables A4, prêts à
découper : format carte à jouer standard (63x88mm), 9 cartes par planche
(grille 3x3), repères de coupe, recto/verso alternés pour impression
recto-verso (le verso est mis en miroir colonne par colonne pour rester
aligné avec le recto en cas de retournement bord long).

Usage : python3 ressources/utils/build_playing_cards_pdf.py
Sortie : ressources/playing_cards/deck_1.pdf, ressources/playing_cards/deck_2.pdf
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
CARDS_DIR = f"{ROOT}/ressources/playing_cards"

DPI = 300
PAGE_MM = (210, 297)  # A4
CARD_MM = (63, 88)  # format carte à jouer poker standard
GAP_MM = 3
COLS, ROWS = 3, 3
PER_PAGE = COLS * ROWS

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def mm(v):
    return round(v * DPI / 25.4)


PAGE_W, PAGE_H = mm(PAGE_MM[0]), mm(PAGE_MM[1])
CARD_W, CARD_H = mm(CARD_MM[0]), mm(CARD_MM[1])
GAP = mm(GAP_MM)
GRID_W = COLS * CARD_W + (COLS - 1) * GAP
GRID_H = ROWS * CARD_H + (ROWS - 1) * GAP
MARGIN_X = (PAGE_W - GRID_W) // 2
MARGIN_Y = (PAGE_H - GRID_H) // 2
MARK_LEN = mm(4)
MARK_GAP = mm(1.5)


def deck_card_files(deck_dir):
    """Ordre d'impression : A..K des 4 couleurs puis tous les jokers
    (triés par nom, donc joker-black[.png/-2/-3] puis joker-red...)."""
    files = []
    for suit in SUITS:
        for rank in RANKS:
            files.append(f"{deck_dir}/{rank}-{suit}.png")
    jokers = sorted(
        f for f in os.listdir(deck_dir)
        if f.startswith("joker-")
    )
    files += [f"{deck_dir}/{f}" for f in jokers]
    return files


def draw_crop_marks(draw, x, y, w, h):
    corners = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
    for cx, cy in corners:
        h_sign = -1 if cx == x else 1
        v_sign = -1 if cy == y else 1
        draw.line([(cx + h_sign * MARK_GAP, cy), (cx + h_sign * (MARK_GAP + MARK_LEN), cy)],
                   fill=(150, 150, 150), width=2)
        draw.line([(cx, cy + v_sign * MARK_GAP), (cx, cy + v_sign * (MARK_GAP + MARK_LEN))],
                   fill=(150, 150, 150), width=2)


def make_page(images, mirror_columns):
    page = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    for idx in range(PER_PAGE):
        col = idx % COLS
        row = idx // COLS
        if mirror_columns:
            col = COLS - 1 - col
        x = MARGIN_X + col * (CARD_W + GAP)
        y = MARGIN_Y + row * (CARD_H + GAP)
        if idx < len(images) and images[idx] is not None:
            im = images[idx].resize((CARD_W, CARD_H), Image.LANCZOS)
            page.paste(im, (x, y))
            draw_crop_marks(draw, x, y, CARD_W, CARD_H)
    return page


def fit_text(draw, text, font_path, max_width, start_size, min_size=8):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(font_path, min_size)


def make_cover_page(deck_label, nb_cards):
    page = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    text_font = ImageFont.truetype(FONT_REG, mm(5))
    cx = PAGE_W // 2
    y = mm(60)
    title_font = fit_text(draw, "FANNY PÉTANQUE WORLD TOUR", FONT_BOLD, PAGE_W - mm(20), mm(12))
    draw.text((cx, y), "FANNY PÉTANQUE WORLD TOUR", font=title_font, fill=(58, 46, 32), anchor="mm")
    y += mm(16)
    draw.text((cx, y), deck_label, font=ImageFont.truetype(FONT_BOLD, mm(8)), fill=(191, 58, 42), anchor="mm")
    y += mm(20)
    lines = [
        f"{nb_cards} cartes (recto + verso), format 63 x 88 mm.",
        "Papier conseillé : 250-300 g/m², impression recto-verso.",
        "Réglage imprimante : retournement sur le bord long (\"flip on long edge\"),",
        "qualité 300 dpi, sans mise à l'échelle (\"taille réelle\" / 100%).",
        "Repères gris aux coins de chaque carte = traits de coupe.",
    ]
    for line in lines:
        draw.text((cx, y), line, font=text_font, fill=(58, 46, 32), anchor="mm")
        y += mm(8)
    return page


def build_deck_pdf(deck_dir, deck_label, out_path):
    files = deck_card_files(deck_dir)
    images = [Image.open(f).convert("RGB") for f in files]
    back = Image.open(f"{deck_dir}/back.png").convert("RGB")

    pages = [make_cover_page(deck_label, len(images))]
    for start in range(0, len(images), PER_PAGE):
        chunk = images[start:start + PER_PAGE]
        pages.append(make_page(chunk, mirror_columns=False))
        back_chunk = [back] * len(chunk)
        pages.append(make_page(back_chunk, mirror_columns=True))

    pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=DPI)
    print(f"{out_path}  <-  {len(images)} cartes, {len(pages)} pages")


def main():
    build_deck_pdf(f"{CARDS_DIR}/deck_1", "Volume 1 — 54 cartes", f"{CARDS_DIR}/deck_1.pdf")
    build_deck_pdf(f"{CARDS_DIR}/deck_2", "Volume 2 — 58 cartes", f"{CARDS_DIR}/deck_2.pdf")


if __name__ == "__main__":
    main()
