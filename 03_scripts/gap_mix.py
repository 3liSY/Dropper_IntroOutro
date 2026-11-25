"""gap_mix.py - the gap table on the real mastered mix (2026-11-21). Run after post5.

    python gap_mix.py <TAG>      # reads 05_renders/edit_v5_<TAG>/_no_voice.wav (effects only) and _with_voice.wav

For each cue: in the window 2 frames before to 6 frames after its picture event, the spike is the first point
within 6 dB of that window's loudest point (2 ms peak envelope). Gap = spike frame - event frame; the bar is -1..+3.
Rise = how much louder the window peak is than the 8 frames before it (a cue that does not rise is not heard as a hit).
Also prints integrated loudness and true peak of both files (ffmpeg ebur128)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as PA  # noqa: E402
import sound6 as S6  # noqa: E402

SR, FPS, T_END = 48000, 60, 17.75
DST = os.path.join(PA.RENDERS, "edit_v5_%s" % sys.argv[1])
wn, ww = os.path.join(DST, "_no_voice.wav"), os.path.join(DST, "_with_voice.wav")
n = int(T_END * SR)
fx = S6.read_wav(wn, SR, n)
k = int(0.002 * SR)
env = np.array([np.abs(fx[i:i + k]).max() for i in range(0, n - k, k)])   # one value per 2 ms
step = k / SR * FPS                                                         # frames per envelope step


def at(f):
    return int(round(f / step))


bad = []
print("cue   event_f  spike_f  gap_f  rise_dB  ok")
evs = sorted(S6.FRAMES.values())
for cue, ev in S6.FRAMES.items():
    nxt = min([e for e in evs if e > ev] or [ev + 99])
    a, b = at(ev - 2), at(min(ev + 6, nxt - 2))                # stop before the next cue's lead-in (swing 417 / punch 421 are 4 frames apart)
    w = env[a:b]
    pk = w.max()
    sp = a + int(np.argmax(w > pk * 0.5))
    before = env[at(ev - 10):at(ev - 2)].max() + 1e-9
    gap, rise = sp * step - ev, 20 * np.log10(pk / before)
    ok = -1 <= gap <= 3 and rise >= 1
    if not ok:
        bad.append("%s %s" % (cue, "%.1f frames off" % gap if rise >= 1 else "no rise: hidden under the sound before it, or silent"))
    print("%-4s  %7d  %7.1f  %5.1f  %7.1f  %s" % (cue, ev, sp * step, gap, rise, "yes" if ok else "NO"))
for name, p in (("with voice", ww), ("effects only", wn)):
    li, tp = S6.lufs(p)
    print("%-12s %.1f LUFS, true peak %.1f dB" % (name, li, tp))
print("FAIL" if bad else "PASS", *bad, sep="\n  ")
