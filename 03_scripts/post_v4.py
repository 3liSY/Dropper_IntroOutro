"""post_v4.py - the V4 motion test's look and sound, then the video and a contact sheet.
Look = post_clip.py's (bloom, S-curve, saturation, vignette, grain; faded golden before 6.1 s flooding to colour in 0.4 s).
Sound = the voice (loudest) + effects synthesized here, about 12 dB under it: an impact and a whoosh on the shout, whooshes on
the camera moves, a pop for the name tag, sparkles for the cube teleport, a chime per ring (rising notes, faster and faster),
a glint on the diamond, a soft wind bed. Whole mix normalized to -14 LUFS. No music.
    python 03_scripts/post_v4.py [frames_dir] [t0=6.0]
Writes 05_renders/edit_v4test_720p/, 05_renders/review/v3/DROPPER_v4_motion_test_720p.mp4 and v4_clip_sheet.png."""
import glob
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


def look(im, f, w_old, bloom=0.5):
    """post_clip.py's look (kept identical)"""
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

SRC = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(PA.RENDERS, "frames_v4test_720p")
OPT = dict(a.split("=") for a in sys.argv[1:] if "=" in a)
T0 = float(OPT.get("t0", 6.0))
FPS, SR = 60, 48000
DST = os.path.join(PA.RENDERS, "edit_v4test_720p")
OUT = os.path.join(PA.REVIEW, "v3", "DROPPER_v4_motion_test_720p.mp4")
os.makedirs(DST, exist_ok=True)

# ---------------------------------------------------------------- picture
frames = sorted(glob.glob(os.path.join(SRC, "f_*.png")))
for p in frames:
    f = int(os.path.basename(p)[2:6])
    t = T0 + f / FPS
    look(Image.open(p), f, 1 - ease((t - 6.10) / 0.4)).save(os.path.join(DST, os.path.basename(p)))
dur = len(frames) / FPS
print("look", len(frames), "frames", "%.2f s" % dur)

# ---------------------------------------------------------------- sound
rng = np.random.default_rng(5)
n = int(dur * SR)
fx = np.zeros(n, dtype=np.float64)


def put(t, sig, gain=1.0):
    i = int((t - T0) * SR)
    if i >= n or i + len(sig) <= 0:
        return
    a, b = max(0, i), min(n, i + len(sig))
    fx[a:b] += gain * sig[a - i:b - i]


def tt(d):
    return np.arange(int(d * SR)) / SR


def band(noise, lo, hi):
    sp = np.fft.rfft(noise)
    fr = np.fft.rfftfreq(len(noise), 1 / SR)
    sp[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(sp, len(noise))


def chime(f0, d=1.1):
    x = tt(d)
    s = sum(a * np.sin(2 * np.pi * f0 * m * x) for m, a in ((1, 1.0), (2.0, 0.45), (3.01, 0.22), (4.2, 0.12)))
    return s * np.exp(-x / 0.35) * np.minimum(1, x / 0.004)


def whoosh(d, lo=250, hi=2600):
    x = tt(d)
    s = band(rng.normal(0, 1, len(x)), lo, hi)
    return s / (np.abs(s).max() + 1e-9) * np.sin(np.pi * x / d) ** 2


def impact():
    x = tt(0.6)
    f = 120 * np.exp(-x / 0.12) + 42
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.18)
    crack = band(rng.normal(0, 1, len(x)), 600, 5000) * np.exp(-x / 0.03)
    return body + 0.35 * crack / (np.abs(crack).max() + 1e-9)


def pop(f0=900, f1=1600):
    x = tt(0.09)
    f = f0 + (f1 - f0) * x / 0.09
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.03)


def sparkle(d=0.45, k=9):
    out = np.zeros(int(d * SR))
    for _ in range(k):
        s = chime(rng.uniform(3000, 6500), 0.25) * 0.5
        i = int(rng.uniform(0, d - 0.25) * SR)
        out[i:i + len(s)] += s
    return out


put(6.06, whoosh(0.22, 400, 4000), 0.6)                 # the fast push-in
put(6.10, impact(), 1.0)                                # the shout lands
put(6.13, sparkle(0.6, 12), 0.5)                        # gold sparks
put(7.05, whoosh(0.65), 0.45)                           # glide back out
put(7.78, pop(), 0.5)                                   # the name tag
put(9.27, sparkle(0.5, 14), 0.55)                       # YoCube1 bursts into pieces
put(9.30, whoosh(0.70, 200, 2200), 0.55)                # rise and tip over the edge
put(9.95, whoosh(0.65, 150, 1800), 0.6)                 # the slide down
NOTES = [523.25, 587.33, 659.25, 783.99, 880.0]         # a rising pentatonic run, one note per ring
for k in range(16):
    tk = 9.62 + 1.05 * math.sqrt(k / 15.0)
    put(tk, chime(NOTES[k % 5] * 2 ** (k // 5)), 0.32)
put(10.42, pop(700, 1300), 0.5)                         # he rebuilds
put(10.42, sparkle(0.4, 10), 0.45)
put(10.62, pop(1100, 1900), 0.35)                       # the diamond appears
put(10.95, whoosh(0.45, 1500, 6000), 0.25)              # the arrow draws itself
put(11.50, chime(2637.0, 0.8), 0.4)                    # the diamond's glint
put(11.52, chime(3951.0, 0.6), 0.25)
wind = band(rng.normal(0, 1, n), 60, 500)
fx += 0.08 * wind / (np.abs(wind).max() + 1e-9)

raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % T0, "-t", "%.3f" % dur, "-i", PA.VOICE["intro"], "-f", "f32le",
                      "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
voice = np.frombuffer(raw, dtype=np.float32).astype(np.float64)[:n]
voice = np.pad(voice, (0, n - len(voice)))
vr = np.sqrt(np.mean(voice[np.abs(voice) > 0.02] ** 2)) if np.any(np.abs(voice) > 0.02) else 0.1
fr_ = np.sqrt(np.mean(fx[np.abs(fx) > 1e-3] ** 2)) if np.any(np.abs(fx) > 1e-3) else 1.0
fx *= (vr * 10 ** (-12 / 20)) / fr_                     # effects about 12 dB under the voice
mix = voice + fx
mix /= max(1.0, np.abs(mix).max() / 0.95)
wav = os.path.join(DST, "_mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-", wav],
               input=mix.astype(np.float64).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(DST, "f_%04d.png"), "-i", wav,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "16",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", OUT], check=True)
pick = [frames[int(i * (len(frames) - 1) / 15)] for i in range(16)]
W, H = 480, 270
sheet = Image.new("RGB", (4 * W + 50, 4 * H + 50), (20, 20, 24))
for i, p in enumerate(pick):
    sheet.paste(Image.open(os.path.join(DST, os.path.basename(p))).resize((W, H)), (10 + (i % 4) * (W + 10), 10 + (i // 4) * (H + 10)))
sheet.save(os.path.join(PA.REVIEW, "v3", "v4_clip_sheet.png"))
print("ok", OUT)
