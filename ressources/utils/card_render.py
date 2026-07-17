# -*- coding: utf-8 -*-
"""Moteur de rendu de cartes - unique source de vérité utilisée à la fois par
les scripts de génération en ligne de commande (build_world_tour_playing_cards.py,
build_mpc_export.py, build_print_europe_export.py) et par l'éditeur web
(card_studio_server.py).

Un même appel render_card(target, trim_mm, corner_style, ...) produit un
rendu correct pour n'importe quelle combinaison cible d'impression / taille
de carte / forme de coins : les marges de fond perdu et de zone de sécurité
changent selon la cible, mais la logique de composition (portrait jamais
rogné, badges et texte toujours dans la zone sûre) est écrite une seule
fois - ça évite qu'un bug corrigé sur un export reste présent sur les
autres.

Cibles ("target") disponibles :
  - "home"/"sprite" : coins découpés dans le fichier (impression maison à la
                       découpeuse/ciseaux, ou sprite de jeu vidéo prêt à
                       charger tel quel - même rendu pour les deux).
  - "mpc"            : 63x88mm (ou autre taille) + fond perdu 1/8"+1/8",
                        coins NON découpés (MakePlayingCards s'en charge).
  - "printeurope"     : taille + fond perdu 2mm+3mm, coins NON découpés
                        (Print Europe s'en charge).

Tailles de carte ("trim_mm") : cf. CARD_SIZES pour les préréglages standards
(poker, bridge, tarot, carrée, mini, jumbo) - n'importe quel (largeur,
hauteur) en mm fonctionne.

Forme des coins ("corner_style") : "rounded" ou "square". Sur les profils
d'impression pro, la découpe réelle est toujours faite par l'imprimeur (le
fichier n'a pas de coins pré-découpés) - ce réglage y est donc surtout
indicatif (cadre décoratif assorti + rappel dans le LISEZ-MOI de bien
sélectionner l'option correspondante sur le site). Sur "home"/"sprite", ça
change réellement la forme du fichier exporté (masque alpha appliqué ou non).
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
PORTRAITS_DIR = f"{ROOT}/assets/Images/FannyWorldTour"
LOGO_PATH = f"{ROOT}/assets/Images/fanny_10x10cm.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SYMBOL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUIT_SYMBOLS = {"hearts": "♥", "diamonds": "♦", "clubs": "♣", "spades": "♠"}
SUIT_COLORS = {
    "hearts": (191, 58, 42), "diamonds": (191, 58, 42),
    "clubs": (58, 46, 32), "spades": (58, 46, 32),
}
PARCHMENT = (245, 240, 222)
INK = (58, 46, 32)

# Préréglages de taille (largeur, hauteur) en mm, format "portrait".
CARD_SIZES = {
    "poker": (63, 88),
    "bridge": (58, 89),
    "tarot": (70, 120),
    "square": (65, 65),
    "mini": (44, 63),
    "jumbo": (88, 122),
}
CORNER_STYLES = ("rounded", "square")
TARGETS = ("home", "sprite", "mpc", "printeurope")


def _mm2px(v, dpi):
    return round(v * dpi / 25.4)


def build_profile(target, trim_mm=(63, 88), corner_style="rounded"):
    if target not in TARGETS:
        raise ValueError(f"target inconnu : {target}")
    if corner_style not in CORNER_STYLES:
        raise ValueError(f"corner_style inconnu : {corner_style}")
    trim_w_mm, trim_h_mm = trim_mm

    if target in ("home", "sprite"):
        dpi = None
        px_per_mm = 9.52  # ~ résolution du deck "impression maison" d'origine (600px/63mm)
        card_w = round(trim_w_mm * px_per_mm)
        card_h = round(trim_h_mm * px_per_mm)
        short_side = min(card_w, card_h)
        safe_margin = max(10, round(short_side * 0.023))
        is_precut = True  # le fichier EST la forme finale (masque alpha si arrondi)
        corner_radius = round(short_side * 0.047) if corner_style == "rounded" else 0
    else:
        dpi = 300
        if target == "mpc":
            bleed = round(dpi * 0.125)  # 1/8" de fond perdu
            safety = bleed  # + 1/8" de marge de sécurité
            card_w = _mm2px(trim_w_mm, dpi) + 2 * bleed
            card_h = _mm2px(trim_h_mm, dpi) + 2 * bleed
            safe_margin = bleed + safety
        else:  # printeurope
            bleed_mm, safety_mm = 2, 3
            card_w = _mm2px(trim_w_mm + 2 * bleed_mm, dpi)
            card_h = _mm2px(trim_h_mm + 2 * bleed_mm, dpi)
            safe_margin = _mm2px(bleed_mm + safety_mm, dpi)
        short_side = min(card_w, card_h)
        is_precut = False  # découpe toujours faite par l'imprimeur, jamais dans le fichier
        # cadre décoratif seulement (purement cosmétique, la vraie découpe est externe)
        corner_radius = round(short_side * 0.036) if corner_style == "rounded" else 0

    badge_w = max(56, round(short_side * 0.155))
    badge_h = round(badge_w * 1.43)
    rank_font = round(badge_h * 0.335)
    symbol_font = round(badge_h * 0.303)
    header_h = max(safe_margin + round(badge_h * 0.12), round(card_h * 0.045))
    accent_h = max(4, round(card_h * 0.007))
    country_font_start = max(15, round(short_side * 0.052))
    footer_h = round(country_font_start * 2.9)
    border_width = max(5, round(short_side * 0.0125))
    joker_badge = (round(card_w * 0.34), round(card_w * 0.34 * 0.30))
    joker_font = round(joker_badge[1] * 0.5)
    back_badge = (round(card_w * 0.58), round(card_w * 0.58 * 0.66))
    back_title_font = max(14, round(back_badge[1] * 0.15))
    back_sub_font = max(10, round(back_badge[1] * 0.086))

    return dict(
        card_w=card_w, card_h=card_h, header_h=header_h, footer_h=footer_h, accent_h=accent_h,
        border_width=border_width, safe_margin=safe_margin,
        is_precut=is_precut, corner_radius=corner_radius, corner_style=corner_style,
        badge_w=badge_w, badge_h=badge_h, rank_font=rank_font, symbol_font=symbol_font,
        country_font_start=country_font_start, country_font_min=13,
        joker_badge=joker_badge, joker_font=joker_font, back_badge=back_badge,
        back_title_font=back_title_font, back_sub_font=back_sub_font, dpi=dpi,
        trim_mm=trim_mm, target=target,
    )


def portrait_path(tier, slug):
    return f"{PORTRAITS_DIR}/{tier + 1:03d}_{slug}.png"


def _rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def _contain_fit_extend(img, target_w, target_h):
    """Image entière toujours visible (jamais rognée en haut/bas comme le
    ferait un cover-fit) ; les bandes de complément prolongent la couleur de
    fond de l'image ligne par ligne / colonne par colonne pour rester
    invisibles quand le fond source est plat."""
    ratio = min(target_w / img.width, target_h / img.height)
    new_w, new_h = round(img.width * ratio), round(img.height * ratio)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h))
    x_off = (target_w - new_w) // 2
    y_off = (target_h - new_h) // 2
    canvas.paste(resized, (x_off, y_off))
    if x_off > 0:
        left_col = resized.crop((0, 0, 1, new_h)).resize((x_off, new_h))
        canvas.paste(left_col, (0, y_off))
        right_col = resized.crop((new_w - 1, 0, new_w, new_h)).resize((target_w - x_off - new_w, new_h))
        canvas.paste(right_col, (x_off + new_w, y_off))
    if y_off > 0:
        top_row = canvas.crop((0, y_off, target_w, y_off + 1)).resize((target_w, y_off))
        canvas.paste(top_row, (0, 0))
        bottom_row = canvas.crop((0, y_off + new_h - 1, target_w, y_off + new_h)).resize((target_w, target_h - y_off - new_h))
        canvas.paste(bottom_row, (0, y_off + new_h))
    return canvas


def _fit_text(draw, text, font_path, max_width, start_size, min_size=13):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(font_path, min_size)


def _draw_corner_index(canvas, p, rank_label, symbol, color):
    badge_w, badge_h = p["badge_w"], p["badge_h"]
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.rounded_rectangle([(0, 0), (badge_w - 1, badge_h - 1)], radius=round(badge_w * 0.19), fill=(255, 255, 255, 235))

    rank_font = ImageFont.truetype(FONT_BOLD, p["rank_font"])
    symbol_font = ImageFont.truetype(FONT_SYMBOL, p["symbol_font"])
    draw.text((badge_w / 2, badge_h * 0.25), rank_label, font=rank_font, fill=color, anchor="mm")
    draw.text((badge_w / 2, badge_h * 0.66), symbol, font=symbol_font, fill=color, anchor="mm")

    m = p["safe_margin"]
    canvas.alpha_composite(badge, (m, m))
    rotated = badge.rotate(180)
    canvas.alpha_composite(rotated, (p["card_w"] - m - badge_w, p["card_h"] - m - badge_h))


def render_card(target, image_path, label, rank_label, symbol, color, is_joker=False,
                 trim_mm=(63, 88), corner_style="rounded", show_label=True):
    p = build_profile(target, trim_mm, corner_style)
    card_w, card_h = p["card_w"], p["card_h"]
    canvas = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))

    art = Image.open(image_path).convert("RGB")
    art_h = card_h - p["header_h"] - p["footer_h"] - p["accent_h"]
    art = _contain_fit_extend(art, card_w, art_h)
    canvas.paste(art, (0, p["header_h"]))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, 0), (card_w, p["header_h"])], fill=PARCHMENT)
    footer_top = card_h - p["footer_h"] - p["accent_h"]
    draw.rectangle([(0, footer_top), (card_w, card_h - p["accent_h"])], fill=PARCHMENT)
    draw.rectangle([(0, card_h - p["accent_h"]), (card_w, card_h)], fill=color)

    corner_radius = p["corner_radius"]
    if p["is_precut"]:
        # version "découpe maison"/sprite : le fichier EST la forme finale,
        # donc le cadre se trace tout près du bord et on masque les coins
        # (uniquement si forme "rounded" - sinon coins carrés, pas de masque)
        bw = p["border_width"]
        border_line_y = card_h - bw // 2
        if corner_radius > 0:
            mask = _rounded_mask((card_w, card_h), corner_radius)
            rounded = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
            rounded.paste(canvas, (0, 0), mask)
            canvas = rounded
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle(
            [(bw // 2, bw // 2), (card_w - bw // 2 - 1, card_h - bw // 2 - 1)],
            radius=corner_radius, outline=color, width=bw,
        )
    else:
        # versions impression pro : le fichier déborde sur le fond perdu,
        # c'est l'imprimeur qui découpe (et arrondit les coins si demandé) -
        # le cadre décoratif reste entièrement dans la zone de sécurité
        m = p["safe_margin"]
        border_line_y = card_h - m
        draw.rounded_rectangle(
            [(m, m), (card_w - m, card_h - m)],
            radius=corner_radius, outline=color, width=p["border_width"],
        )

    if show_label and label:
        label_font = _fit_text(
            draw, label, FONT_BOLD,
            card_w - 2 * (p["safe_margin"] + max(30, p["border_width"] * 4)),
            p["country_font_start"], p["country_font_min"],
        )
        text_clearance = round(p["country_font_start"] * 1.15)
        label_text_y = border_line_y - text_clearance
        draw.text((card_w / 2, label_text_y), label, font=label_font, fill=INK, anchor="mm")

    if is_joker:
        badge_w, badge_h = p["joker_badge"]
        badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.rounded_rectangle([(0, 0), (badge_w - 1, badge_h - 1)], radius=round(badge_h * 0.23), fill=(255, 255, 255, 235))
        font = ImageFont.truetype(FONT_BOLD, p["joker_font"])
        bd.text((badge_w / 2, badge_h / 2), "JOKER", font=font, fill=color, anchor="mm")
        m = p["safe_margin"]
        canvas.alpha_composite(badge, (card_w // 2 - badge_w // 2, m + 8))
        canvas.alpha_composite(badge, (card_w // 2 - badge_w // 2, footer_top - 8 - badge_h))
    else:
        _draw_corner_index(canvas, p, rank_label, symbol, color)

    return canvas if (p["is_precut"] and corner_radius > 0) else canvas.convert("RGB")


def render_back(target, subtitle=None, trim_mm=(63, 88), corner_style="rounded", logo_path=None):
    p = build_profile(target, trim_mm, corner_style)
    card_w, card_h = p["card_w"], p["card_h"]
    canvas = Image.new("RGBA", (card_w, card_h), (191, 58, 42, 255))
    draw = ImageDraw.Draw(canvas)

    step = round(card_w * 0.067)
    for y in range(-card_h, card_h * 2, step):
        draw.line([(0, y), (card_w, y + card_w)], fill=(163, 45, 32, 255), width=max(4, step // 7))
        draw.line([(card_w, y), (0, y + card_w)], fill=(163, 45, 32, 255), width=max(4, step // 7))

    m = p["safe_margin"] if not p["is_precut"] else round(min(card_w, card_h) * 0.06)
    draw.rounded_rectangle([(m, m), (card_w - m, card_h - m)], radius=p["corner_radius"], outline=PARCHMENT, width=max(5, p["border_width"] - 2))

    badge_w, badge_h = p["back_badge"]
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.ellipse([(0, 0), (badge_w - 1, badge_h - 1)], fill=(*PARCHMENT, 255), outline=(255, 255, 255, 255), width=5)

    logo_size = round(badge_h * 0.46)
    logo = Image.open(logo_path or LOGO_PATH).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
    badge.alpha_composite(logo, (badge_w // 2 - logo_size // 2, round(badge_h * 0.11)))

    font_title = ImageFont.truetype(FONT_BOLD, p["back_title_font"])
    font_sub_text = subtitle or "WORLD TOUR"
    font_sub = _fit_text(bd, font_sub_text, FONT_BOLD, badge_w - 40, p["back_sub_font"])
    bd.text((badge_w / 2, badge_h * 0.635), "FANNY", font=font_title, fill=(191, 58, 42), anchor="mm")
    bd.text((badge_w / 2, badge_h * 0.755), font_sub_text, font=font_sub, fill=INK, anchor="mm")
    canvas.alpha_composite(badge, (card_w // 2 - badge_w // 2, card_h // 2 - badge_h // 2))

    if p["is_precut"] and p["corner_radius"] > 0:
        mask = _rounded_mask((card_w, card_h), p["corner_radius"])
        rounded = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        rounded.paste(canvas, (0, 0), mask)
        canvas = rounded
    if p["is_precut"]:
        draw = ImageDraw.Draw(canvas)
        bw = p["border_width"]
        draw.rounded_rectangle(
            [(bw // 2, bw // 2), (card_w - bw // 2 - 1, card_h - bw // 2 - 1)],
            radius=p["corner_radius"], outline=PARCHMENT, width=bw,
        )
        return canvas
    return canvas.convert("RGB")
