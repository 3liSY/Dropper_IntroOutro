# Stage 3: renders the 3 s motion clip (intro 6.10-9.10 s) at 720p into 05_renders/frames_clip3_720p (existing frames are kept).
$root = Split-Path $PSScriptRoot; Set-Location -LiteralPath $root
$o = "$root\05_renders\frames_clip3_720p"
New-Item -ItemType Directory -Force -Path $o | Out-Null
$t = Get-Date
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -P 03_scripts\intro.py -- "$o\f.png" shot=clip res=1280 samples=32 2>&1 |
    Select-String -Pattern 'FRAME|DONE|Traceback|line \d' | Out-File -FilePath "$o\_render.log" -Encoding utf8
('done {0:N0}s' -f ((Get-Date) - $t).TotalSeconds) | Add-Content -LiteralPath "$o\_render.log"
