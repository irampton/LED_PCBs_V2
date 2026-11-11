"""Manually specified global routes, thermal via lands, and mounting features."""
import json
import math
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/2x4x3-Round-64mm.kicad_pcb'
b = p.LoadBoard(str(OUT))
placement = json.loads((ROOT / 'verification/placement.json').read_text())
fp = {f.GetReference(): f for f in b.GetFootprints()}
owned = []

def vec(point):
    return p.VECTOR2I(round(point[0] * 1000000), round(point[1] * 1000000))

def xy(v):
    return (p.ToMM(v.x), p.ToMM(v.y))

def polar(radius, angle):
    a = math.radians(angle)
    return (100 + radius * math.cos(a), 100 + radius * math.sin(a))

def point(radius, tangent, angle):
    a = math.radians(angle)
    return (100 + radius * math.cos(a) - tangent * math.sin(a), 100 + radius * math.sin(a) + tangent * math.cos(a))

def route(name, points, layer=p.F_Cu, width=0.5):
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

def via(name, position, diameter=0.65, drill=0.3):
    v = p.PCB_VIA(b)
    v.SetPosition(vec(position))
    v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetWidth(p.FromMM(diameter))
    v.SetDrill(p.FromMM(drill))
    v.SetFrontTentingMode(p.TENTING_MODE_TENTED)
    v.SetBackTentingMode(p.TENTING_MODE_TENTED)
    v.SetNet(b.FindNet(name))
    b.Add(v)

def arc(name, radius, start, end, layer=p.F_Cu, width=0.5):
    count = max(1, math.ceil(abs(end - start) / 3))
    route(name, [polar(radius, start + (end - start) * i / count) for i in range(count + 1)], layer, width)

def padpos(ref, number):
    return xy(next(pad for pad in fp[ref].Pads() if pad.GetNumber() == str(number)).GetPosition())

for ch, cell in placement['cells'].items():
    angle, led_angle, radius = cell['angle'], cell['led_angle'], cell['radius']
    leds = sorted([item for item in placement['leds'] if item['channel'] == ch], key=lambda item: item['radius'])
    top, ret = ch + '_channel_LED_TOP', ch + '_channel_LED_RETURN'
    via(top, cell['top'])
    corridor = angle + 10
    route(top, [cell['top'], polar(12, corridor), polar(7.725, corridor)])
    arc(top, 7.725, corridor, led_angle if led_angle > angle else led_angle + 360)
    route(top, [polar(7.725, led_angle), padpos(leds[0]['ref'], 2)])
    if ch == 'cool_a':
        route(ret, [cell['return'], polar(25.5, 175)])
        arc(ret, 25.5, 175, 196)
        route(ret, [polar(25.5, 196), polar(30, 196)])
        arc(ret, 30, 196, 202.5)
    else:
        start = angle + math.degrees(math.atan2(-7.8, radius + 3.8))
        route(ret, [cell['return'], polar(31.2, start)])
        arc(ret, 31.2, start, angle + 22.5)
    route(ret, [polar(30 if ch == 'cool_a' else 31.2, led_angle), padpos(leds[-1]['ref'], 1)])

    pwm = 'pwm_' + ch.split('_')[0]
    mid = point(radius - 4, -0.7, angle)
    if ch == 'cool_a':
        mid = point(radius - 4, 0, angle)
    pwm_points = [cell['pwm'], point(radius, 1.3, angle)]
    if ch == 'cool_a':
        pwm_points.append((85.5, 100))
    pwm_points.append(mid)
    route(pwm, pwm_points, width=0.254)
    if ch == 'cool_a':
        route(pwm, [mid, (94.5, 100), (94.5, 97.5), (100, 97.5), (100, 99)], width=0.254)
    elif ch == 'cool_c':
        route(pwm, [mid, (108, 100), (105.5, 100), (105.5, 97.5), (100, 97.5), (100, 99)], width=0.254)
    elif ch.startswith('cool'):
        route(pwm, [mid, polar(1, angle)], width=0.254)
    else:
        inner_radius = 10 if ch == 'warm_d' else 7
        via_angle = angle
        route(pwm, [mid, polar(inner_radius, via_angle)], width=0.254)
        via(pwm, polar(inner_radius, via_angle))
        if ch == 'warm_d':
            route(pwm, [polar(10, via_angle), (97, 108), polar(7, 90)], p.B_Cu, 0.254)

arc('pwm_cool', 1, -90, 90, p.F_Cu, 0.254)
arc('pwm_warm', 7, -135, 90, p.B_Cu, 0.254)
route('pwm_cool', [padpos('H1', 5), (76, 100)], p.B_Cu, 0.254)
via('pwm_cool', (76, 100))
route('pwm_cool', [(76, 100), (94.5, 100), (94.5, 97.5), (100, 97.5), (100, 99)], width=0.254)
route('pwm_warm', [padpos('H1', 6), (68.9, 100), (68.9, 101.27), (73.935, 101.27), (73.935, 104.2), (83.5, 104.2)], p.B_Cu, 0.2)
via('pwm_warm', (83.5, 104.2))
route('pwm_warm', [(83.5, 104.2), (86.5, 104.2)], width=0.254)
via('pwm_warm', (86.5, 104.2))
route('pwm_warm', [(86.5, 104.2), (88, 105.6), (93, 105.6), (97, 108), polar(7, 90)], p.B_Cu, 0.254)
via('pwm_cool', (100, 100))
route('pwm_cool', [(100, 100), polar(1, 90)], width=0.254)
route('pwm_warm', [(100, 108.5), polar(7, 90)], p.B_Cu, 0.254)
route('V+', [padpos('H1', 7), padpos('H1', 9)], p.B_Cu, 0.6)
route('V+', [padpos('H1', 1), padpos('H1', 3)], p.B_Cu, 0.6)

# Each cathode has six ordinary plated thermal vias and a rear contact land.
# These are LIVE LED nets: use an electrically insulating thermal interface.
contacts = []
thermal_zones = []
for item in placement['leds']:
    ref, radius, angle = item['ref'], item['radius'], item['angle']
    name = next(pad.GetNetname() for pad in fp[ref].Pads() if pad.GetNumber() == '1')
    cathode = padpos(ref, 1)
    capped = item['channel'] == 'warm_d' and radius in [9, 18] or item['channel'] == 'cool_a' and radius == 9
    if capped:
        for radial in [0.25, 0.9, 1.55]:
            for tangent in [-0.65, 0, 0.65]:
                via(name, point(radius + radial, tangent, angle), 0.55, 0.3)
        polygon = [point(radius + r, t, angle) for r, t in [(-0.125, -1.15), (1.925, -1.15), (1.925, 1.15), (-0.125, 1.15)]]
    else:
        first = 4.0 if radius == 18 else 2.6
        tangent_offset = 2.0 if radius == 18 else 0
        route(name, [cathode, point(radius + first, tangent_offset, angle), point(radius + first + 1.2, tangent_offset, angle)], width=1)
        for radial in [first, first + 1.2]:
            route(name, [point(radius + radial, tangent_offset - 0.9, angle), point(radius + radial, tangent_offset + 0.9, angle)], width=0.8)
            for tangent in [tangent_offset - 0.9, tangent_offset, tangent_offset + 0.9]:
                via(name, point(radius + radial, tangent, angle), 0.8, 0.5)
        polygon = [point(radius + r, t, angle) for r, t in [(first - 0.6, tangent_offset - 1.6), (first + 1.8, tangent_offset - 1.6), (first + 1.8, tangent_offset + 1.6), (first - 0.6, tangent_offset + 1.6)]]
    z = p.ZONE(b)
    z.SetNet(b.FindNet(name))
    z.SetLayer(p.B_Cu)
    z.SetAssignedPriority(2)
    z.SetLocalClearance(p.FromMM(0.25))
    z.SetPadConnection(p.ZONE_CONNECTION_FULL)
    z.SetMinThickness(p.FromMM(0.5))
    z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    outline = z.Outline()
    outline.NewOutline()
    for pos in polygon:
        v = vec(pos)
        outline.Append(v.x, v.y)
    b.Add(z)
    thermal_zones.append(z)
    contacts.append({'ref': ref, 'net': name, 'polygon': polygon, 'via_count': 9 if capped else 6, 'drill_mm': 0.3 if capped else 0.5, 'filled_and_copper_capped_required': capped})

# Two centre holes clamp an insulated, pocketed metal spreader to the board.
for i, x in enumerate([96.5, 103.5], 1):
    f = p.FOOTPRINT(b)
    f.SetReference('MH' + str(i))
    f.SetValue('M2.5 NPTH')
    f.SetFPIDAsString('Schrune:MountingHole_2.7mm_M2.5')
    f.SetAttributes(p.FP_BOARD_ONLY | p.FP_EXCLUDE_FROM_BOM | p.FP_EXCLUDE_FROM_POS_FILES)
    b.Add(f)
    f.SetPosition(vec((x, 100)))
    pad = p.PAD(f)
    pad.SetNumber('')
    pad.SetAttribute(p.PAD_ATTRIB_NPTH)
    pad.SetShape(p.PAD_SHAPE_CIRCLE)
    pad.SetSize(vec((2.7, 2.7)))
    pad.SetDrillSize(vec((2.7, 2.7)))
    layers = p.LSET.AllCuMask()
    layers.AddLayer(p.F_Mask)
    layers.AddLayer(p.B_Mask)
    pad.SetLayerSet(layers)
    pad.SetPosition(vec((x, 100)))
    f.Add(pad)
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)
    owned.extend([f, pad])

for name, layer in [('V+', p.F_Cu), ('GND', p.B_Cu)]:
    z = p.ZONE(b)
    z.SetNet(b.FindNet(name))
    z.SetLayer(layer)
    z.SetLocalClearance(p.FromMM(0.25))
    z.SetThermalReliefGap(p.FromMM(0.25))
    z.SetThermalReliefSpokeWidth(p.FromMM(0.4))
    z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    z.SetMinThickness(p.FromMM(0.3))
    z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    outline = z.Outline()
    outline.NewOutline()
    for angle in range(0, 360, 2):
        pos = vec(polar(31.5, angle))
        outline.Append(pos.x, pos.y)
    b.Add(z)

p.ZONE_FILLER(b).Fill(b.Zones())
for zone in thermal_zones:
    mask = p.PCB_SHAPE(b)
    mask.SetShape(p.SHAPE_T_POLY)
    mask.SetLayer(p.B_Mask)
    mask.SetPolyShape(p.SHAPE_POLY_SET(zone.GetFilledPolysList(p.B_Cu)))
    mask.SetFilled(True)
    mask.SetWidth(0)
    b.Add(mask)
    owned.append(mask)
p.SaveBoard(str(OUT), b)
(ROOT / 'verification/thermal-contacts.json').write_text(json.dumps(contacts, indent=2))
print('Saved routed board', OUT)
