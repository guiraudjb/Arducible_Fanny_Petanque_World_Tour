# Fanny Pétanque World Tour

## Tapez la boule. Partez pour le tour du monde.

Posez-vous devant la borne, prenez la boule en main, et lancez. C'est ça, Fanny Pétanque World Tour : les vraies sensations de la pétanque, sur une vraie borne d'arcade — trois cibles physiques à toucher, pas un écran tactile à effleurer.

Chaque tir réussi vous fait avancer un peu plus loin sur la carte. Le décor change, l'hymne national retentit, et Fanny — votre partenaire de route — troque sa tenue pour celle du pays suivant. Un tir, un pays. 115 pays à parcourir, de la France au Japon en passant par Madagascar et les Fidji.

---

### Une vraie borne, de vraies sensations

Oubliez la manette. Ici, on joue avec de vraies boules de pétanque, sur de vraies cibles montées sur ressort. Chaque impact est encaissé, amorti, et transformé en score à l'écran. Le geste est le même que sur le boulodrome — la précision, la force, le petit ajustement du poignet au dernier moment.

### 115 pays, un seul jeu

À chaque série de tirs gagnée, le monde défile sous vos yeux. Nouveau décor, nouvel hymne, nouveau portrait de Fanny — et un petit mot d'histoire sur la pétanque locale, glissé au passage. On dit *petanca* en Espagne, *petong* en Thaïlande : le jeu se souvient de tout.

### Un arbitre numérique toujours à l'œil

Une caméra veille discrètement pendant la partie. Son seul rôle : vérifier que vous restez bien dans votre zone de tir, comme le ferait un arbitre sur un vrai terrain. Sortez de la zone, et le jeu patiente sagement que vous reveniez — jamais de triche possible.

### Les bonus du voyage

Le tour du monde laisse des souvenirs : une collection de cartes postales illustrées pour chacun des 115 pays, un jeu de cartes à l'effigie de Fanny en tenue traditionnelle, et trois petits classiques — solitaire, poker, blackjack — jouables directement dans le navigateur pour patienter entre deux parties.

---

## Sous le capot : construire sa propre borne

Vous avez aimé jouer ? Vous pouvez construire la vôtre. Fanny Pétanque World Tour est un projet **100&nbsp;% open source**, publié sous licence **Creative Commons BY&nbsp;4.0** : plans de découpe, modèles 3D, schémas électroniques et code source, tout est en libre accès — réutilisation libre, y compris commerciale, à condition de citer l'auteur.

La suite de cette page s'adresse aux makers, ingénieurs et bricoleurs curieux de savoir ce qui se cache derrière chaque tir détecté. On y descend d'un cran technique.

---

## Le laboratoire

### Architecture matérielle

Toute la borne repose sur un châssis en tôle pliée : les plis de la tôle lui donnent, à eux seuls, la rigidité nécessaire pour porter les trois articulations sans renfort supplémentaire ni surépaisseur.

Chaque cible encaisse l'impact grâce à une chaîne mécanique pensée pour absorber le choc avant qu'il n'atteigne le châssis :

- **L'axe principal** — une vis à tête creuse **M8×70** — porte l'ensemble du mécanisme et fixe l'amplitude de bascule au moment de l'impact.
- **La rotule GE8C** sert de point de pivot : elle permet au support de basculer librement dans toutes les directions autour d'un seul point fixe.
- **Le tampon en caoutchouc (polychloroprène, dureté 60 SHA)** encaisse l'essentiel du choc par compression, puis restitue l'énergie pour ramener le mécanisme en position — c'est ce mouvement de va-et-vient qui écarte puis réaligne l'aimant face au capteur, déclenchant la détection.

**Notes d'atelier — le choix de la boule :** deux alternatives à la boule en acier standard (∅70&nbsp;mm, ~680&nbsp;g) ont été testées pour un usage en intérieur. La boule souple **Al'Comm** (PVC rempli de microbilles d'acier) reprend exactement le poids et le diamètre d'une boule traditionnelle : elle s'installe sans rien changer au montage. La boule **La Schmolle** (plastique léger, 280&nbsp;g) transmet un impact nettement plus faible à l'axe — un tampon de dureté SHA inférieure au 60 standard est recommandé pour conserver une détection fiable avec ce modèle.

### Électronique

Le signal de chaque cible remonte à une carte **Pro Micro** (puce **ATmega32U4**, brochage compatible Arduino Leonardo — reconnue nativement comme un clavier USB par l'ordinateur). Le firmware embarqué est volontairement minimal : trois entrées numériques lues en boucle, retranscrites en pression/relâchement de touches via la bibliothèque `Keyboard`.

La détection elle-même repose sur un réseau de **capteurs à effet Hall** : chaque cible embarque son propre capteur magnétique, qui détecte le passage d'un aimant sans aucun contact électrique avec la boule. Le câblage suit une topologie simple et robuste : un câble réseau **RJ45** (Cat5/6) par cible ramène signal et alimentation jusqu'à la carte contrôleur, avant une liaison Micro-USB unique vers l'ordinateur.

### Logiciel & vision

Le moteur de jeu est écrit en **Python**, avec **Pygame** pour la boucle de jeu et l'affichage. L'ensemble des paramètres — résolution, plein écran, durées, bonus de temps, nombre de tirs par pays — se règle dans un unique fichier `config.ini`, sans toucher au code.

Le suivi du joueur s'appuie sur **OpenCV** et **MediaPipe Pose Landmarker** : un suivi de posture en temps réel via webcam, utilisé exclusivement pour valider la position du joueur dans sa zone de tir désignée.

Le code source complet est disponible sur un **dépôt Git public**. Sa gestion reste volontairement **manuelle** : pas de pipeline de mise à jour ou de déploiement automatisé — chaque évolution est relue et poussée à la main, au fil des sessions d'atelier.
