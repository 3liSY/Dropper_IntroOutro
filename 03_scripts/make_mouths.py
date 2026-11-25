"""make_mouths.py - 3liSY's mouths on his REAL skin (calm eyes, no scream eyes, no tongue), and the voice loudness per frame.

The skin is scaled 4x (nearest, so it looks the same) and only the mouth area below the fringe is redrawn on that finer grid, in the
skin's own colours. Exactly 3 small talking shapes, plus one bigger open for the shout:
    C closed, H slightly open, O open, W the shout (wide, flat top, upper teeth, brows pressed down on the hair and face layers).
Old six-shape version: 06_archive/v4_full/make_mouths.py.
    python 03_scripts/make_mouths.py
Writes 04_assets/art/skins/3liSY_v5_<C|H|O|W>.png, 05_renders/review/v3/mouths_v5_sheet.png and
04_assets/data/env_intro.json (60 fps loudness 0..1, used only to scale how far a mouth opens)."""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

OUT = os.path.join(PA.ASSETS, "art", "skins")
os.makedirs(OUT, exist_ok=True)
K = 4                                                   # finer grid: the face front becomes 32 x 32
FX, FY = 8 * K, 8 * K                                   # face front of the head at (8, 8) in the 64 x 64 skin
HX, HY = 40 * K, 8 * K                                  # the hair layer over the face
DARK, DEEP, TEETH = (0x3A, 0x18, 0x16), (0x24, 0x0E, 0x0E), (0xCE, 0xC6, 0xB8)
LINE, LIP, BROW = (0x8A, 0x4E, 0x3C), (0xA8, 0x62, 0x4A), (0x0E, 0x0C, 0x0B)


def hd(path):
    im = Image.open(path).convert("RGBA")
    return im.resize((im.width * K, im.height * K), Image.NEAREST)


def face_rect(d, x0, y0, x1, y1, c):
    """face-grid rectangle, inclusive"""
    d.rectangle((FX + x0, FY + y0, FX + x1, FY + y1), fill=c + (255,))


def brow(im, pts):
    """one pressed-down brow: a slanted stroke on the face layer, and on the hair layer where the hair has pixels"""
    px = im.load()
    for x, y in pts:
        for dy in (0, 1):
            px[FX + x, FY + y + dy] = BROW + (255,)
            if px[HX + x, HY + y + dy][3] > 0:
                px[HX + x, HY + y + dy] = BROW + (255,)


def draw(im, shape):
    d = ImageDraw.Draw(im)
    if shape == "C":                                    # closed: the skin's own mouth, a thin line so it reads
        face_rect(d, 13, 27, 18, 27, LINE)
    elif shape == "H":                                  # slightly open
        face_rect(d, 13, 26, 18, 28, DARK)
        for x, y in ((13, 28), (18, 28)):
            face_rect(d, x, y, x, y, LIP)
    elif shape == "O":                                  # open
        face_rect(d, 12, 25, 19, 29, DARK)
        face_rect(d, 13, 28, 18, 29, DEEP)
        for x, y in ((12, 25), (19, 25), (12, 29), (19, 29)):
            face_rect(d, x, y, x, y, LIP)
    elif shape == "W":                                  # the shout: wide and flat on top, narrowing to the chin
        for y, (a, b) in zip(range(24, 32), ((9, 22), (9, 22), (9, 22), (9, 22), (10, 21), (10, 21), (11, 20), (12, 19))):
            face_rect(d, a, y, b, y, DEEP if y > 27 else DARK)
        face_rect(d, 10, 24, 21, 25, TEETH)
        brow(im, [(5 + i, 13 + i // 2) for i in range(10)])
        brow(im, [(26 - i, 13 + i // 2) for i in range(10)])
    return im


base = hd(os.path.join(PA.SCENE, "3liSY.png"))
px_ = base.load()                                       # the skin's pale cheek pixels read as white eyes under a key light: toned a little toward the skin
for yy in range(FY + 24, FY + 28):
    for xx in range(FX, FX + 32):
        if px_[xx, yy][:3] == (0xD0, 0xB7, 0xAE):
            px_[xx, yy] = (0xB4, 0x96, 0x88, 255)
tiles = []
for s in "CHOW":
    im = draw(base.copy(), s)
    im.save(os.path.join(OUT, f"3liSY_v5_{s}.png"))
    face = im.crop((FX, FY, FX + 8 * K, FY + 8 * K))
    face.alpha_composite(im.crop((HX, HY, HX + 8 * K, HY + 8 * K)))
    tiles.append(face.resize((256, 256), Image.NEAREST))
sheet = Image.new("RGB", (4 * 264, 264), (40, 40, 40))
for i, t in enumerate(tiles):
    sheet.paste(t.convert("RGB"), (i * 264 + 4, 4))
os.makedirs(os.path.join(PA.REVIEW, "v3"), exist_ok=True)
sheet.save(os.path.join(PA.REVIEW, "v3", "mouths_v5_sheet.png"))

# loudness per frame at 60 fps (scales how far a mouth opens; never picks the shape)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", PA.WAV["intro"], "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32)
hop = 16000 // 60
n = len(x) // hop
rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
lo, hi = np.percentile(rms, 20), np.percentile(rms, 95)
env = np.clip((rms - lo) / max(hi - lo, 1e-6), 0, 1)
env = np.convolve(env, [0.25, 0.5, 0.25], mode="same")
json.dump({"fps": 60, "env": [round(float(v), 3) for v in env]}, open(os.path.join(PA.DATA, "env_intro.json"), "w"))
print("ok", len(tiles), "faces;", n, "loudness frames")
