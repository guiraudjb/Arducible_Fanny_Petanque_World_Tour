# -*- coding: utf-8 -*-
"""Génère un livret PDF (1 page par pays + couverture + page de fin) à
partir du contenu du quizz (Scripts/quiz_questions.py), pour un usage
imprimable/partageable en dehors du jeu (demande utilisateur du
2026-07-13).

Chaque page pays est désormais recto-verso (demande utilisateur du
2026-07-13) :
- RECTO (inchangé) :
  - le fond du pays (assets/Images/BackgroundWorldTour/{n}_{slug}.jpg),
  - le portrait de Fanny en tenue traditionnelle du pays
    (assets/Images/FannyWorldTour/{n}_{slug}.png), placé alternativement
    à droite/à gauche d'une page à l'autre pour une mise en page
    dynamique,
  - les 5 questions/réponses/explications du quizz de ce pays, dans une
    grille de cartes sur un panneau translucide.
- VERSO : une ou deux "cartes postales" (photo réelle + cadre blanc +
  légende), une par question monument/spécialité de ce pays (Q2 toujours,
  + Q5 quand ce n'est pas une question athlète pétanque), posées à des
  angles aléatoires sur un fond flouté du pays, comme éparpillées sur une
  table. Les photos viennent de Wikimedia Commons (dépôt qui n'héberge que
  des fichiers sous licence libre) via
  ressources/utils/fetch_postcard_images.py - à lancer AVANT ce script
  pour peupler ressources/quizz_pdf/_postcards_cache/. Une question sans
  photo trouvée n'a simplement pas de carte postale (jamais d'image
  inventée).

La page de garde est l'écran d'accueil du jeu
(assets/Images/TitleScreenWorldTour.jpg) et la dernière page est l'écran
de fin de partie (assets/Images/EndingScreenWorldTour.jpg), tous deux
utilisés tels quels (déjà finalisés visuellement) avec juste un bandeau
de légende ajouté.

Ne nécessite aucune dépendance PDF externe : Pillow seule sait écrire un
PDF multi-page (Image.save(..., save_all=True, append_images=[...])).

Lancer avec le venv du jeu (Pillow y est installé) :
    /home/adm1/pythonvenv/bin/python3 ressources/utils/build_quiz_pdf.py
Pour ne générer qu'un sous-ensemble de pays (test rapide), passer leurs
tiers en argument :
    /home/adm1/pythonvenv/bin/python3 ressources/utils/build_quiz_pdf.py 0 3 54
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, _REPO_ROOT)

from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from Scripts.quiz_questions import QUIZ_QUESTIONS  # noqa: E402

sys.path.insert(0, _THIS_DIR)
from quiz_country_facts import COUNTRY_FACTS  # noqa: E402
from quiz_monuments_facts import MONUMENTS  # noqa: E402
from quiz_second_monuments_facts import SECOND_MONUMENTS  # noqa: E402
from quiz_petanque_athletes import PETANQUE_ATHLETES  # noqa: E402

POSTCARDS_DIR = os.path.join(_REPO_ROOT, "ressources", "quizz_pdf", "_postcards_cache")
POSTCARDS_MANIFEST = os.path.join(POSTCARDS_DIR, "manifest.json")

IMAGES_DIR = os.path.join(_REPO_ROOT, "assets", "Images")
BG_DIR = os.path.join(IMAGES_DIR, "BackgroundWorldTour")
FANNY_DIR = os.path.join(IMAGES_DIR, "FannyWorldTour")
TITLE_SCREEN = os.path.join(IMAGES_DIR, "TitleScreenWorldTour.jpg")
ENDING_SCREEN = os.path.join(IMAGES_DIR, "EndingScreenWorldTour.jpg")

OUT_DIR = os.path.join(_REPO_ROOT, "ressources", "quizz_pdf")
OUT_PDF = os.path.join(OUT_DIR, "Fanny_Petanque_World_Tour_Quizz.pdf")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
FONT_SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_SANS_ITALIC = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")

W, H = 1920, 1080
DPI = 144.0
MARGIN = 60

CREAM = (246, 241, 224)
INK = (35, 32, 28)
NAVY = (28, 40, 74)
GRAY = (95, 90, 82)
GOLD = (176, 128, 34)
WHITE = (252, 250, 244)

NUM_COLORS = [
    (168, 40, 40),   # rouge
    (36, 104, 72),   # vert
    (32, 52, 104),   # bleu marine
    (168, 118, 26),  # ocre
    (110, 44, 96),   # prune
]

N = len(WORLD_TOUR_COUNTRIES)
assert len(QUIZ_QUESTIONS) == N

_font_cache = {}


def font(path, size):
    key = (path, size)
    f = _font_cache.get(key)
    if f is None:
        f = ImageFont.truetype(path, size)
        _font_cache[key] = f
    return f


def text_w(draw, text, f):
    return draw.textlength(text, font=f)


def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if text_w(draw, candidate, f) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_block(draw, text, font_path, start_size, max_width, max_height, min_size, line_spacing=1.25):
    """Cherche la plus grande taille de police (entre min_size et
    start_size) telle que le texte, une fois découpé en lignes de largeur
    <= max_width, tienne dans max_height. Si même min_size ne suffit pas,
    tronque la dernière ligne avec une ellipse plutôt que de déborder."""
    size = start_size
    while size >= min_size:
        f = font(font_path, size)
        lines = wrap_text(draw, text, f, max_width)
        line_h = f.size * line_spacing
        if len(lines) * line_h <= max_height:
            return f, lines, line_h
        size -= 1
    f = font(font_path, min_size)
    lines = wrap_text(draw, text, f, max_width)
    line_h = f.size * line_spacing
    max_lines = max(1, int(max_height // line_h))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while text_w(draw, last + "…", f) > max_width and len(last) > 1:
            last = last[:-1]
        lines[-1] = last + "…"
    return f, lines, line_h


def draw_lines(draw, lines, f, x, y, line_h, fill, center=False, box_width=None):
    for line in lines:
        lx = x
        if center and box_width:
            lx = x + (box_width - text_w(draw, line, f)) / 2
        draw.text((lx, y), line, font=f, fill=fill)
        y += line_h
    return y


def rounded_panel(size, fill, radius=28):
    panel = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return panel


def add_shadow(base, panel_img, pos, blur=18, opacity=110):
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    alpha = panel_img.split()[-1].point(lambda a: opacity if a > 0 else 0)
    shadow_shape = Image.new("RGBA", panel_img.size, (0, 0, 0, 255))
    shadow_shape.putalpha(alpha)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(shadow_shape, (pos[0] + 8, pos[1] + 10), shadow_shape)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, layer)


def top_gradient(size, top_alpha=190, height_ratio=0.30):
    w, h = size
    grad_h = int(h * height_ratio)
    grad = Image.new("L", (1, grad_h), 0)
    for y in range(grad_h):
        a = int(top_alpha * (1 - y / grad_h) ** 1.4)
        grad.putpixel((0, y), a)
    grad = grad.resize((w, grad_h))
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    black = Image.new("RGBA", (w, grad_h), (5, 8, 14, 255))
    black.putalpha(grad)
    layer.paste(black, (0, 0), black)
    return layer


def pill(draw, xy, text, f, fg, bg, pad_x=16, pad_y=8):
    x, y = xy
    tw = text_w(draw, text, f)
    th = f.size
    box = [x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y]
    draw.rounded_rectangle(box, radius=(th + 2 * pad_y) / 2, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), text, font=f, fill=fg)
    return box


def build_country_page(tier):
    pays, slug, _text = WORLD_TOUR_COUNTRIES[tier]
    _capital, continent, _lang, _currency = COUNTRY_FACTS[tier]
    questions = QUIZ_QUESTIONS[tier]

    bg_path = os.path.join(BG_DIR, f"{tier + 1:03d}_{slug}.jpg")
    page = Image.open(bg_path).convert("RGBA").resize((W, H))

    # bandeau haut (lisibilité du titre sur un fond photo variable)
    page = Image.alpha_composite(page, top_gradient((W, H)))
    draw = ImageDraw.Draw(page)

    # portrait de Fanny, en alternance gauche/droite pour la dynamique -
    # jamais complètement collé au bord de la page (FANNY_EDGE_MARGIN)
    fanny_path = os.path.join(FANNY_DIR, f"{tier + 1:03d}_{slug}.png")
    fanny = Image.open(fanny_path).convert("RGBA")
    fh = int(H * 0.94)
    fw = int(fh * fanny.width / fanny.height)
    fanny = fanny.resize((fw, fh), Image.LANCZOS)
    side_right = (tier % 2 == 0)
    FANNY_EDGE_MARGIN = 36
    fx = W - fw - FANNY_EDGE_MARGIN if side_right else FANNY_EDGE_MARGIN
    fy = H - fh - FANNY_EDGE_MARGIN
    page.paste(fanny, (fx, fy), fanny)
    draw = ImageDraw.Draw(page)

    # panneau de questions ET bandeau de titre, du côté opposé au portrait
    # de Fanny (si Fanny est à gauche, tout le texte passe à droite)
    panel_w = int(W * 0.535)
    panel_x = MARGIN if side_right else W - MARGIN - panel_w
    header_x = panel_x

    f_pill = font(FONT_SANS_BOLD, 22)
    pill(draw, (header_x, 40), f"PAYS {tier + 1:03d} / {N}  ·  {continent.upper()}",
         f_pill, WHITE, (*NAVY, 210))

    title_txt = pays.upper()
    max_title_w = panel_w
    title_size = 72
    f_title = font(FONT_SERIF_BOLD, title_size)
    while text_w(draw, title_txt, f_title) > max_title_w and title_size > 40:
        title_size -= 2
        f_title = font(FONT_SERIF_BOLD, title_size)
    draw.text((header_x + 2, 90), title_txt, font=f_title, fill=(0, 0, 0, 140))
    draw.text((header_x, 86), title_txt, font=f_title, fill=WHITE)
    title_bottom = draw.textbbox((header_x, 86), title_txt, font=f_title)[3]

    f_sub = font(FONT_SANS, 24)
    sub_y = title_bottom + 26
    sub_txt = "Fanny Pétanque World Tour — Quizz culture générale & pétanque"
    draw.text((header_x + 1, sub_y + 2), sub_txt, font=f_sub, fill=(0, 0, 0, 170))
    draw.text((header_x, sub_y), sub_txt, font=f_sub, fill=WHITE)

    # panneau de questions, du côté opposé au portrait de Fanny
    panel_top = int(sub_y + 60)
    panel_bottom = H - 40
    panel_h = panel_bottom - panel_top
    panel = rounded_panel((panel_w, panel_h), (*CREAM, 235), radius=26)
    page = add_shadow(page, panel, (panel_x, panel_top))
    page.paste(panel, (panel_x, panel_top), panel)
    draw = ImageDraw.Draw(page)

    # grille 2 colonnes x 3 lignes (5 questions utilisées)
    pad = 26
    cols, rows = 2, 3
    cell_w = (panel_w - pad * (cols + 1)) / cols
    cell_h = (panel_h - pad * (rows + 1)) / rows

    for i, (question, choices, correct_index, explanation) in enumerate(questions):
        col = i % cols
        row = i // cols
        cx = panel_x + pad + col * (cell_w + pad)
        cy = panel_top + pad + row * (cell_h + pad)
        color = NUM_COLORS[i % len(NUM_COLORS)]

        badge_d = 38
        draw.ellipse([cx, cy, cx + badge_d, cy + badge_d], fill=color)
        f_num = font(FONT_SANS_BOLD, 22)
        num_txt = str(i + 1)
        ntw = text_w(draw, num_txt, f_num)
        draw.text((cx + badge_d / 2 - ntw / 2, cy + badge_d / 2 - 13), num_txt, font=f_num, fill=WHITE)

        text_x = cx + badge_d + 14
        text_max_w = cell_w - badge_d - 14
        y = cy

        qf, qlines, qlh = fit_block(draw, question, FONT_SANS_BOLD, 21, text_max_w, 3 * 27, 14)
        y_q = draw_lines(draw, qlines, qf, text_x, y, qlh, INK)
        y = max(y_q, cy + badge_d + 8)

        answer = choices[correct_index]
        af, alines, alh = fit_block(draw, answer, FONT_SANS_BOLD, 20, cell_w, 2 * 28, 14)
        y = draw_lines(draw, alines, af, cx, y + 6, alh, color)

        remaining_h = (cy + cell_h) - y - 2
        if remaining_h > 12:
            ef, elines, elh = fit_block(draw, explanation, FONT_SANS_ITALIC, 17, cell_w, remaining_h, 12)
            draw_lines(draw, elines, ef, cx, y + 6, elh, GRAY)

    # pied de page discret
    f_foot = font(FONT_SANS, 16)
    foot = "Un jeu Arducible — arducible.fr"
    ftw = text_w(draw, foot, f_foot)
    draw.text((W - MARGIN - ftw, H - 30), foot, font=f_foot, fill=(255, 255, 255, 160))

    return page.convert("RGB")


def load_postcards_manifest():
    if not os.path.exists(POSTCARDS_MANIFEST):
        return {}
    with open(POSTCARDS_MANIFEST, encoding="utf-8") as f:
        return json.load(f)


POSTCARDS_MANIFEST_DATA = load_postcards_manifest()


# Le Danemark (tier 7, Q2, la Petite Sirène) n'a AUCUNE photo librement
# réutilisable montrant la statue elle-même : le Danemark n'a pas de
# liberté de panorama, et la statue (1913) reste protégée par le droit
# d'auteur danois jusqu'en 2029 (70 ans après la mort du sculpteur Edvard
# Eriksen, 1959) - Commons ne peut légalement héberger qu'une version où la
# statue est masquée par une silhouette blanche (vérifié le 2026-07-13 :
# plusieurs tentatives de trouver une photo directe alternative ont toutes
# échoué ou étaient elles-mêmes des violations de droit d'auteur déjà
# supprimées de Commons). On garde donc cette version, mais avec une
# légende qui explique pourquoi plutôt que de laisser croire à un bug.
POSTCARD_LEGAL_NOTES = {
    (7, "q2"): "Silhouette imposée par le droit d'auteur danois (statue protégée jusqu'en 2029, pas de liberté de panorama au Danemark)",
}


def postcard_jobs_for(tier):
    """Les questions monument/spécialité de ce pays (Q2 toujours, + Q5 si
    ce n'est pas la question athlète pétanque), avec leur photo si trouvée
    (jamais d'image inventée pour les autres)."""
    jobs = []
    for slot, facts in (("q2", MONUMENTS), ("q5", SECOND_MONUMENTS)):
        if slot == "q5" and tier in PETANQUE_ATHLETES:
            continue
        name, description = facts[tier]
        entry = POSTCARDS_MANIFEST_DATA.get(f"{tier}_{slot}")
        photo_path = os.path.join(POSTCARDS_DIR, f"{tier}_{slot}.jpg")
        if entry and entry.get("status") == "ok" and os.path.exists(photo_path):
            jobs.append({
                "name": name, "description": description,
                "photo_path": photo_path,
                "credit": entry.get("artist") or "Wikimedia Commons",
                "legal_note": POSTCARD_LEGAL_NOTES.get((tier, slot)),
            })
    return jobs


def sentence_case(name):
    """Majuscule sur la toute première lettre seulement - contrairement à
    str.capitalize(), qui mettrait aussi le reste en minuscules et
    détruirait les majuscules des noms propres (ex: "Neuschwanstein")."""
    return name[:1].upper() + name[1:] if name else name


def cover_crop(im, target_ratio):
    w, h = im.size
    src_ratio = w / h
    if src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, h))
    else:
        new_h = int(w / target_ratio)
        y0 = (h - new_h) // 2
        im = im.crop((0, y0, w, y0 + new_h))
    return im


POSTCARD_MIN_RATIO = 0.35  # portrait le plus étiré toléré (tours, statues, hautes façades)
POSTCARD_MAX_RATIO = 1.6  # paysage le plus étiré toléré (panoramas)


def build_postcard(photo_path, caption, credit, card_w=620, legal_note=None, max_card_h=900):
    """La carte épouse le ratio NATUREL de la photo (borné à des valeurs
    encore "carte postale", ni trop en lame de rasoir ni trop plate) au
    lieu d'imposer un format 3:2 fixe à toutes les photos - un format fixe
    tronquait sévèrement les monuments hauts et étroits (tours, façades)
    photographiés en portrait (repéré via un retour utilisateur : Big Ben,
    tour Eiffel, Manneken-Pis, Sagrada Família... tous rognés en haut et en
    bas par un crop 3:2 forcé sur une photo bien plus haute que large)."""
    border = 24
    caption_h = 92 if not legal_note else 112

    src = Image.open(photo_path).convert("RGB")
    src_ratio = src.width / src.height
    target_ratio = max(POSTCARD_MIN_RATIO, min(POSTCARD_MAX_RATIO, src_ratio))

    photo_w = card_w - 2 * border
    photo_h = photo_w / target_ratio
    if photo_h + border + caption_h > max_card_h:
        photo_h = max_card_h - border - caption_h
        photo_w = photo_h * target_ratio
    photo_w, photo_h = int(photo_w), int(photo_h)

    card_w_total = photo_w + 2 * border
    card_h_total = photo_h + border + caption_h

    card = Image.new("RGBA", (card_w_total, card_h_total), (252, 250, 246, 255))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, card_w_total - 1, card_h_total - 1], outline=(210, 204, 190, 255), width=2)

    photo = cover_crop(src, photo_w / photo_h)
    photo = photo.resize((photo_w, photo_h), Image.LANCZOS)
    card.paste(photo, (border, border))
    d.rectangle([border, border, border + photo_w, border + photo_h], outline=(230, 226, 216, 255), width=1)

    f_cap, cap_lines, cap_lh = fit_block(d, caption, FONT_SERIF_BOLD, 24, photo_w, 60, 15, line_spacing=1.15)
    cap_y = border + photo_h + 10
    draw_lines(d, cap_lines, f_cap, border, cap_y, cap_lh, (50, 44, 36), center=True, box_width=photo_w)

    f_credit = font(FONT_SANS_ITALIC, 13)
    if legal_note:
        # note légale de confiance (écrite à la main, pas une métadonnée
        # brute) - peut dépasser une ligne, pas de filtre anti-texte-brut.
        nf, nlines, nlh = fit_block(d, legal_note, FONT_SANS_ITALIC, 13, photo_w, 40, 11, line_spacing=1.2)
        draw_lines(d, nlines, nf, border, card_h_total - 20 - (len(nlines) - 1) * nlh, nlh,
                   (150, 144, 132, 255), center=True, box_width=photo_w)
        return card

    credit = " ".join((credit or "").split())
    credit = re.sub(r"^photo\s*:?\s*", "", credit, flags=re.IGNORECASE).strip()
    # les métadonnées "Artist" de Commons sont parfois des blocs structurés
    # (crédit du photographe + crédit d'un sculpteur/auteur d'origine via
    # un template Creator, guillemets, parenthèses...) plutôt qu'un simple
    # nom - dans ce cas on préfère un crédit générique sûr à un texte brut
    # illisible sur la carte postale.
    messy = len(credit) > 32 or any(c in credit for c in "«»()[]{}:")
    credit_txt = f"Photo : {credit}" if credit and not messy else "Photo : Wikimedia Commons"
    if text_w(d, credit_txt, f_credit) > photo_w:
        credit_txt = "Photo : Wikimedia Commons"
    ctw = text_w(d, credit_txt, f_credit)
    d.text((border + (photo_w - ctw) / 2, card_h_total - 24), credit_txt, font=f_credit, fill=(150, 144, 132, 255))

    return card


def paste_rotated_with_shadow(page, card, center, angle):
    rotated = card.rotate(angle, expand=True, resample=Image.BICUBIC)

    shadow = Image.new("RGBA", page.size, (0, 0, 0, 0))
    shadow_shape = Image.new("RGBA", rotated.size, (0, 0, 0, 0))
    alpha = rotated.split()[-1].point(lambda a: 130 if a > 0 else 0)
    black = Image.new("RGBA", rotated.size, (10, 8, 6, 255))
    black.putalpha(alpha)
    sx = center[0] - rotated.width // 2 + 10
    sy = center[1] - rotated.height // 2 + 14
    shadow.paste(black, (sx, sy), black)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    page = Image.alpha_composite(page, shadow)

    x = center[0] - rotated.width // 2
    y = center[1] - rotated.height // 2
    page.paste(rotated, (x, y), rotated)
    return page


def card_rotation(tier, slot):
    seed = (tier * 37 + (0 if slot == "q2" else 17)) % 17
    angle = seed - 8
    if -1 <= angle <= 1:
        angle = 6 if slot == "q2" else -6
    return angle


def build_verso_page(tier):
    pays, slug, _text = WORLD_TOUR_COUNTRIES[tier]
    bg_path = os.path.join(BG_DIR, f"{tier + 1:03d}_{slug}.jpg")
    bg = Image.open(bg_path).convert("RGB").resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(22))
    dark = Image.new("RGB", (W, H), (20, 16, 14))
    page = Image.blend(bg, dark, 0.45).convert("RGBA")
    draw = ImageDraw.Draw(page)

    f_pill = font(FONT_SANS_BOLD, 22)
    pill(draw, (MARGIN, 40), f"PAYS {tier + 1:03d} / {N}  ·  SOUVENIRS DE VOYAGE",
         f_pill, WHITE, (*NAVY, 210))

    f_title = font(FONT_SERIF_BOLD, 52)
    title_txt = f"Cartes postales — {pays}"
    draw.text((MARGIN + 2, 104), title_txt, font=f_title, fill=(0, 0, 0, 140))
    draw.text((MARGIN, 100), title_txt, font=f_title, fill=WHITE)

    jobs = postcard_jobs_for(tier)

    if not jobs:
        f_sub = font(FONT_SANS_ITALIC, 26)
        msg = "Aucune photo librement réutilisable trouvée pour ce pays."
        mw = text_w(draw, msg, f_sub)
        draw.text(((W - mw) / 2, H / 2 - 20), msg, font=f_sub, fill=(230, 226, 216, 230))
        return page.convert("RGB")

    if len(jobs) == 1:
        card = build_postcard(jobs[0]["photo_path"], sentence_case(jobs[0]["name"]), jobs[0]["credit"],
                               card_w=760, legal_note=jobs[0].get("legal_note"), max_card_h=760)
        page = paste_rotated_with_shadow(page, card, (W // 2, H // 2 + 40), card_rotation(tier, "q2"))
    else:
        positions = [(int(W * 0.32), H // 2 + 30, "q2"), (int(W * 0.70), H // 2 + 60, "q5")]
        for job, (cx, cy, slot) in zip(jobs, positions):
            card = build_postcard(job["photo_path"], sentence_case(job["name"]), job["credit"],
                                   card_w=600, legal_note=job.get("legal_note"), max_card_h=680)
            page = paste_rotated_with_shadow(page, card, (cx, cy), card_rotation(tier, slot))

    draw = ImageDraw.Draw(page)
    f_foot = font(FONT_SANS, 16)
    foot = "Un jeu Arducible — arducible.fr"
    ftw = text_w(draw, foot, f_foot)
    draw.text((W - MARGIN - ftw, H - 30), foot, font=f_foot, fill=(255, 255, 255, 160))

    return page.convert("RGB")


def build_cover():
    page = Image.open(TITLE_SCREEN).convert("RGBA").resize((W, H))
    draw = ImageDraw.Draw(page)
    f_badge = font(FONT_SANS_BOLD, 30)
    text = f"QUIZZ  ·  {N} PAYS  ·  {N * 5} QUESTIONS"
    tw = text_w(draw, text, f_badge)
    box_w, box_h = tw + 64, 66
    x, y = W - MARGIN - box_w, H - MARGIN - box_h
    draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=box_h / 2, fill=(*NAVY, 235))
    draw.text((x + 32, y + 18), text, font=f_badge, fill=WHITE)
    return page.convert("RGB")


def build_ending():
    page = Image.open(ENDING_SCREEN).convert("RGBA").resize((W, H))
    draw = ImageDraw.Draw(page)

    f_title = font(FONT_SERIF_BOLD, 52)
    f_sub = font(FONT_SANS, 26)
    title = "Merci d'avoir voyagé avec Fanny !"
    sub = "112 pays, 560 questions de culture générale et de pétanque — à rejouer sans limite."

    x = MARGIN
    y = H - 190
    tw = text_w(draw, title, f_title)
    sw = text_w(draw, sub, f_sub)
    box_w = max(tw, sw) + 64
    box = [x - 20, y - 24, x - 20 + box_w, H - 40]
    draw.rounded_rectangle(box, radius=22, fill=(20, 16, 12, 165))
    draw.text((x, y), title, font=f_title, fill=WHITE)
    draw.text((x, y + 66), sub, font=f_sub, fill=(235, 230, 220, 235))
    return page.convert("RGB")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tiers = [int(a) for a in sys.argv[1:]] or list(range(N))

    pages = []
    if tiers == list(range(N)):
        pages.append(build_cover())
    for tier in tiers:
        pays = WORLD_TOUR_COUNTRIES[tier][0]
        pages.append(build_country_page(tier))
        pages.append(build_verso_page(tier))
        n_cards = len(postcard_jobs_for(tier))
        print(f"[{tier + 1}/{N}] page générée : {pays} (recto + verso, {n_cards} carte(s) postale(s))", flush=True)
    if tiers == list(range(N)):
        pages.append(build_ending())

    out_path = OUT_PDF if tiers == list(range(N)) else os.path.join(OUT_DIR, "preview.pdf")
    first, rest = pages[0], pages[1:]
    first.save(out_path, save_all=True, append_images=rest, resolution=DPI)
    print("OK, written", out_path, "-", len(pages), "pages")


if __name__ == "__main__":
    main()
