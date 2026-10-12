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


def write_sheet(out, name, rows, render, pal_module=SR, pal=None, post=None, extra_meta=None):
    """rows = [(anim name, pose fn(i) -> pose dict, fps)] ; render(pose) -> 64x64 image."""
    sheet = Image.new('RGBA', (F * 6, F * len(rows)), (0, 0, 0, 0))
    atlas = {'frames': [], 'animations': {}, 'meta': dict({'image': f'{name}_spritesheet.png', 'frame_size': [F, F],
                                                         'facing': 'right'}, **(extra_meta or {}))}
    with palette(pal_module, **(pal or {})):
        for r, (an, fn, fps) in enumerate(rows):
            for i in range(6):
                img = render(fn(i))
                if post: img = post(img)
                sheet.alpha_composite(img, (i * F, r * F))
                atlas['frames'].append({'filename': f'{an}_{i}', 'frame': {'x': i * F, 'y': r * F, 'w': F, 'h': F}})
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


def build(out):
    # T22 soldier: the knight with an enemy palette; stroke 1 of the sword is its attack (frames 3-4 hit)
    write_sheet(out, 'soldier', human_rows(KG.atk_sword), SR.render, pal=SOLDIER)
    # T21 spearman: same rig, green palette, two-handed spear (carried tilted; thrust is the attack row)
    write_sheet(out, 'spearman', human_rows(KG.atk_spear, hold='spear'), SR.render, pal=SPEARMAN)
    # T23 archer: bow carried in the melee rows, the bow-draw poses as the attack row (arrow leaves on frame 4)
    # T24 shield knight: shield in the free hand + a guard row appended at the end
    write_sheet(out, 'shieldman', shield_rows(), SR.render, pal=SHIELDMAN)
    write_sheet(out, 'archer', human_rows(KG.atk_bow, hold='bow'), SR.render, pal=ARCHER)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    build(out)
