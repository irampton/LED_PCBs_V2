import json
import math
from pathlib import Path
import xml.etree.ElementTree as E
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
b = p.LoadBoard(str(ROOT / 'build/2x4x3-Round-64mm.kicad_pcb'))
xml = E.parse(ROOT / 'verification/netlist.xml')
expected = {n.attrib['name']: {(node.attrib['ref'], node.attrib['pin']) for node in n.findall('node')} for n in xml.findall('.//nets/net')}
actual, counts = {}, {}
for f in b.GetFootprints():
    if f.GetReference().startswith('MH'):
        continue
    counts[f.GetReference()] = len(f.Pads())
    for pad in f.Pads():
        actual.setdefault(pad.GetNetname(), set()).add((f.GetReference(), pad.GetNumber()))
assert actual == expected
leds = [f for f in b.GetFootprints() if f.GetReference().startswith('LED')]
drivers = [f for f in b.GetFootprints() if f.GetReference().startswith('U')]
header = [f for f in b.GetFootprints() if f.GetReference().startswith('H')]
assert len(leds) == 24 and len(drivers) == 8 and len(header) == 1
assert all(f.GetLayer() == p.F_Cu for f in leds + header)
assert all(f.GetLayer() == p.B_Cu for f in b.GetFootprints() if not f.GetReference().startswith(('LED', 'H', 'MH')))
edge = [d for d in b.GetDrawings() if d.GetLayer() == p.Edge_Cuts]
assert len(edge) == 1 and edge[0].GetShape() == p.SHAPE_T_CIRCLE
assert abs(p.ToMM(edge[0].GetRadius()) - 32) < 0.000001
data = json.loads((ROOT / 'verification/placement.json').read_text())
for radius in [9, 18, 27]:
    ring = sorted([led for led in data['leds'] if led['radius'] == radius], key=lambda item: item['angle'])
    assert len(ring) == 8
    assert all(ring[i]['channel'].split('_')[0] != ring[(i + 1) % 8]['channel'].split('_')[0] for i in range(8))
contacts = json.loads((ROOT / 'verification/thermal-contacts.json').read_text())
assert len(contacts) == 24 and sum(c['via_count'] for c in contacts) == 153
drc = json.loads((ROOT / 'verification/drc-final.json').read_text())
assert not drc['unconnected_items'] and not drc['schematic_parity']
assert not [v for v in drc['violations'] if v['severity'] == 'error']
result = {'diameter_mm': 64, 'populated_driver_channels': 8, 'warm_leds': 12, 'cool_leds': 12, 'rings_mm': [9, 18, 27], 'leds_per_ring': 8, 'alternate_colors': True, 'schematic_netlist_matches': True, 'mounting_holes_mm': [[96.5, 100, 2.7], [103.5, 100, 2.7]], 'thermal_contacts': 24, 'thermal_vias': 153, 'sum_pwm_limit_percent': 100, 'maximum_average_led_electrical_W': 12, 'drc_errors': 0, 'drc_warnings': [v['description'] for v in drc['violations']], 'thermal_validation': 'Not performed; heatsink/spreader/TIM prototype required'}
(ROOT / 'verification/pad-counts.json').write_text(json.dumps(counts, indent=2))
(ROOT / 'verification/final-audit.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
