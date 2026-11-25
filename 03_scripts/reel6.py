"""reel6.py - the listening reels for the v6 sound round (2026-11-21). Needs the picture from a post5 run first.

    python reel6.py <TAG> [LUFS]     # TAG = the post5 tag (frames in 05_renders/edit_v5_<TAG>); LUFS = the level the options play at (default -15)

Writes to 05_renders/review/v6/:
  REEL_sound_options.mp4  every cue with a choice: its A, B and C one after the other, the label burned in, every other cue on A.
                          All options play at one fixed gain (the all-A mix mastered to LUFS), so a louder option is really louder.
  REEL_loudness.mp4       the same 5 s (swing, punch, wall, "16") mastered to -15, -14 and -16, then turned to the same loudness,
                          so the ear hears what each level costs (squashed voice, shaved hits), not which one is louder.
Temp wavs and frames go to the system temp folder."""
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402
import sound6 as S6  # noqa: E402

SR, FPS, T_END = 48000, 60, 17.75
TAG = sys.argv[1]
OPT_LUFS = float(sys.argv[2]) if len(sys.argv) > 2 else -15.0
DST = os.path.join(PA.RENDERS, "edit_v5_%s" % TAG)
REV = os.path.join(PA.REVIEW, "v6")
os.makedirs(REV, exist_ok=True)
TMP = tempfile.mkdtemp(prefix="reel6_")
GAP = 0.4                                                     # black and silent between two clips
# cue key in OPTIONS (E = both eggs), plain name, window start and end in seconds (each window shows the cue with the picture around it)
CUES = [("O1", '"14" settles', 0.8, 2.6), ("E", "egg cracks", 2.6, 4.6), ("S1", "swing", 6.4, 7.75), ("P1", "punch", 6.4, 7.75),
        ("W1", "wall hit", 6.6, 9.3), ("N16", '"16" lands', 9.0, 10.5), ("G1", "diamond block", 10.2, 11.7), ("C1", "score slab", 12.0, 13.4),
        ("U5", "score ticks", 12.4, 14.5), ("D1", "dive", 16.2, 17.2), ("D2", "splash", 16.6, 17.75)]
LOUD = [("A", -15.0), ("B", -14.0), ("C", -16.0)]             # pick first
LOUD_WIN = (5.8, 10.8)

voice, comp_db, vr = S6.load_voice(PA.VOICE["intro"], SR, T_END)
n = int(T_END * SR)
LAST = len([x for x in os.listdir(DST) if x.startswith("e_") and x.endswith(".png")]) - 1
first = Image.open(os.path.join(DST, "e_0000.png")).convert("RGB")
W, H = first.size
try:
    BIG = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", H // 11)
    SMALL = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", H // 22)
except OSError:
    BIG = SMALL = ImageFont.load_default()
cache = {}


def mixed(choice, gain=None, target=None):
    """The mastered mix with the voice for one option set. gain fixed = real level; target = mastered to that LUFS."""
    key = (tuple(sorted(choice.items())), gain, target)
    if key not in cache:
        fx, rows = S6.build(n, SR, vr, choice)
        ww, wn = os.path.join(TMP, "w.wav"), os.path.join(TMP, "n.wav")
        lv = S6.master(voice, fx, SR, 0, n, ww, wn, gain=gain, target=target if target is not None else -14.0)
        cache[key] = (S6.read_wav(ww, SR, n), lv)
    return cache[key]


def label(im, top, sub=""):
    d = ImageDraw.Draw(im)
    x, y = W // 30, H // 22
    b = d.textbbox((x, y), top, font=BIG)
    d.rectangle((b[0] - 12, b[1] - 8, b[2] + 12, b[3] + 10), fill=(0, 0, 0))
    d.text((x, y), top, font=BIG, fill=(255, 255, 255))
    if sub:
        d.text((x, b[3] + 18), sub, font=SMALL, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    return im


class Reel:
    def __init__(self, name):
        self.name, self.k, self.audio = name, 0, []

    def frame(self, im):
        im.save(os.path.join(TMP, "%s_%05d.jpg" % (self.name, self.k)), quality=92)
        self.k += 1

    def black(self, sec, text=""):
        for _ in range(int(round(sec * FPS))):
            im = Image.new("RGB", (W, H), (0, 0, 0))
            self.frame(label(im, text) if text else im)
        self.audio.append(np.zeros(int(round(sec * FPS)) * SR // FPS))

    def clip(self, wav, t0, t1, top, sub=""):
        f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
        for f in range(f0, f1):
            self.frame(label(Image.open(os.path.join(DST, "e_%04d.png" % min(f, LAST))).convert("RGB"), top, sub))
        a = wav[f0 * SR // FPS:f1 * SR // FPS].copy()
        k = int(0.015 * SR)                                   # 15 ms fades, no clicks at the cuts
        a[:k] *= np.linspace(0, 1, k)
        a[-k:] *= np.linspace(1, 0, k)
        self.audio.append(a)

    def write(self):
        wav = os.path.join(TMP, self.name + ".wav")
        S6.write_wav(np.concatenate(self.audio), SR, wav)
        out = os.path.join(REV, "REEL_%s.mp4" % self.name)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, self.name + "_%05d.jpg"), "-i", wav,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-shortest", out], check=True)
        print("ok", out, "%.1f s" % (self.k / FPS))


# ---- options: one fixed gain for all of them, from the all-A mix mastered to OPT_LUFS
_, lvA = mixed({}, target=OPT_LUFS)
g = 10 ** (lvA["gain_db"] / 20)
print("options play at the all-A gain %.2f dB (all-A mix = %.1f LUFS, true peak %.1f)" % (lvA["gain_db"], lvA["with_voice_lufs"], lvA["with_voice_truepeak_db"]))
r = Reel("sound_options")
for i, (cue, name, t0, t1) in enumerate(CUES):
    r.black(0.9, "%d/%d  %s:  A, B, C" % (i + 1, len(CUES), name))
    opts = S6.OPTIONS["E1" if cue == "E" else cue]
    for opt in "ABC":
        wav, lv = mixed({cue: opt} if opt != "A" else {}, gain=g)
        silent = not opts[opt]
        r.clip(wav, t0, t1, "%s  -  %s%s" % (name, opt, "  (no sound)" if silent else ""),
               "true peak %.1f dB" % lv["with_voice_truepeak_db"])
        r.black(GAP)
r.write()

# ---- loudness: same 5 s at three levels, turned to the same loudness so louder does not win
r = Reel("loudness")
t0, t1 = LOUD_WIN
parts = []
for opt, tgt in LOUD:
    wav, lv = mixed({}, target=tgt)
    p = os.path.join(TMP, "lw.wav")
    S6.write_wav(wav[int(t0 * SR):int(t1 * SR)], SR, p)
    parts.append((opt, tgt, wav, S6.lufs(p)[0], lv))
ref = min(x[3] for x in parts)
for opt, tgt, wav, li, lv in parts:
    hit = lv["big_hits"].get("W1", {})
    sub = "voice squashed %.1f dB / %d ms   wall front shaved %.1f dB" % (lv["voice_peak_hold_db"], lv["voice_peak_hold_over_1db_ms"], hit.get("fx_took_db", 0))
    r.black(0.9, "Loudness %s:  %g LUFS" % (opt, tgt))
    r.clip(wav * 10 ** ((ref - li) / 20), t0, t1, "Loudness %s  (%g)" % (opt, tgt), sub)
    print("loudness %s %g: got %.1f LUFS TP %.1f, played %.1f dB down to match | %s" % (opt, tgt, lv["with_voice_lufs"], lv["with_voice_truepeak_db"], li - ref, sub))
    r.black(GAP)
r.write()
print("temp:", TMP)
