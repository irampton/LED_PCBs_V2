"""Clean imported silkscreen, add useful markings, and save fabrication notes."""
import json
import math
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/2x4x3-Round-64mm.kicad_pcb'
b = p.LoadBoard(str(OUT))
owned = []
for f in b.GetFootprints():
    for item in list(f.GraphicalItems()):
        if item.GetLayer() in [p.F_SilkS, p.B_SilkS]:
            f.Remove(item)
            owned.append(item)
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)

def text(value, pos, size=0.8, layer=p.F_SilkS):
    t = p.PCB_TEXT(b)
    t.SetText(value)
    t.SetPosition(p.VECTOR2I(p.FromMM(pos[0]), p.FromMM(pos[1])))
    t.SetTextSize(p.VECTOR2I(p.FromMM(size), p.FromMM(size)))
    t.SetTextThickness(p.FromMM(0.12))
    t.SetLayer(layer)
    t.SetMirrored(layer == p.B_SilkS)
    b.Add(t)

placement = json.loads((ROOT / 'verification/placement.json').read_text())
for item in placement['leds']:
    a = math.radians(item['angle'])
    r = item['radius']
    t = 2.6
    text('W' if item['channel'].startswith('warm') else 'C', (100 + r * math.cos(a) - t * math.sin(a), 100 + r * math.sin(a) + t * math.cos(a)))
text('2x4x3', (100, 95.6))
text('SUM PWM <= 100%', (100, 104), 0.8)
text('24V', (75.5, 92.4))
text('INSULATED TIM REQUIRED', (100, 91), 0.8, p.B_SilkS)

# Mark all component-pad vias for filled and copper-capped fabrication.
filled = []
for via in b.GetTracks():
    if not isinstance(via, p.PCB_VIA):
        continue
    for f in b.GetFootprints():
        if f.GetReference().startswith('MH'):
            continue
        for pad in f.Pads():
            if pad.GetNetname() == via.GetNetname() and pad.HitTest(via.GetPosition()):
                filled.append({'x_mm': p.ToMM(via.GetPosition().x), 'y_mm': p.ToMM(via.GetPosition().y), 'drill_mm': p.ToMM(via.GetDrillValue()), 'net': via.GetNetname(), 'ref': f.GetReference(), 'pad': pad.GetNumber()})
                break
text('FAB: VIA-IN-PAD LOCATIONS REQUIRE FILLED + COPPER-CAPPED PROCESS; SEE verification/filled-vias.json', (100, 138), 1, p.Dwgs_User)
text('THERMAL: BACK CONTACTS ARE LIVE NETS. ELECTRICALLY INSULATING TIM AND COMPONENT-CLEARANCE SPREADER REQUIRED.', (100, 141), 1, p.Dwgs_User)
(ROOT / 'verification/filled-vias.json').write_text(json.dumps(filled, indent=2))
p.SaveBoard(str(OUT), b)
print('Saved finished board and', len(filled), 'filled-via locations')
