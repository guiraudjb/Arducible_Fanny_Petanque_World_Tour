#!/usr/bin/env python3
"""Reconstruit `fanny.txt` (prompt de portrait Fanny en tenue traditionnelle,
un par pays, même ordre 1-115 que Scripts.dialogues.WORLD_TOUR_COUNTRIES) :
comme `background.txt` (cf. build_background_prompts_world_tour.py), le
fichier d'origine est irrécupérable (dossier de travail disparu).

Reconstruction calibrée avec WD Tagger (`~/RAID/wdtagger`) sur plusieurs
portraits FannyWorldTour déjà en jeu (001_allemagne, 013_france,
025_pays_de_galles, 047_egypte, 070_chine, 072_inde) : tous montrent de
façon systématique les tags `full body`, `black footwear`/`shoes`,
`hand on own hip`, `looking at viewer`, `standing` — la composition
canonique est donc "corps entier, chaussures visibles, une main sur la
hanche, boule de pétanque dans l'autre main", quelle que soit la tenue.

Erreur corrigée ici (2026-08-31) : la 1ère génération des 3 nouveaux
portraits (Brésil/Israël/Liban) utilisait des tenues à jupe/robe longue au
sol, qui cachent les pieds - vérifié après coup avec WD Tagger, ces 3
portraits n'avaient presque aucun des tags ci-dessus (pas de chaussures
visibles). Toutes les tenues ci-dessous sont donc explicitement à hauteur
genou ou au-dessus, avec des chaussures noires mentionnées explicitement
dans le gabarit commun (STYLE_SUFFIX), pas seulement dans la description
de la tenue.

2e erreur corrigée (2026-08-31) : le fond utilisé pour cette même 1ère
génération était un aplat blanc uni unique - une fois détouré
(remove_background.py), tout l'arrière-plan devient transparent, sans
rien sous les pieds. Or tous les portraits déjà en jeu ont un fond
BICOLORE (vérifié par échantillonnage pixel sur 001_allemagne, 013_france,
070_chine, 025_pays_de_galles : mur crème ~(251,244,230) jusqu'à ~72% de
la hauteur, puis sol brun clair ~(213,184,155) en dessous, transition nette
à une ligne horizontale) : le mur (proche du blanc) est effectivement
retiré par le seuillage `remove_white_background_smart`, mais le sol (trop
éloigné du blanc pour le seuil par défaut thresh=30) reste opaque et sert
de "socle" visuel sous les pieds du personnage une fois composité dans le
jeu. STYLE_SUFFIX décrit maintenant explicitement ce fond bicolore.

Décision utilisateur (2026-08-31, après le point ci-dessus) : pour Brésil/
Israël/Liban puis pour le lot ci-dessous, livrer l'image PLEINE (RGB, sans
canal alpha, fond bicolore inclus tel quel) plutôt que de la détourer -
plus robuste (évite un vrai bug rencontré : le détourage par seuillage sur
le blanc mordait aussi sur des vêtements blancs/crème proches du mur,
rendant des pans de tenue transparents). Conséquence assumée : ces
portraits s'affichent en jeu comme un bloc opaque par-dessus le décor du
pays (FannyCompanion.draw() ne dessine aucun panneau derrière le sprite),
contrairement aux pays encore détourés - accepté explicitement par
l'utilisateur, pas une régression passée inaperçue.

3e correction (2026-08-31) : audit WD Tagger étendu à toute la collection
(score `full body`) a révélé que 14 pays du lot d'origine (001-112, donc
sans rapport avec Brésil/Israël/Liban) ont un cadrage cassé - vue en
plongée/fisheye qui écrase le corps, jusqu'au simple portrait buste
(Pologne, `full body`=0.00) : Angleterre, Belgique, Estonie, Irlande,
Lituanie, Pologne, Roumanie, Serbie, Slovénie, Turquie, Ukraine, Singapour,
Guatemala, Australie. Leurs entrées OUTFITS ci-dessous ont été réécrites
pour décrire fidèlement la tenue déjà visible sur chaque image actuelle
(observée directement, pas réinventée) avant régénération en pose debout
standard - seul le cadrage change, pas le costume. Pologne fait exception :
le cadrage d'origine ne montrait que le buste, jupe non visible, donc
extrapolée à partir du folklore polonais standard (blouse blanche + jupe
rouge) en gardant le seul élément réellement visible (le châle
multicolore).

Usage :
    python3 ressources/utils/build_fanny_outfit_prompts_world_tour.py
Écrit ressources/utils/world_tour_fanny_outfit_prompts.txt (115 lignes,
"{tier:03d}\t{pays}\t{prompt}").
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402

OUT_PATH = os.path.join(REPO_ROOT, "ressources", "utils", "world_tour_fanny_outfit_prompts.txt")

FANNY_BASE = (
    "1woman, gorgeous vintage pinup, black hair styled in a retro rockabilly "
    "updo with short bangs and a red bandana tied at the top, piercing blue "
    "eyes, winged eyeliner, bright red lipstick, red nail polish, curvaceous "
    "body, "
)
STYLE_SUFFIX = (
    "standing full body from head to feet facing camera, one hand on her hip, "
    "holding a single steel petanque boule in the other hand at hip height, "
    "her shoes clearly visible below the hem, confident smile, looking at "
    "viewer, simple two-tone studio backdrop: plain flat cream wall on the "
    "upper part of the frame and a plain flat warm tan floor on the lower "
    "part, straight horizontal line where wall meets floor around 72% down "
    "the frame, no props, no shadow gradient, Modern comic book illustration "
    "style, smooth flawless skin, flat colors, clean cell shading, vector art "
    "style, clear bold black outlines, vibrant colors, masterpiece, textless"
)

# pays -> tenue traditionnelle/typique (anglais), toujours genou ou au-dessus
# pour garder les chaussures visibles (cf. audit WD Tagger dans le docstring).
OUTFITS = {
    "Allemagne": "a Bavarian dirndl: black bodice laced over a white blouse, red skirt, red bow apron",  # (vérifié en jeu) 001
    "Andorre": "a Pyrenean folk dress with a black bodice, white blouse, and a red-and-gold embroidered apron",
    "Angleterre": "a brown houndstooth tweed waistcoat buttoned over a white blouse, brown leather lace-up boots",  # (vérifié en jeu, recadré 2026-08-31) 003
    "Arménie": "an Armenian taraz-inspired dress: deep red velvet with gold trim and a pointed headpiece",
    "Autriche": "an Austrian dirndl in alpine green with white lace blouse and a matching bow",
    "Belgique": "a black lace-trimmed bodice over a white puff-sleeve blouse with a large lace collar, a black-yellow-red ribbon bow at the neck, a red-green-yellow striped skirt with a gold floral trim band, black shoes with white socks",  # (vérifié en jeu, recadré 2026-08-31) 006
    "Bulgarie": "a Bulgarian folk dress with a white embroidered blouse, red apron, and a floral headpiece",
    "Danemark": "a Danish folk dress with a red bodice, striped skirt, and a white lace cap",
    "Écosse": "a tartan mini kilt skirt with a black velvet vest and a small tam o'shanter cap",
    "Espagne": "a flamenco-style red polka-dot dress with ruffled hem and a hair comb with a rose",
    "Estonie": "a white blouse under a black bib-front pinafore apron with red trim, a green-red-pink-mustard striped skirt, layered red-gold-green beaded necklaces, black shoes with red diamond-pattern socks",  # (vérifié en jeu, recadré 2026-08-31) 011
    "Finlande": "a Finnish folk dress with a red bodice, striped apron, and a white lace blouse",
    "France": "her classic red-and-white gingham shirt tied at the midriff with a red skirt",  # (vérifié en jeu) 013
    "Guernesey": "a Guernsey fisherman-inspired outfit: a navy knit sweater dress with a rope belt",
    "Hongrie": "a Hungarian folk dress with a white embroidered blouse, red skirt, and floral apron",
    "Irlande": "a cream Aran cable-knit sweater dress with a green-and-gold Celtic knot brooch at the collar, a black skirt, black lace-up boots",  # (vérifié en jeu, recadré 2026-08-31) 016
    "Italie": "an Italian folk dress with a white blouse, red bodice, and a green skirt",
    "Jersey": "a Jersey fisherman-inspired outfit: a cream knit sweater dress with a rope belt",
    "Lettonie": "a Latvian folk dress with a striped skirt, white blouse, and a beaded crown headpiece",
    "Lituanie": "a white lace bonnet headscarf with gold trim, a flower crown, a red-green-yellow striped skirt, black shoes with white trim",  # (vérifié en jeu, recadré 2026-08-31) 020
    "Luxembourg": "a Luxembourgish folk dress with a black bodice, red skirt, and a white lace collar",
    "Monaco": "a chic red-and-white cocktail dress echoing Monaco's flag, with pearl jewelry",
    "Norvège": "a Norwegian bunad: black bodice with silver brooches over a white blouse and red skirt",
    "Pays-Bas": "a Dutch folk dress with a lace cap, striped skirt, and wooden clog-style shoes",
    "Pays de Galles": "a Welsh folk dress: a red cape over an argyle-patterned dress, tied with a ribbon",  # (vérifié en jeu) 025
    "Pologne": "a white blouse with a red skirt, and a rainbow-striped (red-yellow-green-blue) woven shawl draped over her shoulders",  # (vérifié en jeu, recadré 2026-08-31) 026 — le portrait d'origine était cadré trop serré (buste seul), jupe non visible, extrapolée à partir du folklore polonais standard
    "Portugal": "a Portuguese folk dress with a striped skirt, black vest, and gold filigree earrings",
    "Roumanie": "a white blouse with red-and-black geometric embroidery at the collar and sleeves, a black skirt with a red woven tasseled belt, black shoes",  # (vérifié en jeu, recadré 2026-08-31) 028
    "Russie": "a Russian sarafan dress in red with gold embroidery and a kokoshnik headpiece",
    "Saint-Marin": "a Sammarinese folk dress with a white blouse, blue bodice, and a lace apron",
    "Serbie": "a red vest with black-and-gold geometric embroidery over a white blouse, a black skirt with red-and-gold horizontal banding, black shoes",  # (vérifié en jeu, recadré 2026-08-31) 031
    "Slovaquie": "a Slovak folk dress with a floral-embroidered bodice and a red pleated skirt",
    "Slovénie": "a red bodice vest with green-and-gold embroidered trim over a white embroidered blouse, a white lace apron/skirt with a red-and-black hem border, a white lace headscarf, black mary-jane shoes",  # (vérifié en jeu, recadré 2026-08-31) 033
    "Suède": "a Swedish folk dress with a blue bodice, yellow trim, and a white apron",
    "Suisse": "a Swiss alpine dress with a black bodice, white blouse, and edelweiss embroidery",
    "Tchéquie": "a Czech folk dress with a red bodice, floral apron, and a ribboned headpiece",
    "Turquie": "a red floral-print headscarf, a black vest with gold embroidered trim over a white blouse with red-and-green floral embroidery, a black skirt/apron with gold geometric trim and red flower embroidery, brown lace-up boots",  # (vérifié en jeu, recadré 2026-08-31) 037
    "Ukraine": "a white vyshyvanka blouse with red-and-black cross-stitch embroidery and a red ribbon tie at the neck, a black skirt, red shoes",  # (vérifié en jeu, recadré 2026-08-31) 038

    "Algérie": "an Algerian karakou-inspired outfit: a velvet embroidered vest with gold thread over a blouse",
    "Bénin": "a colorful West African wax-print wrap dress with a matching head wrap",
    "Burkina Faso": "a Burkinabé wax-print dress with bold geometric patterns and a head wrap",
    "Cameroun": "a Cameroonian wax-print dress with bright patterns and beaded jewelry",
    "Comores": "a Comorian shiromani-inspired dress: bright printed fabric with gold trim and a floral headpiece",
    "Congo": "a Congolese wax-print wrap dress with bold colors and a matching headscarf",
    "Côte d'Ivoire": "an Ivorian wax-print dress with kita-inspired patterns and beaded jewelry",
    "Djibouti": "a Djiboutian dirac dress: flowing bright fabric with gold trim and a headscarf",
    "Égypte": "a white Egyptian-inspired dress with gold collar jewelry and kohl-lined eyes",  # (vérifié en jeu) 047
    "Gabon": "a Gabonese wax-print dress with bold patterns and a matching head wrap",
    "Guinée": "a Guinean wax-print dress with bright patterns and beaded jewelry",
    "Libye": "a Libyan embroidered kaftan dress with silver jewelry and a headscarf",
    "Madagascar": "a Malagasy lamba wrap dress in woven earth tones with a straw hat",
    "Mali": "a Malian bogolan mudcloth-patterned dress with beaded jewelry",
    "Maurice": "a Mauritian sega dance dress: colorful ruffled skirt with a floral top",
    "Mauritanie": "a Mauritanian melhfa: flowing bright fabric draped elegantly with gold jewelry",
    "Maroc": "a Moroccan takchita: an embroidered kaftan with a jeweled belt",
    "Niger": "a Nigerien embroidered boubou dress with bold patterns and a head wrap",
    "Ouganda": "a Ugandan gomesi dress: a bright sash-belted dress with puffed sleeves",
    "République Centrafricaine": "a Central African wax-print dress with bold patterns and a head wrap",
    "République Démocratique du Congo": "a Congolese liputa wax-print wrap dress with a matching headscarf",
    "Sénégal": "a Senegalese boubou dress with bold wax-print patterns and gold jewelry",
    "Seychelles": "a Seychellois Creole dress: colorful ruffled skirt with a straw hat",
    "Tchad": "a Chadian embroidered boubou dress with a head wrap",
    "Togo": "a Togolese wax-print dress with bold patterns and beaded jewelry",
    "Tunisie": "a Tunisian embroidered kaftan with silver jewelry and a headscarf",
    "Zambie": "a Zambian chitenge wax-print wrap dress with a matching head wrap",

    "Afghanistan": "an Afghan embroidered dress with mirror-work and a colorful headscarf",
    "Bangladesh": "a Bangladeshi shalwar kameez in vibrant colors with gold jewelry",
    "Brunei": "a Bruneian baju kurung: an elegant loose tunic and long skirt with gold trim",
    "Cambodge": "a Cambodian sampot silk skirt with a fitted embroidered blouse",
    "Chine": "a red Chinese qipao dress with gold floral embroidery and a side slit",  # (vérifié en jeu) 070
    "Corée du Sud": "a Korean hanbok: a short embroidered jacket over a high-waisted skirt",
    "Inde": "a red Indian-inspired dress with gold embroidery and bangles",  # (vérifié en jeu) 072
    "Indonésie": "an Indonesian kebaya: an embroidered blouse over a batik-patterned skirt",
    "Iran": "a Persian-inspired embroidered dress with a colorful patterned scarf",
    "Japon": "a red furisode-inspired kimono dress with a floral obi sash",
    "Kazakhstan": "a Kazakh embroidered dress with a fur-trimmed vest and a beaded headpiece",
    "Kirghizistan": "a Kyrgyz embroidered dress with a velvet vest and a beaded headpiece",
    "Laos": "a Laotian sinh silk skirt with a fitted blouse and a silver belt",
    "Malaisie": "a Malaysian baju kurung: an elegant loose tunic and skirt with batik patterns",
    "Mongolie": "a Mongolian deel: a colorful silk robe with a sash belt",
    "Myanmar": "a Burmese htamein silk skirt with a fitted blouse and flowers in her hair",
    "Népal": "a Nepali gunyu cholo: a red wrap skirt with an embroidered blouse",
    "Pakistan": "a Pakistani shalwar kameez in vibrant embroidered fabric with gold jewelry",
    "Philippines": "a Filipiniana dress with butterfly sleeves and floral embroidery",
    "Singapour": "a rust-red floral batik nyonya kebaya blouse with pearl-beaded edge trim, a matching batik sarong skirt, black shoes",  # (vérifié en jeu, recadré 2026-08-31) 085
    "Taïwan": "a red qipao dress with floral embroidery, Taiwan-style",
    "Thaïlande": "a Thai silk sabai dress with gold trim and a traditional headpiece",
    "Turkménistan": "a Turkmen embroidered velvet dress with a tall traditional headpiece",
    "Vietnam": "a Vietnamese áo dài: a fitted silk tunic over cropped trousers",

    "Argentine": "an Argentine tango dress: a fitted red dress with a slit and fringe hem",
    "Bolivie": "a Bolivian cholita-inspired outfit: a colorful pollera skirt with an embroidered shawl",
    "Canada": "a Canadian lumberjack-chic mini dress: red-and-black plaid with a maple leaf pin",
    "Chili": "a Chilean cueca dance dress with a floral-print full skirt",
    "Colombie": "a Colombian cumbia dress: a bright ruffled skirt with a floral crown",
    "Costa Rica": "a Costa Rican folk dress with a bright ruffled skirt and floral embroidery",
    "Cuba": "a Cuban rumba dress: a fitted polka-dot dress with ruffles",
    "Équateur": "an Ecuadorian Andean-inspired outfit: an embroidered blouse with a full pollera skirt",
    "États-Unis": "a classic American pin-up sailor dress in navy and white with red trim",
    "Guatemala": "a colorful Guatemalan huipil blouse with a red-orange-green-blue-purple diamond zigzag pattern, a black skirt, black shoes",  # (vérifié en jeu, recadré 2026-08-31) 099
    "Haïti": "a Haitian karabela dress: a bright madras-plaid ruffled dress with a headwrap",
    "Mexique": "a Mexican china poblana dress: a sequined green-white-red skirt with an embroidered blouse",
    "Paraguay": "a Paraguayan ñandutí lace dress with delicate white embroidery",
    "Pérou": "a Peruvian Andean-inspired outfit: an embroidered blouse with a colorful pollera skirt",
    "République Dominicaine": "a Dominican merengue dress: a bright ruffled dress with a floral print",
    "Uruguay": "a Uruguayan gaucho-inspired outfit: a full skirt with a embroidered blouse and a neckerchief",
    "Venezuela": "a Venezuelan joropo dress: a bright ruffled dress with a floral print",

    "Australie": "an Akubra-style wide-brim hat, a khaki safari coat with a brown collar and belt over a red shirt, brown lace-up boots",  # (vérifié en jeu, recadré 2026-08-31) 107
    "Nouvelle-Calédonie": "a Kanak-inspired bright floral wrap dress with a flower crown",
    "Nouvelle-Zélande": "a Māori-inspired dress with a woven flax-pattern bodice and a fern motif",
    "Tahiti": "a Tahitian pareo wrap dress in bright tropical print with a flower crown",
    "Vanuatu": "a Vanuatu grass-skirt-inspired festive outfit with a floral top and shell jewelry",
    "Wallis-et-Futuna": "a Wallisian missionary-style white dress with a floral crown and shell necklace",

    "Brésil": "a vibrant Bahian baiana-style dress: white lace off-shoulder blouse, a knee-length colorful tiered skirt in green, yellow and blue, layered beaded necklaces, a white flower in her hair",
    "Israël": "an elegant breezy blue-and-white knee-length Mediterranean summer dress evoking Israel's national colors, a thin blue sash, delicate silver jewelry",
    "Liban": "a festive red-and-white Lebanese dabke folk costume: a gold-trimmed embroidered vest over a white blouse, a knee-length red skirt with gold trim, a red fez-style headpiece",
}


def build_prompt(pays: str) -> str:
    return f"{FANNY_BASE}wearing {OUTFITS[pays]}, {STYLE_SUFFIX}."


def main():
    missing = [pays for pays, _slug, _texte in WORLD_TOUR_COUNTRIES if pays not in OUTFITS]
    if missing:
        raise SystemExit(f"Tenue manquante pour : {missing}")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for i, (pays, _slug, _texte) in enumerate(WORLD_TOUR_COUNTRIES, start=1):
            f.write(f"{i:03d}\t{pays}\t{build_prompt(pays)}\n")

    print(f"{len(WORLD_TOUR_COUNTRIES)} prompts écrits dans {OUT_PATH}")


if __name__ == "__main__":
    main()
