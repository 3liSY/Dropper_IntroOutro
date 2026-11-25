# Renders the Stage 2 test stills (720p) with any extra intro.py options, then the look pass.
#   powershell -File 03_scripts\run_stills.ps1 <tag> [shots] [extra options...]
param([string]$tag = "r1", [string]$shots = "down,two,shout", [Parameter(ValueFromRemainingArguments = $true)][string[]]$extra)
$root = Split-Path $PSScriptRoot; Set-Location -LiteralPath $root
$o = "$root\05_renders\review\v3"
New-Item -ItemType Directory -Force -Path $o | Out-Null
foreach ($s in $shots.Split(',')) {
    $raw = "$o\${s}_$tag.png"
    & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -P 03_scripts\intro.py -- $raw "shot=$s" res=1280 samples=48 @extra 2>&1 |
        Select-String -Pattern 'FIT|DONE|Error|Traceback|line \d' | Where-Object { $_ -notmatch 'Shadow buffer' } | ForEach-Object { "$s  $_" }
    python 03_scripts\post_still.py $raw "$o\${s}_${tag}_p.png" bloom=0.5 | Out-Null
}
