#!/usr/bin/env python3
"""Génère 3 jeux de cartes thématiques (Sexy, Plage/Ville, Outfits) à partir
des illustrations pin-up de outputs/Pin_up_Rétro_Défaut_, avec un assortiment
STRICT de la couleur de la tenue à la couleur de la carte (rouge pour
cœur/carreau, noir pour pique/trèfle) - décidé avec l'utilisateur.

Chaque dossier source a été vérifié visuellement (pas seulement par le nom,
souvent trompeur) avant d'être retenu ici : voir EXCLUDED_* pour les dossiers
écartés (nudité ou transparence trop suggestive).

Usage: python3 tools/generate_themed_decks.py
Sortie: assets/cards/theme-sexy/, assets/cards/theme-plage-ville/,
        assets/cards/theme-outfits/  (52 cartes + 2 jokers + dos, chacun)
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "outputs" / "Pin_up_Rétro_Défaut_"
OUT_ROOT = ROOT / "assets" / "cards"

CARD_W, CARD_H = 600, 840  # ratio 5:7, identique au deck existant
CORNER_RADIUS = 28
BORDER_WIDTH = 8

SUITS_RED = ["hearts", "diamonds"]
SUITS_BLACK = ["clubs", "spades"]
ALL_SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUIT_SYMBOLS = {"hearts": "♥", "diamonds": "♦", "clubs": "♣", "spades": "♠"}
SUIT_COLORS = {"hearts": (196, 30, 40), "diamonds": (196, 30, 40), "clubs": (25, 25, 25), "spades": (25, 25, 25)}
RED = (196, 30, 40)
BLACK = (25, 25, 25)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SYMBOL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Dossiers jamais utilisés (nudité ou transparence trop suggestive, vérifié
# visuellement) - voir generate_card_sprites.py pour l'historique de
# T_shirt_mouillé/Intégral_*, et cette session pour les deux ajouts.
EXCLUDED_FOLDER_PREFIXES = ("Intégral_",)
EXCLUDED_FOLDER_NAMES = {"T_shirt_mouillé", "Nuisette_transparente", "Robe_de_plage_transparent"}


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def bbox_crop(img, margin_frac=0.05):
    """Recadre sur le sujet réel (ignore les marges quasi-blanches autour du
    personnage). Certains rendus source remplissent tout le canevas carré
    sans la moindre marge (tête à y=0, pieds à y=1024) - sans ce recadrage,
    un simple redimensionnement laisserait tête/pieds coller pile aux bords
    de la carte, ce qui se lit comme une image "tronquée" une fois posée
    dans le cadre 5:7 de la carte (voir contain_fit ci-dessous)."""
    rgb = img.convert("RGB")
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg).convert("L")
    diff = diff.point(lambda p: 255 if p > 12 else 0)  # tolérance à l'anti-aliasing
    bbox = diff.getbbox()
    if bbox is None:
        return rgb
    left, top, right, bottom = bbox
    w, h = rgb.size
    margin_y = int((bottom - top) * margin_frac)
    margin_x = int((right - left) * margin_frac)
    left = max(0, left - margin_x)
    top = max(0, top - margin_y)
    right = min(w, right + margin_x)
    bottom = min(h, bottom + margin_y)
    return rgb.crop((left, top, right, bottom))


def contain_fit(img, target_w, target_h, bg=(255, 255, 255)):
    """Redimensionne en 'contain' (le sujet entier reste visible, jamais
    rogné) et centre sur un fond uni - contrairement à un cover-fit qui
    remplirait tout le cadre quitte à rogner, ce qui tronquait des
    personnages déjà cadrés pile dans leur canevas source."""
    src_ratio = img.width / img.height
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_w = target_w
        new_h = max(1, int(new_w / src_ratio))
    else:
        new_h = target_h
        new_w = max(1, int(new_h * src_ratio))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h), bg)
    canvas.paste(resized, ((target_w - new_w) // 2, (target_h - new_h) // 2))
    return canvas


def draw_corner_index(canvas, rank_label, symbol, color, top_left):
    badge_w, badge_h = 92, 132
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.rounded_rectangle([(0, 0), (badge_w - 1, badge_h - 1)], radius=18, fill=(255, 255, 255, 235))

    rank_font = ImageFont.truetype(FONT_BOLD, 44)
    symbol_font = ImageFont.truetype(FONT_SYMBOL, 40)

    draw.text((badge_w / 2, 34), rank_label, font=rank_font, fill=color, anchor="mm")
    draw.text((badge_w / 2, 92), symbol, font=symbol_font, fill=color, anchor="mm")

    canvas.alpha_composite(badge, top_left)
    rotated = badge.rotate(180)
    canvas.alpha_composite(
        rotated,
        (CARD_W - top_left[0] - badge_w, CARD_H - top_left[1] - badge_h),
    )


def build_card(image_path, rank_label, symbol, color, is_joker=False):
    canvas = Image.new("RGBA", (CARD_W, CARD_H), (255, 255, 255, 255))

    art = Image.open(image_path).convert("RGB")
    art = bbox_crop(art)
    art = contain_fit(art, CARD_W, CARD_H - 40)
    canvas.paste(art, (0, 40))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, 0), (CARD_W, 40)], fill=(250, 247, 240, 255))
    draw.rectangle([(0, CARD_H - 4), (CARD_W, CARD_H)], fill=color)

    mask = rounded_mask((CARD_W, CARD_H), CORNER_RADIUS)
    rounded = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    rounded.paste(canvas, (0, 0), mask)
    canvas = rounded

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        [(BORDER_WIDTH // 2, BORDER_WIDTH // 2), (CARD_W - BORDER_WIDTH // 2 - 1, CARD_H - BORDER_WIDTH // 2 - 1)],
        radius=CORNER_RADIUS,
        outline=color,
        width=BORDER_WIDTH,
    )

    if is_joker:
        badge_w, badge_h = 200, 60
        badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.rounded_rectangle([(0, 0), (badge_w - 1, badge_h - 1)], radius=14, fill=(255, 255, 255, 235))
        font = ImageFont.truetype(FONT_BOLD, 30)
        bd.text((badge_w / 2, badge_h / 2), "JOKER", font=font, fill=color, anchor="mm")
        canvas.alpha_composite(badge, (CARD_W // 2 - badge_w // 2, 14))
        canvas.alpha_composite(badge.rotate(180), (CARD_W // 2 - badge_w // 2, CARD_H - 14 - badge_h))
    else:
        draw_corner_index(canvas, rank_label, symbol, color, (14, 14))

    return canvas


def build_back(accent, label):
    canvas = Image.new("RGBA", (CARD_W, CARD_H), (*accent, 255))
    draw = ImageDraw.Draw(canvas)

    dark = tuple(max(0, c - 28) for c in accent)
    step = 40
    for y in range(-CARD_H, CARD_H * 2, step):
        draw.line([(0, y), (CARD_W, y + CARD_W)], fill=(*dark, 255), width=6)
        draw.line([(CARD_W, y), (0, y + CARD_W)], fill=(*dark, 255), width=6)

    inner_margin = 36
    draw.rounded_rectangle(
        [(inner_margin, inner_margin), (CARD_W - inner_margin, CARD_H - inner_margin)],
        radius=20,
        outline=(250, 247, 240, 255),
        width=6,
    )

    badge_w, badge_h = 380, 200
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.ellipse([(0, 0), (badge_w - 1, badge_h - 1)], fill=(250, 247, 240, 255), outline=(*accent, 255), width=5)
    font_title = ImageFont.truetype(FONT_BOLD, 34)
    font_sub = ImageFont.truetype(FONT_BOLD, 20)
    bd.text((badge_w / 2, badge_h / 2 - 22), label, font=font_title, fill=accent, anchor="mm")
    bd.text((badge_w / 2, badge_h / 2 + 24), "RÉTRO", font=font_sub, fill=dark, anchor="mm")
    canvas.alpha_composite(badge, (CARD_W // 2 - badge_w // 2, CARD_H // 2 - badge_h // 2))

    mask = rounded_mask((CARD_W, CARD_H), CORNER_RADIUS)
    rounded = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    rounded.paste(canvas, (0, 0), mask)
    draw = ImageDraw.Draw(rounded)
    draw.rounded_rectangle(
        [(BORDER_WIDTH // 2, BORDER_WIDTH // 2), (CARD_W - BORDER_WIDTH // 2 - 1, CARD_H - BORDER_WIDTH // 2 - 1)],
        radius=CORNER_RADIUS,
        outline=(250, 247, 240, 255),
        width=BORDER_WIDTH,
    )
    return rounded


# ---------------------------------------------------------------------
# Sélection des dossiers sources par thème et par couleur - chaque dossier
# listé ici a été ouvert et relu visuellement (pas seulement le nom, souvent
# trompeur) pendant cette session avant d'être retenu.
# ---------------------------------------------------------------------
THEMES = {
    "theme-sexy": {
        "label": "SEXY",
        "accent": RED,
        "red_folders": [
            "Nuisette_satin_bordeaux", "Set_satin_rouge_classique", "Set_velours_bordeaux",
            "Ensemble_soie_rouge", "Corset_satin_rouge_lacé",
        ],
        "black_folders": [
            "Body_résille_intégral", "Harness_body_Sangles_", "Gu_pière_noire_longue",
            "Vinyle_Latex_Club_", "Body_vinyle_noir", "Résille_en_vogue_Fishnet_",
            "Lingerie_dentelle_noire", "Chemise_courte_dentelle_n", "Longue_chemise_fendue",
        ],
    },
    "theme-plage-ville": {
        "label": "PLAGE VILLE",
        "accent": (30, 110, 170),
        "red_folders": ["Bikini_Rétro_à_pois", "Maillot_une_pièce_rouge", "Haut_Vichy_Jupe_Classique"],
        "black_folders": [
            "All_Black_parisien", "Robe_crayon_noire", "Style_YSL_Le_Smoking_",
            "Bikini_ficelle_noir", "Tenue_de_plongée", "Tenue_de_surfeuse",
        ],
    },
}

# ---------------------------------------------------------------------
# Deck "Outfits" : contrairement à Sexy/Plage-Ville, la couleur de la tenue
# n'a PAS besoin de correspondre à la couleur de la carte (assoupli avec
# l'utilisateur pour pouvoir exploiter toutes les tenues disponibles, pas
# seulement les ~25 rouges/noires). Une tenue = une carte, jamais deux
# cartes avec la même tenue - c'est la variété qui prime ici. Liste
# construite en relisant visuellement la quasi-totalité des dossiers de
# outputs/Pin_up_Rétro_Défaut_ (197 au total) : exclut les dossiers de
# nudité/transparence (EXCLUDED_*), les dossiers de lingerie/maillots de
# bain déjà réservés aux decks Sexy et Plage/Ville (pour que les 3 decks
# restent visuellement distincts), et Enterrement_de_vie_EVJF_ (texte
# "Bride Squad" incrusté dans l'image, inutilisable comme carte générique).
OUTFITS_POOL = [
    "Airport_OOTD", "All_Black_parisien", "Ankara_Mode_africaine_", "Années_2000_It_girl_",
    "Années_2010_Normcore_", "Années_20_Gar_onne_flappe", "Années_30_Hollywood_glamo",
    "Années_40_Wartime_chic_", "Années_50_New_Look_Dior_", "Années_60_Mod_London_",
    "Années_70_Disco_queen_", "Années_80_Power_shoulders", "Années_90_Minimalisme_CK_",
    "Après_ski_chic", "Balletcore", "Barbiecore_Tout_Rose_", "Blazer_pastel_Cigarette",
    "Blazer_robe_Power_dressin", "Bodycon_moulante", "British_country_Chelsea_",
    "Broderie_anglaise", "Brunch_du_dimanche",
    "Cachemire_luxueux", "Canadian_tuxedo_Tout_deni", "Chemise_à_carreaux_Jean_n",
    "Chemise_en_soie_Slip_dres", "Chemise_nouée_Short_taill", "Chemise_oversize_Shirt_dr",
    "Clean_Girl", "Coastal_Grandmother", "Col_carré_Milkmaid_", "Combinaison_lin_caramel",
    "Combishort_vintage", "Corporate_Siren", "Corsaire_Marinière", "Corset_fashion_Denim_",
    "Cottage_Witch", "Crop_top_Pantalon_cargo", "Dark_Academia", "Date_night_romantique",
    "Débardeur_Short_en_jean", "Dolce_Vita_Italienne_", "Dopamine_Dressing_Color_C",
    "Dos_croisé_Criss_cross_", "Drapé_asymétrique", "Empire_Régence_", "Ensemble_Crochet",
    "Ensemble_Rockabilly", "Ensemble_tweed_Co_ord_", "Ensemble_Yoga_Rose",
    "Entretien_Job_interview_", "Equestrian_chic", "Fairy_Grunge", "Festival_Coachella_",
    "Fit_Flare_évasée", "Garden_party", "Gilet_long_Pantalon_blanc", "Golf_fashion",
    "Goth_romantique", "Gyaru_Japanese_", "Haut_Vichy_Jupe_Classique", "Indie_Sleaze",
    "Invitée_mariage_Moderne_c", "Invitée_mariage_Romantiqu", "Jean_Chemisier_soie",
    "K_Fashion_Seoul_street_", "Layering_Superpositions_", "Light_Academia",
    "Look_Coquette_N_uds_Ruban", "Look_f_te_Velours_Paillet", "Look_lin_blanc_épuré",
    "Look_préppy_tennis", "Look_resort_tropical", "Look_scandi_minimal",
    "Look_terracotta_Monochrom", "Longue_décontractée_Maxi_", "Manteau_houndstooth_Béret",
    "Manteau_tartan_Col_roulé", "Manteau_Teddy_Bear", "Métallique_Futurisme",
    "Mini_à_manches_longues", "Mini_robe_à_bretelles_spa", "Mob_Wife_Maximalisme_",
    "Mori_Kei_Forest_girl_", "Nautical_Sailing_", "New_York_downtown",
    "Off_shoulder_paule_dénudé", "Organza_poétique", "Organza_sculpturale",
    "Parisienne_French_chic_", "_paules_bouffantes_Puff_s", "Pique_nique_chic",
    "Portefeuille_Wrap_midi", "Première_Cinéma_Red_carpe", "Pull_oversize_Legging",
    "Pull_Sweater_dress_", "Punk_Fashion_punk_", "Quiet_Luxury_Old_Money_",
    "Regencycore_Bridgerton_", "Réveillon_Nouvel_An", "Robe_à_pois_rouge",
    "Robe_crayon_noire", "Robe_crochet_bohème", "Robe_de_bal_tulle", "Robe_dos_nu_Ibiza_",
    "Robe_d_été_fleurie", "Robe_midi_velours", "Robe_prairie_Cottagecore_",
    "Robe_pull_chunky_knit", "Robe_velours_hivernal", "Robe_Vichy_bleue",
    "Robe_wrap_fleurie", "Salopette_en_jean", "Scandi_épuré_SSENSE_", "Sequins_de_jour",
    "Smockée_Shirred_", "Soft_Girl", "Soie_Pure_luxury_", "Style_Balenciaga_Déstruct",
    "Style_Balmain_Structuré_", "Style_Chanel_Tweed_Perles", "Style_Dior_Bar_Jacket_",
    "Style_Givenchy_Audrey_", "Style_Gucci_Maximalist_", "Style_Prada_Intellectuel_",
    "Style_Valentino_Rosso_", "Style_Versace_Baroque_", "Style_YSL_Le_Smoking_",
    "Surréalisme_Art_Mode_", "Sweat_à_capuche_Jogging", "Tailleur_jupe_tweed",
    "T_shirt_blanc_Jean", "T_shirt_rock_Jupe_cuir", "Trapèze_Mod_60s_",
    "Trench_léger_Slip_dress", "Twee", "Tweed_Chanel_inspired_", "Ura_Harajuku_Tokyo_",
    "Vernissage_Galerie_d_art", "Volants_superposés_Tiered", "Western_Chic_Cowboy_Core_",
]

# ---------------------------------------------------------------------
# 6 decks supplémentaires demandés par l'utilisateur, même principe que
# Outfits (couleur de la tenue libre, non assortie à la couleur de la
# carte) mais chacun avec son propre pool thématique. Les thèmes les plus
# étroits (Décennies, Haute Couture) n'ont qu'une dizaine de tenues
# vraiment uniques disponibles dans le dossier source : on les complète
# avec un ou deux gros réservoirs à poses multiples thématiquement
# cohérents (ex. Haut_Vichy_Jupe_Classique pour les années 50, listés en
# dernier pour que collect_images() les utilise seulement en complément,
# jamais en écrasant les tenues uniques). Un dossier peut apparaître dans
# plusieurs de ces decks (et dans Outfits) - ce n'est pas un problème,
# chaque deck reste indépendant ; la seule règle est "jamais deux fois la
# même tenue DANS le même deck".
FLAT_DECKS = {
    "theme-decennies": {
        "label": "DÉCENNIES",
        "accent": (150, 108, 40),
        "pool": [
            "Années_20_Gar_onne_flappe", "Années_30_Hollywood_glamo", "Années_40_Wartime_chic_",
            "Années_50_New_Look_Dior_", "Années_60_Mod_London_", "Années_70_Disco_queen_",
            "Années_80_Power_shoulders", "Années_90_Minimalisme_CK_", "Années_2000_It_girl_",
            "Années_2010_Normcore_", "Trapèze_Mod_60s_", "Regencycore_Bridgerton_",
            "Empire_Régence_", "Style_Givenchy_Audrey_", "Ensemble_Rockabilly",
            "Look_f_te_Velours_Paillet", "Haut_Vichy_Jupe_Classique", "Robe_wrap_fleurie",
        ],
    },
    "theme-couture": {
        "label": "HAUTE COUTURE",
        "accent": (25, 110, 80),
        # NB : Ensemble_soie_rouge écarté après vérification - malgré son nom
        # (« ensemble soie rouge »), ses poses sont en réalité boudoir/salle de
        # bain (« Sous la douche », « En équilibre Table »), pas de la haute
        # couture. Toujours vérifier plusieurs images d'un dossier avant de
        # l'utiliser comme réservoir de complément, pas seulement la première.
        "pool": [
            "Style_Chanel_Tweed_Perles", "Style_Dior_Bar_Jacket_", "Style_YSL_Le_Smoking_",
            "Style_Valentino_Rosso_", "Style_Gucci_Maximalist_", "Style_Balenciaga_Déstruct",
            "Style_Givenchy_Audrey_", "Style_Versace_Baroque_", "Style_Prada_Intellectuel_",
            "Style_Balmain_Structuré_", "Tweed_Chanel_inspired_", "Quiet_Luxury_Old_Money_",
            "Soie_Pure_luxury_", "Cachemire_luxueux", "Look_terracotta_Monochrom",
            "Première_Cinéma_Red_carpe", "Robe_de_bal_tulle", "Sequins_de_jour",
            "Organza_sculpturale", "Organza_poétique", "Drapé_asymétrique",
            "Métallique_Futurisme", "Broderie_anglaise", "Blazer_pastel_Cigarette",
            "Blazer_robe_Power_dressin", "Tailleur_jupe_tweed", "Manteau_houndstooth_Béret",
        ],
    },
    "theme-souscultures": {
        "label": "SOUS-CULTURES",
        "accent": (110, 25, 85),
        "pool": [
            "Goth_romantique", "Punk_Fashion_punk_", "Dark_Academia", "Light_Academia",
            "Indie_Sleaze", "Gyaru_Japanese_", "Cottage_Witch", "Fairy_Grunge",
            "K_Fashion_Seoul_street_", "Ura_Harajuku_Tokyo_", "Mori_Kei_Forest_girl_",
            "Soft_Girl", "Clean_Girl", "Balletcore", "Twee", "Barbiecore_Tout_Rose_",
            "Corporate_Siren", "Mob_Wife_Maximalisme_", "New_York_downtown",
            "Coastal_Grandmother", "Festival_Coachella_", "Longue_décontractée_Maxi_",
            "Robe_crochet_bohème", "Look_resort_tropical",
        ],
    },
    "theme-voyage": {
        "label": "VOYAGE & VACANCES",
        "accent": (20, 140, 135),
        "pool": [
            "Airport_OOTD", "Nautical_Sailing_", "Après_ski_chic", "Golf_fashion",
            "Equestrian_chic", "Pique_nique_chic", "Dolce_Vita_Italienne_",
            "Corsaire_Marinière", "British_country_Chelsea_", "Look_lin_blanc_épuré",
            "Robe_crochet_bohème", "Combinaison_lin_caramel", "Look_resort_tropical",
            "Robe_dos_nu_Ibiza_", "Paréo_Haut_de_maillot",
        ],
    },
    "theme-soiree": {
        "label": "SOIRÉE & GALA",
        "accent": (170, 130, 35),
        # NB : Longue_chemise_fendue écarté après vérification - c'est en
        # réalité une nuisette longue en voile TRANSPARENT (silhouette et
        # dessous visibles à travers le tissu), pas une robe de soirée. Même
        # leçon que pour Ensemble_soie_rouge dans le deck Couture : toujours
        # vérifier plusieurs images avant d'utiliser un dossier en réservoir.
        "pool": [
            "Réveillon_Nouvel_An", "Invitée_mariage_Moderne_c", "Invitée_mariage_Romantiqu",
            "Robe_velours_hivernal", "Date_night_romantique", "Vernissage_Galerie_d_art",
            "Portefeuille_Wrap_midi", "Robe_de_bal_tulle", "Première_Cinéma_Red_carpe",
            "Sequins_de_jour", "Look_f_te_Velours_Paillet", "Organza_poétique",
            "Organza_sculpturale", "Empire_Régence_", "Regencycore_Bridgerton_",
            "Chemise_en_soie_Slip_dres", "Mini_robe_à_bretelles_spa",
            "Look_Coquette_N_uds_Ruban", "Volants_superposés_Tiered",
        ],
    },
    "theme-sport": {
        "label": "SPORT & LOISIRS",
        "accent": (200, 95, 35),
        "pool": [
            "Ensemble_Yoga_Rose", "Sweat_à_capuche_Jogging", "Short_de_course_Débardeur",
            "Golf_fashion", "Look_préppy_tennis", "Balletcore", "Equestrian_chic",
            "Après_ski_chic", "Triangle_sportif_Micro_", "Legging_noir_Brassière_fl",
            "Tenue_de_surfeuse", "Tenue_de_plongée", "Short_en_jean_Haut_bikini",
        ],
    },
}


def folder_images(name):
    folder = SOURCE_DIR / name
    if not folder.is_dir():
        print(f"  ! dossier introuvable : {name}")
        return []
    if name.startswith(EXCLUDED_FOLDER_PREFIXES) or name in EXCLUDED_FOLDER_NAMES:
        raise RuntimeError(f"dossier exclu utilisé par erreur : {name}")
    pngs = sorted(folder.glob("xy_*.png")) or sorted(folder.glob("*.png"))
    return pngs


def collect_images(folder_names, count_needed):
    """Répartit `count_needed` images sur les dossiers listés, en plusieurs
    passes si besoin : à chaque passe, répartit équitablement entre les
    dossiers qui ont encore des images inutilisées, plutôt que de laisser le
    premier gros dossier tout consommer - garde de la variété de tenues.
    Plusieurs passes (pas une seule) pour ne pas sous-remplir quand un thème
    n'a que quelques dossiers à pose unique suivis d'un ou deux gros
    réservoirs : la première passe capée équitablement ne viderait pas ces
    réservoirs, une deuxième passe y revient tant qu'il reste des images."""
    taken = {name: 0 for name in folder_names}
    pools = {name: folder_images(name) for name in folder_names}
    images = []

    while len(images) < count_needed:
        progress = False
        remaining_names = [n for n in folder_names if taken[n] < len(pools[n])]
        if not remaining_names:
            break
        for name in remaining_names:
            if len(images) >= count_needed:
                break
            pngs = pools[name]
            available = pngs[taken[name]:]
            still_needed = count_needed - len(images)
            folders_left = sum(1 for n in remaining_names if taken[n] < len(pools[n])) or 1
            cap = max(1, -(-still_needed // folders_left))
            take = available[: min(cap, len(available), still_needed)]
            if take:
                images.extend(take)
                taken[name] += len(take)
                progress = True
        if not progress:
            break

    for name in folder_names:
        if taken[name]:
            print(f"    {name} -> {taken[name]} carte(s)")
    return images[:count_needed]


def build_outfits_deck(out_dir, accent, label):
    """Deck Outfits : une tenue distincte par carte (couleur de la tenue
    libre, non assortie à la couleur de la carte - voir commentaire sur
    OUTFITS_POOL). 52 cartes + 2 jokers = 54 tenues uniques nécessaires."""
    needed = 52 + 2
    if len(OUTFITS_POOL) < needed:
        raise RuntimeError(f"OUTFITS_POOL n'a que {len(OUTFITS_POOL)} tenues, il en faut {needed}")

    images = []
    for name in OUTFITS_POOL:
        pngs = folder_images(name)
        if not pngs:
            continue
        images.append(pngs[0])
        if len(images) >= needed:
            break
    print(f"  {len(images)} tenues distinctes réunies (besoin : {needed})")

    all_cards = [(rank, suit) for suit in ALL_SUITS for rank in RANKS]  # 52
    for (rank, suit), image_path in zip(all_cards, images):
        card_img = build_card(image_path, rank, SUIT_SYMBOLS[suit], SUIT_COLORS[suit])
        card_img.save(out_dir / f"{rank}-{suit}.png")

    joker_red_img = build_card(images[52], "JOKER", "", RED, is_joker=True)
    joker_red_img.save(out_dir / "joker-red.png")
    joker_black_img = build_card(images[53], "JOKER", "", BLACK, is_joker=True)
    joker_black_img.save(out_dir / "joker-black.png")

    back_img = build_back(accent, label)
    back_img.save(out_dir / "back.png")
    print(f"  -> 52 cartes (une tenue chacune) + 2 jokers + dos dans {out_dir}")


def build_flat_deck(pool, out_dir, accent, label):
    """Deck à thème libre (couleur de la tenue non assortie à la couleur de
    la carte) : utilise collect_images() pour répartir 54 images sur le
    pool fourni, en réservant les dossiers à pose unique pour garantir un
    maximum de tenues distinctes avant de puiser dans les gros réservoirs
    listés en fin de pool pour compléter."""
    images = collect_images(pool, 52 + 2)
    if len(images) < 54:
        distinct = len(images)
        print(f"  ATTENTION : seulement {distinct}/54 images distinctes disponibles pour {label}"
              f" - certaines images seront réutilisées sur 2 cartes (pénurie de contenu réelle"
              f" pour ce thème précis, pas un bug).")
        i = 0
        while len(images) < 54:
            images.append(images[i % distinct])
            i += 1

    all_cards = [(rank, suit) for suit in ALL_SUITS for rank in RANKS]  # 52
    for (rank, suit), image_path in zip(all_cards, images):
        card_img = build_card(image_path, rank, SUIT_SYMBOLS[suit], SUIT_COLORS[suit])
        card_img.save(out_dir / f"{rank}-{suit}.png")

    if len(images) > 52:
        joker_red_img = build_card(images[52], "JOKER", "", RED, is_joker=True)
        joker_red_img.save(out_dir / "joker-red.png")
    if len(images) > 53:
        joker_black_img = build_card(images[53], "JOKER", "", BLACK, is_joker=True)
        joker_black_img.save(out_dir / "joker-black.png")

    back_img = build_back(accent, label)
    back_img.save(out_dir / "back.png")
    print(f"  -> {min(len(images), 52)} cartes + jokers + dos dans {out_dir}")


def main():
    for theme_key, cfg in THEMES.items():
        print(f"\n=== {theme_key} ===")
        out_dir = OUT_ROOT / theme_key
        out_dir.mkdir(parents=True, exist_ok=True)

        print("  Rouge (cœur/carreau) :")
        red_images = collect_images(cfg["red_folders"], 26 + 1)  # +1 pour le joker rouge
        print("  Noir (pique/trèfle) :")
        black_images = collect_images(cfg["black_folders"], 26 + 1)  # +1 pour le joker noir

        if len(red_images) < 27:
            print(f"  ATTENTION : seulement {len(red_images)}/27 images rouges disponibles")
        if len(black_images) < 27:
            print(f"  ATTENTION : seulement {len(black_images)}/27 images noires disponibles")

        red_cards = [(rank, suit) for suit in SUITS_RED for rank in RANKS]  # 26
        black_cards = [(rank, suit) for suit in SUITS_BLACK for rank in RANKS]  # 26

        for (rank, suit), image_path in zip(red_cards, red_images):
            card_img = build_card(image_path, rank, SUIT_SYMBOLS[suit], SUIT_COLORS[suit])
            card_img.save(out_dir / f"{rank}-{suit}.png")
        for (rank, suit), image_path in zip(black_cards, black_images):
            card_img = build_card(image_path, rank, SUIT_SYMBOLS[suit], SUIT_COLORS[suit])
            card_img.save(out_dir / f"{rank}-{suit}.png")

        if len(red_images) > 26:
            joker_red_img = build_card(red_images[26], "JOKER", "", RED, is_joker=True)
            joker_red_img.save(out_dir / "joker-red.png")
        if len(black_images) > 26:
            joker_black_img = build_card(black_images[26], "JOKER", "", BLACK, is_joker=True)
            joker_black_img.save(out_dir / "joker-black.png")

        back_img = build_back(cfg["accent"], cfg["label"])
        back_img.save(out_dir / "back.png")

        print(f"  -> {len(red_cards)} rouges + {len(black_cards)} noires + 2 jokers + dos dans {out_dir}")

    print("\n=== theme-outfits ===")
    outfits_dir = OUT_ROOT / "theme-outfits"
    outfits_dir.mkdir(parents=True, exist_ok=True)
    build_outfits_deck(outfits_dir, accent=(90, 70, 150), label="OUTFITS")

    for theme_key, cfg in FLAT_DECKS.items():
        print(f"\n=== {theme_key} ===")
        out_dir = OUT_ROOT / theme_key
        out_dir.mkdir(parents=True, exist_ok=True)
        build_flat_deck(cfg["pool"], out_dir, cfg["accent"], cfg["label"])


if __name__ == "__main__":
    main()
