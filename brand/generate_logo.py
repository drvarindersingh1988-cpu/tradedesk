import math, sys, os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
OUT = sys.argv[1]
_cache = {}

def font(name, wght):
    key = (name, wght)
    if key not in _cache:
        f = TTFont(os.path.join(FONTS, name))
        _cache[key] = instantiateVariableFont(f, {"wght": wght})
    return _cache[key]

def text_path(txt, fname, wght, size, tracking=0.0):
    f = font(fname, wght)
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    s = size / upm
    x, parts = 0.0, []
    for i, ch in enumerate(txt):
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        parts.append(pen.getCommands())
        x += gs[g].width * s
        if i < len(txt) - 1:
            x += tracking * size
    return " ".join(parts), x

def cap_height(fname, wght, size):
    f = font(fname, wght)
    return f["OS/2"].sCapHeight * size / f["head"].unitsPerEm

def contour(r, phase, n=180):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1 + 0.038 * math.sin(2 * t + phase) + 0.024 * math.sin(3 * t + 1.7 + phase * 0.6) + 0.012 * math.sin(5 * t + 0.4)
        pts.append((r * k * math.cos(t), r * k * math.sin(t) * 0.94))
    d = "M%.2f %.2f" % pts[0]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += " C%.2f %.2f %.2f %.2f %.2f %.2f" % (*c1, *c2, *p2)
    return d + "Z"

def cross(a, w, rr):
    h = w / 2
    pts = [(-h, -a), (h, -a), (h, -h), (a, -h), (a, h), (h, h), (h, a), (-h, a), (-h, h), (-a, h), (-a, -h), (-h, -h)]
    return "M" + " L".join("%.2f %.2f" % p for p in pts) + "Z"

def emblem(cx, cy, R, line, copper_id, stroke, rings=4, sw=1.6):
    g = ['<g transform="translate(%.2f %.2f)">' % (cx, cy)]
    for i in range(rings):
        r = R * (1 - i * 0.185)
        op = 1 - i * 0.14
        g.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" stroke-opacity="%.2f"/>' % (contour(r, i * 0.5), stroke, sw, op))
    a = R * 0.2
    g.append('<path d="%s" fill="url(#%s)" stroke="url(#%s)" stroke-width="%.2f" stroke-linejoin="round"/>' % (cross(a, a * 0.58, 0), copper_id, copper_id, R * 0.012))
    g.append("</g>")
    return "\n".join(g)

DEFS = '''<defs>
<linearGradient id="cu" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#D9935A"/><stop offset="0.5" stop-color="#B87333"/><stop offset="1" stop-color="#8E5525"/>
</linearGradient>
<linearGradient id="cu2" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#E8A86F"/><stop offset="0.5" stop-color="#C9844A"/><stop offset="1" stop-color="#9C6130"/>
</linearGradient>
</defs>'''

def lockup(dark, fname="Jost[wght].ttf", wght=380, tagline=True):
    ink = "#EDE7DD" if dark else "#1A1F27"
    sub = "#9A958D" if dark else "#6B6F76"
    cu = "cu2" if dark else "cu"
    bg = "#12161C" if dark else "#FBF9F6"
    W, H = 1200, 420
    size = 92
    tr = 0.16
    p1, w1 = text_path("REMOT", fname, wght, size, tr)
    p2, w2 = text_path("EMR", fname, wght + 80, size, tr)
    gap = tr * size
    tx, ch = 400, cap_height(fname, wght, size)
    base = H / 2 + ch / 2 - (22 if tagline else 0)
    body = [emblem(235, H / 2, 125, None, cu, ink, sw=1.7)]
    body.append('<line x1="378" y1="%.1f" x2="378" y2="%.1f" stroke="%s" stroke-opacity="0.25" stroke-width="1"/>' % (H / 2 - 95, H / 2 + 95, ink))
    body.append('<path transform="translate(%.1f %.1f)" d="%s" fill="%s"/>' % (tx + 18, base, p1, ink))
    body.append('<path transform="translate(%.1f %.1f)" d="%s" fill="url(#%s)"/>' % (tx + 18 + w1 + gap, base, p2, cu))
    if tagline:
        ts = 19
        pt, wt = text_path("MEDICAL RECORDS FOR REMOTE SITES", fname, 420, ts, 0.42)
        full = w1 + gap + w2
        body.append('<path transform="translate(%.1f %.1f)" d="%s" fill="%s"/>' % (tx + 18 + (full - wt) / 2, base + 52, pt, sub))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s<rect width="100%%" height="100%%" fill="%s"/>%s</svg>' % (W, H, W, H, DEFS, bg, "\n".join(body))

def icon(dark=True):
    bg = "#12161C" if dark else "#FBF9F6"
    ink = "#EDE7DD" if dark else "#1A1F27"
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">%s<rect width="512" height="512" rx="112" fill="%s"/>%s</svg>' % (DEFS, bg, emblem(256, 256, 190, None, "cu2" if dark else "cu", ink, sw=3.2))

def stacked(dark=False):
    ink = "#EDE7DD" if dark else "#1A1F27"
    sub = "#9A958D" if dark else "#6B6F76"
    cu = "cu2" if dark else "cu"
    bg = "#12161C" if dark else "#FBF9F6"
    W, H = 800, 800
    size, tr = 78, 0.16
    p1, w1 = text_path("REMOT", "Jost[wght].ttf", 380, size, tr)
    p2, w2 = text_path("EMR", "Jost[wght].ttf", 460, size, tr)
    gap = tr * size
    full = w1 + gap + w2
    x0 = (W - full) / 2
    pt, wt = text_path("MEDICAL RECORDS FOR REMOTE SITES", "Jost[wght].ttf", 420, 16, 0.42)
    body = [emblem(W / 2, 300, 170, None, cu, ink, sw=2.2),
            '<path transform="translate(%.1f 600)" d="%s" fill="%s"/>' % (x0, p1, ink),
            '<path transform="translate(%.1f 600)" d="%s" fill="url(#%s)"/>' % (x0 + w1 + gap, p2, cu),
            '<path transform="translate(%.1f 648)" d="%s" fill="%s"/>' % ((W - wt) / 2, pt, sub)]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s<rect width="100%%" height="100%%" fill="%s"/>%s</svg>' % (W, H, W, H, DEFS, bg, "\n".join(body))

os.makedirs(OUT, exist_ok=True)
files = {
    "remotemr-logo-light.svg": lockup(False),
    "remotemr-logo-dark.svg": lockup(True),
    "remotemr-logo-stacked.svg": stacked(False),
    "remotemr-logo-stacked-dark.svg": stacked(True),
    "remotemr-icon.svg": icon(True),
    "remotemr-icon-light.svg": icon(False),
}
for n, s in files.items():
    open(os.path.join(OUT, n), "w").write(s)
print("ok", list(files))
