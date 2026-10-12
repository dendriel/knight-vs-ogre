"""Runs the REAL main.py / view.py / logic.py with a scripted player and records what the screen shows."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import fake_pygame as fp
sys.modules['pygame'] = fp.module
import main
from game import config as C
from PIL import Image


def keys_for(pressed_names):
    fp.PRESSED.clear()
    for n in pressed_names: fp.PRESSED.add({'left': fp.K_LEFT, 'right': fp.K_RIGHT, 'space': fp.K_SPACE, 'attack': fp.MOUSE_LEFT, 'a': fp.K_a, 'd': fp.K_d}[n])


def smart_bot(w):
    """approach, attack, and step back while the ogre winds up"""
    h, o = w.hero, w.ogre; d = o.x - h.x; names = []
    if o.state == 'dead' or h.state != 'idle' and h.state != 'walk': return names
    if o.state == 'attack' and o.frame_index(w.timing) <= 2 and abs(d) < 56:
        return ['left'] if d > 0 else ['right']
    if abs(d) > 41: return ['right'] if d > 0 else ['left']
    return ['attack']


def record(total_s, policy, stills=(), every=3, out_dir='out'):
    g = main.Game('endless'); frames = []; stills = dict(stills)
    for n in range(int(total_s * 60)):
        t = n / 60
        keys_for(policy(g.world, t))
        g.handle_events(); g.update(1 / 60); g.draw(); g.present()
        if n % every == 0: frames.append(g.screen.img.convert('RGB').copy())
        if n in stills: g.screen.img.resize((960, 540), Image.NEAREST).save(os.path.join(out_dir, stills[n]))
    return g, frames


def save_gif(frames, path, fps=20, scale=2):
    big = [f.resize((f.width * scale, f.height * scale), Image.NEAREST) for f in frames]
    step = max(1, len(big) // 10); mont = Image.new('RGB', (big[0].width, big[0].height * 10))
    for i in range(10): mont.paste(big[min(i * step, len(big) - 1)], (0, i * big[0].height))
    pal = mont.quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [b.quantize(palette=pal, dither=Image.NONE) for b in big]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=False)
    print(path, os.path.getsize(path) // 1024, 'KB', len(q), 'frames')

def record_windows(total_s, policy, windows, every=6, stills=()):
    """simulate everything, but only draw frames inside the given [start, end) windows (keeps GIFs small)"""
    g = main.Game('endless'); out = [[] for _ in windows]; stills = dict(stills)
    for n in range(int(total_s * 60)):
        t = n / 60
        keys_for(policy(g.world, t)); g.handle_events(); g.update(1 / 60)
        for i, (a, b) in enumerate(windows):
            if a <= t < b:
                g.draw(); g.present()
                if n % every == 0: out[i].append(g.screen.img.convert('RGB').copy())
        if n in stills: g.draw(); g.screen.img.resize((960, 540), Image.NEAREST).save(stills[n])
    return g, out

if __name__ == '__main__':
    os.makedirs('out', exist_ok=True)
    mem = {'ogre_dead_at': None}
    def policy(w, t):
        if t < 2.0: return []
        if w.ogre_deaths >= 1 and mem['ogre_dead_at'] is None: mem['ogre_dead_at'] = t
        afk = w.ogre_deaths >= 1 and w.hero_deaths == 0 and t - mem['ogre_dead_at'] > 4.0       # let the second ogre kill the hero
        return [] if afk else smart_bot(w)
    g, (a, b) = record_windows(40, policy, [(0, 25.5), (30.0, 38.5)], every=6,
                               stills={int(23.0 * 60): 'out/_s_respawn_ogre.png', int(33.6 * 60): 'out/_s_respawn_hero.png', int(21.2 * 60): 'out/_s_ogre_dies.png'})
    save_gif(a, 'out/gameplay_1_ogre_defeated.gif', fps=10, scale=2)
    save_gif(b, 'out/gameplay_2_hero_defeated.gif', fps=10, scale=2)
