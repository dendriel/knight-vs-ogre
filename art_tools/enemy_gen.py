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
                                       'loop': not an.startswith(('attack', 'hurt', 'death', 'guard'))}
    sheet.save(f'{out}/{name}_spritesheet.png')
    json.dump(atlas, open(f'{out}/{name}_spritesheet.json', 'w'), indent=2)
    print(name, 'ok', sheet.size)


def human_rows(attack_fn, hold=None):
    """idle / walk / attack / hurt / death with the knight's poses (the walk is the slow cycle, not the run)."""
    def carry(fn):
        return (lambda i: KG.carry(fn(i), hold)) if hold else fn
    return [('idle', carry(KG.idle), 6), ('walk', carry(KG.walk), 10), ('attack', attack_fn, 12),
            ('hurt', carry(KG.hurt), 10), ('death', carry(KG.death), 8)]


def build(out):
    # T22 soldier: the knight with an enemy palette; stroke 1 of the sword is its attack (frames 3-4 hit)
    write_sheet(out, 'soldier', human_rows(KG.atk_sword), SR.render, pal=SOLDIER)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    build(out)
