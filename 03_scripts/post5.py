"""post5.py - the v5 look, captions and sound, then the videos and a contact sheet.

Look: bloom, S-curve, saturation, vignette, grain; a lighter faded golden until 6.1 s, flooding to full colour in 0.4 s; a flash that
decays over 0.2 s on the punch; a zoom blur on the dive. The last frames repeat one frame (the freeze), then the hard cut.
Captions: bold white Arabic at the bottom, soft dark shadow, no box, phrase by phrase from the corrected words.
Sound: real recorded files and game sounds (sound6.py), no music, about 9 dB under the voice, one static gain so the whole mix reads -14 LUFS with the voice.
    WITH_VOICE file = preview only, to check the lips.  NO_VOICE file = effects only, the same gain: the voice goes on top later.
    python 03_scripts/post5.py [frames_dir] [tag] [t0 t1]      t0 t1 = only that part of the intro (a clip)
    python 03_scripts/post5.py stills <frames_dir> <out_dir> <frame> <frame> ...       look + captions on a few frames
Writes 05_renders/edit_v5_<tag>/ (finished frames e_####.png),05_renders/review/v5/DROPPER_intro_<tag>_720p_WITH_VOICE.mp4, ..._NO_VOICE.mp4, <tag>_sheet.png."""
import glob
import json
import math
import os
import subprocess
import sys

import arabic_reshaper
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

FPS, SR = 60, 48000
T_END, NF, FREEZE_F = 17.75, 1065, 1064                # v6 mix dive: no freeze, the splash runs to the hard cut (was 1058)
FADE_F0, FADE_F1 = 1065, 1066                         # v6 mix dive: hard cut, no fade (was 1032 -> 1050, the fade to black)
T_CUT1, T_CUT2, T_WET = 16.90, 17.15, 17.30          # the same as full5.py: side fall, top-down water hit, heads touch the water
REV = os.path.join(PA.REVIEW, "v6")                    # v6 sound build 2026-11-21 (was v5)
os.makedirs(REV, exist_ok=True)
RESH = arabic_reshaper.ArabicReshaper(configuration={"support_ligatures": True})
HIT_T = 7.01
OLD_MAX = 0.42                                          # how faded the first 6 seconds are


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


GRADE = os.environ.get("GRADE", "")                    # grade choice sheet 2026-11-18: B clean, C warm film, D punchy; "" = the old v5 look
GR = {"B": dict(curve=0.25, sat=1.00, vig=0.15, glare=0.15, split=0.0, halo=0.2),
      "C": dict(curve=0.30, sat=0.95, vig=0.20, glare=0.15, split=1.0, halo=0.2),
      "D": dict(curve=0.40, sat=1.08, vig=0.18, glare=0.25, split=0.0, halo=0.2)}.get(GRADE)


def look_new(im, f, w_old, g):
    """one restrained look (shaft-look guide): no bloom, one glare only on pixels above 0.85 luma, a gentle curve"""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    hot = Image.fromarray((np.clip((lum - 0.85) / 0.15, 0, 1)[..., None] * a * 255).astype(np.uint8))
    gl = np.asarray(hot.filter(ImageFilter.GaussianBlur(im.width / 120))).astype(np.float32) / 255.0
    a = 1 - (1 - a) * (1 - g["glare"] * gl)
    a = a * a * (3 - 2 * a) * g["curve"] + a * (1 - g["curve"])
    if g["split"]:                                      # warm highlights, cool shadows, small
        lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
        a = a + (lum * np.array([0.035, 0.012, -0.03]) + (1 - lum) * np.array([-0.015, 0.0, 0.025])).astype(np.float32) * g["split"]
    m = a.mean(axis=2, keepdims=True)
    vivid = np.clip(m + (a - m) * g["sat"], 0, 1)
    old = np.clip(m + (a - m) * 0.72, 0, 1) * np.array([1.0, 0.93, 0.8], dtype=np.float32) + 0.03
    a = vivid * (1 - w_old) + old * w_old
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = a * (1 - g["vig"] * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    a = np.clip(a + np.random.default_rng(1000 + f).normal(0, 0.006, a.shape).astype(np.float32), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def look(im, f, w_old, bloom=0.5):
    if GR:
        return look_new(im, f, w_old, GR)
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    lum = a.max(axis=2)
    hot = Image.fromarray((np.clip((lum - 0.62) / 0.38, 0, 1)[..., None] * a * 255).astype(np.uint8))
    big = np.asarray(hot.filter(ImageFilter.GaussianBlur(im.width / 70))).astype(np.float32) / 255.0
    small = np.asarray(hot.filter(ImageFilter.GaussianBlur(im.width / 240))).astype(np.float32) / 255.0
    a = np.clip(1 - (1 - a) * (1 - bloom * big) * (1 - 0.5 * bloom * small), 0, 1)
    a = a * a * (3 - 2 * a) * 0.55 + a * 0.45
    g = a.mean(axis=2, keepdims=True)
    vivid = np.clip(g + (a - g) * 1.18, 0, 1)
    old = np.clip(g + (a - g) * 0.72, 0, 1) * np.array([1.0, 0.93, 0.8], dtype=np.float32) + 0.03
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


def smear(im, k):
    """v6 mix side fall: the wall streaks past the falling pair (a vertical blur, k = streak length in frame heights)"""
    if k <= 0.001:
        return im
    a = np.asarray(im).astype(np.float32)
    acc = a.copy()
    n = 8
    for i in range(1, n):
        s = int(round(k * a.shape[0] * i / (n - 1)))
        acc += np.concatenate((a[s:], np.repeat(a[-1:], s, axis=0)), axis=0) if s else a
    return Image.fromarray((acc / n).astype(np.uint8))


def flash(im, k, cx=0.41, cy=0.42):
    """a hit's flash: white from the hit point (cx, cy as frame fractions), fading out"""
    if k <= 0.003:
        return im
    a = np.asarray(im).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - cx * w) / w) ** 2 + ((yy - cy * h) / w) ** 2)
    m = (k * np.exp(-(d / 0.22) ** 2))[..., None]
    return Image.fromarray((np.clip(a + (1 - a) * m, 0, 1) * 255).astype(np.uint8))


def outline_k(t):
    """how strong the bodies' thin glowing outline is: strong in the moody opening, faint later, none on the close shots"""
    if 7.45 <= t < 8.50 or 9.60 <= t < 10.5 or t >= 16.3:   # v6: shot 5 is a close shot now, the white line read fake there
        return 0.0
    if t < 6.0:
        return 0.85
    return 0.65


def outline(im, mp, t):
    """the thin line round the bodies (mask render from full5.py), and the creators' soft cyan edge"""
    k, kh = outline_k(t), 0.0                                # v7C fault 1: the cyan creator edge read as stacked neon (was 1.0 at 3.14-5.95)
    if (k <= 0 and kh <= 0) or not os.path.exists(mp):
        return im
    s = im.width / 1280
    m = Image.open(mp).convert("RGB").resize(im.size)
    r_, g_, b_ = m.split()
    body = ImageChops.lighter(r_, g_).point(lambda v: 255 if v > 90 else 0)
    a = np.asarray(im).astype(np.float32) / 255.0

    def add(mask, others, col, width, glow, amt):
        nonlocal a
        size = 2 * max(1, round(width * s)) + 1
        ring = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(size)), mask)
        ring = ImageChops.subtract(ring, others)
        line = np.asarray(ring.filter(ImageFilter.GaussianBlur(0.6 * s))).astype(np.float32) / 255.0
        soft = np.asarray(ring.filter(ImageFilter.GaussianBlur(glow * s))).astype(np.float32) / 255.0
        w = np.clip(amt * (0.75 * line + 0.8 * soft), 0, 1)[..., None]
        a = 1 - (1 - a) * (1 - w * np.array(col, dtype=np.float32))

    if k > 0:
        s_ = im.width / 1280                                # a soft glow on the air behind them: black suits never sink into a dark wall
        halo = np.asarray(body.filter(ImageFilter.GaussianBlur(34 * s_))).astype(np.float32) / 255.0
        wide = np.asarray(body.filter(ImageFilter.GaussianBlur(90 * s_))).astype(np.float32) / 255.0
        out_ = 1 - np.asarray(body).astype(np.float32) / 255.0
        w = (np.clip(0.62 * halo + 0.5 * wide, 0, 1) * out_ * min(1.0, k / 0.65) * (GR["halo"] if GR else 0.42))[..., None]
        a = 1 - (1 - a) * (1 - w * np.array((0.82, 0.74, 1.0), dtype=np.float32))
        add(body, b_.point(lambda v: 255 if v > 90 else 0) if 12.05 < t < 14.04 or 7.20 < t < 7.45 else Image.new("L", im.size, 0), (0.95, 0.97, 1.0), 1, 4.0, k)
    if kh > 0:
        add(b_.point(lambda v: 255 if v > 90 else 0), body, (0.35, 0.95, 1.0), 2, 7.0, kh)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------- captions
words = json.load(open(PA.WORDS_FINAL["intro"], encoding="utf-8"))
PHR = []
for w in words:
    if PHR and PHR[-1]["ph"] == w["ph"]:
        PHR[-1]["txt"] += " " + w["w"]
        PHR[-1]["e"] = w["e"]
    else:
        PHR.append({"ph": w["ph"], "txt": w["w"], "s": w["s"], "e": w["e"], "spk": w["spk"], "lead": 0.033, "fi": 0.12})
CAP_COL = {"SRB": (255, 60, 60), "YoCube1": (185, 85, 255)}
CAP_FONT = r"C:\Windows\Fonts\tahomabd.ttf"                 # v7: Tahoma Bold (was Segoe UI Bold)
for p in PHR:
    if p["txt"].startswith("ايوا"):                          # shortcut: caption-only move; Stage B may move the word time itself for the lips
        p.update(s=5.70, lead=0.0, fi=0.03, end=7.45)        # v7E: heard from 5.70 (over YoYo), and "نووب" runs to 7.44; on screen until the cut
    if p["txt"].startswith("كانو"):                          # v7E: heard 4.94 to 6.17 (word file 5.02 to 6.10)
        p.update(s=4.94, e=6.17, end=6.17)
    if p["txt"].startswith("وعلي"):                          # v7E: heard 7.44
        p.update(s=7.45, lead=0.0, fi=0.04)
    if p["txt"].startswith("الماب 16"):                      # v7E: heard 9.31, and it stays while the phrase still runs
        p.update(s=9.31)
    if p["txt"].startswith("وكل مرحلة"):                     # v7E: heard "فيها" and "دايموند" (the word file had "في" and "دايمون")
        p["txt"] = "وكل مرحلة فيها قطعة دايموند"
    if p["txt"].startswith("والي"):                          # v7E: "and the one who", it read as another word
        p["txt"] = "واللي" + p["txt"][4:]
    if p["txt"].startswith("اوو"):                          # v7C: the real voice says "اوووو" from 14.12 (word file 14.56)
        p.update(s=14.12, lead=0.0, fi=0.05)
    if p["txt"].startswith("اكثر"):                         # 2026-11-24: heard from 12.16 (the word file says 12.44)
        p.update(s=12.23)                                    # v7E: 12.16 was still silence
CAP_CACHE = {}


def cap_image(p, width):
    key = (p["ph"], width)
    if key in CAP_CACHE:
        return CAP_CACHE[key]
    f = ImageFont.truetype(CAP_FONT, round(50 * width / 1280))
    t = get_display(RESH.reshape(p["txt"]))
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), t, font=f)
    pad = round(30 * width / 1280)
    W_, H_ = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    sh = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(sh).text((pad - bb[0], pad - bb[1]), t, font=f, fill=255, stroke_width=round(7 * width / 1280), stroke_fill=255)   # v7D s18: wider dark halo (was 3), purple captions sank into the purple wall 15.8-17.7
    sh = sh.filter(ImageFilter.GaussianBlur(7 * width / 1280))   # v7D s18: was 5                    # a soft dark shadow, no box
    sh = sh.point(lambda v: min(235, int(v * 3.0)))   # v7D s18: was 2.3   # v7C fault 6: darker shadow (was 1.5)
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    im.putalpha(sh)
    d = ImageDraw.Draw(im)
    d.text((pad - bb[0], pad - bb[1]), t, font=f, fill=CAP_COL[p["spk"]] + (255,),
           stroke_width=max(2, round(3 * width / 1280)), stroke_fill=(12, 6, 16, 255))   # v7C fault 6: thicker edge (was 2)   # thin dark edge keeps the colour readable
    CAP_CACHE[key] = im
    return im


def caption(im, t):
    if os.environ.get("NO_CAPTIONS"):
        return im
    low = 0
    for i, p in enumerate(PHR):
        nxt = PHR[i + 1]["s"] - PHR[i + 1]["lead"] if i + 1 < len(PHR) else 99
        end = p.get("end", min(p["e"] + 0.18, nxt, T_END))      # v7: the last caption is gone by the last frame, so it ends on black
        fo = 0.12 if "end" not in p and end < nxt else 0.0      # v7E: no early fade when the next caption follows at once or the words run to the end
        if p["s"] - p["lead"] <= t < end:
            a = ease((t - p["s"] + p["lead"] + 1 / 60) / min(p["fi"], 0.034))   # v7E: readable on its first rendered frame
            if fo:
                a = min(a, 1 - ease((t - end + fo) / fo))
            c = cap_image(p, im.width).copy()
            c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
            y = im.height - c.height - round(10 * im.width / 1280) - low
            im.paste(c, ((im.width - c.width) // 2, y), c)
            low += c.height - round(34 * im.width / 1280)
    return im


ENDING = os.environ.get("ENDING", "comments")                # Stage B 2026-11-21: "comments" = the fake comment section, no dive (full5.py ending=)
COM_T0 = 16.47                                               # v7C: first card on "عقاب" (16.48), then one every 0.2 s
# v7C 2026-11-23: x < 0.5 = left edge at x; x >= 0.5 = right edge at x. Pop order = list order, top row first. Heads (0.24-0.72, 0.18-0.45) stay clear.
COMMENTS = [("الفايز يختار صورة قناتك", "@blox_king", (90, 200, 110), 0.235, 0.085, 1.0, 0.9),
            ("الفايز يغير اسم قناتك", "@sara.mc", (200, 90, 220), 0.775, 0.085, -1.0, 0.9),
            ("كول ليمونة", "@mohd_77", (230, 90, 60), 0.508, 0.32, 1.0, 0.9),
            ("وزع ثروتك", "@xNoorx", (70, 150, 230), 0.515, 0.56, -1.0, 1.1),
            ("كول احر شطة", "@3abood", (240, 180, 50), 0.145, 0.66, -1.5, 1.15),
            ("اعترف انك نوب", "@zzz_gamer", (230, 70, 130), 0.85, 0.66, 1.5, 1.15)]
COM_GAP, COM_SC = 0.20, 1.0
COM_CACHE = {}


def comment_card(i, width):
    """one fake comment, drawn like a dark comment row: round avatar, grey handle, white words, a small like count"""
    key = (i, width)
    if key in COM_CACHE:
        return COM_CACHE[key]
    txt, handle, col = COMMENTS[i][:3]
    s = width / 1280
    fb, fs = ImageFont.truetype(CAP_FONT, round(38 * s)), ImageFont.truetype(CAP_FONT, round(20 * s))
    body = get_display(RESH.reshape(txt))
    bw = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), body, font=fb)
    W_ = max(round(285 * s), bw[2] - bw[0] + round(116 * s))
    H_ = round(122 * s)
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = max(1, round(4 * s))                                    # v7E: a Minecraft panel, square pixels: dark edge with cut corners, light bevel, dark face
    d.rectangle((u, 0, W_ - 1 - u, H_ - 1), fill=(8, 8, 10, 255))
    d.rectangle((0, u, W_ - 1, H_ - 1 - u), fill=(8, 8, 10, 255))
    d.rectangle((u, u, W_ - 1 - u, H_ - 1 - u), fill=(96, 96, 104, 255))
    d.rectangle((2 * u, 2 * u, W_ - 1 - u, H_ - 1 - u), fill=(44, 44, 50, 255))
    d.rectangle((2 * u, 2 * u, W_ - 1 - 2 * u, H_ - 1 - 2 * u), fill=(30, 30, 35, 255))
    av = round(56 * s)
    ax, ay = W_ - av - round(16 * s), round(16 * s)                 # Arabic reads right to left: the avatar sits on the right
    d.rectangle((ax, ay, ax + av, ay + av), fill=tuple(v // 2 for v in col) + (255,))   # v7E: a square head, like a skin face
    d.rectangle((ax + u, ay + u, ax + av - u, ay + av - u), fill=col + (255,))
    d.text((ax + av / 2, ay + av / 2), handle[1].upper(), font=ImageFont.truetype(CAP_FONT, round(30 * s)), fill=(255, 255, 255, 255), anchor="mm")
    rx = ax - round(14 * s)
    d.text((rx, round(14 * s)), handle, font=fs, fill=(170, 170, 178, 255), anchor="ra")
    d.text((rx, round(52 * s)), body, font=fb, fill=(255, 255, 255, 255), anchor="ra")
    d.text((round(16 * s), round(14 * s)), "%d ♥" % (120 + 97 * i), font=fs, fill=(170, 170, 178, 255), anchor="la")   # v7E: it sat on the words
    COM_CACHE[key] = im
    return im


def comments(im, t):
    """Stage B ending: the comment section pops in around the frame, one card every COM_GAP s (v7C, was 0.09), every card fully inside the frame so all six punishments read"""
    if ENDING != "comments" or t < COM_T0:
        return im
    W_, H_ = im.size
    dim = 0.25 * ease((t - COM_T0) / 0.2)
    im = im.point(lambda v: int(v * (1 - dim)))                 # the scene steps back a little so the cards read
    for i, (_, _, _, x, y, tilt, size) in enumerate(COMMENTS):
        k = ease((t - COM_T0 - COM_GAP * i) / 0.06)
        if k <= 0:
            continue
        c = comment_card(i, W_)
        sc = COM_SC * size * (0.85 + 0.15 * k)
        c = c.resize((max(1, round(c.width * sc)), max(1, round(c.height * sc))), Image.BICUBIC).rotate(tilt, Image.BICUBIC, expand=True)
        c.putalpha(c.getchannel("A").point(lambda v: int(v * k)))
        drift = round((1 - k) * 18 * W_ / 1280 + (t - COM_T0) * 4 * W_ / 1280)   # a small upward drift, like a feed scrolling
        px = min(W_ - c.width - round(0.008 * W_), max(round(0.008 * W_), round(x * W_ - c.width / 2)))
        im.paste(c, (px, max(round(0.008 * W_), round(y * H_ - c.height / 2) - drift)), c)
    return im


LEVEL_T = (9.60, 10.30, 10.55)   # v7E: one count, 1 on the spoken "16" (f576), 16 inside "مرحلة" (f618); table in v7E_word_table.md
#                              # v7C: counter ticks 1->16 during the fall, holds, fades by 10.70


def level_count(im, t):
    """v7C: a big level number ticking 1 -> 16 while the camera falls down the shaft"""
    t0, t1, t2 = LEVEL_T
    if not t0 <= t < t2:
        return im
    n = max(k for k in range(1, 17) if round(t * FPS) >= round(t0 * FPS) + round((t1 - t0) * FPS * (k - 1) / 15))
    a = 1.0 - ease((t - (t2 - 0.14)) / 0.14)
    W_, H_ = im.size
    f = ImageFont.truetype(CAP_FONT, round(120 * W_ / 1280))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((W_ // 2, round(0.17 * H_)), str(n), font=f, fill=(255, 255, 255, round(255 * a)), anchor="mm",
           stroke_width=round(6 * W_ / 1280), stroke_fill=(12, 6, 16, round(255 * a)))
    return Image.alpha_composite(im.convert("RGBA"), lay).convert(im.mode)




def finish(p, f):
    t = f / FPS
    w_old = OLD_MAX * (1 - ease((t - 6.10) / 0.4))   # v7D: on the 6.10 cut                # Stage B: the colour floods in on the shout cut (5.95)
    im = look(Image.open(p), f, w_old)
    im = outline(im, os.path.join(os.path.dirname(p), "m_%04d.png" % f), t)
    if t >= HIT_T:
        im = flash(im, 0.12 * math.exp(-(t - HIT_T) / 0.06))   # Stage 6: a small pop, no white wash
    if 7.20 <= t < 7.45:                                        # v7D: wall hit 7.20, cut 7.34   # Stage B: the wall hit lands by 7.25, the cut is at 7.30 (was 7.90)
        im = flash(im, 0.16 * math.exp(-(t - 7.20) / 0.02), 0.21, 0.39)
    if t >= T_CUT1 and ENDING != "comments":                   # the v6 dive smear only exists with the dive ending                                             # v6 mix: the side fall streaks up and down, the drop at the water zooms
        if t < T_CUT2:
            k = 0.05
            blurred = smear(im, k)
        else:
            k = 0.12 * (1 - ease((t - T_WET) / 0.05))
            blurred = rush(im, k)
        mp = os.path.join(os.path.dirname(p), "m_%04d.png" % f)
        if os.path.exists(mp) and k > 0.001:                    # the world smears, the two bodies stay sharp
            r_, g_, _ = Image.open(mp).convert("RGB").resize(im.size).split()
            m = ImageChops.lighter(r_, g_).filter(ImageFilter.GaussianBlur(1.5 * im.width / 1280))
            blurred.paste(im, (0, 0), m)
        im = blurred
    return caption(level_count(comments(im, t), t), t)


if len(sys.argv) > 1 and sys.argv[1] == "stills":
    src, dst = sys.argv[2], sys.argv[3]
    os.makedirs(dst, exist_ok=True)
    for f in sys.argv[4:]:
        finish(os.path.join(src, "f_%s.png" % f.zfill(4)), int(f)).save(os.path.join(dst, "p_%s.png" % f.zfill(4)))
    sys.exit(0)

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PA.RENDERS, "frames_v5_720p")
TAG = sys.argv[2] if len(sys.argv) > 2 else "v5_preview"
T0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
T1 = float(sys.argv[4]) if len(sys.argv) > 4 else T_END
DST = os.path.join(PA.RENDERS, "edit_v5_%s" % TAG)
os.makedirs(DST, exist_ok=True)
for old in glob.glob(os.path.join(DST, "e_*.png")):
    os.replace(old, old + ".old") if False else None

# ---------------------------------------------------------------- picture
F0, F1 = int(round(T0 * FPS)), int(round(T1 * FPS))
outn = 0
for f in range(F0, F1):
    src = min(f, FREEZE_F)
    p = os.path.join(SRC, "f_%04d.png" % src)
    if os.environ.get("FILL_GAPS") == "1":                # sound tests only: a render of every 2nd frame shows the last frame that exists
        while not os.path.exists(p) and src > 0:
            src -= 1
            p = os.path.join(SRC, "f_%04d.png" % src)
    im_ = finish(p, src)
    k_ = 1.0 - min(1.0, max(0.0, (f - FADE_F0) / (FADE_F1 - FADE_F0)))   # end fade 2026-11-19: to black before the white orb at the water
    if k_ < 1.0:
        im_ = im_.point(lambda v: int(v * k_))
    im_.save(os.path.join(DST, "e_%04d.png" % outn))
    outn += 1
dur = outn / FPS
print("look", outn, "frames", "%.2f s" % dur)

# ---------------------------------------------------------------- sound
# v6 2026-11-21: real files only, placed and mastered by sound6.py on the locked picture. The old synth cues and the wind bed
import sound6  # noqa: E402

n = int(T_END * SR)
voice, comp_db, vr = sound6.load_voice(PA.VOICE["intro"], SR, T_END)
choice = dict(kv.split("=") for kv in os.environ.get("SOUNDSET", "").split(",") if kv)
fx, rows = sound6.build(n, SR, vr, choice)
ww, wn = os.path.join(DST, "_with_voice.wav"), os.path.join(DST, "_no_voice.wav")
lv = sound6.master(voice, fx, SR, int(T0 * SR), int(T1 * SR), ww, wn,
                   target=float(os.environ.get("TARGET_LUFS", "-14")))   # 2026-11-21: loudness pick for the listening round; unset = -14 as before
g = 10 ** (lv["gain_db"] / 20)
fxg = fx * g
report = dict(soundset=choice, voice_rms_db=20 * math.log10(vr * g), fx_rms_db=20 * math.log10(np.sqrt(np.mean(fxg[np.abs(fxg) > 1e-3] ** 2))),
              voice_comp_max_db=comp_db, mono=True, **lv, cues=rows)
print(json.dumps({k: v for k, v in report.items() if k != "cues"}, indent=1))
json.dump(report, open(os.path.join(REV, TAG + "_levels.json"), "w"), indent=1)
HP = Image.open(os.path.join(DST, "e_0000.png")).height
for name, wav in (("WITH_VOICE", ww), ("NO_VOICE", wn)):
    out = os.path.join(REV, "DROPPER_intro_%s_%dp_%s.mp4" % (TAG, HP, name))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(DST, "e_%04d.png"), "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", out], check=True)
    print("ok", out)
k = 24 if outn > 400 else 12
pick = [int(i * (outn - 1) / (k - 1)) for i in range(k)]
W, H = 400, 225
cols = 6
sheet = Image.new("RGB", (cols * W + 70, (k // cols) * (H + 10) + 10), (20, 20, 24))
for i, f in enumerate(pick):
    sheet.paste(Image.open(os.path.join(DST, "e_%04d.png" % f)).resize((W, H)), (10 + (i % cols) * (W + 10), 10 + (i // cols) * (H + 10)))
sheet.save(os.path.join(REV, TAG + "_sheet.png"))
