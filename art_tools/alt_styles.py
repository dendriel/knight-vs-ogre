"""Alternative art directions (static concepts, NOT used by the game): characters in styles completely different from the
current game, still pixel art and medieval / heroic. Unlike human_styles.py these do not use the game's rig: every figure
is composed of shaded parts by a small "part painter" (base / light / shade from the part's own edges), so each style
brings its own proportions, level of detail, outline rule and palette.

    python art_tools/alt_styles.py [out_dir]       (default: out/art_estilos)
"""
import os, sys, math, random, colorsys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import proposals_gen as PG


# ------------------------------------------------------------------------------------------------ colour helpers
def C(r, g, b): return (r, g, b)


def shift(c, dv=1.0, ds=1.0, dh=0.0):
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    h = (h + dh) % 1.0; s = max(0, min(1, s * ds)); v = max(0, min(1, v * dv))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def ramp(c, shade=0.62, light=1.22, hue=0.025):
    """(shade, base, light): shadows slide towards blue-violet and gain saturation, lights towards warm."""
    return shift(c, shade, 1.08, -hue), c, shift(c, light, 0.92, hue)


# ------------------------------------------------------------------------------------------------ the part painter
class Sprite:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]

    def part(self, draw, base, shade=None, light=None, bevel=1, ld=(-1, -1), dither=0.0, spec=None):
        """Paints a part. `draw(d)` draws it white on a mask. The edge facing the light direction `ld` gets `light`, the
        opposite edge `shade` (both `bevel` px thick); `dither` (0..1) checker-shades the far lower part of the shape."""
        m = Image.new('L', (self.w, self.h), 0); draw(ImageDraw.Draw(m)); mp = m.load()
        w, h = self.w, self.h
        def inside(x, y): return 0 <= x < w and 0 <= y < h and mp[x, y] > 127
        auto = ramp(base)
        shade = shade or auto[0]; light = light or auto[2]
        pts = [(x, y) for y in range(h) for x in range(w) if inside(x, y)]
        if not pts: return
        x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts); y0 = min(p[1] for p in pts); y1 = max(p[1] for p in pts)
        for x, y in pts:
            c = base
            lit = any(not inside(x + ld[0] * k, y + ld[1] * k) for k in range(1, bevel + 1))
            dark = any(not inside(x - ld[0] * k, y - ld[1] * k) for k in range(1, bevel + 1))
            if dither:
                t = ((x - x0) / max(1, x1 - x0) * -ld[0] + (y - y0) / max(1, y1 - y0) * -ld[1]) / 2 + .5
                if t > 1 - dither * 0.5 and (x + y) % 2 == 0: c = shade
                if t > 1 - dither * 0.25: c = shade
            if lit and not dark: c = light
            elif dark and not lit: c = shade
            self.px[y][x] = c
        if spec:                                                       # a single bright pixel on the lit corner
            sx, sy = spec
            if 0 <= sx < w and 0 <= sy < h and self.px[sy][sx] is not None: self.px[sy][sx] = shift(base, 1.55, 0.4)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.px[y][x] = c

    def line(self, a, b, c):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for k in range(n + 1):
            t = k / max(n, 1); self.put(int(round(a[0] + (b[0] - a[0]) * t)), int(round(a[1] + (b[1] - a[1]) * t)), c)

    def image(self, outline=None, thick=1, tint=0.38, glow=None):
        """outline: None | colour tuple | 'tint' (each outline pixel = the darkened colour of the neighbour it surrounds)."""
        w, h = self.w, self.h
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); p = im.load()
        for y in range(h):
            for x in range(w):
                if self.px[y][x] is not None: p[x, y] = self.px[y][x] + (255,)
        if outline is None: return im
        cur = im
        for t in range(thick):
            src = cur.load(); out = cur.copy(); po = out.load()
            for y in range(h):
                for x in range(w):
                    if src[x, y][3]: continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3]:
                            if outline == 'tint': po[x, y] = shift(src[nx, ny][:3], tint, 1.1) + (255,)
                            else: po[x, y] = tuple(outline) + (255,)
                            break
            cur = out
        return cur


def mirror(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


def hflip_draw(w, fn):
    """wraps a draw function so that x coordinates are mirrored inside a canvas of width w"""
    return fn


# ------------------------------------------------------------------------------------------------ style 1: chibi
def chibi(role):
    S = Sprite(48, 58); G = 56
    if role == 'knight':
        steel = C(150, 178, 224); cloth = C(220, 70, 80); skin = C(250, 214, 178); trim = C(255, 214, 90)
        # legs / feet
        S.part(lambda d: d.rectangle([17, 44, 22, 52], fill=255), steel)
        S.part(lambda d: d.rectangle([27, 44, 32, 52], fill=steel and 255), steel)
        S.part(lambda d: d.rounded_rectangle([14, 50, 24, G], 2, fill=255), C(124, 84, 60))
        S.part(lambda d: d.rounded_rectangle([26, 50, 38, G], 2, fill=255), C(124, 84, 60))
        # body + tabard
        S.part(lambda d: d.rounded_rectangle([15, 31, 34, 47], 4, fill=255), steel, bevel=2)
        S.part(lambda d: d.polygon([(20, 35), (30, 35), (31, 48), (19, 48)], fill=255), cloth)
        S.part(lambda d: d.rectangle([15, 41, 34, 42], fill=255), trim)
        # far arm + near arm
        S.part(lambda d: d.rounded_rectangle([10, 33, 16, 44], 2, fill=255), shift(steel, .8))
        S.part(lambda d: d.rounded_rectangle([33, 33, 40, 43], 3, fill=255), steel)
        S.part(lambda d: d.ellipse([37, 38, 44, 45], fill=255), skin)
        # big sword
        S.part(lambda d: d.polygon([(40, 38), (43, 36), (46, 6), (43, 3), (40, 7)], fill=255), C(226, 232, 244), bevel=1)
        S.part(lambda d: d.rectangle([36, 36, 46, 38], fill=255), trim)
        # huge head: helmet over a round face
        S.part(lambda d: d.ellipse([9, 3, 39, 33], fill=255), steel, bevel=2, spec=(17, 8))
        S.part(lambda d: d.ellipse([14, 16, 37, 32], fill=255), skin, bevel=1)
        S.part(lambda d: d.rectangle([11, 12, 37, 17], fill=255), shift(steel, .85), bevel=1)         # brow band of the helm
        S.part(lambda d: d.polygon([(10, 12), (4, 6), (6, 18), (12, 18)], fill=255), cloth)           # plume
        for ex in (26, 33):                                                                          # big eyes
            S.part(lambda d, ex=ex: d.rectangle([ex, 21, ex + 3, 26], fill=255), C(40, 36, 60), bevel=0)
            S.put(ex + 1, 22, C(255, 255, 255)); S.put(ex + 1, 23, C(255, 255, 255))
        S.put(24, 28, C(240, 150, 150)); S.put(36, 28, C(240, 150, 150))
        S.put(31, 29, C(180, 90, 90)); S.put(32, 29, C(180, 90, 90))
    elif role == 'mage':
        robe = C(130, 90, 214); skin = C(250, 214, 178); gold = C(255, 214, 90)
        S.part(lambda d: d.polygon([(13, 33), (36, 33), (40, G), (9, G)], fill=255), robe, bevel=2, dither=.5)
        S.part(lambda d: d.rectangle([14, 42, 35, 44], fill=255), gold)
        S.part(lambda d: d.rounded_rectangle([33, 33, 40, 44], 3, fill=255), shift(robe, 1.05))
        S.part(lambda d: d.ellipse([37, 38, 44, 45], fill=255), skin)
        S.part(lambda d: d.rectangle([43, 6, 45, 54], fill=255), C(150, 100, 60), bevel=0)          # staff
        S.part(lambda d: d.ellipse([39, 0, 49, 10], fill=255), C(120, 230, 255), bevel=1)
        S.part(lambda d: d.ellipse([10, 8, 38, 36], fill=255), skin, bevel=2)
        S.part(lambda d: d.polygon([(9, 15), (39, 15), (37, 8), (26, -8), (13, 8)], fill=255), robe, bevel=1)   # hat
        S.part(lambda d: d.ellipse([4, 12, 44, 19], fill=255), shift(robe, .8), bevel=1)                     # brim
        S.part(lambda d: d.rectangle([14, 28, 34, 33], fill=255), C(240, 240, 245), bevel=1)                 # beard
        for ex in (25, 32):
            S.part(lambda d, ex=ex: d.rectangle([ex, 20, ex + 3, 25], fill=255), C(40, 36, 60), bevel=0)
            S.put(ex + 1, 21, C(255, 255, 255)); S.put(ex + 1, 22, C(255, 255, 255))
    else:                                                                                           # orc
        skin = C(120, 190, 90); leath = C(150, 98, 60); ivory = C(250, 244, 220)
        S.part(lambda d: d.rectangle([16, 44, 23, 53], fill=255), shift(skin, .85))
        S.part(lambda d: d.rectangle([27, 44, 34, 53], fill=255), skin)
        S.part(lambda d: d.rounded_rectangle([13, 51, 25, G], 2, fill=255), C(80, 60, 44))
        S.part(lambda d: d.rounded_rectangle([26, 51, 40, G], 2, fill=255), C(80, 60, 44))
        S.part(lambda d: d.rounded_rectangle([13, 31, 36, 48], 5, fill=255), skin, bevel=2)
        S.part(lambda d: d.polygon([(16, 32), (33, 32), (35, 47), (14, 47)], fill=255), leath)
        S.part(lambda d: d.rounded_rectangle([8, 32, 15, 45], 3, fill=255), shift(skin, .85))
        S.part(lambda d: d.rounded_rectangle([34, 32, 42, 44], 3, fill=255), skin)
        S.part(lambda d: d.rectangle([40, 8, 46, 40], fill=255), C(140, 96, 56), bevel=1)                 # club
        S.part(lambda d: d.ellipse([36, 0, 48, 14], fill=255), C(120, 82, 48), bevel=1)
        S.part(lambda d: d.ellipse([8, 3, 40, 35], fill=255), skin, bevel=2, spec=(15, 8))
        S.part(lambda d: d.polygon([(12, 14), (36, 14), (37, 8), (11, 8)], fill=255), C(64, 70, 84))      # iron cap
        S.part(lambda d: d.rectangle([13, 18, 20, 20], fill=255), C(60, 100, 40), bevel=0)               # brow
        for ex, ey in ((26, 20), (33, 20)):
            S.part(lambda d, ex=ex, ey=ey: d.rectangle([ex, ey, ex + 3, ey + 4], fill=255), C(255, 220, 90), bevel=0)
            S.put(ex + 1, ey + 2, C(60, 20, 10)); S.put(ex + 2, ey + 2, C(60, 20, 10))
        S.part(lambda d: d.rectangle([17, 27, 37, 31], fill=255), shift(skin, .8), bevel=1)               # jaw
        S.part(lambda d: d.polygon([(20, 27), (23, 27), (22, 20)], fill=255), ivory, bevel=0)             # tusks
        S.part(lambda d: d.polygon([(30, 27), (33, 27), (32, 21)], fill=255), ivory, bevel=0)
    return S.image('tint', thick=1)


# ------------------------------------------------------------------------------------------------ style 2: 4-colour mini
GB = [C(15, 56, 15), C(48, 98, 48), C(139, 172, 15), C(198, 222, 120)]      # darkest .. lightest (a hand-held LCD)


def gameboy(role):
    S = Sprite(16, 24); D, M, L, W = GB
    if role == 'knight':
        S.part(lambda d: d.rectangle([5, 17, 7, 22], fill=255), D, bevel=0)                  # legs
        S.part(lambda d: d.rectangle([9, 17, 11, 22], fill=255), D, bevel=0)
        S.part(lambda d: d.rectangle([4, 22, 8, 23], fill=255), D, bevel=0); S.part(lambda d: d.rectangle([9, 22, 13, 23], fill=255), D, bevel=0)
        S.part(lambda d: d.rectangle([4, 9, 11, 17], fill=255), M, shade=D, light=L, bevel=1)   # body
        S.part(lambda d: d.rectangle([6, 11, 9, 15], fill=255), D, bevel=0)                  # tabard
        S.part(lambda d: d.rectangle([4, 2, 11, 9], fill=255), L, shade=M, light=W, bevel=1)    # helm
        S.part(lambda d: d.rectangle([7, 5, 11, 6], fill=255), D, bevel=0)                   # visor
        S.part(lambda d: d.rectangle([6, 0, 8, 2], fill=255), D, bevel=0)                    # plume
        S.part(lambda d: d.rectangle([12, 1, 13, 14], fill=255), W, shade=L, bevel=0)           # sword
        S.part(lambda d: d.rectangle([11, 13, 14, 14], fill=255), D, bevel=0)
    elif role == 'mage':
        S.part(lambda d: d.polygon([(4, 9), (11, 9), (13, 23), (2, 23)], fill=255), M, shade=D, light=L, bevel=1)
        S.part(lambda d: d.rectangle([5, 4, 10, 9], fill=255), W, shade=L, bevel=0)           # face
        S.part(lambda d: d.polygon([(2, 5), (13, 5), (9, 4), (8, -1), (6, 3)], fill=255), D, bevel=0)  # hat
        S.part(lambda d: d.rectangle([7, 6, 9, 6], fill=255), D, bevel=0)
        S.part(lambda d: d.rectangle([13, 3, 13, 22], fill=255), D, bevel=0)                 # staff
        S.part(lambda d: d.rectangle([12, 1, 14, 3], fill=255), W, shade=L, bevel=0)
    else:                                                                                   # ogre
        S.part(lambda d: d.rectangle([4, 18, 7, 22], fill=255), D, bevel=0); S.part(lambda d: d.rectangle([9, 18, 12, 22], fill=255), D, bevel=0)
        S.part(lambda d: d.rectangle([3, 22, 8, 23], fill=255), D, bevel=0); S.part(lambda d: d.rectangle([8, 22, 14, 23], fill=255), D, bevel=0)
        S.part(lambda d: d.rounded_rectangle([2, 8, 13, 19], 2, fill=255), L, shade=M, light=W, bevel=1)
        S.part(lambda d: d.rectangle([4, 13, 11, 16], fill=255), M, bevel=0)
        S.part(lambda d: d.rectangle([4, 2, 11, 9], fill=255), L, shade=M, light=W, bevel=1)   # head
        S.part(lambda d: d.rectangle([5, 4, 6, 5], fill=255), D, bevel=0); S.part(lambda d: d.rectangle([9, 4, 10, 5], fill=255), D, bevel=0)
        S.part(lambda d: d.rectangle([5, 7, 10, 8], fill=255), D, bevel=0)
        S.part(lambda d: d.rectangle([13, 0, 15, 14], fill=255), D, bevel=0)                  # club
    return S.image(D)


# ------------------------------------------------------------------------------------------------ style 3: detailed, 7 heads
def detailed(role):
    S = Sprite(84, 124); G = 122
    if role == 'knight':
        steel = C(150, 160, 178); dark = C(70, 76, 92); gold = C(226, 182, 70); cloth = C(120, 24, 40); leath = C(104, 72, 48)
        # cape behind
        S.part(lambda d: d.polygon([(30, 30), (40, 30), (34, 118), (6, 112), (14, 70)], fill=255), cloth, bevel=1, dither=.6)
        for k, fx in enumerate((14, 20, 26)):
            S.line((fx + 8, 40 + k * 3), (fx, 108 + k), shift(cloth, .7))
        # far leg
        S.part(lambda d: d.polygon([(34, 66), (44, 66), (44, 84), (36, 84)], fill=255), shift(steel, .7), bevel=1)
        S.part(lambda d: d.polygon([(34, 84), (43, 84), (43, 112), (35, 112)], fill=255), shift(steel, .7), bevel=1)
        S.part(lambda d: d.polygon([(34, 112), (44, 112), (52, 117), (52, G), (34, G)], fill=255), shift(dark, .8), bevel=1)
        # near leg: cuisse, knee cop, greave, sabaton
        S.part(lambda d: d.polygon([(40, 66), (52, 66), (54, 86), (44, 88)], fill=255), steel, bevel=1, dither=.4)
        S.part(lambda d: d.ellipse([42, 83, 56, 95], fill=255), steel, bevel=1, spec=(45, 85))
        S.part(lambda d: d.polygon([(43, 94), (55, 94), (53, 112), (44, 112)], fill=255), steel, bevel=1, dither=.5)
        S.part(lambda d: d.line([(44, 100), (53, 100)], fill=255), dark, bevel=0)
        S.part(lambda d: d.polygon([(43, 112), (54, 112), (66, 118), (66, G), (43, G)], fill=255), dark, bevel=1)
        # tassets
        for k, y in enumerate((52, 58, 64)):
            S.part(lambda d, y=y, k=k: d.polygon([(30 - k, y), (52 + k, y), (54 + k, y + 8), (28 - k, y + 8)], fill=255), steel, bevel=1)
        S.part(lambda d: d.rectangle([30, 50, 52, 54], fill=255), leath, bevel=1)                         # belt
        S.part(lambda d: d.rectangle([39, 50, 43, 54], fill=255), gold, bevel=0)
        # torso: breastplate with a ridge and a mail collar
        S.part(lambda d: d.polygon([(30, 26), (50, 26), (56, 38), (52, 52), (32, 52), (28, 38)], fill=255), steel, bevel=2, dither=.5)
        S.line((42, 28), (42, 50), shift(steel, 1.3)); S.line((36, 32), (34, 50), shift(steel, .75))
        S.part(lambda d: d.rectangle([34, 20, 48, 28], fill=255), dark, bevel=1)                          # gorget
        for yy in range(21, 28):
            for xx in range(35, 48):
                if (xx + yy) % 2 == 0: S.put(xx, yy, shift(dark, 1.4))
        # far arm (shield arm) and near arm
        S.part(lambda d: d.polygon([(26, 28), (32, 28), (22, 50), (16, 48)], fill=255), shift(steel, .7), bevel=1)
        S.part(lambda d: d.polygon([(8, 36), (24, 32), (28, 52), (18, 74), (8, 56)], fill=255), C(60, 70, 110), bevel=2, dither=.5)   # shield
        S.part(lambda d: d.polygon([(14, 40), (22, 38), (24, 52), (18, 64), (13, 52)], fill=255), cloth, bevel=1)
        S.part(lambda d: d.ellipse([15, 44, 21, 50], fill=255), gold, bevel=1)
        # pauldron lames + near arm
        S.part(lambda d: d.polygon([(44, 24), (58, 28), (58, 40), (44, 38)], fill=255), steel, bevel=2, spec=(47, 26))
        S.part(lambda d: d.polygon([(46, 36), (58, 36), (59, 44), (47, 44)], fill=255), steel, bevel=1)
        S.part(lambda d: d.polygon([(48, 44), (58, 44), (62, 58), (54, 60)], fill=255), steel, bevel=1)    # rerebrace
        S.part(lambda d: d.ellipse([53, 54, 64, 64], fill=255), steel, bevel=1)                           # couter
        S.part(lambda d: d.polygon([(56, 62), (66, 58), (74, 52), (72, 48), (62, 52), (56, 58)], fill=255), steel, bevel=1)   # vambrace
        S.part(lambda d: d.ellipse([70, 46, 78, 54], fill=255), dark, bevel=1)                           # gauntlet
        # sword held upright-forward
        S.part(lambda d: d.polygon([(72, 48), (76, 48), (80, 6), (77, 2), (73, 8)], fill=255), C(226, 232, 244), bevel=1)
        S.line((77, 8), (75, 46), C(150, 160, 190))
        S.part(lambda d: d.rectangle([66, 46, 82, 48], fill=255), gold, bevel=1)
        # head: bascinet with visor, plume and aventail
        S.part(lambda d: d.polygon([(30, 18), (50, 18), (52, 30), (48, 32), (32, 32), (28, 30)], fill=255), dark, bevel=1)   # aventail
        for yy in range(19, 32):
            for xx in range(29, 52):
                if S.px[yy][xx] == dark and (xx + yy) % 2 == 0: S.px[yy][xx] = shift(dark, 1.35)
        S.part(lambda d: d.ellipse([30, 2, 52, 26], fill=255), steel, bevel=2, spec=(35, 6))
        S.part(lambda d: d.polygon([(42, 10), (52, 12), (52, 22), (44, 24), (42, 18)], fill=255), shift(steel, .8), bevel=1)   # visor
        S.part(lambda d: d.rectangle([44, 14, 52, 15], fill=255), C(10, 10, 16), bevel=0)
        for yy in range(17, 23): S.put(48, yy, C(10, 10, 16))
        S.part(lambda d: d.polygon([(34, 4), (44, 0), (44, 4), (28, 14)], fill=255), cloth, bevel=1)                         # plume
        S.part(lambda d: d.polygon([(28, 6), (24, 18), (30, 14)], fill=255), shift(cloth, .85), bevel=0)
        return S.image(C(8, 8, 14), thick=1)
    if role == 'mage':
        robe = C(86, 62, 140); skin = C(226, 176, 136); gold = C(226, 182, 70); leath = C(96, 66, 44)
        S.part(lambda d: d.polygon([(26, 28), (48, 28), (60, 120), (14, 120)], fill=255), robe, bevel=2, dither=.7)
        for fx in (22, 30, 38, 46): S.line((fx, 60), (fx - 6 + (fx % 3), 118), shift(robe, .62))
        S.part(lambda d: d.polygon([(24, 56), (50, 56), (52, 62), (22, 62)], fill=255), leath, bevel=1)
        S.part(lambda d: d.rectangle([34, 56, 40, 62], fill=255), gold, bevel=0)
        S.part(lambda d: d.polygon([(40, 70), (62, 70), (70, 118), (36, 118)], fill=255), shift(robe, 1.15), bevel=1, dither=.5)
        S.part(lambda d: d.polygon([(44, 28), (58, 30), (64, 54), (56, 58), (50, 40)], fill=255), robe, bevel=1)          # arm
        S.part(lambda d: d.ellipse([60, 52, 68, 60], fill=255), skin, bevel=1)
        S.part(lambda d: d.rectangle([66, 8, 69, 118], fill=255), C(120, 80, 50), bevel=1)                              # staff
        S.part(lambda d: d.ellipse([60, 0, 76, 16], fill=255), C(110, 220, 255), bevel=2, spec=(64, 4))
        S.part(lambda d: d.polygon([(24, 22), (50, 22), (54, 34), (22, 34)], fill=255), shift(robe, .8), bevel=1)         # mantle
        S.part(lambda d: d.ellipse([28, 6, 48, 26], fill=255), skin, bevel=1)
        S.part(lambda d: d.polygon([(28, 22), (48, 22), (46, 40), (38, 46), (30, 40)], fill=255), C(230, 230, 236), bevel=1, dither=.4)   # beard
        S.part(lambda d: d.polygon([(24, 12), (52, 12), (46, 6), (40, -6), (32, 4), (28, 6)], fill=255), robe, bevel=1)    # hat
        S.part(lambda d: d.ellipse([18, 9, 58, 17], fill=255), shift(robe, .8), bevel=1)
        S.part(lambda d: d.rectangle([38, 14, 46, 15], fill=255), C(10, 10, 16), bevel=0)
        return S.image(C(8, 8, 14), thick=1)
    # orc warlord: bigger, bare chest with plates, a huge cleaver
    skin = C(104, 150, 74); dark = C(60, 66, 80); leath = C(96, 66, 44); bone = C(226, 218, 190)
    S2 = Sprite(100, 126); G = 124; S = S2
    S.part(lambda d: d.polygon([(30, 70), (44, 70), (46, 112), (28, 112)], fill=255), shift(skin, .8), bevel=1)
    S.part(lambda d: d.polygon([(48, 70), (66, 70), (70, 112), (48, 112)], fill=255), skin, bevel=1, dither=.4)
    S.part(lambda d: d.polygon([(24, 112), (46, 112), (48, G), (22, G)], fill=255), leath, bevel=1)
    S.part(lambda d: d.polygon([(46, 112), (74, 112), (82, G), (46, G)], fill=255), leath, bevel=1)
    S.part(lambda d: d.polygon([(28, 58), (70, 58), (74, 78), (26, 78)], fill=255), leath, bevel=1)                 # kilt
    for x in range(30, 70, 6): S.line((x, 62), (x - 1, 77), shift(leath, .6))
    S.part(lambda d: d.polygon([(20, 22), (74, 22), (78, 42), (70, 60), (28, 60), (20, 42)], fill=255), skin, bevel=2, dither=.5)  # chest
    S.line((49, 26), (49, 58), shift(skin, .7))
    S.part(lambda d: d.polygon([(30, 30), (68, 30), (64, 52), (34, 52)], fill=255), dark, bevel=1, dither=.4)       # chest plate
    for x in (36, 48, 60): S.put(x, 34, bone)
    S.part(lambda d: d.ellipse([10, 16, 38, 40], fill=255), dark, bevel=2, spec=(15, 20))                           # pauldrons
    S.part(lambda d: d.ellipse([60, 14, 90, 40], fill=255), dark, bevel=2, spec=(66, 18))
    for sx in (18, 74): S.part(lambda d, sx=sx: d.polygon([(sx, 18), (sx + 4, 18), (sx + 2, 8)], fill=255), bone, bevel=0)
    S.part(lambda d: d.polygon([(68, 34), (84, 40), (92, 70), (80, 74), (74, 52)], fill=255), skin, bevel=1)         # arm
    S.part(lambda d: d.ellipse([78, 68, 92, 82], fill=255), shift(skin, 1.05), bevel=1)
    S.part(lambda d: d.rectangle([84, 40, 88, 86], fill=255), C(120, 80, 50), bevel=1)                              # haft
    S.part(lambda d: d.polygon([(84, 40), (98, 36), (100, 6), (84, 10)], fill=255), C(150, 156, 170), bevel=1, dither=.4)   # cleaver
    S.line((96, 30), (88, 12), C(220, 224, 236))
    S.part(lambda d: d.polygon([(10, 36), (24, 34), (26, 56), (14, 70), (8, 56)], fill=255), shift(skin, .8), bevel=1)
    S.part(lambda d: d.ellipse([28, 2, 62, 30], fill=255), skin, bevel=2, spec=(34, 7))                             # head
    S.part(lambda d: d.polygon([(30, 8), (58, 6), (60, 14), (28, 16)], fill=255), dark, bevel=1)                    # helm band
    S.part(lambda d: d.polygon([(40, 4), (48, -4), (52, 6)], fill=255), bone, bevel=0)
    S.part(lambda d: d.rectangle([44, 16, 54, 19], fill=255), C(60, 90, 40), bevel=0)                               # heavy brow
    S.part(lambda d: d.rectangle([48, 18, 52, 21], fill=255), C(255, 200, 70), bevel=0)
    S.part(lambda d: d.polygon([(34, 24), (60, 24), (58, 30), (36, 30)], fill=255), shift(skin, .75), bevel=1)     # jaw
    S.part(lambda d: d.polygon([(40, 24), (43, 24), (42, 14)], fill=255), bone, bevel=0)
    S.part(lambda d: d.polygon([(52, 24), (55, 24), (54, 15)], fill=255), bone, bevel=0)
    return S.image(C(8, 8, 14), thick=1)


# ------------------------------------------------------------------------------------------------ style 4: gothic, slender
def gothic(role):
    S = Sprite(44, 92); G = 90
    coal = C(34, 32, 44); wine = C(122, 24, 38); bone = C(220, 210, 186); steel = C(130, 132, 150)
    if role == 'knight':
        S.part(lambda d: d.polygon([(14, 24), (22, 24), (16, 84), (2, 80), (6, 44)], fill=255), wine, bevel=1, dither=.5)      # cloak
        S.part(lambda d: d.polygon([(18, 52), (22, 52), (22, 84), (18, 84)], fill=255), shift(coal, .7), bevel=0)
        S.part(lambda d: d.polygon([(24, 52), (29, 52), (29, 84), (24, 84)], fill=255), coal, bevel=0)
        S.part(lambda d: d.polygon([(17, 84), (23, 84), (26, G), (14, G)], fill=255), C(18, 16, 22), bevel=0)
        S.part(lambda d: d.polygon([(24, 84), (29, 84), (38, G), (24, G)], fill=255), C(18, 16, 22), bevel=0)
        S.part(lambda d: d.polygon([(16, 24), (30, 24), (32, 54), (30, 62), (16, 62), (14, 54)], fill=255), coal, bevel=1, dither=.5)   # long coat
        S.part(lambda d: d.polygon([(18, 26), (30, 26), (28, 44), (20, 44)], fill=255), steel, bevel=1)                         # a cuirass
        S.part(lambda d: d.polygon([(14, 18), (32, 18), (34, 26), (12, 26)], fill=255), wine, bevel=1)                          # high collar
        S.part(lambda d: d.polygon([(30, 28), (34, 28), (36, 46), (32, 46)], fill=255), coal, bevel=0)                          # arm
        S.part(lambda d: d.rectangle([34, 44, 38, 48], fill=255), steel, bevel=0)
        S.part(lambda d: d.polygon([(37, 46), (39, 46), (42, 2), (40, 0)], fill=255), C(214, 220, 232), bevel=0)               # a long blade
        S.part(lambda d: d.rectangle([34, 46, 42, 47], fill=255), C(180, 150, 70), bevel=0)
        S.part(lambda d: d.ellipse([18, 6, 30, 20], fill=255), coal, bevel=1)                                                  # helm: a beaked mask
        S.part(lambda d: d.polygon([(28, 10), (38, 16), (28, 18)], fill=255), bone, bevel=0)
        S.part(lambda d: d.polygon([(20, 8), (14, 2), (18, 10)], fill=255), wine, bevel=0)
        S.put(26, 11, C(230, 60, 50)); S.put(27, 11, C(230, 60, 50))
        return S.image(None)
    if role == 'mage':
        S.part(lambda d: d.polygon([(14, 22), (30, 22), (40, G), (4, G)], fill=255), coal, bevel=1, dither=.8)
        S.part(lambda d: d.polygon([(22, 24), (28, 24), (30, G), (20, G)], fill=255), wine, bevel=0)                          # a split dress
        S.part(lambda d: d.polygon([(10, 22), (34, 22), (30, 34), (14, 34)], fill=255), shift(coal, 1.2), bevel=1)
        S.part(lambda d: d.rectangle([34, 6, 35, 88], fill=255), C(110, 90, 70), bevel=0)                                      # staff with a lantern
        S.part(lambda d: d.rectangle([32, 0, 38, 10], fill=255), C(255, 190, 80), bevel=1)
        S.part(lambda d: d.polygon([(30, 30), (36, 30), (36, 44), (32, 44)], fill=255), coal, bevel=0)
        S.part(lambda d: d.ellipse([18, 8, 28, 22], fill=255), bone, bevel=1)
        S.part(lambda d: d.polygon([(6, 12), (36, 12), (30, 8), (20, -6), (16, 8)], fill=255), coal, bevel=1)                   # wide hat
        S.part(lambda d: d.rectangle([16, 8, 26, 10], fill=255), wine, bevel=0)
        S.put(25, 14, C(20, 14, 20)); S.put(24, 14, C(20, 14, 20))
        return S.image(None)
    S.part(lambda d: d.polygon([(12, 24), (32, 24), (38, 90), (4, 90)], fill=255), C(52, 40, 40), bevel=1, dither=.8)          # executioner, hooded
    S.part(lambda d: d.polygon([(10, 20), (34, 20), (34, 38), (10, 38)], fill=255), C(70, 52, 48), bevel=1)
    S.part(lambda d: d.polygon([(14, 4), (30, 4), (34, 22), (10, 22)], fill=255), C(30, 24, 28), bevel=1)                     # hood
    S.part(lambda d: d.rectangle([20, 12, 28, 14], fill=255), C(0, 0, 0), bevel=0)
    S.put(26, 13, C(230, 60, 50))
    S.part(lambda d: d.polygon([(30, 30), (36, 30), (38, 56), (34, 56)], fill=255), C(52, 40, 40), bevel=0)
    S.part(lambda d: d.rectangle([38, 8, 40, 80], fill=255), C(100, 76, 56), bevel=0)                                          # axe haft
    S.part(lambda d: d.polygon([(40, 10), (44, 14), (44, 34), (40, 38)], fill=255), steel, bevel=0)
    return S.image(None)


# ------------------------------------------------------------------------------------------------ style 5: cartoon brawler
def brawler(role):
    S = Sprite(72, 76); G = 74
    if role == 'knight':
        steel = C(170, 190, 224); red = C(214, 44, 56); gold = C(255, 210, 60); boot = C(120, 70, 40)
        S.part(lambda d: d.rounded_rectangle([20, 46, 31, 64], 3, fill=255), shift(steel, .8), bevel=2)
        S.part(lambda d: d.rounded_rectangle([34, 46, 46, 64], 3, fill=255), steel, bevel=2)
        S.part(lambda d: d.rounded_rectangle([14, 62, 33, G], 5, fill=255), boot, bevel=2)
        S.part(lambda d: d.rounded_rectangle([32, 62, 54, G], 5, fill=255), boot, bevel=2)
        S.part(lambda d: d.rounded_rectangle([16, 24, 48, 52], 7, fill=255), steel, bevel=2, dither=.4)
        S.part(lambda d: d.polygon([(26, 30), (40, 30), (43, 52), (23, 52)], fill=255), red, bevel=1)
        S.part(lambda d: d.rectangle([16, 44, 48, 48], fill=255), gold, bevel=1)
        S.part(lambda d: d.ellipse([6, 26, 22, 42], fill=255), shift(steel, .85), bevel=2)            # far fist
        S.part(lambda d: d.rounded_rectangle([44, 26, 58, 40], 5, fill=255), steel, bevel=2)
        S.part(lambda d: d.polygon([(54, 38), (60, 36), (68, 2), (60, 0), (56, 8)], fill=255), C(240, 244, 252), bevel=1)   # big sword
        S.part(lambda d: d.rectangle([48, 36, 66, 40], fill=255), gold, bevel=1)
        S.part(lambda d: d.ellipse([50, 34, 64, 48], fill=255), steel, bevel=2)                     # fist
        S.part(lambda d: d.ellipse([14, 2, 50, 36], fill=255), steel, bevel=2, spec=(22, 8))        # helm
        S.part(lambda d: d.rectangle([32, 14, 50, 22], fill=255), C(20, 20, 30), bevel=0)           # visor
        S.part(lambda d: d.polygon([(18, 6), (8, 0), (6, 16), (16, 18)], fill=255), red, bevel=1)    # plume
        return S.image((14, 12, 20), thick=2)
    if role == 'mage':
        robe = C(140, 70, 210); gold = C(255, 210, 60); skin = C(255, 208, 170)
        S.part(lambda d: d.polygon([(16, 26), (50, 26), (58, G), (8, G)], fill=255), robe, bevel=2, dither=.4)
        S.part(lambda d: d.rectangle([16, 46, 50, 51], fill=255), gold, bevel=1)
        S.part(lambda d: d.rounded_rectangle([46, 28, 60, 42], 5, fill=255), shift(robe, 1.1), bevel=1)
        S.part(lambda d: d.ellipse([54, 34, 66, 46], fill=255), skin, bevel=2)
        S.part(lambda d: d.rectangle([62, 6, 66, 72], fill=255), C(150, 100, 56), bevel=1)
        S.part(lambda d: d.ellipse([54, -2, 72, 14], fill=255), C(90, 240, 255), bevel=2, spec=(58, 2))
        S.part(lambda d: d.ellipse([16, 8, 50, 36], fill=255), skin, bevel=2)
        S.part(lambda d: d.polygon([(12, 22), (54, 22), (46, 14), (30, -10), (22, 12)], fill=255), robe, bevel=2)   # hat
        S.part(lambda d: d.ellipse([6, 18, 60, 28], fill=255), shift(robe, .8), bevel=1)
        S.part(lambda d: d.polygon([(20, 30), (46, 30), (42, 48), (33, 56), (24, 48)], fill=255), C(244, 244, 250), bevel=2)   # beard
        S.part(lambda d: d.rectangle([34, 22, 44, 25], fill=255), C(20, 20, 30), bevel=0)
        return S.image((14, 12, 20), thick=2)
    skin = C(104, 190, 70); leath = C(160, 96, 50); ivory = C(250, 244, 220)
    S.part(lambda d: d.rounded_rectangle([18, 48, 31, 66], 4, fill=255), shift(skin, .8), bevel=2)
    S.part(lambda d: d.rounded_rectangle([34, 48, 48, 66], 4, fill=255), skin, bevel=2)
    S.part(lambda d: d.rounded_rectangle([12, 64, 33, G], 5, fill=255), C(90, 60, 40), bevel=2)
    S.part(lambda d: d.rounded_rectangle([32, 64, 56, G], 5, fill=255), C(90, 60, 40), bevel=2)
    S.part(lambda d: d.rounded_rectangle([12, 24, 52, 54], 10, fill=255), skin, bevel=2, dither=.4)
    S.part(lambda d: d.polygon([(18, 26), (48, 26), (50, 52), (16, 52)], fill=255), leath, bevel=1)
    S.part(lambda d: d.rectangle([14, 46, 50, 50], fill=255), C(60, 40, 30), bevel=1)
    S.part(lambda d: d.ellipse([2, 26, 22, 48], fill=255), shift(skin, .85), bevel=2)
    S.part(lambda d: d.rounded_rectangle([46, 26, 62, 42], 6, fill=255), skin, bevel=2)
    S.part(lambda d: d.rectangle([60, 10, 66, 50], fill=255), C(140, 90, 52), bevel=1)                            # club
    S.part(lambda d: d.ellipse([52, 0, 72, 22], fill=255), C(120, 78, 44), bevel=2)
    for sx, sy in ((56, 4), (66, 4), (60, 14), (70, 14)): S.part(lambda d, sx=sx, sy=sy: d.polygon([(sx, sy + 2), (sx + 3, sy + 2), (sx + 1, sy - 3)], fill=255), ivory, bevel=0)
    S.part(lambda d: d.ellipse([54, 40, 68, 54], fill=255), shift(skin, 1.05), bevel=2)
    S.part(lambda d: d.ellipse([12, 4, 50, 38], fill=255), skin, bevel=2, spec=(20, 10))
    S.part(lambda d: d.rectangle([16, 6, 48, 12], fill=255), C(70, 76, 94), bevel=1)                              # iron cap
    S.part(lambda d: d.rectangle([28, 16, 46, 20], fill=255), C(50, 110, 40), bevel=0)
    S.part(lambda d: d.rectangle([34, 20, 38, 26], fill=255), C(255, 220, 70), bevel=0)
    S.part(lambda d: d.rectangle([42, 20, 46, 26], fill=255), C(255, 220, 70), bevel=0)
    S.put(36, 24, C(30, 10, 10)); S.put(44, 24, C(30, 10, 10))
    S.part(lambda d: d.rounded_rectangle([20, 28, 48, 36], 3, fill=255), shift(skin, .8), bevel=1)
    S.part(lambda d: d.polygon([(24, 28), (29, 28), (27, 18)], fill=255), ivory, bevel=0)
    S.part(lambda d: d.polygon([(40, 28), (45, 28), (43, 19)], fill=255), ivory, bevel=0)
    return S.image((14, 12, 20), thick=2)


# ------------------------------------------------------------------------------------------------ style 6: silhouette + rim light
def silhouette(role, rim=(255, 168, 80), eye=(120, 220, 255), ld=(1, -1)):
    S = Sprite(60, 84); G = 82; body = C(14, 14, 24); body2 = C(26, 28, 46); ld = tuple(ld)     # light from the right and above
    def P(draw, base=body, bevel=2): S.part(draw, base, shade=body, light=rim, bevel=bevel, ld=ld)
    if role == 'knight':
        P(lambda d: d.polygon([(14, 26), (24, 26), (16, 80), (2, 76), (6, 44)], fill=255), body2)                 # cape
        P(lambda d: d.polygon([(24, 56), (32, 56), (30, G), (22, G)], fill=255), body2)
        P(lambda d: d.polygon([(34, 56), (42, 56), (48, G), (36, G)], fill=255))
        P(lambda d: d.polygon([(18, 26), (40, 26), (42, 44), (38, 58), (20, 58), (16, 44)], fill=255), body2 if False else body)
        P(lambda d: d.ellipse([34, 20, 48, 34], fill=255))                                                       # pauldron
        P(lambda d: d.polygon([(40, 30), (48, 34), (52, 48), (46, 50)], fill=255))
        P(lambda d: d.polygon([(48, 46), (54, 46), (58, 2), (55, 0), (51, 6)], fill=255), C(230, 240, 255))      # blade catching the light
        P(lambda d: d.ellipse([20, 6, 38, 26], fill=255))                                                         # helm
        P(lambda d: d.polygon([(20, 8), (10, 2), (14, 16), (20, 16)], fill=255))                                 # plume
        for k in range(3): S.put(35 + k, 14, eye); S.put(35 + k, 15, eye)
        return S.image(None)
    if role == 'mage':
        P(lambda d: d.polygon([(18, 26), (40, 26), (48, G), (10, G)], fill=255))
        P(lambda d: d.ellipse([22, 10, 38, 28], fill=255))
        P(lambda d: d.polygon([(14, 16), (46, 16), (38, 12), (32, -2), (26, 12)], fill=255))                     # hat
        P(lambda d: d.polygon([(38, 28), (46, 32), (50, 46), (44, 48)], fill=255))
        P(lambda d: d.rectangle([50, 10, 52, 80], fill=255))
        S.part(lambda d: d.ellipse([46, 2, 56, 12], fill=255), C(255, 120, 50), light=C(255, 230, 150), shade=C(200, 60, 20), bevel=1)
        for k in range(2): S.put(33 + k * 3, 18, eye); S.put(33 + k * 3, 19, eye)
        return S.image(None)
    P(lambda d: d.polygon([(18, 60), (32, 60), (30, G), (14, G)], fill=255), body2)
    P(lambda d: d.polygon([(36, 60), (50, 60), (54, G), (36, G)], fill=255))
    P(lambda d: d.polygon([(10, 24), (50, 24), (56, 50), (46, 64), (16, 64), (6, 50)], fill=255))
    P(lambda d: d.ellipse([2, 14, 24, 36], fill=255)); P(lambda d: d.ellipse([40, 12, 62, 34], fill=255))        # shoulders
    P(lambda d: d.polygon([(50, 34), (58, 40), (58, 66), (50, 62)], fill=255))
    P(lambda d: d.polygon([(56, 20), (60, 22), (60, 62), (56, 62)], fill=255))                                 # a long cleaver
    P(lambda d: d.ellipse([20, 2, 44, 28], fill=255))
    P(lambda d: d.polygon([(22, 10), (16, 0), (26, 6)], fill=255)); P(lambda d: d.polygon([(40, 8), (46, -2), (44, 12)], fill=255))   # horns
    for k in range(2): S.put(32 + k * 5, 14, (255, 70, 50)); S.put(32 + k * 5, 15, (255, 70, 50))
    return S.image(None)


STYLES = [
    ('chibi', 'Chibi heroico', chibi, 'cabecas enormes, corpo minusculo, contornos coloridos, olhos grandes: adoravel, mas ainda heroi'),
    ('minimo', 'Minimo 4 cores', gameboy, 'sprites de 16x24 com 4 tons de verde (LCD portatil): so silhueta e uma ideia por personagem'),
    ('detalhado', 'Detalhado 7 cabecas', detailed, 'proporcao realista, placas sobrepostas, cota de malha, dobras de capa, luz e sombra por material'),
    ('gotico', 'Gotico esguio', gothic, 'figuras altas e finas, casacos longos, sem contorno, so silhueta e uma cor de sangue'),
    ('brutamontes', 'Brutamontes cartum', brawler, 'formas grossas e saturadas, contorno grosso, punhos enormes: estilo de briga de arcade'),
    ('silhueta', 'Silhueta e luz de contorno', silhouette, 'corpos quase pretos; so a borda iluminada pelo sol e os olhos brilham'),
]
ROLES = ('knight', 'mage', 'orc')


# ------------------------------------------------------------------------------------------------ scenes
GY = 217                                               # ground line of the 480x270 scenes


def put_sprite(sc, im, x, base_y=GY, flip=False, scale=1):
    if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    if flip: im = mirror(im)
    sc.blit(im, int(x - im.width // 2), int(base_y - im.height + 1))


def sparks(sc, cx, cy, col, n=14, r=14, seed=1):
    rnd = random.Random(seed)
    for _ in range(n):
        a = rnd.uniform(0, math.tau); d_ = rnd.uniform(3, r)
        sc.put(int(cx + math.cos(a) * d_), int(cy + math.sin(a) * d_ * .8), col)


def star(sc, cx, cy, r, col, col2):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    sc.d.polygon(pts, fill=tuple(col) + (255,))
    pts2 = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55) for x, y in pts]
    sc.d.polygon(pts2, fill=tuple(col2) + (255,))


def clouds(sc, seed, col, n=5, y0=20, y1=90):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.randint(0, PG.W); y = rnd.randint(y0, y1)
        for k in range(4):
            sc.d.ellipse([x + k * 14, y - (k % 2) * 4, x + k * 14 + 26, y + 12 - (k % 2) * 2], fill=tuple(col) + (255,))
        sc.d.rectangle([x + 6, y + 6, x + 60, y + 12], fill=tuple(col) + (255,))


def scene_chibi():
    s = PG.Scene(3)
    s.vgrad(0, 170, (96, 176, 255), (214, 238, 255), levels=7)
    clouds(s, 4, (255, 255, 255), 5)
    s.hills(170, (126, 210, 130), (20, 9, 5), 5, top_col=(160, 232, 150))
    s.castle(300, 170, 1.2, (214, 190, 214), win=(255, 230, 120), seed=3)
    s.hills(190, (88, 184, 100), (12, 6, 3), 9, top_col=(130, 214, 120))
    g = PG.make_grade(sat=1.25, val=1.25)
    tile = PG.grade_image(PG.prop('grass_tile'), g)
    s.tile_ground(tile, GY - 3, g, dark_below=(110, 82, 54))
    PG.prop_at(s, 'oak', 60, PG.make_grade(sat=1.3, val=1.3)); PG.prop_at(s, 'bush', 440, PG.make_grade(sat=1.3, val=1.3))
    put_sprite(s, chibi('mage'), 70); put_sprite(s, chibi('knight'), 150)
    put_sprite(s, chibi('orc'), 290, flip=True)
    star(s, 215, GY - 38, 16, (255, 230, 90), (255, 255, 200)); sparks(s, 215, GY - 38, (255, 255, 255), 10, 26)
    return s


def scene_minimo(path):
    w0, h0 = PG.W, PG.H
    PG.W, PG.H = 160, 90
    try:
        s = PG.Scene(1); D, M, L, Wt = GB
        s.rect(0, 0, 160, 90, Wt)
        for k in range(0, 160, 2):                                         # a dithered sky
            for y in range(0, 50):
                if (k + y) % 2 == 0 and y > 30 - (k % 3): s.put(k, y, L)
        for cx, cy in ((20, 12), (90, 8), (130, 18)):                      # clouds
            s.rect(cx, cy, cx + 14, cy + 2, L); s.rect(cx + 3, cy - 2, cx + 10, cy, L)
        s.hills(58, M, (6, 3), 7); s.hills(66, L, (4, 2), 8, top_col=M)
        s.castle(98, 62, 0.55, D, win=Wt, seed=5)
        s.rect(0, 72, 160, 90, M)
        for x in range(0, 160, 8): s.rect(x, 72, x + 3, 73, D)             # path stones
        s.rect(0, 74, 160, 74, D)
        for x in range(0, 160, 6):
            for y in range(76, 90, 4):
                if (x // 6 + y // 4) % 2: s.rect(x, y, x + 2, y + 1, D)
        put_sprite(s, gameboy('mage'), 24, 73); put_sprite(s, gameboy('knight'), 52, 73)
        put_sprite(s, gameboy('orc'), 100, 73, flip=True)
        for dx, dy in ((74, 58), (75, 57), (76, 56), (77, 57), (78, 58), (76, 60)): s.put(dx, dy, D)    # a slash
        s.rect(75, 58, 77, 58, Wt)
        big = s.im.convert('RGB').resize((160 * 9, 90 * 9), Image.NEAREST)
    finally:
        PG.W, PG.H = w0, h0
    PG.caption(big, 'Estilo Minimo 4 cores', 'sprites de 16x24, 4 tons de LCD, tela de 160x90')
    PG.safe_save(big, path)


def scene_detalhado():
    s = PG.Scene(11)
    s.vgrad(0, 160, (10, 12, 26), (110, 76, 80), levels=9)
    s.glow(300, 150, 120, (255, 160, 90), 0.5)
    s.castle(230, 168, 2.0, (30, 28, 42), win=(255, 190, 90), seed=4)
    s.hills(180, (24, 24, 34), (14, 7, 3), 9, top_col=(52, 48, 60))
    s.fog(140, 215, (110, 100, 120), 0.6)
    g = PG.make_grade(sat=0.5, val=0.55, contrast=1.1)
    tile = PG.grade_image(PG.prop('street_tile'), g)
    s.tile_ground(tile, GY - 3, g, dark_below=(14, 12, 18))
    for tx in (60, 420):
        s.rect(tx - 1, 150, tx + 1, 166, (60, 40, 28)); s.rect(tx - 3, 142, tx + 3, 150, (255, 190, 80)); s.put(tx, 140, (255, 240, 170))
        s.glow(tx, 148, 90, (255, 170, 70), 0.9)
    put_sprite(s, detailed('mage'), 90); put_sprite(s, detailed('knight'), 180); put_sprite(s, detailed('orc'), 330, flip=True)
    sparks(s, 255, GY - 70, (255, 244, 200), 18, 22); sparks(s, 255, GY - 70, (255, 190, 90), 10, 30, 4)
    s.dots(40, (255, 190, 100), 8, 215)
    s.vignette(0.7)
    return s


def scene_gotico():
    s = PG.Scene(21)
    s.vgrad(0, 170, (8, 4, 12), (84, 18, 32), levels=10)
    s.d.ellipse([330, 24, 420, 114], fill=(226, 214, 190, 255)); s.d.ellipse([348, 40, 440, 126], fill=(40, 10, 22, 255))
    s.glow(375, 70, 140, (200, 60, 70), 0.45)
    s.hills(176, (20, 8, 18), (16, 8, 4), 3)
    s.castle(40, 176, 2.4, (10, 4, 10), win=(230, 60, 50), seed=9)
    s.pines(196, (8, 4, 10), 8, 11, 70, 120)
    s.fog(150, 218, (120, 40, 60), 0.5, seed=4)
    g = PG.make_grade(sat=0.4, val=0.5, tint=(1.1, 0.8, 0.9))
    tile = PG.grade_image(PG.prop('street_tile'), g)
    s.tile_ground(tile, GY - 3, g, dark_below=(8, 4, 8))
    PG.prop_at(s, 'dead_tree', 440, PG.make_grade(sat=0.3, val=0.35)); PG.prop_at(s, 'lamppost', 230, PG.make_grade(sat=0.4, val=0.5))
    put_sprite(s, gothic('knight'), 150); put_sprite(s, gothic('mage'), 90); put_sprite(s, gothic('orc'), 330, flip=True)
    s.dots(80, (200, 90, 100), 6, 215)
    s.vignette(0.8)
    return s


def scene_brutamontes():
    s = PG.Scene(31)
    s.vgrad(0, 170, (70, 150, 255), (170, 226, 255), levels=6)
    s.d.ellipse([380, 20, 430, 70], fill=(255, 226, 80, 255))
    clouds(s, 9, (255, 255, 255), 4)
    s.hills(168, (70, 190, 80), (18, 8, 5), 2, top_col=(120, 230, 110))
    s.hills(190, (40, 150, 60), (10, 5, 3), 6, top_col=(90, 200, 90))
    g = PG.make_grade(sat=1.5, val=1.2)
    tile = PG.grade_image(PG.prop('grass_tile'), g)
    s.tile_ground(tile, GY - 3, g, dark_below=(130, 84, 50))
    PG.prop_at(s, 'oak', 410, PG.make_grade(sat=1.5, val=1.25)); PG.prop_at(s, 'banner', 40, PG.make_grade(sat=1.4, val=1.2))
    put_sprite(s, brawler('mage'), 80); put_sprite(s, brawler('knight'), 175); put_sprite(s, brawler('orc'), 310, flip=True)
    star(s, 242, GY - 52, 18, (255, 240, 70), (255, 140, 40))
    return s


def scene_silhueta():
    s = PG.Scene(41)
    s.vgrad(0, 190, (24, 8, 44), (255, 150, 70), levels=11)
    s.d.ellipse([310, 96, 410, 196], fill=(255, 236, 170, 255))
    s.glow(360, 146, 190, (255, 190, 100), 0.7)
    s.hills(180, (30, 12, 36), (20, 9, 5), 4)
    s.castle(380, 190, 1.8, (18, 8, 26), win=None, seed=2)
    s.hills(200, (18, 8, 26), (10, 5, 3), 8, top_col=(220, 100, 60))
    s.rect(0, GY + 1, 480, 270, (14, 8, 20))
    for y in range(GY + 1, 250):                                           # the sun's reflection on the ground, dithered
        for x in range(240, 480):
            k = 1 - (y - GY) / 34.0
            if k > 0 and k * (1 - abs(x - 360) / 120.0) > (PG.BAYER[y % 4][x % 4] + .5) / 16: s.put(x, y, (255, 150, 70))
    put_sprite(s, silhouette('mage'), 90); put_sprite(s, silhouette('knight'), 170)
    put_sprite(s, silhouette('orc', ld=(-1, -1)), 275, flip=True)
    s.dots(60, (255, 180, 100), 3, 215)
    return s


SCENES = [('chibi', scene_chibi, '01_chibi', 'Estilo Chibi heroico', 'cabecas enormes, corpo minusculo, contornos coloridos'),
          ('detalhado', scene_detalhado, '03_detalhado', 'Estilo Detalhado 7 cabecas', 'personagens com ~120 px, placas, malha, capas e luz por material'),
          ('gotico', scene_gotico, '04_gotico', 'Estilo Gotico esguio', 'figuras altas e finas, sem contorno, so uma cor de sangue'),
          ('brutamontes', scene_brutamontes, '05_brutamontes', 'Estilo Brutamontes cartum', 'formas grossas, contorno grosso, cores saturadas'),
          ('silhueta', scene_silhueta, '06_silhueta', 'Estilo Silhueta e luz de contorno', 'corpos quase pretos, so a borda iluminada e os olhos brilham')]


def lineup(path, scale=5):
    mscale = 9
    cell_w = 330; rows = len(STYLES)
    from PIL import ImageDraw as ID
    # first pass: sizes
    figs = {}
    for key, title, fn, desc in STYLES:
        figs[key] = [fn(r) for r in ROLES]
    row_h = [max(f.height for f in figs[k]) * (3 if k == 'detalhado' else 9 if k == 'minimo' else scale) + 50 for k, *_ in STYLES]
    img = Image.new('RGB', (cell_w * 3 + 200, sum(row_h)), (34, 36, 46)); d = ID.Draw(img)
    y = 0
    for (key, title, fn, desc), rh in zip(STYLES, row_h):
        d.text((8, y + 8), title, fill=(255, 240, 200)); d.text((8, y + 24), desc[:60], fill=(190, 190, 205))
        sc = 3 if key == 'detalhado' else (9 if key == 'minimo' else scale)
        for i, f in enumerate(figs[key]):
            big = f.resize((f.width * sc, f.height * sc), Image.NEAREST)
            bg = Image.new('RGBA', big.size, (0, 0, 0, 0)); bg.alpha_composite(big)
            img.paste(bg, (200 + i * cell_w + (cell_w - big.width) // 2, y + rh - big.height - 6), bg)
        y += rh
        d.line([(0, y - 1), (img.width, y - 1)], fill=(70, 72, 90))
    PG.safe_save(img, path)


def export_catalog(dest, out):
    """Per-role transparent PNGs (scaled) + the lineup and the scenes, for docs/PERSONAGENS.md."""
    import shutil
    os.makedirs(dest, exist_ok=True)
    zoom = dict(chibi=5, minimo=10, detalhado=3, gotico=4, brutamontes=4, silhueta=5)
    for key, title, fn, desc in STYLES:
        for role in ROLES:
            im = fn(role); sc = zoom[key]
            PG.safe_save(im.resize((im.width * sc, im.height * sc), Image.NEAREST), os.path.join(dest, f'{key}_{role}.png'))
    for f in os.listdir(out):
        if f.endswith('.png') and '_tmp' not in f and '_new' not in f and not f.endswith('_detalhe.png'): shutil.copyfile(os.path.join(out, f), os.path.join(dest, f))


def main():
    out = os.path.normpath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'out', 'art_estilos'))
    os.makedirs(out, exist_ok=True)
    lineup(os.path.join(out, '00_linha_de_estilos.png'))
    print('wrote lineup')
    for key, fn, fname, title, sub in SCENES:
        PG.finish(fn(), os.path.join(out, fname + '.png'), title, sub); print('wrote', fname)
    scene_minimo(os.path.join(out, '02_minimo.png')); print('wrote 02_minimo')
    export_catalog(os.path.normpath(os.path.join(HERE, '..', 'docs', 'personagens', 'estilos')), out)


if __name__ == '__main__':
    main()
