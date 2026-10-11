import sys, math, json, os
from PIL import Image, ImageDraw
from sprite_rig import *

SK = dict(shade=C(38, 82, 46), base=C(84, 140, 64), hl=C(150, 202, 100))      # near-side skin
SKF = dict(shade=C(26, 56, 36), base=C(58, 100, 50), hl=C(86, 130, 64))       # far-side skin
FUR = C(146, 102, 62); FUR_D = C(100, 66, 40); LTH = C(116, 74, 44); LTH_D = C(70, 44, 28)
TUSK = C(244, 236, 204); EYE = C(246, 214, 60); MOUTH = C(24, 12, 16)
I1 = C(66, 70, 88); I2 = C(110, 116, 134); I3 = C(192, 198, 214)
REACH = 15.6          # leg bones 8 + 8

def o_leg(H, A, pal, pref='x'):
    K, A = ik(H, A, 8, 8, pref)
    t = -int(round((GY - A[1]) * 0.35))
    def f(d):
        limb(d, [H, K, A], 6, pal)
        x, y = rd(K); d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=pal['base'])
        ax, ay = rd(A)
        d.rectangle([ax - 3, ay - 3, ax + 1, ay - 1], fill=FUR if pal is SK else FUR_D)
        d.polygon([(ax - 3, ay), (ax + 1, ay), (ax + 7, ay + 1 + t), (ax + 7, ay + 2 + t), (ax - 3, ay + 2)], fill=pal['base'])
        d.line([(ax + 4, ay + 2 + t), (ax + 7, ay + 2 + t)], fill=pal['shade'])
        d.point((ax + 7, ay + 1 + t), fill=TUSK)
    return layer(f)

def o_arm(S, target, pal, pref='y'):
    E, Hd = ik(S, target, 6.5, 6.5, pref)
    def f(d):
        limb(d, [S, E], 6, pal); limb(d, [E, Hd], 5, pal)
        c0 = (E[0] + (Hd[0] - E[0]) * .5, E[1] + (Hd[1] - E[1]) * .5); c1 = (E[0] + (Hd[0] - E[0]) * .8, E[1] + (Hd[1] - E[1]) * .8)
        seg(d, c0, c1, 5, LTH_D)
        x, y = rd(Hd); d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=pal['base'])
        x, y = rd(S); d.ellipse([x - 4, y - 4, x + 4, y + 3], fill=pal['base']); d.line([(x - 1, y - 4), (x + 3, y - 4)], fill=pal['hl'])
    return layer(f), Hd

def o_torso(H, S, flap=0, cloth_ang=0):
    ux, uy = S[0] - H[0], S[1] - H[1]; l = math.hypot(ux, uy); ux /= l; uy /= l
    n = (-uy, ux)
    W = (H[0] + (S[0] - H[0]) * .4, H[1] + (S[1] - H[1]) * .4)
    def P(o, w): return (o[0] + n[0] * w, o[1] + n[1] * w)
    g = vec(cloth_ang); pv = (g[1], -g[0]); hx, hy = rd(H)
    def Wp(v, u): return (int(round(hx + pv[0] * v + g[0] * u)), int(round(hy + pv[1] * v + g[1] * u)))
    def f(d):
        x, y = rd((S[0] - ux * 1 + n[0] * -4, S[1] - uy * 1 + n[1] * -4)); d.ellipse([x - 5, y - 5, x + 4, y + 4], fill=SK['base'])
        d.polygon([rd(P(S, 6)), rd(P(W, 8)), rd(P(H, 6)), rd(P(H, -5)), rd(P(W, -6)), rd(P(S, -6))], fill=SK['base'])
        d.line([rd(P(S, -6)), rd(P(W, -6)), rd(P(H, -5))], fill=SK['shade'], width=3)
        d.line([rd(P(S, 5)), rd(P(W, 7)), rd(P(H, 5))], fill=SK['hl'], width=1)
        d.line([rd(P(S, 4)), rd(P(H, -3))], fill=LTH, width=2)
        d.point(rd(P(W, 2)), fill=GOLD)
        d.line([Wp(-5, -1), Wp(6, -1)], fill=LTH_D, width=3); d.point(Wp(3, -1), fill=GOLD)
        d.polygon([Wp(-5, 0), Wp(6, 0), Wp(6 + flap, 9), Wp(4 + flap, 7), Wp(2 + flap, 10), Wp(flap, 7), Wp(-2 + flap, 10), Wp(-4 + flap, 8), Wp(-5 + flap, 9)], fill=FUR)
        d.polygon([Wp(-5, 0), Wp(-2, 0), Wp(-2 + flap, 10), Wp(-5 + flap, 9)], fill=FUR_D)
    return layer(f)

def o_head(c, eye='open'):
    x, y = rd(c)
    def f(d):
        d.polygon([(x - 4, y - 1), (x - 9, y - 4), (x - 5, y + 2)], fill=SK['base'])
        d.ellipse([x - 5, y - 6, x + 5, y + 3], fill=SK['shade']); d.ellipse([x - 4, y - 6, x + 5, y + 3], fill=SK['base'])
        d.line([(x - 1, y - 6), (x + 3, y - 6)], fill=SK['hl'])
        d.line([(x, y - 3), (x + 5, y - 2)], fill=SK['shade'])
        d.rectangle([x + 5, y - 1, x + 6, y + 1], fill=SK['base']); d.point((x + 6, y + 1), fill=SK['shade'])
        d.polygon([(x - 3, y + 2), (x + 6, y + 2), (x + 7, y + 6), (x - 2, y + 6)], fill=SK['base'])
        d.line([(x - 3, y + 6), (x + 7, y + 6)], fill=SK['shade'])
        d.line([(x - 1, y + 3), (x + 6, y + 3)], fill=MOUTH)
        d.line([(x + 2, y + 1), (x + 2, y + 3)], fill=TUSK); d.line([(x + 5, y + 1), (x + 5, y + 3)], fill=TUSK)
        if eye == 'open':
            d.line([(x + 2, y - 1), (x + 3, y - 1)], fill=EYE); d.point((x + 3, y), fill=MOUTH)
        else:
            d.line([(x + 2, y - 1), (x + 4, y - 1)], fill=MOUTH)
        d.rectangle([x - 3, y - 8, x - 1, y - 6], fill=LTH_D); d.point((x, y - 8), fill=LTH_D); d.point((x - 4, y - 7), fill=LTH_D)
    return layer(f)

def o_axe(h, a):
    dr = vec(a); n = (dr[1], -dr[0])
    def P(t, s=0): return (h[0] + dr[0] * t + n[0] * s, h[1] + dr[1] * t + n[1] * s)
    def f(d):
        seg(d, P(-6), P(22), 3, WOOD)
        d.line([rd(P(-6, .8)), rd(P(22, .8))], fill=WOOD_D, width=1)
        seg(d, P(-4), P(2), 3, LTH_D)
        d.polygon([rd(P(10, 0)), rd(P(8, -8)), rd(P(14, -11)), rd(P(20, -8)), rd(P(19, 0))], fill=I2)
        d.polygon([rd(P(11, 0)), rd(P(10, -4)), rd(P(18, -4)), rd(P(18, 0))], fill=I1)
        d.polygon([rd(P(12, 1)), rd(P(14, 6)), rd(P(17, 1))], fill=I1)
        d.line([rd(P(8, -8)), rd(P(14, -11)), rd(P(20, -8))], fill=I3, width=1)
        d.point(rd(P(13, -6)), fill=I3); d.point(rd(P(16, -7)), fill=I1)
        seg(d, P(20), P(25), 1, I2)
    return layer(f)

def o_render(p):
    hxw = CX + p.get('hx', 0); hy = 0
    for fx, fy in (p['footN'], p['footF']):
        hy = max(hy, fy - math.sqrt(max(REACH ** 2 - (fx - hxw) ** 2, 0)))
    H = (hxw, hy + p.get('sink', 0))
    lean = math.radians(p.get('lean', 18)); L = 14 - p.get('tdy', 0)
    up = (math.sin(lean), -math.cos(lean)); nn = (math.cos(lean), math.sin(lean))
    S = (H[0] + L * up[0], H[1] + L * up[1])
    ho = p.get('headoff', (0, 0))
    cH = (S[0] + up[0] * 6 + nn[0] * 3.5 + ho[0], S[1] + up[1] * 6 + nn[1] * 3.5 + ho[1])
    img = Image.new('RGBA', (F, F), (0, 0, 0, 0))
    armN, hand = o_arm(S, (S[0] + p['handN'][0], S[1] + p['handN'][1]), SK, p.get('elbow', 'y'))
    dr = vec(p['wang'])
    hF = (hand[0] - dr[0] * 5, hand[1] - dr[1] * 5) if p.get('two_hand') else (S[0] + p['handF'][0], S[1] + p['handF'][1])
    armF, _ = o_arm(S, hF, SKF, 'y')
    kn = p.get('knee', 'x')
    legF = o_leg(H, p['footF'], SKF, kn); legN = o_leg(H, p['footN'], SK, kn)
    head = o_head(cH, p.get('eye', 'open'))
    if p.get('head_rot'): head = head.rotate(p['head_rot'], center=rd(cH), resample=Image.NEAREST)
    tors = o_torso(H, S, p.get('flap', 0), p.get('cloth_ang', 0))
    axe_l = o_axe(p.get('wpos') or hand, p['wang'])
    wo = p.get('worder', 'front')
    if wo == 'back': order = [axe_l, armF, legF, tors, head, legN, armN]
    elif wo == 'mid': order = [armF, legF, tors, axe_l, head, legN, armN]
    else: order = [armF, legF, tors, head, legN, armN, axe_l]
    for l in order: img.alpha_composite(l)
    LAST.update(S=S, H=H, hand=hand)
    if p.get('flash'): img = tint(img, (255, 255, 255, 255), p['flash'])
    sh = p.get('shift', 0)
    if sh:
        o = Image.new('RGBA', (F, F), (0, 0, 0, 0)); o.paste(img, (sh, 0)); img = o
    return img

# ---------------- poses ----------------
def o_idle(i):
    br = [0, 0, 1, 1, 1, 0][i]
    return dict(footN=(CX + 5, GY), footF=(CX - 5, GY), sink=1, lean=18, tdy=br, handN=(4, 2), wang=228,
                handF=[(3, 12), (3, 12), (4, 11), (4, 11), (3, 11), (3, 12)][i], worder='mid')

def o_walk(i):
    p = math.radians(i * 60 + 30); c, s = math.cos(p), math.sin(p)
    def foot(ph): return (CX + 5 * math.cos(ph), GY - 3 * max(0, -math.sin(ph)))
    return dict(footN=foot(p), footF=foot(p + math.pi), sink=.6 + 1.6 * abs(c), lean=20,
                handN=(4, 2 + .7 * s), wang=228 + 3 * c, handF=(3 + 5 * c, 11 - abs(s)), worder='mid', flap=-1,
                headoff=(0, .5 * s))

def o_attack(i):
    return dict(hx=[0, -3, -3, 1, 2, 1][i], footN=(CX + 7, GY), footF=(CX - 6, GY),
                sink=[1, 1.5, 1, 2.5, 4, 2][i], lean=[18, 6, 2, 24, 40, 22][i],
                handN=[(4, 2), (-3, -9), (0, -7), (8, -6), (10, 6), (6, 1)][i],
                wang=[228, 205, 195, 140, 68, 170][i], two_hand=i >= 1,
                worder='mid' if i == 0 else 'front', handF=(3, 11),
                flap=[0, -1, 0, -2, -4, -1][i], headoff=[(0, 0), (-1, 0), (-1, 0), (1, 0), (2, 1), (0, 0)][i],
                shift=[0, 0, 0, -2, -4, -2][i])

def o_hurt(i):
    return dict(hx=[-1, -4, -4, -3, -1, 0][i], footN=(CX + 5, GY), footF=(CX - 5, GY),
                sink=[1, 2, 2.5, 2, 1.5, 1][i], lean=[10, -2, 2, 10, 15, 18][i],
                handN=[(4, 2), (1, -3), (2, -2), (4, 1), (4, 2), (4, 2)][i],
                wang=[228, 238, 236, 231, 229, 228][i], worder='mid',
                handF=[(3, 12), (-6, 6), (-7, 4), (-4, 8), (2, 11), (3, 12)][i],
                headoff=[(-1, 0), (-3, -1), (-3, 0), (-2, 0), (0, 0), (0, 0)][i],
                eye=['open', 'shut', 'shut', 'shut', 'open', 'open'][i],
                flash=[.85, .3, 0, 0, 0, 0][i], flap=[0, 1, 1, 0, 0, 0][i])

def o_death(i):
    lying = i >= 3
    return dict(hx=[-1, -4, -2, 4, 4, 4][i],
                footN=[(CX + 5, GY), (CX + 6, GY), (CX + 12, GY), (CX + 19, GY), (CX + 19, GY), (CX + 19, GY)][i],
                footF=[(CX - 5, GY), (CX - 6, GY), (CX + 8, GY - 3), (CX + 16, GY), (CX + 16, GY), (CX + 16, GY)][i],
                sink=[1, 3, 0.5, .5, 0, 0][i], lean=[8, -18, -50, -86, -88, -88][i],
                handN=[(4, 2), (1, -3), (-4, -6), (-9, 3), (-9, 4), (-9, 4)][i],
                handF=[(3, 12), (-6, 3), (-8, -2), (-6, -5), (-7, -4), (-7, -4)][i],
                wang=[228, 238, 120, 250, 270, 270][i], wpos=[None, None, (36, 34), (54, 55), (54, 55), (54, 55)][i],
                worder='back' if lying else ('mid' if i == 0 else 'front'),
                head_rot=90 if lying else 0, knee='ym' if lying else 'x',
                cloth_ang=[0, 0, 70, 88, 88, 88][i], eye='open' if i == 0 else 'shut',
                flash=[.85, 0, 0, 0, 0, 0][i], shift=[0, 3, 0, 0, 0, 0][i])

ANIMS = [('idle', o_idle, 6), ('walk', o_walk, 10), ('attack', o_attack, 10), ('hurt', o_hurt, 10), ('death', o_death, 8)]
NOLOOP = ('attack', 'hurt', 'death')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    sheet = Image.new('RGBA', (F * 6, F * len(ANIMS)), (0, 0, 0, 0))
    atlas = {'frames': [], 'animations': {}, 'meta': {'image': 'ogre_spritesheet.png', 'frame_size': [64, 64], 'facing': 'right'}}
    for r, (name, fn, fps) in enumerate(ANIMS):
        for i in range(6):
            sheet.alpha_composite(o_render(fn(i)), (i * F, r * F))
            atlas['frames'].append({'filename': f'{name}_{i}', 'frame': {'x': i * F, 'y': r * F, 'w': F, 'h': F}})
        atlas['animations'][name] = {'frames': [f'{name}_{i}' for i in range(6)], 'fps': fps, 'loop': not name.startswith(NOLOOP)}
    sheet.save(f'{out}/ogre_spritesheet.png')
    json.dump(atlas, open(f'{out}/ogre_spritesheet.json', 'w'), indent=2)
    big = Image.new('RGBA', sheet.size, (58, 68, 92, 255)); big.alpha_composite(sheet)
    big.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(f'{out}/ogre_big.png')
    print('ogre ok', sheet.size)
