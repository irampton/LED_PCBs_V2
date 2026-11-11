# ESP32 Controller

Open `build/ESP32 Controller.kicad_pro` in KiCad 10. The Schrune source is
`main.schrune`, with the imported symbols, footprints, and STEP models in
`parts/`.

Run `./build.ps1` to regenerate the schematic and BOM with the local Schrune
checkout. Pass `-SchruneApp <path-to-src/app.js>` for a different installation.
The build uses the designator assignments in
`build/.schrune-designators.json` to keep PCB references stable.

The routed PCB came from `ESP32-Controller/layouts/default/default.kicad_pcb`.
Its fabrication geometry matches the source across all nine plotted layers
and both drill files. The schematic has 38 components and matches all 34
original nets. KiCad reports zero schematic parity issues and zero
unconnected items.

The original board's R2 thermal-relief error and missing QR footprint library
warning are present in the copy. Schematic ERC reports warnings for embedded
symbols without library links and for named single-pin nets.
