"""Projectile sprites (T04): arrow (+ rotated variants for lobbed shots), bolt, knife, fireball, rock.
Small transparent PNGs, facing RIGHT (the game mirrors them). Same outline / palette conventions as scenery_gen.py.

    python proj_gen.py [out_dir]
"""
import os, sys
from PIL import Image

out = sys.argv[1] if len(sys.argv) > 1 else './proj'
os.makedirs(out, exist_ok=True)


def C(r, g, b): return (r, g, b, 255)


OUT = C(18, 18, 30)
STEEL = C(214, 224, 238); STEEL_D = C(150, 164, 186); WOOD = C(190, 140, 80); WOOD_D = C(134, 86, 48)
RED = C(176, 38, 48); LEATH = C(116, 74, 44); GOLD = C(238, 192, 72)
FIRE_1 = C(255, 244, 190); FIRE_2 = C(255, 190, 70); FIRE_3 = C(232, 100, 40); FIRE_4 = C(160, 48, 36)
ROCK_1 = C(176, 180, 196); ROCK_2 = C(124, 130, 150); ROCK_3 = C(82, 88, 108)


def from_grid(rows, pal):
    w = max(len(r) for r in rows); im = Image.new('RGBA', (w, len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal: im.putpixel((x, y), pal[ch])
    return im


def outline(im):
    w, h = im.size; big = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); big.alpha_composite(im, (1, 1))
    px = big.load(); o = big.copy(); po = o.load()
    for y in range(h + 2):
        for x in range(w + 2):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w + 2 and 0 <= ny < h + 2 and px[nx, ny][3] > 0: po[x, y] = OUT; break
    return o


PAL = {'s': STEEL, 'S': STEEL_D, 'w': WOOD, 'W': WOOD_D, 'r': RED, 'l': LEATH, 'g': GOLD,
       'a': FIRE_1, 'b': FIRE_2, 'c': FIRE_3, 'd': FIRE_4, 'x': ROCK_1, 'y': ROCK_2, 'z': ROCK_3}

arrow = outline(from_grid([
    ".r.........",
    "rrwwwwwwsss",
    ".r.....W...",
], PAL))
bolt = outline(from_grid([
    "lll.....",
    "lwwwwsss",
    "lll.....",
], PAL))
knife = outline(from_grid([
    ".......s.",
    "llggssss.",
    ".......S.",
], PAL))
FB_ROWS = [
    "..d....dcd..",
    ".dd..dccbcd.",
    "dccdcbbbabcd",
    ".dd..dccbcd.",
    "..d....dcd..",
]
fireball = outline(from_grid(FB_ROWS, PAL))                      # a flame head with a ragged tail behind it
_fb = from_grid(FB_ROWS, PAL)
fireball_big = outline(_fb.resize((_fb.width * 2, _fb.height * 2), Image.NEAREST))   # 3rd fireball of the mage: twice as big
rock = outline(from_grid([
    ".xxy.",
    "xxyyz",
    "xyyzz",
    ".yzz.",
], PAL))


def rot(im, ang):
    big = im.rotate(ang, expand=True, resample=Image.NEAREST)
    return big


bomb = outline(from_grid([
    "....g.",
    "...gs.",
    ".zzzz.",
    "zxyyyz",
    "zyyyyz",
    "zyyyyz",
    ".zzzz.",
], dict(PAL, g=GOLD, s=C(255, 120, 60), z=C(20, 20, 30), x=C(120, 124, 148), y=C(54, 56, 72))))

sprites = {'bomb': bomb, 'arrow': arrow, 'bolt': bolt, 'knife': knife, 'fireball': fireball, 'fireball_big': fireball_big, 'rock': rock,
           'arrow_u45': rot(arrow, 45), 'arrow_u90': rot(arrow, 90),
           'arrow_d45': rot(arrow, -45), 'arrow_d90': rot(arrow, -90)}
for name, im in sprites.items():
    im.save(f'{out}/proj_{name}.png')
print('ok', len(sprites))
