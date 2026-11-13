# Buck cost comparison

USD, 10 complete controller boards, Economic assembly. Prices refreshed with
`node C:/Code/Schrune/src/app.js tools jlc-bom -n 10` on 2026-11-11.
Quantities below are per board; extended costs are for all 10 boards.

| Design | Components | Extended fees | Setup + stencil | Reported joints | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original TPS54331 | $47.40 | $18.00 | $9.50 | $0.00 | $74.90 |
| First XL1509 version (earlier quote) | $52.31* | $24.00 | $9.50 | $0.06 | $85.87* |
| Optimized XL1509 | $47.43 | $21.00 | $9.50 | $0.10 | $78.02 |

The optimized estimate is $7.85 below the earlier XL1509 lower-bound estimate,
and $3.12 above the refreshed original. Totals are calculated before rounding
each displayed line. *The first XL1509 estimate counted C264063 as $0 because
its price/stock was unavailable; it was not a complete quote.

No suitable no-fee 68 uH inductor or 470 uF electrolytic was found in the live
JLC searches and PCBParts snapshot. The regulator, catch diode and bypass
capacitor are already Basic. Savings come from cheaper Extended parts and
sharing one bulk-capacitor part number, removing one $3 loading fee. Both new
part types are listed as eligible for Economic assembly, and all buck parts
are now SMD.

## Changes from the first XL1509 version

| Action | Part | LCSC | Qty/board | Unit price | Parts for 10 boards | Unique-part fee |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Remove | CYH125-68UH, 68 uH inductor | C7431083 | 1 | $0.3570* | $3.570* | $3 |
| Remove | EEUFR1H471, 470 uF / 50 V input | C178708 | 1 | $0.6817* | $6.817* | $3 |
| Remove | EEUFR1V221, 220 uF / 35 V output | C264063 | 1 | Unknown | Unknown | $3 |
| Add | XR1040-680M, 68 uH inductor | C5307658 | 1 | $0.1500 | $1.500 | $3 |
| Add | RVE470UF35V167RV084, 470 uF / 35 V | C5155332 | 3 | $0.1327 | $3.981 | $3 total |

*Removed-part prices are from the earlier run, retained for traceability.
Two identical capacitors are on the input and one is on the output. Compared
with the first version, the inductor has higher copper loss, the output has
higher ripple, and the bulk capacitors have a shorter rated lifetime. The
electrical calculations and limits are in README.md. This is a cost-oriented
design requiring hardware validation, not a claim of equal performance.

## Parts removed from the original TPS54331 buck

One of the two original 4.7 uF input capacitors and the SS34 catch diode are
retained. The following are the actual removed quantities, not whole-board
BOM quantities for parts also used elsewhere.

| Removed part / function | LCSC | Class | Qty/board | Unit price | Parts for 10 boards |
| --- | --- | --- | ---: | ---: | ---: |
| TPS54331DR regulator | C9865 | Promoted Extended | 1 | $0.2814 | $2.814 |
| SL0630-6R8M, 6.8 uH inductor | C22463822 | Extended | 1 | $0.0889 | $0.889 |
| CL05B104KO5NNNC, 100 nF bootstrap | C1525 | Basic | 1 | $0.0029 | $0.029 |
| CL05B103KB5NNNC, 10 nF bypass/soft-start | C15195 | Basic | 2 | $0.0037 | $0.074 |
| 1206B475K500NT, one 4.7 uF input capacitor | C29823 | Basic | 1 | $0.0697 | $0.697 |
| 0402CG470J500NT, 47 pF compensation | C1567 | Basic | 1 | $0.0044 | $0.044 |
| 0402B102K500NT, 1 nF compensation | C1523 | Basic | 1 | $0.0036 | $0.036 |
| CL31A476MPHNNNE, 47 uF output capacitors | C96123 | Basic | 2 | $0.1628 | $3.256 |
| 0402WGF1002TCE, 10 kR feedback | C25744 | Basic | 1 | $0.0010 | $0.010 |
| 0603WAF1801T5E, 1.8 kR feedback | C4177 | Basic | 1 | $0.0021 | $0.021 |
| 0603WAF3002T5E, 30 kR compensation | C22984 | Basic | 1 | $0.0024 | $0.024 |
| 0402WGF3303TCE, 330 kR enable | C25778 | Promoted Extended | 1 | $0.0013 | $0.013 |
| 0402WGF6802TCE, 68 kR enable | C36871 | Promoted Extended | 1 | $0.0012 | $0.012 |
| **Removed parts subtotal** | | | **15** | | **$7.919** |

Removing the original inductor also removes its $3 Extended-part fee.

## Parts added relative to the original

| Added part | LCSC | Class | Qty/board | Unit price | Parts for 10 boards |
| --- | --- | --- | ---: | ---: | ---: |
| XL1509-5.0E1 regulator | C61063 | Basic | 1 | $0.2465 | $2.465 |
| XR1040-680M, 68 uH inductor | C5307658 | Extended | 1 | $0.1500 | $1.500 |
| RVE470UF35V167RV084, 470 uF / 35 V | C5155332 | Extended | 3 | $0.1327 | $3.981 |
| **Added parts subtotal** | | | **5** | | **$7.946** |

The two new Extended types add $6 in fees. Net change versus the original is
$0.027 in components + $3 in Extended fees + approximately $0.096 in reported
joints = $3.123 before rounding. All other components are unchanged.

The complete original buck's components cost $8.967 per 10 boards versus
$8.994 for the optimized buck. These include the retained $0.697 bypass
capacitors and $0.351 catch diodes. Buck-only components plus loading fees are
$11.967 original versus $14.994 optimized, before joint charges.

The source compiles standalone (7 parts) and in the controller (28 parts).
Exported netlists verify every buck pin and preserve all non-buck components
and connectivity. ERC reports seven library-link warnings and no errors.
The PCB still needs placement/routing updates and thermal/ripple validation.

These are tool estimates, not checkout quotes. PCB fabrication, shipping,
taxes and order-specific assembly charges are excluded. Schrune reports zero
joints for older imported parts with missing footprint metadata, so the joint
line is incomplete in both versions. Component prices use exactly 10 boards'
quantities; checkout minimums or attrition requirements may change them.

Raw reports: `verification/xl1509/original-jlc-10-refreshed.txt`,
`verification/xl1509/new-jlc-10.txt` (earlier XL1509), and
`verification/xl1509/optimized-jlc-10.txt`.
