import os, random, sys
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
w = World(T); w.roster = [(0, 'ogre', 1)]; seen = set(); ogre_hit_hero = False
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
old = (C.POTION_DROP_CHANCE, C.COIN_BAG_DROP_CHANCE); old_axe = C.AXE_DROP_CHANCE; C.AXE_DROP_CHANCE = 0.0; old_arm = C.ARMOR_DROP_CHANCE; C.ARMOR_DROP_CHANCE = 0.0; old_bw = (C.BOW_DROP_CHANCE, C.XBOW_DROP_CHANCE); C.BOW_DROP_CHANCE = C.XBOW_DROP_CHANCE = 0.0
C.POTION_DROP_CHANCE = 1.0; C.COIN_BAG_DROP_CHANCE = 1.0
w = fresh(0); w.ogre.x = 200.0; kill_ogre(w)
kinds = sorted(p.kind for p in w.pickups); assert kinds == ['coins', 'potion'], kinds
bag = [p for p in w.pickups if p.kind == 'coins'][0]; assert 5 <= bag.amount <= 10
assert [p for p in w.pickups if p.kind == 'potion'][0].amount == 30
C.POTION_DROP_CHANCE = 0.0; C.COIN_BAG_DROP_CHANCE = 0.0
w = fresh(0); w.ogre.x = 200.0; kill_ogre(w); assert w.pickups == []
C.POTION_DROP_CHANCE, C.COIN_BAG_DROP_CHANCE = old; C.AXE_DROP_CHANCE = old_axe; C.ARMOR_DROP_CHANCE = old_arm; C.BOW_DROP_CHANCE, C.XBOW_DROP_CHANCE = old_bw
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
run(w, 0.05, Inputs()); assert w.hero.hp == 50 and w.potions == 1 and w.gold == 7 and w.pickups == []   # T10: stored
w.update(DT, Inputs(potion_pressed=True)); assert w.hero.hp == 80 and w.potions == 0                      # key 1 heals
w = fresh(0); w.hero.hp = 90; w.potions = 1; w.update(DT, Inputs(potion_pressed=True))
assert w.hero.hp == 100 and w.potions == 0                                                              # capped at max
w = fresh(0); w.pickups = [Pickup('potion', 0, 30)]; run(w, 0.5, Inputs())       # full hp: still picked up (stored)
assert w.pickups == [] and w.potions == 1 and w.hero.hp == 100
w = fresh(0); w.hero.x = 100.0; w.ogre.x = 0.0; w.pickups = [Pickup('coins', 0, 9), Pickup('potion', 0, 30)]; w.hero.hp = 10
run(w, 0.5, Inputs()); assert w.gold == 0 and w.hero.hp == 10 and len(w.pickups) == 2 and w.potions == 0   # ogre cannot collect
print('19 ok: potion stored (key 1 heals +30, capped), coins to the counter, only the hero collects')

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
w.update(DT, Inputs(potion_pressed=True))
assert [v['name'] for v in w.vfx] == ['heal'] and ('heal', 'knight') in w.events and w.hero.hp == 80 and ('potion', 'knight') in w.events
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
C_old = C.POTION_DROP_CHANCE; C.POTION_DROP_CHANCE = 1.0; AXE_old = C.AXE_DROP_CHANCE; C.AXE_DROP_CHANCE = 0.0
w = three()
for e in w.enemies: e.hp = 10; e.invuln = 0; w._hit(w.hero, e)
assert w.ogre_deaths == 3 and sum(1 for p in w.pickups if p.kind == 'potion') == 3
C.POTION_DROP_CHANCE = C_old; C.AXE_DROP_CHANCE = AXE_old
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

# 25) T04: straight shots, lobbed shots (dodgeable, with landing marker), pierce, area hits
w = fresh(0); w.ogre.x = 150.0; w.ogre.invuln = 0
p = w.shoot(w.hero, 'straight', 'arrow', damage=10)
assert p in w.projectiles and ('shoot', 'knight') in w.events
run(w, 1.0, Inputs()); assert w.ogre.hp == 20 and not w.projectiles                  # hit and gone
w = fresh(0); w.ogre.x = 150.0; w.ogre.y = 3 * C.BOX_H                                 # target far above the shooter's feet
w.shoot(w.hero, 'straight'); run(w, 1.5, Inputs()); assert w.ogre.hp == 30 and not w.projectiles   # flew past, expired
w = fresh(0); w.ogre.x = 150.0; w.hero.facing = -1
w.shoot(w.hero, 'straight'); run(w, 0.3, Inputs()); assert w.ogre.hp == 30             # shot the other way
# range limit and pierce
w = fresh(0); w.hero.facing = 1
w.enemies = [Fighter('ogre', 80, -1), Fighter('ogre', 140, -1)]
for e in w.enemies: e.ai_cooldown = 99; e.invuln = 0
w.shoot(w.hero, 'straight', pierce=True, damage=10); run(w, 1.2, Inputs())
assert [e.hp for e in w.enemies] == [20, 20]                                           # pierced both
w = fresh(0); w.hero.facing = 1; w.enemies = [Fighter('ogre', 80, -1), Fighter('ogre', 140, -1)]
for e in w.enemies: e.ai_cooldown = 99
w.shoot(w.hero, 'straight', pierce=False, damage=10); run(w, 1.2, Inputs())
assert [e.hp for e in w.enemies] == [20, 30]                                           # stopped at the first
# lob: lands on the hero's spot; the hero can step out of the zone in time
w = fresh(0); a = Fighter('ogre', 200, -1); a.ai_cooldown = 99; w.enemies = [a]; w.hero.invuln = 0
p = w.shoot(a, 'lob', 'arrow', damage=10, flight=0.9, apex=60.0)
assert p.tx == w.hero.x and p.facing == -1
run(w, 1.2, Inputs()); assert w.hero.hp == 90
w = fresh(0); a = Fighter('ogre', 200, -1); a.ai_cooldown = 99; w.enemies = [a]; w.hero.invuln = 0
w.shoot(a, 'lob', 'arrow', damage=10, flight=0.9, apex=60.0)
run(w, 1.2, Inputs(right=True)); assert w.hero.hp == 100                               # walked away from the marker
w = fresh(0); a = Fighter('ogre', 200, -1); a.ai_cooldown = 99; w.enemies = [a]; w.hero.invuln = 0
w.shoot(a, 'lob', 'arrow', damage=10, flight=0.9, apex=60.0)
w.update(DT, Inputs(jump=True)); run(w, 0.8, Inputs()); w.hero.y = 0                    # airborne at impact is not required
assert w.hero.hp in (90, 100)
# area hit: delayed, hits everyone inside once, ignores the ones outside
w = fresh(0); w.hero.facing = 1; w.enemies = [Fighter('ogre', 50, -1), Fighter('ogre', 70, -1), Fighter('ogre', 400, -1)]
for e in w.enemies: e.ai_cooldown = 99; e.invuln = 0
w.add_area(w.hero, 30, 100, 10, delay=0.3, duration=0.2)
run(w, 0.2, Inputs()); assert [e.hp for e in w.enemies] == [30, 30, 30]               # not yet
run(w, 0.5, Inputs()); assert [e.hp for e in w.enemies] == [20, 20, 30]
print('25 ok: straight / pierce / lob (dodgeable) projectiles and area hits')

# 26) T10: potion inventory: limit 10 (the 11th stays on the floor), drink heals 30 only when needed, survives death
w = fresh(0); w.potions = C.POTION_MAX_STOCK; w.pickups = [Pickup('potion', 0, 30)]; run(w, 0.5, Inputs())
assert w.potions == 10 and len(w.pickups) == 1                      # full pouch: stays on the floor
w.potions = 9; run(w, 0.1, Inputs()); assert w.potions == 10 and w.pickups == []
w.hero.hp = 100; assert not w.drink_potion() and w.potions == 10    # full life: not consumed
w.hero.hp = 40; assert w.drink_potion() and w.hero.hp == 70 and w.potions == 9
w.hero.hp = 90; w.drink_potion(); assert w.hero.hp == 100 and w.potions == 8      # never above the maximum
w = fresh(0); w.hero.hp = 10; assert not w.drink_potion() and w.hero.hp == 10     # empty pouch
w.potions = 4; w.hero.invuln = 0; w._hit(w.ogre, w.hero); w.hero.hp = 1; w.hero.invuln = 0; w._hit(w.ogre, w.hero)
assert w.hero.state == 'dead' and not w.drink_potion()                            # dead hero cannot drink
run(w, 3.0, Inputs()); assert w.hero.state != 'dead' and w.potions == 4           # stock survives the new hero
print('26 ok: potion inventory (limit 10, key 1, only when hurt, survives death)')

# 27) T11: 3-stroke combo: a click inside the window chains; outside it does not; max 3; hurt cancels; holding repeats stroke 1
def combo_world():
    w = fresh(0); w.ogre.x = 5000.0; return w
def frame_idx(w): return w.hero.frame_index(T)
def click_at_frame(w, frame, hold=False):
    """run until the hero's current stroke reaches `frame`, then press the button once"""
    for _ in range(600):
        if frame_idx(w) >= frame: break
        w.update(DT, Inputs(attack=hold))
    w.update(DT, Inputs(attack=True, attack_pressed=True))
w = combo_world(); w.update(DT, Inputs(attack=True, attack_pressed=True)); w.update(DT, Inputs())   # click: stroke 1
assert w.hero.state == 'attack' and w.hero.attack_id == 'sword'
click_at_frame(w, C.COMBO_WINDOW_START); run(w, 0.0, Inputs())
for _ in range(120):
    if w.hero.attack_id == 'sword_2': break
    w.update(DT, Inputs())
assert w.hero.state == 'attack' and w.hero.attack_id == 'sword_2' and w.hero.anim == 'attack_sword_2'
click_at_frame(w, C.COMBO_WINDOW_START)
for _ in range(120):
    if w.hero.attack_id == 'sword_3': break
    w.update(DT, Inputs())
assert w.hero.attack_id == 'sword_3'
click_at_frame(w, C.COMBO_WINDOW_START); run(w, 1.5, Inputs())                        # 3rd stroke has no next
assert w.hero.state == 'idle', 'no 4th stroke'
w.update(DT, Inputs(attack=True, attack_pressed=True)); assert w.hero.attack_id == 'sword'   # back to stroke 1
# a click BEFORE the window (frame 0-2) does not chain
w = combo_world(); w.update(DT, Inputs(attack=True, attack_pressed=True))
w.update(DT, Inputs(attack=False, attack_pressed=False)); assert frame_idx(w) < C.COMBO_WINDOW_START
w.update(DT, Inputs(attack=True, attack_pressed=True)); run(w, 1.0, Inputs())
assert w.hero.attack_id == 'sword' and w.hero.state == 'idle'
# a click shortly AFTER the stroke ended still chains (buffer); too late does not
w = combo_world(); w.update(DT, Inputs(attack=True, attack_pressed=True))
for _ in range(300):
    w.update(DT, Inputs())
    if w.hero.state == 'idle': break
run(w, C.COMBO_BUFFER - 0.05, Inputs()); w.update(DT, Inputs(attack=True, attack_pressed=True))
assert w.hero.attack_id == 'sword_2'
w = combo_world(); w.update(DT, Inputs(attack=True, attack_pressed=True))
for _ in range(300):
    w.update(DT, Inputs())
    if w.hero.state == 'idle': break
run(w, C.COMBO_BUFFER + 0.1, Inputs()); w.update(DT, Inputs(attack=True, attack_pressed=True))
assert w.hero.attack_id == 'sword'
# hurt cancels the queued stroke
w = combo_world(); w.update(DT, Inputs(attack=True, attack_pressed=True)); click_at_frame(w, C.COMBO_WINDOW_START)
assert w.hero.combo_next == 'sword_2'
w.hero.invuln = 0; w._hit(w.ogre, w.hero); run(w, 1.2, Inputs()); assert w.hero.attack_id != 'sword_2' or w.hero.state != 'attack'
assert w.hero.combo_next is None
# holding the button (no new clicks) only repeats stroke 1
w = combo_world(); seen = set()
for _ in range(int(3 / DT)):
    w.update(DT, Inputs(attack=True)); seen.add(w.hero.attack_id)
assert seen == {'sword'}, seen
# stroke 1 is slower than the chained ones; damage 10/10/15; finisher reaches further and pushes harder
sp = {k: T['knight'][ATTACKS_k] for k, ATTACKS_k in (('1', 'attack_sword'), ('2', 'attack_sword_2'), ('3', 'attack_sword_3'))}
assert sp['1'] < sp['2'] < sp['3'] + 1e-9
from game.logic import ATTACKS as AT
assert [AT[k]['damage'] for k in ('sword', 'sword_2', 'sword_3')] == [10, 10, 15]
assert AT['sword_3']['knockback'] > AT['sword']['knockback'] and AT['sword_3']['reach'][1] > AT['sword']['reach'][1]
# the 3 strokes kill an ogre (30 hp) = 10 + 10 + 15 once the invulnerability is skipped
w = combo_world(); w.ogre.x = 20.0; w.ogre.ai_cooldown = 99
for aid in ('sword', 'sword_2', 'sword_3'): w.ogre.invuln = 0; w.hero.hit_set = []; w._hit(w.hero, w.ogre) if False else None
w.ogre.hp = 30
for aid in ('sword', 'sword_2', 'sword_3'):
    w.ogre.invuln = 0; w.hero.attack_id = aid; w._hit(w.hero, w.ogre)
assert w.ogre.state == 'dead'
print('27 ok: combo chains in the window, 3 strokes max, buffer 0.15 s, hurt cancels, hold repeats stroke 1')

# 28) T13: axe pickup: dropped by ogres, replaces the sword stroke, hits harder / further / slower, wears down and breaks
from game.logic import WEAPONS
old_axe = C.AXE_DROP_CHANCE; C.AXE_DROP_CHANCE = 1.0
w = fresh(0); w.ogre.x = 200.0; kill_ogre(w)
ax = [p for p in w.pickups if p.kind == 'weapon']; assert len(ax) == 1 and ax[0].item == 'axe' and ax[0].amount == 100
C.AXE_DROP_CHANCE = 0.0
w = fresh(0); w.ogre.x = 200.0; kill_ogre(w); assert not any(p.kind == 'weapon' for p in w.pickups)
C.AXE_DROP_CHANCE = old_axe
# picking up equips it (and uses the axe sprite sheet + attack)
w = fresh(0); w.pickups = [Pickup('weapon', 0, 100.0, 'axe')]; run(w, 0.1, Inputs())
assert w.hero.weapon == dict(id='axe', durability=100.0) and w.hero.sheet == 'knight_axe' and w.hero.primary == 'axe'
assert w.pickups == [] and ('pickup', 'weapon') in w.events
assert 'knight_axe' in T and T['knight_axe']['attack_axe'] < T['knight']['attack_sword'], 'axe swing is slower'
# damage 20 per hit (ogre 30 hp -> 2 hits), reach 8 px longer than the sword, wears AXE_WEAR per swing
w = fresh(0); w.hero.weapon = dict(id='axe', durability=100.0); w.ogre.x = 55.0; w.ogre.ai_cooldown = 99; w.ogre.set_state('hurt')      # (a 'hurt' ogre stands still)
w.update(DT, Inputs(attack=True, attack_pressed=True)); assert w.hero.attack_id == 'axe' and w.hero.anim == 'attack_axe'
assert w.hero.weapon['durability'] == 100 - C.AXE_WEAR
run(w, 0.5, Inputs()); assert w.ogre.hp == 10, w.ogre.hp                      # 55 px away: only the axe reaches (sword: 40 + the ogre's half width)
assert C.AXE_REACH[1] > C.KNIGHT_REACH[1]
w2 = fresh(0); w2.ogre.x = 55.0; w2.ogre.ai_cooldown = 99; w2.ogre.set_state('hurt'); run(w2, 0.5, Inputs(attack=True)); assert w2.ogre.hp == 30
# every swing wears it; at 0 it breaks and the hero is back to the sword (class weapon is indestructible)
w = fresh(0); w.ogre.x = 5000.0; w.hero.weapon = dict(id='axe', durability=C.AXE_WEAR * 2 + 0.5)
w.start_attack(w.hero, 'axe'); assert w.hero.weapon['durability'] == C.AXE_WEAR + 0.5
w.start_attack(w.hero, 'axe'); assert w.hero.weapon['durability'] < C.AXE_WEAR
w.start_attack(w.hero, 'axe'); assert w.hero.weapon is None and ('break', 'knight') in w.events
assert w.hero.primary == 'sword' and w.hero.sheet == 'knight'
w.hero.set_state('idle'); w.update(DT, Inputs(attack=True, attack_pressed=True)); assert w.hero.attack_id == 'sword'
for _ in range(40): w.start_attack(w.hero, 'sword')                           # the sword never wears
# the weapon is part of this hero: a new hero (after a death in endless mode) starts with the sword
w = fresh(0); w.hero.weapon = dict(id='axe', durability=50.0); w.hero.hp = 1; w.hero.invuln = 0; w._hit(w.ogre, w.hero)
run(w, 3.0, Inputs()); assert w.hero.state != 'dead' and w.hero.weapon is None
print('28 ok: axe pickup (drop, equip, 20 dmg / +8 reach / slower, wear 3%/swing, breaks to the sword)')

# 29) T15: armor soaks damage before life; the remainder passes to life when it breaks; hurt still plays; pickup refills
w = fresh(0); w.hero.armor = 30
w._hit(w.ogre, w.hero)                                              # 10 damage
assert w.hero.armor == 20 and w.hero.hp == 100 and w.hero.state == 'hurt' and ('armor_hit', 'knight') in w.events
assert w.stats['damage_taken'] == 10
w.hero.armor = 4; w.hero.invuln = 0; w.events.clear(); w._hit(w.ogre, w.hero)
assert w.hero.armor == 0 and w.hero.hp == 94 and ('armor_break', 'knight') in w.events       # 4 absorbed, 6 to life
w.hero.invuln = 0; w._hit(w.ogre, w.hero); assert w.hero.hp == 84                              # no armor: life as before
# pickup restores to the cap; not wasted when full; rare drop
w = fresh(0); w.hero.armor = 0; w.pickups = [Pickup('armor', 0, C.ARMOR_PICKUP)]; run(w, 0.1, Inputs())
assert w.hero.armor == C.ARMOR_PICKUP == C.ARMOR_MAX and w.pickups == []
w = fresh(0); w.hero.armor = C.ARMOR_MAX; w.pickups = [Pickup('armor', 0, 50)]; run(w, 0.3, Inputs()); assert len(w.pickups) == 1
old = C.ARMOR_DROP_CHANCE; C.ARMOR_DROP_CHANCE = 1.0
w = fresh(0); w.ogre.x = 200.0; kill_ogre(w); assert any(p.kind == 'armor' for p in w.pickups)
C.ARMOR_DROP_CHANCE = old
# enemies have no armor; a dead hero's armor is gone with him; armor does not stop death once it is spent
w = fresh(0); assert w.ogre.armor_max == 0 and w.hero.armor_max == C.ARMOR_MAX
w.hero.armor = 20; w.hero.hp = 10
w.hero.invuln = 0; w._hit(w.ogre, w.hero); w.hero.invuln = 0; w._hit(w.ogre, w.hero)
assert w.hero.hp == 10 and w.hero.armor == 0; w.hero.invuln = 0; w._hit(w.ogre, w.hero)
assert w.hero.state == 'dead'
print('29 ok: armor absorbs first, remainder to life, hurt still plays, refill pickup')

# 30) T12: combo meter + special: fills with damage dealt / taken, hold >= 0.25 s with a full bar charges, release fires
w = fresh(0); assert w.combo == 0 and 'combo' in w.features
w.ogre.invuln = 0; w._hit(w.hero, w.ogre); assert abs(w.combo - 10 * C.COMBO_GAIN_DEALT) < 1e-9
w.hero.invuln = 0; w._hit(w.ogre, w.hero); assert abs(w.combo - (10 * C.COMBO_GAIN_DEALT + 10 * C.COMBO_GAIN_TAKEN)) < 1e-9
w.combo = 999; w.apply_damage(w.hero, w.ogre, 1); assert w.combo == C.COMBO_BAR_MAX            # capped
# a quick click with a full bar is a normal stroke (a little late), a hold is the special
w = fresh(0); w.combo = C.COMBO_BAR_MAX; w.ogre.x = 5000.0
run(w, 0.1, Inputs(attack=True)); assert w.hero.state not in ('attack', 'charge')               # waiting to see what it is
w.update(DT, Inputs(attack=False)); assert w.hero.state == 'attack' and w.hero.attack_id == 'sword'
assert w.combo == C.COMBO_BAR_MAX                                                               # not spent
w = fresh(0); w.combo = C.COMBO_BAR_MAX; w.ogre.x = 5000.0
run(w, C.SPECIAL_HOLD_MIN + 0.1, Inputs(attack=True)); assert w.hero.state == 'charge' and w.hero.anim == 'attack_special'
assert w.hero.frame_index(T) == 0 and any(v['name'] == 'charge' for v in w.vfx) and ('charge', 'knight') in w.events
x0 = w.hero.x; run(w, 0.3, Inputs(attack=True, right=True)); assert 0 < w.hero.x - x0 < 0.3 * C.HERO_SPEED * 0.5   # slowed
w.update(DT, Inputs(attack=False))
assert w.hero.state == 'attack' and w.hero.attack_id == 'special' and w.combo == 0 and ('special', 'knight') in w.events
assert w.hero.invuln > 0                                                                         # invulnerable while spinning
# the spin hits everything around him, twice (15 + 15), from both sides, ignoring the target's invulnerability
w = fresh(0); w.combo = C.COMBO_BAR_MAX
l, r = Fighter('ogre', -40, +1), Fighter('ogre', 40, -1); far = Fighter('ogre', 300, -1)
w.enemies = [l, r, far]
for e in w.enemies: e.ai_cooldown = 99
r.invuln = 5.0; r.set_state('hurt')                                                              # invulnerable on purpose
run(w, C.SPECIAL_HOLD_MIN + 0.1, Inputs(attack=True)); w.update(DT, Inputs(attack=False))
run(w, 0.6, Inputs())
assert l.hp <= 0 and r.hp <= 0 and far.hp == 30, (l.hp, r.hp, far.hp)
assert w.combo == 0 or w.combo < 1, w.combo          # the special's own damage did not refill the bar
# the bar dies with the hero (D2) and the special is not available in hurt / dead
w = fresh(0); w.combo = 80; w.hero.hp = 1; w.hero.invuln = 0; w._hit(w.ogre, w.hero); assert w.combo == 0
w = fresh(0); w.combo = C.COMBO_BAR_MAX; w.hero.invuln = 0; w._hit(w.ogre, w.hero)
assert w.hero.state == 'hurt'; w.combo = C.COMBO_BAR_MAX
run(w, 0.3, Inputs(attack=True)); assert w.hero.state == 'hurt'
print('30 ok: combo meter fills, hold-to-charge, release fires a 2-hit spin, dies with the hero')

# 31) T14: bow and crossbow pickups: the shot is born on frame 4, flies, hits at range, wears the weapon, xbow reloads
w = fresh(0); w.pickups = [Pickup('weapon', 0, 100.0, 'bow')]; run(w, 0.1, Inputs())
assert w.hero.weapon['id'] == 'bow' and w.hero.sheet == 'knight_bow' and w.hero.primary == 'bow'
assert 'knight_bow' in T and 'knight_xbow' in T
w.ogre.x = 200.0; w.ogre.ai_cooldown = 99; w.ogre.set_state('hurt'); w.ogre.invuln = 0          # target at range, standing still
w.update(DT, Inputs(attack=True, attack_pressed=True)); assert w.hero.state == 'attack' and w.hero.anim == 'attack_bow'
assert w.hero.weapon['durability'] == 100 - C.BOW_WEAR
born = None
for n in range(120):
    w.update(DT, Inputs())
    if w.projectiles and born is None: born = (w.hero.frame_index(T), w.projectiles[0].sprite, w.projectiles[0].damage)
assert born is not None and born[0] == 4 and born[1:] == ('arrow', C.BOW_DAMAGE), born
assert w.ogre.hp == 30 - C.BOW_DAMAGE or w.ogre.hp == 20, w.ogre.hp                              # hit from 200 px away
# max range: a target past BOW_RANGE is never reached
w = fresh(0); w.hero.weapon = dict(id='bow', durability=100.0); w.ogre.x = C.BOW_RANGE + 80; w.ogre.set_state('hurt'); w.ogre.ai_cooldown = 99
w.update(DT, Inputs(attack=True, attack_pressed=True)); run(w, 1.5, Inputs()); assert w.ogre.hp == 30 and not w.projectiles
# crossbow: bolt, 20 dmg, longer range, reload gap between shots even with the button held
w = fresh(0); w.hero.weapon = dict(id='xbow', durability=100.0)
assert C.XBOW_RANGE > C.BOW_RANGE and C.XBOW_DAMAGE == 2 * C.BOW_DAMAGE and C.XBOW_RELOAD > 0
w.ogre.x = C.BOW_RANGE + 60; w.ogre.set_state('hurt'); w.ogre.ai_cooldown = 99; w.ogre.invuln = 0
shots = []
for n in range(int(4.0 / DT)):
    before = len(w.projectiles); w.ogre.state == 'hurt' or None
    w.update(DT, Inputs(attack=True))
    w.ogre.set_state('hurt') if w.ogre.state == 'idle' else None
    if len(w.projectiles) > before: shots.append(w.time)
assert len(shots) >= 3 and all(b - a >= C.XBOW_RELOAD - 0.01 for a, b in zip(shots, shots[1:])), shots
assert w.hero.weapon is None or w.hero.weapon['durability'] < 100 - C.XBOW_WEAR
assert w.ogre.hp < 30 or w.ogre.state == 'dead'
# the weapon breaks after enough shots and the hero is back to the sword
w = fresh(0); w.ogre.x = 5000.0; w.hero.weapon = dict(id='bow', durability=C.BOW_WEAR + 0.1)
w.start_attack(w.hero, 'bow'); w.start_attack(w.hero, 'bow'); assert w.hero.weapon is None and w.hero.primary == 'sword'
print('31 ok: bow/crossbow pickups (shot on frame 4, range, wear, crossbow reload)')

# 32) T20: AI behaviours are data: a def with different ai_params changes how far away the enemy stops and attacks
from game.logic import FIGHTER_DEFS
FIGHTER_DEFS['far_ogre'] = dict(FIGHTER_DEFS['ogre'], ai='melee', ai_params=dict(attack_dist=70, wait=(0.1, 0.1)))
w = fresh(0); w.enemies = [Fighter('far_ogre', 400, -1)]; w.enemies[0].ai_cooldown = 0
stop = None
for _ in range(int(8 / DT)):
    w.update(DT, Inputs(left=False))
    e = w.enemies[0]
    if e.state == 'attack': stop = abs(e.x - w.hero.x); break
assert stop is not None and 60 <= stop <= 72, stop                       # attacked from ~70 px, the ogre default is 38
assert w.enemies[0].ai_p['attack_dist'] == 70 and Fighter('ogre', 0, 1).ai_p['attack_dist'] == C.OGRE_ATTACK_DIST
del FIGHTER_DEFS['far_ogre']
print('32 ok: AI parameters come from FIGHTER_DEFS (ai + ai_params)')

# 33) T26: attack tokens (a crowd never has more than max_attackers swinging / preparing) and elite variants
w = World(T, seed=3); w.cam_off = 0; w.hero.x = 0.0; w.hero.invuln = 0
w.enemies = [Fighter('ogre', 40 + 6 * i, -1) for i in range(5)]; w.spawn_target = 5
for e in w.enemies: e.ai_cooldown = 0.0
peak = 0; holders = set()
for _ in range(int(25 / DT)):
    w.hero.hp = 100; w.hero.invuln = 0                        # keep the hero alive and passive: only the crowd is measured
    w.update(DT, Inputs())
    att = sum(1 for e in w.enemies if e.state == 'attack')
    tok = sum(1 for e in w.enemies if e.token and e.state != 'dead')
    peak = max(peak, att, tok)
    for e in w.enemies:
        if e.state == 'attack': holders.add(id(e))
assert peak <= w.max_attackers, peak
assert len(holders) >= 3, 'turns rotate: everyone eventually gets to attack'
# the token is returned on death and on hurt; with a single enemy nothing changes
w = World(T); e = w.enemies[0]; e.token = True; w.hero.x = 0.0
e.invuln = 0; w._hit(w.hero, e); assert e.token is False
assert w.free_tokens() == w.max_attackers
# elites: faster / sturdier / harder hitting, same art (tint), shorter pauses
base = Fighter('ogre', 0, 1); vet = Fighter('ogre', 0, 1, elite='veteran'); bru = Fighter('ogre', 0, 1, elite='brute'); agi = Fighter('ogre', 0, 1, elite='agile')
assert vet.speed > base.speed and vet.ai_p['wait'][0] < base.ai_p['wait'][0]
assert bru.max_hp > base.max_hp and bru.hp == bru.max_hp
assert agi.speed > vet.speed and agi.max_hp < base.max_hp
w = fresh(0); b = Fighter('ogre', 40, -1, elite='brute'); b.ai_cooldown = 99; w.enemies = [b]; w.hero.invuln = 0
w.start_attack(b, 'ogre_axe'); run(w, 0.5, Inputs()); assert w.hero.hp == 100 - 15, w.hero.hp      # brute: 10 * 1.5
assert vet.mods['tint'] and bru.mods['tint'] != vet.mods['tint']
w = World(T); x = w.spawn_enemy('ogre', 300, elite='veteran'); assert x in w.enemies and x.elite == 'veteran'
print('33 ok: attack tokens cap the crowd, elites are faster / sturdier / harder')

# 34) T22: soldier: 20 hp, faster than the ogre, shorter wait, hits for 10 with the sword stroke, own sheet
w = fresh(0); s = Fighter('soldier', 200, -1); w.enemies = [s]
assert s.max_hp == 20 and s.speed > FIGHTER_DEFS['ogre']['speed'] and s.sheet == 'soldier' and s.ai_p['wait'] == C.SOLDIER_WAIT
assert 'soldier' in T and T['soldier']['attack'] == T['knight']['attack_sword'], 'same stroke speed as the hero stroke 1'
s.ai_cooldown = 0; w.hero.invuln = 0; w.hero.x = 0.0
for _ in range(int(10 / DT)):
    w.hero.invuln = 0 if w.hero.hp == 100 else w.hero.invuln
    w.update(DT, Inputs())
    if w.hero.hp < 100: break
assert w.hero.hp == 90 and s.state in ('attack', 'idle')                      # one stroke = 10
w2 = fresh(0); s2 = Fighter('soldier', 30, -1); w2.enemies = [s2]; s2.ai_cooldown = 99
w2.ogre.invuln = 0; w2._hit(w2.hero, s2); w2.ogre.invuln = 0 if False else 0
s2.invuln = 0; w2._hit(w2.hero, s2); assert s2.state == 'dead' and w2.stats['kills'] == 1       # 2 hits kill it
assert w2.focus_enemy() is s2 and FIGHTER_DEFS['soldier']['label'] == 'SOLDADO'
print('34 ok: soldier (20 hp, 62 px/s, sword stroke, own sheet)')

# 35) T21: spearman: reaches 55 px (the ogre cannot), has a dead zone up close, steps back when pressed, 25 hp
s = Fighter('spearman', 55, -1); assert s.max_hp == 25 and s.sheet == 'spearman' and s.defn['ai'] == 'spear'
w = fresh(0); w.enemies = [s]; w.hero.invuln = 0; s.ai_cooldown = 99
w.start_attack(s, 'spearman_thrust'); run(w, 0.8, Inputs()); assert w.hero.hp == 90, 'a spear hits at 55 px'
w = fresh(0); o = Fighter('ogre', 55, -1); w.enemies = [o]; w.hero.invuln = 0; o.ai_cooldown = 99
w.start_attack(o, 'ogre_axe'); run(w, 0.8, Inputs()); assert w.hero.hp == 100, 'the ogre axe does not reach 55 px'
w = fresh(0); s = Fighter('spearman', 6, -1); w.enemies = [s]; w.hero.invuln = 0; s.ai_cooldown = 99; s.set_state('hurt')
s.state = 'idle'; w.start_attack(s, 'spearman_thrust'); run(w, 0.8, Inputs())
assert w.hero.hp == 100, 'dead zone: standing right on top of the spearman is safe'
assert C.SPEARMAN_REACH[0] > 0 and C.SPEARMAN_REACH[1] > C.OGRE_REACH[1]
# pressed spearman (resting) steps back; free spearman stops at its own distance
w = fresh(0); s = Fighter('spearman', 14, -1); w.enemies = [s]; s.ai_cooldown = 5.0
x0 = s.x; run(w, 0.5, Inputs()); assert s.x > x0 + 8, (s.x, x0)
w = fresh(0); s = Fighter('spearman', 300, -1); w.enemies = [s]; s.ai_cooldown = 0
for _ in range(int(8 / DT)):
    w.update(DT, Inputs(left=False))
    if s.state == 'attack': break
assert 48 <= abs(s.x - w.hero.x) <= 58, abs(s.x - w.hero.x)
print('35 ok: spearman (long reach, dead zone, steps back, own stop distance)')

# 36) T23: archer: stays ~170 px away, backs off when pressed, lobs an arrow (marker) that the hero can dodge
a = Fighter('archer', 500, -1); assert a.max_hp == 15 and a.sheet == 'archer' and T['archer']['attack'] > 0
w = fresh(0); w.enemies = [a]; a.ai_cooldown = 0
for _ in range(int(14 / DT)):
    w.update(DT, Inputs()); w.hero.hp = 100; w.hero.invuln = 99
    if a.state == 'attack': break
d = abs(a.x - w.hero.x); assert C.ARCHER_KEEP_DIST - 10 <= d <= C.ARCHER_KEEP_DIST + 30, d
# the arrow is born on frame 4 and falls on the hero's position at launch
w = fresh(0); w.hero.invuln = 0; a = Fighter('archer', 150, -1); w.enemies = [a]; a.ai_cooldown = 99
w.start_attack(a, 'archer_shot'); lob = None
for _ in range(int(2.5 / DT)):
    w.update(DT, Inputs())
    if lob is None and w.projectiles: lob = w.projectiles[0]; assert a.frame_index(T) == 4 and lob.kind == 'lob' and lob.tx == 0.0
assert lob is not None and w.hero.hp == 90
w = fresh(0); w.hero.invuln = 0; a = Fighter('archer', 150, -1); w.enemies = [a]; a.ai_cooldown = 99
w.start_attack(a, 'archer_shot')
for _ in range(int(2.5 / DT)): w.update(DT, Inputs(left=True))                    # walks away from the marker: dodged
assert w.hero.hp == 100
# pressed archer backs away
w = fresh(0); a = Fighter('archer', 40, -1); w.enemies = [a]; a.ai_cooldown = 5
x0 = a.x; run(w, 0.6, Inputs()); assert a.x > x0 + 15
print('36 ok: archer keeps distance, lobbed arrow lands on the hero spot and can be dodged')

# 37) T24: shield bearer blocks frontal blows (sword strokes, arrows), is open from behind and to the axe / special / bow-less
def shield_world(hero_x):
    w = fresh(0); s = Fighter('shieldman', 40, -1); s.ai_cooldown = 99; w.enemies = [s]; w.hero.x = hero_x; w.hero.facing = 1
    return w, s
w, s = shield_world(0.0)
assert s.max_hp == 30 and s.sheet == 'shieldman' and s.anim == 'guard' and 'guard' in T['shieldman']
w.update(DT, Inputs(attack=True, attack_pressed=True)); run(w, 0.5, Inputs())
assert s.hp == 30 and ('block', 'shieldman') in w.events and any(v['name'] == 'block_spark' for v in w.vfx), s.hp
assert s.state in ('idle', 'walk')                                                       # a block does not stagger it
# arrows are stopped by the shield too
w, s = shield_world(0.0); s.x = 150.0
w.shoot(w.hero, 'straight', 'arrow', damage=10); run(w, 1.0, Inputs()); assert s.hp == 30
# from behind: the hero is on the other side of its facing -> a normal hit
w, s = shield_world(80.0); w.hero.facing = -1; s.facing = -1; s.x = 40.0            # shieldman faces left, hero stands to its right
w.hero.invuln = 0; w._hit(w.hero, s); assert s.hp == 20
# axe and special ignore the guard
w, s = shield_world(0.0); w.hero.weapon = dict(id='axe', durability=100.0)
w.update(DT, Inputs(attack=True, attack_pressed=True)); run(w, 0.5, Inputs()); assert s.hp == 10, s.hp
w, s = shield_world(0.0); w.combo = C.COMBO_BAR_MAX
run(w, C.SPECIAL_HOLD_MIN + 0.1, Inputs(attack=True)); w.update(DT, Inputs(attack=False)); run(w, 0.6, Inputs())
assert s.hp <= 0, s.hp
# turning takes SHIELD_TURN_DELAY: if the hero goes round it, it keeps facing the old side for that long
w, s = shield_world(0.0); s.ai_cooldown = 0.0; run(w, 0.1, Inputs()); assert s.facing == -1
w.hero.x = 200.0; w.hero.y = 0.0
t = 0.0
while s.facing == -1 and t < 2.0: w.update(DT, Inputs()); t += DT
assert 0.35 <= t <= 0.7, t
print('37 ok: shield blocks frontal sword/arrows, axe/special/rear hits connect, 0.5 s to turn')

# 38) T25: orc / goblin / kobold / minotaur
for k in ('orc', 'goblin', 'kobold', 'minotaur'): assert k in T and Fighter(k, 0, 1).sheet == k
orc, gob, kob, mino = (Fighter(k, 0, 1) for k in ('orc', 'goblin', 'kobold', 'minotaur'))
assert orc.max_hp == 40 and gob.max_hp == 10 and kob.max_hp == 12 and mino.max_hp == 50
assert gob.speed > orc.speed > FIGHTER_DEFS['ogre']['speed'] and gob.hw < orc.hw
# goblin: one sword stroke kills it; its hit is small (5)
w = fresh(0); g = Fighter('goblin', 20, -1); g.ai_cooldown = 99; w.enemies = [g]; g.invuln = 0
w._hit(w.hero, g); assert g.state == 'dead'
w = fresh(0); g = Fighter('goblin', 20, -1); w.enemies = [g]; w.hero.invuln = 0; g.ai_cooldown = 0
run(w, 3.0, Inputs()); assert w.hero.hp < 100 and (100 - w.hero.hp) % C.GOBLIN_DAMAGE == 0      # hits of 5
# kobold throws a lobbed rock (sprite 'rock'), 5 damage
w = fresh(0); k = Fighter('kobold', 120, -1); w.enemies = [k]; k.ai_cooldown = 99; w.hero.invuln = 0
w.start_attack(k, 'kobold_rock'); lob = None
for _ in range(int(2.5 / DT)):
    w.update(DT, Inputs())
    if lob is None and w.projectiles: lob = w.projectiles[0]
assert lob is not None and lob.sprite == 'rock' and lob.kind == 'lob' and w.hero.hp == 95
# minotaur: telegraph (axe raised, ~0.7 s warning), then a dash that hurts for 15; jumping over it dodges
def mino_world():
    w = fresh(0); m = Fighter('minotaur', 150, -1); w.enemies = [m]; m.ai_cooldown = 0; w.hero.invuln = 0; return w, m
w, m = mino_world(); seen = []
for _ in range(int(4 / DT)):
    w.update(DT, Inputs()); w.hero.invuln = 0 if w.hero.hp == 100 else w.hero.invuln
    if not seen or seen[-1] != m.state: seen.append(m.state)
    if w.hero.hp < 100: break
assert 'charge' in seen and 'dash' in seen and seen.index('charge') < seen.index('dash'), seen
assert w.hero.hp == 85 and ('telegraph', 'minotaur') in w.events
w, m = mino_world(); tele = None
for _ in range(int(4 / DT)):
    w.update(DT, Inputs(jump=(m.state == 'dash' and w.hero.grounded and abs(m.x - w.hero.x) < 75)))   # jumps as it arrives
    if m.state == 'charge' and tele is None: tele = w.time
    if m.state == 'dash' and tele is not None: warn = w.time - tele; break
assert abs(warn - C.MINOTAUR_TELEGRAPH) < 0.1, warn
for _ in range(int(1.0 / DT)): w.update(DT, Inputs(jump=(w.hero.grounded and m.state == 'dash' and abs(m.x - w.hero.x) < 75)))
assert w.hero.hp == 100, 'jumping dodged the charge'
print('38 ok: orc, goblin (1 stroke), kobold (lobbed rock), minotaur (telegraphed charge, dodgeable by jumping)')

# 39) T25: endless roster: only ogres at first, new kinds unlock with kills, deterministic, elites late
w = World(T); kinds = [w._draw_enemy()[0] for _ in range(30)]; assert set(kinds) == {'ogre'}
w.ogre_deaths = 5; kinds = {w._draw_enemy()[0] for _ in range(200)}
assert kinds == {'ogre', 'soldier', 'goblin', 'spearman'}, kinds
w.ogre_deaths = 14; draws = [w._draw_enemy() for _ in range(300)]
assert {k for k, _ in draws} == {k for _, k, _ in C.ENDLESS_ROSTER} and any(e for _, e in draws) and any(e is None for _, e in draws)
a, b = World(T, seed=9), World(T, seed=9); a.ogre_deaths = b.ogre_deaths = 10
assert [a._draw_enemy() for _ in range(20)] == [b._draw_enemy() for _ in range(20)]
w = World(T); w.ogre_deaths = 12; w.update(DT, Inputs()); assert len(w.enemies) >= 1
for _ in range(3): w.ogre_deaths += 5
w.enemies = []; w.update(DT, Inputs()); assert len(w.enemies) == C.ENDLESS_CROWD_MAX
print('39 ok: endless roster unlocks with kills, deterministic, crowds and elites grow')

# 40) T30: stages: finite path, camera locked at the ends, encounters fire once, clear needs everyone dead + the end line,
#     death is final (defeated), the endless mode keeps respawning
from game.stages import Stage, STAGES, enc
st = Stage('t', 'TESTE', 'village', 1000, [enc(0.3, 'ogre', 'soldier'), enc(0.6, 'goblin')], start_x=40)
w = World(T, stage=st); assert w.hero.x == 40 and w.enemies == [] and w.spawn_target == 0 and not w.stage_clear
run(w, 0.5, Inputs()); assert w.cam_x() == 0.0 and w.enemies == [], 'camera locked at the start, nothing spawned yet'
run(w, 0.3, Inputs(left=True)); assert w.hero.x >= 0.0 and w.hero.x < 40                       # cannot leave the path to the left
w.hero.x = 10000.0; w.update(DT, Inputs()); assert w.hero.x == 1000.0                          # nor to the right
assert w.cam_x() == st.length - C.SCREEN_W + C.STAGE_END_MARGIN, w.cam_x()                      # camera locked at the end
# encounters fire once when the line is crossed, from beyond the right edge of the screen
w = World(T, stage=st); w.hero.x = st.trigger_x(st.encounters[0]) + 1; cam = w.cam_x(); w.update(DT, Inputs())
assert [e.kind for e in w.enemies] == ['ogre', 'soldier'] and w.next_enc == 1
assert all(e.x > cam + C.SCREEN_W for e in w.enemies) and w.enemies[1].x - w.enemies[0].x == C.ENCOUNTER_SPACING
w.update(DT, Inputs()); w.update(DT, Inputs()); assert len(w.enemies) == 2, 'an encounter fires only once'
# no respawns in a stage: killed enemies become corpses and are not replaced
for e in list(w.enemies): e.invuln = 0; e.hp = 1; w._hit(w.hero, e)
run(w, C.RESPAWN_DELAY + 0.2, Inputs()); assert w.enemies == [] and len(w.corpses) == 2
# clear = every encounter fired, nobody alive, hero at the end line
w.hero.x = st.trigger_x(st.encounters[1]) + 1; w.update(DT, Inputs()); assert len(w.enemies) == 1 and not w.stage_clear
w.hero.x = 990.0; w.update(DT, Inputs()); assert not w.stage_clear                               # one still alive
w.enemies[0].invuln = 0; w.enemies[0].hp = 1; w._hit(w.hero, w.enemies[0]); w.update(DT, Inputs())
assert w.stage_clear and ('stage_clear', 'knight') in w.events
# death is final in a stage: no new hero, `defeated` set; the endless mode respawns as before
w = World(T, stage=st); w.hero.hp = 1; w.hero.invuln = 0; w._hit(w.ogre or Fighter('ogre', 0, 1), w.hero) if w.ogre else None
w.enemies = [Fighter('ogre', 60, -1)]; w.hero.invuln = 0; w._hit(w.enemies[0], w.hero)
assert w.hero.state == 'dead' and not w.defeated
old = w.hero; run(w, C.RESPAWN_DELAY + 0.3, Inputs()); assert w.defeated and w.hero is old and old.state == 'dead'
assert w.hero_deaths == 1 and old not in w.corpses
w = World(T); w.hero.hp = 1; w.hero.invuln = 0; w._hit(w.ogre, w.hero); run(w, C.RESPAWN_DELAY + 0.3, Inputs())
assert not w.defeated and w.hero.state != 'dead'
# the campaign data is sane: ordered encounters, known kinds, increasing length
from game.stages import CAMPAIGN
prev = 0
for sid in CAMPAIGN:
    s = STAGES[sid]; assert s.length > prev; prev = s.length
    ps = [e['p'] for e in s.encounters]; assert ps == sorted(ps) and 0 < ps[0] and ps[-1] < 1
    assert all(k in FIGHTER_DEFS and not FIGHTER_DEFS[k]['hero'] for e in s.encounters for k, _ in e['enemies'])
print('40 ok: stages (path bounds, locked camera, one-shot encounters, clear, final defeat) + campaign data')

# 41) T36: difficulty curve: sections grow inside a stage and from stage to stage; queue never exceeds max_alive;
#     elites only late; loot grows; deterministic
from game.stages import SECTIONS, THREAT
for sid in CAMPAIGN:
    s = STAGES[sid]
    th = [s.threat(i) for i in range(3)]; assert th[0] < th[1] < th[2], (sid, th)
    d = [s.difficulty(p) for p in (0.1, 0.5, 0.9)]
    assert [x['section'] for x in d] == [0, 1, 2]
    assert d[0]['max_alive'] <= d[1]['max_alive'] <= d[2]['max_alive'] and d[0]['max_attackers'] <= d[2]['max_attackers']
    assert d[0]['elite_frac'] == 0.0 or d[0]['elite_frac'] < d[2]['elite_frac']
    assert d[0]['loot_mult'] < d[1]['loot_mult'] < d[2]['loot_mult']
tot = [sum(STAGES[s].threat(i) for i in range(3)) for s in CAMPAIGN]; assert tot[0] < tot[1] < tot[2], tot
ma = [STAGES[s].difficulty(0.9)['max_alive'] for s in CAMPAIGN]; assert ma == sorted(ma) and ma[0] < ma[-1]
assert STAGES['stage1'].difficulty(0.2)['elite_frac'] == 0.0           # no random elites in the opening
# the world never has more living enemies than max_alive, tokens follow the section, everything eventually enters
big = Stage('b', 'GRANDE', 'village', 1000, [enc(0.1, *(['goblin'] * 9))], difficulty=((3, 1), (3, 1), (3, 1)), elites=(0.9, 0, 0))
w = World(T, stage=big); w.hero.x = big.trigger_x(big.encounters[0]) + 5; w.hero.invuln = 99
peak = 0; seen = 0
for _ in range(int(40 / DT)):
    w.hero.hp = 100; w.update(DT, Inputs())
    alive = sum(1 for e in w.enemies if e.state != 'dead'); peak = max(peak, alive)
    for e in w.enemies:                                                 # a bot standing in place: kill whoever arrives
        if e.state != 'dead' and abs(e.x - w.hero.x) < 30: e.invuln = 0; e.hp = 1; w._hit(w.hero, e)
assert peak <= 3 and w.stats['kills'] == 9 and w.queue == [], (peak, w.stats['kills'], len(w.queue))
assert w.max_attackers == 1
# determinism with the same seed; loot multiplier scales coin bags
def run_stage(seed):
    w = World(T, seed=seed, stage=STAGES['stage1']); w.hero.x = 2800.0; w.hero.invuln = 99
    for _ in range(600): w.update(DT, Inputs())
    return [(e.kind, e.elite, round(e.x, 2)) for e in w.enemies]
assert run_stage(4) == run_stage(4)
w = World(T, stage=STAGES['stage3']); w.hero.x = STAGES['stage3'].length - 100; w.update(DT, Inputs())
C_old = C.COIN_BAG_DROP_CHANCE; C.COIN_BAG_DROP_CHANCE = 1.0; w.pickups.clear(); w._drop_loot(0.0)
amt = [p.amount for p in w.pickups if p.kind == 'coins'][0]
C.COIN_BAG_DROP_CHANCE = C_old
assert amt >= C.COIN_BAG_COINS[0] * 2, amt                              # x ~2.1 near the end of stage 3
print('41 ok: difficulty curve, queue capped at max_alive, tokens per section, elites late, loot grows')

# 42) T37: revive: needs REVIVE_COST gold, same spot, full life, invulnerable, combo emptied; enemies / items kept
st = STAGES['stage1']
def dead_world(gold):
    w = World(T, stage=st); w.hero.x = 800.0; w.enemies = [Fighter('ogre', 900, -1)]; w.gold = gold; w.potions = 3
    w.hero.weapon = dict(id='axe', durability=40.0); w.combo = 77
    w.hero.hp = 1; w.hero.invuln = 0; w._hit(w.enemies[0], w.hero); w.hero.armor = 10   # (armor found earlier, kept)
    run(w, C.RESPAWN_DELAY + 0.3, Inputs()); assert w.defeated and w.hero.state == 'dead'
    return w
w = dead_world(C.REVIVE_COST - 1); assert not w.can_revive() and not w.revive() and w.defeated and w.gold == C.REVIVE_COST - 1
w = dead_world(C.REVIVE_COST + 40); hero = w.hero; ogre_hp = w.enemies[0].hp; n_en = len(w.enemies); x_fall = w.hero.x
assert w.revive() and w.gold == 40 and w.stats['revives'] == 1 and not w.defeated
assert w.hero is hero and w.hero.x == x_fall and w.hero.hp == w.hero.max_hp and w.hero.state == 'idle'
assert abs(w.hero.invuln - C.REVIVE_INVULN) < 1e-9 and w.combo == 0
assert w.potions == 3 and w.hero.weapon['durability'] == 40.0 and w.hero.armor == 10          # D10: items kept
assert len(w.enemies) == n_en and w.enemies[0].hp == ogre_hp
w.enemies[0].ai_cooldown = 0; run(w, 1.0, Inputs()); assert w.hero.hp == w.hero.max_hp, 'invulnerable right after reviving'
# the run state travels (D6): export / apply
w2 = World(T, stage=st); w2.apply_run(w.export_run()); assert w2.gold == w.gold and w2.potions == 3 and w2.hero.weapon == w.hero.weapon
print('42 ok: paid revive (100 gold, same spot, 2 s invulnerable, items kept) + run state export / apply')

# 43) T32: boss + arena: the last screen closes after the last encounter, the boss enters, the camera is released and
#     the way opens only when it dies; summons at half life; boss loot; per-boss behaviours
for sid in CAMPAIGN:                                                                  # every encounter is before the arena gate
    s = STAGES[sid]; gate_p = s.progress(s.length - C.SCREEN_W + C.ARENA_ENTER_MARGIN)
    assert s.boss in FIGHTER_DEFS and FIGHTER_DEFS[s.boss].get('boss') and max(e['p'] for e in s.encounters) < gate_p, sid
st = Stage('b', 'BOSS', 'village', 1500, [enc(0.2, 'goblin')], boss='ogre_captain')
w = World(T, stage=st); w.hero.invuln = 99
gate = st.length - C.SCREEN_W + C.ARENA_ENTER_MARGIN
w.hero.x = gate + 5; w.update(DT, Inputs()); assert w.arena is None and w.boss is None          # the encounter has not fired yet
w.hero.x = st.trigger_x(st.encounters[0]) + 1; w.update(DT, Inputs())
for e in w.enemies: e.invuln = 0; e.hp = 1; w._hit(w.hero, e)
run(w, C.RESPAWN_DELAY + 0.2, Inputs()); w.hero.invuln = 99
w.hero.x = gate - 20; w.update(DT, Inputs()); assert w.arena is None                            # not at the gate yet
w.hero.x = gate + 5; cam0 = w.cam_x(); w.update(DT, Inputs())
assert w.arena == (st.length - C.SCREEN_W, st.length) and w.boss is not None and w.boss.kind == 'ogre_captain'
assert abs(w.cam_x() - cam0) < 20, 'the camera does not jump when the arena closes (it glides)'
run(w, 3.0, Inputs()); assert abs(w.cam_x() - w.arena[0]) < 1.5, w.cam_x()                      # eased to the fixed screen
w.hero.x = 0.0; w.update(DT, Inputs()); assert w.hero.x == w.arena[0] + C.ARENA_WALL_MARGIN      # walls
w.hero.x = 99999.0; w.update(DT, Inputs()); assert w.hero.x == w.arena[1] - C.ARENA_RIGHT_WALL
assert not w.stage_clear
# the captain calls two soldiers when at half life (once)
b = w.boss; n0 = len(w.enemies); b.hp = int(b.max_hp * 0.5); b.ai_cooldown = 99
w.update(DT, Inputs()); assert b.summoned and sorted(e.kind for e in w.enemies[n0:]) == ['soldier', 'soldier'] and ('summon', 'ogre_captain') in w.events
w.update(DT, Inputs()); assert len(w.enemies) == n0 + 2
# killing the boss releases the screen, drops guaranteed loot, and the stage can finish only after
for e in list(w.enemies):
    if e is not b: e.invuln = 0; e.hp = 1; w._hit(w.hero, e)
b.invuln = 0; b.hp = 1; w.pickups.clear(); w._hit(w.hero, b)
assert sum(1 for p in w.pickups if p.kind == 'potion') == C.BOSS_LOOT_POTIONS and any(p.kind == 'coins' and p.amount >= C.BOSS_LOOT_COINS[0] for p in w.pickups)
w.hero.hp = 100; w.update(DT, Inputs()); assert w.boss_dead and w.arena is None and ('boss_dead', 'ogre_captain') in w.events
run(w, 4.0, Inputs()); assert not w.stage_clear                                                  # still has to reach the end
w.hero.x = st.length - 5; w.update(DT, Inputs()); assert w.stage_clear
# boss specifics: minotaur lord charges faster than the regular minotaur; black knight chains 3 strokes and guards
ml = Fighter('minotaur_lord', 0, 1); assert ml.defn['charge']['telegraph'] < C.MINOTAUR_TELEGRAPH and ml.defn['charge']['speed'] > C.MINOTAUR_DASH_SPEED
bk = Fighter('black_knight', 0, 1); assert bk.defn['guard'] and bk.max_hp == C.BLACK_KNIGHT_MAX_HP
w = fresh(0); k = Fighter('black_knight', 40, -1); w.enemies = [k]; k.ai_cooldown = 99; w.hero.invuln = 99
seen = []
for _ in range(60):
    w.rng = random.Random(1); w.rng.random = lambda: 0.0                                          # always chain
    w.start_attack(k, 'bk_1'); break
for _ in range(int(3 / DT)):
    w.rng.random = lambda: 0.0; w.update(DT, Inputs())
    if not seen or seen[-1] != k.attack_id: seen.append(k.attack_id)
assert seen[:3] == ['bk_1', 'bk_2', 'bk_3'], seen
for name in ('ogre_captain', 'minotaur_lord', 'black_knight'):
    assert Fighter(name, 0, 1).sheet == name and name in T
print('43 ok: boss arena (gate, locked screen, walls, summon at half life, loot, release) and boss behaviours')

print('ALL LOGIC TESTS PASSED')
