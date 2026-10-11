import sys, os, json
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1] if len(sys.argv) > 1 else './out'        # folder with the 3 sheets
SCN = sys.argv[2] if len(sys.argv) > 2 else './scenery'     # folder with scenery pngs
OUT = sys.argv[3] if len(sys.argv) > 3 else SRC
F = 64; AX = 30                                              # frame size, hip anchor x inside the frame

def sheet(name): return Image.open(f'{SRC}/{name}_spritesheet.png').convert('RGBA')
def atlas(name): return json.load(open(f'{SRC}/{name}_spritesheet.json'))
SHEETS = {k: sheet(k) for k in ('knight', 'ogre', 'vfx')}
ATLAS = {k: atlas(k) for k in SHEETS}
ROWS = {k: {n: r for r, n in enumerate(ATLAS[k]['animations'])} for k in SHEETS}
FPS = {k: {n: a['fps'] for n, a in ATLAS[k]['animations'].items()} for k in SHEETS}

def frame(who, anim, i, flip=False):
    im = SHEETS[who].crop((i * F, ROWS[who][anim] * F, (i + 1) * F, (ROWS[who][anim] + 1) * F))
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im

# ---------------------------------------------------------------- scene engine
W, H, G, TOP = 480, 186, 148, 145
SKY = (122, 178, 224, 255)
street = Image.open(f'{SCN}/street_tile.png').convert('RGBA')
props = {n: Image.open(f'{SCN}/{n}.png').convert('RGBA') for n in ('medieval_house', 'tree', 'well')}

def background():
    bg = Image.new('RGBA', (W, H), SKY)
    for x in range(0, W, 64): bg.alpha_composite(street, (x, TOP))
    for n, x in (('medieval_house', 6), ('tree', 292), ('well', 414)):
        im = props[n]; bg.alpha_composite(im, (x, G - (im.height - 2)))
    return bg
BG = background()

def state(segs, t):
    s = segs[0]
    for sg in segs:
        if sg['t0'] <= t: s = sg
    local = t - s['t0']; n = int(local * s['fps']) if 'fps' in s else int(local * FPS[s['who']][s['anim']])
    idx = n % 6 if s.get('loop') else min(n, 5)
    x = s['x0']
    if 'x1' in s: x = s['x0'] + (s['x1'] - s['x0']) * min(local / s['dur'], 1)
    return s, idx, x

def place(img, who, anim, idx, x, flip):
    fr = frame(who, anim, idx, flip); left = int(round(x)) - ((F - 1 - AX) if flip else AX)
    img.alpha_composite(fr, (left, G - 60))

def render_scene(actors, fx, T, fps=20):
    out = []
    for n in range(int(T * fps)):
        t = n / fps; img = BG.copy(); st = {}
        for name, a in actors.items():
            s, idx, x = state(a['segs'], t); st[name] = (s, idx, x)
            place(img, a['who'], s['anim'], idx, x, a['flip'])
        for e in fx:                                         # effects, anchored on the actor (same flip)
            f = FPS['vfx'][e['name']]; k = int((t - e['t0']) * f)
            if t >= e['t0'] and 0 <= k < 6:
                s, idx, x = st[e['on']]; flip = actors[e['on']]['flip']
                place(img, 'vfx', e['name'], k, x, flip)
        out.append(img)
    return out

def save_gif(frames, path, fps=20, scale=2):
    big = [f.resize((f.width * scale, f.height * scale), Image.NEAREST).convert('RGB') for f in frames]
    # one shared palette keeps colors stable between frames
    step = max(1, len(big) // 8); mont = Image.new('RGB', (big[0].width, big[0].height * 8))
    for i in range(8): mont.paste(big[min(i * step, len(big) - 1)], (0, i * big[0].height))
    pal = mont.quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [b.quantize(palette=pal, dither=Image.NONE) for b in big]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=False)
    print(path, os.path.getsize(path) // 1024, 'KB', len(q), 'frames')

KX, OX0, OX1 = 190, 322, 228
def K(t0, anim, **kw): return dict(t0=t0, who='knight', anim=anim, x0=kw.pop('x0', KX), **kw)
def O(t0, anim, **kw): return dict(t0=t0, who='ogre', anim=anim, x0=kw.pop('x0', OX1), **kw)

# ------------------------------------------------ demo 1: the knight wins
def battle():
    knight = dict(who='knight', flip=False, segs=[
        K(0, 'idle', loop=True), K(3.25, 'hurt'), K(3.85, 'idle', loop=True),
        K(4.3, 'attack_sword', x1=196, dur=.3), K(4.8, 'idle', x0=196, loop=True),
        K(5.25, 'attack_sword', x0=196, x1=200, dur=.3), K(5.75, 'idle', x0=200, loop=True)])
    ogre = dict(who='ogre', flip=True, segs=[
        O(0, 'walk', x0=OX0, x1=OX1, dur=2.85, loop=True), O(2.85, 'attack'), O(3.5, 'idle', loop=True),
        O(4.633, 'hurt'), O(5.233, 'idle', loop=True), O(5.583, 'death')])
    fx = [dict(t0=3.15, name='axe_slash', on='ogre'), dict(t0=3.25, name='blood_splash', on='knight'),
          dict(t0=4.55, name='sword_slash', on='knight'), dict(t0=4.633, name='blood_splash', on='ogre'),
          dict(t0=5.5, name='sword_slash', on='knight'), dict(t0=5.583, name='blood_splash', on='ogre'),
          dict(t0=6.03, name='spirit', on='ogre')]
    return render_scene(dict(knight=knight, ogre=ogre), fx, 8.0)

# ------------------------------------------------ demo 2: the ogre wins
def knight_dies():
    knight = dict(who='knight', flip=False, segs=[K(0, 'idle', loop=True), K(3.25, 'hurt'), K(3.85, 'idle', loop=True), K(4.6, 'death')])
    ogre = dict(who='ogre', flip=True, segs=[
        O(0, 'walk', x0=OX0, x1=OX1, dur=2.85, loop=True), O(2.85, 'attack'), O(3.5, 'idle', loop=True),
        O(4.2, 'attack'), O(4.85, 'idle', loop=True)])
    fx = [dict(t0=3.15, name='axe_slash', on='ogre'), dict(t0=3.25, name='blood_splash', on='knight'),
          dict(t0=4.5, name='axe_slash', on='ogre'), dict(t0=4.6, name='blood_splash', on='knight'),
          dict(t0=5.05, name='spirit', on='knight')]
    return render_scene(dict(knight=knight, ogre=ogre), fx, 7.5)

# ------------------------------------------------ overview grid of every animation
def overview():
    cells = [('knight', n) for n in ATLAS['knight']['animations']] + [('ogre', n) for n in ATLAS['ogre']['animations']] + \
            [('vfx', n) for n in ATLAS['vfx']['animations']]
    cols = 6; rows = (len(cells) + cols - 1) // cols; Z = 2; CW = F * Z
    try: font = ImageFont.load_default()
    except Exception: font = None
    fps = 24; frames = []
    for n in range(72):
        t = n / fps; im = Image.new('RGB', (cols * CW, rows * CW), (44, 52, 72))
        for k, (who, anim) in enumerate(cells):
            cx, cy = (k % cols) * CW, (k // cols) * CW
            idx = int(t * FPS[who][anim]) % 6
            fr = frame(who, anim, idx).resize((CW, CW), Image.NEAREST)
            cell = Image.new('RGBA', (CW, CW), (52, 62, 86, 255)); cell.alpha_composite(fr)
            im.paste(cell.convert('RGB'), (cx, cy))
            d = ImageDraw.Draw(im); label = f'{who}: {anim}'
            d.text((cx + 5, cy + 4), label, fill=(0, 0, 0), font=font); d.text((cx + 4, cy + 3), label, fill=(255, 255, 255), font=font)
        frames.append(im)
    pal = frames[0].quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    mont = Image.new('RGB', (frames[0].width, frames[0].height * 4))
    for i in range(4): mont.paste(frames[i * 9], (0, i * frames[0].height))
    pal = mont.quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    p = f'{OUT}/overview.gif'; q[0].save(p, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=False)
    print(p, os.path.getsize(p) // 1024, 'KB')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fr = battle(); save_gif(fr, f'{OUT}/demo_battle.gif'); fr[int(3.3 * 20)].resize((W * 2, H * 2), Image.NEAREST).save(f'{OUT}/_s1.png')
    fr[int(4.7 * 20)].resize((W * 2, H * 2), Image.NEAREST).save(f'{OUT}/_s2.png'); fr[int(6.4 * 20)].resize((W * 2, H * 2), Image.NEAREST).save(f'{OUT}/_s3.png')
    save_gif(knight_dies(), f'{OUT}/demo_knight_dies.gif')
    overview()
