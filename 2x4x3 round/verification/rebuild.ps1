$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$kicadBin = 'C:\Program Files\KiCad\10.0\bin'
Push-Location -LiteralPath $projectRoot
try {
    New-Item -ItemType Directory -Path verification/backups -Force | Out-Null
    if (Test-Path -LiteralPath build/2x4x3-Round-64mm.kicad_pcb) {
        Copy-Item -LiteralPath build/2x4x3-Round-64mm.kicad_pcb -Destination verification/backups/pre-rebuild.kicad_pcb -Force
    }
    node C:/Code/Schrune/src/app.js build -l
    if ($LASTEXITCODE -ne 0) { throw 'Schrune build failed' }
    & "$kicadBin\kicad-cli.exe" sch export netlist --format kicadxml -o verification/netlist.xml build/2x4x3-Round-64mm.kicad_sch
    if ($LASTEXITCODE -ne 0) { throw 'Netlist export failed' }
    foreach ($script in @('layout.py', 'route.py', 'finish.py', 'sync_library.py', 'normalize_library_instances.py')) {
        & "$kicadBin\python.exe" "verification/$script"
        if ($LASTEXITCODE -ne 0) { throw "$script failed" }
    }
    & "$kicadBin\kicad-cli.exe" pcb drc --severity-error --exit-code-violations --format json --schematic-parity -o verification/drc-errors.json build/2x4x3-Round-64mm.kicad_pcb
    if ($LASTEXITCODE -ne 0) { throw 'DRC errors remain' }
    & "$kicadBin\kicad-cli.exe" pcb drc --format json --schematic-parity -o verification/drc-final.json build/2x4x3-Round-64mm.kicad_pcb
    & "$kicadBin\python.exe" verification/audit.py
    if ($LASTEXITCODE -ne 0) { throw 'Board audit failed' }
    & "$kicadBin\python.exe" verification/thermal_map.py
    if ($LASTEXITCODE -ne 0) { throw 'Contact map failed' }
} finally {
    Pop-Location
}
