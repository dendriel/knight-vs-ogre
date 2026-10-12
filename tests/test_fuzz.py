"""Random-input soak test: every class in the infinite mode and in the three stages (at several positions, so the bosses
and late encounters show up) gets 60 s of random keys, potions, bombs and revives. Nothing may raise and every fighter
must keep a sane state. It found real crashes (a boss parameter clash) that the scripted tests missed."""
import math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import config as C
from game.logic import World, Inputs, load_timing, CLASSES
from game.stages import STAGES

T = load_timing(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets'))
DT = 1 / 60
t0 = time.time(); runs = 0; kinds = set()
for cls in CLASSES:
    for sid in (None, 'stage1', 'stage2', 'stage3'):
        for seed in (1, 2):
            rnd = random.Random(seed * 31 + len(cls) + (len(sid) if sid else 0))
            w = World(T, seed=seed, stage=STAGES[sid] if sid else None, hero_class=cls)
            w.gold = 500; w.potions = 5; w.bombs = 5
            if sid: w.hero.x = rnd.choice([40, 800, 1500, 2500, STAGES[sid].length - 600])
            else: w.ogre_deaths = rnd.choice([0, 6, 15])
            held = dict(left=False, right=False, attack=False, jump=False, secondary=False); prev = False
            for n in range(60 * 60):
                if n % 20 == 0:
                    held.update(left=rnd.random() < .3, right=rnd.random() < .5, attack=rnd.random() < .6,
                                jump=rnd.random() < .1, secondary=rnd.random() < .15)
                inp = Inputs(left=held['left'], right=held['right'], attack=held['attack'], jump=held['jump'],
                             secondary=held['secondary'], attack_pressed=(held['attack'] and not prev) or rnd.random() < .02,
                             secondary_pressed=held['secondary'] and n % 20 == 0, potion_pressed=rnd.random() < .01,
                             bomb_pressed=rnd.random() < .01)
                prev = held['attack']
                w.update(DT, inp)
                if w.defeated and not w.revive(): break
                for f in w.fighters():
                    kinds.add(f.kind)
                    assert math.isfinite(f.x) and math.isfinite(f.y) and 0 <= f.hp <= f.max_hp + 1e-6, (cls, sid, f.kind, f.x, f.hp)
                if n % 600 == 0: w.events.clear()
                w.events.clear() if len(w.events) > 500 else None
            runs += 1
print('fuzz ok: %d runs, %d fighter kinds seen, %.0f s' % (runs, len(kinds), time.time() - t0))
