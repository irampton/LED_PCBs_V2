"""Persist intentional footprint corrections in the project's local library."""
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
b = p.LoadBoard(str(ROOT / 'build/2x4x3-Round-64mm.kicad_pcb'))
seen = set()
retained = []
for source in b.GetFootprints():
    name = str(source.GetFPID().GetLibItemName())
    if name in seen:
        continue
    seen.add(name)
    f = p.FOOTPRINT(source)
    retained.append(f)
    if f.GetLayer() == p.B_Cu:
        f.Flip(f.GetPosition(), True)
    f.SetOrientationDegrees(0)
    f.SetPosition(p.VECTOR2I(0, 0))
    f.SetReference('REF**')
    f.SetValue(name)
    for pad in f.Pads():
        pad.SetNetCode(0)
    p.FootprintSave(str(ROOT / 'build/Schrune.pretty'), f)
print('Saved', len(seen), 'local footprint definitions')

