param(
    [string]$SchruneApp = 'C:/Code/Schrune/src/app.js'
)

$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    & node $SchruneApp build
    if ($LASTEXITCODE -ne 0) {
        throw "Schrune exited with code $LASTEXITCODE."
    }

    $boardPath = 'build/ESP32 Controller.kicad_pcb'
    $sheetPath = 'build/ESP32 Controller.kicad_sch'
    $board = Get-Content -Raw -LiteralPath $boardPath
    $sheet = Get-Content -Raw -LiteralPath $sheetPath
    $datasheets = @{}
    foreach ($footprint in [regex]::Matches($board, '(?ms)^\t\(footprint .*?^\t\)')) {
        $reference = [regex]::Match($footprint.Value, '\(property "Reference" "([^"]+)"')
        $datasheet = [regex]::Match($footprint.Value, '\(property "Datasheet" ("[^"]+")')
        if ($reference.Success -and $datasheet.Success) {
            $datasheets[$reference.Groups[1].Value] = $datasheet.Groups[1].Value
        }
    }

    # The compiler's fixed component grid extends below the A1 border.
    $sheet = $sheet.Replace('(paper "A1")', '(paper "A0")')
    $sheet = [regex]::Replace($sheet, '(?ms)^  \(symbol \(lib_id .*?^  \)', {
        param($symbol)
        $reference = [regex]::Match($symbol.Value, '\(property "Reference" "([^"]+)"')
        $datasheet = $datasheets[$reference.Groups[1].Value]
        if ($datasheet) {
            $position = [regex]::Match($symbol.Value, '\(at [^)]+\)').Value
            $property = '    (property "Datasheet" {0} {1} (hide yes) (effects (font (size 1.27 1.27))))' -f $datasheet, $position
            return $symbol.Value.Insert($symbol.Value.Length - 3, "$property`n")
        }
        return $symbol.Value
    })
    Set-Content -NoNewline -Encoding utf8 -LiteralPath $sheetPath -Value $sheet
} finally {
    Pop-Location
}
