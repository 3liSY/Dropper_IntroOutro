"""full5.py - the whole DROPPER intro, v5, 0 to 17.75 s. Not run on its own: intro.py shot=full5 builds
the scene and runs this file in its own namespace (P, Y, co, cam, place_lights, EMIT_NODES, RING_Z, RING_L, LT, PLAT_Z ...).

    blender -b -P 03_scripts/intro.py -- <frames_dir>/f.png shot=full5 res=1280 samples=32 [f0=a f1=b] [only=a,b,c] [force=1]
run_full5.ps1 renders it in chunks (a fresh Blender per chunk: one long session slows down and crashes).

Voice timing is fixed. Body time = warp(t): the slow motion and the hit freeze fit inside their beats and catch back up; the mouths,
the camera and the sparks of the hit run on the real clock. The punch lands on the spoken word نووب at 7.01 s."""
import json
import random

from mathutils import Matrix, Quaternion

T_END = 17.75
FREEZE_F = 1058                                                  # the last frames hold this one (post5.py repeats it)
V = Vector
DIVE = OPT.get("dive", "M")
if DIVE == "old":
    DIVE = ""
ENDING = OPT.get("ending", "comments")                            # Stage B 2026-11-21: "comments" = no dive; they stay on the ledge, post5.py lays the comment section over 16.3-17.75; "dive" = v6
if ENDING == "comments":
    DIVE = "none"
T_CUT1, T_CUT2, T_WET = 16.90, 17.15, 17.30                      # mix dive: leap -> side fall -> top-down water hit; heads touch the water at T_WET
MIX_CY = -2.5                                                     # mix dive, water hit: the lens's y over the pool
MIX_H, MIX_DY = 3.45, 0.33                                       # dive r2: the lens 3.1 above the bodies; bodies 0.25 ahead of it (0.55 cut the feet)
MIX_ZC = -161.0 + 0.67 + MIX_H                                    # the lens height at the touch: heads reach the pool top (z -161) at T_WET


def mix_dir(s):
    """mix dive, water hit: where the head points (s = +1 3liSY, -1 YoCube1): head first, a little in toward the other"""
    return V((-s * 0.25, -0.85, -0.8)).normalized()
ZW = -159.6                                                      # body middle at the water line (pool top is ZBOT - 1.5)
UPV = V((0, 0, 1))
ART = os.path.join(os.path.dirname(SCENE), "art")
PP = V((0.85, LY + 0.25, 0.0))                                   # 3liSY on the ledge
YP = V((-0.85, LY, 0.0))                                         # YoCube1 on the ledge
YL = V((-1.05, LY, 0.0))                                         # where he stands after climbing back
STAT_F = V((-2.95, -19.3, 0.0))   # v6 shot 2: closer in so all four fit a tighter lens                                 # the creators, a few steps behind on the same ledge
STAT_M = V((2.75, -19.6, 0.0))   # v6 shot 2: closer in, tags still inside the frame top
STAT_S = 1.3
WALLP = V((-4.70, -26.05, 0.0))                                  # YoCube1's spot on the alcove's left wall
PZ = float(PLAT_Z)                                               # the floating platform
YQ = V((-1.62, -9.3, PZ))
YQ2 = YQ                                                          # v6 shot 8: the pair stays put for the board (no hop, no walk)
PQ0 = V((1.62, -9.2, PZ))
PQ = PQ0
DIA_C = V((0.0, -8.5, PZ + 1.62))
BOARD_C = V((-0.1, -10.0, PZ + 1.75))                             # Stage B 2026-11-21: in FRONT of the pair, so no arm covers it (was -0.3, -7.4, 1.55 behind)
TAGU = 2.75 / 1121.0                                              # plate size: units per pixel of plate art
BSC = 0.46                                                         # Stage B 2026-11-21: nearer the camera, so it reads bigger (was 0.55 behind them)
BW = 3.5                                                         # scoreboard width

POSES.update({
    "present_r": {"aR": (-0.85, -0.55, 0.15), "aL": (0.25, -0.3, -1), "elbowR": (-8, 0, 0), "elbowL": (-35, 0, 0), "hip": (4, 0, -10),
                  "legR": (-8, -3, 0), "kneeR": (10, 0, 0), "legL": (8, 4, 0), "head": (-2, 0, -14)},
    "present_l": {"aL": (0.85, -0.55, 0.15), "aR": (-0.25, -0.3, -1), "elbowL": (-8, 0, 0), "elbowR": (-35, 0, 0), "hip": (4, 0, 10),
                  "legL": (-8, 3, 0), "kneeL": (10, 0, 0), "legR": (8, -4, 0), "head": (-2, 0, 14)},
    "teach_up": {"aL": (0.6, -0.5, 0.75), "aR": (-0.35, -0.5, -0.6), "elbowL": (-20, 0, 0), "elbowR": (-70, 0, 0), "hip": (-3, 0, 8),
                 "legL": (-6, 3, 0), "legR": (6, -4, 0), "kneeL": (8, 0, 0), "head": (-10, 0, 14)},
    "hold_up": {"aR": (-0.55, -0.55, 0.65), "aL": (0.35, -0.35, -0.9), "elbowR": (-30, 0, 0), "elbowL": (-40, 0, 0), "hip": (-3, 0, -8),
                "legR": (-6, -3, 0), "legL": (6, 4, 0), "kneeL": (8, 0, 0), "head": (-6, 4, -6)},
    "egg_l": {"aL": (0.55, -0.65, 0.45), "aR": (-0.3, -0.2, -1), "elbowL": (-80, 0, 0), "elbowR": (-30, 0, 0), "hip": (2, 0, 6),
              "legR": (-5, -3, 0), "legL": (5, 3, 0), "head": (2, 0, 16)},
    "throw_r0": {"aR": (-0.5, 0.45, 0.8), "aL": (0.5, -0.5, -0.6), "elbowR": (-95, 0, 0), "elbowL": (-40, 0, 0), "hip": (-6, 0, -14),
                 "legR": (8, -4, 0), "legL": (-8, 4, 0), "kneeL": (12, 0, 0), "head": (-4, 0, -8)},
    "throw_r1": {"aR": (-0.3, -0.9, 0.35), "aL": (0.35, 0.1, -0.9), "elbowR": (-8, 0, 0), "elbowL": (-30, 0, 0), "hip": (10, 0, 12),
                 "legR": (-10, -4, 0), "legL": (10, 4, 0), "kneeR": (12, 0, 0), "head": (-6, 0, -18)},
    "throw_l0": {"aL": (0.5, 0.45, 0.8), "aR": (-0.5, -0.5, -0.6), "elbowL": (-95, 0, 0), "elbowR": (-40, 0, 0), "hip": (-6, 0, 14),
                 "legL": (8, 4, 0), "legR": (-8, -4, 0), "kneeR": (12, 0, 0), "head": (-4, 0, 8)},
    "throw_l1": {"aL": (0.3, -0.9, 0.35), "aR": (-0.35, 0.1, -0.9), "elbowL": (-8, 0, 0), "elbowR": (-30, 0, 0), "hip": (10, 0, -12),
                 "legL": (-10, 4, 0), "legR": (10, -4, 0), "kneeL": (12, 0, 0), "head": (-6, 0, 18)},
    "duck": {"aR": (-0.6, -0.4, 0.6), "aL": (0.6, -0.4, 0.6), "elbowR": (-125, 0, 0), "elbowL": (-125, 0, 0), "hip": (16, 0, 0),
             "legR": (-18, -4, 0), "kneeR": (30, 0, 0), "legL": (-16, 4, 0), "kneeL": (28, 0, 0), "head": (10, 0, 12)},
    # the punch
    "shoutw": {"aR": (-0.78, -0.22, 0.62), "aL": (0.78, -0.22, 0.62), "elbowR": (-22, 0, 0), "elbowL": (-22, 0, 0), "hip": (12, 0, 0),
               "legR": (-14, -8, 0), "kneeR": (14, 0, 0), "legL": (-8, 8, 0), "kneeL": (12, 0, 0), "head": (-24, 0, 0)},
    "windup": {"aR": (-0.62, 0.62, 0.48), "aL": (0.86, -0.12, -0.5), "elbowR": (-118, 0, 0), "elbowL": (-24, 0, 0), "hip": (12, 0, -22),
               "legR": (6, -6, 0), "kneeR": (16, 0, 0), "legL": (-20, 5, 0), "kneeL": (20, 0, 0), "head": (-14, 0, 30)},
    "punch": {"aR": (-0.02, -1, 0.3), "aL": (0.45, 0.55, -0.7), "elbowR": (-3, 0, 0), "elbowL": (-90, 0, 0), "hip": (8, 0, 20),
              "legR": (-26, -4, 0), "kneeR": (20, 0, 0), "legL": (20, 5, 0), "kneeL": (6, 0, 0), "head": (-2, 0, 8)},
    "proud": {"aR": (-0.75, -0.2, -0.65), "aL": (0.35, -0.3, 1), "elbowR": (-115, 0, 0), "elbowL": (-22, 0, 0), "hip": (-4, 0, 6),
              "legR": (-6, -6, 0), "legL": (6, 6, 0), "kneeL": (6, 0, 0), "head": (-10, 0, 10)},
    "hit": {"aR": (-0.95, 0.15, 0.4), "aL": (0.95, 0.15, 0.3), "elbowR": (-12, 0, 0), "elbowL": (-12, 0, 0), "hip": (-20, 0, 0),
            "legR": (26, -8, 0), "kneeR": (10, 0, 0), "legL": (34, 8, 0), "kneeL": (14, 0, 0), "head": (-30, 12, -16)},
    "splat": {"aR": (-1, 0.0, 0.32), "aL": (1, 0.0, 0.32), "elbowR": (-4, 0, 0), "elbowL": (-4, 0, 0), "hip": (0, 0, 0),
              "legR": (0, -24, 0), "legL": (0, 24, 0), "head": (6, 8, 0)},
    "splat_point": {"aR": (-1, 0.0, 0.3), "aL": (0.15, -1, 0.22), "elbowR": (-4, 0, 0), "elbowL": (-3, 0, 0), "hip": (0, 0, 6),
                    "legR": (0, -22, 0), "legL": (0, 18, 0), "head": (2, 4, 10)},
    "slide": {"aR": (-0.9, -0.1, 0.5), "aL": (0.12, -1, 0.18), "elbowR": (-8, 0, 0), "elbowL": (-3, 0, 0), "hip": (3, 0, 4),
              "legR": (0, -12, 0), "legL": (0, 12, 0), "kneeR": (10, 0, 0), "head": (8, -6, 8)},
    "climb": {"aR": (-0.28, -0.8, 0.62), "aL": (0.28, -0.8, 0.62), "elbowR": (-34, 0, 0), "elbowL": (-34, 0, 0), "hip": (20, 0, 0),
              "legR": (-22, -3, 0), "kneeR": (34, 0, 0), "legL": (12, 3, 0), "kneeL": (22, 0, 0), "head": (-14, 0, 0)},
    # the platform
    "awe": {"aR": (-0.6, -0.55, -0.5), "aL": (0.6, -0.55, -0.5), "elbowR": (-70, 0, 0), "elbowL": (-70, 0, 0), "hip": (-4, 0, 0),
            "legR": (-4, -6, 0), "legL": (4, 6, 0), "head": (-12, 0, -22)},
    "reach": {"aR": (-0.55, -0.75, 0.5), "aL": (0.25, -0.2, -1), "elbowR": (-12, 0, 0), "elbowL": (-30, 0, 0), "hip": (10, 0, -10),
              "legR": (-14, -4, 0), "kneeR": (14, 0, 0), "legL": (10, 4, 0), "head": (-10, 0, -22)},
    "count": {"aR": (-0.3, -0.2, -1), "aL": (0.55, -0.55, 0.62), "elbowR": (-26, 0, 0), "elbowL": (-62, 0, 0), "hip": (3, 0, -8),
              "legR": (-5, -4, 0), "legL": (5, 4, 0), "head": (-4, 0, -30)},
    "cheer": {"aR": (-0.45, -0.25, 1), "aL": (0.45, -0.25, 1), "elbowR": (-20, 0, 0), "elbowL": (-20, 0, 0), "hip": (-5, 0, 0),
              "legR": (-4, -7, 0), "legL": (4, 7, 0), "head": (-14, 0, -20)},
    # the reaction, the laugh, the dive
    "hands_head": {"aR": (-0.75, -0.08, 0.66), "aL": (0.75, -0.08, 0.66), "elbowR": (0, 90, 0), "elbowL": (0, -90, 0), "hip": (-6, 0, 0),
                   "legR": (6, -5, 0), "legL": (-8, 5, 0), "kneeL": (12, 0, 0), "head": (-4, 0, 0)},
    "glance": {"aR": (-0.75, -0.08, 0.66), "aL": (0.75, -0.08, 0.66), "elbowR": (0, 90, 0), "elbowL": (0, -90, 0), "hip": (4, 0, 12),
               "legR": (6, -5, 0), "legL": (-8, 5, 0), "kneeL": (12, 0, 0), "head": (22, 0, 58)},
    "wall_sit": {"aR": (-0.35, 0.05, -1), "aL": (0.35, 0.1, -1), "elbowR": (-6, 0, 0), "elbowL": (-10, 0, 0), "hip": (12, 0, 4),
                 "legR": (-84, -8, 0), "kneeR": (6, 0, 0), "legL": (-80, 10, 0), "kneeL": (10, 0, 0), "head": (30, 6, 14)},   # shot 5: sat in the hole, head lolls
    "slump": {"aR": (-0.1, -0.35, -1), "aL": (0.1, -0.35, -1), "elbowR": (-14, 0, 0), "elbowL": (-14, 0, 0), "hip": (15, 0, 0),
              "legR": (-12, -3, 0), "kneeR": (18, 0, 0), "legL": (-10, 3, 0), "kneeL": (16, 0, 0), "head": (16, 0, 6)},
    "laugh": {"aR": (-0.3, -0.75, -0.65), "aL": (0.3, -0.75, -0.65), "elbowR": (-75, 0, 0), "elbowL": (-75, 0, 0), "hip": (13, 0, 8),
              "legR": (-12, -3, 0), "kneeR": (14, 0, 0), "legL": (-8, 3, 0), "head": (-14, 0, 14)},
    "run": {"aR": (-0.25, -0.2, -0.9), "aL": (0.25, -0.2, -0.9), "elbowR": (-80, 0, 0), "elbowL": (-80, 0, 0), "hip": (20, 0, 0),
            "legR": (-8, -2, 0), "kneeR": (24, 0, 0), "legL": (-8, 2, 0), "kneeL": (24, 0, 0), "head": (-16, 0, 0)},
    "dive_j": {"aR": (-0.16, -0.1, 1), "aL": (0.16, -0.1, 1), "elbowR": (-3, 0, 0), "elbowL": (-3, 0, 0), "hip": (-6, 0, 0),
               "legR": (8, -3, 0), "kneeR": (10, 0, 0), "legL": (-6, 3, 0), "kneeL": (6, 0, 0), "head": (-52, 0, 0)},
    "dive": {"aR": (-0.1, -0.04, 1), "aL": (0.1, -0.04, 1), "elbowR": (-3, 0, 0), "elbowL": (-3, 0, 0), "hip": (-4, 0, 0),
             "legR": (3, -2, 0), "kneeR": (6, 0, 0), "legL": (-3, 2, 0), "kneeL": (6, 0, 0), "head": (-18, 0, 0)},
    # the creators
    "h_idle": {"aR": (-0.28, -0.08, -1), "aL": (0.28, -0.08, -1), "elbowR": (-16, 0, 0), "elbowL": (-16, 0, 0), "legR": (0, -4, 0), "legL": (0, 4, 0)},
    "h_flinch": {"aR": (-0.42, -0.7, 0.55), "aL": (0.42, -0.7, 0.55), "elbowR": (-120, 0, 0), "elbowL": (-120, 0, 0), "hip": (-12, 0, 0),
                 "legR": (10, -5, 0), "legL": (-8, 5, 0), "kneeL": (12, 0, 0), "head": (-10, 0, 0)},
    "h_wave": {"aR": (-0.28, -0.08, -1), "aL": (0.72, -0.3, 0.62), "elbowR": (-16, 0, 0), "elbowL": (-24, 0, 0), "hip": (-2, 0, 0), "legR": (0, -4, 0),
               "legL": (0, 4, 0), "head": (-6, 0, 6)},
    "h_salute": {"aR": (-0.7, -0.3, 0.64), "aL": (0.28, -0.08, -1), "elbowR": (-24, 0, 0), "elbowL": (-16, 0, 0), "hip": (-2, 0, 0), "legR": (0, -4, 0),
                 "legL": (0, 4, 0), "head": (-6, 0, -6)},
    "h_clap": {"aR": (-0.32, -0.92, 0.0), "aL": (0.32, -0.92, 0.0), "elbowR": (-52, 0, 0), "elbowL": (-52, 0, 0), "hip": (4, 0, 0),
               "legR": (0, -4, 0), "legL": (0, 4, 0), "head": (2, 0, 0)},
})


# ---------------------------------------------------------------- time
def warp(t):
    """body time: the held "aaaa" in slow motion, the snap into the punch, the hit freeze, the catch-up; a slow diamond at 11.55"""
    if t < 7.01:
        return t                                                 # v7D: real time to the contact (the old snap made the wind-up 0.07 s)
    if t < 7.04:
        return 7.01                                              # Stage B 2026-11-21: 2-frame hit freeze (was to 7.10)
    if t < 7.34:
        return 7.01 + (t - 7.04) * (0.33 / 0.30)                 # v7D: catch-up to the 7.34 cut (start of "وعلي")
    if t < 11.45:
        return t
    if t < 11.95:
        return 11.45 + 0.35 * (t - 11.45)
    if t < 12.25:
        return 11.625 + (12.25 - 11.625) * (t - 11.95) / 0.30
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


def lin(u):
    return clamp01(u)


# ---------------------------------------------------------------- camera keys: (time, position, look-at, lens, roll, ease, pivot); real time
PIV = V((0.0, LY, 0))
SH = V((0.72, -21.85, 1.82))                                     # 3liSY's head during the shout
E1C, E1A, E1L = V((-2.75, -24.75, 1.6)), V((-1.5, -19.9, 1.72)), V((-2.45, -19.6, 1.9))   # egg shot 1: the hand in the foreground, Firas's spot beyond it
E2C, E2A, E2L = V((2.3, -25.15, 1.7)), V((-0.9, -19.6, 1.6)), V((2.65, -19.6, 1.9))   # egg shot 2
WIDE = V((0.35, LY - 5.75, 1.62))
WIDEL = V((0.0, -20.7, 1.9))
FRONT, FRONTL = V((-0.3, LY - 4.35, 1.2)), V((-0.25, LY + 0.3, 1.17))   # v6 2026-11-20: 0.35 closer, pair ~70% (was LY - 4.7, 61-65%); look lower so YoCube1's feet stay in (was 1.38)
WALLC, WALLL = V((1.3, -29.4, 1.7)), V((-3.75, -23.1, 1.72))
WALL_LENS = 23.0                                                  # Stage B: wide enough for the pair and the wall in one frame
W5C0, W5L0 = V((1.85, -28.45, 1.25)), V((-1.75, -24.35, 1.32))   # v6 round 2: shot 5 start tighter on the punch, less empty wall on the left
W5C, W5L = V((1.5, -28.0, 1.2)), V((-2.5, -25.02, 1.21))          # v6: at the wall hit; look 0.06 higher so YoCube1's hands keep a top margin
TWO, TWOL = V((0.3, LY - 5.6, 1.5)), V((-0.15, LY, 1.22))
PLC, PLL = V((0.4, -15.3, -13.5)), V((0.0, -8.8, -15.72))
CAMK = [
    # 1 in from the side, both faces in frame, the "14" rising between them
    (0.00, V((3.75, LY - 4.2, 1.72)), V((-0.2, LY + 0.5, 1.42)), 36, 0.0, None, None),
    (1.95, V((0.5, LY - 5.85, 1.5)), V((0.0, LY + 0.6, 1.5)), 38, 0.0, settle, PIV),
    # 2 Stage 6 2026-11-18: one wide shot of all four, a slow push; the eggs fly inside it (no egg cuts)
    (1.955, V((0.15, LY - 8.1, 1.6)), V((0.0, -21.5, 1.5)), 48.5, 0.0, ease, None),     # v6: back to the alcove wall, long lens: pair ~62-65%, guests ~60%
    (6.095, V((0.1, LY - 7.88, 1.6)), V((0.0, -21.5, 1.5)), 49.6, 0.0, ease, None),   # v7D: shot 2 ends on "ايوا" 6.10 (was 5.945, inside "سنة")
    # 3 the shout: Stage B 2026-11-21 hard cut on 5.95 (was 6.10) to 3liSY close, a slow push, then the cut into the punch
    (6.10, V((1.30, LY - 5.30, 1.45)), V((-0.40, LY + 0.30, 1.05)), 36.0, 0.0, ease, None),   # v7D framing: tight on the pair from "ايوا" (wind-up big in frame)
    (7.01, V((1.05, LY - 4.90, 1.40)), V((-0.45, LY + 0.30, 1.05)), 38.0, 0.0, ease, None),   # v7D framing: slow push to the contact on "نووب"
    (7.04, V((1.05, LY - 4.90, 1.40)), V((-0.55, LY + 0.30, 1.05)), 38.0, 0.0, ease, None),   # held through the 2-frame freeze, then follows YoCube1 to the wall
    (7.20, WALLC, WALLL, WALL_LENS, 0.0, ease, None),              # v7D framing: wide by the wall hit
    # 5 Stage B 2026-11-21: hard cut on the freeze end to one WIDE shot (pair, shaft and the orange wall), the wall hit at 7.25, hard cut at 7.30
    (7.445, WALLC + V((-0.10, 0.12, 0.0)), WALLL, WALL_LENS + 1.0, 0.0, ease, None),   # v7E
    (7.45, TWO, TWOL + V((0, 0, -0.05)), 35.5, 0.0, settle, None),   # v7D: cut on "وعلي" 7.34 (was 7.30)   # hard cut into shot 6: YoCube1 stands and talks from 7.34
    (9.22, TWO + V((0.75, 0.12, 0.05)), TWOL + V((0, 0, -0.05)), 36.0, 0.0, ease, PIV),   # v7E
    # 6 v6 2026-11-20: eases back to a front two-shot, the "16" pops above their heads, they burst, hard cut to the platform
    (9.60, TWO + V((0.75, 0.12, 0.05)), TWOL + V((0, 0, -0.05)), 36.0, 0.0, ease, None),
       # a slow push while the 16 holds
    (9.76, PLC + V((0.25, -0.35, 18.5)), PLL + V((0.0, 0.0, 17.2)), 39, 0.0, lambda u: u ** 1.7, None),   # 2026-11-24 word check: no cut inside the phrase; on the heard "مرحلة" 9.97 the lens flies through the burst into the shaft, then falls. Was:  v7C: hard cut at ledge height in the shaft: we fall 16 levels with the pieces
    (10.34, PLC + V((0.25, -0.35, 0.25)), PLL + V((0.0, 0.0, 0.15)), 39, 0.0, lambda u: 1 - (1 - u) ** 1.25, None),     # lands on the platform before "وكل" (10.56)
    (10.62, PLC, PLL + V((0, 0, -0.12)), 37.5, 0.0, settle, None),   # v7E
    # 7, 8 a slow slide past the platform: the near blocks and the far rings move against each other
    (12.05, PLC + V((-0.6, 0.4, -0.7)), PLL + V((-0.05, 0.0, -0.35)), 38.5, 0.0, ease, None),   # v6: lower, wider end so neither player is cut (was 46)
    (12.42, PLC + V((-0.5, 0.7, -1.25)), PLL + V((-0.1, 0.0, -0.43)), 36, 0.0, ease, None),   # v6 shot 8: closer and level, both ~70%
    (13.92, PLC + V((0.1, 0.6, -1.25)), PLL + V((0.1, 0.0, -0.43)), 36, 0.0, ease, None),   # v7C: was 14.20
    # 9 whooshes upward; hidden cut -> 10: wide on the ledge
    (14.035, PLC + V((0.1, 0.6, -1.25)), PLL + V((0.1, 0.0, -0.43)), 36, 0.0, ease, None),   # v7D s18: no dark whoosh (read as a blink); holds on the platform burst, was (14.07, PLC + V((0.7, 0.3, 9.0)), PLL + V((0.1, 0.0, 14.0)), 31)
    (14.04, PP + V((-0.55, -6.6, 1.8)), PP + V((-0.55, 0.0, 1.06)), 37, 0.0, ease, None),   # v7E
    (15.08, PP + V((-0.65, -6.2, 1.75)), PP + V((-0.6, 0.0, 1.04)), 37, 0.0, ease, None),   # v7E
    # 11 settles on the two, a small orbit
    (15.62, PP + V((-0.75, -6.0, 1.7)), PP + V((-0.85, 0.0, 1.12)), 35.5, 0.0, settle, None),   # v7E
    (16.25, PP + V((-1.15, -5.95, 1.7)), PP + V((-0.85, 0.0, 1.12)), 35.5, 0.0, ease, PIV),   # v7E
    # 12 they run for the tip; cut to a hero shot from out in the shaft as they jump at the lens; it tips down and chases them
    (16.70, V((0.0, -22.0, 3.0)), V((0.0, -15.0, -1.0)), 34, 0.0, ease, None),   # fix-all 2026-11-19: no cut to the grey room, the lens follows them off the ledge
    (17.04, V((0.2, -12.2, 1.4)), V((0.0, -8.0, -24.0)), 30, 0.0, ease, None),
    (17.52, V((0.0, -3.0, -156.5)), V((0.0, -1.5, -200.0)), 26, 0.0, drop, None),
    (17.75, V((0.0, -2.9, -157.8)), V((0.0, -1.5, -200.0)), 26, 0.0, ease, None),
]
if DIVE == "none":                                                # Stage B: no dive, the ledge shot drifts on slowly to the end
    CAMK = [k for k in CAMK if k[0] <= 16.25] + [(17.75, PP + V((-1.35, -5.9, 1.7)), PP + V((-0.85, 0.0, 1.12)), 36, 0.0, ease, None)]


def shake(t):
    a = 0.0
    if t >= 6.10:
        a += 0.012 * math.exp(-(t - 6.10) / 0.12)
    if 6.25 < t < 6.72:
        a += 0.007                                               # trembling with the held shout
    if t >= 7.04:
        a += 0.075 * math.exp(-(t - 7.04) / 0.09)                # the punch, after the freeze
    if t >= 17.52 and DIVE != "none":                            # v6: the wall slam has its own jolt in cam_at

        a += 0.05 * math.exp(-(t - 17.52) / 0.06)
    return a


def cam_at(t):
    k = CAMK
    if t <= k[0][0]:
        a = b = k[0]
        s = 0.0
    else:
        i = max(j for j in range(len(k) - 1) if k[j][0] <= t) if t < k[-1][0] else len(k) - 2
        a, b = k[i], k[i + 1]
        s = (b[5] or ease)((t - a[0]) / (b[0] - a[0]))
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
    sh = shake(t)
    if 7.01 <= t < 7.04:
        sh = 0.0                                                 # the freeze is a freeze
    look = look + V((sh * math.sin(97 * t), 0.0, sh * math.sin(131 * t + 1.0)))
    if T_SLAM <= t < 7.45:                                       # v6 2026-11-20: wall jolt, strongest on the contact frame (Stage B: to the 7.30 cut)
        dt = t - T_SLAM
        k = 0.12 * math.exp(-dt / 0.05)
        look = look + V((0.6 * k * math.sin(2 * math.pi * 9 * dt + 1.2), 0.0, -0.5 * k * math.cos(2 * math.pi * 12 * dt)))   # round 2: half the drop, keeps the top margin
    if not 7.01 <= t < 7.04:
        look = look + V((0.006 * math.sin(1.3 * t), 0.0, 0.005 * math.sin(1.7 * t + 2)))   # a living hand, never a dead tripod
    return pos, look, lens, roll


# ---------------------------------------------------------------- the light
def flood(t):
    shout = ease((t - 6.10) / 0.4) * (1 - ease((t - 7.45) / 0.9))
    cascade = ease((t - 9.60) / 0.5) * (1 - 0.97 * ease((t - 10.45) / 0.55)) * (1 - ease((t - 14.04) / 0.02))   # v7E
    dive = 0.0 if DIVE == "none" else ease((t - 16.6) / 0.35)
    return clamp01(shout + cascade + dive)


RING_T = [9.60 + 0.70 * k / 15.0 for k in range(LV)]  # ignitions, top to bottom, faster and faster   # v7E
POOL_N = emit_node(bpy.data.materials["pool"], 4.0)
POOL_B = next(n for n in bpy.data.materials["pool"].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
POOL_B0 = (POOL_B.inputs["Roughness"].default_value, POOL_B.inputs["Specular IOR Level"].default_value)
PLAT_N = emit_node(bpy.data.materials["plat_e"], 1.2)


def set_glow(t):
    f = flood(t)
    deep = 1 + 2.2 * ease((t - 16.7) / 0.3)    # the rainbow rush: even the deep wall burns (less in the sheet dives: no white-out)
    near = ease((t - 16.95) / 0.4)                               # near the water its light dims: water, not a white-out
    if DIVE == "none":
        deep, near = 1.0, 0.0                                     # Stage B: no rainbow rush, no water
    bpy.data.lights["pool"].energy = 40000 * (1 - 1.0 * near)   # fix-all: the pool light made the white orb
    POOL_N.inputs[1].default_value = 4.0 - 3.7 * near
    matte = DIVE == "M" and t >= T_CUT2                          # dive r3: the glassy pool mirrored the shaft top as a glow ball under the lens
    POOL_B.inputs["Roughness"].default_value = 0.6 if matte else POOL_B0[0]
    POOL_B.inputs["Specular IOR Level"].default_value = 0.0 if matte else POOL_B0[1]
    for node, base in EMIT_NODES["w"]:
        node.inputs[1].default_value = base * (1 + 6.0 * f) * deep
    for node, base in EMIT_NODES["r"]:
        node.inputs[1].default_value = base * (1 + 3.6 * f) * deep
    for k in range(LV):
        node, base = EMIT_NODES["dia"][k]
        lit = 0.0
        if t >= RING_T[k]:
            lit = 1.2 * ease((t - RING_T[k]) / 0.15) + 3.0 * math.exp(-(t - RING_T[k]) / 0.22)
        wave = 0.8 * max(0.0, math.sin(2.2 * t - 0.55 * k)) if 10.6 < t < 14.04 else 0.0   # the rings keep breathing, top to bottom
        calm = 1 - 0.5 * ease((t - 10.5) / 0.5) * (1 - ease((t - 14.04) / 0.02))           # a softer ring behind them on the platform
        node.inputs[1].default_value = (1.6 + 2.6 * (lit + wave)) * calm
        RING_L[k].data.energy = 1800 * (0.6 + 0.8 * (lit + wave)) * ((1 - near) if k >= LV - 2 else 1.0)   # fix-all: the lowest ring lights made the white orb in the haze
    if PLAT_N:
        PLAT_N.inputs[1].default_value = 1.2 + 2.4 * bump(t, 10.42, 0.5) + 0.5 * math.sin(3.0 * t) ** 2


def place_lights5(pos, subj, hp, hy, t):
    """the character lights follow the camera and the subject: rims from behind and high so they run along the suits' edges"""
    fwd, right = axes(pos, subj)
    fw, rg = (fwd, right)
    near = 1.0 if (pos - subj).length < 3.2 else 0.0
    for nm, loc, tgt in (("key", subj - fw * 3.0 - rg * 2.2 + up * 1.6, subj),
                         ("rimA", subj + fw * 4.2 - rg * 2.1 + up * 1.5, subj),
                         ("rimB", subj + fw * 4.2 + rg * 2.1 + up * 1.2, subj),
                         ("under", subj - fw * 1.2 - up * 2.4, subj + up * 0.6),
                         ("faceP", hp - fw * 1.3 - up * 0.1 - rg * 0.2, hp),
                         ("faceY", hy - fw * 1.3 + up * 0.25 - rg * 0.3, hy),
                         ("floor", subj - fw * 1.2 + up * 5.0, subj - up * 1.6)):
        LT[nm].location = loc
        LT[nm].rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    rim = 700.0 if near else 1500.0                              # Stage B (H2): no 2x rim in the opening, it turned 3liSY pink at 0-0.8 s
    if 6.10 <= t < 7.45:   # v7E
        rim = 500.0                                              # v7D: the whole punch shot
    if t < 0.85:                                                 # Stage B (H2): 3liSY faces the magenta rim in shot 1; keep his suit its own dark colour
        rim = 500.0
    shout = False                                                # v7D: the shout close-up is gone (one punch shot)
    if shout:
        rim = 900.0                                              # v7C fault 2: was 2800, read as neon on the arms
    if t >= 14.04:
        rim = min(rim, 700.0)                                    # v7C fault 2: the ending rim read as neon too (was 1500 when not near)
    if 16.20 <= t < 16.62 and DIVE != "none":                    # Stage B (H3): no run any more, so no black-out at 16.3
        rim = 0.0                                                # s6 fix 2026-11-19: side-on while running, the magenta rim flooded 3liSY's whole side; 400 was still purple, 0 tested clean at f980
    LT["rimA"].data.energy = LT["rimB"].data.energy = rim
    LT["rimB"].data.energy = rim * (1 - 0.75 * win(t, 3.70, 4.20, 0.10))   # v7D: moved with the throw   # v7C r2: YoCube1 turns into the cyan rim for the throw, his suit went teal 4.07-4.20
    LT["rimA"].data.size = LT["rimB"].data.size = 1.4
    plat = 10.4 < t < 14.04
    LT["key"].data.energy = 170.0 if near else (430.0 if plat else 300.0)
    LT["faceP"].data.energy = 3.4 if near else (13.0 if plat else (30.0 if shout else 9.0))
    LT["faceY"].data.energy = 1.5
    if DIVE == "M" and t >= T_CUT1:                               # v6 mix: the faces must read in the fall, never dark blobs
        LT["faceP"].data.energy, LT["faceY"].data.energy = 14.0, 4.0
        if t >= T_CUT2:                                           # top-down: the face lights hang between the lens and the faces
            for nm, h_ in (("faceP", hp), ("faceY", hy)):
                LT[nm].location = h_ + V((0.2, -0.3, 1.5))
                LT[nm].rotation_euler = (h_ - LT[nm].location).to_track_quat("-Z", "Y").to_euler()
    bpy.data.lights["floor"].energy = 420.0 if plat else 1500.0
    if DIVE == "M" and t >= T_CUT1:
        bpy.data.lights["floor"].energy = 0.0                     # dive r2: it lit a white dot on the water beside 3liSY's head


bpy.data.lights["floor"].spot_size = math.radians(62)
bpy.data.lights["floor"].energy = 1500.0
NOCH = bpy.data.collections.new("no_chars")                       # the floor light lights the floor, not the tops of their heads
for o in CHARS:
    NOCH.objects.link(o)
LT["floor"].light_linking.receiver_collection = NOCH
for co_ in NOCH.collection_objects:
    co_.light_linking.link_state = "EXCLUDE"
for nm, key in (("P", "head"), ("Y", "lay")):                     # the heads stay matte: stickers and skin keep their colour
    mh = bpy.data.materials[nm].copy()
    mh.name = nm + "h"
    for o in (P if nm == "P" else Y)["meshes"]:
        if key in o.name and o.data.materials:
            o.data.materials[0] = mh
for nm in ("P", "P_o", "Y", "Y_o"):                               # a little gloss so the rims catch the black suits; the skin colours stay
    b_ = next(n for n in bpy.data.materials[nm].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b_.inputs["Roughness"].default_value = 0.68
    b_.inputs["Specular IOR Level"].default_value = 0.34
ALC = area("alcove", V((1.0, -28.0, 6.2)), V((-3.0, -26.0, 1.0)), 260.0, (1.0, 0.86, 0.7), 5.0, linked=False)   # lights the wall of the gag


# ---------------------------------------------------------------- materials and small meshes
def emit_mat(name, col, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b_ = m.node_tree.nodes["Principled BSDF"]
    b_.inputs["Base Color"].default_value = (*col, 1)
    b_.inputs["Emission Color"].default_value = (*col, 1)
    b_.inputs["Emission Strength"].default_value = strength
    return m


def fx_obj(name, col, strength):
    me = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.data.materials.append(emit_mat(name, col, strength))
    o.visible_shadow = False
    return o


def fill(o, cubes):
    """cubes: [(centre, size or (sx, sy, sz))] -> the object's mesh (rebuilt every frame)"""
    bm = bmesh.new()
    for c, s in cubes:
        if isinstance(s, tuple):
            r_ = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=s, verts=r_["verts"])
        else:
            if s <= 0.002:
                continue
            r_ = bmesh.ops.create_cube(bm, size=s)
        bmesh.ops.translate(bm, vec=c, verts=r_["verts"])
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()


def pixel_mesh(name, rows, px, depth, mats, parent=None):
    """pixel art as a real block object: one cube per cell, local +Z toward the viewer. rows use letters; mats maps a letter to
    (front material, side material)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    H, W = len(rows), max(len(r) for r in rows)
    slots = []
    for fm, sm in mats.values():
        for m in (fm, sm):
            if m not in slots:
                slots.append(m)
    for ry, row in enumerate(rows):
        for rx, cell in enumerate(row):
            if cell not in mats:
                continue
            r_ = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(px, px, depth), verts=r_["verts"])
            bmesh.ops.translate(bm, vec=((rx - (W - 1) / 2) * px, ((H - 1) / 2 - ry) * px, 0), verts=r_["verts"])
            fm, sm = mats[cell]
            for f_ in {f_ for v in r_["verts"] for f_ in v.link_faces}:
                f_.normal_update()
                f_.material_index = slots.index(fm if abs(f_.normal.z) > 0.5 else sm)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    for m in slots:
        o.data.materials.append(m)
    o.parent = parent
    o.visible_shadow = False
    return o


def face_cam(o, pos, yaw=0.0):
    """turn a plate to the camera, a little off so its thickness shows"""
    q = (co.location - pos).to_track_quat("Z", "Y")
    o.rotation_mode = "XYZ"
    o.rotation_euler = (Quaternion((0, 0, 1), math.radians(yaw)) @ q).to_euler()


# ---------------------------------------------------------------- the outline mask and the glasses
def mask_scene():
    """a second tiny render per frame: the bodies alone as flat colours (red 3liSY, green YoCube1, blue the creators); post5.py turns its
    edge into the thin glowing outline, so the line sits only on the silhouette and keeps its width in every shot"""
    ms = bpy.data.scenes.new("mask")
    ms.render.engine = sc.render.engine
    ms.render.resolution_x, ms.render.resolution_y, ms.render.resolution_percentage = sc.render.resolution_x, sc.render.resolution_y, 100
    ms.render.image_settings.file_format = "PNG"
    ms.render.filter_size = 0.7
    ms.view_settings.view_transform = "Standard"
    ms.eevee.taa_render_samples = 1
    ms.eevee.bokeh_max_size = 0.0
    ms.camera = co
    ms.collection.objects.link(co)
    ms.collection.children.link(cc)
    m = bpy.data.materials.new("mask")
    m.use_nodes = True
    nt_ = m.node_tree
    for n in list(nt_.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt_.nodes.remove(n)
    oi, em = nt_.nodes.new("ShaderNodeObjectInfo"), nt_.nodes.new("ShaderNodeEmission")
    nt_.links.new(oi.outputs["Color"], em.inputs["Color"])
    nt_.links.new(em.outputs[0], next(n for n in nt_.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    ms.view_layers[0].material_override = m
    return ms


MS = mask_scene()
for rig, col in ((P, (1, 0, 0, 1)), (Y, (0, 1, 0, 1))):
    for o in rig["meshes"]:
        o.color = col
Y_TEX = next(n for n in bpy.data.materials["Yh"].node_tree.nodes if n.type == "TEX_IMAGE")
Y_CLEAN = Y_TEX.image
SCR = [bpy.data.images.load(os.path.join(SKINS, f"YoCube1_scr{i}.png"), check_existing=True) for i in range(6)]
for im_ in SCR:
    im_.alpha_mode = "STRAIGHT"


def lens_glow():
    nt_ = bpy.data.materials["Yh"].node_tree
    bs = next(n for n in nt_.nodes if n.type == "BSDF_PRINCIPLED")
    tx = nt_.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(SKINS, "YoCube1_lens.png"), check_existing=True)
    tx.interpolation = "Closest"
    val = nt_.nodes.new("ShaderNodeValue")
    mul = nt_.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt_.links.new(tx.outputs["Color"], mul.inputs[0])
    nt_.links.new(val.outputs[0], mul.inputs[1])
    bs.inputs["Emission Color"].default_value = (0.7, 0.95, 1.0, 1)
    nt_.links.new(mul.outputs[0], bs.inputs["Emission Strength"])
    return val


LENS = lens_glow()
P_TEX = next(n for n in bpy.data.materials["Ph"].node_tree.nodes if n.type == "TEX_IMAGE")
FACESET = os.environ.get("FACESET", "")   # faces choice sheet (2026-11-18): skins/faceset/<name>/ replaces the mouths and YoCube1's head; empty = v5 as before
_FS = os.path.join(SKINS, "faceset", FACESET) if FACESET else SKINS
if FACESET:
    Y_CLEAN = bpy.data.images.load(os.path.join(_FS, "YoCube1_clean.png"), check_existing=True)
    Y_CLEAN.alpha_mode = "STRAIGHT"
MOUTH5 = {s: bpy.data.images.load(os.path.join(_FS, f"3liSY_v5_{s}.png"), check_existing=True) for s in "CHOW"}
for im_ in MOUTH5.values():
    im_.alpha_mode = "STRAIGHT"
WSHOUT = {"X": "C", "M": "C", "S": "O", "E": "O", "A": "W", "O": "W"}   # during the shout: a bigger open
WTALK = {"X": "C", "M": "C", "S": "H", "E": "H", "A": "O", "O": "O"}   # the 3 small shapes


def mouth5(t):
    f = min(len(SHAPE_P) - 1, int(round(t * FPS)))
    s = SHAPE_P[f]
    return (WSHOUT if 6.10 <= t <= 7.42 else WTALK)[s]


STRESS_Y = LS.track("YoCube1")[1]


def lens_glow_at(t):
    return 0.7 + 7.0 * sum(s * bump(t, ts - 0.03, 0.26) for ts, s in STRESS_Y)


# ---------------------------------------------------------------- effects: sparks, trails, glints (cube particles)
EGG_T = [(2.92, 3.14, STAT_F, "L"), (3.89, 4.09, STAT_M, "R")]  # v7D: in the hand on "ومصطفى" 3.837, lands 4.09 (v7C 4.24/4.46 was late)  # v7C 2026-11-23: Mustafa egg after "فراس جيمر" ends (was 3.62/3.84)  # Stage 6: on the words    # release, landing, target, which hand
HIT = V((-0.72, LY + 0.05, 1.8))
SPLASH = V((0, -8.7, -161.0)) if DIVE else V((0, -2.5, -161.0))
EMIT = []    # body clock: (group, t0, origin, n, speed, life, gravity, size, spread, seed)
EMIT_R = []  # real clock: the hit's sparks keep flying through the freeze
for k in range(LV):
    EMIT.append(("cyan", RING_T[k], V((0, 0, RING_Z[k] + 0.5)), 46, 1.6, 0.9, -0.8, 0.07, "ring", 10 + k))
    EMIT.append(("white", RING_T[k] + 0.05, V((0, 0, RING_Z[k] + 0.5)), 22, 0.4, 1.5, -0.5, 0.045, "ring", 50 + k))
EMIT.append(("white", 9.60, YL + V((0, 0, 1.2)), 30, 1.8, 0.6, 0.0, 0.03, "sphere", 3))   # v6: follows the new burst time
EMIT.append(("white", 9.60, PP + V((0, 0, 1.2)), 30, 1.8, 0.6, 0.0, 0.03, "sphere", 31))   # v7E
EMIT.append(("white", 10.48, YQ + V((0, 0, 1.1)), 40, 1.8, 0.6, 0.0, 0.035, "sphere", 4))
EMIT.append(("white", 10.48, PQ0 + V((0, 0, 1.1)), 40, 1.8, 0.6, 0.0, 0.035, "sphere", 41))
EMIT.append(("cyan", 11.56, DIA_C, 40, 1.6, 0.7, 0.0, 0.04, "star", 5))
EMIT.append(("white", 11.58, DIA_C, 24, 1.1, 0.7, 0.0, 0.03, "star", 51))
# v6 shot 8: YoCube1's hop to the board side is gone (its two puffs were here)
# 2026-11-24 word check: no second burst, plain cut at 14.04. Was: EMIT.append(("white", 14.16, YL + V((0, 0, 1.1)), 60, 1.6, 0.6, 0.0, 0.03, "sphere", 8))
for t1_, pos_, n_ in ((3.14, STAT_F, 9), (4.09, STAT_M, 90)):     # the egg lands: a pop on the ledge
    EMIT.append(("cyan", t1_, pos_ + V((0, 0, 0.5)), 70, 3.6, 0.8, -3.0, 0.07, "sphere", n_))
    EMIT.append(("gold", t1_ + 0.03, pos_ + V((0, 0, 0.8)), 40, 2.8, 0.9, -2.0, 0.05, "sphere", n_ + 1))
    EMIT.append(("white", t1_, pos_ + V((0, 0, 0.1)), 40, 2.0, 0.5, 0.0, 0.05, "disc", n_ + 2))
for k_, g_ in enumerate(("ycr", "ycy", "ycg", "ycb")):            # Stage 6 shot 4: the hit breaks bits off YoCube1's screen, in its own colours
    EMIT_R.append((g_, 7.01, HIT, 3, 3.4, 0.7, -9.8, 0.075, "sphere", 201 + k_))
EMIT_R.append(("quartz", 7.01, HIT, 44, 1.4, 0.6, 0.6, 0.11, "sphere", 206))    # a short dust puff
if DIVE == "M":                                                   # v6 mix: one tight block splash where each head goes in, heavy, no glow
    for s_, sd_ in ((1, 95), (-1, 98)):
        sp_ = V((s_ * 0.9, MIX_CY + MIX_DY, 0.0)) + mix_dir(s_)
        sp_.z = -161.0
        EMIT_R.append(("wetd", T_WET, sp_, 40, 5.5, 0.5, -30.0, 0.11, "up_s", sd_))       # dive r2: smaller, darker, fewer, slower (was a frame-filling white cloud)
        EMIT_R.append(("foamd", T_WET, sp_, 7, 4.5, 0.45, -30.0, 0.09, "up_s", sd_ + 1))     # dive r3: fewer pale bits (read as confetti)
        EMIT_R.append(("foamd", T_WET + 0.02, sp_, 12, 3.0, 0.4, -10.0, 0.10, "crown_s", sd_ + 2))
elif DIVE == "none":
    pass                                                          # Stage B: no dive, no splash
elif DIVE:                                                        # a water splash in blocks: a dark-blue column, a foam crown, low glow
    EMIT_R.append(("water", 17.50, SPLASH, 160, 24.0, 0.9, -30.0, 0.26, "up", 95))
    EMIT_R.append(("foam", 17.50, SPLASH, 40, 18.0, 0.8, -30.0, 0.18, "up", 96))
    EMIT_R.append(("foam", 17.51, SPLASH, 48, 9.0, 0.6, -8.0, 0.3, "crown", 97))
else:
    EMIT_R.append(("cyan", 17.52, SPLASH, 340, 14.0, 0.7, -20.0, 0.28, "up", 95))    # the splash
    EMIT_R.append(("white", 17.52, SPLASH, 50, 11.0, 0.7, -20.0, 0.12, "up", 96))   # fix-all: fewer, smaller white bits, no blown orb
    EMIT_R.append(("white", 17.54, SPLASH, 20, 7.0, 0.5, -6.0, 0.2, "crown", 97))
FXC = {"ycr": (0.85, 0.1, 0.1), "ycy": (1.0, 0.85, 0.15), "ycg": (0.15, 0.8, 0.25), "ycb": (0.1, 0.3, 0.95), "water": (0.05, 0.28, 0.85), "foam": (0.7, 0.88, 1.0), "gold": (1.0, 0.72, 0.25), "cyan": (0.3, 0.95, 1.0), "white": (1.0, 0.97, 0.9), "quartz": (0.85, 0.82, 0.78), "dia": (0.45, 1.0, 1.0),
       "wetd": (0.03, 0.17, 0.5), "foamd": (0.42, 0.6, 0.78)}       # dive r2: the mix splash, real water blocks, not glowing white
FXO = {g: fx_obj("fx_" + g, c, {"quartz": 1.5, "water": 1.6, "foam": 2.6, "ycr": 1.8, "ycy": 1.8, "ycg": 1.8, "ycb": 1.8, "wetd": 0.45, "foamd": 0.6}.get(g, 12.0)) for g, c in FXC.items()}
STREAK = [fx_obj("fx_st%d" % i, c, 9.0) for i, c in enumerate(((0.25, 0.9, 1.0), (1.0, 0.25, 0.8), (1.0, 0.75, 0.25)))]
srng = random.Random(21)
STRK = [(srng.uniform(0, 2 * math.pi), srng.uniform(0, 1), srng.uniform(26.0, 44.0), srng.uniform(4.0, 10.0), srng.randrange(3), srng.uniform(23.2, 24.6))
        for _ in range(50)]


def streaks(t):
    out = [[], [], []]
    a = ease((t - 9.60) / 0.4) * (1 - ease((t - 14.02) / 0.02))   # v7E
    if a <= 0.01:
        return out
    for ang, ph, sp, ln, c, rr in STRK:
        z = -8 - ((ph * 100 + sp * t) % 100)
        p = V((rr * math.cos(ang), rr * math.sin(ang), z))
        out[c].append((p, (0.16 * a, 0.16 * a, ln * a)))
    return out


def burst_cubes(lst, clock, out):
    for g, t0, org, n, sp, life, gz, size, spread, seed in lst:
        age = clock - t0
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
            elif spread == "ringv":                               # a ring in the upright plane, opening outward
                a = i / n * 2 * math.pi
                p0, v = org, V((math.cos(a), 0.0, math.sin(a))) * sp
            elif spread == "disc":                                # a flat ring along the floor
                a = rr.random() * 2 * math.pi
                p0, v = org, V((math.cos(a), math.sin(a), 0.05)) * sp * (0.7 + 0.5 * rr.random())
            elif spread == "wall":                                # off the wall, into the room
                a = rr.random() * 2 * math.pi                     # a ring along the wall, round his outline
                v = V((0.25 + 0.3 * rr.random(), math.cos(a), math.sin(a))).normalized() * sp * (0.5 + rr.random())
                p0 = org + V((0, 0.55 * math.cos(a), 0.95 * math.sin(a)))
            elif spread == "up":                                  # the splash: a wall of water jumps up round the lens
                a = rr.random() * 2 * math.pi
                rad = 1.0 + 6.0 * rr.random()
                p0 = org + V((rad * math.cos(a), rad * math.sin(a), 0))
                v = V((0.55 * math.cos(a), 0.55 * math.sin(a), 0.7 + rr.random())) * sp
            elif spread == "up_s":                                # v6 mix: a tight column where one head goes in
                a = rr.random() * 2 * math.pi
                rad = 0.1 + 0.55 * rr.random()
                p0 = org + V((rad * math.cos(a), rad * math.sin(a), 0))
                v = V((0.45 * math.cos(a), 0.45 * math.sin(a), 0.7 + rr.random())) * sp
            elif spread == "crown_s":                             # v6 mix: a small crown round one head
                a = i / n * 2 * math.pi + 0.05 * rr.random()
                p0 = org + V((0.7 * math.cos(a), 0.7 * math.sin(a), 0))
                v = V((0.8 * math.cos(a), 0.8 * math.sin(a), 1.0 + 0.3 * rr.random())) * sp
            elif spread == "crown":
                a = i / n * 2 * math.pi + 0.05 * rr.random()
                p0 = org + V((5.0 * math.cos(a), 5.0 * math.sin(a), 0))
                v = V((0.5 * math.cos(a), 0.5 * math.sin(a), 1.2 + 0.3 * rr.random())) * sp
            else:
                v = V((rr.gauss(0, 1), rr.gauss(0, 1), rr.gauss(0, 1))).normalized() * sp * (0.4 + rr.random())
                p0 = org
            a_ = age * (0.7 + 0.6 * rr.random())
            p = p0 + v * a_ + V((0, 0, 0.5 * gz * a_ * a_))
            out[g].append((p, size * (1 - age / life) ** 0.7))


def particles(t, tw):
    out = {g: [] for g in FXO}
    burst_cubes(EMIT, tw, out)
    burst_cubes([e for e in EMIT_R if not (e[1] == 7.01 and t >= 7.45)], t, out)   # Stage B: the punch chips end with the wall shot (7.30 cut)
    for rel, land, tgt, hand in EGG_T:                            # the egg's sparkle trail
        for j in range(16):
            te = rel + (land - rel) * j / 16.0
            age = t - te
            if 0 <= age < 0.4:
                out["gold"].append((egg_pos(te, rel, land, tgt, hand), 0.045 * (1 - age / 0.4)))
    if 6.00 < t < 7.0:                                            # the fist charges up (Stage B: from the arm snap)
        fist = hand_of(P, "R")
        rr = random.Random(int(t * 60))
        for i in range(10):
            a = rr.random() * 2 * math.pi
            d = 0.12 + 0.28 * rr.random()
            out["gold"].append((fist + V((d * math.cos(a), d * math.sin(a), rr.uniform(-0.2, 0.3))), 0.022 * rr.random() + 0.008))
    if False:  # shot 5 fix: no dizzy stars, was 7.42 < t < 8.8
        hy_ = head_of(Y)
        for i in range(5):
            a = 7.0 * t + i * 2 * math.pi / 5
            out["gold"].append((hy_ + V((0.44 * math.cos(a), 0.44 * math.sin(a), 0.06 * math.sin(3 * a))), 0.05))
    for i, (t0, t1, row) in enumerate(FLY):                       # the diamonds fly to the board, with a sparkle trail
        if t0 <= t <= t1 - 0.03:                                    # v7C fault 5: gone before it lands (it sat on the icon as a white square at 13.30)
            out["dia"].append((fly_pos(i, clamp01((t - t0) / (t1 - t0))), 0.16))
            for j in range(6):
                u = clamp01((t - 0.018 * (j + 1) - t0) / (t1 - t0))
                out["white"].append((fly_pos(i, u), 0.05 * (1 - j / 6)))
    return out


# ---------------------------------------------------------------- spawn eggs: real block items
EGG_ROWS = ["....oooo....", "...oaaaao...", "..oaabaaao..", "..oaaaaaao..", ".oaabaaabao.", ".oaaaaaaaao.", "oaaaaabaaaao", "oabaaaaaabao",
            "oaaaaaaaaaao", "oaaabaaabaao", ".oaaaaaaaao.", ".oabaaaabao.", "..oaaaaaao..", "...oooooo..."]


def make_egg(name, ca, cb):
    a, b, o_ = emit_mat(name + "a", ca, 0.9), emit_mat(name + "b", cb, 0.9), emit_mat(name + "o", (0.04, 0.03, 0.03), 0.0)
    return pixel_mesh(name, EGG_ROWS, 0.038, 0.1, {"a": (a, a), "b": (b, b), "o": (o_, o_)})


# Stage 6 2026-11-18: colours from the real skins (Firas: charcoal hoodie + dark red; Mustafa: red flannel + cream)
EGGS = [make_egg("egg_f", (0.17, 0.17, 0.18), (0.6, 0.07, 0.06)), make_egg("egg_m", (0.75, 0.02, 0.02), (0.92, 0.7, 0.5))]


def hand_of(rig, side):
    return rig["elbow" + side].matrix_world @ (V((0, 0, -9)) * PX)


def egg_pos(t, rel, land, tgt, side):
    u = clamp01((t - rel) / (land - rel))
    p0 = EGG_H[side] if EGG_H[side] is not None else YP + V((0, 0, 1.5))
    p = p0.lerp(tgt + V((0, 0, 0.35)), u ** 0.85)
    return p + V((0, 0, (1.9 if side == "R" else 1.15) * math.sin(math.pi * u)))  # Stage 6: egg 2 arcs high, clear of 3liSY's head


EGG_H = {"L": None, "R": None}


# ---------------------------------------------------------------- the creators: full colour, sharp, a soft cyan edge, faint scan lines
def holo(tag):
    """returns the reveal height value node, the opacity value node"""
    vals = []
    for nm in (tag, tag + "_o"):
        m = bpy.data.materials[nm]
        nt_ = m.node_tree
        tx = next(n for n in nt_.nodes if n.type == "TEX_IMAGE")
        for n in list(nt_.nodes):
            if n.type not in ("OUTPUT_MATERIAL", "TEX_IMAGE"):
                nt_.nodes.remove(n)
        N = nt_.nodes.new
        gp, sp = N("ShaderNodeNewGeometry"), N("ShaderNodeSeparateXYZ")
        nt_.links.new(gp.outputs["Position"], sp.inputs[0])

        def math_(op, a, b=None, _nt=nt_):
            n = _nt.nodes.new("ShaderNodeMath")
            n.operation = op
            for i, v in enumerate((a, b)):
                if v is None:
                    continue
                if isinstance(v, (int, float)):
                    n.inputs[i].default_value = v
                else:
                    _nt.links.new(v, n.inputs[i])
            return n.outputs[0]

        cut, opa = N("ShaderNodeValue"), N("ShaderNodeValue")
        cut.outputs[0].default_value = 0.0
        opa.outputs[0].default_value = 1.0
        scan = math_("MULTIPLY_ADD", math_("SINE", math_("MULTIPLY", sp.outputs["Z"], 34.0)), 0.07)   # faint scan lines
        scan.node.inputs[2].default_value = 1.0
        lw = N("ShaderNodeLayerWeight")
        lw.inputs[0].default_value = 0.5
        shade = math_("SUBTRACT", 1.0, math_("MULTIPLY", lw.outputs["Facing"], 0.5))                 # the box faces read as a body
        band = math_("SUBTRACT", 1.0, math_("MINIMUM", math_("MULTIPLY", math_("ABSOLUTE", math_("SUBTRACT", sp.outputs["Z"], cut.outputs[0])), 10.0), 1.0))
        tint = N("ShaderNodeMix")
        tint.data_type, tint.blend_type = "RGBA", "MIX"
        nt_.links.new(band, tint.inputs["Factor"])
        nt_.links.new(tx.outputs["Color"], tint.inputs[6])
        tint.inputs[7].default_value = (0.35, 0.95, 1.0, 1)
        em = N("ShaderNodeEmission")
        nt_.links.new(tint.outputs[2], em.inputs["Color"])
        nt_.links.new(math_("MULTIPLY", math_("ADD", math_("MULTIPLY", math_("MULTIPLY", scan, shade), 0.62), 0.0),
                            math_("ADD", 1.0, math_("MULTIPLY", band, 7.0))), em.inputs["Strength"])
        shown = math_("MULTIPLY", math_("LESS_THAN", sp.outputs["Z"], cut.outputs[0]), math_("MULTIPLY", tx.outputs["Alpha"], opa.outputs[0]))
        tr, mx = N("ShaderNodeBsdfTransparent"), N("ShaderNodeMixShader")
        nt_.links.new(shown, mx.inputs[0])
        nt_.links.new(tr.outputs[0], mx.inputs[1])
        nt_.links.new(em.outputs[0], mx.inputs[2])
        nt_.links.new(mx.outputs[0], next(n for n in nt_.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
        m.surface_render_method = "DITHERED"
        vals.append((cut, opa))
    return vals


def creator(tag, skin, pos):
    global ARMW
    ARMW = 4
    r_ = player(tag, os.path.join(SCENE, "creators", skin), {"elbowR": (-20, 0, 0), "elbowL": (-20, 0, 0), "kneeR": (10, 0, 0), "kneeL": (10, 0, 0)})
    ARMW = 3
    r_["base"].location = pos
    r_["base"].scale = (STAT_S, STAT_S, STAT_S)
    return r_, holo(tag)


FIG = {"F": creator("F", "Fir4sGamer.png", STAT_F), "M": creator("M", "Mustafa_GO.png", STAT_M)}
for rig_, _v in FIG.values():
    for o in rig_["meshes"]:
        o.color = (0, 0, 1, 1)
        MS.collection.objects.link(o)
HOLO_K = {"F": [(0.0, "h_wave"), (6.0, "h_wave"), (6.5, "h_idle"), (7.03, "h_idle"), (7.16, "h_flinch"), (7.38, "h_flinch"), (7.52, "h_clap"), (8.4, "h_clap")],
          "M": [(0.0, "h_salute"), (6.0, "h_salute"), (6.5, "h_idle"), (7.05, "h_idle"), (7.20, "h_clap"), (8.4, "h_clap")]}
HOLO_Y = {"F": [(0.0, 25.0), (7.0, 25.0), (7.2, 40.0)], "M": [(0.0, -25.0), (7.0, -25.0), (7.2, -40.0)]}


def animate_h(key, t):
    rig = FIG[key][0]
    ph = 0.9 if key == "F" else 2.3
    pose = pose_at(HOLO_K[key], t)
    for j in ("aR", "aL"):
        rig["arm" + j[1]].rotation_euler = arm_euler(pose.get(j, (0, 0, -1)))
    clap = win(t, 7.3 if key == "F" else 7.18, 8.5, 0.12) * max(0.0, math.sin(2 * math.pi * 3.2 * t + ph))
    wave = win(t, 3.3, 6.0, 0.2) * math.sin(2 * math.pi * 1.6 * t + ph)
    for j in JOINTS:
        v = list(pose.get(j, (0, 0, 0)))
        if j == "hip":
            v[0] += 1.0 * math.sin(2 * math.pi * 0.31 * t + ph)
        if j == "head":
            v[2] += 3.0 * math.sin(2 * math.pi * 0.2 * t + ph)
        if j in ("elbowR", "elbowL"):
            v[1] += (-1 if j == "elbowR" else 1) * 24 * clap
            if (key == "F") == (j == "elbowL"):
                v[1] += 24 * wave                                 # the raised hand waves
        rot(rig[j], tuple(v))
    rot(rig["root"], (0, 0, num_at(HOLO_Y[key], t)))
    rig["base"].location = (rig["base"].location.x, rig["base"].location.y, 0)


# ---------------------------------------------------------------- plates (name tags, the scoreboard): real block slabs
def slab(name, path, width=None, depth=0.14, emit=1.5, side=(0.05, 0.6, 0.7)):
    im = bpy.data.images.load(path, check_existing=True)
    w_, h_ = im.size
    W = width if width else w_ * TAGU
    H = W * h_ / w_
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.verify()
    bmesh.ops.create_cube(bm, size=1.0)
    for f_ in bm.faces:
        f_.normal_update()
        if f_.normal.z > 0.5:
            f_.material_index = 0
            for lp in f_.loops:
                lp[uvl].uv = (lp.vert.co.x + 0.5, lp.vert.co.y + 0.5)
        else:
            f_.material_index = 1
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
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
    n_.links.new(tx.outputs["Color"], em.inputs["Color"])
    n_.links.new(em.outputs[0], next(n for n in n_.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    o.data.materials.append(m)
    o.data.materials.append(emit_mat(name + "_s", side, 1.1))
    o.visible_shadow = False
    return {"o": o, "w": W, "h": H, "d": depth, "tx": tx, "em": em, "base": emit}


def tag_plane(name, path, width, emit=1.15):
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
    return {"o": o, "w": width, "h": width * h_ / w_, "d": 1.0, "tx": tx}


def place(pl, pos, s, yaw=0.0):
    o = pl["o"]
    o.location = pos
    o.scale = (max(1e-4, pl["w"] * s), max(1e-4, pl["h"] * s), max(1e-4, pl["d"] * s))
    o.hide_render = s <= 0.001
    if s > 0.001:
        face_cam(o, pos, yaw)


TAGF = slab("tag_f", os.path.join(ART, "plate_fras.png"))
TAGM = slab("tag_m", os.path.join(ART, "plate_mustafa.png"))
TAGA = slab("tag_ali", os.path.join(ART, "plate_ali.png"), width=1.3, depth=0.09, side=(0.7, 0.12, 0.08))
BUB1 = tag_plane("bub_noob", os.path.join(ART, "bubble5_noob.png"), 1.2)
BUB2 = tag_plane("bub_3iqab", os.path.join(ART, "bubble5_3iqab.png"), 1.2)
BOARDSET = os.environ.get("BOARDSET", "")   # scoreboard choice sheet (2026-11-18): art/boardset/<name>/ from board_sheet_art.py; empty = v5 as before
_BS = os.path.join(ART, "boardset", BOARDSET) if BOARDSET else ART
_BLOOK = json.load(open(os.path.join(_BS, "look.json"))) if BOARDSET else None
BOARD = slab("board", os.path.join(_BS, "board_0.png"), width=BW, depth=0.5, emit=1.25, **({"side": tuple(_BLOOK["side"])} if _BLOOK else {}))
MS.collection.objects.link(BOARD["o"])   # 2026-11-24: blue in the mask, so post5.py draws no body outline over the board
BOARD["o"].color = (0, 0, 1, 1)
SCORES = [bpy.data.images.load(os.path.join(_BS, f"board_{i}.png"), check_existing=True) for i in range(len(_BLOOK["rows_px"]) if _BLOOK else 9)]
FLY = []
if BOARDSET == "E":
    for i, row in enumerate([0, 1, 0, 1, 0, 1]):
        t1_ = 12.28 + i * 0.11   # v7E
        FLY.append((t1_ - 0.16, t1_, row))                        # only the six traded points fly in as diamonds
    SCORE_T = [f_[1] for f_ in FLY] + [12.951 + k * 0.054 for k in range(14)]   # 2026-11-24 word check: first point on "يجمع" 12.836, 64 reached on "الفايز" 13.657 (was 13.40 to 13.92)
else:
    SCORE_ROW = [0, 1, 0, 1, 0, 0, 1, 0]                          # who scores at each step (make_popups.py STEPS)
    for i, row in enumerate(SCORE_ROW):
        t1_ = 12.74 + i * 0.158
        FLY.append((t1_ - 0.34, t1_, row))
    SCORE_T = [f_[1] for f_ in FLY]
frng = random.Random(4)
FLY_SRC = [V((frng.uniform(-14, 14), frng.uniform(4, 16), frng.uniform(-24, -9))) for _ in FLY]


def row_pos(row, i=None):
    if _BLOOK and i is not None:                                    # where diamond i lands on the chosen board design
        px, py = _BLOOK["rows_px"][str(i + 1)][row]
        return BOARD_C + BSC * V(((px / 1120 - 0.5) * BW, -0.14, (340 - py) / 1120 * BW))
    return BOARD_C + BSC * V((0.95, -0.14, 0.09 if row == 0 else -0.5))


def fly_pos(i, u):
    p0, p1 = FLY_SRC[i], row_pos(FLY[i][2], i)
    e = u * u * (3 - 2 * u)
    return p0.lerp(p1, e) + V((0, -1.5, 2.2)) * math.sin(math.pi * e)


for i, (t0, t1, row) in enumerate(FLY):                           # each diamond lands with a burst
    EMIT_R.append(("cyan", t1, row_pos(row, i), 26, 1.3, 0.45, -1.0, 0.03, "sphere", 300 + i))
    EMIT_R.append(("white", t1, row_pos(row, i), 14, 1.7, 0.3, 0.0, 0.022, "star", 320 + i))


BK = bpy.data.objects.new("burst", None)
sc.collection.objects.link(BK)


def star_mesh(name, n, r0, r1, col, strength, z):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rr = random.Random(n)
    vs = []
    for i in range(2 * n):
        a = i * math.pi / n
        rad = (r1 * rr.uniform(0.8, 1.15)) if i % 2 == 0 else r0
        vs.append(bm.verts.new((rad * math.cos(a) * 1.5, rad * math.sin(a), 0)))
    bm.faces.new(vs)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.data.materials.append(emit_mat(name, col, strength))
    o.parent = BK
    o.location = (0, 0, z)
    o.visible_shadow = False
    return o


BK_S1 = star_mesh("bk_star", 11, 0.5, 0.86, (1.0, 0.45, 0.06), 2.4, -0.3)
BK_S2 = star_mesh("bk_star2", 11, 0.38, 0.62, (1.0, 0.95, 0.75), 4.0, -0.26)


# ---------------------------------------------------------------- the cube teleports (both of them)
PIECE_COLS = {"black": (0.02, 0.02, 0.025), "red": (0.9, 0.08, 0.08), "orange": (1.0, 0.45, 0.05), "yellow": (1.0, 0.9, 0.1),
              "green": (0.1, 0.85, 0.2), "blue": (0.05, 0.25, 1.0), "white": (0.9, 0.9, 0.9), "hair": (0.09, 0.07, 0.06), "skin": (0.8, 0.55, 0.36)}
PCO = {c: fx_obj("yp_" + c, col, 2.5 if c not in ("black", "hair") else 0.0) for c, col in PIECE_COLS.items()}
PIECES = {"Y": [], "P": []}
prng = random.Random(11)
for i in range(150):
    c = "black" if i < 60 else ("red", "orange", "yellow", "green", "blue", "white")[i % 6]
    PIECES["Y"].append((c, V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0))),
                        V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0))), prng.uniform(0.0, 0.22),
                        prng.uniform(0.07, 0.12), prng.uniform(-1, 1)))
    c = ("black", "hair", "black", "skin", "hair", "red")[i % 6]
    PIECES["P"].append((c, V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0))),
                        V((prng.uniform(-0.25, 0.25), prng.uniform(-0.15, 0.15), prng.uniform(0.0, 2.0))), prng.uniform(0.0, 0.22),
                        prng.uniform(0.07, 0.12), prng.uniform(-1, 1)))
TELE = [("Y", 9.60, 10.50, YL, YQ, V((0, 2.5, 1.5)), V((0, -2.0, 2.5))),   # v6 2026-11-20: burst after the "16" lands (was 9.28)
        ("P", 9.60, 10.50, PP, PQ0, V((0, 2.5, 1.5)), V((0, -2.0, 2.5)))]   # 2026-11-24 word check: burst on the heard "مرحلة" 9.97; the 13.92 burst inside "الفايز" is gone


def pieces(t):
    out = {c: [] for c in PCO}
    for who, tp0, tp1, src, dst, h0, h1 in TELE:
        if not (tp0 <= t <= tp1 + 0.02):
            continue
        for c, a0, a1, d, s, wob in PIECES[who]:
            dd = d * (tp1 - tp0) / 1.17
            u = clamp01((t - tp0 - dd) / (tp1 - tp0 - 0.25 * (tp1 - tp0) / 1.17))
            p0, p3 = src + a0, dst + a1
            p1 = p0 + (a0 - V((0, 0, 1.0))).normalized() * 1.2 + h0
            p2 = p3 + h1 + V((wob, 0, 0))
            e = ease(u)
            q = (1 - e) ** 3 * p0 + 3 * (1 - e) ** 2 * e * p1 + 3 * (1 - e) * e * e * p2 + e ** 3 * p3
            out[c].append((q, s * (0.75 + 0.25 * abs(math.cos(math.pi * e)))))
    return out


def visible(who, t):
    return not any(w == who and a + 0.04 <= t < b for w, a, b, *_ in TELE)


# ---------------------------------------------------------------- props: diamond, block arrow, block digits, the block that hides the cut
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


DIAMOND = block_cube("diamond_prop", "diamond_block", 0.95, 2.2, TXE)
DIAMOND.location = DIA_C
#   B  lit, not glowing: low self-light, a soft key above shows the real texture, same tilted spin
#   C  on a pedestal: sits on a polished blackstone block, upright, slow turn only, soft key above
#   D  dropped item: smaller, spins upright and bobs like an item on the ground in the game
DIASET = os.environ.get("DIASET", "")
DIA_PED = None
if DIASET in ("B", "C", "D"):
    DIAMOND.data.materials[0] = block_mat("diamond_prop_" + DIASET, "diamond_block", emit={"B": 0.25, "C": 0.6, "D": 0.9}[DIASET],
                                          rough=0.2, texdir=TXE)
    area("dia_key", DIA_C + V((0.6, -2.2, 2.6)), DIA_C, {"B": 160.0, "C": 140.0, "D": 90.0}[DIASET], (1.0, 0.92, 0.82), 1.2, linked=False)
if DIASET == "C":
    DIA_PED = block_cube("dia_ped", "polished_blackstone", 0.95, 0.05, T121)
WIPE = block_cube("wipe", "orange_wool", 2.6, 0.32, T121S, uvs=3.0)
WIPE.hide_render = True
WIPES = []   # v7D s18: hard cut at 14.04 on the end of "الفايز", no whoosh. v7C r2: plain hard cut at 14.075 in the silence; the orange wipe (14.03-14.08) read as a full-screen blink. Was [(14.075, 0.13)].   # v7C: was 14.425 (that was inside the real "اوووو")                                          # (the hidden cut's time, how long the block takes to pass)


def arrow_mat():
    """gold blocks with a band of light that sweeps along the arrow (the value node)"""
    m = bpy.data.materials.new("arrow_f")
    m.use_nodes = True
    nt_ = m.node_tree
    b_ = nt_.nodes["Principled BSDF"]
    b_.inputs["Base Color"].default_value = (1.0, 0.55, 0.05, 1)
    b_.inputs["Emission Color"].default_value = (1.0, 0.42, 0.02, 1)
    tc, sp = nt_.nodes.new("ShaderNodeTexCoord"), nt_.nodes.new("ShaderNodeSeparateXYZ")
    nt_.links.new(tc.outputs["Object"], sp.inputs[0])
    val = nt_.nodes.new("ShaderNodeValue")
    sub, ab, mul, mn, one, gain = (nt_.nodes.new("ShaderNodeMath") for _ in range(6))
    sub.operation, ab.operation, mul.operation, mn.operation, one.operation, gain.operation = "SUBTRACT", "ABSOLUTE", "MULTIPLY", "MINIMUM", "SUBTRACT", "MULTIPLY_ADD"
    nt_.links.new(sp.outputs["X"], sub.inputs[0])
    nt_.links.new(val.outputs[0], sub.inputs[1])
    nt_.links.new(sub.outputs[0], ab.inputs[0])
    nt_.links.new(ab.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = 3.2
    nt_.links.new(mul.outputs[0], mn.inputs[0])
    mn.inputs[1].default_value = 1.0
    one.inputs[0].default_value = 1.0
    nt_.links.new(mn.outputs[0], one.inputs[1])
    nt_.links.new(one.outputs[0], gain.inputs[0])
    gain.inputs[1].default_value = 2.2
    gain.inputs[2].default_value = 0.85
    nt_.links.new(gain.outputs[0], b_.inputs["Emission Strength"])
    return m, val, gain


ARR_ROWS = ["........#.....", "........##....", "........###...", "........####..", "#############.", "##############", "#############.", "........####..",
            "........###...", "........##....", "........#....."]
ARR_F, ARR_V, ARR_G = arrow_mat()
ARROW = pixel_mesh("arrow", ARR_ROWS, 0.075, 0.34, {"#": (ARR_F, emit_mat("arrow_s", (0.75, 0.16, 0.02), 0.9))})


#   B  a Minecraft arrow (flint head, wooden shaft, white feathers) drawn as real blocks, no glow sweep
#   C  no arrow: a thin beacon beam falls on the diamond from above
#   D  three gold chevrons that light up one after another toward the diamond
ARROWSET = os.environ.get("ARROWSET", "")
ARR_B = ARR_C = None
ARR_D = []
if ARROWSET == "B":
    _fl, _wd, _ft = (emit_mat("arrB_flint", (0.22, 0.22, 0.24), 0.6), emit_mat("arrB_wood", (0.42, 0.26, 0.12), 0.55),
                     emit_mat("arrB_feather", (0.92, 0.92, 0.9), 0.7))
    ARR_B = pixel_mesh("arrow_mc", ["ff.........h....", "fff........hhh..", ".ffwwwwwwwwhhhhh", "fff........hhh..",
                                    "ff.........h...."], 0.11, 0.13, {"f": (_ft, _ft), "w": (_wd, _wd), "h": (_fl, _fl)})
if ARROWSET == "C":
    ARR_C = block_cube("beam", "diamond_block", 1.0, 0.0, TXE)
    ARR_C.data.materials[0] = emit_mat("beam_m", (0.45, 0.9, 1.0), 6.0)
    ARR_C.visible_shadow = False
if ARROWSET == "D":
    _g = emit_mat("chev_f", (1.0, 0.72, 0.12), 1.4)
    _gs = emit_mat("chev_s", (0.6, 0.3, 0.02), 0.8)
    ARR_D = [pixel_mesh(f"chev{i}", ["###....", ".###...", "..###..", "...###.", "..###..", ".###...", "###...."], 0.09, 0.3, {"#": (_g, _gs)})
             for i in range(3)]


def arrow_alt(pos, point_deg, s, t):
    for o in [ARROW, ARR_B, ARR_C] + ARR_D:
        if o is not None:
            o.hide_render = True
    if s <= 0.001:
        return
    q = (co.location - pos).to_track_quat("Z", "Y")
    rot = q @ Quaternion((0, 0, 1), math.radians(point_deg))
    d = rot @ V((1, 0, 0))
    if ARR_B is not None:                                           # slow hover toward the diamond, no pulse
        ARR_B.hide_render = False
        ARR_B.rotation_mode = "XYZ"
        ARR_B.rotation_euler = rot.to_euler()                       # flat to the lens, like the item sprite
        ARR_B.location = pos - d * 0.45 + d * (0.12 * math.sin(2 * math.pi * 1.1 * t) - 0.25 * (1 - s))   # head stays clear of the diamond
        ARR_B.scale = (s, s, s)
    if ARR_C is not None:                                           # the beam stands on the diamond
        ARR_C.hide_render = False
        ARR_C.location = DIA_C + UPV * (0.5 + 4.0 * s)
        ARR_C.rotation_euler = (0, 0, 0)
        w = 0.3 * (1 + 0.08 * math.sin(2 * math.pi * 1.5 * t))
        ARR_C.scale = (w, w, 8.0 * s)
    for i, o in enumerate(ARR_D):                                   # chevrons in a row, each lights in turn
        o.hide_render = False
        o.rotation_mode = "XYZ"
        o.rotation_euler = rot.to_euler()
        o.location = pos - d * 0.3 + d * (-0.6 + 0.6 * i)
        lit = max(0.0, math.cos(2 * math.pi * (1.6 * t - i / 3.0)))
        k = s * (0.85 + 0.25 * lit)
        o.scale = (k, k, k)


def arrow_at(pos, point_deg, s, t):
    """pos = its centre, point_deg = where it points on the plane facing the camera (0 right, -90 down)"""
    if ARROWSET:
        return arrow_alt(pos, point_deg, s, t)
    ARROW.hide_render = s <= 0.001
    if s <= 0.001:
        return
    q = (co.location - pos).to_track_quat("Z", "Y")
    ARROW.rotation_mode = "XYZ"
    ARROW.rotation_euler = (q @ Quaternion((0, 0, 1), math.radians(point_deg)) @ Quaternion((1, 0, 0), math.radians(-34 + 10 * math.sin(2.6 * t)))).to_euler()
    pulse = 1 + 0.06 * math.sin(2 * math.pi * 2.2 * t)
    d = q @ Quaternion((0, 0, 1), math.radians(point_deg)) @ V((1, 0, 0))
    ARROW.location = pos + d * 0.09 * math.sin(2 * math.pi * 2.2 * t)
    ARROW.scale = (s * pulse, s * pulse, s * pulse)
    ARR_V.outputs[0].default_value = -0.7 + 1.4 * ((t * 1.3) % 1.0)


DIGITS = {"1": ["...#.", "..##.", "...#.", "...#.", "...#.", "...#.", "..###"], "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
          "4": ["#..#.", "#..#.", "#..#.", "#####", "...#.", "...#.", "...#."]}
BOLD = {"1": ["..##.", ".###.", "..##.", "..##.", "..##.", "..##.", ".####"],
        "4": ["##.##", "##.##", "##.##", "#####", "#####", "...##", "...##"],
        "6": [".####", "##...", "##...", "####.", "##.##", "##.##", ".###."]}   # v6: the 16 matches the bold 14


def block_number(name, txt, px, emit, depth=None, bold=False):
    me_ = bpy.data.meshes.new(name)
    bm_ = bmesh.new()
    W = 6 * len(txt) - 1
    for di, ch in enumerate(txt):
        for ry, row in enumerate((BOLD if bold else DIGITS)[ch]):
            for rx, cell in enumerate(row):
                if cell == "#":
                    r_ = bmesh.ops.create_cube(bm_, size=px)
                    bmesh.ops.translate(bm_, vec=((di * 6 + rx - (W - 1) / 2) * px, 0, (3 - ry) * px), verts=r_["verts"])
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


N14 = block_number("n14", "14", 0.22, 3.6, bold=True)  # v6 2026-11-20: 0.22 (was 0.24), the "1" touched YoCube1's head
N14S = block_number("n14s", "14", 0.075, 1.8)
N16 = block_number("n16", "16", 0.10, 1.6, bold=True)   # v6 2026-11-20: small, above the heads in the front two-shot (was 0.42 over the shaft)
N14S.location = V((-0.1, LY + 0.35, 2.55))
N16.location = V((-0.1, LY + 0.6, 2.68))   # bottom ~0.13 over the heads, just behind the pair


def pop(t, t0, t1=99.0, d=0.22):
    """0 -> 1.12 -> 1 pop in at t0, shrink away at t1"""
    if t < t0:
        return 0.0
    u = (t - t0) / d
    s = 1.0 + 0.12 * math.sin(math.pi * min(u, 1.0)) if u < 1 else 1.0
    s *= ease(u * 1.6)
    return s * (1 - ease((t - t1) / 0.2))


def bounce(t, t0, t1=99.0, d=0.16):   # v7E
    """a springy bounce in"""
    if t < t0:
        return 0.0
    u = t - t0
    s = 1 - math.exp(-u / 0.07) * math.cos(u * 26.0)
    return max(0.0, s) * (1 - ease((t - t1) / d))   # v7E


# ---------------------------------------------------------------- the beats (body time = warped)
P_DIVE = (0.5, -18.2, 0.0)
Y_DIVE = (-0.5, -18.4, 0.0)
P4 = [(0.00, "listen"), (2.70, "listen"), (3.10, "idle"), (3.86, "idle"), (3.94, "duck"), (4.16, "duck"), (4.50, "listen"),   # v7D: ducks under the Mustafa egg (5.20, "listen"),
      (5.70, "lean_in"), (6.10, "lean_in"), (6.40, "windup"), (6.88, "windup"), (7.01, "punch"), (7.445, "punch"), (7.45, "proud"),   # v7D
      (8.40, "proud"), (8.70, "scratch"), (9.34, "scratch"),
      (10.50, "listen"), (11.47, "listen"), (11.56, "awe"), (11.62, "awe"), (11.80, "reach"), (12.20, "reach"), (12.50, "count"), (14.035, "count"),
      (14.04, "listen"), (14.13, "hands_head"), (14.86, "hands_head"), (15.00, "glance"), (15.16, "glance"), (15.36, "slump"), (16.25, "slump"), (16.36, "run"),
      (16.70, "run"), (16.78, "dive_j"), (16.96, "dive_j"), (17.1, "dive"), (18.0, "dive")]
P4Y = [(0.00, -34.0), (2.70, -34.0), (3.10, -18.0), (4.20, -18.0), (4.74, -38.0), (5.20, -38.0), (6.10, -25.0), (6.40, -24.0), (6.88, -32.0),
       (7.01, -79.0), (7.445, -79.0), (7.45, -40.0), (8.40, -50.0),   # Stage B: two-shot from 7.30, he turns to YoCube1   # v6 round 2: face turned to the lens (+32 = square on)
       (9.30, -30.0), (10.50, -12.0), (14.035, -12.0), (14.04, -8.0), (16.25, -12.0),   # 2026-11-20: these keys were lost inside the comment above (he turned away from shot 6 on)
       (16.40, 180.0), (18.0, 180.0)]
P4P = [(0.00, (PP.x, PP.y, 0.0)), (6.12, (PP.x, PP.y, 0.0)), (6.34, (0.7, -21.85, 0.0)), (6.90, (0.68, -21.82, 0.0)), (7.01, (0.05, -21.9, 0.0)),
       (7.445, (0.05, -21.9, 0.0)), (7.45, (PP.x, PP.y, 0.0)),   # Stage B: no cheat; back on his spot at the 7.30 cut
       (10.51, (PP.x, PP.y, 0.0)), (10.52, (PQ0.x, PQ0.y, PQ0.z)), (12.12, (PQ0.x, PQ0.y, PQ0.z)), (12.46, (PQ.x, PQ.y, PQ.z)), (14.035, (PQ.x, PQ.y, PQ.z)), (14.04, (PP.x, PP.y, 0.0)), (14.60, (PP.x, PP.y, 0.0)),
       (14.92, (PP.x + 0.05, PP.y - 0.45, 0.0)), (16.30, (PP.x + 0.05, PP.y - 0.45, 0.0)), (16.72, P_DIVE), (18.0, P_DIVE)]
Y4 = [(0.00, "talk_open"), (0.30, "talk_open"), (0.62, "present_l"), (1.05, "present_l"), (1.20, "hold_up"), (1.88, "hold_up"), (2.06, "talk_open"),
      (2.36, "talk_open"), (2.52, "egg_l"), (2.84, "egg_l"), (2.89, "throw_l0"), (2.95, "throw_l1"), (3.20, "throw_l1"), (3.34, "talk_open"),
      (3.72, "talk_open"), (3.84, "throw_r0"), (3.86, "throw_r0"), (3.92, "throw_r1"), (4.30, "throw_r1"), (4.55, "talk_open"),   # v7D (5.02, "present_r"), (5.40, "talk_open"),
      (5.56, "hold_up"), (5.98, "hold_up"), (6.14, "talk_open"), (6.34, "recoil"), (6.99, "recoil"), (7.01, "hit"), (7.19, "hit"), (7.20, "splat"),
      (7.445, "splat"), (7.45, "wall_sit"), (7.50, "wall_sit"), (7.80, "talk_open"), (8.66, "talk_open"),   # v7C fault 4: 7.30 was "idle" (T-pose)
      (8.80, "lean_point"), (9.08, "lean_point"), (9.25, "talk_open"), (10.45, "talk_open"), (10.75, "present_l"), (11.40, "present_l"),
      (11.55, "teach_up"), (12.08, "teach_up"), (12.46, "talk_open"), (12.70, "present_l"), (13.20, "talk_open"), (13.50, "teach_up"), (13.90, "present_l"), (14.035, "present_l"),
      (14.04, "idle"), (15.03, "idle"), (15.16, "laugh"), (16.22, "laugh"), (16.36, "run"), (16.70, "run"), (16.78, "dive_j"), (16.96, "dive_j"), (17.1, "dive"), (18.0, "dive")]
Y4Y = [(0.00, 32.0), (2.40, 34.0), (2.80, -55.0), (3.70, -55.0), (3.88, 85.0), (4.67, 85.0), (5.10, 36.0), (6.00, 36.0), (7.01, 40.0),
       (7.10, 60.0), (7.20, 90.0), (7.445, 90.0), (7.45, 20.0), (8.72, 20.0), (9.25, 22.0), (10.40, 30.0), (10.41, 14.0), (14.035, 14.0), (14.04, 38.0),   # v7E
       (16.25, 38.0), (16.40, 180.0), (18.0, 180.0)]
Y4P = [(0.00, (YP.x, YP.y, 0.0)), (6.18, (YP.x, YP.y, 0.0)), (6.42, (YP.x - 0.1, YP.y, 0.0)), (7.01, (YP.x - 0.1, YP.y, 0.0)),
       (7.445, (YP.x - 0.1, YP.y, 0.0)), (7.45, (YL.x, YL.y, 0.0)), (8.72, (YL.x, YL.y, 0.0)), (10.39, (YL.x, YL.y, 0.0)), (10.40, (YQ.x, YQ.y, YQ.z)), (12.45, (YQ.x, YQ.y, YQ.z)),   # v7E
       (12.46, (YQ2.x, YQ2.y, YQ2.z)), (14.035, (YQ2.x, YQ2.y, YQ2.z)), (14.04, (YL.x, YL.y, 0.0)), (16.30, (YL.x, YL.y, 0.0)), (16.72, Y_DIVE), (18.0, Y_DIVE)]
if DIVE == "none":                                                # Stage B: they stay on the ledge; YoCube1 talks on to 17.68
    P4 = [k for k in P4 if k[0] <= 16.25] + [(16.70, "listen"), (18.0, "listen")]   # v7D s18: "glance" swung the arms straight out at 16.50
    P4Y = [k for k in P4Y if k[0] <= 16.25] + [(18.0, -12.0)]
    P4P = [k for k in P4P if k[0] <= 16.30] + [(18.0, P4P[-3][1])]
    Y4 = [(k[0], "talk_open" if k[1] == "laugh" else k[1]) for k in Y4 if k[0] <= 16.22] + [(16.40, "talk_open"), (18.0, "talk_open")]   # v7D s18: "present_l" held one arm straight out (17.73)
    Y4Y = [k for k in Y4Y if k[0] <= 16.25] + [(18.0, 38.0)]
    Y4P = [k for k in Y4P if k[0] <= 16.30] + [(18.0, Y4P[-3][1])]
Y_HOPS = [0.20, 1.14, 4.29, 5.56, 10.60, 12.61, 13.66, 15.35]     # small hops on the big words
PH_T = [0.0, 1.96, 3.84, 5.02, 7.45, 9.22, 10.34, 12.16, 15.08, 15.94]   # a new sentence: the head tilts the other way


def tilt_at(t):
    i = max(j for j, ts in enumerate(PH_T) if ts <= t)
    tgt, prev = (-1) ** i * 9.0, ((-1) ** (i - 1) * 9.0 if i else 0.0)
    return prev + (tgt - prev) * ease((t - PH_T[i]) / 0.22)


def animate5(rig, tag, t, keys, yaws, poss, rt):
    ph = 0.0 if tag == "P" else 1.7
    pose = pose_at(keys, t)
    late = pose_at(keys, t if 7.45 <= rt < 7.50 or 14.04 <= rt < 14.15 else t - 0.05)   # v7D: cut moved to 7.34   # the arms follow the body a few frames late; v7C r2: not across the 7.30 cut (arms stayed in "splat" = T-pose to 7.35)
    for j in ("aR", "aL", "elbowR", "elbowL"):
        if j in late:
            pose[j] = late[j]
    add = {j: [0.0, 0.0, 0.0] for j in JOINTS}
    frozen = 7.01 <= rt < 7.04
    amb = 0.0 if frozen else 1.0
    add["hip"][0] += amb * 1.2 * math.sin(2 * math.pi * 0.30 * t + ph)              # breathing
    add["hip"][1] += amb * 1.8 * math.sin(2 * math.pi * 0.23 * t + ph)              # weight shift
    add["head"][0] += amb * 1.5 * math.sin(2 * math.pi * 0.31 * t + ph + 0.5)
    add["head"][2] += amb * 2.5 * math.sin(2 * math.pi * 0.17 * t + ph)
    z = 0.0
    if tag == "P":
        z += 0.10 * bump(t, 6.12, 0.26)                                             # the shout lifts him
        tr = win(rt, 6.22, 6.86, 0.06)
        add["hip"][1] += 1.4 * tr * math.sin(2 * math.pi * 11 * rt)                 # trembling with power
        add["head"][0] += 1.6 * tr * math.sin(2 * math.pi * 13 * rt + 1)
        add["head"][2] += 2.0 * tr * math.sin(2 * math.pi * 9 * rt)
        if t < 5.2 or 8.7 < t < 9.4:                                                # listening: he nods along
            add["head"][0] += 3.0 * sum(s * bump(t, ts, 0.3) for ts, s in STRESS_Y if abs(ts - t) < 0.4)
        add["elbowL"][0] += 14 * math.sin(2 * math.pi * 4.5 * t) * win(t, 8.75, 9.3)   # really scratching his head
        tick = max([bump(t, ts - 0.03, 0.14 if ts < 12.90 else 0.05) for ts in SCORE_T] + [0.0])   # Stage B: max, so the fast count stays a quick flick
        add["elbowL"][0] -= 34 * tick * win(t, 12.5, 13.95)                         # counts on every diamond
        z += 0.05 * tick * win(t, 12.5, 13.95)
        z += 0.26 * bump(t, 13.66, 0.3)                                             # happy hop
    else:
        speaking = t < 6.1 or 7.45 < t < 14.1 or t > 15.05   # v7E
        if speaking:
            for ts, wgt in Y_SYL:
                b = bump(t, ts - 0.01, 0.16)
                if b:
                    add["head"][0] += 8.0 * wgt * b                                 # nod on every syllable
                    z += 0.02 * wgt * b                                             # and a bob
            add["head"][1] += tilt_at(t)
            beat = sum(wg * bump(t, ts, 0.15) for ts, wg in Y_SYL if abs(ts - t) < 0.2)
            add["elbowR"][0] -= 22 * beat                                           # the hands bounce on the words
            add["elbowL"][0] -= 22 * beat
            add["hip"][0] += 5 * beat
            add["hip"][2] += 5 * math.sin(2 * math.pi * 0.9 * t) * beat
        for th in Y_HOPS:
            z += 0.2 * bump(t, th, 0.24)
        # v7E: the 7.34 hop is gone, he gets up instead (Y4 keys 7.45 to 7.80)

        if 15.14 <= t <= 16.22:                                                     # the laugh shakes him
            add["hip"][0] += 5 * math.sin(2 * math.pi * 5.0 * t)
            add["head"][0] += 6 * math.sin(2 * math.pi * 5.0 * t + 1)
            z += 0.05 * abs(math.sin(2 * math.pi * 5.0 * t))
        lay = rig["layers"]
        tw_ = sum(90 * d * ease((t - ts) / 0.16) for ts, d in TWISTS)              # the cube twists on stressed syllables
        lay[0].rotation_euler = (0, 0, math.radians(tw_))
        lay[2].rotation_euler = (0, 0, math.radians(-0.5 * tw_))
        lay[1].rotation_euler = (0, 0, 0)
        g = ease((rt - 7.02) / 0.28)                                                # the hit: the layers spin and settle
        if rt >= 7.02:
            lay[0].rotation_euler = (0, 0, math.radians(tw_ + 900 * g))
            lay[1].rotation_euler = (0, 0, math.radians(-720 * g))
            lay[2].rotation_euler = (0, 0, math.radians(-0.5 * tw_ + 630 * g))
    if 16.3 <= t < 16.76 and DIVE != "none":                                        # the run
        s_ = math.sin(2 * math.pi * 3.4 * (t - 16.3) + ph)
        add["legR"][0] += 38 * s_
        add["legL"][0] -= 38 * s_
        add["kneeR"][0] += 20 * max(0.0, -s_)
        add["kneeL"][0] += 20 * max(0.0, s_)
    if t >= 16.86 and DIVE != "none":                                               # the legs stream behind
        add["legR"][0] += 5 * math.sin(2 * math.pi * 7 * t + ph)
        add["legL"][0] -= 5 * math.sin(2 * math.pi * 7 * t + ph)
    for j in ("aR", "aL"):
        rig["arm" + j[1]].rotation_euler = arm_euler(pose.get(j, (0, 0, -1)))
    for j in JOINTS:
        base = pose.get(j, (0, 0, 0))
        rot(rig[j], tuple(base[i] + add[j][i] for i in range(3)))
    rot(rig["root"], (0, 0, num_at(yaws, t) + amb * 2.0 * math.sin(2 * math.pi * 0.19 * t + ph)))
    pos = num_at(poss, t)                                                           # (x, y, ground height)
    rig["base"].location = (pos[0], pos[1], 0)
    snap_feet(rig, ["legR", "legL"])
    rig["base"].location.z += z + pos[2]


def body_centre(rig, c, q):
    """place a rig by its middle, with an orientation (feet are 1 unit below the middle)"""
    rig["base"].rotation_mode = "XYZ"
    rig["base"].rotation_euler = q.to_euler()
    rig["base"].location = c - q @ V((0, 0, 1.0))


def dive_z(t, z0):
    """a head-first fall to the water: slow off the tip, faster and faster"""
    return z0 + (ZW - z0) * drop((t - 16.92) / 0.58) - 6.0 * max(0.0, t - 17.50)


def dive_mid(t):
    """the pair's middle in the fall (world)"""
    u = ease((t - 16.92) / 0.58)
    return V((0.0, -16.5 + 7.8 * u, dive_z(t, 2.1) if t >= 16.92 else 2.1))   # = the bodies' own path below


def dive_sheet(t):
    dt = t - 16.72
    for rig, st, sgn in ((P, V(P_DIVE), 1), (Y, V(Y_DIVE), -1)):
        flat = V((0, 1, -0.08)).normalized()
        down = V((sgn * 0.12, 0.22, -1.0)).normalized()          # head first, arms forward, a little apart
        q0 = V((0, 0, 1)).rotation_difference(flat)
        q1 = V((0, 0, 1)).rotation_difference(down)
        jump = st + V((0, 0, 0.9)) + V((0, 9.0 * dt, 1.4 * dt - 9.0 * dt * dt))
        if t < 16.92:
            c = jump
        else:
            u = ease((t - 16.92) / 0.58)
            c = V((st.x * (1 - u) + sgn * 0.8 * u, st.y + 1.8 + 7.8 * u, dive_z(t, jump.z if t < 16.92 else 2.1)))
        body_centre(rig, c, lerp_q(q0, q1, ease((t - 16.82) / 0.24)))
        for o in rig["meshes"]:
            o.hide_render = t >= 17.53                            # under the water


def dive_cam(t, pos, look, lens, roll):
    if t < 17.0:
        return pos, look, lens, roll                              # the hero shot at the tip stays
    m = dive_mid(t)
    if DIVE == "A":                                               # chase: the lens falls just above and behind, both big, the pool below
        cz = max(m.z + 3.4, ZW + 5.0)
        return V((0.0, m.y - 2.6, cz)), V((0.0, m.y + 0.2, max(m.z, ZW) - 2.5)), 24, 0.0
    if DIVE == "B":                                               # pool lens: low over the water, looking up the shaft; they fall at it
        return V((3.4, -3.2, ZW + 2.2)), V((-0.6, -9.6, ZW + 14.0)), 18, 0.0
    cz = max(m.z + 0.6, ZW + 2.4)                                 # side drop: the lens falls beside them, wall rushing behind
    return V((11.0, m.y - 1.5, cz)), V((0.0, m.y, max(m.z, ZW) - 0.4)), 30, 0.0


def orient(head, face):
    """a rig's rotation from where its head points and where its face looks (at rest the rig faces -y, head up)"""
    z = head.normalized()
    y = (face - z * face.dot(z)).normalized()                     # dive r2: the old minus showed backs where faces were asked for
    return Matrix((y.cross(z), y, z)).transposed().to_quaternion()


def dive_mix(t):
    """v6 mix dive: A the leap, seen from behind; B hard cut to a side fall, the rainbow wall rushing behind;
    C hard cut to the top-down water hit, both head first, faces up at the lens. Places both bodies, returns the camera."""
    if t < T_CUT1:
        dt = t - 16.72
        e = ease(dt / 0.18)
        a = math.radians(105) * ease(dt / 0.2)                    # they tip forward off the tip, head first
        mids = []
        for rig, st in ((P, V(P_DIVE)), (Y, V(Y_DIVE))):
            c = st + V((0, 9.0 * dt, 1.0 + 3.0 * dt - 12.0 * dt * dt))
            body_centre(rig, c, orient(V((0, math.sin(a), math.cos(a))), V((0, -math.cos(a), math.sin(a)))))   # same look as round 1 (fronts)
            mids.append(c)
        m = (mids[0] + mids[1]) / 2
        zoom = 11.0 * ease((dt - 0.10) / 0.08)                    # dive r2: they lie flat at the end of the leap; the lens pushes in so they stay big
        return V((0, -22.0, 3.0)).lerp(V((0, -20.0, 4.0)), e), V((0, -15.0, -1.0)).lerp(m + V((0, 0.9, -0.8)), e), 31 + zoom, 0.0   # r3: 31 start, raised hands cut the top at 34
    if t < T_CUT2:
        u = (t - T_CUT1) / (T_CUT2 - T_CUT1)
        zm = -60.0 - 30.0 * u * u - 6.0 * u                       # mid shaft, faster and faster
        for rig, s, dz, y in ((P, 1, 0.08, 2.1), (Y, -1, -0.02, 2.2)):   # r3: YoCube1 up a little, its face sat on the caption
            body_centre(rig, V((s * 0.75, y, zm + dz)), orient(V((s * 0.12, -0.05, -1.0)), V((0, -1, 0))))
        cz = zm + 0.1 + 0.1 * u - 0.12
        return V((0, -2.3, cz)), V((0, 2.1, cz - 0.15)), 29, 0.0  # dive r2: closer (was 62-67%); r3: look higher, feet got no top room
    if t < T_WET:
        zc = MIX_ZC + 60.0 * (T_WET - t)                          # the lens falls with them, the water rushes up
    else:
        zc = MIX_ZC - 0.7 * (1 - math.exp(-(t - T_WET) / 0.025))  # it stops hard above the water (r3: 1.5 pushed into the feet)
    for rig, s in ((P, 1), (Y, -1)):
        if t < T_WET:
            zb = zc - MIX_H - 0.4 * (T_WET - t) / (T_WET - T_CUT2)
        else:
            zb = MIX_ZC - MIX_H - 24.0 * (t - T_WET)              # into the water
        body_centre(rig, V((s * 0.9, MIX_CY + MIX_DY, zb)), orient(mix_dir(s), V((0, 0, 1))))
        if t >= T_WET + 0.12:
            for o in rig["meshes"]:
                o.hide_render = True                              # under the water
    cam = V((0, MIX_CY, zc))
    look = V((0, MIX_CY + 0.25, zc - 3.0))
    if t >= T_WET:                                                # the hit's own jolt, gone in about 8 frames
        dt = t - T_WET
        k = 0.10 * math.exp(-dt / 0.05)
        j = V((0.6 * k * math.sin(2 * math.pi * 9 * dt + 1.2), 0.5 * k * math.cos(2 * math.pi * 12 * dt), 0.0))
        cam, look = cam + j, look + j                            # r3: move lens and aim together; moving the aim alone rolled a top-down lens ~10 degrees
    return cam, look, 26, 0.0


Y_C0 = V((-0.95, LY, 1.05))
Y_C1 = WALLP + V((0, 0, 1.6))
SPIN = V((0.55, -0.72, 0.42)).normalized()


# ---------------------------------------------------------------- shot 5: the wall really breaks (ported from the impact-feel test, 2026-11-19)
MCT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SKILLS_SEARCH", "tests", "impact-feel", "mc_rgba")
T_SLAM = 7.20                                                       # v7D: 7.20 (was 7.25) so the slumped reaction holds to "وعلي" 7.34   # Stage B 2026-11-21: the wall hit lands by 7.25 (was 7.90)
T_BREAK = T_SLAM + 2 / 60                                             # v6 2026-11-20: two crack frames, then the blocks go (was 10 frames)
CRACK_STEPS = (6, 9)                                                 # v6: one frame each
GRAV = 20.0                                                         # impact fix 2026-11-19: was 12; chunks must land inside the 1.2 s shot. Shortcut: tuned by eye, game gravity not checked


def tex_mat(name, png, tint=(1, 1, 1)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b_ = nt.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(MCT, png), check_existing=True)
    tx.interpolation = "Closest"
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1
    mix.inputs[7].default_value = (*tint, 1)
    nt.links.new(tx.outputs["Color"], mix.inputs[6])
    nt.links.new(mix.outputs[2], b_.inputs["Base Color"])
    nt.links.new(tx.outputs["Alpha"], b_.inputs["Alpha"])
    b_.inputs["Roughness"].default_value = 1.0
    m.surface_render_method = "DITHERED"
    return m


def quad_obj(name, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = c
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.visible_shadow = False
    o.hide_render = True
    return o


# cracks: the game's own crack overlay on the blocks round the hole, from the slam frame on
CRACKS = []
_cm = {k: tex_mat("crack%d" % k, "crack_%d.png" % k, (0.06, 0.05, 0.05)) for k in (5, 9)}   # bigger break: dark cracks, not white speckle
_hole = {(y, z) for (x, y, z), k in CRATER}
for y in range(-30, -22):
    for z in range(0, 6):
        if (y, z) in _hole:
            continue
        ring = min(max(abs(y - hy), abs(z - hz)) for hy, hz in _hole)
        if ring > 2:
            continue
        o = quad_obj("crack_%d_%d" % (y, z), _cm[9 if ring == 1 else 5])
        o.location = (-4.996, y + 0.5, z + 0.5)
        o.rotation_euler = (math.radians(90), 0, math.radians(90))
        CRACKS.append(o)

# It sits behind the crater blocks, so it only shows once they break.
_hy = [y for (x, y, z), k in CRATER]
_hz = [z for (x, y, z), k in CRATER]
_y0, _y1, _z1 = min(_hy) + 0.01, max(_hy) + 0.99, max(_hz) + 0.99
_x0, _x1 = -6.99, -5.0
_hv = [(_x0, _y0, 0), (_x0, _y1, 0), (_x0, _y1, _z1), (_x0, _y0, _z1),
       (_x1, _y0, 0), (_x1, _y1, 0), (_x1, _y1, _z1), (_x1, _y0, _z1)]
_hm = bpy.data.meshes.new("hole_dark")
_hm.from_pydata(_hv, [], [(0, 1, 2, 3), (0, 4, 7, 3), (1, 5, 6, 2), (3, 2, 6, 7)])   # back, two sides, roof
_hmat = bpy.data.materials.new("hole_dark")
_hmat.use_nodes = True
_hb = _hmat.node_tree.nodes["Principled BSDF"]
_hb.inputs["Base Color"].default_value = (0.012, 0.01, 0.01, 1)
_hb.inputs["Roughness"].default_value = 1.0
_hm.materials.append(_hmat)
HOLE_DARK = bpy.data.objects.new("hole_dark", _hm)
sc.collection.objects.link(HOLE_DARK)

# ROUND 4: growing cracks on the hole blocks themselves, between the hit and the break
_pm = {k: tex_mat("pcrack%d" % k, "crack_%d.png" % k, (0.06, 0.05, 0.05)) for k in CRACK_STEPS}
PRE = []
for (x, y, z), k in CRATER:
    o = quad_obj("pcrack_%d_%d" % (y, z), _pm[CRACK_STEPS[0]])
    o.location = (-4.996, y + 0.5, z + 0.5)
    o.rotation_euler = (math.radians(90), 0, math.radians(90))
    PRE.append(o)

# debris: each hole block -> 4 half-cubes + 6 quarter-cubes in its own wool colour, still until the slam
DEB_MATS = list(dict.fromkeys(kinds[k][1]["side"] for p_, k in CRATER))
DEB = bpy.data.objects.new("debris", bpy.data.meshes.new("debris"))
MS.collection.objects.link(DEB)   # v7E: blue in the mask, so no outline is drawn over the blocks in front of him
DEB.color = (0, 0, 1, 1)
sc.collection.objects.link(DEB)
for m_ in DEB_MATS:
    DEB.data.materials.append(m_)
_rr = random.Random(7)
WALL_PIECES = []
for (x, y, z), k in CRATER:
    for sz in (0.45, 0.35, 0.3, 0.3, 0.2, 0.15, 0.15, 0.15):          # v6: more and bigger chunks for the big hole
        side = 1 if y >= -26 else -1
        c0 = V((x + 0.8 + _rr.uniform(-0.2, 0.2), y + 0.5 + side * _rr.uniform(0.0, 0.4), max(sz / 2 + 0.02, z + _rr.uniform(0.1, 0.9))))   # never starts under the floor
        v0 = V((_rr.uniform(2.0, 4.0), side * _rr.uniform(2.5, 5.0), _rr.uniform(1.0, 3.5)))   # v6: flung harder; sideways, so YoCube shows in the hole
        ax = V((_rr.uniform(-1, 1), _rr.uniform(-1, 1), _rr.uniform(-1, 1))).normalized()
        WALL_PIECES.append((c0, v0, ax, _rr.uniform(1.0, 3.0), sz, DEB_MATS.index(kinds[k][1]["side"]),
                       [(_rr.randrange(4) * 0.25, _rr.randrange(4) * 0.25) for _ in range(6)]))


def piece_at(c0, v0, ax, rps, sz, age):
    """ballistic flight, then it lands, skids 0.15 s and lies still"""
    floor = sz / 2                                                  # shot 5 fix: the gap under the wall is filled again
    a_, b_, c_ = -GRAV / 2, v0.z, c0.z - floor                      # z(t) = floor -> landing time
    tl = (-b_ - math.sqrt(b_ * b_ - 4 * a_ * c_)) / (2 * a_)
    ta = min(age, tl)
    p = c0 + V((v0.x * ta, v0.y * ta, v0.z * ta - GRAV * ta * ta / 2))
    if age > tl:
        k = min(age - tl, 0.15)
        p += V((v0.x, v0.y, 0)) * (0.25 * (k - k * k / 0.3))
        p.z = floor
    ang = 2 * math.pi * rps * ta
    return p, Quaternion(ax, ang)


def fill_debris(age):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.verify()
    for c0, v0, ax, rps, sz, mi, tiles in WALL_PIECES:
        p, q = piece_at(c0, v0, ax, rps, sz, age)
        r_ = bmesh.ops.create_cube(bm, size=sz)
        bmesh.ops.rotate(bm, verts=r_["verts"], cent=(0, 0, 0), matrix=q.to_matrix())
        bmesh.ops.translate(bm, vec=p, verts=r_["verts"])
        fs = {f for v in r_["verts"] for f in v.link_faces}
        for f, (u0, v0_) in zip(fs, tiles):
            f.material_index = mi
            w = 0.25 if sz < 0.3 else (0.75 if sz > 0.35 else 0.5)
            u0, v0_ = min(u0, 1 - w), min(v0_, 1 - w)
            for lp, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                lp[uvl].uv = (u0 + uv[0] * w, v0_ + uv[1] * w)
    bm.to_mesh(DEB.data)
    bm.free()
    DEB.data.update()


# dust: the game's own puff frames on camera-facing cards, short and grey, never glowing
DUST_M = [tex_mat("dustf%d" % i, "generic_%d.png" % (7 - i // 2), (0.4, 0.38, 0.36)) for i in range(16)]   # ROUND 4: darker grey
DUSTS = []
for i in range(18):
    o = quad_obj("dustc%d" % i, DUST_M[0])
    sg = _rr.choice((-1, 1))
    DUSTS.append((o, T_BREAK + _rr.randrange(4) / 60, _rr.uniform(0.5, 0.75), _rr.uniform(0.6, 1.0),
                  V((-4.8 + _rr.uniform(0.0, 0.3), -26.05 + sg * _rr.uniform(2.3, 3.0), _rr.uniform(0.2, 3.6))),
                  V((_rr.uniform(0.3, 0.8), sg * _rr.uniform(0.4, 0.9), _rr.uniform(0.0, 0.3)))))

for i in range(8):
    o = quad_obj("dusts%d" % i, DUST_M[0])
    sg = _rr.choice((-1, 1))
    DUSTS.append((o, T_SLAM + _rr.randrange(2) / 60, _rr.uniform(0.35, 0.5), _rr.uniform(0.5, 0.8),
                  V((-4.75, -26.05 + sg * _rr.uniform(0.8, 1.6), _rr.uniform(0.8, 3.0))),
                  V((_rr.uniform(0.6, 1.2), sg * _rr.uniform(0.5, 1.2), _rr.uniform(0.0, 0.3)))))

RIM = bpy.data.objects.new("hole_rim", bpy.data.lights.new("hole_rim", "POINT"))
RIM.data.color = (1.0, 0.75, 0.5)
RIM.data.shadow_soft_size = 0.4
RIM.location = (-6.5, -25.5, 1.2)                             # v7E: behind him as the camera sees it, so the wall of the hole lights up round the black suit
sc.collection.objects.link(RIM)
FILL = bpy.data.objects.new("hole_fill", bpy.data.lights.new("hole_fill", "POINT"))   # v7E: light on his front in the hole
FILL.data.shadow_soft_size = 0.5
FILL.location = (-3.4, -27.6, 1.7)
sc.collection.objects.link(FILL)


def wall_break(t, pos):
    """t is the gag clock: real time up to the slam, body time (slow-mo) after it"""
    broken = t >= T_BREAK
    hit = T_SLAM <= t < T_BREAK
    st = CRACK_STEPS[min(len(CRACK_STEPS) - 1, int((t - T_SLAM) * 60 + 1e-6))] if hit else CRACK_STEPS[0]
    for o in PRE:
        o.hide_render = not hit
        o.data.materials[0] = _pm[st]
    for o in CRATER_OBJ:
        o.hide_render = broken
    for o in CRACKS:
        o.hide_render = not (broken or hit)                       # v6: cracks round the hole from the contact frame
    DEB.hide_render = not broken
    RIM.data.energy = 420.0 if broken and t < 7.45 else 0.0   # v7E: on from the break, no ramp
    FILL.data.energy = 260.0 if broken and t < 7.45 else 0.0   # v7E
    if broken:
        fill_debris(t - T_BREAK)
    for o, t0, life, sz, p0, vel in DUSTS:
        age = t - t0
        o.hide_render = not (0 <= age < life)
        if o.hide_render:
            continue
        o.data.materials[0] = DUST_M[min(15, int(16 * age / life))]
        o.location = p0 + vel * age
        o.scale = (sz, sz, sz)
        o.rotation_euler = (pos - o.location).to_track_quat("Z", "Y").to_euler()



def y_gag(t):
    """shot 5 (gag clock: real time to the slam, slow-mo body time after): knocked back on an eased arc, slams flat on the wool wall at T_SLAM, breaks in, slumps down and sits"""
    Y["base"].scale = (1, 1, 1)
    if 7.04 <= t < T_SLAM:
        u = (t - 7.04) / (T_SLAM - 7.04)
        u = 0.4 * (1 - (1 - u) ** 2) + 0.6 * u                    # eased: fast off the punch, still quick into the wall
        c = Y_C0.lerp(Y_C1, u) + UPV * 0.45 * math.sin(math.pi * u)
        body_centre(Y, c, Quaternion(SPIN, math.radians(360 * max(0.0, (u - 0.2) / 0.8))))
    elif T_SLAM <= t < T_BREAK:                                    # flat on the wall face while it cracks
        Y["base"].scale = (0.62, 1.16, 1.16)
        Y["base"].location = (-4.80, WALLP.y, Y_C1.z - 1.0)
    elif T_BREAK <= t < 7.45:   # v7E
        q = 1 - ease((t - T_BREAK) / 0.13)
        Y["base"].scale = (1 - 0.38 * q, 1 + 0.16 * q, 1 + 0.16 * q)
        s_ = clamp01((t - T_BREAK) / 0.21) ** 1.3                               # slides down into a sit at the hole's floor
        z_sit = Y["base"].location.z                               # animate5 already snapped the sitting legs to the floor
        Y["base"].location = (WALLP.x - 0.42 - 0.14 * q - 0.1 * s_, WALLP.y, (Y_C1.z - 1.0) * (1 - s_) + z_sit * s_)


def holo_state(key, land, t):
    rig, vals = FIG[key]
    reveal = (t - land - 0.01) / 0.24
    gone = ease((t - 5.683) / 0.066)   # v7E
    cut = -0.1 + 3.0 * ease(reveal) if reveal < 1 else 3.0
    if gone > 0:
        cut = 3.0 * (1 - gone) - 0.1
    for c_, o_ in vals:
        c_.outputs[0].default_value = cut
    on = t >= land and gone < 1 and t < 5.80  # v7D: shot 2 ends 6.10  # Stage 6 2026-11-18: guests only in shot 2 (Stage B: shot 2 ends 5.95)   # v7E
    for o in rig["meshes"]:
        o.hide_render = not on
    return on


def lerp_q(a, b, s):
    return a.slerp(b, clamp01(s))


def set_frame5(t):
    tw = warp(t)
    for rig in (P, Y):
        rig["base"].rotation_euler = (0, 0, 0)
    animate5(P, "P", tw, P4, P4Y, P4P, t)
    animate5(Y, "Y", tw, Y4, Y4Y, Y4P, t)
    g = t                                                          # Stage B: no wall slow-mo, the gag runs on the real clock
    y_gag(g)
    for who, rig in (("P", P), ("Y", Y)):
        vis = visible(who, t)
        for o in rig["meshes"]:
            o.hide_render = not vis
    shape = mouth5(t)
    P_TEX.image = MOUTH5[shape]
    if 7.02 <= t < 7.45:                                           # the stickers scramble in the flight (Stage B: clean face when he talks)
        Y_TEX.image = SCR[int((t - 7.02) * 60 / 3) % 6]
    elif 15.14 <= t < 15.3:                    # a small embarrassed glitch
        Y_TEX.image = SCR[int(t * 60 / 3) % 6]
    else:
        Y_TEX.image = Y_CLEAN
    LENS.outputs[0].default_value = lens_glow_at(t)
    for key, land in (("F", 3.14), ("M", 4.09)):
        if holo_state(key, land, t):
            animate_h(key, tw)
    upd()
    pos, look, lens, roll = cam_at(t)
    if DIVE == "none":
        pass                                                       # Stage B: no dive
    elif DIVE == "M" and t >= 16.72:                               # v6 mix dive: leap, side fall, top-down water hit
        pos, look, lens, roll = dive_mix(t)
        upd()
    elif DIVE and t >= 16.72:                                      # the sheet dives: both fall in the world, the lens follows its own rule
        dive_sheet(t)
        pos, look, lens, roll = dive_cam(t, pos, look, lens, roll)
    elif t >= 16.72:                                                 # the leap at the lens, then they fall ahead of it, head first, arms forward
        dt = t - 16.72
        for rig, st, off, sgn, yrot in ((P, V(P_DIVE), V((1.55, 1.3, -6.0)), 1, 0.0), (Y, V(Y_DIVE), V((-1.55, 1.0, -7.0)), -1, 0.0)):
            flat = V((0, 1, -0.08)).normalized()
            d1 = V((-sgn * 0.44, -0.5, -0.75)).normalized()       # down the shaft, toward the middle of the frame
            q0 = V((0, 0, 1)).rotation_difference(flat)
            q1 = Quaternion(d1, math.radians(yrot)) @ V((0, 0, 1)).rotation_difference(d1)
            path = st + V((0, 0, 0.9)) + V((0, 9.0 * dt, 1.4 * dt - 9.0 * dt * dt))
            body_centre(rig, path.lerp(pos + off, ease((t - 16.80) / 0.2)),   # fix-all: in the lens by 17.00 (no empty frame)
                        lerp_q(q0, q1, ease((t - 16.86) / 0.26)))
            if t >= 17.54:
                for o in rig["meshes"]:
                    o.hide_render = True                          # under the water
        upd()
    hp, hy = head_of(P), head_of(Y)
    co.location = pos
    q = (look - pos).to_track_quat("-Z", "Y")
    co.rotation_euler = (q @ Quaternion((0, 0, 1), math.radians(roll))).to_euler()
    cam.lens = lens
    wall_break(g, pos)                                             # shot 5: cracks, loose blocks, dust
    bpy.data.objects["sparkle"].hide_render = 6.9 <= t < 7.45      # no glowing specks during the hit
    # focus and aperture, shot by shot: the wall melts behind sharp bodies
    if t < 1.955:
        fp, fs = (hp + hy) / 2, 0.8
    elif t < 6.10:
        fp, fs = pos + (look - pos).normalized() * 8.9, 1.4           # v6: long lens, focus between the pair and the guests
    elif t < 7.45:                                                    # v7D: one punch shot 6.10-7.34
        fp, fs = pos + (look - pos).normalized() * 7.0, 5.6           # Stage B: the wide wall shot, deep focus
    elif t < 9.60:   # v7E
        fp, fs = (hp + hy) / 2, 0.9
    elif t < 9.60:   # v7E
        fp, fs = pos + (look - pos).normalized() * 6.6, 1.4           # v6: the front two-shot, focus on the pair
    elif t < 10.52:
        fp, fs = pos + (look - pos).normalized() * 12.0, 5.6           # v6: the platform after the cut
    elif t < 12.10:   # v7E
        fp, fs = (hp + hy) / 2, 0.55
    elif t < 14.04:
        fp, fs = ((hp + hy) / 2).lerp(BOARD_C, 0.4), 2.2             # Stage B: the board sits in front of the pair, keep both sharp
    elif t < 14.04:   # v7D s18: whoosh gone, empty window kept for the record (was 14.08)
        fp, fs = pos + (look - pos).normalized() * 30.0, 5.6
    elif t < 16.3:
        fp, fs = (hp + hy) / 2, 0.9
    else:
        fp, fs = (hp + hy) / 2, 5.6
    cam.dof.focus_distance = max(0.5, (fp - pos).length)
    cam.dof.aperture_fstop = fs
    subj = (hp + hy) / 2 - V((0, 0, 0.3))
    if not visible("Y", t) and t > 13.99:
        subj = hp + V((-0.7, 0, -0.3))
    if 6.10 <= t < 7.45:   # v7E
        subj = V((0.0, LY, 0.0)).lerp(V(WALLP), 0.5) + V((0, 0, 0.9))   # Stage B: between the pair and the wall
    place_lights5(pos, subj, hp, hy, t)
    set_glow(t)
    for g, cubes in particles(t, tw).items():
        fill(FXO[g], cubes)
    for o, cubes in zip(STREAK, streaks(t)):
        fill(o, cubes)
    for c, cubes in pieces(t).items():
        fill(PCO[c], cubes)
    # eggs
    for (rel, land, tgt, hand), egg, show in zip(EGG_T, EGGS, (2.50, 3.837)):   # v7D: the Mustafa egg appears in the hand on "ومصطفى" 3.837
        on = show <= t < land
        egg.hide_render = not on
        if t < rel:
            EGG_H[hand] = hand_of(Y, hand)
        if on:
            egg.location = EGG_H[hand] if t < rel else egg_pos(t, rel, land, tgt, hand)
            q_e = (pos - egg.location).to_track_quat("Z", "Y")
            spin = 0.0 if t < rel else 14.0 * (t - rel)
            egg.rotation_euler = (q_e @ Quaternion((0, 1, 0), spin) @ Quaternion((0, 0, 1), 0.3 * math.sin(9 * t))).to_euler()
    # name plates: fully in frame, gone before the close shots
    place(TAGF, STAT_F + V((0.5, 0, 2 * STAT_S + 0.54)), 1.25 * bounce(t, 3.14, 5.683, 0.066), 8.0)
    place(TAGM, STAT_M + V((-1.0, 0, 2 * STAT_S + 0.54)), 1.25 * bounce(t, 4.09, 5.683, 0.066), -8.0)   # v7E
    # numbers
    s14 = pop(t, 0.89, 2.05, 0.3)
    N14.scale = (s14, s14, s14)
    N14.hide_render = s14 <= 0.001 or t >= 1.955  # Stage 6: gone at the cut, never shrinks in shot 2
    N14.location = V((-0.78, -14.5, -4.5 + 8.42 * ease((t - 0.925) / 0.42)))
    ss = 0.0  # Stage 6 2026-11-18: the second 14 lives in the caption only
    # was: pop(t, 5.56, 5.82)  # fully gone by 6.02, before the shout close-up (2026-11-08: a shrinking 14 peeked in at f_0370)
    N14S.scale = (ss, ss, ss)
    N14S.hide_render = ss <= 0.001
    s6 = pop(t, 9.555, 99.0, 0.2)   # 2026-11-24 word check: word file 9.54, heard from about 9.60 (the old note 9.76 was wrong)   # v6 2026-11-20: lands on the spoken "16" (9.54), holds to the cut
    N16.scale = (s6, s6, s6)
    N16.hide_render = True   # gone on the burst; the level counter starts there
    # the hit
    bk = 0.0
    BK.location = HIT + V((0.0, 0.55, 0.02))
    BK.scale = (bk, bk, bk)
    BK.rotation_mode = "XYZ"
    BK.rotation_euler = ((pos - BK.location).to_track_quat("Z", "Y") @ Quaternion((0, 0, 1), math.radians(7.0))).to_euler()
    st_ = 1 + 0.2 * ease((t - 7.01) / 0.2)
    for o in (BK_S1, BK_S2):
        o.hide_render = bk <= 0.001
    BK_S1.scale = BK_S2.scale = (st_, st_, 1)
    # diamond, arrow, board
    s = pop(t, 11.547, 12.06)   # v7E
    DIAMOND.scale = (s, s, s)
    DIAMOND.rotation_euler = (0.35, 0.25, 1.4 * tw)
    DIAMOND.location = DIA_C + UPV * (0.07 * math.sin(2.4 * tw))
    if DIASET == "C":                                               # upright on its pedestal, slow turn
        DIAMOND.rotation_euler = (0, 0, 0.6 * tw)
        DIAMOND.location = DIA_C
        DIA_PED.scale = (s, s, s)
        DIA_PED.location = DIA_C - UPV * 0.95 * s
        DIA_PED.hide_render = s <= 0.001
    elif DIASET == "D":                                             # like a dropped item: small, upright spin, bob
        DIAMOND.scale = (0.55 * s, 0.55 * s, 0.55 * s)
        DIAMOND.rotation_euler = (0, 0, 1.8 * tw)
        DIAMOND.location = DIA_C + UPV * (0.12 + 0.12 * math.sin(2.0 * tw))
    DIAMOND.hide_render = s <= 0.001
    arrow_at(DIA_C + V((-0.8, -0.2, 0.32)), -18, 0.6 * pop(t, 11.547, 12.02, 0.3), t)   # v6: smaller and lower, the whole arrow in frame above YoCube1 (was -1.05/0.62, -26, 0.9)
    sb = 0.0 if t >= 14.04 else pop(t, 12.10, 99.0, 0.2)   # v7E
    last = sum(1 for x in SCORE_T if t >= x)
    tick = max([bump(t, x, 0.14 if x < 12.90 else 0.05) for x in SCORE_T] + [0.0])   # v7E
    place(BOARD, BOARD_C, BSC * sb * (1 + 0.02 * tick), -13.0)
    BOARD["tx"].image = SCORES[last]
    BOARD["em"].inputs["Strength"].default_value = BOARD["base"] * (1 + 0.35 * tick)
    # name tag, bubbles
    place(TAGA, hp + V((-0.40, -0.98, 0.54)), bounce(t, 7.73, 8.50), 6.0)   # on "الفاشل" to the cut; v6 round 2: beside his head (screen left), he fills the frame now
    place(BUB1, hp + V((-1.0, 0, 0.52)), 0.0)
    place(BUB2, hp + V((0.6, 0, 0.54)), 0.0)
    # the block that hides the cut: crosses the frame in front of the lens, covering it at the cut
    WIPE.hide_render = True
    for tc, d_ in WIPES:
        if abs(t - tc) <= d_ / 2 + 0.02:
            u = (t - tc) / (d_ / 2)
            rgt = q @ V((1, 0, 0))
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
frames = [int(v) for v in OPT["only"].split(",")] if "only" in OPT else range(f0, min(f1, FREEZE_F + 1))
for fr in frames:
    path = os.path.join(outdir, "f_%04d.png" % fr)
    if os.path.exists(path) and OPT.get("force") != "1":
        continue
    t = fr / FPS
    if "only" in OPT or fr == f0:                                  # the egg starts in the hand even when a chunk starts later
        set_frame5(min(t, 2.60))
        EGG_H["R"] = hand_of(Y, "R")
        EGG_H["L"] = hand_of(Y, "L")
        set_frame5(min(t, 3.87))
        EGG_H["R"] = hand_of(Y, "R")
    shape = set_frame5(t)
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    MS.render.filepath = os.path.join(outdir, "m_%04d.png" % fr)
    bpy.ops.render.render(write_still=True, scene="mask")
    if fr % 20 == 0:
        print("FRAME", fr, "t %.2f" % t, "mouth", shape, flush=True)
print("FULL5 DONE", len(frames))
