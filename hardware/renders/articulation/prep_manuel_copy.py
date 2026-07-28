"""
Prepare hardware/cad/assemblage-articulation-eclate-manuel.FCStd : une
COPIE de assemblage-articulation.FCStd (jamais le fichier source lui-meme,
voir le garde-fou de render_articulation_eclate.py) sur laquelle on
applique la meme position eclatee que celle des rendus actuels, PUIS on
sauvegarde -- pour que l'utilisateur puisse l'ouvrir dans FreeCAD et
deplacer les pieces a la main a partir d'un point de depart deja proche,
plutot que de tout repositionner depuis la position assemblee.

Reprend telle quelle la logique de calcul des positions de
render_articulation_eclate.py (memes constantes STEP_*/RANK_OVERRIDE/gap_*
-- si ce fichier est retouche, reappliquer les memes changements ici, ou
mieux : factoriser un module commun si ce script sert plus d'une fois).
Seule difference : cible le fichier copie et appelle doc.save() a la fin
(le script de rendu, lui, reste volontairement lecture-seule).

A savoir avant d'ouvrir la copie dans FreeCAD :
  - Deplacer une piece a la souris (poignee de positionnement / Placement)
    doit fonctionner normalement et rester en l'etat apres sauvegarde --
    confirme indirectement par ce script lui-meme, qui modifie les
    Placement par script puis sauvegarde sans que l'assemblage A2plus ne
    les recalcule/annule.
  - En revanche, si un outil A2plus explicite de "resolution" des
    contraintes est lance depuis le menu (pas juste un recompute normal),
    il pourrait re-contraindre les pieces a leur position d'origine -- ne
    pas lancer cette commande sur cette copie.
  - Sauvegarder normalement (Ctrl+S) une fois les positions ajustees.

Ensuite, relancer un script d'inspection (voir inspect_manuel_copy.py) sur
cette copie pour recuperer les positions finales choisies a la main.

Run headlessly (voir ~/.claude/skills/freecad-headless) avec le binaire
GUI complet (necessaire pour sauvegarder un fichier A2plus sans perdre
GuiDocument.xml -- jamais via freecadcmd) :

    xvfb-run -a --server-args="-screen 0 1920x1080x24" \
      /path/to/freecad/bin/freecad prep_manuel_copy.py
"""
import FreeCAD, FreeCADGui

ASM_PATH = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/cad/assemblage-articulation-eclate-manuel.FCStd'

STEP_AXE = 22.0
STEP_COIN = 22.0
STEP_PCB = 16.0

Z_TIE_BREAK = {
    'ChapeExterieureReelle': 0,
    'BilleAxeReelle': 0,
    'plaquearticulationMilieu_001': 1,
}

RANK_OVERRIDE = {
    'interfaceAxeAimant4mm_001': -34.0,
    'aimant4x2_001': -31.0,
}

SPINE_LABEL_SUBSTR = 'CHC BTR'

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

real_objs = []
for obj in doc.Objects:
    if not hasattr(obj, 'Shape') or obj.Shape.isNull():
        continue
    if obj.Shape.BoundBox.DiagonalLength < 0.5:
        continue
    vobj = gdoc.getObject(obj.Name)
    if not vobj or not vobj.Visibility:
        continue
    real_objs.append(obj)

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

CHAPE_BILLE = {'ChapeExterieureReelle', 'BilleAxeReelle'}
ROTULE_LABELS = CHAPE_BILLE | {'plaquearticulationMilieu_001'}
NUT_LABEL = 'EcrouM8_001'


def gap_after(label_a, label_b):
    if label_a in CHAPE_BILLE and label_b in CHAPE_BILLE:
        return 0.0
    a_in, b_in = label_a in ROTULE_LABELS, label_b in ROTULE_LABELS
    if a_in and b_in:
        return STEP_AXE * 1.3
    if a_in != b_in:
        return STEP_AXE * 1.8
    if label_a == NUT_LABEL or label_b == NUT_LABEL:
        return STEP_AXE * 1.6
    return STEP_AXE


axe_list = groups['axe']
axe_list.sort(key=lambda t: (round(RANK_OVERRIDE.get(ident(t[0]), t[3]), 1), Z_TIE_BREAK.get(ident(t[0]), 99)))
n = len(axe_list)
mean_z = sum(t[3] for t in axe_list) / n
positions = [0.0]
for i in range(n - 1):
    positions.append(positions[-1] + gap_after(ident(axe_list[i][0]), ident(axe_list[i + 1][0])))
pos_mean = sum(positions) / n
offsets = {}
axe_target_z = {}
for (obj, cx, cy, cz), pos in zip(axe_list, positions):
    target_z = mean_z + (pos - pos_mean)
    offsets[obj.Name] = FreeCAD.Vector(0, 0, target_z - cz)
    axe_target_z[ident(obj)] = target_z

COIN_GAP_ABOVE_SUP = 25.0
sup_target_z = axe_target_z['plaquearticulationsup_001']
for key in ('coin_pp', 'coin_pm', 'coin_mp', 'coin_mm'):
    lst = groups[key]
    if not lst:
        continue
    lst.sort(key=lambda t: t[3])
    n = len(lst)
    base_z = sup_target_z + COIN_GAP_ABOVE_SUP
    for rank, (obj, cx, cy, cz) in enumerate(lst):
        target_z = base_z + rank * STEP_COIN
        offsets[obj.Name] = FreeCAD.Vector(0, 0, target_z - cz)

PCB_GAP_BELOW_INF = 35.0
inf_target_z = axe_target_z['plaquearticulationINF_001']
pcb_list = groups['pcb']
pcb_list.sort(key=lambda t: t[3])
n = len(pcb_list)
closest_z = inf_target_z - PCB_GAP_BELOW_INF
for rank, (obj, cx, cy, cz) in enumerate(pcb_list):
    target_z = closest_z - (n - 1 - rank) * STEP_PCB
    offsets[obj.Name] = FreeCAD.Vector(0, 0, target_z - cz)

if spine is not None:
    offsets[spine.Name] = FreeCAD.Vector(0, 0, 0)

for obj in real_objs:
    delta = offsets.get(obj.Name, FreeCAD.Vector(0, 0, 0))
    base = FreeCAD.Placement(obj.Placement)
    obj.Placement = FreeCAD.Placement(base.Base + delta, base.Rotation)

doc.recompute()
doc.save()
print("Sauvegarde ->", ASM_PATH)

FreeCADGui.getMainWindow().close()
