# -*- coding: utf-8 -*-
"""Anime un portrait Fanny World Tour avec une illusion de "balancement"
(sway + rebond + léger glissement horizontal) via ffmpeg pur - aucune
dépendance nouvelle (pas de Node/Remotion).

Limite assumée : un seul portrait plat par pays (pas de vue de dos/profil,
pas de membres séparés en calques), donc PAS un vrai cycle de marche
(les jambes ne s'alternent pas) - juste un mouvement d'ensemble qui donne
une impression de vie ("elle se balance, prête à bouger"), validé
visuellement sur le portrait France le 2026-07-15 (cf. mémoire projet).

Technique : pad (fond uni prolongé, couleur échantillonnée au coin du
portrait) -> rotate (balancement d'ensemble, angle sinusoïdal) -> crop
(fenêtre de sortie qui se déplace en x/y de façon sinusoïdale = rebond
vertical + dérive horizontale). Trois filtres ffmpeg, un seul passage,
pas de calques séparés.

Usage :
    python3 ressources/utils/build_portrait_sway_animation.py <pays_ou_tier> [duree_s]
    python3 ressources/utils/build_portrait_sway_animation.py france
    python3 ressources/utils/build_portrait_sway_animation.py 12 6

Sortie : ressources/portrait_animations/<tier>_<slug>_sway.mp4
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
PORTRAITS_DIR = f"{ROOT}/assets/Images/FannyWorldTour"
OUT_DIR = f"{ROOT}/ressources/portrait_animations"

FPS = 30

# Paramètres validés visuellement sur le portrait France (cf. mémoire projet) :
ROT_AMPLITUDE_RAD = 0.035   # ~2° de balancement d'ensemble
ROT_FREQ_HZ = 1.0           # un cycle balancement gauche-droite par seconde
BOB_AMPLITUDE_PX = 22        # rebond vertical
BOB_FREQ_HZ = 2.0            # deux fois la fréquence du balancement (un rebond par appui)
BOB_PHASE = "PI/2"
WALK_AMPLITUDE_PX = 50       # dérive horizontale (pas un vrai déplacement, juste une dérive)
WALK_FREQ_HZ = 0.5

MARGIN_X = 115  # place pour la rotation + la dérive horizontale
MARGIN_Y = 90   # place pour la rotation + le rebond vertical
CROP_MARGIN_X = 70
CROP_MARGIN_Y = 50


def resolve_tier(arg):
    if arg.isdigit():
        return int(arg)
    needle = arg.strip().lower()
    for tier, (pays, slug, _texte) in enumerate(WORLD_TOUR_COUNTRIES):
        if needle in (pays.lower(), slug.lower()):
            return tier
    raise SystemExit(f"Pays introuvable : {arg!r}")


def sample_bg_color(image_path):
    img = Image.open(image_path).convert("RGB")
    r, g, b = img.getpixel((2, 2))
    return f"0x{r:02X}{g:02X}{b:02X}"


def build_sway_animation(tier, duration_s=4.0, out_path=None):
    pays, slug, _texte = WORLD_TOUR_COUNTRIES[tier]
    src = f"{PORTRAITS_DIR}/{tier + 1:03d}_{slug}.png"
    if not os.path.isfile(src):
        raise SystemExit(f"Portrait introuvable : {src}")

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = out_path or f"{OUT_DIR}/{tier + 1:03d}_{slug}_sway.mp4"
    bg = sample_bg_color(src)

    img = Image.open(src)
    padded_w = img.width + 2 * MARGIN_X
    padded_h = img.height + 2 * MARGIN_Y
    crop_w = img.width + 2 * CROP_MARGIN_X
    crop_h = img.height + 2 * CROP_MARGIN_Y

    filter_complex = (
        f"[0:v]format=rgba,"
        f"pad=w={padded_w}:h={padded_h}:x={MARGIN_X}:y={MARGIN_Y}:color={bg}[padded];"
        f"[padded]rotate=a='{ROT_AMPLITUDE_RAD}*sin(2*PI*t*{ROT_FREQ_HZ})':ow=iw:oh=ih:c={bg}[rotated];"
        f"[rotated]crop=w={crop_w}:h={crop_h}:"
        f"x='(in_w-out_w)/2+{WALK_AMPLITUDE_PX}*sin(2*PI*t*{WALK_FREQ_HZ})':"
        f"y='(in_h-out_h)/2+{BOB_AMPLITUDE_PX}*sin(2*PI*t*{BOB_FREQ_HZ}+{BOB_PHASE})'[final]"
    )

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", src, "-t", str(duration_s),
        "-filter_complex", filter_complex, "-map", "[final]",
        "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", out_path,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print(result.stdout[-3000:])
        raise SystemExit(1)
    print(f"{out_path}  <-  {pays} ({duration_s}s, {FPS}fps)")
    return out_path


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    tier = resolve_tier(sys.argv[1])
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
    build_sway_animation(tier, duration)


if __name__ == "__main__":
    main()
