"""Eight compact PT4115 cells, 24 alternating LEDs, native KiCad layout."""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as E
import pcbnew as p
from normalize_leds import normalize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/2x4x3-Round-64mm.kicad_pcb'
LIB = ROOT / 'verification/source-footprints.pretty'
b = p.BOARD()
xml = E.parse(ROOT / 'verification/netlist.xml')
comps = {c.attrib['ref']: c for c in xml.findall('.//components/comp')}
expected = {}
for n in xml.findall('.//nets/net'):
    for node in n.findall('node'):
        expected.setdefault(node.attrib['ref'], {})[node.attrib['pin']] = n.attrib['name']
owned = []

def vec(point):
    return p.VECTOR2I(round(point[0] * 1000000), round(point[1] * 1000000))

def xy(v):
    return (p.ToMM(v.x), p.ToMM(v.y))

def route(name, points, layer=p.B_Cu, width=0.5):
    for start, end in zip(points, points[1:]):
        if math.dist(start, end) < 0.00001:
            continue
        t = p.PCB_TRACK(b)
        t.SetStart(vec(start))
        t.SetEnd(vec(end))
        t.SetWidth(p.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(b.FindNet(name))
        b.Add(t)

def via(name, point, diameter=0.65, drill=0.3):
    v = p.PCB_VIA(b)
    v.SetPosition(vec(point))
    v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetWidth(p.FromMM(diameter))
    v.SetDrill(p.FromMM(drill))
    v.SetFrontTentingMode(p.TENTING_MODE_TENTED)
    v.SetBackTentingMode(p.TENTING_MODE_TENTED)
    v.SetNet(b.FindNet(name))
    b.Add(v)

for item in list(b.GetDrawings()) + list(b.GetTracks()) + list(b.Zones()):
    b.Remove(item)
    owned.append(item)
for name in [n.attrib['name'] for n in xml.findall('.//nets/net')]:
    b.Add(p.NETINFO_ITEM(b, name))
for ref, comp in comps.items():
    name = comp.findtext('footprint').split(':', 1)[-1]
    original = p.FootprintLoad(str(LIB), name)
    b.Add(original)
    raw = original.Duplicate(False)
    f = p.Cast_to_FOOTPRINT(raw)
    b.Remove(original)
    b.Add(f)
    owned.extend([original, raw, f])
    f.SetFPIDAsString('Schrune:' + name)
    f.SetReference(ref)
    f.SetValue(comps[ref].findtext('value'))
    f.SetPath(p.KIID_PATH(comps[ref].find('sheetpath').attrib['tstamps'] + comps[ref].findtext('tstamps')))
    for pad in f.Pads():
        pad.SetNet(b.FindNet(expected[ref][pad.GetNumber()]))
    if ref.startswith('TP'):
        f.SetAttributes(f.GetAttributes() | p.FP_DNP | p.FP_EXCLUDE_FROM_BOM | p.FP_EXCLUDE_FROM_POS_FILES)
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)
fp = {f.GetReference(): f for f in b.GetFootprints()}
b.SetCopperLayerCount(2)

channels = ['cool_a', 'warm_a', 'cool_b', 'warm_b', 'cool_c', 'warm_c', 'cool_d', 'warm_d']
led_angles = [-157.5 + 45 * i for i in range(8)]
driver_angles = [180, -135, -90, -45, 0, 45, 90, 135]
# The left cell moves inward to leave a clear through-hole header corridor.
cells = {}
led_records = []

for ch, led_angle, angle in zip(channels, led_angles, driver_angles):
    print('Placing', ch, flush=True)
    index = ['cool_a', 'cool_b', 'cool_c', 'cool_d', 'warm_a', 'warm_b', 'warm_c', 'warm_d'].index(ch)
    i = index + 1
    caps = [ref for ref, c in comps.items() if ref.startswith('C') and c.find('sheetpath').attrib['names'] == '/' + ch + '.channel/']
    roles = {'driver': 'U' + str(i), 'inductor': 'L' + str(i), 'diode': 'D' + str(i), 'cap1': caps[0], 'cap2': caps[1], 'sense1': 'R' + str(index * 2 + 1), 'sense2': 'R' + str(index * 2 + 2), 'series': 'R' + str(33 + index), 'pull': 'R' + str(17 + index), 'bleed': 'R' + str(25 + index)}
    radius = 14.5 if ch == 'cool_a' else 23.5
    a = math.radians(angle)

    def point(tangent, radial):
        r = radius + radial
        return (100 + r * math.cos(a) - tangent * math.sin(a), 100 + r * math.sin(a) + tangent * math.cos(a))

    placements = {'driver': (2.2, 0, 90), 'inductor': (-4, 3.8, 0), 'diode': (-2.5, -2.5, 270), 'cap1': (6.2, 2, 180), 'cap2': (6.2, 4.5, 180), 'sense1': (5.9, -1.5, 180), 'sense2': (5.9, -4, 180), 'series': (3, 5.7, 0), 'pull': (5.9, 0.8, 0), 'bleed': (-4, -7.4, 0)}
    if ch == 'cool_a':
        placements['inductor'] = (0, 8.5, 0)
        placements['cap1'] = (0, -4, 180)
        placements['sense2'] = (9, -4, 180)
        placements['bleed'] = (-4, -9, 0)
        placements['diode'] = (-6.8, -2.5, 270)
        placements['series'] = (3, 3.3, 0)
    if ch == 'warm_d':
        placements['sense2'] = (10.5, 2, 180)
    for role, ref in roles.items():
        print('  ', role, ref, flush=True)
        f = fp[ref]
        f.Flip(f.GetPosition(), True)
        x, y, rotation = placements[role]
        f.SetOrientationDegrees(rotation - angle - 90)
        f.SetPosition(vec(point(x, y)))
        for pad in f.Pads():
            pad.SetNet(b.FindNet(expected[ref][pad.GetNumber()]))
            if role == 'cap1' and pad.GetNetname() == 'GND':
                pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
        f.Reference().SetVisible(False)
        f.Value().SetVisible(False)
        fp[ref] = f

    def local(name, points, width=0.5):
        route(name, [point(*pt) for pt in points], p.B_Cu, width)

    sw, top, ret, dim = [ch + '_channel_' + suffix for suffix in ['driver_SW', 'LED_TOP', 'LED_RETURN', 'pwm_2_2_1']]
    pwm = 'pwm_' + ch.split('_')[0]
    l1, l2 = -1.67, -6.33
    if ch == 'cool_a':
        route(sw, [(86.04, 106.8), (85, 105.76), (85, 100.5), (83.8, 99.3), (80, 99.3), (78.37, 97.67), (77, 97.67)], p.B_Cu, 0.6)
    else:
        local(sw, [(-2.5, -0.54), (-2.5, 0.8), (0.7, 0.8), (0.7, 1.7)], 0.6)
        local(sw, [(0.7, 1.7), (0.43, 1.7), (l1, 3.8)], 0.6)
    top_points = [(3.7, -1.7), (4.9, -1.5), (4.9, -4), (3.5, -4)]
    if ch == 'cool_a':
        top_points = [(3.7, -1.7), (4.9, -1.5), (4.9, -2.6), (6.3, -4), (8, -4)]
    if ch == 'warm_d':
        top_points = [(3.7, -1.7), (4.9, -1.5)]
    local(top, top_points, 0.5)
    top_point = (4.7, 0) if ch == 'cool_a' else (3.5, -4)
    if ch == 'cool_a':
        local(top, [(4.9, -1.5), (4.7, -1.3), top_point], 0.5)
    if ch == 'warm_d':
        local(top, [(4.9, -1.5), (4.9, -4), (3.5, -4)], 0.5)
        local(top, [(9.5, 2), (9.5, 4)], 0.5)
        via(top, point(9.5, 4), 0.6, 0.3)
        route(top, [point(3.5, -4), (81.968777, 115.1), (74.7, 115.1), (74.7, 113.2), point(9.5, 4)], p.F_Cu, 0.5)
    if ch == 'cool_a':
        route(ret, [(94.5, 103), (93.8, 101)], p.B_Cu, 0.5)
        via(ret, (93.8, 101))
        route(ret, [(93.8, 101), (83, 101)], p.F_Cu, 0.5)
        via(ret, (83, 101))
        route(ret, [(83, 101), (80.8, 102.33)], p.B_Cu, 0.5)
    else:
        local(ret, [(-3, -7.4), (-3, -6.2), (-4.5, -6.2), (-4.5, 0.9), (l2, 0.9), (l2, 3.8)], 0.5)
    return_point = (12.17, 4.7) if ch == 'cool_a' else (-7.8, 3.8)
    if ch == 'cool_a':
        route(ret, [(77, 102.33), (80.8, 102.33)], p.B_Cu, 0.5)
        via(ret, (80.8, 102.33))
    else:
        local(ret, [(l2, 3.8), (l2, return_point[1]), return_point], 0.5)
    if ch != 'cool_a':
        via(ret, point(*return_point))
    local(dim, [(3.7, 1.7), (3.7, 0.8), (5.47, 0.8)], 0.254)
    if ch == 'cool_a':
        route(dim, [(82.2, 96.57), (83.8, 96.3)], p.B_Cu, 0.254)
        route(pwm, [(82.2, 97.43), (80.9, 97.43)], p.B_Cu, 0.254)
        via(pwm, (80.9, 97.43))
    else:
        local(dim, [(3.43, 5.7), (3.43, 1.7), (3.7, 1.7)], 0.254)
        local(pwm, [(2.57, 5.7), (1.3, 5.7)], 0.254)
        via(pwm, point(1.3, 5.7))
    local('V+', [(0.7, -1.7), (0.7, -3.2)], 0.6)
    via('V+', point(0.7, -3.2))
    if ch == 'cool_a':
        local('V+', [(1, -4), (0.7, -3.2)], 0.5)
        via('V+', point(6.9, -1.5), 0.6, 0.3)
        local('V+', [(10, -4), (10, -5.5)], 0.5)
        via('V+', point(10, -5.5))
        local('V+', [(7.2, 4.5), (7.2, 6.5)], 0.5)
        via('V+', point(7.2, 6.5))
    else:
        local('V+', [(8.5, -1.5 if ch == 'warm_d' else -4), (8.5, 5.3)], 0.4 if ch == 'warm_d' else 0.5)
        for x, y in [(6.9, -1.5), (6.9, -4), (7.2, 2), (7.2, 4.5)]:
            if ch == 'warm_d' and y == -4:
                continue
            local('V+', [(x, y), (8.5, y)], 0.4 if ch == 'warm_d' else 0.5)
        via('V+', point(8.5, 5.3))
        if ch == 'warm_d':
            local('V+', [(11.5, 2), (13.2, 2)], 0.5)
            via('V+', point(13.2, 2), 0.6, 0.3)
    if ch == 'cool_a':
        route('V+', [(94.5, 105), (96, 105)], p.B_Cu, 0.5)
        via('V+', (96, 105))
    else:
        local('V+', [(-5, -7.4), (-5, -9), (-3, -9)], 0.5)
        via('V+', point(-3, -9))

    leds = [f for f in b.GetFootprints() if f.GetReference().startswith('LED') and any(pad.GetNetname().startswith(ch + '_') for pad in f.Pads())]
    def sig(f):
        return {pad.GetNumber(): pad.GetNetname() for pad in f.Pads()}
    leds.sort(key=lambda f: 0 if sig(f)['2'] == top else 2 if sig(f)['1'] == ret else 1)
    for f, r in zip(leds, [9, 18, 27]):
        owned.extend(normalize(f))
        f.SetOrientationDegrees(180 - led_angle)
        t = math.radians(led_angle)
        f.SetPosition(vec((100 + r * math.cos(t), 100 + r * math.sin(t))))
        f.SetValue(comps[f.GetReference()].findtext('value'))
        f.SetLocked(True)
        led_records.append({'ref': f.GetReference(), 'channel': ch, 'radius': r, 'angle': led_angle})
    for first, second in zip(leds, leds[1:]):
        start = next(pad for pad in first.Pads() if pad.GetNumber() == '1')
        end = next(pad for pad in second.Pads() if pad.GetNumber() == '2')
        route(start.GetNetname(), [xy(start.GetPosition()), xy(end.GetPosition())], p.F_Cu, 1)
    cells[ch] = {'angle': angle, 'radius': radius, 'led_angle': led_angle, 'roles': roles, 'top': point(*top_point), 'return': point(*return_point), 'pwm': point(1.3, 5.7)}
    if ch == 'cool_a':
        cells[ch]['return'] = (80.8, 102.33)
        cells[ch]['pwm'] = (80.9, 97.43)

header = fp['H1']
header.SetOrientationDegrees(90)
header.SetPosition(vec((71.5, 100)))
header.SetAttributes(p.FP_THROUGH_HOLE)
header.SetLocked(True)
for f in b.GetFootprints():
    if f.GetReference().startswith('TP'):
        if f.GetLayer() != p.B_Cu:
            f.Flip(f.GetPosition(), True)
        name = next(iter(f.Pads())).GetNetname()
        f.SetPosition(vec({'V+': (101.5, 95), 'GND': (100, 103.5), 'pwm_cool': (100, 100), 'pwm_warm': (100, 108.5)}[name]))
        if name == 'V+':
            via(name, xy(next(iter(f.Pads())).GetPosition()))

shape = p.PCB_SHAPE(b)
shape.SetShape(p.SHAPE_T_CIRCLE)
shape.SetCenter(vec((100, 100)))
shape.SetEnd(vec((132, 100)))
shape.SetLayer(p.Edge_Cuts)
shape.SetWidth(p.FromMM(0.05))
b.Add(shape)
p.SaveBoard(str(OUT), b)
(ROOT / 'verification/placement.json').write_text(json.dumps({'diameter_mm': 64, 'cells': cells, 'leds': led_records}, indent=2))
print('Saved compact eight-channel placement', OUT)

