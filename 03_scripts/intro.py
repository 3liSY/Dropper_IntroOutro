"""intro.py (v3) - the DROPPER intro in Blender 5.2 EEVEE: the two stand on a quartz start ledge inside a huge round
rainbow-wool shaft (the thumbnail's twisted spiral), 16 levels deep, a glowing diamond ring at every level line,
floating obstacles, a glowing water pool at the bottom, haze, dust and sparkles, PHOBOS-style coloured light.
Bodies and blocks come from the thumbnail tools (04_assets/scene/thumb.py, its top section).

    blender -b -P 03_scripts/intro.py -- <out.png> shot=<down|two|shout> [res=1280] [samples=48] [expo=0] [look=vivid|old]
One block = 1 unit; a body is 2 units tall. Shaft axis = z through (0, 0); the ledge sticks out from the -y wall, top at z = 0.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
SCENE = os.path.normpath(os.path.join(HERE, "..", "04_assets", "scene"))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = args[0]
OPT = dict(a.split("=", 1) for a in args[1:] if "=" in a)
SHOT = OPT.get("shot", "two")
V5 = SHOT == "full5"                      # the v5 world: wide ledge, gap, floating platform, dim wall
OLD = OPT.get("look", "vivid") == "old"
F = lambda k, d: float(OPT.get(k, d))   # noqa: E731
for k, v in (("JOINTOV", "auto"), ("VOX3D", "1")):
    os.environ.setdefault(k, v)

_thumb = open(os.path.join(SCENE, "thumb.py"), encoding="utf-8").read().split('\nT121 = os.path.join(D, "tex121")')[0]
_thumb = _thumb.replace("D = os.path.dirname(os.path.abspath(__file__))", "D = SCENE").replace(
    'OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.join(D, "thumb.png")', "OUT = args[0]")
_thumb = _thumb.replace('limb("arm" + side, (3, 12, 4), uv', 'limb("arm" + side, (ARMW, 12, 4), uv').replace(
    '(("R", (40, 16), (40, 32), -5.5), ("L", (32, 48), (48, 48), 5.5))', '(("R", (40, 16), (40, 32), -(4 + ARMW / 2)), ("L", (32, 48), (48, 48), 4 + ARMW / 2))')
ARMW = 3                                                      # 3 px arms (the creators' classic skins use 4)
exec(compile(_thumb, "thumb.py", "exec"), globals())          # skin_mat, player, block_mat, build_blocks, rot, upd, snap_feet
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

T121, T121S = os.path.join(SCENE, "tex121"), os.path.join(SCENE, "tex121s")
T189, TXE = os.path.join(SCENE, "tex189"), os.path.join(SCENE, "tex_extra")

# ------------------------------------------------------------------ the shaft
R = 26                    # inner radius of the wall (blocks): huge, so the far wall is small blocks and soft focus
LV, LH = 16, 10           # 16 levels, 10 blocks each
ZTOP, ZBOT = 30, -LV * LH  # wall top (open sky far above) and the pool level
BANDS = ["red", "orange", "yellow", "lime", "green", "cyan", "light_blue", "blue", "purple", "magenta"]
BOOST = {"red": 1.4, "purple": 1.6, "blue": 1.9, "green": 1.5, "cyan": 1.2, "light_blue": 1.0, "magenta": 1.1, "yellow": 0.85,
         "lime": 0.9}
WOFF, TW = F("woff", 0.62), F("tw", 0.6)   # colour wheel offset, log twist per depth (the thumbnail's spiral)
GLOW = F("glow", 0.3 if OLD else 0.62)
LY = -22.5                # the pair's spot on the ledge (y); x = 0


def rnd01(x, y, z, salt):
    return (((x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ salt) & 0xFFFF) / 65535.0


def band_of(x, y, z):
    a = (math.atan2(y + 0.5, x + 0.5) + math.pi) / (2 * math.pi) * F("arms", 2)   # two rainbows round the wall: narrower bands
    f = a + WOFF + TW * math.log(ZTOP + 3 - z)
    return int((f % 1.0) * len(BANDS)) % len(BANDS)


LEDGE = [(x, y) for x in range(-2, 2) for y in range(-28, -20)]       # the start ledge (tip row y = -21), top at z = 0
TIP = -21
if V5:                                                                # v5: wide enough for the creators a few steps behind the pair
    LEDGE = [(x, y) for x in range(-4, 4) for y in range(-28, -17)]
    TIP = -18
world = {}
for x in range(-R - 3, R + 3):
    for y in range(-R - 3, R + 3):
        d = math.hypot(x + 0.5, y + 0.5)
        if not (R - 1 <= d < R + 2):
            continue
        for z in range(ZBOT, ZTOP + 1):
            if d < R and rnd01(x, y, z, 11) > 0.33:                       # relief: a third of the inner layer sticks out
                continue
            world[(x, y, z)] = ("r%d" if d < R else "w%d") % band_of(x, y, z)   # relief blocks glow more: the edges glow
RING_Z = [-12 - k * 9 for k in range(LV)]                             # a ring per level, the first below a level shot's frame
for k, z in enumerate(RING_Z):
    for x in range(-R - 1, R + 1):
        for y in range(-R - 1, R + 1):
            if R - 1 <= math.hypot(x + 0.5, y + 0.5) < R:
                world[(x, y, z)] = "dia%d" % k
TGT_A = math.radians(-125)                                            # where YoCube1 rebuilds himself: standing on ring 2
TGT = (25.3 * math.cos(TGT_A), 25.3 * math.sin(TGT_A), RING_Z[1] + 1)
TGT3_A = math.radians(-160)                                           # and on ring 3 for the scoreboard
TGT3 = (25.3 * math.cos(TGT3_A), 25.3 * math.sin(TGT3_A), RING_Z[2] + 1)
for spot, ring in ((TGT, 1), (TGT3, 2)):
    for x in range(int(math.floor(spot[0])) - 1, int(math.floor(spot[0])) + 2):   # no relief blocks where he stands
        for y in range(int(math.floor(spot[1])) - 1, int(math.floor(spot[1])) + 2):
            for z in range(RING_Z[ring] + 1, RING_Z[ring] + 5):
                if world.get((x, y, z), "")[:1] == "r":
                    del world[(x, y, z)]
for x in range(-R - 3, R + 3):                                        # the rim at the top: quartz with sea lanterns
    for y in range(-R - 3, R + 3):
        d = math.hypot(x + 0.5, y + 0.5)
        if R - 1 <= d < R + 2:
            world[(x, y, ZTOP + 1)] = "lamp" if (x * 7 + y * 3) % 9 == 0 and d >= R else "chis"
for x, y in LEDGE:
    world[(x, y, -1)] = "ledge_tip" if y == TIP else "ledge"
    for z in range(0, 4):                                              # keep the wall relief off the ledge
        if world.get((x, y, z), "")[:1] in ("w", "r") and math.hypot(x + 0.5, y + 0.5) < R:
            del world[(x, y, z)]
for x in range(-4, 4) if V5 else range(-2, 2):                       # a chiseled quartz lip under the tip
    world[(x, TIP, -2)] = "chis"
# the start room: an alcove cut into the wall behind the ledge (the camera can stand in it and look out into the shaft)
for x in range(-6, 6):
    for y in range(-33, -22):
        for z in range(-1, 9):
            inside = -5 <= x <= 4 and y >= -31 and 0 <= z <= 7
            shell = -6 <= x <= 5 and y >= -32 and -1 <= z <= 8 and math.hypot(x + 0.5, y + 0.5) >= R - 1
            if inside and math.hypot(x + 0.5, y + 0.5) >= R - 1:
                world.pop((x, y, z), None)
            elif shell and not inside:
                world[(x, y, z)] = "brick"
for x in range(-5, 5):
    for y in range(-31, -27):
        world[(x, y, -1)] = "ledge"
if False and V5:   # shot 5 fix 2026-11-19: gap filled again (no slide; he sits in the hole). Was: the one-block gap under the alcove's left wall
    for y in range(-28, -23):
        for z in range(-6, 0):
            world.pop((-5, y, z), None)
CRATER = []                                                           # shot 5: the gag wall is colourful wool; 2x3 blocks break out
if V5:
    for (x, y, z), k in list(world.items()):
        if x == -6 and k == "brick" and -32 <= y <= -23 and 0 <= z <= 7:
            world[(x, y, z)] = "w%d" % band_of(x, y, z)
    for y in (-28, -27, -26, -25):                                    # bigger break 2026-11-19: 4x4 blocks (was 2x3)
        for z in (0, 1, 2, 3):
            CRATER.append(((-6, y, z), world.pop((-6, y, z))))
            world.pop((-7, y, z), None)                               # two-deep hole

# floating obstacles at different depths, never in the centre column (the dive and the water stay visible): the real
# Dropper's beams, iron grids (built as geometry below), floating wool islands, glass with a gap, glowing lantern clusters
OBST = []
PLAN = [(k, kind) for k in range(LV) for kind in (("island", "grid", "glass", "glow", "beam", "cross", "grid")[k % 7],
                                                   ("glow", "glass", "island", "grid")[k % 4])]
for n_, (k, kind) in enumerate(PLAN):
    zc = -k * LH - (6 if n_ % 2 == 0 else 11) - (4 if k == 0 else 0)  # nothing at eye level from the ledge
    ang = rnd01(k, 3 + n_ % 2, 5, 91) * 2 * math.pi
    if k == 0:
        ang = math.radians(150 if n_ % 2 == 0 else 35)                    # level 1: clear of the ledge view
    rr = 9 + 9 * rnd01(k, 4 + n_ % 2, 5, 92)
    cx, cy = rr * math.cos(ang), rr * math.sin(ang)
    if kind == "grid":
        OBST.append((kind, cx, cy, zc))
        continue
    if kind in ("beam", "cross"):
        for t in range(-R, R):
            for ax in ((1, 0),) if kind == "beam" else ((1, 0), (0, 1)):
                px, py = int(math.floor(cx * 0.5 + ax[0] * t)), int(math.floor(cy * 0.5 + ax[1] * t))
                dd = math.hypot(px + 0.5, py + 0.5)
                if 3.5 < dd < R - 1:
                    world[(px, py, zc)] = "beam"
                    world[(px, py, zc - 1)] = "beam"
    elif kind == "glow":
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                for dz in range(-2, 2):
                    if rnd01(dx, dy, dz + k, 5) < 0.7:
                        world[(int(cx) + dx, int(cy) + dy, zc + dz)] = "glow"
    elif kind == "island":
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if abs(dx) + abs(dy) < 5:
                    world[(int(cx) + dx, int(cy) + dy, zc)] = "r%d" % ((k * 3) % len(BANDS))
                    if abs(dx) + abs(dy) < 3:
                        world[(int(cx) + dx, int(cy) + dy, zc - 1)] = "r%d" % ((k * 3 + 1) % len(BANDS))
    else:                                                             # glass floor with a one-block gap to drop through
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if (dx, dy) != (1, -1):
                    world[(int(cx) + dx, int(cy) + dy, zc)] = "glass"
    OBST.append((kind, cx, cy, zc))
PLAT_Z = -17                                                          # v5: the floating platform of the diamond part, between two rings
if V5:
    for p_ in [p_ for p_, k_ in world.items() if abs(p_[0]) < 10 and -19 < p_[1] < -2 and -24 < p_[2] < -9 and k_[:1] != "d"]:
        del world[p_]                                                 # the air round the platform stays clear
    OBST = [o_ for o_ in OBST if not (abs(o_[1]) < 13 and -22 < o_[2] < 1 and -26 < o_[3] < -7)]
    for x in range(-7, 7):
        for y in range(-12, -6):
            edge = x in (-7, 6) or y in (-12, -7)
            world[(x, y, PLAT_Z - 1)] = "plat_e" if edge else "plat"
            if -6 < x < 5 and -11 < y < -7:
                world[(x, y, PLAT_Z - 2)] = "brick"
            if -4 < x < 3 and y in (-10, -9):
                world[(x, y, PLAT_Z - 3)] = "brick"
if V5:                                                                # floating blocks round the platform: near, middle and far, they slide against each other
    for cx, cy, cz, rad, band_ in ((-6, 1, -12, 3, 7), (7, 5, -13, 2, 0), (-11, 9, -19, 3, 2), (11, 12, -21, 3, 5), (-2, 15, -25, 3, 8)):
        for dx in range(-rad, rad + 1):
            for dy in range(-rad, rad + 1):
                if abs(dx) + abs(dy) <= rad + 1:
                    world[(cx + dx, cy + dy, cz)] = "r%d" % band_
                    if abs(dx) + abs(dy) <= rad - 1:
                        world[(cx + dx, cy + dy, cz - 1)] = "r%d" % ((band_ + 1) % len(BANDS))
    for cx, cy, cz in ((6, -1, -11), (-9, 6, -15)):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if rnd01(dx, dy, dz, 5) < 0.75:
                        world[(cx + dx, cy + dy, cz + dz)] = "glow"
for x in range(-R, R):                                                # the pool at the bottom
    for y in range(-R, R):
        if math.hypot(x + 0.5, y + 0.5) < R:
            world[(x, y, ZBOT - 2)] = "pool"

DEEP = (-95.0, 2.0, F("deep", 0.12))                                          # the wall glows less far down: the drop reads deep
kinds = {}
GLOW_W, GLOW_R = F("gloww", 0.045 if V5 else 0.07), F("glowr", 0.15 if V5 else 0.24)   # talking look: a dark wall whose relief edges glow
EMIT_NODES = {"w": [], "r": [], "dia": {}}                            # emission multipliers, so a clip can flood the colour


def emit_node(m, base):
    for n in m.node_tree.nodes:
        if n.type == "MATH" and n.operation == "MULTIPLY" and n.inputs[0].is_linked and not n.inputs[1].is_linked \
                and abs(n.inputs[1].default_value - base) < 1e-6:
            return n
    return None


for i, b in enumerate(BANDS):
    for pre, g in (("w", GLOW_W), ("r", GLOW_R)):
        e_ = g * BOOST.get(b, 1.0)
        m = block_mat("%s%d" % (pre, i), b + "_wool", (0.8, 0.8, 0.8) if pre == "w" else (1, 1, 1), emit=e_, rough=0.7,
                      texdir=T121S, cam_only=True, depth_fall=DEEP, ao_dist=1.0)
        kinds["%s%d" % (pre, i)] = (True, {"side": m})
        EMIT_NODES[pre].append((emit_node(m, e_), e_))
DIA = F("dia", 3.0)
for k in range(LV):
    m = block_mat("dia%d" % k, "diamond_block", emit=DIA, rough=0.2, texdir=TXE, cam_only=True)
    kinds["dia%d" % k] = (True, {"side": m})
    EMIT_NODES["dia"][k] = (emit_node(m, DIA), DIA)
kinds["chis"] = (True, {"side": block_mat("chis", "chiseled_quartz_block", (0.85, 0.85, 0.9), rough=0.5, texdir=T121),
                        "top": block_mat("chis_t", "chiseled_quartz_block_top", (0.85, 0.85, 0.9), rough=0.5, texdir=T121)})
kinds["lamp"] = (True, {"side": block_mat("lamp", "sea_lantern", (0.75, 0.95, 1.0), emit=3.0, texdir=T121, cam_only=True)})
LQ = (0.9, 0.86, 0.8) if V5 else (0.62, 0.58, 0.54)                  # v5: a brighter ledge, the suits stand out on it
m_lq = block_mat("ledge_t", "quartz_block_top", LQ, rough=0.45, texdir=T121, ao_dist=0.6)
m_ls = block_mat("ledge_s", "quartz_block_side", (0.55, 0.52, 0.5), rough=0.5, texdir=T121)
kinds["ledge"] = (True, {"top": m_lq, "side": m_ls, "bottom": m_ls})
kinds["ledge_tip"] = (True, {"top": block_mat("tip_t", "chiseled_quartz_block_top", (0.85, 0.85, 0.9), rough=0.45, texdir=T121),
                             "side": block_mat("tip_s", "chiseled_quartz_block", (0.85, 0.85, 0.9), rough=0.5, texdir=T121)})
kinds["brick"] = (True, {"side": block_mat("brick", "quartz_bricks", (0.75, 0.75, 0.8), rough=0.5, texdir=T121, ao_dist=0.6)})
kinds["beam"] = (True, {"side": block_mat("beam", "quartz_bricks", (0.7, 0.7, 0.76), rough=0.5, texdir=T121, ao_dist=0.6)})
kinds["glow"] = (True, {"side": block_mat("glow", "sea_lantern", (0.6, 0.95, 1.0), emit=2.2, texdir=T121, cam_only=True)})
kinds["glass"] = (False, {"side": block_mat("glass", "glass", alpha=True, rough=0.1, texdir=T189)})
kinds["pool"] = (True, {"side": block_mat("pool", "water", (0.2, 0.75, 1.0), emit=4.0, rough=0.1, texdir=T121, cam_only=True)})
kinds["plat"] = (True, {"top": block_mat("plat_t", "quartz_block_top", (0.5, 0.52, 0.6), rough=0.45, texdir=T121, ao_dist=0.6), "side": m_ls})
kinds["plat_e"] = (True, {"side": block_mat("plat_e", "sea_lantern", (0.7, 0.95, 1.0), emit=1.2, texdir=T121, cam_only=True)})
build_blocks(world, kinds)
CRATER_OBJ = []                                                       # each crater block its own object, hidden when the wall breaks
for i_, (p_, k_) in enumerate(CRATER):
    _before = set(bpy.data.objects)
    build_blocks({p_: k_}, {k_: kinds[k_]})
    o_ = (set(bpy.data.objects) - _before).pop()
    o_.name = "crater_%d" % i_
    CRATER_OBJ.append(o_)
for m in bpy.data.materials:
    if m.name == "glass":
        m.surface_render_method = "DITHERED"


def iron_grids():
    """Dropper iron-bar grids: flat 7 x 7 block lattices of thin dark-iron bars, floating at their level (one mesh)"""
    me = bpy.data.meshes.new("grids")
    bm = bmesh.new()
    for kind, cx, cy, zc in OBST:
        if kind != "grid":
            continue
        for i in range(15):
            off = -3.5 + i * 0.5
            for a, b, sx, sy in ((cx + off, cy, 0.07, 7.0), (cx, cy + off, 7.0, 0.07)):
                res = bmesh.ops.create_cube(bm, size=1.0)
                bmesh.ops.scale(bm, vec=(sx, sy, 0.07), verts=res["verts"])
                bmesh.ops.translate(bm, vec=(a, b, zc + 0.5), verts=res["verts"])
        for a, b, sx, sy in ((cx - 3.6, cy, 0.18, 7.3), (cx + 3.6, cy, 0.18, 7.3), (cx, cy - 3.6, 7.3, 0.18), (cx, cy + 3.6, 7.3, 0.18)):
            res = bmesh.ops.create_cube(bm, size=1.0)                 # the frame
            bmesh.ops.scale(bm, vec=(sx, sy, 0.16), verts=res["verts"])
            bmesh.ops.translate(bm, vec=(a, b, zc + 0.5), verts=res["verts"])
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("grids", me)
    sc.collection.objects.link(o)
    m = bpy.data.materials.new("iron")
    m.use_nodes = True
    b_ = m.node_tree.nodes["Principled BSDF"]
    b_.inputs["Base Color"].default_value = (0.32, 0.33, 0.36, 1)
    b_.inputs["Metallic"].default_value = 0.9
    b_.inputs["Roughness"].default_value = 0.35
    o.data.materials.append(m)


iron_grids()
print("SHAFT blocks", len(world), "obstacles", len(OBST))

# ------------------------------------------------------------------ bodies (the thumbnail rigs)
# A pose: "aR"/"aL" = the upper arm's direction in the body frame (+x = the character's LEFT, -y = front, +z = up),
# "elbowR/L" = forearm bend (negative x bends it forward), other joints = Euler degrees. Head: positive x tips the face
# down, positive z turns it to the character's left.
POSES = {
    "idle": {"aR": (-0.15, -0.1, -1), "aL": (0.2, -0.15, -1), "elbowR": (-14, 0, 0), "elbowL": (-22, 0, 0), "hip": (2, 0, -3),
             "legR": (-5, -3, 0), "kneeR": (8, 0, 0), "legL": (4, 3, 0), "head": (4, 0, 0)},
    "peer": {"aR": (-0.25, -0.5, -1), "aL": (0.3, -0.55, -1), "elbowR": (-40, 0, 0), "elbowL": (-35, 0, 0), "hip": (20, 0, 0),
             "legR": (-16, -3, 0), "kneeR": (26, 0, 0), "legL": (-12, 3, 0), "kneeL": (22, 0, 0), "head": (24, 0, -6)},
    "sweep": {"aR": (-0.2, -0.2, -1), "aL": (0.9, -0.9, -0.15), "elbowR": (-25, 0, 0), "elbowL": (-10, 0, 0), "hip": (4, 0, 10),
              "legR": (-6, -3, 0), "legL": (6, 3, 0), "kneeL": (8, 0, 0), "head": (12, 0, 30)},
    "point": {"aR": (-0.25, -0.15, -1), "aL": (0.8, -0.6, 0.08), "elbowR": (-30, 0, 0), "elbowL": (-4, 0, 0), "hip": (-3, -3, 12),
              "legR": (-6, -4, 0), "kneeR": (10, 0, 0), "legL": (8, 3, 0), "head": (-4, 0, 26)},
    "sheepish": {"aR": (-0.15, -0.25, -1), "aL": (1, -0.3, 0.55), "elbowR": (-20, 0, 0), "elbowL": (-125, 0, 0), "hip": (3, 4, -5),
                 "legR": (-4, 0, 0), "legL": (8, 3, 0), "kneeL": (6, 0, 0), "head": (6, -12, 16)},
    "shrug": {"aR": (-0.45, -0.35, -1), "aL": (0.45, -0.35, -1), "elbowR": (-85, 0, 0), "elbowL": (-85, 0, 0), "hip": (2, 3, 0),
              "legR": (-4, -2, 0), "legL": (6, 3, 0), "kneeL": (8, 0, 0), "head": (2, 14, 8)},
    "shout": {"aR": (-0.32, -0.12, 1), "aL": (0.42, -0.18, 1), "elbowR": (-12, 0, 0), "elbowL": (-28, 0, 0), "hip": (-8, 0, 0),
              "legR": (0, -9, 0), "legL": (0, 9, 0), "head": (F("hs", -16), 0, 0)},
    "lean_point": {"aR": (-0.2, 0.35, -1), "aL": (0.85, -0.55, 0.18), "elbowR": (-20, 0, 0), "elbowL": (-3, 0, 0), "hip": (10, 0, 14),
                   "legR": (12, -3, 0), "kneeR": (6, 0, 0), "legL": (-22, 4, 0), "kneeL": (18, 0, 0), "head": (-8, 0, 24)},
    "recoil_shrug": {"aR": (-0.8, -0.3, -0.55), "aL": (0.8, -0.3, -0.55), "elbowR": (-55, 0, 0), "elbowL": (-55, 0, 0),
                     "hip": (-9, 0, -6), "legR": (14, -4, 0), "kneeR": (10, 0, 0), "legL": (-6, 4, 0), "head": (-4, 10, -12)},
    "build": {"elbowR": (-110, 0, 0), "elbowL": (-110, 0, 0), "kneeR": (30, 0, 0), "kneeL": (30, 0, 0)},   # joint overlap only
    "lean_in": {"aR": (-0.3, -0.45, -1), "aL": (0.3, -0.45, -1), "elbowR": (-45, 0, 0), "elbowL": (-45, 0, 0), "hip": (12, 0, 4),
                "legR": (-14, -3, 0), "kneeR": (24, 0, 0), "legL": (-10, 3, 0), "kneeL": (20, 0, 0), "head": (2, 0, -14)},
    "noob_point": {"aR": (-1.0, 0.05, 0.25), "aL": (0.35, -0.3, -1), "elbowR": (-4, 0, 0), "elbowL": (-35, 0, 0), "hip": (-4, -3, -4),
                   "legR": (-8, -4, 0), "legL": (6, 4, 0), "kneeL": (8, 0, 0), "head": (-12, 0, -6)},
    "scratch": {"aR": (-0.2, -0.2, -1), "aL": (0.8, -0.15, 0.6), "elbowR": (-25, 0, 0), "elbowL": (-140, 0, 0), "hip": (3, 4, -4),
                "legR": (-4, 0, 0), "legL": (8, 3, 0), "kneeL": (6, 0, 0), "head": (8, -12, 10)},
    "listen": {"aR": (-0.2, -0.15, -1), "aL": (0.35, 0.05, -0.9), "elbowR": (-18, 0, 0), "elbowL": (-70, 0, 0), "hip": (3, 4, -6),
               "legR": (-6, -3, 0), "kneeR": (10, 0, 0), "legL": (6, 4, 0), "head": (4, 6, 8)},
    "talk_open": {"aR": (-0.6, -0.6, -0.55), "aL": (0.6, -0.6, -0.55), "elbowR": (-60, 0, 0), "elbowL": (-60, 0, 0), "hip": (2, 0, 0),
                  "legR": (-5, -3, 0), "kneeR": (6, 0, 0), "legL": (5, 3, 0), "head": (-4, 0, 0)},
    "idle_talk": {"aR": (-0.25, -0.35, -1), "aL": (0.25, -0.35, -1), "elbowR": (-40, 0, 0), "elbowL": (-35, 0, 0), "hip": (2, 0, 4),
                  "legR": (-5, -3, 0), "kneeR": (8, 0, 0), "legL": (4, 3, 0), "head": (2, 0, 16)},
    "recoil": {"aR": (-0.3, -1, 0.4), "aL": (0.4, -1, 0.1), "elbowR": (-80, 0, 0), "elbowL": (-45, 0, 0), "hip": (-10, 0, 0),
               "legR": (-12, -4, 0), "legL": (12, 5, 0), "kneeL": (25, 0, 0), "head": (-10, 0, -12)},
}
CHARS = []


def arm_euler(d):
    return Vector((0, 0, -1)).rotation_difference(Vector(d).normalized()).to_euler("XYZ")


def body(tag, skin, cfg):
    pose = POSES[cfg["pose"]]
    bends = POSES[cfg.get("build", cfg["pose"])]
    r = player(tag, os.path.join(SCENE, skin), {k: v for k, v in bends.items() if k.startswith(("elbow", "knee"))})
    CHARS.extend(r["meshes"])
    for j, deg in pose.items():
        if j in ("aR", "aL"):
            r["arm" + j[1]].rotation_euler = arm_euler(deg)
        else:
            rot(r[j], deg)
    rot(r["root"], (0, 0, cfg["yaw"]))
    r["base"].location = (cfg["pos"][0], cfg["pos"][1], 0)
    snap_feet(r, ["legR", "legL"])
    return r


# ------------------------------------------------------------------ the shots
# P = 3liSY, Y = YoCube1. yaw 0 faces -y, 90 faces +x, 180 faces +y (into the shaft).
SHOTS = {
    # beat 1/6: from just behind and above their heads, straight down the spiral
    "down": dict(cam=(2.0, LY - 2.4, 3.5), look=(-1.0, LY + 16.0, -12.0), lens=22, fstop=8, rimf=1.2, rim=2200,
                 P=dict(skin="3liSY.png", pos=(0.8, LY + 1.0), yaw=176, pose="peer"),
                 Y=dict(skin="YoCube1.png", pos=(-0.8, LY + 0.8), yaw=150, pose="sweep")),
    # beat 1 variant: over the drop just past the tip, looking almost straight down; the pair at the frame's edge
    "down2": dict(cam=(0.4, LY + 2.6, 4.6), look=(0.4, LY + 3.4, -60.0), lens=17, fstop=8, roll=True,
                  P=dict(skin="3liSY.png", pos=(0.8, LY + 1.0), yaw=176, pose="peer"),
                  Y=dict(skin="YoCube1.png", pos=(-0.8, LY + 0.8), yaw=160, pose="sweep")),
    # beat 5: from the start room out into the shaft; YoCube1 (left) points at 3liSY (right), the drop behind them
    "two": dict(cam=(0.5, LY - 4.7, 0.9), look=(0.0, LY, 1.3), lens=36, fstop=1.4, fore=True,
                P=dict(skin="3liSY.png", pos=(1.1, LY + 0.35), yaw=-8, pose="recoil_shrug"),
                Y=dict(skin="YoCube1.png", pos=(-1.0, LY), yaw=40, pose="lean_point")),
    # beat 4: 3liSY's shout, close and low, the open top and the far wall behind
    "shout": dict(cam=(0.55, LY - 1.95, 0.9), look=(0.15, LY, 2.05), lens=36, fstop=1.6, fore=True,
                  P=dict(skin="3liSY_scream.png", pos=(0.15, LY), yaw=-12, pose="shout"),
                  Y=dict(skin="YoCube1.png", pos=(-2.5, LY - 3.5), yaw=0, pose="recoil")),
    # ---- V4 stills (level camera, longer lens, depth of field)
    # opening reveal: behind and above their shoulders, the dark glowing shaft below
    "reveal": dict(cam=(0.3, LY - 1.4, 4.0), look=(0.0, LY + 15.0, -16.0), lens=28, fstop=5.6, rimf=0.6, rim=1400,
                   P=dict(skin="3liSY.png", pos=(0.8, LY + 1.0), yaw=176, pose="peer"),
                   Y=dict(skin="YoCube1.png", pos=(-0.8, LY + 0.8), yaw=150, pose="sweep")),
    # talking two-shot: from the start room, level, 50 mm; they face each other three-quarters, the shaft deep behind
    "talk": dict(cam=(0.35, LY - 5.6, 1.45), look=(0.0, LY, 1.08), lens=45, fstop=2.0,
                 P=dict(skin="3liSY.png", pos=(0.85, LY + 0.25), yaw=-48, pose="listen"),
                 Y=dict(skin="YoCube1.png", pos=(-0.85, LY), yaw=44, pose="talk_open")),
    # the shout: near face height, 50 mm, 4 degrees of tilt for impact, the fists in frame
    "shout4": dict(cam=(0.6, LY - 2.55, 1.6), look=(0.15, LY, 1.95), lens=50, fstop=2.0, roll=4.0, rim=650, key=420, face=12,
                   P=dict(skin=os.path.join(os.path.dirname(SCENE), "art", "skins", "3liSY_hds_A.png"), pos=(0.15, LY), yaw=-10,
                          pose="shout"),
                   Y=dict(skin="YoCube1.png", pos=(-2.5, LY - 3.5), yaw=0, pose="recoil")),
}
SKINS = os.path.normpath(os.path.join(SCENE, "..", "art", "skins"))
SHOTS["clip4"] = dict(cam=(0.35, LY - 5.6, 1.45), look=(0.0, LY, 1.08), lens=45, fstop=2.0,
                      P=dict(skin=os.path.join(os.path.dirname(SCENE), "art", "skins", "3liSY_hd_X.png"), pos=(0.85, LY + 0.25),
                             yaw=-30, pose="lean_in", build="build"),
                      Y=dict(skin="YoCube1.png", pos=(-0.85, LY), yaw=44, pose="talk_open", build="build"))
for nm in ("clip", "proof"):   # animated: poses, camera, mouths and lights are set per frame (see the end of this file)
    SHOTS[nm] = dict(cam=(1.32, LY - 1.62, 0.92), look=(0.95, LY + 0.3, 2.0), lens=36, fstop=1.6, fore=False,
                     P=dict(skin=os.path.join(SKINS, "3liSY_hd_X.png"), pos=(0.95, LY + 0.3), yaw=-20, pose="lean_in", build="build"),
                     Y=dict(skin="YoCube1.png", pos=(-0.95, LY), yaw=35, pose="idle_talk", build="build"))
SHOTS["full4"] = SHOTS["clip4"]
SHOTS["full5"] = dict(SHOTS["clip4"], P=dict(SHOTS["clip4"]["P"], skin=os.path.join(SKINS, "3liSY_v5_C.png")),
                      Y=dict(SHOTS["clip4"]["Y"], skin=os.path.join(SKINS, "YoCube1_clean.png")))
ANIM = SHOT in ("clip", "proof", "clip4", "full4", "full5")
S = SHOTS[SHOT]
for kk, idx in (("cx", 0), ("cy", 1), ("cz", 2)):
    if kk in OPT:
        S["cam"] = tuple(F(kk, 0) if i == idx else v for i, v in enumerate(S["cam"]))
for kk, idx in (("lx", 0), ("ly", 1), ("lz", 2)):
    if kk in OPT:
        S["look"] = tuple(F(kk, 0) if i == idx else v for i, v in enumerate(S["look"]))
S["lens"] = F("lens", S["lens"])
P = body("P", S["P"]["skin"], S["P"])
Y = body("Y", S["Y"]["skin"], S["Y"])


def split_head(r, tag, split=3):
    """YoCube1's head is a Rubik's cube: rebuild it as a top layer (rows 0..split) on its own pivot, so it can twist,
    and the rest; a black core between the layers shows only mid-twist, like a real cube."""
    mat = bpy.data.materials[tag]
    for nm in (tag + "head", tag + "head_o"):
        o = bpy.data.objects[nm]
        r["meshes"].remove(o)
        CHARS.remove(o)
        bpy.data.objects.remove(o)
    r["headtop"] = empty(tag + "_headtop", r["head"], (0, 0, 4))
    for suffix, uv, g in (("", (0, 0), 0), ("_o", (32, 0), 0.5)):
        for rows, par, z in (((0, split), r["headtop"], 4 - split / 2), ((split, 8), r["head"], (8 - split) / 2)):
            if suffix and os.environ.get("VOX3D") == "1":
                o = vox_box(tag + "head%d" % rows[0] + suffix, (8, 8, 8), uv, mat, g, rows=rows, vfrom=rows[0] if rows[0] else None)
            else:
                o = box(tag + "head%d" % rows[0] + suffix, (8, 8, 8), uv, mat, g, rows=rows)
            o.parent = par
            o.location = Vector((0, 0, z)) * PX
            r["meshes"].append(o)
            CHARS.append(o)
    core = bpy.data.meshes.new(tag + "core")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(core)
    bm.free()
    co_ = bpy.data.objects.new(tag + "core", core)
    sc.collection.objects.link(co_)
    co_.parent = r["head"]
    co_.location = Vector((0, 0, 8 - split)) * PX
    co_.scale = (7.8 * PX, 7.8 * PX, 0.3 * PX)
    cm = bpy.data.materials.new(tag + "core")
    cm.use_nodes = True
    cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
    co_.data.materials.append(cm)
    r["meshes"].append(co_)
    CHARS.append(co_)


def dim_skin(name, k_):
    """multiply a skin material's colour (YoCube1's bright stickers washed out to pastel under the key light)"""
    nt_ = bpy.data.materials[name].node_tree
    bs = next(n for n in nt_.nodes if n.type == "BSDF_PRINCIPLED")
    src = bs.inputs["Base Color"].links[0].from_socket
    mx = nt_.nodes.new("ShaderNodeMix")
    mx.data_type, mx.blend_type = "RGBA", "MULTIPLY"
    mx.inputs["Factor"].default_value = 1.0
    mx.inputs[7].default_value = (k_, k_, k_, 1)
    nt_.links.new(src, mx.inputs[6])
    nt_.links.new(mx.outputs[2], bs.inputs["Base Color"])


def split_head3(r, tag, cuts=(2, 5)):
    """v5: three real cube layers (the glasses sit whole on the middle one), no outer layer: the clean head. r["layers"] = the pivots."""
    mat = bpy.data.materials[tag]
    for nm in (tag + "head", tag + "head_o"):
        o = bpy.data.objects[nm]
        r["meshes"].remove(o)
        CHARS.remove(o)
        bpy.data.objects.remove(o)
    r["layers"] = []
    bounds = (0,) + tuple(cuts) + (8,)
    for i in range(3):
        a, b = bounds[i], bounds[i + 1]
        piv = empty(tag + "_lay%d" % i, r["head"], (0, 0, 4))
        r["layers"].append(piv)
        o = box(tag + "lay%d" % i, (8, 8, 8), (0, 0), mat, 0, rows=(a, b))
        o.parent = piv
        o.location = Vector((0, 0, 4 - (a + b) / 2)) * PX
        r["meshes"].append(o)
        CHARS.append(o)
    for i, z in enumerate((8 - cuts[0], 8 - cuts[1])):
        core = bpy.data.meshes.new(tag + "core%d" % i)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(core)
        bm.free()
        co_ = bpy.data.objects.new(tag + "core%d" % i, core)
        sc.collection.objects.link(co_)
        co_.parent = r["head"]
        co_.location = Vector((0, 0, z)) * PX
        co_.scale = (7.8 * PX, 7.8 * PX, 0.5 * PX)
        cm = bpy.data.materials.new(tag + "core%d" % i)
        cm.use_nodes = True
        cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
        co_.data.materials.append(cm)
        r["meshes"].append(co_)
        CHARS.append(co_)


if ANIM:
    (split_head3 if V5 else split_head)(Y, "Y")
    dim_skin("Y", F("ydim", 0.72))

# ------------------------------------------------------------------ camera
cam = bpy.data.cameras.new("cam")
cam.lens = S["lens"]
cam.sensor_width = 36
co = bpy.data.objects.new("cam", cam)
sc.collection.objects.link(co)
sc.camera = co
co.location = Vector(S["cam"])
co.rotation_euler = (Vector(S["look"]) - co.location).to_track_quat("-Z", "Y").to_euler()
if isinstance(S.get("roll"), float):   # a few degrees of tilt (only the shout)
    from mathutils import Quaternion
    co.rotation_euler = (co.rotation_euler.to_quaternion() @ Quaternion((0, 0, 1), math.radians(S["roll"]))).to_euler()
elif S.get("roll"):   # nearly straight down: the frame's long side runs along the ledge, the pair on the left
    from mathutils import Matrix
    dv = (Vector(S["look"]) - co.location).normalized()
    upv = (Vector((-1, 0, 0)) - dv * dv.x).normalized()
    rgt = dv.cross(upv).normalized()
    co.rotation_euler = Matrix((rgt, upv, -dv)).transposed().to_euler()
cam.dof.use_dof = True
cam.dof.aperture_fstop = S["fstop"]
cam.clip_end = 600
sc.render.resolution_x = int(OPT.get("res", 1280))
sc.render.resolution_y = sc.render.resolution_x * 9 // 16
sc.render.resolution_percentage = 100

# ------------------------------------------------------------------ characters in their own collection (linked lights)
cc = bpy.data.collections.new("chars")
sc.collection.children.link(cc)
for o in CHARS:
    for c in o.users_collection:
        c.objects.unlink(o)
    cc.objects.link(o)
upd()


def head_of(rig):
    return rig["head"].matrix_world @ Vector((0, 0, 4 * PX))


hP, hY = head_of(P), head_of(Y)
mid = (hP + hY) / 2 - Vector((0, 0, 0.35)) if SHOT not in ("shout", "clip", "proof") else hP - Vector((0, 0, 0.25))
cam.dof.focus_distance = (mid - co.location).length if not SHOT.startswith("down") else 3.5


def axes(cam_pos, target):
    f_ = target - cam_pos
    f_.z = 0
    f_.normalize()
    return f_, f_.cross(Vector((0, 0, 1))).normalized()


fwd, right = axes(co.location, mid)
up = Vector((0, 0, 1))


def area(name, loc, target, energy, color, size, linked=True):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.color, L.size = energy, color, size
    o = bpy.data.objects.new(name, L)
    sc.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if linked:
        o.light_linking.receiver_collection = cc
        L.volume_factor = 0.0                    # character lights never glow in the haze
    return o


def point(name, loc, energy, color, radius=0.3):
    L = bpy.data.lights.new(name, "POINT")
    L.energy, L.color, L.shadow_soft_size = energy, color, radius
    o = bpy.data.objects.new(name, L)
    sc.collection.objects.link(o)
    o.location = loc
    return o


k = 0.5 if OLD else 1.0
warm = (1.0, 0.6, 0.35) if OLD else (1.0, 0.8, 0.62)
rf = S.get("rimf", 3.5)                                                                                  # how far behind them the rims sit
re = F("rim", S.get("rim", 1700))
LT = {"key": area("key", mid, mid + up, F("key", S.get("key", 300)), warm, F("keysize", 2.2)),         # soft warm key, front side
      "rimA": area("rimA", mid, mid + up, re * k, (1.0, 0.1, 0.55), 1.0),                               # magenta rim, back left
      "rimB": area("rimB", mid, mid + up, re * k, (0.1, 0.75, 1.0), 1.0),                               # cyan rim, back right
      "under": area("under", mid, mid + up, 220 * k, (0.45, 0.35, 1.0), 2.0),                           # the shaft glow from below
      "faceP": area("faceP", mid, mid + up, F("face", S.get("face", 9)), (1.0, 0.93, 0.85), 0.8),        # soft face lights
      "faceY": area("faceY", mid, mid + up, 1.5, (1.0, 0.93, 0.85), 0.6)}
fl = bpy.data.lights.new("floor", "SPOT")                                                                # a warm pool on the ledge
fl.energy, fl.color, fl.spot_size, fl.spot_blend, fl.shadow_soft_size = F("floor", 450), (1.0, 0.8, 0.6), math.radians(30), 0.8, 0.5
LT["floor"] = bpy.data.objects.new("floor", fl)
sc.collection.objects.link(LT["floor"])


def place_lights(cam_pos, mid, hP, hY):
    """the character lights follow the camera and the subject (called once for a still, every frame for a clip)"""
    fwd, right = axes(cam_pos, mid)
    for nm, loc, tgt in (("key", mid - fwd * 3.0 - right * 2.2 + up * 1.4, mid),
                         ("rimA", mid + fwd * rf - right * 1.7 + up * 0.8, mid),
                         ("rimB", mid + fwd * rf + right * 1.7 + up * 0.6, mid),
                         ("under", mid - fwd * 1.2 - up * 2.4, mid + up * 0.6),
                         ("faceP", hP - fwd * 1.1 - up * 0.3 - right * 0.2, hP),   # from below the lens: the face reads under the hair
                         ("faceY", hY - fwd * 1.3 + up * 0.25 - right * 0.3, hY),
                         ("floor", mid - fwd * 1.5 + up * 4.5, mid - up * 1.6)):
        LT[nm].location = loc
        LT[nm].rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()


place_lights(co.location, mid, hP, hY)
# the shaft's own light: a cyan glow at every diamond ring, the pool's glow from the bottom, a soft top light
RING_L = {}
for kk, zr in enumerate(RING_Z):
    RING_L[kk] = point("ring%d" % kk, (0, 0, zr), F("ring", 3200) * k, (0.25, 0.9, 1.0), 3.0)
    RING_L[kk].data.use_shadow = False
point("pool", (0, 0, ZBOT + 3), 40000 * k, (0.2, 0.75, 1.0), 6.0).data.use_shadow = False
area("sky", (0, 0, ZTOP + 8), (0, 0, 0), 9000 if OLD else 2500, (1.0, 0.6, 0.35) if OLD else (0.8, 0.85, 1.0), 40.0, linked=False)

# ------------------------------------------------------------------ haze below the ledge, dust, sparkles
bpy.ops.mesh.primitive_cylinder_add(radius=R + 0.5, depth=-3 - ZBOT, location=(0, 0, (-3 + ZBOT) / 2), vertices=64)
hz = bpy.context.active_object
hz.name = "haze"
hm = bpy.data.materials.new("haze")
hm.use_nodes = True
hn = hm.node_tree
hn.nodes.clear()
pv = hn.nodes.new("ShaderNodeVolumePrincipled")
pv.inputs["Density"].default_value = F("haze", 0.009)
pv.inputs["Anisotropy"].default_value = 0.4
pv.inputs["Color"].default_value = (0.35, 0.4, 0.7, 1)
ho = hn.nodes.new("ShaderNodeOutputMaterial")
hn.links.new(pv.outputs["Volume"], ho.inputs["Volume"])
hz.data.materials.append(hm)
bpy.ops.mesh.primitive_cylinder_add(radius=R + 0.5, depth=ZTOP + 3, location=(0, 0, (ZTOP - 3) / 2), vertices=64)
hz2 = bpy.context.active_object                                       # a thinner air above: the far wall recedes behind them
hz2.name = "haze_air"
hm2 = hm.copy()
hm2.node_tree.nodes["Principled Volume"].inputs["Density"].default_value = F("haze2", 0.0012)
hz2.data.materials.append(hm2)


def specks(name, n, size, zr, color, strength, salt):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for i in range(n):
        a = rnd01(i, 1, salt, 3) * 2 * math.pi
        rr = (R - 2) * math.sqrt(rnd01(i, 2, salt, 4))
        z = zr[0] + (zr[1] - zr[0]) * rnd01(i, 3, salt, 5)
        s = size * (0.5 + rnd01(i, 4, salt, 6))
        res = bmesh.ops.create_cube(bm, size=s)
        bmesh.ops.translate(bm, verts=res["verts"], vec=(rr * math.cos(a), rr * math.sin(a), z))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b_ = m.node_tree.nodes["Principled BSDF"]
    b_.inputs["Base Color"].default_value = (*color, 1)
    b_.inputs["Emission Color"].default_value = (*color, 1)
    b_.inputs["Emission Strength"].default_value = strength
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


specks("dust", 2600, 0.03, (-50, 12), (1.0, 0.82, 0.55), 5.0 * k, 1)
specks("sparkle", 420, 0.05, (-70, 10), (0.55, 0.95, 1.0), 16.0 * k, 2)
if S.get("fore"):   # a few out-of-focus sparkles between the lens and them: depth in front, not only behind
    me = specks("fore", 18, 0.012, (0, 1), (1.0, 0.85, 0.6), 6.0 * k, 3).data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    cl = Vector(S["cam"])
    for i in range(0, len(bm.verts), 8):
        g = bm.verts[i:i + 8]
        c0 = sum((v.co for v in g), Vector()) / 8
        u_, v_ = rnd01(i, 7, 3, 8) - 0.5, rnd01(i, 8, 3, 9) - 0.5
        tgt = cl + fwd * (0.9 + 1.4 * rnd01(i, 9, 3, 10)) + right * u_ * 2.6 + up * v_ * 1.5
        if abs(u_) < 0.42:
            tgt += right * (1.2 if u_ >= 0 else -1.2)               # keep them at the frame's sides, off the bodies
        for v in g:
            v.co += tgt - c0
    bm.to_mesh(me)
    bm.free()

# ------------------------------------------------------------------ sky through the open top
w = bpy.data.worlds.new("sky")
sc.world = w
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
outn = nt.nodes.new("ShaderNodeOutputWorld")
bg = nt.nodes.new("ShaderNodeBackground")
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Generated"], sep.inputs[0])
ramp = nt.nodes.new("ShaderNodeValToRGB")
nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
ramp.color_ramp.elements[0].color = (0.9, 0.45, 0.2, 1) if OLD else (0.28, 0.04, 0.42, 1)
ramp.color_ramp.elements[1].color = (0.35, 0.3, 0.55, 1) if OLD else (0.008, 0.01, 0.045, 1)
ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = 0.0, 0.75
vor = nt.nodes.new("ShaderNodeTexVoronoi")
vor.inputs["Scale"].default_value = 140
nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
star = nt.nodes.new("ShaderNodeMapRange")
star.inputs["From Min"].default_value, star.inputs["From Max"].default_value = 0.13, 0.0
star.inputs["To Min"].default_value, star.inputs["To Max"].default_value = 0.0, 0.0 if OLD else 6.0
nt.links.new(vor.outputs["Distance"], star.inputs["Value"])
add = nt.nodes.new("ShaderNodeMix")
add.data_type, add.blend_type = "RGBA", "ADD"
add.inputs["Factor"].default_value = 1.0
nt.links.new(ramp.outputs["Color"], add.inputs[6])
nt.links.new(star.outputs["Result"], add.inputs[7])
nt.links.new(add.outputs[2], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 0.6
nt.links.new(bg.outputs["Background"], outn.inputs["Surface"])

# ------------------------------------------------------------------ fit report: how big each body is in frame
upd()


def fit(rig):
    xs, ys = [], []
    for o in rig["meshes"]:
        mw = o.matrix_world
        for v in list(o.data.vertices)[::3]:
            p = world_to_camera_view(sc, co, mw @ v.co)
            if p.z > 0:
                xs.append(p.x)
                ys.append(p.y)
    return min(xs), max(xs), min(ys), max(ys)


for nm, rig in (("3liSY", P), ("YoCube1", Y)):
    x0, x1, y0, y1 = fit(rig)
    print("FIT %s x %.2f-%.2f y %.2f-%.2f  h %.2f" % (nm, x0, x1, y0, y1, min(y1, 1) - max(y0, 0)))

# ------------------------------------------------------------------ render (EEVEE)
for vt in (OPT.get("vt", "Khronos PBR Neutral"), "Standard"):
    try:
        sc.view_settings.view_transform = vt
        break
    except TypeError:
        continue
sc.view_settings.exposure = F("expo", 0.0)
r = sc.render
try:
    r.engine = "BLENDER_EEVEE"
except TypeError:
    r.engine = "BLENDER_EEVEE_NEXT"
ee = sc.eevee
for attr, val in (("taa_render_samples", int(OPT.get("samples", 48))), ("use_raytracing", True), ("use_shadows", True),
                  ("volumetric_tile_size", "4"), ("volumetric_samples", 64), ("volumetric_end", 220.0),
                  ("use_volumetric_shadows", False), ("shadow_pool_size", "1024")):
    if hasattr(ee, attr):
        try:
            setattr(ee, attr, val)
        except (TypeError, ValueError):
            pass
r.image_settings.file_format = "PNG"
if not ANIM:
    r.filepath = OUT
    bpy.ops.render.render(write_still=True)
    print("DONE", OUT, SHOT, "engine", r.engine, "vt", sc.view_settings.view_transform)
    sys.exit(0)

# ================================================================== animation: the Stage 3 clip and the lip-sync proof
# Every frame: poses from eased keys (arms follow the body a few frames late), breathing, weight shift and head drift so
# nothing freezes, 3liSY's mouth from lipsync.py (syllables of the word times), YoCube1's nod, bob and cube twist on
# their syllables, a smooth camera spline, the character lights following camera and subject.
import json  # noqa: E402

sys.path.insert(0, HERE)
import lipsync as LS  # noqa: E402

FPS = 60
T0, T1 = F("t0", 6.10), F("t1", 9.10)
JOINTS = ("hip", "head", "legR", "legL", "kneeR", "kneeL", "elbowR", "elbowL")


def clamp01(x):
    return max(0.0, min(1.0, x))


def ease(x):
    x = clamp01(x)
    return x * x * x * (x * (x * 6 - 15) + 10)


def bump(t, t0, d):
    x = (t - t0) / d
    return math.sin(math.pi * x) if 0 <= x <= 1 else 0.0


def win(t, a, b, f=0.12):
    return ease((t - (a - f)) / f) * (1 - ease((t - b) / f))


def mix_pose(a, b, w):
    out = {}
    for j in set(a) | set(b):
        if j in ("aR", "aL"):
            va, vb = Vector(a.get(j, (0, 0, -1))).normalized(), Vector(b.get(j, (0, 0, -1))).normalized()
            v = va.lerp(vb, w)
            out[j] = tuple(v.normalized()) if v.length > 1e-4 else tuple(vb)
        else:
            va, vb = a.get(j, (0, 0, 0)), b.get(j, (0, 0, 0))
            out[j] = tuple(x + (y - x) * w for x, y in zip(va, vb))
    return out


def keyed(keys, t):
    if t <= keys[0][0]:
        return keys[0][1], keys[0][1], 0.0
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        if t < tb:
            return va, vb, ease((t - ta) / (tb - ta))
    return keys[-1][1], keys[-1][1], 0.0


def pose_at(keys, t):
    a, b, w = keyed(keys, t)
    return mix_pose(POSES[a], POSES[b], w)


def num_at(keys, t):
    a, b, w = keyed(keys, t)
    if isinstance(a, tuple):
        return tuple(x + (y - x) * w for x, y in zip(a, b))
    return a + (b - a) * w


# ---- the beats of 6.10-9.10 s (word times: ايوااااا 6.10, يا 6.74, نووب 7.01 | وعلي 7.34, الفاشل 7.73, توه 8.23 ...)
P_POSE = [(6.10, "lean_in"), (6.22, "shout"), (6.88, "shout"), (7.05, "noob_point"), (7.40, "noob_point"), (7.62, "idle"),
          (7.88, "recoil_shrug"), (8.32, "recoil_shrug"), (8.62, "scratch"), (9.20, "scratch")]
P_YAW = [(6.10, -20.0), (6.25, -10.0), (6.86, -10.0), (7.06, -16.0), (7.45, -16.0), (7.95, -14.0), (9.20, -8.0)]
P_POS = [(6.10, (0.95, LY + 0.3)), (9.20, (0.95, LY + 0.3))]
Y_POSE = [(6.10, "idle_talk"), (6.16, "idle_talk"), (6.32, "recoil"), (6.95, "recoil"), (7.22, "idle"), (7.40, "idle"),
          (7.64, "lean_point"), (8.22, "lean_point"), (8.48, "talk_open"), (9.20, "talk_open")]
Y_YAW = [(6.10, 35.0), (6.30, 18.0), (7.20, 24.0), (7.62, 55.0), (8.24, 50.0), (8.55, 12.0), (9.20, 8.0)]
Y_POS = [(6.10, (-0.95, LY)), (6.17, (-0.95, LY)), (6.42, (-1.22, LY - 0.18)), (7.25, (-1.22, LY - 0.18)), (7.70, (-1.05, LY)),
         (9.20, (-1.05, LY))]
CAM = [(6.10, (1.32, LY - 1.62, 0.92), (0.95, LY + 0.3, 2.0)), (7.20, (1.24, LY - 1.36, 0.98), (0.95, LY + 0.3, 2.0)),
       (8.60, (0.42, LY - 4.70, 1.00), (0.0, LY, 1.30)), (9.20, (0.37, LY - 4.40, 1.00), (0.0, LY, 1.30))]

SHAPE_P, STRESS_P = LS.track("SRB")
WORDS, ENV = LS.load()
Y_SYL = []                                                  # YoCube1's syllable onsets: (time, weight)
for w in WORDS:
    if w["spk"] == "YoCube1":
        for t0, t1, letters, plan in LS.word_syllables(w):
            Y_SYL.append((t0, 0.5 + 0.5 * ENV[min(len(ENV) - 1, int(t0 * FPS) + 2)]))
TWISTS, last = [], -9.0                                     # the cube's top layer turns on stressed syllables
for ts, s in LS.track("YoCube1")[1]:
    if s >= 0.55 and ts - last >= 0.45:
        TWISTS.append((ts, 1 if len(TWISTS) % 2 == 0 else -1))
        last = ts
MOUTH = {} if V5 else {(st, s): bpy.data.images.load(os.path.join(SKINS, f"3liSY_{st}_{s}.png"), check_existing=True)
                       for st in ("hd", "hds") for s in LS.SHAPES}
for im in MOUTH.values():
    im.alpha_mode = "STRAIGHT"
MOUTH_NODE = next(n for n in bpy.data.materials["P"].node_tree.nodes if n.type == "TEX_IMAGE")


def hermite(keys, t, idx):
    """camera spline: Catmull-Rom tangents in time, so moves flow from one into the next without a stop"""
    ts = [k[0] for k in keys]
    if t <= ts[0]:
        return Vector(keys[0][idx])
    if t >= ts[-1]:
        return Vector(keys[-1][idx])
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    p = [Vector(k[idx]) for k in keys]

    def tan(j):
        if j == 0 or j == len(p) - 1:
            return Vector((0, 0, 0))
        return (p[j + 1] - p[j - 1]) / (ts[j + 1] - ts[j - 1])
    h = ts[i + 1] - ts[i]
    s = (t - ts[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return p[i] * h00 + tan(i) * h * h10 + p[i + 1] * h01 + tan(i + 1) * h * h11


def animate(rig, tag, t, keys, yaws, poss):
    ph = 0.0 if tag == "P" else 1.7
    pose = pose_at(keys, t)
    late = pose_at(keys, t - 0.07)                          # the arms follow the body a few frames late
    for j in ("aR", "aL", "elbowR", "elbowL"):
        if j in late:
            pose[j] = late[j]
    add = {j: [0.0, 0.0, 0.0] for j in JOINTS}
    add["hip"][0] += 1.2 * math.sin(2 * math.pi * 0.30 * t + ph)              # breathing
    add["hip"][1] += 1.8 * math.sin(2 * math.pi * 0.23 * t + ph)              # weight shift
    add["head"][0] += 1.5 * math.sin(2 * math.pi * 0.31 * t + ph + 0.5)
    add["head"][2] += 2.5 * math.sin(2 * math.pi * 0.17 * t + ph)
    add["elbowR"][0] += 4.0 * math.sin(2 * math.pi * 0.37 * t + ph)
    add["elbowL"][0] += 4.0 * math.sin(2 * math.pi * 0.41 * t + ph + 1.0)
    z = 0.0
    arm_dz = 0.0
    if tag == "P":
        pm = win(t, 6.30, 6.80, 0.08) * max(0.0, math.sin(2 * math.pi * 2.6 * (t - 6.30)))   # two arm pumps on the shout
        arm_dz -= 0.9 * pm
        add["elbowR"][0] -= 55 * pm
        add["elbowL"][0] -= 55 * pm
        z += 0.04 * pm + 0.10 * bump(t, 6.13, 0.32)                                     # a little jump on the YES
        snap = clamp01((t - 6.11) / 0.05) * math.exp(-max(0.0, t - 6.16) / 0.25)
        add["head"][0] -= 10 * snap                                                     # the head snaps back
        for ts, s in STRESS_P:
            add["head"][0] -= 5 * s * bump(t, ts - 0.02, 0.16)                          # accent on the stressed syllable
        add["head"][2] += 3 * math.sin(2 * math.pi * 3.0 * t) * win(t, 6.25, 6.70)      # a shake on the long aaaa
        add["elbowL"][0] += 14 * math.sin(2 * math.pi * 4.5 * t) * win(t, 8.70, 9.30)   # really scratching his head
    else:
        z += 0.10 * bump(t, 6.17, 0.30)                                                 # startled hop
        for ts, wgt in Y_SYL:
            b = bump(t, ts - 0.01, 0.15)
            add["head"][0] += 5.0 * wgt * b                                             # nod on every syllable
            z += 0.012 * wgt * b                                                        # and a bob
        add["elbowL"][0] -= 10 * sum(bump(t, ts, 0.12) for ts, _ in Y_SYL if 7.70 <= ts <= 8.25)   # jabs while pointing
        beat = sum(wg * bump(t, ts, 0.14) for ts, wg in Y_SYL if ts >= 8.45 or ts < 6.05)   # open hands bounce on the words
        add["elbowR"][0] -= 14 * beat
        add["elbowL"][0] -= 14 * beat
        add["hip"][0] += 3 * beat
        rig["headtop"].rotation_euler = (0, 0, math.radians(sum(90 * d * ease((t - ts) / 0.16) for ts, d in TWISTS)))
    for j in ("aR", "aL"):
        v = Vector(pose.get(j, (0, 0, -1)))
        v.z += arm_dz
        rig["arm" + j[1]].rotation_euler = arm_euler(v)
    for j in JOINTS:
        base = pose.get(j, (0, 0, 0))
        rot(rig[j], tuple(base[i] + add[j][i] for i in range(3)))
    rot(rig["root"], (0, 0, num_at(yaws, t) + 2.0 * math.sin(2 * math.pi * 0.19 * t + ph)))
    pos = num_at(poss, t)                                   # (x, y) or (x, y, ground height)
    rig["base"].location = (pos[0], pos[1], 0)
    snap_feet(rig, ["legR", "legL"])
    rig["base"].location.z += z + (pos[2] if len(pos) > 2 else 0.0)


def set_mouth(t):
    f = min(len(SHAPE_P) - 1, int(round(t * FPS)))
    MOUTH_NODE.image = MOUTH[("hds" if t < 7.5 else "hd", SHAPE_P[f])]
    return SHAPE_P[f]


def set_frame(t):
    animate(P, "P", t, P_POSE, P_YAW, P_POS)
    animate(Y, "Y", t, Y_POSE, Y_YAW, Y_POS)
    shape = set_mouth(t)
    upd()
    hp, hy = head_of(P), head_of(Y)
    cpos, look = hermite(CAM, t, 1), hermite(CAM, t, 2)
    co.location = cpos
    co.rotation_euler = (look - cpos).to_track_quat("-Z", "Y").to_euler()
    focus = hp.lerp((hp + hy) / 2, ease((t - 7.5) / 0.8))
    cam.dof.focus_distance = (focus - cpos).length
    place_lights(cpos, focus - Vector((0, 0, 0.3)), hp, hy)
    for nm, sp in (("dust", 0.22), ("sparkle", 0.35)):
        bpy.data.objects[nm].location.z = sp * (t - T0)
    return shape


if SHOT in ("clip4", "full4", "full5"):   # the V4 motion test and the full intros live in their own files, run in this scene
    fn_ = os.path.join(HERE, SHOT + ".py")
    exec(compile(open(fn_, encoding="utf-8").read(), fn_, "exec"), globals())
    sys.exit(0)

if SHOT == "clip":
    outdir = os.path.dirname(OUT)
    os.makedirs(outdir, exist_ok=True)
    f0, f1 = int(F("f0", 0)), int(F("f1", round((T1 - T0) * FPS)))
    frames = [int(v) for v in OPT["only"].split(",")] if "only" in OPT else range(f0, f1)
    for fr in frames:
        path = os.path.join(outdir, "f_%04d.png" % fr)
        if os.path.exists(path) and OPT.get("force") != "1":
            continue
        t = T0 + fr / FPS
        shape = set_frame(t)
        r.filepath = path
        bpy.ops.render.render(write_still=True)
        if fr % 10 == 0:
            print("FRAME", fr, "t %.2f" % t, "mouth", shape, flush=True)
    print("CLIP DONE", f0, f1)
    sys.exit(0)

# ---- proof: a face close-up at every syllable of six key words (shape shown = the shape the clip uses at that time)
outdir = os.path.dirname(OUT)
os.makedirs(outdir, exist_ok=True)
sc.render.resolution_x = sc.render.resolution_y = 360
cam.lens, cam.dof.use_dof = 55, False
KEY = {"ايوااااا": "P", "نووب": "P", "اوووو": "P", "الفاشل": "Y", "دايموند": "Y", "عقاب": "Y"}
manifest = []
for w in WORDS:
    if w["w"] not in KEY or (w["w"], w["s"]) in [(m["word"], m["ws"]) for m in manifest]:
        continue
    who = KEY[w["w"]]
    rig = P if who == "P" else Y
    for k_, (t0, t1, letters, plan) in enumerate(LS.word_syllables(w)):
        tt, acc = t0, 0.0
        for frac, shp in plan:
            tm = tt + (t1 - t0) * frac / 2
            tt += (t1 - t0) * frac
            for rg, tg in ((P, "P"), (Y, "Y")):
                animate(rg, tg, 7.0, [(0, "idle")], [(0, 0.0)], [(0, (0.95, LY + 0.3) if tg == "P" else (-1.6, LY))])
            if who == "Y":
                animate(Y, "Y", tm, [(0, "idle")], [(0, 0.0)], [(0, (-1.6, LY))])
            shown = set_mouth(tm) if who == "P" else "-"
            upd()
            h = head_of(rig)
            co.location = h + Vector((0.0, -1.25, 0.05))
            co.rotation_euler = (h - co.location).to_track_quat("-Z", "Y").to_euler()
            place_lights(co.location, h - Vector((0, 0, 0.3)), head_of(P), head_of(Y))
            fn = os.path.join(outdir, "proof_%s_%.3f.png" % (who, tm))
            r.filepath = fn
            bpy.ops.render.render(write_still=True)
            manifest.append(dict(word=w["w"], ws=w["s"], we=w["e"], who=who, syl="".join(c for c, _ in letters), plan=shp,
                                 shown=shown, t=round(tm, 3), file=fn))
json.dump(manifest, open(os.path.join(outdir, "proof.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("PROOF DONE", len(manifest))
