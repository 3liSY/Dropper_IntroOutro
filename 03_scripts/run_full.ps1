# The full intro preview: renders 0-17.75 s (1065 frames, 720p) in chunks into 05_renders/frames_full4_720p, a fresh Blender per chunk
# (one long session slows down and crashes). Existing frames are kept, so it can be re-run; then the look, captions, sound and video.
param([int]$chunk = 150, [string]$samples = "32")
$root = Split-Path $PSScriptRoot; Set-Location -LiteralPath $root
$o = "$root\05_renders\frames_full4_720p"
New-Item -ItemType Directory -Force -Path $o | Out-Null
$t = Get-Date
for ($pass = 1; $pass -le 3; $pass++) {
    for ($a = 0; $a -lt 1065; $a += $chunk) {
        $b = [Math]::Min($a + $chunk, 1065)
        $have = (Get-ChildItem -LiteralPath $o -Filter 'f_*.png' | Where-Object { [int]$_.BaseName.Substring(2) -ge $a -and [int]$_.BaseName.Substring(2) -lt $b }).Count
        if ($have -ge ($b - $a)) { continue }
        & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -P 03_scripts\intro.py -- "$o\f.png" shot=full4 res=1280 "samples=$samples" "f0=$a" "f1=$b" *> "$o\_render_$a.log"
        ('pass {0} chunk {1}-{2} done, {3:N0} s so far' -f $pass, $a, $b, ((Get-Date) - $t).TotalSeconds)
    }
    if ((Get-ChildItem -LiteralPath $o -Filter 'f_*.png').Count -ge 1065) { break }
}
('frames {0}, render {1:N0} s' -f (Get-ChildItem -LiteralPath $o -Filter 'f_*.png').Count, ((Get-Date) - $t).TotalSeconds)
python 03_scripts\post_full.py
