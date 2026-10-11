import random, math, os, sys
from PIL import Image, ImageDraw

out = sys.argv[1] if len(sys.argv) > 1 else './scenery'
os.makedirs(out, exist_ok=True)

def C(r, g, b): return (r, g, b, 255)
def dk(c, f): return (min(255, int(c[0] * f)), min(255, int(c[1] * f)), min(255, int(c[2] * f)), 255)
OUT = C(18, 18, 30)
# stone
S1 = C(70, 74, 92); S1b = C(88, 94, 112); S2 = C(112, 118, 136); S3 = C(132, 138, 156); S4 = C(180, 186, 202)
# wood
WD = C(74, 48, 30); WM = C(116, 74, 44); WL = C(156, 104, 60)
# plaster
P1 = C(196, 182, 154); P2 = C(224, 212, 186); P3 = C(164, 150, 126)
# roof
R1 = C(104, 34, 40); R2 = C(156, 54, 52); R3 = C(198, 86, 64); R4 = C(174, 64, 56)
# leaves
L1 = C(28, 66, 48); L2 = C(50, 108, 58); L3 = C(88, 152, 72); L4 = C(146, 194, 100)
IRON = C(50, 52, 66); GOLD = C(238, 192, 72); GLASS = C(110, 160, 196); GLASS_HL = C(204, 232, 246)

def outline(im):
    w, h = im.size; px = im.load(); o = im.copy(); po = o.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0:
                        po[x, y] = OUT; break
    return o

def R(d, x0, y0, x1, y1, col): d.rectangle([x0, y0, x1, y1], fill=col)

def stone_wall(d, x0, y0, x1, y1, rnd, row_h=8, tones=(S2, S2, S3)):
    R(d, x0, y0, x1, y1, S1)
    y = y0; r = 0
    while y <= y1:
        h = min(row_h, y1 - y + 1)
        x = x0 - (rnd.randint(3, 9) if r % 2 else 0)
        while x <= x1:
            w = rnd.randint(10, 17)
            bx0 = max(x, x0); bx1 = min(x + w - 2, x1)
            if bx1 >= bx0 and h >= 3:
                col = rnd.choice(tones)
                R(d, bx0, y, bx1, y + h - 2, col)
                d.line([(bx0, y), (bx1, y)], fill=S4)
                d.line([(bx0, y + h - 2), (bx1, y + h - 2)], fill=S1b)
                if rnd.random() < .5: d.point((rnd.randint(bx0, bx1), rnd.randint(y + 1, y + h - 3)), fill=S1b)
            x += w
        y += row_h; r += 1

def roof_tiles(d, apex, base_y, half_w, rowh, tw, seed=1):
    ax, ay = apex
    for y in range(ay, base_y + 1):
        hw = (y - ay) / max(base_y - ay, 1) * half_w
        for x in range(int(ax - hw), int(ax + hw) + 1):
            row = (y - ay) // rowh; ry = (y - ay) % rowh
            off = (row % 2) * (tw // 2)
            ti = (x + off) // tw; cx_ = (x + off) % tw
            tone = R2 if ((ti * 7 + row * 13) % 5) else R4
            if ry == rowh - 1: col = R1
            elif ry == 0: col = R3
            elif cx_ == tw - 1: col = R1
            else: col = tone
            if abs(x - ax) >= hw - 1.5: col = R1
            d.point((x, y), fill=col)

# ===================== TREE =====================
def make_tree(seed=3):
    rnd = random.Random(seed); W, H = 112, 128
    tr = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tr); cx = 56
    for y in range(66, 127):
        t = (y - 66) / 60; w = int(11 + 8 * t ** 2.4); x0 = cx - w // 2
        for x in range(x0, x0 + w):
            u = (x - x0) / max(w - 1, 1)
            d.point((x, y), fill=WL if u < .22 else (WM if u < .62 else WD))
    for _ in range(30):
        x = rnd.randint(cx - 6, cx + 5); y0 = rnd.randint(78, 118); ln = rnd.randint(3, 9)
        for y in range(y0, y0 + ln):
            if tr.getpixel((x, y))[3] > 0 and tr.getpixel((x, y)) != WL: d.point((x, y), fill=WD)
    for _ in range(14):
        x = rnd.randint(cx - 5, cx + 1); y = rnd.randint(80, 120)
        if tr.getpixel((x, y)) == WM: d.line([(x, y), (x, y + 2)], fill=WL)
    d.line([(52, 84), (34, 66)], fill=WM, width=4); d.line([(60, 84), (80, 64)], fill=WM, width=4)
    can = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c = ImageDraw.Draw(can)
    circles = [(56, 62, 15), (22, 64, 12), (90, 64, 12), (32, 52, 20), (80, 52, 20), (56, 40, 28), (42, 28, 18), (72, 26, 19)]
    for (x, y, r) in circles:
        c.ellipse([x - r, y - r, x + r, y + r], fill=L1)
        for (sx, sy, dr, col) in ((-2, -3, 2, L2), (-4, -6, 8, L3), (-6, -9, 14, L4)):
            rr = r - dr
            if rr >= 2: c.ellipse([x + sx - rr, y + sy - rr, x + sx + rr, y + sy + rr], fill=col)
    src = can.copy(); sp = src.load(); cp = can.load()
    for y in range(1, H):
        for x in range(1, W):
            cc = sp[x, y]
            if cc[3] > 0:
                for dx, dy in ((-1, 0), (0, -1)):
                    n = sp[x + dx, y + dy]
                    if n[3] > 0 and n != cc and rnd.random() < .32: cp[x, y] = n; break
    for _ in range(60):
        x = rnd.randint(8, W - 9); y = rnd.randint(14, 80)
        if sp[x, y][3] > 0 and sp[x, y] in (L2, L3):
            c.rectangle([x, y, x + 1, y], fill=L4 if sp[x, y] == L3 else L3)
    tp = tr.load()
    for y in range(66, 92):
        for x in range(W):
            if tp[x, y][3] > 0 and can.getpixel((x, y))[3] == 0: tp[x, y] = dk(tp[x, y], .72)
    tr.alpha_composite(can)
    return outline(tr)

# ===================== HOUSE =====================
def make_house(seed=5):
    rnd = random.Random(seed); W, H = 160, 160
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # chimney (behind roof)
    stone_wall(d, 117, 6, 131, 54, rnd, row_h=6)
    R(d, 114, 2, 134, 7, S3); d.line([(114, 2), (134, 2)], fill=S4); d.line([(114, 7), (134, 7)], fill=S1b)
    # base floor (stone)
    stone_wall(d, 16, 115, 143, 158, rnd, row_h=8)
    R(d, 16, 115, 143, 118, S1)
    # upper floor plaster
    R(d, 8, 71, 151, 110, P2)
    for _ in range(140): d.point((rnd.randint(8, 151), rnd.randint(75, 109)), fill=rnd.choice((P1, P1, P3)))
    # timbers
    def post(x0, x1, y0, y1):
        R(d, x0, y0, x1, y1, WM); d.line([(x0, y0), (x0, y1)], fill=WL); d.line([(x1, y0), (x1, y1)], fill=WD)
    post(8, 11, 71, 110); post(148, 151, 71, 110); post(56, 59, 71, 110); post(100, 103, 71, 110)
    for (a, b) in (((60, 74), (99, 106)), ((99, 74), (60, 106))):
        d.line([a, b], fill=WD, width=5); d.line([a, b], fill=WM, width=3)
    R(d, 8, 71, 151, 75, WM); d.line([(8, 71), (151, 71)], fill=WL); d.line([(8, 75), (151, 75)], fill=WD)
    R(d, 8, 106, 151, 109, WM); d.line([(8, 106), (151, 106)], fill=WL)
    # jetty beam + corbels
    R(d, 6, 110, 153, 114, WD); d.line([(6, 110), (153, 110)], fill=WM)
    for x in (20, 60, 100, 138):
        d.polygon([(x, 115), (x + 5, 115), (x, 122)], fill=WM)
    # eave shadow
    R(d, 12, 76, 147, 77, P3)
    # upper windows (left, mirrored right)
    def win_up(ox, mir):
        def X(x): return 159 - x if mir else x
        gx0, gx1, gy0, gy1 = 24, 38, 80, 98
        xs = sorted((X(gx0), X(gx1)))
        R(d, xs[0] - 2, gy0 - 2, xs[1] + 2, gy1 + 2, WM)
        R(d, xs[0], gy0, xs[1], gy1, GLASS)
        d.line([(xs[0] + 1, gy0 + 1), (xs[0] + 4, gy0 + 1)], fill=GLASS_HL)
        d.line([(xs[0] + 1, gy0 + 1), (xs[0] + 1, gy0 + 5)], fill=GLASS_HL)
        mx = (xs[0] + xs[1]) // 2
        d.line([(mx, gy0), (mx, gy1)], fill=WD); d.line([(xs[0], (gy0 + gy1) // 2), (xs[1], (gy0 + gy1) // 2)], fill=WD)
        for sx in ((X(17), X(22)), (X(40), X(45))):
            a, b = sorted(sx); R(d, a, gy0 - 2, b, gy1 + 2, WM); d.line([(a + 1, gy0 - 2), (a + 1, gy1 + 2)], fill=WD)
            d.line([(a, gy0 - 2), (a, gy1 + 2)], fill=WL)
        R(d, xs[0] - 2, 99, xs[1] + 2, 103, WM); d.line([(xs[0] - 2, 99), (xs[1] + 2, 99)], fill=WL)
        for k in range(xs[0] - 1, xs[1] + 2, 2):
            d.line([(k, 96), (k, 98)], fill=L3 if k % 4 else L2)
            if k % 6 == 1: d.point((k, 95), fill=C(230, 80, 90))
            if k % 6 == 3: d.point((k, 96), fill=C(240, 210, 90))
    win_up(0, False); win_up(0, True)
    # base windows
    def win_base(mir):
        def X(x): return 159 - x if mir else x
        xs = sorted((X(28), X(41)))
        R(d, xs[0] - 2, 128, xs[1] + 2, 148, S4)
        R(d, xs[0], 130, xs[1], 146, C(40, 56, 88))
        mx = (xs[0] + xs[1]) // 2
        d.line([(mx, 130), (mx, 146)], fill=S1); d.line([(xs[0], 138), (xs[1], 138)], fill=S1)
        d.point((xs[0] + 1, 131), fill=C(130, 160, 200)); d.point((xs[0] + 2, 131), fill=C(130, 160, 200))
        for sx in ((X(21), X(26)), (X(43), X(48))):
            a, b = sorted(sx); R(d, a, 128, b, 148, WM); d.line([(a + 1, 128), (a + 1, 148)], fill=WD); d.line([(a, 128), (a, 148)], fill=WL)
    win_base(False); win_base(True)
    # door
    d.ellipse([66, 118, 93, 142], fill=S4); R(d, 66, 130, 93, 158, S4)
    d.ellipse([69, 121, 90, 139], fill=WM); R(d, 69, 130, 90, 158, WM)
    for x in range(72, 90, 5): d.line([(x, 124 if x in range(73, 87) else 131), (x, 158)], fill=WD)
    d.line([(69, 126), (69, 158)], fill=WD)
    for y in (135, 149): d.line([(69, y), (81, y)], fill=IRON, width=2)
    d.rectangle([86, 146, 87, 147], fill=GOLD)
    R(d, 62, 156, 97, 158, S3); d.line([(62, 156), (97, 156)], fill=S4)
    # roof
    roof_tiles(d, (80, 14), 70, 77, 5, 8)
    R(d, 3, 68, 157, 70, R1)
    d.line([(3, 67), (157, 67)], fill=R3)
    # attic round window
    d.ellipse([71, 37, 89, 55], fill=WM); d.ellipse([73, 39, 87, 53], fill=WD); d.ellipse([74, 40, 86, 52], fill=GLASS)
    d.line([(80, 40), (80, 52)], fill=WD); d.line([(74, 46), (86, 46)], fill=WD)
    d.point((76, 42), fill=GLASS_HL); d.point((77, 42), fill=GLASS_HL)
    return outline(im)

# ===================== WELL =====================
def make_well(seed=9):
    rnd = random.Random(seed); W, H = 48, 64
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
    stone_wall(td, 5, 39, 42, 62, rnd, row_h=6)
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    md.rectangle([5, 39, 42, 57], fill=255); md.ellipse([5, 52, 42, 62], fill=255)
    tp = tmp.load(); mp = mask.load()
    for y in range(H):
        for x in range(W):
            if mp[x, y] and tp[x, y][3]:
                f = 1.12 if x < 9 else (0.62 if x > 39 else (0.8 if x > 34 else 1))
                im.putpixel((x, y), dk(tp[x, y], f) if f < 1 else tp[x, y])
    d.ellipse([5, 33, 42, 45], fill=S3); d.arc([5, 33, 42, 45], 180, 360, fill=S4)
    d.ellipse([9, 35, 38, 43], fill=C(26, 40, 72)); d.line([(14, 37), (22, 37)], fill=C(80, 116, 170))
    for x in (8, 36):
        R(d, x, 16, x + 3, 41, WM); d.line([(x, 16), (x, 41)], fill=WL); d.line([(x + 3, 16), (x + 3, 41)], fill=WD)
    R(d, 6, 18, 42, 22, WM); d.line([(6, 18), (42, 18)], fill=WL); d.line([(6, 22), (42, 22)], fill=WD)
    for x in range(16, 34, 3): d.line([(x, 18), (x + 1, 22)], fill=C(196, 172, 120))
    d.line([(42, 20), (44, 20)], fill=IRON, width=2); d.line([(44, 20), (44, 26)], fill=IRON, width=2); d.rectangle([43, 26, 45, 28], fill=WM)
    d.line([(24, 22), (24, 29)], fill=C(196, 172, 120))
    R(d, 20, 29, 28, 36, WM); d.line([(20, 29), (28, 29)], fill=WD); d.line([(20, 32), (28, 32)], fill=IRON); d.line([(20, 35), (28, 35)], fill=IRON)
    d.line([(21, 29), (21, 36)], fill=WL)
    roof_tiles(d, (24, 1), 16, 22, 4, 6)
    return outline(im)

# ===================== STREET (tileable) =====================
def make_street(seed=7):
    rnd = random.Random(seed); W, H = 64, 40
    big = Image.new('RGBA', (W * 3, H), (0, 0, 0, 255)); d = ImageDraw.Draw(big)
    GAP = C(40, 40, 54); DIRT = C(70, 54, 46)
    R(d, 0, 0, W * 3 - 1, H - 1, GAP)
    R(d, 0, 34, W * 3 - 1, H - 1, DIRT)
    for _ in range(54 * 3 // 3):
        x = rnd.randint(0, W - 1); y = rnd.randint(35, H - 1); col = rnd.choice((C(96, 78, 62), C(52, 40, 36), C(120, 104, 86)))
        for k in range(3): d.point((k * W + x, y), fill=col); d.point((k * W + x + 1, y), fill=col)
    tones = [S2, S3, C(98, 104, 122), C(124, 118, 124)]
    rows = [(4, 10, [18, 14, 16, 16]), (14, 10, [12, 18, 16, 18]), (24, 10, [16, 16, 14, 18])]
    for (y, h, widths) in rows:
        attrs = []; x = 0
        for w in widths:
            sp = [(rnd.randint(1, w - 4), rnd.randint(1, h - 4)) for _ in range(3)]
            attrs.append((x, w, rnd.choice(tones), sp)); x += w
        for k in range(3):
            for (x0, w, col, sp) in attrs:
                X = k * W + x0
                R(d, X, y, X + w - 2, y + h - 2, col)
                for (cx_, cy_) in ((X, y), (X + w - 2, y), (X, y + h - 2), (X + w - 2, y + h - 2)): d.point((cx_, cy_), fill=GAP)
                d.line([(X + 1, y), (X + w - 3, y)], fill=dk(col, 1.32)); d.line([(X + 1, y + h - 2), (X + w - 3, y + h - 2)], fill=dk(col, .72))
                for (sx, sy) in sp: d.point((X + sx, y + sy), fill=dk(col, .85))
    R(d, 0, 0, W * 3 - 1, 1, S4); R(d, 0, 2, W * 3 - 1, 2, S3); R(d, 0, 3, W * 3 - 1, 3, GAP)
    return big.crop((W, 0, 2 * W, H))

tree = make_tree(); house = make_house(); well = make_well(); street = make_street()
tree.save(f'{out}/tree.png'); house.save(f'{out}/medieval_house.png'); well.save(f'{out}/well.png'); street.save(f'{out}/street_tile.png')

# preview scene with the knight for scale
knight = None
_here = os.path.dirname(os.path.abspath(__file__))
for p in ('/mnt/user-data/outputs/knight_spritesheet.png', './knight_spritesheet.png', os.path.join(_here, '..', 'assets', 'knight_spritesheet.png'), os.path.join(_here, '..', '..', '..', '..', 'assets', 'knight_spritesheet.png')):
    if os.path.exists(p): knight = Image.open(p).convert('RGBA').crop((0, 0, 64, 64)); break
W, H = 560, 190; scene = Image.new('RGBA', (W, H), C(122, 178, 224))
for y in range(H): scene.paste(C(122 + y // 6, 178 + y // 10, 224), (0, y, W, y + 1))
TOP = 140
for x in range(0, W, 64): scene.alpha_composite(street, (x, TOP))
G = TOP + 3
def put(im, x, bottom_row=None):
    h = im.size[1]; scene.alpha_composite(im, (x, G - (h - 2)))
put(house, 10); put(tree, 180); put(well, 300)
if knight: scene.alpha_composite(knight, (370, G - 60))
scene.resize((W * 2, H * 2), Image.NEAREST).save(f'{out}/scene_preview.png')
st = Image.new('RGBA', (256, 40))
for k in range(4): st.paste(street, (k * 64, 0))
st.resize((768, 120), Image.NEAREST).save(f'{out}/street_seam_check.png')
print('ok')
