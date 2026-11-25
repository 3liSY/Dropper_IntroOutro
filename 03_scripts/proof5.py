"""proof5.py - the lip-sync proof for v5: 3liSY's face in the real frames at every syllable he says (ايوااااا, يا, نووب, اوووو), the
mouth shape shown, under it the voice waveform of that word with a mark at each face's moment.
YoCube1 has no mouth, so his row shows the glasses' glow against his stressed syllables.
    python 03_scripts/proof5.py [frames_dir]     -> 05_renders/review/v5/lipsync_proof.png"""
import os
import subprocess
import sys

import arabic_reshaper
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lipsync as LS  # noqa: E402
import paths as PA  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PA.RENDERS, "frames_v5_720p")
FPS = 60
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", PA.WAV["intro"], "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32)
FONT = os.path.join(PA.FONTS, "segoeuib.ttf")
big, small = ImageFont.truetype(FONT, 34), ImageFont.truetype(FONT, 17)
SHOUT = {"X": "C", "M": "C", "S": "O", "E": "O", "A": "W", "O": "W"}
TALK = {"X": "C", "M": "C", "S": "H", "E": "H", "A": "O", "O": "O"}
NAME = {"C": "closed", "H": "slightly open", "O": "open", "W": "shout"}
shape, _ = LS.track("SRB")
words, _ = LS.load()


def ar(s):
    return get_display(arabic_reshaper.reshape(s))


def warp(t):                                            # full5.py's body time is not needed: the mouth runs on the real clock
    return t


def face(f):
    p = os.path.join(SRC, "f_%04d.png" % f)
    im = Image.open(p).convert("RGB")
    m = np.asarray(Image.open(os.path.join(SRC, "m_%04d.png" % f)).convert("RGB"))[..., 0] > 90
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return im.resize((170, 96)).crop((0, 0, 170, 96))
    top = ys.min()
    h = max(90, int((ys.max() - top) * 0.3))            # the head is about the top quarter of the body
    row = m[top:top + h].any(axis=0).nonzero()[0]
    cx, cy, r = (row.min() + row.max()) // 2, top + h // 2, max(h, (row.max() - row.min()) // 2) * 0.72
    box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    return im.crop(box).resize((170, 170), Image.LANCZOS)


rows = []
for w in words:
    if w["spk"] != "SRB":
        continue
    items = []
    for t0, t1, letters, plan in LS.word_syllables(w):
        tt = t0
        for frac, s in plan:
            tm = tt + (t1 - t0) * frac / 2
            tt += (t1 - t0) * frac
            f = int(round(tm * FPS))
            m = (SHOUT if 6.05 <= tm <= 7.42 else TALK)[shape[min(f, len(shape) - 1)]]
            items.append((tm, f, m, "".join(c for c, _ in letters)))
    rows.append((w, items))
T, WH = 170, 90
Wd = max(len(it) for _, it in rows) * (T + 8) + 260
sheet = Image.new("RGB", (Wd, len(rows) * (T + WH + 50) + 20), (24, 24, 28))
d = ImageDraw.Draw(sheet)
y = 10
for w, items in rows:
    d.text((10, y + 40), ar(w["w"]), font=big, fill=(255, 255, 255))
    d.text((10, y + 90), "%.2f-%.2f s" % (w["s"], w["e"]), font=small, fill=(180, 180, 180))
    a = int(w["s"] * 16000)
    b = int(w["e"] * 16000)
    seg = x[a:b]
    X0 = 240
    Wv = len(items) * (T + 8) - 8
    wave = Image.new("RGB", (Wv, WH), (34, 34, 40))
    wd = ImageDraw.Draw(wave)
    for i in range(Wv):
        c = seg[int(i / Wv * len(seg)):int((i + 1) / Wv * len(seg)) + 1]
        v = float(np.abs(c).max()) if len(c) else 0.0
        wd.line((i, WH / 2 - v * WH * 0.9, i, WH / 2 + v * WH * 0.9), fill=(110, 200, 230))
    for i, (tm, f, m, syl) in enumerate(items):
        px = X0 + i * (T + 8)
        sheet.paste(face(f), (px, y))
        d.text((px, y + T + 2), "%s  %.2f s" % (NAME[m], tm), font=small, fill=(255, 220, 120))
        xm = int((tm - w["s"]) / (w["e"] - w["s"]) * Wv)
        wd.line((xm, 0, xm, WH), fill=(255, 220, 120), width=2)
    sheet.paste(wave, (X0, y + T + 24))
    y += T + WH + 50
out = os.path.join(PA.REVIEW, "v5", "lipsync_proof.png")
sheet.save(out)
print("ok", out)
