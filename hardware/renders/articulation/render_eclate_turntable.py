"""
Turntable (camera fixe, la piece tourne) de
hardware/cad/assemblage-articulation-eclate-manuel.FCStd -- la copie deja
en position eclatee (calculee + ajustee a la main, voir
render_articulation_eclate.py et prep_manuel_copy.py).

Lecture seule -- n'appelle jamais doc.save(). Reprend le meme principe que
le turntable de render_assemblage_articulation.py (rotation rigide de
toutes les pieces visibles autour de l'axe Z passant par l'origine, camera
fixe en vue isometrique) : chaque frame recalcule la rotation depuis le
Placement d'ORIGINE (jamais de rotation incrementale composee d'une frame
sur l'autre, pour eviter toute derive numerique).

Contrairement au turntable de l'assemblage assemble (camera viewRight,
profil), celui-ci utilise une camera isometrique fixe : une vue de profil
montrerait les plaques par la tranche (lignes fines), peu lisible pour une
vue eclatee dont l'interet est justement de voir l'empilement en
profondeur. Le fit de camera est aussi tres elargi (x1.6) car la pile
eclatee mesure ~340mm de haut (bien plus que l'assemblage ferme) et n'est
pas symetrique en rotation (sous-ensemble PCB decale en X).

Assembler les frames en GIF avec ffmpeg (palette optimisee en 2 passes,
sinon teinte jaune visible sur les rendus CAO gris clair/blancs) :

    ffmpeg -y -framerate 12 -i eclate_turntable_frames/frame_%03d.png \
      -vf "fps=12,scale=900:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=200[p];[b][p]paletteuse=dither=bayer" \
      -loop 0 assemblage-articulation-eclate-turntable.gif
"""
import FreeCAD, FreeCADGui
import os

ASM_PATH = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/cad/assemblage-articulation-eclate-manuel.FCStd'
OUT_DIR = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/renders/articulation/'
FRAMES_DIR = OUT_DIR + 'eclate_turntable_frames/'
os.makedirs(FRAMES_DIR, exist_ok=True)

N_FRAMES = 36   # pas de 10 degres, meme convention que le turntable existant


def rotate_about(placement, pivot, rot):
    delta = FreeCAD.Placement(pivot, rot).multiply(FreeCAD.Placement(-pivot, FreeCAD.Rotation()))
    return delta.multiply(placement)


doc = FreeCAD.openDocument(ASM_PATH)
gdoc = FreeCADGui.getDocument(doc.Name)
view = gdoc.mdiViewsOfType("Gui::View3DInventor")[0]

turntable_objs = []
base_placements = {}
for obj in doc.Objects:
    if not hasattr(obj, 'Shape') or obj.Shape.isNull():
        continue
    if obj.Shape.BoundBox.DiagonalLength < 0.5:
        continue
    vobj = gdoc.getObject(obj.Name)
    if not vobj or not vobj.Visibility:
        continue
    turntable_objs.append(obj)
    base_placements[obj.Name] = FreeCAD.Placement(obj.Placement)

print("Turntable eclate : rotation de", len(turntable_objs), "objets visibles")

PIVOT = FreeCAD.Vector(0, 0, 0)

view.viewIsometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
cam = view.getCameraNode()
cam.height.setValue(cam.height.getValue() * 1.6)

for i in range(N_FRAMES):
    angle = i * (360.0 / N_FRAMES)
    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle)
    for obj in turntable_objs:
        obj.Placement = rotate_about(base_placements[obj.Name], PIVOT, rot)
    doc.recompute()
    fname = FRAMES_DIR + 'frame_%03d.png' % i
    view.saveImage(fname, 900, 900, 'White')

print("Frames ecrites ->", FRAMES_DIR)

# IMPORTANT : remettre chaque objet a son Placement d'origine avant de
# fermer. Constate a l'usage (2026-07-29) : fermer la fenetre principale
# via FreeCADGui.getMainWindow().close() sur un document modifie (par les
# rotations ci-dessus) declenche une sauvegarde SILENCIEUSE du fichier
# reel sur disque, malgre l'intention "lecture seule" -- ca a ecrase une
# fois la calibration manuelle de l'utilisateur avec la derniere frame de
# rotation (350 deg). Restaurer les Placements originaux ici fait que,
# meme si ce comportement se reproduit, ce qui serait sauvegarde est
# l'etat correct et non une frame de rotation intermediaire.
for obj in turntable_objs:
    obj.Placement = base_placements[obj.Name]
doc.recompute()

FreeCADGui.getMainWindow().close()
