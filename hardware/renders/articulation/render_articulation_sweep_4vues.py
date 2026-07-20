"""
Renders the target articulation moving through 4 discrete cardinal strikes
(+X/+Y/-X/-Y) then a continuous 360deg azimuthal sweep, from 4 different
fixed cameras (isometric / top / front / right) -- one GIF per camera, for
the "4 vues" gallery on index.html next to the single-strike hero animation
(render_articulation_mouvement.py).

Same validated physics as the single-strike animation (see that script's
docstring and the project memory "Rotule GE8 wobble animation" /
"GE8 articulation mechanics" for the full history): real chape/bille tilt
via one direct axis-angle Rotation per frame, axial float, flat sliding
washers, wedge-compressing tampon built as a real Part.makeLoft.

The only new thing here vs. the single-strike animation is that the tilt
AXIS itself sweeps through azimuth (4 cardinal directions, then continuously
360deg) instead of staying fixed on X. Each frame still uses exactly ONE
direct `FreeCAD.Rotation(axis_vector(azimuth), tilt_deg)` -- never composed
from two separate Rotations, which is what caused the very first (rejected)
attempt's self-spin artifact.

Run headlessly (~/.claude/skills/freecad-headless):

    xvfb-run -a --server-args="-screen 0 1920x1080x24" \
      /path/to/freecad/bin/freecad render_articulation_sweep_4vues.py

Requires the full GUI freecad binary (not freecadcmd). Read-only against
assemblage-articulation.FCStd -- never calls doc.save().

Assemble each view's frames into a GIF with ffmpeg (palettegen/paletteuse
two-pass -- a plain scale+pad was tried first for the turntable GIF and
gave a visible yellow tint on the light grey/white renders, confirmed by
the user on the live site):

    for view in iso top front right; do
      ffmpeg -y -framerate 20 -i sweep4_frames_$view/frame_%03d.png \
        -vf "fps=20,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160[p];[b][p]paletteuse=dither=bayer" \
        -loop 0 assemblage-articulation-sweep-$view.gif
    done
"""
import FreeCAD, FreeCADGui, Part
import math, os

ASM_PATH = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/cad/assemblage-articulation.FCStd'
OUT_DIR = '/home/adm1/Fanny_P-tanque_World_Tour/hardware/renders/articulation/'

PIVOT = FreeCAD.Vector(0, 0, 2.5)
PEAK_TILT = 10.0
MAX_AXIAL_RISE = 1.5

TAMPON_H0 = 15.0
TAMPON_ROUT0 = 10.0
TAMPON_RIN = 4.25

AXES_DEG = [0.0, 90.0, 180.0, 270.0]
STRIKE_FRAMES = 12
STRIKE_RISE = 3
STRIKE_DECAY_TAU = 4.0
PHASE1_FRAMES = STRIKE_FRAMES * len(AXES_DEG)

PHASE2_FRAMES = 60
PHASE2_RAMP = 6

N_FRAMES = PHASE1_FRAMES + PHASE2_FRAMES

VIEWS = ['iso', 'top', 'front', 'right']


def phase1_tilt(local_i):
    if local_i <= STRIKE_RISE:
        return PEAK_TILT * (local_i / float(STRIKE_RISE))
    return PEAK_TILT * math.exp(-(local_i - STRIKE_RISE) / STRIKE_DECAY_TAU)


def phase2_tilt(local_i):
    if local_i < PHASE2_RAMP:
        return PEAK_TILT * (local_i / float(PHASE2_RAMP))
    if local_i > PHASE2_FRAMES - 1 - PHASE2_RAMP:
        return PEAK_TILT * ((PHASE2_FRAMES - 1 - local_i) / float(PHASE2_RAMP))
    return PEAK_TILT


def phase2_azimuth(local_i):
    return 360.0 * local_i / (PHASE2_FRAMES - 1)


def frame_axis_tilt(i):
    if i < PHASE1_FRAMES:
        axis_idx = i // STRIKE_FRAMES
        local_i = i % STRIKE_FRAMES
        return AXES_DEG[axis_idx], phase1_tilt(local_i)
    local_i = i - PHASE1_FRAMES
    return phase2_azimuth(local_i), phase2_tilt(local_i)


def axis_vector(az_deg):
    r = math.radians(az_deg)
    return FreeCAD.Vector(math.cos(r), math.sin(r), 0)


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

housing = doc.getObject('b_interfaceAxeAimant4mm_001_')
if housing:
    gdoc.getObject(housing.Name).Transparency = 70

doc.recompute()

view = gdoc.mdiViewsOfType("Gui::View3DInventor")[0]
VIEW_FUNCS = {
    'iso': view.viewIsometric,
    'top': view.viewTop,
    'front': view.viewFront,
    'right': view.viewRight,
}

# Fit the camera once per view using the peak-extent frame (azimuth doesn't
# change the extent by symmetry), then lock it for that view's whole sequence.
peak_axis = axis_vector(0.0)
peak_rot = FreeCAD.Rotation(peak_axis, PEAK_TILT)


def apply_frame(az, tilt):
    rot = FreeCAD.Rotation(axis_vector(az), tilt)
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


for view_name in VIEWS:
    frames_dir = OUT_DIR + 'sweep4_frames_%s/' % view_name
    os.makedirs(frames_dir, exist_ok=True)

    VIEW_FUNCS[view_name]()
    apply_frame(0.0, PEAK_TILT)
    FreeCADGui.SendMsgToActiveView("ViewFit")
    cam = view.getCameraNode()
    cam.height.setValue(cam.height.getValue() * 1.2)

    for i in range(N_FRAMES):
        az, tilt = frame_axis_tilt(i)
        apply_frame(az, tilt)
        view.saveImage(frames_dir + 'frame_%03d.png' % i, 900, 810, 'White')

    print("DONE view", view_name, "-", N_FRAMES, "frames in", frames_dir)

print("ALL VIEWS DONE. Document never saved.")
FreeCADGui.getMainWindow().close()
