"""Calibration caméra partagée entre Fanny World Tour, Round the Clock et
calibrate_camera.py.

Fichier dédié (camera_calibration.json, pas config.ini) : une entrée par
INDEX de caméra, pour ne pas perdre le calibrage d'une caméra en en
recalibrant une autre (plusieurs bornes/caméras peuvent partager ce dépôt).
config.ini garde seulement `Webcam` (active/désactive la fonctionnalité) -
tout ce qui décrit LA caméra elle-même (résolution, zone de tir, cadence
d'analyse) vit ici."""
import json
import os

CALIBRATION_FILE = "camera_calibration.json"

DEFAULTS = {
    "CaptureWidth": 320,
    "CaptureHeight": 240,
    "ZoneWidthPercent": 35,
    "ZoneHeightPercent": 55,
    "ZoneOffsetXPercent": 0,
    "ZoneOffsetYPercent": 0,
    "CamFPS": 5,
}


def _read_all(path=CALIBRATION_FILE):
    if not os.path.exists(path):
        return {"active_camera_index": 0, "cameras": {}}
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Erreur lecture {path} : {e}. Valeurs par défaut utilisées.")
        return {"active_camera_index": 0, "cameras": {}}
    data.setdefault("active_camera_index", 0)
    data.setdefault("cameras", {})
    return data


def load_camera_settings(camera_index=None, path=CALIBRATION_FILE):
    """Réglages de calibration pour `camera_index` (index caméra actif
    du fichier si omis), complétés par les défauts pour les clés absentes
    (première utilisation, ou caméra jamais calibrée)."""
    data = _read_all(path)
    if camera_index is None:
        camera_index = data["active_camera_index"]
    profile = data["cameras"].get(str(camera_index), {})
    values = dict(DEFAULTS)
    values.update({k: v for k, v in profile.items() if k in DEFAULTS})
    values["CameraIndex"] = camera_index
    return values


def save_camera_settings(camera_index, values, set_active=True, path=CALIBRATION_FILE):
    """Enregistre le profil de `camera_index` (seules les clés de DEFAULTS
    sont conservées). set_active=True en fait la caméra utilisée par les
    jeux au prochain lancement."""
    data = _read_all(path)
    data["cameras"][str(camera_index)] = {k: v for k, v in values.items() if k in DEFAULTS}
    if set_active:
        data["active_camera_index"] = camera_index
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return data
