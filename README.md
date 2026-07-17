# Fanny Pétanque World Tour

*An #ARDUCIBLE pétanque game.*

Borne d'arcade de pétanque en Python/Pygame : le joueur vise trois cibles
physiques à capteurs à effet Hall (pilotées par un Arduino Leonardo en
clavier), pendant qu'une webcam avec suivi de pose (MediaPipe) vérifie qu'il
reste dans la zone de tir. Tour du monde à travers 115 pays, chacun avec son
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
  `config.ini`) fait passer au pays suivant parmi 115 : décor, hymne
  national, portrait et réplique de la compagne de route Fanny changent à
  chaque étape (voir `Scripts/dialogues.py`).
- Le jeu reste jouable sans webcam ni cibles physiques (mode clavier seul).

## Les 4 jeux en un coup d'œil

Un seul châssis physique (3 cibles en ligne) sert au jeu de base, un second
châssis (7 cibles en étoile de David, cochonet au centre) sert à Hardcore et
Round the Clock. Quizz ne tire sur aucun châssis.

| Jeu | Fichier | Chassis | Principe | Touches | Modes | High score |
|---|---|---|---|---|---|---|
| **Fanny World Tour** | `main.py` | 3 cibles en ligne | Solo, contre-la-montre, tour du monde | `E R T` | Tour complet ou par continent | `[Score]` |
| **Hardcore** | `main_hardcore.py` | 7 cibles étoile | Identique à Fanny, cochonet = pays suivant | `E R T Y U I O` | Tour complet ou par continent | `[Hardcore]` |
| **Quizz** | `main_quizz.py` | Aucun (pas de tir) | 5 questions par pays (pétanque + culture générale) | `E R T` (choix) | Tour complet ou par continent | `[Quizz]` |
| **Round the Clock** | `main_round_the_clock.py` | 7 cibles étoile | Multijoueur tour par tour, viser la cible imposée dans l'ordre 1→7 | `E R T Y U I O` (+ `Y`/`U`/`O` pour options/aide/valider) | Nombre de joueurs (1-6) et de manches (3-12) réglables en jeu | Aucun (non persistant, absent de l'original) |

Déroulement commun à Fanny World Tour, Hardcore et Quizz (Round the Clock a
son propre menu à cibles, voir plus bas) : **accueil** (`INSERT COIN` ou
`FREEPLAY`) → **choix du mode** (tour complet ou un seul continent, carrousel
`E`/`T`, validation `R`, ou lancement automatique au bout de 60 s sans choix)
→ **décompte `GAME START IN`** → **partie** → **écran de fin**, puis retour à
l'accueil.

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
| `CamActivation` | `Webcam` | Active/désactive la webcam. Tout ce qui décrit la caméra elle-même (index, résolution, cadrage de la zone de tir, cadence d'analyse) est dans `camera_calibration.json`, pas ici — voir plus bas |
| `Screen` | `Fullscreen`, `CRT` | Plein écran, effet de superposition CRT rétro |
| `Audio` | `Music`, `Effects`, `FadeoutTime` | Musique de menu, effets sonores, fondu |
| `Resolution` | `Resolution` | `1080`, `720`, `360`, `240` (sinon 1024x768) |
| `Debug` | `DebugLine`, `FPS`, `ShowFps`, `DebugCam`, `Credit`, `FreePlay` | Grille de repérage, FPS cible/affiché, superposition du squelette MediaPipe sur l'image caméra réelle (au lieu d'un fond noir), crédits de départ, mode freeplay (voir ci-dessous) — section partagée par les 3 jeux |
| `Score` | `high_score` | Meilleur score de Fanny World Tour (jeu de base), sauvegardé automatiquement |
| `Hardcore` | `high_score`, `hits_per_country` | Meilleur score et rythme du tour du monde propres au mode Hardcore (7 cibles) |
| `Quizz` | `high_score` | Meilleur score du Quizz (bonnes réponses sur 575), sauvegardé automatiquement |
| `RoundTheClock` | `targets`, `default_players`, `min_players`, `max_players`, `default_rounds`, `min_rounds`, `max_rounds`, `shots_per_turn`, `hit_cooldown_ms`, `menu_cooldown_ms`, `banner_duration_s` | Réglages propres à Round the Clock (pas de high score persistant) |

### Crédits / mode freeplay

Comportement identique sur les 3 jeux (Fanny World Tour, Hardcore, Round the
Clock) : par défaut, l'écran d'accueil affiche **INSERT COIN** et le nombre
de crédits (`[Debug] Credit`) en bas à droite tant qu'aucun crédit n'est
disponible ; la touche `C` en ajoute un (borne réelle : pièce détectée par
l'Arduino). Sur Hardcore et Round the Clock, les 7 touches de cible
`E R T Y U I O` occupent déjà tout l'alphabet utile du chassis étoile, d'où
le choix de `C`, libre sur les 3 jeux.

Avec `[Debug] FreePlay = True` : "INSERT COIN" et le compteur de crédits
sont remplacés par **"PRESS A TARGET TO PLAY"** / **FREEPLAY**. Presser
n'importe quelle cible physique équivaut alors à insérer un crédit fictif —
Fanny/Hardcore/Quizz lancent leur écran de choix du mode (voir ci-dessous),
Round the Clock débloque directement son menu (`O` pour démarrer).

### Choix du mode (tour complet ou par continent)

Sur Fanny World Tour, Hardcore et Quizz, un crédit disponible ouvre un écran
de sélection avant que la partie ne démarre : un mode à la fois au centre
(tour complet des 115 pays, ou un seul continent), avec le nombre de pays
qu'il contient. Navigation au carrousel — `E` précédent, `T` suivant, `R`
valider — matérialisée par les 3 boules physiques du socle (gauche/centre/
droite), le joueur n'ayant pas de clavier sous les yeux sur la borne. Sans
choix au bout de **60 secondes**, la partie démarre automatiquement sur le
mode affiché (comme un appui sur `R`). Seul le mode "Tour complet" alimente
le high score de sa section (`[Score]`/`[Hardcore]`/`[Quizz]`) — un score sur
un seul continent, moins long, n'est pas comparable et s'affiche à part.

## Contrôles clavier

| Touche | Action |
|---|---|
| `E` / `R` / `T` | Cible gauche / centre / droite (normalement envoyées par l'Arduino) |
| `C` | Ajoute un crédit |
| `M` | Coupe / relance la musique |
| `S` | Active / coupe les effets sonores |
| `Échap` | Quitte le jeu |

## Structure du projet

```
main.py                        Fanny World Tour : boucle de jeu et logique d'écran
main_hardcore.py                Hardcore (7 cibles), fork de main.py
main_quizz.py                   Quizz (sans tir), fork de main.py
main_round_the_clock.py         Round the Clock (7 cibles, multijoueur), indépendant
Scripts/init.py                 Config.ini, polices, couleurs, canaux audio
Scripts/Sprites.py               Sprites (cibles, fonds, Fanny, bulles de dialogue)
Scripts/opencvcam.py             Capture webcam + détection de pose MediaPipe
Scripts/camera_calibration.py    Lecture/écriture camera_calibration.json
Scripts/dialogues.py             Données des 115 pays (généré automatiquement)
Scripts/quiz_questions.py        Questions du quizz par pays (voir main_quizz.py)
Scripts/quiz_audio.py            Retrouve le mp3 TTS correspondant à un texte de quizz
Scripts/round_the_clock/         État et sprites propres à Round the Clock
assets/                          Images, sons, fonts, modèle MediaPipe
```

## Calibration de la caméra

`calibrate_camera.py` est un script autonome (indépendant des deux jeux) pour
régler la webcam et la zone de tir qu'elle analyse : index de la caméra,
résolution de capture (réglage manuel pixel par pixel, ou menu déroulant
"Preset resolution" listant les résolutions courantes — la caméra détectée
est automatiquement sondée pour ne proposer que celles qu'elle supporte
réellement), taille et position (décalage) de la zone recadrée envoyée à
MediaPipe. Deux fenêtres live — l'image caméra complète avec la zone en
surbrillance, et exactement ce que le jeu voit (recadrage + squelette
détecté + statut "ZONE OK"/"HORS ZONE") — permettent d'ajuster les curseurs
jusqu'à ce que le cadrage corresponde à la zone marquée au sol.

```bash
python3 calibrate_camera.py
# ou
./run_calibrate_camera.sh
```

Réglages enregistrés dans `camera_calibration.json` (à la racine du dépôt,
**pas** `config.ini`) : un profil complet par index de caméra, pour ne pas
perdre le calibrage d'une caméra en en recalibrant une autre — changer de
caméra dans le script recharge automatiquement son profil déjà sauvegardé.
`config.ini` garde seulement l'interrupteur `[CamActivation] Webcam`.

Sauvegarde : bouton **SAUVEGARDER** cliquable en haut à gauche de la fenêtre
"Camera complete" (vert = modifications non sauvegardées, gris = déjà à
jour), ou touche `s` — les deux font la même chose : sauvegardent le profil
de la caméra courante et en font la caméra active pour les jeux.

Autres touches : `r` réinitialise aux valeurs sauvegardées, `p` ressonde les
résolutions supportées, `q`/Échap quitte.

## Round the Clock (chassis à 7 cibles)

`main_round_the_clock.py` est un **second jeu**, indépendant de Fanny World
Tour, pour un chassis différent équipé de **7 cibles physiques disposées en
étoile de David** (6 boules sur les pointes de l'étoile, un **cochonet** au
centre). Même principe électronique (capteurs à effet Hall → Arduino →
clavier USB, touches `E R T Y U I O` pour les cibles 1 à 7), mais un jeu très
différent : un **multijoueur au tour par tour (1 à 6 joueurs, 3 à 12
manches)**, porté fidèlement depuis la version Lua/Defold d'origine
(`ressources/Petanque-challenge-Round-the-clock/`).

- Chaque joueur dispose de 3 tirs par passage et doit toucher les cibles
  dans l'ordre 1 à 7 (au-delà, cible aléatoire).
- Toucher une autre cible que celle désignée compte comme un raté — c'est
  aussi le seul moyen de comptabiliser un tir qui n'a touché aucune cible
  physique (pas de capteur dédié à "l'échec total").
- Jouable sans matériel physique : flèches gauche/droite simulent
  respectivement un tir réussi / raté sur la cible active (pas de bouton
  affiché à l'écran, c'est un raccourci clavier discret).
- Reprend le suivi de zone par webcam (MediaPipe) comme Fanny World Tour
  (absent du jeu Defold d'origine, ajouté lors du portage) : même position à
  l'écran (caméra et anneau rouge/vert centrés en haut) et même système de
  double fond par pays (variante `.jpg` pleine si pas de webcam, variante
  `.png` à découpe ovale transparente si webcam active, à travers laquelle
  la caméra apparaît).
- Le décor change de pays (parmi les fonds de `assets/Images/BackgroundWorldTour/`
  déjà utilisés par Fanny World Tour) après chaque tir réussi.
- Menu et écran de fin reprennent l'illustration de fin de Fanny World Tour
  (`assets/Images/EndingScreenWorldTour.jpg`).

```bash
python3 main_round_the_clock.py
# ou
./run_round_the_clock.sh
```

Partage le même `config.ini` que Fanny World Tour (sections `Screen`,
`Audio`, `CamActivation`, `Debug`, `Resolution` communes), avec sa propre
section `[RoundTheClock]` (nombre de joueurs/manches par défaut, tirs par
passage, anti-rebond).

## Hardcore (chassis à 7 cibles)

`main_hardcore.py` est un **troisième jeu** : le principe exact de Fanny
World Tour (solo, contre-la-montre, tour du monde à travers 115 pays, Fanny
en compagne de route) mais joué sur le chassis à **7 cibles en étoile de
David** de Round the Clock, au lieu des 3 cibles en ligne du jeu d'origine.
Réutilise directement `Scripts/init.py` et `Scripts/Sprites.py` (mêmes
fonds, portraits, hymnes, webcam) — seule la gestion des cibles change.

- 7 cibles, touches `E R T Y U I O`. Le tir qui fait passer au pays suivant
  (score+1 multiple de `hits_per_country`) vise systématiquement le
  **cochonet**, au centre de l'étoile ; tous les autres tirs visent une
  boule périphérique tirée au hasard (jamais deux fois de suite la même).
- Pas d'annonce vocale de cible ("gauche/centre/droite" ne correspond plus
  à rien en étoile) : seul le son d'impact joue.
- `high_score` et `hits_per_country` (rythme du tour du monde) propres à
  Hardcore, dans leur propre section `[Hardcore]` de `config.ini`,
  indépendants du jeu de base.

```bash
python3 main_hardcore.py
# ou
./run_hardcore.sh
```

## Quizz (tour du monde + culture générale, sans tir)

`main_quizz.py` est un **quatrième jeu**, quizz uniquement : pas de cibles,
pas de webcam, pas de chrono de partie. Après avoir inséré un crédit, le
joueur enchaîne directement les **115 quizz** (un par pays du tour, 5
questions chacun) dans l'ordre, en répondant avec les touches `E R T`
(choix gauche/centre/droite). Le score final est le nombre total de bonnes
réponses sur l'ensemble du tour (sur 575).

- Décor, hymne et portrait de Fanny changent à chaque pays, comme dans
  Fanny World Tour, mais pilotés directement par pays plutôt que par un
  score de tir.
- Questions dans `Scripts/quiz_questions.py` (généré à partir de
  `Scripts/dialogues.py` + une table de métadonnées pays) : 1 question sur
  la pétanque dans le pays (reconnaître la bonne réplique de Fanny parmi 3),
  4 questions de culture générale (capitale, continent, langue, monnaie).
  Chaque mauvaise réponse est toujours un vrai fait — juste celui d'un
  *autre* pays de la liste — jamais une donnée inventée.
- Questions et réponses affichées à l'écran avec une police pleine à
  accentuation complète (`assets/RoundTheClock/Fonts/DejaVuSans.ttf`) —
  Alfa Slab One n'a pas les glyphes accentués (é, à, ç...) nécessaires en
  français — et **narrées en voix de synthèse** (gTTS) : un mp3 par texte
  unique dans `assets/Sounds/QuizzTTS/`, généré hors-ligne par
  `ressources/utils/generate_quiz_audio.py` et retrouvé à l'exécution via
  `Scripts/quiz_audio.py` (silencieux si un fichier manque plutôt que de
  planter).
- `high_score` propre à Quizz (nombre de bonnes réponses sur 575), dans sa
  propre section `[Quizz]` de `config.ini`, indépendant des autres jeux.

```bash
python3 main_quizz.py
# ou
./run_quizz.sh
```

## Licence

CC BY 4.0 — voir [`LICENSE`](LICENSE).

Fanny Pétanque World Tour © Jean-Baptiste Guiraud. Vous êtes libre de
partager et d'adapter ce travail, y compris à des fins commerciales, à
condition de créditer l'auteur.
