#!/usr/bin/env python3
"""Génère les cartes-silhouette manquantes pour les 3 pays ajoutés le
2026-07-15 (Brésil, Israël, Liban - tiers 112/113/114, cf. Scripts/dialogues.py)
qui n'avaient jamais eu leur assets/Images/CountryMapsWorldTour/*.png.

Adapté de ~/story/build_world_tour_country_maps.py : ce script original
pointait vers un dossier de travail "fanny wold tour/" qui n'existe plus sur
le disque (pays_index.txt, worldtour background/, etc. ont disparu, sans
rapport avec les manipulations git d'aujourd'hui - ~/story n'a jamais été un
dépôt git). On réécrit donc en dur la liste des 3 pays manquants et on
écrit directement dans le jeu (ce dépôt), même logique de rendu (PLUME +
Playwright) que l'original.

Nécessite l'environnement Playwright dédié :
    /home/adm1/RAID/plume-automation-venv/bin/python3 \
        ressources/utils/generate_missing_country_maps_113_115.py
"""
import csv
import http.server
import os
import socketserver
import sys
import threading

from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.expanduser("~/story"))
from remove_background import remove_white_background_smart  # noqa: E402

PLUME_DIR = os.path.expanduser("~/PLUME")
IMG_OUT_DIR = os.path.join(REPO_ROOT, "assets", "Images", "CountryMapsWorldTour")

# (tier, pays, slug, iso3) - aucun des 3 n'est dans SMALL_COUNTRY_MARKER_COORDS
# ni COUNTRY_MARKER_COORDS de l'original (silhouette normale, taille correcte).
MISSING = [
    (112, "Brésil", "bresil", "BRA"),
    (113, "Israël", "israel", "ISR"),
    (114, "Liban", "liban", "LBN"),
]

LABEL_SIZE = 46
IMG_WIDTH, IMG_HEIGHT = 1600, 900
OUTPUT_WIDTH = 1024
HTTP_PORT = 8934

_JS_RENDER_COLORED = """
    async ({iso3, w, h}) => {
        let div = document.getElementById('__export_div__');
        if (div) div.remove();
        div = document.createElement('div');
        div.id = '__export_div__';
        div.style.position = 'fixed';
        div.style.left = '0';
        div.style.top = '0';
        div.style.width = w + 'px';
        div.style.height = h + 'px';
        div.style.background = '#ffffff';
        div.style.zIndex = '2147483647';
        document.body.appendChild(div);
        const dataMap = new Map([[iso3, 1]]);
        const config = {
            scale: 'world',
            labelType: 'none',
            palette: 'custom',
            customColors: ['#00A651', '#00A651'],
            showLegend: false,
            title: ''
        };
        await drawD3Map(div, config, dataMap);
        await document.fonts.ready;
    }
"""


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_server():
    os.chdir(PLUME_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = ReusableTCPServer(("127.0.0.1", HTTP_PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def _screenshot_and_resize(page, out_path):
    el = page.query_selector("#__export_div__")
    el.screenshot(path=out_path)
    with Image.open(out_path) as img:
        ratio = OUTPUT_WIDTH / img.width
        resized = img.resize((OUTPUT_WIDTH, round(img.height * ratio)), Image.LANCZOS)
        detoured = remove_white_background_smart(resized, thresh=20, min_hole_area=50)
        detoured.save(out_path)


def main():
    os.makedirs(IMG_OUT_DIR, exist_ok=True)
    from playwright.sync_api import sync_playwright

    httpd = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": IMG_WIDTH, "height": IMG_HEIGHT})
            page.goto(f"http://127.0.0.1:{HTTP_PORT}/index.html")
            page.wait_for_function("typeof drawD3Map === 'function'")

            for tier, pays, slug, iso3 in MISSING:
                out_path = os.path.join(IMG_OUT_DIR, f"{tier + 1:03d}_{slug}.png")
                page.evaluate(_JS_RENDER_COLORED, {"iso3": iso3, "w": IMG_WIDTH, "h": IMG_HEIGHT})
                page.wait_for_timeout(150)
                _screenshot_and_resize(page, out_path)
                print(f"[{tier + 1:03d}] {pays} ({iso3}) -> {out_path}")

            browser.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
