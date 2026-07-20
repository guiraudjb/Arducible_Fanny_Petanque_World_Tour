"""
Renders the target articulation actually moving -- a single strike-then-
damped-return cycle -- for use as a hero animation on index.html, as
opposed to render_assemblage_articulation.py's turntable (camera orbits a
static object; this one keeps the camera fixed and moves the mechanism).

Physics/kinematics validated with the user across the 2026-07-20 session
(see the project memory "GE8 articulation mechanics" and "Rotule GE8
wobble animation" for the full history):

  - The ball+axle tilt as one rigid group about the real pivot, via a
    single direct axis-angle Rotation per frame (never composed from two
    separate Rotations -- that's what caused an earlier attempt's self-spin).
  - The shaft also floats axially (rises) through the ball's bore as the
    tampon compresses.
  - The two DIN7349 washers stay flat (constrained only by the flat fixed
    plates) and only slide laterally to track the tilted shaft.
  - The tampon-ressort's bottom face is rigid with the tilting/rising shaft
    while its top face stays flat against the (sliding but flat) washer --
    so it compresses as a wedge, hard on one side, barely on the other,
    not as a uniform squeeze. Built as a real Part.makeLoft between the two
    faces, not an axisymmetric revolve.

Run headlessly (see ~/.claude/skills/freecad-headless):

    xvfb-run -a --server-args="-screen 0 1920x1080x24" \
      /path/to/freecad/bin/freecad render_articulation_mouvement.py

Requires the full GUI freecad binary (not freecadcmd) for saveImage().
Read-only against assemblage-articulation.FCStd -- never calls doc.save().

Assemble the frames into a GIF with ffmpeg, e.g.:

    ffmpeg -y -framerate 20 -i mouvement_frames/frame_%03d.png \
      -vf "fps=20,scale=900:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160[p];[b][p]paletteuse=dither=bayer" \
      -loop 0 assemblage-articulation-mouvement.gif
"""
import FreeCAD, FreeCADGui, Part
import math, os

ASM_PATH = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/cad/assemblage-articulation.FCStd'
OUT_DIR = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/renders/articulation/'
FRAMES_DIR = OUT_DIR + 'mouvement_frames/'
os.makedirs(FRAMES_DIR, exist_ok=True)

PIVOT = FreeCAD.Vector(0, 0, 2.5)          # real ball pivot center, measured on the solid
TILT_AXIS = FreeCAD.Vector(1, 0, 0)        # global X, validated to read well from isometric
PEAK_TILT = 10.0                            # deg -- illustrative placeholder, never measured
MAX_AXIAL_RISE = 1.5                        # mm -- illustrative placeholder, never measured
N_FRAMES = 40
PEAK_FRAME = 4
DECAY_TAU = 8.0

TAMPON_H0 = 15.0
TAMPON_ROUT0 = 10.0
TAMPON_RIN = 4.25


def tilt_profile(i):
    if i <= PEAK_FRAME:
        return PEAK_TILT * (i / float(PEAK_FRAME))
    return PEAK_TILT * math.exp(-(i - PEAK_FRAME) / DECAY_TAU)


def rotate_about(placement, pivot, rot):
    delta = FreeCAD.Placement(pivot, rot).multiply(FreeCAD.Placement(-pivot, FreeCAD.Rotation()))
    return delta.multiply(placement)


def build_tampon_wedge(bottom_placement, top_z, top_center_xy):
    bottom_center = bottom_placement.Base
    bottom_normal = bottom_placement.Rotation.multVec(FreeCAD.Vector(0, 0, 1))
    top_center = FreeCAD.Vector(top_center_xy.x, top_center_xy.y, top_z)
    top_normal = FreeCAD.Vector(0, 0, 1)

    outer_bottom = Part.Wire([Part.makeCircle(TAMPON_ROUT0, bottom_center, bottom_normal)])
    outer_top = Part.Wire([Part.makeCircle(TAMPON_ROUT0, top_center, top_normal)])
    outer_solid = Part.makeLoft([outer_bottom, outer_top], True, True)

    inner_bottom = Part.Wire([Part.makeCircle(TAMPON_RIN, bottom_center, bottom_normal)])
    inner_top = Part.Wire([Part.makeCircle(TAMPON_RIN, top_center, top_normal)])
    inner_solid = Part.makeLoft([inner_bottom, inner_top], True, True)

    return outer_solid.cut(inner_solid)


def washer_slide_xy(base_placement, pivot, rot):
    z0 = base_placement.Base.z
    d = rot.multVec(FreeCAD.Vector(0, 0, 1))
    if abs(d.z) < 1e-9:
        return FreeCAD.Vector(pivot.x, pivot.y, z0)
    t = (z0 - pivot.z) / d.z
    p = pivot + d * t
    return FreeCAD.Vector(p.x, p.y, z0)


doc = FreeCAD.openDocument(ASM_PATH)
gdoc = FreeCADGui.getDocument(doc.Name)

# These are the real objects already integrated into the assembly (2026-07-20) --
# no need to rebuild geometry, just animate the existing Placements/Shape.
bille = doc.getObject('BilleAxeReelle')
tampon = doc.getObject('TamponRessortDeformableReel')
base_bille_placement = FreeCAD.Placement(bille.Placement)
base_tampon_placement = FreeCAD.Placement(tampon.Placement)
tampon_top_z = base_tampon_placement.Base.z + TAMPON_H0

moving_names = [
    'b_Vis_m_xc3_xa9taux_CHC_BTR_Cl_xc3_xa9_de_6_HC6_M8X70_Filet_xc3_xa9e_sur_22_Classe_12_9_Acier_brut_001_',
    'b_rondelle8x22x1_5_001_',
    'b_EcrouM8_001_',
    'b_boulepleineV2_001_',
    'b_interfaceAxeAimant4mm_001_',
    'b_aimant4x2_001_',
]
moving_objs = [doc.getObject(n) for n in moving_names]
moving_base = {n: FreeCAD.Placement(o.Placement) for n, o in zip(moving_names, moving_objs)}

washer_names = ['b_DIN_7349_M8_001_', 'b_DIN_7349_M8_001_001']
washer_objs = [doc.getObject(n) for n in washer_names]
washer_base = {n: FreeCAD.Placement(o.Placement) for n, o in zip(washer_names, washer_objs)}

# See through the housing so the tampon's compression is actually visible.
housing = doc.getObject('b_interfaceAxeAimant4mm_001_')
if housing:
    gdoc.getObject(housing.Name).Transparency = 70

doc.recompute()

view = gdoc.mdiViewsOfType("Gui::View3DInventor")[0]
view.viewIsometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
cam = view.getCameraNode()
cam.height.setValue(cam.height.getValue() * 1.15)  # small safety margin for the tilt/rise

for i in range(N_FRAMES):
    tilt = tilt_profile(i)
    rot = FreeCAD.Rotation(TILT_AXIS, tilt)
    compression_ratio = tilt / PEAK_TILT
    rise = MAX_AXIAL_RISE * compression_ratio

    bp = rotate_about(base_bille_placement, PIVOT, rot)
    bp.Base.z += rise
    bille.Placement = bp

    for n, o in zip(moving_names, moving_objs):
        p = rotate_about(moving_base[n], PIVOT, rot)
        p.Base.z += rise
        o.Placement = p

    for n, o in zip(washer_names, washer_objs):
        o.Placement = FreeCAD.Placement(washer_slide_xy(washer_base[n], PIVOT, rot), FreeCAD.Rotation())

    tampon_bottom = rotate_about(base_tampon_placement, PIVOT, rot)
    tampon_bottom.Base.z += rise
    tampon_top_xy = washer_slide_xy(washer_base['b_DIN_7349_M8_001_'], PIVOT, rot)
    tampon.Shape = build_tampon_wedge(tampon_bottom, tampon_top_z, tampon_top_xy)

    doc.recompute()
    view.saveImage(FRAMES_DIR + 'frame_%03d.png' % i, 1200, 1080, 'White')

print("DONE", N_FRAMES, "frames in", FRAMES_DIR, "-- document never saved.")
FreeCADGui.getMainWindow().close()
