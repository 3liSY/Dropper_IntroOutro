"""post_still.py - the look on top of a render: bloom on the glow, a gentle S-curve and saturation, vignette, fine film grain.
    python 03_scripts/post_still.py in.png out.png [bloom=0.55] [old=0]
old=1 adds the faded golden-hour 'fourteen years ago' look (beats 1-3)."""
import sys

import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
opt = dict(a.split("=") for a in sys.argv[3:])
bloom, old = float(opt.get("bloom", 0.55)), opt.get("old", "0") == "1"
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32) / 255.0
lum = a.max(axis=2)
hot = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None] * a                      # only the glow blooms
big = Image.fromarray((hot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(im.width / 70))
small = Image.fromarray((hot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(im.width / 240))
a = 1 - (1 - a) * (1 - bloom * np.asarray(big).astype(np.float32) / 255.0) * (1 - 0.5 * bloom * np.asarray(small).astype(np.float32) / 255.0)
a = np.clip(a, 0, 1)
a = a * a * (3 - 2 * a) * 0.55 + a * 0.45                                       # S-curve
g = a.mean(axis=2, keepdims=True)
a = np.clip(g + (a - g) * (0.55 if old else 1.18), 0, 1)                       # saturation
if old:
    a = a * np.array([1.0, 0.9, 0.74], dtype=np.float32) * 0.95 + 0.04         # warm and faded
h, w = a.shape[:2]
yy, xx = np.mgrid[0:h, 0:w]
r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
a = a * (1 - 0.32 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]                 # vignette
a = np.clip(a + np.random.default_rng(3).normal(0, 0.006, a.shape).astype(np.float32), 0, 1)   # grain
Image.fromarray((a * 255).astype(np.uint8)).save(dst)
print("ok", dst)
