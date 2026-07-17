# -*- coding: utf-8 -*-
# Deuxième fait pétanque réel et sourcé (une année), DISTINCT du fait déjà
# utilisé en Q1 (quiz_petanque_researched_facts.py), tiré de
# ressources/utils/RECHERCHE_ATHLETES_PETANQUE.md. Remplace la question
# monnaie (Q4) quand disponible, pour maximiser la part de questions sur
# la pétanque elle-même (demande utilisateur du 2026-07-12).
#
# Même garantie que le reste du projet : chaque année est un vrai fait
# sourcé (médaille, titre, date de championnat...), jamais inventée.
# Seuls les pays où j'ai trouvé un DEUXIÈME fait clairement distinct de Q1
# (année différente, événement différent) sont inclus ici - pas de
# remplissage arbitraire.
#
# Étendu le 2026-07-12 (demande utilisateur : "il faut plus de question sur
# la pétanque") avec des faits plus modestes (participation sans médaille,
# candidature à une organisation, championnat national...), toujours réels
# et sourcés dans RECHERCHE_ATHLETES_PETANQUE.md.

SECOND_PETANQUE_FACTS = {
    # --- Europe ---
    0: ("En quelle année l'Allemagne a-t-elle organisé le tout premier championnat d'Europe de pétanque en triplette féminine, à Rastatt ?", "2003"),
    2: ("En quelle année l'Angleterre a-t-elle remporté l'or en tir de précision Espoirs femmes au championnat d'Europe de pétanque ?", "2017"),
    4: ("En quelle année l'Autriche a-t-elle remporté le bronze en triplette femmes au championnat d'Europe de pétanque ?", "2016"),
    5: ("En quelle année la Belgique a-t-elle remporté l'or à l'EuroCup de pétanque, pour la première fois ?", "2016"),
    6: ("En quelle année la Bulgarie a-t-elle accueilli pour la première fois le championnat d'Europe hommes de pétanque, à Albena ?", "2015"),
    7: ("En quelle année le Danemark a-t-il remporté l'argent à l'EuroCup de pétanque ?", "1998"),
    9: ("En quelle année l'Espagne a-t-elle remporté l'or en triplette féminine au championnat d'Europe de pétanque ?", "1971"),
    10: ("En quelle année l'Estonie a-t-elle remporté le bronze en FedCup au championnat d'Europe de pétanque ?", "2022"),
    11: ("En quelle année la Finlande a-t-elle remporté l'or en triplette hommes Espoirs au championnat d'Europe de pétanque ?", "2019"),
    14: ("En quelle année la Hongrie a-t-elle remporté l'argent au tir de précision juniors filles au championnat d'Europe de pétanque ?", "2022"),
    15: ("En quelle année l'équipe Ireland A1 de pétanque est-elle restée invaincue en Celtic Challenge ?", "2023"),
    16: ("En quelle année l'Italie a-t-elle remporté l'or mondial en doublette de pétanque ?", "2022"),
    20: ("En quelle année le Luxembourg a-t-il remporté l'argent en junior mixte au championnat d'Europe de pétanque ?", "2014"),
    21: ("En quelle année Monaco a-t-il remporté l'or à l'EuroCup de pétanque ?", "2011"),
    22: ("En quelle année la Norvège a-t-elle remporté l'or en FedCup au championnat d'Europe de pétanque ?", "2022"),
    23: ("En quelle année les Pays-Bas ont-ils remporté l'or au tir de précision femmes au championnat d'Europe de pétanque ?", "2007"),
    25: ("En quelle année le Polonais Jędrzej Śliż a-t-il remporté le bronze au tir de précision juniors au championnat d'Europe de pétanque, à Brno ?", "2003"),
    26: ("En quelle année le Portugal a-t-il remporté l'argent au tir de précision hommes au championnat d'Europe de pétanque ?", "2011"),
    28: ("En quelle année la Russie a-t-elle remporté le bronze en Vétérans au championnat d'Europe de pétanque, à Monaco ?", "2016"),
    31: ("En quelle année la Slovaquie a-t-elle remporté le bronze au tir de précision hommes au championnat d'Europe de pétanque, à Albena ?", "2015"),
    32: ("En quelle année la Slovénie a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", "2022"),
    33: ("En quelle année la Suède a-t-elle remporté l'or en triplette femmes au championnat d'Europe de pétanque ?", "2007"),
    34: ("En quelle année la Suissesse Sylviane Métairon a-t-elle été sacrée championne du monde féminine de pétanque en tête-à-tête ?", "2020"),
    35: ("En quelle année la Tchéquie a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", "2021"),
    36: ("En quelle année la Turquie a-t-elle accueilli le championnat du monde féminin de pétanque, pour la première fois ?", "2008"),

    # --- Afrique ---
    38: ("En quelle année l'Algérie a-t-elle remporté le bronze en triplette hommes au championnat d'Afrique de pétanque ?", "2021"),
    39: ("En quelle année le Bénin a-t-il remporté l'argent en triplette hommes au championnat d'Afrique de pétanque, pour la première fois ?", "2007"),
    40: ("En quelle année le Burkina Faso a-t-il remporté le bronze au tir de précision par équipe au championnat du monde de pétanque, à Dakar ?", "2008"),
    41: ("En quelle année le Cameroun a-t-il remporté l'argent en triplette hommes au championnat d'Afrique de pétanque ?", "2015"),
    42: ("En quelle année les Comores ont-ils terminé 5e au championnat du monde de pétanque en triplette, à Cotonou (Bénin) ?", "2023"),
    43: ("En quelle année le Congo a-t-il remporté l'or à la Coupe des nations hommes au championnat d'Afrique de pétanque, à Marrakech ?", "2024"),
    49: ("En quelle année la Libye est-elle devenue membre fondateur de la Confédération Africaine de Sport Pétanque ?", "2019"),
    50: ("En quelle année Madagascar a-t-il remporté son tout premier titre de champion du monde de pétanque en triplette hommes ?", "1999"),
    52: ("En quelle année l'Île Maurice a-t-elle remporté le bronze au tir de précision au championnat d'Afrique de pétanque ?", "2019"),
    53: ("En quelle année la Mauritanie a-t-elle accueilli le championnat d'Afrique de pétanque, à Nouakchott, pour sa 10e édition ?", "2025"),
    54: ("En quelle année le Maroc a-t-il remporté son tout premier titre de champion du monde de pétanque en triplette, à Rotterdam (Pays-Bas) ?", "1984"),
    55: ("En quelle année le Niger a-t-il remporté l'argent à la Coupe des nations hommes au championnat d'Afrique de pétanque ?", "2024"),
    59: ("En quelle année le Sénégal a-t-il remporté le bronze en triplette hommes au championnat d'Afrique de pétanque, pour la première fois ?", "2009"),
    61: ("En quelle année le Tchad a-t-il candidaté, sans succès, pour organiser le championnat du monde de pétanque (finalement attribué à Madagascar) ?", "2016"),
    62: ("En quelle année le Togo a-t-il remporté l'argent en triplette hommes au championnat d'Afrique de pétanque ?", "2019"),
    63: ("En quelle année la Tunisie a-t-elle remporté son tout premier titre de championne du monde de pétanque en triplette hommes ?", "1983"),

    # --- Asie ---
    67: ("En quelle année Brunei a-t-il participé au championnat d'Asie de pétanque à Kuala Lumpur, sans obtenir de médaille ?", "2025"),
    68: ("En quelle année le Cambodge a-t-il remporté l'or en triplette féminine au championnat d'Asie de pétanque, à Kuala Lumpur ?", "2025"),
    69: ("En quelle année la Chine a-t-elle remporté le bronze en triplette hommes (Nation Cup) au championnat d'Asie de pétanque ?", "2025"),
    70: ("En quelle année la Corée du Sud a-t-elle participé au championnat d'Asie de pétanque, sans obtenir de médaille ?", "2025"),
    71: ("En quelle année l'Inde a-t-elle participé au championnat d'Asie de pétanque à Kuala Lumpur, terminant dernière (16e) en triplette masculine ?", "2025"),
    72: ("En quelle année l'Indonésie a-t-elle remporté le bronze en triplette masculine à l'Asian Cup de pétanque ?", "2025"),
    73: ("En quelle année s'est tenue la 13e édition du championnat national de pétanque d'Iran, à Sari ?", "2023"),
    74: ("En quelle année le Japon a-t-il remporté le bronze au tir de précision juniors au championnat d'Asie de pétanque ?", "2025"),
    78: ("En quelle année la Malaisie a-t-elle remporté l'or en triplette junior (Nation Cup) au championnat d'Asie de pétanque, disputé à domicile à Kuala Lumpur ?", "2025"),
    80: ("En quelle année le Myanmar a-t-il remporté l'argent au tir de précision féminin de pétanque aux SEA Games ?", "2025"),
    83: ("En quelle année les Philippines ont-elles remporté le bronze en double dames de pétanque aux SEA Games, seule médaille philippine cette année-là ?", "2023"),
    84: ("En quelle année Singapour a-t-il remporté le bronze en triplette féminine (Nation Cup) au championnat d'Asie de pétanque ?", "2025"),
    85: ("En quelle année Taïwan a-t-il remporté l'argent en triplette féminine (Nation Cup) au championnat d'Asie de pétanque ?", "2025"),
    86: ("En quelle année la Thaïlande a-t-elle été la nation la plus titrée en pétanque aux SEA Games, avec 5 médailles d'or ?", "2025"),
    88: ("En quelle année le Vietnam a-t-il conservé son titre de champion du monde de pétanque en triplette féminine, à Sin-le-Noble (France) ?", "2025"),

    # --- Amérique ---
    91: ("En quelle année a eu lieu le championnat du monde de pétanque de Montauban, après lequel le Canada comptait 3 médailles d'argent et 4 de bronze (mais aucun titre) ?", "2013"),
    100: ("En quelle année la Federación Mexicana de Petanca a-t-elle été fondée ?", "2011"),
    103: ("En quelle année la République Dominicaine a-t-elle participé au Championnat Panaméricain de pétanque de Limache (Chili) ?", "2023"),

    # --- Océanie ---
    106: ("En quelle année l'Australie a-t-elle remporté 4 médailles à l'Oceania Championship de pétanque, en Nouvelle-Calédonie ?", "2023"),
    107: ("En quelle année les hommes de Nouvelle-Calédonie ont-ils remporté l'or au tir de précision à l'Oceania Championship de pétanque, à Wallis ?", "2025"),
    108: ("En quelle année la Nouvelle-Zélande a-t-elle remporté six médailles d'or à l'Oceania Championship de pétanque, à Rotorua ?", "2005"),
    109: ("En quelle année la délégation polynésienne de pétanque a-t-elle réalisé tous les podiums et terminé 1ère à l'Oceania Championship, organisé à Wallis-et-Futuna ?", "2025"),
}
