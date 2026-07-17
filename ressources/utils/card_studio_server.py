# -*- coding: utf-8 -*-
"""Éditeur web local pour composer manuellement un jeu de cartes à partir des
112 portraits "Fanny Pétanque World Tour" et/ou d'images importées librement,
avec prévisualisation en direct (taille de carte, forme des coins, nom
affiché ou non) et export vers MakePlayingCards, Print Europe, ou en sprites
prêts pour un jeu vidéo.

Aucune dépendance externe (pas de Flask) : un simple serveur HTTP basé sur
la bibliothèque standard, pour éviter tout souci d'environnement Python
"externally managed". Le rendu des cartes réutilise ressources/utils/
card_render.py, le même moteur que les scripts de génération en ligne de
commande - la prévisualisation dans le navigateur est donc pixel-identique
à ce que produira l'export final.

Usage : python3 ressources/utils/card_studio_server.py [port, défaut 8765]
Puis ouvrir http://localhost:8765/ dans un navigateur.
"""
import base64
import io
import json
import os
import sys
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = "/home/adm1/Fanny_P-tanque_World_Tour"
sys.path.insert(0, ROOT)
from Scripts.dialogues import WORLD_TOUR_COUNTRIES  # noqa: E402
from ressources.utils.card_render import (  # noqa: E402
    CARD_SIZES, RANKS, SUITS, SUIT_COLORS, SUIT_SYMBOLS, portrait_path, render_back, render_card,
)
from PIL import Image  # noqa: E402

STATIC_DIR = f"{ROOT}/ressources/utils/card_studio"
THUMB_CACHE_DIR = f"{ROOT}/ressources/playing_cards/_web_thumbs"
UPLOADS_DIR = f"{ROOT}/ressources/playing_cards/_web_uploads"
UPLOADS_INDEX = f"{UPLOADS_DIR}/index.json"
EXPORT_DIR = f"{ROOT}/ressources/playing_cards/web_export"

MIME = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8", ".png": "image/png", ".jpg": "image/jpeg"}

MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 Mo par image, garde-fou

# ---------- registre des assets (portraits Fanny + imports libres) ----------

ASSETS = {}  # asset_id -> {"label": str, "image_path": str, "source": "fanny"|"custom"}


def _load_fanny_assets():
    for tier, (pays, slug, _texte) in enumerate(WORLD_TOUR_COUNTRIES):
        ASSETS[f"fanny:{tier}"] = {
            "label": pays, "image_path": portrait_path(tier, slug), "source": "fanny",
        }


def _load_custom_assets():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    if not os.path.isfile(UPLOADS_INDEX):
        return
    with open(UPLOADS_INDEX, encoding="utf-8") as f:
        index = json.load(f)
    for asset_id, entry in index.items():
        path = f"{UPLOADS_DIR}/{entry['file']}"
        if os.path.isfile(path):
            ASSETS[asset_id] = {"label": entry["label"], "image_path": path, "source": "custom"}


def _save_custom_index():
    index = {
        aid: {"file": os.path.basename(a["image_path"]), "label": a["label"]}
        for aid, a in ASSETS.items() if a["source"] == "custom"
    }
    with open(UPLOADS_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def add_custom_asset(filename, raw_bytes):
    if len(raw_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError(f"{filename} dépasse la taille max ({MAX_UPLOAD_BYTES // (1024*1024)} Mo)")
    img = Image.open(io.BytesIO(raw_bytes))
    img.load()  # lève une exception si le fichier n'est pas une image valide
    asset_id = f"custom:{uuid.uuid4().hex[:12]}"
    stored_name = f"{asset_id.split(':')[1]}.png"
    out_path = f"{UPLOADS_DIR}/{stored_name}"
    img.convert("RGB").save(out_path, "PNG")
    label = os.path.splitext(filename)[0][:60]
    ASSETS[asset_id] = {"label": label, "image_path": out_path, "source": "custom"}
    _save_custom_index()
    return asset_id


def assets_payload():
    return [
        {"id": aid, "label": a["label"], "source": a["source"]}
        for aid, a in ASSETS.items()
    ]


def ensure_thumb(asset_id):
    safe_name = asset_id.replace(":", "_")
    out_path = f"{THUMB_CACHE_DIR}/{safe_name}.jpg"
    if os.path.isfile(out_path):
        return out_path
    asset = ASSETS.get(asset_id)
    if asset is None:
        return None
    os.makedirs(THUMB_CACHE_DIR, exist_ok=True)
    img = Image.open(asset["image_path"]).convert("RGB")
    img.thumbnail((220, 300))
    img.save(out_path, "JPEG", quality=82)
    return out_path


# ---------- plan de jeu / rendu ----------

def build_slot_list(joker_count):
    slots = [(rank, suit) for suit in SUITS for rank in RANKS]  # 52, ordre standard
    jokers = [("JOKER", "red" if i % 2 == 0 else "black") for i in range(joker_count)]
    return slots + jokers


def _size_from_payload(payload):
    size_key = payload.get("size_preset")
    if size_key and size_key in CARD_SIZES:
        return CARD_SIZES[size_key]
    custom = payload.get("trim_mm")
    if custom and len(custom) == 2:
        return (float(custom[0]), float(custom[1]))
    return CARD_SIZES["poker"]


def render_slot(target, asset_id, rank, suit_or_color, trim_mm, corner_style, show_label):
    asset = ASSETS.get(asset_id)
    if asset is None:
        raise ValueError(f"asset inconnu : {asset_id}")
    if rank == "JOKER":
        color = SUIT_COLORS["hearts"] if suit_or_color == "red" else SUIT_COLORS["clubs"]
        return render_card(target, asset["image_path"], asset["label"], "JOKER", "", color, is_joker=True,
                            trim_mm=trim_mm, corner_style=corner_style, show_label=show_label)
    color = SUIT_COLORS[suit_or_color]
    symbol = SUIT_SYMBOLS[suit_or_color]
    return render_card(target, asset["image_path"], asset["label"], rank, symbol, color,
                        trim_mm=trim_mm, corner_style=corner_style, show_label=show_label)


def image_to_bytes(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, fmt)
    return buf.getvalue()


def build_export_sprites(assignment, joker_count, trim_mm, corner_style, show_label):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for rank, suit in build_slot_list(joker_count):
            key = f"{rank}-{suit}"
            asset_id = assignment[key]
            img = render_slot("sprite", asset_id, rank, suit, trim_mm, corner_style, show_label)
            b = io.BytesIO()
            img.save(b, "PNG")
            fname = f"{rank}-{suit}.png" if rank != "JOKER" else f"joker-{suit}.png"
            zf.writestr(fname, b.getvalue())
        back = render_back("sprite", trim_mm=trim_mm, corner_style=corner_style)
        b = io.BytesIO()
        back.save(b, "PNG")
        zf.writestr("back.png", b.getvalue())
    return buf.getvalue(), "fanny_card_studio_sprites.zip", "application/zip"


def build_export_mpc(assignment, joker_count, trim_mm, corner_style, show_label):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        seq = 1
        for rank, suit in build_slot_list(joker_count):
            key = f"{rank}-{suit}"
            asset_id = assignment[key]
            img = render_slot("mpc", asset_id, rank, suit, trim_mm, corner_style, show_label).convert("RGB")
            b = io.BytesIO()
            img.save(b, "PNG", dpi=(300, 300))
            fname = f"{seq:02d}_{rank}-{suit}.png" if rank != "JOKER" else f"{seq:02d}_joker-{suit}.png"
            zf.writestr(f"fronts/{fname}", b.getvalue())
            seq += 1
        back = render_back("mpc", trim_mm=trim_mm, corner_style=corner_style).convert("RGB")
        b = io.BytesIO()
        back.save(b, "PNG", dpi=(300, 300))
        zf.writestr("back.png", b.getvalue())
        w_mm, h_mm = trim_mm
        readme = (
            "Fanny Card Studio - export MakePlayingCards.com\n\n"
            f"1. Produit \"Custom Game Cards\", taille {w_mm}x{h_mm}mm (verifier la disponibilite\n"
            "   de cette taille exacte sur le configurateur MPC, sinon choisir le format standard\n"
            "   le plus proche).\n"
            f"2. {len(assignment)} cartes uniques, verso : option \"same image for all cards\" avec back.png.\n"
            "3. Uploader les fichiers de fronts/ en conservant l'ordre numerique du prefixe.\n"
            "4. Fichiers deja au bon format (fond perdu + marge de securite inclus, 300 dpi).\n"
            f"5. Coins : {'arrondis' if corner_style == 'rounded' else 'carres'} - selectionner\n"
            "   l'option correspondante sur le site si disponible (c'est MPC qui decoupe).\n"
        )
        zf.writestr("LISEZ-MOI.txt", readme)
    return buf.getvalue(), "fanny_card_studio_mpc.zip", "application/zip"


def build_export_printeurope(assignment, joker_count, trim_mm, corner_style, show_label):
    pages = []
    for rank, suit in build_slot_list(joker_count):
        key = f"{rank}-{suit}"
        asset_id = assignment[key]
        pages.append(render_slot("printeurope", asset_id, rank, suit, trim_mm, corner_style, show_label).convert("CMYK"))
    back = render_back("printeurope", trim_mm=trim_mm, corner_style=corner_style).convert("CMYK")
    all_pages = [back] + pages
    buf = io.BytesIO()
    all_pages[0].save(buf, format="PDF", save_all=True, append_images=all_pages[1:], resolution=300)
    return buf.getvalue(), "fanny_card_studio_printeurope.pdf", "application/pdf"


EXPORTERS = {"sprite": build_export_sprites, "mpc": build_export_mpc, "printeurope": build_export_printeurope}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, data, content_type, filename=None):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path):
        if not path or not os.path.isfile(path):
            self.send_error(404)
            return
        ext = os.path.splitext(path)[1]
        with open(path, "rb") as f:
            data = f.read()
        self._send_bytes(data, MIME.get(ext, "application/octet-stream"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "":
            self._send_file(f"{STATIC_DIR}/index.html")
        elif path.startswith("/static/"):
            self._send_file(f"{STATIC_DIR}/{path[len('/static/'):]}")
        elif path == "/api/assets":
            self._send_json({"assets": assets_payload(), "sizes": CARD_SIZES})
        elif path.startswith("/thumbs/"):
            asset_id = path[len("/thumbs/"):].rsplit(".", 1)[0].replace("_", ":", 1)
            self._send_file(ensure_thumb(asset_id))
        else:
            self.send_error(404)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json({"error": "JSON invalide"}, 400)
            return

        if parsed.path == "/api/upload":
            try:
                added = []
                for f in payload.get("files", []):
                    raw = base64.b64decode(f["data"])
                    asset_id = add_custom_asset(f["name"], raw)
                    added.append({"id": asset_id, "label": ASSETS[asset_id]["label"], "source": "custom"})
                self._send_json({"assets": added})
            except Exception as e:  # noqa: BLE001
                self._send_json({"error": str(e)}, 400)
            return

        if parsed.path == "/api/preview":
            try:
                target = payload["target"]
                asset_id = payload["asset_id"]
                rank, suit = payload["rank"], payload["suit"]
                trim_mm = _size_from_payload(payload)
                corner_style = payload.get("corner_style", "rounded")
                show_label = bool(payload.get("show_label", True))
                img = render_slot(target, asset_id, rank, suit, trim_mm, corner_style, show_label)
                self._send_bytes(image_to_bytes(img), "image/png")
            except Exception as e:  # noqa: BLE001
                self._send_json({"error": str(e)}, 400)
            return

        if parsed.path == "/api/preview_back":
            try:
                target = payload["target"]
                trim_mm = _size_from_payload(payload)
                corner_style = payload.get("corner_style", "rounded")
                img = render_back(target, trim_mm=trim_mm, corner_style=corner_style)
                self._send_bytes(image_to_bytes(img), "image/png")
            except Exception as e:  # noqa: BLE001
                self._send_json({"error": str(e)}, 400)
            return

        if parsed.path == "/api/export":
            try:
                target = payload["target"]
                assignment = dict(payload["assignment"])
                joker_count = int(payload["joker_count"])
                trim_mm = _size_from_payload(payload)
                corner_style = payload.get("corner_style", "rounded")
                show_label = bool(payload.get("show_label", True))
                expected = {f"{r}-{s}" for r, s in build_slot_list(joker_count)}
                missing = sorted(expected - set(assignment.keys()))
                if missing:
                    self._send_json({"error": f"Cases non remplies : {', '.join(missing)}"}, 400)
                    return
                unknown = sorted(set(assignment.values()) - set(ASSETS.keys()))
                if unknown:
                    self._send_json({"error": f"Image(s) inconnue(s) : {', '.join(unknown)}"}, 400)
                    return
                exporter = EXPORTERS[target]
                data, filename, content_type = exporter(assignment, joker_count, trim_mm, corner_style, show_label)
                os.makedirs(EXPORT_DIR, exist_ok=True)
                with open(f"{EXPORT_DIR}/{filename}", "wb") as f:
                    f.write(data)
                self._send_bytes(data, content_type, filename)
            except KeyError as e:
                self._send_json({"error": f"Champ manquant : {e}"}, 400)
            except Exception as e:  # noqa: BLE001
                self._send_json({"error": str(e)}, 400)
            return

        self.send_error(404)


def main():
    _load_fanny_assets()
    _load_custom_assets()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Card Studio sur http://localhost:{port}/  (Ctrl+C pour arrêter)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
