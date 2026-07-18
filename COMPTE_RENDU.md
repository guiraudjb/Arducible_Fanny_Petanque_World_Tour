# Compte rendu — sessions du 15-18 juillet 2026

Résumé pour reprendre le travail à un autre poste (rappel : la mémoire Claude Code
n'est pas synchronisée entre machines, seul ce dépôt git l'est - voir aussi
`.claude/` pour la config de session). La skill FreeCAD headless mentionnée
plus bas (`~/.claude/skills/freecad-headless/`) est en revanche **locale à
cette machine** : à recréer sur un autre poste si besoin, voir sa description
ci-dessous.

## ✅ Tout est commité et poussé (au 18 juillet)

`git status` est propre sur `main`, à jour avec `origin/main`
(`github.com/guiraudjb/Arducible_Fanny_Petanque_World_Tour` - **dépôt
renommé** depuis `Fanny_P-tanque_World_Tour` le 17 juillet, voir plus bas).
Seuls restent volontairement non versionnés (trop lourds, régénérables, ou
sensibles) :
- `ressources/social_videos/` (~9,6 Go de rendus vidéo), `ressources/playing_cards/`
  (~250 Mo), `ressources/quizz_pdf/_postcards_cache/` (cache d'images
  téléchargées) — tous régénérables via les scripts de `ressources/utils/`.
- `ressources/Petanque-challenge-Round-the-clock/.../.internal/` et
  `x86_64-linux/` (cache/build Defold), `manifest.private.der`/`.public.der`
  (vraie clé privée RSA - **ne jamais commiter**), `social_videos_build.log`.

## Session du 15-16 juillet 2026 (+ suite du 16)

### 1. Écran de choix du continent repositionné
Avant : le décompte "GAME START IN" tournait avant l'écran de choix de mode.
Maintenant : accueil → **choix du continent** → décompte "GAME START IN" →
partie. Nouvel état `start_pregame_countdown()` dans les 3 jeux (gamestate 4
pour `main.py`/`main_hardcore.py`, gamestate 5 pour `main_quizz.py`).

### 2. Police "Neon Glow" abandonnée → Alfa Slab One
Neon Glow n'avait pas les glyphes accentués (« Amérique », « Océanie »
illisibles) et jurait avec le nouveau style. Remplacée partout par **Alfa
Slab One** (`assets/fonts/AlfaSlabOne-Regular.ttf`, licence OFL), choisie
avec l'utilisateur parmi 7 candidats après un vote sur la direction
stylistique (affiche de voyage vintage). `draw_text()` dans les 3 jeux garde
exactement la même signature/dispatch (`fnt`, `col`) : seul le rendu change
(ombre portée au lieu du halo néon superposé), donc aucun site d'appel à
toucher. Les 8 fichiers `NEON GLOW*.otf` ont été supprimés de
`assets/fonts/`.

### 3. Timeout + musique + boules physiques sur l'écran de choix du continent
- **Timeout 60s** : `CONTINENT_SELECT_TIMEOUT` - si le joueur ne choisit pas,
  la partie démarre automatiquement sur le mode affiché (comme un appui sur
  R).
- **Musique de menu maintenue** : le fondu (`channel1.fadeout(9000)`) ne se
  déclenche plus à l'insertion du crédit mais seulement quand le choix est
  validé (`start_pregame_countdown()`) - avant, la musique s'éteignait
  pendant que le joueur choisissait encore.
- **Boules du socle physique au lieu de lettres E/T/R** : le joueur n'a pas
  de clavier sous les yeux. `init_mode_select_cibles()` affiche 3 boules
  (gauche=E, centre=R, droite=T) avec légendes "PRÉCÉDENT/VALIDER/SUIVANT" -
  même principe que les boules déjà utilisées dans l'écran de quizz.

### 4. Palette de couleurs du HUD réajustée
Les couleurs (rouge/orange/jaune/bleu/vert dans `Scripts/init.py`) étaient
calibrées pour l'ancienne police néon - trop vives, elles juraient avec le
nouveau style. Désaturées/réchauffées vers les tons sépia/terracotta de
l'illustration elle-même (échantillonnés par k-means sur les images de
titre/fin), tout en gardant assez de contraste pour rester lisibles sur les
fonds de pays très variés. Choisi avec l'utilisateur parmi 3 options
rendues côte à côte. Un seul point de changement (`Scripts/init.py`), partagé
par les 3 jeux.

**Non touché volontairement** : `Scripts/round_the_clock/state.py` a sa
propre copie indépendante des anciennes couleurs néon (contexte visuel
différent - planches de bois, pas l'affiche vintage) - à voir si l'utilisateur
veut harmoniser un jour.

### 5. Vérification score final / high score + bug trouvé
Vérification demandée par l'utilisateur : la correspondance affichée entre
"YOUR SCORE" et "HIGH SCORE" était **déjà correcte** dans les 3 jeux (testé
cas record et non-record, avec captures d'écran en mode headless). Mais la
vérification a mis en évidence un vrai bug à côté : le test
"score >= high_score → sauver" tournait à **chaque frame** de l'écran de fin
(~10s) au lieu d'une seule fois - mesuré à **283 appels** à
`save_high_score()` pour un seul écran de fin. Corrigé en déplaçant le test
dans `next_gamestate()` (transition 1→2, `main.py`/`main_hardcore.py`) ou
`finish_quiz_tour()` (`main_quizz.py`), au moment exact où le score devient
définitif. Vérifié : 1 seul appel désormais, résultat affiché inchangé.

### 6. Chevauchements HUD corrigés dans `main_hardcore.py`
Sur le chassis à 7 cibles (étoile de David), plusieurs éléments de texte
chevauchaient les sprites des billes/cochonet à l'écran :
- **Score ("POINTS" + valeur)** : décalé de `x=4/20` (chevauchait la cible I,
  la plus haute) → `x=2/20` (rognait le bord gauche de l'écran, trop loin) →
  **`x=LARGEUR_ECRAN/8`**, le compromis qui évite les deux.
- **Temps restant** : recentré à **`(LARGEUR_ECRAN/3, HAUTEUR_ECRAN/3)`** -
  cette position correspond exactement au milieu entre la cible 6/I (la plus
  haute de l'étoile) et la cible 7/O (cochonet, cible centrale), qui
  partagent le même x (`TARGET_LAYOUT` dans `main_hardcore.py`).
- **"Go to the shooting zone"** : d'abord réduit de taille et calé dans
  l'étroit espace libre entre le cochonet et la rangée E/T/R (police custom
  `fnt=3`), mais l'utilisateur a préféré un texte **plus grand** repositionné
  **à droite du cochonet**, dans la zone libre à droite de l'étoile
  (`LARGEUR_ECRAN*4/5`, même hauteur que le cochonet via
  `TARGET_LAYOUT[COCHONET_INDEX][1]`) - la police custom `fnt=3` a été
  retirée (redevenue inutile) et `fnt=2` (Fontsize2) réutilisée telle quelle.
- **"CHOISIS TON MODE"** (écran de choix du continent) : remonté de `y=4/20`
  à `y=2/20`.
- **"GAME START IN" + décompte** (écran d'intro) : bloc des 3 lignes
  recentré verticalement sur l'écran - "GAME START" à `y=8/20`, "IN" pile au
  centre (`y=10/20`), le décompte à `y=12/20` (avant : `6/20`, `8/20`,
  `10/20`, décalé vers le haut de l'écran).

Méthode de vérification : script Python autonome (hors dépôt, dans le
scratchpad de session) import direct de `Scripts.init`/`Scripts.Sprites`
avec `SDL_VIDEODRIVER=dummy`, qui recrée les 7 cibles + le texte aux
nouvelles coordonnées et sauvegarde un PNG (`pygame.image.save`) - permet de
vérifier au pixel près l'absence de chevauchement sans lancer le vrai jeu
(webcam/Arduino absents de ce poste). Différent de la technique
d'exec-injection habituelle ([[feedback_headless_testing_technique]]) : ici
pas besoin de faire tourner `main_hardcore.py` lui-même, juste reproduire le
rendu des éléments concernés.

### 7. Sensibilité de la détection MediaPipe réduite
Signalé : la détection de pose (utilisée pour vérifier que le joueur reste
dans la zone de tir) détectait parfois des "corps" qui n'en étaient pas
(faux positifs). Deux correctifs dans `Scripts/opencvcam.py` (module caméra
partagé par les 3 jeux à cibles) :
- Seuils de confiance MediaPipe relevés de **0.5 à 0.7**
  (`min_pose_detection_confidence`, `min_pose_presence_confidence`,
  `min_tracking_confidence`).
- **Filtre de visibilité par point** : les 6 repères de pied (index 27 à 32,
  chevilles/talons/orteils) ne sont désormais pris en compte pour la
  décision "dans/hors zone" que si `landmark.visibility >= 0.5` chacun ; si
  aucun n'est fiable, la zone est considérée interdite (comportement
  conservateur, identique au cas "aucune pose détectée du tout"). Avant, la
  position d'un point était utilisée même quand MediaPipe n'était pas sûr de
  le voir.

**Non testé en conditions réelles** (pas de caméra sur ce poste) - à valider
sur la borne physique, et à retoucher le seuil 0.7 (à la hausse ou à la
baisse) selon ce qui est observé sur place.

### 8. Textes de post TikTok (hors code, pas dans le dépôt)
Rédaction de légendes/hashtags pour un post TikTok présentant le jeu, angle
final retenu : **refonte graphique + gameplay, premiers essais, appel aux
retours des viewers** (pas un simple teaser hardware). Texte fourni dans la
conversation Claude Code, pas encore posté, pas enregistré dans le dépôt (à
redemander si besoin - non conservé ailleurs que dans l'historique de
session).

## Session du 17-18 juillet 2026

### 1. Tout commité et poussé (9 commits par sujet)
Le vrac non commité des sessions précédentes a été trié en 9 commits
thématiques (licence, CAD/BOM matériel, calibration caméra, Round the Clock,
Quizz, Hardcore + système crédit/freeplay partagé, pays ajoutés, outils
marketing, docs) puis poussé. Au passage : identité git configurée sur ce
poste (`guiraudjb <guiraudjb@gmail.com>`), remote basculé en SSH (HTTPS sans
identifiants stockés ne fonctionnait pas). Plusieurs pièges évités en cours
de route : un dépôt git imbriqué (`ressources/Petanque-challenge-Round-the-clock/`
avait son propre `.git` pointant vers un repo GitHub séparé - `.git` retiré,
contenu vendored tel quel), 251 Mo de cache de build Defold, une vraie clé
privée RSA (`manifest.private.der`), et 9,6 Go de vidéos render exclus du
dépôt (bien trop gros, régénérables).

### 2. Dépôt GitHub renommé
`Fanny_P-tanque_World_Tour` → `Arducible_Fanny_Petanque_World_Tour` (correction
du nom du projet, cohérent avec #ARDUCIBLE partout ailleurs). Fait via un
renommage GitHub classique (historique/stars/issues conservés, redirect
automatique sur les pages du dépôt et les remotes git) plutôt qu'un nouveau
dépôt vide. **Piège** : ce redirect ne couvre PAS GitHub Pages - l'ancienne
URL (`guiraudjb.github.io/Fanny_P-tanque_World_Tour/`) renvoie un 404 pur et
simple. Nouvelle URL : `guiraudjb.github.io/Arducible_Fanny_Petanque_World_Tour/`.
Toutes les références internes (`index.html`, `robots.txt`, `sitemap.xml`,
`README.md`) mises à jour et vérifiées à la fois en local et sur le site
déployé.

### 3. Référencement Google (SEO) de `index.html`
La page n'avait **aucune structure HTML réelle** (pas de `<!doctype>`, `<html>`,
`<head>`, `<body>` - juste des balises nues) ni de `<h1>` nulle part sur toute
la page (tout partait de `<h2>`). Corrigé, plus canonical/Open
Graph/Twitter Card/JSON-LD (`schema.org/VideoGame`), `robots.txt` et
`sitemap.xml` créés (n'existaient pas). Ajout mots-clés multilingues
réfléchis (pas de bourrage) : `alternateName` JSON-LD + une phrase visible
citant les noms locaux vérifiés de la pétanque (Petanque, Petanca,
Petong/เปตอง, петанк - sourcés depuis les recherches déjà faites sur
l'écosystème pétanque, pas inventés). Volontairement **pas** de
`hreflang`/`og:locale:alternate` : la page n'existe qu'en français, en
ajouter aurait été factuellement faux.

### 4. Corrections diverses trouvées en vérifiant le contenu
- 3 mentions "111 pays" oubliées dans `index.html` lors du passage à 115
  (README avait déjà été corrigé une session plus tôt).
- `main.py`/`main_quizz.py` : écran "CHOISIS TON MODE" et bloc "GAME START
  IN" pas alignés sur les positions déjà réajustées dans `main_hardcore.py`
  - synchronisés.
- README enrichi d'un tableau récapitulatif des 4 jeux et d'une section
  "Choix du mode" qui n'était documentée nulle part ; découverte au passage
  que la narration TTS du Quizz (`assets/Sounds/QuizzTTS/`) est bien câblée
  alors que le README affirmait encore "aucun fichier audio".
- PCB détection v3 (ajout d'un connecteur JST-XH) : fichiers de commande
  JLCPCB récupérés depuis `ressources/archives/PCB pour détection/last pcb/`,
  copiés dans `hardware/pcb/`, liés depuis `index.html`/`BOM.md`.

### 5. Vérifications high-score et score Round the Clock
Revérifié (technique headless habituelle, voir plus bas) que
`save_high_score()`/`_hardcore()`/`_quizz()` ne s'exécutent bien qu'une
seule fois par partie pour les 3 jeux à score, et que le score de Round the
Clock (sans persistance, volontairement fidèle à l'original) s'accumule
correctement en session et repart bien à zéro entre deux parties. Aucun bug
trouvé cette fois - juste une re-confirmation après les changements
récents.

### 6. FreeCAD piloté en headless (nouvelle capacité, voir la skill)
Nouveaux rendus 3D (plusieurs angles) de l'articulation complète et de ses
3 plaques (`hardware/renders/articulation/`), et export des **plans cotés**
qui existaient déjà dans les `.FCStd` mais n'avaient jamais été exportés
(`hardware/plans/plaque-{sup,inf,milieu}.pdf`, liés depuis `index.html` et
`BOM.md`). Deux bugs trouvés dans les fichiers CAD sources (pas introduits
cette session) :
- Cartouches copiés-collés sans être renommés : `plaque-inf.FCStd` affichait
  "Plaque supérieure", `plaque-milieu.FCStd` affichait "Plaque inférieure" -
  **corrigés**.
- 3 cotes corrompues sur le plan de `plaque-inf` (2D references corrompues/
  pointant vers une ligne au lieu d'un cercle) - **les 3 corrigées et
  vérifiées** (session suivante) :
  - Diamètre : rattaché au cercle du 4ᵉ trou du losange central, affiche
    Ø4,5 comme les 3 autres trous identiques.
  - Les 2 cotes d'espacement X/Y : une première tentative (référencer les
    arêtes de 2 cercles directement) donnait 7,32 mm pour les deux au lieu
    des 14 mm attendus - en creusant, TechDraw mesure entre le **bord** des
    cercles référencés, pas leurs centres (confirmé par un test sur une
    paire de trous alignés : 28 mm de centre à centre, 23,5 mm mesurés =
    28 − 2×2,25 de rayon). Solution : référencer les **Vertex** du centre de
    chaque cercle plutôt que les Edge du cercle lui-même (chaque cercle a un
    vertex de centre discret dans la vue TechDraw, en plus de son edge de
    circonférence - repéré en comparant aux coordonnées du sketch). Donne
    bien 14 mm pour les deux, confirmé par export.

Toute la démarche (AppImage, Xvfb, piège `freecadcmd` qui corrompt les
fichiers avec pages TechDraw, attente réelle nécessaire après `recompute()`,
addon A2plus...) est documentée dans une skill réutilisable :
`~/.claude/skills/freecad-headless/SKILL.md` (locale à cette machine, à
recréer ailleurs si besoin - son contenu peut servir de base).

## Repères utiles pour la suite

- Numéros de gamestate : `main.py`/`main_hardcore.py` — 0 accueil, 3 choix du
  continent, 4 décompte, 1 partie, 2 fin. `main_quizz.py` — 0 accueil, 4 choix
  du continent, 5 décompte, 3 quizz, 2 fin.
- Technique de test headless utilisée tout du long : lancer une copie du
  script avec `SDL_VIDEODRIVER=dummy`/`SDL_AUDIODRIVER=dummy`, état injecté
  directement dans une copie du fichier (pas le vrai `main*.py`), captures
  via `pygame.image.save()`. Toujours restaurer `config.ini` après (des
  écrans de fin de partie y écrivent le high score).
- Détails complets, choix de conception et justifications : voir la mémoire
  Claude Code (memory) de ce projet - fichiers `project_continent_select_*`,
  `project_neon_glow_replaced`, `project_hud_palette_muted`,
  `project_score_highscore_verification`, `project_hardcore_hud_layout`,
  `project_mediapipe_sensitivity_fix`, `reference_site_and_repo_urls`,
  `reference_freecad_headless_skill`. Ce compte-rendu en est un résumé
  condensé, pensé pour être lisible sans Claude Code (autre poste, autre
  outil).
- Nouvelle URL du dépôt/site : voir section "Dépôt GitHub renommé" plus haut.

## Points de vigilance pour une prochaine session

- `index.html` (page marketing) embarque toujours "Neon Glow" en base64 pour
  le style décoratif des compteurs de stats (typo volontairement différente
  du HUD du jeu, une police vintage néon pour l'affiche) - ce n'est **pas**
  un oubli du remplacement par Alfa Slab One, juste un choix graphique
  distinct pour cette page marketing ; à ne pas "corriger" par réflexe.
- Le correctif de sensibilité MediaPipe (session du 15-16) n'a toujours pas
  été testé avec une vraie caméra sur ce poste - à vérifier en priorité sur
  la borne physique à la reprise.
- L'ancienne URL GitHub Pages (`.../Fanny_P-tanque_World_Tour/`) est morte
  (404 permanent, pas de redirect) - si elle traîne quelque part en externe
  (bio TikTok, post, favori...), il faut la mettre à jour à la main.
- Gros dossiers volontairement non versionnés (voir section "Tout est
  commité et poussé" en haut) - ne pas s'étonner de leur absence après un
  clone frais, ils sont régénérables via `ressources/utils/`.
