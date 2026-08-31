#!/usr/bin/env python3
"""Reconstruit `background.txt` (un prompt de génération d'image par pays,
même ordre 1-115 que Scripts.dialogues.WORLD_TOUR_COUNTRIES) : le fichier
d'origine, dans le dossier de travail `fanny wold tour/` (jamais versionné,
disparu du disque), est irrécupérable tel quel (cf. mémoire
`~/.claude/projects/-home-adm1-story/memory/fanny_world_tour.md`).

Reconstruction basée sur l'inspection visuelle directe de plusieurs fonds
déjà en jeu (assets/Images/BackgroundWorldTour/*.jpg) pour en extraire la
formule réellement utilisée :
  - style BD ligne claire : contours encrés épais, aplats de couleurs
    (cel-shading), palette chaude/lumineuse ;
  - un boulodrome (terrain rectangulaire sablé, bordure en bois) au premier
    plan, quelques boules dessus, aucun personnage ;
  - un décor emblématique/culturellement représentatif du pays en fond
    (grand monument connu pour les pays "évidents" - Chine = Grande
    Muraille, Saint-Marin = tour Guaita du Monte Titano ; scène
    culturelle générique mais typée pour les autres - Wallis-et-Futuna =
    église de mission + fale traditionnelles, France = place de village
    provençale avec un café "Le Cochonnet").

Les 4 pays cités ci-dessus reprennent fidèlement ce qui est déjà à l'écran
(vérifié image par image) ; les 111 autres sont de nouvelles propositions
suivant la même formule (paysage/monument réel et défendable, jamais
inventé au hasard - même philosophie que la recherche factuelle documentée
dans la mémoire du projet pour les répliques vocales).

Usage :
    python3 ressources/utils/build_background_prompts_world_tour.py
Écrit ressources/utils/world_tour_background_prompts.txt (115 lignes,
"{tier:03d}\t{pays}\t{prompt}").
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402

OUT_PATH = os.path.join(REPO_ROOT, "ressources", "utils", "world_tour_background_prompts.txt")

STYLE_PREFIX = (
    "Comic-book style illustration, bold clean ink outlines, flat cel-shading, "
    "warm inviting color palette, no gradients banding, no photorealism"
)
STYLE_SUFFIX = (
    "in the foreground a rectangular sand petanque court (boulodrome) with a "
    "low wooden border, a few steel petanque boules scattered on the sand, "
    "empty court, no people, wide 16:9 landscape composition, establishing shot"
)

# pays -> décor emblématique/représentatif (anglais, pour le moteur de génération).
# Les 4 marquées "(vérifié)" reprennent ce qui est déjà visible dans le jeu.
LANDMARKS = {
    "Allemagne": "Neuschwanstein Castle rising above pine forests in the Bavarian Alps",
    "Andorre": "Andorra la Vella's stone-roofed village tucked in a steep green Pyrenean valley",
    "Angleterre": "Tower Bridge over the Thames with the London skyline behind",
    "Arménie": "Khor Virap monastery with snow-capped Mount Ararat rising behind it",
    "Autriche": "Hallstatt's lakeside houses beneath the alpine cliffs",
    "Belgique": "the Grand-Place of Brussels, gilded gothic guild houses",
    "Bulgarie": "Rila Monastery's striped arcades in the forested mountains",
    "Danemark": "Nyhavn's colorful harbor houses and old sailing ships in Copenhagen",
    "Écosse": "Edinburgh Castle on its volcanic crag above the Old Town",
    "Espagne": "the Alhambra's Moorish towers above Granada, Sierra Nevada behind",
    "Estonie": "Tallinn's medieval Old Town spires and city walls",
    "Finlande": "Helsinki Cathedral's white dome above the harbor market square",
    "France": (
        "a sunny Provençal village square, plane trees, a café called "
        "'Le Cochonnet' with a red awning and outdoor tables, ochre stone "
        "houses with green shutters"
    ),  # (vérifié) — 013_france.jpg
    "Guernesey": "St Peter Port's pastel harbor houses and marina",
    "Hongrie": "Budapest's Parliament building glowing on the Danube riverbank",
    "Irlande": "the Cliffs of Moher above the Atlantic, green fields inland",
    "Italie": "the Colosseum in Rome under a golden afternoon light",
    "Jersey": "Mont Orgueil Castle above the harbor of Gorey",
    "Lettonie": "Riga's Old Town skyline, the House of the Blackheads facade",
    "Lituanie": "Trakai Island Castle reflected in its lake",
    "Luxembourg": "Luxembourg City's fortified Old Town above the green Alzette valley",
    "Monaco": "Monte-Carlo's Belle Époque casino square with yachts in the harbor below",
    "Norvège": "Geirangerfjord's dramatic cliffs and waterfalls",
    "Pays-Bas": "an Amsterdam canal lined with narrow gabled houses and a windmill",
    "Pays de Galles": "Conwy Castle above the Welsh coastal town and estuary",
    "Pologne": "Kraków's Wawel Castle above the Vistula river",
    "Portugal": "Lisbon's Belém Tower on the Tagus riverbank",
    "Roumanie": "Bran Castle perched above the forested Carpathian foothills",
    "Russie": "Saint Basil's Cathedral's colorful domes on Red Square",
    "Saint-Marin": (
        "Guaita Tower's fortress ramparts atop Monte Titano, the Sammarinese "
        "flag flying, a hilltop medieval town and Tuscan countryside beyond"
    ),  # (vérifié) — 030_saint_marin.jpg
    "Serbie": "Belgrade Fortress at the confluence of the Sava and Danube rivers",
    "Slovaquie": "Bratislava Castle on its hill above the Danube",
    "Slovénie": "Lake Bled's island church and hilltop castle",
    "Suède": "Stockholm's Gamla Stan colorful waterfront buildings",
    "Suisse": "the Matterhorn peak above a wooden-chalet alpine village",
    "Tchéquie": "Prague's Charles Bridge with the castle skyline behind",
    "Turquie": "the Hagia Sophia and Istanbul's skyline above the Bosphorus",
    "Ukraine": "Kyiv's Saint Sophia Cathedral golden domes",

    "Algérie": "the whitewashed Casbah of Algiers overlooking the Mediterranean",
    "Bénin": "the stilt village of Ganvié on Lake Nokoué at sunset",
    "Burkina Faso": "the Sudano-Sahelian mudbrick Grande Mosquée de Bobo-Dioulasso",
    "Cameroun": "Mount Cameroon rising above a lush coastal village",
    "Comores": "Mount Karthala's volcanic silhouette above a turquoise lagoon and a coral-stone mosque",
    "Congo": "Brazzaville's riverside promenade on the wide Congo River",
    "Côte d'Ivoire": "the Basilica of Our Lady of Peace rising above Yamoussoukro",
    "Djibouti": "Lake Assal's white salt flats against a volcanic desert coastline",
    "Égypte": "the Pyramids of Giza and the Sphinx at golden hour",
    "Gabon": "Libreville's coastline with dense equatorial rainforest behind",
    "Guinée": "the terraced green highlands of the Fouta Djallon",
    "Libye": "the Roman ruins of Leptis Magna above the Mediterranean shore",
    "Madagascar": "the Avenue of the Baobabs silhouetted at sunset",
    "Mali": "the Great Mosque of Djenné's mudbrick towers",
    "Maurice": "Le Morne Brabant mountain above a turquoise lagoon",
    "Mauritanie": "the ancient caravan library town of Chinguetti at the Sahara's edge",
    "Maroc": "Jemaa el-Fnaa square in Marrakech with the Koutoubia minaret behind",
    "Niger": "Agadez's mudbrick Grand Mosque minaret against a Sahel skyline",
    "Ouganda": "the source of the Nile at Jinja, lush green hills along the river",
    "République Centrafricaine": "the Boali Falls cascading over savanna cliffs",
    "République Démocratique du Congo": "the Congo River's rapids near Kinshasa, green hills beyond",
    "Sénégal": "Gorée Island's colonial-era pastel houses above the Atlantic",
    "Seychelles": "Anse Source d'Argent's giant granite boulders and palm-lined beach",
    "Tchad": "a Sahel village on the shore of Lake Chad",
    "Togo": "the Koutammakou tower-houses ('Land of the Batammariba')",
    "Tunisie": "Sidi Bou Saïd's blue-and-white cliffside village above the sea",
    "Zambie": "mist rising over Victoria Falls on the Zambezi",

    "Afghanistan": "the turquoise-tiled Blue Mosque of Mazar-i-Sharif",
    "Bangladesh": "a wooden boat gliding through the Sundarbans mangrove delta",
    "Brunei": "the Sultan Omar Ali Saifuddien Mosque reflected in its lagoon",
    "Cambodge": "Angkor Wat's temple towers at sunrise",
    "Chine": (
        "the Great Wall of China winding over forested autumn mountains, "
        "watchtowers and a red flag"
    ),  # (vérifié) — 070_chine.jpg
    "Corée du Sud": "Gyeongbokgung Palace with the Seoul skyline and mountains behind",
    "Inde": "the Taj Mahal at sunrise, its reflection in the long pool",
    "Indonésie": "Borobudur's stone stupas with volcanoes rising behind",
    "Iran": "Naqsh-e Jahan Square in Isfahan, turquoise-tiled mosque domes",
    "Japon": "Mount Fuji framed by a red torii gate and cherry blossoms",
    "Kazakhstan": "the futuristic Bayterek Tower on Astana's skyline",
    "Kirghizistan": "yurts by Lake Issyk-Kul with the Tian Shan mountains behind",
    "Laos": "the golden stupa of Pha That Luang in Vientiane",
    "Malaisie": "the Petronas Towers rising over Kuala Lumpur",
    "Mongolie": "white gers (yurts) scattered across the open steppe under a vast sky",
    "Myanmar": "the golden stupa of Shwedagon Pagoda in Yangon",
    "Népal": "the Himalayas rising behind Kathmandu's Boudhanath stupa",
    "Pakistan": "the Badshahi Mosque's domes and minarets in Lahore",
    "Philippines": "the terraced rice fields of Banaue carved into the mountains",
    "Singapour": "the Supertrees of Gardens by the Bay against the skyline",
    "Taïwan": "the Taipei 101 skyscraper rising above the city",
    "Thaïlande": "Wat Arun's spires on the bank of the Chao Phraya river",
    "Turkménistan": "Ashgabat's gleaming white marble skyline",
    "Vietnam": "Ha Long Bay's limestone karst islands rising from emerald water",

    "Argentine": "the Obelisco de Buenos Aires on a wide tree-lined avenue",
    "Bolivie": "the mirror-like horizon of the Salar de Uyuni salt flat",
    "Canada": "Château Frontenac's copper turrets above Québec City's old town",
    "Chili": "the granite towers of Torres del Paine in Patagonia",
    "Colombie": "Cartagena's colorful colonial old-town houses",
    "Costa Rica": "Arenal Volcano rising above a green rainforest village",
    "Cuba": "vintage cars along Havana's seaside Malecón boulevard",
    "Équateur": "Quito's colonial skyline with Pichincha volcano behind",
    "États-Unis": "the Golden Gate Bridge over San Francisco Bay in the fog",
    "Guatemala": "Tikal's Mayan stone pyramids rising above the jungle canopy",
    "Haïti": "the Citadelle Laferrière fortress crowning its mountain",
    "Mexique": "El Castillo pyramid at Chichén Itzá",
    "Paraguay": "the Jesuit ruins of Trinidad del Paraná",
    "Pérou": "Machu Picchu's terraces beneath the Andean peaks",
    "République Dominicaine": "the colonial Zona Colonial streets of Santo Domingo",
    "Uruguay": "the lighthouse and cobbled streets of colonial Colonia del Sacramento",
    "Venezuela": "Angel Falls plunging from a tabletop tepui",

    "Australie": "the Sydney Opera House and Harbour Bridge",
    "Nouvelle-Calédonie": "the Amédée lighthouse above a turquoise lagoon",
    "Nouvelle-Zélande": "Milford Sound's sheer cliffs and waterfalls",
    "Tahiti": "Moorea's jagged green peaks above a lagoon",
    "Vanuatu": "Mount Yasur's glowing crater above a coastal village",
    "Wallis-et-Futuna": (
        "a white mission church with a red steeple beside a turquoise lagoon, "
        "traditional thatched fale huts among palm trees, sunset sky"
    ),  # (vérifié) — 112_wallis_et_futuna.jpg

    "Brésil": "Christ the Redeemer above Rio de Janeiro's bay and Sugarloaf Mountain",
    "Israël": "Jerusalem's Old City walls glowing at golden hour",
    "Liban": "the ancient Cedars of God forest on a Lebanese mountainside",
}


def build_prompt(pays: str) -> str:
    return f"{STYLE_PREFIX}, {LANDMARKS[pays]}, {STYLE_SUFFIX}."


def main():
    missing = [pays for pays, _slug, _texte in WORLD_TOUR_COUNTRIES if pays not in LANDMARKS]
    if missing:
        raise SystemExit(f"Décor manquant pour : {missing}")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for i, (pays, _slug, _texte) in enumerate(WORLD_TOUR_COUNTRIES, start=1):
            f.write(f"{i:03d}\t{pays}\t{build_prompt(pays)}\n")

    print(f"{len(WORLD_TOUR_COUNTRIES)} prompts écrits dans {OUT_PATH}")


if __name__ == "__main__":
    main()
