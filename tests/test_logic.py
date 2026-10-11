import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import config as C
from game.logic import World, Inputs, load_timing, Fighter

T = load_timing(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets'))
DT = 1 / 60
def run(w, secs, inp=None, bot=None):
    for _ in range(int(secs / DT)): w.update(DT, bot(w) if bot else (inp or Inputs()))

def bot_fighter(w):                       # simple player: approach, attack when in reach
    h, o = w.hero, w.ogre
    d = o.x - h.x
    if o.state == 'dead': return Inputs()
    if abs(d) > 42: return Inputs(right=d > 0, left=d < 0)
    return Inputs(attack=True)

# 1) initial layout and numbers
w = World(T)
assert w.hero.hp == 100 and w.ogre.hp == 100 and w.ogre.x > w.hero.x
assert abs((w.hero.x - w.cam_x()) - C.START_HERO_SCREEN_X) < 1e-6          # hero starts on the left of the screen
run(w, 3.0, Inputs())
assert abs(w.hero.x - w.cam_x() - C.SCREEN_W / 2) < 0.5                      # ...then the camera centers him
print('1 ok: start layout + camera glide')

# 2) a hit removes exactly 10 hp, plays hurt, and blocks moving/attacking during hurt
w = World(T); w.ogre.x = w.hero.x + 5000                                      # keep the ogre out of the way
w._hit(w.ogre, w.hero)
assert w.hero.hp == 90 and w.hero.state == 'hurt'
x0 = w.hero.x
for _ in range(int(0.3 / DT)): w.update(DT, Inputs(right=True, attack=True))
assert w.hero.state == 'hurt', 'must stay in hurt'
assert w.hero.x <= x0 + 1e-6, 'cannot walk during hurt (only the knockback moves him)'
assert not w.hero.hit_done and w.hero.state != 'attack'
run(w, 0.5, Inputs())
assert w.hero.state == 'idle'
print('2 ok: -10 hp, hurt blocks move/attack')

# 3) no extra damage while hurt/invulnerable
w = World(T); w.ogre.x = w.hero.x + 5000
w._hit(w.ogre, w.hero); hp = w.hero.hp
a = Fighter('ogre', w.hero.x + 30, -1); a.set_state('attack'); a.t = 3 / 10 + .01
w.ogre = a; w._attacks()
assert w.hero.hp == hp
print('3 ok: invulnerable during hurt')

# 4) ten hits kill, counters, respawn, corpse stays
w = World(T); w.ogre.x = w.hero.x + 5000; w.ai_cooldown = 99
for i in range(10):
    w.ogre.invuln = 0; w._hit(w.hero, w.ogre)
    assert w.ogre.hp == 100 - 10 * (i + 1)
assert w.ogre.state == 'dead' and w.ogre_deaths == 1 and w.hero_deaths == 0
dead = w.ogre
run(w, C.RESPAWN_DELAY + .1, Inputs())
assert w.ogre is not dead and w.ogre.hp == 100 and dead in w.corpses and dead.state == 'dead'
assert w.ogre.x - w.cam_x() > C.SCREEN_W - 1, 'new ogre enters from the right edge'
print('4 ok: death, counter, corpse stays, ogre respawns right')

# 5) hero death: counter, respawn on the LEFT edge, camera continuity
w = World(T); w.ogre.x = w.hero.x + 5000
run(w, 3, Inputs())
for i in range(10): w.hero.invuln = 0; w._hit(w.ogre, w.hero)
assert w.hero.state == 'dead' and w.hero_deaths == 1
old = w.hero; cam_before = w.cam_x()
for _ in range(int(3 / DT)):
    w.update(DT, Inputs())
    if w.hero is not old: break
assert w.hero is not old and old in w.corpses and w.hero.hp == 100
assert abs((w.hero.x - w.cam_x()) - C.HERO_SPAWN_MARGIN) < 16, (w.hero.x - w.cam_x())
run(w, 3, Inputs()); assert abs(w.hero.x - w.cam_x() - C.SCREEN_W / 2) < 0.5
print('5 ok: hero respawns at the left edge, camera recenters')

# 6) the ogre pauses before its first swing (passive hero)
w = World(T); arrived = None; first = None
for n in range(int(20 / DT)):
    w.update(DT, Inputs())
    if arrived is None and abs(w.hero.x - w.ogre.x) <= C.OGRE_ATTACK_DIST + 1: arrived = w.time
    if first is None and w.ogre.state == 'attack': first = w.time - arrived; break
assert first is not None and first >= C.OGRE_WAIT_BEFORE_ATTACK[0] - 0.05
print('6 ok: ogre waited %.2fs in range before its first swing' % first)

# 6b) spamming attack does not stun-lock the ogre: it gets to hit back; damage is always a multiple of 10
w = World(T); seen = set(); ogre_hit_hero = False
for n in range(int(90 / DT)):
    hp0 = w.hero.hp
    w.update(DT, bot_fighter(w)); seen.add(w.hero.hp); seen.add(w.ogre.hp)
    if w.hero.hp < hp0 and w.hero.state != 'dead': ogre_hit_hero = True
assert all(v % 10 == 0 for v in seen)
assert ogre_hit_hero or w.hero_deaths > 0, 'spamming must not make the hero untouchable'
print('6b ok: spam fight in 90s -> hero deaths=%d, ogre deaths=%d' % (w.hero_deaths, w.ogre_deaths))
assert w.ogre_deaths + w.hero_deaths >= 1

# 7) idle hero eventually dies to the AI
w = World(T); run(w, 60, Inputs())
assert w.hero_deaths >= 1
print('7 ok: passive hero dies %d times in 60s' % w.hero_deaths)
print('ALL LOGIC TESTS PASSED')
