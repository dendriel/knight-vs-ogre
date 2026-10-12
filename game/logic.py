"""Game rules. No pygame in here: this module can be tested without a window."""
import json, math, os, random
from . import config as C
from .stages import THEMES, PROP_PLACE

# Default parameters of the enemy AIs (T20); a fighter def may override any of them in 'ai_params'.
#   attack_dist: stops walking and prepares to swing | wait: random pause before a swing (the player's window) |
#   cooldown: rest after a swing | retaliate: shorter pause after recovering from a hit | patience: how far the hero may
#   step back before the enemy forgets its plan | retreat_dist: hero closer than this and the enemy steps back
#   while resting (0 = never)
AI_DEFAULT = dict(attack_dist=C.OGRE_ATTACK_DIST, wait=C.OGRE_WAIT_BEFORE_ATTACK, cooldown=C.OGRE_COOLDOWN,
                  retaliate=C.OGRE_RETALIATE_WAIT, patience=C.OGRE_PATIENCE_DIST, retreat_dist=0)

# Elite variants (T26): modifiers over any fighter def. speed/hp/damage multiply; wait/cooldown scale the AI pauses.
# `tint` is a colour the view multiplies over the sprite, so elites need no new art.
ELITE_MODS = {
    'veteran': dict(speed=1.25, hp=1.0, damage=1.0, wait=0.7, cooldown=0.85, tint=(110, 160, 255)),
    'brute': dict(speed=0.95, hp=1.6, damage=1.5, wait=1.0, cooldown=1.0, tint=(255, 100, 90)),
    'agile': dict(speed=1.4, hp=0.7, damage=1.0, wait=0.8, cooldown=0.8, tint=(255, 235, 90)),
}

# One entry per kind of fighter: everything that differs between a knight and an ogre lives here (T01).
FIGHTER_DEFS = {
    'knight': dict(hero=True, max_hp=C.HERO_MAX_HP, speed=C.HERO_SPEED, half_width=8, sheet='knight', ai=None,
                   voice='knight', jump=1.0, special='special', secondary=None,
                   anim={'idle': 'idle', 'walk': 'run', 'hurt': 'hurt', 'dead': 'death'}, primary='sword',
                   slash='sword_slash', reach=C.KNIGHT_REACH, label='HERÓI'),
    'ogre_captain': dict(hero=False, boss=True, max_hp=C.CAPTAIN_MAX_HP, speed=C.CAPTAIN_SPEED, half_width=18,
                         sheet='ogre_captain', ai='boss', boss_id='captain', summon=('soldier', 'soldier'),
                         anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='captain_slam',
                         slash=None, reach=C.CAPTAIN_REACH, label='OGRO-CAPITAO',
                         ai_params=dict(attack_dist=62, wait=(0.4, 0.7), cooldown=(0.9, 1.4), patience=30)),
    'minotaur_lord': dict(hero=False, boss=True, max_hp=C.MINO_LORD_MAX_HP, speed=C.MINO_LORD_SPEED, half_width=18,
                          sheet='minotaur_lord', ai='boss', boss_id='minotaur_lord', summon=('goblin', 'goblin', 'kobold'),
                          anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death', 'charge': 'attack',
                                'dash': 'walk'}, charge_frame=2, primary='mino_lord_axe', slash=None, reach=(-16, 70),
                          label='REI MINOTAURO', ai_params=dict(attack_dist=54, wait=(0.3, 0.5), cooldown=(0.8, 1.2)),
                          charge=dict(cooldown=2.6, telegraph=0.55, speed=300.0, time=0.7, damage=18, rest=0.8)),
    'black_knight': dict(hero=False, boss=True, max_hp=C.BLACK_KNIGHT_MAX_HP, speed=C.BLACK_KNIGHT_SPEED, half_width=11,
                         sheet='black_knight', ai='boss', boss_id='black_knight', guard=True, turn_delay=0.3,
                         summon=('archer', 'archer'), chain_chance=0.75,
                         anim={'idle': 'guard', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='bk_1',
                         slash=None, reach=(-14, 56), label='CAVALEIRO NEGRO',
                         ai_params=dict(attack_dist=44, wait=(0.35, 0.6), cooldown=(0.7, 1.1), patience=26)),
    'orc': dict(hero=False, max_hp=C.ORC_MAX_HP, speed=C.ORC_SPEED, half_width=10, sheet='orc', ai='melee',
                anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='orc_axe',
                slash='axe_slash', reach=C.OGRE_REACH, label='ORC',
                ai_params=dict(wait=C.ORC_WAIT, cooldown=C.ORC_COOLDOWN)),
    'goblin': dict(hero=False, max_hp=C.GOBLIN_MAX_HP, speed=C.GOBLIN_SPEED, half_width=6, sheet='goblin', ai='melee',
                   anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='goblin_stab',
                   slash=None, reach=C.GOBLIN_REACH, label='GOBLIN',
                   ai_params=dict(attack_dist=C.GOBLIN_ATTACK_DIST, wait=C.GOBLIN_WAIT, cooldown=C.GOBLIN_COOLDOWN,
                                  retaliate=(0.0, 0.1), patience=14)),
    'kobold': dict(hero=False, max_hp=C.KOBOLD_MAX_HP, speed=C.KOBOLD_SPEED, half_width=7, sheet='kobold', ai='ranged_lob',
                   anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='kobold_rock',
                   slash=None, reach=(0, 0), label='KOBOLD',
                   ai_params=dict(attack_dist=C.KOBOLD_KEEP_DIST, wait=C.KOBOLD_WAIT, cooldown=C.KOBOLD_COOLDOWN,
                                  retreat_dist=C.KOBOLD_TOO_CLOSE)),
    'minotaur': dict(hero=False, max_hp=C.MINOTAUR_MAX_HP, speed=C.MINOTAUR_SPEED, half_width=11, sheet='minotaur',
                     ai='charger', anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death',
                                         'charge': 'attack', 'dash': 'walk'}, charge_frame=2, primary='minotaur_axe',
                     slash='axe_slash', reach=C.OGRE_REACH, label='MINOTAURO',
                     ai_params=dict(wait=(0.3, 0.5), cooldown=(0.9, 1.4))),
    'shieldman': dict(hero=False, max_hp=C.SHIELDMAN_MAX_HP, speed=C.SHIELDMAN_SPEED, half_width=9, sheet='shieldman',
                      ai='guard', guard=True, turn_delay=C.SHIELD_TURN_DELAY,
                      anim={'idle': 'guard', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='shield_sword',
                      slash='sword_slash', reach=C.KNIGHT_REACH, label='ESCUDEIRO',
                      ai_params=dict(wait=C.SHIELDMAN_WAIT, cooldown=C.SHIELDMAN_COOLDOWN)),
    'archer': dict(hero=False, max_hp=C.ARCHER_MAX_HP, speed=C.ARCHER_SPEED, half_width=8, sheet='archer', ai='ranged_lob',
                   anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='archer_shot',
                   slash=None, reach=(0, 0), label='ARQUEIRO',
                   ai_params=dict(attack_dist=C.ARCHER_KEEP_DIST, wait=C.ARCHER_WAIT, cooldown=C.ARCHER_COOLDOWN,
                                  retreat_dist=C.ARCHER_TOO_CLOSE)),
    'spearman': dict(hero=False, max_hp=C.SPEARMAN_MAX_HP, speed=C.SPEARMAN_SPEED, half_width=8, sheet='spearman', ai='spear',
                     anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='spearman_thrust',
                     slash=None, reach=C.SPEARMAN_REACH, label='LANCEIRO',
                     ai_params=dict(attack_dist=C.SPEARMAN_ATTACK_DIST, wait=C.SPEARMAN_WAIT, cooldown=C.SPEARMAN_COOLDOWN,
                                    retreat_dist=C.SPEARMAN_RETREAT_DIST)),
    'soldier': dict(hero=False, max_hp=C.SOLDIER_MAX_HP, speed=C.SOLDIER_SPEED, half_width=8, sheet='soldier', ai='melee',
                    anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='soldier_sword',
                    slash='sword_slash', reach=C.KNIGHT_REACH, label='SOLDADO',
                    ai_params=dict(wait=C.SOLDIER_WAIT, cooldown=C.SOLDIER_COOLDOWN)),
    'ogre': dict(hero=False, max_hp=C.OGRE_MAX_HP, speed=C.OGRE_SPEED, half_width=10, sheet='ogre', ai='melee',
                 anim={'idle': 'idle', 'walk': 'walk', 'hurt': 'hurt', 'dead': 'death'}, primary='ogre_axe',
                 slash='axe_slash', reach=C.OGRE_REACH, label='OGRO'),
}

# Playable classes (T40): the id is a FIGHTER_DEFS key with hero=True. Everything a class changes is data there:
# max_hp, speed, jump (height multiplier), sheet, anim map, primary (id of the first attack of its combo chain), secondary,
# special, label and `blurb`. The three extra classes are added below (T42-T44).
CLASSES = ['knight']

# Every attack is data (T03). Adding one = one entry here + one row in a sprite sheet.
#   anim: sheet row | damage | reach: (from, to) in front of the hip | active: frames that can hit | slash_frame: frame
#   where the trail effect is born | slash: vfx row | move_factor: walking speed multiplier while swinging |
#   knockback: pixels the victim is pushed | guard_break: ignores shields (T24) | cooldown: seconds before reuse
WEAPONS = {                                  # pickup weapons the hero can hold (T13): attack id + sprite sheet
    'axe': dict(attack='axe', sheet='knight_axe'),
    'bow': dict(attack='bow', sheet='knight_bow'),
    'xbow': dict(attack='xbow', sheet='knight_xbow'),
}

ATTACKS = {
    'sword': dict(anim='attack_sword', damage=C.COMBO_DAMAGE[0], reach=C.KNIGHT_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                  slash='sword_slash', move_factor=C.ATTACK_MOVE_FACTOR, knockback=C.COMBO_KNOCKBACK[0], guard_break=False,
                  cooldown=0.0, wear=0.0, next='sword_2'),
    'sword_2': dict(anim='attack_sword_2', damage=C.COMBO_DAMAGE[1], reach=C.KNIGHT_REACH, active=C.ACTIVE_FRAMES,
                    slash_frame=3, slash='sword_slash_2', move_factor=C.ATTACK_MOVE_FACTOR,
                    knockback=C.COMBO_KNOCKBACK[1], guard_break=False, cooldown=0.0, wear=0.0, next='sword_3'),
    'sword_3': dict(anim='attack_sword_3', damage=C.COMBO_DAMAGE[2], reach=(C.KNIGHT_REACH[0], C.KNIGHT_REACH[1] + 6),
                    active=C.ACTIVE_FRAMES, slash_frame=3, slash='sword_slash_3', move_factor=C.ATTACK_MOVE_FACTOR,
                    knockback=C.COMBO_KNOCKBACK[2], guard_break=False, cooldown=0.0, wear=0.0, next=None),
    'axe': dict(anim='attack_axe', damage=C.AXE_DAMAGE, reach=C.AXE_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                slash=None, move_factor=C.AXE_MOVE_FACTOR, knockback=C.AXE_KNOCKBACK, guard_break=True, cooldown=0.0,
                wear=C.AXE_WEAR, next=None),
    'bow': dict(anim='attack_bow', damage=C.BOW_DAMAGE, reach=(0, 0), active=(), slash_frame=4, slash=None,
                move_factor=C.BOW_MOVE_FACTOR, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0, wear=C.BOW_WEAR,
                next=None, shoot=dict(kind='straight', sprite='arrow', speed=C.BOW_SPEED, max_range=C.BOW_RANGE)),
    'xbow': dict(anim='attack_crossbow', damage=C.XBOW_DAMAGE, reach=(0, 0), active=(), slash_frame=4, slash=None,
                 move_factor=C.XBOW_MOVE_FACTOR, knockback=C.KNOCKBACK * 1.5, guard_break=False, cooldown=C.XBOW_RELOAD,
                 wear=C.XBOW_WEAR, next=None,
                 shoot=dict(kind='straight', sprite='bolt', speed=C.XBOW_SPEED, max_range=C.XBOW_RANGE)),
    'special': dict(anim='attack_special', damage=C.SPECIAL_DAMAGE, reach=(-C.SPECIAL_RADIUS, C.SPECIAL_RADIUS),
                    active=(2, 3, 4, 5), slash_frame=1, slash='spin_slash', move_factor=0.0, knockback=C.SPECIAL_KNOCKBACK,
                    guard_break=True, cooldown=0.0, wear=0.0, next=None, rehit=4, ignore_invuln=True, ring=True),
    'soldier_sword': dict(anim='attack', damage=C.DAMAGE, reach=C.KNIGHT_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                          slash='sword_slash', move_factor=1.0, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0,
                          wear=0.0, next=None),
    'spearman_thrust': dict(anim='attack', damage=C.DAMAGE, reach=C.SPEARMAN_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                            slash=None, move_factor=1.0, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0,
                            wear=0.0, next=None),
    'archer_shot': dict(anim='attack', damage=C.DAMAGE, reach=(0, 0), active=(), slash_frame=4, slash=None,
                        move_factor=0.0, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0, wear=0.0, next=None,
                        shoot=dict(kind='lob', sprite='arrow', flight=C.LOB_FLIGHT, apex=C.LOB_APEX, radius=C.LOB_RADIUS)),
    'shield_sword': dict(anim='attack', damage=C.DAMAGE, reach=C.KNIGHT_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                         slash='sword_slash', move_factor=1.0, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0,
                         wear=0.0, next=None),
    'captain_slam': dict(anim='attack', damage=C.CAPTAIN_DAMAGE, reach=C.CAPTAIN_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                         slash=None, move_factor=0.6, knockback=C.KNOCKBACK * 2.0, guard_break=True, cooldown=0.0, wear=0.0,
                         next=None),
    'mino_lord_axe': dict(anim='attack', damage=C.MINO_LORD_DAMAGE, reach=(-16, 70), active=C.ACTIVE_FRAMES, slash_frame=3,
                          slash=None, move_factor=0.8, knockback=C.KNOCKBACK * 1.8, guard_break=False, cooldown=0.0,
                          wear=0.0, next=None),
    'bk_1': dict(anim='attack', damage=C.BLACK_KNIGHT_DAMAGE[0], reach=(-14, 56), active=C.ACTIVE_FRAMES, slash_frame=3,
                 slash=None, move_factor=0.8, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0, wear=0.0, next='bk_2'),
    'bk_2': dict(anim='attack_2', damage=C.BLACK_KNIGHT_DAMAGE[1], reach=(-14, 56), active=C.ACTIVE_FRAMES, slash_frame=3,
                 slash=None, move_factor=0.8, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0, wear=0.0, next='bk_3'),
    'bk_3': dict(anim='attack_3', damage=C.BLACK_KNIGHT_DAMAGE[2], reach=(-14, 60), active=C.ACTIVE_FRAMES, slash_frame=3,
                 slash=None, move_factor=0.8, knockback=C.KNOCKBACK * 1.6, guard_break=False, cooldown=0.0, wear=0.0, next=None),
    'orc_axe': dict(anim='attack', damage=C.DAMAGE, reach=C.OGRE_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                    slash='axe_slash', move_factor=1.0, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0, wear=0.0,
                    next=None),
    'goblin_stab': dict(anim='attack', damage=C.GOBLIN_DAMAGE, reach=C.GOBLIN_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                        slash=None, move_factor=1.0, knockback=C.KNOCKBACK * 0.6, guard_break=False, cooldown=0.0,
                        wear=0.0, next=None),
    'kobold_rock': dict(anim='attack', damage=C.KOBOLD_DAMAGE, reach=(0, 0), active=(), slash_frame=3, slash=None,
                        move_factor=0.0, knockback=C.KNOCKBACK * 0.6, guard_break=False, cooldown=0.0, wear=0.0, next=None,
                        shoot=dict(kind='lob', sprite='rock', flight=C.LOB_FLIGHT, apex=C.LOB_APEX, radius=C.LOB_RADIUS)),
    'minotaur_axe': dict(anim='attack', damage=C.MINOTAUR_DAMAGE, reach=(-12, 50), active=C.ACTIVE_FRAMES, slash_frame=3,
                         slash='axe_slash', move_factor=1.0, knockback=C.KNOCKBACK * 1.4, guard_break=False, cooldown=0.0,
                         wear=0.0, next=None),
    'ogre_axe': dict(anim='attack', damage=C.DAMAGE, reach=C.OGRE_REACH, active=C.ACTIVE_FRAMES, slash_frame=3,
                     slash='axe_slash', move_factor=1.0, knockback=C.KNOCKBACK, guard_break=False, cooldown=0.0,
                     wear=0.0, next=None),
}
ANIM = {k: d['anim'] for k, d in FIGHTER_DEFS.items()}          # (aliases kept for old code / tests)
SLASH = {k: d['slash'] for k, d in FIGHTER_DEFS.items()}
REACH = {k: d['reach'] for k, d in FIGHTER_DEFS.items()}
LOOPING = ('idle', 'walk', 'dash')


def load_timing(assets_dir):
    """fps of every animation, read from the sprite atlases (every *_spritesheet.json) and scaled by config.ANIM_SPEED."""
    t = {}
    for fn in sorted(os.listdir(assets_dir)):
        if not fn.endswith('_spritesheet.json'): continue
        k = fn[:-len('_spritesheet.json')]
        with open(os.path.join(assets_dir, fn)) as f:
            mult = C.ANIM_SPEED.get(k) or C.ANIM_SPEED.get(k.split('_')[0], {})      # 'knight_axe' shares the knight's speeds
            t[k] = {n: a['fps'] * mult.get(n, 1.0) for n, a in json.load(f)['animations'].items()}
    return t


class Inputs:
    """What the player does this frame. `attack` is the level (button held); the *_pressed / *_released flags are edges
    computed by main.py; attack_held_t = seconds the attack button has been held (T05)."""
    def __init__(self, left=False, right=False, attack=False, jump=False, secondary=False, attack_pressed=False,
                 attack_released=False, attack_held_t=0.0, secondary_pressed=False, potion_pressed=False):
        self.left, self.right, self.attack, self.jump = left, right, attack, jump
        self.secondary, self.attack_pressed, self.attack_released = secondary, attack_pressed, attack_released
        self.attack_held_t, self.secondary_pressed, self.potion_pressed = attack_held_t, secondary_pressed, potion_pressed


class Fighter:
    def __init__(self, kind, x, facing, hp=None, invuln=0.0, elite=None):
        self.defn = FIGHTER_DEFS[kind]; self.max_hp = self.defn['max_hp']
        self.ai_p = dict(AI_DEFAULT, **self.defn.get('ai_params', {}))
        self.elite = elite; self.mods = ELITE_MODS.get(elite, {}); self.token = False; self.turn_t = 0.0
        if self.mods:                                           # elites: more / less life, shorter pauses
            self.max_hp = max(1, int(round(self.max_hp * self.mods['hp'])))
            self.ai_p['wait'] = tuple(v * self.mods['wait'] for v in self.ai_p['wait'])
            self.ai_p['cooldown'] = tuple(v * self.mods['cooldown'] for v in self.ai_p['cooldown'])
        if hp is None: hp = self.max_hp
        self.kind, self.x, self.facing, self.hp, self.invuln = kind, float(x), facing, hp, invuln
        self.state = 'idle'; self.t = 0.0
        self.y = 0.0; self.vy = 0.0; self.grounded = True      # y = height of the feet above the ground (up is +)
        self.air_t = 0.0; self.air_phase = None                 # time in the current rising / falling phase
        self.hit_done = False; self.slash_done = False
        self.kb_dir = 0; self.kb_t = 0.0; self.kb_speed = C.KNOCKBACK / C.KNOCKBACK_TIME
        self.charge_t = 0.0; self.charge_fx = 0.0                # holding the button with a full meter (T12)
        self.armor = 0; self.armor_max = C.ARMOR_MAX if self.defn['hero'] else 0; self.weapon = None   # equipment (T13, T15); weapon = dict(id, durability)
        self.attack_id = self.defn['primary']                   # which ATTACKS entry the 'attack' state plays
        self.hit_set = []                                       # targets already hit by the current swing
        self.charge_cd = 0.0; self.dash_t = 0.0; self.dash_hit = False; self.summoned = False
        self.rehit_done = False; self.cd = {}                    # cd: attack id -> time it can be used again
        self.combo_next = None; self.chain = None               # queued next stroke / (time, id) just after a stroke ended
        self.ai_wait = None; self.ai_cooldown = 0.6             # enemy AI state (per fighter, so many enemies can coexist)
        self.respawn_t = None                                   # enemies: countdown (after death) until the body is buried

    def set_state(self, s):
        self.state = s; self.t = 0.0; self.hit_done = False; self.slash_done = False; self.hit_set = []; self.combo_next = None
        self.rehit_done = False; self.charge_t = 0.0

    @property
    def is_hero(self): return self.defn['hero']

    @property
    def voice(self):
        """Name the audio layer uses for this fighter's events (all hero classes sound like 'knight' for now)."""
        return self.defn.get('voice', self.kind)

    @property
    def speed(self): return self.defn['speed'] * self.mods.get('speed', 1.0)

    @property
    def airborne(self): return not self.grounded

    @property
    def anim(self):
        if self.is_hero and self.airborne and self.state in ('idle', 'walk'):
            return 'jump_up' if self.vy > 0 else 'jump_fall'      # falling off a ledge without jumping plays jump_fall too
        if self.state == 'attack': return ATTACKS[self.attack_id]['anim']
        if self.state == 'charge': return self.defn['anim'].get('charge', 'attack_special')   # hero: frame 0 of the spin
        return self.defn['anim'][self.state]

    @property
    def sheet(self):
        if self.weapon: return WEAPONS[self.weapon['id']]['sheet']        # the hero draws with the weapon in hand
        return self.defn['sheet']

    @property
    def primary(self):
        """attack id of the primary attack: the held weapon's, or the class's own"""
        return WEAPONS[self.weapon['id']]['attack'] if self.weapon else self.defn['primary']

    @property
    def hw(self): return self.defn['half_width']

    def frame_index(self, timing):
        a = self.anim; tm = timing[self.sheet]
        if a == 'jump_up': return min(int(self.air_t * tm[a]), 5)
        if a == 'jump_fall': return int(self.air_t * tm[a]) % 6
        if self.state == 'charge': return self.defn.get('charge_frame', 0)
        n = int(self.t * tm[a])
        return n % 6 if self.state in LOOPING else min(n, 5)

    def duration(self, timing): return 6.0 / timing[self.sheet][self.anim]

    def can_act(self): return self.state in ('idle', 'walk')


class Pickup:
    """An item lying in the world. kind: 'potion' | 'coins' | 'armor' | 'weapon' (item = weapon id, amount = durability). y = height above the ground; it pops up and falls."""
    def __init__(self, kind, x, amount=0, item=None):
        self.kind, self.x, self.amount, self.item = kind, float(x), amount, item
        self.y = 14.0; self.vy = 90.0; self.t = 0.0


class Projectile:
    """Something in flight (T04). kind 'straight': flies level in the facing direction and hits the first target on its
    path (within VERTICAL_REACH of the shooter's feet). kind 'lob': a parabola over the sky towards where the target
    stood at launch (tx, ty); it hurts whatever is inside the landing zone when it comes down, so the hero can dodge."""
    def __init__(self, kind, owner, x, base_y, facing, damage, sprite, speed=240.0, max_range=260.0, pierce=False,
                 knockback=C.KNOCKBACK, tx=None, flight=0.9, apex=60.0, radius=14.0, chest=C.PROJ_CHEST):
        self.kind, self.owner, self.x, self.x0, self.base_y, self.facing = kind, owner, float(x), float(x), base_y, facing
        self.damage, self.sprite, self.speed, self.max_range, self.pierce = damage, sprite, speed, max_range, pierce
        self.knockback, self.tx, self.ty = knockback, tx, base_y
        self.flight, self.apex, self.radius, self.chest = flight, apex, radius, chest
        self.t = 0.0; self.height = chest; self.hit_set = []; self.done = False


class AreaHit:
    """A box on the ground that hurts everyone inside it once, after `delay`, and lingers for `duration` (T04)."""
    def __init__(self, owner, x0, x1, base_y, damage, delay=0.0, duration=0.1, knockback=C.KNOCKBACK, vfx=None,
                 guard_break=True):
        self.owner, self.x0, self.x1, self.base_y, self.damage = owner, x0, x1, base_y, damage
        self.delay, self.duration, self.knockback, self.vfx, self.guard_break = delay, duration, knockback, vfx, guard_break
        self.t = 0.0; self.hit_set = []; self.done = False


class World:
    def __init__(self, timing, seed=1, stage=None, hero_class='knight'):
        self.timing = timing; self.rng = random.Random(seed)
        self.hero = Fighter(hero_class, 0.0, +1)
        self.enemies = [Fighter('ogre', C.START_OGRE_OFFSET, -1)]
        self.features = {'potions', 'weapon', 'armor', 'combo'}                              # HUD slots that exist: 'armor', 'combo', 'weapon', 'potions'
        self.potions = 0; self.combo = 0                   # inventory / combo meter (T10, T12)
        self.max_attackers = C.MAX_ATTACKERS               # tokens (T26)
        self.stage = stage; self.next_enc = 0              # None = the endless mode; else a finite stage (T30)
        self.stage_clear = False; self.defeated = False
        self.arena = None; self.boss = None; self.boss_dead = False     # boss arena (T32)
        self.queue = []                                    # enemies of fired encounters waiting for room (T36)
        self.diff = stage.difficulty(0.0) if stage is not None else None
        if stage is not None:                              # a path: starts at the left end, no automatic respawns
            self.hero.x = stage.start_x; self.enemies = []; self.cam_off = 0.0
        self.spawn_target = 1                              # endless mode keeps this many enemies in the world (T02)
        if stage is not None: self.spawn_target = 0
        self._jump_held = False; self._box_cache = {}
        self.corpses = []; self.vfx = []
        self.projectiles = []; self.areas = []
        self.hero_deaths = 0; self.ogre_deaths = 0
        self.pickups = []; self.gold = 0                   # gold belongs to the player, so it survives hero deaths
        self.spawn_rng = random.Random(seed + 2000)        # which enemy enters next (separate stream, like loot)
        self.roster = C.ENDLESS_ROSTER                     # endless mode: grows with the kill count
        self.loot_rng = random.Random(seed + 1000)         # separate stream: drops never disturb the AI's random sequence
        self.hero_timer = None
        self.cam_off = C.SCREEN_W / 2 - C.START_HERO_SCREEN_X     # hero starts on the left, camera glides to center
        if stage is not None: self.cam_off = 0.0                    # stages: the camera clamps at the start instead
        self.shake = 0.0; self.time = 0.0
        self.events = []                                           # (name, kind) for the audio layer; main.py drains it
        self.stats = dict(kills=0, damage_dealt=0, damage_taken=0, gold_gained=0, revives=0)

    # ------------------------------------------------------------------ helpers
    @property
    def theme_id(self): return self.stage.theme if self.stage is not None else 'village'

    def _cam_base(self):
        st = self.stage
        if st is None: return self.hero.x - C.SCREEN_W / 2
        if self.arena is not None: return self.arena[0]                    # the arena is one fixed screen
        return max(0.0, min(st.length - C.SCREEN_W + C.STAGE_END_MARGIN, self.hero.x - C.SCREEN_W / 2))

    def cam_x(self): return self._cam_base() + self.cam_off

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
        if inp.potion_pressed: self.drink_potion()
        self._hero_control(dt, inp)
        for e in self.enemies: self._enemy_ai(e, dt)
        self._knockback(dt)
        for f in self.fighters(): self._physics(f, dt)
        self._attacks()
        self._projectiles(dt)
        self._areas(dt)
        self._pickups(dt)
        self._timeouts()
        self._respawns(dt)
        self._stage(dt)
        for v in self.vfx: v['t'] += dt
        self.vfx = [v for v in self.vfx if int(v['t'] * self.timing['vfx'][v['name']]) < 6]
        self.cam_off *= math.exp(-C.CAMERA_EASE * dt)
        if abs(self.cam_off) < 0.25: self.cam_off = 0.0

    def _hero_control(self, dt, inp):
        h = self.hero
        jump_edge = inp.jump and not self._jump_held; self._jump_held = inp.jump     # one jump per key press
        if h.state not in ('idle', 'walk', 'attack', 'charge'): return                # hurt / dead: no control
        dx = (1 if inp.right else 0) - (1 if inp.left else 0)
        if jump_edge and h.grounded:
            h.vy = 2 * C.JUMP_HEIGHT / C.JUMP_RISE_TIME * math.sqrt(h.defn.get('jump', 1.0))   # class jump = height multiplier
            h.grounded = False; h.air_phase = None
            self.events.append(('jump', h.voice))
        full = self.combo >= C.COMBO_BAR_MAX
        if h.state == 'charge':                                                       # holding with a full bar
            h.charge_fx -= dt
            if h.charge_fx <= 0: h.charge_fx = 0.4; self.add_vfx('charge', h.x, h.facing < 0, y=h.y)
            if not inp.attack:                                                        # released: fire the special
                self.combo = 0; self.start_attack(h, h.defn['special']); h.invuln = max(h.invuln, h.duration(self.timing))
                self.events.append(('special', h.voice)); return
            h.x += dx * h.defn['speed'] * C.CHARGE_MOVE_FACTOR * dt
            return
        if h.state in ('idle', 'walk') and inp.attack and full and 'combo' in self.features:
            h.charge_t += dt                                                          # the swing waits to see if it is a hold
            if h.charge_t >= C.SPECIAL_HOLD_MIN:
                h.set_state('charge'); h.charge_fx = 0.0; self.events.append(('charge', h.voice)); return
            if dx: h.facing = dx; h.x += dx * h.defn['speed'] * dt
            return
        if h.charge_t > 0 and h.state in ('idle', 'walk'):                            # released early: it was a plain click
            h.charge_t = 0.0
            if not inp.attack: self.start_attack(h, h.primary)
        if h.state == 'attack' and inp.attack_pressed:                                # a click inside the window queues the next stroke
            nxt = ATTACKS[h.attack_id].get('next')
            if nxt and h.frame_index(self.timing) >= C.COMBO_WINDOW_START: h.combo_next = nxt
        ready = h.state == 'attack' or self.time >= h.cd.get(h.primary, 0.0)         # (reload of a crossbow)
        if h.state == 'attack' or ((inp.attack or (inp.attack_pressed and h.chain)) and ready):   # can walk (not turn) while swinging
            if h.state != 'attack':
                if inp.attack_pressed and h.chain and self.time - h.chain[0] <= C.COMBO_BUFFER:
                    self.start_attack(h, h.chain[1])                                 # clicked just after the stroke ended
                else: self.start_attack(h, h.primary)
            h.x += dx * h.defn['speed'] * ATTACKS[h.attack_id]['move_factor'] * dt
            return
        if dx:
            h.facing = dx; h.x += dx * h.defn['speed'] * dt
            if h.state != 'walk': h.set_state('walk')
        elif h.state != 'idle':
            h.set_state('idle')

    def _enemy_ai(self, o, dt):
        """Dispatches to the behaviour named by FIGHTER_DEFS[kind]['ai'] (T20): _ai_melee, and the ones added later."""
        getattr(self, '_ai_' + o.defn['ai'])(o, dt)

    def _draw_enemy(self):
        """Next endless enemy: weighted draw among the roster entries unlocked by the kill count (+ maybe an elite)."""
        pool = [(k, wgt) for need, k, wgt in self.roster if self.ogre_deaths >= need]
        total = sum(wgt for _, wgt in pool); r = self.spawn_rng.uniform(0, total)
        kind = pool[-1][0]
        for k, wgt in pool:
            r -= wgt
            if r <= 0: kind = k; break
        elite = None
        if self.ogre_deaths >= C.ENDLESS_ELITE_FROM and self.spawn_rng.random() < C.ENDLESS_ELITE_CHANCE:
            elite = self.spawn_rng.choice(sorted(ELITE_MODS))
        return kind, elite

    def spawn_enemy(self, kind, x, facing=-1, elite=None):
        e = Fighter(kind, x, facing, elite=elite); e.ai_cooldown = 0.6
        self.enemies.append(e); self.events.append(('spawn', kind))
        return e

    def focus_enemy(self):
        """The living enemy shown in the HUD: the nearest to the hero (None when nobody is alive)."""
        alive = [e for e in self.enemies if e.state != 'dead']
        if not alive: return self.ogre
        return min(alive, key=lambda e: (abs(e.x - self.hero.x), id(e)))

    def free_tokens(self):
        """Attack tokens left: only `max_attackers` enemies may prepare / throw a blow at once (T26)."""
        return self.max_attackers - sum(1 for e in self.enemies if e.token and e.state != 'dead')

    def wait_rank(self, o):
        """How many other token-less enemies are closer to the hero than `o` (0 = first in line)."""
        d = abs(o.x - self.hero.x)
        return sum(1 for e in self.enemies if e is not o and e.state != 'dead' and not e.token
                   and (abs(e.x - self.hero.x), id(e)) < (d, id(o)))

    def _ai_ranged_lob(self, o, dt):
        """Archer: keeps its distance (steps back when pressed, walks closer when far) and lobs an arrow that lands where
        the hero stood, so he has to move. No attack token: it never stands next to him."""
        h = self._ai_prelude(o, dt)
        if h is None: return
        p = o.ai_p; dist = abs(h.x - o.x)
        if dist < p['retreat_dist']:                       # too close: back away (the walk plays, facing the hero)
            o.x -= o.facing * o.speed * 0.9 * dt
            if o.state != 'walk': o.set_state('walk')
            o.ai_wait = None
            return
        if dist > p['attack_dist'] + 24:                   # too far: approach
            o.x += o.facing * o.speed * dt
            if o.state != 'walk': o.set_state('walk')
            o.ai_wait = None
            return
        if o.state != 'idle': o.set_state('idle')
        if o.ai_cooldown <= 0:
            if o.ai_wait is None: o.ai_wait = self.rng.uniform(*p['wait'])
            o.ai_wait -= dt
            if o.ai_wait <= 0:
                o.ai_wait = None; self.start_attack(o, o.defn['primary'])

    def _ai_spear(self, o, dt): self._ai_melee(o, dt)       # same plan, other numbers (attack_dist / retreat_dist)

    def _face(self, o, d, dt):
        """Turns an enemy towards `d`. Shield bearers take `turn_delay` seconds to bring the shield round (T24)."""
        delay = o.defn.get('turn_delay', 0.0)
        if o.facing == d: o.turn_t = 0.0; return
        if delay <= 0: o.facing = d; return
        o.turn_t += dt
        if o.turn_t >= delay: o.facing = d; o.turn_t = 0.0

    def _ai_charger(self, o, dt):
        """Minotaur: a telegraphed charge in a straight line (a pose with the axe raised, then a dash), otherwise a
        heavy melee fighter. Jumping over it (feet above VERTICAL_REACH) dodges the dash. T25."""
        h = self.hero
        cp = dict(cooldown=C.MINOTAUR_CHARGE_COOLDOWN, telegraph=C.MINOTAUR_TELEGRAPH, speed=C.MINOTAUR_DASH_SPEED,
                  time=C.MINOTAUR_DASH_TIME, damage=C.MINOTAUR_DASH_DAMAGE, rest=C.MINOTAUR_REST, **o.defn.get('charge', {}))
        o.charge_cd = max(0.0, getattr(o, 'charge_cd', 0.0) - dt)
        if o.state == 'charge':                            # telegraph: standing still, axe raised, tracking nothing
            o.ai_wait -= dt
            if o.ai_wait <= 0:
                o.set_state('dash'); o.dash_t = cp['time']; o.dash_hit = False
            return
        if o.state == 'dash':
            o.dash_t -= dt; o.x += o.facing * cp['speed'] * dt
            if self.arena is not None: o.x = max(self.arena[0] + C.ARENA_WALL_MARGIN, min(self.arena[1] - C.ARENA_WALL_MARGIN, o.x))
            if (not o.dash_hit and h.state != 'dead' and h.invuln <= 0 and abs(h.x - o.x) <= o.hw + h.hw + 4
                    and abs(h.y - o.y) <= C.VERTICAL_REACH):
                o.dash_hit = True
                self._hit(o, h, at=dict(damage=cp['damage'], knockback=C.MINOTAUR_DASH_KNOCKBACK), src_x=o.x)
            if o.dash_t <= 0:
                o.set_state('idle'); o.ai_cooldown = cp['rest']; o.token = False
            return
        if o.can_act() and h.state != 'dead' and o.charge_cd <= 0 and o.ai_cooldown <= 0:
            d = abs(h.x - o.x)
            if C.MINOTAUR_CHARGE_MIN <= d <= C.MINOTAUR_CHARGE_MAX and abs(h.y - o.y) <= C.VERTICAL_REACH:
                o.facing = 1 if h.x > o.x else -1
                o.set_state('charge'); o.ai_wait = cp['telegraph']; o.charge_cd = cp['cooldown']
                o.token = False; self.events.append(('telegraph', o.kind))
                return
        self._ai_melee(o, dt)

    def _ai_boss(self, o, dt):
        """Boss behaviours (T32): call reinforcements once at half life, then the fighting style of the boss id."""
        if not o.summoned and o.hp <= o.max_hp * C.BOSS_SUMMON_AT and o.can_act():
            o.summoned = True; o.set_state('idle'); o.ai_cooldown = 0.8
            self._summon(o); return
        if o.defn['boss_id'] == 'minotaur_lord': self._ai_charger(o, dt)
        else: self._ai_melee(o, dt)

    def _ai_guard(self, o, dt): self._ai_melee(o, dt)          # shield bearer: melee plan, the guard is in _hit()

    def _ai_prelude(self, o, dt):
        """Shared first steps of every behaviour. Returns the hero when the enemy is free to decide something."""
        h = self.hero
        if o.state == 'attack' and h.state != 'dead' and abs(h.x - o.x) > 2 and o.frame_index(self.timing) < C.ACTIVE_FRAMES[0]:
            self._face(o, 1 if h.x > o.x else -1, dt)       # wind-up: keep tracking a hero who walks through him
        if not o.can_act(): return None
        if h.state == 'dead':
            if o.state != 'idle': o.set_state('idle')
            return None
        if abs(h.x - o.x) > 2: self._face(o, 1 if h.x > o.x else -1, dt)   # no flip-flop when the hero is right on top of him
        if o.ai_cooldown > 0: o.ai_cooldown -= dt
        return h

    def _ai_melee(self, o, dt):
        h = self._ai_prelude(o, dt)
        if h is None: return
        p = o.ai_p; dist = abs(h.x - o.x)
        reachable = abs(h.y - o.y) <= C.VERTICAL_REACH
        rd = p['retreat_dist']
        if rd and dist < rd and o.ai_cooldown > 0:        # spear: too close while resting -> step back to regain space
            o.x -= o.facing * o.speed * 0.8 * dt
            if o.state != 'walk': o.set_state('walk')
            return
        need = p['attack_dist']
        if not o.token and self.free_tokens() <= 0:        # crowd: no free attack token, keep a standoff distance (T26)
            need += C.STANDOFF_BASE + C.STANDOFF_STEP * self.wait_rank(o)
        if dist > need:                                    # approach
            o.x += o.facing * o.speed * dt
            if o.state != 'walk': o.set_state('walk')
            if dist > p['attack_dist'] + p['patience']: o.ai_wait = None; o.token = False   # hero ran away: forget the plan
            return
        if o.state != 'idle': o.set_state('idle')
        if not reachable: o.ai_wait = None; o.token = False; return   # hero too high: the enemy just waits below him
        if not o.token:
            if self.free_tokens() <= 0: return             # still waiting for a turn
            o.token = True
        if o.ai_cooldown <= 0:                             # in range: pause first, then swing
            if o.ai_wait is None: o.ai_wait = self.rng.uniform(*p['wait'])
            o.ai_wait -= dt
            if o.ai_wait <= 0:
                o.ai_wait = None; self.start_attack(o, o.defn['primary'])

    def _knockback(self, dt):
        for f in self.fighters():
            if f.kb_t > 0:
                f.x += f.kb_dir * f.kb_speed * dt; f.kb_t -= dt

    def _attacks(self):
        hits = []
        pairs = [(self.hero, e) for e in self.enemies] + [(e, self.hero) for e in self.enemies]
        for atk, tgt in pairs:
            if atk.state != 'attack': continue
            idx = atk.frame_index(self.timing)
            at = ATTACKS[atk.attack_id]
            if idx >= at['slash_frame'] and not atk.slash_done:
                atk.slash_done = True
                if at.get('shoot'):                                         # bows: the arrow leaves the hand on this frame
                    self.shoot(atk, damage=at['damage'], knockback=at['knockback'], **at['shoot'])
                else:
                    if at['slash']: self.add_vfx(at['slash'], atk.x, atk.facing < 0, y=atk.y)   # (None: the sprite has its own trail)
                    self.events.append(('swing', atk.voice))
            if at.get('rehit') and idx >= at['rehit'] and not atk.rehit_done:
                atk.rehit_done = True; atk.hit_set = []                    # multi-hit moves (the spin) hit again here
            if tgt in atk.hit_set or idx not in at['active']: continue         # one hit per target per swing
            if tgt.state == 'dead' or (tgt.invuln > 0 and not at.get('ignore_invuln')): continue
            if abs(atk.y - tgt.y) > C.VERTICAL_REACH: continue          # too high / low for the swing to connect
            lo, hi = at['reach']
            a0, a1 = (atk.x + lo, atk.x + hi) if atk.facing > 0 else (atk.x - hi, atk.x - lo)
            if a0 <= tgt.x + tgt.hw and a1 >= tgt.x - tgt.hw:
                atk.hit_done = True; atk.hit_set.append(tgt); hits.append((atk, tgt))
        for atk, tgt in hits: self._hit(atk, tgt)          # applied together, so trades are possible

    def apply_damage(self, atk, tgt, amount):
        """The single funnel for damage: stats now, armor / guard / combo meter plug in here later."""
        amount = min(amount, tgt.hp + tgt.armor)
        absorbed = min(tgt.armor, amount)                     # armor soaks the blow first; what is left goes to life
        if absorbed:
            tgt.armor -= absorbed; amount -= absorbed
            self.events.append(('armor_break' if tgt.armor <= 0 else 'armor_hit', tgt.kind))
        tgt.hp -= amount
        total = absorbed + amount
        if tgt is self.hero: self.stats['damage_taken'] += total
        else: self.stats['damage_dealt'] += total
        if 'combo' in self.features and not (atk is self.hero and atk.attack_id == 'special' and atk.state == 'attack'):
            gain = total * (C.COMBO_GAIN_TAKEN if tgt is self.hero else C.COMBO_GAIN_DEALT)
            self.combo = min(C.COMBO_BAR_MAX, self.combo + gain)           # the special itself does not refill the bar
        return total

    def _hit(self, atk, tgt, at=None, src_x=None):
        """A connected blow. `at` = ATTACKS-like dict (damage, knockback); `src_x` = where it came from (a projectile
        or an area hit instead of the attacker's own position)."""
        at = at or ATTACKS[atk.attack_id]; sx = atk.x if src_x is None else src_x
        if (tgt.defn.get('guard') and tgt.state in ('idle', 'walk') and not at.get('guard_break')
                and (sx - tgt.x) * tgt.facing > 0):         # shield up and the blow comes from the front (T24)
            self.add_vfx('block_spark', tgt.x, tgt.facing < 0, y=tgt.y)
            self.events.append(('block', tgt.kind)); self.shake = C.SHAKE_TIME * 0.5
            tgt.kb_dir = 1 if tgt.x >= sx else -1; tgt.kb_t = C.KNOCKBACK_TIME; tgt.kb_speed = C.BLOCK_KNOCKBACK / C.KNOCKBACK_TIME
            return False
        self.apply_damage(atk, tgt, int(round(at['damage'] * atk.mods.get('damage', 1.0))))
        self.add_vfx('blood_splash', tgt.x, tgt.x > sx, y=tgt.y)
        self.shake = C.SHAKE_TIME
        self.events.append(('hit', tgt.voice))
        tgt.chain = None; tgt.combo_next = None                  # a hit breaks the combo
        tgt.token = False
        dirn = 1 if tgt.x >= sx else -1
        tgt.facing = -dirn                                   # turns toward the attacker, recoils backwards
        tgt.kb_dir = dirn; tgt.kb_t = C.KNOCKBACK_TIME; tgt.kb_speed = at['knockback'] / C.KNOCKBACK_TIME
        if tgt.hp <= 0:
            tgt.set_state('dead'); tgt.invuln = 999.0
            self.events.append(('death', tgt.voice))
            if tgt is not self.hero: self.stats['kills'] += 1
            if not tgt.is_hero: self._drop_loot(tgt.x, boss=bool(tgt.defn.get('boss'))); tgt.respawn_t = C.RESPAWN_DELAY
            self.add_vfx('spirit', tgt.x, tgt.x > sx, delay=C.SPIRIT_DELAY, y=tgt.y)
            if tgt is self.hero: self.hero_deaths += 1; self.hero_timer = C.RESPAWN_DELAY; self.combo = 0   # D2: dies with the hero
            else: self.ogre_deaths += 1
        else:
            self.events.append(('hurt', tgt.voice))
            tgt.set_state('hurt')
            if tgt is self.hero: tgt.invuln = tgt.duration(self.timing) + C.HURT_INVULN_EXTRA
            elif C.OGRE_HURT_INVULN: tgt.invuln = tgt.duration(self.timing) + C.OGRE_HURT_INVULN_EXTRA
            if not tgt.is_hero: tgt.ai_wait = None

    # ------------------------------------------------------------------ projectiles and areas (T04)
    def targets_of(self, owner):
        return [e for e in self.enemies] if owner.is_hero else [self.hero]

    def shoot(self, owner, kind='straight', sprite='arrow', damage=C.DAMAGE, **kw):
        """Fires a projectile from the owner's hand. For 'lob' pass nothing else: it is aimed at the hero's position."""
        x = owner.x + owner.facing * 14
        p = Projectile(kind, owner, x, owner.y, owner.facing, damage, sprite, **kw)
        if kind == 'lob':
            tgt = self.hero if not owner.is_hero else (self.ogre or self.hero)
            p.tx = tgt.x; p.ty = tgt.y
            p.facing = 1 if p.tx >= x else -1
        self.projectiles.append(p); self.events.append(('shoot', owner.voice))
        return p

    def add_area(self, owner, x0, x1, damage, delay=0.0, duration=0.1, **kw):
        a = AreaHit(owner, x0, x1, owner.y, damage, delay=delay, duration=duration, **kw)
        self.areas.append(a)
        if a.vfx: self.add_vfx(a.vfx, (x0 + x1) / 2, False, delay=delay, y=owner.y)
        return a

    def _projectiles(self, dt):
        for p in self.projectiles:
            p.t += dt
            targets = [t for t in self.targets_of(p.owner) if t.state != 'dead']
            if p.kind == 'straight':
                p.x += p.facing * p.speed * dt; p.height = p.chest
                for tgt in targets:
                    if tgt in p.hit_set or tgt.invuln > 0: continue
                    if abs(p.x - tgt.x) > tgt.hw + 3 or abs(p.base_y - tgt.y) > C.VERTICAL_REACH: continue
                    p.hit_set.append(tgt)
                    self._hit(p.owner, tgt, at=dict(damage=p.damage, knockback=p.knockback), src_x=p.x - p.facing * 8)
                    if not p.pierce: p.done = True; break
                if abs(p.x - p.x0) >= p.max_range: p.done = True
            else:                                                  # lob
                u = min(1.0, p.t / p.flight)
                p.x = p.x0 + (p.tx - p.x0) * u
                p.height = p.chest * (1 - u) + 4 * p.apex * u * (1 - u)
                if u >= 1.0:
                    p.done = True; self.events.append(('impact', 'lob'))
                    for tgt in targets:
                        if tgt.invuln > 0 or abs(tgt.x - p.tx) > p.radius + tgt.hw or abs(tgt.y - p.ty) > C.VERTICAL_REACH:
                            continue
                        self._hit(p.owner, tgt, at=dict(damage=p.damage, knockback=p.knockback), src_x=p.tx - p.facing * 4)
        self.projectiles = [p for p in self.projectiles if not p.done and abs(p.x - self.hero.x) < 900]

    def _areas(self, dt):
        for a in self.areas:
            a.t += dt
            if a.t < a.delay or a.t > a.delay + a.duration: continue
            for tgt in self.targets_of(a.owner):
                if tgt in a.hit_set or tgt.state == 'dead' or tgt.invuln > 0: continue
                if abs(a.base_y - tgt.y) > C.VERTICAL_REACH: continue
                if a.x0 <= tgt.x + tgt.hw and a.x1 >= tgt.x - tgt.hw:
                    a.hit_set.append(tgt)
                    self._hit(a.owner, tgt, at=dict(damage=a.damage, knockback=a.knockback), src_x=(a.x0 + a.x1) / 2)
        self.areas = [a for a in self.areas if a.t <= a.delay + a.duration]

    def drink_potion(self):
        """Key 1: spends one stored potion to heal. Does nothing with a full life bar, an empty pouch or a dead hero."""
        h = self.hero
        if self.potions <= 0 or h.state == 'dead' or h.hp >= h.max_hp: return False
        self.potions -= 1; self.heal(h, C.POTION_HEAL); self.events.append(('potion', h.voice))
        return True

    # ------------------------------------------------------------------ run state / revive (T37)
    def export_run(self):
        """What travels between stages (D6): gold, potions, weapon, armor."""
        h = self.hero
        return dict(gold=self.gold, potions=self.potions, weapon=dict(h.weapon) if h.weapon else None, armor=h.armor)

    def apply_run(self, run):
        h = self.hero
        self.gold = run.get('gold', 0); self.potions = run.get('potions', 0)
        h.weapon = dict(run['weapon']) if run.get('weapon') else None
        h.armor = min(h.armor_max, run.get('armor', 0))

    def can_revive(self): return self.defeated and self.gold >= C.REVIVE_COST

    def revive(self):
        """Paid revival (D1/D10): same spot, full life, a short invulnerability, combo meter empty; enemies, queue and
        encounters keep their state; potions / weapon / armor are kept; costs REVIVE_COST gold."""
        if not self.can_revive(): return False
        h = self.hero
        self.gold -= C.REVIVE_COST; self.stats['revives'] += 1
        h.hp = h.max_hp; h.set_state('idle'); h.invuln = C.REVIVE_INVULN; h.kb_t = 0.0
        self.combo = 0; self.defeated = False; self.hero_timer = None
        self.add_vfx('heal', h.x, h.facing < 0, y=h.y); self.events.append(('revive', h.voice))
        return True

    def start_attack(self, f, attack_id):
        f.attack_id = attack_id; f.set_state('attack'); f.chain = None
        if ATTACKS[attack_id]['cooldown']: f.cd[attack_id] = self.time + ATTACKS[attack_id]['cooldown']
        wear = ATTACKS[attack_id].get('wear', 0.0)
        if wear and f.weapon:                                  # every swing wears the held weapon down
            f.weapon['durability'] -= wear
            if f.weapon['durability'] <= 0:
                f.weapon = None; self.events.append(('break', f.kind)); self.shake = C.SHAKE_TIME

    def heal(self, f, amount):
        """Restores life (capped at max_hp) with the heal effect and sound. Any healing item should go through here."""
        f.hp = min(f.max_hp, f.hp + amount)
        self.add_vfx('heal', f.x, f.facing < 0, y=f.y)
        self.events.append(('heal', f.voice))

    def _drop_loot(self, x, boss=False):
        r = self.loot_rng; items = []
        if boss:                                                 # a boss always pays
            items = [Pickup('potion', 0, C.POTION_HEAL) for _ in range(C.BOSS_LOOT_POTIONS)]
            items.append(Pickup('coins', 0, r.randint(*C.BOSS_LOOT_COINS)))
            for i, p in enumerate(items): p.x = x + (i - (len(items) - 1) / 2) * 16; self.pickups.append(p)
            del self.pickups[:-C.PICKUP_MAX]
            return
        if r.random() < C.POTION_DROP_CHANCE: items.append(Pickup('potion', 0, C.POTION_HEAL))
        mult = self.diff['loot_mult'] if self.diff else 1.0          # later parts of a stage pay more (T36)
        if r.random() < C.COIN_BAG_DROP_CHANCE: items.append(Pickup('coins', 0, int(round(r.randint(*C.COIN_BAG_COINS) * mult))))
        if r.random() < C.AXE_DROP_CHANCE: items.append(Pickup('weapon', 0, C.WEAPON_DURABILITY, 'axe'))
        if r.random() < C.ARMOR_DROP_CHANCE: items.append(Pickup('armor', 0, C.ARMOR_PICKUP))
        if r.random() < C.BOW_DROP_CHANCE: items.append(Pickup('weapon', 0, C.WEAPON_DURABILITY, 'bow'))
        if r.random() < C.XBOW_DROP_CHANCE: items.append(Pickup('weapon', 0, C.WEAPON_DURABILITY, 'xbow'))
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
                    and not (p.kind == 'potion' and self.potions >= C.POTION_MAX_STOCK)    # full pouch: stays on the floor
                    and not (p.kind == 'armor' and h.armor >= h.armor_max)):               # full armor: not wasted
                if p.kind == 'potion': self.potions += 1                  # stored; drinking is a key press (T10)
                elif p.kind == 'armor':
                    h.armor = min(h.armor_max, max(h.armor, p.amount)); self.add_vfx('coin_glint', h.x, h.facing < 0, y=h.y)
                elif p.kind == 'weapon':                                 # replaces whatever the hero holds (T13)
                    h.weapon = dict(id=p.item, durability=p.amount); self.add_vfx('coin_glint', h.x, h.facing < 0, y=h.y)
                else:
                    self.gold += p.amount; self.stats['gold_gained'] += p.amount; self.add_vfx('coin_glint', h.x, h.facing < 0, y=h.y)
                self.events.append(('pickup', p.kind)); continue
            keep.append(p)
        self.pickups = keep

    def _timeouts(self):
        for f in self.fighters():
            if f.state in ('attack', 'hurt') and f.t >= f.duration(self.timing):
                was_attack = f.state == 'attack'
                nxt = ATTACKS[f.attack_id].get('next') if was_attack else None; queued = f.combo_next
                f.set_state('idle')
                if f.is_hero and was_attack and nxt:
                    if queued: self.start_attack(f, queued); continue              # chained: no gap between strokes
                    f.chain = (self.time, nxt)                                       # a click in the next 0.15 s still chains
                f.token = False
                if (not f.is_hero and was_attack and nxt and f.defn.get('chain_chance')
                        and self.rng.random() < f.defn['chain_chance']):
                    self.start_attack(f, nxt); continue                  # enemies with a combo (black knight)
                if not f.is_hero:
                    if was_attack: f.ai_cooldown = self.rng.uniform(*f.ai_p['cooldown'])
                    else: f.ai_cooldown = 0.0; f.ai_wait = self.rng.uniform(*f.ai_p['retaliate'])

    def _stage(self, dt):
        """Stage rules (T30/T36): path bounds, encounters that fire when the hero crosses their line (their enemies
        wait in a queue and enter from the right edge while fewer than max_alive are alive), end of the stage."""
        st = self.stage
        if st is None: return
        h = self.hero
        lo, hi = (0.0, st.length) if self.arena is None else (self.arena[0] + C.ARENA_WALL_MARGIN, self.arena[1] - C.ARENA_RIGHT_WALL)
        if h.state != 'dead': h.x = max(lo, min(hi, h.x))
        self.diff = d = st.difficulty(st.progress(h.x))
        self.max_attackers = d['max_attackers']
        while self.next_enc < len(st.encounters) and h.x >= st.trigger_x(st.encounters[self.next_enc]):
            self.queue.extend(st.encounters[self.next_enc]['enemies']); self.next_enc += 1
        alive = sum(1 for e in self.enemies if e.state != 'dead')
        if st.boss and self.boss is None and not self.boss_dead and self.next_enc >= len(st.encounters) and not self.queue:
            gate = st.length - C.SCREEN_W + C.ARENA_ENTER_MARGIN                # the last screen of the path is the arena
            if h.x >= gate and h.state != 'dead': self._start_arena()
        if self.boss is not None and self.boss.state == 'dead' and not self.boss_dead:
            self.boss_dead = True; self.events.append(('boss_dead', self.boss.kind))
            old = self.cam_x(); self.arena = None; self.cam_off = old - self._cam_base()   # the screen is released
        while self.queue and alive < d['max_alive'] and self.arena is None:
            kind, elite = self.queue.pop(0)
            if elite is None and d['elite_frac'] > 0 and self.spawn_rng.random() < d['elite_frac']:
                elite = self.spawn_rng.choice(sorted(ELITE_MODS))
            x = self.cam_x() + C.SCREEN_W + C.OGRE_SPAWN_MARGIN + (alive % 3) * C.ENCOUNTER_SPACING
            e = Fighter(kind, x, -1, elite=elite); e.ai_cooldown = 0.6
            self.enemies.append(e); self.events.append(('spawn', kind)); alive += 1
        if (not self.stage_clear and self.next_enc >= len(st.encounters) and not self.queue and h.state != 'dead'
                and (not st.boss or self.boss_dead)
                and not any(e.state != 'dead' for e in self.enemies) and h.x >= st.length - C.STAGE_FINISH_DIST):
            self.stage_clear = True; self.events.append(('stage_clear', h.voice))

    def _start_arena(self):
        """The boss fight: the last screen of the path closes (camera eases to it), the boss walks in from the right."""
        st = self.stage; old = self.cam_x()
        self.arena = (st.length - C.SCREEN_W, st.length)
        self.cam_off = old - self._cam_base()
        b = Fighter(st.boss, self.arena[1] - 30, -1); b.ai_cooldown = 1.0
        self.enemies.append(b); self.boss = b; self.events.append(('boss_start', st.boss))

    def _summon(self, boss):
        """Reinforcements around a boss that crossed half of its life (once)."""
        lo = self.arena[0] + 40 if self.arena else boss.x - 200
        hi = self.arena[1] - 40 if self.arena else boss.x + 200
        for i, kind in enumerate(boss.defn['summon']):
            x = max(lo, min(hi, boss.x + (-1 if i % 2 == 0 else 1) * (70 + 30 * (i // 2))))
            e = Fighter(kind, x, boss.facing); e.ai_cooldown = 0.8
            self.enemies.append(e); self.events.append(('spawn', kind))
        self.events.append(('summon', boss.kind))

    def _respawns(self, dt):
        if self.hero_timer is not None:
            self.hero_timer -= dt
            if self.hero_timer <= 0 and self.stage is not None:      # in a stage death is final: the defeat screen decides
                self.hero_timer = None; self.defeated = True
            elif self.hero_timer <= 0:
                self.hero_timer = None; old_cam = self.cam_x(); self.bury(self.hero)
                nx = old_cam + C.HERO_SPAWN_MARGIN
                self.hero = Fighter(self.hero.kind, nx, +1, invuln=C.SPAWN_INVULN)
                self.cam_off = old_cam - (nx - C.SCREEN_W / 2)      # camera keeps its place, then glides
                self.events.append(('spawn', self.hero.voice))
        for e in list(self.enemies):                       # bury the dead after RESPAWN_DELAY
            if e.respawn_t is not None:
                e.respawn_t -= dt
                if e.respawn_t <= 0: self.bury(e); self.enemies.remove(e)
        quota = 0 if self.stage is not None else max(self.spawn_target, min(1 + self.ogre_deaths // C.ENDLESS_CROWD_EVERY, C.ENDLESS_CROWD_MAX))
        while len(self.enemies) < quota:                   # endless mode: keep the quota filled, entering from the right
            kind, elite = self._draw_enemy()
            e = Fighter(kind, self.cam_x() + C.SCREEN_W + C.OGRE_SPAWN_MARGIN, -1, elite=elite)
            e.ai_cooldown = 0.6; self.enemies.append(e); self.events.append(('spawn', kind))


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


def slot_props(slot, seed=7, theme='village'):
    """Scenery of one world slot: a list of (prop name, world x). Deterministic, so the world is 'infinite'.
    The table of what may appear comes from THEMES[theme] (T33); 'village' reproduces the original draw exactly."""
    r = random.Random(slot * 7919 + seed); x0 = slot * C.SLOT_W; out = []
    t = THEMES[theme]
    table = t['props_even'] if slot % 2 == 0 else t['props_odd']
    v = r.random(); acc = 0.0
    for name, p in table:
        acc += p
        if v < acc:
            a, b = PROP_PLACE[name]
            out.append((name, x0 + r.randint(a, C.SLOT_W - b))); break
    return out
