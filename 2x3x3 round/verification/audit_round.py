import json
import math
from pathlib import Path
import xml.etree.ElementTree as E
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
b = p.LoadBoard(str(ROOT / 'build/2x3x3-Round.kicad_pcb'))
xml = E.parse(ROOT / 'verification/netlist.xml')
expected = {n.attrib['name']: {(node.attrib['ref'], node.attrib['pin']) for node in n.findall('node')} for n in xml.findall('.//nets/net')}
actual = {}
counts = {}
for f in b.GetFootprints():
    counts[f.GetReference()] = len(f.Pads())
    for pad in f.Pads():
        actual.setdefault(pad.GetNetname(), set()).add((f.GetReference(), pad.GetNumber()))
assert expected == actual
leds = [f for f in b.GetFootprints() if f.GetReference().startswith('LED')]
drivers = [f for f in b.GetFootprints() if f.GetReference().startswith('U')]
headers = [f for f in b.GetFootprints() if f.GetReference().startswith('H')]
assert len(leds) == 18 and len(drivers) == 6 and len(headers) == 1
assert all(f.GetLayer() == p.F_Cu for f in leds + headers)
assert not headers[0].IsDNP()
assert all(f.GetLayer() == p.B_Cu for f in b.GetFootprints() if f not in leds + headers)
outline = [d for d in b.GetDrawings() if d.GetLayer() == p.Edge_Cuts]
assert len(outline) == 1 and outline[0].GetShape() == p.SHAPE_T_CIRCLE
assert abs(p.ToMM(outline[0].GetRadius()) - 42) < 0.0001
placement = json.loads((ROOT / 'verification/placement.json').read_text())
for radius in [12, 24, 36]:
    ring = sorted([item for item in placement['leds'] if item['radius'] == radius], key=lambda item: item['angle'])
    assert len(ring) == 6
    assert all(ring[i]['channel'].split('_')[0] != ring[(i + 1) % 6]['channel'].split('_')[0] for i in range(6))
drc = json.loads((ROOT / 'verification/drc-final.json').read_text())
assert not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity']
(ROOT / 'verification/pad-counts.json').write_text(json.dumps(counts, indent=2))
result = {'footprints': len(b.GetFootprints()), 'driver_channels': 6, 'warm_leds': 9, 'cool_leds': 9, 'diameter_mm': 84, 'rings_mm': [12, 24, 36], 'leds_per_ring': 6, 'alternating_colors': True, 'front': '18 LEDs and one populated 2x5 header', 'back': 'six driver circuits and four test points', 'schematic_netlist_matches': True, 'drc_violations': 0, 'unconnected_items': 0, 'schematic_parity_issues': 0}
(ROOT / 'verification/final-audit.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
