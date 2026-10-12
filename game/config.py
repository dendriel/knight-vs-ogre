"""Tunable game settings. Change the numbers here to adjust difficulty and feel."""

# ---- screen -------------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 480, 270      # internal resolution (pixel art), scaled up by an integer factor
DEFAULT_SCALE = 3                  # window opens at 1440x810
FPS = 60
GROUND_Y = 217                     # screen row where the feet touch the ground
ANCHOR_X = 30                      # hip column inside a 64x64 frame (30 normal, 33 when mirrored)
ANCHOR_X_FLIP = 33

# ---- fighters -----------------------------------------------------------------------------
HERO_MAX_HP = 100
OGRE_MAX_HP = 30                   # 3 hits
MAX_HP = HERO_MAX_HP               # (kept for old code/tests)
CAPTAIN_MAX_HP = 90                # 3x an ogre
CAPTAIN_SPEED = 44.0
CAPTAIN_DAMAGE = 15                # a wide slam
CAPTAIN_REACH = (-20, 92)
MINO_LORD_MAX_HP = 120
MINO_LORD_SPEED = 66.0
MINO_LORD_DAMAGE = 15
BLACK_KNIGHT_MAX_HP = 110
BLACK_KNIGHT_SPEED = 54.0
BLACK_KNIGHT_DAMAGE = (10, 10, 15) # his own three-stroke combo
BOSS_SUMMON_AT = 0.5               # fraction of life at which a boss calls reinforcements (once)
CAPTAIN_MAX_HP = 90                # 3x an ogre
CAPTAIN_SPEED = 44.0
CAPTAIN_DAMAGE = 15                # a wide slam
CAPTAIN_REACH = (-20, 92)
MINO_LORD_MAX_HP = 120
MINO_LORD_SPEED = 66.0
MINO_LORD_DAMAGE = 15
BLACK_KNIGHT_MAX_HP = 110
BLACK_KNIGHT_SPEED = 54.0
BLACK_KNIGHT_DAMAGE = (10, 10, 15) # his own three-stroke combo
BOSS_SUMMON_AT = 0.5               # fraction of life at which a boss calls reinforcements (once)
ORC_MAX_HP = 40                    # 4 strokes: an ogre with more teeth
ORC_SPEED = 56.0
ORC_WAIT = (0.3, 0.55)
ORC_COOLDOWN = (0.8, 1.2)
GOBLIN_MAX_HP = 10                 # one stroke; they come in bands
GOBLIN_SPEED = 70.0
GOBLIN_DAMAGE = 5
GOBLIN_REACH = (-8, 28)
GOBLIN_ATTACK_DIST = 24
GOBLIN_WAIT = (0.15, 0.3)
GOBLIN_COOLDOWN = (0.5, 0.9)
KOBOLD_MAX_HP = 12
KOBOLD_SPEED = 54.0
KOBOLD_DAMAGE = 5                  # a thrown rock
KOBOLD_KEEP_DIST = 130
KOBOLD_TOO_CLOSE = 80
KOBOLD_WAIT = (0.35, 0.6)
KOBOLD_COOLDOWN = (1.3, 2.0)
MINOTAUR_MAX_HP = 50
MINOTAUR_SPEED = 58.0
MINOTAUR_DAMAGE = 15               # the axe
MINOTAUR_CHARGE_MIN = 70           # it charges when the hero is between these distances (px)...
MINOTAUR_CHARGE_MAX = 200
MINOTAUR_TELEGRAPH = 0.7           # ...after this long pose with the axe raised (the player's warning)
MINOTAUR_DASH_SPEED = 240.0
MINOTAUR_DASH_TIME = 0.6           # seconds (about 144 px); he stops, tired, and rests
MINOTAUR_DASH_DAMAGE = 15          # a jump over it (hero feet higher than VERTICAL_REACH) dodges the charge
MINOTAUR_DASH_KNOCKBACK = 34.0
MINOTAUR_CHARGE_COOLDOWN = 4.0
MINOTAUR_REST = 1.0
SHIELDMAN_MAX_HP = 30              # as sturdy as an ogre, but only open from behind / to heavy blows
SHIELDMAN_SPEED = 46.0
SHIELDMAN_WAIT = (0.5, 0.9)
SHIELDMAN_COOLDOWN = (1.0, 1.6)
SHIELD_TURN_DELAY = 0.5            # seconds it takes to turn the shield towards a hero who went round it
BLOCK_KNOCKBACK = 8.0              # px the shield pushes the attacker's blow back (the defender slides)
ARCHER_MAX_HP = 15                 # fragile
ARCHER_SPEED = 48.0
ARCHER_KEEP_DIST = 170             # it tries to stay about this far from the hero
ARCHER_TOO_CLOSE = 110             # closer than this and it backs away
ARCHER_WAIT = (0.45, 0.8)          # aiming pause before the shot (the arrow lands 0.95 s later)
ARCHER_COOLDOWN = (1.6, 2.4)       # rest between shots
SPEARMAN_MAX_HP = 25               # 3 sword strokes
SPEARMAN_SPEED = 52.0
SPEARMAN_REACH = (18, 62)          # reach from 18 to 62 px: the start is the DEAD ZONE, too close and it misses
SPEARMAN_ATTACK_DIST = 56          # stops here to thrust (the ogre stops at 38)
SPEARMAN_RETREAT_DIST = 24         # hero closer than this: the spearman steps back to regain space
SPEARMAN_WAIT = (0.4, 0.7)
SPEARMAN_COOLDOWN = (1.0, 1.5)
SOLDIER_MAX_HP = 20                # 2 sword strokes
SOLDIER_SPEED = 62.0               # faster than the ogre (50)
SOLDIER_WAIT = (0.25, 0.5)         # shorter window than the ogre's: it is the quick enemy
SOLDIER_COOLDOWN = (0.7, 1.1)
DAMAGE = 10                        # damage of every hit (both sides)
HERO_SPEED = 120.0                 # pixels per second (was 84)
OGRE_SPEED = 50.0
MAGE_SPEED = 115.0                 # a little slower than the knight
CROSSBOWMAN_SPEED = 105.0           # heavy armour: the slowest class
RANGER_SPEED = 135.0               # the ranger is quicker than the knight (120); see the classes block below
ATTACK_MOVE_FACTOR = 1.0           # hero speed multiplier while the attack animation plays (he can move and swing)

# ---- jump / boxes -------------------------------------------------------------------------
JUMP_HEIGHT = 44.0                 # pixels the hero rises: about his own height (45 px)
JUMP_RISE_TIME = 0.34              # seconds from take-off to the top of the jump (gravity is derived from the two)
BOX_W = 24                         # box cell size in the world (sprite is 24x24; stacked boxes share the outline row)
BOX_H = 23                         # half the knight's height: the top of a box is this high (23 px per level)
BOX_EDGE = 3                       # the hero's hip may hang this far past a box edge and still stand on it
VERTICAL_REACH = 30                # a swing only connects if both fighters' feet are within this height difference

# animation speed multipliers, applied on top of the fps stored in the sprite atlases (.json stays untouched)
ATTACK_ANIM_SPEED = 1.5            # ogre axe swing AND its slash effect (they must stay in sync)
KNIGHT_ATTACK_ANIM_SPEED = 1.7     # knight sword stroke 1 AND its slash effect (they must stay in sync); slower than the chained ones
KNIGHT_COMBO2_ANIM_SPEED = 2.4     # combo stroke 2 (rising cut) AND sword_slash_2
KNIGHT_COMBO3_ANIM_SPEED = 2.6     # combo stroke 3 (overhead chop) AND sword_slash_3
SPECIAL_ANIM_SPEED = 1.5           # spin animation AND its ring effect (they must stay in sync)
BOW_ANIM_SPEED = 1.3               # picked-up bow: draw and release
XBOW_ANIM_SPEED = 1.0              # picked-up crossbow: slower aim
AXE_ANIM_SPEED = 1.26              # picked-up axe: 1.35x slower than stroke 1 (KNIGHT_ATTACK_ANIM_SPEED / 1.35)
COMBO_WINDOW_START = 3             # a new click chains the next stroke from this frame of the current one...
COMBO_BUFFER = 0.15                # ...until this many seconds after it ended
COMBO_DAMAGE = (10, 10, 15)        # damage of strokes 1, 2, 3
COMBO_KNOCKBACK = (8.0, 8.0, 24.0)   # strokes 1-2 barely push (the next one must still connect); the finisher shoves
WALK_ANIM_SPEED = 1.2              # ogre walk cycle; keep it proportional to OGRE_SPEED so the feet don't slide
RUN_ANIM_SPEED = 1.65              # the hero's movement uses the 'run' cycle (~72 px/s per 1.0x), proportional to HERO_SPEED
SHIELD_WALK_ANIM_SPEED = 1.1
ORC_WALK_ANIM_SPEED = 1.35           # proportional to the move speeds below (ogre: 1.2 at 50 px/s)
GOBLIN_WALK_ANIM_SPEED = 2.8
KOBOLD_WALK_ANIM_SPEED = 2.0
MINOTAUR_WALK_ANIM_SPEED = 1.5
CAPTAIN_ATTACK_ANIM_SPEED = 1.1      # the ogre captain's slam is slow and heavy (row fps 10)
BOSS_WALK_ANIM_SPEED = 1.1
CAPTAIN_ATTACK_ANIM_SPEED = 1.1      # the ogre captain's slam is slow and heavy (row fps 10)
BOSS_WALK_ANIM_SPEED = 1.1
ARCHER_WALK_ANIM_SPEED = 1.2
ARCHER_ATTACK_ANIM_SPEED = 1.1        # draw and release (row fps 10): the arrow leaves on frame 4
SPEAR_WALK_ANIM_SPEED = 1.25         # spearman walk cycle, proportional to SPEARMAN_SPEED (52)
SPEAR_ATTACK_ANIM_SPEED = 1.3        # slow, telegraphed thrust (row fps 12)
SOLDIER_WALK_ANIM_SPEED = 1.55      # soldier walk cycle, proportional to SOLDIER_SPEED (62)
SOLDIER_ATTACK_ANIM_SPEED = KNIGHT_ATTACK_ANIM_SPEED   # same sword stroke as the hero's stroke 1 AND its slash effect
ANIM_SPEED = {
    'mage': {'attack_staff': 1.2, 'attack_staff_2': 1.8, 'attack_staff_3': 1.3, 'attack_stomp': 1.4, 'attack_special': 1.1,
             'run': RUN_ANIM_SPEED * MAGE_SPEED / HERO_SPEED, 'jump_up': 1.6},
    'crossbowman': {'attack_crossbow': 0.9, 'attack_crossbow_2': 1.5, 'attack_crossbow_3': 1.2, 'attack_axe_small': 1.6,
                    'attack_special': 1.0, 'run': RUN_ANIM_SPEED * CROSSBOWMAN_SPEED / HERO_SPEED, 'jump_up': 1.6},
    'ranger': {'attack_bow': 1.1, 'attack_bow_2': 1.7, 'attack_bow_3': 1.3, 'attack_short': 2.0, 'attack_special': 1.1,
               'run': RUN_ANIM_SPEED * RANGER_SPEED / HERO_SPEED, 'jump_up': 1.6},
    'ranger': {'attack_bow': 1.1, 'attack_bow_2': 1.7, 'attack_bow_3': 1.3, 'attack_short': 2.0, 'attack_special': 1.1,
               'run': RUN_ANIM_SPEED * RANGER_SPEED / HERO_SPEED, 'jump_up': 1.6},
    'knight': {'throw': 1.5, 'attack_special': SPECIAL_ANIM_SPEED, 'attack_sword': KNIGHT_ATTACK_ANIM_SPEED, 'attack_sword_2': KNIGHT_COMBO2_ANIM_SPEED,
               'attack_sword_3': KNIGHT_COMBO3_ANIM_SPEED, 'attack_axe': AXE_ANIM_SPEED,
               'attack_bow': BOW_ANIM_SPEED, 'attack_crossbow': XBOW_ANIM_SPEED,
               'run': RUN_ANIM_SPEED, 'jump_up': 1.6},
    'ogre': {'attack': ATTACK_ANIM_SPEED, 'walk': WALK_ANIM_SPEED},
    'soldier': {'attack': SOLDIER_ATTACK_ANIM_SPEED, 'walk': SOLDIER_WALK_ANIM_SPEED},
    'spearman': {'attack': SPEAR_ATTACK_ANIM_SPEED, 'walk': SPEAR_WALK_ANIM_SPEED},
    'archer': {'attack': ARCHER_ATTACK_ANIM_SPEED, 'walk': ARCHER_WALK_ANIM_SPEED},
    'shieldman': {'attack': SOLDIER_ATTACK_ANIM_SPEED, 'walk': SHIELD_WALK_ANIM_SPEED},
    'orc': {'attack': ATTACK_ANIM_SPEED, 'walk': ORC_WALK_ANIM_SPEED},
    'ogre_captain': {'attack': CAPTAIN_ATTACK_ANIM_SPEED, 'walk': BOSS_WALK_ANIM_SPEED},
    'minotaur_lord': {'attack': 1.4, 'walk': 1.6},
    'black_knight': {'attack': 1.6, 'attack_2': 2.2, 'attack_3': 2.4, 'walk': 1.25},
    'ogre_captain': {'attack': CAPTAIN_ATTACK_ANIM_SPEED, 'walk': BOSS_WALK_ANIM_SPEED},
    'minotaur_lord': {'attack': 1.4, 'walk': 1.6},
    'black_knight': {'attack': 1.6, 'attack_2': 2.2, 'attack_3': 2.4, 'walk': 1.25},
    'goblin': {'attack': 1.8, 'walk': GOBLIN_WALK_ANIM_SPEED},
    'kobold': {'attack': 1.3, 'walk': KOBOLD_WALK_ANIM_SPEED},
    'minotaur': {'attack': 1.35, 'walk': MINOTAUR_WALK_ANIM_SPEED},
    'vfx': {'sword_slash': KNIGHT_ATTACK_ANIM_SPEED, 'sword_slash_2': KNIGHT_COMBO2_ANIM_SPEED,
            'sword_slash_3': KNIGHT_COMBO3_ANIM_SPEED, 'axe_slash': ATTACK_ANIM_SPEED,
            'spin_slash': SPECIAL_ANIM_SPEED},
}
HURT_INVULN_EXTRA = 0.6            # extra invulnerable seconds after the hurt animation (prevents stun-lock)
OGRE_HURT_INVULN = True            # True: the ogre cannot be hit again during hurt + OGRE_HURT_INVULN_EXTRA
OGRE_HURT_INVULN_EXTRA = 0.15      # extra invulnerable seconds for enemies only (was 0.4); the next stroke of a combo ignores it
SPAWN_INVULN = 1.0                 # a freshly spawned hero cannot be hit during this time
KNOCKBACK = 14.0                   # pixels the victim is pushed back
KNOCKBACK_TIME = 0.25

# attack reach: interval in front of the attacker's hip (pixels), and which frames can hit
KNIGHT_REACH = (-12, 40)           # negative start: a target overlapping the attacker (no body collision) is still hit
OGRE_REACH = (-12, 44)
ACTIVE_FRAMES = (3, 4)             # the swing frames of both attack animations
HALF_WIDTH = {'knight': 8, 'ogre': 10}

# ---- pickups (dropped by ogres, only the hero can collect them) ---------------------------
POTION_HEAL = 30                   # hp restored by a red potion (never above HERO_MAX_HP)
POTION_DROP_CHANCE = 0.12          # chance that a dying enemy drops a potion (was 0.30: too many)
COIN_BAG_DROP_CHANCE = 0.50        # chance that a dying ogre drops a bag of gold (rolled separately from the potion)
COIN_BAG_COINS = (5, 10)           # coins in a bag (inclusive range)
PICKUP_RADIUS = 14                 # horizontal distance (px) at which the hero picks an item up
PICKUP_REACH_Y = 24                # vertical tolerance (px) between the hero's feet and the item
PICKUP_MAX = 30                    # items kept in the world (oldest vanish)

# ---- weapons picked up from the floor (T13) -------------------------------------------------
AXE_DROP_CHANCE = 0.15             # chance that a dying ogre drops its axe (separate roll)
AXE_DAMAGE = 20                    # the hero's axe hits twice as hard as the sword stroke...
AXE_REACH = (-12, 48)              # ...reaches 8 px further...
AXE_KNOCKBACK = 24.0
AXE_MOVE_FACTOR = 0.8              # walking speed multiplier while the heavy swing plays
AXE_WEAR = 3.0                     # durability (percent) lost per swing; at 0 the weapon breaks
WEAPON_DURABILITY = 30.0           # weapons wear out at 30% of the old 100 (durability in percent points)

# bow and crossbow pickups (T14): same pickup / durability rules as the axe, but the strike is a shot
BOW_DROP_CHANCE = 0.06             # rare drops (separate rolls)
XBOW_DROP_CHANCE = 0.04
BOW_DAMAGE = 10                    # an arrow = one sword stroke, from a distance
BOW_SPEED = 260.0                  # px/s
BOW_RANGE = 280.0                  # px
BOW_WEAR = 2.5                     # durability (percent) per shot
BOW_MOVE_FACTOR = 0.5
XBOW_DAMAGE = 20                   # the crossbow hits harder, reaches further, but needs a reload
XBOW_SPEED = 360.0
XBOW_RANGE = 380.0
XBOW_WEAR = 4.0
XBOW_RELOAD = 0.8                  # seconds before the next shot can start
XBOW_MOVE_FACTOR = 0.4

# ---- secondary attack of the knight: a thrown knife (T41) --------------------------------------
KNIFE_DAMAGE = 8
KNIFE_SPEED = 340.0
KNIFE_RANGE = 300.0
KNIFE_COOLDOWN = 1.0               # infinite uses, limited only by the recharge (D3)
KNIFE_MOVE_FACTOR = 0.7

# ---- classes (T42-T44) --------------------------------------------------------------------
RANGER_MAX_HP = 80                 # fragile and quick
RANGER_JUMP = 1.1
RANGER_ARROW_DAMAGE = (8, 8, 14)   # the 3rd arrow of the chain is the strong, piercing one
RANGER_ARROW_SPEED = (300.0, 320.0, 360.0)
RANGER_ARROW_RANGE = 300.0
RANGER_SHORT_DAMAGE = 10           # secondary: a short sword slash
RANGER_SHORT_REACH = (-10, 32)
RANGER_SHORT_COOLDOWN = 0.45
RAIN_DAMAGE = 8                    # special: arrows falling over an area in front of the ranger
RAIN_COUNT = 10
RAIN_SPAN = (60, 230)              # px in front of the ranger covered by the rain
RAIN_FALL_TIME = 0.55
RAIN_RADIUS = 16

# ---- classes (T42-T44) --------------------------------------------------------------------
RANGER_MAX_HP = 80                 # fragile and quick
RANGER_SPEED = 135.0
RANGER_JUMP = 1.1
RANGER_ARROW_DAMAGE = (8, 8, 14)   # the 3rd arrow of the chain is the strong, piercing one
RANGER_ARROW_SPEED = (300.0, 320.0, 360.0)
RANGER_ARROW_RANGE = 300.0
RANGER_SHORT_DAMAGE = 10           # secondary: a short sword slash
RANGER_SHORT_REACH = (-10, 32)
RANGER_SHORT_COOLDOWN = 0.45
RAIN_DAMAGE = 8                    # special: arrows falling over an area in front of the ranger
RAIN_COUNT = 10
RAIN_SPAN = (60, 230)              # px in front of the ranger covered by the rain
RAIN_FALL_TIME = 0.55
RAIN_RADIUS = 16

MAGE_MAX_HP = 70                   # the most fragile class
FIREBALL_DAMAGE = (12, 12, 16)     # the 3rd fireball is bigger and explodes
FIREBALL_SPEED = (210.0, 240.0, 200.0)
FIREBALL_RANGE = 300.0
FIREBALL_EXPLOSION = (36, 10)      # radius (px) and damage of the 3rd fireball's explosion (everyone nearby, once)
SPIKES_DAMAGE = 14                 # secondary: stone spikes erupting in front (area, several targets)
SPIKES_FROM_TO = (22, 104)
SPIKES_DELAY = 0.12
SPIKES_COOLDOWN = 1.4
STORM_COUNT = 12                   # special: a rain of fireballs around the mage
STORM_DAMAGE = 10
STORM_SPAN = 170                   # px each side of the mage
STORM_FALL_TIME = 0.6
STORM_RADIUS = 22
XBOWMAN_MAX_HP = 110
XBOWMAN_JUMP = 0.9
XBOW_HERO_DAMAGE = (14, 14, 22)    # chain of bolts: the 3rd is heavy and pierces
XBOW_HERO_SPEED = (360.0, 380.0, 430.0)
XBOW_HERO_RANGE = 380.0
XBOW_HERO_RELOAD = 0.8             # the chain cannot restart sooner than this after its first bolt
AXE_SMALL_DAMAGE = 12              # secondary: a small axe
AXE_SMALL_REACH = (-10, 38)
AXE_SMALL_COOLDOWN = 0.6
VOLLEY_COUNT = 6
VOLLEY_DAMAGE = 10

# ---- shop and consumables (T50, D8) -------------------------------------------------------
SHOP_PRICES = dict(potion=25, armor=60, axe=70, bow=80, xbow=100, bomb=30)
BOMB_MAX_STOCK = 5                 # throwable consumables (key 2): they are spent, unlike the infinite primary / secondary
BOMB_DAMAGE = 25                   # everyone in the landing radius
BOMB_RADIUS = 40
BOMB_RANGE = 150                   # where it lands when nobody is in front of the hero
BOMB_FLIGHT = 0.7
BOMB_COOLDOWN = 0.6

# ---- armor (T15) --------------------------------------------------------------------------
ARMOR_MAX = 50                     # armor points; damage is taken from them before the life bar
ARMOR_PICKUP = 50                  # a found armor piece restores the bar to this much (capped at ARMOR_MAX)
ARMOR_DROP_CHANCE = 0.10           # chance that a dying ogre drops armor (rare, separate roll)

# ---- projectiles / areas ------------------------------------------------------------------
PROJ_CHEST = 28                    # height (px above the shooter's feet) at which a shot leaves the hand
ARROW_SPEED = 260.0                # px/s of a straight shot
ARROW_RANGE = 280.0                # max distance of a straight shot
LOB_FLIGHT = 0.95                  # seconds a lobbed shot stays in the air
LOB_APEX = 70.0                    # extra height (px) of the top of the arc
LOB_RADIUS = 12.0                  # landing zone half-width (px), plus the target's own half width

# ---- HUD (positions of the fixed parts; the slots below the life bar stack automatically) --------
HUD = dict(name=(10, 6), hp_bar=(10, 20), hp_num=(156, 18))
COMBO_BAR_MAX = 100                # points (damage dealt / taken, weighted below) that fill the combo meter (T12)
COMBO_GAIN_DEALT = 1.5             # meter points per point of damage the hero deals
COMBO_GAIN_TAKEN = 1.0             # meter points per point of damage the hero takes
SPECIAL_HOLD_MIN = 0.25            # seconds the attack button must be held (with a full meter) to charge the special
SPECIAL_DAMAGE = 15                # per hit; the spin hits twice (30 = one whole ogre)
SPECIAL_RADIUS = 56                # px each side of the hero
SPECIAL_KNOCKBACK = 26.0
CHARGE_MOVE_FACTOR = 0.35          # walking speed multiplier while charging
POTION_MAX_STOCK = 3               # potions the hero can carry (T10; was 10)

# ---- ogre AI ------------------------------------------------------------------------------
OGRE_ATTACK_DIST = 38              # distance at which the ogre stops walking and prepares to attack
OGRE_WAIT_BEFORE_ATTACK = (0.35, 0.65)   # random pause (seconds) before each swing: the player's window
OGRE_PATIENCE_DIST = 22            # if the hero steps back less than this, the ogre keeps its attack plan
OGRE_COOLDOWN = (0.8, 1.3)         # random rest (seconds) after a swing
OGRE_RETALIATE_WAIT = (0.05, 0.18) # shorter pause when the ogre has just recovered from a hit (its strike must land inside its own invulnerable window, or button mashing becomes a stun-lock)

# ---- crowds (T26) -------------------------------------------------------------------------
MAX_ATTACKERS = 2                  # enemies allowed to prepare / throw a blow at the same time (the rest circle and wait)
STANDOFF_STEP = 8                  # px: each waiting enemy keeps this much more distance than the one closer to the hero
STANDOFF_BASE = 14                 # px beyond OGRE_ATTACK_DIST where the first waiting enemy stops

# ---- endless mode roster (the fight that never ends grows with the kill count) --------------------
# (kills needed, kind, weight): a new enemy is drawn among the kinds whose threshold has been reached
ENDLESS_ROSTER = [(0, 'ogre', 5), (2, 'soldier', 3), (4, 'goblin', 2), (5, 'spearman', 3), (7, 'archer', 2),
                  (8, 'shieldman', 2), (9, 'orc', 2), (10, 'kobold', 2), (12, 'minotaur', 1)]
ENDLESS_ELITE_FROM = 8             # kills from which new enemies may be elites...
ENDLESS_ELITE_CHANCE = 0.25        # ...with this chance
ENDLESS_CROWD_EVERY = 5            # one more simultaneous enemy every N kills (up to ENDLESS_CROWD_MAX)
ENDLESS_CROWD_MAX = 3

# ---- boss arena (T32) ---------------------------------------------------------------------
ARENA_ENTER_MARGIN = 30            # the arena (the last screen of the path) closes when the hero is this far into it
ARENA_WALL_MARGIN = 10             # px of wall at the left side of the arena
ARENA_RIGHT_WALL = 50              # ...and at the right: the exit line (STAGE_FINISH_DIST from the end) stays beyond the wall
BOSS_LOOT_POTIONS = 2              # a boss always drops this many potions...
BOSS_LOOT_COINS = (30, 50)         # ...and a bag with this much gold

# ---- boss arena (T32) ---------------------------------------------------------------------
ARENA_ENTER_MARGIN = 30            # the arena (the last screen of the path) closes when the hero is this far into it
ARENA_WALL_MARGIN = 10             # px of wall at the left side of the arena
ARENA_RIGHT_WALL = 50              # ...and at the right: the exit line (STAGE_FINISH_DIST from the end) stays beyond the wall
BOSS_LOOT_POTIONS = 2              # a boss always drops this many potions...
BOSS_LOOT_COINS = (30, 50)         # ...and a bag with this much gold

# ---- stages (T30) -------------------------------------------------------------------------
STAGE_END_MARGIN = 40              # px of scenery shown past the end of the path when the camera is locked at the end
STAGE_FINISH_DIST = 30             # the hero must be this close to the end line (and everything dead) to finish the stage
ENCOUNTER_SPACING = 30             # px between the enemies of one encounter as they enter

# ---- defeat (T37) -------------------------------------------------------------------------
REVIVE_COST = 100                  # gold to come back to life exactly where the hero fell
REVIVE_INVULN = 2.0                # seconds of invulnerability after reviving

# ---- spawning / camera --------------------------------------------------------------------
RESPAWN_DELAY = 1.6                # seconds between a death and the new fighter appearing
SPIRIT_DELAY = 0.45                # the spirit leaves the body this long after the death starts
HERO_SPAWN_MARGIN = 28             # new hero appears this many pixels from the left screen edge
OGRE_SPAWN_MARGIN = 20             # new ogre appears this many pixels beyond the right screen edge
START_HERO_SCREEN_X = 120          # at game start the hero is on the left and the camera glides to center
START_OGRE_OFFSET = 280            # ogre starts this far to the right of the hero (screen x = 400)
CAMERA_EASE = 4.0                  # how fast the camera recenters after a respawn
SHAKE_TIME = 0.12

# ---- audio --------------------------------------------------------------------------------
SFX_ENABLED = True
SFX_VOLUME = 0.7                   # master volume of the sound effects (0..1)
MUSIC_ENABLED = True
MUSIC_VOLUME = 0.35                # background loop (0..1), kept under the sound effects. M mutes everything in game
MUSIC_FILE = 'medieval_theme.wav'  # inside assets/music/

# ---- world --------------------------------------------------------------------------------
SLOT_W = 176                       # width of one scenery slot (house / tree / well / empty)

# ---- controls (the 'Ver comandos' screen reads this table; keep README in sync) ------------------
CONTROLS = [
    ('Setas / A D', 'Andar'),
    ('Espaço', 'Pular'),
    ('Mouse esquerdo', 'Atacar; clicar de novo = combo (3 golpes)'),
    ('Segurar mouse esq.', 'Barra cheia: carrega; soltar = giro especial'),
    ('1', 'Beber poção'),
    ('2', 'Arremessar bomba (da loja)'),
    ('E', 'Pegar arma / armadura do chao; de novo = soltar a arma'),
    ('Mouse direito', 'Ataque secundario (faca)'),
    ('M', 'Liga / desliga o som'),
    ('F11', 'Tela cheia'),
    ('Esc', 'Menu'),
]

# ---- fixes after the first play-test ---------------------------------------------------------
ENEMY_DAMAGE_MULT = 1.2            # every blow an enemy lands hurts 20% more (applied in World._hit)
COMBO_OPEN_TIME = 1.0              # seconds the victim of a combo stroke stays open to the NEXT stroke (ignores hurt invuln)
COMBO_LUNGE_SPEED = 90.0           # px/s a combo stroke (hero sword, black knight) drives the attacker forward...
LUNGE_RANGE = 70.0                 # ...while a foe is this close ahead (or nobody is: it just steps forward)...
LUNGE_STOP = 12.0                  # ...and stops this far from the foe so it never walks through him
