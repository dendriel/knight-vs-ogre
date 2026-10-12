"""Chibi hero variations (static concepts, NOT used by the game).

Two groups, both built with the part painter of alt_styles.py (no game rig):
  R1-R5  "chibi realista": chibi proportions (head ~ 1/3 of the figure) but with the detail of a realistic drawing: layered
         plates, mail texture, straps, pouches, emblems, materials with their own light and shade.
  H1-H5  "chibi humanos": the equipment and the dark, muted look of the art_humanos styles (human_styles.py) on chibi bodies.

    python art_tools/chibi_variants.py [out_dir]       (default: out/art_chibi)
"""
import os, sys, math, random
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import proposals_gen as PG
from alt_styles import Sprite, shift, ramp, mirror, put_sprite, sparks, star, GY

SKIN = (236, 188, 148)
BLACK = (12, 10, 18)


def mailize(S, color, light=1.35, box=None):
    """chain-mail texture: a dither pattern on every pixel of `color` (inside the box if given)."""
    for y in range(S.h):
        for x in range(S.w):
            if box and not (box[0] <= x <= box[2] and box[1] <= y <= box[3]): continue
            if S.px[y][x] == color and (x + y) % 2 == 0: S.px[y][x] = shift(color, light)
            elif S.px[y][x] == color and (x // 2 + y) % 3 == 0: S.px[y][x] = shift(color, .8)


def eyes(S, x, y, kind, col=(30, 26, 44)):
    if kind == 'glow':
        for k in (0, 5): S.put(x + k, y, (255, 70, 50)); S.put(x + k + 1, y, (255, 70, 50)); S.put(x + k, y + 1, (255, 150, 90))
    elif kind == 'slit':
        for k in range(8): S.put(x + k, y, BLACK)
    else:                                                                     # two eyes, with a catch-light
        for k in (0, 6):
            S.part(lambda d, k=k: d.rectangle([x + k, y, x + k + 2, y + 4], fill=255), col, bevel=0)
            S.put(x + k + 1, y + 1, (255, 255, 255))


def build(v, role='hero'):
    """v: style dict (see R / H). role: 'hero' | 'orc' | 'foe' (the human enemy of the style, in its enemy colours)."""
    if role == 'orc': return build_orc(v)
    S = Sprite(72, 64)
    pal = v['pal'] if role != 'foe' else v.get('foe_pal', v['pal'])
    steel, cloth, trim, leath, skin = pal['steel'], pal['cloth'], pal['trim'], pal['leath'], pal.get('skin', SKIN)
    hh, hw, bw = v['hh'], v['hw'], v['bw']
    bev = v.get('bev', 1); dit = v.get('dither', 0.0)
    cx = 28; y_t = 2 + hh - 3; bh = v.get('bh', 16); y_h = y_t + bh
    legh = v.get('legh', 13); G = y_h + legh + 6
    ol = v.get('outline', 'tint')

    def P(draw, base, **kw):
        kw.setdefault('bevel', bev); kw.setdefault('dither', dit)
        S.part(draw, base, **kw)

    # ---- behind the body: cape and the shield on the back
    if v.get('cape'):
        P(lambda d: d.polygon([(cx - 5, y_t), (cx + 2, y_t + 1), (cx - 4, G - 3), (cx - 22, G - 5), (cx - 14, y_h)], fill=255), shift(cloth, .72), bevel=1, dither=.55)
        for k in range(3): S.line((cx - 5 - k * 3, y_t + 5 + k), (cx - 8 - k * 5, G - 6 + k % 2), shift(cloth, .5))
    if v.get('back_shield'):
        P(lambda d: d.polygon([(cx - 18, y_t + 1), (cx - 5, y_t - 1), (cx - 5, y_t + 11), (cx - 11, y_t + 19), (cx - 18, y_t + 11)], fill=255),
          v['pal'].get('shield', shift(cloth, .9)), bevel=1)
        S.put(cx - 11, y_t + 7, trim); S.put(cx - 12, y_t + 7, trim)
    # ---- legs
    lw = v.get('lw', 6)
    for i, (lx, tone) in enumerate(((cx - lw - 1, .76), (cx + 1, 1.0))):
        P(lambda d, lx=lx: d.rectangle([lx, y_h - 2, lx + lw, G - 6], fill=255), shift(steel, tone))
        if v.get('plates'):
            P(lambda d, lx=lx: d.ellipse([lx - 1, y_h + 2, lx + lw + 1, y_h + 8], fill=255), shift(steel, tone * 1.06), bevel=1)   # knee cop
            S.line((lx + 1, G - 12), (lx + lw - 1, G - 12), shift(steel, tone * .6))                                              # greave edge
        P(lambda d, lx=lx: d.rounded_rectangle([lx - 2, G - 7, lx + lw + 5, G], 2, fill=255), shift(leath, .82 if i == 0 else 1.0))
    # ---- torso
    body = steel if v.get('body', 'plate') == 'plate' else v['pal'].get('tunic', leath)
    P(lambda d: d.rounded_rectangle([cx - bw, y_t, cx + bw, y_h], 4, fill=255), body, bevel=2, dither=.5)
    if v.get('chest'):
        S.line((cx + 2, y_t + 3), (cx + 2, y_h - 3), shift(body, 1.35)); S.line((cx - 3, y_t + 3), (cx - 4, y_h - 4), shift(body, .72))
    if v.get('robe'):
        rb = v['pal'].get('robe', cloth)
        P(lambda d: d.polygon([(cx - bw - 1, y_t), (cx + bw + 1, y_t), (cx + bw + 6, G - 2), (cx - bw - 6, G - 2)], fill=255), rb, bevel=2, dither=.7)
        for k in range(-2, 3): S.line((cx + k * 4, y_h + 2), (cx + k * 5, G - 3), shift(rb, .62))
        P(lambda d: d.rectangle([cx - bw - 6, G - 5, cx + bw + 6, G - 3], fill=255), trim, bevel=0)
        for k in range(-3, 4): S.put(cx + k * 4, G - 4, shift(trim, .6))                                    # runes on the hem
    if v.get('tabard'):
        sk = v.get('skirt', 3)
        P(lambda d: d.polygon([(cx - 5, y_t + 3), (cx + 6, y_t + 3), (cx + 7, y_h + sk), (cx - 6, y_h + sk)], fill=255), cloth, bevel=1)
        if v.get('emblem') == 'cross':
            P(lambda d: d.rectangle([cx - 1, y_t + 4, cx + 2, y_h - 1], fill=255), trim, bevel=0)
            P(lambda d: d.rectangle([cx - 4, y_t + 7, cx + 5, y_t + 9], fill=255), trim, bevel=0)
        elif v.get('emblem') == 'stripe':
            P(lambda d: d.rectangle([cx - 5, y_t + 7, cx + 6, y_t + 9], fill=255), trim, bevel=0)
    if v.get('tassets'):
        for k in range(2):
            P(lambda d, k=k: d.polygon([(cx - bw - k, y_h - 1 + k * 3), (cx + bw + k, y_h - 1 + k * 3), (cx + bw + 2 + k, y_h + 3 + k * 3), (cx - bw - 2 - k, y_h + 3 + k * 3)], fill=255), steel, bevel=1)
    P(lambda d: d.rectangle([cx - bw, y_h - 4, cx + bw, y_h - 2], fill=255), leath, bevel=0)                  # belt
    S.put(cx + 1, y_h - 3, trim); S.put(cx + 2, y_h - 3, trim)
    if v.get('pouches'):
        P(lambda d: d.rectangle([cx - bw - 3, y_h - 3, cx - bw + 3, y_h + 4], fill=255), shift(leath, 1.1), bevel=1)
        P(lambda d: d.rectangle([cx + bw - 2, y_h - 3, cx + bw + 3, y_h + 3], fill=255), shift(leath, .9), bevel=1)
    if v.get('bandolier'):
        S.line((cx - bw + 1, y_t + 2), (cx + bw - 1, y_h - 4), shift(leath, .7)); S.line((cx - bw + 1, y_t + 3), (cx + bw - 1, y_h - 3), leath)
    if v.get('mail'): mailize(S, body)
    if v.get('quiver'):
        P(lambda d: d.rounded_rectangle([cx - bw - 9, y_t - 3, cx - bw - 2, y_t + 14], 2, fill=255), leath, bevel=1)
        for k in range(3): S.put(cx - bw - 8 + k * 2, y_t - 5, (220, 210, 190))
    # ---- far arm, near pauldron + arm (under the head)
    pr = v.get('pauld', 5)
    P(lambda d: d.rounded_rectangle([cx - bw - 4, y_t + 3, cx - bw + 2, y_h - 4], 2, fill=255), shift(steel, .72), bevel=1)
    P(lambda d: d.rounded_rectangle([cx + bw - 2, y_t + 5, cx + bw + 6, y_t + 15], 3, fill=255), steel, bevel=1)
    P(lambda d: d.ellipse([cx + bw - pr - 1, y_t + 1, cx + bw + pr, y_t + 2 * pr], fill=255), steel, bevel=2, spec=(cx + bw - pr + 1, y_t + 2))
    if v.get('lames'):
        for k in range(2):
            P(lambda d, k=k: d.rounded_rectangle([cx + bw - pr, y_t + 2 * pr - 3 + k * 3, cx + bw + pr + 1, y_t + 2 * pr + k * 3], 1, fill=255), shift(steel, .9), bevel=1)
    if v.get('spikes'):
        P(lambda d: d.polygon([(cx + bw - 2, y_t + 2), (cx + bw + 3, y_t + 2), (cx + bw, y_t - 6)], fill=255), shift(steel, 1.2), bevel=0)
    # ---- head
    hx0, hx1 = cx - hw, cx + hw; hy1 = 2 + hh
    helm = v.get('helm', 'bascinet')
    ey = 2 + int(hh * 0.52)                                             # eye line
    if helm in ('bascinet', 'winged'):
        P(lambda d: d.rectangle([hx0 + 3, hy1 - 8, hx1 - 2, y_t + 5], fill=255), shift(steel, .6), bevel=0); mailize(S, shift(steel, .6))
        P(lambda d: d.ellipse([hx0, 2, hx1, hy1], fill=255), steel, bevel=2, spec=(hx0 + 5, 6))
        P(lambda d: d.polygon([(cx + 1, ey - 4), (hx1 + 1, ey - 3), (hx1 + 1, hy1 - 3), (cx + 6, hy1 + 1), (cx + 1, hy1 - 5)], fill=255), shift(steel, .78), bevel=1)
        S.line((cx + 5, ey - 3), (hx1, ey - 2), BLACK); S.line((cx + 5, ey - 2), (hx1, ey - 1), (60, 70, 92))
        S.line((cx + 5, ey), (cx + 5, hy1 - 2), shift(steel, .55))
        for k in range(3): S.put(hx1 - 2, ey + 3 + k * 2, BLACK)
        if helm == 'winged':
            P(lambda d: d.polygon([(hx0 + 2, 10), (hx0 - 9, 2), (hx0 - 7, 15)], fill=255), trim, bevel=1)
            P(lambda d: d.polygon([(hx0 + 4, 15), (hx0 - 7, 10), (hx0 - 3, 20)], fill=255), shift(trim, 1.12), bevel=0)
        elif v.get('plume', True):
            P(lambda d: d.polygon([(hx0 + 5, 4), (hx0 - 6, 7), (hx0 - 8, 21), (hx0 + 2, 14)], fill=255), cloth, bevel=1)
    elif helm == 'kettle':
        P(lambda d: d.rectangle([hx0 + 3, hy1 - 8, hx1 - 3, y_t + 5], fill=255), shift(steel, .6), bevel=0)
        P(lambda d: d.ellipse([hx0 + 1, 6, hx1 - 1, hy1], fill=255), skin, bevel=1)
        P(lambda d: d.ellipse([hx0 + 1, 2, hx1 - 1, 2 + hh // 2 + 2], fill=255), steel, bevel=2, spec=(hx0 + 5, 5))
        P(lambda d: d.ellipse([hx0 - 7, 2 + hh // 2, hx1 + 7, 2 + hh // 2 + 6], fill=255), shift(steel, .88), bevel=1)
        eyes(S, cx + 1, ey + 3, 'dot'); S.put(cx + 9, ey + 8, (176, 100, 92)); S.put(cx + 10, ey + 8, (176, 100, 92))
    elif helm in ('greathelm', 'bucket'):
        P(lambda d: d.rounded_rectangle([hx0, 2, hx1, hy1], 6, fill=255), steel, bevel=2, spec=(hx0 + 4, 5))
        if helm == 'bucket':
            P(lambda d: d.rectangle([cx + 4, 6, cx + 7, hy1 - 3], fill=255), BLACK, bevel=0)
            P(lambda d: d.rectangle([cx - 1, ey - 1, hx1 - 1, ey + 2], fill=255), BLACK, bevel=0)
        else:
            P(lambda d: d.rectangle([cx - 1, ey - 1, hx1 - 1, ey + 2], fill=255), BLACK, bevel=0)
            S.line((cx + 5, ey + 4), (cx + 5, hy1 - 1), shift(steel, .6))
            for k in range(4): S.put(cx + 9, ey + 5 + k * 3, BLACK)
        for k in range(3): S.put(hx0 + 2, 6 + k * 6, trim)
        if v.get('plume'):
            P(lambda d: d.polygon([(cx - 9, 3), (cx + 2, 0), (cx + 2, 4), (cx - 15, 14)], fill=255), cloth, bevel=1)
    elif helm == 'coif':
        P(lambda d: d.ellipse([hx0, 2, hx1, hy1 + 1], fill=255), steel, bevel=2); mailize(S, steel)
        P(lambda d: d.ellipse([cx, ey - 5, hx1 - 1, hy1 - 3], fill=255), skin, bevel=1)
        eyes(S, cx + 2, ey, 'dot'); S.line((cx + 9, ey - 4), (cx + 9, ey + 4), shift(steel, 1.3))
    elif helm == 'hood':
        hood = v['pal'].get('hood', leath)
        P(lambda d: d.ellipse([hx0 - 1, 1, hx1 + 1, hy1 + 2], fill=255), hood, bevel=2, dither=.5)
        P(lambda d: d.ellipse([cx, ey - 5, hx1 - 1, hy1 - 2], fill=255), shift(skin, .85), bevel=1)
        P(lambda d: d.polygon([(hx0 + 2, 6), (hx0 - 7, 18), (hx0 + 4, 20)], fill=255), shift(hood, .8), bevel=0)
        eyes(S, cx + 2, ey, 'dot', (20, 16, 24))
        P(lambda d: d.rectangle([hx0 + 5, hy1 - 3, hx1 - 1, y_t + 6], fill=255), cloth, bevel=1)
    elif helm == 'horned':
        P(lambda d: d.ellipse([hx0, 2, hx1, hy1], fill=255), steel, bevel=2, spec=(hx0 + 5, 5))
        P(lambda d: d.polygon([(hx0 + 3, 9), (hx0 - 5, 2), (hx0 - 2, 0), (hx0 + 7, 5)], fill=255), (222, 214, 190), bevel=0)
        P(lambda d: d.polygon([(hx1 - 5, 6), (hx1 + 2, 0), (hx1 + 6, 3), (hx1 - 1, 10)], fill=255), (190, 182, 160), bevel=0)
        P(lambda d: d.rectangle([cx + 1, ey - 1, hx1, ey + 2], fill=255), (230, 50, 50), bevel=0); S.put(cx + 4, ey, (255, 200, 120))
        P(lambda d: d.rectangle([cx + 2, hy1 - 7, hx1 - 2, hy1], fill=255), shift(steel, .7), bevel=0)
    elif helm == 'fur':
        fur = v['pal'].get('fur', (150, 120, 86)); beard = v['pal'].get('beard', (190, 100, 50))
        P(lambda d: d.ellipse([hx0 + 1, 7, hx1, hy1], fill=255), skin, bevel=1)
        P(lambda d: d.ellipse([hx0 - 2, 1, hx1 + 2, 9 + hh // 3], fill=255), fur, bevel=2, dither=.6)
        P(lambda d: d.polygon([(cx + 1, ey + 5), (hx1, ey + 5), (hx1 - 2, hy1 + 7), (cx + 3, hy1 + 9)], fill=255), beard, bevel=1, dither=.5)
        eyes(S, cx + 2, ey - 1, 'dot'); S.line((cx + 2, ey - 3), (hx1 - 1, ey - 4), shift(beard, .6))
        P(lambda d: d.polygon([(hx0 + 4, 5), (hx0 - 3, 0), (hx0 + 9, 3)], fill=255), (222, 214, 190), bevel=0)
    elif helm == 'wizhat':
        hat = v['pal'].get('hat', cloth)
        P(lambda d: d.ellipse([hx0 + 2, 7, hx1, hy1], fill=255), skin, bevel=1)
        eyes(S, cx + 2, ey - 1, 'dot')
        P(lambda d: d.polygon([(cx + 2, ey + 6), (hx1, ey + 5), (hx1 - 3, hy1 + 8), (cx + 3, hy1 + 10), (cx - 3, hy1 + 3)], fill=255), (238, 238, 244), bevel=1, dither=.4)
        P(lambda d: d.polygon([(hx0 - 2, 11), (hx1 + 4, 11), (hx1 - 2, 7), (cx + 4, 0), (cx - 4, 7)], fill=255), hat, bevel=2, dither=.5)
        P(lambda d: d.ellipse([hx0 - 8, 8, hx1 + 8, 15], fill=255), shift(hat, .8), bevel=1)
        P(lambda d: d.rectangle([cx - 7, 8, cx + 8, 10], fill=255), trim, bevel=0)
    # ---- hand and weapon (on top of everything)
    hand = (cx + bw + 7, y_t + 14)
    P(lambda d: d.ellipse([hand[0] - 4, hand[1] - 4, hand[0] + 4, hand[1] + 4], fill=255), shift(steel, .9) if v.get('gauntlets', True) else skin, bevel=1)
    wp = v.get('weapon', 'sword'); hx_, hy_ = hand
    if wp == 'sword':
        P(lambda d: d.polygon([(hx_ - 2, hy_ - 2), (hx_ + 2, hy_ - 2), (hx_ + 5, hy_ - 27), (hx_ + 3, hy_ - 31), (hx_ + 1, hy_ - 26)], fill=255), (228, 234, 246), bevel=1)
        S.line((hx_ + 2, hy_ - 5), (hx_ + 4, hy_ - 25), (150, 160, 190))
        P(lambda d: d.rectangle([hx_ - 6, hy_ - 4, hx_ + 6, hy_ - 2], fill=255), trim, bevel=0)
    elif wp == 'axe':
        P(lambda d: d.rectangle([hx_ - 1, hy_ - 22, hx_ + 1, hy_ + 4], fill=255), (130, 90, 56), bevel=0)
        P(lambda d: d.polygon([(hx_ + 1, hy_ - 22), (hx_ + 13, hy_ - 26), (hx_ + 13, hy_ - 11), (hx_ + 1, hy_ - 13)], fill=255), (190, 196, 210), bevel=1)
    elif wp == 'mace':
        P(lambda d: d.rectangle([hx_ - 1, hy_ - 18, hx_ + 1, hy_ + 4], fill=255), (130, 90, 56), bevel=0)
        P(lambda d: d.ellipse([hx_ - 6, hy_ - 28, hx_ + 6, hy_ - 16], fill=255), trim, bevel=1)
        for sx, sy in ((hx_ - 8, hy_ - 22), (hx_ + 7, hy_ - 22), (hx_, hy_ - 30)): S.put(sx, sy, shift(trim, 1.3))
    elif wp == 'bow':
        P(lambda d: d.arc([hx_ - 8, hy_ - 28, hx_ + 14, hy_ + 6], 270, 90, fill=255, width=2), (140, 96, 56), bevel=0)
        S.line((hx_ + 3, hy_ - 28), (hx_ + 3, hy_ + 6), (230, 226, 210))
    elif wp == 'staff':
        P(lambda d: d.rectangle([hx_ - 1, hy_ - 26, hx_ + 1, hy_ + 6], fill=255), (130, 90, 56), bevel=0)
        P(lambda d: d.ellipse([hx_ - 6, hy_ - 36, hx_ + 6, hy_ - 24], fill=255), v['pal'].get('orb', (110, 220, 255)), bevel=2, spec=(hx_ - 3, hy_ - 34))
    return S.image(ol if ol != 'dark' else BLACK, thick=1)


def build_orc(v):
    """The enemy of every variant: a chibi orc drawn with the same level of detail / colours as the hero."""
    S = Sprite(72, 64); cx = 30; G = 58
    skin = v['pal'].get('orc_skin', (112, 170, 80)); iron = v['pal'].get('orc_iron', (96, 102, 120)); leath = v['pal'].get('orc_leath', (122, 84, 52))
    cloth = v['pal'].get('orc_cloth', (140, 40, 36)); ivory = (240, 232, 204)
    bev = v.get('bev', 1); ol = v.get('outline', 'tint')
    detail = v.get('orc_detail', 1)
    if v.get('orc_scars'):
        pass
    def P(draw, base, **kw):
        kw.setdefault('bevel', bev); S.part(draw, base, **kw)
    P(lambda d: d.rectangle([cx - 8, 38, cx - 2, G - 6], fill=255), shift(skin, .8))
    P(lambda d: d.rectangle([cx + 2, 38, cx + 8, G - 6], fill=255), skin)
    P(lambda d: d.rounded_rectangle([cx - 10, G - 7, cx - 1, G], 2, fill=255), shift(leath, .7))
    P(lambda d: d.rounded_rectangle([cx + 1, G - 7, cx + 12, G], 2, fill=255), shift(leath, .85))
    P(lambda d: d.rounded_rectangle([cx - 12, 22, cx + 12, 42], 5, fill=255), skin, bevel=2, dither=.5)
    P(lambda d: d.polygon([(cx - 9, 24), (cx + 9, 24), (cx + 10, 40), (cx - 10, 40)], fill=255), leath, bevel=1)
    P(lambda d: d.rectangle([cx - 12, 37, cx + 12, 40], fill=255), shift(leath, .55), bevel=0)
    if detail:
        for k in range(3): S.line((cx - 7 + k * 6, 26), (cx - 5 + k * 6, 36), shift(leath, .6))                  # stitched hide
        P(lambda d: d.polygon([(cx - 8, 30), (cx + 8, 28), (cx + 6, 36), (cx - 6, 37)], fill=255), iron, bevel=1, dither=.4)   # a chest plate
        for sx in (cx - 5, cx, cx + 5): S.put(sx, 31, ivory)                                                     # bone studs
    P(lambda d: d.ellipse([cx - 19, 18, cx - 5, 32], fill=255), shift(skin, .8), bevel=1)                         # far shoulder
    P(lambda d: d.ellipse([cx + 4, 17, cx + 20, 33], fill=255), iron, bevel=2, spec=(cx + 7, 19))                  # iron pauldron
    for sx in (cx + 8, cx + 14): P(lambda d, sx=sx: d.polygon([(sx - 2, 19), (sx + 2, 19), (sx, 11)], fill=255), shift(iron, 1.25), bevel=0)
    P(lambda d: d.rounded_rectangle([cx + 12, 26, cx + 21, 38], 3, fill=255), skin, bevel=1)
    P(lambda d: d.ellipse([cx + 16, 33, cx + 25, 42], fill=255), shift(skin, 1.05), bevel=1)
    # head
    P(lambda d: d.ellipse([cx - 14, 1, cx + 14, 26], fill=255), skin, bevel=2, spec=(cx - 8, 5))
    P(lambda d: d.polygon([(cx - 13, 11), (cx + 14, 9), (cx + 12, 3), (cx - 11, 3)], fill=255), iron, bevel=1)    # iron cap
    P(lambda d: d.rectangle([cx - 1, 12, cx + 13, 14], fill=255), shift(skin, .55), bevel=0)                      # brow
    P(lambda d: d.rectangle([cx + 1, 15, cx + 4, 18], fill=255), (255, 214, 80), bevel=0)
    P(lambda d: d.rectangle([cx + 8, 15, cx + 11, 18], fill=255), (255, 214, 80), bevel=0)
    S.put(cx + 2, 17, (60, 20, 10)); S.put(cx + 9, 17, (60, 20, 10))
    P(lambda d: d.rounded_rectangle([cx - 8, 19, cx + 13, 26], 2, fill=255), shift(skin, .78), bevel=1)          # jaw
    P(lambda d: d.polygon([(cx - 3, 20), (cx, 20), (cx - 1, 13)], fill=255), ivory, bevel=0)                      # tusks
    P(lambda d: d.polygon([(cx + 8, 20), (cx + 11, 20), (cx + 10, 13)], fill=255), ivory, bevel=0)
    # cleaver
    P(lambda d: d.rectangle([cx + 22, 6, cx + 24, 40], fill=255), (130, 90, 56), bevel=0)
    P(lambda d: d.polygon([(cx + 24, 6), (cx + 37, 2), (cx + 39, 22), (cx + 24, 18)], fill=255), (178, 184, 198), bevel=1, dither=.4)
    return S.image(ol if ol != 'dark' else BLACK, thick=1)


# ------------------------------------------------------------------------------------------------ the variants
def pal(**k): return dict(**k)


R = [   # chibi, realistic detail
    dict(key='r1_placas', label='R1  Cavaleiro de placas', note='todas as placas: peitoral com nervura, tassets, joelheiras, grevas, ombreira em laminas, aventail de malha, capa com dobras e escudo nas costas',
         hh=20, hw=13, bw=9, lw=6, pauld=6, bev=2, dither=.5, helm='bascinet', plume=True, chest=True, tassets=True, plates=True, lames=True,
         tabard=True, emblem='stripe', cape=True, back_shield=True, pouches=True, weapon='sword', outline='tint',
         pal=pal(steel=(150, 162, 190), cloth=(176, 34, 52), trim=(232, 190, 72), leath=(112, 76, 52), shield=(52, 62, 110))),
    dict(key='r2_patrulheiro', label='R2  Patrulheiro', note='capuz e capa, couro com costuras, bandoleira, aljava, bracadeiras, arco; tons de floresta',
         hh=20, hw=13, bw=8, lw=5, pauld=4, bev=1, dither=.6, helm='hood', body='tunic', chest=False, tabard=False, skirt=0, cape=True,
         bandolier=True, pouches=True, quiver=True, weapon='bow', gauntlets=False, outline='tint',
         pal=pal(steel=(110, 122, 108), cloth=(70, 104, 70), trim=(214, 176, 80), leath=(122, 90, 58), tunic=(78, 120, 76), hood=(70, 98, 64))),
    dict(key='r3_arcano', label='R3  Mago arcano', note='manto em camadas com runas na barra, cinto com bolsas, chapeu largo, barba, cajado com orbe luminoso',
         hh=20, hw=13, bw=9, lw=5, pauld=3, bev=2, dither=.7, helm='wizhat', body='tunic', robe=True, pouches=True, weapon='staff', gauntlets=False, outline='tint',
         pal=pal(steel=(110, 100, 150), cloth=(64, 74, 170), trim=(240, 200, 90), leath=(112, 76, 52), tunic=(64, 74, 170), robe=(60, 70, 160), hat=(52, 60, 140), orb=(120, 230, 255))),
    dict(key='r4_barbaro', label='R4  Barbaro nortenho', note='gorro de pele com chifre, barba ruiva, manto de pele, torso de couro, ombreiras de ferro com espinhos, machado',
         hh=21, hw=14, bw=10, lw=6, pauld=6, bev=2, dither=.6, helm='fur', body='tunic', chest=False, tabard=False, spikes=True, pouches=True, weapon='axe', outline='tint',
         pal=pal(steel=(126, 130, 144), cloth=(150, 120, 86), trim=(200, 170, 90), leath=(120, 82, 52), tunic=(130, 98, 64), fur=(150, 120, 86), beard=(190, 100, 50))),
    dict(key='r5_paladino', label='R5  Paladino', note='placas brancas com bordas douradas, elmo alado, tabardo com cruz, capa azul clara, macas; brilho quente',
         hh=20, hw=13, bw=9, lw=6, pauld=6, bev=2, dither=.4, helm='winged', plume=False, chest=True, tassets=True, plates=True, lames=True,
         tabard=True, emblem='cross', skirt=7, cape=True, weapon='mace', outline='tint',
         pal=pal(steel=(224, 228, 240), cloth=(236, 236, 244), trim=(240, 192, 80), leath=(120, 84, 56), shield=(70, 110, 200))),
]
ENEMY = pal(steel=(104, 92, 126), cloth=(96, 52, 130), trim=(170, 136, 66), leath=(84, 56, 40))
for r in R:
    r['pal']['orc_iron'] = (104, 110, 128); r['foe_pal'] = ENEMY

dark = dict(bev=1, dither=.3, outline='dark')
H = [   # chibi in the look of art_humanos
    dict(key='h1_soldado', label='H1  Soldado robusto (chibi)', note='elmo de aba, peitoral, ombreira redonda; aco escuro, tabardo vinho',
         hh=22, hw=14, bw=10, lw=7, pauld=5, helm='kettle', chest=True, tabard=True, skirt=4, weapon='sword', **dark,
         pal=pal(steel=(98, 100, 114), cloth=(120, 36, 40), trim=(196, 160, 80), leath=(96, 66, 44)),
         foe_pal=pal(steel=(104, 92, 126), cloth=(96, 52, 130), trim=(170, 136, 66), leath=(84, 56, 40))),
    dict(key='h2_blindado', label='H2  Cavaleiro blindado (chibi)', note='elmo fechado com fenda e furos, ombreiras grandes com espinhos, grevas, pluma curta',
         hh=22, hw=15, bw=11, lw=7, pauld=7, helm='greathelm', plume=True, chest=True, tabard=True, tassets=True, plates=True, spikes=True, weapon='sword', **dark,
         pal=pal(steel=(124, 134, 164), cloth=(150, 30, 36), trim=(214, 178, 70), leath=(70, 52, 40)),
         foe_pal=pal(steel=(104, 92, 126), cloth=(96, 52, 130), trim=(170, 136, 66), leath=(84, 56, 40))),
    dict(key='h3_sombrio', label='H3  Guarda sombrio (chibi)', note='armadura preta-arroxeada, elmo com chifres de osso e fenda vermelha, capa rasgada',
         hh=22, hw=14, bw=10, lw=7, pauld=6, helm='horned', chest=True, tabard=True, cape=True, spikes=True, plates=True, weapon='sword', **dark,
         pal=pal(steel=(82, 76, 112), cloth=(120, 24, 40), trim=(180, 70, 60), leath=(52, 38, 40)),
         foe_pal=pal(steel=(104, 92, 126), cloth=(96, 52, 130), trim=(170, 136, 66), leath=(84, 56, 40))),
    dict(key='h4_veterano', label='H4  Veterano de malha (chibi)', note='touca de malha com rosto a mostra, cota de malha texturizada, tunica longa verde-musgo',
         hh=22, hw=14, bw=10, lw=7, pauld=4, helm='coif', mail=True, tabard=True, skirt=8, emblem='stripe', pouches=True, weapon='sword', **dark,
         pal=pal(steel=(118, 122, 128), cloth=(72, 84, 70), trim=(176, 150, 80), leath=(88, 62, 42)),
         foe_pal=pal(steel=(104, 92, 126), cloth=(96, 52, 130), trim=(170, 136, 66), leath=(84, 56, 40))),
    dict(key='h5_cruzado', label='H5  Cavaleiro cruzado (chibi)', note='elmo de balde com fenda em cruz, sobreveste longa clara com cruz, capa; destaca no escuro',
         hh=22, hw=15, bw=10, lw=7, pauld=5, helm='bucket', chest=True, tabard=True, emblem='cross', skirt=9, cape=True, weapon='sword', **dark,
         pal=pal(steel=(150, 154, 168), cloth=(196, 190, 176), trim=(204, 170, 70), leath=(74, 54, 40)),
         foe_pal=pal(steel=(104, 92, 126), cloth=(96, 52, 130), trim=(170, 136, 66), leath=(84, 56, 40))),
]
for h in H:
    h['pal'].update(orc_iron=(70, 76, 94), orc_skin=(96, 142, 74), orc_leath=(96, 66, 44), orc_cloth=(110, 34, 32))


# ------------------------------------------------------------------------------------------------ scenes
def mood_scene(kind, seed):
    s = PG.Scene(seed)
    if kind == 'penumbra':
        g = PG.make_grade(sat=0.5, val=0.62, tint=(0.95, 0.95, 1.0))
        s.vgrad(0, 150, (28, 30, 42), (150, 112, 92), levels=9); s.glow(360, 150, 120, (255, 170, 110), 0.5)
        s.hills(158, (66, 58, 74), (22, 10, 6), 3); s.castle(280, 150, 1.3, (38, 34, 48), win=(255, 190, 90))
        s.hills(176, (40, 38, 46), (14, 7, 3), 9, top_col=(70, 62, 70)); s.pines(190, (26, 28, 34), 9, 4, 40, 70)
        s.fog(150, 205, (150, 130, 130), 0.55); tile = PG.grade_image(PG.prop('street_tile'), g); s.tile_ground(tile, GY - 3, g)
        PG.prop_at(s, 'dead_tree', 70, g); PG.prop_at(s, 'banner', 240, g)
    elif kind == 'noite':
        g = PG.make_grade(sat=0.5, val=0.55, tint=(0.8, 0.92, 1.15))
        s.vgrad(0, 160, (8, 12, 28), (52, 74, 112), levels=9); s.dots(60, (200, 215, 255), 5, 110)
        s.d.ellipse([360, 30, 392, 62], fill=(226, 232, 245, 255)); s.d.ellipse([368, 36, 394, 58], fill=(18, 24, 46, 255)); s.glow(376, 46, 90, (140, 170, 230), 0.5)
        s.hills(170, (26, 38, 62), (20, 9, 5), 6); s.pines(185, (14, 20, 36), 14, 8, 50, 95)
        s.fog(150, 212, (90, 120, 170), 0.6, seed=12); tile = PG.grade_image(PG.prop('forest_tile'), g); s.tile_ground(tile, GY - 3, g, dark_below=(10, 14, 24))
        PG.prop_at(s, 'dead_tree', 60, g); PG.prop_at(s, 'oak', 430, g)
    elif kind == 'masmorra':
        g = PG.make_grade(sat=0.35, val=0.5, contrast=1.15, tint=(1.05, 0.98, 0.95))
        wall = PG.grade_image(PG.prop('stone_wall'), g); s.rect(0, 0, 480, 270, (16, 14, 18))
        for y in range(40, GY - 12, wall.height - 6):
            for x in range(0, 480, wall.width): s.blit(wall, x - 10, y)
        s.rect(0, 0, 480, 40, (10, 9, 12))
        for ax in (80, 240, 400): s.rect(ax - 12, 30, ax + 12, GY, (34, 30, 38)); s.rect(ax - 12, 30, ax - 9, GY, (52, 46, 54))
        for tx in (160, 320):
            s.rect(tx - 1, 96, tx + 1, 112, (60, 40, 28)); s.rect(tx - 2, 90, tx + 2, 96, (255, 190, 80)); s.glow(tx, 96, 100, (255, 170, 70), 0.85)
        tile = PG.grade_image(PG.prop('street_tile'), g); s.tile_ground(tile, GY - 3, g, dark_below=(14, 12, 16))
    elif kind == 'chuva':
        g = PG.make_grade(sat=0.42, val=0.6)
        s.vgrad(0, 160, (54, 60, 64), (128, 138, 134), levels=7); s.hills(160, (74, 84, 82), (20, 10, 6), 14)
        s.pines(178, (46, 56, 56), 10, 17, 40, 70); s.hills(186, (52, 60, 58), (12, 6, 3), 22, top_col=(88, 98, 94)); s.fog(140, 200, (140, 150, 148), 0.7, seed=9)
        tile = PG.grade_image(PG.prop('grass_tile'), g); s.tile_ground(tile, GY - 3, g, dark_below=(26, 30, 30))
        PG.prop_at(s, 'tent', 90, g); PG.prop_at(s, 'log', 400, g)
    elif kind == 'brasas':
        g = PG.make_grade(sat=0.55, val=0.55, tint=(1.15, 0.85, 0.75))
        s.vgrad(0, 160, (20, 12, 16), (196, 80, 36), levels=10); s.glow(240, 175, 200, (255, 140, 60), 0.6)
        s.hills(170, (46, 24, 26), (18, 9, 5), 4)
        for hx in (70, 220, 400):
            h = PG.grade_image(PG.prop('medieval_house'), PG.make_grade(sat=0.3, val=0.28, tint=(1.1, 0.9, 0.85)))
            h = h.resize((int(h.width * .75), int(h.height * .75)), Image.NEAREST); s.blit(h, hx - h.width // 2, 178 - h.height + 24); s.glow(hx, 150, 60, (255, 150, 60), 0.7)
        s.fog(120, 200, (60, 30, 30), 0.6, seed=2)
        tile = PG.grade_image(PG.prop('street_tile'), g); s.tile_ground(tile, GY - 3, g, dark_below=(24, 12, 14))
    return s


def trim_bottom(im):
    bb = im.getbbox()
    return im.crop((0, 0, im.width, bb[3])) if bb else im


def compose(v, mood, seed, extra_hero=None):
    s = mood_scene(mood, seed)
    hero = trim_bottom(build(v, 'hero'))
    foe = trim_bottom(build(v, 'orc')); foe2 = trim_bottom(build(v, 'foe'))
    put_sprite(s, hero, 130)
    put_sprite(s, foe, 300, flip=True)
    put_sprite(s, foe2, 390, flip=True)
    star(s, 215, GY - 40, 14, (255, 236, 150), (255, 255, 230)); sparks(s, 215, GY - 40, (255, 255, 255), 12, 26)
    s.dots(40, (255, 200, 140), seed, 215)
    s.vignette(0.55)
    return s


def lineup(path, items, scale=4):
    from PIL import ImageDraw as ID
    cols = len(items); cw = 210
    sprites = [(v, build(v, 'hero'), build(v, 'orc'), build(v, 'foe')) for v in items]
    img = Image.new('RGB', (cw * cols + 10, 2 * 64 * scale + 150), (32, 34, 44)); d = ID.Draw(img)
    for i, (v, h, o, f) in enumerate(sprites):
        x0 = 5 + i * cw
        d.text((x0 + 4, 6), v['label'], fill=(255, 240, 200))
        words = v['note']; y = 22
        while words and y < 90:
            d.text((x0 + 4, y), words[:34], fill=(185, 185, 200)); words = words[34:]; y += 12
        for j, im in enumerate((h, o)):
            big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
            if j == 1: big = mirror(big)
            bg = Image.new('RGBA', big.size, (0, 0, 0, 0)); bg.alpha_composite(big)
            img.paste(bg, (x0 + (cw - big.width) // 2 if j == 0 else x0 + (cw - big.width) // 2, 120 + j * 64 * scale), bg)
    PG.safe_save(img, path)


def export_catalog(dest, out):
    """Hero / orc PNGs (5x) + the lineups and scenes for docs/PERSONAGENS.md."""
    import shutil
    os.makedirs(dest, exist_ok=True)
    for v in R + H:
        for role in ('hero', 'orc'):
            im = trim_bottom(build(v, role)); bb = im.getbbox(); im = im.crop(bb)
            PG.safe_save(im.resize((im.width * 5, im.height * 5), Image.NEAREST), os.path.join(dest, f"{v['key']}_{role}.png"))
    for f in os.listdir(out):
        if f.endswith('.png') and '_tmp' not in f and '_new' not in f and not f.endswith('_detalhe.png'):
            shutil.copyfile(os.path.join(out, f), os.path.join(dest, f))


def main():
    out = os.path.normpath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'out', 'art_chibi'))
    os.makedirs(out, exist_ok=True)
    lineup(os.path.join(out, '00_realista_linha.png'), R)
    lineup(os.path.join(out, '00_humanos_linha.png'), H)
    moods = ['penumbra', 'noite', 'masmorra', 'chuva', 'brasas']
    for i, v in enumerate(R):
        PG.finish(compose(v, moods[i], 10 + i), os.path.join(out, f'R{i + 1}_{v["key"][3:]}.png'), v['label'], v['note'][:110]); print('wrote', v['key'])
    for i, v in enumerate(H):
        PG.finish(compose(v, moods[(i + 2) % 5], 30 + i), os.path.join(out, f'H{i + 1}_{v["key"][3:]}.png'), v['label'], v['note'][:110]); print('wrote', v['key'])

    export_catalog(os.path.normpath(os.path.join(HERE, '..', 'docs', 'personagens', 'chibi')), out)


if __name__ == '__main__':
    main()
