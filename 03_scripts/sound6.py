"""sound6.py - v6 sound effects for the Dropper intro. Real files only: Minecraft's own game sounds on this PC
(read-only, no download) and a local sound folder. No synth.

    fx, rows = build(n, SR, voice_rms, choice)   # choice: {"W1": "B", ...}; a cue not named plays option A

Each layer is placed so its spike (first point within 6 dB of its loudest point; its very start, for splash and debris) lands on the picture event.
Layers keep their real level difference (dB per layer). The whole cue is then set against the voice:
W1 equal to the voice, P1/C1 3 dB under, N16 8 dB under, small cues 12 dB under (RMS over 400 ms at the cue's peak)."""
import json
import os
import subprocess

import numpy as np

MC = os.path.expandvars(r"%APPDATA%\.minecraft\assets")
LIB = os.path.expanduser(r"~\Desktop\Editing\Sound effects")
FPS = 60
_ix, _cache = None, {}


def _path(src, name):
    global _ix
    if src == "mc":
        if _ix is None:
            _ix = json.load(open(os.path.join(MC, "indexes", "32.json")))["objects"]
        h = _ix["minecraft/sounds/%s.ogg" % name]["hash"]
        return os.path.join(MC, "objects", h[:2], h)
    for root, _, files in os.walk(LIB):
        if name in files:
            return os.path.join(root, name)
    raise FileNotFoundError(name)


def load(src, name, SR):
    if (src, name) not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", _path(src, name), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        _cache[(src, name)] = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return _cache[(src, name)]


def L(src, name, db=0.0, st=0.0, dur=None, at=0.0, fin=0.0, align="spike"):
    """One layer: file, level in dB, pitch in semitones, length cap, offset from the event, fade-in, align on spike or onset.
    spike = the first point within 6 dB of the layer's loudest point: that is where the ear hears the hit, so it goes on the frame."""
    return dict(src=src, name=name, db=db, st=st, dur=dur, at=at, fin=fin, align=align)


def shape(x, SR, st, dur, fin):
    if st:
        x = np.interp(np.arange(0, len(x) - 1, 2 ** (st / 12)), np.arange(len(x)), x)   # pitch down = slower and lower, like Minecraft
    x = x[np.argmax(np.abs(x) > np.abs(x).max() * 0.01):]                                 # cut leading silence (-40 dB)
    if dur:
        x = x[:int(dur * SR)]
    x = x.copy()
    k = min(len(x), int(0.03 * SR))
    x[len(x) - k:] *= np.linspace(1, 0, k)                                                # 30 ms fade so no click
    if fin:
        k = min(len(x), int(fin * SR))
        x[:k] *= np.linspace(0, 1, k)
    return x


#   O1 the "14" stops rising (ease 0.925 -> 1.345, last move about f78) | E1/E2 the egg bursts (3.14 / 3.84, first frame showing it)
#   S1 the throw starts (v7D 6.88, 8 frames before contact; was 4) | P1 first frame of the "hit" pose and the flash (7.01) | W1 the wall hit 7.25 (Stage B 2026-11-21, was 7.90)
#   N16 "16" full size (pop 9.52) | G1 diamond full size (pop 10.62) | C1 score slab full size (pop 12.40) | U5 last score change (13.92)
FRAMES = {"O1": 78, "E1": 189, "E2": 245, "S1": 413, "P1": 421, "W1": 432, "N16": 576, "G1": 700, "C1": 738, "U5": 819,
          # E0 egg throw 2.50 | SH shout, on the cut to the close-up (moves to ~5.95 in Stage B) | T1/T2 the pixel-break transitions
          # v7C 2026-11-23: E2 4.46 (Mustafa egg after "فراس جيمر") | N16 9.76 (real spoken "16") | T1 9.92 burst | T2 14.00 (teleport in the silence before "اوووو")
          "E0": 150, "SH": 366, "T1": 576, "T2": 842, "K0": 989, "K1": 1001, "K2": 1013, "K3": 1025, "K4": 1037, "K5": 1049}
U5_ALL = [round((12.28 + i * 0.11) * FPS) for i in range(6)] + [round((12.951 + k * 0.054) * FPS) for k in range(14)]   # v7E: with the new board times
EVENTS = {k: f / FPS for k, f in FRAMES.items()}
LEVEL = {"W1": 0, "P1": -3, "C1": -3, "N16": -8, "SH": -8, "U5": -14, "E0": -15, "K0": -16, "K1": -16, "K2": -16, "K3": -16, "K4": -16, "K5": -16}   # every other cue: -12
STONE = "block/deepslate/place1"
MACE, HEAVY = "item/mace/smash_ground1", "item/mace/smash_ground_heavy"
DEBRIS = [L("mc", "dig/gravel1", -10, at=0.17, align="onset"), L("mc", "block/tuff/break1", -12, at=0.30, align="onset"),
          L("mc", "dig/gravel2", -16, at=0.50, align="onset")]                            # W2: loose blocks from f484; v7: a last small fall, the tail
SWOOSH = "Fast Swoosh.mp3"
OPTIONS = {
    "O1": {"A": [L("mc", STONE, st=-5)], "B": [L("mc", "dig/stone1", st=-3)], "C": []},
    # egg cracks hold 4-6 small cracks over 0.5 s; dur=0.2 keeps only the first, so no crack sounds before the burst
    "E1": {"A": [L("mc", "mob/turtle/egg/egg_crack1", st=-4, dur=0.2), L("mc", STONE, -8, st=-8)],
           "B": [L("mc", STONE, st=-8), L("mc", "mob/turtle/egg/egg_crack1", -10, st=-4, dur=0.2)], "C": []},
    "E2": {"A": [L("mc", "mob/turtle/egg/egg_crack2", st=-4, dur=0.2), L("mc", STONE, -8, st=-8)],
           "B": [L("mc", STONE, st=-8), L("mc", "mob/turtle/egg/egg_crack2", -10, st=-4, dur=0.2)], "C": []},
    "S1": {"A": [L("mc", "entity/player/attack/sweep1", st=-4)], "B": [L("lib", "Swoosh 1.wav", dur=0.4)], "C": []},
    "P1": {"A": [L("mc", "entity/player/attack/strong1"), L("mc", "entity/player/attack/knockback1", -4), L("mc", MACE, -6, st=-2, dur=0.6)],
           "B": [L("lib", "Hit 1.wav"), L("lib", "Thud Sharp.wav", -4), L("mc", MACE, -6, dur=0.6)],
           "C": [L("mc", "entity/player/attack/strong1"), L("lib", "Boom hit.mp3", -4, dur=0.8)]},
    "W1": {"A": [L("mc", HEAVY, dur=0.9), L("mc", "block/deepslate/break1", -4, st=-3)] + DEBRIS,
           "B": [L("mc", HEAVY, dur=0.9), L("mc", "random/explode1", -5, st=-5, dur=1.0)] + DEBRIS,
           "C": [L("lib", "THE Boom.mp3", dur=1.2), L("mc", "block/deepslate/break1", -4, st=-3)] + DEBRIS},
    "N16": {"A": [L("mc", STONE, st=-6), L("mc", MACE, -8, dur=0.5)], "B": [L("mc", "block/heavy_core/break1")], "C": []},
    "G1": {"A": [L("mc", "block/heavy_core/break1")], "B": [L("mc", STONE, st=-3)], "C": []},
    "C1": {"A": [L("mc", MACE, dur=0.7), L("mc", STONE, -4, st=-6), L("mc", "dig/stone1", -10, at=0.05, align="onset")],
           "B": [L("mc", HEAVY, dur=0.5)], "C": [L("lib", "Boom hit.mp3", dur=0.8), L("mc", STONE, -4, st=-6)]},
    # v7: one Minecraft XP-orb tick per score change, each a little higher (was one stone at the last change only)
    "U5": {"A": [L("mc", "random/orb", -3 + min(i, 8) * 0.4, st=-3 + min(i, 12), at=(f - U5_ALL[-1]) / FPS) for i, f in enumerate(U5_ALL)],   # Stage B: the pitch stops rising after 12 steps
           "B": [L("mc", "dig/stone1", -6, at=(f - U5_ALL[-1]) / FPS) for f in U5_ALL], "C": []},
    "E0": {"A": [L("mc", "random/bow", st=-3)]},
    "SH": {"A": [L("lib", SWOOSH, dur=0.5), L("mc", STONE, -6, st=-9)]},
    "T1": {"A": [L("lib", SWOOSH, dur=0.5), L("mc", "block/amethyst/break1", -8, st=-4)]},
    "T2": {"A": [L("lib", SWOOSH, dur=0.5), L("mc", "block/amethyst/break2", -8, st=-4)]},
    "K0": {"A": [L("mc", "random/pop", st=-2)]},
    "K1": {"A": [L("mc", "random/pop", st=-4)]},
    "K2": {"A": [L("mc", "random/pop", st=-1)]},
    "K3": {"A": [L("mc", "random/pop", st=-3)]},
    "K4": {"A": [L("mc", "random/pop", st=-2)]},
    "K5": {"A": [L("mc", "random/pop", st=-5)]},
}
BED, BED_DB = "Wind.wav", -30          # v7: a quiet real wind bed under the whole intro, 30 dB under the voice, so no digital silence
                                       # (v6 was dead silent in 11 of 36 half seconds). It dips under the gap before the wall hit.


def bed(n, SR, voice_rms):
    x = load("lib", BED, SR)
    k = int(0.5 * SR)                                                                      # loop with a 0.5 s crossfade
    out = np.zeros(n + len(x))
    i, fade = 0, np.linspace(0, 1, k)
    while i < n:
        y = x.copy()
        y[:k] *= fade
        y[-k:] *= fade[::-1]
        out[i:i + len(y)] += y
        i += len(y) - k
    out = out[:n]
    out *= voice_rms * 10 ** (BED_DB / 20) / (np.sqrt(np.mean(out ** 2)) + 1e-12)
    t = np.arange(n) / SR
    e = EVENTS["W1"]
    out *= np.interp(t, [0, 0.4, e - QUIET_BEFORE_W1 - 0.05, e - QUIET_BEFORE_W1, e, e + 0.3, T_ENDS - 0.3, T_ENDS], [0, 1, 1, 0.15, 0.15, 1, 1, 0])
    return out


T_ENDS = 17.75
QUIET_BEFORE_W1 = 0.15                                                                    # no effect sound for 150 ms before the wall hit


def cue_signal(cue, opt, n, SR):
    buf = np.zeros(n)
    for ly in OPTIONS[cue][opt]:
        x = shape(load(ly["src"], ly["name"], SR), SR, ly["st"], ly["dur"], ly["fin"])
        a = np.abs(x[:int(0.6 * SR)])
        pk = int(np.argmax(a))
        lo = max(0, pk - int(0.5 * SR))
        lead = 0 if ly["align"] == "onset" else lo + int(np.argmax(a[lo:pk + 1] > a[pk] * 0.5))   # spike: first point within 6 dB of the peak
        i = int(round((EVENTS[cue] + ly["at"]) * SR)) - lead
        a, b = max(i, 0), min(n, i + len(x))
        if b > a:
            buf[a:b] += 10 ** (ly["db"] / 20) * x[a - i:b - i]
    return buf


def write_wav(x, SR, path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-", path], input=x.astype(np.float64).tobytes(), check=True)


def lufs(path):
    """integrated loudness (LUFS) and true peak (dBTP), from ffmpeg ebur128"""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = r[r.rfind("Summary:"):]
    return float(tail.split("I:")[1].split("LUFS")[0]), float(tail.split("Peak:")[1].split("dBFS")[0])


def rms_active(x):
    return np.sqrt(np.mean(x[np.abs(x) > 0.02] ** 2))


def load_voice(path, SR, T_END):
    """The voice line, mono, then a gentle compressor: 2:1 above the voice's own RMS, never more than 3 dB down
    (5 ms steps, 10 ms attack, 150 ms release). Returns the voice, the most it took off (dB) and the voice RMS."""
    n = int(T_END * SR)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-t", "%.3f" % T_END, "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    v = np.frombuffer(raw, dtype=np.float32).astype(np.float64)[:n]
    v = np.pad(v, (0, n - len(v)))
    B = int(0.005 * SR)
    m = len(v) // B
    e = np.sqrt(np.mean(v[:m * B].reshape(m, B) ** 2, axis=1)) + 1e-12
    want = np.clip(0.5 * 20 * np.log10(e / rms_active(v)), 0, 3.0)
    g = np.zeros(m)
    for i in range(1, m):
        c = 0.61 if want[i] > g[i - 1] else 0.967                                          # exp(-5/10) attack, exp(-5/150) release
        g[i] = c * g[i - 1] + (1 - c) * want[i]
    v = v * 10 ** (-np.interp(np.arange(len(v)), np.arange(m) * B + B / 2, g) / 20)
    return v, float(g.max()), rms_active(v)


CEIL_DB, LIM_MAX_DB = -1.5, 1.5        # sample-peak ceiling (true peak lands under -1 dBTP, measured after); the last limiter may take
                                       # at most 1.5 dB off voice + effects together, past that the whole mix goes down instead
# 2026-11-21 fix: at -14 LUFS the voice peaks sat 2.8 dB over the ceiling and the big hits 3-5 dB over, so the 1.5 dB rule pulled the
# whole mix down to -17.6. Now each channel holds its own peaks first (only the first few ms of a hit), then the last limiter.
VOICE_HEAD_DB, FX_HEAD_DB = 1.0, 0.5   # the voice peaks 1 dB and the effects 0.5 dB under the ceiling before they are added
DIP_CUES, DIP_DB = ("P1", "W1", "C1"), -3.0   # the voice dips 3 dB under the three big hits (Stage B: no D2 splash), so they read bigger without more peak


def read_wav(path, SR, n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f64le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype=np.float64)[:n]
    return np.pad(y, (0, n - len(y)))


def limited(x, SR, path, limit=None, release=60):
    """lookahead limiter (ffmpeg alimiter, delay compensated so nothing shifts in time, no auto level); limit is linear, default the ceiling"""
    write_wav(x, SR, path + ".pre.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path + ".pre.wav", "-af",
                    "alimiter=limit=%.5f:attack=2:release=%d:level=false:latency=true" % (limit or 10 ** (CEIL_DB / 20), release), path], check=True)


def peak_hold(x, SR, ceil, path):
    """x with its peaks held to ceil (linear). Scaled so ceil maps to 0.5, inside alimiter's range. Returns the held signal."""
    s = 0.5 / ceil
    limited(x * s, SR, path, limit=0.5)
    return read_wav(path, SR, len(x)) / s


def took_db(x, y, SR):
    """most a limiter took off (dB) and for how long it took more than 1 dB (ms), from 5 ms block peaks"""
    B = int(0.005 * SR)
    m = len(x) // B
    px, py = (np.abs(z[:m * B]).reshape(m, B).max(1) for z in (x, y))
    gr = 20 * np.log10((px + 1e-9) / (py + 1e-9)) * (px > 1e-4)
    return float(max(gr.max(), 0.0)), int((gr > 1.0).sum() * 5)


def yield_voice(v, f, SR, C):
    """the voice steps back only where voice + effects would pass C (linear): 2.5 ms blocks, 5 ms look both ways, 50 ms recovery.
    The hit keeps its peak; the hit masks the short voice dip. Returns the voice, the most it dipped (dB) and for how long > 1 dB (ms)."""
    B = int(0.0025 * SR)
    m = -(-len(v) // B)
    pv, pf = (np.abs(np.pad(z, (0, m * B - len(z)))).reshape(m, B).max(1) for z in (v, f))
    pv, pf = (np.max([np.roll(p, s) for s in (-2, -1, 0, 1, 2)], axis=0) for p in (pv, pf))
    want = 20 * np.log10(np.clip((C - pf) / (pv + 1e-9), 0.02, 1.0))
    g = np.zeros(m)
    c = np.exp(-2.5 / 50)
    for i in range(m):
        g[i] = min(want[i], c * g[i - 1] if i else 0.0)
    gain = 10 ** (np.interp(np.arange(len(v)), np.arange(m) * B + B / 2, g) / 20)
    return v * gain, float(-g.min()), int((g < -1.0).sum() * 2.5)


def dip_voice(voice, SR):
    t = np.arange(len(voice)) / SR
    g = np.ones(len(voice))
    d = 10 ** (DIP_DB / 20)
    for c in DIP_CUES:
        e = EVENTS[c]
        g = np.minimum(g, np.interp(t, [e - 0.14, e - 0.08, e + 0.25, e + 0.50], [1, d, d, 1]))   # down over 60 ms, back up over 250 ms
    return voice * g


def master(voice, fx, SR, a0, a1, ww, wn, gain=None, target=-14.0):
    """Writes the mix with the voice (ww) and the effects alone (wn), samples a0:a1. Without gain: two passes to -14 LUFS for
    the mix with the voice (target LUFS). With gain (the listening reel): that exact gain, so every option plays at the real level."""
    voice = dip_voice(voice, SR)
    ceil = 10 ** (CEIL_DB / 20)

    def buses(g):
        vi, fi = voice[a0:a1] * g, fx[a0:a1] * g
        vh = peak_hold(vi, SR, ceil * 10 ** (-VOICE_HEAD_DB / 20), ww + ".voice.wav")
        fo = peak_hold(fi, SR, ceil * 10 ** (-FX_HEAD_DB / 20), ww + ".fx.wav")
        vo, yd, ym = yield_voice(vh, fo, SR, ceil * 10 ** (LIM_MAX_DB / 20))
        yielded.update(db=yd, ms=ym, held=vh)
        return vi, fi, vo, fo, 20 * np.log10(max(np.abs(vo + fo).max(), 1e-9) / ceil)

    yielded = {}

    if gain is None:
        write_wav(voice + fx, SR, ww)
        gain = 10 ** ((target - lufs(ww)[0]) / 20)
        passes = 2
    else:
        passes = 1
    for k in range(passes):
        vi, fi, vo, fo, over_db = buses(gain)
        if over_db > LIM_MAX_DB:
            gain *= 10 ** (-(over_db - LIM_MAX_DB) / 20)
            vi, fi, vo, fo, over_db = buses(gain)
        limited(vo + fo, SR, ww)
        Iw, Pw = lufs(ww)
        if k == 0 and passes == 2 and abs(target - Iw) > 0.2:
            gain *= 10 ** ((target - Iw) / 20)                                               # pass 2 puts back what the limiters took
        else:
            break
    limited(fo, SR, wn)
    In, Pn = lufs(wn)
    mixed = read_wav(ww, SR, a1 - a0)
    voice_took, voice_ms = took_db(vi, yielded["held"], SR)                               # the peak hold alone, not the step-back
    hits = {}
    write_wav(vo, SR, ww + ".voice_only.wav")
    Iv = lufs(ww + ".voice_only.wav")[0]
    for c in DIP_CUES:                                                                     # each big hit: what the effect channel took, and
        e = int(EVENTS[c] * SR) - a0                                                        # how loud it lands over the voice (0.55 s from the hit)
        if 0 <= e - int(0.1 * SR) and e + int(0.45 * SR) <= a1 - a0:
            w = slice(e - int(0.1 * SR), e + int(0.45 * SR))
            t_db, t_ms = took_db(fi[w], fo[w], SR)
            write_wav(mixed[w], SR, ww + ".hit.wav")
            Ih = lufs(ww + ".hit.wav")[0]
            hits[c] = dict(fx_took_db=round(t_db, 2), fx_took_over_1db_ms=t_ms, hit_lufs=Ih, hit_over_voice_lu=round(Ih - Iv, 1))
    return dict(gain_db=20 * np.log10(gain), limiter_max_db=max(0.0, min(over_db, LIM_MAX_DB)), voice_peak_hold_db=round(voice_took, 2),
                voice_peak_hold_over_1db_ms=voice_ms, voice_yield_db=round(yielded["db"], 2), voice_yield_over_1db_ms=yielded["ms"], voice_lufs=Iv, with_voice_lufs=Iw, with_voice_truepeak_db=Pw,
                no_voice_lufs=In, no_voice_truepeak_db=Pn, big_hits=hits)


def build(n, SR, voice_rms, choice=None):
    choice = dict(choice or {})
    if "E" in choice:                                                                  # one pick for both eggs
        choice.setdefault("E1", choice["E"])
        choice.setdefault("E2", choice["E"])
    fx, rows = np.zeros(n), []
    order = [c for c in OPTIONS if c != "W1"] + ["W1"]                                  # the wall goes in last, after the quiet gap is cut
    for cue in order:
        opt = choice.get(cue, "A")
        if cue == "W1":
            g0 = int((EVENTS["W1"] - QUIET_BEFORE_W1) * SR)
            k = int(0.04 * SR)
            fx[g0 - k:g0] *= np.linspace(1, 0, k)
            fx[g0:int(EVENTS["W1"] * SR) + int(0.3 * SR)] = 0
        if not OPTIONS[cue][opt]:
            rows.append(dict(cue=cue, opt=opt, event_f=EVENTS[cue] * FPS, silent=True))
            continue
        s = cue_signal(cue, opt, n, SR)
        p = int(np.argmax(np.abs(s)))
        w = s[max(0, p - int(0.2 * SR)):p + int(0.2 * SR)]
        s *= voice_rms * 10 ** (LEVEL.get(cue, -12) / 20) / (np.sqrt(np.mean(w ** 2)) + 1e-12)
        lo = max(0, p - int(0.5 * SR))
        sp = lo + int(np.argmax(np.abs(s[lo:p + 1]) > np.abs(s[p]) * 0.5))                   # spike: first point within 6 dB of the peak
        fx += s
        rows.append(dict(cue=cue, opt=opt, event_f=round(EVENTS[cue] * FPS, 2), spike_f=round(sp / SR * FPS, 2), peak_f=round(p / SR * FPS, 2),
                         gap_spike_f=round(sp / SR * FPS - EVENTS[cue] * FPS, 2), gap_peak_f=round(p / SR * FPS - EVENTS[cue] * FPS, 2), silent=False))
    fx += bed(n, SR, voice_rms)
    rows.append(dict(cue="BED", opt=BED, level_db=BED_DB, silent=False))
    k = int(0.05 * SR)
    fx[n - k:] *= np.linspace(1, 0, k)                                                     # nothing rings past 17.75
    return fx, rows
