import math, json, os
from PIL import Image, ImageDraw

F = 64; GY = 58; CX = 30
def C(r, g, b): return (r, g, b, 255)
OUT = C(18, 18, 30)
PN = dict(shade=C(84, 94, 118), base=C(146, 158, 182), hl=C(214, 224, 240))
PF = dict(shade=C(44, 50, 70), base=C(88, 98, 120), hl=C(124, 134, 156))
RED = C(176, 38, 48); RED_D = C(112, 22, 34)
GOLD = C(238, 192, 72); LEATH = C(116, 74, 44); LEATH_D = C(74, 48, 30)
BLADE = C(214, 224, 238); BLADE_HL = C(252, 253, 255); BLADE_SH = C(150, 164, 186)
WOOD = C(134, 86, 48); WOOD_D = C(92, 58, 34)
TRAIL1 = C(240, 246, 255); TRAIL2 = C(140, 196, 255)

def rd(p): return (int(round(p[0])), int(round(p[1])))

def outline(im):
    px = im.load(); out = im.copy(); po = out.load()
    for y in range(F):
        for x in range(F):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < F and 0 <= ny < F and px[nx, ny][3] > 0:
                        po[x, y] = OUT; break
    return out

def layer(fn, ol=True):
    im = Image.new('RGBA', (F, F), (0, 0, 0, 0)); d = ImageDraw.Draw(im); fn(d)
    return outline(im) if ol else im

def seg(d, p, q, w, col):
    p = rd(p); q = rd(q)
    d.line([p, q], fill=col, width=w)
    h = w // 2
    for x, y in (p, q):
        d.ellipse([x - h, y - h, x - h + w - 1, y - h + w - 1], fill=col)

def limb(d, pts, w, pal):
    pairs = list(zip(pts, pts[1:]))
    for a, b in pairs: seg(d, (a[0] - 1, a[1]), (b[0] - 1, b[1]), w, pal['shade'])
    for a, b in pairs: seg(d, a, b, w - 1, pal['base'])
    for a, b in pairs: seg(d, (a[0] + 1, a[1]), (b[0] + 1, b[1]), 1, pal['hl'])

def ik(a, b, l1, l2, prefer):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay; d = max(math.hypot(dx, dy), 0.001)
    dm = l1 + l2 - 0.05
    if d > dm: bx = ax + dx * dm / d; by = ay + dy * dm / d; dx, dy = bx - ax, by - ay; d = dm
    aa = (l1 * l1 - l2 * l2 + d * d) / (2 * d); h = math.sqrt(max(l1 * l1 - aa * aa, 0))
    px, py = ax + dx * aa / d, ay + dy * aa / d
    ox, oy = -dy / d, dx / d
    c1 = (px + ox * h, py + oy * h); c2 = (px - ox * h, py - oy * h)
    if prefer == 'x': k = c1 if c1[0] >= c2[0] else c2
    elif prefer == 'xm': k = c1 if c1[0] <= c2[0] else c2
    elif prefer == 'ym': k = c1 if c1[1] <= c2[1] else c2
    else: k = c1 if c1[1] >= c2[1] else c2
    return k, (bx, by)

def leg(H, A, pal, boot, pref='x'):
    K, A = ik(H, A, 8, 9, pref)
    lift = GY - A[1]; t = -int(round(lift * 0.35))
    def f(d):
        limb(d, [H, K, A], 4, pal)
        x, y = rd(K); d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=pal['hl'])
        ax, ay = rd(A)
        d.polygon([(ax - 2, ay - 1), (ax + 1, ay - 1), (ax + 5, ay + 1 + t), (ax + 5, ay + 2 + t), (ax - 2, ay + 2)], fill=boot)
    return layer(f)

def arm(S, target, pal, boot, pref='y'):
    E, Hd = ik(S, target, 6.5, 6.5, pref)
    def f(d):
        limb(d, [S, E], 4, pal); limb(d, [E, Hd], 3, pal)
        x, y = rd(Hd); d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=boot)
        x, y = rd(S); d.ellipse([x - 3, y - 3, x + 3, y + 2], fill=pal['base'])
        d.line([(x - 1, y - 3), (x + 2, y - 3)], fill=pal['hl'])
        d.line([(x - 3, y), (x - 3, y + 2)], fill=pal['shade'])
    return layer(f), Hd

def torso(H, S, flap, cloth_ang=0, tabard=True):
    ux, uy = S[0] - H[0], S[1] - H[1]; l = math.hypot(ux, uy); ux /= l; uy /= l
    n = (-uy, ux)
    W = (H[0] + (S[0] - H[0]) * .35, H[1] + (S[1] - H[1]) * .35)
    def P(o, w): return (o[0] + n[0] * w, o[1] + n[1] * w)
    g = vec(cloth_ang); pv = (g[1], -g[0])
    hx, hy = rd(H)
    def Wp(v, u): return (int(round(hx + pv[0] * v + g[0] * u)), int(round(hy + pv[1] * v + g[1] * u)))
    def f(d):
        d.polygon([rd(P(S, 5)), rd(P(W, 3.5)), rd(P(H, 3.5)), rd(P(H, -3.5)), rd(P(W, -3.5)), rd(P(S, -5))], fill=PN['base'])
        d.line([rd(P(S, -5)), rd(P(W, -3.5)), rd(P(H, -3.5))], fill=PN['shade'], width=2)
        d.line([rd(P(S, 4)), rd(P(W, 2.5))], fill=PN['hl'], width=1)
        d.line([rd(P(S, -1)), rd(P(S, 4))], fill=GOLD, width=1)
        if tabard:
            d.polygon([Wp(-4, -2), Wp(4, -2), Wp(5 + flap, 7), Wp(-4 + flap, 7)], fill=RED)
            d.polygon([Wp(-4, -2), Wp(-2, -2), Wp(-2 + flap, 7), Wp(-4 + flap, 7)], fill=RED_D)
            d.line([Wp(-4 + flap, 7), Wp(5 + flap, 7)], fill=GOLD, width=1)
        d.line([Wp(-4, -2), Wp(4, -2)], fill=LEATH, width=2)
        d.point(Wp(2, -2), fill=GOLD)
    return layer(f)

def head(c, plume):
    x, y = rd(c)
    def pl(d):
        tx, ty = x + plume[0], y + plume[1]
        seg(d, (x - 2, y - 5), (tx, ty), 3, RED_D)
        seg(d, (x - 2, y - 6), (tx + 1, ty - 1), 2, RED)
    def hd(d):
        d.ellipse([x - 5, y - 6, x + 5, y + 4], fill=PN['shade'])
        d.ellipse([x - 4, y - 6, x + 5, y + 3], fill=PN['base'])
        d.line([(x - 1, y - 6), (x + 3, y - 6)], fill=PN['hl'])
        d.line([(x + 3, y - 4), (x + 5, y - 1)], fill=PN['hl'])
        d.rectangle([x + 1, y - 2, x + 5, y - 1], fill=OUT)
        d.rectangle([x + 1, y + 1, x + 5, y + 1], fill=PN['shade'])
        d.rectangle([x - 3, y + 4, x + 3, y + 6], fill=PN['shade'])
    return layer(pl), layer(hd)

def vec(a):
    r = math.radians(a); return (math.sin(r), math.cos(r))

def sword(h, a):
    dr = vec(a); n = (dr[1], -dr[0])
    def P(t, s=0): return (h[0] + dr[0] * t + n[0] * s, h[1] + dr[1] * t + n[1] * s)
    def f(d):
        seg(d, P(-3), P(1), 2, LEATH)
        d.line([rd(P(2, -3)), rd(P(2, 3))], fill=GOLD, width=2)
        d.line([rd(P(3)), rd(P(18))], fill=BLADE_SH, width=3)
        d.line([rd(P(3, .6)), rd(P(18, .6))], fill=BLADE, width=2)
        d.line([rd(P(3, .8)), rd(P(19, .8))], fill=BLADE_HL, width=1)
        seg(d, P(18), P(21), 1, BLADE)
        x, y = rd(P(-4)); d.point((x, y), fill=GOLD)
    return layer(f)

def axe(h, a):
    dr = vec(a); n = (dr[1], -dr[0])
    def P(t, s=0): return (h[0] + dr[0] * t + n[0] * s, h[1] + dr[1] * t + n[1] * s)
    def f(d):
        seg(d, P(-5), P(18), 2, WOOD)
        d.line([rd(P(-5, .5)), rd(P(18, .5))], fill=WOOD_D, width=1)
        d.polygon([rd(P(9, 0)), rd(P(7, -6)), rd(P(12, -8)), rd(P(17, -6)), rd(P(16, 0))], fill=BLADE)
        d.polygon([rd(P(10, 0)), rd(P(9, -3)), rd(P(15, -3)), rd(P(15, 0))], fill=BLADE_SH)
        d.polygon([rd(P(11, 1)), rd(P(12, 4)), rd(P(15, 1))], fill=PN['shade'])
        d.line([rd(P(7, -6)), rd(P(12, -8)), rd(P(17, -6))], fill=BLADE_HL, width=1)
        seg(d, P(17), P(21), 1, PN['base'])
    return layer(f)

def spear(h, a):
    """Two-handed spear (T21): long shaft, leaf-shaped steel head, small red tassel under it."""
    dr = vec(a); n = (dr[1], -dr[0])
    def P(t, s=0): return (h[0] + dr[0] * t + n[0] * s, h[1] + dr[1] * t + n[1] * s)
    def f(d):
        seg(d, P(-6), P(16), 2, WOOD)
        d.line([rd(P(-6, .5)), rd(P(16, .5))], fill=WOOD_D, width=1)
        d.polygon([rd(P(15, 0)), rd(P(17, -2.5)), rd(P(23, 0)), rd(P(17, 2.5))], fill=BLADE)
        d.line([rd(P(17, -1.2)), rd(P(22, 0))], fill=BLADE_HL, width=1)
        d.point(rd(P(15, 2)), fill=RED); d.point(rd(P(14, 3)), fill=RED); d.point(rd(P(13, 2.5)), fill=RED_D)
    return layer(f)


def trail(h, a0, a1, r):
    def f(d):
        for rr, col in ((r, TRAIL1), (r - 3, TRAIL2)):
            pts = []
            for k in range(9):
                a = a0 + (a1 - a0) * k / 8; v = vec(a)
                pts.append(rd((h[0] + v[0] * rr, h[1] + v[1] * rr)))
            d.line(pts, fill=col, width=1)
    return layer(f, ol=False)

LAST = {}

def tint(img, col, amt):
    px = img.load(); out = img.copy(); po = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a > 0 and (r, g, b, a) != OUT:
                po[x, y] = (int(r + (col[0] - r) * amt), int(g + (col[1] - g) * amt), int(b + (col[2] - b) * amt), 255)
    return out

def held(kind, pos, ang):
    """Layers of a weapon simply carried in the hand at `pos`, pointing along `ang` (sword / axe / bow / xbow)."""
    if kind == 'sword': return [sword(pos, ang)]
    if kind == 'axe': return [axe(pos, ang)]
    if kind == 'spear': return [spear(pos, ang)]
    if kind == 'bow':
        bl, st, _ = bow(pos, 90 - ang, 0)                      # limbs along the direction the blade used to point
        return [bl, st]
    xs, xst = xbow(pos, ang, False)
    return [xs, xst]


def render(p):
    if p['weapon'] in ('bow', 'xbow'): return render_ranged(p)
    hxw = CX + p.get('hx', 0); hy = 0
    for fx, fy in (p['footN'], p['footF']):
        hy = max(hy, fy - math.sqrt(max(16.8 ** 2 - (fx - hxw) ** 2, 0)))
    H = (hxw, hy + p.get('sink', 0))
    lean = math.radians(p.get('lean', 0)); L = 12 - p.get('tdy', 0)
    S = (H[0] + L * math.sin(lean), H[1] - L * math.cos(lean))
    if p.get('rot_head'):
        up = (math.sin(lean), -math.cos(lean)); nn = (math.cos(lean), math.sin(lean))
        cH = (S[0] + up[0] * 6 + nn[0] * 1.5, S[1] + up[1] * 6 + nn[1] * 1.5)
    else: cH = (S[0] + 1.5, S[1] - 6)
    ho = p.get('headoff', (0, 0)); cH = (cH[0] + ho[0], cH[1] + ho[1])
    img = Image.new('RGBA', (F, F), (0, 0, 0, 0))
    hN = (S[0] + p['handN'][0], S[1] + p['handN'][1])
    armN, hand = arm(S, hN, PN, LEATH_D)
    if p['weapon'] in ('axe', 'spear') and not p.get('wback'):                  # lying body (death): the free hand stays where it was
        k = 7 if p['weapon'] == 'spear' else 4                       # the free hand grips the shaft behind the first
        v = vec(p['wang']); hF = (hand[0] - v[0] * k, hand[1] - v[1] * k)
    else:
        hF = (S[0] + p['handF'][0], S[1] + p['handF'][1])
    armF, _ = arm(S, hF, PF, LEATH_D)
    plume, hd = head(cH, p.get('plume', (-7, -1)))
    if p.get('head_rot'):
        plume = plume.rotate(p['head_rot'], center=rd(cH), resample=Image.NEAREST); hd = hd.rotate(p['head_rot'], center=rd(cH), resample=Image.NEAREST)
    kn = p.get('knee', 'x')
    order = [armF, leg(H, p['footF'], PF, LEATH_D, kn), plume, torso(H, S, p.get('flap', 0), p.get('cloth_ang', 0), p.get('tabard', True)), hd,
             leg(H, p['footN'], PN, LEATH, kn), armN]
    kind = p.get('hold') or p['weapon']                    # 'hold': carry another weapon with a melee pose (T14)
    if p.get('wback'):
        for l in reversed(held(kind, p['wpos'], p['wang'])): order.insert(0, l)
    if p.get('trail'): order.append(trail(hand, *p['trail']))
    wp = p.get('wpos') or hand
    if not p.get('wback'): order.extend(held(kind, wp, p['wang']))
    for l in order: img.alpha_composite(l)
    LAST.update(S=S, H=H, hand=hand)
    if p.get('flash'): img = tint(img, (255, 255, 255, 255), p['flash'])
    sh = p.get('shift', 0)
    if sh:
        o = Image.new('RGBA', (F, F), (0, 0, 0, 0)); o.paste(img, (sh, 0)); img = o
    return img

# ---------------- ranged weapons ----------------
def arrow_layers(N, a, length, fly=False):
    dr = vec(a); n = (dr[1], -dr[0])
    def P(t, s=0): return (N[0] + dr[0] * t + n[0] * s, N[1] + dr[1] * t + n[1] * s)
    def shaft(d):
        d.line([rd(P(0)), rd(P(length))], fill=C(190, 140, 80), width=1)
        for t in (0, 1.5):
            d.point(rd(P(t, 1)), fill=RED); d.point(rd(P(t, -1)), fill=RED)
        if fly:
            d.line([rd(P(-3, 1.5)), rd(P(-8, 1.5))], fill=TRAIL1, width=1)
            d.line([rd(P(-4, -1.5)), rd(P(-10, -1.5))], fill=TRAIL2, width=1)
    def headf(d):
        d.polygon([rd(P(length - 1, 1)), rd(P(length + 3, 0)), rd(P(length - 1, -1))], fill=BLADE)
    return [layer(shaft, ol=False), layer(headf)]

def bow(hb, a, pull):
    dr = vec(a); u = (dr[1], -dr[0]); dd = pull * 0.25
    def P(t, s): return (hb[0] + dr[0] * t + u[0] * s, hb[1] + dr[1] * t + u[1] * s)
    tU = P(-3 - dd, 11); tD = P(-3 - dd, -11); cc = P(3 + dd, 0); N = P(-3 - pull, 0)
    def f(d):
        pts = []
        for k in range(15):
            t = k / 14
            pts.append(rd(((1 - t) ** 2 * tU[0] + 2 * (1 - t) * t * cc[0] + t * t * tD[0],
                           (1 - t) ** 2 * tU[1] + 2 * (1 - t) * t * cc[1] + t * t * tD[1])))
        d.line(pts, fill=WOOD, width=2)
        d.line([(x + 1, y) for x, y in pts], fill=C(170, 118, 66), width=1)
        seg(d, P(1, -2), P(1, 2), 3, LEATH)
    def st(d):
        d.line([rd(tU), rd(N), rd(tD)], fill=C(226, 222, 206), width=1)
    return layer(f), layer(st, ol=False), N

def xbow(R, a, loaded):
    dr = vec(a); n = (dr[1], -dr[0])
    def P(t, s=0): return (R[0] + dr[0] * t + n[0] * s, R[1] + dr[1] * t + n[1] * s)
    tt = 14 if loaded else 18
    def f(d):
        seg(d, P(-2), P(2), 4, WOOD_D)
        seg(d, P(0), P(18), 3, WOOD)
        d.line([rd(P(0, 1)), rd(P(17, 1))], fill=C(172, 118, 68), width=1)
        seg(d, P(7, -2), P(7, -4), 2, LEATH)
        d.line([rd(P(tt, 7)), rd(P(17, 3)), rd(P(17.5, 0)), rd(P(17, -3)), rd(P(tt, -7))], fill=PF['base'], width=2)
        d.line([rd(P(tt, 7)), rd(P(17.5, 0))], fill=PF['hl'], width=1)
    def st(d):
        col = C(226, 222, 206)
        if loaded: d.line([rd(P(tt, 7)), rd(P(5, 0)), rd(P(tt, -7))], fill=col, width=1)
        else: d.line([rd(P(tt, 7)), rd(P(tt, -7))], fill=col, width=1)
    return layer(f), layer(st, ol=False)

def render_ranged(p):
    hxw = CX + p.get('hx', 0); hy = 0
    for fx, fy in (p['footN'], p['footF']):
        hy = max(hy, fy - math.sqrt(max(16.8 ** 2 - (fx - hxw) ** 2, 0)))
    H = (hxw, hy + p.get('sink', 0))
    lean = math.radians(p.get('lean', 0)); L = 12 - p.get('tdy', 0)
    S = (H[0] + L * math.sin(lean), H[1] - L * math.cos(lean))
    cH = (S[0] + 1.5, S[1] - 6)
    img = Image.new('RGBA', (F, F), (0, 0, 0, 0))
    plume, hd = head(cH, p.get('plume', (-7, -1)))
    legF = leg(H, p['footF'], PF, LEATH_D); legN = leg(H, p['footN'], PN, LEATH); tors = torso(H, S, p.get('flap', 0))
    if p['weapon'] == 'bow':
        armF, hb = arm(S, (S[0] + p['bowhand'][0], S[1] + p['bowhand'][1]), PF, LEATH_D)
        dr = vec(p['aim']); hp = 3 + p['hand_pull']
        armN, _ = arm(S, (hb[0] - dr[0] * hp, hb[1] - dr[1] * hp), PN, LEATH, p.get('elbow', 'y'))
        bl, stg, N = bow(hb, p['aim'], p['pull'])
        parts = [armF, legF, plume, tors, hd, legN, armN, bl, stg]
        if p.get('arrow') == 'nock': parts += arrow_layers(N, p['aim'], 19)
        elif p.get('arrow') == 'fly': parts += arrow_layers((hb[0] + dr[0] * 3, hb[1] + dr[1] * 3), p['aim'], 17, fly=True)
    else:
        R = (S[0] + p['R'][0], S[1] + p['R'][1]); dr = vec(p['ang']); n = (dr[1], -dr[0])
        hN = (R[0] + dr[0] * 7, R[1] + dr[1] * 7); hF = (R[0] + dr[0] * 13, R[1] + dr[1] * 13)
        armF, _ = arm(S, hF, PF, LEATH_D); armN, _ = arm(S, hN, PN, LEATH)
        xs, xst = xbow(R, p['ang'], p['loaded'])
        parts = [armF, legF, plume, tors, hd, legN, xs, xst]
        if p.get('bolt') == 'load':
            parts += arrow_layers((R[0] + dr[0] * 4 + n[0] * 2, R[1] + dr[1] * 4 + n[1] * 2), p['ang'], 15)
        elif p.get('bolt') == 'fly':
            parts += arrow_layers((R[0] + dr[0] * 12 + n[0] * 2, R[1] + dr[1] * 12 + n[1] * 2), p['ang'], 15, fly=True)
        parts.append(armN)
    for l in parts: img.alpha_composite(l)
    sh = p.get('shift', 0)
    if sh:
        o = Image.new('RGBA', (F, F), (0, 0, 0, 0)); o.paste(img, (sh, 0)); img = o
    return img

