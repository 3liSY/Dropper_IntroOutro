# V4 motion test: renders intro 6.0-12.0 s (360 frames, 720p) into 05_renders/frames_v4test_720p, then the look, sound and video.
$root = Split-Path $PSScriptRoot; Set-Location -LiteralPath $root
$o = "$root\05_renders\frames_v4test_720p"
New-Item -ItemType Directory -Force -Path $o | Out-Null
$t = Get-Date
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -P 03_scripts\intro.py -- "$o\f.png" shot=clip4 res=1280 samples=32 @args *> "$o\_render.log"
('render {0:N0}s' -f ((Get-Date) - $t).TotalSeconds)
python 03_scripts\post_v4.py
