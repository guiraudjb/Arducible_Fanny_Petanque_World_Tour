# -*- coding: utf-8 -*-
# Personnalité de pétanque réelle et sourcée, associée à un pays, tirée de
# ressources/utils/RECHERCHE_ATHLETES_PETANQUE.md. Remplace la question
# "second monument/spécialité" (Q5) quand disponible, pour maximiser la
# part de questions sur la pétanque elle-même (demande utilisateur du
# 2026-07-12, élargie le même jour : "il faut plus de question sur la
# pétanque"). Clé = tier. Valeur = (nom, description), même format que
# quiz_second_facts.py : nom = réponse QCM, description = utilisée dans
# l'énoncé de la question et l'explication.
#
# Malgré son nom, ce dict n'est pas limité aux joueurs/joueuses en
# compétition : pour certains pays, la seule personnalité de pétanque
# réelle et nommée trouvée est un(e) président(e) de fédération ou un(e)
# entraîneur(e) - jamais un nom inventé, la question est phrasée de façon
# assez générique ("quelle personnalité") pour couvrir les deux cas.
#
# Uniquement des personnalités réelles avec un rôle/une réalisation
# vérifiable et sourcée (titre, médaille, record, sélection, présidence de
# fédération...) - jamais un nom inventé.

PETANQUE_ATHLETES = {
    # --- Europe ---
    4: ("Maris Newerkla", "joueur autrichien de pétanque classé 5e au championnat d'Europe juniors"),
    5: ("Claudy Weibel", "2 fois champion du monde de pétanque (triplette 2000, tête-à-tête 2015) et champion d'Europe de tir de précision en 2009"),
    7: ("Lasse Dithmar", "détenteur du meilleur score de tir de précision jamais réalisé par un joueur danois de pétanque (36 points) en grand championnat"),
    9: ("Sara Díaz Reyes", "citée comme joueuse espagnole de référence, championne d'Europe de pétanque"),
    11: ("Mikko Soikkeli", "a représenté la Finlande au championnat du monde de pétanque de Dijon, en décembre 2024"),
    12: ("Philippe Quintais", "surnommé « le Roi Quintais » ou « le Zidane de la pétanque », 14 fois champion du monde (8 fois en triplette, 4 fois au tir de précision, 2 fois comme coach)"),
    13: ("Andrew Bellamy-Burt", "vainqueur en simple du tournoi international « Guernsey Open » de pétanque en 2025"),
    14: ("Ágnes Kocsis-Simon", "présidente de la Fédération hongroise de pétanque, joueuse et entraîneuse détentrice de 11 titres nationaux"),
    15: ("Colin Delaney", "membre de l'équipe Ireland A1 de pétanque, restée invaincue en Celtic Challenge en 2023"),
    16: ("Diego Rizzi", "surnommé « l'Alieno » (l'extraterrestre), 46 fois champion d'Italie, 6 fois champion d'Europe et 5 fois champion du monde de pétanque"),
    17: ("Cassie Stewart-Le Gallais", "victorieuse des Island Singles Championships de pétanque 2025 (catégorie femmes), à Jersey"),
    19: ("Nerijus Kukcinavičius", "champion de Lituanie de pétanque en simple hommes"),
    20: ("Luc Cattazzo", "joueur luxembourgeois cité parmi les figures notables de la pétanque au Luxembourg"),
    21: ("Myriam Chambeiron et Laura Vierjon", "championnes d'Europe de pétanque en doublette féminine en 2022, à 's-Hertogenbosch (Pays-Bas)"),
    23: ("Edward Vinke", "champion national néerlandais de pétanque, plusieurs fois sélectionné en équipe des Pays-Bas au championnat d'Europe"),
    24: ("J-Y Robic", "champion national de pétanque du Pays de Galles"),
    25: ("Katarzyna Błasiak", "joueuse polonaise de pétanque, plusieurs fois médaillée internationale"),
    37: ("Andriy Kameniev", "champion national ukrainien de pétanque (Kharkiv)"),

    # --- Afrique ---
    38: ("Hmida Zerrouk", "médaillé d'argent au tir de précision au championnat d'Afrique de pétanque en 2019"),
    39: ("Marcel Bio, dit « Terrazini »", "capitaine de l'équipe nationale et champion d'Afrique de tir de précision de pétanque en 2019"),
    40: ("Florence Kanzié", "médaillée de bronze au tir de précision femmes au championnat d'Afrique de pétanque en 2024"),
    41: ("Charles Mbenoun", "médaillé d'argent au tir de précision au championnat d'Afrique de pétanque en 2024"),
    42: ("Zaidou Maoulida Mhamadi", "médaillé d'argent en tête-à-tête au championnat d'Afrique de pétanque en 2025, lors de la toute première finale de l'histoire des Comores dans cette compétition"),
    43: ("Batambika Verdorold", "membre de l'équipe congolaise médaillée d'argent en triplette hommes au championnat d'Afrique de pétanque en 2025"),
    44: ("Salif Kourouma", "médaillé d'or en tête-à-tête au championnat d'Afrique de pétanque en 2025"),
    48: ("Baba Conté", "membre de la triplette guinéenne sacrée championne nationale de boules et pétanque en 2024, à Conakry"),
    50: ("Jean-François « Zigle » Rakotondrainibe", "champion du monde de tir de précision de pétanque en 2024"),
    53: ("Tarek Akili", "entraîneur de l'équipe nationale mauritanienne de pétanque, qualifiée pour le championnat du monde après une 5e place à Cotonou en 2023"),
    54: ("Abdessamad El Mankari", "champion du monde de tir de précision de pétanque en 2008 (à Dakar) et quadruple champion d'Afrique de tir de précision"),
    59: ("François Fara Ndiaye", "vice-champion du monde de tir de précision de pétanque en 2008, à Dakar"),
    63: ("Mouna Béji", "championne du monde de pétanque en triplette femmes (2011), en individuel femmes (2023) et en doublette femmes (2025)"),

    # --- Asie ---
    68: ("Sok Chanmean", "champion du monde de tir de précision de pétanque en 2016 (à Madagascar), avec 39 médailles internationales cumulées depuis 2001"),
    72: ("Andri Irawan", "médaillé d'or en pétanque simple messieurs aux SEA Games 2025, en battant le Laotien Southammavong Bountamy en finale"),
    74: ("Ayumi Goma", "joueuse japonaise classée 1ère de la sélection nationale de pétanque trois fois consécutives"),
    77: ("Southammavong Bountamy", "médaillé d'argent en pétanque simple hommes aux SEA Games 2025, battu en finale par l'Indonésien Andri Irawan"),
    78: ("Muhamad Nuzul Azwan Ahmad Temizi", "médaillé de bronze au tir de précision hommes au championnat d'Asie de pétanque 2025, à domicile en Malaisie"),
    83: ("Cesiel Domenios et Ma. Corazon Soberre", "médaillées de bronze en pétanque double dames aux SEA Games 2025"),
    84: ("Tan Lay Tin", "membre de l'équipe de Singapour médaillée de bronze en triplette féminine (Nation Cup) au championnat d'Asie de pétanque 2025"),
    85: ("Tsai Chih-Hsuan", "membre de l'équipe taïwanaise médaillée de bronze en triplette junior (Asian Cup) au championnat d'Asie de pétanque 2025"),
    86: ("Ratchata Khamdee", "champion du monde de pétanque en simple messieurs en 2023, et champion d'Asie de tir de précision hommes en 2025"),
    88: ("Trinh Thi Kim Thanh", "membre de l'équipe vietnamienne devenue championne du monde de pétanque en triplette féminine en 2023, à Bangkok"),

    # --- Amérique ---
    89: ("José Giménez", "entraîneur de l'équipe nationale argentine de pétanque, médaillée de bronze au championnat panaméricain à Iquique (Chili)"),
    90: ("Yerko Castro", "président de la Fédération Bolivienne de Petanque"),
    92: ("Melisa Polito et Renato Donoso", "médaillés d'argent en pétanque paire mixte aux Jeux Bolivariens d'Ayacucho, en 2024"),
    93: ("Gustavo Henao", "président de la Fédération Colombienne de Petanque"),
    97: ("Rebekah « Bekah » Howe", "première Amérindienne (nation Crow Creek Sioux) à remporter une médaille internationale de pétanque : argent au tir de précision individuel dames aux World Games de Birmingham en 2022"),
    99: ("Dieufils Pierre", "président de la Fédération Haïtienne de Sport Boules"),
    102: ("Erik Bardelli", "finaliste (médaille d'argent) en pétanque individuelle messieurs aux Jeux Bolivariens d'Ayacucho, en 2024, battu par le Vénézuélien José Manuel Marcano"),
    103: ("Juan Moreno", "coordinateur de la République Dominicaine au sein de la Confédération Panaméricaine de Pétanque"),
    104: ("Fredy Isaias", "président de la Fédération Uruguayenne de Bochas (pétanque)"),
    105: ("José Manuel Marcano", "médaillé d'or en pétanque individuelle messieurs aux Jeux Bolivariens d'Ayacucho, en 2024"),

    # --- Océanie ---
    106: ("Delys Brady", "médaillée de bronze en pointage femmes à l'Oceania Championship de pétanque en 2025"),
    107: ("Toma Wai", "joueur des « Cagous », triple champion d'Océanie de pétanque en triplette"),
    108: ("Claire Wilson", "médaillée d'or en pointage femmes à l'Oceania Championship de pétanque en 2017"),
    111: ("Tofata Tautapu", "joueuse wallisienne réputée invaincue aux championnats d'Océanie de pétanque pendant huit ans, triple médaillée d'or à l'Oceania Championship de 2017"),

    # Ajoutés le 2026-07-15 (pas de nom de joueur/joueuse trouvé pour ces deux
    # pays malgré recherche - seule personnalité réelle et sourcée disponible :
    # le/la président(e) de fédération, même registre que d'autres entrées
    # ci-dessus, ex. 90/93/99/104)
    113: ("Amil Cordova", "président de la Fédération Israélienne de Pétanque"),
    114: ("George Gebrael", "président et chef du comité exécutif de la Fédération Libanaise de Pétanque"),
}
