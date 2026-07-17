# Recherche du 2e monument / site touristique / spécialité par pays

Registre des recherches menées pour trouver, pour chacun des 112 pays du
tour (`Scripts/dialogues.py`), un **second** monument, site touristique ou
spécialité locale réel et vérifiable, DIFFÉRENT de celui déjà utilisé dans
`quiz_monuments_facts.py` (question 2 du quizz). Ce second fait remplace
la question "sur quel continent ?" (question 5), jugée trop facile, sans
jamais révéler dans l'énoncé qu'il s'agit d'un monument ou d'une
spécialité (voir `ressources/utils/build_quiz_questions.py`).

Données dans `ressources/utils/quiz_second_monuments_facts.py`
(`SECOND_MONUMENTS`), catégorisées dans
`ressources/utils/quiz_monument_categories.py`
(`SECOND_MONUMENT_CATEGORIES`) pour permettre des distracteurs de la même
catégorie (château face à château, etc.), comme pour la question 2.

**112/112 pays documentés**, aucun "aucune information trouvée".

## Europe

0 Allemagne : la porte de Brandebourg — fr.wikipedia.org/wiki/Porte_de_Brandebourg
1 Andorre : la Casa de la Vall — museus.ad/fr/monuments/casa-de-la-vall2, en.wikipedia.org/wiki/Casa_de_la_Vall
2 Angleterre : Big Ben — fr.wikipedia.org/wiki/Big_Ben
4 Autriche : le Sachertorte — fr.wikipedia.org/wiki/Sachertorte
5 Belgique : l'Atomium — fr.wikipedia.org/wiki/Atomium
6 Bulgarie : la vallée des Roses — fr.wikipedia.org/wiki/Vallée_des_Roses_(Bulgarie)
7 Danemark : les jardins de Tivoli — fr.wikipedia.org/wiki/Jardins_de_Tivoli
8 Écosse : le château d'Édimbourg — fr.wikipedia.org/wiki/Château_d'Édimbourg
9 Espagne : l'Alhambra de Grenade — fr.wikipedia.org/wiki/Alhambra
10 Estonie : le Laulupidu — estonianworld.com, en.wikipedia.org/wiki/Estonian_Song_Festival
11 Finlande : la forteresse de Suomenlinna — fr.wikipedia.org/wiki/Suomenlinna
12 France : le Mont-Saint-Michel — fr.wikipedia.org/wiki/Mont-Saint-Michel
13 Guernesey : Hauteville House — fr.wikipedia.org/wiki/Hauteville_House
14 Hongrie : les bains Széchenyi — fr.wikipedia.org/wiki/Bains_Széchenyi
15 Irlande : Newgrange — fr.wikipedia.org/wiki/Newgrange
16 Italie : la tour de Pise — fr.wikipedia.org/wiki/Tour_de_Pise
17 Jersey : le château de Mont Orgueil — fr.wikipedia.org/wiki/Château_de_Mont_Orgueil
18 Lettonie : la vieille ville de Riga (Art nouveau) — whc.unesco.org/en/list/852
19 Lituanie : la colline des Croix — fr.wikipedia.org/wiki/Colline_des_Croix
20 Luxembourg : le palais grand-ducal — fr.wikipedia.org/wiki/Palais_grand-ducal_(Luxembourg)
21 Monaco : le Grand Prix de Monaco — fr.wikipedia.org/wiki/Grand_Prix_automobile_de_Monaco
22 Norvège : les stavkirker — fr.wikipedia.org/wiki/Stavkirke
23 Pays-Bas : le parc floral de Keukenhof — fr.wikipedia.org/wiki/Keukenhof
24 Pays de Galles : Llanfairpwllgwyngyll... — en.wikipedia.org/wiki/Llanfairpwllgwyngyll
25 Pologne : les mines de sel de Wieliczka — fr.wikipedia.org/wiki/Mine_de_sel_de_Wieliczka
26 Portugal : le palais de Pena — fr.wikipedia.org/wiki/Palais_national_de_Pena
27 Roumanie : le palais du Parlement — en.wikipedia.org/wiki/Palace_of_the_Parliament
28 Russie : la cathédrale Saint-Basile-le-Bienheureux — fr.wikipedia.org/wiki/Cathédrale_Basile-le-Bienheureux
29 Saint-Marin : les timbres-poste saint-marinais — en.wikipedia.org/wiki/Postage_stamps_and_postal_history_of_San_Marino
30 Serbie : le monastère de Studenica — fr.wikipedia.org/wiki/Monastère_de_Studenica
31 Slovaquie : le château de Spiš — fr.wikipedia.org/wiki/Château_de_Spiš
32 Slovénie : les grottes de Postojna — fr.wikipedia.org/wiki/Grottes_de_Postojna
33 Suède : l'Icehotel de Jukkasjärvi — fr.wikipedia.org/wiki/Icehotel
34 Suisse : le Jungfraujoch — fr.wikipedia.org/wiki/Jungfraujoch
35 Tchéquie : l'horloge astronomique de Prague — fr.wikipedia.org/wiki/Horloge_astronomique_de_Prague
37 Ukraine : le bortsch ukrainien — ich.unesco.org/fr/USL/la-culture-de-la-preparation-du-bortsch-ukrainien-01852

## Asie

3 Arménie : le monastère de Guéghard — whc.unesco.org/en/list/960
36 Turquie : Pamukkale — en.wikipedia.org/wiki/Pamukkale
65 Afghanistan : le Minaret de Jam — whc.unesco.org/en/list/211
66 Bangladesh : les Sundarbans — en.wikipedia.org/wiki/Sundarbans
67 Brunei : Kampong Ayer — en.wikipedia.org/wiki/Kampong_Ayer
68 Cambodge : le temple de Preah Vihear — whc.unesco.org/en/list/1224
69 Chine : l'Armée de terre cuite de Xi'an — fr.wikipedia.org/wiki/Armée_de_terre_cuite
70 Corée du Sud : le palais Gyeongbokgung — en.wikipedia.org/wiki/Gyeongbokgung
71 Inde : le Fort Rouge de Delhi — en.wikipedia.org/wiki/Red_Fort
72 Indonésie : le temple de Prambanan — en.wikipedia.org/wiki/Prambanan
73 Iran : la place Naghsh-e Jahan — en.wikipedia.org/wiki/Naqsh-e_Jahan_Square
74 Japon : le château de Himeji — en.wikipedia.org/wiki/Himeji_Castle
75 Kazakhstan : le mausolée de Khoja Ahmed Yasavi — whc.unesco.org/en/list/1103
76 Kirghizistan : le lac Issyk-Koul — islands.com
77 Laos : la Plaine des Jarres — en.wikipedia.org/wiki/Plain_of_Jars
78 Malaisie : les grottes de Batu — en.wikipedia.org/wiki/Batu_Caves
79 Mongolie : le monastère d'Erdene Zuu — en.wikipedia.org/wiki/Erdene_Zuu_Monastery
80 Myanmar : Bagan — en.wikipedia.org/wiki/Bagan
81 Népal : Lumbini — en.wikipedia.org/wiki/Lumbini
82 Pakistan : la mosquée Badshahi — en.wikipedia.org/wiki/Badshahi_Mosque
83 Philippines : les Chocolate Hills — en.wikipedia.org/wiki/Chocolate_Hills
84 Singapour : Gardens by the Bay — en.wikipedia.org/wiki/Gardens_by_the_Bay
85 Taïwan : le bubble tea — taipeitimes.com
86 Thaïlande : le parc historique d'Ayutthaya — en.wikipedia.org/wiki/Ayutthaya_Historical_Park
87 Turkménistan : le cheval Akhal-Teke — en.wikipedia.org/wiki/Akhal-Teke
88 Vietnam : la vieille ville de Hoi An — en.wikipedia.org/wiki/Hoi_An

## Afrique

38 Algérie : Timgad — whc.unesco.org/en/list/194
39 Bénin : la Porte du Non-Retour d'Ouidah — en.wikipedia.org/wiki/Door_of_No_Return,_Ouidah
40 Burkina Faso : la Grande Mosquée de Bobo-Dioulasso — en.wikipedia.org/wiki/Grand_Mosque_of_Bobo-Dioulasso
41 Cameroun : le mont Cameroun — en.wikipedia.org/wiki/Mount_Cameroon
42 Comores : la Grande Mosquée du Vendredi de Moroni — fr.wikipedia.org/wiki/Mosquée_de_Moroni
43 Congo : la basilique Sainte-Anne-du-Congo — fr.wikipedia.org/wiki/Basilique_Sainte-Anne-du-Congo_de_Brazzaville
44 Côte d'Ivoire : Grand-Bassam — whc.unesco.org/en/list/1322
45 Djibouti : le lac Abbé — cityzeum.com
46 Égypte : le temple d'Abou Simbel — fr.wikipedia.org/wiki/Abou_Simbel
47 Gabon : le parc national de Loango — en.wikipedia.org/wiki/Loango_National_Park
48 Guinée : le mont Nimba — whc.unesco.org/en/list/155
49 Libye : la vieille ville de Ghadamès — whc.unesco.org/en/list/362
50 Madagascar : les Tsingy de Bemaraha — whc.unesco.org/en/list/494
51 Mali : la falaise de Bandiagara (pays Dogon) — whc.unesco.org/en/list/516
52 Maurice : Le Morne Brabant — whc.unesco.org/en/list/1259
53 Mauritanie : la structure de Richat — en.wikipedia.org/wiki/Richat_Structure
54 Maroc : le Jardin Majorelle — en.wikipedia.org/wiki/Majorelle_Garden
55 Niger : la réserve naturelle de l'Aïr et du Ténéré — whc.unesco.org/en/list/573
56 Ouganda : les tombeaux des rois du Buganda à Kasubi — whc.unesco.org/en/list/1022
57 République Centrafricaine : le parc national Manovo-Gounda St Floris — whc.unesco.org/en/list/475
58 RD Congo : la réserve de faune à okapis — whc.unesco.org/en/list/718
59 Sénégal : le lac Rose — fr.wikipedia.org/wiki/Lac_Rose
60 Seychelles : l'atoll d'Aldabra — whc.unesco.org/en/list/185
61 Tchad : le parc national de Zakouma — africanparks.org
62 Togo : le marché des féticheurs d'Akodessewa — fr.wikipedia.org/wiki/Marché_des_féticheurs
63 Tunisie : la médina de Tunis — whc.unesco.org/en/list/36
64 Zambie : le parc national de South Luangwa — southluangwa.com

## Amérique

89 Argentine : le glacier Perito Moreno — en.wikipedia.org/wiki/Perito_Moreno_Glacier
90 Bolivie : Tiwanaku — whc.unesco.org/en/list/567
91 Canada : le sirop d'érable — thecanadianencyclopedia.ca
92 Chili : Torres del Paine — en.wikipedia.org/wiki/Torres_del_Paine_National_Park
93 Colombie : Carthagène des Indes — whc.unesco.org/en/list/285
94 Costa Rica : Monteverde — en.wikipedia.org/wiki/Monteverde_Cloud_Forest_Reserve
95 Cuba : La Havane Vieille — whc.unesco.org/en/list/204
96 Équateur : le chapeau « Panama » de Montecristi — ecuadorianhands.com
97 États-Unis : le Grand Canyon — en.wikipedia.org/wiki/Grand_Canyon
98 Guatemala : Antigua Guatemala — whc.unesco.org/en/list/65
99 Haïti : le Palais Sans-Souci — whc.unesco.org/en/list/180
100 Mexique : la tequila — en.wikipedia.org/wiki/Tequila
101 Paraguay : le barrage d'Itaipu — en.wikipedia.org/wiki/Itaipu_Dam
102 Pérou : les lignes de Nazca — whc.unesco.org/en/list/700
103 République Dominicaine : le larimar — en.wikipedia.org/wiki/Larimar
104 Uruguay : Colonia del Sacramento — whc.unesco.org/en/list/747
105 Venezuela : les éclairs du Catatumbo — en.wikipedia.org/wiki/Catatumbo_lightning

## Océanie

106 Australie : la Grande Barrière de Corail — whc.unesco.org/en/list/154
107 Nouvelle-Calédonie : le lagon de Nouvelle-Calédonie — whc.unesco.org/en/list/1115
108 Nouvelle-Zélande : le Hobbiton Movie Set — en.wikipedia.org/wiki/Hobbiton_Movie_Set
109 Tahiti : le marae Taputapuatea — whc.unesco.org/en/list/1529
110 Vanuatu : le saut du Gol — fr.wikipedia.org/wiki/Saut_du_gol_(Vanuatu)
111 Wallis-et-Futuna : le site de Talietumu — easyvoyage.com, archeodyssee.fr
