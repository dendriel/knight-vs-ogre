"""Game rules. No pygame in here: this module can be tested without a window."""
import json, math, os, random
from . import config as C

# One entry per kind of fighter: everything that differs between a knight and an ogre lives here (T01).
FIGHTER_DEFS = {
    'knight': dict(hero=True, max_hp=C.HERO_MAX_HP, speed=C.HERO_SPEED, half_width=8, sheet='knight', ai=None,
                   anim={'idle': 'idle', 'walk': 'run', 'attack': 'attack_sword', 'hurt': 'hurt', 'dead': 'death'},
                   slash='sword_slash', reach=C.KNIGHT_REACH),
    'ogre': dict(hero=False, max_hp=C.OGRE_MAX_HP, speed=C.OGRE_SPEED, half_width=10, sheet='ogre', ai='melee',
                 anim={'idle': 'idle', 'walk': 'walk', 'attack': 'attack', 'hurt': 'hurt', 'dead': 'death'},
                 slash='axe_slash', reach=C.OGRE_REACH),
}
ANIM = {k: d['anim'] for k, d in FIGHTER_DEFS.items()}          # (aliases kept for old code / tests)
SLASH = {k: d['slash'] for k, d in FIGHTER_DEFS.items()}
REACH = {k: d['reach'] for k, d in FIGHTER_DEFS.items()}
LOOPING = ('idle', 'walk')


def load_timing(assets_dir):
    """fps of every animation, read from the sprite atlases and scaled by config.ANIM_SPEED."""
    t = {}
    for k in ('knight', 'ogre', 'vfx'):
        with open(os.path.join(assets_dir, f'{k}_spritesheet.json')) as f:
            mult = C.ANIM_SPEED.get(k, {})
            t[k] = {n: a['fps'] * mult.get(n, 1.0) for n, a in json.load(f)['animations'].items()}
    return t


class Inputs:
    def __init__(self, left=False, right=False, attack=False, jump=False):
        self.left, self.right, self.attack, self.jump = left, right, attack, jump


class Fighter:
    def __init__(self, kind, x, facing, hp=None, invuln=0.0):
        self.defn = FIGHTER_DEFS[kind]; self.max_hp = self.defn['max_hp']
        if hp is None: hp = self.max_hp
        self.kind, self.x, self.facing, self.hp, self.invuln = kind, float(x), facing, hp, invuln
        self.state = 'idle'; self.t = 0.0
        self.y = 0.0; self.vy = 0.0; self.grounded = True      # y = height of the feet above the ground (up is +)
        self.air_t = 0.0; self.air_phase = None                 # time in the current rising / falling phase
        self.hit_done = False; self.slash_done = False
        self.kb_dir = 0; self.kb_t = 0.0
        self.hit_set = []                                       # targets already hit by the current swing
        self.ai_wait = None; self.ai_cooldown = 0.6             # enemy AI state (per fighter, so many enemies can coexist)
        self.respawn_t = None                                   # enemies: countdown (after death) until the body is buried

    def set_state(self, s):
        self.state = s; self.t = 0.0; self.hit_done = False; self.slash_done = False; self.hit_set = []

    @property
    def is_hero(self): return self.defn['hero']

    @property
    def airborne(self): return not self.grounded

    @property
    def anim(self):
        if self.kind == 'knight' and self.airborne and self.state in ('idle', 'walk'):
            return 'jump_up' if self.vy > 0 else 'jump_fall'      # falling off a ledge without jumping plays jump_fall too
        return ANIM[self.kind][self.state]

    @property
    def hw(self): return self.defn['half_width']

    def frame_index(self, timing):
        a = self.anim
        if a == 'jump_up': return min(int(self.air_t * timing[self.kind][a]), 5)
        if a == 'jump_fall': return int(self.air_t * timing[self.kind][a]) % 6
        n = int(self.t * timing[self.kind][a])
        return n % 6 if self.state in LOOPING else min(n, 5)

    def duration(self, timing): return 6.0 / timing[self.kind][self.anim]

    def can_act(self): return self.state in ('idle', 'walk')


class Pickup:
    """An item lying in the world. kind: 'potion' | 'coins'. y = height above the ground; it pops up and falls."""
    def __init__(self, kind, x, amount=0):
        self.kind, self.x, self.amount = kind, float(x), amount
        self.y = 14.0; self.vy = 90.0; self.t = 0.0


class World:
    def __init__(self, timing, seed=1):
        self.timing = timing; self.rng = random.Random(seed)
        self.hero = Fighter('knight', 0.0, +1)
        self.enemies = [Fighter('ogre', C.START_OGRE_OFFSET, -1)]
        self.spawn_target = 1                              # endless mode keeps this many enemies in the world (T02)
        self._jump_held = False; self._box_cache = {}
        self.corpses = []; self.vfx = []
        self.hero_deaths = 0; self.ogre_deaths = 0
        self.pickups = []; self.gold = 0                   # gold belongs to the player, so it survives hero deaths
        self.loot_rng = random.Random(seed + 1000)         # separate stream: drops never disturb the AI's random sequence
        self.hero_timer = None
        self.cam_off = C.SCREEN_W / 2 - C.START_HERO_SCREEN_X     # hero starts on the left, camera glides to center
        self.shake = 0.0; self.time = 0.0
        self.events = []                                           # (name, kind) for the audio layer; main.py drains it
        self.stats = dict(kills=0, damage_dealt=0, damage_taken=0, gold_gained=0)

    # ------------------------------------------------------------------ helpers
    def cam_x(self): return self.hero.x - C.SCREEN_W / 2 + self.cam_off
    def fighters(self): return (self.hero, *self.enemies)

    @property
    def ogre(self):
        """Compatibility: the first living enemy (or the last body still lying around, or None)."""
        for e in self.enemies:
            if e.state != 'dead': return e
        return self.enemies[-1] if self.enemies else None

    @ogre.setter
    def ogre(self, f):
        if self.enemies: self.enemies[0] = f
        else: self.enemies.append(f)

    @property
    def ai_wait(self): return self.ogre.ai_wait
    @ai_wait.setter
    def ai_wait(self, v):
        for e in self.enemies: e.ai_wait = v
    @property
    def ai_cooldown(self): return self.ogre.ai_cooldown
    @ai_cooldown.setter
    def ai_cooldown(self, v):
        for e in self.enemies: e.ai_cooldown = v

    def add_vfx(self, name, x, flip, delay=0.0, y=0.0):
        self.vfx.append({'name': name, 'x': x, 'flip': flip, 't': -delay, 'y': y})

    # ------------------------------------------------------------------ boxes (one-way platforms)
    def box_tops(self, x):
        """Heights of the tops of every box cell under world x (with a little edge slack)."""
        slot = math.floor(x / C.SLOT_W); out = []
        for s in (slot - 1, slot, slot + 1):
            if s not in self._box_cache: self._box_cache[s] = slot_boxes(s)
            for bx, lvl in self._box_cache[s]:
                if bx - C.BOX_EDGE <= x <= bx + C.BOX_W + C.BOX_EDGE: out.append(lvl * C.BOX_H)
        return out

    def support_height(self, x, y):
        """Height of the floor under a fighter whose feet are at height y: the ground, or the highest box top that is
        not above his feet. Boxes are one-way: walking at ground level goes straight through them."""
        return max([0.0] + [t for t in self.box_tops(x) if t <= y + 1e-6])

    def _physics(self, f, dt):
        if not f.is_hero: return                          # enemies always walk on the ground
        if f.grounded and self.support_height(f.x, f.y) < f.y - 1e-6:
            f.grounded = False; f.vy = 0.0                # walked off a ledge: starts falling
        if f.grounded:
            f.y = self.support_height(f.x, f.y); f.air_phase = None; return
        g = 2 * C.JUMP_HEIGHT / C.JUMP_RISE_TIME ** 2
        ny = f.y + f.vy * dt - 0.5 * g * dt * dt; f.vy -= g * dt      # exact for constant gravity (apex = JUMP_HEIGHT)
        if f.vy <= 0:                                     # falling: land on the highest top crossed this step
            land = [t for t in self.box_tops(f.x) if ny <= t <= f.y + 1e-6] + ([0.0] if ny <= 0 else [])
            if land:
                f.y = max(land); f.vy = 0.0; f.grounded = True; f.air_phase = None
                self.events.append(('land', f.kind)); return
        f.y = ny
        phase = 'up' if f.vy > 0 else 'fall'
        if phase != f.air_phase: f.air_phase = phase; f.air_t = 0.0
        else: f.air_t += dt

    def bury(self, f):
        self.corpses.append(f)
        if len(self.corpses) > 40: self.corpses.pop(0)

    # ------------------------------------------------------------------ update
    def update(self, dt, inp):
        dt = min(dt, 0.05); self.time += dt
        for f in self.fighters():
            f.t += dt; f.invuln = max(0.0, f.invuln - dt)
        for f in self.corpses: f.t += dt
        self.shake = max(0.0, self.shake - dt)
        self._hero_control(dt, inp)
        for e in self.enemies: self._enemy_ai(e, dt)
        self._knockback(dt)
        for f in self.fighters(): self._physics(f, dt)
        self._attacks()
        self._pickups(dt)
        self._timeouts()
        self._respawns(dt)
        for v in self.vfx: v['t'] += dt
        self.vfx = [v for v in self.vfx if int(v['t'] * self.timing['vfx'][v['name']]) < 6]
        self.cam_off *= math.exp(-C.CAMERA_EASE * dt)
        if abs(self.cam_off) < 0.25: self.cam_off = 0.0

    def _hero_control(self, dt, inp):
        h = self.hero
        jump_edge = inp.jump and not self._jump_held; self._jump_held = inp.jump     # one jump per key press
        if h.state not in ('idle', 'walk', 'attack'): return                          # hurt / dead: no control
        dx = (1 if inp.right else 0) - (1 if inp.left else 0)
        if jump_edge and h.grounded:
            h.vy = 2 * C.JUMP_HEIGHT / C.JUMP_RISE_TIME; h.grounded = False; h.air_phase = None
            self.events.append(('jump', 'knight'))
        if h.state == 'attack' or inp.attack:                                         # can walk (not turn) while swinging
            if h.state != 'attack': h.set_state('attack')
            h.x += dx * C.HERO_SPEED * C.ATTACK_MOVE_FACTOR * dt
            return
        if dx:
            h.facing = dx; h.x += dx * C.HERO_SPEED * dt
            if h.state != 'walk': h.set_state('walk')
        elif h.state != 'idle':
            h.set_state('idle')

    def _enemy_ai(self, o, dt):
        h = self.hero
        if o.state == 'attack' and h.state != 'dead' and abs(h.x - o.x) > 2 and o.frame_index(self.timing) < C.ACTIVE_FRAMES[0]:
            o.facing = 1 if h.x > o.x else -1               # wind-up: keep tracking a hero who walks through him
        if not o.can_act(): return
        if h.state == 'dead':
            if o.state != 'idle': o.set_state('idle')
            return
        if abs(h.x - o.x) > 2: o.facing = 1 if h.x > o.x else -1        # no flip-flop when the hero is right on top of him
        dist = abs(h.x - o.x)
        reachable = abs(h.y - o.y) <= C.VERTICAL_REACH
        if o.ai_cooldown > 0: o.ai_cooldown -= dt
        if dist > C.OGRE_ATTACK_DIST:                      # approach
            o.x += o.facing * o.defn['speed'] * dt
            if o.state != 'walk': o.set_state('walk')
            if dist > C.OGRE_ATTACK_DIST + C.OGRE_PATIENCE_DIST: o.ai_wait = None   # hero ran away: forget the plan
            return
        if o.state != 'idle': o.set_state('idle')
        if not reachable: o.ai_wait = None; return         # hero too high: the enemy just waits below him
        if o.ai_cooldown <= 0:                             # in range: pause first, then swing
            if o.ai_wait is None: o.ai_wait = self.rng.uniform(*C.OGRE_WAIT_BEFORE_ATTACK)
            o.ai_wait -= dt
            if o.ai_wait <= 0:
                o.ai_wait = None; o.set_state('attack')

    def _knockback(self, dt):
        for f in self.fighters():
            if f.kb_t > 0:
                f.x += f.kb_dir * (C.KNOCKBACK / C.KNOCKBACK_TIME) * dt; f.kb_t -= dt

    def _attacks(self):
        hits = []
        pairs = [(self.hero, e) for e in self.enemies] + [(e, self.hero) for e in self.enemies]
        for atk, tgt in pairs:
            if atk.state != 'attack': continue
            idx = atk.frame_index(self.timing)
            if idx >= 3 and not atk.slash_done:
                atk.slash_done = True; self.add_vfx(SLASH[atk.kind], atk.x, atk.facing < 0, y=atk.y)
                self.events.append(('swing', atk.kind))
            if tgt in atk.hit_set or idx not in C.ACTIVE_FRAMES: continue     # one hit per target per swing
            if tgt.state == 'dead' or tgt.invuln > 0: continue
            if abs(atk.y - tgt.y) > C.VERTICAL_REACH: continue          # too high / low for the swing to connect
            lo, hi = REACH[atk.kind]
            a0, a1 = (atk.x + lo, atk.x + hi) if atk.facing > 0 else (atk.x - hi, atk.x - lo)
            if a0 <= tgt.x + tgt.hw and a1 >= tgt.x - tgt.hw:
                atk.hit_done = True; atk.hit_set.append(tgt); hits.append((atk, tgt))
        for atk, tgt in hits: self._hit(atk, tgt)          # applied together, so trades are possible

    def apply_damage(self, atk, tgt, amount):
        """The single funnel for damage: stats now, armor / guard / combo meter plug in here later."""
        amount = min(amount, tgt.hp)
        tgt.hp -= amount
        if tgt is self.hero: self.stats['damage_taken'] += amount
        else: self.stats['damage_dealt'] += amount
        return amount

    def _hit(self, atk, tgt):
        self.apply_damage(atk, tgt, C.DAMAGE)
        self.add_vfx('blood_splash', tgt.x, tgt.x > atk.x, y=tgt.y)
        self.shake = C.SHAKE_TIME
        self.events.append(('hit', tgt.kind))
        dirn = 1 if tgt.x >= atk.x else -1
        tgt.facing = -dirn                                   # turns toward the attacker, recoils backwards
        tgt.kb_dir = dirn; tgt.kb_t = C.KNOCKBACK_TIME
        if tgt.hp <= 0:
            tgt.set_state('dead'); tgt.invuln = 999.0
            self.events.append(('death', tgt.kind))
            if tgt is not self.hero: self.stats['kills'] += 1
            if not tgt.is_hero: self._drop_loot(tgt.x); tgt.respawn_t = C.RESPAWN_DELAY
            self.add_vfx('spirit', tgt.x, tgt.x > atk.x, delay=C.SPIRIT_DELAY, y=tgt.y)
            if tgt is self.hero: self.hero_deaths += 1; self.hero_timer = C.RESPAWN_DELAY
            else: self.ogre_deaths += 1
        else:
            self.events.append(('hurt', tgt.kind))
            tgt.set_state('hurt')
            if tgt is self.hero: tgt.invuln = tgt.duration(self.timing) + C.HURT_INVULN_EXTRA
            elif C.OGRE_HURT_INVULN: tgt.invuln = tgt.duration(self.timing) + C.OGRE_HURT_INVULN_EXTRA
            if not tgt.is_hero: tgt.ai_wait = None

    def heal(self, f, amount):
        """Restores life (capped at max_hp) with the heal effect and sound. Any healing item should go through here."""
        f.hp = min(f.max_hp, f.hp + amount)
        self.add_vfx('heal', f.x, f.facing < 0, y=f.y)
        self.events.append(('heal', f.kind))

    def _drop_loot(self, x):
        r = self.loot_rng; items = []
        if r.random() < C.POTION_DROP_CHANCE: items.append(Pickup('potion', 0, C.POTION_HEAL))
        if r.random() < C.COIN_BAG_DROP_CHANCE: items.append(Pickup('coins', 0, r.randint(*C.COIN_BAG_COINS)))
        for i, p in enumerate(items):
            p.x = x + (i - (len(items) - 1) / 2) * 16        # side by side when both drop
            self.pickups.append(p)
        del self.pickups[:-C.PICKUP_MAX]

    def _pickups(self, dt):
        g = 2 * C.JUMP_HEIGHT / C.JUMP_RISE_TIME ** 2; h = self.hero; keep = []
        for p in self.pickups:
            p.t += dt
            if p.y > 0 or p.vy > 0:                            # pop up, then fall to the ground
                p.y += p.vy * dt - 0.5 * g * dt * dt; p.vy -= g * dt
                if p.y <= 0: p.y = 0.0; p.vy = 0.0
            if (h.state != 'dead' and abs(h.x - p.x) <= C.PICKUP_RADIUS and abs(h.y - p.y) <= C.PICKUP_REACH_Y
                    and not (p.kind == 'potion' and h.hp >= h.max_hp)):          # a potion is not wasted on a full bar
                if p.kind == 'potion': self.heal(h, p.amount)
                else:
                    self.gold += p.amount; self.stats['gold_gained'] += p.amount; self.add_vfx('coin_glint', h.x, h.facing < 0, y=h.y)
                self.events.append(('pickup', p.kind)); continue
            keep.append(p)
        self.pickups = keep

    def _timeouts(self):
        for f in self.fighters():
            if f.state in ('attack', 'hurt') and f.t >= f.duration(self.timing):
                was_attack = f.state == 'attack'
                f.set_state('idle')
                if not f.is_hero:
                    if was_attack: f.ai_cooldown = self.rng.uniform(*C.OGRE_COOLDOWN)
                    else: f.ai_cooldown = 0.0; f.ai_wait = self.rng.uniform(*C.OGRE_RETALIATE_WAIT)

    def _respawns(self, dt):
        if self.hero_timer is not None:
            self.hero_timer -= dt
            if self.hero_timer <= 0:
                self.hero_timer = None; old_cam = self.cam_x(); self.bury(self.hero)
                nx = old_cam + C.HERO_SPAWN_MARGIN
                self.hero = Fighter('knight', nx, +1, invuln=C.SPAWN_INVULN)
                self.cam_off = old_cam - (nx - C.SCREEN_W / 2)      # camera keeps its place, then glides
                self.events.append(('spawn', 'knight'))
        for e in list(self.enemies):                       # bury the dead after RESPAWN_DELAY
            if e.respawn_t is not None:
                e.respawn_t -= dt
                if e.respawn_t <= 0: self.bury(e); self.enemies.remove(e)
        while len(self.enemies) < self.spawn_target:       # endless mode: keep the quota filled, entering from the right
            e = Fighter('ogre', self.cam_x() + C.SCREEN_W + C.OGRE_SPAWN_MARGIN, -1)
            e.ai_cooldown = 0.6; self.enemies.append(e); self.events.append(('spawn', 'ogre'))


def _stairs(x, direction):
    """Three columns of 1, 2 and 3 boxes (rising to the right when direction > 0)."""
    out = []
    for c in range(3):
        n = c + 1 if direction > 0 else 3 - c
        out += [(x + c * C.BOX_W, lvl) for lvl in range(1, n + 1)]
    return out


def slot_boxes(slot, seed=7):
    """Box cells of one world slot: a list of (left x, level); a cell's top is level * BOX_H above the ground.
    Deterministic like slot_props. Slot 0 has a lone box and slot 2 a staircase, so both are close to the start."""
    x0 = slot * C.SLOT_W
    if slot == 0: return [(x0 + 90, 1)]
    if slot == 2: return _stairs(x0 + 14, +1)
    r = random.Random(slot * 6571 + seed); v = r.random()
    if v < .22: return [(x0 + r.randint(0, C.SLOT_W - C.BOX_W), 1)]
    if v < .36: return _stairs(x0 + r.randint(0, C.SLOT_W - 3 * C.BOX_W), r.choice((1, -1)))
    return []


def slot_props(slot, seed=7):
    """Scenery of one world slot: a list of (prop name, world x). Deterministic, so the world is 'infinite'."""
    r = random.Random(slot * 7919 + seed); x0 = slot * C.SLOT_W; out = []
    if slot % 2 == 0:
        v = r.random()
        if v < .6: out.append(('medieval_house', x0 + r.randint(0, C.SLOT_W - 160)))
        elif v < .78: out.append(('well', x0 + r.randint(8, C.SLOT_W - 56)))
    else:
        v = r.random()
        if v < .6: out.append(('tree', x0 + r.randint(0, C.SLOT_W - 112)))
        elif v < .72: out.append(('well', x0 + r.randint(8, C.SLOT_W - 56)))
    return out
