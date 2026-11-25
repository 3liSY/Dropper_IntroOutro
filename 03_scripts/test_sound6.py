"""test_sound6.py - checks sound6.py without the picture: every option of every cue loads and builds, nothing is NaN,
and each cue's spike lands -1 to +3 frames from its picture event. Prints the gap table.

    python test_sound6.py            # all options
Spike = the first point within 6 dB of the cue's own loudest point (that is where the ear hears the hit)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound6  # noqa: E402

SR, FPS, N = 48000, 60, int(17.75 * 48000)
VR = 0.1                                                     # any voice level works: the test looks at timing, not loudness
bad = []
print("cue  opt  event_f  spike_f  gap_f  peak_gap_f  ok")
for cue, opts in sound6.OPTIONS.items():
    for opt, layers in opts.items():
        if not layers:
            print("%-4s %-4s %7.1f  silent" % (cue, opt, sound6.FRAMES[cue]))
            continue
        s = sound6.cue_signal(cue, opt, N, SR)
        if not np.isfinite(s).all() or np.abs(s).max() == 0:
            bad.append((cue, opt, "empty or NaN"))
            continue
        ev = sound6.FRAMES[cue]
        if cue == "U5":                                      # one tap per score change: build each tap alone and check it against its own change
            for f, layer in zip(sound6.U5_ALL, layers):        # (Stage B 2026-11-21: the fast count puts taps 2-3 frames apart, so a shared window no longer works)
                sound6.OPTIONS["U5"]["_one"] = [layer]
                a1 = np.abs(sound6.cue_signal("U5", "_one", N, SR))
                pk1 = int(np.argmax(a1))
                lo1 = max(0, pk1 - int(0.5 * SR))
                sp = (lo1 + int(np.argmax(a1[lo1:pk1 + 1] > a1[pk1] * 0.5))) / SR * FPS
                ok = -1 <= sp - f <= 3
                bad += [] if ok else [(cue, opt, "tap at f%d is %.1f frames off" % (f, sp - f))]
            del sound6.OPTIONS["U5"]["_one"]
            print("%-4s %-4s  %2d taps                         %s" % (cue, opt, len(layers), "yes" if not [b for b in bad if b[:2] == (cue, opt)] else "NO"))
            continue
        a = np.abs(s)
        pk = int(np.argmax(a))
        lo = max(0, pk - int(0.5 * SR))
        sp = lo + int(np.argmax(a[lo:pk + 1] > a[pk] * 0.5))  # first point within 6 dB of the peak, at most 0.5 s before it
        gap, pgap = sp / SR * FPS - ev, pk / SR * FPS - ev
        ok = -1 <= gap <= 3
        if not ok:
            bad.append((cue, opt, "spike %.1f frames off" % gap))
        print("%-4s %-4s %7.1f  %7.1f  %5.1f  %10.1f  %s" % (cue, opt, ev, sp / SR * FPS, gap, pgap, "yes" if ok else "NO"))
fx, rows = sound6.build(N, SR, VR, {})
assert np.isfinite(fx).all() and len(fx) == N
w0 = int((sound6.EVENTS["W1"] - sound6.QUIET_BEFORE_W1) * SR)
quiet = np.abs(fx[w0:int((sound6.EVENTS["W1"] - 0.03) * SR)]).max()   # the 150 ms before the wall: only the wall's own lead-in may sound
print("quiet before wall (dB vs wall peak): %.1f" % (20 * np.log10(quiet / np.abs(fx).max() + 1e-12)))

# the peak tools added 2026-11-21: the voice dip, the voice step-back and the peak hold
t = np.arange(N) / SR
v = 0.3 * np.sin(2 * np.pi * 220 * t)
d = sound6.dip_voice(v, SR)
e = int(sound6.EVENTS["W1"] * SR)
if abs(np.abs(d[e:e + 2400]).max() / 0.3 - 10 ** (sound6.DIP_DB / 20)) > 0.02 or abs(np.abs(d[:2400]).max() - 0.3) > 1e-6:
    bad.append(("dip", "-", "voice dip is not %g dB at the wall or not 0 dB at the start" % sound6.DIP_DB))
f = np.zeros(N)
f[e:e + 480] = 0.8                                           # a 10 ms hit at 0.8 under a voice at 0.3, limit 0.9
y, ydb, yms = sound6.yield_voice(v, f, SR, 0.9)
if (np.abs(y + f) > 0.9 + 1e-3).any() or abs(np.abs(y[:2400]).max() - 0.3) > 1e-6 or not 0 < yms < 200:   # 10 ms hit + 50 ms recovery from -9.5 dB = ~130 ms
    bad.append(("yield", "-", "voice + hit passes the limit, or the voice moves away from the hit (%.1f dB, %d ms)" % (ydb, yms)))
s = np.zeros(N)
s[e] = 1.0                                                   # one spike over a 0.5 ceiling must stay on its sample, held under the ceiling
h = sound6.peak_hold(s, SR, 0.5, os.path.join(os.environ.get("TEMP", "."), "test_sound6_hold.wav"))
if int(np.argmax(np.abs(h))) != e or np.abs(h).max() > 0.5 * 1.01:
    bad.append(("hold", "-", "peak hold moved the spike %d samples or let it reach %.3f" % (int(np.argmax(np.abs(h))) - e, np.abs(h).max())))
print("peak tools: dip, step-back and hold checked")
print("FAIL" if bad else "PASS", *bad, sep="\n  ")
