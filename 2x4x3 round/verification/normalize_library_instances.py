"""Normalize inductor instances against the saved project footprint library."""
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/2x4x3-Round-64mm.kicad_pcb'
b = p.LoadBoard(str(OUT))
owned = []
for source in list(b.GetFootprints()):
    if not source.GetReference().startswith('L') or source.GetReference().startswith('LED'):
        continue
    f = p.FootprintLoad(str(ROOT / 'build/Schrune.pretty'), 'CY54_68UH')
    b.Add(f)
    f.SetFPID(source.GetFPID())
    f.SetReference(source.GetReference())
    f.SetValue(source.GetValue())
    f.SetPath(source.GetPath())
    f.Flip(f.GetPosition(), True)
    f.SetOrientationDegrees(source.GetOrientationDegrees())
    f.SetPosition(source.GetPosition())
    for pad in f.Pads():
        other = next(pad2 for pad2 in source.Pads() if pad2.GetNumber() == pad.GetNumber())
        pad.SetNet(b.FindNet(other.GetNetname()))
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)
    b.Remove(source)
    owned.extend([source, f])
p.SaveBoard(str(OUT), b)
print('Normalized eight inductor instances')
