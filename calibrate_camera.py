#!/usr/bin/env python3
"""Calibration de la caméra / zone de tir pour Fanny World Tour et Round the
Clock. Réglages enregistrés dans camera_calibration.json (pas config.ini) :
un profil par INDEX de caméra, pour ne pas perdre le calibrage d'une caméra
en en recalibrant une autre - voir Scripts/camera_calibration.py.

Ouvre deux fenêtres OpenCV :
- "Camera complete" : l'image brute de la caméra (miroir), avec un
  rectangle indiquant la zone de tir actuellement configurée, et le bouton
  cliquable SAUVEGARDER en haut à gauche (vert = modifications non
  sauvegardées, gris = déjà à jour).
- "Zone de tir (vue du jeu)" : exactement ce que le jeu analyse - la zone
  recadrée, avec le squelette MediaPipe superposé et l'état "ZONE OK" /
  "HORS ZONE" (même logique que Scripts/opencvcam.py::Cam.update, indices
  de landmarks 27-32 = pieds/chevilles).

Réglages ajustables en direct via les curseurs : index caméra (change de
caméra recharge automatiquement SON profil déjà sauvegardé, s'il existe),
résolution de capture (réglage manuel pixel par pixel, ou "Preset
resolution" - menu déroulant des résolutions les plus courantes, dont la
caméra détectée est automatiquement sondée pour ne proposer que celles
qu'elle supporte réellement), taille de la zone de tir (%), décalage de la
zone (%, si la caméra n'est pas parfaitement centrée sur la zone marquée au
sol), cadence d'analyse MediaPipe.

Sauvegarde : clic sur le bouton SAUVEGARDER (fenêtre "Camera complete"), ou
touche 's'.

Autres touches :
  r : réinitialise les curseurs au profil sauvegardé de la caméra courante
  p : ressonde les résolutions supportées par la caméra courante
  q / Échap : quitte (sans sauvegarder si ni le bouton ni 's' n'ont été
              utilisés après une modification)

Usage :
  python3 calibrate_camera.py [--calibration camera_calibration.json]
"""
import argparse
import os
import sys
import time

import cv2
import mediapipe as mp

from Scripts.camera_calibration import DEFAULTS as CAM_DEFAULTS, \
    load_camera_settings, save_camera_settings

# Résolutions webcam les plus courantes, du plus bas au plus haut - proposées
# dans le menu déroulant "Preset résolution", après vérification de celles
# réellement supportées par la caméra détectée (cf. probe_resolutions).
COMMON_RESOLUTIONS = [
    (160, 120), (320, 240), (424, 240), (640, 480), (800, 600),
    (1024, 768), (1280, 720), (1280, 960), (1600, 900), (1920, 1080),
]

FULL_WINDOW = "Camera complete"
ZONE_WINDOW = "Zone de tir (vue du jeu)"

# Bouton "Sauvegarder" cliquable à la souris, dessiné dans le coin
# supérieur gauche de la fenêtre FULL_WINDOW (OpenCV HighGUI n'a pas de
# vrai widget bouton en dehors du backend Qt - un rectangle cliquable via
# setMouseCallback est la méthode portable standard).
SAVE_BUTTON_RECT = (10, 10, 190, 50)  # x1, y1, x2, y2


def point_in_rect(x, y, rect):
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def load_config(camera_index, path):
    values = load_camera_settings(camera_index, path=path)
    values["CameraIndex"] = camera_index
    return values


def save_config(camera_index, values, path):
    persisted = {k: v for k, v in values.items() if k in CAM_DEFAULTS}
    save_camera_settings(camera_index, persisted, set_active=True, path=path)
    print(f"Profil de la caméra {camera_index} sauvegardé dans {path} (caméra active) : {persisted}")


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def nothing(_):
    pass


def probe_resolutions(cap, candidates=COMMON_RESOLUTIONS, tolerance=4):
    """Teste chaque résolution candidate sur la caméra déjà ouverte : la
    demande (cap.set), lit ce que le pilote a réellement appliqué (cap.get),
    et ne garde que celles où la caméra a accepté la valeur demandée (à
    quelques pixels près - certains pilotes arrondissent). OpenCV n'offre
    pas d'énumération directe des modes supportés, c'est la seule méthode
    fiable multi-plateforme."""
    supported = []
    for w, h in candidates:
        cap.set(3, w)
        cap.set(4, h)
        cap.read()  # laisse le pilote appliquer le changement avant de lire les valeurs réelles
        actual_w, actual_h = cap.get(3), cap.get(4)
        if abs(actual_w - w) <= tolerance and abs(actual_h - h) <= tolerance:
            supported.append((w, h))
    return supported


def make_trackbars(values, resolution_presets):
    cv2.namedWindow(FULL_WINDOW)
    cv2.createTrackbar("Cam index", FULL_WINDOW, values["CameraIndex"], 4, nothing)
    cv2.createTrackbar("Preset resolution (0=manuel)", FULL_WINDOW, 0, max(1, len(resolution_presets)), nothing)
    cv2.createTrackbar("Largeur", FULL_WINDOW, values["CaptureWidth"], 1920, nothing)
    cv2.createTrackbar("Hauteur", FULL_WINDOW, values["CaptureHeight"], 1080, nothing)
    cv2.createTrackbar("Zone largeur %", FULL_WINDOW, int(values["ZoneWidthPercent"]), 100, nothing)
    cv2.createTrackbar("Zone hauteur %", FULL_WINDOW, int(values["ZoneHeightPercent"]), 100, nothing)
    # decalage stocke en -100..100 ; trackbar OpenCV n'accepte pas de negatif -> offset +100
    cv2.createTrackbar("Decalage X (100=centre)", FULL_WINDOW, int(values["ZoneOffsetXPercent"]) + 100, 200, nothing)
    cv2.createTrackbar("Decalage Y (100=centre)", FULL_WINDOW, int(values["ZoneOffsetYPercent"]) + 100, 200, nothing)
    cv2.createTrackbar("CamFPS (analyse)", FULL_WINDOW, values["CamFPS"], 30, nothing)


def read_trackbars():
    return {
        "CameraIndex": cv2.getTrackbarPos("Cam index", FULL_WINDOW),
        "PresetIndex": cv2.getTrackbarPos("Preset resolution (0=manuel)", FULL_WINDOW),
        "CaptureWidth": max(160, cv2.getTrackbarPos("Largeur", FULL_WINDOW)),
        "CaptureHeight": max(120, cv2.getTrackbarPos("Hauteur", FULL_WINDOW)),
        "ZoneWidthPercent": max(10, cv2.getTrackbarPos("Zone largeur %", FULL_WINDOW)),
        "ZoneHeightPercent": max(10, cv2.getTrackbarPos("Zone hauteur %", FULL_WINDOW)),
        "ZoneOffsetXPercent": cv2.getTrackbarPos("Decalage X (100=centre)", FULL_WINDOW) - 100,
        "ZoneOffsetYPercent": cv2.getTrackbarPos("Decalage Y (100=centre)", FULL_WINDOW) - 100,
        "CamFPS": max(1, cv2.getTrackbarPos("CamFPS (analyse)", FULL_WINDOW)),
    }


def set_trackbars(values):
    cv2.setTrackbarPos("Cam index", FULL_WINDOW, values["CameraIndex"])
    cv2.setTrackbarPos("Preset resolution (0=manuel)", FULL_WINDOW, 0)
    cv2.setTrackbarPos("Largeur", FULL_WINDOW, values["CaptureWidth"])
    cv2.setTrackbarPos("Hauteur", FULL_WINDOW, values["CaptureHeight"])
    cv2.setTrackbarPos("Zone largeur %", FULL_WINDOW, int(values["ZoneWidthPercent"]))
    cv2.setTrackbarPos("Zone hauteur %", FULL_WINDOW, int(values["ZoneHeightPercent"]))
    cv2.setTrackbarPos("Decalage X (100=centre)", FULL_WINDOW, int(values["ZoneOffsetXPercent"]) + 100)
    cv2.setTrackbarPos("Decalage Y (100=centre)", FULL_WINDOW, int(values["ZoneOffsetYPercent"]) + 100)
    cv2.setTrackbarPos("CamFPS (analyse)", FULL_WINDOW, values["CamFPS"])


def compute_zone(values):
    """Même calcul que Scripts/opencvcam.py::Cam.__init__."""
    largeur, hauteur = values["CaptureWidth"], values["CaptureHeight"]
    largeur_champ = round(values["ZoneWidthPercent"] * largeur / 100)
    hauteur_champ = round(values["ZoneHeightPercent"] * hauteur / 100)
    marge_x = largeur - largeur_champ
    marge_y = hauteur - hauteur_champ
    gauche = clamp(round((marge_x / 2) * (1 + values["ZoneOffsetXPercent"] / 100)), 0, marge_x)
    basse = clamp(round((marge_y / 2) * (1 + values["ZoneOffsetYPercent"] / 100)), 0, marge_y)
    return gauche, gauche + largeur_champ, basse, basse + hauteur_champ


def draw_skeleton(image, landmarks, img_height, img_width):
    connections = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS
    for conn in connections:
        start, end = landmarks[conn.start], landmarks[conn.end]
        cv2.line(image,
                 (int(start.x * img_width), int(start.y * img_height)),
                 (int(end.x * img_width), int(end.y * img_height)),
                 (0, 255, 0), 2)
    for lm in landmarks:
        cv2.circle(image, (int(lm.x * img_width), int(lm.y * img_height)), 4, (255, 255, 0), -1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--calibration", default="camera_calibration.json",
                         help="Chemin du fichier de calibration à lire/écrire (défaut : ./camera_calibration.json)")
    args = parser.parse_args()

    model_path = "assets/pose_landmarker_lite.task"
    if not os.path.isfile(model_path):
        print(f"Modèle MediaPipe introuvable : {model_path}")
        print("Lancez ce script depuis la racine du dépôt (là où se trouve assets/).")
        sys.exit(1)

    # Sans index explicite : profil de la caméra ACTIVE du fichier de
    # calibration (celle utilisée par les jeux), ou les défauts si le
    # fichier n'existe pas encore.
    values = load_camera_settings(path=args.calibration)
    make_trackbars(values, [])
    set_trackbars(values)

    save_clicked = [False]

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and point_in_rect(x, y, SAVE_BUTTON_RECT):
            save_clicked[0] = True

    cv2.setMouseCallback(FULL_WINDOW, on_mouse)

    base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

    cap = None
    current_index = None
    current_size = None
    pose_result = None
    last_pose_time = 0.0
    dirty = False
    saved_values = dict(values)
    resolution_presets = []
    verified_presets = False
    last_preset_index = 0

    def reprobe():
        nonlocal resolution_presets, verified_presets, last_preset_index, current_size
        print(f"Sondage des résolutions supportées par la caméra {current_index}...")
        found = probe_resolutions(cap)
        verified_presets = bool(found)
        resolution_presets = found if found else list(COMMON_RESOLUTIONS)
        if found:
            print("Résolutions confirmées supportées :")
        else:
            print("Impossible de vérifier les résolutions supportées par cette caméra "
                  "(pilote ne répond pas aux requêtes) - liste indicative, non garantie :")
        for i, (rw, rh) in enumerate(resolution_presets, 1):
            print(f"  {i}. {rw}x{rh}")
        cv2.setTrackbarMax("Preset resolution (0=manuel)", FULL_WINDOW, len(resolution_presets))
        cv2.setTrackbarPos("Preset resolution (0=manuel)", FULL_WINDOW, 0)
        last_preset_index = 0
        # le sondage change le mode de capture en direct : on revient à la
        # résolution actuellement réglée dans les curseurs.
        cap.set(3, values["CaptureWidth"])
        cap.set(4, values["CaptureHeight"])
        current_size = (values["CaptureWidth"], values["CaptureHeight"])

    print(__doc__)

    try:
        while True:
            values = read_trackbars()
            # PresetIndex est un simple raccourci UI pour préremplir Largeur/
            # Hauteur, pas un réglage à comparer/sauvegarder pour lui-même.
            dirty = {k: v for k, v in values.items() if k != "PresetIndex"} != saved_values

            if values["CameraIndex"] != current_index:
                if cap is not None:
                    cap.release()
                new_index = values["CameraIndex"]
                # Chaque caméra a son propre profil sauvegardé (résolution,
                # zone, décalage...) - on le recharge automatiquement en
                # changeant d'index, plutôt que de garder les réglages de
                # la caméra précédente.
                profile = load_config(new_index, args.calibration)
                set_trackbars(profile)
                values = read_trackbars()
                saved_values = {k: v for k, v in profile.items()}
                cap = cv2.VideoCapture(new_index)
                current_index = new_index
                current_size = None
                if not cap.isOpened():
                    print(f"Caméra {current_index} introuvable / non accessible.")
                else:
                    print(f"Profil chargé pour la caméra {current_index} : {profile}")
                    reprobe()

            if values["PresetIndex"] != last_preset_index:
                last_preset_index = values["PresetIndex"]
                if 1 <= values["PresetIndex"] <= len(resolution_presets):
                    preset_w, preset_h = resolution_presets[values["PresetIndex"] - 1]
                    cv2.setTrackbarPos("Largeur", FULL_WINDOW, preset_w)
                    cv2.setTrackbarPos("Hauteur", FULL_WINDOW, preset_h)
                    values["CaptureWidth"], values["CaptureHeight"] = preset_w, preset_h

            size = (values["CaptureWidth"], values["CaptureHeight"])
            if cap is not None and cap.isOpened() and size != current_size:
                cap.set(3, size[0])
                cap.set(4, size[1])
                current_size = size

            if cap is None or not cap.isOpened():
                time.sleep(0.2)
                continue

            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            gauche, droite, basse, haute = compute_zone(values)
            gauche, droite = clamp(gauche, 0, w), clamp(droite, 0, w)
            basse, haute = clamp(basse, 0, h), clamp(haute, 0, h)
            zone = frame[basse:haute, gauche:droite]

            if last_preset_index == 0:
                preset_label = "manuel"
            else:
                preset_label = f"{last_preset_index}/{len(resolution_presets)}"
            preset_tag = "verifiees" if verified_presets else "indicatives (non verifiees)"

            full_preview = frame.copy()
            cv2.rectangle(full_preview, (gauche, basse), (droite, haute), (0, 255, 255), 2)
            cv2.putText(full_preview, f"cam={values['CameraIndex']} {w}x{h}  zone={values['ZoneWidthPercent']}%x{values['ZoneHeightPercent']}%  decalage=({values['ZoneOffsetXPercent']},{values['ZoneOffsetYPercent']})",
                        (10, h - 26), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(full_preview, f"preset={preset_label} ({preset_tag}) - 'p' pour resonder",
                        (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

            bx1, by1, bx2, by2 = SAVE_BUTTON_RECT
            button_color = (0, 200, 0) if dirty else (90, 90, 90)
            cv2.rectangle(full_preview, (bx1, by1), (bx2, by2), button_color, -1)
            cv2.rectangle(full_preview, (bx1, by1), (bx2, by2), (255, 255, 255), 1)
            button_label = "SAUVEGARDER" if dirty else "SAUVEGARDE"
            cv2.putText(full_preview, button_label, (bx1 + 8, by1 + 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(FULL_WINDOW, full_preview)

            zh, zw = zone.shape[:2] if zone.size else (0, 0)
            if zh > 0 and zw > 0:
                pose_interval = 1.0 / values["CamFPS"]
                now = time.time()
                zone_interdite = True
                if now - last_pose_time >= pose_interval:
                    last_pose_time = now
                    rgb = cv2.cvtColor(zone, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                    pose_result = landmarker.detect_for_video(mp_image, int(now * 1000))

                zone_preview = zone.copy()
                if pose_result is not None and pose_result.pose_landmarks:
                    landmarks = pose_result.pose_landmarks[0]
                    draw_skeleton(zone_preview, landmarks, zh, zw)
                    zone_interdite = False
                    for i in range(27, 33):
                        pos_y = landmarks[i].y * zh
                        if not (0 < pos_y < zh):
                            zone_interdite = True
                            break

                label, color = ("HORS ZONE", (0, 0, 255)) if zone_interdite else ("ZONE OK", (0, 255, 0))
                cv2.putText(zone_preview, label, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
                cv2.imshow(ZONE_WINDOW, zone_preview)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                if dirty:
                    print("Quitté sans sauvegarder (appuyez sur 's' avant de quitter pour garder les réglages).")
                break
            elif key == ord('s') or save_clicked[0]:
                save_clicked[0] = False
                persisted_values = {k: v for k, v in values.items() if k != "PresetIndex"}
                save_config(current_index, persisted_values, args.calibration)
                saved_values = persisted_values
            elif key == ord('r'):
                values = load_config(current_index, args.calibration)
                set_trackbars(values)
                saved_values = dict(values)
            elif key == ord('p') and cap is not None and cap.isOpened():
                reprobe()
    finally:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
