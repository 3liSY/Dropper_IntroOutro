"""paths.py - every folder and file of the DROPPER intro + outro, in one place. Every script imports this.

Intros&Outros/DROPPER/
    01_final/       the finished videos (DROPPER_intro_1080p/4K.mp4, DROPPER_outro_1080p/4K.mp4)
    02_source/      intro_voice.mp4, outro_voice.mp4 - the recordings (not in this repo)
    03_scripts/     these scripts
    04_assets/      scene/ (copied thumbnail scene, skins, wool textures, HUD), data/ (word times), sfx/, fonts/
    05_renders/     frames_<piece>_<res>/ (3D), edit_<piece>_<res>/ (post), review/ (stills, sheets, test videos)
    06_archive/     old tests, check images, logs

Everything is relative to this file, so the folder works wherever it sits (the folder name has an & in it: quote it in shells).
"""
import os

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)                             # Intros&Outros/DROPPER
FINAL = os.path.join(ROOT, "01_final")
SOURCE = os.path.join(ROOT, "02_source")
ASSETS = os.path.join(ROOT, "04_assets")
SCENE = os.path.join(ASSETS, "scene")                       # solo.py, thumb.py, skins, tex*, hearts, grade tools
DATA = os.path.join(ASSETS, "data")
SFX = os.path.join(ASSETS, "sfx")
FONTS = os.path.join(ASSETS, "fonts")
RENDERS = os.path.join(ROOT, "05_renders")
REVIEW = os.path.join(RENDERS, "review")
ARCHIVE = os.path.join(ROOT, "06_archive")

PIECES = ("intro", "outro")
VOICE = {p: os.path.join(SOURCE, f"{p}_voice.mp4") for p in PIECES}
WAV = {p: os.path.join(DATA, f"{p}_voice.wav") for p in PIECES}
WORDS = {p: os.path.join(DATA, f"{p}_words.json") for p in PIECES}
WORDS_FINAL = {p: os.path.join(DATA, f"{p}_words_final.json") for p in PIECES}   # corrected text + fitted times
TURNS = os.path.join(DATA, "turns.json")

RES = {"quick": "720p", "preview": "1080p", "final": "2160p"}


def frames_dir(piece, mode):
    return os.path.join(RENDERS, f"frames_{piece}_{RES[mode]}")


def edit_dir(piece, mode):
    return os.path.join(RENDERS, f"edit_{piece}_{RES[mode]}")


def video(piece, mode):
    folder = REVIEW if mode == "quick" else FINAL
    return os.path.join(folder, f"DROPPER_{piece}_{RES[mode]}.mp4")


for _d in (FINAL, DATA, SFX, FONTS, REVIEW, ARCHIVE):
    os.makedirs(_d, exist_ok=True)
