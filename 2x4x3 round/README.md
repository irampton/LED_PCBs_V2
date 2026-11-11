# 2x4x3 round, 64 mm

Open `build/2x4x3-Round-64mm.kicad_pro`. The canonical board is
`build/2x4x3-Round-64mm.kicad_pcb`.

One two-sided, two-copper-layer FR4 board, 64 mm circular outline, 1.6 mm
thickness. Eight PT4115 channels drive three LEDs each: 12 warm and 12 cool.
The front has three rings of eight evenly spaced LEDs, alternating warm/cool,
at 9, 18 and 27 mm radii. The single populated 2x5 header remains on the front
left; all driver circuits are on the back. Two 2.7 mm NPTH holes are provided
for M2.5 mounting, at x=96.5 and 103.5, y=100 mm in PCB coordinates.

Copied from `2x3x3 round`, adding cool_d and warm_d in the Schrune source.
Nominal current remains 166.7 mA per string, with two 1.2R sense resistors in
parallel per channel. Four channels share cool PWM; four share warm PWM.
Firmware MUST enforce cool duty + warm duty <=100%; the PCB does not enforce
this itself. At nominal 6 V per LED the maximum average LED electrical load
is approximately 12 W under that limit, or 24 W if both inputs are fully on.

Header pinout: 1/3/7/9 = +24V; 2/4/8/10 = GND; 5 = cool PWM; 6 = warm PWM.

## Verification and status

- KiCad 10.0.4 DRC: zero errors, zero unconnected items, zero schematic parity
  issues. One unsuppressed **Copper sliver (B.Cu)** warning remains. KiCad
  supplies no item/location in that warning. Review the final manufacturing
  copper with the fabricator before releasing production.
- Independent XML netlist audit matches every electrical PCB pad/net.
- Audit confirms eight drivers, 24 LEDs, correct sides, 64 mm circle, three
  equal-count alternating rings and the combined PWM assumption.
- ERC: zero electrical errors; 109 inherited embedded-symbol library warnings.
- Native courtyard check finds no thermal-contact-to-component-body conflicts
  at 0.25 mm clearance. Imported courtyards and models are not dimensional
  qualification of the physical parts. Thermal testing has not been performed.
- Front/back plots and 3D views were inspected. Preview PNGs are in verification.

## Cooling and fabrication requirements

There are 24 exposed rear thermal contact lands, one per LED, with 153 thermal
vias in total. Most have six 0.5 mm drilled vias outside the LED lands. The
three crowded LED locations LED11, LED12 and LED14 instead use nine 0.3 mm
via-in-pad vias each. Several circuit routing vias also lie in component pads.
`verification/filled-vias.json` identifies all such positions, including bare
test-point lands. Require **filled and copper-capped** processing for component
pad vias. Tenting or ordinary soldermask plugging is not equivalent. A simple
ordering option is to request all 0.3 mm vias filled and capped. Confirm the
two-layer process and price with the fabricator; it is not in the assembly
estimate below. Prefer copper-paste-filled/capped vias for the thermal locations.

The rear contact lands carry DIFFERENT LIVE LED NETS. A bare metal heatsink or
conductive adhesive must not touch them directly. Use a specified electrically
insulating thermal interface with a qualified dielectric rating. Use insulating
washers at the mounting screws. A thin interface is desirable; its final type,
compressed thickness, pressure and dielectric performance need qualification.

See `heatsinks.md` for sourcing. `mechanical/thermal-contact-map.svg` gives
contact positions and back-side component bodies. `mechanical/spreader-concept.scad`
is a preliminary raised-contact spreader concept: 64 mm diameter, 3 mm base,
5.5 mm contact posts, and a nominal 0.3 mm interface gap. It is NOT a released
machining drawing: review contact flatness, compression, board warpage, screw
loads, component heights, tool radii and cooler mounting before manufacture.
Thinner qualified insulation may be needed for the final thermal budget.

Plan around 10–12 W of heat as a conservative starting budget with the duty
limit. Verify the hottest LED solder point and driver temperatures at steady
state, in the actual enclosure and orientation, at maximum ambient. Check the
LED's current derating curve including driver/current-sense tolerances.

## Live JLC parts and assembly estimate

Retrieved November 9, 2026 using Schrune jlc-bom pricing functions. Corrected
the filename-based joint undercount using actual PCB pads: 250 joints per board.
Standard assembly is required for both quantities because both sides are populated.

| Quantity | Components and assembly, USD | Per board |
|---|---:|---:|
| 30 | $165.72 | $5.52 |
| 100 | $333.49 | $3.33 |

Includes second-side setup/stencil allowances and a $3.50 batch hand-solder
allowance. Excludes PCB fabrication, ENIG/via fill/capping, heatsink, spreader,
insulation, hardware, shipping, taxes, attrition, minimum purchases and additional
manual assembly or panel fees. This is not a checkout quotation.

Warm LED C49435727 stock is 1,153; 100 boards require 1,200 before attrition,
so that run is short by at least 47 LEDs. Stock suffices for 30 boards. The
100-board price assumes additional stock can be procured at the reported tier.

## Rebuild

Run `verification/rebuild.ps1` in PowerShell. It runs Schrune build, exports
the netlist, constructs native KiCad board objects from the schematic netlist
and saved local footprint definitions, rebuilds the manual layout/routing,
fills zones, creates mask openings that follow the actual thermal copper,
synchronizes the local library, and runs DRC/audits. A pre-rebuild PCB copy is
saved under verification/backups. Manual layout edits are overwritten.

Schrune's initial 109-part draft grid exceeds KiCad's coordinate limit in this
installed version. The layout script therefore uses the generated schematic
netlist and libraries rather than loading that oversized draft. No PCB text
editing or external autorouter was used. There is no connected KiCad IPC
service here; native pcbnew and kicad-cli perform the board operations.

`verification/price.cjs` refreshes prices; `verification/thermal_map.py`
regenerates the contact map and preliminary spreader concept.
