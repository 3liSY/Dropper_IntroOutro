"""post_full.py - the full preview's look, captions and sound, then the video and a contact sheet.
Look: bloom, S-curve, saturation, vignette, grain; faded golden until 6.1 s, flooding to full colour in 0.4 s; a zoom blur on the
dive (the rainbow rush). Captions: small thin white Arabic at the bottom, phrase by phrase from the corrected words, easing in and
out, no colour, no glow. Sound: the voice loudest, effects synthesized here about 12 dB under it, whole mix at -14 LUFS, no music.
    python 03_scripts/post_full.py [frames_dir]
Writes 05_renders/edit_full4_720p/, 05_renders/review/v3/DROPPER_intro_preview_720p.mp4 and full_sheet.png."""
import glob
import json
import math
import os
import subprocess
import sys

import arabic_reshaper
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PA.RENDERS, "frames_full4_720p")
FPS, SR = 60, 48000
DST = os.path.join(PA.RENDERS, "edit_full4_720p")
OUT = os.path.join(PA.REVIEW, "v3", "DROPPER_intro_preview_720p.mp4")
os.makedirs(DST, exist_ok=True)
RESH = arabic_reshaper.ArabicReshaper(configuration={"support_ligatures": True})


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


def rush(im, k):
    """zoom blur toward the centre: a few enlarged copies averaged"""
    if k <= 0.001:
        return im
    w, h = im.size
    acc = np.asarray(im).astype(np.float32)
    n = 7
    for i in range(1, n):
        z = 1 + k * i / (n - 1)
        cw, ch = int(w / z), int(h / z)
        x0, y0 = (w - cw) // 2, (h - ch) // 2
        acc += np.asarray(im.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)).astype(np.float32)
    return Image.fromarray((acc / n).astype(np.uint8))


# ---------------------------------------------------------------- captions
words = json.load(open(PA.WORDS_FINAL["intro"], encoding="utf-8"))
PHR = []
for w in words:
    if PHR and PHR[-1]["ph"] == w["ph"]:
        PHR[-1]["txt"] += " " + w["w"]
        PHR[-1]["e"] = w["e"]
    else:
        PHR.append({"ph": w["ph"], "txt": w["w"], "s": w["s"], "e": w["e"]})
CAPF = ImageFont.truetype(os.path.join(PA.FONTS, "segoeui.ttf"), 29)
CAPS = {}
for p in PHR:
    t = get_display(RESH.reshape(p["txt"]))
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), t, font=CAPF)
    PAD = 44
    W_, H_ = bb[2] - bb[0] + 2 * PAD, bb[3] - bb[1] + 2 * PAD
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((PAD - 14, PAD - 8, W_ - PAD + 14, H_ - PAD + 8), 18, fill=(0, 0, 0, 150))   # a soft dark pool under the line:
    sh = im.filter(ImageFilter.GaussianBlur(16))                                                    # it reads on the bright floor too
    d2 = ImageDraw.Draw(sh)
    d2.text((PAD - bb[0], PAD - bb[1]), t, font=CAPF, fill=(255, 255, 255, 255))
    CAPS[p["ph"]] = sh


def caption(im, t):
    for i, p in enumerate(PHR):
        nxt = PHR[i + 1]["s"] if i + 1 < len(PHR) else 99
        end = min(p["e"] + 0.18, nxt)
        if p["s"] - 0.05 <= t < end:
            a = min(ease((t - p["s"] + 0.05) / 0.12), 1 - ease((t - end + 0.12) / 0.12))
            c = CAPS[p["ph"]].copy()
            c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
            im.paste(c, ((im.width - c.width) // 2, im.height - c.height + 18), c)
            break
    return im


# ---------------------------------------------------------------- picture
frames = sorted(glob.glob(os.path.join(SRC, "f_*.png")))
for p in frames:
    f = int(os.path.basename(p)[2:6])
    t = f / FPS
    im = look(Image.open(p), f, 1 - ease((t - 6.10) / 0.4))
    if t > 16.9:
        im = rush(im, 0.16 * ease((t - 16.9) / 0.5))
    caption(im, t).save(os.path.join(DST, os.path.basename(p)))
dur = len(frames) / FPS
print("look", len(frames), "frames", "%.2f s" % dur)

# ---------------------------------------------------------------- sound
rng = np.random.default_rng(5)
n = int(dur * SR)
fx = np.zeros(n, dtype=np.float64)


def put(t, sig, gain=1.0):
    i = int(t * SR)
    if i >= n:
        return
    b = min(n, i + len(sig))
    fx[i:b] += gain * sig[:b - i]


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


def splash():
    x = tt(0.6)
    s = band(rng.normal(0, 1, len(x)), 200, 7000)
    return s / (np.abs(s).max() + 1e-9) * np.exp(-x / 0.16) * np.minimum(1, x / 0.01)


put(0.10, whoosh(1.7, 120, 900), 0.28)                  # the slow push over the edge
put(1.05, whoosh(0.5, 300, 2500), 0.35)                 # "14" rises
put(1.14, chime(330.0, 0.9), 0.22)
put(1.86, whoosh(0.16, 500, 5000), 0.45)                # the block passes the lens
for rel, land in ((2.60, 2.92), (3.52, 3.87)):          # spawn eggs: throw, pop, sparkle
    put(rel - 0.03, whoosh(0.32, 800, 5000), 0.3)
    put(land, pop(600, 1200), 0.6)
    put(land + 0.02, sparkle(0.6, 12), 0.45)
put(5.56, pop(800, 1400), 0.3)                          # the small "14"
put(6.06, whoosh(0.22, 400, 4000), 0.6)                 # the push-in
put(6.10, impact(), 1.0)                                # the shout lands
put(6.13, sparkle(0.6, 12), 0.5)
put(7.05, whoosh(0.65), 0.45)                           # glide back out
put(7.78, pop(), 0.5)                                   # the name tag
put(9.27, sparkle(0.5, 14), 0.55)                       # YoCube1 bursts into pieces
put(9.30, whoosh(0.70, 200, 2200), 0.55)                # rise and tip over the edge
put(9.60, pop(500, 1000), 0.4)                          # "16"
put(9.95, whoosh(0.65, 150, 1800), 0.6)                 # the slide down
NOTES = [523.25, 587.33, 659.25, 783.99, 880.0]         # a rising pentatonic run, one note per ring
for k in range(16):
    put(9.62 + 1.05 * math.sqrt(k / 15.0), chime(NOTES[k % 5] * 2 ** (k // 5)), 0.32)
put(10.42, pop(700, 1300), 0.5)                         # he rebuilds
put(10.42, sparkle(0.4, 10), 0.45)
put(10.62, pop(1100, 1900), 0.35)                       # the diamond appears
put(10.95, whoosh(0.45, 1500, 6000), 0.25)              # the arrow draws itself
put(11.50, chime(2637.0, 0.8), 0.4)                     # the diamond's glint
put(11.52, chime(3951.0, 0.6), 0.25)
put(12.10, sparkle(0.4, 10), 0.45)                      # on to ring 3
put(12.12, whoosh(0.55, 200, 2400), 0.45)
put(12.60, pop(700, 1300), 0.45)
put(12.68, pop(500, 900), 0.4)                          # the scoreboard
for i in range(8):
    put(12.75 + i * 0.17, pop(1400 + 80 * i, 1700 + 80 * i), 0.22)   # the counts tick up
put(13.05, whoosh(0.4, 1500, 6000), 0.25)
put(14.20, sparkle(0.4, 10), 0.4)
put(14.26, whoosh(0.30, 300, 4000), 0.55)               # whoosh up, the block passes
put(14.56, impact(), 0.45)                              # "اوووو"
put(15.03, pop(700, 1300), 0.45)                        # YoCube1 is back
put(15.03, sparkle(0.4, 10), 0.4)
put(15.60, pop(), 0.4)                                  # the comment bubbles
put(15.98, pop(1000, 1800), 0.4)
put(16.50, whoosh(0.4, 300, 3000), 0.45)                # the jump
put(16.80, whoosh(0.85, 120, 3500), 0.85)               # the dive
put(17.60, splash(), 1.0)                               # the splash
wind = band(rng.normal(0, 1, n), 60, 500)
fx += 0.08 * wind / (np.abs(wind).max() + 1e-9)

raw = subprocess.run(["ffmpeg", "-v", "error", "-t", "%.3f" % dur, "-i", PA.VOICE["intro"], "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                     capture_output=True, check=True).stdout
voice = np.frombuffer(raw, dtype=np.float32).astype(np.float64)[:n]
voice = np.pad(voice, (0, n - len(voice)))
vr = np.sqrt(np.mean(voice[np.abs(voice) > 0.02] ** 2))
fr_ = np.sqrt(np.mean(fx[np.abs(fx) > 1e-3] ** 2))
fx *= (vr * 10 ** (-12 / 20)) / fr_                     # effects about 12 dB under the voice
mix = voice + fx
mix /= max(1.0, np.abs(mix).max() / 0.95)
wav = os.path.join(DST, "_mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-", wav],
               input=mix.astype(np.float64).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(DST, "f_%04d.png"), "-i", wav,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "16",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", OUT], check=True)
pick = [frames[int(i * (len(frames) - 1) / 23)] for i in range(24)]
W, H = 400, 225
sheet = Image.new("RGB", (6 * W + 70, 4 * H + 50), (20, 20, 24))
for i, p in enumerate(pick):
    sheet.paste(Image.open(os.path.join(DST, os.path.basename(p))).resize((W, H)), (10 + (i % 6) * (W + 10), 10 + (i // 6) * (H + 10)))
sheet.save(os.path.join(PA.REVIEW, "v3", "full_sheet.png"))
print("ok", OUT)
