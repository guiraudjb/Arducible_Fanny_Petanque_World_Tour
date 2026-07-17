# -*- coding: utf-8 -*-
# Troisième fait pétanque réel et sourcé (une année), DISTINCT de Q1
# (quiz_petanque_researched_facts.py) et Q4 (quiz_petanque_facts_2.py),
# tiré de ressources/utils/RECHERCHE_ATHLETES_PETANQUE.md. Remplace la
# question capitale (Q3) UNIQUEMENT pour les pays les plus riches en faits
# pétanque réels, afin de maximiser la part de questions sur la pétanque
# elle-même (demande utilisateur du 2026-07-12 : "il faut plus de question
# sur la pétanque").
#
# Volontairement très restreint : seuls les pays disposant d'un troisième
# fait pétanque clairement distinct des deux premiers (année différente,
# titre différent) sont inclus - pas de remplissage arbitraire, et jamais
# au prix d'inventer un fait.

THIRD_PETANQUE_FACTS = {
    50: ("En quelle année Madagascar a-t-il remporté l'or en doublette mixte au championnat du monde de pétanque, à Rome (avec les joueurs Lova et Fana) ?", "2025"),
    54: ("En quelle année le Maroc a-t-il remporté son 3e titre de champion du monde de pétanque en triplette, à Monaco ?", "1990"),
    63: ("En quelle année la Tunisie a-t-elle remporté son 3e titre de championne du monde de pétanque en triplette hommes, à Montpellier ?", "1997"),
    # Ajouté le 2026-07-15 : remplace la question capitale pour Israël (choix
    # éditorial délibéré, cf. quiz_country_facts.py - statut de Jérusalem disputé).
    113: ("En quelle année Israël est-il devenu membre fondateur de la Confédération Asiatique des Sports Boules (APSBC) ?", "1997"),
}
