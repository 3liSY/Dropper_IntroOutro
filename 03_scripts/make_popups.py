"""make_popups.py - the pop-up art that lives in the 3D scene: the big diamond scoreboard (one image per score step, the leader's row
glows) and the comment bubbles (only words from the audio: نووب, عقاب), bold black on white.
    python 03_scripts/make_popups.py     -> 04_assets/art/board_<n>.png, bubble5_noob.png, bubble5_3iqab.png"""
import os
import sys

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

ART = os.path.join(PA.ASSETS, "art")
FONT = os.path.join(PA.FONTS, "segoeuib.ttf")
RESH = arabic_reshaper.ArabicReshaper(configuration={"support_ligatures": True})
DIA = Image.open(os.path.join(PA.SCENE, "tex_extra", "diamond_block.png")).convert("RGBA")
STEPS = [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (4, 2), (4, 3), (5, 3)]   # never real numbers: it only shows the race


def ar(s):
    return get_display(RESH.reshape(s))


def face(path, hat=True):
    im = Image.open(path).convert("RGBA")
    f = im.crop((8, 8, 16, 16))
    if hat:
        f.alpha_composite(im.crop((40, 8, 48, 16)))
    return f.resize((150, 150), Image.NEAREST)


def scoreboard(a, b, path):
    W, H = 1120, 680
    im = Image.new("RGBA", (W, H), (70, 230, 240, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((16, 16, W - 17, H - 17), fill=(9, 11, 22, 255))
    f1, f2, f3 = ImageFont.truetype(FONT, 92), ImageFont.truetype(FONT, 92), ImageFont.truetype(FONT, 150)
    d.text((W / 2, 34), ar("دايموند"), font=f1, fill=(120, 240, 250, 255), anchor="ma")
    rows = (("3liSY", a, face(os.path.join(PA.SCENE, "3liSY.png"))),
            ("YoCube1", b, face(os.path.join(PA.ASSETS, "art", "skins", "YoCube1_clean.png"), hat=False)))
    for i, (name, n, ic) in enumerate(rows):
        y = 176 + i * 236
        lead = n > (b if i == 0 else a)
        if lead:
            d.rectangle((34, y - 14, W - 35, y + 200), fill=(24, 110, 140, 255))
        im.alpha_composite(ic, (56, y + 18))
        d.text((236, y + 42), name, font=f2, fill=(255, 255, 255, 255))
        im.alpha_composite(DIA.resize((132, 132), Image.NEAREST), (W - 330, y + 28))
        d.text((W - 150, y + 94), str(n), font=f3, fill=(255, 255, 255, 255), anchor="mm")
    im.save(path)


def bubble(txt, path):
    f = ImageFont.truetype(FONT, 170)
    t = ar(txt)
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), t, font=f)
    w, h = bb[2] - bb[0] + 170, bb[3] - bb[1] + 110
    im = Image.new("RGBA", (w + 24, h + 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for off, fill, line in ((14, (0, 0, 0, 150), (0, 0, 0, 150)), (0, (255, 255, 255, 255), (10, 10, 14, 255))):
        d.rounded_rectangle((6 + off, 6 + off, w - 6 + off, h - 6 + off), 40, fill=fill, outline=line, width=12)
        d.polygon(((w * 0.28 + off, h - 10 + off), (w * 0.28 + 84 + off, h - 10 + off), (w * 0.28 + 14 + off, h + 76 + off)), fill=fill, outline=line)
    d.polygon(((w * 0.28 + 12, h - 22), (w * 0.28 + 72, h - 22), (w * 0.28 + 20, h + 44)), fill=(255, 255, 255, 255))
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=(10, 10, 14, 255))
    im.save(path)
    return im.size


for i, (a, b) in enumerate(STEPS):
    scoreboard(a, b, os.path.join(ART, f"board_{i}.png"))
print(len(STEPS), bubble("نووب", os.path.join(ART, "bubble5_noob.png")), bubble("عقاب", os.path.join(ART, "bubble5_3iqab.png")))
sheet = Image.new("RGB", (2300, 720), (60, 40, 90))
for i, n in enumerate(("board_0", "board_8")):
    p = Image.open(os.path.join(ART, n + ".png"))
    sheet.paste(p, (10 + i * 1140, 20), p)
sheet.save(os.path.join(PA.REVIEW, "v3", "_popups5.png"))
