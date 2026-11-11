"""Rebuild only LED copper, using KiCad's board API and the original as baseline."""
import json
from pathlib import Path
import pcbnew as p
from normalize_leds import normalize

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '2x2x3/build/2x2x3-LED-Panel.kicad_pcb'
GEN = ROOT / '2x2x3/verification/generated.kicad_pcb'
if not GEN.exists():
    GEN.write_bytes(OUT.read_bytes())
b = p.LoadBoard(str(ROOT / '2x2x4/build/2x2x4-LED-Panel.kicad_pcb'))
g = p.LoadBoard(str(GEN))
for f in g.GetFootprints():
    if f.GetReference() == 'REF**':
        name = next(iter(f.Pads())).GetNetname()
        f.SetReference({'V+': 'TP1', 'GND': 'TP2', 'pwm_cool': 'TP3', 'pwm_warm': 'TP4'}[name])
gf = {f.GetReference(): f for f in g.GetFootprints()}

def xy(v):
    return (round(p.ToMM(v.x), 6), round(p.ToMM(v.y), 6))

def vec(point):
    return p.VECTOR2I(p.FromMM(point[0]), p.FromMM(point[1]))

def net(name):
    found = b.FindNet(name)
    if found is None:
        found = p.NETINFO_ITEM(b, name)
        b.Add(found)
    return found

original = {f.GetReference(): [*xy(f.GetPosition()), f.GetOrientationDegrees(), f.GetLayer()] for f in b.GetFootprints()}
original_footprints = list(b.GetFootprints())
for f in original_footprints:
    ref = f.GetReference()
    if ref.startswith('LED'):
        b.Remove(f)
        continue
    nf = gf[ref]
    f.SetValue(nf.GetValue())
    if ref.startswith('TP'):
        f.SetValue('TestPoint')
    if ref in ['R1', 'R2', 'R3', 'R4', 'R13', 'R14', 'R15', 'R16']:
        f.SetFPID(nf.GetFPID())
    f.SetPath(nf.GetPath())
    for field in nf.GetFields():
        if field.GetName() not in ['Reference', 'Value']:
            f.SetField(field.GetName(), field.GetText())
    desired = {pad.GetNumber(): pad.GetNetname() for pad in nf.Pads()}
    for pad in f.Pads():
        pad.SetNet(net(desired[pad.GetNumber()]))

positions = {
    'LED2': (168.5, 126, 0), 'LED3': (143.25, 126, 0), 'LED4': (120.25, 126, 0),
    'LED6': (154.75, 104, 0), 'LED7': (131.75, 104, 0), 'LED8': (108.75, 104, 0),
    'LED10': (108.75, 126, 180), 'LED11': (131.75, 126, 180), 'LED12': (154.75, 126, 180),
    'LED14': (120.25, 104, 180), 'LED15': (143.25, 104, 180), 'LED16': (166.25, 104, 180),
}
added_footprints = []
removed_graphics = []
for ref, (x, y, rot) in positions.items():
    f = p.FOOTPRINT(gf[ref])
    removed_graphics.extend(normalize(f))
    b.Add(f)
    added_footprints.append(f)
    f.SetPosition(vec((x, y)))
    f.SetOrientationDegrees(rot)
    for pad in f.Pads():
        pad.SetNet(net(pad.GetNetname()))
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)

kept = []
removed = []
original_tracks = list(b.GetTracks())
for t in original_tracks:
    name = t.GetNetname()
    if 'led' not in name.lower():
        kept.append(t.m_Uuid.AsString())
        continue
    a, z = xy(t.GetStart()), xy(t.GetEnd())
    keep = False
    if name.endswith('LED_RETURN') and t.GetLayer() == p.F_Cu:
        keep = not isinstance(t, p.PCB_VIA) and min(a[1], z[1]) >= 108 and max(a[1], z[1]) <= 121
    if name.endswith('LED_TOP'):
        if 'cool_a' in name:
            keep = max(a[0], z[0]) <= 164.6283
        elif 'cool_b' in name:
            keep = min(a[1], z[1]) >= 106.9 and not (a[1] == z[1] == 106.9 and abs(a[0] - z[0]) < 1)
        elif 'warm_a' in name:
            keep = min(a[0], z[0]) >= 115.6
        elif 'warm_b' in name:
            keep = min(a[1], z[1]) >= 106.6
    if keep:
        kept.append(t.m_Uuid.AsString())
    else:
        removed.append(t.m_Uuid.AsString())
        b.Remove(t)

def route(name, points, layer=p.F_Cu, width=0.5):
    for a, z in zip(points, points[1:]):
        if a == z:
            continue
        t = p.PCB_TRACK(b)
        t.SetStart(vec(a))
        t.SetEnd(vec(z))
        t.SetWidth(p.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(net(name))
        b.Add(t)

def via(name, point):
    v = p.PCB_VIA(b)
    v.SetPosition(vec(point))
    v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetWidth(p.FromMM(0.6))
    v.SetDrill(p.FromMM(0.3))
    v.SetNet(net(name))
    b.Add(v)

fp = {f.GetReference(): f for f in b.GetFootprints()}
def pad(ref, number):
    return xy(next(x for x in fp[ref].Pads() if x.GetNumber() == str(number)).GetPosition())

# Alternate warm/cool LEDs. Series traces use the existing two edge corridors.
for refs, corridor in [(['LED2', 'LED3', 'LED4'], 124.4), (['LED6', 'LED7', 'LED8'], 105.8), (['LED10', 'LED11', 'LED12'], 128), (['LED14', 'LED15', 'LED16'], 102)]:
    for left, right in zip(refs, refs[1:]):
        a, z = pad(left, 1), pad(right, 2)
        direction = 1 if z[0] > a[0] else -1
        rise = abs(corridor - a[1])
        name = next(x.GetNetname() for x in fp[left].Pads() if x.GetNumber() == '1')
        route(name, [a, (a[0] + direction * rise, corridor), (z[0] - direction * rise, corridor), z])

route('cool_a_channel_LED_TOP', [(164.62793, 123.411203), (167.811203, 123.411203), (169.15, 124.75), pad('LED2', 2)])
route('cool_b_channel_LED_TOP', [(157.52826, 106.9), (157.52826, 105.68826), pad('LED6', 2)])
route('warm_a_channel_LED_TOP', [(118.4, 123.15), (116.95, 121.7), (115.6, 121.7), (114.3, 123), (108.6, 123), (107.66, 123.94), pad('LED10', 2)])
via('warm_b_channel_LED_TOP', (110.4, 106.9))
via('warm_b_channel_LED_TOP', pad('LED14', 2))
route('warm_b_channel_LED_TOP', [(110.4, 106.9), (116.26, 106.9), pad('LED14', 2)], p.B_Cu)

# Return connections follow the original back-layer approach and avoid control copper.
returns = [
    ('cool_a', 'LED4', [(141.17, 120), (140.048, 118.878), (126.772, 118.878), (119.16, 126)]),
    ('cool_b', 'LED8', [(141.57, 110.75), (126.5, 110.75), (126.5, 104.5), (124.5, 102.5), (108.16, 102.5), (107.6, 103.06), (107.6, 104)]),
    ('warm_a', 'LED12', [(134, 120.2), (134, 120.25), (139.75, 126), (155.84, 126)]),
    ('warm_b', 'LED16', [(133.83, 108.9), (133.85, 108.9), (138.75, 104), (167.34, 104)]),
]
for channel, ref, points in returns:
    name = channel + '_channel_LED_RETURN'
    points[-1] = pad(ref, 1)
    for point in [points[0], points[-1]]:
        via(name, point)
    route(name, points, p.B_Cu)

# Preserve the original project design rules and all outline geometry.
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(OUT), b)
check = p.LoadBoard(str(OUT))
after = {f.GetReference(): [*xy(f.GetPosition()), f.GetOrientationDegrees(), f.GetLayer()] for f in check.GetFootprints()}
fixed = {ref: pos for ref, pos in original.items() if not ref.startswith('LED')}
assert all(after[ref] == pos for ref, pos in fixed.items())
assert len(check.GetFootprints()) == 58
(ROOT / '2x2x3/verification/placement-audit.json').write_text(json.dumps({'fixed_placements_unchanged': fixed, 'led_placements': positions, 'retained_track_uuids': kept, 'removed_led_track_uuids': removed}, indent=2))
print('Saved', OUT, 'with', len(check.GetTracks()), 'tracks/vias; all 46 non-LED placements unchanged.')
