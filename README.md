# Fanny Pétanque World Tour

*An #ARDUCIBLE pétanque game.*

Borne d'arcade de pétanque en Python/Pygame : le joueur vise trois cibles
physiques à capteurs à effet Hall (pilotées par un Arduino Leonardo en
clavier), pendant qu'une webcam avec suivi de pose (MediaPipe) vérifie qu'il
reste dans la zone de tir. Tour du monde à travers 111 pays, chacun avec son
hymne, son portrait et sa réplique.

## Comment ça marche

- **Les cibles sont physiques**, montées sur un socle et équipées de capteurs
  à effet Hall. Elles sont raccordées à un **Arduino Leonardo**, que
  l'ordinateur reconnaît comme un clavier USB : toucher une cible envoie une
  touche (`E`, `R` ou `T`) au jeu.
- **La webcam ne sert pas à viser.** Couplée à un suivi de pose
  ([MediaPipe](https://ai.google.dev/edge/mediapipe)), elle vérifie juste que
  le joueur est bien positionné dans la zone de tir désignée. S'il en sort,
  les cibles sont inhibées (`zoneinterdite`) jusqu'à ce qu'il y revienne.
- **Tour du monde.** Chaque série de tirs réussis (`hits_per_country` dans
  `config.ini`) fait passer au pays suivant parmi 111 : décor, hymne
  national, portrait et réplique de la compagne de route Fanny changent à
  chaque étape (voir `Scripts/dialogues.py`).
- Le jeu reste jouable sans webcam ni cibles physiques (mode clavier seul).

## Installation

```bash
pip install -r requirements.txt
python main.py
```

Un `config.ini` est généré automatiquement au premier lancement s'il
n'existe pas.

## Configuration (`config.ini`)

| Section | Clé | Rôle |
|---|---|---|
| `TimeSetting` | `intro_length`, `game_length`, `ending_length`, `splash_length` | Durées (s) des différents écrans |
| `BonusTime` | `time`, `country_change_time` | Bonus de temps par tir réussi / par changement de pays |
| `WorldTour` | `hits_per_country` | Nombre de tirs pour passer au pays suivant |
| `CamActivation` | `Webcam`, `CamFPS` | Active la webcam et sa cadence d'analyse MediaPipe |
| `Screen` | `Fullscreen`, `CRT` | Plein écran, effet de superposition CRT rétro |
| `Audio` | `Music`, `Effects`, `FadeoutTime` | Musique de menu, effets sonores, fondu |
| `Resolution` | `Resolution` | `1080`, `720`, `360`, `240` (sinon 1024x768) |
| `Debug` | `DebugLine`, `FPS`, `ShowFps`, `DebugCam`, `Credit` | Grille de repérage, FPS cible/affiché, superposition du squelette MediaPipe sur l'image caméra réelle (au lieu d'un fond noir), crédits de départ |
| `Score` | `high_score` | Meilleur score, sauvegardé automatiquement |

## Contrôles clavier

| Touche | Action |
|---|---|
| `E` / `R` / `T` | Cible gauche / centre / droite (normalement envoyées par l'Arduino) |
| `I` | Ajoute un crédit |
| `M` | Coupe / relance la musique |
| `S` | Active / coupe les effets sonores |
| `Échap` | Quitte le jeu |

## Structure du projet

```
main.py                  Boucle de jeu et logique d'écran
Scripts/init.py           Config.ini, polices, couleurs, canaux audio
Scripts/Sprites.py        Sprites (cibles, fonds, Fanny, bulles de dialogue)
Scripts/opencvcam.py      Capture webcam + détection de pose MediaPipe
Scripts/dialogues.py      Données des 111 pays (généré automatiquement)
assets/                   Images, sons, fonts, modèle MediaPipe
```

## Licence

CC0 1.0 Universal — voir [`LICENSE`](LICENSE).
