# -*- coding: utf-8 -*-
"""Assemble les mp4 verticaux (9:16, TikTok) par pays à partir des frames
+ manifest.json produits par render_social_video_frames.py :

  intro (7s, hook : écran d'accueil + logo Fanny tournant + "Aujourd'hui :
  {pays} !" + "Teste tes connaissances sur ce pays et sa pétanque !")
  -> 5x(question : asking -> feedback -> explication de Fanny)
  -> récap ("5/5 bonnes réponses")
  -> outro (3.5s, prochain pays + CTA like/abonnement)

puis conversion 16:9 -> 9:16 : contenu net centré, fond = portrait de
Fanny en tenue traditionnelle du pays (validé face à un fond flouté/zoomé,
préféré pour son identité visuelle propre à la série).

Audio : narration TTS (gTTS) de chaque question/choix/explication, plus
l'hymne national du pays en fond continu (18% de volume, limiteur anti-
écrêtage). Concaténation finale via le FILTRE `concat` (pas le demuxer en
copie de flux), qui décode et ré-encode tout en un seul flux continu -
indispensable : des segments AAC indépendants juxtaposés en copie de flux
produisent des grésillements/coupures à chaque raccord.

Usage (n'importe quel python3 avec ffmpeg dans le PATH - pas besoin du
venv du jeu ici, ce script ne fait que piloter ffmpeg) :
    python3 ressources/utils/build_social_videos.py [tier1 tier2 ...]

Sans argument : construit la vidéo de TOUS les pays présents dans le
manifest (généré par render_social_video_frames.py au préalable).
"""
import json
import os
import subprocess
import sys

os.chdir("/home/adm1/Fanny_P-tanque_World_Tour")
sys.path.insert(0, "/home/adm1/Fanny_P-tanque_World_Tour")
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402

BASE = "/home/adm1/Fanny_P-tanque_World_Tour/ressources/social_videos"
WORK = f"{BASE}/_work"
SEG_DIR = f"{WORK}/segments"
os.makedirs(SEG_DIR, exist_ok=True)

SILENCE_FEEDBACK = f"{WORK}/silence_feedback.mp3"
SILENCE_PAUSE = f"{WORK}/silence_pause.mp3"
SILENCE_RECAP = f"{WORK}/silence_recap.mp3"
INTRO_JINGLE = "/home/adm1/Fanny_P-tanque_World_Tour/assets/Sounds/intro.wav"
FANNY_DISC = f"{WORK}/fanny_disc.png"
ANTHEMS_DIR = "/home/adm1/Fanny_P-tanque_World_Tour/assets/Sounds/AnthemsWorldTour"
PORTRAITS_DIR = "/home/adm1/Fanny_P-tanque_World_Tour/assets/Images/FannyWorldTour"

INTRO_DURATION = 7.0
OUTRO_DURATION = 3.5
ANTHEM_VOLUME = 0.18  # cf. retour utilisateur : 0.5 couvrait trop la voix

# Position du logo tournant : même ancrage que fanny.draw() dans
# main_quizz.py (centre à LARGEUR_ECRAN - HAUTEUR_ECRAN*0.12, HAUTEUR_ECRAN*0.12)
# pour 1920x1080, taille du disque = HAUTEUR_ECRAN*0.22 (238px).
DISC_SIZE = 238
DISC_X = round(1920 - 1080 * 0.12 - DISC_SIZE / 2)
DISC_Y = round(1080 * 0.12 - DISC_SIZE / 2)
ROTATE_EXPR = "t*(PI/3)"  # 60°/s, même vitesse perçue que le jeu (2°/frame à 30fps)


def run(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("CMD FAILED:", " ".join(cmd))
        print(result.stdout[-3000:])
        raise SystemExit(1)


def ensure_helper_assets():
    """Génère les silences et le logo Fanny redimensionné s'ils n'existent
    pas déjà - rend ce script autonome (pas besoin de ré-exécuter les
    commandes ad-hoc utilisées lors du prototypage)."""
    if not os.path.isfile(SILENCE_PAUSE):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", "0.4", "-q:a", "9", SILENCE_PAUSE])
    if not os.path.isfile(SILENCE_FEEDBACK):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", "1.5", "-q:a", "9", SILENCE_FEEDBACK])
    if not os.path.isfile(SILENCE_RECAP):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", "2.5", "-q:a", "9", SILENCE_RECAP])
    if not os.path.isfile(FANNY_DISC):
        from PIL import Image
        img = Image.open("assets/Images/fanny_10x10cm.png")
        img.resize((DISC_SIZE, DISC_SIZE), Image.LANCZOS).save(FANNY_DISC)


_silence_cache = {}


def safe_audio(path, fallback_duration):
    """Renvoie `path` tel quel s'il existe et fait une taille plausible
    (>1KB - un mp3 gTTS valide n'est jamais plus petit), sinon un silence
    de `fallback_duration` secondes généré à la volée (mis en cache par
    durée). Nécessaire car la génération audio (gTTS) peut être
    incomplète au moment de construire les vidéos (ex : quota API
    temporairement épuisé - voir mémoire feedback_gtts_rate_limits) ; le
    jeu lui-même dégrade déjà silencieusement dans ce cas
    (`get_quiz_audio()` dans main_quizz.py), donc la vidéo doit pouvoir
    faire pareil plutôt que de planter en pleine génération d'un pays."""
    if os.path.isfile(path) and os.path.getsize(path) >= 1024:
        return path
    if fallback_duration not in _silence_cache:
        silence_path = f"{WORK}/_silence_fallback_{fallback_duration}s.mp3"
        if not os.path.isfile(silence_path):
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                 "-t", str(fallback_duration), "-q:a", "9", silence_path])
        _silence_cache[fallback_duration] = silence_path
    print(f"  (audio manquant, remplacé par {fallback_duration}s de silence : {path})")
    return _silence_cache[fallback_duration]


def make_segment(image, audio, out_path):
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", image, "-i", audio,
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-shortest", "-r", "24",
        out_path,
    ])


def make_hook_segment(background_png, duration, out_path):
    """Fond statique + logo Fanny tournant (filtre `rotate` ffmpeg, pas de
    frames pré-rendues) + jingle du jeu (intro.wav) tronqué à `duration`.
    intro.wav pointe déjà à -0.7 dB en amont (proche du plafond) : sans
    limiteur, le réencodage AAC dépasse 0 dBFS et grésille. `level=0` est
    indispensable - alimiter a `level=true` par défaut (compensation de
    gain automatique) qui republie le signal près de 0 dBFS quel que soit
    `limit` sinon."""
    filter_complex = (
        f"[1:v]rotate={ROTATE_EXPR}:c=none:ow={DISC_SIZE}:oh={DISC_SIZE}[discrot];"
        f"[0:v][discrot]overlay={DISC_X}:{DISC_Y}[vout];"
        "[2:a]alimiter=limit=0.65:attack=5:release=50:level=0[aout]"
    )
    run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", background_png,
        "-loop", "1", "-i", FANNY_DISC,
        "-i", INTRO_JINGLE,
        "-filter_complex", filter_complex, "-map", "[vout]", "-map", "[aout]",
        "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-r", "24",
        out_path,
    ])


def concat_audio(parts, out_path):
    inputs = []
    filter_inputs = []
    for i, p in enumerate(parts):
        inputs += ["-i", p]
        filter_inputs.append(f"[{i}:a]")
    filter_complex = "".join(filter_inputs) + f"concat=n={len(parts)}:v=0:a=1[aout]"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", filter_complex, "-map", "[aout]",
         "-ar", "44100", "-ac", "1", out_path])


def concat_segments(segment_paths, output_path):
    """Concatène tous les segments en UN SEUL flux ré-encodé (filtre
    `concat`, jamais `-f concat -c copy`) : le demuxer en copie de flux
    juxtapose des paquets AAC encodés indépendamment par segment, dont les
    échantillons d'amorçage ne se recalculent pas proprement à la
    jonction - grésillements et coupures de son à chaque raccord."""
    inputs = []
    concat_inputs = []
    for i, p in enumerate(segment_paths):
        inputs += ["-i", p]
        concat_inputs.append(f"[{i}:v:0][{i}:a:0]")
    filter_complex = "".join(concat_inputs) + f"concat=n={len(segment_paths)}:v=1:a=1[vout][aout]"
    run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        output_path,
    ])


def mix_anthem(video_path, tier, output_path):
    """Mixe l'hymne national du pays en fond sonore (ANTHEM_VOLUME, en
    boucle sur toute la durée de la vidéo) sous la narration existante -
    narration gardée à son niveau normal (amix sans normalize, sinon ffmpeg
    diviserait aussi son volume par le nombre de pistes). `level=0` sur le
    limiteur final pour la même raison que dans make_hook_segment."""
    _pays, slug, _text = WORLD_TOUR_COUNTRIES[tier]
    anthem_path = f"{ANTHEMS_DIR}/{tier + 1:03d}_{slug}.mp3"
    if not os.path.isfile(anthem_path):
        run(["ffmpeg", "-y", "-i", video_path, "-c", "copy", output_path])
        return
    filter_complex = (
        f"[1:a]volume={ANTHEM_VOLUME},aloop=loop=-1:size=2e9[anthem];"
        "[0:a][anthem]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mixed];"
        "[mixed]alimiter=limit=0.65:attack=5:release=50:level=0[aout]"
    )
    run([
        "ffmpeg", "-y", "-i", video_path, "-i", anthem_path,
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        output_path,
    ])


def to_vertical_fanny_bg(input_path, portrait_path, output_path):
    """16:9 -> 9:16 : contenu net centré, fond = portrait de Fanny en
    tenue traditionnelle du pays (recadré pour remplir le canevas
    vertical). Préféré par l'utilisateur à un fond flouté/zoomé du
    contenu lui-même (identité visuelle propre à la série)."""
    filter_complex = (
        "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[vout]"
    )
    run([
        "ffmpeg", "-y", "-i", input_path, "-loop", "1", "-i", portrait_path,
        "-filter_complex", filter_complex, "-map", "[vout]", "-map", "0:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
        output_path,
    ])


def build_one(tier, data):
    pays = data["pays"]
    segment_paths = []

    intro_seg = f"{SEG_DIR}/{tier:03d}_intro.mp4"
    make_hook_segment(data["intro_bg"], INTRO_DURATION, intro_seg)
    segment_paths.append(intro_seg)

    for qi, q in enumerate(data["questions"]):
        asking_audio = [safe_audio(a, 3.0) for a in q["asking_audio"]]
        parts = [asking_audio[0]]
        for a in asking_audio[1:]:
            parts.append(SILENCE_PAUSE)
            parts.append(a)
        combined_audio = f"{SEG_DIR}/{tier:03d}_q{qi}_asking_audio.mp3"
        concat_audio(parts, combined_audio)
        asking_seg = f"{SEG_DIR}/{tier:03d}_q{qi}_asking.mp4"
        make_segment(q["asking_image"], combined_audio, asking_seg)
        segment_paths.append(asking_seg)

        feedback_seg = f"{SEG_DIR}/{tier:03d}_q{qi}_feedback.mp4"
        make_segment(q["feedback_image"], SILENCE_FEEDBACK, feedback_seg)
        segment_paths.append(feedback_seg)

        explanation_seg = f"{SEG_DIR}/{tier:03d}_q{qi}_explanation.mp4"
        make_segment(q["explanation_image"], safe_audio(q["explanation_audio"], 5.0), explanation_seg)
        segment_paths.append(explanation_seg)

    recap_seg = f"{SEG_DIR}/{tier:03d}_recap.mp4"
    make_segment(data["recap_image"], SILENCE_RECAP, recap_seg)
    segment_paths.append(recap_seg)

    outro_seg = f"{SEG_DIR}/{tier:03d}_outro.mp4"
    make_hook_segment(data["outro_bg"], OUTRO_DURATION, outro_seg)
    segment_paths.append(outro_seg)

    _pays, slug, _text = WORLD_TOUR_COUNTRIES[tier]
    landscape_path = f"{SEG_DIR}/{tier:03d}_{slug}_16x9.mp4"
    concat_segments(segment_paths, landscape_path)

    with_anthem_path = f"{SEG_DIR}/{tier:03d}_{slug}_16x9_anthem.mp4"
    mix_anthem(landscape_path, tier, with_anthem_path)

    final_path = f"{BASE}/{tier:03d}_{slug}.mp4"
    portrait_path = f"{PORTRAITS_DIR}/{tier + 1:03d}_{slug}.png"
    to_vertical_fanny_bg(with_anthem_path, portrait_path, final_path)
    return final_path


def main():
    ensure_helper_assets()
    with open(f"{WORK}/manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)

    tiers_to_build = [int(a) for a in sys.argv[1:]] or sorted(int(k) for k in manifest.keys())

    for tier in tiers_to_build:
        data = manifest[str(tier)]
        final_path = build_one(tier, data)
        print(f"[{tier + 1}/112] {data['pays']} -> {final_path}", flush=True)

    print("Terminé :", len(tiers_to_build), "pays")


if __name__ == "__main__":
    main()
