"""Faces choice sheet skins (2026-11-18): three new face sets beside today's v5 faces (A).
Each set is a folder 04_assets/art/skins/faceset/<letter>/ with 3liSY_v5_C/H/O/W.png (closed, half open, open, shout)
and YoCube1_clean.png (the head used outside the punch scramble). full5.py reads it when env FACESET=<letter>.
  B  real skins untouched: no mouth ever moves, YoCube1's own head.
  C  skin-pixel mouth: on the skin's own 8 x 8 face grid, the chin pixels darken (1 px half open, 2 px open, 4 px shout).
  D  half-step mouth: a 16 x 16 face grid, small dark mouth in the skin's own browns, no teeth, no drawn brows.
C and D also tone the two pale cheek pixels (they read as white eyes under a key light), like v5 does.
    python 03_scripts/face_sheet_skins.py"""
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

SK = os.path.join(PA.ASSETS, "art", "skins")
P0 = Image.open(os.path.join(PA.SCENE, "3liSY.png")).convert("RGBA")
Y0 = os.path.join(PA.SCENE, "YoCube1.png")
HALF, OPEN, DEEP = (150, 95, 70), (96, 50, 38), (64, 30, 24)


def cheeks(im, k):
    px = im.load()
    for yy in range((8 + 6) * k, (8 + 7) * k):
        for xx in range(8 * k, 16 * k):
            if px[xx, yy][:3] == (0xD0, 0xB7, 0xAE):
                px[xx, yy] = (0xB4, 0x96, 0x88, 255)
    return im


def fill(im, k, cells, c):
    """cells on a face grid of 8*k: (x0, y0, x1, y1) inclusive"""
    px = im.load()
    for x0, y0, x1, y1 in cells:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                px[8 * k + x, 8 * k + y] = c + (255,)


SETS = {
    "B": (1, False, {"C": [], "H": [], "O": [], "W": []}),
    "C": (1, True, {"C": [], "H": [((3, 7, 3, 7), HALF)], "O": [((3, 7, 4, 7), OPEN)], "W": [((2, 7, 5, 7), DEEP)]}),
    "D": (2, True, {"C": [], "H": [((7, 14, 8, 14), OPEN)], "O": [((6, 14, 9, 15), OPEN)],
                    "W": [((5, 14, 10, 15), DEEP), ((6, 13, 9, 13), OPEN)]}),
}
for name, (k, tone, shapes) in SETS.items():
    out = os.path.join(SK, "faceset", name)
    os.makedirs(out, exist_ok=True)
    base = P0.resize((64 * k, 64 * k), Image.NEAREST)
    if tone:
        cheeks(base, k)
    for s, cells in shapes.items():
        im = base.copy()
        for box, c in cells:
            fill(im, k, [box], c)
        im.save(os.path.join(out, f"3liSY_v5_{s}.png"))
    shutil.copyfile(Y0, os.path.join(out, "YoCube1_clean.png"))
    print(name, "ok")
