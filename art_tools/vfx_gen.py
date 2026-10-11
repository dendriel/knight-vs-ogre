import sys, math, json, os, random
from PIL import Image

F = 64
def C(r, g, b): return (r, g, b, 255)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def keep(x, y, alpha): return alpha >= 1 or alpha > (BAYER[y % 4][x % 4] + .5) / 16      # ordered dithering = fake transparency

def put(im, x, y, col, alpha=1.0):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < F and 0 <= y < F and keep(x, y, alpha): im.putpixel((x, y), col)

def line(im, a, b, col, alpha=1.0):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for k in range(n + 1):
        t = k / max(n, 1); put(im, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, col, alpha)

def circumcircle(p1, p2, p3):
    ax, ay = p1; bx, by = p2; cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay) + (cx ** 2 + cy ** 2) * (ay - by)) / d
    uy = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx) + (cx ** 2 + cy ** 2) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)

def crescent(im, c, r_out, th0, th1, tail, head, tmax, pal, alpha=1.0):
    core, mid, edge, outer = pal; N = 500
    for k in range(N + 1):
        u = k / N
        if u < tail or u > head: continue
        env = math.sin(math.pi * (u - tail) / max(head - tail, 1e-6)) ** 0.7
        th = tmax * env
        if th < 0.7: continue
        a = th0 + (th1 - th0) * u; ca, sa = math.cos(a), math.sin(a)
        steps = int(th * 2) + 1
        for s in range(steps + 1):
            f = s / steps; r = r_out - th * f
            col = edge if f < .14 else (core if f < .62 else (mid if f < .88 else outer))
            if th < 2.2: col = core if f < .7 else mid
            put(im, c[0] + ca * r, c[1] + sa * r, col, alpha)

def sparks(im, c, r, th0, th1, u_lo, u_hi, n, cols, seed, alpha=1.0, spread=(2, 7)):
    rnd = random.Random(seed)
    for _ in range(n):
        u = rnd.uniform(u_lo, u_hi); a = th0 + (th1 - th0) * u; rr = r + rnd.uniform(*spread)
        x, y = c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr
        col = rnd.choice(cols); put(im, x, y, col, alpha)
        if rnd.random() < .5: put(im, x + math.cos(a), y + math.sin(a), col, alpha)

def arc_through(p1, p2, p3):
    c, R = circumcircle(p1, p2, p3)
    ang = [math.atan2(p[1] - c[1], p[0] - c[0]) for p in (p1, p2, p3)]
    d = (ang[2] - ang[0] + math.pi) % (2 * math.pi) - math.pi
    return c, R, ang[0], ang[0] + d

SWORD = (C(252, 254, 255), C(196, 226, 255), C(120, 176, 240), C(74, 116, 206))
AXEC = (C(255, 248, 222), C(255, 208, 120), C(238, 134, 62), C(172, 72, 44))
SPARK_S = (C(255, 255, 255), C(196, 226, 255), C(140, 190, 250))
SPARK_A = (C(255, 250, 220), C(255, 214, 120), C(244, 150, 70))

# ---- 1) knight sword slash: effect frame i is played together with attack_sword frame 3+i (same anchor) ----
def sword_slash(i):
    im = Image.new('RGBA', (F, F), (0, 0, 0, 0))
    c, R, t0, t1 = arc_through((8, 29), (33, 42), (61, 34))   # varredura lateral: arco raso na altura do peito
    r = R - 2
    win = [(0.0, 0.5, 4, 1), (0.0, 1.0, 6, 1), (0.3, 1.0, 5, 1), (0.6, 1.0, 3.5, .7), (0.8, 1.0, 2.5, .4), None][i]
    if win:
        tail, head, tmax, al = win
        crescent(im, c, r, t0, t1, tail, head, tmax, SWORD, al)
        sparks(im, c, r, t0, t1, max(tail, .3), head, [3, 6, 5, 4, 3][i], SPARK_S, 10 + i, al)
    else:
        sparks(im, c, r, t0, t1, .75, 1.0, 5, SPARK_S, 99, .6, spread=(-2, 6))
    return im

# ---- 2) ogre axe slash: effect frame i is played together with the ogre attack frame 3+i (same anchor) ----
def axe_slash(i):
    im = Image.new('RGBA', (F, F), (0, 0, 0, 0))
    c, R, t0, t1 = arc_through((24, 14), (51, 16), (58, 47))
    r = R - 4
    win = [(0.15, 0.62, 7, 1), (0.1, 1.0, 10, 1), (0.4, 1.0, 7, 1), (0.65, 1.0, 5, .65), (0.85, 1.0, 3, .4), None][i]
    if win:
        tail, head, tmax, al = win
        crescent(im, c, r, t0, t1, tail, head, tmax, AXEC, al)
        sparks(im, c, r, t0, t1, max(tail, .3), head, [3, 7, 5, 4, 3][i], SPARK_A, 20 + i, al)
    # impact burst where the axe lands (frames 1..4), at the end of the arc
    ix, iy = 56, 47
    if 1 <= i <= 4:
        rnd = random.Random(5); L = [0, 8, 11, 12, 13][i]
        for k in range(10):
            a = rnd.uniform(-math.pi * 1.1, math.pi * .35); ln = rnd.uniform(.5, 1) * L
            a0 = ln * .45
            line(im, (ix + math.cos(a) * a0, iy + math.sin(a) * a0), (ix + math.cos(a) * ln, iy + math.sin(a) * ln),
                 SPARK_A[0] if i < 3 else SPARK_A[2], 1 if i < 4 else .5)
        if i == 1:
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)): put(im, ix + dx, iy + dy, C(255, 255, 255))
    return im

# ---- 3) blood splash (hit): origin on the victim's chest; sprays backwards (-x). Flip with the victim ----
B1, B2, B3, B4 = C(92, 8, 22), C(148, 16, 30), C(204, 34, 44), C(238, 88, 80)
def blood(i):
    im = Image.new('RGBA', (F, F), (0, 0, 0, 0)); ox, oy = 30, 32
    rnd = random.Random(11); GROUND = 58
    if i <= 2:   # central burst
        sc = [.7, 1.1, .55][i]
        for k in range(14):
            a = rnd.uniform(0, math.tau); ln = rnd.uniform(3, 9) * sc * (1.3 if math.cos(a) < 0 else .7)
            line(im, (ox + math.cos(a) * 2, oy + math.sin(a) * 2), (ox + math.cos(a) * ln, oy + math.sin(a) * ln), B2 if k % 2 else B3)
        rr = [3.4, 4.6, 2.4][i]
        for y in range(-6, 7):
            for x in range(-6, 7):
                if x * x + y * y <= rr * rr: put(im, ox + x, oy + y, B3 if x * x + y * y > (rr - 1.7) ** 2 else B4)
        put(im, ox - 1, oy - 1, C(255, 170, 160))
    for d in range(34):
        vx = -rnd.uniform(.6, 4.4); vy = rnd.uniform(-2.8, .6); big = rnd.random() < .6
        col = rnd.choice((B2, B3, B3, B4))
        if i == 0 and d > 14: continue
        def pos(t): return ox + vx * t, oy + vy * t + .55 * t * t
        tl = None
        for k in range(1, 400):
            if pos(k * .05)[1] >= GROUND: tl = k * .05; break
        t = i * 1.5
        if tl is not None and t >= tl:                    # landed: flat splat stays on the floor
            gx = pos(tl)[0]; put(im, gx, GROUND, B1); put(im, gx + 1, GROUND, B2)
            if big: put(im, gx - 1, GROUND, B2)
            continue
        x, y = pos(t); px, py = pos(max(t - 1.5, 0))
        if i >= 1 and i <= 3 and big: line(im, (px, py), (x, y), B2)
        put(im, x, y, col)
        if big and i <= 4:
            put(im, x + 1, y, col); put(im, x, y + 1, col); put(im, x + 1, y + 1, B2)
    return im

# ---- 4) spirit leaving the body: anchored on a body lying on the ground (head left, feet right) ----
GH_BODY = C(222, 240, 255); GH_HL = C(255, 255, 255); GH_EDGE = C(120, 176, 232); GH_DARK = C(52, 78, 140); GH_GLOW = C(150, 210, 245)
def ghost_in(lx, ly, ph):
    if (lx / 5.6) ** 2 + (ly / 6.0) ** 2 <= 1: return True
    if 2 <= ly <= 17:
        t = (ly - 2) / 15
        return abs(lx - 2.4 * math.sin(ph + ly * .45) * t) <= 5.2 * (1 - t) ** .75 + .4
    return False

def spirit(i):
    im = Image.new('RGBA', (F, F), (0, 0, 0, 0))
    cx = 24 + 3 * math.sin(i * 1.1 + .5); cy = [48, 41, 33, 25, 17, 10][i]
    s = [.6, .85, 1, 1, 1, .85][i]; al = [.45, .7, .92, .92, .6, .3][i]; ph = i * .9
    def inside(x, y): return ghost_in((x - cx) / s, (y - cy) / s, ph)
    for y in range(F):
        for x in range(F):
            if inside(x, y):
                edge = not (inside(x + 1, y) and inside(x - 1, y) and inside(x, y + 1) and inside(x, y - 1))
                lx, ly = (x - cx) / s, (y - cy) / s
                if edge: col, a = GH_EDGE, min(1, al + .3)
                elif lx < -1.5 and ly < 3: col, a = GH_HL, al
                else: col, a = GH_BODY, al
                put(im, x, y, col, a)
            elif any(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2))):
                put(im, x, y, GH_GLOW, al * .35)
    for (ex, ey) in ((-2.3, -1.4), (2.3, -1.4)):          # eyes + mouth
        for dy in (0, 1): put(im, cx + ex * s, cy + (ey + dy * .9) * s, GH_DARK, min(1, al + .2))
    put(im, cx, cy + 3.4 * s, GH_DARK, min(1, al + .2)); put(im, cx, cy + 4.3 * s, GH_DARK, min(1, al + .2))
    rnd = random.Random(7)
    for k in range(7):                                   # drifting sparkles
        sx = rnd.uniform(8, 44); sy0 = rnd.uniform(40, 52); sp = rnd.uniform(2.5, 6); sy = sy0 - sp * i - (i == 5) * 3
        if i == 0 or not (4 <= sy <= 56): continue
        a2 = al if i < 5 else .8
        put(im, sx, sy, GH_HL, a2)
        if (k + i) % 2 == 0 and i >= 2:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(im, sx + dx, sy + dy, GH_GLOW, a2 * .8)
    return im

EFFECTS = [('sword_slash', sword_slash, 12), ('axe_slash', axe_slash, 10), ('blood_splash', blood, 12), ('spirit', spirit, 6)]

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    sheet = Image.new('RGBA', (F * 6, F * len(EFFECTS)), (0, 0, 0, 0))
    atlas = {'frames': [], 'animations': {}, 'meta': {'image': 'vfx_spritesheet.png', 'frame_size': [64, 64], 'note':
             'sword_slash: play together with knight attack_sword frame 3+i; axe_slash: with ogre attack frame 3+i; '
             'blood_splash: on the victim (flip with it); spirit: on a body lying on the ground. Same anchor as the character frames.'}}
    for r, (name, fn, fps) in enumerate(EFFECTS):
        for i in range(6):
            sheet.alpha_composite(fn(i), (i * F, r * F))
            atlas['frames'].append({'filename': f'{name}_{i}', 'frame': {'x': i * F, 'y': r * F, 'w': F, 'h': F}})
        atlas['animations'][name] = {'frames': [f'{name}_{i}' for i in range(6)], 'fps': fps, 'loop': False}
    sheet.save(f'{out}/vfx_spritesheet.png'); json.dump(atlas, open(f'{out}/vfx_spritesheet.json', 'w'), indent=2)
    big = Image.new('RGBA', sheet.size, (58, 68, 92, 255)); big.alpha_composite(sheet)
    big.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(f'{out}/vfx_big.png')
    print('vfx ok')
