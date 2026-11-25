"""lipsync.py - mouths from speech, not from loudness.

Each word (the corrected words with their fitted times) is split into syllables from its Arabic letters; each
syllable gets a slice of the word's time, weighted by its letters (long vowels count more), and a mouth shape:
    A wide open  (ا ع ح ه)      O round (و)      E wide smile (ي)
    M nearly closed (م ب ف)     S small open (the rest)      X closed (between words, silence)
A lip consonant at a syllable's start or end closes the lips for a moment (M). Loudness only scales how far it
opens (a quiet A becomes S). Shapes are shown one frame ahead of the sound and held at least 3 frames.
Pure Python: Blender's intro.py and the proof-strip script both import it.

    python 03_scripts/lipsync.py      prints the syllables and shapes of every SRB word
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as PA  # noqa: E402

FPS = 60
VOWEL = set("اأإآى")
SEMI = set("وي")
OPEN_C = set("عحهةء")
LIPS = set("مبف")
SHAPES = "XMSAOE"


def syllables(word):
    """[(letters, roles)], roles 'C' consonant / 'V' vowel letter. Long vowels end a syllable (open CVV); one consonant
    may close a syllable (coda) when the next letter is a consonant or the word ends; a lone consonant carries an
    unwritten short vowel."""
    w = [c for c in word if c.isalpha()]
    out, cur = [], None

    def push():
        if cur:
            out.append(cur)

    for i, c in enumerate(w):
        nxt = w[i + 1] if i + 1 < len(w) else ""
        nxt_v = nxt in VOWEL
        if c in VOWEL:
            if cur is None:
                cur = [(c, "V")]
            else:
                cur.append((c, "V"))
            continue
        if c in SEMI and cur is not None and not nxt_v:            # و / ي as a long vowel (نوو، داي، لي)
            cur.append((c, "V"))
            continue
        # a consonant (or و / ي starting a syllable)
        if cur is not None:
            last, role = cur[-1]
            has_coda = len(cur) >= 2 and cur[-1][1] == "C" and any(r == "V" for _, r in cur[:-1])
            ends_long = role == "V" and not (len(cur) == 1 and i == 1)  # a word-initial alone ا is short (ال، ان)
            lone_c = all(r == "C" for _, r in cur) and len(cur) == 1
            if (not nxt_v) and not ends_long and not has_coda and not (lone_c and False):
                if not (len(cur) >= 2 and all(r == "C" for _, r in cur)):
                    cur.append((c, "C"))                            # coda
                    continue
        push()
        cur = [(c, "C")]
    push()
    return out


def vshape(c):
    return "O" if c == "و" else "E" if c == "ي" else "A"


def syl_plan(letters, final):
    """[(fraction, shape)] for one syllable."""
    chars = [c for c, _ in letters]
    vs = [c for c, r in letters if r == "V"]
    onset = chars[0] if letters[0][1] == "C" else None
    coda = chars[-1] if len(letters) > 1 and letters[-1][1] == "C" else None
    if vs:
        main = vshape(vs[-1])
    elif onset in OPEN_C:
        main = "A"
    elif onset in LIPS:
        main = "M" if final else "S"
    else:
        main = "S"
    plan = []
    if onset in LIPS and main != "M":
        plan.append((0.28, "M"))
    elif onset in SEMI and vshape(onset) != main:
        plan.append((0.25, vshape(onset)))                    # w rounds the lips, y spreads them, for a moment
    plan.append((1.0, main))
    if coda in LIPS:
        plan.append((0.25, "M"))
    tot = sum(f for f, _ in plan)
    return [(f / tot, s) for f, s in plan]


def weight(letters):
    return sum(1.6 if r == "V" else 1.0 for _, r in letters)


SPOKEN = {"14": "اربعطعش", "16": "ستطعش", "8": "تمانة"}     # numbers as they are said


def word_syllables(w):
    """[(t0, t1, letters, plan)] for one word dict {w, s, e}."""
    syl = syllables(SPOKEN.get(w["w"], w["w"]))
    if not syl:
        return []
    ws = [weight(s) for s in syl]
    tot, t, out = sum(ws), w["s"], []
    for i, (s, k) in enumerate(zip(syl, ws)):
        d = (w["e"] - w["s"]) * k / tot
        out.append((t, t + d, s, syl_plan(s, i == len(syl) - 1)))
        t += d
    return out


def load(piece="intro"):
    words = json.load(open(PA.WORDS_FINAL[piece], encoding="utf-8"))
    env = json.load(open(os.path.join(PA.DATA, f"env_{piece}.json")))["env"]
    return words, env


def track(speaker, piece="intro", n_frames=None, lead=1, hold=3):
    """Per-frame mouth shape for one speaker (list of letters from SHAPES), plus [(time, strength)] stress accents."""
    words, env = load(piece)
    n = n_frames or len(env)
    segs, stress = [], []
    for w in words:
        if w["spk"] != speaker:
            continue
        syl = word_syllables(w)
        for k, (t0, t1, letters, plan) in enumerate(syl):
            t = t0
            for frac, shape in plan:
                segs.append((t, t + (t1 - t0) * frac, shape))
                t += (t1 - t0) * frac
        if syl:                                               # the word's heaviest syllable carries the accent
            t0, t1, letters, _ = max(syl, key=lambda s: (weight(s[2]), -s[0]))
            e = max(env[min(len(env) - 1, int(t * FPS))] for t in (t0, (t0 + t1) / 2))
            stress.append((t0, round(0.4 + 0.6 * e, 3)))
    shape = []
    for f in range(n):
        t = (f + lead) / FPS
        s = next((sh for a, b, sh in segs if a <= t < b), "X")
        e = env[min(len(env) - 1, f + lead)]
        if s == "A" and e < 0.18:
            s = "S"                                           # a quiet open vowel opens less
        shape.append(s)
    i = 0                                                     # no shape shorter than `hold` frames
    while i < n:
        j = i
        while j < n and shape[j] == shape[i]:
            j += 1
        if j - i < hold and i > 0:
            for q in range(i, j):
                shape[q] = shape[i - 1]
        i = j
    return shape, stress


if __name__ == "__main__":
    words, _ = load()
    for w in words:
        parts = ["".join(c for c, _ in s) + ":" + "".join(sh for _, sh in p) for _, _, s, p in word_syllables(w)]
        print(w["spk"][:3], f"{w['s']:.2f}-{w['e']:.2f}", w["w"], " | ".join(parts))
    sh, st = track("SRB")
    print("SRB frames", "".join(sh[360:460]))
