$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$kicadBin = 'C:\Program Files\KiCad\10.0\bin'
Push-Location -LiteralPath $projectRoot
try {
    node C:/Code/Schrune/src/app.js build -l
    if ($LASTEXITCODE -ne 0) { throw 'Schrune build failed' }
    Copy-Item -LiteralPath 'build/2x3x3-Round.kicad_pcb' -Destination 'verification/generated.kicad_pcb' -Force
    & "$kicadBin\kicad-cli.exe" sch export netlist --format kicadxml -o verification/netlist.xml build/2x3x3-Round.kicad_sch
    if ($LASTEXITCODE -ne 0) { throw 'Netlist export failed' }
    foreach ($script in @('layout_round.py', 'route_round.py', 'sync_library.py', 'finish_board.py')) {
        & "$kicadBin\python.exe" "verification/$script"
        if ($LASTEXITCODE -ne 0) { throw "$script failed" }
    }
    & "$kicadBin\kicad-cli.exe" pcb drc --format json --schematic-parity --exit-code-violations -o verification/drc-final.json build/2x3x3-Round.kicad_pcb
    if ($LASTEXITCODE -ne 0) { throw 'DRC failed' }
    & "$kicadBin\python.exe" verification/audit_round.py
    if ($LASTEXITCODE -ne 0) { throw 'Board audit failed' }
} finally {
    Pop-Location
}
