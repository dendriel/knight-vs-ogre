"""Scenery for the three stage themes (T33 plains, T34 forest, T35 city): props + a ground tile each.
Same conventions as scenery_gen.py: 1 px outline (18,18,30), light from the top-left, the last solid row is the ground and
the row below it is the outline. Props are drawn on a canvas with a 1 px transparent margin.

    python theme_gen.py [out_dir]
"""
import math, os, random, sys
from PIL import Image, ImageDraw

out = sys.argv[1] if len(sys.argv) > 1 else './themes'
os.makedirs(out, exist_ok=True)


def C(r, g, b): return (r, g, b, 255)


OUT = C(18, 18, 30)
# wood
WD, WM, WL = C(74, 48, 30), C(116, 74, 44), C(156, 104, 60)
# cloth
CRD, CRM, CRL = C(112, 28, 36), C(176, 50, 50), C(214, 90, 70)
CRM_, CRH = C(238, 226, 190), C(204, 188, 150)          # cream cloth light / shade
GOLD, GOLD_D = C(238, 192, 72), C(176, 130, 44)
# steel / stone
ST1, ST2, ST3, ST4 = C(70, 74, 92), C(112, 118, 136), C(160, 166, 182), C(214, 224, 240)
# earth / grass
DIRT1, DIRT2, DIRT3 = C(70, 54, 46), C(112, 84, 56), C(150, 118, 80)
GR1, GR2, GR3, GR4 = C(40, 88, 52), C(70, 140, 66), C(112, 182, 84), C(168, 214, 112)
HAY1, HAY2, HAY3 = C(150, 116, 40), C(204, 164, 64), C(238, 208, 112)
FIRE1, FIRE2, FIRE3 = C(220, 70, 40), C(250, 150, 50), C(255, 226, 110)


def canvas(w, h): return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def outline(im):
    w, h = im.size; px = im.load(); o = im.copy(); po = o.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0: po[x, y] = OUT; break
    return o


def box(d, x0, y0, x1, y1, base, hl=None, sh=None):
    d.rectangle([x0, y0, x1, y1], fill=base)
    if hl: d.line([(x0, y0), (x1, y0)], fill=hl); d.line([(x0, y0), (x0, y1)], fill=hl)
    if sh: d.line([(x0, y1), (x1, y1)], fill=sh); d.line([(x1, y0), (x1, y1)], fill=sh)


def tile_ground(top, body, body_hl, dirt, pebble_cols, blade_cols, seed, tuft=True):
    """64x40 tile that repeats horizontally: a few rows of surface (top..body), dirt below with pebbles."""
    rnd = random.Random(seed); W, H = 64, 40
    big = Image.new('RGBA', (W * 3, H), dirt); d = ImageDraw.Draw(big)
    for y in range(0, 8):                                      # surface band, lightest on the first rows
        col = top if y < 2 else (body_hl if y < 4 else body)
        d.rectangle([0, y, W * 3 - 1, y], fill=col)
    for _ in range(70):                                        # pebbles / roots in the dirt (wrap-safe: 3 copies)
        x = rnd.randint(0, W - 1); y = rnd.randint(10, H - 1); c = rnd.choice(pebble_cols)
        for k in range(3): d.point((k * W + x, y), fill=c); d.point((k * W + x + 1, y), fill=c)
    if tuft:
        for _ in range(26):                                    # blades hanging into the dirt line
            x = rnd.randint(0, W - 1); h = rnd.randint(2, 5); c = rnd.choice(blade_cols)
            for k in range(3): d.line([(k * W + x, 7), (k * W + x, 7 + h)], fill=c)
    return big.crop((W, 0, 2 * W, H))


props = {}

# =============================================================== plains (T33)
def tent():
    w, h = 82, 60; im = canvas(w, h); d = ImageDraw.Draw(im); ap = (41, 8); gy = h - 2
    n = 6
    for i in range(n):                                          # coloured wedges from the apex to the ground
        xa = 4 + i * (74 // n); xb = 4 + (i + 1) * (74 // n)
        left = xa + (xb - xa) / 2 < 41
        col = (CRM if i % 2 == 0 else CRM_) if left else (CRD if i % 2 == 0 else CRH)
        d.polygon([ap, (xa, gy), (xb, gy)], fill=col)
    d.polygon([(41, 26), (31, gy), (51, gy)], fill=C(34, 24, 28))      # entrance
    d.line([(41, 26), (41, gy)], fill=C(54, 38, 42))
    d.line([(41, 1), (41, 8)], fill=WM, width=1)                          # pole + pennant
    d.polygon([(42, 1), (52, 3), (42, 6)], fill=CRM)
    for x in (2, 78): d.line([(x, gy - 6), (x + (-1 if x < 41 else 1), gy)], fill=WD)   # tie pegs
    return outline(im)

def banner():
    w, h = 24, 66; im = canvas(w, h); d = ImageDraw.Draw(im); gy = h - 2
    d.line([(11, 2), (11, gy)], fill=WM, width=2); d.line([(10, 2), (10, gy)], fill=WL)
    d.ellipse([9, 0, 13, 4], fill=GOLD)                                   # finial
    d.line([(4, 7), (19, 7)], fill=WD, width=1)                           # cross bar
    d.polygon([(5, 8), (18, 8), (18, 36), (11, 42), (5, 36)], fill=CRM)   # cloth with a swallow-tail edge
    d.polygon([(5, 8), (11, 8), (11, 42), (5, 36)], fill=CRL)
    d.polygon([(11, 8), (18, 8), (18, 36), (11, 42)], fill=CRD)
    d.polygon([(11, 15), (14, 21), (11, 27), (8, 21)], fill=GOLD)         # emblem
    d.point((11, 21), fill=GOLD_D)
    d.rectangle([7, gy - 2, 15, gy], fill=ST2)                            # base stone
    return outline(im)

def palisade():
    w, h = 68, 36; im = canvas(w, h); d = ImageDraw.Draw(im); gy = h - 2
    for i in range(5):
        x0 = 2 + i * 13; top = 6 + (i % 2) * 3
        d.polygon([(x0, gy), (x0, top + 5), (x0 + 5, top), (x0 + 10, top + 5), (x0 + 10, gy)], fill=WM)
        d.line([(x0 + 1, top + 5), (x0 + 5, top + 1)], fill=WL); d.line([(x0 + 1, top + 5), (x0 + 1, gy)], fill=WL)
        d.line([(x0 + 10, top + 5), (x0 + 10, gy)], fill=WD); d.line([(x0 + 5, top + 1), (x0 + 5, gy)], fill=WD)
    d.rectangle([1, 18, w - 3, 20], fill=WD); d.line([(1, 18), (w - 3, 18)], fill=WL)       # cross rope / beam
    return outline(im)

def planted_swords():
    w, h = 34, 36; im = canvas(w, h); d = ImageDraw.Draw(im); gy = h - 2
    d.ellipse([3, gy - 4, 30, gy + 1], fill=DIRT2)                          # mound
    for x, tilt in ((9, -3), (17, 0), (25, 3)):
        d.line([(x, gy - 2), (x + tilt, 6)], fill=ST3, width=3); d.line([(x - 1, gy - 2), (x + tilt - 1, 6)], fill=ST4)
        d.polygon([(x + tilt - 4, 12), (x + tilt + 4, 12), (x + tilt + 3, 14), (x + tilt - 3, 14)], fill=GOLD)
        d.line([(x + tilt, 12), (x + tilt, 12)], fill=GOLD_D)
    d.rectangle([13, 4, 21, 7], fill=ST2)                                   # a helmet hung on the middle sword
    d.line([(13, 4), (21, 4)], fill=ST4)
    return outline(im)

def dead_tree():
    w, h = 64, 90; im = canvas(w, h); d = ImageDraw.Draw(im); gy = h - 2
    d.polygon([(24, gy), (28, 52), (36, 52), (42, gy)], fill=WM)
    d.polygon([(24, gy), (28, 52), (31, 52), (30, gy)], fill=WL)
    d.polygon([(36, 52), (42, gy), (37, gy)], fill=WD)
    br = [((32, 54), (16, 36), 4), ((32, 52), (46, 30), 4), ((16, 36), (8, 22), 2), ((16, 36), (22, 18), 2),
          ((46, 30), (54, 16), 2), ((46, 30), (40, 12), 2), ((32, 52), (32, 26), 4), ((32, 26), (26, 8), 2),
          ((32, 26), (38, 6), 2), ((22, 18), (18, 6), 1), ((54, 16), (60, 8), 1)]
    for a, b, wd in br:
        d.line([a, b], fill=WM, width=wd)
        d.line([(a[0] - 1, a[1]), (b[0] - 1, b[1])], fill=WL, width=1)
    return outline(im)

def cart():
    w, h = 80, 48; im = canvas(w, h); d = ImageDraw.Draw(im); gy = h - 2
    d.polygon([(10, 14), (62, 14), (58, 32), (14, 32)], fill=WM)                  # body
    for i in range(3): d.line([(12 + i * 1, 18 + i * 5), (60 - i, 18 + i * 5)], fill=WD)
    d.line([(10, 14), (62, 14)], fill=WL)
    d.polygon([(14, 14), (20, 6), (32, 4), (46, 5), (56, 7), (60, 14)], fill=HAY2)   # hay load
    d.polygon([(14, 14), (20, 6), (32, 4), (24, 14)], fill=HAY3)
    d.line([(32, 4), (46, 5), (56, 7), (60, 14)], fill=HAY1)
    d.line([(62, 20), (78, 28)], fill=WD, width=2); d.line([(62, 22), (78, 30)], fill=WL)   # shafts
    for cx in (24, 50):                                                                 # wheels
        d.ellipse([cx - 11, gy - 22, cx + 11, gy], fill=WD)
        d.ellipse([cx - 9, gy - 20, cx + 9, gy - 2], fill=WM)
        d.ellipse([cx - 6, gy - 17, cx + 6, gy - 5], fill=WD)
        for a in range(0, 180, 45):
            r = math.radians(a); d.line([(cx - 9 * math.cos(r), gy - 11 - 9 * math.sin(r)),
                                         (cx + 9 * math.cos(r), gy - 11 + 9 * math.sin(r))], fill=WL)
        d.ellipse([cx - 2, gy - 13, cx + 2, gy - 9], fill=GOLD_D)
    return outline(im)

def campfire():
    w, h = 24, 20; im = canvas(w, h); d = ImageDraw.Draw(im); gy = h - 2
    for x in (3, 7, 12, 16): d.ellipse([x, gy - 4, x + 5, gy], fill=ST2); d.point((x + 1, gy - 3), fill=ST4)   # ring of stones
    d.line([(6, gy - 3), (17, gy - 6)], fill=WM, width=2); d.line([(7, gy - 6), (16, gy - 2)], fill=WD, width=2)   # crossed logs
    d.polygon([(12, 1), (16, 8), (14, 12), (10, 12), (8, 7)], fill=FIRE1)
    d.polygon([(12, 4), (15, 9), (13, 12), (10, 12), (9, 8)], fill=FIRE2)
    d.polygon([(12, 7), (13, 10), (11, 12), (10, 10)], fill=FIRE3)
    return outline(im)

props.update(tent=tent(), banner=banner(), palisade=palisade(), planted_swords=planted_swords(), dead_tree=dead_tree(),
             cart=cart(), campfire=campfire())
props['grass_tile'] = tile_ground(GR3, GR2, GR4, DIRT1, (DIRT2, C(54, 42, 36), DIRT3), (GR1, GR2, GR3), seed=11)

for name, im in props.items():
    im.save(f'{out}/{name}.png')
print('ok', len(props))
