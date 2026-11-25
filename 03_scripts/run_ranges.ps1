# Re-renders only some frame ranges of the full intro (overwrites them), then the look, captions, sound and video.
#   powershell -File 03_scripts\run_ranges.ps1 0-120 570-640 1000-1065
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ranges)
$root = Split-Path $PSScriptRoot; Set-Location -LiteralPath $root
$o = "$root\05_renders\frames_full4_720p"
foreach ($rg in $ranges) {
    $a, $b = $rg.Split('-')
    & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -P 03_scripts\intro.py -- "$o\f.png" shot=full4 res=1280 samples=32 "f0=$a" "f1=$b" force=1 *> "$o\_range_$a.log"
    "range $rg done"
}
python 03_scripts\post_full.py
