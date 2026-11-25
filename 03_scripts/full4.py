"""full4.py - the whole DROPPER intro, 0 to 17.75 s (12 beats). Not run on its own: intro.py shot=full4 builds the scene
and runs this file in its own namespace (P, Y, co, cam, animate, place_lights, EMIT_NODES, RING_Z, RING_L, TGT, TGT3 ...).

    blender -b -P 03_scripts/intro.py -- <frames_dir>/f.png shot=full4 res=1280 samples=32 [f0=a f1=b] [only=a,b,c] [force=1]
run_full.ps1 renders it in chunks (a fresh Blender per chunk: one long session slows down and crashes).

Beats: 1 reveal over the shoulders, "14" rises, hidden cut behind a passing block; 2 two-shot, slow orbit, spawn eggs and the
hologram statues of the two creators; 3 slow push, small "14", 3liSY winds up; 4 the shout (push-in, slow motion, shake, flood);
5 orbit, YoCube1 points, name tag; 6 cube teleport, camera tips over and slides down, rings ignite, "16"; 7 he rebuilds on ring 2,
diamond, arrow; 8 teleport to ring 3, scoreboard counts up; 9 hidden cut back up; 10 "اوووو" close-up; 11 YoCube1 rebuilds on the
ledge laughing, comment bubbles; 12 both jump, the dive down the shaft, the splash. Hidden cuts sit behind a block passing the lens.
Camera: level (roll only on the shout), eased moves that overshoot a little and settle, never a straight-line glide."""
import random

from mathutils import Quaternion

T_END = 17.75
V = Vector
UPV = V((0, 0, 1))
PP = V((0.85, LY + 0.25, 0.0))                                   # 3liSY on the ledge
YP = V((-0.85, LY, 0.0))                                         # YoCube1 on the ledge
TG, TG3 = V(TGT), V(TGT3)                                        # YoCube1's spots on rings 2 and 3
SCENE_ART = os.path.join(os.path.dirname(SCENE), "art")


def spot_axes(p):
    i = V((-p.x, -p.y, 0)).normalized()                          # toward the shaft's axis
    return i, i.cross(UPV).normalized()


INW, SIDE = spot_axes(TG)
INW3, SIDE3 = spot_axes(TG3)
CAM_END = TG - SIDE * 4.6 + INW * 3.4 + UPV * 1.5                # along the wall: it curves away behind him, soft
CAM_LOOK = TG + SIDE * 0.4 + UPV * 1.15
CAM3 = TG3 - SIDE3 * 4.8 + INW3 * 3.8 + UPV * 1.55
CAM3_LOOK = TG3 + SIDE3 * 0.8 + INW3 * 0.6 + UPV * 1.3


def yaw_to(a, b):
    d = (b - a).normalized()
    return math.degrees(math.atan2(d.x, -d.y))


TG_YAW = yaw_to(TG, CAM_END) - 15                                # facing the lens, turned a little to his right
TG3_YAW = yaw_to(TG3, CAM3) - 15
DIA_P = TG + INW * 1.0 + SIDE * 1.15 + UPV * 1.15                # the floating diamond beside him
BOARD_P = TG3 + INW3 * 1.3 + SIDE3 * 2.0 + UPV * 1.55            # the scoreboard beside him
STAT_F = V((-12.5, 17.0, -10.0))                                 # the hologram statues, across the shaft
STAT_M = V((12.5, 17.0, -10.0))
STAT_S = 8.0

POSES.update({
    "present_r": {"aR": (-0.85, -0.55, 0.15), "aL": (0.25, -0.3, -1), "elbowR": (-8, 0, 0), "elbowL": (-35, 0, 0), "hip": (4, 0, -10),
                  "legR": (-8, -3, 0), "kneeR": (10, 0, 0), "legL": (8, 4, 0), "head": (-2, 0, -14)},
    "throw_r0": {"aR": (-0.5, 0.45, 0.8), "aL": (0.5, -0.5, -0.6), "elbowR": (-95, 0, 0), "elbowL": (-40, 0, 0), "hip": (-6, 0, -14),
                 "legR": (8, -4, 0), "legL": (-8, 4, 0), "kneeL": (12, 0, 0), "head": (-4, 0, -8)},
    "throw_r1": {"aR": (-0.8, -0.6, 0.3), "aL": (0.35, 0.1, -0.9), "elbowR": (-8, 0, 0), "elbowL": (-30, 0, 0), "hip": (10, 0, 12),
                 "legR": (-10, -4, 0), "legL": (10, 4, 0), "kneeR": (12, 0, 0), "head": (-6, 0, -18)},
    "throw_l0": {"aL": (0.5, 0.45, 0.8), "aR": (-0.5, -0.5, -0.6), "elbowL": (-95, 0, 0), "elbowR": (-40, 0, 0), "hip": (-6, 0, 14),
                 "legL": (8, 4, 0), "legR": (-8, -4, 0), "kneeR": (12, 0, 0), "head": (-4, 0, 8)},
    "throw_l1": {"aL": (0.8, -0.6, 0.3), "aR": (-0.35, 0.1, -0.9), "elbowL": (-8, 0, 0), "elbowR": (-30, 0, 0), "hip": (10, 0, -12),
                 "legL": (-10, 4, 0), "legR": (10, -4, 0), "kneeL": (12, 0, 0), "head": (-6, 0, 18)},
    "wince": {"aR": (-0.8, -0.55, 0.05), "aL": (0.8, -0.55, 0.05), "elbowR": (-110, 0, 0), "elbowL": (-110, 0, 0), "hip": (-7, 0, 0),
              "legR": (8, -4, 0), "legL": (-6, 4, 0), "kneeL": (10, 0, 0), "head": (-6, 0, 0)},
    "slump": {"aR": (-0.1, -0.35, -1), "aL": (0.1, -0.35, -1), "elbowR": (-14, 0, 0), "elbowL": (-14, 0, 0), "hip": (15, 0, 0),
              "legR": (-12, -3, 0), "kneeR": (18, 0, 0), "legL": (-10, 3, 0), "kneeL": (16, 0, 0), "head": (16, 0, 6)},
    "laugh": {"aR": (-0.3, -0.75, -0.65), "aL": (0.3, -0.75, -0.65), "elbowR": (-75, 0, 0), "elbowL": (-75, 0, 0), "hip": (13, 0, 8),
              "legR": (-12, -3, 0), "kneeR": (14, 0, 0), "legL": (-8, 3, 0), "head": (-14, 0, 14)},
    "skydive": {"aR": (-1, 0.1, 0.45), "aL": (1, 0.1, 0.45), "elbowR": (-25, 0, 0), "elbowL": (-25, 0, 0), "hip": (-6, 0, 0),
                "legR": (6, -14, 0), "kneeR": (18, 0, 0), "legL": (6, 14, 0), "kneeL": (18, 0, 0), "head": (-22, 0, 0)},
})


# ---------------------------------------------------------------- time
def warp(t):
    """slow motion on the held "aaaa" of the shout: 0.3x for half a second, then a quick catch-up"""
    if t < 6.25:
        return t
    if t < 6.75:
        return 6.25 + 0.3 * (t - 6.25)
    if t < 7.10:
        return 6.40 + 2.0 * (t - 6.75)
    return t


def settle(u, a=0.03):
    """ease in and out to a small overshoot, then settle back (a camera operator's landing)"""
    u = clamp01(u)
    if u < 0.82:
        return (1 + a) * ease(u / 0.82)
    return 1 + a - a * ease((u - 0.82) / 0.18)


def accel(u):
    u = clamp01(u)
    return settle(u ** 1.35, 0.025)


def drop(u):
    """the dive: gathers speed all the way down"""
    u = clamp01(u)
    return u ** 2.4


# ---------------------------------------------------------------- camera keys: (time, position, look-at, lens, roll, ease, pivot)
PIV = PP + V((-0.85, 0.0, 0))
TALK = (PP + V((-0.50, -5.85, 1.45)), PP + V((-0.85, 0.0, 1.08)))
CAMK = [
    # 1 reveal: behind and above their shoulders, a slow push forward over the edge
    (0.00, V((0.3, LY - 2.15, 4.0)), V((0.0, LY + 14.25, -16.0)), 28, 0.0, None, None),
    (1.93, V((0.25, LY - 1.3, 4.05)), V((0.0, LY + 15.0, -13.0)), 28, 0.0, settle, None),
    # hidden cut behind a passing block -> 2: two-shot, slow orbit
    (1.935, PIV + V((0.15, -5.85, 1.45)), TALK[1], 45, 0.0, ease, None),
    (4.89, PIV + V((-0.20, -5.55, 1.47)), PP + V((-0.85, 0.0, 1.12)), 46, 0.0, ease, None),
    # 3 a slow push in
    (6.10, PP + V((-1.25, -5.05, 1.48)), PP + V((-0.80, 0.0, 1.20)), 50, 0.0, ease, None),
    # 4 the shout
    (6.24, PP + V((0.42, -2.55, 1.60)), PP + V((0.0, 0.0, 1.95)), 50, 4.0, settle, None),
    (6.95, PP + V((0.36, -2.30, 1.62)), PP + V((0.0, 0.0, 1.97)), 50, 4.0, ease, None),
    (7.70, PP + V((-0.55, -5.95, 1.62)), PP + V((-0.85, 0.0, 1.30)), 43, 0.0, settle, None),
    # 5 orbit
    (9.20, PP + V((1.35, -5.65, 1.66)), PP + V((-0.85, 0.0, 1.32)), 45, 0.0, ease, PIV),
    # 6 rises past the tip, tips down, slides down the Dropper
    (9.62, PP + V((0.75, 2.30, 3.60)), PP + V((-1.70, 9.50, -6.50)), 38, 0.0, ease, None),
    (10.55, CAM_END, CAM_LOOK, 38, 0.0, accel, None),
    # 7 slow push beside him
    (12.05, CAM_END + (CAM_LOOK - CAM_END) * 0.14, CAM_LOOK, 40, 0.0, ease, None),
    # 8 slides on to ring 3, slow push
    (12.75, CAM3, CAM3_LOOK, 38, 0.0, settle, None),
    (14.25, CAM3 + (CAM3_LOOK - CAM3) * 0.12, CAM3_LOOK, 40, 0.0, ease, None),
    # 9 whooshes upward; hidden cut -> 10: close on 3liSY
    (14.42, CAM3 + V((0, 0, 7.0)), CAM3_LOOK + V((0, 0, 10.0)), 40, 0.0, ease, None),
    (14.425, PP + V((0.34, -2.35, 1.62)), PP + V((0.0, 0.0, 1.82)), 55, 0.0, ease, None),
    (15.08, PP + V((0.28, -2.05, 1.63)), PP + V((0.0, 0.0, 1.84)), 55, 0.0, ease, None),
    # 11 glides out, orbit
    (15.62, PP + V((-0.25, -5.85, 1.55)), PP + V((-0.85, 0.0, 1.22)), 45, 0.0, settle, None),
    (16.25, PP + V((-1.05, -5.75, 1.56)), PP + V((-0.85, 0.0, 1.22)), 45, 0.0, ease, PIV),
    # 12 over their shoulders, looking out over their heads, tips over the edge, the dive
    (16.62, PP + V((-0.85, -2.7, 3.3)), V((0.0, LY + 14.0, -1.5)), 34, 0.0, ease, None),
    (16.85, V((0.3, LY + 3.4, 3.9)), V((0.1, LY + 8.0, -22.0)), 30, 0.0, ease, None),
    (17.62, V((0.0, -3.0, -158.0)), V((0.0, -1.5, -200.0)), 24, 0.0, drop, None),
    (17.75, V((0.0, -2.6, -160.6)), V((0.0, -1.5, -200.0)), 24, 0.0, ease, None),
]


def cam_at(t):
    w = warp(t)
    k = CAMK
    if w <= k[0][0]:
        a = b = k[0]
        s = 0.0
    else:
        i = max(j for j in range(len(k) - 1) if k[j][0] <= w) if w < k[-1][0] else len(k) - 2
        a, b = k[i], k[i + 1]
        s = (b[5] or ease)((w - a[0]) / (b[0] - a[0]))
    if b[6] is not None:                                         # orbit: angle and radius round a pivot
        pv = b[6]
        va, vb = a[1] - pv, b[1] - pv
        ang_a, ang_b = math.atan2(va.y, va.x), math.atan2(vb.y, vb.x)
        rr = va.xy.length + (vb.xy.length - va.xy.length) * s
        an = ang_a + (ang_b - ang_a) * s
        pos = V((pv.x + rr * math.cos(an), pv.y + rr * math.sin(an), a[1].z + (b[1].z - a[1].z) * s))
    else:
        pos = a[1].lerp(b[1], s)
    look = a[2].lerp(b[2], s)
    lens = a[3] + (b[3] - a[3]) * s
    roll = a[4] + (b[4] - a[4]) * s
    sh = 0.0 if w < 6.12 else 0.035 * math.exp(-(w - 6.12) / 0.10)                    # the shout's small shake
    look = look + V((sh * math.sin(97 * w), 0.0, sh * math.sin(131 * w + 1.0)))
    look = look + V((0.006 * math.sin(1.3 * t), 0.0, 0.005 * math.sin(1.7 * t + 2)))  # a living hand, never a dead tripod
    return pos, look, lens, roll


# ---------------------------------------------------------------- the light: talking dark, flood on the shout, the cascade, the dive
def flood(t):
    shout = ease((t - 6.10) / 0.4) * (1 - ease((t - 7.6) / 1.1))
    cascade = ease((t - 9.35) / 0.6) * (1 - 0.72 * ease((t - 10.55) / 0.6)) * (1 - ease((t - 14.3) / 0.15))
    dive = ease((t - 16.6) / 0.35)
    return clamp01(shout + cascade + dive)


RING_T = [9.62 + 1.05 * math.sqrt(k / 15.0) for k in range(LV)]   # ignitions, top to bottom, faster and faster
POOL_N = emit_node(bpy.data.materials["pool"], 4.0)


def set_glow(t):
    f = flood(t)
    deep = 1 + 5 * ease((t - 16.7) / 0.3)                         # the rainbow rush: even the deep wall burns
    near = ease((t - 17.05) / 0.4)                                # near the water its light dims: water, not a white-out
    bpy.data.lights["pool"].energy = 40000 * (1 - 0.985 * near)
    POOL_N.inputs[1].default_value = 4.0 - 3.0 * near
    for node, base in EMIT_NODES["w"]:
        node.inputs[1].default_value = base * (1 + 3.3 * f) * deep
    for node, base in EMIT_NODES["r"]:
        node.inputs[1].default_value = base * (1 + 2.1 * f) * deep
    for k in range(LV):
        node, base = EMIT_NODES["dia"][k]
        lit = 0.0
        if t >= RING_T[k]:
            lit = 1.2 * ease((t - RING_T[k]) / 0.15) + 3.0 * math.exp(-(t - RING_T[k]) / 0.22)
        if k == 1:
            lit += 1.5 * bump(t, 11.0, 0.6)                       # the highlight on his ring while he explains
        node.inputs[1].default_value = 1.6 + 2.6 * lit
        RING_L[k].data.energy = 1800 * (0.6 + 0.8 * lit)


# ---------------------------------------------------------------- effects: sparks, trails, glints (cube particles)
EGG_T = [(2.60, 2.92, STAT_F, 0), (3.52, 3.87, STAT_M, 1)]        # release, landing, target, which hand
EMIT = []   # (group, t0, origin, n, speed, life, gravity, size, spread, seed)
EMIT.append(("gold", 6.12, PP + V((0, 0.35, 1.9)), 44, 2.6, 1.0, -1.4, 0.022, "away", 1))   # behind him, away from the lens
EMIT.append(("white", 7.80, PP + V((0, 0, 2.55)), 18, 1.0, 0.5, 0.0, 0.025, "sphere", 2))
for k in range(LV):
    EMIT.append(("cyan", RING_T[k], V((0, 0, RING_Z[k] + 0.5)), 46, 1.6, 0.9, -0.8, 0.07, "ring", 10 + k))
    EMIT.append(("white", RING_T[k] + 0.05, V((0, 0, RING_Z[k] + 0.5)), 22, 0.4, 1.5, -0.5, 0.045, "ring", 50 + k))
EMIT.append(("white", 9.27, YP + V((-0.1, 0, 1.2)), 30, 1.8, 0.6, 0.0, 0.03, "sphere", 3))
EMIT.append(("white", 10.42, TG + V((0, 0, 1.1)), 34, 1.6, 0.6, 0.0, 0.03, "sphere", 4))
EMIT.append(("white", 11.50, DIA_P, 20, 0.9, 0.7, 0.0, 0.03, "star", 5))
EMIT.append(("white", 12.10, TG + V((0, 0, 1.1)), 30, 1.8, 0.6, 0.0, 0.03, "sphere", 6))
EMIT.append(("white", 12.60, TG3 + V((0, 0, 1.1)), 34, 1.6, 0.6, 0.0, 0.03, "sphere", 7))
EMIT.append(("white", 15.03, YP + V((0, 0, 1.1)), 34, 1.6, 0.6, 0.0, 0.03, "sphere", 8))
for t1_, pos_, n_ in ((2.92, STAT_F, 9), (3.87, STAT_M, 90)):     # the egg lands: a pop on the far pad
    EMIT.append(("cyan", t1_, pos_ + V((0, 0, 1.0)), 70, 7.0, 0.8, -3.0, 0.22, "sphere", n_))
    EMIT.append(("gold", t1_ + 0.04, pos_ + V((0, 0, 2.0)), 40, 5.0, 0.9, -2.0, 0.16, "sphere", n_ + 1))
EMIT.append(("cyan", 17.60, V((0, -2.5, -161.0)), 120, 9.0, 0.5, -14.0, 0.16, "up", 95))    # the splash
EMIT.append(("white", 17.60, V((0, -2.5, -161.0)), 50, 7.0, 0.5, -14.0, 0.09, "up", 96))
FXC = {"gold": (1.0, 0.72, 0.25), "cyan": (0.3, 0.95, 1.0), "white": (1.0, 0.97, 0.9)}


def fx_obj(name, col, strength):
    me = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b_ = m.node_tree.nodes["Principled BSDF"]
    b_.inputs["Base Color"].default_value = (*col, 1)
    b_.inputs["Emission Color"].default_value = (*col, 1)
    b_.inputs["Emission Strength"].default_value = strength
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


FXO = {g: fx_obj("fx_" + g, c, 12.0) for g, c in FXC.items()}


def fill(o, cubes):
    """cubes: [(centre, size)] -> the object's mesh (rebuilt every frame)"""
    bm = bmesh.new()
    for c, s in cubes:
        if s <= 0.002:
            continue
        r_ = bmesh.ops.create_cube(bm, size=s)
        bmesh.ops.translate(bm, vec=c, verts=r_["verts"])
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()


def particles(tw):
    out = {g: [] for g in FXO}
    for g, t0, org, n, sp, life, gz, size, spread, seed in EMIT:
        age = tw - t0
        if age < 0 or age > life:
            continue
        rr = random.Random(seed)
        for i in range(n):
            if spread == "ring":                                  # along the ring, flying inward and up
                a = rr.random() * 2 * math.pi
                p0 = org + V(((R - 1.2) * math.cos(a), (R - 1.2) * math.sin(a), 0))
                v = V((-math.cos(a), -math.sin(a), 0.3 + rr.random())) * sp * (0.5 + rr.random())
            elif spread == "star":                                # a glint: a cross of rays
                d = [V((1, 0, 0)), V((-1, 0, 0)), V((0, 0, 1)), V((0, 0, -1))][i % 4]
                p0, v = org, d * sp * (0.6 + 0.8 * (i // 4) / max(1, n // 4))
            else:
                v = V((rr.gauss(0, 1), rr.gauss(0, 1), rr.gauss(0, 1))).normalized() * sp * (0.4 + rr.random())
                p0 = org
                if spread == "away":                              # nothing flies between the lens and his face
                    v.y = abs(v.y) + 0.3 * sp
                elif spread == "up":                              # the splash jumps up round the lens
                    a = rr.random() * 2 * math.pi
                    rad = 0.6 + 2.6 * rr.random()
                    p0 = org + V((rad * math.cos(a), rad * math.sin(a), 0))
                    v = V((0.5 * math.cos(a), 0.5 * math.sin(a), 1.0 + rr.random())) * sp
            a_ = age * (0.7 + 0.6 * rr.random())
            p = p0 + v * a_ + V((0, 0, 0.5 * gz * a_ * a_))
            out[g].append((p, size * (1 - age / life) ** 0.7))
    for rel, land, tgt, hand in EGG_T:                            # the egg's sparkle trail
        for j in range(14):
            te = rel + (land - rel) * j / 14.0
            age = tw - te
            if 0 <= age < 0.45:
                out["gold"].append((egg_pos(te, rel, land, tgt), 0.09 * (1 - age / 0.45)))
    return out


# ---------------------------------------------------------------- spawn eggs
def egg_pos(t, rel, land, tgt):
    u = clamp01((t - rel) / (land - rel))
    p0 = YP + V((-0.1, 0, 2.1))
    p = p0.lerp(tgt + V((0, 0, 1.0)), u ** 0.75)
    return p + V((0, 0, 9.0 * math.sin(math.pi * u)))


def make_egg(name, c1, c2):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.13)
    o = bpy.context.active_object
    o.name = name
    o.scale = (1, 1, 1.28)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt_ = m.node_tree
    b_ = nt_.nodes["Principled BSDF"]
    vo = nt_.nodes.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 26
    cr = nt_.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.interpolation = "CONSTANT"
    cr.color_ramp.elements[0].color = (*c2, 1)
    cr.color_ramp.elements[1].position = 0.28
    cr.color_ramp.elements[1].color = (*c1, 1)
    nt_.links.new(vo.outputs["Distance"], cr.inputs["Fac"])
    nt_.links.new(cr.outputs["Color"], b_.inputs["Base Color"])
    nt_.links.new(cr.outputs["Color"], b_.inputs["Emission Color"])
    b_.inputs["Emission Strength"].default_value = 1.6
    o.data.materials.append(m)
    return o


EGGS = [make_egg("egg_f", (0.95, 0.85, 0.5), (0.8, 0.1, 0.08)), make_egg("egg_m", (0.3, 0.75, 0.95), (0.05, 0.1, 0.5))]


# ---------------------------------------------------------------- the hologram statues
def hologram(rig, tag, tint):
    """the skin as glowing see-through light; returns the opacity value nodes"""
    vals = []
    for nm in (tag, tag + "_o"):
        m = bpy.data.materials[nm]
        nt_ = m.node_tree
        tx = next(n for n in nt_.nodes if n.type == "TEX_IMAGE")
        for n in list(nt_.nodes):
            if n.type not in ("OUTPUT_MATERIAL", "TEX_IMAGE"):
                nt_.nodes.remove(n)
        mul = nt_.nodes.new("ShaderNodeMix")
        mul.data_type, mul.blend_type = "RGBA", "MIX"
        mul.inputs["Factor"].default_value = 0.72
        mul.inputs[7].default_value = (*tint, 1)
        nt_.links.new(tx.outputs["Color"], mul.inputs[6])
        em = nt_.nodes.new("ShaderNodeEmission")
        nt_.links.new(mul.outputs[2], em.inputs["Color"])
        gp = nt_.nodes.new("ShaderNodeNewGeometry")                # scan lines running up the figure
        sp = nt_.nodes.new("ShaderNodeSeparateXYZ")
        nt_.links.new(gp.outputs["Position"], sp.inputs[0])
        m1 = nt_.nodes.new("ShaderNodeMath")
        m1.operation = "MULTIPLY"
        m1.inputs[1].default_value = 4.0
        nt_.links.new(sp.outputs["Z"], m1.inputs[0])
        s1 = nt_.nodes.new("ShaderNodeMath")
        s1.operation = "SINE"
        nt_.links.new(m1.outputs[0], s1.inputs[0])
        m2 = nt_.nodes.new("ShaderNodeMath")
        m2.operation = "MULTIPLY_ADD"
        m2.inputs[1].default_value = 0.55
        m2.inputs[2].default_value = 1.25
        nt_.links.new(s1.outputs[0], m2.inputs[0])
        nt_.links.new(m2.outputs[0], em.inputs["Strength"])
        tr = nt_.nodes.new("ShaderNodeBsdfTransparent")
        val = nt_.nodes.new("ShaderNodeValue")
        val.outputs[0].default_value = 0.0
        am_ = nt_.nodes.new("ShaderNodeMath")
        am_.operation = "MULTIPLY"
        nt_.links.new(tx.outputs["Alpha"], am_.inputs[0])
        nt_.links.new(val.outputs[0], am_.inputs[1])
        mx = nt_.nodes.new("ShaderNodeMixShader")
        nt_.links.new(am_.outputs[0], mx.inputs[0])
        nt_.links.new(tr.outputs[0], mx.inputs[1])
        nt_.links.new(em.outputs[0], mx.inputs[2])
        nt_.links.new(mx.outputs[0], next(n for n in nt_.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
        m.surface_render_method = "DITHERED"
        vals.append(val)
    return vals


def statue(tag, skin, pos, tint):
    r_ = player(tag, os.path.join(SCENE, "creators", skin), {"elbowR": (-20, 0, 0), "elbowL": (-20, 0, 0)})
    r_["armR"].rotation_euler = arm_euler((-0.3, -0.1, -1))
    r_["armL"].rotation_euler = arm_euler((0.3, -0.1, -1))
    rot(r_["elbowR"], (-20, 0, 0))
    rot(r_["elbowL"], (-20, 0, 0))
    rot(r_["legR"], (0, -4, 0))
    rot(r_["legL"], (0, 4, 0))
    r_["base"].location = pos
    r_["base"].scale = (0.001, 0.001, 0.001)
    return r_, hologram(r_, tag, tint)


FIG = {"F": statue("F", "Fir4sGamer.png", STAT_F, (0.25, 0.85, 1.0)), "M": statue("M", "Mustafa_GO.png", STAT_M, (0.25, 0.85, 1.0))}


def tag_plane(name, path, width, emit=1.6):
    im = bpy.data.images.load(path, check_existing=True)
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object
    o.name = name
    w_, h_ = im.size
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n_ = m.node_tree
    for n in list(n_.nodes):
        if n.type != "OUTPUT_MATERIAL":
            n_.nodes.remove(n)
    tx = n_.nodes.new("ShaderNodeTexImage")
    tx.image = im
    em = n_.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = emit
    tr = n_.nodes.new("ShaderNodeBsdfTransparent")
    mx = n_.nodes.new("ShaderNodeMixShader")
    n_.links.new(tx.outputs["Color"], em.inputs["Color"])
    n_.links.new(tx.outputs["Alpha"], mx.inputs[0])
    n_.links.new(tr.outputs[0], mx.inputs[1])
    n_.links.new(em.outputs[0], mx.inputs[2])
    n_.links.new(mx.outputs[0], next(n for n in n_.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    o.data.materials.append(m)
    o.visible_shadow = False
    c = o.constraints.new("TRACK_TO")
    c.target, c.track_axis, c.up_axis = co, "TRACK_Z", "UP_Y"
    return o, width, width * h_ / w_, tx


TAGF = tag_plane("tag_f", os.path.join(SCENE_ART, "tag_fras.png"), 7.5)
TAGM = tag_plane("tag_m", os.path.join(SCENE_ART, "tag_mustafa.png"), 8.0)
TAGA = tag_plane("tag_ali", os.path.join(SCENE_ART, "tag_ali.png"), 0.95)
BUB1 = tag_plane("bub_noob", os.path.join(SCENE_ART, "bubble_noob.png"), 0.85, 1.4)
BUB2 = tag_plane("bub_3iqab", os.path.join(SCENE_ART, "bubble_3iqab.png"), 0.85, 1.4)
BOARD = tag_plane("board", os.path.join(SCENE_ART, "score_0.png"), 2.3, 1.3)
SCORES = [bpy.data.images.load(os.path.join(SCENE_ART, f"score_{i}.png"), check_existing=True) for i in range(8)]


def place(pl, pos, s):
    o, w_, h_, _ = pl
    o.location = pos
    o.scale = (max(1e-4, w_ * s), max(1e-4, h_ * s), 1)
    o.hide_render = s <= 0.001


# ---------------------------------------------------------------- the cube teleports
PIECE_COLS = {"black": (0.02, 0.02, 0.025), "red": (0.9, 0.08, 0.08), "orange": (1.0, 0.45, 0.05), "yellow": (1.0, 0.9, 0.1),
              "green": (0.1, 0.85, 0.2), "blue": (0.05, 0.25, 1.0), "white": (0.9, 0.9, 0.9)}
PCO = {c: fx_obj("yp_" + c, col, 2.5 if c != "black" else 0.0) for c, col in PIECE_COLS.items()}
PIECES = []
prng = random.Random(11)
for i in range(150):
    c = "black" if i < 60 else list(PIECE_COLS)[1 + i % 6]
    a0 = V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0)))
    a1 = V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0)))
    PIECES.append((c, a0, a1, prng.uniform(0.0, 0.22), prng.uniform(0.07, 0.12), prng.uniform(-1, 1)))
YL = YP + V((-0.1, 0, 0))
TELE = [(9.28, 10.45, YL, TG, V((0, 2.5, 1.5)), INW * 3.0 + V((0, 0, 2.5))),
        (12.10, 12.62, TG, TG3, INW * 1.5 + V((0, 0, 1.0)), INW3 * 2.0 + V((0, 0, 1.5))),
        (14.20, 15.05, TG3, YL, INW3 * 2.0 + V((0, 0, 2.0)), V((0, 3.0, -4.0)))]


def pieces(t):
    out = {c: [] for c in PCO}
    for tp0, tp1, src, dst, h0, h1 in TELE:
        if not (tp0 <= t <= tp1 + 0.02):
            continue
        for c, a0, a1, d, s, wob in PIECES:
            dd = d * (tp1 - tp0) / 1.17
            u = clamp01((t - tp0 - dd) / (tp1 - tp0 - 0.25 * (tp1 - tp0) / 1.17))
            p0, p3 = src + a0, dst + a1
            p1 = p0 + (a0 - V((0, 0, 1.0))).normalized() * 1.2 + h0
            p2 = p3 + h1 + SIDE * wob
            e = ease(u)
            q = (1 - e) ** 3 * p0 + 3 * (1 - e) ** 2 * e * p1 + 3 * (1 - e) * e * e * p2 + e ** 3 * p3
            out[c].append((q, s * (0.75 + 0.25 * abs(math.cos(math.pi * e)))))
    return out


def y_visible(t):
    return not any(a + 0.04 <= t < b for a, b, *_ in TELE)


# ---------------------------------------------------------------- props: diamond, arrows, block digits, the block that hides the cuts
def block_cube(name, tex, size, emit, texdir, tint=(1, 1, 1), uvs=1.0):
    me_ = bpy.data.meshes.new(name)
    bm_ = bmesh.new()
    uvl = bm_.loops.layers.uv.verify()
    bmesh.ops.create_cube(bm_, size=size)
    for f_ in bm_.faces:                                          # one whole texture per face (or uvs tiles of it)
        for lp, uv in zip(f_.loops, [(0, 0), (uvs, 0), (uvs, uvs), (0, uvs)]):
            lp[uvl].uv = uv
    bm_.to_mesh(me_)
    bm_.free()
    o = bpy.data.objects.new(name, me_)
    sc.collection.objects.link(o)
    o.data.materials.append(block_mat(name, tex, tint, emit=emit, rough=0.2, texdir=texdir))
    return o


DIAMOND = block_cube("diamond_prop", "diamond_block", 0.55, 2.2, TXE)
DIAMOND.location = DIA_P
WIPE = block_cube("wipe", "orange_wool", 2.6, 0.32, T121S, uvs=3.0)
WIPE.hide_render = True
WIPES = [(1.935, 0.13), (14.425, 0.13)]                           # (the hidden cut's time, how long the block takes to pass)


def make_arrow(name, pts):
    cu_ = bpy.data.curves.new(name, "CURVE")
    cu_.dimensions = "3D"
    spl = cu_.splines.new("BEZIER")
    spl.bezier_points.add(len(pts) - 1)
    for bp, p in zip(spl.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    cu_.bevel_depth = 0.028
    cu_.bevel_resolution = 3
    ob = bpy.data.objects.new(name, cu_)
    sc.collection.objects.link(ob)
    am = bpy.data.materials.new(name)
    am.use_nodes = True
    ab = am.node_tree.nodes["Principled BSDF"]
    ab.inputs["Base Color"].default_value = (1.0, 0.85, 0.3, 1)
    ab.inputs["Emission Color"].default_value = (1.0, 0.82, 0.3, 1)
    ab.inputs["Emission Strength"].default_value = 6.0
    cu_.materials.append(am)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.09, depth=0.2)
    hd = bpy.context.active_object
    hd.name = name + "_head"
    hd.data.materials.append(am)
    hd.location = pts[-1]
    hd.rotation_euler = (pts[-1] - pts[-2]).to_track_quat("Z", "Y").to_euler()
    return cu_, hd


ARW1 = make_arrow("arrow", [TG + INW * 0.75 + SIDE * 0.1 + UPV * 1.55, TG + INW * 0.95 + SIDE * 0.35 + UPV * 2.3,
                            DIA_P + UPV * 0.95 - SIDE * 0.1, DIA_P + UPV * 0.42])
ARW2 = make_arrow("arrow2", [TG3 + INW3 * 0.7 + SIDE3 * 0.15 + UPV * 1.6, TG3 + INW3 * 0.9 + SIDE3 * 0.7 + UPV * 2.15,
                             BOARD_P + UPV * 1.1 - SIDE3 * 0.8, BOARD_P + UPV * 0.72 - SIDE3 * 1.0])

DIGITS = {"1": [".#.", "##.", ".#.", ".#.", "###"], "6": ["###", "#..", "###", "#.#", "###"],
          "4": ["#.#", "#.#", "###", "..#", "..#"]}


def block_number(name, txt, px, emit):
    me_ = bpy.data.meshes.new(name)
    bm_ = bmesh.new()
    for di, ch in enumerate(txt):
        for ry, row in enumerate(DIGITS[ch]):
            for rx, cell in enumerate(row):
                if cell == "#":
                    r_ = bmesh.ops.create_cube(bm_, size=px)
                    bmesh.ops.translate(bm_, vec=((di * 4 + rx - 3.5) * px, 0, (2 - ry) * px), verts=r_["verts"])
    uvl = bm_.loops.layers.uv.verify()
    for f_ in bm_.faces:                                          # each block face shows the whole lantern texture
        for lp, uv in zip(f_.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            lp[uvl].uv = uv
    bm_.to_mesh(me_)
    bm_.free()
    o = bpy.data.objects.new(name, me_)
    sc.collection.objects.link(o)
    o.data.materials.append(block_mat(name, "sea_lantern", (0.75, 0.95, 1.0), emit=emit, texdir=T121))
    return o


N14 = block_number("n14", "14", 0.5, 1.6)
N14S = block_number("n14s", "14", 0.11, 1.8)
N16 = block_number("n16", "16", 0.36, 0.7)
N14S.location = V((0.0, LY + 0.3, 2.45))
N16.location = V((-0.85, LY + 8.0, -3.0))


def pop(t, t0, t1=99.0, d=0.22):
    """0 -> 1.12 -> 1 pop in at t0, shrink away at t1"""
    if t < t0:
        return 0.0
    u = (t - t0) / d
    s = 1.0 + 0.12 * math.sin(math.pi * min(u, 1.0)) if u < 1 else 1.0
    s *= ease(u * 1.6)
    return s * (1 - ease((t - t1) / 0.2))


# ---------------------------------------------------------------- the beats (body time = warped)
P4 = [(0.00, "peer"), (1.92, "peer"), (1.94, "listen"), (4.95, "listen"), (5.60, "lean_in"), (6.10, "lean_in"), (6.22, "shout"),
      (6.88, "shout"), (7.05, "noob_point"), (7.40, "noob_point"), (7.62, "idle"), (7.88, "recoil_shrug"), (8.32, "recoil_shrug"),
      (8.62, "scratch"), (9.30, "scratch"), (9.70, "peer"), (14.40, "peer"), (14.42, "idle"), (14.60, "wince"), (15.05, "wince"),
      (15.38, "slump"), (16.25, "slump"), (16.48, "lean_in"), (16.66, "shout"), (16.90, "skydive"), (18.0, "skydive")]
P4Y = [(0.00, 176.0), (1.92, 176.0), (1.94, -48.0), (4.90, -40.0), (6.10, -24.0), (6.25, -10.0), (6.86, -10.0), (7.06, -16.0),
       (7.45, -16.0), (7.95, -28.0), (9.30, -28.0), (9.80, 120.0), (14.40, 120.0), (14.42, -12.0), (16.25, -12.0), (16.50, 180.0),
       (18.0, 180.0)]
P4P = [(0.00, (PP.x, PP.y)), (16.50, (PP.x, PP.y)), (16.75, (PP.x, PP.y + 1.3)), (18.0, (PP.x, PP.y + 1.3))]
Y4 = [(0.00, "sweep"), (1.92, "sweep"), (1.94, "talk_open"), (2.45, "talk_open"), (2.56, "throw_r0"), (2.66, "throw_r1"),
      (2.98, "talk_open"), (3.38, "talk_open"), (3.48, "throw_l0"), (3.58, "throw_l1"), (3.92, "talk_open"), (6.16, "talk_open"),
      (6.32, "recoil"), (6.95, "recoil"), (7.22, "idle"), (7.40, "idle"), (7.64, "lean_point"), (8.22, "lean_point"),
      (8.48, "talk_open"), (9.25, "talk_open"), (10.45, "talk_open"), (10.90, "present_r"), (12.08, "present_r"), (12.62, "talk_open"),
      (13.00, "present_r"), (14.05, "present_r"), (14.20, "idle"), (15.03, "idle"), (15.16, "laugh"), (16.22, "laugh"),
      (16.48, "lean_in"), (16.66, "shout"), (16.90, "skydive"), (18.0, "skydive")]
Y4Y = [(0.00, 150.0), (1.92, 150.0), (1.94, 44.0), (6.00, 40.0), (6.30, 25.0), (7.20, 30.0), (7.62, 55.0), (8.24, 50.0), (8.55, 22.0),
       (9.25, 22.0), (10.40, 22.0), (10.41, TG_YAW), (10.9, TG_YAW - 8), (12.09, TG_YAW - 8), (12.60, TG_YAW - 8), (12.61, TG3_YAW),
       (13.0, TG3_YAW - 8), (15.02, TG3_YAW - 8), (15.03, 38.0), (16.25, 38.0), (16.50, 180.0), (18.0, 180.0)]
Y4P = [(0.00, (YP.x, YP.y, 0.0)), (6.17, (YP.x, YP.y, 0.0)), (6.42, (YP.x - 0.25, YP.y - 0.15, 0.0)),
       (7.25, (YP.x - 0.25, YP.y - 0.15, 0.0)), (7.70, (YL.x, YL.y, 0.0)), (10.39, (YL.x, YL.y, 0.0)), (10.40, (TG.x, TG.y, TG.z)),
       (12.59, (TG.x, TG.y, TG.z)), (12.60, (TG3.x, TG3.y, TG3.z)), (15.02, (TG3.x, TG3.y, TG3.z)), (15.03, (YL.x, YL.y, 0.0)),
       (16.50, (YL.x, YL.y, 0.0)), (16.75, (YL.x, YL.y + 1.3, 0.0)), (18.0, (YL.x, YL.y + 1.3, 0.0))]
SCORE_T = [12.75 + i * 0.17 for i in range(8)]                    # the race on the board
SHOUT_EYES = lambda t: t < 7.5 or 14.45 <= t <= 15.2             # noqa: E731
FOCUS = [(0.0, "far"), (1.5, "far"), (1.93, "Y"), (6.10, "Y"), (6.2, "P"), (7.3, "P"), (7.9, "mid"), (9.3, "mid"), (9.7, "far"),
         (10.3, "far"), (10.6, "Y"), (14.3, "Y"), (14.42, "P"), (15.1, "P"), (15.6, "mid"), (16.5, "mid"), (16.9, "far")]


def focus_at(t, hp, hy, pos, look):
    def tgt(k):
        return {"P": hp, "Y": hy, "mid": (hp + hy) / 2}.get(k, pos + (look - pos).normalized() * 40.0)
    a, b, s = keyed(FOCUS, t)
    return tgt(a).lerp(tgt(b), s)


def set_frame4(t):
    tw = warp(t)
    for rig in (P, Y):
        rig["base"].rotation_euler = (0, 0, 0)
    animate(P, "P", tw, P4, P4Y, P4P)
    animate(Y, "Y", tw, Y4, Y4Y, Y4P)
    if 15.14 <= t <= 16.22:                                       # the laugh shakes him
        rot(Y["hip"], (13 + 5 * math.sin(2 * math.pi * 5.0 * t), 0, 8))
        rot(Y["head"], (-14 + 6 * math.sin(2 * math.pi * 5.0 * t + 1), 0, 14))
    vis = y_visible(t)
    for o in Y["meshes"]:
        o.hide_render = not vis
    f = min(len(SHAPE_P) - 1, int(round(t * FPS)))
    shape = SHAPE_P[f]
    MOUTH_NODE.image = MOUTH[("hds" if SHOUT_EYES(t) else "hd", shape)]   # the mouth runs on the real clock
    upd()
    pos, look, lens, roll = cam_at(t)
    if t > 16.9:                                                  # they fall ahead of the lens, belly down
        for rig, off in ((P, V((1.1, 0.5, -6.5))), (Y, V((-1.3, 0.9, -8.0)))):
            rig["base"].location = pos + off
            rig["base"].rotation_euler = (math.radians(-75), 0, 0)
        upd()
    hp, hy = head_of(P), head_of(Y)
    co.location = pos
    q = (look - pos).to_track_quat("-Z", "Y")
    co.rotation_euler = (q @ Quaternion((0, 0, 1), math.radians(roll))).to_euler()
    cam.lens = lens
    focus = focus_at(tw, hp, hy, pos, look)
    cam.dof.focus_distance = max(0.5, (focus - pos).length)
    cam.dof.aperture_fstop = 5.6 if tw < 1.9 or 9.3 < tw < 10.4 or tw > 16.6 else 2.0
    near_y = 10.3 < tw < 14.3
    subj = (hy - V((0, 0, 0.3))) if near_y else ((hp + hy) / 2 - V((0, 0, 0.3)))   # the lights stay on them, wherever the focus is
    place_lights(pos, subj, hp, hy)
    set_glow(t)
    for nm in ("rimA", "rimB"):                                   # the rims edge the suits, they do not tint them
        LT[nm].data.energy = 1200.0
    for g, cubes in particles(tw).items():
        fill(FXO[g], cubes)
    for c, cubes in pieces(t).items():
        fill(PCO[c], cubes)
    # eggs and statues
    for (rel, land, tgt, hand), egg in zip(EGG_T, EGGS):
        on = rel <= t < land
        egg.hide_render = not on
        if on:
            egg.location = egg_pos(t, rel, land, tgt)
            egg.rotation_euler = (9 * t, 7 * t, 0)
    fade = 1 - ease((t - 6.12) / 0.5)                             # the holograms go out with the shout
    for key, land, pl in (("F", 2.92, TAGF), ("M", 3.87, TAGM)):
        rig, vals = FIG[key]
        s = STAT_S * ease((t - land) / 0.42) if t >= land and fade > 0 else 0.001
        rig["base"].scale = (s, s, s)
        for v in vals:
            v.outputs[0].default_value = 0.62 * fade
        for o in rig["meshes"]:
            o.hide_render = s <= 0.01 or fade <= 0.001
        place(pl, rig["base"].location + V((0, 0, 2 * STAT_S + 1.3)), pop(t, land + 0.3, 4.85))
    # numbers
    s14 = pop(t, 1.12, 1.95, 0.3)
    N14.scale = (s14, s14, s14)
    N14.location = V((0.1, LY + 9.0, -16 + 12.5 * ease((t - 1.12) / 0.45)))
    N14.rotation_euler = (math.radians(-25), 0, 0)
    ss = pop(t, 5.56, 6.02)
    N14S.scale = (ss, ss, ss)
    s6 = pop(t, 9.60, 10.55)
    N16.scale = (s6, s6, s6)
    # diamond, arrows, board
    s = pop(t, 10.62, 12.05)
    DIAMOND.scale = (s, s, s)
    DIAMOND.rotation_euler = (0.35, 0.25, 1.4 * t)
    DIAMOND.location = DIA_P + UPV * (0.06 * math.sin(2.4 * t))
    DIAMOND.hide_render = s <= 0.001
    ARW1[0].bevel_factor_end = ease((t - 10.95) / 0.45) if t < 12.05 else 0.0
    h1 = pop(t, 11.35, 12.02)
    ARW1[1].scale = (h1, h1, h1)
    ARW2[0].bevel_factor_end = ease((t - 13.05) / 0.4) if t < 14.2 else 0.0
    h2 = pop(t, 13.42, 14.15)
    ARW2[1].scale = (h2, h2, h2)
    place(BOARD, BOARD_P, pop(t, 12.68, 14.2))
    BOARD[3].image = SCORES[max(0, sum(1 for x in SCORE_T if t >= x) - 1)]
    # name tag, bubbles
    place(TAGA, hp + V((0, 0, 0.5)), pop(t, 7.78, 9.15))
    place(BUB1, hp + V((-0.62, 0, 0.42)), pop(t, 15.60, 16.30))
    place(BUB2, hp + V((0.72, 0, 0.30)), pop(t, 15.98, 16.30))
    # the block that hides the cuts: crosses the frame in front of the lens, covering it at the cut
    WIPE.hide_render = True
    for tc, d_ in WIPES:
        if abs(t - tc) <= d_ / 2 + 0.02:
            u = (t - tc) / (d_ / 2)
            rgt = (co.matrix_world.to_3x3() @ V((1, 0, 0))).normalized() if False else q @ V((1, 0, 0))
            WIPE.location = pos + (look - pos).normalized() * 1.4 + rgt * (-2.6 * u)
            WIPE.rotation_euler = co.rotation_euler
            WIPE.hide_render = False
            cam.dof.aperture_fstop = 22.0                         # the block stays sharp as it passes
    for nm, sp in (("dust", 0.22), ("sparkle", 0.35)):
        bpy.data.objects[nm].location.z = sp * tw - 1.5
    return shape


outdir = os.path.dirname(OUT)
os.makedirs(outdir, exist_ok=True)
NF = int(round(T_END * FPS))
f0, f1 = int(F("f0", 0)), int(F("f1", NF))
frames = [int(v) for v in OPT["only"].split(",")] if "only" in OPT else range(f0, min(f1, NF))
for fr in frames:
    path = os.path.join(outdir, "f_%04d.png" % fr)
    if os.path.exists(path) and OPT.get("force") != "1":
        continue
    t = fr / FPS
    shape = set_frame4(t)
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    if fr % 20 == 0:
        print("FRAME", fr, "t %.2f" % t, "mouth", shape, flush=True)
print("FULL4 DONE", len(frames))
