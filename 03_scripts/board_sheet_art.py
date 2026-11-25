"""Scoreboard choice sheet art (2026-11-18): three new board designs beside today's (A).
Each set is 04_assets/art/boardset/<letter>/board_0..8.png (same 1120 x 680 size and same score steps as make_popups.py)
plus look.json (the slab side colour and where each row's flying diamond lands). full5.py reads it when env BOARDSET=<letter>.
Names exactly "انا" (yellow) and "يويو" (lime), Tahoma Bold, real skins and real block textures only.
  B  stone sign:   polished blackstone card, obsidian rim, the count shown as a row of real diamond blocks plus the number.
  C  wool race:    quartz card, a yellow-wool lane and a lime-wool lane; diamond blocks fill each lane like a race.
  D  versus split: yellow half for انا, lime half for يويو, side by side, giant numbers.
    python 03_scripts/board_sheet_art.py"""
import json
import os
import sys

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

ART = os.path.join(PA.ASSETS, "art")
FONT = r"C:\Windows\Fonts\tahomabd.ttf"
RESH = arabic_reshaper.ArabicReshaper(configuration={"support_ligatures": True})
TX = os.path.join(PA.SCENE, "tex121")
DIA = Image.open(os.path.join(PA.SCENE, "tex_extra", "diamond_block.png")).convert("RGBA")
STEPS = [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (4, 2), (4, 3), (5, 3)]   # same as make_popups.py
W, H = 1120, 680
YELLOW, LIME = (255, 255, 85, 255), (85, 255, 85, 255)
NAMES = ("انا", "يويو")


def ar(s):
    return get_display(RESH.reshape(s))


def tex(name, px):
    return Image.open(os.path.join(PA.SCENE, name)).convert("RGBA").resize((px, px), Image.NEAREST)


def tile(im, t, box):
    x0, y0, x1, y1 = box
    for y in range(y0, y1, t.height):
        for x in range(x0, x1, t.width):
            c = t.crop((0, 0, min(t.width, x1 - x), min(t.height, y1 - y)))
            im.alpha_composite(c, (x, y))


def face(path, hat, px):
    im = Image.open(path).convert("RGBA")
    f = im.crop((8, 8, 16, 16))
    if hat:
        f.alpha_composite(im.crop((40, 8, 48, 16)))
    return f.resize((px, px), Image.NEAREST)


FACES = (lambda px: face(os.path.join(PA.SCENE, "3liSY.png"), True, px),
         lambda px: face(os.path.join(PA.SCENE, "YoCube1.png"), False, px))


def text(im, xy, s, size, fill, anchor, shadow=True):
    f = ImageFont.truetype(FONT, size)
    if shadow:
        sh = Image.new("L", im.size, 0)
        ImageDraw.Draw(sh).text((xy[0] + 6, xy[1] + 6), s, font=f, fill=200, anchor=anchor)
        im.paste((0, 0, 0, 255), (0, 0), sh)
    ImageDraw.Draw(im).text(xy, s, font=f, fill=fill, anchor=anchor)


def dia(n):
    return DIA.resize((n, n), Image.NEAREST)


def board_B(a, b):
    im = Image.new("RGBA", (W, H))
    tile(im, tex("tex/obsidian.png", 80), (0, 0, W, H))
    tile(im, tex("tex121/polished_blackstone.png", 80), (24, 24, W - 24, H - 24))
    rows = []
    for i, n in enumerate((a, b)):
        y = 70 + i * 300
        lead = n > (b, a)[i]
        col = (YELLOW, LIME)[i]
        if lead:
            d = ImageDraw.Draw(im)
            d.rectangle((40, y - 20, W - 40, y + 250), outline=col, width=8)
        im.alpha_composite(FACES[i](120), (W - 60 - 120, y))
        text(im, (W - 210, y + 60), ar(NAMES[i]), 96, col, "rm")
        text(im, (70, y + 60), str(n), 120, (255, 255, 255, 255), "lm")
        for k in range(5):                                   # five slots, filled ones are real diamond blocks
            x = W - 70 - 5 * 120 + k * 120
            if k >= 5 - n:
                im.alpha_composite(dia(104), (x, y + 136))
            else:
                ImageDraw.Draw(im).rectangle((x + 8, y + 144, x + 96, y + 232), fill=(20, 18, 24, 255))
        rows.append((W - 70 - 60, y + 188))
    return im, rows


def board_C(a, b):
    im = Image.new("RGBA", (W, H))
    tile(im, tex("tex121/quartz_bricks.png", 80), (0, 0, W, H))
    rows = []
    for i, n in enumerate((a, b)):
        y = 60 + i * 310
        lane = tex(("tex121/yellow_wool.png", "tex121/lime_wool.png")[i], 70)
        d = ImageDraw.Draw(im)
        d.rectangle((36, y - 6, W - 36, y + 260), fill=(30, 30, 36, 255))
        tile(im, lane, (48, y + 6, W - 48, y + 106))
        im.alpha_composite(FACES[i](100), (W - 48 - 100, y + 6))
        text(im, (W - 170, y + 56), ar(NAMES[i]), 84, (20, 20, 24, 255), "rm", shadow=False)
        # the race track: five slots from right to left (Arabic reads right to left)
        for k in range(5):
            x = W - 160 - (k + 1) * 150
            if k < n:
                im.alpha_composite(dia(130), (x, y + 118))
            else:
                d.rectangle((x + 10, y + 128, x + 120, y + 238), outline=(90, 90, 100, 255), width=6)
        text(im, (110, y + 182), str(n), 150, (255, 255, 255, 255), "mm", shadow=False)
        rows.append((W - 160 - max(1, n) * 150 + 65, y + 183))
    return im, rows


def board_D(a, b):
    im = Image.new("RGBA", (W, H))
    half = W // 2
    tile(im, tex("tex121/lime_concrete.png", 80), (0, 0, half, H))           # يويو on the left
    tile(im, tex("tex121/yellow_concrete.png", 80), (half, 0, W, H))        # انا on the right: Arabic reads right first
    d = ImageDraw.Draw(im)
    d.rectangle((half - 10, 0, half + 10, H), fill=(14, 14, 18, 255))
    rows = [None, None]
    for i, n in enumerate((a, b)):
        cx = half + half // 2 if i == 0 else half // 2
        lead = n > (b, a)[i]
        im.alpha_composite(FACES[i](150), (cx - 75, 40))
        text(im, (cx, 260), ar(NAMES[i]), 84, (20, 20, 24, 255), "mm", shadow=False)
        text(im, (cx + 70, 470), str(n), 260, (255, 255, 255, 255) if lead else (30, 30, 34, 255), "mm")
        im.alpha_composite(dia(110), (cx - 190, 415))
        rows[i] = (cx - 135, 470)
    if a == b:
        pass
    return im, rows


RED, PURPLE = (255, 60, 60, 255), (185, 85, 255, 255)
STEPS_E = [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3)] + [(n, 3) for n in (4, 5, 6, 8, 10, 13, 16, 20, 25, 32, 40, 48, 56, 64)]


def board_E(a, b):
    """Versus split like D, in the Stage B colours: purple half for يويو on the left, red half for انا on the right."""
    im = Image.new("RGBA", (W, H))
    half = W // 2
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, half, H), fill=PURPLE)
    d.rectangle((half, 0, W, H), fill=RED)
    d.rectangle((0, 0, W - 1, H - 1), outline=(14, 14, 18, 255), width=14)
    d.rectangle((half - 10, 0, half + 10, H), fill=(14, 14, 18, 255))
    rows = [None, None]
    for i, n in enumerate((a, b)):
        cx = half + half // 2 if i == 0 else half // 2
        lead = n > (b, a)[i]
        im.alpha_composite(FACES[i](140), (cx - 70, 34))
        text(im, (cx, 240), ar(NAMES[i]), 80, (255, 255, 255, 255), "mm")
        size = 250 if n < 10 else 210                       # two digits stay inside the half
        text(im, (cx + 60, 470), str(n), size, (255, 255, 255, 255), "mm")
        im.alpha_composite(dia(100), (cx - 220, 420))
        rows[i] = (cx - 170, 470)
    return im, rows


SETS = {"B": (board_B, (0.25, 0.22, 0.28)), "C": (board_C, (0.85, 0.83, 0.80)), "D": (board_D, (0.08, 0.08, 0.1)),
        "E": (board_E, (0.08, 0.08, 0.1))}
ONLY = sys.argv[1:] or list(SETS)                         # Stage B: python board_sheet_art.py E builds only set E
for k, (fn, side) in SETS.items():
    if k not in ONLY:
        continue
    out = os.path.join(ART, "boardset", k)
    os.makedirs(out, exist_ok=True)
    land = {}
    for i, (a, b) in enumerate(STEPS_E if k == "E" else STEPS):
        im, rows = fn(a, b)
        im.convert("RGB").save(os.path.join(out, f"board_{i}.png"))
        land[i] = rows
    json.dump({"side": side, "rows_px": land}, open(os.path.join(out, "look.json"), "w"))
    print(k, "ok")
