"""clip4.py - the V4 motion test (intro 6.0-12.0 s). Not run on its own: intro.py shot=clip4 builds the scene and runs this
file in its own namespace (P, Y, co, cam, animate, set_mouth, place_lights, EMIT_NODES, RING_Z, RING_L, TGT ... come from there).

    blender -b -P 03_scripts/intro.py -- <frames_dir>/f.png shot=clip4 res=1280 samples=32 [only=a,b,c] [force=1]

What happens:
  6.10 the shout: a fast push-in, half a second of slow motion (bodies, camera and sparks; the mouth stays on the real
       clock), a small shake, the colour floods back, a gold spark burst; "يا نووب" he points; the camera glides back out
       with a small overshoot and settles; then a slow orbit round the two, the Minecraft name tag "علي الفاشل" pops.
  9.25 YoCube1 bursts into coloured cube pieces; the camera rises, tips over the edge and slides down the Dropper while the
       rings ignite one by one (burst, sparkle trail), the "16" in glowing blocks hangs in the shaft; the pieces stream down
       and rebuild him on ring 2 beside a floating diamond; a glowing hand-drawn arrow draws itself to the diamond.
Camera: level (roll only on the shout), eased moves that overshoot a little and settle, never a straight-line glide."""
import random

T0, T1 = F("t0", 6.0), F("t1", 12.0)
V = Vector
UPV = V((0, 0, 1))
PP = V((0.85, LY + 0.25, 0.0))                                   # 3liSY on the ledge
YP = V((-0.85, LY, 0.0))                                         # YoCube1 on the ledge
TG = V(TGT)                                                      # YoCube1's spot on ring 2
INW = V((-TG.x, -TG.y, 0)).normalized()                          # from that spot toward the shaft's axis
SIDE = INW.cross(UPV).normalized()
CAM_END = TG - SIDE * 5.0 + INW * 3.3 + UPV * 1.5               # along the wall: the wall curves away behind him, soft
CAM_LOOK = TG + SIDE * 0.4 + UPV * 1.15
_cdir = (CAM_END - TG).normalized()
TG_YAW = math.degrees(math.atan2(_cdir.x, -_cdir.y)) - 15        # facing the lens, turned a little to his right (the diamond)
DIA_P = TG + INW * 1.0 + SIDE * 1.15 + UPV * 1.15                # the floating diamond beside him
POSES["present_r"] = {"aR": (-0.85, -0.55, 0.15), "aL": (0.25, -0.3, -1), "elbowR": (-8, 0, 0), "elbowL": (-35, 0, 0),
                      "hip": (4, 0, -10), "legR": (-8, -3, 0), "kneeR": (10, 0, 0), "legL": (8, 4, 0), "head": (-2, 0, -14)}


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
    """slow start, fast middle, soft landing with overshoot - the slide down the shaft"""
    u = clamp01(u)
    return settle(u ** 1.35, 0.025)


# ---------------------------------------------------------------- camera keys: (time, position, look-at, lens, roll, ease, pivot)
CAMK = [
    (6.00, PP + V((-0.50, -5.85, 1.45)), PP + V((-0.85, 0.0, 1.08)), 45, 0.0, None, None),
    (6.10, PP + V((-0.52, -5.80, 1.45)), PP + V((-0.85, 0.0, 1.08)), 45, 0.0, ease, None),
    (6.24, PP + V((0.42, -2.55, 1.60)), PP + V((0.0, 0.0, 1.95)), 50, 4.0, settle, None),       # fast push-in to the shout
    (6.95, PP + V((0.36, -2.30, 1.62)), PP + V((0.0, 0.0, 1.97)), 50, 4.0, ease, None),         # drifting in (slow-mo)
    (7.70, PP + V((-0.55, -5.95, 1.62)), PP + V((-0.85, 0.0, 1.30)), 43, 0.0, settle, None),    # glides back out, headroom
    (9.20, PP + V((1.35, -5.65, 1.66)), PP + V((-0.85, 0.0, 1.32)), 45, 0.0, ease, PP + V((-0.85, 0.0, 0))),  # orbit
    (9.62, PP + V((0.75, 2.30, 3.60)), PP + V((-1.70, 9.50, -6.50)), 38, 0.0, ease, None),      # rises past the tip, tips down
    (10.55, CAM_END, CAM_LOOK, 38, 0.0, accel, None),                                           # slides down the Dropper
    (12.00, CAM_END + (CAM_LOOK - CAM_END) * 0.12, CAM_LOOK, 40, 0.0, ease, None),              # slow push
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


# ---------------------------------------------------------------- the light: talking dark, flood on the shout and the cascade
def flood(t):
    return clamp01(ease((t - 6.10) / 0.4) * (1 - ease((t - 7.6) / 1.1)) + ease((t - 9.35) / 0.6))


RING_T = [9.62 + 1.05 * math.sqrt(k / 15.0) for k in range(LV)]   # ignitions, top to bottom, faster and faster


def set_glow(t):
    f = flood(t)
    for node, base in EMIT_NODES["w"]:
        node.inputs[1].default_value = base * (1 + 3.3 * f)
    for node, base in EMIT_NODES["r"]:
        node.inputs[1].default_value = base * (1 + 2.1 * f)
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
rng = random.Random(7)
EMIT = []   # (group, t0, origin, n, speed, life, gravity, size, spread, seed)
EMIT.append(("gold", 6.12, PP + V((0, 0.35, 1.9)), 44, 2.6, 1.0, -1.4, 0.022, "away", 1))   # behind him, away from the lens
EMIT.append(("white", 7.80, PP + V((0, 0, 2.55)), 18, 1.0, 0.5, 0.0, 0.025, "sphere", 2))
for k in range(LV):
    EMIT.append(("cyan", RING_T[k], V((0, 0, RING_Z[k] + 0.5)), 46, 1.6, 0.9, -0.8, 0.07, "ring", 10 + k))
    EMIT.append(("white", RING_T[k] + 0.05, V((0, 0, RING_Z[k] + 0.5)), 22, 0.4, 1.5, -0.5, 0.045, "ring", 50 + k))
EMIT.append(("white", 9.27, YP + V((0, 0, 1.2)), 30, 1.8, 0.6, 0.0, 0.03, "sphere", 3))
EMIT.append(("white", 10.42, TG + V((0, 0, 1.1)), 34, 1.6, 0.6, 0.0, 0.03, "sphere", 4))
EMIT.append(("white", 11.50, DIA_P, 20, 0.9, 0.7, 0.0, 0.03, "star", 5))
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
            a_ = age * (0.7 + 0.6 * rr.random())
            p = p0 + v * a_ + V((0, 0, 0.5 * gz * a_ * a_))
            out[g].append((p, size * (1 - age / life) ** 0.7))
    return out


# ---------------------------------------------------------------- YoCube1's teleport: coloured cube pieces
PIECE_COLS = {"black": (0.02, 0.02, 0.025), "red": (0.9, 0.08, 0.08), "orange": (1.0, 0.45, 0.05), "yellow": (1.0, 0.9, 0.1),
              "green": (0.1, 0.85, 0.2), "blue": (0.05, 0.25, 1.0), "white": (0.9, 0.9, 0.9)}
PCO = {c: fx_obj("yp_" + c, col, 2.5 if c != "black" else 0.0) for c, col in PIECE_COLS.items()}
PIECES = []
prng = random.Random(11)
for i in range(150):
    c = "black" if i < 60 else list(PIECE_COLS)[1 + i % 6]
    a0 = V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0)))   # body offsets at the start
    a1 = V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0)))   # and at the end
    PIECES.append((c, a0, a1, prng.uniform(0.0, 0.22), prng.uniform(0.07, 0.12), prng.uniform(-1, 1)))
TP0, TP1 = 9.28, 10.45                                            # dissolve starts, rebuilt


def pieces(t):
    out = {c: [] for c in PCO}
    if not (TP0 <= t <= TP1 + 0.02):
        return out
    for c, a0, a1, d, s, wob in PIECES:
        u = clamp01((t - TP0 - d) / (TP1 - TP0 - 0.25))
        p0, p3 = YP + a0, TG + a1
        p1 = p0 + (a0 - V((0, 0, 1.0))).normalized() * 1.2 + V((0, 2.5, 1.5))     # burst out and over the edge
        p2 = p3 + INW * 3.0 + V((0, 0, 2.5)) + SIDE * wob                         # sweep in from the shaft
        e = ease(u)
        q = (1 - e) ** 3 * p0 + 3 * (1 - e) ** 2 * e * p1 + 3 * (1 - e) * e * e * p2 + e ** 3 * p3
        out[c].append((q, s * (0.75 + 0.25 * abs(math.cos(math.pi * e)))))
    return out


def y_visible(t):
    return not (TP0 + 0.04 <= t < TP1)


# ---------------------------------------------------------------- props: the floating diamond, the arrow, the "16", the name tag
def block_cube(name, tex, size, emit, texdir):
    me_ = bpy.data.meshes.new(name)
    bm_ = bmesh.new()
    uvl = bm_.loops.layers.uv.verify()
    bmesh.ops.create_cube(bm_, size=size)
    for f_ in bm_.faces:                                          # one whole texture per face
        for lp, uv in zip(f_.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            lp[uvl].uv = uv
    bm_.to_mesh(me_)
    bm_.free()
    o = bpy.data.objects.new(name, me_)
    sc.collection.objects.link(o)
    o.data.materials.append(block_mat(name, tex, emit=emit, rough=0.2, texdir=texdir))
    return o


DIAMOND = block_cube("diamond_prop", "diamond_block", 0.55, 2.2, TXE)
DIAMOND.location = DIA_P

pts = [TG + INW * 0.75 + SIDE * 0.1 + UPV * 1.55, TG + INW * 0.95 + SIDE * 0.35 + UPV * 2.3,
       DIA_P + UPV * 0.95 - SIDE * 0.1, DIA_P + UPV * 0.42]          # from above his pointing hand, arcing down onto the diamond
cu = bpy.data.curves.new("arrow", "CURVE")
cu.dimensions = "3D"
spl = cu.splines.new("BEZIER")
spl.bezier_points.add(len(pts) - 1)
for bp, p in zip(spl.bezier_points, pts):
    bp.co = p
    bp.handle_left_type = bp.handle_right_type = "AUTO"
cu.bevel_depth = 0.028
cu.bevel_resolution = 3
ARROW = bpy.data.objects.new("arrow", cu)
sc.collection.objects.link(ARROW)
am = bpy.data.materials.new("arrow")
am.use_nodes = True
ab = am.node_tree.nodes["Principled BSDF"]
ab.inputs["Base Color"].default_value = (1.0, 0.85, 0.3, 1)
ab.inputs["Emission Color"].default_value = (1.0, 0.82, 0.3, 1)
ab.inputs["Emission Strength"].default_value = 8.0
cu.materials.append(am)
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.09, depth=0.2)
HEAD = bpy.context.active_object
HEAD.name = "arrow_head"
HEAD.data.materials.append(am)
HEAD.location = pts[-1]
HEAD.rotation_euler = (pts[-1] - pts[-2]).to_track_quat("Z", "Y").to_euler()

DIGITS = {"1": [".#.", "##.", ".#.", ".#.", "###"], "6": ["###", "#..", "###", "#.#", "###"]}
me16 = bpy.data.meshes.new("sixteen")
bm = bmesh.new()
for di, ch in enumerate("16"):
    for ry, row in enumerate(DIGITS[ch]):
        for rx, cell in enumerate(row):
            if cell == "#":
                r_ = bmesh.ops.create_cube(bm, size=0.5)
                bmesh.ops.translate(bm, vec=((di * 4 + rx) * 0.5 - 1.75, 0, (4 - ry) * 0.5 - 1.0), verts=r_["verts"])
uvl16 = bm.loops.layers.uv.verify()
for f_ in bm.faces:                                               # each block face shows the whole lantern texture
    for lp, uv in zip(f_.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        lp[uvl16].uv = uv
bm.to_mesh(me16)
bm.free()
SIX = bpy.data.objects.new("sixteen", me16)
sc.collection.objects.link(SIX)
SIX.data.materials.append(block_mat("sixteen", "sea_lantern", (0.75, 0.95, 1.0), emit=1.6, texdir=T121))
SIX.location = V((-0.85, LY + 8.0, -4.0))

tim = bpy.data.images.load(os.path.join(os.path.dirname(SCENE), "art", "tag_ali.png"), check_existing=True)
bpy.ops.mesh.primitive_plane_add(size=1)
TAG = bpy.context.active_object
TAG.name = "tag_ali"
tw_, th_ = tim.size
TAG_W = 0.95
TAG.scale = (TAG_W, TAG_W * th_ / tw_, 1)
tmat = bpy.data.materials.new("tag_ali")
tmat.use_nodes = True
tn = tmat.node_tree
for n in list(tn.nodes):
    if n.type != "OUTPUT_MATERIAL":
        tn.nodes.remove(n)
ttx = tn.nodes.new("ShaderNodeTexImage")
ttx.image = tim
tem = tn.nodes.new("ShaderNodeEmission")
tem.inputs["Strength"].default_value = 1.6
ttr = tn.nodes.new("ShaderNodeBsdfTransparent")
tmx = tn.nodes.new("ShaderNodeMixShader")
tn.links.new(ttx.outputs["Color"], tem.inputs["Color"])
tn.links.new(ttx.outputs["Alpha"], tmx.inputs[0])
tn.links.new(ttr.outputs[0], tmx.inputs[1])
tn.links.new(tem.outputs[0], tmx.inputs[2])
tn.links.new(tmx.outputs[0], next(n for n in tn.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
TAG.data.materials.append(tmat)
TAG.visible_shadow = False
trk = TAG.constraints.new("TRACK_TO")
trk.target, trk.track_axis, trk.up_axis = co, "TRACK_Z", "UP_Y"


def pop(t, t0, t1=99.0, d=0.22):
    """0 -> 1.12 -> 1 pop in at t0, shrink away at t1"""
    if t < t0:
        return 0.0
    u = (t - t0) / d
    s = 1.0 + 0.12 * math.sin(math.pi * min(u, 1.0)) if u < 1 else 1.0
    s *= ease(u * 1.6)
    return s * (1 - ease((t - t1) / 0.2))


# ---------------------------------------------------------------- the beats (body time = warped)
P4 = [(6.00, "lean_in"), (6.10, "lean_in"), (6.22, "shout"), (6.88, "shout"), (7.05, "noob_point"), (7.40, "noob_point"),
      (7.62, "idle"), (7.88, "recoil_shrug"), (8.32, "recoil_shrug"), (8.62, "scratch"), (9.30, "scratch"), (9.70, "peer")]
P4Y = [(6.00, -30.0), (6.10, -24.0), (6.25, -10.0), (6.86, -10.0), (7.06, -16.0), (7.45, -16.0), (7.95, -28.0), (9.30, -28.0),
       (9.80, 120.0)]
P4P = [(6.00, (PP.x, PP.y)), (12.0, (PP.x, PP.y))]
Y4 = [(6.00, "talk_open"), (6.16, "talk_open"), (6.32, "recoil"), (6.95, "recoil"), (7.22, "idle"), (7.40, "idle"),
      (7.64, "lean_point"), (8.22, "lean_point"), (8.48, "talk_open"), (9.25, "talk_open"), (10.45, "talk_open"),
      (10.90, "present_r"), (12.0, "present_r")]
Y4Y = [(6.00, 44.0), (6.30, 25.0), (7.20, 30.0), (7.62, 55.0), (8.24, 50.0), (8.55, 22.0), (9.25, 22.0), (10.40, 22.0),
       (10.41, TG_YAW), (10.9, TG_YAW - 8), (12.0, TG_YAW - 8)]
Y4P = [(6.00, (YP.x, YP.y, 0.0)), (6.17, (YP.x, YP.y, 0.0)), (6.42, (YP.x - 0.25, YP.y - 0.15, 0.0)),
       (7.25, (YP.x - 0.25, YP.y - 0.15, 0.0)), (7.70, (YP.x - 0.1, YP.y, 0.0)), (10.39, (YP.x - 0.1, YP.y, 0.0)),
       (10.40, (TG.x, TG.y, TG.z)), (12.0, (TG.x, TG.y, TG.z))]


def set_frame4(t):
    tw = warp(t)
    animate(P, "P", tw, P4, P4Y, P4P)
    animate(Y, "Y", tw, Y4, Y4Y, Y4P)
    vis = y_visible(t)
    for o in Y["meshes"]:
        o.hide_render = not vis
    shape = set_mouth(t)                                          # the mouth runs on the real clock
    upd()
    hp, hy = head_of(P), head_of(Y)
    pos, look, lens, roll = cam_at(t)
    co.location = pos
    q = (look - pos).to_track_quat("-Z", "Y")
    from mathutils import Quaternion
    co.rotation_euler = (q @ Quaternion((0, 0, 1), math.radians(roll))).to_euler()
    cam.lens = lens
    if tw < 7.3:
        focus = hp
    elif tw < 9.3:
        focus = hp.lerp((hp + hy) / 2, ease((tw - 7.3) / 0.6))
    else:
        focus = (TG + UPV * 1.6) if tw > 9.9 else look
    cam.dof.focus_distance = max(0.5, (focus - pos).length)
    cam.dof.aperture_fstop = 2.0 if tw < 9.3 or tw > 10.4 else 4.0
    subj = (hy - V((0, 0, 0.3))) if tw > 10.3 else (focus - V((0, 0, 0.3)))
    place_lights(pos, subj, hp, hy)
    set_glow(t)
    for g, cubes in particles(tw).items():
        fill(FXO[g], cubes)
    for c, cubes in pieces(t).items():
        fill(PCO[c], cubes)
    s = pop(t, 10.62)                                             # the diamond appears, spins and bobs
    DIAMOND.scale = (s, s, s)
    DIAMOND.rotation_euler = (0.35, 0.25, 1.4 * t)
    DIAMOND.location = DIA_P + UPV * (0.06 * math.sin(2.4 * t))
    cu.bevel_factor_end = ease((t - 10.95) / 0.45)                # the arrow draws itself
    hs = pop(t, 11.35)
    HEAD.scale = (hs, hs, hs)
    s6 = pop(t, 9.60, 10.55)                                      # "16"
    SIX.scale = (s6, s6, s6)
    TAG.location = hp + V((0, 0, 0.5))                            # the name tag rides above 3liSY
    st = pop(t, 7.78, 9.15)
    TAG.scale = (TAG_W * st, TAG_W * th_ / tw_ * st, 1)
    for nm, sp in (("dust", 0.22), ("sparkle", 0.35)):
        bpy.data.objects[nm].location.z = sp * (tw - T0)
    return shape


outdir = os.path.dirname(OUT)
os.makedirs(outdir, exist_ok=True)
NF = int(round((T1 - T0) * FPS))
frames = [int(v) for v in OPT["only"].split(",")] if "only" in OPT else range(NF)
for fr in frames:
    path = os.path.join(outdir, "f_%04d.png" % fr)
    if os.path.exists(path) and OPT.get("force") != "1":
        continue
    t = T0 + fr / FPS
    shape = set_frame4(t)
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    if fr % 20 == 0:
        print("FRAME", fr, "t %.2f" % t, "mouth", shape, flush=True)
print("CLIP4 DONE", len(frames))
