# -*- coding: utf-8 -*-
"""Monnaie nationale utilisée avant l'euro, pour les 19 pays de la zone euro
présents dans le tour du monde (COUNTRY_FACTS). Remplace la question
"quelle monnaie est utilisée dans ce pays ?" pour ces pays précis : comme
les 19 partagent aujourd'hui la même réponse ("l'euro"), cette question
serait triviale/répétitive - la monnaie D'AVANT l'euro reste, elle, un vrai
fait distinctif par pays.

Andorre n'a jamais eu sa propre monnaie nationale avant l'euro : elle
utilisait conjointement le franc français et la peseta espagnole - une
réponse à deux monnaies, mais toujours un fait réel (pas une invention).

Sources : faits historiques monétaires bien établis (introduction de
l'euro fiduciaire au 1er janvier 2002, monnaies nationales retirées de la
circulation à cette occasion pour les pays de la "zone euro historique" +
adoptants ultérieurs Estonie/Lettonie/Lituanie/Slovaquie/Slovénie).
"""

PRE_EURO_CURRENCIES = {
    0: "le deutsche mark",
    1: "le franc français et la peseta espagnole",
    4: "le schilling autrichien",
    5: "le franc belge",
    9: "la peseta espagnole",
    10: "la couronne estonienne (kroon)",
    11: "le mark finlandais (markka)",
    12: "le franc français",
    15: "la livre irlandaise (punt)",
    16: "la lire italienne",
    18: "le lats letton",
    19: "le litas lituanien",
    20: "le franc luxembourgeois",
    21: "le franc monégasque",
    23: "le florin néerlandais (gulden)",
    26: "l'escudo portugais",
    29: "la lire sammarinaise",
    31: "la couronne slovaque",
    32: "le tolar slovène",
}
