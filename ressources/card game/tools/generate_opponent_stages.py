#!/usr/bin/env python3
"""Prépare les illustrations de l'adversaire du Strip Poker (6 tenues, de la
plus couvrante à la moins couvrante) à partir d'images déjà existantes dans
outputs/Pin_up_Rétro_Défaut_. Ne génère aucune nouvelle image : recadre/encadre
simplement les fichiers choisis dans un cadre visuel cohérent avec le reste du
projet. La tenue finale (lingerie) est la plus dévêtue utilisée : le jeu ne va
jamais au-delà de ce qui existe déjà dans outputs/.

Usage: python3 tools/generate_opponent_stages.py
Sortie: assets/opponent/stage-0.png .. stage-5.png
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "outputs" / "Pin_up_Rétro_Défaut_"
OUT_DIR = ROOT / "assets" / "opponent"

CANVAS_W, CANVAS_H = 560, 840
CORNER_RADIUS = 24
BORDER_WIDTH = 6
BORDER_COLOR = (178, 34, 52, 255)

# Progression de la tenue la plus couvrante (0) à la moins couvrante (5).
STAGES = [
    ("Entretien_Job_interview_", "xy_00076_pose-Debout_classique_outfit-Entretien_Job_interview__seed0.png"),
    ("Robe_d_été_fleurie", "xy_00142_pose-Debout_classique_outfit-Robe_d_été_fleurie_seed0.png"),
    ("Débardeur_Short_en_jean", "xy_00141_pose-Debout_classique_outfit-Débardeur_Short_en_jean_seed0.png"),
    ("Short_en_jean_Haut_bikini", "xy_00014_outfit-Short_en_jean_Haut_bikini_pose-unique_seed0.png"),
    ("Bikini_Rétro_à_pois", "xy_00001_outfit-Bikini_Rétro_à_pois_pose-Debout_classique_seed0.png"),
    ("Lingerie_dentelle_noire", "xy_00001_outfit-Lingerie_dentelle_noire_pose-Envoie_un_baiser_seed419965184.png"),
]


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def contain_fit(img, target_w, target_h):
    """Redimensionne en 'contain' (image entière visible, marges blanches)."""
    ratio = min(target_w / img.width, target_h / img.height)
    new_w, new_h = int(img.width * ratio), int(img.height * ratio)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    canvas.paste(resized, ((target_w - new_w) // 2, (target_h - new_h) // 2))
    return canvas


def build_frame(image_path):
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
    art = Image.open(image_path).convert("RGB")
    art = contain_fit(art, CANVAS_W, CANVAS_H)
    canvas.paste(art, (0, 0))

    mask = rounded_mask((CANVAS_W, CANVAS_H), CORNER_RADIUS)
    rounded = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    rounded.paste(canvas, (0, 0), mask)

    draw = ImageDraw.Draw(rounded)
    draw.rounded_rectangle(
        [(BORDER_WIDTH // 2, BORDER_WIDTH // 2), (CANVAS_W - BORDER_WIDTH // 2 - 1, CANVAS_H - BORDER_WIDTH // 2 - 1)],
        radius=CORNER_RADIUS,
        outline=BORDER_COLOR,
        width=BORDER_WIDTH,
    )
    return rounded


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for i, (folder, filename) in enumerate(STAGES):
        src = SOURCE_DIR / folder / filename
        framed = build_frame(src)
        out_path = OUT_DIR / f"stage-{i}.png"
        framed.save(out_path)
        print(f"{out_path.relative_to(ROOT)}  <-  {src.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
