"""
Regenerates the official renders of hardware/cad/assemblage-articulation.FCStd
used on index.html (Partie 3 -- La cible et son articulation):

    assemblage-articulation-face.png      (viewFront,  1800x1350)
    assemblage-articulation-droite.png    (viewRight,  1800x1350)
    assemblage-articulation-dessous.png   (viewBottom, 1800x1350)
    assemblage-articulation-turntable.gif (isometric, 36 frames / 10deg, 640x480, 10fps)

Run headlessly via the freecad-headless skill (~/.claude/skills/freecad-headless):

    xvfb-run -a --server-args="-screen 0 1920x1080x24" \
      /path/to/freecad_extracted/squashfs-root/usr/bin/freecad \
      render_assemblage_articulation.py

Requires the FULL GUI freecad binary (not freecadcmd) for saveImage(). This
script only READS assemblage-articulation.FCStd -- it never calls doc.save(),
so it's safe to re-run any time the assembly's rest-state geometry changes;
the turntable frames temporarily rotate every object's Placement in memory
only, never persisted back to the file.

The turntable is built by rotating every visible part's Placement about the
vertical (Z) axis through the origin, camera held fixed at isometric --
*not* by moving the Coin3D camera around the object. This reuses the same
rotate_about() rigid-transform helper validated across the GE8 articulation
animation work (see hardware/cad/rotule-ge8-articulee.FCStd and the project
memory on that work) instead of hand-rolling camera look-at math.

After running, assemble the turntable GIF with ffmpeg, e.g.:

    ffmpeg -y -framerate 10 -i turntable_frames/frame_%03d.png \
      -vf "fps=10,scale=640:480:force_original_aspect_ratio=decrease,pad=640:480:-1:-1:color=white" \
      -loop 0 assemblage-articulation-turntable.gif
"""
import FreeCAD, FreeCADGui
import math, os

ASM_PATH = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/cad/assemblage-articulation.FCStd'
OUT_DIR = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/renders/articulation/'
TURNTABLE_FRAMES_DIR = OUT_DIR + 'turntable_frames/'
os.makedirs(TURNTABLE_FRAMES_DIR, exist_ok=True)

N_TURNTABLE_FRAMES = 36  # matches the existing 10deg-step / 36-frame turntables in this project


def rotate_about(placement, pivot, rot):
    delta = FreeCAD.Placement(pivot, rot).multiply(FreeCAD.Placement(-pivot, FreeCAD.Rotation()))
    return delta.multiply(placement)


doc = FreeCAD.openDocument(ASM_PATH)
gdoc = FreeCADGui.getDocument(doc.Name)
view = gdoc.mdiViewsOfType("Gui::View3DInventor")[0]

# --- Static views (matches the framing already used on index.html) ---
static_views = [
    ('assemblage-articulation-face.png', view.viewFront),
    ('assemblage-articulation-droite.png', view.viewRight),
    ('assemblage-articulation-dessous.png', view.viewBottom),
]
for fname, view_func in static_views:
    view_func()
    FreeCADGui.SendMsgToActiveView("ViewFit")
    view.saveImage(OUT_DIR + fname, 1800, 1350, 'White')
    print("Rendered", fname)

# --- Turntable: rotate every real part about Z through the origin, camera fixed ---
PIVOT = FreeCAD.Vector(0, 0, 0)

# Skip A2plus's auxiliary constraint/centerOfMass proxy objects (zero-size
# markers, not meant to be visually rotated) -- keep only objects with a
# real Shape of non-trivial size.
turntable_objs = []
base_placements = {}
for obj in doc.Objects:
    if not hasattr(obj, 'Shape') or obj.Shape.isNull():
        continue
    if obj.Shape.BoundBox.DiagonalLength < 0.5:
        continue
    if not gdoc.getObject(obj.Name).Visibility:
        continue
    turntable_objs.append(obj)
    base_placements[obj.Name] = FreeCAD.Placement(obj.Placement)

print("Turntable: rotating", len(turntable_objs), "visible objects")

view.viewIsometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
# The assembly isn't rotationally symmetric (140mm-long plates), so a fit at
# one azimuth can clip at another -- pad the fit with extra margin.
cam = view.getCameraNode()
cam.height.setValue(cam.height.getValue() * 1.4)

for i in range(N_TURNTABLE_FRAMES):
    angle = 360.0 * i / N_TURNTABLE_FRAMES
    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle)
    for obj in turntable_objs:
        obj.Placement = rotate_about(base_placements[obj.Name], PIVOT, rot)
    doc.recompute()
    view.saveImage(TURNTABLE_FRAMES_DIR + 'frame_%03d.png' % i, 640, 480, 'White')

print("DONE:", N_TURNTABLE_FRAMES, "turntable frames in", TURNTABLE_FRAMES_DIR)
print("Assemble with ffmpeg (see docstring) -- this script never saves the document.")
FreeCADGui.getMainWindow().close()
