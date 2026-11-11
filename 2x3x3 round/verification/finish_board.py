from pathlib import Path
import json
import math
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/2x3x3-Round.kicad_pcb'
b = p.LoadBoard(str(OUT))
retained = []
for item in list(b.GetDrawings()):
    if isinstance(item, p.PCB_TEXT):
        b.Remove(item)
        retained.append(item)
for old in list(b.GetFootprints()):
    if not old.GetReference().startswith('U'):
        continue
    f = p.FootprintLoad(str(ROOT / 'build/Schrune.pretty'), 'PT4115')
    b.Add(f)
    f.SetFPID(old.GetFPID())
    f.SetReference(old.GetReference())
    f.SetValue(old.GetValue())
    f.SetPath(old.GetPath())
    f.Flip(f.GetPosition(), True)
    f.SetOrientationDegrees(old.GetOrientationDegrees())
    f.SetPosition(old.GetPosition())
    for pad in f.Pads():
        same = next(pad2 for pad2 in old.Pads() if pad2.GetNumber() == pad.GetNumber())
        pad.SetNet(b.FindNet(same.GetNetname()))
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)
    b.Remove(old)
    retained.extend([old, f])

# The imported header STEP has an unrelated assembly origin. Use a nominal,
# centred visual model; pad geometry remains the manufacturer's imported pattern.
model_dir = ROOT / 'parts/PZ2_54_2X5P_H25'
visual = ['#VRML V2.0 utf8', 'Group { children [']
visual.append('Transform { translation 0 0 0.4921259843 children [ Shape { appearance Appearance { material Material { diffuseColor 0.07 0.07 0.07 } } geometry Box { size 5.0 1.9685039370 0.9842519685 } } ] }')
for x in [-5.08, -2.54, 0, 2.54, 5.08]:
    for y in [-1.27, 1.27]:
        visual.append('Transform { translation %s %s 0.7874015748 children [ Shape { appearance Appearance { material Material { diffuseColor 0.75 0.68 0.35 specularColor 0.8 0.8 0.7 shininess 0.6 } } geometry Box { size 0.2519685039 0.2519685039 4.3307086614 } } ] }' % (x / 2.54, y / 2.54))
visual.append('] }')
(model_dir / 'header-visual.wrl').write_text('\n'.join(visual))
header = next(f for f in b.GetFootprints() if f.GetReference() == 'H1')
header.Models()[0].m_Filename = '${KIPRJMOD}/../parts/PZ2_54_2X5P_H25/header-visual.wrl'
lib_header = p.FOOTPRINT(header)
lib_header.SetOrientationDegrees(0)
lib_header.SetPosition(p.VECTOR2I(0, 0))
lib_header.SetReference('REF**')
lib_header.SetValue('PZ2_54_2X5P_H25')
for pad in lib_header.Pads():
    pad.SetNetCode(0)
p.FootprintSave(str(ROOT / 'build/Schrune.pretty'), lib_header)

def text(value, point, size=0.8, layer=p.F_SilkS):
    t = p.PCB_TEXT(b)
    t.SetText(value)
    t.SetPosition(p.VECTOR2I(p.FromMM(point[0]), p.FromMM(point[1])))
    t.SetTextSize(p.VECTOR2I(p.FromMM(size), p.FromMM(size)))
    t.SetTextThickness(p.FromMM(0.12))
    t.SetLayer(layer)
    b.Add(t)

placement = json.loads((ROOT / 'verification/placement.json').read_text())
for item in placement['leds']:
    a = math.radians(item['angle'])
    radius = item['radius']
    point = (100 + radius * math.cos(a) - 3.4 * math.sin(a), 100 + radius * math.sin(a) + 3.4 * math.cos(a))
    text('W' if item['channel'].startswith('warm') else 'C', point)
text('2x3x3', (100, 97), 1)
text('24V', (67, 90), 0.85)
text('5:C 6:W', (70, 94), 0.8)
text('1', (65.5, 101.08), 0.8)
text('166.7mA / CH', (100, 109), 0.8)
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(OUT), b)
print('Saved final board', OUT)
