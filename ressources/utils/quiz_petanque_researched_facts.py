# -*- coding: utf-8 -*-
# Faits pétanque réels, sourcés via recherche web (5 des 8 lots continentaux :
# Europe A/B, Afrique A, Asie A/B), enrichis le 2026-07-12 avec des faits
# d'ATHLÈTES/titres tirés de RECHERCHE_ATHLETES_PETANQUE.md quand une donnée
# plus précise/intéressante qu'une simple date de fondation de fédération a
# été trouvée. Clé = tier (index dans WORLD_TOUR_COUNTRIES). Valeur =
# (question, réponse_correcte). Toutes les réponses sont des années réelles
# (ou un fait ponctuel daté), sourcées sur fipjp.org, cep-petanque.com,
# sites de fédérations nationales, Wikipédia ou presse spécialisée — voir
# RECHERCHE_PETANQUE_PAYS.md et RECHERCHE_ATHLETES_PETANQUE.md pour le
# détail des sources par pays. Les pays sans fait assez solide/clair gardent
# le fallback SECOND_FACTS (Saint-Marin, RCA, RDC, Zambie, Afghanistan,
# Kazakhstan, Costa Rica, Équateur, Guatemala, Paraguay, Vanuatu).

RESEARCHED_FACTS = {
    0: ("En quelle année l'Allemagne a-t-elle remporté son tout premier titre de championne d'Europe de pétanque en triplette masculine, en battant la France en finale (à Santa Susanna, Espagne) ?", "2025"),
    1: ("En quelle année la Fédération Andorrane de Pétanque a-t-elle rejoint la FIPJP ?", "1987"),
    2: ("En quelle année la série de victoires de l'Angleterre au championnat des « Home Nations » de pétanque (24 ans consécutifs) a-t-elle pris fin, battue par Jersey ?", "2025"),
    3: ("En quelle année la Fédération Arménienne de Pétanque a-t-elle été créée ?", "2004"),
    4: ("En quelle année la fédération autrichienne de pétanque a-t-elle rejoint la FIPJP ?", "1995"),
    5: ("En quelle année le Belge Claudy Weibel a-t-il été sacré champion du monde de pétanque en triplette, pour la première fois ?", "2000"),
    6: ("En quelle année la Fédération Bulgare de Pétanque a-t-elle rejoint la FIPJP ?", "2021"),
    7: ("En quelle année le Danemark a-t-il remporté sa première médaille d'or en FedCup au championnat d'Europe de pétanque ?", "2024"),
    8: ("En quelle année la Scottish Pétanque Association a-t-elle été fondée ?", "1985"),
    9: ("En quelle année la Federación Española de Petanca a-t-elle été créée ?", "1954"),
    10: ("En quelle année l'Estonie a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", "2023"),
    11: ("En quelle année la Finlande a-t-elle remporté l'argent en FedCup au championnat d'Europe de pétanque ?", "2024"),
    12: ("En quelle année la Fédération Française de Pétanque et Jeu Provençal a-t-elle été fondée à Marseille ?", "1945"),
    13: ("En quelle année le premier club de pétanque de Guernesey a-t-il été fondé ?", "1984"),
    14: ("En quelle année la fédération hongroise de pétanque a-t-elle été créée ?", "1989"),
    15: ("En quelle année l'Irish Pétanque Association a-t-elle été fondée ?", "1990"),
    16: ("En quelle année l'Italie a-t-elle remporté son 2e titre mondial de pétanque, 45 ans après le premier ?", "2024"),
    17: ("En quelle année le Jersey Petanque Club a-t-il été fondé ?", "1986"),
    18: ("En quelle année la Fédération Lettonienne de Pétanque a-t-elle été créée ?", "2009"),

    19: ("En quelle année la Lituanie a-t-elle remporté le bronze en doublette femmes au championnat d'Europe de pétanque, à 's-Hertogenbosch (Pays-Bas) ?", "2024"),
    20: ("En quelle année la Fédération Luxembourgeoise de Boules et de Pétanque a-t-elle été fondée ?", "1959"),
    21: ("En quelle année Monaco a-t-il participé à la fondation de la FIPJP, à Marseille ?", "1958"),
    22: ("En quelle année la fédération norvégienne de pétanque a-t-elle été fondée ?", "1984"),
    23: ("En quelle année la fédération néerlandaise de pétanque (NJBB) a-t-elle été fondée ?", "1972"),
    24: ("En quelle année la Welsh Pétanque Association a-t-elle été fondée ?", "2004"),
    25: ("En quelle année le Polonais Paweł Pieprzyk a-t-il remporté l'or au tir de précision juniors au championnat d'Europe de pétanque, à Gand (Belgique) ?", "2012"),
    26: ("En quelle année la Federação Portuguesa de Petanca a-t-elle été fondée ?", "1992"),
    27: ("En quelle année la pétanque a-t-elle été introduite en Roumanie par Titus Marin ?", "2006"),
    28: ("En quelle année la Fédération de pétanque de Russie, sous sa forme actuelle, a-t-elle été créée ?", "2018"),
    30: ("En quelle année a eu lieu le tout premier championnat national serbe de pétanque ?", "2025"),
    31: ("En quelle année la fédération slovaque de pétanque a-t-elle été fondée ?", "1994"),
    32: ("En quelle année la fédération slovène de pétanque a-t-elle été fondée ?", "1999"),
    33: ("En quelle année le Suédois Ivar Liljegren a-t-il été vice-champion d'Europe de pétanque en tête-à-tête, à Martigny (Suisse) ?", "2024"),
    34: ("En quelle année le Suisse Maïky Molinas a-t-il été sacré champion du monde de pétanque en tête-à-tête ?", "2019"),
    35: ("En quelle année l'équipe féminine tchèque a-t-elle remporté l'argent au championnat d'Europe de pétanque, à Ankara (Turquie) ?", "2007"),
    36: ("En quelle année la pétanque a-t-elle été intégrée à la fédération turque de Bocce, Bowling et Fléchettes ?", "2006"),
    37: ("En quelle année la Fédération ukrainienne de pétanque a-t-elle été cofondée par Dmytro Bugaï ?", "2004"),

    38: ("En quelle année l'Algérie a-t-elle remporté son unique titre de championne du monde de pétanque en triplette, à Genève (Suisse) ?", "1964"),
    39: ("En quelle année le Bénin a-t-il accueilli les championnats du monde de pétanque à Cotonou, où l'équipe béninoise est devenue championne du monde en doublette mixte ?", "2023"),
    40: ("En quelle année le Burkina Faso est-il devenu le tout premier champion d'Afrique de pétanque en triplette hommes, à Cotonou ?", "2007"),
    41: ("En quelle année le Cameroun a-t-il remporté sa première médaille de bronze en triplette hommes au championnat d'Afrique de pétanque ?", "2011"),
    42: ("En quelle année la Fédération Comorienne de Pétanque a-t-elle rejoint la FIPJP ?", "1998"),
    43: ("En quelle année le Congolais Galy Chabrol Binguila a-t-il remporté l'or au tir de précision au championnat d'Afrique de pétanque ?", "2015"),
    44: ("En quelle année la Côte d'Ivoire a-t-elle remporté la Coupe des Nations au championnat du monde de pétanque, en battant le Bénin 13-3 (à Cotonou) ?", "2023"),
    45: ("En quelle année le Djiboutien Said Kadir a-t-il remporté l'argent au tir de précision au championnat d'Afrique de pétanque ?", "2009"),
    46: ("En quelle année la Fédération Égyptienne de Pétanque a-t-elle été créée ?", "2010"),
    47: ("En quelle année la Fédération Gabonaise de Pétanque (FEGAP) a-t-elle été créée ?", "2006"),
    48: ("En quelle année la triplette guinéenne (Baba Conté, Djiba Camara, Alseny Sylla Bongo) a-t-elle remporté l'or au championnat national de boules et pétanque, à Conakry ?", "2024"),
    49: ("En quelle année la Fédération Libyenne de Boules a-t-elle été créée ?", "2009"),
    50: ("En quelle année Madagascar a-t-il remporté son 2e titre mondial de pétanque (triplette masculine), à Antananarivo ?", "2016"),

    66: ("En quelle année la fédération de pétanque du Bangladesh a-t-elle été créée ?", "2017"),
    67: ("En quelle année la fédération de pétanque de Brunei a-t-elle été créée ?", "2007"),
    68: ("En quelle année le Cambodge a-t-il remporté son 5e titre mondial de pétanque consécutif, en Espagne ?", "2021"),
    69: ("En quelle année la pétanque a-t-elle commencé à être introduite en Chine, par le promoteur français Bernard Champey ?", "1985"),
    70: ("En quelle année la Fédération coréenne de pétanque a-t-elle été créée ?", "2013"),
    71: ("En quelle année la Petanque India Association a-t-elle été officiellement incorporée ?", "2019"),
    72: ("En quelle année l'Indonésienne Anni Saputri est-elle devenue championne d'Asie de tir de précision femmes, à Kuala Lumpur ?", "2025"),
    73: ("En quelle année la fédération iranienne de boules et pétanque a-t-elle été fondée ?", "2009"),
    74: ("En quelle année la Japan Petanque Boules Federation a-t-elle été créée ?", "2014"),
    76: ("En quelle année la Fédération kirghize de pétanque a-t-elle été fondée ?", "2022"),

    77: ("En quelle année la Laotienne Bovilak Thepphakan a-t-elle remporté la toute première médaille d'or de l'histoire du Laos aux SEA Games, en pétanque simple femmes ?", "2025"),
    78: ("En quelle année la Malaisienne Nur Iman Aina binti Ahmad Sabti a-t-elle remporté l'argent au tir de précision femmes au championnat d'Asie de pétanque, à Kuala Lumpur ?", "2025"),
    79: ("En quelle année la Fédération de Pétanque de Mongolie a-t-elle été créée ?", "2012"),
    80: ("En quelle année la Fédération de Pétanque du Myanmar a-t-elle été créée ?", "2013"),
    81: ("En quelle année la Petanque Federation Nepal a-t-elle été créée ?", "2012"),
    82: ("En quelle année la Pakistan Petanque Sports Boules Federation a-t-elle rejoint la FIPJP ?", "2006"),
    83: ("En quelle année « Pétanque Pinas » a-t-elle été créée et affiliée à la FIPJP ?", "2005"),
    84: ("En quelle année la fédération de pétanque de Singapour a-t-elle été créée ?", "1989"),
    85: ("En quelle année le Taïwanais Wu Kun-Yu a-t-il remporté l'argent au tir de précision hommes au championnat d'Asie de pétanque ?", "2025"),
    86: ("En quelle année la Thaïlande a-t-elle remporté pour la première fois l'or mondial en triplette messieurs, en battant la France ?", "2023"),
    87: ("En quelle année la Fédération Nationale de Pétanque du Turkménistan a-t-elle été créée ?", "2019"),
    88: ("En quelle année le Vietnam a-t-il remporté son tout premier titre de championne du monde de pétanque en triplette féminine, à Bangkok ?", "2023"),

    # Afrique B (retry)
    51: ("En quelle année le Malien Sangaré Nouhoum a-t-il remporté le bronze au tir de précision au championnat d'Afrique de pétanque ?", "2009"),
    52: ("En quelle année le Mauricien Parvez Khodabaccus a-t-il atteint les demi-finales du tir de précision au championnat du monde de pétanque, à Dijon ?", "2024"),
    53: ("En quelle année la Mauritanie a-t-elle remporté la médaille de bronze au championnat du monde de pétanque, à Izmir (Turquie) ?", "2010"),
    54: ("En quelle année le Maroc a-t-il été champion du monde de pétanque en triplette messieurs, à Boumerdès (Algérie) ?", "1987"),
    55: ("En quelle année le Nigérien Mohamed Harouna est-il devenu champion d'Afrique de tir de précision de pétanque ?", "2021"),
    56: ("En quelle année la fédération ougandaise de pétanque a-t-elle été créée et affiliée à la FIPJP ?", "2013"),
    59: ("En quelle année le Sénégal a-t-il remporté l'or en triplette hommes au championnat d'Afrique de pétanque, à Marrakech ?", "2024"),
    60: ("En quelle année la Seychelles Pétanque Association a-t-elle été fondée et affiliée à la FIPJP ?", "1996"),
    61: ("En quelle année le Tchadien Hounaye Raymon a-t-il remporté l'argent au tir de précision au championnat d'Afrique de pétanque ?", "2013"),
    62: ("En quelle année le Togo a-t-il remporté le bronze au tir de précision par équipe au championnat du monde de pétanque, à Cotonou (Bénin) ?", "2023"),
    63: ("En quelle année la Fédération Tunisienne de Boules et de Pétanque a-t-elle été créée et affiliée à la FIPJP ?", "1958"),

    # Amérique (retry)
    89: ("En quelle année la Fédération Argentine de Pétanque a-t-elle été créée ?", "2002"),
    90: ("En quelle année la Fédération Bolivienne de Petanque a-t-elle été affiliée à la FIPJP ?", "2025"),
    91: ("En quelle année la fédération canadienne de pétanque a-t-elle été créée (sous le nom de Fédération Canadienne Bouliste) ?", "1955"),
    92: ("En quelle année le Chili a-t-il remporté l'argent en pétanque par équipe mixte aux Jeux Bolivariens, à Ayacucho (Pérou) ?", "2024"),
    93: ("En quelle année la Fédération Colombienne de Petanque a-t-elle été affiliée à la FIPJP ?", "2025"),
    95: ("En quelle année la Fédération Cuba Pétanque a-t-elle été créée et affiliée à la FIPJP ?", "2013"),
    97: ("En quelle année les États-Unis ont-ils remporté leur toute première médaille d'or internationale en pétanque, aux World Games de Birmingham, grâce à Stefan Nicolas ?", "2022"),
    99: ("En quelle année la Fédération Haïtienne de Sport Boules a-t-elle été créée ?", "2010"),
    100: ("En quelle année le Mexique a-t-il participé pour la première fois au championnat du monde de pétanque en triplette masculine, à Marseille ?", "2012"),
    102: ("En quelle année la Péruvienne Rosalba Rojas a-t-elle remporté l'or en pétanque individuelle dames aux Jeux Bolivariens, à Ayacucho ?", "2024"),
    103: ("En quelle année la Federación Dominicana de Bochas (FEDOBOCHAS) a-t-elle été affiliée à la FIPJP ?", "2003"),
    104: ("En quelle année la Federación Uruguaya de Bochas a-t-elle été fondée ?", "1930"),
    105: ("En quelle année le Venezuela a-t-il remporté l'or en pétanque par équipe mixte aux Jeux Bolivariens, à Ayacucho (Pérou) ?", "2024"),

    # Océanie (retry)
    106: ("En quelle année la Fédération Australienne de Pétanque a-t-elle rejoint la FIPJP ?", "1990"),
    107: ("En quelle année la Fédération de Nouvelle-Calédonie de pétanque a-t-elle été créée et a rejoint la FIPJP ?", "2013"),
    108: ("En quelle année Petanque New Zealand a-t-elle été fondée, lors d'une réunion à l'Atomic Café d'Auckland ?", "1993"),
    109: ("En quelle année le Polynésien Jean Manéa a-t-il été vice-champion du monde de tir de précision de pétanque, à Izmir (Turquie) ?", "2010"),
    111: ("En quelle année les Océania de pétanque ont-ils eu lieu à Wallis, où Futuna a remporté le titre en triplette dames pour la première fois seule ?", "2025"),

    # Ajoutés le 2026-07-15 (RECHERCHE_ECOSYSTEME_PETANQUE.md)
    112: ("En quelle année la Confédération Brésilienne de Bocha e Bolão (regroupant la pétanque, le raffa et le zerbin) a-t-elle été fondée ?", "1991"),
    113: ("En quelle année la fédération israélienne de pétanque a-t-elle été reconnue lors du Congrès de la FIPJP, à Rome ?", "1992"),
    114: ("En quelle année le Liban a-t-il disputé un tournoi préliminaire des Championnats du Monde de pétanque, à Dijon (France), aux côtés de l'Écosse, l'Estonie, la Lettonie, la Norvège et l'Ukraine ?", "2024"),
}
