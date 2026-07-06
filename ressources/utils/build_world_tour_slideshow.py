#!/usr/bin/env python3
"""Génère un diaporama vidéo (mp4) à partir des 112 cartes postales
("fanny wold tour/postcards/{i:03d}_{slug}.png", cf.
build_world_tour_postcards.py) sur la musique "Arducible vibe.mp3".

La vidéo s'ouvre sur "page de garde.png" (écran-titre) et se termine sur
"écran fin.png", chacune affichée --bookend-duration secondes ; entre les
deux défilent les 112 cartes postales à durée égale.

La durée totale de la vidéo = --loops x la durée EXACTE du morceau (jamais
tronqué ; par défaut --loops 2, soit deux fois la chanson, à la demande de
l'utilisateur du 2026-07-06 qui trouvait un défilement à 1x trop rapide).
Le temps pris par les deux écrans de titre/fin est déduit de cette durée
totale AVANT de répartir le reste également entre les 112 cartes postales,
pour que l'audio (le morceau répété `loops` fois via `-stream_loop`) ait
toujours très exactement la même longueur que la vidéo — condition
nécessaire pour qu'une lecture en boucle (loop) reparte de la musique dès
le premier instant de la vidéo, sans coupure audible.

Usage :
    python3 build_world_tour_slideshow.py [--fps 30] [--loops 2] [--bookend-duration 4]
        [--postcards-dir PATH] [--music PATH] [--out PATH]
"""
import argparse
import os
import subprocess

from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TOUR_DIR = os.path.join(PROJECT_ROOT, "fanny wold tour")
POSTCARDS_DIR = os.path.join(TOUR_DIR, "postcards")
TITLE_IMAGE = os.path.join(TOUR_DIR, "page de garde.png")
END_IMAGE = os.path.join(TOUR_DIR, "écran fin.png")
DEFAULT_MUSIC = os.path.join(
    TOUR_DIR, "Fanny Wold Tour Game", "assets", "Sounds", "Arducible vibe.mp3"
)
DEFAULT_OUT = os.path.join(TOUR_DIR, "fanny_world_tour_slideshow.mp4")
CONCAT_LIST_PATH = os.path.join(TOUR_DIR, "_slideshow_concat.txt")
TITLE_RESIZED_PATH = os.path.join(TOUR_DIR, "_slideshow_title_1080.png")
END_RESIZED_PATH = os.path.join(TOUR_DIR, "_slideshow_end_1080.png")
CANVAS_W, CANVAS_H = 1920, 1080


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--loops", type=int, default=2, help="Nombre de fois où la chanson est jouée d'affilée")
    parser.add_argument("--bookend-duration", type=float, default=4.0,
                         help="Durée (s) de l'écran-titre et de l'écran de fin")
    parser.add_argument("--postcards-dir", default=POSTCARDS_DIR,
                         help="Dossier des cartes postales (permet de générer la version d'une autre langue)")
    parser.add_argument("--music", default=DEFAULT_MUSIC)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    files = sorted(f for f in os.listdir(args.postcards_dir) if f.endswith(".png"))
    if not files:
        raise SystemExit(f"Aucune carte postale trouvée dans {args.postcards_dir}")
    for path in (TITLE_IMAGE, END_IMAGE):
        if not os.path.isfile(path):
            raise SystemExit(f"Image introuvable : {path}")

    # "page de garde.png"/"écran fin.png" ne sont pas exactement à la même
    # résolution que les cartes postales (1920x1088 au lieu de 1920x1080) :
    # un changement de résolution entre la 1ère et la 2e image d'un concat
    # ffmpeg fait perdre la durée de la toute première entrée (bug constaté
    # le 2026-07-06, indépendant du filtre -vf scale appliqué en aval) —
    # on uniformise donc la taille de ces deux images AVANT le concat.
    Image.open(TITLE_IMAGE).convert("RGB").resize((CANVAS_W, CANVAS_H), Image.LANCZOS).save(TITLE_RESIZED_PATH)
    Image.open(END_IMAGE).convert("RGB").resize((CANVAS_W, CANVAS_H), Image.LANCZOS).save(END_RESIZED_PATH)

    song_duration = probe_duration(args.music)
    duration = song_duration * args.loops
    postcards_duration = duration - 2 * args.bookend_duration
    if postcards_duration <= 0:
        raise SystemExit("bookend-duration trop long : plus de temps disponible pour les cartes postales")
    per_image = postcards_duration / len(files)
    print(f"{len(files)} cartes postales, musique = {song_duration:.3f}s x{args.loops} = {duration:.3f}s "
          f"(dont {args.bookend_duration:.1f}s x2 pour titre/fin) -> {per_image:.6f}s par carte")

    with open(CONCAT_LIST_PATH, "w", encoding="utf-8") as f:
        f.write(f"file '{TITLE_RESIZED_PATH}'\n")
        f.write(f"duration {args.bookend_duration:.6f}\n")
        for name in files:
            path = os.path.join(args.postcards_dir, name).replace("'", "'\\''")
            f.write(f"file '{path}'\n")
            f.write(f"duration {per_image:.6f}\n")
        f.write(f"file '{END_RESIZED_PATH}'\n")
        f.write(f"duration {args.bookend_duration:.6f}\n")
        # Quirk du concat demuxer ffmpeg : la durée du dernier fichier est
        # ignorée sauf si on le répète une dernière fois sans "duration".
        f.write(f"file '{END_RESIZED_PATH}'\n")

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", CONCAT_LIST_PATH,
                "-stream_loop", str(args.loops - 1), "-i", args.music,
                "-vf", f"fps={args.fps},format=yuv420p",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k",
                "-t", f"{duration:.6f}",
                "-movflags", "+faststart",
                args.out,
            ],
            check=True,
        )
    finally:
        os.remove(CONCAT_LIST_PATH)
        os.remove(TITLE_RESIZED_PATH)
        os.remove(END_RESIZED_PATH)

    print(f"\nTerminé : {args.out}")


if __name__ == "__main__":
    main()
