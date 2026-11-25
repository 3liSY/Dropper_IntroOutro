"""proof_strips.py - the lip-sync proof: for each key word, the face at every syllable (rendered by intro.py shot=proof),
under it the voice waveform of that word with a mark at each face's moment, and the word itself.
    python 03_scripts/proof_strips.py      -> 05_renders/review/v3/proof/lipsync_proof.png"""
import json
import os
import subprocess
import sys

import arabic_reshaper
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

D = os.path.join(PA.REVIEW, "v3", "proof")
man = json.load(open(os.path.join(D, "proof.json"), encoding="utf-8"))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", PA.WAV["intro"], "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32)
FONT = os.path.join(PA.FONTS, "segoeuib.ttf")
big, small = ImageFont.truetype(FONT, 34), ImageFont.truetype(FONT, 17)
NAME = {"X": "closed", "M": "lips shut", "S": "small", "A": "wide open", "O": "round", "E": "smile", "-": "nod/twist"}


def ar(s):
    return get_display(arabic_reshaper.reshape(s))


words = []
for m in man:
    if not words or words[-1][0] != (m["word"], m["ws"]):
        words.append(((m["word"], m["ws"]), []))
    words[-1][1].append(m)
T, WAVE_H = 170, 90
rows = []
for (word, ws), items in words:
    we = items[0]["we"]
    n = len(items)
    w = max(n * (T + 8) + 16, 520)
    im = Image.new("RGB", (w, T + 60 + WAVE_H + 60), (22, 22, 28))
    d = ImageDraw.Draw(im)
    for i, m in enumerate(items):
        tile = Image.open(m["file"]).convert("RGB").resize((T, T))
        im.paste(tile, (8 + i * (T + 8), 8))
        d.text((10 + i * (T + 8), T + 12), ar(m["syl"]) + "  " + NAME.get(m["plan"], m["plan"]), font=small, fill=(235, 235, 235))
        d.text((10 + i * (T + 8), T + 34), "%.2fs  shown: %s" % (m["t"], NAME.get(m["shown"], m["shown"])), font=small,
               fill=(150, 220, 255) if m["shown"] in (m["plan"], "-") else (255, 140, 120))
    a, b = ws - 0.08, we + 0.08                                   # the waveform of the word (+ a little air)
    seg = x[int(a * 16000): int(b * 16000)]
    y0 = T + 60
    cols = np.array_split(np.abs(seg), w - 16)
    for cx, c in enumerate(cols):
        v = float(c.max()) if len(c) else 0.0
        hh = min(1.0, v * 3.0) * WAVE_H / 2
        d.line((8 + cx, y0 + WAVE_H / 2 - hh, 8 + cx, y0 + WAVE_H / 2 + hh), fill=(120, 200, 140))
    for tm in (ws, we):
        px = 8 + (tm - a) / (b - a) * (w - 16)
        d.line((px, y0, px, y0 + WAVE_H), fill=(90, 90, 110), width=1)
    for i, m in enumerate(items):
        px = 8 + (m["t"] - a) / (b - a) * (w - 16)
        d.line((px, y0 - 4, px, y0 + WAVE_H + 4), fill=(255, 210, 80), width=2)
        d.text((px - 4, y0 + WAVE_H + 4), str(i + 1), font=small, fill=(255, 210, 80))
    who = "3liSY (mouth)" if items[0]["who"] == "P" else "YoCube1 (no mouth: nod + cube twist)"
    d.text((w - 12, y0 + WAVE_H + 22), ar(word), font=big, fill=(255, 255, 255), anchor="ra")
    d.text((12, y0 + WAVE_H + 30), "%s   %.2f-%.2f s" % (who, ws, we), font=small, fill=(200, 200, 200))
    rows.append(im)
W = max(r.width for r in rows)
sheet = Image.new("RGB", (W, sum(r.height + 6 for r in rows)), (10, 10, 12))
y = 0
for r in rows:
    sheet.paste(r, (0, y))
    y += r.height + 6
sheet.save(os.path.join(D, "lipsync_proof.png"))
print("ok", len(rows), "words", sheet.size)
