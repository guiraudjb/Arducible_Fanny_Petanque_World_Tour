"""Généré automatiquement par build_world_tour_dialogues_module.py 
à partir de fanny wold tour/speach.txt + pays_index.txt. 
Ne pas éditer à la main : relancer le script après modification des sources."""

WORLD_TOUR_COUNTRIES = [
    ("Allemagne", "allemagne", "Coucou depuis l'Allemagne ! Ici, la pétanque se joue souvent après le travail, entre deux chopes de bière, dans des clubs affiliés à la Fédération allemande, membre de la Confédération Européenne de Pétanque."),
    ("Andorre", "andorre", "Perchée dans les Pyrénées, l'Andorre a aussi sa fédération de pétanque ! Un petit pays, mais des boulodromes qui grimpent jusque dans la montagne."),
    ("Angleterre", "angleterre", "En Angleterre, on appelle ça 'petanque' sans accent, et on y joue volontiers sur le green du village, juste à côté du terrain de cricket !"),
    ("Arménie", "armenie", "En Arménie, la pétanque est une discipline plus récente mais bien organisée, avec le mont Ararat en toile de fond pour les parties les plus spectaculaires !"),
    ("Autriche", "autriche", "En Autriche, entre deux randonnées dans les Alpes, les clubs de pétanque affiliés à la CEP se retrouvent pour des concours conviviaux."),
    ("Belgique", "belgique", "En Belgique, la pétanque est une histoire de famille : nos voisins belges ont été champions du monde en 1981 et en 2000, et Charles Weibel a même décroché le titre mondial de tête-à-tête en 2015 !"),
    ("Bulgarie", "bulgarie", "En Bulgarie, la pétanque se joue aussi près des champs de roses ! Un club discret mais bien vivant, affilié à la fédération européenne."),
    ("Danemark", "danemark", "Au Danemark, on joue à la pétanque sur les quais, entre deux maisons colorées, dans une ambiance toujours détendue et hyggelig."),
    ("Écosse", "ecosse", "En Écosse, la pétanque partage parfois le terrain avec le lancer de troncs ! Un joli mélange de traditions écossaises et provençales."),
    ("Espagne", "espagne", "En Espagne, la pétanque se joue volontiers sur la plaza du village, sous le soleil — l'Espagne a même été championne du monde en 1971, et Jesús Escacho Alarcón a décroché le titre mondial de tête-à-tête en 2022 !"),
    ("Estonie", "estonie", "En Estonie, les boulodromes sont plus rares, mais la fédération locale grandit doucement au sein de la Confédération Européenne de Pétanque."),
    ("Finlande", "finlande", "En Finlande, on joue à la pétanque même sous le soleil de minuit, entre deux passages au sauna !"),
    ("France", "france", "Ici, chez moi, en France, tout a commencé en 1907 à La Ciotat ! Jules Lenoir, trop rhumatisant pour courir, a joué 'les pieds tanqués' — et la pétanque était née. La France reste la nation la plus titrée du monde, avec près de trente titres mondiaux !"),
    ("Guernesey", "guernesey", "Sur l'île de Guernesey, la pétanque se joue face à la mer — un petit territoire mais une vraie fédération affiliée à la CEP !"),
    ("Hongrie", "hongrie", "En Hongrie, on troque parfois les bains thermaux contre un concours de pétanque au bord du Danube !"),
    ("Irlande", "irlande", "En Irlande, la pétanque se joue parfois juste à côté du pub — histoire de refaire la partie autour d'une pinte ensuite !"),
    ("Italie", "italie", "En Italie, la pétanque cousine avec les bocce, mais elle a bel et bien sa propre fédération — championne du monde en 1975, 1978, 1979 et 2024, et Diego Rizzi a décroché le titre mondial de tête-à-tête en 2025 !"),
    ("Jersey", "jersey", "Sur l'île de Jersey, tout comme à Guernesey, la pétanque a ses propres clubs, juste en face des côtes françaises !"),
    ("Lettonie", "lettonie", "En Lettonie, la pétanque reste discrète mais bien réelle, portée par une poignée de clubs passionnés à Riga."),
    ("Lituanie", "lituanie", "En Lituanie, la fédération de pétanque est jeune, mais elle grandit doucement au fil des rencontres européennes."),
    ("Luxembourg", "luxembourg", "Au Luxembourg, petit pays mais grand cœur bouliste : la pétanque y est pratiquée avec sérieux dans plusieurs clubs actifs."),
    ("Monaco", "monaco", "À Monaco, on joue à la pétanque avec vue sur le port et les yachts — so chic, mais toujours fidèle à l'esprit provençal, et même championne du monde en 1982 !"),
    ("Norvège", "norvege", "En Norvège, même au bord des fjords, quelques irréductibles se retrouvent pour une partie de pétanque entre deux aurores boréales !"),
    ("Pays-Bas", "pays_bas", "Aux Pays-Bas, on joue à la pétanque au bord des canaux, entre deux champs de tulipes et quelques moulins à vent."),
    ("Pays de Galles", "pays_de_galles", "Au Pays de Galles, la pétanque se joue à l'ombre des châteaux — un joli mélange entre tradition galloise et art de vivre provençal."),
    ("Pologne", "pologne", "En Pologne, la pétanque gagne du terrain sur les places de marché, portée par une fédération de plus en plus active."),
    ("Portugal", "portugal", "Au Portugal, la pétanque se joue devant les murs couverts d'azulejos, souvent en fin de journée entre voisins."),
    ("Roumanie", "roumanie", "En Roumanie, la pétanque se pratique au pied des Carpates, portée par une fédération de plus en plus dynamique."),
    ("Russie", "russie", "En Russie, la fédération de pétanque existe bel et bien, même si sa participation internationale est actuellement suspendue."),
    ("Saint-Marin", "saint_marin", "À Saint-Marin, minuscule république perchée sur son rocher, la pétanque a elle aussi ses propres passionnés et sa fédération."),
    ("Serbie", "serbie", "En Serbie, la pétanque se joue sur les places des petites villes, avec une ferveur qui grandit à chaque tournoi régional."),
    ("Slovaquie", "slovaquie", "En Slovaquie, entre les châteaux et les Tatras, la pétanque trouve doucement sa place au sein des clubs affiliés à la CEP."),
    ("Slovénie", "slovenie", "En Slovénie, on joue volontiers à la pétanque au bord du lac de Bled — un décor de carte postale pour un tir bien placé !"),
    ("Suède", "suede", "En Suède, la pétanque se joue en été, entre les maisons rouges et un bon fika sucré après la partie."),
    ("Suisse", "suisse", "En Suisse, la pétanque se joue à l'ombre des Alpes, souvent avec la même précision légendaire que les montres locales — la Suisse a même été championne du monde en 1965, 1966, 1973 et 1980, et Maïki Molinas a été champion du monde de tête-à-tête en 2019 !"),
    ("Tchéquie", "tchequie", "En Tchéquie, la pétanque se joue sur les places pavées, souvent juste après un bon verre de bière locale."),
    ("Turquie", "turquie", "En Turquie, la pétanque se joue au bord du Bosphore, à la croisée de l'Europe et de l'Asie — une fédération jeune mais motivée !"),
    ("Ukraine", "ukraine", "En Ukraine, la pétanque continue d'être pratiquée par des clubs courageux, fidèles à la Confédération Européenne de Pétanque."),
    ("Algérie", "algerie", "En Algérie, la pétanque est arrivée avec la colonisation française et y est restée bien ancrée — au point de devenir, dès 1964, le tout premier pays hors de France sacré champion du monde !"),
    ("Bénin", "benin", "Au Bénin, la pétanque se joue près des marchés animés — et en 2023, à domicile à Cotonou, Marcel Gbétablé et Laïmath Sambo ont même décroché le titre mondial de doublette mixte face à la France !"),
    ("Burkina Faso", "burkina_faso", "Au Burkina Faso, on trouve des clubs de pétanque jusque dans les cours d'école — et en 2024, à Marrakech, les Burkinabè sont devenues championnes d'Afrique dames face au Togo !"),
    ("Cameroun", "cameroun", "Au Cameroun, la pétanque se joue en musique, entre deux points marqués et une bonne ambiance de quartier."),
    ("Comores", "comores", "Aux Comores, la pétanque se joue à l'ombre des cocotiers, entre deux baignades dans le lagon turquoise."),
    ("Congo", "congo", "Au Congo, la pétanque se joue au bord du fleuve, souvent avec autant d'élégance que les célèbres sapeurs de Brazzaville !"),
    ("Côte d'Ivoire", "cote_d_ivoire", "En Côte d'Ivoire, la pétanque se joue à l'ombre des grands arbres, appréciée dans les quartiers d'Abidjan comme dans les villages."),
    ("Djibouti", "djibouti", "À Djibouti, la pétanque se joue malgré la chaleur, souvent tôt le matin ou en fin de journée près du port."),
    ("Égypte", "egypte", "En Égypte, la pétanque a ses adeptes jusqu'au pied des pyramides ! Le pays fait partie des fédérations africaines affiliées à la FIPJP."),
    ("Gabon", "gabon", "Au Gabon, la pétanque se joue à la lisière de la forêt équatoriale, entre deux averses tropicales."),
    ("Guinée", "guinee", "En Guinée, la pétanque se joue dans les hauteurs du Fouta Djallon, un vrai château d'eau de l'Afrique de l'Ouest."),
    ("Libye", "libye", "En Libye, la pétanque garde ses fidèles, avec des parties disputées parfois à l'ombre de vestiges romains millénaires."),
    ("Madagascar", "madagascar", "À Madagascar, la pétanque est reine ! Introduite par les colons français, elle est aujourd'hui portée par la FSBM, championne du monde en 1999 et en 2016 !"),
    ("Mali", "mali", "Au Mali, la pétanque se joue près des grandes mosquées de terre — un sport venu de loin, mais adopté avec passion."),
    ("Maurice", "maurice", "À l'Île Maurice, la pétanque se joue au bord du lagon, dans une ambiance créole métissée et toujours souriante."),
    ("Mauritanie", "mauritanie", "En Mauritanie, la pétanque se joue aux portes du désert, dans une chaleur qui n'arrête pas les plus passionnés."),
    ("Maroc", "maroc", "Au Maroc, la Fédération Royale Marocaine de Pétanque organise régulièrement des rencontres, y compris le Championnat d'Afrique — et le pays a même été champion du monde en 1984, 1987 et 1990 !"),
    ("Niger", "niger", "Au Niger, la pétanque se joue aux portes du Sahara, entre deux caravanes et un peu d'ombre bienvenue."),
    ("Ouganda", "ouganda", "En Ouganda, la pétanque reste un sport de niche, mais une petite communauté s'entraîne fidèlement au bord du lac Victoria."),
    ("République Centrafricaine", "republique_centrafricaine", "En République Centrafricaine, la pétanque se joue près des chutes de Boali, dans une ambiance conviviale de quartier."),
    ("République Démocratique du Congo", "republique_democratique_du_congo", "En République Démocratique du Congo, la pétanque se joue au rythme de la ville, entre deux airs de rumba congolaise."),
    ("Sénégal", "senegal", "Au Sénégal, la fédération compte de plus en plus de licenciés — l'équipe nationale a décroché le bronze mondial en 2018, avant de devenir championne d'Afrique en 2024 et 2025 !"),
    ("Seychelles", "seychelles", "Aux Seychelles, la pétanque se joue pieds nus sur le sable, entre deux rochers de granit géants."),
    ("Tchad", "tchad", "Au Tchad, la pétanque se joue au bord du lac, un rendez-vous convivial malgré la chaleur du Sahel."),
    ("Togo", "togo", "Au Togo, la pétanque se joue près des célèbres cases Tata Somba, un sport qui s'est parfaitement intégré aux traditions locales."),
    ("Tunisie", "tunisie", "En Tunisie, la Fédération tunisienne de boules et pétanque organise régulièrement des championnats d'Afrique — et le pays a même été champion du monde en 1983, 1986 et 1997 !"),
    ("Zambie", "zambie", "En Zambie, la pétanque reste un sport discret, pratiqué par une poignée de passionnés non loin des chutes Victoria."),
    ("Afghanistan", "afghanistan", "En Afghanistan, la pétanque existe bel et bien, avec une fédération affiliée à la Confédération Asiatique des Sports Boules."),
    ("Bangladesh", "bangladesh", "Au Bangladesh, la pétanque reste un sport discret, mais bien réel, entre les rivières et les rizières du delta."),
    ("Brunei", "brunei", "Au Brunei, la pétanque se joue près du village flottant de Kampong Ayer, un décor unique au monde."),
    ("Cambodge", "cambodge", "Au Cambodge, comme dans tout l'ex-Indochine française, on trouve des terrains de pétanque même dans les plus petits villages, tout près d'Angkor Wat ! Le pays a même décroché plusieurs titres en or aux Jeux d'Asie du Sud-Est, dont le triplé dames de 2019."),
    ("Chine", "chine", "En Chine, la pétanque se développe surtout dans les grandes villes, portée par une fédération affiliée à la Confédération Asiatique."),
    ("Corée du Sud", "coree_du_sud", "En Corée du Sud, la pétanque compte une fédération active, avec des concours organisés jusque devant les palais royaux de Séoul."),
    ("Inde", "inde", "En Inde, la pétanque reste un sport de niche, mais une fédération existe bel et bien, portée par des passionnés urbains."),
    ("Indonésie", "indonesie", "En Indonésie, la pétanque se joue entre deux temples et rizières, avec une communauté de plus en plus active."),
    ("Iran", "iran", "En Iran, la pétanque a elle aussi sa fédération, discrète mais bien affiliée à la Confédération Asiatique des Sports Boules."),
    ("Japon", "japon", "Au Japon, la pétanque a sa propre fédération, membre de la Confédération Asiatique, avec des concours au pied du mont Fuji."),
    ("Kazakhstan", "kazakhstan", "Au Kazakhstan, la pétanque se joue sur l'immense steppe, entre deux yourtes et les sommets enneigés d'Almaty."),
    ("Kirghizistan", "kirghizistan", "Au Kirghizistan, la pétanque se joue au bord du lac Issyk-Koul, l'une des plus grandes étendues d'eau de montagne du monde."),
    ("Laos", "laos", "Au Laos, on appelle la pétanque 'petong', et c'est un véritable sport national ! Depuis le premier or historique de Soulasith Khamvongsa en 2001, le pays rafle régulièrement l'or aux Jeux d'Asie du Sud-Est, retransmis à la télévision nationale."),
    ("Malaisie", "malaisie", "En Malaisie, la pétanque se joue à l'ombre des gratte-ciel, portée par une fédération affiliée à la Confédération Asiatique."),
    ("Mongolie", "mongolie", "En Mongolie, la pétanque se joue en plein désert de Gobi, entre deux courses de chevaux traditionnelles."),
    ("Myanmar", "myanmar", "Au Myanmar (Birmanie), la pétanque se joue au milieu des milliers de temples de Bagan, un décor à couper le souffle."),
    ("Népal", "nepal", "Au Népal, la pétanque se joue au pied de l'Himalaya, un sport modeste mais bien vivant dans la vallée de Kathmandu."),
    ("Pakistan", "pakistan", "Au Pakistan, la pétanque reste rare mais existe, portée par une petite fédération affiliée à la Confédération Asiatique."),
    ("Philippines", "philippines", "Aux Philippines, la pétanque se joue entre deux îles, portée par une communauté grandissante de passionnés — médaillée d'or aux Jeux d'Asie du Sud-Est 2025 en doublette hommes et en doublette dames !"),
    ("Singapour", "singapour", "À Singapour, la pétanque se joue entre gratte-ciel et jardins futuristes, portée par une fédération bien organisée."),
    ("Taïwan", "taiwan", "À Taïwan (Chinese Taipei), la pétanque a sa propre fédération, active au sein de la Confédération Asiatique des Sports Boules."),
    ("Thaïlande", "thailande", "En Thaïlande, la pétanque est un véritable sport d'État ! Importée il y a 60 ans par la reine mère, elle compte 2 millions de pratiquants — et le pays truste les titres mondiaux depuis 2010, dont Ratchata Khamdee, champion du monde en individuel et en triplette en 2023 !"),
    ("Turkménistan", "turkmenistan", "Au Turkménistan, la pétanque se joue aux portes du désert du Karakoum, un sport discret mais bien affilié à la FIPJP."),
    ("Vietnam", "vietnam", "Au Vietnam, comme partout en ex-Indochine française, on trouve des terrains de pétanque même dans les petites villes, cochonnet à l'appui ! Depuis son premier or historique en 2022, le pays enchaîne les médailles aux Jeux d'Asie du Sud-Est, dont trois en 2025."),
    ("Argentine", "argentine", "En Argentine, la pétanque est portée par des clubs de passionnés, souvent nés de la communauté française installée à Buenos Aires."),
    ("Bolivie", "bolivie", "En Bolivie, la pétanque reste rare mais existe, portée par une petite communauté à plus de 3000 mètres d'altitude !"),
    ("Canada", "canada", "Au Canada, la pétanque est née en 1955 à Montréal et à Québec, portée par des pionniers comme Jean Raffa et Jean Fuschino — et elle ne se joue quasiment qu'au Québec !"),
    ("Chili", "chili", "Au Chili, la pétanque se joue dans les rues colorées de Valparaíso, portée par une fédération affiliée à la Confédération Panaméricaine."),
    ("Colombie", "colombie", "En Colombie, la pétanque se joue dans les rues pavées de Carthagène, portée par une communauté encore modeste mais passionnée."),
    ("Costa Rica", "costa_rica", "Au Costa Rica, la pétanque se joue au pied des volcans, un sport encore discret mais bien présent parmi les expatriés et les curieux locaux."),
    ("Cuba", "cuba", "À Cuba, la pétanque se joue au bord du Malecón, entre deux vieilles voitures américaines et une bonne dose de musique."),
    ("Équateur", "equateur", "En Équateur, la pétanque se joue à plus de 2800 mètres d'altitude, dans les rues coloniales de Quito."),
    ("États-Unis", "etats_unis", "Aux États-Unis, le plus ancien club de pétanque, le Mistral Club, a été fondé en 1958 dans le Massachusetts — aujourd'hui, la FPUSA fédère environ 30 000 joueurs à travers le pays."),
    ("Guatemala", "guatemala", "Au Guatemala, la pétanque se joue dans les ruelles pavées d'Antigua, à l'ombre des volcans environnants."),
    ("Haïti", "haiti", "En Haïti, la pétanque se joue près de la Citadelle Laferrière, un sport hérité mais bien vivant dans quelques clubs locaux."),
    ("Mexique", "mexique", "Au Mexique, la pétanque se joue dans les ruelles colorées de Guanajuato, portée par une fédération affiliée à la Confédération Panaméricaine."),
    ("Paraguay", "paraguay", "Au Paraguay, la pétanque se joue près des ruines jésuites de Trinidad, un sport discret mais fidèle à ses passionnés."),
    ("Pérou", "perou", "Au Pérou, la pétanque se joue jusque dans l'ombre du Machu Picchu, un sport venu de loin mais désormais bien installé."),
    ("République Dominicaine", "republique_dominicaine", "En République Dominicaine, la pétanque se joue dans la Zona Colonial de Saint-Domingue, la plus ancienne ville coloniale des Amériques."),
    ("Uruguay", "uruguay", "En Uruguay, la pétanque se joue dans les ruelles pavées de Colonia del Sacramento, portée par une petite fédération panaméricaine."),
    ("Venezuela", "venezuela", "Au Venezuela, la pétanque se joue au pied des tepuys et des chutes Angel, un sport modeste mais bien réel."),
    ("Australie", "australie", "En Australie, la pétanque se joue jusque dans l'outback ! Le pays participe régulièrement aux Océania, la grande compétition régionale créée en 1996."),
    ("Nouvelle-Calédonie", "nouvelle_caledonie", "En Nouvelle-Calédonie, la pétanque rassemble tout le monde — Kanaks, Tahitiens, Wallisiens — et les boulistes calédoniens brillent régulièrement aux championnats d'Océanie !"),
    ("Nouvelle-Zélande", "nouvelle_zelande", "En Nouvelle-Zélande, la pétanque se joue entre deux collines verdoyantes, et le pays a déjà décroché l'or aux Océania, comme Georgio Vakauta au tir de précision en 2016 !"),
    ("Tahiti", "tahiti", "À Tahiti, la pétanque prospère depuis près de 40 ans ! Des compétitions sont organisées chaque semaine en Polynésie française, un vrai vivier de talents dans le Pacifique."),
    ("Vanuatu", "vanuatu", "Au Vanuatu, la pétanque se joue à l'ombre des volcans, avec une sélection qui participe fièrement aux Océania face à l'Australie et la Nouvelle-Zélande."),
    ("Wallis-et-Futuna", "wallis_et_futuna", "À Wallis-et-Futuna, la pétanque est un vrai sport de cœur : le territoire a même accueilli les Océania 2025, où les Futuniennes ont décroché l'or en triplette dames !"),
    # Ajoutés le 2026-07-15 (recherche ressources/utils/RECHERCHE_ECOSYSTEME_PETANQUE.md,
    # section "Pays absents du tour à considérer") - portraits assets/Images/FannyWorldTour/
    # à fournir séparément (113_bresil.png, 114_israel.png, 115_liban.png), aucun outil de
    # génération d'image disponible pour les produire automatiquement.
    ("Brésil", "bresil", "Au Brésil, la « petanca » est l'une des trois disciplines de bocha reconnues par le Comité International Olympique, portée depuis 1991 par la Confédération Brésilienne de Bocha e Bolão !"),
    ("Israël", "israel", "En Israël, la pétanque a sa propre fédération, reconnue par la FIPJP dès 1992 et membre fondateur de la Confédération Asiatique des Sports Boules en 1997 — un sport reconnu de haut niveau, soutenu par le ministère des Sports !"),
    ("Liban", "liban", "Au Liban, la pétanque compte environ 400 licenciés répartis dans onze clubs à travers le pays — de quoi représenter fièrement les couleurs libanaises jusqu'aux Championnats du Monde à Dijon en 2024 !"),
]

COUNTRY_SCORE_SEUIL = 5  # un nouveau pays tous les 5 tirs réussis
COUNTRY_MAX_TIER = 114  # 115 pays (112 d'origine + Brésil/Israël/Liban, 2026-07-15)

# Tiers groupés par continent (même classification que
# ressources/utils/quiz_country_facts.py, dupliquée ici en dur pour rester
# disponible à l'exécution sans dépendre d'un fichier "build-only") - sert
# aux modes de quizz par continent (main_quizz.py, 2026-07-15 : "le jeu est
# trop long, il faut proposer plusieurs modes, un par continent"). Listes
# volontairement non contiguës : certains pays géographiquement "européens"
# du tour (Arménie, Turquie) sont classés Asie, et les 3 pays ajoutés le
# 2026-07-15 s'insèrent dans leur continent réel, pas à la suite de la liste.
CONTINENT_TIERS = {
    "Europe": [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37],
    "Afrique": [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
    "Asie": [3, 36, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 113, 114],
    "Amérique": [89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 112],
    "Océanie": [106, 107, 108, 109, 110, 111],
}



def get_country_tier(score, score_seuil=COUNTRY_SCORE_SEUIL, max_tier=COUNTRY_MAX_TIER):
    """Retourne l'index de pays courant (0..max_tier) : un nouveau pays
    toutes les score_seuil points, plafonné au dernier pays (Wallis-et-Futuna).
    """
    return min(score // score_seuil, max_tier)


# Modes de jeu proposés à l'écran de sélection (le tour complet ou un tour
# limité à un seul continent), PARTAGÉS par les 3 jeux qui parcourent
# WORLD_TOUR_COUNTRIES (main.py, main_hardcore.py, main_quizz.py -
# main_round_the_clock.py n'utilise pas ce système). Demande utilisateur du
# 2026-07-15 : "le jeu est trop long, il faut proposer plusieurs modes, un
# par continent", élargie le même jour à "l'ensemble des variantes du jeu".
# Chaque entrée : (nom affiché, liste de tiers à jouer dans l'ordre). Seul
# le mode "Tour complet" (index 0) doit alimenter un high score comparé à
# l'historique (calibré sur les 115 pays) - un score sur un continent n'est
# pas comparable, à gérer côté appelant (voir main_quizz.py::quiz_is_full_tour
# pour l'exemple de référence).
WORLD_TOUR_MODES = [
    ("Tour complet", list(range(COUNTRY_MAX_TIER + 1))),
    ("Europe", CONTINENT_TIERS["Europe"]),
    ("Afrique", CONTINENT_TIERS["Afrique"]),
    ("Asie", CONTINENT_TIERS["Asie"]),
    ("Amérique", CONTINENT_TIERS["Amérique"]),
    ("Océanie", CONTINENT_TIERS["Océanie"]),
]


def get_country_tier_for_mode(score, mode_tiers, score_seuil=COUNTRY_SCORE_SEUIL):
    """Comme get_country_tier(), mais pour un mode restreint (continent) :
    l'index de PROGRESSION dérivé du score (0..len(mode_tiers)-1) est
    résolu à travers `mode_tiers` pour retrouver le vrai tier du pays
    (nécessaire car les tiers d'un continent ne sont pas contigus - ex.
    l'Asie inclut l'Arménie(3), la Turquie(36) et Israël/Liban(113/114),
    entrecoupés d'autres continents)."""
    position = min(score // score_seuil, len(mode_tiers) - 1)
    return mode_tiers[position]


# Score auquel le 5e tir est touché dans le dernier pays (Wallis-et-Futuna) :
# la partie s'arrête alors immédiatement, même s'il reste du temps.
TOUR_COMPLETE_SCORE = (COUNTRY_MAX_TIER + 1) * COUNTRY_SCORE_SEUIL - 1


def is_tour_complete(score, tour_complete_score=TOUR_COMPLETE_SCORE):
    return score >= tour_complete_score
