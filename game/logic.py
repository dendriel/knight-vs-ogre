"""Game rules. No pygame in here: this module can be tested without a window."""
import json, math, os, random
from . import config as C

ANIM = {'knight': {'idle': 'idle', 'walk': 'walk', 'attack': 'attack_sword', 'hurt': 'hurt', 'dead': 'death'},
        'ogre': {'idle': 'idle', 'walk': 'walk', 'attack': 'attack', 'hurt': 'hurt', 'dead': 'death'}}
LOOPING = ('idle', 'walk')
SLASH = {'knight': 'sword_slash', 'ogre': 'axe_slash'}
REACH = {'knight': C.KNIGHT_REACH, 'ogre': C.OGRE_REACH}


def load_timing(assets_dir):
    """fps of every animation, read from the sprite atlases and scaled by config.ANIM_SPEED."""
    t = {}
    for k in ('knight', 'ogre', 'vfx'):
        with open(os.path.join(assets_dir, f'{k}_spritesheet.json')) as f:
            mult = C.ANIM_SPEED.get(k, {})
            t[k] = {n: a['fps'] * mult.get(n, 1.0) for n, a in json.load(f)['animations'].items()}
    return t


class Inputs:
    def __init__(self, left=False, right=False, attack=False):
        self.left, self.right, self.attack = left, right, attack


class Fighter:
    def __init__(self, kind, x, facing, hp=C.MAX_HP, invuln=0.0):
        self.kind, self.x, self.facing, self.hp, self.invuln = kind, float(x), facing, hp, invuln
        self.state = 'idle'; self.t = 0.0
        self.hit_done = False; self.slash_done = False
        self.kb_dir = 0; self.kb_t = 0.0

    def set_state(self, s):
        self.state = s; self.t = 0.0; self.hit_done = False; self.slash_done = False

    @property
    def anim(self): return ANIM[self.kind][self.state]

    @property
    def hw(self): return C.HALF_WIDTH[self.kind]

    def frame_index(self, timing):
        n = int(self.t * timing[self.kind][self.anim])
        return n % 6 if self.state in LOOPING else min(n, 5)

    def duration(self, timing): return 6.0 / timing[self.kind][self.anim]

    def can_act(self): return self.state in ('idle', 'walk')


class World:
    def __init__(self, timing, seed=1):
        self.timing = timing; self.rng = random.Random(seed)
        self.hero = Fighter('knight', 0.0, +1)
        self.ogre = Fighter('ogre', C.START_OGRE_OFFSET, -1)
        self.corpses = []; self.vfx = []
        self.hero_deaths = 0; self.ogre_deaths = 0
        self.hero_timer = None; self.ogre_timer = None
        self.cam_off = C.SCREEN_W / 2 - C.START_HERO_SCREEN_X     # hero starts on the left, camera glides to center
        self.shake = 0.0; self.time = 0.0
        self.events = []                                           # (name, kind) for the audio layer; main.py drains it
        self.ai_wait = None; self.ai_cooldown = 0.6

    # ------------------------------------------------------------------ helpers
    def cam_x(self): return self.hero.x - C.SCREEN_W / 2 + self.cam_off
    def fighters(self): return (self.hero, self.ogre)

    def add_vfx(self, name, x, flip, delay=0.0):
        self.vfx.append({'name': name, 'x': x, 'flip': flip, 't': -delay})

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
        self._ogre_ai(dt)
        self._knockback(dt)
        self._attacks()
        self._timeouts()
        self._respawns(dt)
        for v in self.vfx: v['t'] += dt
        self.vfx = [v for v in self.vfx if int(v['t'] * self.timing['vfx'][v['name']]) < 6]
        self.cam_off *= math.exp(-C.CAMERA_EASE * dt)
        if abs(self.cam_off) < 0.25: self.cam_off = 0.0

    def _hero_control(self, dt, inp):
        h = self.hero
        if not h.can_act(): return
        dx = (1 if inp.right else 0) - (1 if inp.left else 0)
        if inp.attack:
            h.set_state('attack'); return
        if dx:
            side = 1 if h.x >= self.ogre.x else -1
            h.facing = dx; h.x += dx * C.HERO_SPEED * dt
            o = self.ogre
            if o.state != 'dead' and abs(h.x - o.x) < C.MIN_SEPARATION: h.x = o.x + side * C.MIN_SEPARATION
            if h.state != 'walk': h.set_state('walk')
        elif h.state != 'idle':
            h.set_state('idle')

    def _ogre_ai(self, dt):
        o, h = self.ogre, self.hero
        if not o.can_act(): return
        if h.state == 'dead':
            if o.state != 'idle': o.set_state('idle')
            return
        o.facing = 1 if h.x > o.x else -1
        dist = abs(h.x - o.x)
        if self.ai_cooldown > 0: self.ai_cooldown -= dt
        if dist > C.OGRE_ATTACK_DIST:                      # approach
            o.x += o.facing * C.OGRE_SPEED * dt
            if o.state != 'walk': o.set_state('walk')
            if dist > C.OGRE_ATTACK_DIST + C.OGRE_PATIENCE_DIST: self.ai_wait = None   # hero ran away: forget the plan
            return
        if o.state != 'idle': o.set_state('idle')
        if self.ai_cooldown <= 0:                          # in range: pause first, then swing
            if self.ai_wait is None: self.ai_wait = self.rng.uniform(*C.OGRE_WAIT_BEFORE_ATTACK)
            self.ai_wait -= dt
            if self.ai_wait <= 0:
                self.ai_wait = None; o.set_state('attack')

    def _knockback(self, dt):
        for f in self.fighters():
            if f.kb_t > 0:
                f.x += f.kb_dir * (C.KNOCKBACK / C.KNOCKBACK_TIME) * dt; f.kb_t -= dt

    def _attacks(self):
        hits = []
        for atk, tgt in ((self.hero, self.ogre), (self.ogre, self.hero)):
            if atk.state != 'attack': continue
            idx = atk.frame_index(self.timing)
            if idx >= 3 and not atk.slash_done:
                atk.slash_done = True; self.add_vfx(SLASH[atk.kind], atk.x, atk.facing < 0)
                self.events.append(('swing', atk.kind))
            if atk.hit_done or idx not in C.ACTIVE_FRAMES: continue
            if tgt.state == 'dead' or tgt.invuln > 0: continue
            lo, hi = REACH[atk.kind]
            a0, a1 = (atk.x + lo, atk.x + hi) if atk.facing > 0 else (atk.x - hi, atk.x - lo)
            if a0 <= tgt.x + tgt.hw and a1 >= tgt.x - tgt.hw:
                atk.hit_done = True; hits.append((atk, tgt))
        for atk, tgt in hits: self._hit(atk, tgt)          # applied together, so trades are possible

    def _hit(self, atk, tgt):
        tgt.hp = max(0, tgt.hp - C.DAMAGE)
        self.add_vfx('blood_splash', tgt.x, tgt.x > atk.x)
        self.shake = C.SHAKE_TIME
        self.events.append(('hit', tgt.kind))
        dirn = 1 if tgt.x >= atk.x else -1
        tgt.facing = -dirn                                   # turns toward the attacker, recoils backwards
        tgt.kb_dir = dirn; tgt.kb_t = C.KNOCKBACK_TIME
        if tgt.hp <= 0:
            tgt.set_state('dead'); tgt.invuln = 999.0
            self.events.append(('death', tgt.kind))
            self.add_vfx('spirit', tgt.x, tgt.x > atk.x, delay=C.SPIRIT_DELAY)
            if tgt is self.hero: self.hero_deaths += 1; self.hero_timer = C.RESPAWN_DELAY
            else: self.ogre_deaths += 1; self.ogre_timer = C.RESPAWN_DELAY
        else:
            self.events.append(('hurt', tgt.kind))
            tgt.set_state('hurt'); tgt.invuln = tgt.duration(self.timing) + C.HURT_INVULN_EXTRA
            if tgt is self.ogre: self.ai_wait = None

    def _timeouts(self):
        for f in self.fighters():
            if f.state in ('attack', 'hurt') and f.t >= f.duration(self.timing):
                was_attack = f.state == 'attack'
                f.set_state('idle')
                if f is self.ogre:
                    if was_attack: self.ai_cooldown = self.rng.uniform(*C.OGRE_COOLDOWN)
                    else: self.ai_cooldown = 0.0; self.ai_wait = self.rng.uniform(*C.OGRE_RETALIATE_WAIT)

    def _respawns(self, dt):
        if self.hero_timer is not None:
            self.hero_timer -= dt
            if self.hero_timer <= 0:
                self.hero_timer = None; old_cam = self.cam_x(); self.bury(self.hero)
                nx = old_cam + C.HERO_SPAWN_MARGIN
                self.hero = Fighter('knight', nx, +1, invuln=C.SPAWN_INVULN)
                self.cam_off = old_cam - (nx - C.SCREEN_W / 2)      # camera keeps its place, then glides
                self.events.append(('spawn', 'knight'))
        if self.ogre_timer is not None:
            self.ogre_timer -= dt
            if self.ogre_timer <= 0:
                self.ogre_timer = None; self.bury(self.ogre)
                self.ogre = Fighter('ogre', self.cam_x() + C.SCREEN_W + C.OGRE_SPAWN_MARGIN, -1)
                self.ai_wait = None; self.ai_cooldown = 0.6
                self.events.append(('spawn', 'ogre'))


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
