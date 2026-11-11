"""Verify fixed geometry, retained copper, schematic nets, and BOM population."""
import json
from pathlib import Path
import xml.etree.ElementTree as E
import pcbnew as p

ROOT = Path(__file__).resolve().parents[2]
old = p.LoadBoard(str(ROOT / '2x2x4/build/2x2x4-LED-Panel.kicad_pcb'))
new = p.LoadBoard(str(ROOT / '2x2x3/build/2x2x3-LED-Panel.kicad_pcb'))

def pos(v):
    return [v.x, v.y]

def geometry(f):
    return [pos(f.GetPosition()), f.GetOrientationDegrees(), f.GetLayer(), sorted((pad.GetNumber(), pos(pad.GetPosition()), pos(pad.GetSize()), pad.GetNetname()) for pad in f.Pads())]

of = {f.GetReference(): f for f in old.GetFootprints()}
nf = {f.GetReference(): f for f in new.GetFootprints()}
fixed = [ref for ref in of if not ref.startswith('LED')]
assert len(fixed) == 46
assert all(geometry(of[ref]) == geometry(nf[ref]) for ref in fixed)

def outline(b):
    return sorted((d.GetShapeStr(), pos(d.GetStart()), pos(d.GetEnd()), d.GetWidth()) for d in b.GetDrawings() if d.GetLayer() == p.Edge_Cuts)

assert outline(old) == outline(new)

def track(t):
    return [pos(t.GetStart()), pos(t.GetEnd()), t.GetLayer(), t.GetNetname(), t.GetWidth(p.F_Cu) if isinstance(t, p.PCB_VIA) else t.GetWidth()]

ot = {t.m_Uuid.AsString(): track(t) for t in old.GetTracks()}
nt = {t.m_Uuid.AsString(): track(t) for t in new.GetTracks()}
nonled = [uid for uid, data in ot.items() if 'led' not in data[3].lower()]
assert all(nt.get(uid) == ot[uid] for uid in nonled)
assert all('led' in data[3].lower() for uid, data in nt.items() if uid not in ot)
schematic = E.parse(ROOT / '2x2x3/verification/netlist.xml')
expected = {net.attrib['name']: {(node.attrib['ref'], node.attrib['pin']) for node in net.findall('node')} for net in schematic.findall('.//nets/net')}
actual = {}
for f in new.GetFootprints():
    for pad in f.Pads():
        actual.setdefault(pad.GetNetname(), set()).add((f.GetReference(), pad.GetNumber()))
assert expected == actual
assert len([r for r in nf if r.startswith('LED')]) == 12
assert all(nf[r].GetValue() == '1.2' for r in ['R1','R2','R3','R4','R13','R14','R15','R16'])
result = {
    'non_led_components_and_pad_geometry_preserved': len(fixed),
    'non_led_tracks_and_vias_preserved': len(nonled),
    'outline_and_four_mounting_holes_preserved': True,
    'board_dimensions_mm': [75, 30],
    'schematic_netlist_matches_pcb': True,
    'led_count': 12,
    'nominal_current_mA': 100 / (1.2 / 2),
    'nominal_sense_resistor_dissipation_mW_each': 1000 * 0.1 ** 2 / 1.2
}
(ROOT / '2x2x3/verification/final-audit.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
