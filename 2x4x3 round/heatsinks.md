# Passive heatsink sourcing for the 64 mm eight-driver board

Research checked November 9, 2026. One two-sided board is retained; there are
no fixed enclosure diameter or depth limits. No purchases or supplier messages
were sent.

## Preferred route

Buy a standard passive LED cooler and commission a small raised-contact or
pocketed aluminum spreader, using the board/contact map to clear the back-side
components. Clamp through an electrically insulating thermal interface to the
24 live thermal lands, and couple the spreader's flat rear face to the cooler.
The board cannot make broad flat contact with a heatsink because of the rear
drivers, inductors, header tails and other components.

For 30 or 100 units, first request a combined cooler + machined-interface quote
from the LED cooler manufacturer/distributor, and compare that with a standard
cooler plus a local CNC-machined spreader. A custom extrusion die is unnecessary
for the initial batch. Ask suppliers to review the contact pattern, component
clearance, cooler orientation and thermal performance before ordering tooling.

## Shortlist

| Candidate | Size | Thermal data | Sourcing/use |
|---|---|---|---|
| **MechaTronix MODULED MICRO 8650-B** | 86 mm diameter x 50 mm high | Manufacturer table gives 20°C rise at 10 W heat and 27°C at 15 W; nominal 1.5°C/W corresponds to a higher test load | Preferred starting point since enclosure size is open. Request 30/100-unit pricing and machining/interface advice through CDI or MechaTronix. |
| Fischer SK 578/37,5 SA | 60 mm diameter x 37.5 mm high | RS lists 1.8°C/W; distributor listings disagree about natural vs forced-air figures, so obtain the manufacturer curve for the actual orientation | Smaller option. RS US lists order code 70748507; EU RS lists 722-6795. Confirm stock, delivered price and passive performance. |
| Wakefield 882-300AB | 76.2 mm diameter x 76.2 mm high | Manufacturer lists 28°C natural-convection rise at 9 W; the 1.55°C/W figure is FORCED convection | Readily identifiable US distribution route, but taller and less attractive passive performance than the ModuLED option. |

Do not use a distributor's forced-convection rating as the fanless design
rating. Likewise, a nominal heatsink rating at a 50°C rise does not describe
its resistance at every load. For the ModuLED 8650, interpolate its actual
10–15 W manufacturer data: approximately 20–25°C sink rise is a reasonable
planning estimate around 10–12 W heat under the published conditions. Add the
spreader/interface/PCB/package temperature rises; that is not an LED junction
temperature prediction.

The existing LED datasheet gives roughly 20°C/W junction-to-solder resistance.
At full-on operation of one color, individual active packages still dissipate
substantial heat even though the combined average input is limited. The common
PWM limit reduces total cooling load; it does not eliminate local hot spots.
The hottest solder-point temperature, including current tolerances, is the
prototype acceptance measurement.

## What to send for quotations

- Final PCB and rear 3D view, with a statement that this is a 64 mm FR4 board.
- Contact map and component-clearance map in mechanical/.
- Preliminary spreader SCAD file, clearly marked CONCEPT / NOT FOR MACHINING.
- Required maximum ambient, mounting orientation and desired touch temperature
  once the enclosure is defined; these are currently unspecified.
- 30 and 100 unit quantities; request cooler, spreader machining, insulating
  interface and mounting hardware as separate cost lines.
- Ask for sample hardware before committing the full production quantity.

The 7 mm spacing of the board's two M2.5 mounting holes is a custom spreader
interface, not a claimed match to any heatsink's factory hole pattern. The
spreader-to-cooler attachment must be adapted to the selected cooler drawing.
The SCAD concept does not yet define that attachment.

## Fabrication and insulation

The PCB needs filled/copper-capped vias in component lands. JLC documents the
distinction between tenting, soldermask plugging, epoxy filling/capping and
copper-paste filling/capping. Obtain a specific two-layer fabrication quote;
the assembly estimate does not include this process.

Never bridge the thermal lands with bare metal, conductive adhesive, or an
unspecified thermal paste. Choose a genuine electrically insulating thermal
pad/film with a qualified dielectric rating, controlled compressed thickness,
and pressure. Typical paste recommendations for an electrically isolated LED
module are not sufficient for this board's live contact pattern.

## Sources

- [CDI: ModuLED Micro 8650-B, distributor and quote route](https://www.cdiweb.com/products/detail/moduledmicro8650b-mechatronix/574036/)
- [MechaTronix manufacturer drawings and load-dependent thermal data, hosted by CDI](https://www.cdiweb.com/datasheets/mechatronix/ModuLED_Micro_Modular_Passive_Star_LED_Cooler86.pdf)
- [RS US: Fischer SK 578/37,5 SA](https://us.rs-online.com/product/fischer/sk-578-37-5-sa/70748507/)
- [RS EU: same Fischer part](https://de.rs-online.com/web/p/kuhlkorper/7226795)
- [Fischer manufacturer LED-heatsink catalog excerpt, hosted by RS](https://docs.rs-online.com/f613/0900766b80f3d60f.pdf)
- [Wakefield manufacturer: 882-300AB](https://wakefieldthermal.com/wakefield-thermal-76-2mm-round-heatsink-star-led-board-882-300ab/)
- [JLC: via covering process definitions](https://jlcpcb.com/help/article/pcb-via-covering)
- [JLC: via-in-pad process and ordering](https://jlcpcb.com/help/article/via-in-pad-pofv-guide)
- [Cree: thermal-stack and measurement methods](https://downloads.cree-led.com/files/da/x/XLamp-Thermal-Management.pdf)
