"""
Superpose des etiquettes numerotees sur les rendus de vue eclatee
(assemblage-articulation-eclate-{iso,face,droite,dessous}.png), a partir
de eclate_labels.json produit par render_articulation_eclate.py.

Post-traitement PIL pur (pas de FreeCAD) : un texte 3D dans la scene ne
resterait lisible que sous UN angle de camera donne, alors qu'un calcul de
projection 2D par vue reste net et bien oriente sous les 4 angles a la
fois.

Projection : pour une camera orthographique centree par ViewFit (voir
render_articulation_eclate.py), le pixel central correspond toujours a
l'axe de visee (proj_u = proj_v = 0 par construction, la camera regarde
droit devant elle), et l'echelle pixels/mm vaut img_h / cam.height. D'ou,
pour un point 3D p et une vue (campos, right, up, height) :

    proj_u = dot(p - campos, right)
    proj_v = dot(p - campos, up)
    px = img_w/2 + proj_u * (img_h / height)
    py = img_h/2 - proj_v * (img_h / height)   # Y image vers le bas, proj_v vers le haut

Usage :
    python3 label_eclate_views.py
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, 'eclate_labels.json')
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

CIRCLE_R = 15
FONT_SIZE = 18
CIRCLE_FILL = (255, 255, 255, 235)
CIRCLE_OUTLINE = (200, 30, 30)
TEXT_COLOR = (200, 30, 30)

VIEWS = [
    'assemblage-articulation-eclate-iso.png',
    'assemblage-articulation-eclate-face.png',
    'assemblage-articulation-eclate-droite.png',
    'assemblage-articulation-eclate-dessous.png',
]


def project(p, cam):
    dx = p[0] - cam['campos'][0]
    dy = p[1] - cam['campos'][1]
    dz = p[2] - cam['campos'][2]
    right, up = cam['right'], cam['up']
    proj_u = dx * right[0] + dy * right[1] + dz * right[2]
    proj_v = dx * up[0] + dy * up[1] + dz * up[2]
    scale = cam['img_h'] / cam['height']
    px = cam['img_w'] / 2.0 + proj_u * scale
    py = cam['img_h'] / 2.0 - proj_v * scale
    return px, py


def spread_labels(anchors, min_dist, iterations=60):
    """Ecarte iterativement les etiquettes qui se chevaucheraient (deux
    pieces proches en 3D peuvent se projeter au meme endroit a l'ecran,
    ex. la rotule juste a cote de l'axe central). Renvoie une position de
    label par piece, distincte de son ancrage si necessaire -- les
    positions modifiees recoivent une ligne de rappel vers l'ancrage
    reel lors du dessin."""
    labels = [list(p) for p in anchors]
    for _ in range(iterations):
        moved = False
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                dx = labels[j][0] - labels[i][0]
                dy = labels[j][1] - labels[i][1]
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < min_dist and dist > 1e-6:
                    push = (min_dist - dist) / 2.0
                    ux, uy = dx / dist, dy / dist
                    labels[i][0] -= ux * push
                    labels[i][1] -= uy * push
                    labels[j][0] += ux * push
                    labels[j][1] += uy * push
                    moved = True
                elif dist <= 1e-6:
                    # positions quasi identiques : ecart initial arbitraire pour amorcer la separation
                    labels[j][0] += min_dist / 2.0
                    labels[j][1] += 0.1
                    moved = True
        if not moved:
            break
    return [tuple(p) for p in labels]


def main():
    with open(JSON_PATH) as f:
        data = json.load(f)
    parts = data['parts']
    views = data['views']
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    for fname in VIEWS:
        img_path = os.path.join(HERE, fname)
        if not os.path.exists(img_path) or fname not in views:
            print("SKIP (introuvable) :", fname)
            continue
        cam = views[fname]
        img = Image.open(img_path).convert('RGBA')
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        anchors = [project((p['x'], p['y'], p['z']), cam) for p in parts]
        label_pos = spread_labels(anchors, min_dist=CIRCLE_R * 2 + 4)

        for (ax, ay), (lx, ly), part in zip(anchors, label_pos, parts):
            if (ax - lx) ** 2 + (ay - ly) ** 2 > 4:
                draw.line([ax, ay, lx, ly], fill=CIRCLE_OUTLINE, width=1)
            draw.ellipse(
                [lx - CIRCLE_R, ly - CIRCLE_R, lx + CIRCLE_R, ly + CIRCLE_R],
                fill=CIRCLE_FILL, outline=CIRCLE_OUTLINE, width=2,
            )
            num_str = str(part['num'])
            bbox = draw.textbbox((0, 0), num_str, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((lx - tw / 2 - bbox[0], ly - th / 2 - bbox[1]), num_str, fill=TEXT_COLOR, font=font)
        out = Image.alpha_composite(img, overlay).convert('RGB')
        out_name = fname.replace('.png', '-numerote.png')
        out.save(os.path.join(HERE, out_name))
        print("Ecrit ->", out_name)

    # Legende commune aux 4 vues (numerotation identique partout)
    legend_font = ImageFont.truetype(FONT_PATH, 22)
    line_h = 28
    legend_img = Image.new('RGB', (520, line_h * len(parts) + 20), 'white')
    d = ImageDraw.Draw(legend_img)
    for i, part in enumerate(parts):
        d.text((10, 10 + i * line_h), "%2d. %s" % (part['num'], part['label']), fill=(30, 30, 30), font=legend_font)
    legend_path = os.path.join(HERE, 'assemblage-articulation-eclate-legende.png')
    legend_img.save(legend_path)
    print("Ecrit -> assemblage-articulation-eclate-legende.png")


if __name__ == '__main__':
    main()
