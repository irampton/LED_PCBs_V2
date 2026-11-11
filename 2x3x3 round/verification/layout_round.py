"""Create the round board using native KiCad objects and the proven channel layout."""
import json
import math
import shutil
import xml.etree.ElementTree as E
from pathlib import Path
import pcbnew as p
from normalize_leds import normalize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/2x3x3-Round.kicad_pcb'
BASE = ROOT.parent / '2x2x3/build/2x2x3-LED-Panel.kicad_pcb'
GEN = ROOT / 'verification/generated.kicad_pcb'
if not GEN.exists():
    shutil.copy2(OUT, GEN)
b = p.LoadBoard(str(GEN))
owned = []
for original in list(b.GetFootprints()):
    raw = original.Duplicate(False)
    copied = p.Cast_to_FOOTPRINT(raw)
    b.Remove(original)
    b.Add(copied)
    owned.extend([raw, copied, original])
old = p.LoadBoard(str(BASE))
xml = E.parse(ROOT / 'verification/netlist.xml')
comps = {c.attrib['ref']: c for c in xml.findall('.//components/comp')}
expected = {}
for n in xml.findall('.//nets/net'):
    for node in n.findall('node'):
        expected.setdefault(node.attrib['ref'], {})[node.attrib['pin']] = n.attrib['name']

def vec(xy):
    return p.VECTOR2I(round(xy[0] * 1000000), round(xy[1] * 1000000))

def xy(v):
    return (p.ToMM(v.x), p.ToMM(v.y))

def net(name):
    return b.FindNet(name)

def route(name, points, layer=p.B_Cu, width=0.5):
    for a, z in zip(points, points[1:]):
        if math.dist(a, z) < 0.00001:
            continue
        t = p.PCB_TRACK(b)
        t.SetStart(vec(a))
        t.SetEnd(vec(z))
        t.SetWidth(p.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(net(name))
        b.Add(t)

def via(name, point, diameter=0.65):
    v = p.PCB_VIA(b)
    v.SetPosition(vec(point))
    v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetWidth(p.FromMM(diameter))
    v.SetDrill(p.FromMM(0.3))
    v.SetNet(net(name))
    b.Add(v)

def signature(f):
    return {pad.GetNumber(): pad.GetNetname() for pad in f.Pads()}

# Schrune leaves imported LED/test-point references and all paths empty in PCB output.
for f in b.GetFootprints():
    if f.GetReference() == 'REF**':
        matches = [ref for ref, pins in expected.items() if pins == signature(f)]
        assert len(matches) == 1, matches
        f.SetReference(matches[0])
    comp = comps[f.GetReference()]
    f.SetPath(p.KIID_PATH(comp.find('sheetpath').attrib['tstamps'] + comp.findtext('tstamps')))

new = {f.GetReference(): f for f in b.GetFootprints()}
of = {f.GetReference(): f for f in old.GetFootprints()}
for item in list(b.GetDrawings()) + list(b.GetTracks()) + list(b.Zones()):
    b.Remove(item)
    owned.append(item)
b.SetCopperLayerCount(2)

channels = ['cool_a', 'warm_a', 'cool_b', 'warm_b', 'cool_c', 'warm_c']
angles = [-90, -30, 30, 90, 150, 210]
template = {'U2': 'driver', 'L1': 'inductor', 'D1': 'diode', 'C4': 'cap1', 'C6': 'cap2', 'R1': 'sense1', 'R13': 'sense2', 'R9': 'series', 'R5': 'pull', 'R17': 'bleed'}
all_leds = []
channel_ports = {}
retained = []

for ch, angle in zip(channels, angles):
    index = ['cool_a', 'cool_b', 'cool_c', 'warm_a', 'warm_b', 'warm_c'].index(ch)
    i = index + 1
    caps = [ref for ref, c in comps.items() if ref.startswith('C') and c.find('sheetpath').attrib['names'] == '/' + ch + '.channel/']
    roles = {'driver': 'U' + str(i), 'inductor': 'L' + str(i), 'diode': 'D' + str(i), 'cap1': caps[0], 'cap2': caps[1], 'sense1': 'R' + str(index * 2 + 1), 'sense2': 'R' + str(index * 2 + 2), 'series': 'R' + str(25 + index), 'pull': 'R' + str(13 + index), 'bleed': 'R' + str(19 + index)}
    theta = math.radians(angle + 90)
    a = math.radians(angle)
    target = (100 + 30 * math.cos(a), 100 + 30 * math.sin(a))

    def transform(point):
        dx, dy = point[0] - 151.5, -(point[1] - 120)
        return (target[0] + dx * math.cos(theta) - dy * math.sin(theta), target[1] + dx * math.sin(theta) + dy * math.cos(theta))

    for oldref, role in template.items():
        ref = roles[role]
        source = new[ref]
        f = p.Cast_to_FOOTPRINT(of[oldref].Duplicate(False))
        f.SetReference(ref)
        f.SetPath(source.GetPath())
        f.SetValue(source.GetValue())
        f.SetFPID(source.GetFPID())
        f.Flip(vec((151.5, 120)), True)
        f.Rotate(vec((151.5, 120)), p.EDA_ANGLE(-(angle + 90), p.DEGREES_T))
        f.Move(vec((target[0] - 151.5, target[1] - 120)))
        b.Remove(source)
        b.Add(f)
        for pad in f.Pads():
            pad.SetNet(net(expected[ref][pad.GetNumber()]))
        f.Reference().SetVisible(False)
        f.Value().SetVisible(False)
        new[ref] = f
        retained.append(source)

    # Reuse only compact, proven local switching, sense, and DIM copper.
    for track in old.GetTracks():
        name = track.GetNetname()
        start, end = xy(track.GetStart()), xy(track.GetEnd())
        if isinstance(track, p.PCB_VIA):
            continue
        keep = name in ['cool_a_channel_driver_SW', 'cool_a_channel_pwm_2_2_1']
        keep = keep or (name == 'cool_a_channel_LED_TOP' and max(start[0], end[0]) <= 164.7)
        keep = keep or (name == 'cool_a_channel_LED_RETURN' and track.GetLayer() == p.F_Cu and min(start[0], end[0]) >= 138.8)
        if keep:
            route(name.replace('cool_a', ch), [transform(start), transform(end)], p.B_Cu, p.ToMM(track.GetWidth()))

    # Short VIN stubs keep ordinary drilled vias outside component solder lands.
    for x in [162.4, 164.62793]:
        via('V+', transform((x, 120)))
    for role, endpoint in [('cap1', (162.4, 120)), ('sense1', (162.4, 120)), ('cap2', (164.62793, 120)), ('sense2', (164.62793, 120)), ('bleed', (138.9, 115.3))]:
        pad = next(pad for pad in new[roles[role]].Pads() if pad.GetNetname() == 'V+')
        route('V+', [xy(pad.GetPosition()), transform(endpoint)], p.B_Cu, 0.5)
    via('V+', transform((138.9, 115.3)))
    route('V+', [transform((159.2, 118.5)), transform((161.2, 118.5)), transform((162.37793, 118.788797))], p.B_Cu, 0.5)
    # Local input capacitor GND and driver return will be connected by the back pour.
    series = next(pad for pad in new[roles['series']].Pads() if pad.GetNumber() == '1')
    pwm = 'pwm_' + ch.split('_')[0]
    pwm_point = transform((152.55, 118.92))
    route(pwm, [xy(series.GetPosition()), pwm_point], p.B_Cu, 0.254)
    via(pwm, pwm_point, 0.6)
    top_port, return_port = transform((164.62793, 125)), transform((141.67, 123.2))
    route(ch + '_channel_LED_TOP', [transform((164.62793, 123.411203)), top_port], p.B_Cu, 0.5)
    route(ch + '_channel_LED_RETURN', [transform((141.67, 120)), return_port], p.B_Cu, 0.5)
    channel_ports[ch] = {'pwm': pwm_point, 'top': top_port, 'return': return_port}

    leds = [f for f in list(b.GetFootprints()) if f.GetReference().startswith('LED') and any(pad.GetNetname().startswith(ch + '_') for pad in f.Pads())]
    leds.sort(key=lambda f: 0 if signature(f).get('2') == ch + '_channel_LED_TOP' else 2 if signature(f).get('1') == ch + '_channel_LED_RETURN' else 1)
    for f, radius in zip(leds, [12, 24, 36]):
        retained.extend(normalize(f))
        # Anode faces inward, cathode outward along the radial series chain.
        f.SetOrientationDegrees(180 - angle)
        f.SetPosition(vec((100 + radius * math.cos(a), 100 + radius * math.sin(a))))
        f.Reference().SetVisible(False)
        f.Value().SetVisible(False)
        f.SetLocked(True)
        all_leds.append({'ref': f.GetReference(), 'channel': ch, 'radius': radius, 'angle': angle})
    def padpos(f, number):
        return xy(next(pad for pad in f.Pads() if pad.GetNumber() == str(number)).GetPosition())
    for first, second in zip(leds, leds[1:]):
        name = signature(first)['1']
        route(name, [padpos(first, 1), padpos(second, 2)], p.F_Cu, 0.6)

# Perfect circular outline: 84 mm diameter; connector sits within its left edge.
circle = p.PCB_SHAPE(b)
circle.SetShape(p.SHAPE_T_CIRCLE)
circle.SetCenter(vec((100, 100)))
circle.SetEnd(vec((142, 100)))
circle.SetLayer(p.Edge_Cuts)
circle.SetWidth(p.FromMM(0.05))
b.Add(circle)
h = new['H1']
h.SetPosition(vec((62, 96)))
h.SetOrientationDegrees(90)
h.Reference().SetVisible(False)
h.Value().SetVisible(False)
h.SetLocked(True)
h.SetAttributes(p.FP_THROUGH_HOLE)

for f in b.GetFootprints():
    if f.GetReference().startswith('TP'):
        if f.GetLayer() != p.B_Cu:
            f.Flip(f.GetPosition(), False)
        name = next(iter(f.Pads())).GetNetname()
        f.SetPosition(vec({'V+': (96, 98), 'GND': (104, 98), 'pwm_cool': (100, 100), 'pwm_warm': (102, 90)}[name]))
        f.Reference().SetVisible(False)
        f.Value().SetVisible(False)
        if name == 'V+':
            via(name, xy(next(iter(f.Pads())).GetPosition()))

for f in b.GetFootprints():
    f.SetValue(comps[f.GetReference()].findtext('value'))
    for item in list(f.GraphicalItems()):
        if item.GetLayer() in [p.F_SilkS, p.B_SilkS] and item.GetShape() == p.SHAPE_T_CIRCLE:
            f.Remove(item)

p.SaveBoard(str(OUT), b)
(ROOT / 'verification/placement.json').write_text(json.dumps({'diameter_mm': 84, 'leds': all_leds, 'ports': channel_ports}, indent=2))
print('Saved placement and local copper:', OUT)
