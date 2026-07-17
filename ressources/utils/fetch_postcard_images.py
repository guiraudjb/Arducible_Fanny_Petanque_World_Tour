# -*- coding: utf-8 -*-
"""Récupère, pour chaque question "monument ou spécialité" du quizz
(quiz_monuments_facts.py = Q2 toujours, quiz_second_monuments_facts.py =
Q5 quand le pays n'a pas de question athlète pétanque), une photo réelle
librement réutilisable sur Wikimedia Commons (dépôt qui n'héberge QUE des
fichiers sous licence libre ou domaine public) - demande utilisateur du
2026-07-13 pour un verso "carte postale" du livret PDF.

Jamais d'image inventée/générée : si aucune photo pertinente n'est
trouvée après plusieurs tentatives de recherche, l'entrée est marquée
"missing" dans le manifest et la carte postale correspondante sera
simplement omise (même discipline que "AUCUNE INFORMATION TROUVÉE"
ailleurs dans le projet).

Idempotent : une entrée déjà "ok" dans le manifest avec son fichier
présent n'est pas re-téléchargée. Relancer après interruption ne refait
que le travail manquant.

Usage :
    python3 ressources/utils/fetch_postcard_images.py
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _THIS_DIR)

from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from quiz_monuments_facts import MONUMENTS  # noqa: E402
from quiz_second_monuments_facts import SECOND_MONUMENTS  # noqa: E402
from quiz_petanque_athletes import PETANQUE_ATHLETES  # noqa: E402

CACHE_DIR = os.path.join(_REPO_ROOT, "ressources", "quizz_pdf", "_postcards_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")

UA = "FannyPetanqueWorldTour/1.0 (educational hobby project; contact: guiraudjb@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"

STOPWORDS = {
    "le", "la", "les", "l", "de", "du", "des", "d", "en", "et", "à", "a",
    "sur", "sous", "dans", "un", "une", "au", "aux", "pour", "avec",
    "son", "ses", "ces", "cet", "cette", "qui", "que", "est", "ou",
    "très", "tout", "tous", "the", "of", "in", "and",
}

BAD_EXT = (".svg", ".pdf", ".djvu", ".ogv", ".webm", ".gif")

# corrections manuelles pour les cas où la recherche automatique risque de
# se tromper sur un homonyme (vérifié à la main pendant le prototypage) -
# ce ne sont que des REQUÊTES de recherche différentes, jamais une image
# choisie à l'aveugle : le même filtre de pertinence s'applique ensuite.
QUERY_OVERRIDES = {
    (0, "q5"): "Brandenburg Gate Berlin",
    (16, "q2"): "Colosseum Rome",
    (5, "q5"): "Atomium Brussels",
    (13, "q2"): "Guernsey cattle breed",
    (3, "q5"): "Geghard Monastery Armenia",
    (6, "q5"): "Kazanlak Rose Valley Bulgaria",
    (8, "q5"): "Edinburgh Castle Scotland",
    (22, "q5"): "Norwegian stave church",
    (23, "q2"): "Kinderdijk windmills",
    (69, "q2"): "Great Wall of China",
    (18, "q2"): "Freedom Monument Riga",
    (55, "q5"): "Air Tenere Niger reserve",
    (75, "q2"): "Baiterek Tower Astana",
    (95, "q2"): "Cuban cigar Habano",
    (95, "q5"): "La Habana Vieja street",
    (29, "q2"): "Three Towers San Marino Monte Titano",
    (29, "q5"): "San Marino postage stamp",
    (62, "q5"): "Akodessewa fetish market Togo",
    (76, "q2"): "Burana Tower Kyrgyzstan",
    (94, "q5"): "Monteverde Cloud Forest Reserve",
    (96, "q5"): "Montecristi Panama hat Ecuador",
    (110, "q5"): "Naghol land diving Pentecost Vanuatu",
}

# quand même une requête de recherche ciblée continue de ramener une image
# hors-sujet (photo de l'INTÉRIEUR d'une tour au lieu de la tour elle-même,
# logo au lieu d'une vraie photo...), on impose directement le fichier
# Commons choisi à la main après vérification visuelle - toujours un vrai
# fichier Commons réel, jamais une image inventée.
EXACT_FILE_OVERRIDES = {
    (75, "q2"): "File:Baiterek August.jpg",
    (95, "q2"): "File:Cohiba Habanos Cigars from Cuba.jpg",

    # corrections de la relecture visuelle du 2026-07-13 (sujet erroné,
    # illustration/gravure au lieu d'une photo, ou cadrage trop serré/trop
    # éloigné pour reconnaître le monument) - chaque remplacement vérifié
    # visuellement avant d'être fixé ici.
    (2, "q2"): "File:Stonehenge, Wiltshire, England.jpg",
    (2, "q5"): "File:Big Ben Elizabeth Tower Full View.JPG",
    (4, "q2"): "File:Schonbrunn Palace - Vienna.jpg",
    (5, "q2"): "File:Bruxelles Manneken Pis.jpg",
    (6, "q5"): "File:Young rose pickers are documenting their grandma's outfits (Kazanlak, Bulgaria).jpg",
    (7, "q2"): "File:Petite sirène de Copenhague (conforme à la loi danoise).JPG",
    (12, "q2"): "File:Eiffel Tower from north Avenue de New York, Aug 2010.jpg",
    (18, "q2"): "File:Le monument de la liberté (Riga) (7585762710).jpg",
    (21, "q2"): "File:2024-09-22 Casino de Monte Carlo.jpg",
    (23, "q2"): "File:The windmills of Kinderdijk.JPG",
    (27, "q5"): "File:Casa Poporului 2 0 (6739696).jpeg",
    (35, "q2"): "File:Prague Castle and Charles Bridge, Czech Republic - Diliff.jpg",
    (36, "q2"): "File:Hagia Sophia Mars 2013.jpg",
    (37, "q2"): "File:Great Lavra Belltower panorama.jpg",
    (44, "q2"): "File:Basilique notre Dame de la Paix de Yamoussoukro 16.jpg",
    (46, "q2"): "File:The Great Pyramid of Giza from southeast corner.JPG",
    (46, "q5"): "File:Facade Abou Simbel2.JPG",
    (47, "q2"): "File:Elephants in Lopé National Park.JPG",
    (48, "q2"): "File:Guinee Fouta Djalon Canyon.jpg",
    (51, "q2"): "File:Great Mosque of Djenné 1.jpg",
    (52, "q2"): "File:Mauritius Seven-Coloured-Earths-01.jpg",
    (55, "q2"): "File:Niger, Agadez (43), Grand Mosque.jpg",
    (55, "q5"): "File:Fachi-Bilma-Dünen.jpg",
    (97, "q2"): "File:Statue of Liberty frontal 2.jpg",
    (101, "q2"): "File:Jesuit Missions of La Santísima Trinidad - panoramio (2).jpg",
    (58, "q5"): "File:The Rare Okapi (10549264174).jpg",

    # corrections de la relecture visuelle du 2026-07-13 (2e passe) : sujet
    # erroné (outil agricole au lieu de la mangrove, avions militaires
    # masquant le Mont Fuji), gravure au lieu d'une photo (Moaï), cadrage
    # trop serré (tours Petronas) ou trop éloigné (île de Gorée), vue
    # incomplète (Laure des Grottes de Kiev).
    (37, "q2"): "File:Kyiv Pechersk Lavra View from the Dnieper River.jpg",
    (59, "q2"): "File:Maison-des-esclaves-goree-01.jpg",
    (66, "q5"): "File:Dense Mangrove Forest of the Sundarban Tiger Reserve during High Tide, West Bengal, India 03.jpg",
    (74, "q2"): "File:Mount Fuji from Lake Yamanaka.JPG",
    (78, "q2"): "File:Kuala Lumpur Malaysia Petronas-Twin-Towers-01.jpg",
    (92, "q2"): "File:Moai at Rano Raraku - Easter Island (5956405378).jpg",

    # 104_q2 (Uruguay, "« La Mano »") : la requête entre guillemets a
    # matché un manuscrit de Chopin ("Là ci darem la mano", un air de
    # Mozart) sur le seul mot "mano" - repéré via demande utilisateur du
    # 2026-07-13.
    (104, "q2"): "File:La mano de Punta del Este.JPG",

    # 0_q5 (Allemagne, porte de Brandebourg) : la photo précédente ne
    # montrait que le quadrige tout en haut, pas la porte (colonnes/arches)
    # elle-même - demande utilisateur du 2026-07-13.
    (0, "q5"): "File:Brandenburger Tor morgens.jpg",

    # 87_q2 (Turkménistan, "la Porte de l'Enfer") : la recherche avait
    # matché la sculpture de Rodin "La Porte de l'Enfer" (Zurich) au lieu
    # du cratère gazier du Turkménistan - demande utilisateur du 2026-07-13.
    (87, "q2"): "File:Darvaza gas crater, Jähennem derwezesi, Door to Hell, Gates of Hell, Derweze, Turkmenistan.jpg",

    # 96_q2 (Équateur, îles Galápagos) : la photo précédente montrait un
    # crabe Sally Lightfoot en gros plan - remplacée par une image plus
    # représentative des Galápagos (tortue géante) - demande utilisateur
    # du 2026-07-13.
    (96, "q2"): "File:Santa Cruz giant tortoise 01.jpg",
}


def strip_article(name):
    m = re.match(r"^(le|la|les|l)[' ’]", name, re.IGNORECASE)
    if m:
        return name[m.end():]
    return name


def strip_accents(word):
    nfkd = unicodedata.normalize("NFKD", word)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def significant_words(text):
    words = re.findall(r"[A-Za-zÀ-ÿ]+", text.lower())
    return {strip_accents(w) for w in words if len(w) >= 3 and w not in STOPWORDS}


def api_get(params, retries=3):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except Exception as e:
            if attempt == retries - 1:
                print(f"  API error ({url}): {e}")
                return None
            time.sleep(2 * (attempt + 1))
    return None


def commons_search(query, limit=5):
    data = api_get({
        "action": "query", "list": "search", "srsearch": query,
        "srnamespace": 6, "srlimit": limit,
    })
    if not data:
        return []
    return [r["title"] for r in data.get("query", {}).get("search", [])]


def imageinfo(file_title, width=1600):
    data = api_get({
        "action": "query", "titles": file_title, "prop": "imageinfo",
        "iiprop": "url|extmetadata", "iiurlwidth": width,
    })
    if not data:
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        infos = page.get("imageinfo")
        if infos:
            return infos[0]
    return None


def pick_best_candidate(candidates, sig_words):
    """Ne retient un candidat QUE si son titre partage un mot significatif
    avec le nom recherché - sinon on préfère essayer la requête suivante
    (plus précise) plutôt que de risquer une image hors sujet (le
    "premier résultat quoi qu'il arrive" avait déjà produit un mauvais
    match lors du prototypage : une page de journal satirique de 1869
    pour "vache Guernesey", trouvée via le texte de description indexé
    par la recherche plein texte, pas via le titre du fichier)."""
    for title in candidates:
        if title.lower().endswith(BAD_EXT):
            continue
        title_words = significant_words(title)
        if sig_words & title_words:
            return title
    return None


def resolve_job(tier, slot, name, description, pays):
    if (tier, slot) in EXACT_FILE_OVERRIDES:
        title = EXACT_FILE_OVERRIDES[(tier, slot)]
        info = imageinfo(title)
        if info and "thumburl" in info:
            return {
                "status": "ok",
                "query_used": "(fichier imposé manuellement)",
                "commons_title": title,
                "image_url": info["thumburl"],
                "page_url": info.get("descriptionurl", ""),
                "artist": re.sub("<[^>]+>", "", info.get("extmetadata", {}).get("Artist", {}).get("value", "")),
                "license": info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", ""),
            }
        return {"status": "missing"}

    stripped = strip_article(name)
    override = QUERY_OVERRIDES.get((tier, slot))

    # Le mot-clé requis pour accepter un candidat est TOUJOURS dérivé du
    # sujet réel (le nom, ou la requête de correction manuelle qui le
    # désigne explicitement) - jamais du pays/mot de description ajoutés
    # aux requêtes suivantes pour élargir la recherche. Sinon un candidat
    # peut être accepté juste parce qu'il partage le nom du PAYS avec la
    # requête (repéré pendant le prototypage : une photo nocturne
    # quelconque d'Astana acceptée pour "tour Baïterek" via le seul mot
    # "astana" en commun, sans rapport avec la tour elle-même).
    core_words = significant_words(override if override else stripped)

    queries = []
    if override:
        queries.append(override)
    queries.append(stripped)
    queries.append(f"{stripped} {pays}")
    first_desc_word = next(iter(significant_words(description)), None)
    if first_desc_word:
        queries.append(f"{stripped} {first_desc_word}")

    for query in queries:
        candidates = commons_search(query)
        best = pick_best_candidate(candidates, core_words)
        if best:
            info = imageinfo(best)
            if info and "thumburl" in info:
                return {
                    "status": "ok",
                    "query_used": query,
                    "commons_title": best,
                    "image_url": info["thumburl"],
                    "page_url": info.get("descriptionurl", ""),
                    "artist": re.sub("<[^>]+>", "", info.get("extmetadata", {}).get("Artist", {}).get("value", "")),
                    "license": info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", ""),
                }
        time.sleep(0.3)
    return {"status": "missing"}


def download(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def build_jobs():
    jobs = []
    for tier, (pays, _slug, _text) in enumerate(WORLD_TOUR_COUNTRIES):
        name, desc = MONUMENTS[tier]
        jobs.append((tier, "q2", name, desc, pays))
        if tier not in PETANQUE_ATHLETES:
            name2, desc2 = SECOND_MONUMENTS[tier]
            jobs.append((tier, "q5", name2, desc2, pays))
    return jobs


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)

    jobs = build_jobs()
    only_tiers = [int(a) for a in sys.argv[1:]] or None

    counts = {"ok": 0, "missing": 0, "skipped": 0}
    for tier, slot, name, desc, pays in jobs:
        if only_tiers is not None and tier not in only_tiers:
            continue
        key = f"{tier}_{slot}"
        dest_path = os.path.join(CACHE_DIR, f"{key}.jpg")
        existing = manifest.get(key)
        if existing and existing.get("status") == "ok" and os.path.exists(dest_path) and os.path.getsize(dest_path) > 2000:
            counts["skipped"] += 1
            continue

        result = resolve_job(tier, slot, name, desc, pays)
        result.update({"tier": tier, "slot": slot, "pays": pays, "name": name})

        if result["status"] == "ok":
            try:
                download(result["image_url"], dest_path)
                result["local_path"] = dest_path
                counts["ok"] += 1
                print(f"[{tier:03d}/{slot}] {pays} - {name} -> {result['commons_title']}", flush=True)
            except Exception as e:
                print(f"[{tier:03d}/{slot}] {pays} - {name} : ÉCHEC téléchargement ({e})", flush=True)
                result = {"status": "missing", "tier": tier, "slot": slot, "pays": pays, "name": name}
                counts["missing"] += 1
        else:
            counts["missing"] += 1
            print(f"[{tier:03d}/{slot}] {pays} - {name} : AUCUNE IMAGE TROUVÉE", flush=True)

        manifest[key] = result
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        time.sleep(0.2)

    print("Terminé :", counts)


if __name__ == "__main__":
    main()
