"""Questions de quizz du fork Fanny Pétanque World Tour Quizz.

QUIZ_QUESTIONS est parallèle à WORLD_TOUR_COUNTRIES (Scripts/dialogues.py) :
même longueur, même ordre, même index de pays (tier). Chaque élément est une
liste de 5 questions (une par cible dans main_quizz.py), chaque question un
tuple (texte, [choix_a, choix_b, choix_c], index_bonne_reponse, explication).
L'explication est le texte que Fanny affiche après le feedback (bonne/
mauvaise réponse en couleur) pour expliquer la bonne réponse, avant de
passer à la question suivante - toujours au moins une confirmation de la
valeur correcte, enrichie de la description réelle du fait quand il y en a
une (monument, second fait...), jamais une donnée inventée.

Généré par ressources/utils/build_quiz_questions.py à partir de :
- ressources/utils/quiz_country_facts.py (capitale, continent, monnaie)
- ressources/utils/quiz_petanque_researched_facts.py (faits pétanque réels
  et sourcés, recherchés sur le web pour 100/112 pays — voir
  ressources/utils/RECHERCHE_PETANQUE_PAYS.md)
- ressources/utils/quiz_monuments_facts.py (monument/site touristique/
  spécialité locale par pays, recherché pour les 112 pays — voir
  ressources/utils/RECHERCHE_MONUMENTS_SPECIALITES.md)
- ressources/utils/quiz_second_facts.py (deuxième fait notable, pour les
  12 pays sans fait pétanque sourcé)
- ressources/utils/quiz_monument_categories.py (catégorie de chaque
  monument/spécialité des questions 2 et 5, pour des distracteurs du même
  type)
- ressources/utils/quiz_pre_euro_currencies.py (monnaie nationale d'avant
  l'euro, pour les 19 pays de la zone euro)
- ressources/utils/quiz_second_monuments_facts.py (2e monument/site/
  spécialité par pays, différent de celui de la question 2 — voir
  ressources/utils/RECHERCHE_2E_MONUMENT_SPECIALITE.md)
- ressources/utils/quiz_petanque_facts_2.py (2e fait pétanque réel et
  sourcé, distinct de celui de la question 1, quand disponible — remplace
  la monnaie en question 4)
- ressources/utils/quiz_petanque_athletes.py (personnalité de pétanque
  réelle associée au pays, quand disponible — remplace le second monument
  en question 5)
- ressources/utils/quiz_petanque_facts_3.py (3e fait pétanque réel et
  sourcé, distinct des questions 1 et 4, pour 3 pays seulement — remplace
  la capitale en question 3) — ces trois derniers voir
  ressources/utils/RECHERCHE_ATHLETES_PETANQUE.md

Principe de contenu : chaque option de réponse, correcte ou non, est
toujours un vrai fait rattaché à un pays réel de la liste — les mauvaises
réponses sont uniquement de vrais faits d'AUTRES pays (jamais une donnée
inventée). Elles sont choisies en priorité dans le MÊME CONTINENT que la
bonne réponse pour rester plausibles (éviter qu'un choix soit "évidemment"
faux), et pour les questions monument/spécialité, en plus dans la MÊME
CATÉGORIE (un château face à d'autres châteaux, jamais face à un casino ou
un navire). Les répliques de Fanny (Scripts/dialogues.py) ne sont PAS
utilisées comme question de quizz.

Les 5 questions de chaque pays (maximisant la part de pétanque quand les
recherches le permettent — jusqu'à 4/5 questions pétanque pour Madagascar,
le Maroc et la Tunisie ; jusqu'à 3/5 pour les autres) :
1. Fait pétanque précis et sourcé (année de fondation de fédération,
   résultat en championnat...) si trouvé en recherche, sinon un deuxième
   fait notable (ressource, tradition...).
2. Monument, site touristique ou spécialité locale (distracteurs de même
   catégorie).
3. Un TROISIÈME fait pétanque réel, distinct des questions 1 et 4, pour
   les quelques pays qui en ont un ; sinon la capitale.
4. Un DEUXIÈME fait pétanque réel, distinct du premier, quand disponible ;
   sinon la monnaie (ou la monnaie d'avant l'euro pour les 19 pays de la
   zone euro, "l'euro" étant une réponse trop répétitive).
5. Une personnalité de pétanque réelle associée au pays (joueur/joueuse,
   ou président(e)/entraîneur(e) quand c'est la seule trouvée), quand
   disponible ; sinon un second monument/site/spécialité, différent de
   celui de la question 2 (distracteurs de même catégorie) — cette
   dernière ne dit jamais explicitement "monument" ni "spécialité".
"""

QUIZ_QUESTIONS = [
    # 0 Allemagne
    [
        ("En quelle année l'Allemagne a-t-elle remporté son tout premier titre de championne d'Europe de pétanque en triplette masculine, en battant la France en finale (à Santa Susanna, Espagne) ?", ['1996', '2015', '2025'], 2, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Allemagne (Château romantique du roi Louis II de Bavière, modèle du château de la Belle au Bois Dormant à Disneyland) ?', ['le château de Neuschwanstein', 'le château de Schönbrunn', 'le château de Caernarfon'], 0, 'La bonne réponse était le château de Neuschwanstein : Château romantique du roi Louis II de Bavière, modèle du château de la Belle au Bois Dormant à Disneyland.'),
        ("Quelle est la capitale d'Allemagne ?", ['Berlin', 'Madrid', 'Édimbourg'], 0, 'La bonne réponse était Berlin.'),
        ("En quelle année l'Allemagne a-t-elle organisé le tout premier championnat d'Europe de pétanque en triplette féminine, à Rastatt ?", ['2015', '1983', '2003'], 2, 'La bonne réponse était 2003.'),
        ("À quoi d'autre est associé Allemagne (Monument néoclassique de Berlin, ancien symbole de la division puis de la réunification allemande) ?", ['la vieille ville de Riga', 'Llanfairpwllgwyngyll', 'la porte de Brandebourg'], 2, 'La bonne réponse était la porte de Brandebourg : Monument néoclassique de Berlin, ancien symbole de la division puis de la réunification allemande.'),
    ],
    # 1 Andorre
    [
        ('En quelle année la Fédération Andorrane de Pétanque a-t-elle rejoint la FIPJP ?', ['1958', '1987', '2011'], 1, 'La bonne réponse était 1987.'),
        ('Quel monument ou quelle spécialité est associé à Andorre (Pot-au-feu traditionnel andorran (viandes, légumes, pâtes ou riz)) ?', ['le poisson cru au lait de coco', "l'escudella", 'le kimchi'], 1, "La bonne réponse était l'escudella : Pot-au-feu traditionnel andorran (viandes, légumes, pâtes ou riz)."),
        ("Quelle est la capitale d'Andorre ?", ['Prague', 'Luxembourg', 'Andorre-la-Vieille'], 2, 'La bonne réponse était Andorre-la-Vieille.'),
        ("Quelle monnaie était utilisée en Andorre avant l'euro ?", ['le mark finlandais (markka)', 'le franc français et la peseta espagnole', 'le franc monégasque'], 1, 'La bonne réponse était le franc français et la peseta espagnole.'),
        ("À quoi d'autre est associé Andorre (Siège du parlement andorran de 1702 à 2011, l'un des plus anciens parlements d'Europe, avec son « armoire aux sept clés ») ?", ['le palais grand-ducal', 'la Casa de la Vall', "le château d'Édimbourg"], 1, "La bonne réponse était la Casa de la Vall : Siège du parlement andorran de 1702 à 2011, l'un des plus anciens parlements d'Europe, avec son « armoire aux sept clés »."),
    ],
    # 2 Angleterre
    [
        ("En quelle année la série de victoires de l'Angleterre au championnat des « Home Nations » de pétanque (24 ans consécutifs) a-t-elle pris fin, battue par Jersey ?", ['2013', '2025', '1964'], 1, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Angleterre (Cercle de mégalithes préhistoriques du Wiltshire) ?', ['Stonehenge', 'le Colisée', 'les ruines de Loropéni'], 0, 'La bonne réponse était Stonehenge : Cercle de mégalithes préhistoriques du Wiltshire.'),
        ("Quelle est la capitale d'Angleterre ?", ['Lisbonne', 'Londres', 'Saint-Hélier'], 1, 'La bonne réponse était Londres.'),
        ("En quelle année l'Angleterre a-t-elle remporté l'or en tir de précision Espoirs femmes au championnat d'Europe de pétanque ?", ['2023', '2024', '2017'], 2, 'La bonne réponse était 2017.'),
        ("À quoi d'autre est associé Angleterre (Surnom de la cloche de la tour Elizabeth du Palais de Westminster à Londres) ?", ['Big Ben', 'la porte de Brandebourg', "l'Atomium"], 0, 'La bonne réponse était Big Ben : Surnom de la cloche de la tour Elizabeth du Palais de Westminster à Londres.'),
    ],
    # 3 Arménie
    [
        ('En quelle année la Fédération Arménienne de Pétanque a-t-elle été créée ?', ['2014', '2004', '2019'], 1, 'La bonne réponse était 2004.'),
        ('Quel monument ou quelle spécialité est associé à Arménie (Célèbre pour sa vue sur le mont Ararat) ?', ['Sainte-Sophie', 'le Wat Arun', 'le monastère de Khor Virap'], 2, 'La bonne réponse était le monastère de Khor Virap : Célèbre pour sa vue sur le mont Ararat.'),
        ("Quelle est la capitale d'Arménie ?", ['Kuala Lumpur', 'Naypyidaw', 'Erevan'], 2, 'La bonne réponse était Erevan.'),
        ('Quelle est la monnaie utilisée en Arménie ?', ['le dram arménien', 'la roupie pakistanaise', 'le dong'], 0, 'La bonne réponse était le dram arménien.'),
        ("À quoi d'autre est associé Arménie (Complexe monastique du XIIIe siècle, en partie taillé à même la roche, classé UNESCO) ?", ['le monastère de Guéghard', 'les grottes de Batu', 'la mosquée Badshahi'], 0, 'La bonne réponse était le monastère de Guéghard : Complexe monastique du XIIIe siècle, en partie taillé à même la roche, classé UNESCO.'),
    ],
    # 4 Autriche
    [
        ('En quelle année la fédération autrichienne de pétanque a-t-elle rejoint la FIPJP ?', ['1986', '2018', '1995'], 2, 'La bonne réponse était 1995.'),
        ("Quel monument ou quelle spécialité est associé à Autriche (Ancienne résidence d'été des Habsbourg à Vienne) ?", ['le château de Caernarfon', 'le château de Schönbrunn', 'le château de Neuschwanstein'], 1, "La bonne réponse était le château de Schönbrunn : Ancienne résidence d'été des Habsbourg à Vienne."),
        ("Quelle est la capitale d'Autriche ?", ['Bucarest', 'Vienne', 'Édimbourg'], 1, 'La bonne réponse était Vienne.'),
        ("En quelle année l'Autriche a-t-elle remporté le bronze en triplette femmes au championnat d'Europe de pétanque ?", ['2016', '2022', '2025'], 0, 'La bonne réponse était 2016.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Autriche (joueur autrichien de pétanque classé 5e au championnat d'Europe juniors) ?", ['Edward Vinke', 'Maris Newerkla', 'Zaidou Maoulida Mhamadi'], 1, "La bonne réponse était Maris Newerkla : joueur autrichien de pétanque classé 5e au championnat d'Europe juniors."),
    ],
    # 5 Belgique
    [
        ('En quelle année le Belge Claudy Weibel a-t-il été sacré champion du monde de pétanque en triplette, pour la première fois ?', ['2000', '2004', '2011'], 0, 'La bonne réponse était 2000.'),
        ("Quel monument ou quelle spécialité est associé à Belgique (Statuette bruxelloise en bronze d'un jeune garçon) ?", ['les moulins de Kinderdijk', 'le Manneken-Pis', 'le Casino de Monte-Carlo'], 1, "La bonne réponse était le Manneken-Pis : Statuette bruxelloise en bronze d'un jeune garçon."),
        ('Quelle est la capitale de Belgique ?', ['Moscou', 'Budapest', 'Bruxelles'], 2, 'La bonne réponse était Bruxelles.'),
        ("En quelle année la Belgique a-t-elle remporté l'or à l'EuroCup de pétanque, pour la première fois ?", ['2021', '2007', '2016'], 2, 'La bonne réponse était 2016.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Belgique (2 fois champion du monde de pétanque (triplette 2000, tête-à-tête 2015) et champion d'Europe de tir de précision en 2009) ?", ['Ayumi Goma', 'Diego Rizzi', 'Claudy Weibel'], 2, "La bonne réponse était Claudy Weibel : 2 fois champion du monde de pétanque (triplette 2000, tête-à-tête 2015) et champion d'Europe de tir de précision en 2009."),
    ],
    # 6 Bulgarie
    [
        ('En quelle année la Fédération Bulgare de Pétanque a-t-elle rejoint la FIPJP ?', ['2010', '2021', '1985'], 1, 'La bonne réponse était 2021.'),
        ('Quel monument ou quelle spécialité est associé à Bulgarie (Plus grand monastère orthodoxe de Bulgarie) ?', ['la Laure des Grottes de Kiev', 'le monastère de Rila', 'la Sagrada Família'], 1, 'La bonne réponse était le monastère de Rila : Plus grand monastère orthodoxe de Bulgarie.'),
        ('Quelle est la capitale de Bulgarie ?', ['Édimbourg', 'Sofia', 'Rome'], 1, 'La bonne réponse était Sofia.'),
        ("En quelle année la Bulgarie a-t-elle accueilli pour la première fois le championnat d'Europe hommes de pétanque, à Albena ?", ['2015', '2016', '2025'], 0, 'La bonne réponse était 2015.'),
        ("À quoi d'autre est associé Bulgarie (Région autour de Kazanlak, premier producteur mondial d'huile de rose) ?", ['la vallée des Roses', 'les timbres-poste saint-marinais', 'le Laulupidu'], 0, "La bonne réponse était la vallée des Roses : Région autour de Kazanlak, premier producteur mondial d'huile de rose."),
    ],
    # 7 Danemark
    [
        ("En quelle année le Danemark a-t-il remporté sa première médaille d'or en FedCup au championnat d'Europe de pétanque ?", ['2010', '1999', '2024'], 2, 'La bonne réponse était 2024.'),
        ("Quel monument ou quelle spécialité est associé à Danemark (Statue de bronze à Copenhague inspirée du conte d'Andersen) ?", ['la Petite Sirène', 'le Manneken-Pis', 'la tour Eiffel'], 0, "La bonne réponse était la Petite Sirène : Statue de bronze à Copenhague inspirée du conte d'Andersen."),
        ('Quelle est la capitale du Danemark ?', ['Copenhague', 'Madrid', 'Amsterdam'], 0, 'La bonne réponse était Copenhague.'),
        ("En quelle année le Danemark a-t-il remporté l'argent à l'EuroCup de pétanque ?", ['1998', '2025', '2003'], 0, 'La bonne réponse était 1998.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Danemark (détenteur du meilleur score de tir de précision jamais réalisé par un joueur danois de pétanque (36 points) en grand championnat) ?', ['Cesiel Domenios et Ma. Corazon Soberre', 'Lasse Dithmar', 'Charles Mbenoun'], 1, 'La bonne réponse était Lasse Dithmar : détenteur du meilleur score de tir de précision jamais réalisé par un joueur danois de pétanque (36 points) en grand championnat.'),
    ],
    # 8 Écosse
    [
        ('En quelle année la Scottish Pétanque Association a-t-elle été fondée ?', ['2015', '1990', '1985'], 2, 'La bonne réponse était 1985.'),
        ('Quel monument ou quelle spécialité est associé à Écosse (Lac écossais réputé pour sa légende du monstre « Nessie ») ?', ['les falaises de Moher', 'le Loch Ness', 'le Cervin (Matterhorn)'], 1, 'La bonne réponse était le Loch Ness : Lac écossais réputé pour sa légende du monstre « Nessie ».'),
        ("Quelle est la capitale d'Écosse ?", ['Édimbourg', 'Helsinki', 'Varsovie'], 0, 'La bonne réponse était Édimbourg.'),
        ('Quelle est la monnaie utilisée en Écosse ?', ['la hryvnia', 'la couronne norvégienne', 'la livre sterling'], 2, 'La bonne réponse était la livre sterling.'),
        ("À quoi d'autre est associé Écosse (Forteresse dominant la capitale écossaise, l'un des monuments les plus visités du Royaume-Uni) ?", ["l'Alhambra de Grenade", "le château d'Édimbourg", 'le palais grand-ducal'], 1, "La bonne réponse était le château d'Édimbourg : Forteresse dominant la capitale écossaise, l'un des monuments les plus visités du Royaume-Uni."),
    ],
    # 9 Espagne
    [
        ('En quelle année la Federación Española de Petanca a-t-elle été créée ?', ['2004', '2018', '1954'], 2, 'La bonne réponse était 1954.'),
        ('Quel monument ou quelle spécialité est associé à Espagne (Basilique inachevée de Gaudí à Barcelone) ?', ['la Sagrada Família', 'le monastère de Rila', 'la Laure des Grottes de Kiev'], 0, 'La bonne réponse était la Sagrada Família : Basilique inachevée de Gaudí à Barcelone.'),
        ("Quelle est la capitale d'Espagne ?", ['Rome', 'Madrid', 'Vilnius'], 1, 'La bonne réponse était Madrid.'),
        ("En quelle année l'Espagne a-t-elle remporté l'or en triplette féminine au championnat d'Europe de pétanque ?", ['2019', '2025', '1971'], 2, 'La bonne réponse était 1971.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Espagne (citée comme joueuse espagnole de référence, championne d'Europe de pétanque) ?", ['J-Y Robic', 'Colin Delaney', 'Sara Díaz Reyes'], 2, "La bonne réponse était Sara Díaz Reyes : citée comme joueuse espagnole de référence, championne d'Europe de pétanque."),
    ],
    # 10 Estonie
    [
        ("En quelle année l'Estonie a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", ['2023', '2024', '2019'], 0, 'La bonne réponse était 2023.'),
        ('Quel monument ou quelle spécialité est associé à Estonie (Centre médiéval fortifié classé UNESCO) ?', ['la vieille ville de Tallinn', 'le château de Prague', 'le château de Neuschwanstein'], 0, 'La bonne réponse était la vieille ville de Tallinn : Centre médiéval fortifié classé UNESCO.'),
        ("Quelle est la capitale d'Estonie ?", ['Dublin', 'Tallinn', 'Paris'], 1, 'La bonne réponse était Tallinn.'),
        ("En quelle année l'Estonie a-t-elle remporté le bronze en FedCup au championnat d'Europe de pétanque ?", ['2022', '2016', '2008'], 0, 'La bonne réponse était 2022.'),
        ("À quoi d'autre est associé Estonie (Grand festival de chant estonien, tradition inscrite au patrimoine immatériel de l'UNESCO, qui joua un rôle dans la « Révolution chantante ») ?", ["l'Icehotel de Jukkasjärvi", 'le Laulupidu', 'les timbres-poste saint-marinais'], 1, "La bonne réponse était le Laulupidu : Grand festival de chant estonien, tradition inscrite au patrimoine immatériel de l'UNESCO, qui joua un rôle dans la « Révolution chantante »."),
    ],
    # 11 Finlande
    [
        ("En quelle année la Finlande a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", ['1992', '2024', '1964'], 1, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Finlande (Tradition ancestrale de bain de vapeur finlandaise) ?', ['la vache Guernesey', 'la Jersey Royal', 'le sauna'], 2, 'La bonne réponse était le sauna : Tradition ancestrale de bain de vapeur finlandaise.'),
        ('Quelle est la capitale de Finlande ?', ['Saint-Marin', 'Berlin', 'Helsinki'], 2, 'La bonne réponse était Helsinki.'),
        ("En quelle année la Finlande a-t-elle remporté l'or en triplette hommes Espoirs au championnat d'Europe de pétanque ?", ['2019', '2007', '2008'], 0, 'La bonne réponse était 2019.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Finlande (a représenté la Finlande au championnat du monde de pétanque de Dijon, en décembre 2024) ?', ['Mikko Soikkeli', 'Abdessamad El Mankari', 'Marcel Bio, dit « Terrazini »'], 0, 'La bonne réponse était Mikko Soikkeli : a représenté la Finlande au championnat du monde de pétanque de Dijon, en décembre 2024.'),
    ],
    # 12 France
    [
        ('En quelle année la Fédération Française de Pétanque et Jeu Provençal a-t-elle été fondée à Marseille ?', ['1945', '2021', '2009'], 0, 'La bonne réponse était 1945.'),
        ('Quel monument ou quelle spécialité est associé à France (Monument emblématique de Paris construit par Gustave Eiffel) ?', ['le Monument de la Liberté', 'la Petite Sirène', 'la tour Eiffel'], 2, 'La bonne réponse était la tour Eiffel : Monument emblématique de Paris construit par Gustave Eiffel.'),
        ('Quelle est la capitale de France ?', ['Lisbonne', 'Paris', 'Cardiff'], 1, 'La bonne réponse était Paris.'),
        ("Quelle monnaie était utilisée en France avant l'euro ?", ['le franc luxembourgeois', 'le tolar slovène', 'le franc français'], 2, 'La bonne réponse était le franc français.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à France (surnommé « le Roi Quintais » ou « le Zidane de la pétanque », 14 fois champion du monde (8 fois en triplette, 4 fois au tir de précision, 2 fois comme coach)) ?', ['Marcel Bio, dit « Terrazini »', 'Andriy Kameniev', 'Philippe Quintais'], 2, 'La bonne réponse était Philippe Quintais : surnommé « le Roi Quintais » ou « le Zidane de la pétanque », 14 fois champion du monde (8 fois en triplette, 4 fois au tir de précision, 2 fois comme coach).'),
    ],
    # 13 Guernesey
    [
        ('En quelle année le premier club de pétanque de Guernesey a-t-il été fondé ?', ['2023', '1984', '2009'], 1, 'La bonne réponse était 1984.'),
        ('Quel monument ou quelle spécialité est associé à Guernesey (Race bovine réputée pour son lait très riche en crème) ?', ['la vache Guernesey', 'la Jersey Royal', 'le sauna'], 0, 'La bonne réponse était la vache Guernesey : Race bovine réputée pour son lait très riche en crème.'),
        ('Quelle est la capitale de Guernesey ?', ['Saint-Pierre-Port', 'Andorre-la-Vieille', 'Riga'], 0, 'La bonne réponse était Saint-Pierre-Port.'),
        ('Quelle est la monnaie utilisée à Guernesey ?', ['le dinar serbe', "l'euro", 'la livre sterling'], 2, 'La bonne réponse était la livre sterling.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Guernesey (vainqueur en simple du tournoi international « Guernsey Open » de pétanque en 2025) ?', ['Trinh Thi Kim Thanh', 'Tan Lay Tin', 'Andrew Bellamy-Burt'], 2, 'La bonne réponse était Andrew Bellamy-Burt : vainqueur en simple du tournoi international « Guernsey Open » de pétanque en 2025.'),
    ],
    # 14 Hongrie
    [
        ('En quelle année la fédération hongroise de pétanque a-t-elle été créée ?', ['1989', '1995', '2018'], 0, 'La bonne réponse était 1989.'),
        ('Quel monument ou quelle spécialité est associé à Hongrie (Imposant édifice néogothique sur les rives du Danube) ?', ['le Parlement de Budapest', 'la Petite Sirène', 'la tour Eiffel'], 0, 'La bonne réponse était le Parlement de Budapest : Imposant édifice néogothique sur les rives du Danube.'),
        ('Quelle est la capitale de Hongrie ?', ['Saint-Hélier', 'Budapest', 'Cardiff'], 1, 'La bonne réponse était Budapest.'),
        ("En quelle année la Hongrie a-t-elle remporté l'argent au tir de précision juniors filles au championnat d'Europe de pétanque ?", ['2019', '2025', '2022'], 2, 'La bonne réponse était 2022.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Hongrie (présidente de la Fédération hongroise de pétanque, joueuse et entraîneuse détentrice de 11 titres nationaux) ?', ['Cassie Stewart-Le Gallais', 'Ágnes Kocsis-Simon', 'Charles Mbenoun'], 1, 'La bonne réponse était Ágnes Kocsis-Simon : présidente de la Fédération hongroise de pétanque, joueuse et entraîneuse détentrice de 11 titres nationaux.'),
    ],
    # 15 Irlande
    [
        ("En quelle année l'Irish Pétanque Association a-t-elle été fondée ?", ['2016', '2013', '1990'], 2, 'La bonne réponse était 1990.'),
        ('Quel monument ou quelle spécialité est associé à Irlande (Spectaculaires falaises côtières du comté de Clare) ?', ['le lac de Bled', 'le Cervin (Matterhorn)', 'les falaises de Moher'], 2, 'La bonne réponse était les falaises de Moher : Spectaculaires falaises côtières du comté de Clare.'),
        ("Quelle est la capitale d'Irlande ?", ['Copenhague', 'Dublin', 'Vilnius'], 1, 'La bonne réponse était Dublin.'),
        ("En quelle année l'équipe Ireland A1 de pétanque est-elle restée invaincue en Celtic Challenge ?", ['2024', '2022', '2023'], 2, 'La bonne réponse était 2023.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Irlande (membre de l'équipe Ireland A1 de pétanque, restée invaincue en Celtic Challenge en 2023) ?", ['François Fara Ndiaye', 'Colin Delaney', 'Charles Mbenoun'], 1, "La bonne réponse était Colin Delaney : membre de l'équipe Ireland A1 de pétanque, restée invaincue en Celtic Challenge en 2023."),
    ],
    # 16 Italie
    [
        ("En quelle année l'Italie a-t-elle remporté son 2e titre mondial de pétanque, 45 ans après le premier ?", ['2024', '2013', '1930'], 0, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Italie (Amphithéâtre antique emblématique de Rome) ?', ['le Colisée', 'les ruines jésuites de Trinidad', 'Stonehenge'], 0, 'La bonne réponse était le Colisée : Amphithéâtre antique emblématique de Rome.'),
        ("Quelle est la capitale d'Italie ?", ['Rome', 'Tallinn', 'Budapest'], 0, 'La bonne réponse était Rome.'),
        ("En quelle année l'Italie a-t-elle remporté l'or mondial en doublette de pétanque ?", ['2025', '2021', '2022'], 2, 'La bonne réponse était 2022.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Italie (surnommé « l'Alieno » (l'extraterrestre), 46 fois champion d'Italie, 6 fois champion d'Europe et 5 fois champion du monde de pétanque) ?", ['Diego Rizzi', 'Andriy Kameniev', 'Muhamad Nuzul Azwan Ahmad Temizi'], 0, "La bonne réponse était Diego Rizzi : surnommé « l'Alieno » (l'extraterrestre), 46 fois champion d'Italie, 6 fois champion d'Europe et 5 fois champion du monde de pétanque."),
    ],
    # 17 Jersey
    [
        ('En quelle année le Jersey Petanque Club a-t-il été fondé ?', ['1986', '2021', '2011'], 0, 'La bonne réponse était 1986.'),
        ("Quel monument ou quelle spécialité est associé à Jersey (Variété de pomme de terre nouvelle originaire de l'île) ?", ['la vache Guernesey', 'la Jersey Royal', 'le sauna'], 1, "La bonne réponse était la Jersey Royal : Variété de pomme de terre nouvelle originaire de l'île."),
        ('Quelle est la capitale de Jersey ?', ['Madrid', 'Saint-Hélier', 'Berne'], 1, 'La bonne réponse était Saint-Hélier.'),
        ('Quelle est la monnaie utilisée à Jersey ?', ['la livre sterling', 'le rouble russe', "l'euro"], 0, 'La bonne réponse était la livre sterling.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Jersey (victorieuse des Island Singles Championships de pétanque 2025 (catégorie femmes), à Jersey) ?', ['Tan Lay Tin', 'Luc Cattazzo', 'Cassie Stewart-Le Gallais'], 2, 'La bonne réponse était Cassie Stewart-Le Gallais : victorieuse des Island Singles Championships de pétanque 2025 (catégorie femmes), à Jersey.'),
    ],
    # 18 Lettonie
    [
        ('En quelle année la Fédération Lettonienne de Pétanque a-t-elle été créée ?', ['1991', '2009', '1945'], 1, 'La bonne réponse était 2009.'),
        ("Quel monument ou quelle spécialité est associé à Lettonie (Colonne de granit à Riga, symbole de l'indépendance lettone) ?", ['le Monument de la Liberté', 'la tour Eiffel', 'le Casino de Monte-Carlo'], 0, "La bonne réponse était le Monument de la Liberté : Colonne de granit à Riga, symbole de l'indépendance lettone."),
        ('Quelle est la capitale de Lettonie ?', ['Riga', 'Kiev', 'Berlin'], 0, 'La bonne réponse était Riga.'),
        ("Quelle monnaie était utilisée en Lettonie avant l'euro ?", ['le mark finlandais (markka)', 'le lats letton', 'la couronne estonienne (kroon)'], 1, 'La bonne réponse était le lats letton.'),
        ("À quoi d'autre est associé Lettonie (Quartier classé UNESCO, réputé pour sa densité de bâtiments Art nouveau) ?", ['le Grand Prix de Monaco', 'la vieille ville de Riga', 'Big Ben'], 1, 'La bonne réponse était la vieille ville de Riga : Quartier classé UNESCO, réputé pour sa densité de bâtiments Art nouveau.'),
    ],
    # 19 Lituanie
    [
        ("En quelle année la Lituanie a-t-elle remporté le bronze en doublette femmes au championnat d'Europe de pétanque, à 's-Hertogenbosch (Pays-Bas) ?", ['1986', '2019', '2024'], 2, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Lituanie (Forteresse médiévale de brique rouge sur une île du lac Galvė) ?', ['la vieille ville de Tallinn', 'le château de Trakai', 'le château du Wawel'], 1, 'La bonne réponse était le château de Trakai : Forteresse médiévale de brique rouge sur une île du lac Galvė.'),
        ('Quelle est la capitale de Lituanie ?', ['Vilnius', 'Dublin', 'Bratislava'], 0, 'La bonne réponse était Vilnius.'),
        ("Quelle monnaie était utilisée en Lituanie avant l'euro ?", ['la couronne slovaque', 'le litas lituanien', 'le franc monégasque'], 1, 'La bonne réponse était le litas lituanien.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Lituanie (champion de Lituanie de pétanque en simple hommes) ?', ['Abdessamad El Mankari', 'Nerijus Kukcinavičius', 'Muhamad Nuzul Azwan Ahmad Temizi'], 1, 'La bonne réponse était Nerijus Kukcinavičius : champion de Lituanie de pétanque en simple hommes.'),
    ],
    # 20 Luxembourg
    [
        ('En quelle année la Fédération Luxembourgeoise de Boules et de Pétanque a-t-elle été fondée ?', ['1959', '2005', '1990'], 0, 'La bonne réponse était 1959.'),
        ('Quel monument ou quelle spécialité est associé à Luxembourg (Galeries souterraines fortifiées creusées dans le rocher) ?', ['la vieille ville de Tallinn', 'les Casemates du Bock', 'la forteresse de Belgrade (Kalemegdan)'], 1, 'La bonne réponse était les Casemates du Bock : Galeries souterraines fortifiées creusées dans le rocher.'),
        ('Quelle est la capitale du Luxembourg ?', ['Berlin', 'Luxembourg', 'Andorre-la-Vieille'], 1, 'La bonne réponse était Luxembourg.'),
        ("En quelle année le Luxembourg a-t-il remporté l'argent en junior mixte au championnat d'Europe de pétanque ?", ['2014', '2007', '2023'], 0, 'La bonne réponse était 2014.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Luxembourg (joueur luxembourgeois cité parmi les figures notables de la pétanque au Luxembourg) ?', ['Amil Cordova', 'Luc Cattazzo', 'Toma Wai'], 1, 'La bonne réponse était Luc Cattazzo : joueur luxembourgeois cité parmi les figures notables de la pétanque au Luxembourg.'),
    ],
    # 21 Monaco
    [
        ('En quelle année Monaco a-t-il participé à la fondation de la FIPJP, à Marseille ?', ['1992', '1958', '2024'], 1, 'La bonne réponse était 1958.'),
        ('Quel monument ou quelle spécialité est associé à Monaco (Célèbre casino et symbole du luxe monégasque) ?', ['le Manneken-Pis', 'le Casino de Monte-Carlo', 'les moulins de Kinderdijk'], 1, 'La bonne réponse était le Casino de Monte-Carlo : Célèbre casino et symbole du luxe monégasque.'),
        ('Quelle est la capitale de Monaco ?', ['Saint-Hélier', 'Budapest', 'Monaco'], 2, 'La bonne réponse était Monaco.'),
        ("En quelle année Monaco a-t-il remporté l'or à l'EuroCup de pétanque ?", ['2011', '1984', '2007'], 0, 'La bonne réponse était 2011.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Monaco (championnes d'Europe de pétanque en doublette féminine en 2022, à 's-Hertogenbosch (Pays-Bas)) ?", ['Tofata Tautapu', 'Myriam Chambeiron et Laura Vierjon', 'Katarzyna Błasiak'], 1, "La bonne réponse était Myriam Chambeiron et Laura Vierjon : championnes d'Europe de pétanque en doublette féminine en 2022, à 's-Hertogenbosch (Pays-Bas)."),
    ],
    # 22 Norvège
    [
        ('En quelle année la fédération norvégienne de pétanque a-t-elle été fondée ?', ['2006', '2013', '1984'], 2, 'La bonne réponse était 1984.'),
        ('Quel monument ou quelle spécialité est associé à Norvège (Fjord classé UNESCO entouré de falaises et de cascades) ?', ['le Geirangerfjord', 'le Cervin (Matterhorn)', 'le Loch Ness'], 0, 'La bonne réponse était le Geirangerfjord : Fjord classé UNESCO entouré de falaises et de cascades.'),
        ('Quelle est la capitale de Norvège ?', ['Tallinn', 'Oslo', 'Riga'], 1, 'La bonne réponse était Oslo.'),
        ("En quelle année la Norvège a-t-elle remporté l'or en FedCup au championnat d'Europe de pétanque ?", ['2022', '2016', '2024'], 0, 'La bonne réponse était 2022.'),
        ("À quoi d'autre est associé Norvège (Églises en bois debout médiévales, comme celle d'Urnes, classée UNESCO) ?", ['le Mont-Saint-Michel', 'les stavkirker', 'la tour de Pise'], 1, "La bonne réponse était les stavkirker : Églises en bois debout médiévales, comme celle d'Urnes, classée UNESCO."),
    ],
    # 23 Pays-Bas
    [
        ('En quelle année la fédération néerlandaise de pétanque (NJBB) a-t-elle été fondée ?', ['1972', '2004', '2025'], 0, 'La bonne réponse était 1972.'),
        ('Quel monument ou quelle spécialité est associé à Pays-Bas (19 moulins historiques du XVIIIe siècle utilisés pour drainer les polders) ?', ['la Petite Sirène', 'le Manneken-Pis', 'les moulins de Kinderdijk'], 2, 'La bonne réponse était les moulins de Kinderdijk : 19 moulins historiques du XVIIIe siècle utilisés pour drainer les polders.'),
        ('Quelle est la capitale des Pays-Bas ?', ['Riga', 'Vilnius', 'Amsterdam'], 2, 'La bonne réponse était Amsterdam.'),
        ("En quelle année les Pays-Bas ont-ils remporté l'or au tir de précision femmes au championnat d'Europe de pétanque ?", ['2016', '2007', '2023'], 1, 'La bonne réponse était 2007.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Pays-Bas (champion national néerlandais de pétanque, plusieurs fois sélectionné en équipe des Pays-Bas au championnat d'Europe) ?", ['José Manuel Marcano', 'Edward Vinke', 'Claudy Weibel'], 1, "La bonne réponse était Edward Vinke : champion national néerlandais de pétanque, plusieurs fois sélectionné en équipe des Pays-Bas au championnat d'Europe."),
    ],
    # 24 Pays de Galles
    [
        ('En quelle année la Welsh Pétanque Association a-t-elle été fondée ?', ['1984', '2004', '1954'], 1, 'La bonne réponse était 2004.'),
        ("Quel monument ou quelle spécialité est associé à Pays de Galles (Forteresse médiévale, lieu d'investiture des princes de Galles) ?", ['le château de Caernarfon', 'le château de Bratislava', 'le château de Schönbrunn'], 0, "La bonne réponse était le château de Caernarfon : Forteresse médiévale, lieu d'investiture des princes de Galles."),
        ('Quelle est la capitale du Pays de Galles ?', ['Cardiff', 'Luxembourg', 'Helsinki'], 0, 'La bonne réponse était Cardiff.'),
        ('Quelle est la monnaie utilisée au Pays de Galles ?', ['la couronne danoise', "l'euro", 'la livre sterling'], 2, 'La bonne réponse était la livre sterling.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Pays de Galles (champion national de pétanque du Pays de Galles) ?', ['Salif Kourouma', 'J-Y Robic', 'Tsai Chih-Hsuan'], 1, 'La bonne réponse était J-Y Robic : champion national de pétanque du Pays de Galles.'),
    ],
    # 25 Pologne
    [
        ("En quelle année le Polonais Paweł Pieprzyk a-t-il remporté l'or au tir de précision juniors au championnat d'Europe de pétanque, à Gand (Belgique) ?", ['2012', '2009', '2025'], 0, 'La bonne réponse était 2012.'),
        ('Quel monument ou quelle spécialité est associé à Pologne (Résidence historique des rois de Pologne à Cracovie) ?', ['la tour de Belém', 'le château du Wawel', 'le château de Schönbrunn'], 1, 'La bonne réponse était le château du Wawel : Résidence historique des rois de Pologne à Cracovie.'),
        ('Quelle est la capitale de Pologne ?', ['Kiev', 'Berne', 'Varsovie'], 2, 'La bonne réponse était Varsovie.'),
        ("En quelle année le Polonais Jędrzej Śliż a-t-il remporté le bronze au tir de précision juniors au championnat d'Europe de pétanque, à Brno ?", ['2003', '2021', '2017'], 0, 'La bonne réponse était 2003.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Pologne (joueuse polonaise de pétanque, plusieurs fois médaillée internationale) ?', ['Melisa Polito et Renato Donoso', 'Katarzyna Błasiak', 'Nerijus Kukcinavičius'], 1, 'La bonne réponse était Katarzyna Błasiak : joueuse polonaise de pétanque, plusieurs fois médaillée internationale.'),
    ],
    # 26 Portugal
    [
        ('En quelle année la Federação Portuguesa de Petanca a-t-elle été fondée ?', ['2005', '2019', '1992'], 2, 'La bonne réponse était 1992.'),
        ('Quel monument ou quelle spécialité est associé à Portugal (Tour fortifiée du XVIe siècle à Lisbonne) ?', ['le château de Trakai', 'la tour de Belém', 'le château de Bratislava'], 1, 'La bonne réponse était la tour de Belém : Tour fortifiée du XVIe siècle à Lisbonne.'),
        ('Quelle est la capitale du Portugal ?', ['Lisbonne', 'Bucarest', 'Budapest'], 0, 'La bonne réponse était Lisbonne.'),
        ("En quelle année le Portugal a-t-il remporté l'argent au tir de précision hommes au championnat d'Europe de pétanque ?", ['2025', '2011', '2009'], 1, 'La bonne réponse était 2011.'),
        ("À quoi d'autre est associé Portugal (Palais romantique coloré perché sur les collines de Sintra, classé UNESCO) ?", ['le château de Spiš', 'la Casa de la Vall', 'le palais de Pena'], 2, 'La bonne réponse était le palais de Pena : Palais romantique coloré perché sur les collines de Sintra, classé UNESCO.'),
    ],
    # 27 Roumanie
    [
        ('En quelle année la pétanque a-t-elle été introduite en Roumanie par Titus Marin ?', ['2024', '1958', '2006'], 2, 'La bonne réponse était 2006.'),
        ('Quel monument ou quelle spécialité est associé à Roumanie (Forteresse des Carpates associée à la légende de Dracula) ?', ['le château de Bran', 'le château de Bratislava', 'le château de Schönbrunn'], 0, 'La bonne réponse était le château de Bran : Forteresse des Carpates associée à la légende de Dracula.'),
        ('Quelle est la capitale de Roumanie ?', ['Moscou', 'Bucarest', 'Prague'], 1, 'La bonne réponse était Bucarest.'),
        ('Quelle est la monnaie utilisée en Roumanie ?', ["l'euro", 'la couronne danoise', 'le leu roumain'], 2, 'La bonne réponse était le leu roumain.'),
        ("À quoi d'autre est associé Roumanie (Bâtiment administratif civil le plus lourd et l'un des plus vastes du monde, à Bucarest) ?", ["l'Atomium", 'le palais du Parlement', 'Big Ben'], 1, "La bonne réponse était le palais du Parlement : Bâtiment administratif civil le plus lourd et l'un des plus vastes du monde, à Bucarest."),
    ],
    # 28 Russie
    [
        ('En quelle année la Fédération de pétanque de Russie, sous sa forme actuelle, a-t-elle été créée ?', ['2018', '2025', '2013'], 0, 'La bonne réponse était 2018.'),
        ('Quel monument ou quelle spécialité est associé à Russie (Ancienne citadelle fortifiée de Moscou) ?', ['le Kremlin', 'la vieille ville de Tallinn', 'la forteresse de Belgrade (Kalemegdan)'], 0, 'La bonne réponse était le Kremlin : Ancienne citadelle fortifiée de Moscou.'),
        ('Quelle est la capitale de Russie ?', ['Édimbourg', 'Paris', 'Moscou'], 2, 'La bonne réponse était Moscou.'),
        ("En quelle année la Russie a-t-elle remporté le bronze en Vétérans au championnat d'Europe de pétanque, à Monaco ?", ['2025', '2009', '2016'], 2, 'La bonne réponse était 2016.'),
        ("À quoi d'autre est associé Russie (Édifice orthodoxe aux bulbes colorés sur la place Rouge à Moscou) ?", ['la cathédrale Saint-Basile-le-Bienheureux', 'les stavkirker', 'le monastère de Studenica'], 0, 'La bonne réponse était la cathédrale Saint-Basile-le-Bienheureux : Édifice orthodoxe aux bulbes colorés sur la place Rouge à Moscou.'),
    ],
    # 29 Saint-Marin
    [
        ('Quel fait notable est associé à Saint-Marin (Saint-Marin est réputé dans le monde entier pour ses timbres-poste, très prisés des philatélistes) ?', ['le lapis-lazuli', 'les timbres-poste', 'le cuivre'], 1, 'La bonne réponse était les timbres-poste : Saint-Marin est réputé dans le monde entier pour ses timbres-poste, très prisés des philatélistes.'),
        ('Quel monument ou quelle spécialité est associé à Saint-Marin (Trois forteresses médiévales, symbole national de Saint-Marin) ?', ['les Tre Torri du Mont Titano', 'la tour de Belém', 'le château de Prague'], 0, 'La bonne réponse était les Tre Torri du Mont Titano : Trois forteresses médiévales, symbole national de Saint-Marin.'),
        ('Quelle est la capitale de Saint-Marin ?', ['Saint-Marin', 'Riga', 'Amsterdam'], 0, 'La bonne réponse était Saint-Marin.'),
        ("Quelle monnaie était utilisée à Saint-Marin avant l'euro ?", ['le tolar slovène', 'la lire sammarinaise', 'le franc français et la peseta espagnole'], 1, 'La bonne réponse était la lire sammarinaise.'),
        ("À quoi d'autre est associé Saint-Marin (Production philatélique prisée des collectionneurs du monde entier, importante source de revenus du pays) ?", ["l'Icehotel de Jukkasjärvi", 'la vallée des Roses', 'les timbres-poste saint-marinais'], 2, 'La bonne réponse était les timbres-poste saint-marinais : Production philatélique prisée des collectionneurs du monde entier, importante source de revenus du pays.'),
    ],
    # 30 Serbie
    [
        ('En quelle année a eu lieu le tout premier championnat national serbe de pétanque ?', ['2025', '2006', '2024'], 0, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Serbie (Citadelle historique au confluent de la Save et du Danube) ?', ['la forteresse de Belgrade (Kalemegdan)', 'les Casemates du Bock', 'la vieille ville de Tallinn'], 0, 'La bonne réponse était la forteresse de Belgrade (Kalemegdan) : Citadelle historique au confluent de la Save et du Danube.'),
        ('Quelle est la capitale de Serbie ?', ['Paris', 'Belgrade', 'Kiev'], 1, 'La bonne réponse était Belgrade.'),
        ('Quelle est la monnaie utilisée en Serbie ?', ['le dinar serbe', "l'euro", 'la couronne danoise'], 0, 'La bonne réponse était le dinar serbe.'),
        ("À quoi d'autre est associé Serbie (Monastère orthodoxe médiéval classé UNESCO) ?", ['le monastère de Studenica', 'les stavkirker', 'le Mont-Saint-Michel'], 0, 'La bonne réponse était le monastère de Studenica : Monastère orthodoxe médiéval classé UNESCO.'),
    ],
    # 31 Slovaquie
    [
        ('En quelle année la fédération slovaque de pétanque a-t-elle été fondée ?', ['1994', '2023', '2022'], 0, 'La bonne réponse était 1994.'),
        ('Quel monument ou quelle spécialité est associé à Slovaquie (Forteresse aux quatre tours dominant le Danube) ?', ['le château de Neuschwanstein', 'le château de Bratislava', 'le château de Trakai'], 1, 'La bonne réponse était le château de Bratislava : Forteresse aux quatre tours dominant le Danube.'),
        ('Quelle est la capitale de Slovaquie ?', ['Sofia', 'Riga', 'Bratislava'], 2, 'La bonne réponse était Bratislava.'),
        ("En quelle année la Slovaquie a-t-elle remporté le bronze au tir de précision hommes au championnat d'Europe de pétanque, à Albena ?", ['2021', '2015', '2016'], 1, 'La bonne réponse était 2015.'),
        ("À quoi d'autre est associé Slovaquie (L'un des plus grands complexes castraux d'Europe centrale, classé UNESCO) ?", ['le château de Spiš', "le château d'Édimbourg", 'le château de Mont Orgueil'], 0, "La bonne réponse était le château de Spiš : L'un des plus grands complexes castraux d'Europe centrale, classé UNESCO."),
    ],
    # 32 Slovénie
    [
        ('En quelle année la fédération slovène de pétanque a-t-elle été fondée ?', ['2010', '1958', '1999'], 2, 'La bonne réponse était 1999.'),
        ('Quel monument ou quelle spécialité est associé à Slovénie (Lac alpin avec sa petite île et son château médiéval) ?', ['le Geirangerfjord', 'le lac de Bled', 'le Loch Ness'], 1, 'La bonne réponse était le lac de Bled : Lac alpin avec sa petite île et son château médiéval.'),
        ('Quelle est la capitale de Slovénie ?', ['Rome', 'Bucarest', 'Ljubljana'], 2, 'La bonne réponse était Ljubljana.'),
        ("En quelle année la Slovénie a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", ['2022', '2023', '2015'], 0, 'La bonne réponse était 2022.'),
        ("À quoi d'autre est associé Slovénie (L'un des plus grands réseaux de grottes karstiques d'Europe, visitées en petit train depuis 1872) ?", ['le Jungfraujoch', 'le parc floral de Keukenhof', 'les grottes de Postojna'], 2, "La bonne réponse était les grottes de Postojna : L'un des plus grands réseaux de grottes karstiques d'Europe, visitées en petit train depuis 1872."),
    ],
    # 33 Suède
    [
        ("En quelle année le Suédois Ivar Liljegren a-t-il été vice-champion d'Europe de pétanque en tête-à-tête, à Martigny (Suisse) ?", ['2022', '1987', '2024'], 2, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Suède (Navire de guerre suédois du XVIIe siècle, coulé puis conservé au musée de Stockholm) ?', ['le sauna', 'la vache Guernesey', 'le Vasa'], 2, 'La bonne réponse était le Vasa : Navire de guerre suédois du XVIIe siècle, coulé puis conservé au musée de Stockholm.'),
        ('Quelle est la capitale de Suède ?', ['Madrid', 'Stockholm', 'Budapest'], 1, 'La bonne réponse était Stockholm.'),
        ("En quelle année la Suède a-t-elle remporté l'or en triplette femmes au championnat d'Europe de pétanque ?", ['2011', '2022', '2007'], 2, 'La bonne réponse était 2007.'),
        ("À quoi d'autre est associé Suède (Premier hôtel de glace au monde, reconstruit chaque hiver) ?", ['les mines de sel de Wieliczka', 'la vallée des Roses', "l'Icehotel de Jukkasjärvi"], 2, "La bonne réponse était l'Icehotel de Jukkasjärvi : Premier hôtel de glace au monde, reconstruit chaque hiver."),
    ],
    # 34 Suisse
    [
        ('En quelle année le Suisse Maïky Molinas a-t-il été sacré champion du monde de pétanque en tête-à-tête ?', ['2019', '2006', '2012'], 0, 'La bonne réponse était 2019.'),
        ('Quel monument ou quelle spécialité est associé à Suisse (Montagne emblématique des Alpes suisses près de Zermatt) ?', ['le lac de Bled', 'le Cervin (Matterhorn)', 'le Loch Ness'], 1, 'La bonne réponse était le Cervin (Matterhorn) : Montagne emblématique des Alpes suisses près de Zermatt.'),
        ('Quelle est la capitale de Suisse ?', ['Oslo', 'Berne', 'Sofia'], 1, 'La bonne réponse était Berne.'),
        ('En quelle année la Suissesse Sylviane Métairon a-t-elle été sacrée championne du monde féminine de pétanque en tête-à-tête ?', ['2025', '2017', '2020'], 2, 'La bonne réponse était 2020.'),
        ("À quoi d'autre est associé Suisse (« Top of Europe », plus haute gare ferroviaire d'Europe, dans les Alpes bernoises) ?", ['le parc floral de Keukenhof', 'les grottes de Postojna', 'le Jungfraujoch'], 2, "La bonne réponse était le Jungfraujoch : « Top of Europe », plus haute gare ferroviaire d'Europe, dans les Alpes bernoises."),
    ],
    # 35 Tchéquie
    [
        ("En quelle année l'équipe féminine tchèque a-t-elle remporté l'argent au championnat d'Europe de pétanque, à Ankara (Turquie) ?", ['1990', '1989', '2007'], 2, 'La bonne réponse était 2007.'),
        ('Quel monument ou quelle spécialité est associé à Tchéquie (Plus vaste complexe castral ancien au monde) ?', ['les Casemates du Bock', 'le Kremlin', 'le château de Prague'], 2, 'La bonne réponse était le château de Prague : Plus vaste complexe castral ancien au monde.'),
        ('Quelle est la capitale de Tchéquie ?', ['Prague', 'Moscou', 'Berne'], 0, 'La bonne réponse était Prague.'),
        ("En quelle année la Tchéquie a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", ['2021', '2025', '2007'], 0, 'La bonne réponse était 2021.'),
        ("À quoi d'autre est associé Tchéquie (Installée en 1410, la plus ancienne horloge astronomique encore en fonctionnement) ?", ['les bains Széchenyi', 'le palais du Parlement', "l'horloge astronomique de Prague"], 2, "La bonne réponse était l'horloge astronomique de Prague : Installée en 1410, la plus ancienne horloge astronomique encore en fonctionnement."),
    ],
    # 36 Turquie
    [
        ('En quelle année la pétanque a-t-elle été intégrée à la fédération turque de Bocce, Bowling et Fléchettes ?', ['2015', '2006', '2025'], 1, 'La bonne réponse était 2006.'),
        ('Quel monument ou quelle spécialité est associé à Turquie (Ancienne basilique byzantine puis mosquée ottomane à Istanbul) ?', ['Sainte-Sophie', 'la mosquée Sultan Omar Ali Saifuddien', 'le That Luang'], 0, 'La bonne réponse était Sainte-Sophie : Ancienne basilique byzantine puis mosquée ottomane à Istanbul.'),
        ('Quelle est la capitale de Turquie ?', ['Katmandou', 'Ankara', 'Vientiane'], 1, 'La bonne réponse était Ankara.'),
        ('En quelle année la Turquie a-t-elle accueilli le championnat du monde féminin de pétanque, pour la première fois ?', ['1983', '2008', '2025'], 1, 'La bonne réponse était 2008.'),
        ("À quoi d'autre est associé Turquie (Vasques et terrasses de calcaire blanc formées par des sources chaudes, site UNESCO en Anatolie) ?", ['Pamukkale', 'la mer Morte', 'les Sundarbans'], 0, 'La bonne réponse était Pamukkale : Vasques et terrasses de calcaire blanc formées par des sources chaudes, site UNESCO en Anatolie.'),
    ],
    # 37 Ukraine
    [
        ('En quelle année la Fédération ukrainienne de pétanque a-t-elle été cofondée par Dmytro Bugaï ?', ['2019', '2025', '2004'], 2, 'La bonne réponse était 2004.'),
        ('Quel monument ou quelle spécialité est associé à Ukraine (Monastère orthodoxe aux coupoles dorées) ?', ['la Laure des Grottes de Kiev', 'la Sagrada Família', 'le monastère de Rila'], 0, 'La bonne réponse était la Laure des Grottes de Kiev : Monastère orthodoxe aux coupoles dorées.'),
        ("Quelle est la capitale d'Ukraine ?", ['Oslo', 'Kiev', 'Bratislava'], 1, 'La bonne réponse était Kiev.'),
        ('Quelle est la monnaie utilisée en Ukraine ?', ['le lev bulgare', 'la hryvnia', "l'euro"], 1, 'La bonne réponse était la hryvnia.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Ukraine (champion national ukrainien de pétanque (Kharkiv)) ?', ['Florence Kanzié', 'Andriy Kameniev', 'Marcel Bio, dit « Terrazini »'], 1, 'La bonne réponse était Andriy Kameniev : champion national ukrainien de pétanque (Kharkiv).'),
    ],
    # 38 Algérie
    [
        ("En quelle année l'Algérie a-t-elle remporté son unique titre de championne du monde de pétanque en triplette, à Genève (Suisse) ?", ['1964', '1991', '1955'], 0, 'La bonne réponse était 1964.'),
        ("Quel monument ou quelle spécialité est associé à Algérie (Quartier historique fortifié surplombant la baie d'Alger) ?", ['le palais royal de Foumban', "la Casbah d'Alger", 'la médina de Fès'], 1, "La bonne réponse était la Casbah d'Alger : Quartier historique fortifié surplombant la baie d'Alger."),
        ("Quelle est la capitale d'Algérie ?", ['Alger', 'Kampala', 'Lusaka'], 0, 'La bonne réponse était Alger.'),
        ("En quelle année l'Algérie a-t-elle remporté le bronze en triplette hommes au championnat d'Afrique de pétanque ?", ['2021', '2025', '2008'], 0, 'La bonne réponse était 2021.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Algérie (médaillé d'argent au tir de précision au championnat d'Afrique de pétanque en 2019) ?", ['Katarzyna Błasiak', 'Hmida Zerrouk', 'Juan Moreno'], 1, "La bonne réponse était Hmida Zerrouk : médaillé d'argent au tir de précision au championnat d'Afrique de pétanque en 2019."),
    ],
    # 39 Bénin
    [
        ("En quelle année le Bénin a-t-il accueilli les championnats du monde de pétanque à Cotonou, où l'équipe béninoise est devenue championne du monde en doublette mixte ?", ['2023', '2024', '1994'], 0, 'La bonne réponse était 2023.'),
        ('Quel monument ou quelle spécialité est associé à Bénin (Palais en terre des rois du royaume du Dahomey) ?', ['la médina de Fès', "la Casbah d'Alger", "les palais royaux d'Abomey"], 2, "La bonne réponse était les palais royaux d'Abomey : Palais en terre des rois du royaume du Dahomey."),
        ('Quelle est la capitale du Bénin ?', ['Yaoundé', 'Kinshasa', 'Porto-Novo'], 2, 'La bonne réponse était Porto-Novo.'),
        ("En quelle année le Bénin a-t-il remporté l'argent en triplette hommes au championnat d'Afrique de pétanque, pour la première fois ?", ['2007', '2015', '1998'], 0, 'La bonne réponse était 2007.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Bénin (capitaine de l'équipe nationale et champion d'Afrique de tir de précision de pétanque en 2019) ?", ['Tan Lay Tin', 'J-Y Robic', 'Marcel Bio, dit « Terrazini »'], 2, "La bonne réponse était Marcel Bio, dit « Terrazini » : capitaine de l'équipe nationale et champion d'Afrique de tir de précision de pétanque en 2019."),
    ],
    # 40 Burkina Faso
    [
        ("En quelle année le Burkina Faso est-il devenu le tout premier champion d'Afrique de pétanque en triplette hommes, à Cotonou ?", ['2004', '2007', '2024'], 1, 'La bonne réponse était 2007.'),
        ("Quel monument ou quelle spécialité est associé à Burkina Faso (Forteresse en pierre liée au commerce transsaharien de l'or) ?", ['les ruines de Loropéni', 'les pyramides de Gizeh', 'Leptis Magna'], 0, "La bonne réponse était les ruines de Loropéni : Forteresse en pierre liée au commerce transsaharien de l'or."),
        ('Quelle est la capitale du Burkina Faso ?', ['Ouagadougou', 'Nouakchott', 'Port-Louis'], 0, 'La bonne réponse était Ouagadougou.'),
        ('En quelle année le Burkina Faso a-t-il remporté le bronze au tir de précision par équipe au championnat du monde de pétanque, à Dakar ?', ['2008', '2025', '2014'], 0, 'La bonne réponse était 2008.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Burkina Faso (médaillée de bronze au tir de précision femmes au championnat d'Afrique de pétanque en 2024) ?", ['Edward Vinke', 'Charles Mbenoun', 'Florence Kanzié'], 2, "La bonne réponse était Florence Kanzié : médaillée de bronze au tir de précision femmes au championnat d'Afrique de pétanque en 2024."),
    ],
    # 41 Cameroun
    [
        ("En quelle année le Cameroun a-t-il remporté sa première médaille de bronze en triplette hommes au championnat d'Afrique de pétanque ?", ['2011', '2002', '2025'], 0, 'La bonne réponse était 2011.'),
        ('Quel monument ou quelle spécialité est associé à Cameroun (Siège du royaume Bamoun, construit en 1917) ?', ["les palais royaux d'Abomey", 'la médina de Fès', 'le palais royal de Foumban'], 2, 'La bonne réponse était le palais royal de Foumban : Siège du royaume Bamoun, construit en 1917.'),
        ('Quelle est la capitale du Cameroun ?', ['Ouagadougou', 'Yaoundé', 'Port-Louis'], 1, 'La bonne réponse était Yaoundé.'),
        ("En quelle année le Cameroun a-t-il remporté l'argent en triplette hommes au championnat d'Afrique de pétanque ?", ['2015', '2025', '2022'], 0, 'La bonne réponse était 2015.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Cameroun (médaillé d'argent au tir de précision au championnat d'Afrique de pétanque en 2024) ?", ['Charles Mbenoun', 'Mikko Soikkeli', 'Delys Brady'], 0, "La bonne réponse était Charles Mbenoun : médaillé d'argent au tir de précision au championnat d'Afrique de pétanque en 2024."),
    ],
    # 42 Comores
    [
        ('En quelle année la Fédération Comorienne de Pétanque a-t-elle rejoint la FIPJP ?', ['2025', '1998', '1992'], 1, 'La bonne réponse était 1998.'),
        ("Quel monument ou quelle spécialité est associé à Comores (Volcan actif de Grande Comore à l'un des plus grands cratères du monde) ?", ['le parc national de la Lopé', 'le Karthala', 'le lac Assal'], 1, "La bonne réponse était le Karthala : Volcan actif de Grande Comore à l'un des plus grands cratères du monde."),
        ('Quelle est la capitale des Comores ?', ['Kinshasa', 'Port-Louis', 'Moroni'], 2, 'La bonne réponse était Moroni.'),
        ('En quelle année les Comores ont-ils terminé 5e au championnat du monde de pétanque en triplette, à Cotonou (Bénin) ?', ['2016', '2023', '2015'], 1, 'La bonne réponse était 2023.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Comores (médaillé d'argent en tête-à-tête au championnat d'Afrique de pétanque en 2025, lors de la toute première finale de l'histoire des Comores dans cette compétition) ?", ['Zaidou Maoulida Mhamadi', 'Sara Díaz Reyes', 'Colin Delaney'], 0, "La bonne réponse était Zaidou Maoulida Mhamadi : médaillé d'argent en tête-à-tête au championnat d'Afrique de pétanque en 2025, lors de la toute première finale de l'histoire des Comores dans cette compétition."),
    ],
    # 43 Congo
    [
        ("En quelle année le Congolais Galy Chabrol Binguila a-t-il remporté l'or au tir de précision au championnat d'Afrique de pétanque ?", ['2013', '2025', '2015'], 2, 'La bonne réponse était 2015.'),
        ("Quel monument ou quelle spécialité est associé à Congo (L'un des plus anciens parcs d'Afrique, réputé pour ses gorilles) ?", ["le parc national d'Odzala-Kokoua", 'le parc national impénétrable de Bwindi', 'la Vallée de Mai'], 0, "La bonne réponse était le parc national d'Odzala-Kokoua : L'un des plus anciens parcs d'Afrique, réputé pour ses gorilles."),
        ('Quelle est la capitale du Congo ?', ['Dakar', 'Brazzaville', 'Kampala'], 1, 'La bonne réponse était Brazzaville.'),
        ("En quelle année le Congo a-t-il remporté l'or à la Coupe des nations hommes au championnat d'Afrique de pétanque, à Marrakech ?", ['2024', '2025', '2022'], 0, 'La bonne réponse était 2024.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Congo (membre de l'équipe congolaise médaillée d'argent en triplette hommes au championnat d'Afrique de pétanque en 2025) ?", ['Ayumi Goma', 'Batambika Verdorold', 'Katarzyna Błasiak'], 1, "La bonne réponse était Batambika Verdorold : membre de l'équipe congolaise médaillée d'argent en triplette hommes au championnat d'Afrique de pétanque en 2025."),
    ],
    # 44 Côte d'Ivoire
    [
        ("En quelle année la Côte d'Ivoire a-t-elle remporté la Coupe des Nations au championnat du monde de pétanque, en battant le Bénin 13-3 (à Cotonou) ?", ['1945', '2012', '2023'], 2, 'La bonne réponse était 2023.'),
        ("Quel monument ou quelle spécialité est associé à Côte d'Ivoire (Plus grande basilique du monde par sa superficie, à Yamoussoukro) ?", ['la Grande Mosquée de Djenné', "la Grande Mosquée d'Agadez", 'la basilique Notre-Dame de la Paix'], 2, 'La bonne réponse était la basilique Notre-Dame de la Paix : Plus grande basilique du monde par sa superficie, à Yamoussoukro.'),
        ("Quelle est la capitale de Côte d'Ivoire ?", ['Lusaka', 'Djibouti', 'Yamoussoukro'], 2, 'La bonne réponse était Yamoussoukro.'),
        ("Quelle est la monnaie utilisée en Côte d'Ivoire ?", ['le franc guinéen', 'la roupie mauricienne', 'le franc CFA'], 2, 'La bonne réponse était le franc CFA.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Côte d'Ivoire (médaillé d'or en tête-à-tête au championnat d'Afrique de pétanque en 2025) ?", ['Colin Delaney', 'Erik Bardelli', 'Salif Kourouma'], 2, "La bonne réponse était Salif Kourouma : médaillé d'or en tête-à-tête au championnat d'Afrique de pétanque en 2025."),
    ],
    # 45 Djibouti
    [
        ("En quelle année le Djiboutien Said Kadir a-t-il remporté l'argent au tir de précision au championnat d'Afrique de pétanque ?", ['2009', '2010', '2013'], 0, 'La bonne réponse était 2009.'),
        ("Quel monument ou quelle spécialité est associé à Djibouti (Point le plus bas d'Afrique, lac hypersalé entouré de laves noires) ?", ['le Karthala', 'le lac Assal', 'le parc national des Virunga'], 1, "La bonne réponse était le lac Assal : Point le plus bas d'Afrique, lac hypersalé entouré de laves noires."),
        ('Quelle est la capitale de Djibouti ?', ['Djibouti', 'Tripoli', 'Yaoundé'], 0, 'La bonne réponse était Djibouti.'),
        ('Quelle est la monnaie utilisée à Djibouti ?', ['le franc djiboutien', 'la roupie mauricienne', 'le franc CFA'], 0, 'La bonne réponse était le franc djiboutien.'),
        ("À quoi d'autre est associé Djibouti (Cheminées naturelles de calcaire de plusieurs dizaines de mètres, formées par des fumerolles, dans un paysage lunaire) ?", ['le lac Abbé', 'le parc national Manovo-Gounda St Floris', 'le mont Nimba'], 0, 'La bonne réponse était le lac Abbé : Cheminées naturelles de calcaire de plusieurs dizaines de mètres, formées par des fumerolles, dans un paysage lunaire.'),
    ],
    # 46 Égypte
    [
        ('En quelle année la Fédération Égyptienne de Pétanque a-t-elle été créée ?', ['2023', '1945', '2010'], 2, 'La bonne réponse était 2010.'),
        ('Quel monument ou quelle spécialité est associé à Égypte (Dont la grande pyramide de Khéops, dernière merveille du monde antique) ?', ["l'île de Gorée", 'Leptis Magna', 'les pyramides de Gizeh'], 2, 'La bonne réponse était les pyramides de Gizeh : Dont la grande pyramide de Khéops, dernière merveille du monde antique.'),
        ("Quelle est la capitale d'Égypte ?", ['Le Caire', 'Port-Louis', 'Brazzaville'], 0, 'La bonne réponse était Le Caire.'),
        ('Quelle est la monnaie utilisée en Égypte ?', ['la livre égyptienne', 'le franc guinéen', 'le franc CFA'], 0, 'La bonne réponse était la livre égyptienne.'),
        ("À quoi d'autre est associé Égypte (Temple monumental creusé dans la roche par Ramsès II, déplacé pierre par pierre dans les années 1960) ?", ['la Plaine des Jarres', 'Timgad', "le temple d'Abou Simbel"], 2, "La bonne réponse était le temple d'Abou Simbel : Temple monumental creusé dans la roche par Ramsès II, déplacé pierre par pierre dans les années 1960."),
    ],
    # 47 Gabon
    [
        ('En quelle année la Fédération Gabonaise de Pétanque (FEGAP) a-t-elle été créée ?', ['2024', '2006', '1993'], 1, 'La bonne réponse était 2006.'),
        ('Quel monument ou quelle spécialité est associé à Gabon (Forêts et savanes classées UNESCO, gravures rupestres préhistoriques) ?', ["l'allée des Baobabs", 'la Vallée de Mai', 'le parc national de la Lopé'], 2, 'La bonne réponse était le parc national de la Lopé : Forêts et savanes classées UNESCO, gravures rupestres préhistoriques.'),
        ('Quelle est la capitale du Gabon ?', ['Tunis', 'Libreville', 'Yamoussoukro'], 1, 'La bonne réponse était Libreville.'),
        ('Quelle est la monnaie utilisée au Gabon ?', ['le shilling ougandais', 'le franc CFA', 'le franc congolais'], 1, 'La bonne réponse était le franc CFA.'),
        ("À quoi d'autre est associé Gabon (Célèbre pour ses « hippopotames surfeurs » photographiés sur la plage, où éléphants et gorilles se promènent aussi sur le sable) ?", ['la structure de Richat', 'le parc national de Loango', 'le parc national de Zakouma'], 1, 'La bonne réponse était le parc national de Loango : Célèbre pour ses « hippopotames surfeurs » photographiés sur la plage, où éléphants et gorilles se promènent aussi sur le sable.'),
    ],
    # 48 Guinée
    [
        ("En quelle année la triplette guinéenne (Baba Conté, Djiba Camara, Alseny Sylla Bongo) a-t-elle remporté l'or au championnat national de boules et pétanque, à Conakry ?", ['1985', '2012', '2024'], 2, 'La bonne réponse était 2024.'),
        ("Quel monument ou quelle spécialité est associé à Guinée (« Château d'eau de l'Afrique de l'Ouest », falaises et cascades) ?", ['les chutes Victoria', 'les Terres des Sept Couleurs', 'le massif du Fouta Djalon'], 2, "La bonne réponse était le massif du Fouta Djalon : « Château d'eau de l'Afrique de l'Ouest », falaises et cascades."),
        ('Quelle est la capitale de Guinée ?', ['Conakry', 'Bamako', 'Kinshasa'], 0, 'La bonne réponse était Conakry.'),
        ('Quelle est la monnaie utilisée en Guinée ?', ['le franc CFA', 'le franc guinéen', 'la roupie seychelloise'], 1, 'La bonne réponse était le franc guinéen.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Guinée (membre de la triplette guinéenne sacrée championne nationale de boules et pétanque en 2024, à Conakry) ?', ['Zaidou Maoulida Mhamadi', 'Baba Conté', 'Trinh Thi Kim Thanh'], 1, 'La bonne réponse était Baba Conté : membre de la triplette guinéenne sacrée championne nationale de boules et pétanque en 2024, à Conakry.'),
    ],
    # 49 Libye
    [
        ('En quelle année la Fédération Libyenne de Boules a-t-elle été créée ?', ['1964', '2017', '2009'], 2, 'La bonne réponse était 2009.'),
        ('Quel monument ou quelle spécialité est associé à Libye (Cité antique romaine remarquablement conservée sur la côte) ?', ['Leptis Magna', 'les ruines de Loropéni', "l'amphithéâtre d'El Jem"], 0, 'La bonne réponse était Leptis Magna : Cité antique romaine remarquablement conservée sur la côte.'),
        ('Quelle est la capitale de Libye ?', ['Moroni', 'Tripoli', 'Bamako'], 1, 'La bonne réponse était Tripoli.'),
        ('En quelle année la Libye est-elle devenue membre fondateur de la Confédération Africaine de Sport Pétanque ?', ['2025', '2019', '2023'], 1, 'La bonne réponse était 2019.'),
        ("À quoi d'autre est associé Libye (« Perle du désert », cité pré-saharienne aux maisons superposées reliées par des ruelles couvertes, UNESCO) ?", ['la ville historique de Grand-Bassam', 'la vieille ville de Ghadamès', 'la médina de Tunis'], 1, 'La bonne réponse était la vieille ville de Ghadamès : « Perle du désert », cité pré-saharienne aux maisons superposées reliées par des ruelles couvertes, UNESCO.'),
    ],
    # 50 Madagascar
    [
        ('En quelle année Madagascar a-t-il remporté son 2e titre mondial de pétanque (triplette masculine), à Antananarivo ?', ['2010', '2007', '2016'], 2, 'La bonne réponse était 2016.'),
        ('Quel monument ou quelle spécialité est associé à Madagascar (Alignement spectaculaire de baobabs centenaires près de Morondava) ?', ['la réserve de Dzanga-Sangha', 'le parc national de la Lopé', "l'allée des Baobabs"], 2, "La bonne réponse était l'allée des Baobabs : Alignement spectaculaire de baobabs centenaires près de Morondava."),
        ("En quelle année Madagascar a-t-il remporté l'or en doublette mixte au championnat du monde de pétanque, à Rome (avec les joueurs Lova et Fana) ?", ['2025', '1997', '1990'], 0, 'La bonne réponse était 2025.'),
        ('En quelle année Madagascar a-t-il remporté son tout premier titre de champion du monde de pétanque en triplette hommes ?', ['1999', '2015', '2022'], 0, 'La bonne réponse était 1999.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Madagascar (champion du monde de tir de précision de pétanque en 2024) ?', ['Jean-François « Zigle » Rakotondrainibe', 'Luc Cattazzo', 'Rebekah « Bekah » Howe'], 0, 'La bonne réponse était Jean-François « Zigle » Rakotondrainibe : champion du monde de tir de précision de pétanque en 2024.'),
    ],
    # 51 Mali
    [
        ("En quelle année le Malien Sangaré Nouhoum a-t-il remporté le bronze au tir de précision au championnat d'Afrique de pétanque ?", ['2004', '1989', '2009'], 2, 'La bonne réponse était 2009.'),
        ('Quel monument ou quelle spécialité est associé à Mali (Plus grand édifice en terre crue au monde) ?', ["la Grande Mosquée d'Agadez", 'la basilique Notre-Dame de la Paix', 'la Grande Mosquée de Djenné'], 2, 'La bonne réponse était la Grande Mosquée de Djenné : Plus grand édifice en terre crue au monde.'),
        ('Quelle est la capitale du Mali ?', ['Bamako', 'Yamoussoukro', 'Lusaka'], 0, 'La bonne réponse était Bamako.'),
        ('Quelle est la monnaie utilisée au Mali ?', ['le franc CFA', 'le dirham marocain', "l'ariary"], 0, 'La bonne réponse était le franc CFA.'),
        ("À quoi d'autre est associé Mali (Escarpement gréseux de 200 km abritant 289 villages dogons, greniers et cases à toits pointus, UNESCO) ?", ['la falaise de Bandiagara', 'Le Morne Brabant', 'le lac Rose'], 0, 'La bonne réponse était la falaise de Bandiagara : Escarpement gréseux de 200 km abritant 289 villages dogons, greniers et cases à toits pointus, UNESCO.'),
    ],
    # 52 Maurice
    [
        ('En quelle année le Mauricien Parvez Khodabaccus a-t-il atteint les demi-finales du tir de précision au championnat du monde de pétanque, à Dijon ?', ['2012', '2023', '2024'], 2, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Maurice (Dunes de sable volcanique multicolore à Chamarel) ?', ['le Karthala', 'les Terres des Sept Couleurs', "l'allée des Baobabs"], 1, 'La bonne réponse était les Terres des Sept Couleurs : Dunes de sable volcanique multicolore à Chamarel.'),
        ("Quelle est la capitale de l'Île Maurice ?", ['Conakry', 'Le Caire', 'Port-Louis'], 2, 'La bonne réponse était Port-Louis.'),
        ("En quelle année l'Île Maurice a-t-elle remporté le bronze au tir de précision au championnat d'Afrique de pétanque ?", ['2019', '2025', '2022'], 0, 'La bonne réponse était 2019.'),
        ("À quoi d'autre est associé Maurice (Montagne péninsulaire ayant servi de refuge aux esclaves marrons aux XVIIIe-XIXe siècles, symbole de résistance, UNESCO) ?", ['Le Morne Brabant', 'le mont Cameroun', 'la réserve de faune à okapis'], 0, 'La bonne réponse était Le Morne Brabant : Montagne péninsulaire ayant servi de refuge aux esclaves marrons aux XVIIIe-XIXe siècles, symbole de résistance, UNESCO.'),
    ],
    # 53 Mauritanie
    [
        ('En quelle année la Mauritanie a-t-elle remporté la médaille de bronze au championnat du monde de pétanque, à Izmir (Turquie) ?', ['2024', '1995', '2010'], 2, 'La bonne réponse était 2010.'),
        ("Quel monument ou quelle spécialité est associé à Mauritanie (Cité caravanière du désert, « Sorbonne du désert », septième ville sainte de l'Islam) ?", ["l'île de Gorée", 'Chinguetti', "l'amphithéâtre d'El Jem"], 1, "La bonne réponse était Chinguetti : Cité caravanière du désert, « Sorbonne du désert », septième ville sainte de l'Islam."),
        ('Quelle est la capitale de Mauritanie ?', ['Niamey', 'Nouakchott', 'Ouagadougou'], 1, 'La bonne réponse était Nouakchott.'),
        ("En quelle année la Mauritanie a-t-elle accueilli le championnat d'Afrique de pétanque, à Nouakchott, pour sa 10e édition ?", ['2025', '2022', '1971'], 0, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Mauritanie (entraîneur de l'équipe nationale mauritanienne de pétanque, qualifiée pour le championnat du monde après une 5e place à Cotonou en 2023) ?", ['Colin Delaney', 'Tarek Akili', 'Yerko Castro'], 1, "La bonne réponse était Tarek Akili : entraîneur de l'équipe nationale mauritanienne de pétanque, qualifiée pour le championnat du monde après une 5e place à Cotonou en 2023."),
    ],
    # 54 Maroc
    [
        ('En quelle année le Maroc a-t-il été champion du monde de pétanque en triplette messieurs, à Boumerdès (Algérie) ?', ['2023', '1987', '2012'], 1, 'La bonne réponse était 1987.'),
        ('Quel monument ou quelle spécialité est associé à Maroc (Plus grande zone piétonne du monde, centre historique classé UNESCO) ?', ["les palais royaux d'Abomey", 'la médina de Fès', 'le palais royal de Foumban'], 1, 'La bonne réponse était la médina de Fès : Plus grande zone piétonne du monde, centre historique classé UNESCO.'),
        ('En quelle année le Maroc a-t-il remporté son 3e titre de champion du monde de pétanque en triplette, à Monaco ?', ['1997', '1990', '2025'], 1, 'La bonne réponse était 1990.'),
        ('En quelle année le Maroc a-t-il remporté son tout premier titre de champion du monde de pétanque en triplette, à Rotterdam (Pays-Bas) ?', ['2019', '2023', '1984'], 2, 'La bonne réponse était 1984.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Maroc (champion du monde de tir de précision de pétanque en 2008 (à Dakar) et quadruple champion d'Afrique de tir de précision) ?", ['Southammavong Bountamy', 'Charles Mbenoun', 'Abdessamad El Mankari'], 2, "La bonne réponse était Abdessamad El Mankari : champion du monde de tir de précision de pétanque en 2008 (à Dakar) et quadruple champion d'Afrique de tir de précision."),
    ],
    # 55 Niger
    [
        ("En quelle année le Nigérien Mohamed Harouna est-il devenu champion d'Afrique de tir de précision de pétanque ?", ['1992', '2007', '2021'], 2, 'La bonne réponse était 2021.'),
        ('Quel monument ou quelle spécialité est associé à Niger (Plus haute structure en terre crue du monde (minaret de 27 m)) ?', ["la Grande Mosquée d'Agadez", 'la basilique Notre-Dame de la Paix', 'la Grande Mosquée de Djenné'], 0, "La bonne réponse était la Grande Mosquée d'Agadez : Plus haute structure en terre crue du monde (minaret de 27 m)."),
        ('Quelle est la capitale du Niger ?', ['Lomé', 'Niamey', 'Lusaka'], 1, 'La bonne réponse était Niamey.'),
        ("En quelle année le Niger a-t-il remporté l'argent à la Coupe des nations hommes au championnat d'Afrique de pétanque ?", ['2008', '2024', '2023'], 1, 'La bonne réponse était 2024.'),
        ("À quoi d'autre est associé Niger (L'une des plus grandes aires protégées d'Afrique, massif montagneux et désert, UNESCO) ?", ["l'atoll d'Aldabra", 'la structure de Richat', "la réserve naturelle de l'Aïr et du Ténéré"], 2, "La bonne réponse était la réserve naturelle de l'Aïr et du Ténéré : L'une des plus grandes aires protégées d'Afrique, massif montagneux et désert, UNESCO."),
    ],
    # 56 Ouganda
    [
        ('En quelle année la fédération ougandaise de pétanque a-t-elle été créée et affiliée à la FIPJP ?', ['2013', '2024', '2021'], 0, 'La bonne réponse était 2013.'),
        ('Quel monument ou quelle spécialité est associé à Ouganda (Abrite près de la moitié des gorilles de montagne survivants) ?', ['les Terres des Sept Couleurs', "le parc national d'Odzala-Kokoua", 'le parc national impénétrable de Bwindi'], 2, 'La bonne réponse était le parc national impénétrable de Bwindi : Abrite près de la moitié des gorilles de montagne survivants.'),
        ("Quelle est la capitale d'Ouganda ?", ['Rabat', 'Porto-Novo', 'Kampala'], 2, 'La bonne réponse était Kampala.'),
        ('Quelle est la monnaie utilisée en Ouganda ?', ['le shilling ougandais', 'le dinar tunisien', 'le franc CFA'], 0, 'La bonne réponse était le shilling ougandais.'),
        ("À quoi d'autre est associé Ouganda (Mausolée royal circulaire construit en 1882 en matériaux végétaux, lieu spirituel du royaume baganda, UNESCO) ?", ['les tombeaux des rois du Buganda à Kasubi', 'la Grande Mosquée du Vendredi de Moroni', 'la basilique Sainte-Anne-du-Congo'], 0, 'La bonne réponse était les tombeaux des rois du Buganda à Kasubi : Mausolée royal circulaire construit en 1882 en matériaux végétaux, lieu spirituel du royaume baganda, UNESCO.'),
    ],
    # 57 République Centrafricaine
    [
        ("Quel fait notable est associé à République Centrafricaine (Chutes d'eau spectaculaires situées à une centaine de kilomètres de Bangui) ?", ["l'artisanat textile maya", 'les chutes de Boali', 'le saut au gôl (Naghol)'], 1, "La bonne réponse était les chutes de Boali : Chutes d'eau spectaculaires situées à une centaine de kilomètres de Bangui."),
        ("Quel monument ou quelle spécialité est associé à République Centrafricaine (Clairière où se rassemblent chaque jour des dizaines d'éléphants de forêt) ?", ['le parc national de la Lopé', 'le Karthala', 'la réserve de Dzanga-Sangha'], 2, "La bonne réponse était la réserve de Dzanga-Sangha : Clairière où se rassemblent chaque jour des dizaines d'éléphants de forêt."),
        ('Quelle est la capitale de République Centrafricaine ?', ['Tunis', 'Kinshasa', 'Bangui'], 2, 'La bonne réponse était Bangui.'),
        ('Quelle est la monnaie utilisée en République Centrafricaine ?', ['le franc congolais', 'le franc CFA', 'le dinar algérien'], 1, 'La bonne réponse était le franc CFA.'),
        ("À quoi d'autre est associé République Centrafricaine (Plus grand parc des savanes d'Afrique centrale, abritant rhinocéros noirs et éléphants, UNESCO) ?", ['le mont Cameroun', 'le parc national de Loango', 'le parc national Manovo-Gounda St Floris'], 2, "La bonne réponse était le parc national Manovo-Gounda St Floris : Plus grand parc des savanes d'Afrique centrale, abritant rhinocéros noirs et éléphants, UNESCO."),
    ],
    # 58 République Démocratique du Congo
    [
        ("Quel fait notable est associé à République Démocratique du Congo (Le fleuve Congo est le fleuve le plus profond du monde et le deuxième plus long d'Afrique) ?", ["le barrage d'Itaipu", 'le fleuve Congo', 'les timbres-poste'], 1, "La bonne réponse était le fleuve Congo : Le fleuve Congo est le fleuve le plus profond du monde et le deuxième plus long d'Afrique."),
        ("Quel monument ou quelle spécialité est associé à République Démocratique du Congo (Plus ancien parc d'Afrique, seul site avec trois espèces de grands singes) ?", ['la Vallée de Mai', 'le parc national de la Lopé', 'le parc national des Virunga'], 2, "La bonne réponse était le parc national des Virunga : Plus ancien parc d'Afrique, seul site avec trois espèces de grands singes."),
        ('Quelle est la capitale de République Démocratique du Congo ?', ['Bangui', 'Kinshasa', 'Yaoundé'], 1, 'La bonne réponse était Kinshasa.'),
        ('Quelle est la monnaie utilisée en République Démocratique du Congo ?', ["l'ariary", 'la livre égyptienne', 'le franc congolais'], 2, 'La bonne réponse était le franc congolais.'),
        ("À quoi d'autre est associé République Démocratique du Congo (Forêt de l'Ituri abritant environ 5000 okapis sauvages et les peuples pygmées Mbuti et Efe, UNESCO) ?", ['le parc national de Zakouma', 'la réserve de faune à okapis', 'la falaise de Bandiagara'], 1, "La bonne réponse était la réserve de faune à okapis : Forêt de l'Ituri abritant environ 5000 okapis sauvages et les peuples pygmées Mbuti et Efe, UNESCO."),
    ],
    # 59 Sénégal
    [
        ("En quelle année le Sénégal a-t-il remporté l'or en triplette hommes au championnat d'Afrique de pétanque, à Marrakech ?", ['2023', '2024', '2007'], 1, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Sénégal (Ancien comptoir de la traite négrière au large de Dakar) ?', ["l'amphithéâtre d'El Jem", "l'île de Gorée", 'Leptis Magna'], 1, "La bonne réponse était l'île de Gorée : Ancien comptoir de la traite négrière au large de Dakar."),
        ('Quelle est la capitale du Sénégal ?', ['Niamey', 'Bamako', 'Dakar'], 2, 'La bonne réponse était Dakar.'),
        ("En quelle année le Sénégal a-t-il remporté le bronze en triplette hommes au championnat d'Afrique de pétanque, pour la première fois ?", ['2025', '1999', '2009'], 2, 'La bonne réponse était 2009.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Sénégal (vice-champion du monde de tir de précision de pétanque en 2008, à Dakar) ?', ['Edward Vinke', 'François Fara Ndiaye', 'Erik Bardelli'], 1, 'La bonne réponse était François Fara Ndiaye : vice-champion du monde de tir de précision de pétanque en 2008, à Dakar.'),
    ],
    # 60 Seychelles
    [
        ('En quelle année la Seychelles Pétanque Association a-t-elle été fondée et affiliée à la FIPJP ?', ['2023', '2024', '1996'], 2, 'La bonne réponse était 1996.'),
        ('Quel monument ou quelle spécialité est associé à Seychelles (Forêt primaire abritant le coco de mer, plus grosse graine du monde) ?', ['la Vallée de Mai', 'les chutes Victoria', 'le parc national des Virunga'], 0, 'La bonne réponse était la Vallée de Mai : Forêt primaire abritant le coco de mer, plus grosse graine du monde.'),
        ('Quelle est la capitale des Seychelles ?', ['Victoria', 'Rabat', 'Brazzaville'], 0, 'La bonne réponse était Victoria.'),
        ('Quelle est la monnaie utilisée aux Seychelles ?', ['la roupie seychelloise', 'la roupie mauricienne', 'le franc CFA'], 0, 'La bonne réponse était la roupie seychelloise.'),
        ("À quoi d'autre est associé Seychelles (Plus grand récif corallien surélevé du monde, abritant environ 100 000 à 150 000 tortues géantes, UNESCO) ?", ["l'atoll d'Aldabra", 'la structure de Richat', 'la falaise de Bandiagara'], 0, "La bonne réponse était l'atoll d'Aldabra : Plus grand récif corallien surélevé du monde, abritant environ 100 000 à 150 000 tortues géantes, UNESCO."),
    ],
    # 61 Tchad
    [
        ("En quelle année le Tchadien Hounaye Raymon a-t-il remporté l'argent au tir de précision au championnat d'Afrique de pétanque ?", ['2013', '2002', '1984'], 0, 'La bonne réponse était 2013.'),
        ("Quel monument ou quelle spécialité est associé à Tchad (Oasis rocheuse de l'Ennedi, dernière population de crocodiles du désert) ?", ['le parc national de la Lopé', 'la Vallée de Mai', "la Guelta d'Archei"], 2, "La bonne réponse était la Guelta d'Archei : Oasis rocheuse de l'Ennedi, dernière population de crocodiles du désert."),
        ('Quelle est la capitale du Tchad ?', ['Le Caire', "N'Djamena", 'Alger'], 1, "La bonne réponse était N'Djamena."),
        ('En quelle année le Tchad a-t-il candidaté, sans succès, pour organiser le championnat du monde de pétanque (finalement attribué à Madagascar) ?', ['2016', '2025', '2008'], 0, 'La bonne réponse était 2016.'),
        ("À quoi d'autre est associé Tchad (Plus ancien parc national du Tchad, population d'éléphants remontée d'environ 450 à près de 800 grâce à la lutte anti-braconnage) ?", ['la structure de Richat', 'le parc national Manovo-Gounda St Floris', 'le parc national de Zakouma'], 2, "La bonne réponse était le parc national de Zakouma : Plus ancien parc national du Tchad, population d'éléphants remontée d'environ 450 à près de 800 grâce à la lutte anti-braconnage."),
    ],
    # 62 Togo
    [
        ('En quelle année le Togo a-t-il remporté le bronze au tir de précision par équipe au championnat du monde de pétanque, à Cotonou (Bénin) ?', ['2023', '1991', '2017'], 0, 'La bonne réponse était 2023.'),
        ('Quel monument ou quelle spécialité est associé à Togo (« Pays des Batammariba », cases-tours en terre appelées Takienta) ?', ['la Jersey Royal', 'le Koutammakou', 'le sauna'], 1, 'La bonne réponse était le Koutammakou : « Pays des Batammariba », cases-tours en terre appelées Takienta.'),
        ('Quelle est la capitale du Togo ?', ['Tunis', 'Kampala', 'Lomé'], 2, 'La bonne réponse était Lomé.'),
        ("En quelle année le Togo a-t-il remporté l'argent en triplette hommes au championnat d'Afrique de pétanque ?", ['2019', '2025', '2022'], 0, 'La bonne réponse était 2019.'),
        ("À quoi d'autre est associé Togo (Plus grand marché vaudou au monde, à Lomé, installé en 1946) ?", ['le cheval Akhal-Teke', 'la vallée des Roses', "le marché des féticheurs d'Akodessewa"], 2, "La bonne réponse était le marché des féticheurs d'Akodessewa : Plus grand marché vaudou au monde, à Lomé, installé en 1946."),
    ],
    # 63 Tunisie
    [
        ('En quelle année la Fédération Tunisienne de Boules et de Pétanque a-t-elle été créée et affiliée à la FIPJP ?', ['2012', '1958', '2025'], 1, 'La bonne réponse était 1958.'),
        ("Quel monument ou quelle spécialité est associé à Tunisie (L'un des plus grands amphithéâtres romains au monde) ?", ['Chinguetti', 'les ruines de Loropéni', "l'amphithéâtre d'El Jem"], 2, "La bonne réponse était l'amphithéâtre d'El Jem : L'un des plus grands amphithéâtres romains au monde."),
        ('En quelle année la Tunisie a-t-elle remporté son 3e titre de championne du monde de pétanque en triplette hommes, à Montpellier ?', ['1990', '1997', '2025'], 1, 'La bonne réponse était 1997.'),
        ('En quelle année la Tunisie a-t-elle remporté son tout premier titre de championne du monde de pétanque en triplette hommes ?', ['2015', '1983', '2019'], 1, 'La bonne réponse était 1983.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Tunisie (championne du monde de pétanque en triplette femmes (2011), en individuel femmes (2023) et en doublette femmes (2025)) ?', ['Mouna Béji', 'Fredy Isaias', 'Lasse Dithmar'], 0, 'La bonne réponse était Mouna Béji : championne du monde de pétanque en triplette femmes (2011), en individuel femmes (2023) et en doublette femmes (2025).'),
    ],
    # 64 Zambie
    [
        ("Quel fait notable est associé à Zambie (La Zambie est l'un des plus grands producteurs mondiaux de cuivre) ?", ['le saut au gôl (Naghol)', 'les chutes de Boali', 'le cuivre'], 2, "La bonne réponse était le cuivre : La Zambie est l'un des plus grands producteurs mondiaux de cuivre."),
        ("Quel monument ou quelle spécialité est associé à Zambie (L'une des plus grandes chutes d'eau du monde, sur le Zambèze) ?", ['le massif du Fouta Djalon', 'les chutes Victoria', "la Guelta d'Archei"], 1, "La bonne réponse était les chutes Victoria : L'une des plus grandes chutes d'eau du monde, sur le Zambèze."),
        ('Quelle est la capitale de Zambie ?', ['Alger', 'Djibouti', 'Lusaka'], 2, 'La bonne réponse était Lusaka.'),
        ('Quelle est la monnaie utilisée en Zambie ?', ['le franc congolais', 'le kwacha zambien', 'le franc CFA'], 1, 'La bonne réponse était le kwacha zambien.'),
        ("À quoi d'autre est associé Zambie (Considéré comme le berceau du safari à pied, popularisé dans les années 1950 par Norman Carr) ?", ['la structure de Richat', 'la réserve de faune à okapis', 'le parc national de South Luangwa'], 2, 'La bonne réponse était le parc national de South Luangwa : Considéré comme le berceau du safari à pied, popularisé dans les années 1950 par Norman Carr.'),
    ],
    # 65 Afghanistan
    [
        ("Quel fait notable est associé à Afghanistan (L'Afghanistan est depuis l'Antiquité l'une des principales sources mondiales de lapis-lazuli) ?", ['le lapis-lazuli', 'les timbres-poste', "le barrage d'Itaipu"], 0, "La bonne réponse était le lapis-lazuli : L'Afghanistan est depuis l'Antiquité l'une des principales sources mondiales de lapis-lazuli."),
        ('Quel monument ou quelle spécialité est associé à Afghanistan (Statues monumentales sculptées au VIe siècle, détruites en 2001) ?', ['le Taj Mahal', 'le mur des Lamentations', 'les Bouddhas de Bamiyan'], 2, 'La bonne réponse était les Bouddhas de Bamiyan : Statues monumentales sculptées au VIe siècle, détruites en 2001.'),
        ("Quelle est la capitale d'Afghanistan ?", ['Jérusalem', 'Kaboul', 'Islamabad'], 1, 'La bonne réponse était Kaboul.'),
        ('Quelle est la monnaie utilisée en Afghanistan ?', ["l'afghani", 'le nouveau dollar taïwanais', 'la livre turque'], 0, "La bonne réponse était l'afghani."),
        ("À quoi d'autre est associé Afghanistan (Tour en briques cuites du XIIe siècle, haute de 65 m, premier site afghan classé UNESCO) ?", ["le monastère d'Erdene Zuu", 'le Minaret de Jam', 'les grottes de Batu'], 1, 'La bonne réponse était le Minaret de Jam : Tour en briques cuites du XIIe siècle, haute de 65 m, premier site afghan classé UNESCO.'),
    ],
    # 66 Bangladesh
    [
        ('En quelle année la fédération de pétanque du Bangladesh a-t-elle été créée ?', ['2025', '2017', '2004'], 1, 'La bonne réponse était 2017.'),
        ('Quel monument ou quelle spécialité est associé à Bangladesh (Tissage traditionnel de mousseline de coton brodée à la main) ?', ['le Vasa', 'le Jamdani', 'le Koutammakou'], 1, 'La bonne réponse était le Jamdani : Tissage traditionnel de mousseline de coton brodée à la main.'),
        ('Quelle est la capitale du Bangladesh ?', ['Astana', 'Dacca', 'Erevan'], 1, 'La bonne réponse était Dacca.'),
        ('Quelle est la monnaie utilisée au Bangladesh ?', ['la roupie indienne', 'le taka', 'la roupie népalaise'], 1, 'La bonne réponse était le taka.'),
        ("À quoi d'autre est associé Bangladesh (Plus grande forêt de mangrove au monde, dans le delta du Gange, classée UNESCO, refuge du tigre du Bengale) ?", ['le lac Issyk-Koul', 'les Sundarbans', 'les cèdres du Liban'], 1, 'La bonne réponse était les Sundarbans : Plus grande forêt de mangrove au monde, dans le delta du Gange, classée UNESCO, refuge du tigre du Bengale.'),
    ],
    # 67 Brunei
    [
        ('En quelle année la fédération de pétanque de Brunei a-t-elle été créée ?', ['2007', '2024', '2013'], 0, 'La bonne réponse était 2007.'),
        ('Quel monument ou quelle spécialité est associé à Brunei (Dôme doré et colonnes de marbre italien, achevée en 1958) ?', ['Borobudur', 'la mosquée Sultan Omar Ali Saifuddien', 'les Bouddhas de Bamiyan'], 1, 'La bonne réponse était la mosquée Sultan Omar Ali Saifuddien : Dôme doré et colonnes de marbre italien, achevée en 1958.'),
        ('Quelle est la capitale du Brunei ?', ['New Delhi', 'Ankara', 'Bandar Seri Begawan'], 2, 'La bonne réponse était Bandar Seri Begawan.'),
        ("En quelle année Brunei a-t-il participé au championnat d'Asie de pétanque à Kuala Lumpur, sans obtenir de médaille ?", ['2023', '2021', '2025'], 2, 'La bonne réponse était 2025.'),
        ("À quoi d'autre est associé Brunei (Plus grand village sur pilotis au monde, environ 30 000 habitants sur la rivière Brunei) ?", ['la place Naghsh-e Jahan', 'Kampong Ayer', 'la vieille ville de Hoi An'], 1, 'La bonne réponse était Kampong Ayer : Plus grand village sur pilotis au monde, environ 30 000 habitants sur la rivière Brunei.'),
    ],
    # 68 Cambodge
    [
        ('En quelle année le Cambodge a-t-il remporté son 5e titre mondial de pétanque consécutif, en Espagne ?', ['1987', '2021', '1992'], 1, 'La bonne réponse était 2021.'),
        ('Quel monument ou quelle spécialité est associé à Cambodge (Le plus grand complexe religieux du monde, temple khmer du XIIe siècle) ?', ['la pagode Shwedagon', 'Angkor Vat', 'Borobudur'], 1, 'La bonne réponse était Angkor Vat : Le plus grand complexe religieux du monde, temple khmer du XIIe siècle.'),
        ('Quelle est la capitale du Cambodge ?', ['Islamabad', 'Phnom Penh', 'Manille'], 1, 'La bonne réponse était Phnom Penh.'),
        ("En quelle année le Cambodge a-t-il remporté l'or en triplette féminine au championnat d'Asie de pétanque, à Kuala Lumpur ?", ['2007', '2017', '2025'], 2, 'La bonne réponse était 2025.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Cambodge (champion du monde de tir de précision de pétanque en 2016 (à Madagascar), avec 39 médailles internationales cumulées depuis 2001) ?', ['Rebekah « Bekah » Howe', 'Colin Delaney', 'Sok Chanmean'], 2, 'La bonne réponse était Sok Chanmean : champion du monde de tir de précision de pétanque en 2016 (à Madagascar), avec 39 médailles internationales cumulées depuis 2001.'),
    ],
    # 69 Chine
    [
        ('En quelle année la pétanque a-t-elle commencé à être introduite en Chine, par le promoteur français Bernard Champey ?', ['2021', '2009', '1985'], 2, 'La bonne réponse était 1985.'),
        ('Quel monument ou quelle spécialité est associé à Chine (Fortification de plusieurs milliers de kilomètres) ?', ['la Grande Muraille', 'le château du Wawel', 'le château de Caernarfon'], 0, 'La bonne réponse était la Grande Muraille : Fortification de plusieurs milliers de kilomètres.'),
        ('Quelle est la capitale de Chine ?', ['Pékin', 'New Delhi', 'Hanoï'], 0, 'La bonne réponse était Pékin.'),
        ("En quelle année la Chine a-t-elle remporté le bronze en triplette hommes (Nation Cup) au championnat d'Asie de pétanque ?", ['2016', '2025', '1998'], 1, 'La bonne réponse était 2025.'),
        ("À quoi d'autre est associé Chine (Des milliers de statues de soldats en terre cuite gardant le tombeau du premier empereur Qin) ?", ['la Plaine des Jarres', "le parc historique d'Ayutthaya", "l'Armée de terre cuite de Xi'an"], 2, "La bonne réponse était l'Armée de terre cuite de Xi'an : Des milliers de statues de soldats en terre cuite gardant le tombeau du premier empereur Qin."),
    ],
    # 70 Corée du Sud
    [
        ('En quelle année la Fédération coréenne de pétanque a-t-elle été créée ?', ['1972', '2012', '2013'], 2, 'La bonne réponse était 2013.'),
        ('Quel monument ou quelle spécialité est associé à Corée du Sud (Chou fermenté épicé, spécialité culinaire quotidienne coréenne) ?', ['le kimchi', 'le poisson cru au lait de coco', "l'escudella"], 0, 'La bonne réponse était le kimchi : Chou fermenté épicé, spécialité culinaire quotidienne coréenne.'),
        ('Quelle est la capitale de Corée du Sud ?', ['Séoul', 'Ankara', 'Katmandou'], 0, 'La bonne réponse était Séoul.'),
        ("En quelle année la Corée du Sud a-t-elle participé au championnat d'Asie de pétanque, sans obtenir de médaille ?", ['2025', '2019', '2008'], 0, 'La bonne réponse était 2025.'),
        ("À quoi d'autre est associé Corée du Sud (Principal palais royal de la dynastie Joseon, construit en 1395 à Séoul) ?", ['le château de Himeji', 'le Fort Rouge de Delhi', 'le palais Gyeongbokgung'], 2, 'La bonne réponse était le palais Gyeongbokgung : Principal palais royal de la dynastie Joseon, construit en 1395 à Séoul.'),
    ],
    # 71 Inde
    [
        ('En quelle année la Petanque India Association a-t-elle été officiellement incorporée ?', ['2019', '2002', '2003'], 0, 'La bonne réponse était 2019.'),
        ('Quel monument ou quelle spécialité est associé à Inde (Mausolée de marbre blanc construit à Agra au XVIIe siècle) ?', ['le Taj Mahal', 'les Bouddhas de Bamiyan', 'Sainte-Sophie'], 0, 'La bonne réponse était le Taj Mahal : Mausolée de marbre blanc construit à Agra au XVIIe siècle.'),
        ("Quelle est la capitale d'Inde ?", ['Phnom Penh', 'New Delhi', 'Manille'], 1, 'La bonne réponse était New Delhi.'),
        ("En quelle année l'Inde a-t-elle participé au championnat d'Asie de pétanque à Kuala Lumpur, terminant dernière (16e) en triplette masculine ?", ['2025', '2024', '2013'], 0, 'La bonne réponse était 2025.'),
        ("À quoi d'autre est associé Inde (Forteresse moghole en grès rouge du XVIIe siècle, résidence des empereurs moghols, classée UNESCO) ?", ['le château de Himeji', 'le Fort Rouge de Delhi', 'le palais Gyeongbokgung'], 1, 'La bonne réponse était le Fort Rouge de Delhi : Forteresse moghole en grès rouge du XVIIe siècle, résidence des empereurs moghols, classée UNESCO.'),
    ],
    # 72 Indonésie
    [
        ("En quelle année l'Indonésienne Anni Saputri est-elle devenue championne d'Asie de tir de précision femmes, à Kuala Lumpur ?", ['2009', '2021', '2025'], 2, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Indonésie (Le plus grand temple bouddhiste du monde, à Java) ?', ['la mosquée Sultan Omar Ali Saifuddien', 'la pagode Shwedagon', 'Borobudur'], 2, 'La bonne réponse était Borobudur : Le plus grand temple bouddhiste du monde, à Java.'),
        ("Quelle est la capitale d'Indonésie ?", ['Jakarta', 'Bichkek', 'Katmandou'], 0, 'La bonne réponse était Jakarta.'),
        ("En quelle année l'Indonésie a-t-elle remporté le bronze en triplette masculine à l'Asian Cup de pétanque ?", ['2023', '2007', '2025'], 2, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Indonésie (médaillé d'or en pétanque simple messieurs aux SEA Games 2025, en battant le Laotien Southammavong Bountamy en finale) ?", ['Lasse Dithmar', 'Mouna Béji', 'Andri Irawan'], 2, "La bonne réponse était Andri Irawan : médaillé d'or en pétanque simple messieurs aux SEA Games 2025, en battant le Laotien Southammavong Bountamy en finale."),
    ],
    # 73 Iran
    [
        ('En quelle année la fédération iranienne de boules et pétanque a-t-elle été fondée ?', ['2009', '2024', '1996'], 0, 'La bonne réponse était 2009.'),
        ("Quel monument ou quelle spécialité est associé à Iran (Cité cérémonielle de l'Empire perse achéménide) ?", ['la tour Bourana', 'les ruines de Mohenjo-daro', 'Persépolis'], 2, "La bonne réponse était Persépolis : Cité cérémonielle de l'Empire perse achéménide."),
        ("Quelle est la capitale d'Iran ?", ['Kaboul', 'Oulan-Bator', 'Téhéran'], 2, 'La bonne réponse était Téhéran.'),
        ("En quelle année s'est tenue la 13e édition du championnat national de pétanque d'Iran, à Sari ?", ['2022', '2019', '2023'], 2, 'La bonne réponse était 2023.'),
        ("À quoi d'autre est associé Iran (Immense place royale du XVIIe siècle à Ispahan, classée UNESCO) ?", ['Kampong Ayer', 'la place Naghsh-e Jahan', 'Gardens by the Bay'], 1, 'La bonne réponse était la place Naghsh-e Jahan : Immense place royale du XVIIe siècle à Ispahan, classée UNESCO.'),
    ],
    # 74 Japon
    [
        ('En quelle année la Japan Petanque Boules Federation a-t-elle été créée ?', ['2014', '2022', '2023'], 0, 'La bonne réponse était 2014.'),
        ('Quel monument ou quelle spécialité est associé à Japon (Plus haut sommet du Japon, volcan sacré et symbole national) ?', ['le Mont Fuji', 'les rizières de Banaue', "la Porte de l'Enfer"], 0, 'La bonne réponse était le Mont Fuji : Plus haut sommet du Japon, volcan sacré et symbole national.'),
        ('Quelle est la capitale du Japon ?', ['Hanoï', 'Naypyidaw', 'Tokyo'], 2, 'La bonne réponse était Tokyo.'),
        ("En quelle année le Japon a-t-il remporté le bronze au tir de précision juniors au championnat d'Asie de pétanque ?", ['2021', '2025', '2024'], 1, 'La bonne réponse était 2025.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Japon (joueuse japonaise classée 1ère de la sélection nationale de pétanque trois fois consécutives) ?', ['Ayumi Goma', 'François Fara Ndiaye', 'Andri Irawan'], 0, 'La bonne réponse était Ayumi Goma : joueuse japonaise classée 1ère de la sélection nationale de pétanque trois fois consécutives.'),
    ],
    # 75 Kazakhstan
    [
        ('Quel fait notable est associé à Kazakhstan (Plus grand et plus ancien pas de tir spatial au monde, loué par la Russie au Kazakhstan) ?', ['le fleuve Congo', 'le cuivre', 'le cosmodrome de Baïkonour'], 2, 'La bonne réponse était le cosmodrome de Baïkonour : Plus grand et plus ancien pas de tir spatial au monde, loué par la Russie au Kazakhstan.'),
        ("Quel monument ou quelle spécialité est associé à Kazakhstan (Tour d'observation surmontée d'une sphère dorée, à Astana) ?", ['le Taipei 101', 'la tour Baïterek', 'le Merlion'], 1, "La bonne réponse était la tour Baïterek : Tour d'observation surmontée d'une sphère dorée, à Astana."),
        ('Quelle est la capitale du Kazakhstan ?', ['Ankara', 'Manille', 'Astana'], 2, 'La bonne réponse était Astana.'),
        ('Quelle est la monnaie utilisée au Kazakhstan ?', ['la roupie pakistanaise', 'le tenge', 'le taka'], 1, 'La bonne réponse était le tenge.'),
        ("À quoi d'autre est associé Kazakhstan (Bâti sur ordre de Tamerlan entre 1389 et 1405 à Turkestan, chef-d'œuvre inachevé de l'architecture timouride, UNESCO) ?", ["le monastère d'Erdene Zuu", 'le temple de Prambanan', 'le mausolée de Khoja Ahmed Yasavi'], 2, "La bonne réponse était le mausolée de Khoja Ahmed Yasavi : Bâti sur ordre de Tamerlan entre 1389 et 1405 à Turkestan, chef-d'œuvre inachevé de l'architecture timouride, UNESCO."),
    ],
    # 76 Kirghizistan
    [
        ('En quelle année la Fédération kirghize de pétanque a-t-elle été fondée ?', ['1984', '2022', '2024'], 1, 'La bonne réponse était 2022.'),
        ('Quel monument ou quelle spécialité est associé à Kirghizistan (Ancien minaret du XIe siècle vestige de la Route de la Soie) ?', ['les ruines de Baalbek', 'la tour Bourana', 'Persépolis'], 1, 'La bonne réponse était la tour Bourana : Ancien minaret du XIe siècle vestige de la Route de la Soie.'),
        ('Quelle est la capitale du Kirghizistan ?', ['Bichkek', 'Naypyidaw', 'Vientiane'], 0, 'La bonne réponse était Bichkek.'),
        ('Quelle est la monnaie utilisée au Kirghizistan ?', ['le tenge', 'le som kirghiz', 'le baht'], 1, 'La bonne réponse était le som kirghiz.'),
        ("À quoi d'autre est associé Kirghizistan (Deuxième plus grand lac alpin du monde, ne gèle jamais malgré son altitude de 1607 m) ?", ['les Chocolate Hills', 'le lac Issyk-Koul', 'les Sundarbans'], 1, 'La bonne réponse était le lac Issyk-Koul : Deuxième plus grand lac alpin du monde, ne gèle jamais malgré son altitude de 1607 m.'),
    ],
    # 77 Laos
    [
        ("En quelle année la Laotienne Bovilak Thepphakan a-t-elle remporté la toute première médaille d'or de l'histoire du Laos aux SEA Games, en pétanque simple femmes ?", ['2025', '2015', '2004'], 0, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Laos (Grand stupa bouddhiste doré, monument national du Laos) ?', ['le That Luang', 'le mur des Lamentations', 'le Wat Arun'], 0, 'La bonne réponse était le That Luang : Grand stupa bouddhiste doré, monument national du Laos.'),
        ('Quelle est la capitale du Laos ?', ['Dacca', 'Singapour', 'Vientiane'], 2, 'La bonne réponse était Vientiane.'),
        ('Quelle est la monnaie utilisée au Laos ?', ['le kip', 'le dram arménien', 'la roupie népalaise'], 0, 'La bonne réponse était le kip.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Laos (médaillé d'argent en pétanque simple hommes aux SEA Games 2025, battu en finale par l'Indonésien Andri Irawan) ?", ['Jean-François « Zigle » Rakotondrainibe', 'Erik Bardelli', 'Southammavong Bountamy'], 2, "La bonne réponse était Southammavong Bountamy : médaillé d'argent en pétanque simple hommes aux SEA Games 2025, battu en finale par l'Indonésien Andri Irawan."),
    ],
    # 78 Malaisie
    [
        ("En quelle année la Malaisienne Nur Iman Aina binti Ahmad Sabti a-t-elle remporté l'argent au tir de précision femmes au championnat d'Asie de pétanque, à Kuala Lumpur ?", ['2025', '1984', '2012'], 0, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Malaisie (Gratte-ciel jumeaux de 452 m à Kuala Lumpur) ?', ['les tours Petronas', 'le Merlion', 'la tour Baïterek'], 0, 'La bonne réponse était les tours Petronas : Gratte-ciel jumeaux de 452 m à Kuala Lumpur.'),
        ('Quelle est la capitale de Malaisie ?', ['Pékin', 'Téhéran', 'Kuala Lumpur'], 2, 'La bonne réponse était Kuala Lumpur.'),
        ("En quelle année la Malaisie a-t-elle remporté l'or en triplette junior (Nation Cup) au championnat d'Asie de pétanque, disputé à domicile à Kuala Lumpur ?", ['1971', '2024', '2025'], 2, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Malaisie (médaillé de bronze au tir de précision hommes au championnat d'Asie de pétanque 2025, à domicile en Malaisie) ?", ['Muhamad Nuzul Azwan Ahmad Temizi', 'Katarzyna Błasiak', 'Melisa Polito et Renato Donoso'], 0, "La bonne réponse était Muhamad Nuzul Azwan Ahmad Temizi : médaillé de bronze au tir de précision hommes au championnat d'Asie de pétanque 2025, à domicile en Malaisie."),
    ],
    # 79 Mongolie
    [
        ('En quelle année la Fédération de Pétanque de Mongolie a-t-elle été créée ?', ['1991', '2012', '2010'], 1, 'La bonne réponse était 2012.'),
        ('Quel monument ou quelle spécialité est associé à Mongolie (Statue en acier de 40 m, la plus grande statue équestre du monde) ?', ['le Merlion', 'la statue équestre de Gengis Khan', 'le Taipei 101'], 1, 'La bonne réponse était la statue équestre de Gengis Khan : Statue en acier de 40 m, la plus grande statue équestre du monde.'),
        ('Quelle est la capitale de Mongolie ?', ['Oulan-Bator', 'Bangkok', 'Taipei'], 0, 'La bonne réponse était Oulan-Bator.'),
        ('Quelle est la monnaie utilisée en Mongolie ?', ['le tugrik', 'le ringgit', 'le dollar de Singapour'], 0, 'La bonne réponse était le tugrik.'),
        ("À quoi d'autre est associé Mongolie (Premier monastère bouddhiste de Mongolie, fondé en 1585 près de Kharkhorin) ?", ['le temple de Prambanan', "le monastère d'Erdene Zuu", 'les grottes de Batu'], 1, "La bonne réponse était le monastère d'Erdene Zuu : Premier monastère bouddhiste de Mongolie, fondé en 1585 près de Kharkhorin."),
    ],
    # 80 Myanmar
    [
        ('En quelle année la Fédération de Pétanque du Myanmar a-t-elle été créée ?', ['2013', '2025', '1958'], 0, 'La bonne réponse était 2013.'),
        ("Quel monument ou quelle spécialité est associé à Myanmar (Stupa bouddhiste recouvert de feuilles d'or à Yangon) ?", ['Sainte-Sophie', 'les Bouddhas de Bamiyan', 'la pagode Shwedagon'], 2, "La bonne réponse était la pagode Shwedagon : Stupa bouddhiste recouvert de feuilles d'or à Yangon."),
        ('Quelle est la capitale du Myanmar (Birmanie) ?', ['Naypyidaw', 'Phnom Penh', 'Singapour'], 0, 'La bonne réponse était Naypyidaw.'),
        ("En quelle année le Myanmar a-t-il remporté l'argent au tir de précision féminin de pétanque aux SEA Games ?", ['2007', '2025', '2022'], 1, 'La bonne réponse était 2025.'),
        ("À quoi d'autre est associé Myanmar (Ancienne capitale de royaume, plaine parsemée de plus de 2000 temples et pagodes bouddhiques des XIe-XIIIe siècles) ?", ['Bagan', 'le temple de Preah Vihear', 'le temple de Prambanan'], 0, 'La bonne réponse était Bagan : Ancienne capitale de royaume, plaine parsemée de plus de 2000 temples et pagodes bouddhiques des XIe-XIIIe siècles.'),
    ],
    # 81 Népal
    [
        ('En quelle année la Petanque Federation Nepal a-t-elle été créée ?', ['1996', '2012', '2024'], 1, 'La bonne réponse était 2012.'),
        ('Quel monument ou quelle spécialité est associé à Népal (Plus haut sommet du monde, à la frontière Népal-Tibet) ?', ["l'Everest", 'le Mont Fuji', 'les rizières de Banaue'], 0, "La bonne réponse était l'Everest : Plus haut sommet du monde, à la frontière Népal-Tibet."),
        ('Quelle est la capitale du Népal ?', ['Kuala Lumpur', 'Katmandou', 'Singapour'], 1, 'La bonne réponse était Katmandou.'),
        ('Quelle est la monnaie utilisée au Népal ?', ['la roupie népalaise', 'le ringgit', 'le kip'], 0, 'La bonne réponse était la roupie népalaise.'),
        ("À quoi d'autre est associé Népal (Lieu de naissance de Bouddha, site de pèlerinage bouddhiste classé UNESCO) ?", ['Lumbini', 'les grottes de Batu', 'le Minaret de Jam'], 0, 'La bonne réponse était Lumbini : Lieu de naissance de Bouddha, site de pèlerinage bouddhiste classé UNESCO.'),
    ],
    # 82 Pakistan
    [
        ('En quelle année la Pakistan Petanque Sports Boules Federation a-t-elle rejoint la FIPJP ?', ['2006', '2010', '1989'], 0, 'La bonne réponse était 2006.'),
        ("Quel monument ou quelle spécialité est associé à Pakistan (Cité antique de la civilisation de la vallée de l'Indus) ?", ['les ruines de Baalbek', 'les ruines de Mohenjo-daro', 'la tour Bourana'], 1, "La bonne réponse était les ruines de Mohenjo-daro : Cité antique de la civilisation de la vallée de l'Indus."),
        ('Quelle est la capitale du Pakistan ?', ['Islamabad', 'Singapour', 'Vientiane'], 0, 'La bonne réponse était Islamabad.'),
        ('Quelle est la monnaie utilisée au Pakistan ?', ['le rial iranien', 'la roupie pakistanaise', 'le baht'], 1, 'La bonne réponse était la roupie pakistanaise.'),
        ("À quoi d'autre est associé Pakistan (Construite en 1673 par l'empereur moghol Aurangzeb à Lahore, l'une des plus grandes mosquées du monde) ?", ['la mosquée Badshahi', 'Lumbini', 'le monastère de Guéghard'], 0, "La bonne réponse était la mosquée Badshahi : Construite en 1673 par l'empereur moghol Aurangzeb à Lahore, l'une des plus grandes mosquées du monde."),
    ],
    # 83 Philippines
    [
        ('En quelle année « Pétanque Pinas » a-t-elle été créée et affiliée à la FIPJP ?', ['2005', '2025', '2007'], 0, 'La bonne réponse était 2005.'),
        ('Quel monument ou quelle spécialité est associé à Philippines (Terrasses agricoles sculptées il y a environ 2000 ans) ?', ['les rizières de Banaue', 'le Mont Fuji', "la baie d'Halong"], 0, 'La bonne réponse était les rizières de Banaue : Terrasses agricoles sculptées il y a environ 2000 ans.'),
        ('Quelle est la capitale des Philippines ?', ['Kaboul', 'Manille', 'Kuala Lumpur'], 1, 'La bonne réponse était Manille.'),
        ('En quelle année les Philippines ont-elles remporté le bronze en double dames de pétanque aux SEA Games, seule médaille philippine cette année-là ?', ['2016', '2023', '1999'], 1, 'La bonne réponse était 2023.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Philippines (médaillées de bronze en pétanque double dames aux SEA Games 2025) ?', ['Katarzyna Błasiak', 'Diego Rizzi', 'Cesiel Domenios et Ma. Corazon Soberre'], 2, 'La bonne réponse était Cesiel Domenios et Ma. Corazon Soberre : médaillées de bronze en pétanque double dames aux SEA Games 2025.'),
    ],
    # 84 Singapour
    [
        ('En quelle année la fédération de pétanque de Singapour a-t-elle été créée ?', ['1989', '2013', '2005'], 0, 'La bonne réponse était 1989.'),
        ('Quel monument ou quelle spécialité est associé à Singapour (Statue mi-lion mi-poisson à Marina Bay, symbole de Singapour) ?', ['les tours Petronas', 'la statue équestre de Gengis Khan', 'le Merlion'], 2, 'La bonne réponse était le Merlion : Statue mi-lion mi-poisson à Marina Bay, symbole de Singapour.'),
        ('Quelle est la capitale de Singapour ?', ['Téhéran', 'Manille', 'Singapour'], 2, 'La bonne réponse était Singapour.'),
        ("En quelle année Singapour a-t-il remporté le bronze en triplette féminine (Nation Cup) au championnat d'Asie de pétanque ?", ['2025', '2007', '2019'], 0, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Singapour (membre de l'équipe de Singapour médaillée de bronze en triplette féminine (Nation Cup) au championnat d'Asie de pétanque 2025) ?", ['Trinh Thi Kim Thanh', 'Delys Brady', 'Tan Lay Tin'], 2, "La bonne réponse était Tan Lay Tin : membre de l'équipe de Singapour médaillée de bronze en triplette féminine (Nation Cup) au championnat d'Asie de pétanque 2025."),
    ],
    # 85 Taïwan
    [
        ("En quelle année le Taïwanais Wu Kun-Yu a-t-il remporté l'argent au tir de précision hommes au championnat d'Asie de pétanque ?", ['2023', '1990', '2025'], 2, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Taïwan (Gratte-ciel de 508 m, longtemps le plus haut bâtiment du monde) ?', ['le Taipei 101', 'la statue équestre de Gengis Khan', 'la tour Baïterek'], 0, 'La bonne réponse était le Taipei 101 : Gratte-ciel de 508 m, longtemps le plus haut bâtiment du monde.'),
        ('Quelle est la capitale de Taïwan (Chinese Taipei) ?', ['Ankara', 'Taipei', 'Singapour'], 1, 'La bonne réponse était Taipei.'),
        ("En quelle année Taïwan a-t-il remporté l'argent en triplette féminine (Nation Cup) au championnat d'Asie de pétanque ?", ['2017', '2019', '2025'], 2, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Taïwan (membre de l'équipe taïwanaise médaillée de bronze en triplette junior (Asian Cup) au championnat d'Asie de pétanque 2025) ?", ['Tsai Chih-Hsuan', 'Edward Vinke', 'Baba Conté'], 0, "La bonne réponse était Tsai Chih-Hsuan : membre de l'équipe taïwanaise médaillée de bronze en triplette junior (Asian Cup) au championnat d'Asie de pétanque 2025."),
    ],
    # 86 Thaïlande
    [
        ("En quelle année la Thaïlande a-t-elle remporté pour la première fois l'or mondial en triplette messieurs, en battant la France ?", ['2023', '2016', '2021'], 0, 'La bonne réponse était 2023.'),
        ("Quel monument ou quelle spécialité est associé à Thaïlande (Temple de l'Aube orné de porcelaine, sur le fleuve Chao Phraya) ?", ['le Wat Arun', 'les Bouddhas de Bamiyan', 'Angkor Vat'], 0, "La bonne réponse était le Wat Arun : Temple de l'Aube orné de porcelaine, sur le fleuve Chao Phraya."),
        ('Quelle est la capitale de Thaïlande ?', ['Bangkok', 'Tokyo', 'Kaboul'], 0, 'La bonne réponse était Bangkok.'),
        ("En quelle année la Thaïlande a-t-elle été la nation la plus titrée en pétanque aux SEA Games, avec 5 médailles d'or ?", ['2025', '2022', '2016'], 0, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Thaïlande (champion du monde de pétanque en simple messieurs en 2023, et champion d'Asie de tir de précision hommes en 2025) ?", ['Claire Wilson', 'Juan Moreno', 'Ratchata Khamdee'], 2, "La bonne réponse était Ratchata Khamdee : champion du monde de pétanque en simple messieurs en 2023, et champion d'Asie de tir de précision hommes en 2025."),
    ],
    # 87 Turkménistan
    [
        ('En quelle année la Fédération Nationale de Pétanque du Turkménistan a-t-elle été créée ?', ['1990', '2019', '2012'], 1, 'La bonne réponse était 2019.'),
        ('Quel monument ou quelle spécialité est associé à Turkménistan (Cratère gazier en combustion continue depuis 1971, désert du Karakoum) ?', ['les rizières de Banaue', "la Porte de l'Enfer", "la baie d'Halong"], 1, "La bonne réponse était la Porte de l'Enfer : Cratère gazier en combustion continue depuis 1971, désert du Karakoum."),
        ('Quelle est la capitale du Turkménistan ?', ['Astana', 'Beyrouth', 'Achgabat'], 2, 'La bonne réponse était Achgabat.'),
        ('Quelle est la monnaie utilisée au Turkménistan ?', ['le won sud-coréen', 'le manat turkmène', 'la roupie pakistanaise'], 1, 'La bonne réponse était le manat turkmène.'),
        ("À quoi d'autre est associé Turkménistan (Race chevaline ancienne de plus de 3000 ans, symbole national figurant sur les armoiries du Turkménistan) ?", ["le marché des féticheurs d'Akodessewa", 'le cheval Akhal-Teke', 'le Laulupidu'], 1, 'La bonne réponse était le cheval Akhal-Teke : Race chevaline ancienne de plus de 3000 ans, symbole national figurant sur les armoiries du Turkménistan.'),
    ],
    # 88 Vietnam
    [
        ('En quelle année le Vietnam a-t-il remporté son tout premier titre de championne du monde de pétanque en triplette féminine, à Bangkok ?', ['2006', '2012', '2023'], 2, 'La bonne réponse était 2023.'),
        ('Quel monument ou quelle spécialité est associé à Vietnam (Baie parsemée de près de 2000 îlots karstiques) ?', ["la baie d'Halong", 'les rizières de Banaue', "la Porte de l'Enfer"], 0, "La bonne réponse était la baie d'Halong : Baie parsemée de près de 2000 îlots karstiques."),
        ('Quelle est la capitale du Vietnam ?', ['Hanoï', 'Jérusalem', 'Katmandou'], 0, 'La bonne réponse était Hanoï.'),
        ('En quelle année le Vietnam a-t-il conservé son titre de champion du monde de pétanque en triplette féminine, à Sin-le-Noble (France) ?', ['2008', '2025', '2022'], 1, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Vietnam (membre de l'équipe vietnamienne devenue championne du monde de pétanque en triplette féminine en 2023, à Bangkok) ?", ['Zaidou Maoulida Mhamadi', 'Trinh Thi Kim Thanh', 'Nerijus Kukcinavičius'], 1, "La bonne réponse était Trinh Thi Kim Thanh : membre de l'équipe vietnamienne devenue championne du monde de pétanque en triplette féminine en 2023, à Bangkok."),
    ],
    # 89 Argentine
    [
        ('En quelle année la Fédération Argentine de Pétanque a-t-elle été créée ?', ['2007', '2002', '1990'], 1, 'La bonne réponse était 2002.'),
        ('Quel monument ou quelle spécialité est associé à Argentine (Ensemble de 275 cascades à la frontière avec le Brésil) ?', ["les chutes d'Iguazu", 'le volcan Arenal', 'le Salto Ángel'], 0, "La bonne réponse était les chutes d'Iguazu : Ensemble de 275 cascades à la frontière avec le Brésil."),
        ("Quelle est la capitale d'Argentine ?", ['Quito', 'Buenos Aires', 'Montevideo'], 1, 'La bonne réponse était Buenos Aires.'),
        ('Quelle est la monnaie utilisée en Argentine ?', ['le dollar américain', 'le peso argentin', 'le peso mexicain'], 1, 'La bonne réponse était le peso argentin.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Argentine (entraîneur de l'équipe nationale argentine de pétanque, médaillée de bronze au championnat panaméricain à Iquique (Chili)) ?", ['José Giménez', 'Sara Díaz Reyes', 'Amil Cordova'], 0, "La bonne réponse était José Giménez : entraîneur de l'équipe nationale argentine de pétanque, médaillée de bronze au championnat panaméricain à Iquique (Chili)."),
    ],
    # 90 Bolivie
    [
        ('En quelle année la Fédération Bolivienne de Petanque a-t-elle été affiliée à la FIPJP ?', ['2024', '2025', '2013'], 1, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Bolivie (Plus grand désert de sel du monde, effet miroir après la pluie) ?', ['le volcan Arenal', 'le Salar de Uyuni', "les chutes d'Iguazu"], 1, 'La bonne réponse était le Salar de Uyuni : Plus grand désert de sel du monde, effet miroir après la pluie.'),
        ('Quelle est la capitale de Bolivie ?', ['Sucre', 'Asuncion', 'Buenos Aires'], 0, 'La bonne réponse était Sucre.'),
        ('Quelle est la monnaie utilisée en Bolivie ?', ['le dollar américain', 'le sol péruvien', 'le boliviano'], 2, 'La bonne réponse était le boliviano.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Bolivie (président de la Fédération Bolivienne de Petanque) ?', ['Cesiel Domenios et Ma. Corazon Soberre', 'Florence Kanzié', 'Yerko Castro'], 2, 'La bonne réponse était Yerko Castro : président de la Fédération Bolivienne de Petanque.'),
    ],
    # 91 Canada
    [
        ('En quelle année la fédération canadienne de pétanque a-t-elle été créée (sous le nom de Fédération Canadienne Bouliste) ?', ['1955', '2025', '2013'], 0, 'La bonne réponse était 1955.'),
        ("Quel monument ou quelle spécialité est associé à Canada (Spectaculaires chutes d'eau à la frontière avec les États-Unis) ?", ['les îles Galápagos', 'les chutes du Niagara', 'le Salar de Uyuni'], 1, "La bonne réponse était les chutes du Niagara : Spectaculaires chutes d'eau à la frontière avec les États-Unis."),
        ('Quelle est la capitale du Canada ?', ['San José', 'Ottawa', 'Lima'], 1, 'La bonne réponse était Ottawa.'),
        ("En quelle année a eu lieu le championnat du monde de pétanque de Montauban, après lequel le Canada comptait 3 médailles d'argent et 4 de bronze (mais aucun titre) ?", ['1984', '2013', '2023'], 1, 'La bonne réponse était 2013.'),
        ("À quoi d'autre est associé Canada (Le Canada, et surtout le Québec, produit plus de 70% du sirop d'érable mondial) ?", ['le Sachertorte', "le sirop d'érable", 'la tequila'], 1, "La bonne réponse était le sirop d'érable : Le Canada, et surtout le Québec, produit plus de 70% du sirop d'érable mondial."),
    ],
    # 92 Chili
    [
        ("En quelle année le Chili a-t-il remporté l'argent en pétanque par équipe mixte aux Jeux Bolivariens, à Ayacucho (Pérou) ?", ['2024', '2005', '2025'], 0, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Chili (Statues monumentales du peuple Rapa Nui) ?', ['Tikal', "les Moaï de l'île de Pâques", 'le Machu Picchu'], 1, "La bonne réponse était les Moaï de l'île de Pâques : Statues monumentales du peuple Rapa Nui."),
        ('Quelle est la capitale du Chili ?', ['Sucre', 'Santiago', 'Asuncion'], 1, 'La bonne réponse était Santiago.'),
        ('Quelle est la monnaie utilisée au Chili ?', ['le peso chilien', 'le peso mexicain', 'le boliviano'], 0, 'La bonne réponse était le peso chilien.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Chili (médaillés d'argent en pétanque paire mixte aux Jeux Bolivariens d'Ayacucho, en 2024) ?", ['Marcel Bio, dit « Terrazini »', 'Claire Wilson', 'Melisa Polito et Renato Donoso'], 2, "La bonne réponse était Melisa Polito et Renato Donoso : médaillés d'argent en pétanque paire mixte aux Jeux Bolivariens d'Ayacucho, en 2024."),
    ],
    # 93 Colombie
    [
        ('En quelle année la Fédération Colombienne de Petanque a-t-elle été affiliée à la FIPJP ?', ['1972', '2019', '2025'], 2, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Colombie (Église souterraine sculptée dans une ancienne mine de sel) ?', ['la basilique Notre-Dame de la Paix', 'le mur des Lamentations', 'la cathédrale de Sel de Zipaquirá'], 2, 'La bonne réponse était la cathédrale de Sel de Zipaquirá : Église souterraine sculptée dans une ancienne mine de sel.'),
        ('Quelle est la capitale de Colombie ?', ['Asuncion', 'Bogota', 'Caracas'], 1, 'La bonne réponse était Bogota.'),
        ('Quelle est la monnaie utilisée en Colombie ?', ['le peso cubain', 'le réal brésilien', 'le peso colombien'], 2, 'La bonne réponse était le peso colombien.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Colombie (président de la Fédération Colombienne de Petanque) ?', ['Mikko Soikkeli', 'Mouna Béji', 'Gustavo Henao'], 2, 'La bonne réponse était Gustavo Henao : président de la Fédération Colombienne de Petanque.'),
    ],
    # 94 Costa Rica
    [
        ('Quel fait notable est associé à Costa Rica (Le Costa Rica est mondialement réputé pour la qualité de son café) ?', ['le cosmodrome de Baïkonour', 'le cuivre', 'le café'], 2, 'La bonne réponse était le café : Le Costa Rica est mondialement réputé pour la qualité de son café.'),
        ("Quel monument ou quelle spécialité est associé à Costa Rica (L'un des volcans les plus emblématiques d'Amérique centrale) ?", ['le Salar de Uyuni', 'le volcan Arenal', 'les chutes du Niagara'], 1, "La bonne réponse était le volcan Arenal : L'un des volcans les plus emblématiques d'Amérique centrale."),
        ('Quelle est la capitale du Costa Rica ?', ['San José', 'Santiago', 'Montevideo'], 0, 'La bonne réponse était San José.'),
        ('Quelle est la monnaie utilisée au Costa Rica ?', ['le colón costaricien', 'le guarani', 'le boliviano'], 0, 'La bonne réponse était le colón costaricien.'),
        ("À quoi d'autre est associé Costa Rica (Forêt tropicale d'altitude d'une biodiversité exceptionnelle, plus de 400 espèces d'oiseaux dont le quetzal resplendissant) ?", ['la réserve de forêt nuageuse de Monteverde', 'les éclairs du Catatumbo', 'le parc national Torres del Paine'], 0, "La bonne réponse était la réserve de forêt nuageuse de Monteverde : Forêt tropicale d'altitude d'une biodiversité exceptionnelle, plus de 400 espèces d'oiseaux dont le quetzal resplendissant."),
    ],
    # 95 Cuba
    [
        ('En quelle année la Fédération Cuba Pétanque a-t-elle été créée et affiliée à la FIPJP ?', ['2021', '1958', '2013'], 2, 'La bonne réponse était 2013.'),
        ('Quel monument ou quelle spécialité est associé à Cuba (Spécialité artisanale roulée à la main, région de Viñales) ?', ['les cigares cubains (Habanos)', 'le Jamdani', 'le sauna'], 0, 'La bonne réponse était les cigares cubains (Habanos) : Spécialité artisanale roulée à la main, région de Viñales.'),
        ('Quelle est la capitale de Cuba ?', ['Buenos Aires', 'Saint-Domingue', 'La Havane'], 2, 'La bonne réponse était La Havane.'),
        ('Quelle est la monnaie utilisée à Cuba ?', ['le peso cubain', 'le boliviano', 'le sol péruvien'], 0, 'La bonne réponse était le peso cubain.'),
        ("À quoi d'autre est associé Cuba (Centre historique colonial de La Havane, architecture baroque et néoclassique, classé UNESCO) ?", ['le quartier historique de Colonia del Sacramento', 'Antigua Guatemala', 'La Havane Vieille'], 2, 'La bonne réponse était La Havane Vieille : Centre historique colonial de La Havane, architecture baroque et néoclassique, classé UNESCO.'),
    ],
    # 96 Équateur
    [
        ('Quel fait notable est associé à Équateur (Monument marquant le passage de la ligne équatoriale près de Quito, qui a donné son nom au pays) ?', ['les chutes de Boali', 'le café', 'la Mitad del Mundo'], 2, 'La bonne réponse était la Mitad del Mundo : Monument marquant le passage de la ligne équatoriale près de Quito, qui a donné son nom au pays.'),
        ('Quel monument ou quelle spécialité est associé à Équateur (Archipel volcanique à la faune endémique qui a inspiré Darwin) ?', ["les chutes d'Iguazu", 'les chutes du Niagara', 'les îles Galápagos'], 2, 'La bonne réponse était les îles Galápagos : Archipel volcanique à la faune endémique qui a inspiré Darwin.'),
        ("Quelle est la capitale d'Équateur ?", ['Quito', 'Mexico', 'Ottawa'], 0, 'La bonne réponse était Quito.'),
        ('Quelle est la monnaie utilisée en Équateur ?', ['le peso uruguayen', 'le dollar américain', 'le peso mexicain'], 1, 'La bonne réponse était le dollar américain.'),
        ("À quoi d'autre est associé Équateur (Chapeau tissé à la main en paille toquilla, en réalité originaire d'Équateur et non du Panama) ?", ['le larimar', 'le chapeau « Panama » de Montecristi', 'le Laulupidu'], 1, "La bonne réponse était le chapeau « Panama » de Montecristi : Chapeau tissé à la main en paille toquilla, en réalité originaire d'Équateur et non du Panama."),
    ],
    # 97 États-Unis
    [
        ("En quelle année les États-Unis ont-ils remporté leur toute première médaille d'or internationale en pétanque, aux World Games de Birmingham, grâce à Stefan Nicolas ?", ['1999', '2013', '2022'], 2, 'La bonne réponse était 2022.'),
        ("Quel monument ou quelle spécialité est associé à États-Unis (Offerte par la France, à l'entrée du port de New York) ?", ['« La Mano »', 'la Statue de la Liberté', 'le Christ Rédempteur'], 1, "La bonne réponse était la Statue de la Liberté : Offerte par la France, à l'entrée du port de New York."),
        ('Quelle est la capitale des États-Unis ?', ['Brasília', 'Washington', 'San José'], 1, 'La bonne réponse était Washington.'),
        ('Quelle est la monnaie utilisée aux États-Unis ?', ['le colón costaricien', 'le dollar américain', 'le sol péruvien'], 1, 'La bonne réponse était le dollar américain.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à États-Unis (première Amérindienne (nation Crow Creek Sioux) à remporter une médaille internationale de pétanque : argent au tir de précision individuel dames aux World Games de Birmingham en 2022) ?', ['José Giménez', 'Rebekah « Bekah » Howe', 'Maris Newerkla'], 1, 'La bonne réponse était Rebekah « Bekah » Howe : première Amérindienne (nation Crow Creek Sioux) à remporter une médaille internationale de pétanque : argent au tir de précision individuel dames aux World Games de Birmingham en 2022.'),
    ],
    # 98 Guatemala
    [
        ('Quel fait notable est associé à Guatemala (Le Guatemala est réputé pour ses tissages traditionnels mayas très colorés) ?', ['le saut au gôl (Naghol)', 'le fleuve Congo', "l'artisanat textile maya"], 2, "La bonne réponse était l'artisanat textile maya : Le Guatemala est réputé pour ses tissages traditionnels mayas très colorés."),
        ('Quel monument ou quelle spécialité est associé à Guatemala (Ancienne cité maya dans la jungle, temples-pyramides) ?', ['Tikal', 'les ruines jésuites de Trinidad', "les Moaï de l'île de Pâques"], 0, 'La bonne réponse était Tikal : Ancienne cité maya dans la jungle, temples-pyramides.'),
        ('Quelle est la capitale du Guatemala ?', ['Guatemala Ciudad', 'Buenos Aires', 'Brasília'], 0, 'La bonne réponse était Guatemala Ciudad.'),
        ('Quelle est la monnaie utilisée au Guatemala ?', ['la gourde', 'le boliviano', 'le quetzal'], 2, 'La bonne réponse était le quetzal.'),
        ("À quoi d'autre est associé Guatemala (Ancienne capitale coloniale espagnole fondée en 1543, célèbre pour son architecture baroque, classée UNESCO) ?", ['La Havane Vieille', 'Antigua Guatemala', "le barrage d'Itaipu"], 1, 'La bonne réponse était Antigua Guatemala : Ancienne capitale coloniale espagnole fondée en 1543, célèbre pour son architecture baroque, classée UNESCO.'),
    ],
    # 99 Haïti
    [
        ('En quelle année la Fédération Haïtienne de Sport Boules a-t-elle été créée ?', ['2023', '2016', '2010'], 2, 'La bonne réponse était 2010.'),
        ('Quel monument ou quelle spécialité est associé à Haïti (Plus grande forteresse des Amériques, construite par Henri Christophe) ?', ['la Zone coloniale de Saint-Domingue', 'le château de Bran', 'la Citadelle Laferrière'], 2, 'La bonne réponse était la Citadelle Laferrière : Plus grande forteresse des Amériques, construite par Henri Christophe.'),
        ('Quelle est la capitale de Haïti ?', ['Port-au-Prince', 'Guatemala Ciudad', 'Quito'], 0, 'La bonne réponse était Port-au-Prince.'),
        ('Quelle est la monnaie utilisée en Haïti ?', ['le colón costaricien', 'la gourde', 'le peso dominicain'], 1, 'La bonne réponse était la gourde.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Haïti (président de la Fédération Haïtienne de Sport Boules) ?', ['Dieufils Pierre', 'Andriy Kameniev', 'J-Y Robic'], 0, 'La bonne réponse était Dieufils Pierre : président de la Fédération Haïtienne de Sport Boules.'),
    ],
    # 100 Mexique
    [
        ('En quelle année le Mexique a-t-il participé pour la première fois au championnat du monde de pétanque en triplette masculine, à Marseille ?', ['1994', '2024', '2012'], 2, 'La bonne réponse était 2012.'),
        ('Quel monument ou quelle spécialité est associé à Mexique (Cité maya-toltèque célèbre pour sa pyramide El Castillo) ?', ["les Moaï de l'île de Pâques", 'Chichén Itzá', 'les ruines jésuites de Trinidad'], 1, 'La bonne réponse était Chichén Itzá : Cité maya-toltèque célèbre pour sa pyramide El Castillo.'),
        ('Quelle est la capitale du Mexique ?', ['Santiago', 'Mexico', 'Ottawa'], 1, 'La bonne réponse était Mexico.'),
        ('En quelle année la Federación Mexicana de Petanca a-t-elle été fondée ?', ['2025', '2011', '2023'], 1, 'La bonne réponse était 2011.'),
        ("À quoi d'autre est associé Mexique (Spiritueux issu de l'agave bleue, produit exclusivement dans la région de Jalisco, paysage agavier classé UNESCO) ?", ["le sirop d'érable", 'le Sachertorte', 'la tequila'], 2, "La bonne réponse était la tequila : Spiritueux issu de l'agave bleue, produit exclusivement dans la région de Jalisco, paysage agavier classé UNESCO."),
    ],
    # 101 Paraguay
    [
        ("Quel fait notable est associé à Paraguay (L'un des plus grands barrages hydroélectriques du monde, partagé entre le Paraguay et le Brésil) ?", ['la bauxite', 'le lapis-lazuli', "le barrage d'Itaipu"], 2, "La bonne réponse était le barrage d'Itaipu : L'un des plus grands barrages hydroélectriques du monde, partagé entre le Paraguay et le Brésil."),
        ("Quel monument ou quelle spécialité est associé à Paraguay (Vestiges d'une mission jésuite du XVIIIe siècle) ?", ['les ruines jésuites de Trinidad', 'le Machu Picchu', 'Chichén Itzá'], 0, "La bonne réponse était les ruines jésuites de Trinidad : Vestiges d'une mission jésuite du XVIIIe siècle."),
        ('Quelle est la capitale du Paraguay ?', ['Saint-Domingue', 'Asuncion', 'Quito'], 1, 'La bonne réponse était Asuncion.'),
        ('Quelle est la monnaie utilisée au Paraguay ?', ['le dollar américain', 'le guarani', 'le colón costaricien'], 1, 'La bonne réponse était le guarani.'),
        ("À quoi d'autre est associé Paraguay (Barrage hydroélectrique binational Paraguay-Brésil, l'un des plus puissants au monde, fournissant près de 90% de l'électricité du Paraguay) ?", ["le barrage d'Itaipu", 'Antigua Guatemala', 'La Havane Vieille'], 0, "La bonne réponse était le barrage d'Itaipu : Barrage hydroélectrique binational Paraguay-Brésil, l'un des plus puissants au monde, fournissant près de 90% de l'électricité du Paraguay."),
    ],
    # 102 Pérou
    [
        ("En quelle année la Péruvienne Rosalba Rojas a-t-elle remporté l'or en pétanque individuelle dames aux Jeux Bolivariens, à Ayacucho ?", ['1955', '2024', '2010'], 1, 'La bonne réponse était 2024.'),
        ('Quel monument ou quelle spécialité est associé à Pérou (Cité inca perchée dans les Andes péruviennes) ?', ['Chichén Itzá', 'le Machu Picchu', 'Tikal'], 1, 'La bonne réponse était le Machu Picchu : Cité inca perchée dans les Andes péruviennes.'),
        ('Quelle est la capitale du Pérou ?', ['Montevideo', 'Brasília', 'Lima'], 2, 'La bonne réponse était Lima.'),
        ('Quelle est la monnaie utilisée au Pérou ?', ['le sol péruvien', 'le peso uruguayen', 'le peso dominicain'], 0, 'La bonne réponse était le sol péruvien.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Pérou (finaliste (médaille d'argent) en pétanque individuelle messieurs aux Jeux Bolivariens d'Ayacucho, en 2024, battu par le Vénézuélien José Manuel Marcano) ?", ['Tsai Chih-Hsuan', 'Erik Bardelli', 'Amil Cordova'], 1, "La bonne réponse était Erik Bardelli : finaliste (médaille d'argent) en pétanque individuelle messieurs aux Jeux Bolivariens d'Ayacucho, en 2024, battu par le Vénézuélien José Manuel Marcano."),
    ],
    # 103 République Dominicaine
    [
        ('En quelle année la Federación Dominicana de Bochas (FEDOBOCHAS) a-t-elle été affiliée à la FIPJP ?', ['1987', '2003', '1991'], 1, 'La bonne réponse était 2003.'),
        ('Quel monument ou quelle spécialité est associé à République Dominicaine (Premier centre urbain européen des Amériques) ?', ['la Citadelle Laferrière', 'la Zone coloniale de Saint-Domingue', 'le château de Caernarfon'], 1, 'La bonne réponse était la Zone coloniale de Saint-Domingue : Premier centre urbain européen des Amériques.'),
        ('Quelle est la capitale de République Dominicaine ?', ['Saint-Domingue', 'Buenos Aires', 'Ottawa'], 0, 'La bonne réponse était Saint-Domingue.'),
        ('En quelle année la République Dominicaine a-t-elle participé au Championnat Panaméricain de pétanque de Limache (Chili) ?', ['2015', '2016', '2023'], 2, 'La bonne réponse était 2023.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à République Dominicaine (coordinateur de la République Dominicaine au sein de la Confédération Panaméricaine de Pétanque) ?', ['Abdessamad El Mankari', 'Zaidou Maoulida Mhamadi', 'Juan Moreno'], 2, 'La bonne réponse était Juan Moreno : coordinateur de la République Dominicaine au sein de la Confédération Panaméricaine de Pétanque.'),
    ],
    # 104 Uruguay
    [
        ('En quelle année la Federación Uruguaya de Bochas a-t-elle été fondée ?', ['1930', '1958', '2009'], 0, 'La bonne réponse était 1930.'),
        ("Quel monument ou quelle spécialité est associé à Uruguay (Sculpture d'une main enfoncée dans le sable, à Punta del Este) ?", ['la Statue de la Liberté', 'le Christ Rédempteur', '« La Mano »'], 2, "La bonne réponse était « La Mano » : Sculpture d'une main enfoncée dans le sable, à Punta del Este."),
        ("Quelle est la capitale d'Uruguay ?", ['Guatemala Ciudad', 'Caracas', 'Montevideo'], 2, 'La bonne réponse était Montevideo.'),
        ('Quelle est la monnaie utilisée en Uruguay ?', ['le peso colombien', 'le peso argentin', 'le peso uruguayen'], 2, 'La bonne réponse était le peso uruguayen.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Uruguay (président de la Fédération Uruguayenne de Bochas (pétanque)) ?', ['Fredy Isaias', 'Sok Chanmean', 'François Fara Ndiaye'], 0, 'La bonne réponse était Fredy Isaias : président de la Fédération Uruguayenne de Bochas (pétanque).'),
    ],
    # 105 Venezuela
    [
        ("En quelle année le Venezuela a-t-il remporté l'or en pétanque par équipe mixte aux Jeux Bolivariens, à Ayacucho (Pérou) ?", ['2004', '2022', '2024'], 2, 'La bonne réponse était 2024.'),
        ("Quel monument ou quelle spécialité est associé à Venezuela (Plus haute chute d'eau du monde (979 m), parc national Canaima) ?", ['les chutes du Niagara', 'le Salto Ángel', 'les îles Galápagos'], 1, "La bonne réponse était le Salto Ángel : Plus haute chute d'eau du monde (979 m), parc national Canaima."),
        ('Quelle est la capitale du Venezuela ?', ['Caracas', 'Santiago', 'Ottawa'], 0, 'La bonne réponse était Caracas.'),
        ('Quelle est la monnaie utilisée au Venezuela ?', ['le peso uruguayen', 'le bolivar', 'le réal brésilien'], 1, 'La bonne réponse était le bolivar.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Venezuela (médaillé d'or en pétanque individuelle messieurs aux Jeux Bolivariens d'Ayacucho, en 2024) ?", ['Juan Moreno', 'Andri Irawan', 'José Manuel Marcano'], 2, "La bonne réponse était José Manuel Marcano : médaillé d'or en pétanque individuelle messieurs aux Jeux Bolivariens d'Ayacucho, en 2024."),
    ],
    # 106 Australie
    [
        ('En quelle année la Fédération Australienne de Pétanque a-t-elle rejoint la FIPJP ?', ['1945', '1990', '1984'], 1, 'La bonne réponse était 1990.'),
        ('Quel monument ou quelle spécialité est associé à Australie (Célèbre bâtiment aux voiles blanches en forme de coquillages) ?', ['les moulins de Kinderdijk', 'le Parlement de Budapest', "l'Opéra de Sydney"], 2, "La bonne réponse était l'Opéra de Sydney : Célèbre bâtiment aux voiles blanches en forme de coquillages."),
        ("Quelle est la capitale d'Australie ?", ['Canberra', 'Nouméa', 'Port-Vila'], 0, 'La bonne réponse était Canberra.'),
        ("En quelle année l'Australie a-t-elle remporté 4 médailles à l'Oceania Championship de pétanque, en Nouvelle-Calédonie ?", ['2016', '2023', '2022'], 1, 'La bonne réponse était 2023.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Australie (médaillée de bronze en pointage femmes à l'Oceania Championship de pétanque en 2025) ?", ['Melisa Polito et Renato Donoso', 'José Manuel Marcano', 'Delys Brady'], 2, "La bonne réponse était Delys Brady : médaillée de bronze en pointage femmes à l'Oceania Championship de pétanque en 2025."),
    ],
    # 107 Nouvelle-Calédonie
    [
        ('En quelle année la Fédération de Nouvelle-Calédonie de pétanque a-t-elle été créée et a rejoint la FIPJP ?', ['2004', '2013', '2024'], 1, 'La bonne réponse était 2013.'),
        ("Quel monument ou quelle spécialité est associé à Nouvelle-Calédonie (Plat traditionnel kanak cuit à l'étouffée sous des pierres chaudes) ?", ['le poisson cru au lait de coco', 'le kimchi', 'le bougna'], 2, "La bonne réponse était le bougna : Plat traditionnel kanak cuit à l'étouffée sous des pierres chaudes."),
        ('Quelle est la capitale de Nouvelle-Calédonie ?', ['Port-Vila', 'Papeete', 'Nouméa'], 2, 'La bonne réponse était Nouméa.'),
        ("En quelle année les hommes de Nouvelle-Calédonie ont-ils remporté l'or au tir de précision à l'Oceania Championship de pétanque, à Wallis ?", ['2003', '2007', '2025'], 2, 'La bonne réponse était 2025.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Nouvelle-Calédonie (joueur des « Cagous », triple champion d'Océanie de pétanque en triplette) ?", ['Toma Wai', 'Salif Kourouma', 'J-Y Robic'], 0, "La bonne réponse était Toma Wai : joueur des « Cagous », triple champion d'Océanie de pétanque en triplette."),
    ],
    # 108 Nouvelle-Zélande
    [
        ("En quelle année Petanque New Zealand a-t-elle été fondée, lors d'une réunion à l'Atomic Café d'Auckland ?", ['1992', '1993', '1964'], 1, 'La bonne réponse était 1993.'),
        ('Quel monument ou quelle spécialité est associé à Nouvelle-Zélande (Fjord du Fiordland aux falaises abruptes et à la cascade Stirling Falls) ?', ['le volcan Yasur', 'le lac Assal', 'Milford Sound'], 2, 'La bonne réponse était Milford Sound : Fjord du Fiordland aux falaises abruptes et à la cascade Stirling Falls.'),
        ('Quelle est la capitale de Nouvelle-Zélande ?', ['Canberra', 'Mata-Utu', 'Wellington'], 2, 'La bonne réponse était Wellington.'),
        ("En quelle année la Nouvelle-Zélande a-t-elle remporté six médailles d'or à l'Oceania Championship de pétanque, à Rotorua ?", ['2021', '2005', '2025'], 1, 'La bonne réponse était 2005.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Nouvelle-Zélande (médaillée d'or en pointage femmes à l'Oceania Championship de pétanque en 2017) ?", ['Tarek Akili', 'Claire Wilson', 'Southammavong Bountamy'], 1, "La bonne réponse était Claire Wilson : médaillée d'or en pointage femmes à l'Oceania Championship de pétanque en 2017."),
    ],
    # 109 Tahiti
    [
        ('En quelle année le Polynésien Jean Manéa a-t-il été vice-champion du monde de tir de précision de pétanque, à Izmir (Turquie) ?', ['2004', '2007', '2010'], 2, 'La bonne réponse était 2010.'),
        ('Quel monument ou quelle spécialité est associé à Tahiti (Thon cru mariné au citron vert et au lait de coco, plat emblématique de Tahiti) ?', ['le poisson cru au lait de coco', 'le bougna', 'le kimchi'], 0, 'La bonne réponse était le poisson cru au lait de coco : Thon cru mariné au citron vert et au lait de coco, plat emblématique de Tahiti.'),
        ('Quelle est la capitale de Tahiti ?', ['Papeete', 'Port-Vila', 'Nouméa'], 0, 'La bonne réponse était Papeete.'),
        ("En quelle année la délégation polynésienne de pétanque a-t-elle réalisé tous les podiums et terminé 1ère à l'Oceania Championship, organisé à Wallis-et-Futuna ?", ['1998', '2007', '2025'], 2, 'La bonne réponse était 2025.'),
        ("À quoi d'autre est associé Tahiti (Ancien centre cérémoniel et politique majeur de la civilisation polynésienne, sur l'île de Raiatea, classé UNESCO) ?", ['le Mont-Saint-Michel', 'la mosquée Badshahi', 'le marae Taputapuatea'], 2, "La bonne réponse était le marae Taputapuatea : Ancien centre cérémoniel et politique majeur de la civilisation polynésienne, sur l'île de Raiatea, classé UNESCO."),
    ],
    # 110 Vanuatu
    [
        ("Quel fait notable est associé à Vanuatu (Rituel de saut à la liane sur l'île de Pentecôte, considéré comme l'ancêtre du saut à l'élastique) ?", ['le saut au gôl (Naghol)', 'le lapis-lazuli', "le barrage d'Itaipu"], 0, "La bonne réponse était le saut au gôl (Naghol) : Rituel de saut à la liane sur l'île de Pentecôte, considéré comme l'ancêtre du saut à l'élastique."),
        ("Quel monument ou quelle spécialité est associé à Vanuatu (Volcan actif de l'île de Tanna, surnommé « le phare du Pacifique ») ?", ['le volcan Yasur', 'Milford Sound', 'le Loch Ness'], 0, "La bonne réponse était le volcan Yasur : Volcan actif de l'île de Tanna, surnommé « le phare du Pacifique »."),
        ('Quelle est la capitale du Vanuatu ?', ['Wellington', 'Nouméa', 'Port-Vila'], 2, 'La bonne réponse était Port-Vila.'),
        ('Quelle est la monnaie utilisée au Vanuatu ?', ['le dollar australien', 'le franc CFP', 'le vatu'], 2, 'La bonne réponse était le vatu.'),
        ("À quoi d'autre est associé Vanuatu (Rituel initiatique de l'île de Pentecôte : des hommes sautent d'une tour en bois de 20 à 30 mètres retenus aux chevilles par des lianes) ?", ['le saut du Gol', 'le larimar', 'le cheval Akhal-Teke'], 0, "La bonne réponse était le saut du Gol : Rituel initiatique de l'île de Pentecôte : des hommes sautent d'une tour en bois de 20 à 30 mètres retenus aux chevilles par des lianes."),
    ],
    # 111 Wallis-et-Futuna
    [
        ('En quelle année les Océania de pétanque ont-ils eu lieu à Wallis, où Futuna a remporté le titre en triplette dames pour la première fois seule ?', ['2025', '2005', '2010'], 0, 'La bonne réponse était 2025.'),
        ('Quel monument ou quelle spécialité est associé à Wallis-et-Futuna (Construite en pierre de lave et corail à Mata-Utu) ?', ['Borobudur', "la cathédrale Notre-Dame de l'Assomption", 'la pagode Shwedagon'], 1, "La bonne réponse était la cathédrale Notre-Dame de l'Assomption : Construite en pierre de lave et corail à Mata-Utu."),
        ('Quelle est la capitale de Wallis-et-Futuna ?', ['Wellington', 'Mata-Utu', 'Nouméa'], 1, 'La bonne réponse était Mata-Utu.'),
        ('Quelle est la monnaie utilisée à Wallis-et-Futuna ?', ['le franc CFP', 'le vatu', 'le dollar néo-zélandais'], 0, 'La bonne réponse était le franc CFP.'),
        ("Quel joueur ou quelle joueuse de pétanque est associé(e) à Wallis-et-Futuna (joueuse wallisienne réputée invaincue aux championnats d'Océanie de pétanque pendant huit ans, triple médaillée d'or à l'Oceania Championship de 2017) ?", ['Abdessamad El Mankari', 'Tofata Tautapu', 'François Fara Ndiaye'], 1, "La bonne réponse était Tofata Tautapu : joueuse wallisienne réputée invaincue aux championnats d'Océanie de pétanque pendant huit ans, triple médaillée d'or à l'Oceania Championship de 2017."),
    ],
    # 112 Brésil
    [
        ('En quelle année la Confédération Brésilienne de Bocha e Bolão (regroupant la pétanque, le raffa et le zerbin) a-t-elle été fondée ?', ['2023', '1989', '1991'], 2, 'La bonne réponse était 1991.'),
        ('Quel monument ou quelle spécialité est associé à Brésil (Statue monumentale du Christ dominant Rio de Janeiro depuis le sommet du Corcovado) ?', ['« La Mano »', 'le Christ Rédempteur', 'la Statue de la Liberté'], 1, 'La bonne réponse était le Christ Rédempteur : Statue monumentale du Christ dominant Rio de Janeiro depuis le sommet du Corcovado.'),
        ('Quelle est la capitale du Brésil ?', ['Guatemala Ciudad', 'Mexico', 'Brasília'], 2, 'La bonne réponse était Brasília.'),
        ('Quelle est la monnaie utilisée au Brésil ?', ['le peso uruguayen', 'le réal brésilien', 'le quetzal'], 1, 'La bonne réponse était le réal brésilien.'),
        ("À quoi d'autre est associé Brésil (Impressionnantes chutes d'eau à la frontière du Brésil et de l'Argentine, parmi les plus larges au monde) ?", ["les chutes d'Iguaçu", 'le glacier Perito Moreno', 'le Grand Canyon'], 0, "La bonne réponse était les chutes d'Iguaçu : Impressionnantes chutes d'eau à la frontière du Brésil et de l'Argentine, parmi les plus larges au monde."),
    ],
    # 113 Israël
    [
        ('En quelle année la fédération israélienne de pétanque a-t-elle été reconnue lors du Congrès de la FIPJP, à Rome ?', ['1993', '2004', '1992'], 2, 'La bonne réponse était 1992.'),
        ('Quel monument ou quelle spécialité est associé à Israël (Vestige du second Temple de Jérusalem, lieu de prière et de pèlerinage parmi les plus visités au monde) ?', ['Angkor Vat', 'le mur des Lamentations', 'le That Luang'], 1, 'La bonne réponse était le mur des Lamentations : Vestige du second Temple de Jérusalem, lieu de prière et de pèlerinage parmi les plus visités au monde.'),
        ('En quelle année Israël est-il devenu membre fondateur de la Confédération Asiatique des Sports Boules (APSBC) ?', ['1997', '1990', '2025'], 0, 'La bonne réponse était 1997.'),
        ('Quelle est la monnaie utilisée en Israël ?', ['le tugrik', 'le nouveau shekel israélien', 'le nouveau dollar taïwanais'], 1, 'La bonne réponse était le nouveau shekel israélien.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Israël (président de la Fédération Israélienne de Pétanque) ?', ['Myriam Chambeiron et Laura Vierjon', 'Baba Conté', 'Amil Cordova'], 2, 'La bonne réponse était Amil Cordova : président de la Fédération Israélienne de Pétanque.'),
    ],
    # 114 Liban
    [
        ("En quelle année le Liban a-t-il disputé un tournoi préliminaire des Championnats du Monde de pétanque, à Dijon (France), aux côtés de l'Écosse, l'Estonie, la Lettonie, la Norvège et l'Ukraine ?", ['1993', '2000', '2024'], 2, 'La bonne réponse était 2024.'),
        ("Quel monument ou quelle spécialité est associé à Liban (Vaste complexe de temples romains antiques, l'un des mieux conservés au monde) ?", ['Persépolis', 'la tour Bourana', 'les ruines de Baalbek'], 2, "La bonne réponse était les ruines de Baalbek : Vaste complexe de temples romains antiques, l'un des mieux conservés au monde."),
        ('Quelle est la capitale du Liban ?', ['Beyrouth', 'Kaboul', 'Hanoï'], 0, 'La bonne réponse était Beyrouth.'),
        ('Quelle est la monnaie utilisée au Liban ?', ['le ringgit', 'le yen', 'la livre libanaise'], 2, 'La bonne réponse était la livre libanaise.'),
        ('Quel joueur ou quelle joueuse de pétanque est associé(e) à Liban (président et chef du comité exécutif de la Fédération Libanaise de Pétanque) ?', ['Toma Wai', 'George Gebrael', 'Zaidou Maoulida Mhamadi'], 1, 'La bonne réponse était George Gebrael : président et chef du comité exécutif de la Fédération Libanaise de Pétanque.'),
    ],
]
