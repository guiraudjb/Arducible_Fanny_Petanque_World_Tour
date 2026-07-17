import cv2
import mediapipe as mp
import numpy as np
import pygame

_CAM_DISPLAY_W = 224  # largeur stickman à 1920x1080
_CAM_DISPLAY_H = 383  # hauteur stickman à 1920x1080


def draw_skeleton(image, landmarks, img_height, img_width):
    pose_connections = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS
    for conn in pose_connections:
        start = landmarks[conn.start]
        end = landmarks[conn.end]
        cv2.line(image,
                 (int(start.x * img_width), int(start.y * img_height)),
                 (int(end.x * img_width), int(end.y * img_height)),
                 (0, 255, 0), 2)
    for lm in landmarks:
        cv2.circle(image,
                   (int(lm.x * img_width), int(lm.y * img_height)),
                   4, (255, 255, 0), -1)


class Cam(pygame.sprite.Sprite):
    def __init__(self, cam_fps=None, debug_cam=None, largeur_ecran=None, hauteur_ecran=None,
                 camera_index=None, capture_width=None, capture_height=None,
                 zone_width_percent=None, zone_height_percent=None,
                 zone_offset_x_percent=None, zone_offset_y_percent=None):
        """Tous les paramètres sont optionnels : si omis, on retombe sur
        Scripts.init (comportement historique de Fanny World Tour, appelée
        via Cam() sans argument). Les appelants indépendants de Fanny
        (ex : Round the Clock) passent leurs propres valeurs pour éviter
        d'importer tout le bootstrap de Fanny.

        zone_width_percent/zone_height_percent : taille de la zone de tir
        analysée par MediaPipe, en % de l'image capturée (recadrage centré
        par défaut). zone_offset_x_percent/zone_offset_y_percent (-100 à
        100, 0 = centré) décalent ce recadrage dans la marge disponible,
        pour les cas où la caméra n'est pas parfaitement alignée avec la
        zone de tir marquée au sol - voir calibrate_camera.py."""
        args = (cam_fps, debug_cam, largeur_ecran, hauteur_ecran, camera_index, capture_width,
                capture_height, zone_width_percent, zone_height_percent,
                zone_offset_x_percent, zone_offset_y_percent)
        if None in args:
            from Scripts.init import cam_fps as _cam_fps, DebugCam as _DebugCam, \
                LARGEUR_ECRAN as _LARGEUR_ECRAN, HAUTEUR_ECRAN as _HAUTEUR_ECRAN, \
                camera_index as _camera_index, capture_width as _capture_width, \
                capture_height as _capture_height, zone_width_percent as _zone_width_percent, \
                zone_height_percent as _zone_height_percent, \
                zone_offset_x_percent as _zone_offset_x_percent, \
                zone_offset_y_percent as _zone_offset_y_percent
            cam_fps = _cam_fps if cam_fps is None else cam_fps
            debug_cam = _DebugCam if debug_cam is None else debug_cam
            largeur_ecran = _LARGEUR_ECRAN if largeur_ecran is None else largeur_ecran
            hauteur_ecran = _HAUTEUR_ECRAN if hauteur_ecran is None else hauteur_ecran
            camera_index = _camera_index if camera_index is None else camera_index
            capture_width = _capture_width if capture_width is None else capture_width
            capture_height = _capture_height if capture_height is None else capture_height
            zone_width_percent = _zone_width_percent if zone_width_percent is None else zone_width_percent
            zone_height_percent = _zone_height_percent if zone_height_percent is None else zone_height_percent
            zone_offset_x_percent = _zone_offset_x_percent if zone_offset_x_percent is None else zone_offset_x_percent
            zone_offset_y_percent = _zone_offset_y_percent if zone_offset_y_percent is None else zone_offset_y_percent
        self.cam_fps = cam_fps
        self.debug_cam = debug_cam
        self.largeur_ecran = largeur_ecran
        self.hauteur_ecran = hauteur_ecran

        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.zoneinterdite = True
        self.PourcentageLargeurCamera = zone_width_percent
        self.PourcentageHauteurCamera = zone_height_percent
        self.Largeur = capture_width
        self.Hauteur = capture_height

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.webcam_compatibility = False
        else:
            self.webcam_compatibility = True
        self.cap.set(3, self.Largeur)
        self.cap.set(4, self.Hauteur)

        self.LargeurChampCamera = round((self.PourcentageLargeurCamera * self.Largeur) / 100)
        self.HauteurChampCamera = round((self.PourcentageHauteurCamera * self.Hauteur) / 100)
        marge_x = self.Largeur - self.LargeurChampCamera
        marge_y = self.Hauteur - self.HauteurChampCamera
        self.LimiteGaucheCamera = round((marge_x / 2) * (1 + zone_offset_x_percent / 100))
        self.LimiteGaucheCamera = max(0, min(marge_x, self.LimiteGaucheCamera))
        self.LimiteDroiteCamera = self.LimiteGaucheCamera + self.LargeurChampCamera
        self.LimiteBasseCamera = round((marge_y / 2) * (1 + zone_offset_y_percent / 100))
        self.LimiteBasseCamera = max(0, min(marge_y, self.LimiteBasseCamera))
        self.LimiteHauteCamera = self.LimiteBasseCamera + self.HauteurChampCamera

        base_options = mp.tasks.BaseOptions(model_asset_path='assets/pose_landmarker_lite.task')
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.7,
            min_pose_presence_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

        self.pose_result = None
        self.last_pose_time = 0
        self.pose_interval = round(1000 / max(1, self.cam_fps))

        self.cap.read()  # warm-up frame

    def update(self):

        # Lecture et recadrage à chaque frame (vide le buffer caméra)
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return
        self.photo = cv2.flip(frame, 1)
        self.photo = self.photo[self.LimiteBasseCamera:self.LimiteHauteCamera, self.LimiteGaucheCamera:self.LimiteDroiteCamera]

        # MediaPipe uniquement à la cadence configurée (CamFPS dans config.ini)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pose_time >= self.pose_interval:
            self.last_pose_time = current_time
            rgb = cv2.cvtColor(self.photo, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            self.pose_result = self.landmarker.detect_for_video(mp_image, current_time)

            if self.pose_result.pose_landmarks:
                landmarks = self.pose_result.pose_landmarks[0]
                # Un point de pied peu visible (occlusion, faux positif sur
                # un arrière-plan) ne doit pas compter comme "hors zone" ni
                # "dans la zone" - on l'ignore plutôt que de lui faire
                # confiance, MediaPipe pouvant halluciner des coordonnées
                # même à faible visibilité - détection trop sensible,
                # demande utilisateur du 2026-07-16.
                visible_feet = [landmarks[i] for i in range(27, 33) if landmarks[i].visibility >= 0.5]
                if not visible_feet:
                    self.zoneinterdite = True
                else:
                    self.zoneinterdite = False
                    for lm in visible_feet:
                        posY = lm.y * self.HauteurChampCamera
                        if not (0 < posY < self.HauteurChampCamera):
                            self.zoneinterdite = True
                            break
            else:
                self.zoneinterdite = True

        # Stickman sur fond noir, ou sur l'image caméra si debug_cam est actif
        h, w = self.photo.shape[:2]
        base_frame = self.photo.copy() if self.debug_cam else np.zeros((h, w, 3), dtype=np.uint8)
        if self.pose_result is not None and self.pose_result.pose_landmarks:
            draw_skeleton(base_frame, self.pose_result.pose_landmarks[0], h, w)

        rgb_frame = cv2.cvtColor(base_frame, cv2.COLOR_BGR2RGB)
        self.cam = pygame.surfarray.make_surface(rgb_frame)
        self.cam = pygame.transform.rotate(self.cam, -90)
        self.cam = pygame.transform.scale(
            self.cam,
            (_CAM_DISPLAY_W * self.largeur_ecran // 1920, _CAM_DISPLAY_H * self.hauteur_ecran // 1080))
        self.image = self.cam
        self.rect = self.image.get_rect()
        self.width, self.height = self.image.get_rect().size
