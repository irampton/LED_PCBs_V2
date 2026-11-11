"""Mechanical thermal-contact map and preliminary parametric spreader model."""
import json
import math
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'mechanical'
OUT.mkdir(exist_ok=True)
b = p.LoadBoard(str(ROOT / 'build/2x4x3-Round-64mm.kicad_pcb'))
contacts = json.loads((ROOT / 'verification/thermal-contacts.json').read_text())

def hull(points):
    points = sorted(set(points))
    def cross(a, z, q):
        return (z[0] - a[0]) * (q[1] - a[1]) - (z[1] - a[1]) * (q[0] - a[0])
    low, high = [], []
    for point in points:
        while len(low) >= 2 and cross(low[-2], low[-1], point) <= 0:
            low.pop()
        low.append(point)
    for point in reversed(points):
        while len(high) >= 2 and cross(high[-2], high[-1], point) <= 0:
            high.pop()
        high.append(point)
    return low[:-1] + high[:-1]

def intersects(a, z, clearance=0):
    for poly in [a, z]:
        for first, second in zip(poly, poly[1:] + poly[:1]):
            axis = (second[1] - first[1], first[0] - second[0])
            norm = math.hypot(*axis)
            if norm < 0.00001:
                continue
            av = [q[0] * axis[0] + q[1] * axis[1] for q in a]
            zv = [q[0] * axis[0] + q[1] * axis[1] for q in z]
            if max(av) + clearance * norm < min(zv) or max(zv) + clearance * norm < min(av):
                return False
    return True

parts = []
for f in b.GetFootprints():
    if f.GetLayer() != p.B_Cu or f.GetReference().startswith(('TP', 'MH')):
        continue
    points = []
    for shape in f.GraphicalItems():
        if shape.GetLayer() == p.B_CrtYd:
            for v in [shape.GetStart(), shape.GetEnd()]:
                points.append((p.ToMM(v.x), p.ToMM(v.y)))
    if len(points) >= 3:
        parts.append({'ref': f.GetReference(), 'polygon': hull(points)})
conflicts = []
for contact in contacts:
    for part in parts:
        if intersects(contact['polygon'], part['polygon'], 0.25):
            conflicts.append({'contact': contact['ref'], 'part': part['ref']})
(ROOT / 'verification/thermal-mechanical-audit.json').write_text(json.dumps({'clearance_mm': 0.25, 'contact_body_conflicts': conflicts, 'scope': 'Imported courtyard convex hulls; 3D model tolerances and board warpage not qualified'}, indent=2))

svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="64 64 72 72" width="1000" height="1000">', '<rect x="64" y="64" width="72" height="72" fill="#f5f4ef"/>', '<circle cx="100" cy="100" r="32" fill="white" stroke="#272b30" stroke-width="0.25"/>']
for part in parts:
    points = ' '.join('%g,%g' % point for point in part['polygon'])
    svg.append('<polygon points="%s" fill="#e2e4e6" stroke="#838990" stroke-width="0.08"/>' % points)
for contact in contacts:
    points = ' '.join('%g,%g' % tuple(point) for point in contact['polygon'])
    svg.append('<polygon points="%s" fill="#d88b37" stroke="#76420d" stroke-width="0.1"/>' % points)
    cx = sum(q[0] for q in contact['polygon']) / 4
    cy = sum(q[1] for q in contact['polygon']) / 4
    svg.append('<text x="%g" y="%g" font-family="Arial" font-size="0.8" text-anchor="middle">%s</text>' % (cx, cy + 0.25, contact['ref']))
for x in [96.5, 103.5]:
    svg.append('<circle cx="%g" cy="100" r="1.35" fill="white" stroke="#272b30" stroke-width="0.15"/>' % x)
svg.append('<text x="100" y="132.8" text-anchor="middle" font-family="Arial" font-size="1">PCB coordinates, viewed through the front; mirror for back-side machining</text>')
svg.append('</svg>')
(OUT / 'thermal-contact-map.svg').write_text('\n'.join(svg))

scad = ['// Preliminary concept only. Dimensions mm. PCB BACK face is z=0.', '// Thermal interface is 0.3mm; metal contacts stop at z=-0.3.', '// Obtain machining/clearance/flatness review before manufacture.', '$fn=160;', 'difference() {', '    union() {', '        translate([0,0,-8.8]) cylinder(h=3,r=32);']
for contact in contacts:
    points = [[round(q[0] - 100, 6), round(100 - q[1], 6)] for q in contact['polygon']]
    scad.append('        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=%s); // %s' % (json.dumps(points), contact['ref']))
scad.extend(['    }', '    for (x=[-3.5,3.5]) {', '        translate([x,0,-10]) cylinder(h=12,d=2.7);', '    }', '}'])
(OUT / 'spreader-concept.scad').write_text('\n'.join(scad))
print('Contact/body conflicts:', conflicts)
print('Saved contact map and preliminary spreader concept')
