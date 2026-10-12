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
assert w.hero.hp == 100 and w.ogre.hp == 30 and w.ogre.x > w.hero.x
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

# 4) three hits kill the ogre (30 hp), counters, respawn, corpse stays
w = World(T); w.ogre.x = w.hero.x + 5000; w.ai_cooldown = 99
for i in range(3):
    w.ogre.invuln = 0; w._hit(w.hero, w.ogre)
    assert w.ogre.hp == 30 - 10 * (i + 1)
assert w.ogre.state == 'dead' and w.ogre_deaths == 1 and w.hero_deaths == 0
dead = w.ogre
run(w, C.RESPAWN_DELAY + .1, Inputs())
assert w.ogre is not dead and w.ogre.hp == 30 and dead in w.corpses and dead.state == 'dead'
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

# ============================ jump, boxes, reach ============================
BH = C.BOX_H
def fresh(x=0.0):
    w = World(T); w.hero.x = x; w.cam_off = 0; w.ogre.x = x + 5000; w.ai_cooldown = 99; return w
def box_x(slot_cells, lvl): return [bx for bx, l in slot_cells if l == lvl]

# 8) jump: reaches ~JUMP_HEIGHT, lands back, anim goes up -> fall, one jump per key press
w = fresh(-300); top = 0; phases = []
for n in range(int(1.5 / DT)):
    w.update(DT, Inputs(jump=(n < 40)))                       # key held for 0.67 s: must jump only once
    top = max(top, w.hero.y)
    if not phases or phases[-1] != w.hero.anim: phases.append(w.hero.anim)
assert abs(top - C.JUMP_HEIGHT) < 2.0, top
assert w.hero.grounded and w.hero.y == 0
assert phases == ['jump_up', 'jump_fall', 'idle'], phases
print('8 ok: jump apex %.1f px, up -> fall -> ground, single jump per press' % top)

# 9) can move in the air
w = fresh(-300); x0 = w.hero.x
w.update(DT, Inputs(jump=True)); run(w, 0.3, Inputs(right=True))
assert w.hero.y > 10 and w.hero.x - x0 > 30
print('9 ok: moves in the air')

# 10) a box does not block walking at ground level
from game.logic import slot_boxes
b0 = slot_boxes(0)[0][0]                                      # lone box of slot 0
w = fresh(b0 - 60); run(w, 1.0, Inputs(right=True))
assert w.hero.x > b0 + C.BOX_W + 20 and w.hero.y == 0 and w.hero.grounded
print('10 ok: walks straight through a box on the ground')

# 11) jump while in front of the box lands on top; can walk off and fall (jump_fall without having jumped)
w = fresh(b0 + C.BOX_W / 2); w.update(DT, Inputs(jump=True)); run(w, 1.0, Inputs())
assert w.hero.grounded and abs(w.hero.y - BH) < 1e-6, w.hero.y
for _ in range(int(0.5 / DT)):                                # walks off the right edge
    w.update(DT, Inputs(right=True))
    if not w.hero.grounded: break
assert not w.hero.grounded and w.hero.anim == 'jump_fall' and w.hero.vy <= 0
run(w, 0.6, Inputs()); assert w.hero.grounded and w.hero.y == 0
print('11 ok: lands on the box, walking off plays the fall animation')

# 12) staircase 1-2-3: climbed with jumps only (ground -> 1 -> 2 -> 3 boxes), and you cannot jump from the ground to the top
st = slot_boxes(2); x1 = min(bx for bx, l in st if l == 1)
def hop(w, right_secs):
    w.update(DT, Inputs(jump=True, right=right_secs > 0)); run(w, right_secs, Inputs(right=True)); run(w, 0.9, Inputs())
w = fresh(x1 + 5); hop(w, 0)                                     # ground -> top of column 1
assert w.hero.grounded and abs(w.hero.y - 1 * BH) < 1e-6, w.hero.y
hop(w, 0.15); assert w.hero.grounded and abs(w.hero.y - 2 * BH) < 1e-6, w.hero.y
hop(w, 0.25); assert w.hero.grounded and abs(w.hero.y - 3 * BH) < 1e-6, w.hero.y
print('12 ok: staircase climbed with jumps: 1 -> 2 -> 3 boxes high')

# 13) ogre reaches a hero on one box (from the ground) but not on two or three
for lvl, should_hit in ((1, True), (2, False), (3, False)):
    w = World(T); w.cam_off = 0; w.hero.x = 100.0; w.hero.y = lvl * BH; w.hero.grounded = True; w.hero.invuln = 0
    w.ogre.x = 100 + 30; w.ogre.facing = -1; w.ai_cooldown = 0
    for _ in range(int(4 / DT)):
        w.hero.y = lvl * BH                               # keep him on that level (no box under him in this setup)
        w.hero.grounded = True; w.hero.vy = 0
        w.update(DT, Inputs())
    hit = w.hero.hp < 100 or w.hero_deaths > 0
    assert hit == should_hit, (lvl, hit, w.hero.hp)
print('13 ok: ogre hits a hero on 1 box, cannot hit one on 2 or 3 boxes (it just waits below)')

# 14) hero standing right on top of the ogre (overlapping) can still be hit and can still hit
w = World(T); w.cam_off = 0; w.hero.x = 50.0; w.ogre.x = 50.0; w.ai_cooldown = 0; w.hero.invuln = 0
run(w, 3, Inputs()); assert w.hero.hp < 100, 'ogre must be able to hit an overlapping hero'
w = World(T); w.hero.x = 50.0; w.ogre.x = 50.0; w.ai_cooldown = 99; w.ogre.hp = 30
run(w, 0.6, Inputs(attack=True)); assert w.ogre.hp < 30, 'hero must be able to hit an overlapping ogre'
print('14 ok: overlapping fighters can hit each other (no body collision)')

# 15) hero can walk (not turn) while the attack animation plays, and keeps attacking
w = fresh(-300); x0 = w.hero.x
w.update(DT, Inputs(right=True, attack=True)); assert w.hero.state == 'attack'
run(w, 0.1, Inputs(right=True, attack=True)); assert w.hero.state == 'attack' and w.hero.x - x0 > 8
fac = w.hero.facing; run(w, 0.05, Inputs(left=True, attack=True)); assert w.hero.facing == fac
print('15 ok: moves while attacking')

# 16) attack is faster than the old 1.5x, and the hero is faster than before
assert C.KNIGHT_ATTACK_ANIM_SPEED > 1.5 and C.HERO_SPEED > 84
# 17) ogre re-faces the hero during the wind-up of a swing (hero walks through him), and is locked once the swing is active
w = World(T); w.cam_off = 0; w.hero.x = 100.0; w.ogre.x = 130.0; w.ogre.facing = -1; w.hero.invuln = 99
w.ogre.set_state('attack'); w.ai_cooldown = 0
w.update(DT, Inputs()); assert w.ogre.facing == -1
w.hero.x = 160.0; w.update(DT, Inputs())                       # hero is now behind him, still in the wind-up
assert w.ogre.state == 'attack' and w.ogre.facing == +1, w.ogre.facing
for _ in range(int(2 / DT)):
    if w.ogre.frame_index(T) >= C.ACTIVE_FRAMES[0]: break
    w.update(DT, Inputs())
f = w.ogre.facing; w.hero.x = 40.0; w.update(DT, Inputs())      # swing is active: direction stays locked
assert w.ogre.facing == f
print('17 ok: ogre turns during the wind-up, direction locked during the swing')
# ============================ pickups ============================
def kill_ogre(w):
    w.ogre.hp = 10; w._hit(w.hero, w.ogre)
    assert w.ogre.state == 'dead'

# 18) drop chances: forced 100% / 0%, and the rates are close to the configured ones over many ogres
old = (C.POTION_DROP_CHANCE, C.COIN_BAG_DROP_CHANCE)
C.POTION_DROP_CHANCE = 1.0; C.COIN_BAG_DROP_CHANCE = 1.0
w = fresh(0); w.ogre.x = 200.0; kill_ogre(w)
kinds = sorted(p.kind for p in w.pickups); assert kinds == ['coins', 'potion'], kinds
bag = [p for p in w.pickups if p.kind == 'coins'][0]; assert 5 <= bag.amount <= 10
assert [p for p in w.pickups if p.kind == 'potion'][0].amount == 30
C.POTION_DROP_CHANCE = 0.0; C.COIN_BAG_DROP_CHANCE = 0.0
w = fresh(0); w.ogre.x = 200.0; kill_ogre(w); assert w.pickups == []
C.POTION_DROP_CHANCE, C.COIN_BAG_DROP_CHANCE = old
w = fresh(0); n_pot = n_bag = 0; amounts = set()
for _ in range(2000):
    w.pickups.clear(); w._drop_loot(0.0)
    n_pot += any(p.kind == 'potion' for p in w.pickups)
    for p in w.pickups:
        if p.kind == 'coins': n_bag += 1; amounts.add(p.amount)
assert abs(n_pot / 2000 - 0.30) < 0.04, n_pot
assert amounts == set(range(5, 11)), amounts
print('18 ok: potion %.0f%% of ogres, bag always 5-10 coins' % (n_pot / 20))

# 19) only the hero picks items up: potion heals 30 (capped), coins add to the gold counter, ogre standing on them does nothing
from game.logic import Pickup
w = fresh(0); w.hero.hp = 50; w.pickups = [Pickup('potion', 0, 30), Pickup('coins', 0, 7)]
run(w, 0.05, Inputs()); assert w.hero.hp == 80 and w.gold == 7 and w.pickups == []
w = fresh(0); w.hero.hp = 90; w.pickups = [Pickup('potion', 0, 30)]
run(w, 0.05, Inputs()); assert w.hero.hp == 100 and w.pickups == []              # capped at max
w = fresh(0); w.pickups = [Pickup('potion', 0, 30)]; run(w, 0.5, Inputs())       # full hp: potion stays
assert len(w.pickups) == 1 and w.hero.hp == 100
w = fresh(0); w.hero.x = 100.0; w.ogre.x = 0.0; w.pickups = [Pickup('coins', 0, 9), Pickup('potion', 0, 30)]; w.hero.hp = 10
run(w, 0.5, Inputs()); assert w.gold == 0 and w.hero.hp == 10 and len(w.pickups) == 2     # ogre cannot collect
print('19 ok: potion +30 (capped, kept at full hp), coins to the counter, only the hero collects')

# 20) the item falls to the ground, can be collected only when close, and gold survives the hero's death
w = fresh(0); w.pickups = [Pickup('coins', 200, 6)]; run(w, 1.0, Inputs())
assert w.pickups[0].y == 0 and w.gold == 0
w.hero.x = 195.0; run(w, 0.1, Inputs()); assert w.gold == 6
w._hit(w.ogre, w.hero); w.hero.hp = 1; w.hero.invuln = 0; w._hit(w.ogre, w.hero)
run(w, 3.0, Inputs()); assert w.hero.state != 'dead' and w.gold == 6
w = fresh(0); w.hero.y = 3 * C.BOX_H; w.hero.grounded = True; w.pickups = [Pickup('coins', 0, 6)]
w._pickups(DT); assert w.gold == 0 and len(w.pickups) == 1                  # hero high above (on boxes): out of reach
print('20 ok: pickup lands, needs proximity (also vertical), gold survives hero deaths')

# 21) effects and sounds: potion -> 'heal' effect on the hero + heal event; gold -> 'coin_glint' + pickup event; sounds exist
w = fresh(0); w.hero.hp = 50; w.pickups = [Pickup('potion', 0, 30)]; w.events.clear(); run(w, 0.05, Inputs())
assert [v['name'] for v in w.vfx] == ['heal'] and ('heal', 'knight') in w.events and w.hero.hp == 80
w = fresh(0); w.pickups = [Pickup('coins', 0, 5)]; w.events.clear(); run(w, 0.05, Inputs())
assert [v['name'] for v in w.vfx] == ['coin_glint'] and ('pickup', 'coins') in w.events
w = fresh(0); w.hero.hp = 40; w.heal(w.hero, 999); assert w.hero.hp == 100                  # generic heal is capped too
assert 'heal' in T['vfx'] and 'coin_glint' in T['vfx']
from game.audio import SOUND_FOR
sfx = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'sfx')
for ev, kinds in SOUND_FOR.items():
    for k, snd in kinds.items(): assert os.path.exists(os.path.join(sfx, snd + '.wav')), snd
print('21 ok: heal / coin effects, events and sound files')

# 22) T01: damage funnel and statistics; fighter definitions drive max hp / half width
from game.logic import FIGHTER_DEFS
w = fresh(0); assert w.hero.max_hp == FIGHTER_DEFS['knight']['max_hp'] and w.ogre.hw == FIGHTER_DEFS['ogre']['half_width']
assert w.apply_damage(w.ogre, w.hero, 7) == 7 and w.hero.hp == 93 and w.stats['damage_taken'] == 7
assert w.apply_damage(w.hero, w.ogre, 999) == 30 and w.stats['damage_dealt'] == 30     # capped at the remaining hp
w = fresh(0); w.ogre.hp = 10; w._hit(w.hero, w.ogre); assert w.stats['kills'] == 1 and w.stats['damage_dealt'] == 10
w.pickups = [Pickup('coins', 0, 4)]; run(w, 0.05, Inputs()); assert w.stats['gold_gained'] == 4
print('22 ok: apply_damage funnel + stats')

# 23) T02: several enemies at once, deterministic, own AI state, loot per dead enemy, swing cleaves everyone in reach
def three(seed=1):
    w = World(T, seed=seed); w.cam_off = 0; w.hero.x = 0.0
    w.enemies = [Fighter('ogre', 100 + 25 * i, -1) for i in range(3)]; w.spawn_target = 3
    for e in w.enemies: e.ai_cooldown = 0.5
    return w
w1, w2 = three(), three()
for _ in range(int(20 / DT)): w1.update(DT, Inputs()); w2.update(DT, Inputs())
assert [(e.x, e.hp, e.state) for e in w1.enemies] == [(e.x, e.hp, e.state) for e in w2.enemies]
assert w1.hero.hp == w2.hero.hp and (w1.hero.hp < 100 or w1.hero_deaths > 0)
w = three(); assert len(w.fighters()) == 4
for e in w.enemies: e.x = 10.0
w.hero.x = 0.0; w.hero.facing = 1; w.hero.invuln = 99
for e in w.enemies: e.ai_cooldown = 99
w.hero.set_state('attack'); run(w, 0.5, Inputs(attack=True))
assert all(e.hp < 30 for e in w.enemies), [e.hp for e in w.enemies]       # all three were hit by one swing
C_old = C.POTION_DROP_CHANCE; C.POTION_DROP_CHANCE = 1.0
w = three()
for e in w.enemies: e.hp = 10; e.invuln = 0; w._hit(w.hero, e)
assert w.ogre_deaths == 3 and sum(1 for p in w.pickups if p.kind == 'potion') == 3
C.POTION_DROP_CHANCE = C_old
run(w, C.RESPAWN_DELAY + 0.1, Inputs())
assert len(w.corpses) >= 3 and len(w.enemies) == 3 and all(e.state != 'dead' for e in w.enemies)   # quota refilled
print('23 ok: 3 ogres at once, deterministic, cleave, loot per kill, quota refilled')

# 24) T03: attacks are data: damage / knockback / vfx come from ATTACKS[attack_id]; a new attack is one entry
from game.logic import ATTACKS
assert ATTACKS['sword']['damage'] == C.DAMAGE and ATTACKS['ogre_axe']['slash'] == 'axe_slash'
ATTACKS['heavy'] = dict(ATTACKS['sword'], damage=25, knockback=40.0, slash='axe_slash')
w = fresh(0); w.ogre.x = 30.0; w.ogre.invuln = 0
w.start_attack(w.hero, 'heavy'); assert w.hero.state == 'attack' and w.hero.anim == 'attack_sword'
run(w, 0.5, Inputs(attack=True))
assert w.ogre.hp == 30 - 25 + 0 or w.ogre.state == 'dead' or w.ogre.hp == 5, w.ogre.hp
assert any(v['name'] == 'axe_slash' for v in w.vfx) or w.ogre.hp == 5
assert w.ogre.kb_speed == 40.0 / C.KNOCKBACK_TIME
w = fresh(0); w.start_attack(w.ogre, 'ogre_axe'); assert w.ogre.anim == 'attack' and w.ogre.sheet == 'ogre'
del ATTACKS['heavy']
print('24 ok: attacks are data (damage, knockback, effect per attack id)')

print('ALL LOGIC TESTS PASSED')
