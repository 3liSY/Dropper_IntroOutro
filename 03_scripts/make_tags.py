"""make_tags.py - the name plates of the intro: the faces of 3D block plates in the scene (full5.py gives them thickness and sides).
Arabic joined, Segoe UI Bold, white on a dark block with a coloured block border. Names only, never a caption word.
    python 03_scripts/make_tags.py        -> 04_assets/art/plate_*.png"""
import os
import sys

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

RESH = arabic_reshaper.ArabicReshaper(configuration={"support_ligatures": True})
TAGS = {"fras": ("فراس جيمر", (70, 230, 240)), "mustafa": ("مصطفى جيم اوفر", (70, 230, 240)), "ali": ("علي الفاشل", (255, 90, 70))}


def make(txt, accent, path, sz=132):
    f = ImageFont.truetype(os.path.join(PA.FONTS, "segoeuib.ttf"), sz)
    t = get_display(RESH.reshape(txt))
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), t, font=f)
    B = 20
    w, h = bb[2] - bb[0] + 2 * B + 96, bb[3] - bb[1] + 2 * B + 64
    im = Image.new("RGBA", (w, h), accent + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((B, B, w - B - 1, h - B - 1), fill=(13, 15, 26, 255))
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=(255, 255, 255, 255))
    im.save(path)
    return im.size


if __name__ == "__main__":
    for k, (v, c) in TAGS.items():
        print(k, make(v, c, os.path.join(PA.ASSETS, "art", f"plate_{k}.png")))
