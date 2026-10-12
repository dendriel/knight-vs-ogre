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
    # golpe LATERAL: a lamina fica na altura do ombro e varre de tras para a frente (nao desce de cima)
    hx = [-1, -3, -4, 2, 5, 2][i]
    return dict(weapon='sword', hx=hx, footN=(CX + 8, GY), footF=(CX - 5, GY),
                sink=[1, 2, 2.5, 2.5, 3, 2][i], lean=[-4, -12, -16, 6, 18, 8][i],
                handN=[(5, -2), (-4, -4), (-5, -3), (7, -1), (12, 0), (5, 1)][i],
                wang=[175, 240, 252, 100, 80, 98][i],
                handF=[(-1, 10), (-6, 2), (-8, 0), (-5, 1), (-2, 3), (0, 10)][i],
                plume=[(-7, -1), (-8, 1), (-9, 1), (-9, 0), (-10, 2), (-8, 0)][i],
                flap=[0, -1, -2, -2, -3, -1][i],
                shift=[0, 1, 3, -1, -3, 0][i])

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


def jump_up(i):
    # subindo: impulso (i0 agacha) -> estica -> encolhe o joelho da frente; o pe de tras fica na linha do chao
    return dict(weapon='sword', hx=[0, 0, 1, 1, 1, 1][i],
                footN=[(CX + 5, GY), (CX + 5, GY - 3), (CX + 7, GY - 8), (CX + 8, GY - 11), (CX + 8, GY - 12), (CX + 7, GY - 11)][i],
                footF=[(CX - 4, GY), (CX - 5, GY), (CX - 5, GY - 1), (CX - 4, GY), (CX - 4, GY), (CX - 4, GY)][i],
                sink=[2.5, 0, 0, 0, 0, 0][i], lean=[0, 6, 8, 8, 6, 6][i],
                handN=[(7, 8), (9, -3), (10, -7), (9, -9), (9, -9), (9, -8)][i],
                wang=[165, 145, 128, 120, 118, 122][i],
                handF=[(1, 11), (-2, 4), (-4, -1), (-5, -3), (-5, -3), (-5, -2)][i],
                plume=[(-7, -1), (-8, 1), (-8, 2), (-8, 3), (-8, 3), (-8, 2)][i],
                flap=[0, 1, 2, 2, 3, 2][i], shift=[0, 0, 0, 0, 0, 0][i])

def jump_fall(i):
    # caindo: pernas esticadas, bracos abertos para equilibrio, capa e pluma subindo (loop de 6 quadros)
    return dict(weapon='sword', hx=0,
                footN=[(CX + 8, GY - 1), (CX + 8, GY - 1), (CX + 7, GY - 2), (CX + 8, GY - 2), (CX + 8, GY - 1), (CX + 7, GY - 1)][i],
                footF=[(CX - 7, GY), (CX - 7, GY), (CX - 6, GY), (CX - 7, GY), (CX - 7, GY), (CX - 6, GY)][i],
                sink=0, lean=[-2, -3, -2, -3, -2, -3][i],
                handN=[(9, -5), (9, -6), (10, -5), (9, -4), (9, -5), (10, -6)][i],
                wang=[150, 146, 148, 152, 148, 145][i],
                handF=[(-3, -3), (-4, -4), (-3, -2), (-4, -3), (-3, -4), (-4, -3)][i],
                plume=[(-7, 2), (-8, 3), (-7, 3), (-8, 2), (-7, 3), (-8, 3)][i],
                flap=[3, 4, 3, 4, 3, 4][i])

def atk_sword_2(i):
    # 2o golpe do combo: corte ASCENDENTE de baixo-tras para cima-frente (varre perto do chao e sobe); golpe nos frames 3-4
    return dict(weapon='sword', hx=[-1, -3, -2, 3, 5, 2][i], footN=(CX + 8, GY), footF=(CX - 5, GY),
                sink=[1, 3, 3.5, 2, 2.5, 2][i], lean=[-2, -12, -16, 10, 20, 8][i],
                handN=[(5, -2), (-2, 6), (-5, 8), (6, -5), (11, -8), (6, -2)][i],
                wang=[175, 300, 320, 70, 112, 122][i],
                handF=[(-1, 10), (-6, 6), (-8, 4), (-5, 0), (-2, -2), (0, 10)][i],
                plume=[(-7, -1), (-8, 1), (-9, 2), (-9, 0), (-10, 2), (-8, 0)][i],
                flap=[0, -1, -2, -2, -3, -1][i], shift=[0, 1, 3, -1, -3, 0][i])

def atk_sword_3(i):
    # 3o golpe (finalizador): a espada sobe acima da cabeca e desce em um golpe forte, com o corpo todo para a frente
    return dict(weapon='sword', hx=[-1, -1, 0, 4, 6, 1][i], footN=(CX + 9, GY), footF=(CX - 6, GY),
                sink=[1, 0, 0, 3, 4.5, 3][i], lean=[-4, -8, -12, 16, 28, 12][i],
                handN=[(5, -2), (4, -6), (2, -8), (8, -4), (11, 5), (3, 3)][i],
                wang=[175, 185, 196, 128, 72, 90][i],
                handF=[(-1, 10), (0, 0), (0, -6), (-2, -2), (2, 4), (0, 10)][i],
                plume=[(-7, -1), (-8, 0), (-9, -2), (-9, 1), (-11, 3), (-8, 0)][i],
                flap=[0, -1, -1, -3, -4, -1][i], shift=[0, 0, 1, -2, -4, -2][i])

def atk_special(i):
    # especial giratorio: frame 0 = carga (agachado, espada recolhida; o jogo congela nele enquanto segura), 1-5 = giro:
    # a lamina varre para a frente e para tras com o corpo torcido; o aro de luz (vfx spin_slash) completa os 360 graus
    return dict(weapon='sword', hx=[-2, -1, 2, -2, 2, 0][i], footN=(CX + 9, GY), footF=(CX - 7, GY),
                sink=[3, 2, 1.5, 1.5, 1.5, 2][i], lean=[-12, -4, 10, -10, 12, 4][i],
                handN=[(-4, 4), (-2, 0), (11, -1), (-11, -1), (11, -1), (6, 0)][i],
                wang=[250, 270, 92, 268, 92, 130][i],
                handF=[(-6, 6), (-3, 2), (6, 1), (-8, 1), (6, 1), (0, 8)][i],
                plume=[(-8, 1), (-9, 0), (-6, -1), (-10, 1), (-6, -1), (-8, 0)][i],
                flap=[-1, -2, -4, 2, -4, -1][i], shift=[1, 0, -2, 2, -2, 0][i])

def atk_spear(i):
    # estocada: recolhe a lanca, o corpo vai todo para a frente no golpe (frames 3-4 acertam)
    return dict(weapon='spear', hx=[0, -3, -4, 3, 5, 2][i], footN=(CX + 8, GY), footF=(CX - 6, GY),
                sink=[1, 2, 2.5, 2.5, 3, 2][i], lean=[0, -10, -14, 10, 16, 5][i],
                handN=[(6, 4), (-1, 5), (-5, 5), (10, 3), (13, 3), (8, 4)][i],
                wang=[110, 102, 98, 92, 90, 100][i],
                handF=[(2, 9), (0, 8), (-2, 8), (4, 6), (6, 6), (3, 8)][i],
                plume=[(-7, -1), (-8, 1), (-9, 1), (-9, 0), (-10, 2), (-8, 0)][i],
                flap=[0, -1, -2, -2, -3, -1][i], shift=[-2, 1, 2, -5, -7, -3][i])

ANIMS = [('idle', idle, 6), ('walk', walk, 10), ('run', lambda i: walk(i, True), 12),
         ('attack_sword', atk_sword, 12), ('attack_axe', atk_axe, 10),
         ('attack_bow', atk_bow, 10), ('attack_crossbow', atk_xbow, 10),
         ('hurt', hurt, 10), ('death', death, 8),
         ('jump_up', jump_up, 12), ('jump_fall', jump_fall, 10),
         ('attack_sword_2', atk_sword_2, 12), ('attack_sword_3', atk_sword_3, 12),
         ('attack_special', atk_special, 12)]
NOLOOP = ('attack', 'hurt', 'death')

def carry(pose, weapon):
    """Same pose, holding another weapon (T13). Melee poses just swap the sword for the axe; ranged rows keep theirs."""
    if weapon in ('bow', 'xbow') and pose['weapon'] == 'sword':
        pose = dict(pose, hold=weapon)                               # melee pose, bow / crossbow carried in the hand
        if weapon == 'xbow': pose['wang'] = (pose['wang'] + 2 * 165) / 3.0      # held more upright than a blade (stays inside the frame)
        if pose.get('wpos'): pose['wpos'] = (pose['wpos'][0] - 8, pose['wpos'][1] - 3)     # keep the lying weapon inside the frame
    if weapon == 'spear' and pose['weapon'] == 'sword':
        pose = dict(pose, weapon='spear')                            # carried tilted forward so it stays inside the frame
        if not pose.get('wback'): pose['wang'] = 132 + (pose['wang'] - 165) * 0.45
        pose['shift'] = pose.get('shift', 0) - 3
        if pose.get('wpos'): pose['wpos'] = (pose['wpos'][0] - 4, pose['wpos'][1] - 2)
        return pose
    if weapon == 'axe' and pose['weapon'] == 'sword':
        pose = dict(pose, weapon='axe')
        if pose.get('wpos'): pose['wpos'] = (pose['wpos'][0], pose['wpos'][1] - 3)     # the axe head is bigger: keep it in the frame
    return pose


def write_sheet(out, weapon=None):
    """weapon=None -> knight_spritesheet; 'axe' / 'bow' / 'xbow' -> knight_<weapon>_spritesheet (every row, hero holding it)."""
    name = 'knight' + (f'_{weapon}' if weapon else '')
    sheet = Image.new('RGBA', (F * 6, F * len(ANIMS)), (0, 0, 0, 0))
    atlas = {'frames': [], 'animations': {}, 'meta': {'image': f'{name}_spritesheet.png', 'frame_size': [64, 64], 'facing': 'right'}}
    for r, (an, fn, fps) in enumerate(ANIMS):
        for i in range(6):
            sheet.alpha_composite(render(carry(fn(i), weapon)), (i * F, r * F))
            atlas['frames'].append({'filename': f'{an}_{i}', 'frame': {'x': i * F, 'y': r * F, 'w': F, 'h': F}})
        atlas['animations'][an] = {'frames': [f'{an}_{i}' for i in range(6)], 'fps': fps, 'loop': not an.startswith(NOLOOP)}
    sheet.save(f'{out}/{name}_spritesheet.png')
    json.dump(atlas, open(f'{out}/{name}_spritesheet.json', 'w'), indent=2)
    print(name, 'ok', sheet.size)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else './out'; os.makedirs(out, exist_ok=True)
    write_sheet(out)
    write_sheet(out, 'axe')
    write_sheet(out, 'bow')
    write_sheet(out, 'xbow')
