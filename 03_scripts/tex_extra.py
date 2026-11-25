"""tex_extra.py - the one block texture the game files here do not have: a diamond block (own pixel art, 16x16).
    python 03_scripts/tex_extra.py   -> 04_assets/scene/tex_extra/diamond_block.png"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

OUT = os.path.join(PA.SCENE, "tex_extra")
os.makedirs(OUT, exist_ok=True)

DARK, MID, LIGHT, SHINE, EDGE = (23, 150, 160), (46, 196, 190), (96, 240, 226), (225, 255, 250), (14, 100, 120)
# 16x16 pattern: a bright rim, diagonal facets, a few shine pixels
im = Image.new("RGB", (16, 16), MID)
px = im.load()
for y in range(16):
    for x in range(16):
        c = MID
        if (x + y) % 8 < 3:
            c = LIGHT
        if (x - y) % 8 == 0:
            c = DARK
        if x in (0, 15) or y in (0, 15):
            c = EDGE
        elif x in (1, 14) or y in (1, 14):
            c = LIGHT
        px[x, y] = c
for x, y in ((3, 3), (4, 3), (3, 4), (11, 5), (12, 5), (6, 11), (7, 11), (6, 12)):
    px[x, y] = SHINE
im.save(os.path.join(OUT, "diamond_block.png"))
print("ok", os.path.join(OUT, "diamond_block.png"))
