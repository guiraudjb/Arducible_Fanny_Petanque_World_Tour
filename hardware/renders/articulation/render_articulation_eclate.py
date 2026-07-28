"""
Vue eclatee (exploded view) de hardware/cad/assemblage-articulation.FCStd.

Lecture seule -- n'appelle jamais doc.save(), sans danger a relancer.
Utilise le meme filtre "objets reels visibles" que
render_assemblage_articulation.py (Shape non nulle, diag > 0.5, visible via
gdoc) pour ignorer automatiquement les objets d'aide A2plus
(centerOfMass_*, axisCoincident_*, planeCoincident_*, pointOnPlane_*,
planesParallel_*) et les variantes masquees (RotuleGE8_001, tamponressort_001
-- remplacees par leurs versions "reelles" ChapeExterieureReelle /
BilleAxeReelle / TamponRessortDeformableReel, voir hardware/BOM.md).

Strategie d'eclatement (3 groupes identifies par la position X/Y du centre
de bounding box, voir l'inspection prealable de l'assemblage) :

  - "axe" (|x|<8, |y|<8) : la pile centrale le long de l'axe M8 vertical
    (aimant -> interface -> rondelle -> tampon -> rondelle DIN7349 -> plaque
    INF -> rotule (chape+bille, un seul bloc rigide) -> plaque milieu ->
    plaque sup -> rondelle DIN7349 -> ecrou M8 -> boule). Ecartee le long de
    Z, en conservant l'ordre reel, centree sur la position moyenne du
    groupe. La vis CHC M8x70 (la tige centrale) reste immobile : c'est
    l'axe visuel autour duquel les autres pieces se separent (comme un
    arbre de transmission fixe dans une vue eclatee de boite de vitesses).
  - "coin" (|x| et |y| ~14mm, les 4 vis+ecrou M4x30 qui traversent la pile
    de plaques aux 4 coins) : 4 chaines identiques, chacune ecartee le long
    de Z de la meme facon que le groupe "axe" (memes vis sont paralleles a
    l'axe principal).
  - "pcb" (x <~ -25mm : entretoise H31, PCB detection, 2 vis M4x50, leurs
    ecrous) : sous-ensemble lateral (le capteur a effet Hall n'est pas sur
    l'axe M8). Ecarte UNIQUEMENT le long de Z (jamais lateralement en X) --
    l'entretoise doit rester alignee sous son point de fixation reel sur la
    plaque inferieure, sinon la vue eclatee donne l'illusion trompeuse
    qu'elle etait montee ailleurs.

Corrections apportees suite a la relecture utilisateur du premier rendu :
  - L'aimant et l'interface-axe-aimant etaient dans le mauvais ordre : leurs
    centres de bounding box (utilises pour le tri) sont trompeurs car
    l'interface est une piece longue qui depasse l'aimant vers le bas.
    Physiquement, l'aimant est logiquement situe ENTRE l'axe (la vis, qui
    reste fixe) et l'interface (qui l'entoure/le depasse) -- voir
    RANK_OVERRIDE ci-dessous, qui force cet ordre independamment du tri par
    Z brut.
  - La rotule GE8C (chape) et sa bille sont considerees comme UNE SEULE
    piece rigide : aucun espacement n'est introduit entre elles (leurs
    centres coincident deja dans le fichier d'origine -- la bille est a
    l'interieur de la chape), seul l'ensemble {chape+bille} se separe de
    ses voisins (plaque INF en dessous, plaque milieu au-dessus).
  - Plus de decalage lateral (PCB_LATERAL supprime) pour le sous-ensemble
    PCB : il s'eclate seulement le long de Z, en gardant son alignement X/Y
    d'origine avec son point de fixation sur la plaque inferieure.

Rendu sous plusieurs angles (isometrique, face, droite, dessous) -- voir
STATIC_VIEWS en bas de fichier.
"""
import FreeCAD, FreeCADGui
import os
import json
from pivy import coin

ASM_PATH = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/cad/assemblage-articulation.FCStd'
OUT_DIR = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/renders/articulation/'
os.makedirs(OUT_DIR, exist_ok=True)

STEP_AXE = 22.0      # mm entre deux pieces consecutives du groupe "axe"
STEP_COIN = 22.0      # mm entre deux pieces consecutives du groupe "coin" (vis+ecrou)
STEP_PCB = 16.0      # mm entre deux pieces consecutives du groupe "pcb" (interne)

# Priorite de depart (tie-break) pour les objets partageant le meme Z, dans
# l'ordre physique reel (la chape+bille -- un seul bloc rigide -- est logee
# dans la plaque milieu) :
Z_TIE_BREAK = {
    'ChapeExterieureReelle': 0,
    'BilleAxeReelle': 0,   # meme rang que la chape : jamais separees l'une de l'autre
    'plaquearticulationMilieu_001': 1,
}

# Correction manuelle de l'ordre pour les 2 pieces dont le centre de
# bounding box ne reflete pas la position physique reelle (voir
# docstring) : plus la valeur est petite, plus la piece est eclatee loin
# du centre. L'aimant doit rester ENTRE l'axe (immobile) et l'interface.
RANK_OVERRIDE = {
    'interfaceAxeAimant4mm_001': -34.0,  # la plus eloignee (l'interface entoure/depasse l'aimant)
    'aimant4x2_001': -31.0,              # entre l'interface et le reste de la pile
}

# La vis centrale : reste immobile, sert de "colonne vertebrale" visuelle.
SPINE_LABEL_SUBSTR = 'CHC BTR'

# ATTENTION : ChapeExterieureReelle/BilleAxeReelle (les remplacements
# "reels" de la rotule GE8, ajoutes hors A2plus -- voir hardware/BOM.md)
# sont de simples Part::Feature dont le .Name interne (stable) ne
# correspond PAS a leur .Label (une description libre en francais). Tous
# les autres objets de cet assemblage (A2plus) ont un Label "propre" qui
# sert de cle partout ci-dessus -- on utilise donc le Name uniquement pour
# ces deux-la, le Label pour tout le reste.
_NAME_AS_KEY = {'ChapeExterieureReelle', 'BilleAxeReelle'}


def ident(obj):
    return obj.Name if obj.Name in _NAME_AS_KEY else obj.Label


def classify(obj, cx, cy):
    if abs(cx) < 8 and abs(cy) < 8:
        return 'axe'
    if 8 <= abs(cx) <= 20 and 8 <= abs(cy) <= 20:
        return 'coin'
    return 'pcb'


doc = FreeCAD.openDocument(ASM_PATH)
gdoc = FreeCADGui.getDocument(doc.Name)
view = gdoc.mdiViewsOfType("Gui::View3DInventor")[0]

real_objs = []
orig_center = {}   # obj.Name -> (cx,cy,cz) d'origine, pour les overrides manuels plus bas
for obj in doc.Objects:
    if not hasattr(obj, 'Shape') or obj.Shape.isNull():
        continue
    if obj.Shape.BoundBox.DiagonalLength < 0.5:
        continue
    vobj = gdoc.getObject(obj.Name)
    if not vobj or not vobj.Visibility:
        continue
    real_objs.append(obj)
    c = obj.Shape.BoundBox.Center
    orig_center[obj.Name] = (c.x, c.y, c.z)

print("Objets reels visibles retenus :", len(real_objs))

spine = None
groups = {'axe': [], 'coin_pp': [], 'coin_pm': [], 'coin_mp': [], 'coin_mm': [], 'pcb': []}

for obj in real_objs:
    bbox = obj.Shape.BoundBox
    cx, cy, cz = bbox.Center.x, bbox.Center.y, bbox.Center.z
    if SPINE_LABEL_SUBSTR in obj.Label:
        spine = obj
        continue
    grp = classify(obj, cx, cy)
    if grp == 'coin':
        key = 'coin_' + ('p' if cx > 0 else 'm') + ('p' if cy > 0 else 'm')
    else:
        key = grp
    groups[key].append((obj, cx, cy, cz))

# --- Groupe "axe" : ecartement le long de Z, ordre reel preserve ---
# Espacement variable : le bloc rotule (chape+bille, considere comme une
# seule piece rigide -- jamais separees l'une de l'autre) et la plaque
# milieu qui le loge sont la partie la plus documentee du projet (cf.
# memoire project_ge8_articulation_mechanics /
# project_rotule_ge8_wobble_animation) -- ils meritent plus d'air autour
# d'eux qu'un espacement uniforme.
CHAPE_BILLE = {'ChapeExterieureReelle', 'BilleAxeReelle'}
ROTULE_LABELS = CHAPE_BILLE | {'plaquearticulationMilieu_001'}


# L'ecrou M8 (entre la rondelle epaisse superieure et la boule) est une
# petite piece facilement invisible/confondue avec ses voisins a
# l'espacement uniforme -- ecart supplementaire de part et d'autre,
# signale manquant par l'utilisateur sur le rendu precedent.
NUT_LABEL = 'EcrouM8_001'


def gap_after(label_a, label_b):
    if label_a in CHAPE_BILLE and label_b in CHAPE_BILLE:
        return 0.0               # chape+bille : un seul bloc rigide, jamais separees
    a_in, b_in = label_a in ROTULE_LABELS, label_b in ROTULE_LABELS
    if a_in and b_in:
        return STEP_AXE * 1.3   # entre le bloc rotule et la plaque milieu
    if a_in != b_in:
        return STEP_AXE * 1.8   # juste avant/apres tout le groupe rotule+milieu
    if label_a == NUT_LABEL or label_b == NUT_LABEL:
        return STEP_AXE * 1.6   # ecrou M8 bien degage de la rondelle et de la boule
    return STEP_AXE


axe_list = groups['axe']
# Le tri utilise RANK_OVERRIDE pour les pieces dont le centre de bounding
# box induit en erreur (l'aimant doit rester entre l'axe et l'interface,
# voir docstring) ; Z_TIE_BREAK depallage les pieces a Z egal (chape+bille).
axe_list.sort(key=lambda t: (round(RANK_OVERRIDE.get(ident(t[0]), t[3]), 1), Z_TIE_BREAK.get(ident(t[0]), 99)))
n = len(axe_list)
mean_z = sum(t[3] for t in axe_list) / n
positions = [0.0]
for i in range(n - 1):
    positions.append(positions[-1] + gap_after(ident(axe_list[i][0]), ident(axe_list[i + 1][0])))
pos_mean = sum(positions) / n
offsets = {}
friendly = {}   # obj.Name -> nom court en francais, pour la legende numerotee
AXE_FRIENDLY = {
    'interfaceAxeAimant4mm_001': 'Interface axe-aimant',
    'aimant4x2_001': 'Aimant neodyme',
    'rondelle8x22x1,5_001': 'Rondelle 8x22x1,5',
    'Tampon ressort CR60 deformable': 'Tampon ressort CR60',
    'DIN 7349 M8_001': 'Rondelle epaisse M8 (bas)',
    'plaquearticulationINF_001': 'Plaque inferieure',
    'plaquearticulationMilieu_001': 'Plaque milieu',
    'plaquearticulationsup_001': 'Plaque superieure',
    'DIN 7349 M8_002': 'Rondelle epaisse M8 (haut)',
    'EcrouM8_001': 'Ecrou M8',
    'boulepleineV2_001': 'Boule de petanque',
}
axe_target_z = {}   # ident(obj) -> target_z, pour ancrer les groupes coin/pcb dessus
with open('/tmp/eclate_debug.txt', 'w') as dbg:
    for (obj, cx, cy, cz), pos in zip(axe_list, positions):
        target_z = mean_z + (pos - pos_mean)
        offsets[obj.Name] = FreeCAD.Vector(0, 0, target_z - cz)
        axe_target_z[ident(obj)] = target_z
        if ident(obj) in CHAPE_BILLE:
            friendly[obj.Name] = 'Rotule GE8 (chape+bille)'
        else:
            friendly[obj.Name] = AXE_FRIENDLY.get(ident(obj), ident(obj))
        dbg.write("%-35s orig_z=%8.2f target_z=%8.2f\n" % (ident(obj), cz, target_z))
        dbg.flush()

# --- Groupes "coin" (4 chaines vis+ecrou M4x30) : les 4 vis d'assemblage
# des 3 plaques doivent ressortir AU-DESSUS de la plaque superieure (comme
# si on les devissait par le dessus), pas flotter au milieu de la pile --
# ancrees sur le target_z reel (deja eclate) de la plaque sup, pas sur leur
# propre moyenne locale.
COIN_GAP_ABOVE_SUP = 25.0   # mm de degagement entre la plaque sup et l'ecrou du premier coin
sup_target_z = axe_target_z['plaquearticulationsup_001']
for coin_idx, key in enumerate(('coin_pp', 'coin_pm', 'coin_mp', 'coin_mm'), start=1):
    lst = groups[key]
    if not lst:
        continue
    lst.sort(key=lambda t: t[3])   # ecrou (z le plus bas) d'abord, vis (tete) ensuite
    n = len(lst)
    base_z = sup_target_z + COIN_GAP_ABOVE_SUP
    for rank, (obj, cx, cy, cz) in enumerate(lst):
        target_z = base_z + rank * STEP_COIN
        offsets[obj.Name] = FreeCAD.Vector(0, 0, target_z - cz)
        piece = 'Ecrou M4' if rank == 0 else 'Vis M4x30'
        friendly[obj.Name] = '%s (coin %d)' % (piece, coin_idx)

# --- Groupe "pcb" : ecartement interne le long de Z SEULEMENT -- aucun
# decalage lateral, pour rester aligne avec son point de fixation reel sur
# la plaque inferieure (voir docstring, defaut signale par l'utilisateur).
# Ancre sous le target_z reel (deja eclate) de la plaque INF et non sur sa
# propre moyenne locale, pour rester nettement detachee de la plaque (plus
# "basse", comme demande).
PCB_GAP_BELOW_INF = 35.0   # mm de degagement entre la plaque INF et le sous-ensemble PCB
inf_target_z = axe_target_z['plaquearticulationINF_001']
pcb_list = groups['pcb']
pcb_list.sort(key=lambda t: t[3])   # le plus eloigne de la plaque (rang 0) au plus proche (dernier rang)
n = len(pcb_list)
closest_z = inf_target_z - PCB_GAP_BELOW_INF
PCB_FRIENDLY_PREFIX = {
    'entretoisesV5H31_001': 'Entretoise carte electronique',
    'detection-pcb-v3_001': 'PCB detection',
}
vis_m4x50_count = 0
ecrou_m4_count = 0
ecrou_frein_count = 0
for rank, (obj, cx, cy, cz) in enumerate(pcb_list):
    target_z = closest_z - (n - 1 - rank) * STEP_PCB
    offsets[obj.Name] = FreeCAD.Vector(0, 0, target_z - cz)
    lbl = ident(obj)
    if lbl in PCB_FRIENDLY_PREFIX:
        friendly[obj.Name] = PCB_FRIENDLY_PREFIX[lbl]
    elif 'M4X50' in lbl.upper():
        vis_m4x50_count += 1
        friendly[obj.Name] = 'Vis M4x50 (PCB %d)' % vis_m4x50_count
    elif lbl.startswith('EcrouM4'):
        ecrou_m4_count += 1
        friendly[obj.Name] = 'Ecrou M4 (PCB, haut %d)' % ecrou_m4_count
    elif lbl.startswith('ecrou-frein-m4') or lbl.startswith('ecrou_frein_m4'):
        ecrou_frein_count += 1
        friendly[obj.Name] = 'Ecrou frein M4 (PCB, bas %d)' % ecrou_frein_count
    else:
        friendly[obj.Name] = lbl

if spine is not None:
    offsets[spine.Name] = FreeCAD.Vector(0, 0, 0)
    friendly[spine.Name] = 'Vis CHC M8x70 (axe central)'

print("Groupes : axe=%d coin(pp/pm/mp/mm)=%d/%d/%d/%d pcb=%d spine=%s" % (
    len(axe_list), len(groups['coin_pp']), len(groups['coin_pm']),
    len(groups['coin_mp']), len(groups['coin_mm']), len(pcb_list),
    spine.Label if spine else 'NON TROUVEE'))

# --- Overrides manuels : positions Z relevees sur
# assemblage-articulation-eclate-manuel.FCStd (copie ouverte par
# l'utilisateur dans FreeCAD, pieces deplacees a la souris puis
# sauvegardees). Remplacent le resultat de l'algorithme ci-dessus pour ces
# 5 pieces precises -- tout le reste garde le calcul automatique. Le plus
# notable : la vis centrale ne reste plus immobile ("colonne vertebrale"),
# l'utilisateur l'a explicitement tiree vers le bas comme les autres pieces.
MANUAL_TARGET_Z = {
    'Vis métaux CHC BTR Clé de 6 HC6 M8X70 Filetée sur 22 Classe 12.9 Acier brut_001': -74.5,
    'plaquearticulationINF_001': -9.3,
    'EcrouM8_001': 111.7,
    'entretoisesV5H31_001': -118.3,
    'interfaceAxeAimant4mm_001': -129.3,
}
for obj in real_objs:
    key = ident(obj)
    if key in MANUAL_TARGET_Z:
        cx, cy, cz = orig_center[obj.Name]
        offsets[obj.Name] = FreeCAD.Vector(0, 0, MANUAL_TARGET_Z[key] - cz)

for obj in real_objs:
    delta = offsets.get(obj.Name, FreeCAD.Vector(0, 0, 0))
    base = FreeCAD.Placement(obj.Placement)
    obj.Placement = FreeCAD.Placement(base.Base + delta, base.Rotation)

doc.recompute()

# --- Numerotation des pieces pour la legende. Les etiquettes sont ajoutees
# en post-traitement PIL (voir label_eclate_views.py) plutot qu'en texte 3D
# dans la scene FreeCAD -- un texte 3D ne resterait lisible que sous UN
# angle de camera, alors qu'un overlay 2D calcule par vue reste net sous
# les 4 angles. Deux pieces a la position EXACTEMENT identique (chape+bille
# de la rotule, jamais separees -- voir plus haut) partagent un seul numero.
IMG_W, IMG_H = 1800, 1500
parts_by_pos = {}
for obj in real_objs:
    c = obj.Shape.BoundBox.Center
    key_pos = (round(c.x, 1), round(c.y, 1), round(c.z, 1))
    if key_pos not in parts_by_pos:
        parts_by_pos[key_pos] = friendly.get(obj.Name, ident(obj))

numbered = []
for i, (pos, label) in enumerate(sorted(parts_by_pos.items(), key=lambda kv: -kv[0][2]), start=1):
    numbered.append({'num': i, 'label': label, 'x': pos[0], 'y': pos[1], 'z': pos[2]})
    print("#%2d %-35s (%.1f, %.1f, %.1f)" % (i, label, pos[0], pos[1], pos[2]))

# --- Plusieurs angles de vue, meme convention de nommage que les rendus
# assembles existants (assemblage-articulation-{face,droite,dessous}.png).
# Calibration camera capturee juste avant chaque saveImage (position +
# base orthonormee right/up dans le repere monde, via SbRotation.multVec)
# pour permettre a label_eclate_views.py de projeter chaque piece en 2D
# sans avoir a redeviner l'API de projection de FreeCAD : pour une camera
# orthographique centree par ViewFit, le pixel central correspond toujours
# a l'axe de visee (proj_u=proj_v=0 par construction), et l'echelle
# pixels/mm vaut IMG_H / cam.height (cam.height = hauteur du monde en mm
# couverte par la hauteur de l'image).
STATIC_VIEWS = [
    ('assemblage-articulation-eclate-iso.png', view.viewIsometric),
    ('assemblage-articulation-eclate-face.png', view.viewFront),
    ('assemblage-articulation-eclate-droite.png', view.viewRight),
    ('assemblage-articulation-eclate-dessous.png', view.viewBottom),
]
camera_calib = {}
for fname, view_func in STATIC_VIEWS:
    view_func()
    FreeCADGui.SendMsgToActiveView("ViewFit")
    cam = view.getCameraNode()
    cam.height.setValue(cam.height.getValue() * 1.15)
    view.saveImage(OUT_DIR + fname, IMG_W, IMG_H, 'White')
    print("Rendu ->", fname)
    campos = cam.position.getValue().getValue()
    right = cam.orientation.getValue().multVec(coin.SbVec3f(1, 0, 0)).getValue()
    up = cam.orientation.getValue().multVec(coin.SbVec3f(0, 1, 0)).getValue()
    camera_calib[fname] = {
        'campos': list(campos), 'right': list(right), 'up': list(up),
        'height': cam.height.getValue(), 'img_w': IMG_W, 'img_h': IMG_H,
    }

with open(OUT_DIR + 'eclate_labels.json', 'w') as f:
    json.dump({'parts': numbered, 'views': camera_calib}, f, indent=2)
print("Export -> eclate_labels.json")

FreeCADGui.getMainWindow().close()
