"""Correct the installed D68W land patterns to datasheet B-22-A-1355 p2."""
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]

def normalize(f):
    f.SetOrientationDegrees(0)
    f.SetPosition(p.VECTOR2I(0, 0))
    f.SetAttributes(p.FP_SMD)
    for pad in f.Pads():
        cathode = pad.GetNumber() == '1'
        pad.SetPosition(p.VECTOR2I(p.FromMM(-0.9 if cathode else 1.275), 0))
        pad.SetSize(p.VECTOR2I(p.FromMM(2.05 if cathode else 1.3), p.FromMM(2.3)))
    graphics = list(f.GraphicalItems())
    for item in graphics:
        if item.GetLayer() in [p.F_CrtYd, p.F_SilkS]:
            f.Remove(item)
    def line(a, z, layer, width):
        shape = p.PCB_SHAPE(f)
        shape.SetShape(p.SHAPE_T_SEGMENT)
        shape.SetStart(p.VECTOR2I(p.FromMM(a[0]), p.FromMM(a[1])))
        shape.SetEnd(p.VECTOR2I(p.FromMM(z[0]), p.FromMM(z[1])))
        shape.SetLayer(layer)
        shape.SetWidth(p.FromMM(width))
        f.Add(shape)
    for a, z in [((-2.2,-1.65),(2.2,-1.65)),((2.2,-1.65),(2.2,1.65)),((2.2,1.65),(-2.2,1.65)),((-2.2,1.65),(-2.2,-1.65))]:
        line(a, z, p.F_CrtYd, 0.05)
    for y in [-1.5,1.5]:
        line((-1.85,y),(1.85,y),p.F_SilkS,0.12)
    line((-2.1,-1.5),(-2.1,1.5),p.F_SilkS,0.12)
    return graphics

if __name__ == '__main__':
    retained = []
    for directory in (ROOT / 'parts').glob('HL_AS_2835D68W*'):
        f = p.FootprintLoad(str(directory), directory.name)
        retained.extend(normalize(f))
        f.SetFPIDAsString(directory.name)
        p.FootprintSave(str(directory), f)
        retained.append(f)
        print('Normalized', directory.name)
