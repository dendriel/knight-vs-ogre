"""Human character style proposals (static images, NOT used by the game).

The shared rig (sprite_rig.py) reads its body proportions and part drawers at call time, so a "style" here is a
temporary override: shorter legs / torso, a broader chest with pauldrons, another helmet, belt, cape, mail texture and a
darker palette. The poses are the existing ones (knight_gen / class_gen), so every style can show idle, sword, bow, staff...

    python art_tools/human_styles.py [out_dir]       (default: out/art_humanos)
"""
import os, sys, math
from contextlib import contextmanager
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sprite_rig as SR
import knight_gen as KG
import class_gen as CG
import enemy_gen as EG
import proposals_gen as PG

C = SR.C
SKIN = C(226, 176, 136); SKIN_D = C(168, 118, 88)
BONE = C(222, 214, 190); BONE_D = C(150, 140, 120)
OUTD = C(10, 8, 16)


# ------------------------------------------------------------------------------------------------ part drawers
def make_parts(st):
    """torso / head / arm / leg drawers closed over the style `st` (same signatures as the originals)."""
    rd, layer, seg, limb = SR.rd, SR.layer, SR.seg, SR.limb

    def torso(H, S, flap, cloth_ang=0, tabard=True):
        PN = SR.PN
        ux, uy = S[0] - H[0], S[1] - H[1]; l = math.hypot(ux, uy); ux /= l; uy /= l
        n = (-uy, ux)
        Wp_ = (H[0] + (S[0] - H[0]) * .4, H[1] + (S[1] - H[1]) * .4)
        sh, wa, hw = st['sh'], st['wa'], st['hip']
        def P(o, w): return (o[0] + n[0] * w, o[1] + n[1] * w)
        g = SR.vec(cloth_ang); pv = (g[1], -g[0]); hx, hy = rd(H)
        def Wp(v, u): return (int(round(hx + pv[0] * v + g[0] * u)), int(round(hy + pv[1] * v + g[1] * u)))
        def f(d):
            if st.get('robe'):                                                        # long robe down to the ankles
                bot = SR.GY - 3
                d.polygon([rd(P(H, hw)), rd(P(H, -hw)), (hx - hw - 3 + int(flap), bot), (hx + hw + 4 + int(flap), bot)], fill=PN['base'])
                d.polygon([rd(P(H, -hw)), (hx - hw - 3 + int(flap), bot), (hx - 1, bot)], fill=PN['shade'])
                d.line([(hx - hw - 3 + int(flap), bot), (hx + hw + 4 + int(flap), bot)], fill=SR.RED, width=1)
            if st.get('skirt'):                                                       # tunic / surcoat below the belt
                ln = st['skirt']
                d.polygon([Wp(-hw, 0), Wp(hw, 0), Wp(hw + 1 + flap, ln), Wp(-hw - 1 + flap, ln)], fill=SR.RED)
                d.polygon([Wp(-hw, 0), Wp(-hw + 3, 0), Wp(-hw + 3 + flap, ln), Wp(-hw - 1 + flap, ln)], fill=SR.RED_D)
                d.line([Wp(-hw - 1 + flap, ln), Wp(hw + 1 + flap, ln)], fill=SR.GOLD, width=1)
            d.polygon([rd(P(S, sh)), rd(P(Wp_, wa)), rd(P(H, hw)), rd(P(H, -hw)), rd(P(Wp_, -wa)), rd(P(S, -sh))], fill=PN['base'])
            d.line([rd(P(S, -sh)), rd(P(Wp_, -wa)), rd(P(H, -hw))], fill=PN['shade'], width=3 if st['sh'] >= 6 else 2)   # the back
            d.line([rd(P(S, sh - 1)), rd(P(Wp_, wa - 1))], fill=PN['hl'], width=1)
            if st.get('chest'):                                                       # a plate: highlight + a centre ridge
                d.line([rd(P(S, sh - 3)), rd(P(Wp_, wa - 3)), rd(P(H, hw - 2))], fill=PN['hl'], width=1)
                d.line([rd(P(S, 0)), rd(P(H, 0))], fill=PN['shade'], width=1)
            if tabard and st.get('tabard', True):
                tl = st.get('tab_len', 7)
                d.polygon([Wp(-4, -2), Wp(4, -2), Wp(5 + flap, tl), Wp(-4 + flap, tl)], fill=SR.RED)
                d.polygon([Wp(-4, -2), Wp(-2, -2), Wp(-2 + flap, tl), Wp(-4 + flap, tl)], fill=SR.RED_D)
                d.line([Wp(-4 + flap, tl), Wp(5 + flap, tl)], fill=SR.GOLD, width=1)
            d.line([Wp(-hw, -2), Wp(hw, -2)], fill=SR.LEATH, width=2)                 # belt
            d.point(Wp(2, -2), fill=SR.GOLD)
            if st.get('bandolier'):
                d.line([rd(P(S, sh - 1)), rd(P(H, -hw + 1))], fill=SR.LEATH_D, width=2)
                d.point(rd(P(Wp_, 0)), fill=SR.GOLD)
        im = layer(f)
        if st.get('mail'):                                                           # chain mail: a dither pattern on the plate colour
            px = im.load(); b, s = PN['base'], PN['shade']
            for y in range(im.height):
                for x in range(im.width):
                    if px[x, y][:3] == b[:3] and (x + y) % 2 == 0 and (x // 2 + y) % 3 != 0: px[x, y] = s
        return im

    def arm(S, target, pal, boot, pref='y'):
        E, Hd = SR.ik(S, target, SR.ARM_L, SR.ARM_L, pref)
        r = st['pr']
        def f(d):
            limb(d, [S, E], st.get('aw', 4), pal); limb(d, [E, Hd], st.get('aw', 4) - 1, pal)
            x, y = rd(Hd); d.ellipse([x - 2, y - 2, x + 1, y + 1], fill=boot)         # a glove / gauntlet
            if st.get('bracer'): d.line([rd(((E[0] + Hd[0]) / 2, (E[1] + Hd[1]) / 2)), rd(Hd)], fill=SR.LEATH, width=2)
            x, y = rd(S)
            d.ellipse([x - r, y - r, x + r, y + r - 1], fill=pal['base'])             # pauldron
            d.arc([x - r, y - r, x + r, y + r - 1], 200, 340, fill=pal['hl'])
            d.line([(x - r, y + 1), (x - r, y + r - 2)], fill=pal['shade'])
            d.line([(x - r + 1, y + r - 2), (x + r - 1, y + r - 2)], fill=pal['shade'])
            if st.get('spikes'):
                d.polygon([(x - 2, y - r), (x + 1, y - r), (x - 1, y - r - 4)], fill=pal['hl'])
            if st.get('rivet'): d.point((x, y - 1), fill=SR.GOLD)
        return layer(f), Hd

    def leg(Hp, A, pal, boot, pref='x'):
        K, A = SR.ik(Hp, A, SR.LEG1, SR.LEG2, pref)
        lift = SR.GY - A[1]; t = -int(round(lift * 0.35))
        lw = st.get('lw', 5)
        def f(d):
            limb(d, [Hp, K, A], lw, pal)
            x, y = rd(K); d.ellipse([x - 2, y - 2, x + 2, y + 1], fill=pal['hl'])        # knee pad
            ax, ay = rd(A)
            d.polygon([(ax - 3, ay - 2), (ax + 1, ay - 2), (ax + 6, ay + 1 + t), (ax + 6, ay + 2 + t), (ax - 3, ay + 2)], fill=boot)
            if st.get('greaves'): d.line([(ax - 2, ay - 4), (ax, ay - 7)], fill=pal['hl'], width=1)
        return layer(f)

    def head(c, plume):
        x, y = rd(c); kind = st['head']; PN = SR.PN
        def back(d):
            if st.get('cape'):                                                        # a cloak hanging from the shoulders
                sway = int(round(plume[0] * 0.5))
                d.polygon([(x - 3, y + 3), (x + 1, y + 4), (x - 2 + sway, y + 25), (x - 11 + sway, y + 23)], fill=SR.RED_D)
                d.polygon([(x - 3, y + 3), (x - 1, y + 4), (x - 4 + sway, y + 25), (x - 11 + sway, y + 23)], fill=SR.LEATH_D)
                d.line([(x - 11 + sway, y + 23), (x - 2 + sway, y + 25)], fill=SR.GOLD, width=1)
            if st.get('crest'):
                tx, ty = x + plume[0], y + plume[1]
                seg(d, (x - 2, y - 6), (tx, ty - 1), 3, SR.RED_D); seg(d, (x - 2, y - 7), (tx + 1, ty - 2), 2, SR.RED)
            if kind == 'hood':
                d.polygon([(x - 6, y - 2), (x - 8, y + 6), (x - 3, y + 6)], fill=SR.LEATH_D)
        def hd(d):
            if kind == 'kettle':
                d.ellipse([x - 5, y - 8, x + 5, y + 1], fill=PN['base'])
                d.line([(x - 1, y - 8), (x + 3, y - 8)], fill=PN['hl'])
                d.line([(x - 8, y - 1), (x + 7, y - 1)], fill=PN['shade'], width=2)             # the brim
                d.line([(x - 7, y - 2), (x + 6, y - 2)], fill=PN['hl'])
                d.rectangle([x - 3, y + 1, x + 4, y + 5], fill=SKIN); d.rectangle([x - 3, y + 1, x - 2, y + 5], fill=SKIN_D)
                d.rectangle([x + 2, y + 2, x + 3, y + 2], fill=OUTD)                             # an eye
                d.rectangle([x - 3, y + 5, x + 4, y + 6], fill=PN['shade'])                      # gorget
            elif kind == 'greathelm':
                d.rounded_rectangle([x - 5, y - 8, x + 5, y + 6], 3, fill=PN['base'])
                d.rectangle([x - 5, y - 8, x - 3, y + 6], fill=PN['shade'])
                d.line([(x - 1, y - 8), (x + 3, y - 8)], fill=PN['hl']); d.line([(x + 4, y - 6), (x + 5, y + 3)], fill=PN['hl'])
                d.rectangle([x, y - 3, x + 5, y - 2], fill=OUTD)                                  # eye slit
                d.line([(x + 2, y - 2), (x + 2, y + 5)], fill=PN['shade'])                        # centre ridge
                for k in range(3): d.point((x + 4, y + 1 + k * 2), fill=OUTD)                     # breathing holes
            elif kind == 'hood':
                d.ellipse([x - 5, y - 7, x + 5, y + 5], fill=SR.LEATH)
                d.ellipse([x - 4, y - 7, x + 5, y + 4], fill=SR.LEATH_D if st.get('dark_hood') else PN['base'])
                d.line([(x - 1, y - 7), (x + 3, y - 7)], fill=PN['hl'])
                d.rectangle([x, y - 3, x + 5, y + 2], fill=OUTD)                                  # shadowed face
                d.rectangle([x + 1, y - 1, x + 3, y + 2], fill=SKIN_D); d.point((x + 3, y - 1), fill=C(235, 220, 160))
                d.polygon([(x - 6, y - 2), (x - 9, y + 2), (x - 5, y + 3)], fill=SR.LEATH)
            elif kind == 'coif':
                d.ellipse([x - 5, y - 7, x + 5, y + 5], fill=PN['base'])
                px_ = [(x + i, y + j) for i in range(-4, 5) for j in range(-6, 5) if (i + j) % 2 == 0]
                for p in px_: d.point(p, fill=PN['shade'])
                d.rectangle([x + 1, y - 2, x + 5, y + 2], fill=SKIN); d.rectangle([x + 1, y - 2, x + 2, y + 2], fill=SKIN_D)
                d.point((x + 4, y - 1), fill=OUTD); d.line([(x + 3, y - 5), (x + 3, y + 1)], fill=PN['hl'])   # nose guard
                d.line([(x - 1, y - 7), (x + 3, y - 7)], fill=PN['hl'])
            elif kind == 'horned':
                d.ellipse([x - 5, y - 7, x + 5, y + 4], fill=PN['shade'])
                d.ellipse([x - 4, y - 7, x + 5, y + 3], fill=PN['base'])
                d.rectangle([x + 1, y - 3, x + 5, y - 2], fill=C(220, 60, 50))                    # glowing slit
                d.rectangle([x + 1, y + 1, x + 5, y + 1], fill=PN['shade']); d.rectangle([x - 3, y + 4, x + 3, y + 6], fill=PN['shade'])
                d.polygon([(x - 4, y - 5), (x - 2, y - 6), (x - 8, y - 12)], fill=BONE)
                d.polygon([(x + 2, y - 6), (x + 4, y - 5), (x + 7, y - 12)], fill=BONE_D)
            elif kind == 'wizhat':
                d.ellipse([x - 4, y - 5, x + 5, y + 4], fill=SKIN)
                d.rectangle([x + 1, y - 2, x + 5, y - 1], fill=OUTD); d.rectangle([x - 2, y + 1, x + 5, y + 5], fill=C(200, 200, 205))   # a beard
                d.polygon([(x - 8, y - 4), (x + 8, y - 4), (x + 4, y - 7), (x + 2, y - 15), (x - 3, y - 9), (x - 4, y - 7)], fill=PN['base'])
                d.polygon([(x - 8, y - 4), (x, y - 4), (x - 1, y - 12), (x - 4, y - 7)], fill=PN['hl'])
                d.line([(x - 8, y - 4), (x + 8, y - 4)], fill=PN['shade'], width=2)
        return layer(back), layer(hd)

    return torso, head, arm, leg


# ------------------------------------------------------------------------------------------------ styles
def pal(pn, pf, red, red_d, gold, leath, leath_d):
    return dict(PN=dict(shade=pn[0], base=pn[1], hl=pn[2]), PF=dict(shade=pf[0], base=pf[1], hl=pf[2]),
                RED=red, RED_D=red_d, GOLD=gold, LEATH=leath, LEATH_D=leath_d)


STYLES = {
    'atual': dict(label='ATUAL', geom=None),
    'soldado': dict(
        label='A  Soldado robusto', pct=85,
        geom=dict(LEG1=7.5, LEG2=8, TORSO_L=11, ARM_L=6, HEAD_UP=6),
        st=dict(sh=6.5, wa=5, hip=4.5, pr=4, lw=5, aw=4, head='kettle', chest=True, skirt=0, tab_len=8, rivet=True),
        pal=pal((C(40, 40, 50), C(98, 100, 114), C(168, 172, 188)), (C(24, 24, 32), C(62, 64, 76), C(104, 108, 122)),
                C(120, 36, 40), C(72, 22, 28), C(196, 160, 80), C(96, 66, 44), C(58, 40, 30))),
    'blindado': dict(
        label='B  Cavaleiro blindado', pct=80,
        geom=dict(LEG1=7, LEG2=7, TORSO_L=10, ARM_L=6, HEAD_UP=6),
        st=dict(sh=7.5, wa=6, hip=5, pr=5, lw=5, aw=5, head='greathelm', chest=True, tab_len=7, spikes=True, rivet=True, greaves=True,
                crest=True),
        pal=pal((C(52, 58, 80), C(124, 134, 164), C(206, 216, 242)), (C(30, 34, 50), C(78, 86, 112), C(130, 142, 172)),
                C(150, 30, 36), C(90, 18, 26), C(214, 178, 70), C(70, 52, 40), C(44, 32, 26))),
    'mercenario': dict(
        label='C  Mercenario de couro', pct=88,
        geom=dict(LEG1=8, LEG2=8, TORSO_L=11, ARM_L=6.5, HEAD_UP=6),
        st=dict(sh=6, wa=4.5, hip=4, pr=3, lw=4, aw=4, head='hood', tabard=False, cape=True, skirt=6, bracer=True, bandolier=True),
        pal=pal((C(54, 42, 30), C(112, 88, 62), C(170, 142, 102)), (C(34, 26, 20), C(76, 58, 40), C(112, 90, 64)),
                C(86, 44, 36), C(48, 26, 24), C(190, 150, 70), C(70, 50, 34), C(44, 32, 24))),
    'sombrio': dict(
        label='D  Guarda sombrio', pct=82,
        geom=dict(LEG1=7.5, LEG2=7.5, TORSO_L=10.5, ARM_L=6, HEAD_UP=6),
        st=dict(sh=7, wa=5.5, hip=4.5, pr=4, lw=5, aw=4, head='horned', chest=True, spikes=True, tab_len=9, cape=True, greaves=True),
        pal=pal((C(30, 28, 46), C(82, 76, 112), C(160, 152, 196)), (C(18, 16, 28), C(52, 48, 72), C(100, 94, 130)),
                C(120, 24, 40), C(66, 14, 28), C(180, 70, 60), C(52, 38, 40), C(32, 24, 28))),
    'veterano': dict(
        label='E  Veterano de cota de malha', pct=85,
        geom=dict(LEG1=7.5, LEG2=8, TORSO_L=11, ARM_L=6, HEAD_UP=6),
        st=dict(sh=6.5, wa=5, hip=4.5, pr=3, lw=5, aw=4, head='coif', mail=True, skirt=9, tab_len=5, tabard=False, bracer=True),
        pal=pal((C(52, 54, 58), C(118, 122, 128), C(184, 190, 196)), (C(32, 34, 38), C(78, 82, 88), C(120, 126, 134)),
                C(72, 84, 70), C(44, 54, 44), C(176, 150, 80), C(88, 62, 42), C(52, 38, 28))),
    'cruzado': dict(
        label='F  Cavaleiro cruzado', pct=82,
        geom=dict(LEG1=7, LEG2=7.5, TORSO_L=10.5, ARM_L=6, HEAD_UP=6),
        st=dict(sh=7, wa=5.5, hip=5, pr=4, lw=5, aw=4, head='greathelm', chest=True, skirt=12, tab_len=11, cape=True, rivet=True),
        pal=pal((C(60, 62, 72), C(150, 154, 168), C(226, 230, 240)), (C(36, 38, 46), C(92, 96, 108), C(140, 144, 160)),
                C(196, 190, 176), C(130, 124, 110), C(204, 170, 70), C(74, 54, 40), C(46, 34, 26))),
}

# the other human roles keep the proportions of a style but change the head / palette (set per use below)
RANGER_PAL = pal((C(24, 40, 28), C(62, 98, 58), C(122, 162, 92)), (C(14, 26, 18), C(40, 68, 40), C(70, 100, 60)),
                 C(190, 150, 50), C(130, 100, 30), C(190, 160, 80), C(86, 60, 36), C(56, 40, 26))
MAGE_PAL = pal((C(34, 26, 60), C(80, 62, 130), C(140, 118, 190)), (C(20, 16, 40), C(52, 40, 90), C(88, 72, 130)),
               C(220, 180, 70), C(150, 112, 36), C(240, 210, 110), C(70, 48, 36), C(44, 30, 24))
ENEMY_PAL = pal((C(48, 40, 62), C(104, 92, 126), C(168, 156, 194)), (C(30, 24, 42), C(66, 58, 86), C(104, 96, 128)),
                C(96, 52, 130), C(58, 28, 88), C(170, 136, 66), C(84, 56, 40), C(52, 36, 26))


@contextmanager
def style_ctx(name, palette=None, **over):
    """Draw with the rig under style `name` (geometry + parts); `palette` replaces the style's colours; **over change the
    style dict (head=..., cape=...)."""
    s = STYLES[name]
    if s['geom'] is None:
        yield; return
    st = dict(s['st'], **over)
    torso, head, arm, leg = make_parts(st)
    ov = dict(s['geom'], torso=torso, head=head, arm=arm, leg=leg, **(palette or s['pal']))
    with EG.palette(SR, **ov): yield


def render(name, pose, palette=None, **over):
    with style_ctx(name, palette, **over): return SR.render(pose)


# ------------------------------------------------------------------------------------------------ images
def figure(name, role, pose_i=3, **kw):
    """One frame of a role in a style. roles: knight (idle), knight_atk, ranger (bow), mage (staff), soldier (enemy sword)."""
    if role == 'knight': return render(name, KG.idle(0), **kw)
    if role == 'knight_atk': return render(name, KG.atk_sword(pose_i), **kw)
    if role == 'ranger': return render(name, KG.atk_bow(1), palette=RANGER_PAL, head='hood', cape=False, tabard=False, skirt=0,
                                       chest=False, mail=False, spikes=False, **kw)
    if role == 'mage': return render(name, KG.carry(KG.idle(0), 'staff'), palette=MAGE_PAL, head='wizhat', robe=True, cape=False,
                                     tabard=False, skirt=0, chest=False, mail=False, spikes=False, **kw)
    if role == 'soldier': return render(name, KG.idle(0), palette=ENEMY_PAL, **kw)
    raise KeyError(role)


def prep(im, f=1.0, out=OUTD):
    """grade for the dark look + re-outline in the dark outline colour (same finishing as the scene images)."""
    g = PG.make_grade(sat=0.8, val=0.9, contrast=1.1)
    im = PG.grade_image(PG.strip_outline(im), g)
    return PG.outline(im, out[:3])


def lineup(path):
    roles = [('knight', 'Cavaleiro'), ('knight_atk', 'Golpe'), ('ranger', 'Arqueiro'), ('mage', 'Mago'), ('soldier', 'Soldado (inimigo)')]
    names = list(STYLES)
    cw, ch, z = 56, 54, 6
    img = Image.new('RGB', (len(roles) * cw * z + 260, len(names) * ch * z), (36, 38, 48))
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    for r, n in enumerate(names):
        y0 = r * ch * z
        d.rectangle([0, y0, img.width, y0 + ch * z - 1], fill=(44, 46, 58) if r % 2 else (36, 38, 48))
        d.text((10, y0 + 10), STYLES[n]['label'], fill=(255, 240, 200))
        if STYLES[n].get('pct'): d.text((10, y0 + 28), f"altura ~{STYLES[n]['pct']}%", fill=(190, 190, 200))
        for c, (role, lab) in enumerate(roles):
            im = figure(n, role)
            im = im.crop((8, 8, 8 + cw, 8 + ch))
            im = im.resize((cw * z, ch * z), Image.NEAREST)
            bg = Image.new('RGBA', im.size, (0, 0, 0, 0)); bg.alpha_composite(im)
            img.paste(bg, (260 + c * cw * z, y0), bg)
            if r == 0: d.text((260 + c * cw * z + 8, 4), lab, fill=(220, 220, 230))
        d.line([(0, y0 + ch * z - 1), (img.width, y0 + ch * z - 1)], fill=(70, 72, 86))
    img.save(path)


HUMANS = ('knight', 'ranger', 'mage', 'soldier', 'shieldman', 'spearman', 'archer', 'crossbowman', 'black_knight')


def _human(style, name, anim, i):
    """Styled frame of a human role for the pose the scene asks for (sheet name + animation + frame)."""
    over = {}
    if name == 'knight': pal_ = None
    elif name == 'mage': pal_ = MAGE_PAL; over = dict(head='wizhat', robe=True, cape=False, tabard=False, skirt=0, chest=False, mail=False, spikes=False)
    elif name in ('ranger', 'archer'):
        pal_ = RANGER_PAL; over = dict(head='hood', cape=False, tabard=False, skirt=0, chest=False, mail=False, spikes=False)
    elif name == 'black_knight': pal_ = ENEMY_PAL; over = dict(head='horned', spikes=True)
    else: pal_ = ENEMY_PAL                                              # soldier / shieldman / spearman / crossbowman: enemy colours
    if anim == 'attack_staff': pose = CG.atk_staff(i)
    elif anim in ('attack_sword', 'attack'): pose = KG.atk_sword(i)
    elif anim == 'walk': pose = KG.walk(i)
    elif anim == 'hurt': pose = KG.hurt(i)
    elif name == 'mage': pose = KG.carry(KG.idle(i), 'staff')
    elif name in ('ranger', 'archer'): pose = KG.atk_bow(1)
    elif name == 'crossbowman': pose = KG.atk_xbow(1)
    elif name == 'spearman': pose = KG.carry(KG.idle(i), 'spear')
    else: pose = KG.idle(i)
    if name == 'shieldman' or anim == 'guard': pose = dict(pose, shield=True)
    return render(style, pose, palette=pal_, **over)


def styled_place(style, original):
    def place(scene, name, anim, i, x_hip, flip=False, f=0.85, g=None, light='l', rim=(255, 220, 170), rim_amt=0.4,
              shade=0.25, out=(10, 8, 16), top_boost=0.08, dy=0, fs_override=None):
        if name not in HUMANS: return original(scene, name, anim, i, x_hip, flip, f, g, light, rim, rim_amt, shade, out, top_boost, dy)
        im = PG.strip_outline(_human(style, name, anim, i))
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if g: im = PG.grade_image(im, g)
        im = PG.lit(im, light, rim, rim_amt, shade, out, top_boost)
        scene.blit(im, x_hip - PG.hip_col('knight', flip), PG.GROUND_Y - 58 + dy)
    return place


MOODS = [('soldado', PG.p1_penumbra, '01_soldado_robusto'), ('blindado', PG.p4_masmorra, '02_cavaleiro_blindado'),
         ('mercenario', PG.p5_chuva, '03_mercenario_de_couro'), ('sombrio', PG.p3_noite, '04_guarda_sombrio'),
         ('veterano', PG.p2_cinzas, '05_veterano_cota_de_malha'), ('cruzado', PG.p6_inverno, '06_cavaleiro_cruzado')]


def scenes(out):
    orig_place, orig_finish = PG.place, PG.finish
    for style, fn, fname in MOODS:
        cap = []
        PG.place = styled_place(style, orig_place); PG.finish = lambda scene, path, t, s_: cap.append(scene)
        try: fn(out)
        finally: PG.place, PG.finish = orig_place, orig_finish
        st = STYLES[style]
        PG.finish(cap[0], os.path.join(out, fname + '.png'), 'Estilo ' + st['label'],
                  'humanos ~%d%% da altura atual, ombros/peito mais largos; monstros inalterados' % st['pct'])
        print('wrote', fname)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'out', 'art_humanos')
    os.makedirs(out, exist_ok=True)
    lineup(os.path.join(out, '00_linha_de_estilos.png'))
    print('wrote lineup')
    scenes(out)


if __name__ == '__main__':
    main()
