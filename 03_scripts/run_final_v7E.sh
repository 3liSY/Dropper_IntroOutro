#!/bin/bash
# v7E final 2026-11-24: 1080p60, every frame, no captions, SFX only. Safe to run again: frames already there are skipped.
cd "$(dirname "$0")/.." || exit 1; ROOT="$(pwd -W 2>/dev/null || pwd)"
export FACESET=B BOARDSET=E ARROWSET=B
O="$ROOT/05_renders/frames_v7E_1080p"; mkdir -p "$O"
for a in $(seq 0 100 1064); do b=$((a+100)); [ $b -gt 1065 ] && b=1065
  for pass in 1 2 3; do
    n=0; for i in $(seq $a $((b-1))); do p=$(printf %04d $i); [ -s "$O/f_$p.png" ] && [ -s "$O/m_$p.png" ] && n=$((n+1)); done
    [ $n -ge $((b-a)) ] && break
    "/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -P 03_scripts/intro.py -- "$O/f.png" shot=full5 res=1920 samples=32 f0=$a f1=$b > "$O/_render_$a.log" 2>&1
  done
  echo "$(date +%H:%M) chunk $a-$b: $(ls $O | grep -c ^f_) f, $(ls $O | grep -c ^m_) m"
done
