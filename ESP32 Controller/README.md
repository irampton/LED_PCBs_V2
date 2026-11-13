# ESP32 Controller

Open `build/ESP32 Controller.kicad_pro` in KiCad 10. The Schrune source is
`main.schrune`, with the imported symbols, footprints, and STEP models in
`parts/`.

Run `./build.ps1` to regenerate the schematic and BOM with the local Schrune
checkout. Pass `-SchruneApp <path-to-src/app.js>` for a different installation.
The build uses the designator assignments in
`build/.schrune-designators.json` to keep PCB references stable.

`buck.schrune` contains the reusable `Buck5V` module and a standalone `top`.
It exposes only `input.h/input.l` and `output.h/output.l`; the low sides are
connected internally. `main.schrune` imports it and connects V+, 5V and ground.
No external enable, feedback, filtering or compensation components are required.

`old_buck.schrune` preserves the original 17-component TPS54331 circuit as an
alternative `Buck5V` module with the same input/output rails. To select it,
change only the import in `main.schrune` to
`@require(Buck5V from "./old_buck.schrune");`. It also has a standalone `top`.
An isolated build of the controller using this import matches all 38 original
components, footprints and 34 pin-level nets, allowing reference/net renaming.
The active controller continues to use `buck.schrune`.

The supply targets 7–28 V DC input and 5 V output, up to 2 A subject to layout
and thermal validation. It replaces the original 3 A TPS54331 circuit.
The XL1509 is internally compensated; FB connects directly to the output and
ON/OFF connects to ground. All four ground pins are connected.

| Function | Part | LCSC | Rating |
| --- | --- | --- | --- |
| Regulator | XL1509-5.0E1 | C61063 | Fixed 5 V, 2 A |
| Inductor | XR1040-680M | C5307658 | 68 uH, 2.5 A Irms typ, 3 A Isat typ, 195 mOhm max DCR |
| Input bulk (2 in parallel) | RVE470UF35V167RV084 | C5155332 | Each 470 uF, 35 V, 670 mA ripple at 100 kHz |
| Input bypass | 1206B475K500NT | C29823 | 4.7 uF, 50 V, X7R, 1206 |
| Output bulk | RVE470UF35V167RV084 | C5155332 | 470 uF, 35 V, ESR <= 230 mOhm at 100 kHz |
| Catch diode | SS34 | C8678 | 3 A, 40 V |

All seven buck components are SMD. The three electrolytics share one part
number, so they incur only one Extended-part loading fee. The two input
capacitors provide 940 uF nominal and a combined 1.34 A ripple rating; connect
them with similar short paths. The first-order worst input RMS ripple is about
1 A at 2 A load. The 35 V rating retains 20% voltage headroom at 28 V input.
The ceramic bypass supplements the bulk capacitors rather than supplying the
required bulk capacitance after DC-bias derating.

At 28 V input, 127 kHz and -20% inductance tolerance, the ideal inductor ripple
is about 0.59 A peak-to-peak (2.30 A peak, 2.01 A RMS at 2 A load). The selected
inductor specifies 3 A typical Isat at 30% inductance loss and 2.5 A typical
Irms at 40 C rise. Its maximum DCR gives about 0.79 W copper loss at 2 A,
versus about 0.26 W for the first XL1509 inductor. Both have 30 V maximum ratings.

The lower-cost output capacitor has higher ESR: first-order ripple is roughly
0.14 V peak-to-peak at the above corner, excluding switching spikes, inductance
loss under bias and temperature effects. This is a cost/ripple/thermal tradeoff,
not an equal-performance substitution. The capacitor lifetime rating is
2,000 h at 105 C. Validate ripple, loop stability, temperatures and lifetime
at the actual load and ambient temperature before production.

Keep the VIN bypass and catch-diode loops short, use a ground plane, and sense
FB at the output capacitor away from the switching node. Verify startup,
load transients, ripple and temperatures before release.

Sources: [XL1509 reference circuit](https://www.xlsemi.com/datasheet/XL1509-EN.pdf),
[inductor datasheet](https://www.lcsc.com/datasheet/C5307658.pdf),
[shared capacitor datasheet](https://www.lcsc.com/datasheet/C5155332.pdf).

The updated controller schematic has 28 components. The routed PCB still
contains the original TPS54331 design and requires placement/routing changes;
it is not fabrication-ready for this revised schematic.

Standalone compilation: `node C:/Code/Schrune/src/app.js build buck.schrune`.
Run `./build.ps1` afterward to regenerate the controller's shared build library
and designator map. Both sources compile; exported KiCad netlists verify the
buck connections. Standalone ERC has seven library-link warnings, no errors.

For 10 boards, the refreshed Schrune JLC-BOM Economic estimates on 2026-11-11
are $74.90 original and $78.02 optimized XL1509. The earlier XL1509 estimate
was $85.87 and omitted the unpriced C264063 capacitor. The optimized BOM is
fully priced with sufficient stock. See [cost comparison](buck-cost-comparison.md)
for all added/removed parts and loading fees. These estimates exclude PCB
fabrication, shipping and other order-specific charges. Schrune undercounts
joints where older imported parts have blank BOM footprint metadata.

The original board's R2 thermal-relief error and missing QR footprint library
warning are present in the copy. Schematic ERC reports warnings for embedded
symbols without library links and for named single-pin nets.
