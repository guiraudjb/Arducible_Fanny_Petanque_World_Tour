#!/usr/bin/env python3
"""Génère les 54 sprites de cartes (+ dos de carte) à partir des illustrations
du dossier outputs/Pin_up_Rétro_Défaut_.

Usage: python3 tools/generate_card_sprites.py
Sortie: assets/cards/{RANK}-{suit}.png, joker-red.png, joker-black.png, back.png
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "outputs" / "Pin_up_Rétro_Défaut_"
OUT_DIR = ROOT / "assets" / "cards"

CARD_W, CARD_H = 600, 840  # ratio 5:7
CORNER_RADIUS = 28
BORDER_WIDTH = 8

SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUIT_SYMBOLS = {"hearts": "♥", "diamonds": "♦", "clubs": "♣", "spades": "♠"}
SUIT_COLORS = {"hearts": (196, 30, 40), "diamonds": (196, 30, 40), "clubs": (25, 25, 25), "spades": (25, 25, 25)}

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SYMBOL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def cover_fit(img, target_w, target_h):
    """Redimensionne l'image en 'cover' (remplit tout le cadre, rogne le surplus)."""
    src_ratio = img.width / img.height
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


# Dossiers exclus car contenant des poses nues ou trop suggestives (nudité
# implicite via transparence), repérées lors d'une relecture visuelle
# manuelle de chaque sprite généré. Le nom des dossiers n'est pas un
# indicateur fiable de leur contenu (ex: "Intégral_debout_de_face" est
# habillé alors que les autres poses "Intégral_*" ne le sont pas) : toute la
# série "Intégral_*" est donc écartée par prudence plutôt qu'au cas par cas.
EXCLUDED_FOLDER_PREFIXES = ("Intégral_",)
EXCLUDED_FOLDER_NAMES = {"T_shirt_mouillé"}


def pick_source_images(count):
    folders = sorted(
        p for p in SOURCE_DIR.iterdir()
        if p.is_dir()
        and not p.name.startswith(EXCLUDED_FOLDER_PREFIXES)
        and p.name not in EXCLUDED_FOLDER_NAMES
    )
    stride_indices = [round(i * len(folders) / count) for i in range(count)]
    stride_indices = sorted(set(stride_indices))
    # comble les collisions dues à l'arrondi en piochant les index manquants
    i = 0
    while len(stride_indices) < count:
        if i not in stride_indices:
            stride_indices.append(i)
        i += 1
    stride_indices = sorted(stride_indices)[:count]

    images = []
    for idx in stride_indices:
        folder = folders[idx]
        # Les rendus "xy_*" sont les poses pin-up canoniques ; on ignore les
        # fichiers annexes (ex: "batch_*", "k2_*", assets hors-thème) qui
        # traînent parfois dans le même dossier.
        pngs = sorted(folder.glob("xy_*.png")) or sorted(folder.glob("*.png"))
        images.append(pngs[0])
    return images


def draw_corner_index(canvas, rank_label, symbol, color, top_left):
    badge_w, badge_h = 92, 132
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.rounded_rectangle([(0, 0), (badge_w - 1, badge_h - 1)], radius=18, fill=(255, 255, 255, 235))

    rank_font = ImageFont.truetype(FONT_BOLD, 44)
    symbol_font = ImageFont.truetype(FONT_SYMBOL, 40)

    draw.text((badge_w / 2, 34), rank_label, font=rank_font, fill=color, anchor="mm")
    draw.text((badge_w / 2, 92), symbol, font=symbol_font, fill=color, anchor="mm")

    canvas.alpha_composite(badge, top_left)
    rotated = badge.rotate(180)
    canvas.alpha_composite(
        rotated,
        (CARD_W - top_left[0] - badge_w, CARD_H - top_left[1] - badge_h),
    )


def build_card(image_path, rank_label, symbol, color, is_joker=False):
    canvas = Image.new("RGBA", (CARD_W, CARD_H), (255, 255, 255, 255))

    art = Image.open(image_path).convert("RGB")
    art = cover_fit(art, CARD_W, CARD_H - 40)
    canvas.paste(art, (0, 40))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, 0), (CARD_W, 40)], fill=(250, 247, 240, 255))
    draw.rectangle([(0, CARD_H - 4), (CARD_W, CARD_H)], fill=color)

    mask = rounded_mask((CARD_W, CARD_H), CORNER_RADIUS)
    rounded = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    rounded.paste(canvas, (0, 0), mask)
    canvas = rounded

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        [(BORDER_WIDTH // 2, BORDER_WIDTH // 2), (CARD_W - BORDER_WIDTH // 2 - 1, CARD_H - BORDER_WIDTH // 2 - 1)],
        radius=CORNER_RADIUS,
        outline=color,
        width=BORDER_WIDTH,
    )

    if is_joker:
        badge_w, badge_h = 200, 60
        badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.rounded_rectangle([(0, 0), (badge_w - 1, badge_h - 1)], radius=14, fill=(255, 255, 255, 235))
        font = ImageFont.truetype(FONT_BOLD, 30)
        bd.text((badge_w / 2, badge_h / 2), "JOKER", font=font, fill=color, anchor="mm")
        canvas.alpha_composite(badge, (CARD_W // 2 - badge_w // 2, 14))
        canvas.alpha_composite(badge.rotate(180), (CARD_W // 2 - badge_w // 2, CARD_H - 14 - badge_h))
    else:
        draw_corner_index(canvas, rank_label, symbol, color, (14, 14))

    return canvas


def build_back():
    canvas = Image.new("RGBA", (CARD_W, CARD_H), (178, 34, 52, 255))
    draw = ImageDraw.Draw(canvas)

    step = 40
    for y in range(-CARD_H, CARD_H * 2, step):
        draw.line([(0, y), (CARD_W, y + CARD_W)], fill=(150, 20, 36, 255), width=6)
        draw.line([(CARD_W, y), (0, y + CARD_W)], fill=(150, 20, 36, 255), width=6)

    inner_margin = 36
    draw.rounded_rectangle(
        [(inner_margin, inner_margin), (CARD_W - inner_margin, CARD_H - inner_margin)],
        radius=20,
        outline=(250, 247, 240, 255),
        width=6,
    )

    badge_w, badge_h = 340, 200
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.ellipse([(0, 0), (badge_w - 1, badge_h - 1)], fill=(250, 247, 240, 255), outline=(178, 34, 52, 255), width=5)
    font_title = ImageFont.truetype(FONT_BOLD, 40)
    font_sub = ImageFont.truetype(FONT_BOLD, 22)
    bd.text((badge_w / 2, badge_h / 2 - 22), "PIN-UP", font=font_title, fill=(178, 34, 52), anchor="mm")
    bd.text((badge_w / 2, badge_h / 2 + 24), "RÉTRO", font=font_sub, fill=(90, 20, 28), anchor="mm")
    canvas.alpha_composite(badge, (CARD_W // 2 - badge_w // 2, CARD_H // 2 - badge_h // 2))

    mask = rounded_mask((CARD_W, CARD_H), CORNER_RADIUS)
    rounded = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    rounded.paste(canvas, (0, 0), mask)
    draw = ImageDraw.Draw(rounded)
    draw.rounded_rectangle(
        [(BORDER_WIDTH // 2, BORDER_WIDTH // 2), (CARD_W - BORDER_WIDTH // 2 - 1, CARD_H - BORDER_WIDTH // 2 - 1)],
        radius=CORNER_RADIUS,
        outline=(250, 247, 240, 255),
        width=BORDER_WIDTH,
    )
    return rounded


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cards = [(rank, suit) for suit in SUITS for rank in RANKS]  # 52
    images = pick_source_images(len(cards) + 2)  # + 2 jokers

    for (rank, suit), image_path in zip(cards, images):
        color = SUIT_COLORS[suit]
        symbol = SUIT_SYMBOLS[suit]
        card_img = build_card(image_path, rank, symbol, color)
        out_path = OUT_DIR / f"{rank}-{suit}.png"
        card_img.save(out_path)
        print(f"{out_path.relative_to(ROOT)}  <-  {image_path.relative_to(ROOT)}")

    joker_red_img = build_card(images[-2], "JOKER", "", (196, 30, 40), is_joker=True)
    joker_red_img.save(OUT_DIR / "joker-red.png")
    print(f"assets/cards/joker-red.png  <-  {images[-2].relative_to(ROOT)}")

    joker_black_img = build_card(images[-1], "JOKER", "", (25, 25, 25), is_joker=True)
    joker_black_img.save(OUT_DIR / "joker-black.png")
    print(f"assets/cards/joker-black.png  <-  {images[-1].relative_to(ROOT)}")

    back_img = build_back()
    back_img.save(OUT_DIR / "back.png")
    print("assets/cards/back.png  <-  (généré, motif géométrique)")


if __name__ == "__main__":
    main()
