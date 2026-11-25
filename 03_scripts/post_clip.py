"""post_clip.py - the look on the frames, then the clip with the voice and a contact sheet.
Look = post_still.py's (bloom on the glow, gentle S-curve, saturation, vignette, fine grain that changes every frame);
before the shout the faded golden "14 years ago" look, flooding back to full colour over 0.4 s from 6.10 s (eased).
    python 03_scripts/post_clip.py [frames_dir] [t0=6.10]
Writes 05_renders/edit_clip3_720p/, 05_renders/review/v3/DROPPER_motion_test_720p.mp4 and clip_sheet.png."""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(PA.RENDERS, "frames_clip3_720p")
OPT = dict(a.split("=") for a in sys.argv[1:] if "=" in a)
T0 = float(OPT.get("t0", 6.10))
FPS = 60
DST = os.path.join(PA.RENDERS, "edit_clip3_720p")
OUT = os.path.join(PA.REVIEW, "v3", "DROPPER_motion_test_720p.mp4")
os.makedirs(DST, exist_ok=True)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


def look(im, f, w_old, bloom=0.5):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    lum = a.max(axis=2)
    hot = Image.fromarray((np.clip((lum - 0.62) / 0.38, 0, 1)[..., None] * a * 255).astype(np.uint8))
    big = np.asarray(hot.filter(ImageFilter.GaussianBlur(im.width / 70))).astype(np.float32) / 255.0
    small = np.asarray(hot.filter(ImageFilter.GaussianBlur(im.width / 240))).astype(np.float32) / 255.0
    a = np.clip(1 - (1 - a) * (1 - bloom * big) * (1 - 0.5 * bloom * small), 0, 1)
    a = a * a * (3 - 2 * a) * 0.55 + a * 0.45
    g = a.mean(axis=2, keepdims=True)
    vivid = np.clip(g + (a - g) * 1.18, 0, 1)
    old = np.clip(g + (a - g) * 0.55, 0, 1) * np.array([1.0, 0.9, 0.74], dtype=np.float32) * 0.95 + 0.04
    a = vivid * (1 - w_old) + old * w_old
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = a * (1 - 0.32 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]
    a = np.clip(a + np.random.default_rng(1000 + f).normal(0, 0.006, a.shape).astype(np.float32), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


frames = sorted(glob.glob(os.path.join(SRC, "f_*.png")))
for p in frames:
    f = int(os.path.basename(p)[2:6])
    t = T0 + f / FPS
    look(Image.open(p), f, 1 - ease((t - 6.10) / 0.4)).save(os.path.join(DST, os.path.basename(p)))
print("look", len(frames), "frames")
dur = len(frames) / FPS
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(DST, "f_%04d.png"),
                "-ss", "%.3f" % T0, "-t", "%.3f" % dur, "-i", PA.VOICE["intro"], "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT],
               check=True)
pick = [frames[int(i * (len(frames) - 1) / 15)] for i in range(16)]
W, H = 480, 270
sheet = Image.new("RGB", (4 * W + 50, 4 * H + 50), (20, 20, 24))
for i, p in enumerate(pick):
    sheet.paste(Image.open(os.path.join(DST, os.path.basename(p))).resize((W, H)), (10 + (i % 4) * (W + 10), 10 + (i // 4) * (H + 10)))
sheet.save(os.path.join(PA.REVIEW, "v3", "clip_sheet.png"))
print("ok", OUT)
