"""Hero class sprite sheets (T42-T44): same rows as knight_spritesheet (idle ... throw) + the class' own attack rows
appended at the end. Built with the knight's rig and a palette override (see enemy_gen.palette), so the poses, the
anchors (hip column 30 / feet row 58) and the timing contract are the knight's.

    python class_gen.py [out_dir]  ->  ranger_spritesheet.png/.json, ...
"""
import json, math, os, sys
from PIL import Image

import sprite_rig as SR
import knight_gen as KG
from enemy_gen import palette, C

F = 64


def write_class_sheet(out, name, extra_rows, hold, pal, post=None, head=None):
    """rows = knight ANIMS (carrying `hold`) + extra_rows [(anim, pose fn, fps, still_hold?)]."""
    rows = [(an, (lambda fn: (lambda i: KG.carry(fn(i), hold) if hold else fn(i)))(fn), fps) for an, fn, fps in KG.ANIMS]
    for er in extra_rows:                                       # same name as a knight row: replaces it in place
        names = [r[0] for r in rows]
        if er[0] in names: rows[names.index(er[0])] = er
        else: rows.append(er)
    sheet = Image.new('RGBA', (F * 6, F * len(rows)), (0, 0, 0, 0))
    atlas = {'frames': [], 'animations': {}, 'meta': {'image': f'{name}_spritesheet.png', 'frame_size': [F, F], 'facing': 'right'}}
    over = dict(pal)
    if head is not None: over['head'] = head(SR.head)
    with palette(SR, **over):
        for r, (an, fn, fps) in enumerate(rows):
            for i in range(6):
                img = SR.render(fn(i))
                if post: img = post(img)
                sheet.alpha_composite(img, (i * F, r * F))
                atlas['frames'].append({'filename': f'{an}_{i}', 'frame': {'x': i * F, 'y': r * F, 'w': F, 'h': F}})
            atlas['animations'][an] = {'frames': [f'{an}_{i}' for i in range(6)], 'fps': fps,
                                       'loop': not an.startswith(KG.NOLOOP + ('throw',))}
    sheet.save(f'{out}/{name}_spritesheet.png')
    json.dump(atlas, open(f'{out}/{name}_spritesheet.json', 'w'), indent=2)
    print(name, 'ok', sheet.size)


# ------------------------------------------------------------------ ranger (T42)
RANGER = dict(
    PN=dict(shade=C(34, 62, 40), base=C(78, 128, 72), hl=C(150, 192, 112)),     # forest green leathers
    PF=dict(shade=C(22, 40, 28), base=C(52, 88, 52), hl=C(88, 124, 76)),
    RED=C(214, 168, 60), RED_D=C(150, 112, 36),                                  # a yellow feather / sash
    GOLD=C(210, 180, 90), LEATH=C(110, 76, 44), LEATH_D=C(72, 50, 30))


def atk_bow_2(i):
    # 2nd shot of the chain: a quick half-draw (shorter pull), arrow leaves on frame 4
    p = KG.atk_bow(i)
    p['pull'] = [0, 0, 2, 5, 0, 0][i]; p['hand_pull'] = [0, 0, 2, 5, 7, 3][i]; p['shift'] = [0, 0, 0, 0, -2, 0][i]
    return p


def atk_bow_3(i):
    # 3rd shot: full draw and a strong release (the piercing arrow), the body leans back with the recoil
    p = KG.atk_bow(i)
    p['pull'] = [0, 1, 6, 11, 0, 0][i]; p['hand_pull'] = [0, 1, 6, 11, 12, 5][i]
    p['lean'] = [0, -2, -5, -6, -7, -2][i]; p['shift'] = [0, 0, 0, 1, -4, 0][i]
    return p


def atk_rain(i):
    # special: the bow is raised to the sky and shoots upwards (frame 0 = crouched, drawing: the charge pose)
    return dict(weapon='bow', footN=(CX_ + 7, GY_), footF=(CX_ - 6, GY_),
                sink=[3, 2, 1.5, 1.5, 1.5, 1][i], lean=[-6, -4, -6, -8, -3, 0][i],
                bowhand=[(5, 4), (8, -3), (9, -9), (9, -10), (9, -9), (8, -2)][i],
                aim=[100, 130, 158, 166, 160, 120][i],
                pull=[2, 4, 8, 11, 0, 0][i], hand_pull=[2, 4, 8, 11, 9, 3][i],
                arrow=['nock', 'nock', 'nock', 'nock', 'fly', None][i],
                elbow='xm', plume=[(-7, -1), (-8, 0), (-9, 1), (-9, 1), (-9, 1), (-8, 0)][i],
                flap=[0, -1, -1, -2, -2, -1][i], shift=[0, 0, 0, 0, -1, 0][i])


CX_, GY_ = SR.CX, SR.GY


def atk_short(i):
    # short sword (secondary): a quick close slash, same swing as the knight's stroke but tighter
    p = KG.atk_sword(i)
    p['wang'] = [175, 232, 240, 96, 84, 100][i]; p['handN'] = [(5, -2), (-3, -3), (-4, -2), (6, -1), (10, 0), (5, 1)][i]
    return p


# ------------------------------------------------------------------ crossbowman (T43)
CROSSBOWMAN = dict(
    PN=dict(shade=C(92, 40, 30), base=C(168, 84, 56), hl=C(232, 156, 112)),     # rust-red plate
    PF=dict(shade=C(60, 26, 22), base=C(112, 56, 40), hl=C(158, 98, 72)),
    RED=C(70, 90, 160), RED_D=C(44, 58, 112),                                    # blue sash and plume
    GOLD=C(214, 176, 80), LEATH=C(100, 66, 40), LEATH_D=C(64, 42, 28))


def atk_xbow_2(i):
    # 2nd bolt: the crossbow is still up, so the reload is quick; light recoil
    p = KG.atk_xbow(i)
    p['sink'] = [1, 1, 1.2, 1.2, 1.6, 1][i]; p['shift'] = [0, 0, 0, 0, -1, 0][i]
    p['loaded'] = [True, True, True, True, False, True][i]
    return p


def atk_xbow_3(i):
    # 3rd bolt: heavy shot, the whole body takes the recoil (the bolt pierces)
    p = KG.atk_xbow(i)
    p['lean'] = [0, 0, -3, -4, -9, -3][i]; p['shift'] = [0, 0, 0, 1, -5, 0][i]; p['sink'] = [1, 1, 1.5, 2, 3, 1.5][i]
    return p


def atk_volley(i):
    # special: aims forward and fires bolt after bolt (frames 1-4 all show a bolt leaving), frame 0 = the charge pose
    p = KG.atk_xbow(i)
    p['loaded'] = [True, False, True, False, True, False][i]
    p['bolt'] = ['load', 'fly', 'fly', 'fly', 'fly', None][i]
    p['ang'] = [100, 92, 90, 92, 90, 96][i]
    p['lean'] = [0, -3, -2, -3, -2, -1][i]; p['shift'] = [0, -1, 0, -1, 0, 0][i]
    return p


def atk_axe_small(i):
    # small axe (secondary): the knight's axe chop, quicker and tighter (the trail is drawn in the frame)
    p = KG.atk_axe(i)
    return p


# ------------------------------------------------------------------ mage (T44)
MAGE = dict(
    PN=dict(shade=C(52, 36, 88), base=C(110, 80, 168), hl=C(176, 148, 226)),    # violet robe
    PF=dict(shade=C(32, 22, 60), base=C(72, 52, 120), hl=C(110, 88, 166)),
    RED=C(238, 196, 76), RED_D=C(176, 132, 40),                                  # golden sash / plume
    GOLD=C(255, 226, 120), LEATH=C(86, 58, 42), LEATH_D=C(56, 38, 28))


def mage_head(orig):
    """Helmet head + a pointed wizard hat with a brim."""
    def head(c, plume):
        pl, hd = orig(c, plume); x, y = SR.rd(c)
        def hat(d):
            d.polygon([(x - 7, y - 4), (x + 7, y - 4), (x + 4, y - 7), (x + 1, y - 15), (x - 3, y - 8), (x - 4, y - 7)], fill=C(88, 60, 148))
            d.polygon([(x - 7, y - 4), (x, y - 4), (x - 1, y - 12), (x - 4, y - 7)], fill=C(120, 88, 188))
            d.line([(x - 7, y - 4), (x + 7, y - 4)], fill=C(54, 36, 92), width=2)
            d.line([(x - 3, y - 6), (x + 4, y - 6)], fill=C(238, 196, 76))
        hd.alpha_composite(SR.layer(hat))
        return pl, hd
    return head


def _cast(i, hn, wang, hx, lean, hf, shift):
    return dict(weapon='sword', hold='staff', hx=hx[i], footN=(CX_ + 7, GY_), footF=(CX_ - 6, GY_),
                sink=[1, 1.5, 2, 2, 2.5, 1.5][i], lean=lean[i], handN=hn[i], wang=wang[i], handF=hf[i],
                plume=[(-7, -1), (-8, 0), (-9, 0), (-9, 1), (-10, 1), (-8, 0)][i], flap=[0, -1, -1, -2, -3, -1][i], shift=shift[i])


def atk_staff(i):
    # cast: the staff is raised and thrust forward; the fireball leaves on frame 3
    return _cast(i, [(6, 6), (2, -2), (0, -5), (7, -3), (8, -1), (6, 4)], [170, 185, 200, 110, 95, 125],
                 [-1, -2, -3, 1, 2, 1], [0, -6, -10, 6, 10, 4], [(2, 9), (-1, 4), (-2, 0), (5, -1), (6, 0), (3, 7)],
                 [0, 1, 2, -3, -5, -1])


def atk_staff_2(i):
    # 2nd cast: a quick flick of the staff
    return _cast(i, [(6, 6), (4, 0), (5, -3), (8, -2), (8, 0), (6, 4)], [170, 160, 140, 100, 92, 120],
                 [-1, 0, -1, 1, 2, 1], [0, -3, -5, 6, 8, 3], [(2, 9), (1, 6), (1, 4), (5, 0), (6, 1), (3, 7)],
                 [0, 0, 1, -3, -5, -1])


def atk_staff_3(i):
    # 3rd cast: raised high, then a big forward cast (the larger fireball that explodes)
    return _cast(i, [(6, 6), (3, -3), (2, -6), (8, -2), (9, 2), (7, 4)], [170, 190, 200, 115, 88, 120],
                 [-1, -2, -3, 2, 3, 1], [0, -8, -12, 10, 14, 6], [(2, 9), (0, 0), (-1, -4), (5, -2), (7, 1), (3, 7)],
                 [0, 1, 2, -4, -6, -1])


def atk_stomp(i):
    # secondary: the staff comes down on the ground in front (the spikes erupt on frame 3)
    return _cast(i, [(6, 6), (2, -3), (1, -6), (8, 2), (8, 8), (7, 6)], [170, 190, 200, 70, 52, 70],
                 [-1, -2, -3, 2, 3, 1], [0, -8, -12, 12, 16, 8], [(2, 9), (0, 2), (-1, -3), (5, 3), (6, 7), (3, 8)],
                 [0, 1, 2, -3, -4, -1])


def atk_storm(i):
    # special: both arms raised high with the staff (frame 0 = the charge pose), then a slam that calls the storm
    return _cast(i, [(4, -4), (4, -5), (5, -6), (8, -4), (10, 0), (6, 4)], [185, 190, 195, 170, 128, 118],
                 [-1, -1, 0, 1, 2, 1], [-2, -4, -6, 4, 10, 4], [(2, -2), (2, -4), (2, -5), (4, -3), (6, 0), (3, 6)],
                 [0, 0, 0, 0, -3, -3])


def build(out):
    ranger_extra = [('attack_bow_2', atk_bow_2, 10), ('attack_bow_3', atk_bow_3, 10),
                    ('attack_short', lambda i: dict(atk_short(i)), 12), ('attack_special', atk_rain, 10)]
    write_class_sheet(out, 'ranger', ranger_extra, 'bow', RANGER)
    xbow_extra = [('attack_crossbow_2', atk_xbow_2, 10), ('attack_crossbow_3', atk_xbow_3, 10),
                  ('attack_axe_small', atk_axe_small, 10), ('attack_special', atk_volley, 10)]
    write_class_sheet(out, 'crossbowman', xbow_extra, 'xbow', CROSSBOWMAN)
    mage_extra = [('attack_staff', atk_staff, 12), ('attack_staff_2', atk_staff_2, 12), ('attack_staff_3', atk_staff_3, 12),
                  ('attack_stomp', atk_stomp, 12), ('attack_special', atk_storm, 10)]
    write_class_sheet(out, 'mage', mage_extra, 'staff', MAGE, head=mage_head)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    build(out)
