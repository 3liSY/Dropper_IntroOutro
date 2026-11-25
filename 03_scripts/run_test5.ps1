# A few v5 frames at 720p for looking: renders them over any old copy into 05_renders/frames_v5test, then the look and captions.
#   powershell -File 03_scripts\run_test5.ps1 54,250,421 [samples] [extra blender options]
param([string]$only, [string]$samples = "24", [string]$extra = "")
$root = Split-Path $PSScriptRoot; Set-Location -LiteralPath $root
$o = "$root\05_renders\frames_v5test"
New-Item -ItemType Directory -Force -Path $o | Out-Null
$a = @('-b', '-P', '03_scripts\intro.py', '--', "$o\f.png", 'shot=full5', 'res=1280', "samples=$samples", "only=$only", 'force=1')
if ($extra) { $a += $extra.Split(' ') }
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' @a *> "$o\_log.txt"
Get-Content -LiteralPath "$o\_log.txt" | Select-String -Pattern 'Error|Traceback|line \d+, in|FULL5 DONE' | ForEach-Object { $_.Line }
python 03_scripts\post5.py stills $o "$o\p" @($only.Split(','))
