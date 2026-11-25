# v5 frames in chunks of 150 into 05_renders/frames_v5_720p, a fresh Blender per chunk (one long session slows down and crashes).
#   powershell -File 03_scripts\run_full5.ps1                      everything missing, 0 to the freeze frame
#   powershell -File 03_scripts\run_full5.ps1 330-540 540-870      only these ranges
#   powershell -File 03_scripts\run_full5.ps1 330-540 -force       re-render them over the old copies
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ranges)
$root = Split-Path $PSScriptRoot; Set-Location -LiteralPath $root
$o = "$root\05_renders\frames_v5_720p"
New-Item -ItemType Directory -Force -Path $o | Out-Null
$force = $ranges -contains '-force'
$ranges = @($ranges | Where-Object { $_ -ne '-force' })
if ($ranges.Count -eq 0) { $ranges = @('0-1059') }
$t = Get-Date
foreach ($rg in $ranges) {
    $lo, $hi = $rg.Split('-')
    for ($a = [int]$lo; $a -lt [int]$hi; $a += 150) {
        $b = [Math]::Min($a + 150, [int]$hi)
        $args5 = @('-b', '-P', '03_scripts\intro.py', '--', "$o\f.png", 'shot=full5', 'res=1280', 'samples=32', "f0=$a", "f1=$b")
        if ($force) { $args5 += 'force=1' }
        # with -force only frames written in this run count, so a Blender crash can never leave old frames passing as new (2026-11-08: 787-869 stayed old after a crash)
        $tc = Get-Date
        for ($pass = 1; $pass -le 3; $pass++) {
            & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' @args5 *> "$o\_render_$a.log"
            $have = (Get-ChildItem -LiteralPath $o -Filter 'f_*.png' | Where-Object { [int]$_.BaseName.Substring(2) -ge $a -and [int]$_.BaseName.Substring(2) -lt $b -and (-not $force -or $_.LastWriteTime -ge $tc) }).Count
            if ($have -ge ($b - $a)) { break }
            if ($force) { $args5 = @($args5 | Where-Object { $_ -notlike 'f0=*' }) + @("f0=$($a + $have)") }
        }
        if ($have -lt ($b - $a)) { "CHUNK $a-$b INCOMPLETE: only $have new frames, check $o\_render_$a.log" }
        ('chunk {0}-{1} done, {2:N0} s so far' -f $a, $b, ((Get-Date) - $t).TotalSeconds)
    }
}
('frames {0}, render {1:N0} s' -f (Get-ChildItem -LiteralPath $o -Filter 'f_*.png').Count, ((Get-Date) - $t).TotalSeconds)
