"""make_cube.py - YoCube1's head cleaned up: the skin's own Rubik's cube and grey glasses, sharp sticker squares, no mouth.
The hair layer's stray pixels and the red/orange/white smudge under the glasses go; the front gets the same 3 x 3 sticker grid as the
other five faces, with the glasses across the middle (so the top layer can twist without breaking them). Also: the lens mask (the
glasses glow on stressed words) and 6 scrambled heads for the punch (the stickers change, the glasses stay).
    python 03_scripts/make_cube.py     -> 04_assets/art/skins/YoCube1_clean.png, YoCube1_lens.png, YoCube1_scr<n>.png"""
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

OUT = os.path.join(PA.ASSETS, "art", "skins")
O_, G_, Y_, R_, B_, W_ = (0xFF, 0x77, 0x00), (0x00, 0xFF, 0x48), (0xFF, 0xFB, 0x00), (0xFF, 0x26, 0x00), (0x03, 0x2D, 0xFF), (0xFF, 0xFF, 0xFF)
GREY, BLACK = (0x81, 0x77, 0x99), (0, 0, 0)
FACES = {"top": (8, 0), "bottom": (16, 0), "right": (0, 8), "front": (8, 8), "left": (16, 8), "back": (24, 8)}
CELLS = [(cx, cy) for cy in (0, 3, 6) for cx in (0, 3, 6)]
im = Image.open(os.path.join(PA.SCENE, "YoCube1.png")).convert("RGBA")
px = im.load()


def sticker(u, v, cx, cy, c):
    for y in range(2):
        for x in range(2):
            px[u + cx + x, v + cy + y] = c + (255,)


for y in range(8):                                      # the hair layer over the face: nothing
    for x in range(8):
        px[40 + x, 8 + y] = (0, 0, 0, 0)
u, v = FACES["front"]
for y in range(8):
    for x in range(8):
        px[u + x, v + y] = BLACK + (255,)
for cell, c in zip(CELLS, (O_, G_, Y_, None, None, None, R_, O_, B_)):
    if c:
        sticker(u, v, cell[0], cell[1], c)
for x0 in (0, 5):                                       # the glasses: two 3 x 3 frames, the bridge, the lenses
    for y in range(2, 5):
        for x in range(x0, x0 + 3):
            px[u + x, v + y] = GREY + (255,)
for x in (3, 4):
    px[u + x, v + 3] = GREY + (255,)
LENS = [(u + 1, v + 3), (u + 6, v + 3)]
for p in LENS:
    px[p] = W_ + (255,)
u, v = FACES["bottom"]                                  # the bottom was nearly empty: a full sticker grid like the rest
for y in range(8):
    for x in range(8):
        px[u + x, v + y] = BLACK + (255,)
for cell, c in zip(CELLS, (W_, G_, R_, Y_, W_, O_, B_, Y_, G_)):
    sticker(u, v, cell[0], cell[1], c)
im.save(os.path.join(OUT, "YoCube1_clean.png"))

mask = Image.new("RGBA", im.size, (0, 0, 0, 255))
for p in LENS:
    mask.putpixel(p, (255, 255, 255, 255))
mask.save(os.path.join(OUT, "YoCube1_lens.png"))

rng = random.Random(7)
for n in range(6):
    s = im.copy()
    px = s.load()
    for name, (u, v) in FACES.items():
        for cell in CELLS:
            if name == "front" and cell[1] == 3:
                continue                                # the glasses stay
            if rng.random() < 0.75:
                c = rng.choice((O_, G_, Y_, R_, B_, W_))
                keep = [(cell[0] + x, cell[1] + y) for y in range(2) for x in range(2) if px[u + cell[0] + x, v + cell[1] + y][:3] == GREY]
                sticker(u, v, cell[0], cell[1], c)
                for x, y in keep:
                    px[u + x, v + y] = GREY + (255,)
    s.save(os.path.join(OUT, f"YoCube1_scr{n}.png"))
sheet = Image.new("RGB", (7 * 300, 300), (70, 70, 70))
for i, n in enumerate(["clean"] + [f"scr{k}" for k in range(6)]):
    t = Image.open(os.path.join(OUT, f"YoCube1_{n}.png")).convert("RGBA").crop((8, 8, 16, 16)).resize((288, 288), Image.NEAREST)
    sheet.paste(t, (i * 300 + 6, 6), t)
sheet.save(os.path.join(PA.REVIEW, "v3", "cube_v5_sheet.png"))
print("ok")
