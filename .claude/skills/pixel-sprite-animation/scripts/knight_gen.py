import sys
from sprite_rig import *
# ---------------- poses ----------------
def idle(i):
    br = [0, 0, 1, 1, 1, 0][i]
    return dict(weapon='sword', footN=(CX + 5, GY), footF=(CX - 4, GY), sink=1, tdy=br, lean=2,
                handN=(7, 8), wang=165, handF=(1, 11), plume=(-7, -2 + br), flap=0)

def walk(i, run=False):
    p = math.radians(i * 60 + 30); c, s = math.cos(p), math.sin(p)
    St, Lf = (9, 6) if run else (6, 3)
    def foot(ph): return (CX + St * math.cos(ph), GY - Lf * max(0, -math.sin(ph)))
    if run:
        return dict(weapon='sword', footN=foot(p), footF=foot(p + math.pi), sink=.5 + 2.5 * abs(c), lean=14,
                    handN=(8 - 3 * c, 4 - 2 * s), wang=125 - 8 * c, handF=(3 + 7 * c, 6 - 3 * max(0, c)),
                    plume=(-10, 1 + s), flap=-3)
    return dict(weapon='sword', footN=foot(p), footF=foot(p + math.pi), sink=.4 + 1.2 * abs(c), lean=4,
                handN=(7 - 2 * c, 8), wang=160 - 5 * c, handF=(2 + 4 * c, 10 - abs(s)),
                plume=(-7, -1 + s), flap=-1)

def atk_sword(i):
    hx = [-1, -3, 0, 3, 5, 2][i]
    return dict(weapon='sword', hx=hx, footN=(CX + 8, GY), footF=(CX - 5, GY),
                sink=[1, 1.5, 1, 2, 3.5, 2][i], lean=[-4, -12, -2, 8, 16, 6][i],
                handN=[(5, -2), (-5, -8), (6, -9), (11, 0), (10, 7), (6, 2)][i],
                wang=[175, 225, 150, 100, 35, 120][i],
                handF=[(-1, 10), (-8, 3), (-8, -1), (-6, 4), (-4, 9), (0, 10)][i],
                plume=[(-7, -1), (-8, 1), (-7, -2), (-9, 0), (-10, 2), (-8, 0)][i],
                flap=[0, -1, 0, -2, -3, -1][i],
                trail=[None, None, None, (160, 95, 18), (100, 35, 18), None][i],
                shift=[0, 0, 0, -2, -2, 0][i])

def atk_axe(i):
    hx = [-1, -3, -2, 1, 0, 0][i]
    return dict(weapon='axe', hx=hx, footN=(CX + 8, GY), footF=(CX - 5, GY),
                sink=[1, 1.5, 1, 2.5, 4, 2][i], lean=[-4, -14, -8, 12, 22, 6][i],
                handN=[(5, -4), (-4, -10), (-1, -10), (7, -6), (9, 6), (7, 0)][i],
                wang=[185, 215, 200, 140, 70, 165][i],
                plume=[(-7, -1), (-8, 1), (-8, -2), (-9, 0), (-10, 3), (-8, 0)][i],
                flap=[0, -1, 0, -2, -4, -1][i],
                trail=[None, None, None, (195, 130, 19), (135, 60, 17), None][i],
                shift=[0, 0, 0, -2, -3, 0][i])


def atk_bow(i):
    return dict(weapon='bow', footN=(CX + 7, GY), footF=(CX - 6, GY),
                sink=[1, 1, 1.5, 2, 2, 1][i], lean=[0, 0, -2, -4, -3, -1][i],
                bowhand=[(7, 5), (10, -1), (12, -5), (12, -5), (11, -5), (9, 0)][i],
                aim=[65, 80, 90, 92, 94, 75][i],
                pull=[0, 0, 4, 9, 0, 0][i], hand_pull=[0, 0, 4, 9, 10, 4][i],
                arrow=['nock', 'nock', 'nock', 'nock', 'fly', None][i],
                elbow=['y', 'y', 'xm', 'xm', 'xm', 'y'][i],
                plume=[(-7, -1), (-7, -1), (-8, -1), (-8, 0), (-9, 1), (-8, 0)][i],
                flap=[0, 0, -1, -1, -2, -1][i],
                shift=[0, 0, 0, 0, -3, 0][i])

def atk_xbow(i):
    return dict(weapon='xbow', footN=(CX + 7, GY), footF=(CX - 6, GY),
                sink=[1, 1, 1.5, 1.5, 2, 1][i], lean=[0, 0, -2, -2, -4, -1][i],
                R=[(-2, 8), (-1, 3), (1, -2), (1, -3), (-1, -3), (-1, 2)][i],
                ang=[100, 95, 92, 90, 98, 100][i],
                loaded=[True, True, True, True, False, False][i],
                bolt=['load', 'load', 'load', 'load', 'fly', None][i],
                plume=[(-7, -1), (-7, -1), (-8, -1), (-8, 0), (-9, 1), (-8, 0)][i],
                flap=[0, 0, -1, -1, -2, -1][i],
                shift=[0, 0, 0, 0, -2, 0][i])


def hurt(i):
    return dict(weapon='sword', hx=[-1, -4, -5, -4, -2, 0][i],
                footN=[(CX + 6, GY), (CX + 4, GY), (CX + 3, GY), (CX + 3, GY), (CX + 4, GY), (CX + 5, GY)][i],
                footF=[(CX - 4, GY), (CX - 7, GY), (CX - 8, GY), (CX - 7, GY), (CX - 5, GY), (CX - 4, GY)][i],
                sink=[1, 1.5, 2, 2, 1.5, 1][i], lean=[-6, -16, -14, -8, -3, 2][i],
                handN=[(7, 6), (3, -2), (1, -4), (4, 2), (6, 6), (7, 8)][i],
                wang=[165, 200, 205, 185, 170, 165][i],
                handF=[(1, 11), (-7, 3), (-8, 2), (-5, 6), (-2, 9), (1, 11)][i],
                headoff=[(0, 0), (-2, -1), (-2, 0), (-1, 0), (0, 0), (0, 0)][i],
                plume=[(-7, -1), (-9, -2), (-9, -1), (-8, 0), (-7, -1), (-7, -1)][i],
                flash=[.85, .3, 0, 0, 0, 0][i], flap=[0, 1, 1, 0, 0, 0][i])

def death(i):
    lying = i >= 3
    return dict(weapon='sword', hx=[-1, -4, -2, 4, 4, 4][i],
                footN=[(CX + 6, GY), (CX + 7, GY), (CX + 13, GY), (CX + 19, GY), (CX + 19, GY), (CX + 19, GY)][i],
                footF=[(CX - 4, GY), (CX - 6, GY), (CX + 8, GY - 3), (CX + 17, GY), (CX + 17, GY), (CX + 17, GY)][i],
                sink=[1, 3, 3, 4.5, 3, 4][i], lean=[-8, -22, -52, -86, -88, -88][i],
                handN=[(5, 5), (0, -3), (-4, -6), (-9, 3), (-9, 4), (-9, 4)][i],
                handF=[(-1, 10), (-6, 2), (-8, -2), (-6, -5), (-7, -4), (-7, -4)][i],
                wang=[165, 200, 120, 250, 270, 270][i],
                wpos=[None, None, (40, 34), (54, 55), (56, 57), (56, 57)][i], wback=lying,
                rot_head=i >= 1, head_rot=90 if lying else 0, knee='ym' if lying else 'x',
                cloth_ang=[0, 0, 40, 88, 88, 88][i],
                plume=[(-7, -1), (-9, -2), (-9, -1), (-8, 0), (-7, -1), (-7, -1)][i],
                flash=[.85, 0, 0, 0, 0, 0][i], flap=0)

ANIMS = [('idle', idle, 6), ('walk', walk, 10), ('run', lambda i: walk(i, True), 12),
         ('attack_sword', atk_sword, 12), ('attack_axe', atk_axe, 10),
         ('attack_bow', atk_bow, 10), ('attack_crossbow', atk_xbow, 10),
         ('hurt', hurt, 10), ('death', death, 8)]
NOLOOP = ('attack', 'hurt', 'death')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    sheet = Image.new('RGBA', (F * 6, F * len(ANIMS)), (0, 0, 0, 0))
    atlas = {'frames': [], 'animations': {}, 'meta': {'image': 'knight_spritesheet.png', 'frame_size': [64, 64], 'facing': 'right'}}
    for r, (name, fn, fps) in enumerate(ANIMS):
        for i in range(6):
            sheet.alpha_composite(render(fn(i)), (i * F, r * F))
            atlas['frames'].append({'filename': f'{name}_{i}', 'frame': {'x': i * F, 'y': r * F, 'w': F, 'h': F}})
        atlas['animations'][name] = {'frames': [f'{name}_{i}' for i in range(6)], 'fps': fps, 'loop': not name.startswith(NOLOOP)}
    sheet.save(f'{out}/knight_spritesheet.png')
    json.dump(atlas, open(f'{out}/knight_spritesheet.json', 'w'), indent=2)
    print('knight ok', sheet.size)
