"""Art direction proposals (static images, NOT used by the game): shorter characters + a darker / slightly more realistic
pixel-art look. Re-uses the current sheets / props, re-proportions the characters and grades everything per proposal.

    python art_tools/proposals_gen.py [out_dir]       (default: out/art_proposals)
"""
import sys, os, json, math, random, colorsys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'assets')
W, H = 480, 270
GROUND_Y = 217
SCALE = 3
OUT_OLD = (18, 18, 30)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


# ------------------------------------------------------------------------------------------------ loading
_sheets = {}


def sheet(name):
    if name not in _sheets:
        im = Image.open(os.path.join(ASSETS, f'{name}_spritesheet.png')).convert('RGBA')
        meta = json.load(open(os.path.join(ASSETS, f'{name}_spritesheet.json')))
        _sheets[name] = (im, list(meta['animations']), meta['meta'].get('frame_size', [64, 64])[0], meta['meta'])
    return _sheets[name]


def frame(name, anim, i=0):
    im, rows, fs, meta = sheet(name)
    r = rows.index(anim)
    return im.crop((i * fs, r * fs, (i + 1) * fs, (r + 1) * fs))


def hip_col(name, flip):
    _, _, fs, meta = sheet(name)
    ax = meta.get('anchor_x', 30)
    return fs - 1 - ax if flip else ax


def prop(name): return Image.open(os.path.join(ASSETS, name + '.png')).convert('RGBA')


# ------------------------------------------------------------------------------------------------ colour grading
def make_grade(sat=1.0, val=1.0, contrast=1.0, tint=(1, 1, 1), lift=(0, 0, 0), gamma=1.0):
    cache = {}

    def g(c):
        if c in cache: return cache[c]
        r, gg, b = c[0] / 255.0, c[1] / 255.0, c[2] / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, gg, b)
        s = min(1.0, s * sat); v = ((v - 0.5) * contrast + 0.5) * val
        v = max(0.0, min(1.0, v)) ** gamma
        r, gg, b = colorsys.hsv_to_rgb(h, s, v)
        out = tuple(max(0, min(255, int(round((ch * t) * 255 + l)))) for ch, t, l in zip((r, gg, b), tint, lift))
        cache[c] = out
        return out
    return g


def grade_image(im, g, keep_alpha=True):
    im = im.copy(); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3] == 0: continue
            px[x, y] = g(p[:3]) + (p[3],)
    return im


def outline(im, col):
    src = im.load(); out = im.copy(); po = out.load()
    for y in range(im.height):
        for x in range(im.width):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < im.width and 0 <= ny < im.height and src[nx, ny][3] > 0:
                        po[x, y] = col + (255,); break
    return out


def strip_outline(im):
    im = im.copy(); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3] and p[:3] == OUT_OLD: px[x, y] = (0, 0, 0, 0)
    return im


def shorten(im, f):
    """Lower the character: crop the body (no outline), squash it vertically to f of its height keeping the feet where
    they were, and let the caller re-outline."""
    im = strip_outline(im)
    bb = im.getbbox()
    if bb is None or f >= 0.999: return im
    crop = im.crop(bb); nh = max(1, int(round(crop.height * f)))
    crop = crop.resize((crop.width, nh), Image.NEAREST)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(crop, (bb[0], bb[3] - nh), crop)
    return out


def lit(im, light, rim_col, rim_amt, shade_amt, out_col, top_boost=0.0):
    """Extra depth: a rim light on the side facing the light, a darker lower edge, and a top-to-feet gradient. Works on the
    body (outline excluded), then the outline is added again."""
    px = im.load(); res = im.copy(); pr = res.load()
    bb = im.getbbox()
    if bb is None: return res
    h = max(1, bb[3] - bb[1])
    dx = {'l': -1, 'r': 1, 't': 0}[light]; dy = -1 if light == 't' else 0
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3] == 0: continue
            r, g, b = p[:3]
            k = 1.0 + top_boost * (1.0 - (y - bb[1]) / h) - 0.12 * ((y - bb[1]) / h)       # lighter head, darker legs
            r, g, b = r * k, g * k, b * k
            n = (x * 7 + y * 13) % 11                                                        # grain: grime and worn cloth / metal
            if n == 0: r, g, b = r * 0.82, g * 0.82, b * 0.82
            elif (x * 5 + y * 3) % 17 == 0: r, g, b = r * 1.1 + 4, g * 1.1 + 4, b * 1.1 + 4
            def empty(ax, ay): return not (0 <= ax < im.width and 0 <= ay < im.height) or px[ax, ay][3] == 0
            if empty(x + dx, y + dy):                                                        # edge towards the light
                r, g, b = (r + (rim_col[0] - r) * rim_amt, g + (rim_col[1] - g) * rim_amt, b + (rim_col[2] - b) * rim_amt)
            if empty(x, y + 1) and light != 't':                                             # underside in shadow
                r, g, b = r * (1 - shade_amt), g * (1 - shade_amt), b * (1 - shade_amt)
            pr[x, y] = (int(max(0, min(255, r))), int(max(0, min(255, g))), int(max(0, min(255, b))), 255)
    return outline(res, out_col)


# ------------------------------------------------------------------------------------------------ scene
class Scene:
    def __init__(self, seed=1):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); self.px = self.im.load(); self.rnd = random.Random(seed)
        self.d = ImageDraw.Draw(self.im)

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H: self.px[x, y] = tuple(c[:3]) + (255,)

    def lerp(self, a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))

    def vgrad(self, y0, y1, c0, c1, levels=8):
        for y in range(y0, y1):
            t = (y - y0) / max(1, y1 - y0 - 1) * levels; k = int(t); fr = t - k
            for x in range(W):
                kk = min(levels, k + (1 if fr > (BAYER[y % 4][x % 4] + .5) / 16 else 0))
                self.put(x, y, self.lerp(c0, c1, kk / levels))
        self.rect(0, y1, W, H, c1)                                  # below the gradient: the horizon colour (no gaps behind the hills)

    def hills(self, base_y, col, amps, seed, top_col=None, floor=H):
        rnd = random.Random(seed); ph = [rnd.uniform(0, 6.28) for _ in amps]
        for x in range(W):
            y = base_y - sum(a * math.sin(x * (0.012 + 0.017 * i) + ph[i]) for i, a in enumerate(amps))
            y = int(y)
            for yy in range(y, floor): self.put(x, yy, col)
            if top_col: self.put(x, y, top_col)

    def rect(self, x0, y0, x1, y1, col):
        self.d.rectangle([x0, y0, x1, y1], fill=tuple(col) + (255,))

    def castle(self, x, base_y, s, col, win=None, seed=2):
        rnd = random.Random(seed)
        self.rect(x, base_y - int(26 * s), x + int(80 * s), base_y, col)                       # curtain wall
        for cx in range(x, x + int(80 * s), 6):                                               # battlements
            if rnd.random() < .8: self.rect(cx, base_y - int(26 * s) - 3, cx + 3, base_y - int(26 * s), col)
        for t, tx in enumerate((x - 8, x + int(30 * s), x + int(70 * s))):
            hh = int((50 + rnd.randint(0, 30)) * s)
            self.rect(tx, base_y - hh, tx + int(18 * s), base_y, col)
            for cx in range(tx, tx + int(18 * s), 5): self.rect(cx, base_y - hh - 4, cx + 2, base_y - hh, col)
            if rnd.random() < .7:                                                              # a broken top
                self.d.polygon([(tx, base_y - hh), (tx + int(18 * s), base_y - hh), (tx + int(9 * s), base_y - hh - int(14 * s))],
                               fill=tuple(col) + (255,))
            if win:
                for wy in range(base_y - hh + 8, base_y - 6, 14):
                    if rnd.random() < .6: self.rect(tx + int(7 * s), wy, tx + int(9 * s), wy + 3, win)

    def pines(self, base_y, col, n, seed, hmin=40, hmax=80, x0=0, x1=W):
        rnd = random.Random(seed)
        for _ in range(n):
            x = rnd.randint(x0, x1); h = rnd.randint(hmin, hmax); w = h // 3
            for k in range(0, h, 4):
                ww = int(w * (k / h)) + 2
                self.rect(x - ww, base_y - h + k, x + ww, base_y - h + k + 5, col)
            self.rect(x - 1, base_y - 6, x + 1, base_y, col)

    def blit(self, im, x, y):
        self.im.alpha_composite(im, (x, y)) if 0 <= x and 0 <= y and x + im.width <= W and y + im.height <= H else self._clipped(im, x, y)
        self.px = self.im.load(); self.d = ImageDraw.Draw(self.im)

    def _clipped(self, im, x, y):
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); tmp.paste(im, (x, y)); self.im.alpha_composite(tmp)

    def tile_ground(self, tile, y, g, dark_below=(20, 18, 22)):
        for x in range(0, W, tile.width): self.blit(tile, x, y)
        for yy in range(y + tile.height, H):
            for x in range(W): self.put(x, yy, dark_below)

    def glow(self, cx, cy, r, col, strength=0.55, steps=5):
        """A pixel-art light: brightens (towards col) in dithered concentric steps."""
        for y in range(max(0, cy - r), min(H, cy + r)):
            for x in range(max(0, cx - r), min(W, cx + r)):
                d = math.hypot(x - cx, (y - cy) * 1.15) / r
                if d >= 1: continue
                t = (1 - d) ** 1.6 * strength * steps
                k = int(t); fr = t - k
                lvl = k + (1 if fr > (BAYER[y % 4][x % 4] + .5) / 16 else 0)
                if lvl <= 0: continue
                a = min(1.0, lvl / steps)
                p = self.px[x, y]
                self.px[x, y] = tuple(int(p[i] + (col[i] - p[i]) * a * 0.55) for i in range(3)) + (255,)

    def fog(self, y0, y1, col, density=0.5, seed=5):
        rnd = random.Random(seed); ph = rnd.uniform(0, 6)
        for y in range(y0, y1):
            band = (0.5 + 0.5 * math.sin(y * 0.35 + ph)) * density * (1 - abs((y - (y0 + y1) / 2) / ((y1 - y0) / 2)))
            for x in range(W):
                m = band * (0.7 + 0.3 * math.sin(x * 0.03 + y * 0.2))
                if m > (BAYER[y % 4][x % 4] + .5) / 16:
                    p = self.px[x, y]; self.px[x, y] = tuple(int(p[i] + (col[i] - p[i]) * 0.6) for i in range(3)) + (255,)

    def vignette(self, amt=0.55):
        for y in range(H):
            for x in range(W):
                dx = (x - W / 2) / (W / 2); dy = (y - H / 2) / (H / 2)
                d = max(0.0, (dx * dx * .8 + dy * dy) - 0.55) * amt * 2.2
                if d <= 0: continue
                lvl = min(1.0, d)
                if lvl > (BAYER[y % 4][x % 4] + .5) / 16 or lvl > .7:
                    p = self.px[x, y]; k = 1 - 0.45 * min(1.0, lvl + .2)
                    self.px[x, y] = (int(p[0] * k), int(p[1] * k), int(p[2] * k), 255)

    def rain(self, n, col, seed=3, slant=1):
        rnd = random.Random(seed)
        for _ in range(n):
            x = rnd.randint(0, W - 1); y = rnd.randint(0, H - 20); l = rnd.randint(3, 6)
            for k in range(l): self.put(x + k * slant // 2, y + k, col)

    def dots(self, n, col, seed=4, ymax=H, drift=0, size=1):
        rnd = random.Random(seed)
        for _ in range(n):
            x = rnd.randint(0, W - 1); y = rnd.randint(0, ymax - 1)
            for dx in range(size):
                for dy in range(size): self.put(x + dx, y + dy, col)

    def label(self, text, col=(230, 230, 230)):
        pass


def place(scene, name, anim, i, x_hip, flip=False, f=0.85, g=None, light='l', rim=(255, 220, 170), rim_amt=0.4,
          shade=0.25, out=(10, 8, 16), top_boost=0.08, dy=0, fs_override=None):
    im = frame(name, anim, i)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = shorten(im, f)
    if g: im = grade_image(im, g)
    im = lit(im, light, rim, rim_amt, shade, out, top_boost)
    _, _, fs, meta = sheet(name)
    ground_row = meta.get('ground_row', 58)
    scene.blit(im, x_hip - hip_col(name, flip), GROUND_Y - ground_row + dy)
    return im


def fx(scene, anim, i, x_hip, flip=False, f=0.85, g=None, dy=0, sheet_name='vfx', ground_shift=True):
    im = frame(sheet_name, anim, i)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if g: im = grade_image(im, g)
    shift = int(round((1 - f) * 22)) if ground_shift else 0
    scene.blit(im, x_hip - hip_col(sheet_name, flip), GROUND_Y - 58 + shift + dy)


def proj(scene, name, x, y, flip=False, g=None):
    im = prop(name)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if g: im = grade_image(im, g)
    scene.blit(im, x - im.width // 2, y - im.height // 2)


def prop_at(scene, name, x_base, g=None, flip=False, f=1.0, dy=0, out=None):
    im = prop(name)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if g: im = grade_image(im, g)
    scene.blit(im, x_base - im.width // 2, GROUND_Y + 1 - im.height + dy)


def caption(im, title, sub):
    d = ImageDraw.Draw(im)
    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1), (0, 2)):
        d.text((12 + dx, 10 + dy), title, fill=(0, 0, 0))
        d.text((12 + dx, 26 + dy), sub, fill=(0, 0, 0))
    d.text((12, 10), title, fill=(255, 240, 200)); d.text((12, 26), sub, fill=(205, 205, 215))
    return im


DETAIL = (70, 120, 430, 240)          # the fighting area, shown at 4x in the "_detalhe" image


def finish(scene, path, title, sub):
    rgb = scene.im.convert('RGB')
    big = rgb.resize((W * SCALE, H * SCALE), Image.NEAREST)
    caption(big, title, sub); big.save(path)
    det = rgb.crop(DETAIL); det = det.resize((det.width * 4, det.height * 4), Image.NEAREST)
    det.save(path.replace('.png', '_detalhe.png'))
    return big


# ------------------------------------------------------------------------------------------------ proposals
def p0_compare(out):
    """Current proportions vs the shorter options, side by side, plain background."""
    s = Scene(1); s.vgrad(0, GROUND_Y, (58, 66, 84), (120, 128, 140)); s.rect(0, GROUND_Y + 1, W, H, (40, 38, 46))
    for k, (f, lab) in enumerate(((1.0, 'ATUAL'), (0.88, '88%'), (0.80, '80%'), (0.72, '72%'))):
        x = 60 + k * 112
        place(s, 'knight', 'idle', 0, x, False, f, None, rim_amt=0.0, shade=0.0, out=OUT_OLD, top_boost=0)
        place(s, 'ogre', 'idle', 0, x + 40, True, f, None, rim_amt=0.0, shade=0.0, out=OUT_OLD, top_boost=0)
        s.d.text((x - 14, GROUND_Y + 14), lab, fill=(255, 255, 255, 255))
    return finish(s, os.path.join(out, '00_comparativo_altura.png'), 'Altura dos personagens',
                  'atual / 88% / 80% / 72% (cavaleiro e ogro)')


def p1_penumbra(out):
    s = Scene(11)
    g = make_grade(sat=0.62, val=0.82, contrast=1.12, tint=(1.02, 0.97, 0.93))
    gp = make_grade(sat=0.5, val=0.62, contrast=1.1, tint=(0.95, 0.95, 1.0))
    s.vgrad(0, 150, (28, 30, 42), (150, 112, 92), levels=9)                              # dusk, a warm band on the horizon
    s.glow(360, 150, 120, (255, 170, 110), 0.5)
    s.hills(158, (66, 58, 74), (22, 10, 6), 3)
    s.castle(280, 150, 1.3, (38, 34, 48), win=(255, 190, 90))
    s.hills(176, (40, 38, 46), (14, 7, 3), 9, top_col=(70, 62, 70))
    s.pines(190, (26, 28, 34), 9, 4, 40, 70)
    s.fog(150, 205, (150, 130, 130), 0.55)
    tile = grade_image(prop('street_tile'), gp)
    s.tile_ground(tile, GROUND_Y - 3, gp)
    prop_at(s, 'dead_tree', 70, gp); prop_at(s, 'banner', 240, gp); prop_at(s, 'palisade', 420, gp)
    s.fog(200, 222, (110, 100, 110), 0.35, seed=8)
    place(s, 'knight', 'attack_sword', 3, 150, False, 0.85, g, light='r', rim=(255, 190, 120))
    fx(s, 'sword_slash', 0, 150, False, 0.85, make_grade(sat=0.5, val=0.9))
    place(s, 'ranger', 'idle', 0, 96, False, 0.85, g, light='r', rim=(255, 190, 120))
    place(s, 'ogre', 'hurt', 2, 205, True, 0.85, g, light='r', rim=(255, 190, 120))
    fx(s, 'blood_splash', 2, 205, True, 0.85, make_grade(sat=1.0, val=0.8))
    place(s, 'soldier', 'walk', 1, 320, True, 0.85, g, light='r', rim=(255, 190, 120))
    place(s, 'shieldman', 'guard', 0, 395, True, 0.85, g, light='r', rim=(255, 190, 120))
    s.dots(40, (255, 200, 140), 6, 200)
    s.vignette(0.6)
    return finish(s, os.path.join(out, '01_penumbra.png'), 'Proposta 1 - Penumbra',
                  'crepusculo, cores apagadas, castelo em ruinas, nevoa, personagens a 85% da altura')


def p2_cinzas(out):
    s = Scene(21)
    g = make_grade(sat=0.8, val=0.75, contrast=1.2, tint=(1.1, 0.88, 0.78))
    gp = make_grade(sat=0.55, val=0.55, contrast=1.15, tint=(1.15, 0.85, 0.75))
    s.vgrad(0, 160, (20, 12, 16), (196, 80, 36), levels=10)
    s.glow(240, 175, 200, (255, 140, 60), 0.6)
    s.hills(170, (46, 24, 26), (18, 9, 5), 4)
    for hx in (60, 190, 330, 430):                                                       # burning houses (silhouettes)
        h = prop('medieval_house'); h = grade_image(h, make_grade(sat=0.3, val=0.28, tint=(1.1, 0.9, 0.85)))
        h = h.resize((int(h.width * .75), int(h.height * .75)), Image.NEAREST); s.blit(h, hx - h.width // 2, 178 - h.height + 24)
        s.glow(hx, 150, 60, (255, 150, 60), 0.7)
    s.fog(120, 200, (60, 30, 30), 0.6, seed=2)
    tile = grade_image(prop('street_tile'), gp)
    s.tile_ground(tile, GROUND_Y - 3, gp, dark_below=(24, 12, 14))
    prop_at(s, 'cart', 110, gp); prop_at(s, 'planted_swords', 380, gp); prop_at(s, 'campfire', 250, make_grade(sat=1.1, val=0.9))
    s.glow(250, 206, 60, (255, 160, 70), 0.9)
    place(s, 'knight', 'idle', 0, 120, False, 0.8, g, light='r', rim=(255, 160, 80), rim_amt=0.55)
    place(s, 'mage', 'attack_staff', 3, 175, False, 0.8, g, light='r', rim=(255, 160, 80), rim_amt=0.55)
    proj(s, 'proj_fireball_big', 215, 189, False, make_grade(sat=1.1, val=1.0))
    s.glow(215, 189, 30, (255, 170, 60), 0.9)
    place(s, 'orc', 'attack', 3, 305, True, 0.8, g, light='l', rim=(255, 140, 70), rim_amt=0.5)
    place(s, 'goblin', 'walk', 0, 372, True, 0.8, g, light='l', rim=(255, 140, 70), rim_amt=0.5)
    place(s, 'kobold', 'walk', 2, 420, True, 0.8, g, light='l', rim=(255, 140, 70), rim_amt=0.5)
    s.dots(110, (255, 160, 70), 7, 215); s.dots(60, (255, 220, 140), 9, 200)
    s.vignette(0.7)
    return finish(s, os.path.join(out, '02_cinzas.png'), 'Proposta 2 - Cinzas',
                  'vila em chamas, ceu vermelho, brasas, luz alaranjada nas bordas, personagens a 80%')


def p3_noite(out):
    s = Scene(31)
    g = make_grade(sat=0.55, val=0.78, contrast=1.15, tint=(0.82, 0.92, 1.12))
    gp = make_grade(sat=0.5, val=0.55, contrast=1.1, tint=(0.8, 0.92, 1.15))
    s.vgrad(0, 160, (8, 12, 28), (52, 74, 112), levels=9)
    s.dots(60, (200, 215, 255), 5, 110)
    s.d.ellipse([360, 30, 392, 62], fill=(226, 232, 245, 255)); s.d.ellipse([368, 36, 394, 58], fill=(8 + 10, 14 + 10, 34 + 12, 255))
    s.glow(376, 46, 90, (140, 170, 230), 0.5)
    s.hills(170, (26, 38, 62), (20, 9, 5), 6)
    s.pines(185, (14, 20, 36), 14, 8, 50, 95)
    s.hills(196, (16, 24, 40), (10, 5, 3), 2, top_col=(40, 58, 90))
    s.fog(150, 212, (90, 120, 170), 0.6, seed=12)
    tile = grade_image(prop('forest_tile'), gp)
    s.tile_ground(tile, GROUND_Y - 3, gp, dark_below=(10, 14, 24))
    prop_at(s, 'dead_tree', 60, gp); prop_at(s, 'oak', 430, gp); prop_at(s, 'mushrooms', 250, make_grade(sat=0.9, val=0.7, tint=(0.8, 0.9, 1.2)))
    place(s, 'knight', 'idle', 0, 130, False, 0.85, g, light='r', rim=(150, 190, 255), rim_amt=0.5)
    place(s, 'mage', 'attack_staff', 3, 188, False, 0.85, g, light='r', rim=(255, 170, 90), rim_amt=0.6)
    proj(s, 'proj_fireball', 232, 189, False, make_grade(sat=1.2, val=1.0)); s.glow(232, 189, 70, (255, 170, 70), 0.9)
    s.glow(195, 195, 60, (255, 150, 60), 0.5)
    place(s, 'minotaur', 'idle', 1, 330, True, 0.85, g, light='l', rim=(150, 190, 255), rim_amt=0.45)
    place(s, 'archer', 'idle', 0, 405, True, 0.85, g, light='l', rim=(150, 190, 255), rim_amt=0.45)
    fx(s, 'fire_burst', 2, 330, True, 0.85, make_grade(sat=1.1, val=1.0), dy=-4)
    s.glow(330, 200, 50, (255, 150, 60), 0.8)
    s.dots(30, (180, 210, 255), 14, 215)
    s.vignette(0.65)
    return finish(s, os.path.join(out, '03_noite_de_lua.png'), 'Proposta 3 - Noite de Lua',
                  'azul frio, luar, floresta morta, luz quente da magia contra o frio, personagens a 85%')


def p4_masmorra(out):
    s = Scene(41)
    g = make_grade(sat=0.55, val=0.7, contrast=1.2, tint=(1.06, 0.97, 0.9))
    gp = make_grade(sat=0.35, val=0.5, contrast=1.15, tint=(1.05, 0.98, 0.95))
    wall = prop('stone_wall'); wall = grade_image(wall, gp)
    s.rect(0, 0, W, H, (16, 14, 18))
    for y in range(40, GROUND_Y - 12, wall.height - 6):                                    # a wall of stone blocks
        for x in range(0, W, wall.width): s.blit(wall, x - 10, y)
    s.rect(0, 0, W, 40, (10, 9, 12))
    for ax in (80, 240, 400):                                                              # arches / pillars
        s.rect(ax - 12, 30, ax + 12, GROUND_Y, (34, 30, 38)); s.rect(ax - 12, 30, ax - 9, GROUND_Y, (52, 46, 54))
    for tx in (160, 320):                                                                  # torches
        s.rect(tx - 1, 96, tx + 1, 112, (60, 40, 28)); s.rect(tx - 2, 90, tx + 2, 96, (255, 190, 80)); s.put(tx, 88, (255, 240, 170))
        s.glow(tx, 96, 100, (255, 170, 70), 0.85)
    tile = grade_image(prop('street_tile'), gp)
    s.tile_ground(tile, GROUND_Y - 3, gp, dark_below=(14, 12, 16))
    for tx in (160, 320): s.glow(tx, GROUND_Y - 6, 70, (255, 170, 70), 0.5)
    prop_at(s, 'barrels', 40, gp); prop_at(s, 'box', 440, gp)
    place(s, 'knight', 'attack_sword', 3, 130, False, 0.8, g, light='r', rim=(255, 190, 110), rim_amt=0.5)
    fx(s, 'sword_slash', 0, 130, False, 0.8, make_grade(sat=0.4, val=0.9))
    place(s, 'shieldman', 'guard', 0, 215, True, 0.8, g, light='l', rim=(255, 190, 110), rim_amt=0.5)
    fx(s, 'shield_break', 2, 215, True, 0.8, make_grade(sat=0.9, val=1.0))
    place(s, 'black_knight', 'idle', 0, 330, True, 0.8, g, light='l', rim=(255, 190, 110), rim_amt=0.5)
    place(s, 'crossbowman', 'idle', 0, 70, False, 0.8, g, light='r', rim=(255, 190, 110), rim_amt=0.5)
    s.dots(35, (255, 190, 100), 3, 200)
    s.vignette(0.9)
    return finish(s, os.path.join(out, '04_masmorra.png'), 'Proposta 4 - Masmorra',
                  'interior de pedra, tochas com luz dithered, vinheta forte, chefe ao fundo, personagens a 80%')


def p5_chuva(out):
    s = Scene(51)
    g = make_grade(sat=0.5, val=0.8, contrast=1.1, tint=(0.95, 1.0, 0.98))
    gp = make_grade(sat=0.42, val=0.6, contrast=1.05, tint=(0.92, 1.0, 0.98))
    s.vgrad(0, 160, (54, 60, 64), (128, 138, 134), levels=7)
    s.hills(160, (74, 84, 82), (20, 10, 6), 14)
    s.pines(178, (46, 56, 56), 10, 17, 40, 70)
    s.hills(186, (52, 60, 58), (12, 6, 3), 22, top_col=(88, 98, 94))
    s.fog(140, 200, (140, 150, 148), 0.7, seed=9)
    tile = grade_image(prop('grass_tile'), gp)
    s.tile_ground(tile, GROUND_Y - 3, gp, dark_below=(26, 30, 30))
    prop_at(s, 'tent', 90, gp); prop_at(s, 'log', 330, gp); prop_at(s, 'bush', 430, gp)
    place(s, 'ranger', 'idle', 0, 95, False, 0.85, g, light='t', rim=(210, 220, 215), rim_amt=0.2)
    place(s, 'knight', 'idle', 0, 150, False, 0.85, g, light='t', rim=(210, 220, 215), rim_amt=0.2)
    place(s, 'ogre', 'idle', 0, 260, True, 0.85, g, light='t', rim=(210, 220, 215), rim_amt=0.2)
    place(s, 'soldier', 'idle', 0, 340, True, 0.85, g, light='t', rim=(210, 220, 215), rim_amt=0.2)
    place(s, 'spearman', 'idle', 0, 410, True, 0.85, g, light='t', rim=(210, 220, 215), rim_amt=0.2)
    # puddle reflections (squashed, dark, dithered) right under the feet
    for k, x in enumerate((150, 260, 340, 410)):
        for yy in range(GROUND_Y + 2, GROUND_Y + 9):
            for xx in range(x - 14, x + 14):
                if (BAYER[yy % 4][xx % 4] + .5) / 16 < 0.5 - (yy - GROUND_Y) * 0.05: s.put(xx, yy, (70, 82, 84))
    s.rain(260, (170, 184, 190), 3, 1); s.rain(120, (110, 124, 130), 8, 1)
    s.vignette(0.5)
    return finish(s, os.path.join(out, '05_chuva_cinzenta.png'), 'Proposta 5 - Chuva Cinzenta',
                  'nublado, verde-acinzentado, chuva, poças, luz difusa de cima, personagens a 85%')


def p6_inverno(out):
    s = Scene(61)
    g = make_grade(sat=0.45, val=0.9, contrast=1.2, tint=(0.95, 1.0, 1.1))
    gp = make_grade(sat=0.3, val=0.85, contrast=1.05, tint=(0.95, 1.0, 1.1))
    s.vgrad(0, 150, (34, 40, 58), (186, 196, 214), levels=8)
    s.hills(150, (150, 162, 184), (22, 10, 6), 7, top_col=(210, 220, 235))
    s.pines(180, (44, 56, 78), 12, 3, 45, 90)
    s.castle(300, 160, 1.1, (90, 100, 128), win=(255, 200, 110), seed=7)
    s.hills(190, (120, 134, 160), (10, 5, 3), 8, top_col=(224, 232, 244))
    s.fog(150, 205, (214, 222, 235), 0.45, seed=3)
    tile = grade_image(prop('grass_tile'), make_grade(sat=0.1, val=1.7, tint=(0.95, 1.0, 1.1)))
    s.tile_ground(tile, GROUND_Y - 3, gp, dark_below=(170, 182, 204))
    prop_at(s, 'dead_tree', 60, make_grade(sat=0.4, val=0.7, tint=(0.9, 0.95, 1.1)))
    prop_at(s, 'banner', 250, make_grade(sat=0.9, val=0.85)); prop_at(s, 'planted_swords', 420, gp)
    place(s, 'knight', 'attack_sword', 3, 140, False, 0.8, g, light='t', rim=(240, 246, 255), rim_amt=0.5)
    fx(s, 'sword_slash', 0, 140, False, 0.8, make_grade(sat=0.3, val=1.0))
    place(s, 'orc', 'hurt', 2, 205, True, 0.8, g, light='t', rim=(240, 246, 255), rim_amt=0.5)
    fx(s, 'blood_splash', 3, 205, True, 0.8, make_grade(sat=1.3, val=0.9))                 # blood against the snow
    place(s, 'goblin', 'walk', 0, 275, True, 0.8, g, light='t', rim=(240, 246, 255), rim_amt=0.5)
    place(s, 'ogre_captain', 'idle', 0, 380, True, 0.8, g, light='t', rim=(240, 246, 255), rim_amt=0.5)
    s.dots(160, (240, 244, 255), 5, 215); s.dots(60, (240, 244, 255), 8, 215, size=2)
    s.vignette(0.4)
    return finish(s, os.path.join(out, '06_inverno.png'), 'Proposta 6 - Inverno',
                  'neve, claro e frio, o sangue e o fogo ganham contraste, chefe grande ao fundo, personagens a 80%')


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'out', 'art_proposals')
    os.makedirs(out, exist_ok=True)
    imgs = []
    for fn in (p0_compare, p1_penumbra, p2_cinzas, p3_noite, p4_masmorra, p5_chuva, p6_inverno):
        imgs.append(fn(out)); print('wrote', fn.__name__)
    cell = (W * 2, H * 2)
    sheet_im = Image.new('RGB', (cell[0] * 2, cell[1] * 4), (0, 0, 0))
    for i, im in enumerate(imgs):
        sheet_im.paste(im.resize(cell, Image.NEAREST), ((i % 2) * cell[0], (i // 2) * cell[1]))
    sheet_im.save(os.path.join(out, '_visao_geral.png'))


if __name__ == '__main__':
    main()
