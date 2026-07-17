# -*- coding: utf-8 -*-
# Table de métadonnées par pays, dans le même ordre que WORLD_TOUR_COUNTRIES
# (Scripts/dialogues.py). Sert uniquement à générer Scripts/quiz_questions.py
# — pas destinée à être livrée telle quelle dans le dépôt.
#
# Chaque entrée : (capitale, continent, langue_principale, monnaie)
# continent in {"Europe", "Afrique", "Asie", "Amérique", "Océanie"}

COUNTRY_FACTS = [
    ("Berlin", "Europe", "l'allemand", "l'euro"),                          # 0 Allemagne
    ("Andorre-la-Vieille", "Europe", "le catalan", "l'euro"),              # 1 Andorre
    ("Londres", "Europe", "l'anglais", "la livre sterling"),               # 2 Angleterre
    ("Erevan", "Asie", "l'arménien", "le dram arménien"),                  # 3 Arménie
    ("Vienne", "Europe", "l'allemand", "l'euro"),                          # 4 Autriche
    ("Bruxelles", "Europe", "le néerlandais/français/allemand", "l'euro"),  # 5 Belgique
    ("Sofia", "Europe", "le bulgare", "le lev bulgare"),                   # 6 Bulgarie
    ("Copenhague", "Europe", "le danois", "la couronne danoise"),          # 7 Danemark
    ("Édimbourg", "Europe", "l'anglais", "la livre sterling"),             # 8 Écosse
    ("Madrid", "Europe", "l'espagnol", "l'euro"),                          # 9 Espagne
    ("Tallinn", "Europe", "l'estonien", "l'euro"),                         # 10 Estonie
    ("Helsinki", "Europe", "le finnois", "l'euro"),                        # 11 Finlande
    ("Paris", "Europe", "le français", "l'euro"),                          # 12 France
    ("Saint-Pierre-Port", "Europe", "l'anglais", "la livre sterling"),     # 13 Guernesey
    ("Budapest", "Europe", "le hongrois", "le forint hongrois"),          # 14 Hongrie
    ("Dublin", "Europe", "l'anglais/irlandais", "l'euro"),                 # 15 Irlande
    ("Rome", "Europe", "l'italien", "l'euro"),                             # 16 Italie
    ("Saint-Hélier", "Europe", "l'anglais", "la livre sterling"),          # 17 Jersey
    ("Riga", "Europe", "le letton", "l'euro"),                             # 18 Lettonie
    ("Vilnius", "Europe", "le lituanien", "l'euro"),                       # 19 Lituanie
    ("Luxembourg", "Europe", "le luxembourgeois/français/allemand", "l'euro"),  # 20 Luxembourg
    ("Monaco", "Europe", "le français", "l'euro"),                        # 21 Monaco
    ("Oslo", "Europe", "le norvégien", "la couronne norvégienne"),         # 22 Norvège
    ("Amsterdam", "Europe", "le néerlandais", "l'euro"),                   # 23 Pays-Bas
    ("Cardiff", "Europe", "le gallois/anglais", "la livre sterling"),      # 24 Pays de Galles
    ("Varsovie", "Europe", "le polonais", "le zloty"),                     # 25 Pologne
    ("Lisbonne", "Europe", "le portugais", "l'euro"),                      # 26 Portugal
    ("Bucarest", "Europe", "le roumain", "le leu roumain"),                # 27 Roumanie
    ("Moscou", "Europe", "le russe", "le rouble russe"),                   # 28 Russie
    ("Saint-Marin", "Europe", "l'italien", "l'euro"),                      # 29 Saint-Marin
    ("Belgrade", "Europe", "le serbe", "le dinar serbe"),                  # 30 Serbie
    ("Bratislava", "Europe", "le slovaque", "l'euro"),                     # 31 Slovaquie
    ("Ljubljana", "Europe", "le slovène", "l'euro"),                       # 32 Slovénie
    ("Stockholm", "Europe", "le suédois", "la couronne suédoise"),         # 33 Suède
    ("Berne", "Europe", "l'allemand/français/italien", "le franc suisse"),  # 34 Suisse
    ("Prague", "Europe", "le tchèque", "la couronne tchèque"),             # 35 Tchéquie
    ("Ankara", "Asie", "le turc", "la livre turque"),                      # 36 Turquie
    ("Kiev", "Europe", "l'ukrainien", "la hryvnia"),                       # 37 Ukraine
    ("Alger", "Afrique", "l'arabe", "le dinar algérien"),                  # 38 Algérie
    ("Porto-Novo", "Afrique", "le français", "le franc CFA"),              # 39 Bénin
    ("Ouagadougou", "Afrique", "le français", "le franc CFA"),             # 40 Burkina Faso
    ("Yaoundé", "Afrique", "le français/anglais", "le franc CFA"),         # 41 Cameroun
    ("Moroni", "Afrique", "le comorien/français/arabe", "le franc comorien"),  # 42 Comores
    ("Brazzaville", "Afrique", "le français", "le franc CFA"),             # 43 Congo
    ("Yamoussoukro", "Afrique", "le français", "le franc CFA"),            # 44 Côte d'Ivoire
    ("Djibouti", "Afrique", "le français/arabe", "le franc djiboutien"),   # 45 Djibouti
    ("Le Caire", "Afrique", "l'arabe", "la livre égyptienne"),             # 46 Égypte
    ("Libreville", "Afrique", "le français", "le franc CFA"),              # 47 Gabon
    ("Conakry", "Afrique", "le français", "le franc guinéen"),             # 48 Guinée
    ("Tripoli", "Afrique", "l'arabe", "le dinar libyen"),                  # 49 Libye
    ("Antananarivo", "Afrique", "le malgache/français", "l'ariary"),       # 50 Madagascar
    ("Bamako", "Afrique", "le français", "le franc CFA"),                  # 51 Mali
    ("Port-Louis", "Afrique", "l'anglais/créole mauricien", "la roupie mauricienne"),  # 52 Maurice
    ("Nouakchott", "Afrique", "l'arabe", "l'ouguiya"),                     # 53 Mauritanie
    ("Rabat", "Afrique", "l'arabe", "le dirham marocain"),                 # 54 Maroc
    ("Niamey", "Afrique", "le français", "le franc CFA"),                  # 55 Niger
    ("Kampala", "Afrique", "l'anglais/swahili", "le shilling ougandais"),  # 56 Ouganda
    ("Bangui", "Afrique", "le français/sango", "le franc CFA"),            # 57 République Centrafricaine
    ("Kinshasa", "Afrique", "le français", "le franc congolais"),          # 58 République Démocratique du Congo
    ("Dakar", "Afrique", "le français", "le franc CFA"),                   # 59 Sénégal
    ("Victoria", "Afrique", "le créole seychellois/anglais/français", "la roupie seychelloise"),  # 60 Seychelles
    ("N'Djamena", "Afrique", "le français/arabe", "le franc CFA"),         # 61 Tchad
    ("Lomé", "Afrique", "le français", "le franc CFA"),                    # 62 Togo
    ("Tunis", "Afrique", "l'arabe", "le dinar tunisien"),                  # 63 Tunisie
    ("Lusaka", "Afrique", "l'anglais", "le kwacha zambien"),               # 64 Zambie
    ("Kaboul", "Asie", "le dari/pachto", "l'afghani"),                     # 65 Afghanistan
    ("Dacca", "Asie", "le bengali", "le taka"),                            # 66 Bangladesh
    ("Bandar Seri Begawan", "Asie", "le malais", "le dollar de Brunei"),   # 67 Brunei
    ("Phnom Penh", "Asie", "le khmer", "le riel"),                         # 68 Cambodge
    ("Pékin", "Asie", "le mandarin", "le yuan"),                          # 69 Chine
    ("Séoul", "Asie", "le coréen", "le won sud-coréen"),                  # 70 Corée du Sud
    ("New Delhi", "Asie", "l'hindi/anglais", "la roupie indienne"),        # 71 Inde
    ("Jakarta", "Asie", "l'indonésien", "la roupie indonésienne"),         # 72 Indonésie
    ("Téhéran", "Asie", "le persan", "le rial iranien"),                   # 73 Iran
    ("Tokyo", "Asie", "le japonais", "le yen"),                            # 74 Japon
    ("Astana", "Asie", "le kazakh/russe", "le tenge"),                     # 75 Kazakhstan
    ("Bichkek", "Asie", "le kirghiz/russe", "le som kirghiz"),             # 76 Kirghizistan
    ("Vientiane", "Asie", "le lao", "le kip"),                             # 77 Laos
    ("Kuala Lumpur", "Asie", "le malais", "le ringgit"),                   # 78 Malaisie
    ("Oulan-Bator", "Asie", "le mongol", "le tugrik"),                     # 79 Mongolie
    ("Naypyidaw", "Asie", "le birman", "le kyat"),                         # 80 Myanmar
    ("Katmandou", "Asie", "le népalais", "la roupie népalaise"),           # 81 Népal
    ("Islamabad", "Asie", "l'ourdou", "la roupie pakistanaise"),           # 82 Pakistan
    ("Manille", "Asie", "le filipino/anglais", "le peso philippin"),       # 83 Philippines
    ("Singapour", "Asie", "l'anglais/mandarin/malais/tamoul", "le dollar de Singapour"),  # 84 Singapour
    ("Taipei", "Asie", "le mandarin", "le nouveau dollar taïwanais"),      # 85 Taïwan
    ("Bangkok", "Asie", "le thaï", "le baht"),                             # 86 Thaïlande
    ("Achgabat", "Asie", "le turkmène", "le manat turkmène"),              # 87 Turkménistan
    ("Hanoï", "Asie", "le vietnamien", "le dong"),                         # 88 Vietnam
    ("Buenos Aires", "Amérique", "l'espagnol", "le peso argentin"),        # 89 Argentine
    ("Sucre", "Amérique", "l'espagnol", "le boliviano"),                   # 90 Bolivie
    ("Ottawa", "Amérique", "l'anglais/français", "le dollar canadien"),    # 91 Canada
    ("Santiago", "Amérique", "l'espagnol", "le peso chilien"),             # 92 Chili
    ("Bogota", "Amérique", "l'espagnol", "le peso colombien"),             # 93 Colombie
    ("San José", "Amérique", "l'espagnol", "le colón costaricien"),        # 94 Costa Rica
    ("La Havane", "Amérique", "l'espagnol", "le peso cubain"),             # 95 Cuba
    ("Quito", "Amérique", "l'espagnol", "le dollar américain"),            # 96 Équateur
    ("Washington", "Amérique", "l'anglais", "le dollar américain"),        # 97 États-Unis
    ("Guatemala Ciudad", "Amérique", "l'espagnol", "le quetzal"),          # 98 Guatemala
    ("Port-au-Prince", "Amérique", "le français/créole haïtien", "la gourde"),  # 99 Haïti
    ("Mexico", "Amérique", "l'espagnol", "le peso mexicain"),              # 100 Mexique
    ("Asuncion", "Amérique", "l'espagnol/guarani", "le guarani"),          # 101 Paraguay
    ("Lima", "Amérique", "l'espagnol", "le sol péruvien"),                 # 102 Pérou
    ("Saint-Domingue", "Amérique", "l'espagnol", "le peso dominicain"),    # 103 République Dominicaine
    ("Montevideo", "Amérique", "l'espagnol", "le peso uruguayen"),         # 104 Uruguay
    ("Caracas", "Amérique", "l'espagnol", "le bolivar"),                   # 105 Venezuela
    ("Canberra", "Océanie", "l'anglais", "le dollar australien"),          # 106 Australie
    ("Nouméa", "Océanie", "le français", "le franc CFP"),                  # 107 Nouvelle-Calédonie
    ("Wellington", "Océanie", "l'anglais/maori", "le dollar néo-zélandais"),  # 108 Nouvelle-Zélande
    ("Papeete", "Océanie", "le français/tahitien", "le franc CFP"),        # 109 Tahiti
    ("Port-Vila", "Océanie", "le bichlamar/anglais/français", "le vatu"),  # 110 Vanuatu
    ("Mata-Utu", "Océanie", "le français", "le franc CFP"),                # 111 Wallis-et-Futuna
    ("Brasília", "Amérique", "le portugais", "le réal brésilien"),         # 112 Brésil
    # Capitale volontairement non exploitée en quiz (choix éditorial du 2026-07-15 :
    # statut disputé de Jérusalem) - Q3 remplacée par THIRD_PETANQUE_FACTS pour ce
    # pays, cf. quiz_petanque_facts_3.py. Valeur gardée ici juste pour la cohérence
    # du tuple (jamais lue par le générateur pour ce tier).
    ("Jérusalem", "Asie", "l'hébreu", "le nouveau shekel israélien"),      # 113 Israël
    ("Beyrouth", "Asie", "l'arabe/le français", "la livre libanaise"),     # 114 Liban
]
