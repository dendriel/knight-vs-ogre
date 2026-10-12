"""Enemy sprite sheets built from the existing rigs (T22+): recolours of the knight / ogre with other weapons.

Every enemy sheet follows the OGRE contract (rows in this order, 6 frames of 64x64, facing right, hip column 30, feet on
row 58):  idle(6) walk(10) attack(…) hurt(10) death(8)  [+ extra rows appended at the end].

    python enemy_gen.py [out_dir]  ->  soldier_spritesheet.png/.json, ...

The knight rig reads its colours from sprite_rig module globals at call time, so a "palette" is a temporary override of
those globals (see `palette`). Nothing here changes knight_gen.py / ogre_gen.py output.
"""
import json, os, sys
from contextlib import contextmanager
from PIL import Image

import sprite_rig as SR
import knight_gen as KG
import ogre_gen as OG

F = 64


def C(r, g, b): return (r, g, b, 255)


@contextmanager
def palette(module, **kw):
    """Temporarily replaces colour globals of a rig module (sprite_rig or ogre_gen) while frames are rendered."""
    old = {k: getattr(module, k) for k in kw}
    for k, v in kw.items(): setattr(module, k, v)
    try: yield
    finally:
        for k, v in old.items(): setattr(module, k, v)


# ---- knight-rig palettes ---------------------------------------------------------------------------------------
SOLDIER = dict(
    PN=dict(shade=C(46, 40, 60), base=C(88, 80, 112), hl=C(150, 142, 176)),     # dark violet-grey plate
    PF=dict(shade=C(26, 22, 38), base=C(56, 50, 76), hl=C(92, 86, 116)),
    RED=C(108, 56, 150), RED_D=C(64, 30, 100),                                   # purple tabard and plume
    GOLD=C(196, 156, 70), LEATH=C(92, 62, 44), LEATH_D=C(56, 38, 28))


def write_sheet(out, name, rows, render, pal_module=SR, pal=None, post=None, extra_meta=None, fs=F):
    """rows = [(anim name, pose fn(i) -> pose dict, fps)] ; render(pose) -> fs x fs image (64 normally, 96 for bosses)."""
    sheet = Image.new('RGBA', (fs * 6, fs * len(rows)), (0, 0, 0, 0))
    meta = {'image': f'{name}_spritesheet.png', 'frame_size': [fs, fs], 'facing': 'right'}
    if fs != F: meta.update(anchor_x=48, ground_row=90)          # hip column / feet row inside the big frame
    atlas = {'frames': [], 'animations': {}, 'meta': dict(meta, **(extra_meta or {}))}
    with palette(pal_module, **(pal or {})):
        for r, (an, fn, fps) in enumerate(rows):
            for i in range(6):
                img = render(fn(i))
                if post: img = post(img)
                sheet.alpha_composite(img, (i * fs, r * fs))
                atlas['frames'].append({'filename': f'{an}_{i}', 'frame': {'x': i * fs, 'y': r * fs, 'w': fs, 'h': fs}})
            atlas['animations'][an] = {'frames': [f'{an}_{i}' for i in range(6)], 'fps': fps,
                                       'loop': not an.startswith(('attack', 'hurt', 'death'))}
    sheet.save(f'{out}/{name}_spritesheet.png')
    json.dump(atlas, open(f'{out}/{name}_spritesheet.json', 'w'), indent=2)
    print(name, 'ok', sheet.size)


def human_rows(attack_fn, hold=None):
    """idle / walk / attack / hurt / death with the knight's poses (the walk is the slow cycle, not the run)."""
    def carry(fn):
        return (lambda i: KG.carry(fn(i), hold)) if hold else fn
    return [('idle', carry(KG.idle), 6), ('walk', carry(KG.walk), 10), ('attack', attack_fn, 12),
            ('hurt', carry(KG.hurt), 10), ('death', carry(KG.death), 8)]


SPEARMAN = dict(
    PN=dict(shade=C(66, 56, 42), base=C(124, 108, 84), hl=C(184, 166, 130)),     # leather / bronze
    PF=dict(shade=C(40, 34, 26), base=C(84, 72, 54), hl=C(120, 104, 80)),
    RED=C(52, 128, 74), RED_D=C(30, 82, 46),                                     # green tabard and plume
    GOLD=C(214, 176, 80), LEATH=C(100, 68, 40), LEATH_D=C(62, 42, 26))


ARCHER = dict(
    PN=dict(shade=C(78, 62, 40), base=C(156, 132, 88), hl=C(214, 194, 140)),     # tan leather
    PF=dict(shade=C(48, 38, 26), base=C(104, 86, 58), hl=C(140, 118, 80)),
    RED=C(214, 118, 40), RED_D=C(138, 70, 24),                                   # orange tabard and plume
    GOLD=C(226, 188, 84), LEATH=C(108, 72, 44), LEATH_D=C(68, 46, 28))


SHIELDMAN = dict(
    PN=dict(shade=C(60, 76, 108), base=C(122, 146, 190), hl=C(200, 218, 244)),   # bright blue steel
    PF=dict(shade=C(34, 44, 70), base=C(76, 92, 128), hl=C(110, 128, 164)),
    RED=C(40, 84, 176), RED_D=C(22, 52, 118),                                    # blue tabard / shield face
    GOLD=C(238, 198, 84), LEATH=C(112, 76, 46), LEATH_D=C(70, 48, 30))


def shield_rows():
    """soldier rows with the shield in the free hand, plus an appended `guard` row (shield raised, blade low)."""
    def sh(fn, hand=None):
        def g(i):
            p = dict(fn(i), shield=True)
            if hand: p['handF'] = hand
            return p
        return g
    rows = [('idle', sh(KG.idle, (7, 3)), 6), ('walk', sh(KG.walk, (7, 3)), 10), ('attack', sh(KG.atk_sword), 12),
            ('hurt', sh(KG.hurt), 10), ('death', sh(KG.death), 8), ('guard', sh(KG.idle, (9, 0)), 6)]
    return rows


# ---- ogre-rig variants (T25): recolours, small or large versions, extra head parts ---------------------------------------
def scaler(k):
    """Post-process: scales a frame about the hip column / feet row so the anchors stay valid (k < 1 small, k > 1 large)."""
    def post(img):
        if k == 1: return img
        bb0 = img.getbbox(); kk = k
        if bb0 and k > 1:                                       # a frame that would cross the edge is scaled down to fit
            x0, y0, x1, y1 = bb0
            lim = [k, 57.0 / max(1, 58 - y0), 58.0 / max(1, x1 - x0)]
            if x1 > 30: lim.append(32.0 / (x1 - 30))
            if x0 < 30: lim.append(29.0 / (30 - x0))
            kk = min(lim)
        n = int(round(F * kk)); big = img.resize((n, n), Image.NEAREST)
        out = Image.new('RGBA', (F, F), (0, 0, 0, 0))
        out.paste(big, (int(round(30 - 30 * kk)), int(round(58 - 58 * kk))), big)
        bb = out.getbbox()
        if bb and bb[0] < 1:                                   # a scaled lying body must not cross the frame edge
            o2 = Image.new('RGBA', (F, F), (0, 0, 0, 0)); o2.paste(out, (1 - bb[0], 0), out); out = o2
        return out
    return post


def ogre_rows(): return list(OG.ANIMS)


ORC = dict(SK=dict(shade=C(46, 54, 44), base=C(98, 112, 82), hl=C(158, 172, 124)),
           SKF=dict(shade=C(30, 38, 32), base=C(66, 78, 58), hl=C(96, 110, 78)),
           FUR=C(122, 54, 46), FUR_D=C(78, 32, 30), TUSK=C(236, 228, 196), EYE=C(236, 70, 50))
GOBLIN = dict(SK=dict(shade=C(30, 92, 44), base=C(110, 188, 76), hl=C(188, 240, 124)),
              SKF=dict(shade=C(22, 62, 36), base=C(70, 136, 58), hl=C(100, 170, 80)),
              FUR=C(150, 104, 62), FUR_D=C(104, 70, 42), EYE=C(255, 236, 90))
KOBOLD = dict(SK=dict(shade=C(120, 56, 40), base=C(206, 112, 70), hl=C(244, 170, 112)),
              SKF=dict(shade=C(84, 38, 30), base=C(150, 78, 52), hl=C(186, 112, 76)),
              FUR=C(88, 74, 60), FUR_D=C(56, 46, 38), EYE=C(255, 255, 160))
MINOTAUR = dict(SK=dict(shade=C(60, 36, 24), base=C(122, 78, 46), hl=C(180, 128, 80)),
                SKF=dict(shade=C(40, 24, 18), base=C(88, 54, 34), hl=C(120, 80, 52)),
                FUR=C(70, 50, 40), FUR_D=C(44, 32, 28), EYE=C(255, 90, 60))


def minotaur_head():
    """Ogre head + two curved horns (the head function is swapped only while the minotaur is rendered)."""
    orig = OG.o_head
    def head(c, eye='open'):
        base = orig(c, eye); x, y = SR.rd(c)
        def horns(d):
            d.polygon([(x - 3, y - 6), (x - 7, y - 9), (x - 8, y - 13), (x - 5, y - 10), (x - 2, y - 7)], fill=C(236, 226, 196))
            d.polygon([(x + 3, y - 6), (x + 7, y - 9), (x + 8, y - 13), (x + 5, y - 10), (x + 2, y - 7)], fill=C(236, 226, 196))
            d.line([(x - 7, y - 10), (x - 5, y - 8)], fill=C(176, 166, 140))
            d.line([(x + 7, y - 10), (x + 5, y - 8)], fill=C(176, 166, 140))
        base.alpha_composite(SR.layer(horns))
        return base
    return head


def big(k):
    """Post-process for bosses: scale a 64x64 frame by k about hip column 30 / feet row 58 into a 96x96 frame whose hip
    column is 48 and feet row 90 (the sheet meta carries those anchors)."""
    def post(img):
        kk = k
        bb = img.getbbox()
        if bb:                                              # a frame that would cross the 96x96 edge is scaled down to fit
            x0, y0, x1, y1 = bb; lim = [k, 89.0 / max(1, 58 - y0)]
            if x1 > 30: lim.append(45.0 / (x1 - 30))
            if x0 < 30: lim.append(46.0 / (30 - x0))
            if y1 > 59: lim.append(4.0 / (y1 - 58))
            kk = min(lim)
        n = int(round(F * kk)); b = img.resize((n, n), Image.NEAREST)
        out = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
        out.paste(b, (int(round(48 - 30 * kk)), int(round(90 - 58 * kk))), b)
        return out
    return post


def captain_head():
    """Ogre head + a spiked iron cap (the ogre captain)."""
    orig = OG.o_head
    def head(c, eye='open'):
        base = orig(c, eye); x, y = SR.rd(c)
        def cap(d):
            d.polygon([(x - 5, y - 4), (x - 4, y - 9), (x + 4, y - 9), (x + 6, y - 3), (x + 2, y - 5)], fill=C(128, 134, 154))
            d.polygon([(x - 4, y - 9), (x, y - 12), (x + 4, y - 9)], fill=C(188, 196, 214))
            d.line([(x - 4, y - 7), (x + 4, y - 7)], fill=C(80, 86, 104))
            d.point((x - 6, y - 5), fill=C(188, 196, 214)); d.point((x + 7, y - 4), fill=C(188, 196, 214))
        base.alpha_composite(SR.layer(cap))
        return base
    return head


CAPTAIN = dict(SK=dict(shade=C(78, 44, 36), base=C(150, 84, 62), hl=C(214, 148, 112)),
               SKF=dict(shade=C(52, 30, 26), base=C(108, 60, 46), hl=C(150, 96, 74)),
               FUR=C(90, 40, 40), FUR_D=C(58, 26, 28), EYE=C(255, 230, 80), I1=C(70, 70, 86), I2=C(150, 156, 176), I3=C(226, 232, 246))
MINO_LORD = dict(SK=dict(shade=C(52, 22, 22), base=C(108, 46, 40), hl=C(164, 92, 76)),
                 SKF=dict(shade=C(34, 14, 16), base=C(76, 32, 30), hl=C(110, 60, 52)),
                 FUR=C(40, 28, 28), FUR_D=C(26, 18, 20), EYE=C(255, 60, 40), I1=C(60, 50, 66), I2=C(132, 120, 150), I3=C(214, 206, 230))
BLACK_KNIGHT = dict(
    PN=dict(shade=C(20, 20, 26), base=C(50, 50, 62), hl=C(104, 104, 128)),
    PF=dict(shade=C(12, 12, 18), base=C(34, 34, 44), hl=C(70, 70, 90)),
    RED=C(170, 24, 48), RED_D=C(100, 14, 30), GOLD=C(168, 132, 60), LEATH=C(60, 40, 30), LEATH_D=C(36, 24, 20),
    BLADE=C(176, 178, 200), BLADE_SH=C(116, 118, 146))


def black_knight_rows():
    def sh(fn, hand=None):
        def g(i):
            p = dict(fn(i), shield=True)
            if hand: p['handF'] = hand
            return p
        return g
    return [('idle', sh(KG.idle, (7, 3)), 6), ('walk', sh(KG.walk, (7, 3)), 10), ('attack', sh(KG.atk_sword), 12),
            ('hurt', sh(KG.hurt), 10), ('death', sh(KG.death), 8), ('attack_2', sh(KG.atk_sword_2), 12),
            ('attack_3', sh(KG.atk_sword_3), 12), ('guard', sh(KG.idle, (9, 0)), 6)]


def build(out):
    # T22 soldier: the knight with an enemy palette; stroke 1 of the sword is its attack (frames 3-4 hit)
    write_sheet(out, 'soldier', human_rows(KG.atk_sword), SR.render, pal=SOLDIER)
    # T21 spearman: same rig, green palette, two-handed spear (carried tilted; thrust is the attack row)
    write_sheet(out, 'spearman', human_rows(KG.atk_spear, hold='spear'), SR.render, pal=SPEARMAN)
    # T23 archer: bow carried in the melee rows, the bow-draw poses as the attack row (arrow leaves on frame 4)
    # T25 monsters: the ogre rig recoloured / scaled (rows idle, walk, attack, hurt, death)
    write_sheet(out, 'orc', ogre_rows(), OG.o_render, pal_module=OG, pal=ORC)
    write_sheet(out, 'goblin', ogre_rows(), OG.o_render, pal_module=OG, pal=GOBLIN, post=scaler(0.72))
    write_sheet(out, 'kobold', ogre_rows(), OG.o_render, pal_module=OG, pal=KOBOLD, post=scaler(0.8))
    write_sheet(out, 'minotaur', ogre_rows(), OG.o_render, pal_module=OG, pal=dict(MINOTAUR, o_head=minotaur_head()),
                post=scaler(1.1))
    # T32 bosses: 96x96 frames (1.5x), hip column 48 / feet row 90 (meta anchor_x / ground_row)
    write_sheet(out, 'ogre_captain', ogre_rows(), OG.o_render, pal_module=OG, pal=dict(CAPTAIN, o_head=captain_head()),
                post=big(1.5), fs=96)
    write_sheet(out, 'minotaur_lord', ogre_rows(), OG.o_render, pal_module=OG, pal=dict(MINO_LORD, o_head=minotaur_head()),
                post=big(1.45), fs=96)
    write_sheet(out, 'black_knight', black_knight_rows(), SR.render, pal=BLACK_KNIGHT, post=big(1.3), fs=96)
    # T24 shield knight: shield in the free hand + a guard row appended at the end
    write_sheet(out, 'shieldman', shield_rows(), SR.render, pal=SHIELDMAN)
    write_sheet(out, 'archer', human_rows(KG.atk_bow, hold='bow'), SR.render, pal=ARCHER)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    build(out)
