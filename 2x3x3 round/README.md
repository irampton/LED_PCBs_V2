# 2x3x3 round LED board

Open `build/2x3x3-Round.kicad_pro`; the final board is
`build/2x3x3-Round.kicad_pcb`.

Copied the Schrune source and parts from 2x2x3. Added cool_c and warm_c,
removed h2, and made the retained h1 a populated part. There are six PT4115
channels, three series LEDs per channel, nine warm and nine cool LEDs.
The existing two PWM inputs still control the three warm channels together
and the three cool channels together. Sense resistance remains two 1.2R
resistors in parallel per channel: 0.600R, nominal 166.7 mA.

The board is a true 84 mm diameter circle, two copper layers, 1.6 mm thick.
Three concentric LED rings have radii 12, 24 and 36 mm. Every ring contains
six equally spaced LEDs, alternating warm/cool. All LEDs and the one 2x5
through-hole header are on the front; all driver circuitry and test points
are on the back. The header fits inside the left edge, so no bump is needed.
The old rectangular outline and mounting holes were not retained.

Header pinout is unchanged: 1/3/7/9 = +24V, 2/4/8/10 = GND,
5 = cool PWM, 6 = warm PWM. C/W silkscreen identifies each LED color.
The header is included in the new BOM; unlike the original board it is
not marked DNP. Test points remain bare PCB probe lands.

Routing reuses the proven compact local switching, current-sense and DIM
connections from the original channel, mirrored onto the back and repeated
around the circle. VIN capacitors have short connections to their drivers.
The front has a V+ pour; the back has a GND pour. Ordinary drilled vias are
outside component solder lands. No external autorouter was used.

KiCad 10.0.4 final verification:

- DRC: zero errors/warnings, zero unconnected items, zero schematic parity issues.
- An independent schematic XML netlist comparison matches every board pad/net.
- Native API audit confirms 83 footprints, six drivers, 18 LEDs, one populated
  front header, correct component sides, circular outline and alternating rings.
- ERC: zero electrical errors; 83 inherited symbol-library warnings because
  Schrune embeds symbols without a named library prefix. These are not suppressed.
- Copper plots and top/bottom 3D views were visually reviewed.

The original imported header STEP has an unrelated assembly origin. A centred
nominal header VRML replaces it for visualization. All 3D models are visual
representations, not dimensional qualification of the actual components.

## Price estimate

Live Schrune JLC pricing retrieved November 9, 2026, USD. Standard assembly
is required at both quantities because components populate both sides.
Corrected the tool's footprint lookup undercount using actual board pads:
190 solder joints per populated board, including the header.

| Item | 30 boards | 100 boards |
|---|---:|---:|
| Components, including header | $51.537 | $157.02 |
| Standard setup | $25.00 | $25.00 |
| Standard stencil | $7.68 | $7.68 |
| Solder joints | $9.12 | $30.40 |
| Loader fees | $16.50 | $16.50 |
| Second-side setup allowance | $25.00 | $25.00 |
| Second-side stencil allowance | $7.86 | $7.86 |
| Hand-solder allowance | $3.50 | $3.50 |
| Estimated batch total | **$146.20** | **$272.96** |
| Estimated per board | **$4.87** | **$2.73** |

All BOM lines report enough stock for 100 boards; the warm LED requires
900 pieces against 1,153 reported in stock, before attrition. These are
component/assembly estimates, not checkout quotes. PCB fabrication, shipping,
tax, attrition, minimum purchases and other panel/manual-assembly/x-ray fees
are excluded. The through-hole header and second-side surcharges need quote
confirmation; $3.50 is only a hand-solder allowance.

At nominal 6 V per LED and 166.7 mA, the LEDs consume approximately 18 W
at full output before driver losses. Cooling and peak LED current require
prototype validation; DRC does not establish thermal performance.

## Rebuild

Run `verification/rebuild.ps1` from PowerShell. It runs Schrune build -l,
exports the schematic netlist, rebuilds placement/routing through KiCad's
native board API, synchronizes the local corrected footprint library, and
runs DRC and the independent board audit. This intentionally overwrites the
round board layout; preserve manual edits before rerunning it.

Schrune build alone generates schematics/BOM and a draft PCB, not the final
round layout. This machine has no connected KiCad IPC service; native pcbnew
and kicad-cli were used instead. `verification/price.cjs` refreshes the live
component pricing and calculates the corrected double-sided estimate.
