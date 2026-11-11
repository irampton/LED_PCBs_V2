import json
import math
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/2x3x3-Round.kicad_pcb'
b = p.LoadBoard(str(OUT))
placement = json.loads((ROOT / 'verification/placement.json').read_text())
fp = {f.GetReference(): f for f in b.GetFootprints()}

def vec(point):
    return p.VECTOR2I(round(point[0] * 1000000), round(point[1] * 1000000))

def xy(v):
    return (p.ToMM(v.x), p.ToMM(v.y))

def route(name, points, layer=p.F_Cu, width=0.5):
    for a, z in zip(points, points[1:]):
        if math.dist(a, z) < 0.00001:
            continue
        t = p.PCB_TRACK(b)
        t.SetStart(vec(a))
        t.SetEnd(vec(z))
        t.SetWidth(p.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(b.FindNet(name))
        b.Add(t)

def via(name, point):
    v = p.PCB_VIA(b)
    v.SetPosition(vec(point))
    v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetWidth(p.FromMM(0.65))
    v.SetDrill(p.FromMM(0.3))
    v.SetNet(b.FindNet(name))
    b.Add(v)

def polar(radius, angle):
    a = math.radians(angle)
    return (100 + radius * math.cos(a), 100 + radius * math.sin(a))

def point(radius, tangent, angle):
    a = math.radians(angle)
    return (100 + radius * math.cos(a) - tangent * math.sin(a), 100 + radius * math.sin(a) + tangent * math.cos(a))

def padpos(ref, number):
    return xy(next(pad for pad in fp[ref].Pads() if pad.GetNumber() == str(number)).GetPosition())

for ch, ports in placement['ports'].items():
    leds = sorted([item for item in placement['leds'] if item['channel'] == ch], key=lambda item: item['radius'])
    angle = leds[0]['angle']
    top, ret = ch + '_channel_LED_TOP', ch + '_channel_LED_RETURN'
    via(top, ports['top'])
    via(ret, ports['return'])
    route(top, [ports['top'], point(35, 9, angle), point(15, 9, angle), point(10.725, 4.725, angle), padpos(leds[0]['ref'], 2)])
    route(ret, [ports['return'], point(30, -4, angle), point(39, -4, angle), point(39, -1.5, angle), padpos(leds[-1]['ref'], 1)])
    pwm = 'pwm_' + ch.split('_')[0]
    inner = point(20, 4, angle)
    route(pwm, [ports['pwm'], point(29.57, 4, angle), inner], width=0.254)
    via(pwm, inner)
    if 'cool' in ch:
        route(pwm, [inner, point(17, 4, angle), polar(9, angle)], p.B_Cu, 0.254)
        via(pwm, polar(9, angle))
        route(pwm, [polar(9, angle), polar(6, angle)], p.F_Cu, 0.254)
    else:
        route(pwm, [inner, point(17, 4, angle), polar(8, angle)], p.B_Cu, 0.254)

# Two concentric control buses on the back, in the quiet central region.
route('pwm_cool', [polar(6, angle) for angle in range(-90, 151, 5)], p.F_Cu, 0.254)
route('pwm_warm', [polar(8, angle) for angle in range(-30, 211, 5)], p.B_Cu, 0.254)

# Header power pins join pours. Control pins escape on front into the central buses.
cool = padpos('H1', 5)
warm = padpos('H1', 6)
route('pwm_cool', [cool, (65, 96), (67, 98), (67, 100)], p.F_Cu, 0.254)
via('pwm_cool', (67, 100))
route('pwm_cool', [(67, 100), (89, 100)], p.B_Cu, 0.254)
via('pwm_cool', (89, 100))
route('pwm_cool', [(89, 100), (94, 100), polar(6, 150)], p.F_Cu, 0.254)
route('pwm_warm', [warm, (59, 96), (59, 97.27), (64.5, 97.27), (66.23, 99), (90, 99), (92, 100)], p.B_Cu, 0.254)
for f in b.GetFootprints():
    if f.GetReference().startswith('TP'):
        name = next(iter(f.Pads())).GetNetname()
        if name == 'pwm_cool':
            via(name, (100, 100))
            route(name, [(100, 100), polar(6, 90)], p.F_Cu, 0.254)
        elif name == 'pwm_warm':
            route(name, [(102, 90), (105, 93), polar(8, -30)], p.B_Cu, 0.254)

for name, layer in [('V+', p.F_Cu), ('GND', p.B_Cu)]:
    z = p.ZONE(b)
    z.SetNet(b.FindNet(name))
    z.SetLayer(layer)
    z.SetLocalClearance(p.FromMM(0.25))
    z.SetThermalReliefGap(p.FromMM(0.25))
    z.SetThermalReliefSpokeWidth(p.FromMM(0.5))
    z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    z.SetMinThickness(p.FromMM(0.2))
    outline = z.Outline()
    outline.NewOutline()
    for a in range(0, 360, 2):
        pt = vec(polar(41.5, a))
        outline.Append(pt.x, pt.y)
    b.Add(z)

p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(OUT), b)
print('Saved routed board', OUT, len(b.GetTracks()), 'tracks/vias')
