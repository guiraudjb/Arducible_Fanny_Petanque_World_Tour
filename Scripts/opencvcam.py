import cv2
import mediapipe as mp
import numpy as np
import pygame
from Scripts.init import *

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
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.zoneinterdite = True
        self.PourcentageLargeurCamera = 35
        self.PourcentageHauteurCamera = 55
        self.Largeur = 320
        self.Hauteur = 240

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.webcam_compatibility = False
        else:
            self.webcam_compatibility = True
        self.cap.set(3, self.Largeur)
        self.cap.set(4, self.Hauteur)

        self.LargeurChampCamera = round((self.PourcentageLargeurCamera * self.Largeur) / 100)
        self.HauteurChampCamera = round((self.PourcentageHauteurCamera * self.Hauteur) / 100)
        self.LimiteGaucheCamera = round((self.Largeur - self.LargeurChampCamera) / 2)
        self.LimiteDroiteCamera = round(self.Largeur - (self.Largeur - self.LargeurChampCamera) / 2)
        self.LimiteBasseCamera = round((self.Hauteur - self.HauteurChampCamera) / 2)
        self.LimiteHauteCamera = round(self.Hauteur - (self.Hauteur - self.HauteurChampCamera) / 2)

        base_options = mp.tasks.BaseOptions(model_asset_path='assets/pose_landmarker_lite.task')
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

        self.pose_result = None
        self.last_pose_time = 0
        self.pose_interval = round(1000 / max(1, cam_fps))

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
                self.zoneinterdite = False
                for i in range(27, 33):
                    posY = landmarks[i].y * self.HauteurChampCamera
                    if not (0 < posY < self.HauteurChampCamera):
                        self.zoneinterdite = True
                        break
            else:
                self.zoneinterdite = True

        # Stickman sur fond noir, ou sur l'image caméra si DebugCam est actif
        h, w = self.photo.shape[:2]
        base_frame = self.photo.copy() if DebugCam else np.zeros((h, w, 3), dtype=np.uint8)
        if self.pose_result is not None and self.pose_result.pose_landmarks:
            draw_skeleton(base_frame, self.pose_result.pose_landmarks[0], h, w)

        rgb_frame = cv2.cvtColor(base_frame, cv2.COLOR_BGR2RGB)
        self.cam = pygame.surfarray.make_surface(rgb_frame)
        self.cam = pygame.transform.rotate(self.cam, -90)
        self.cam = pygame.transform.scale(self.cam, (_CAM_DISPLAY_W * LARGEUR_ECRAN // 1920, _CAM_DISPLAY_H * HAUTEUR_ECRAN // 1080))
        self.image = self.cam
        self.rect = self.image.get_rect()
        self.width, self.height = self.image.get_rect().size
