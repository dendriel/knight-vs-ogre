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
DAMAGE = 10                        # damage of every hit (both sides)
HERO_SPEED = 120.0                 # pixels per second (was 84)
OGRE_SPEED = 50.0
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
KNIGHT_ATTACK_ANIM_SPEED = 2.0     # knight sword swing AND its slash effect (they must stay in sync)
WALK_ANIM_SPEED = 1.2              # ogre walk cycle; keep it proportional to OGRE_SPEED so the feet don't slide
RUN_ANIM_SPEED = 1.65              # the hero's movement uses the 'run' cycle (~72 px/s per 1.0x), proportional to HERO_SPEED
ANIM_SPEED = {
    'knight': {'attack_sword': KNIGHT_ATTACK_ANIM_SPEED, 'attack_axe': KNIGHT_ATTACK_ANIM_SPEED, 'run': RUN_ANIM_SPEED,
               'jump_up': 1.6},
    'ogre': {'attack': ATTACK_ANIM_SPEED, 'walk': WALK_ANIM_SPEED},
    'vfx': {'sword_slash': KNIGHT_ATTACK_ANIM_SPEED, 'axe_slash': ATTACK_ANIM_SPEED},
}
HURT_INVULN_EXTRA = 0.6            # extra invulnerable seconds after the hurt animation (prevents stun-lock)
OGRE_HURT_INVULN = True            # True: the ogre cannot be hit again during hurt + OGRE_HURT_INVULN_EXTRA
OGRE_HURT_INVULN_EXTRA = 0.4       # extra invulnerable seconds for the ogre only (hero uses HURT_INVULN_EXTRA)
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
POTION_DROP_CHANCE = 0.30          # chance that a dying ogre drops a potion
COIN_BAG_DROP_CHANCE = 0.50        # chance that a dying ogre drops a bag of gold (rolled separately from the potion)
COIN_BAG_COINS = (5, 10)           # coins in a bag (inclusive range)
PICKUP_RADIUS = 14                 # horizontal distance (px) at which the hero picks an item up
PICKUP_REACH_Y = 24                # vertical tolerance (px) between the hero's feet and the item
PICKUP_MAX = 30                    # items kept in the world (oldest vanish)

# ---- projectiles / areas ------------------------------------------------------------------
PROJ_CHEST = 28                    # height (px above the shooter's feet) at which a shot leaves the hand
ARROW_SPEED = 260.0                # px/s of a straight shot
ARROW_RANGE = 280.0                # max distance of a straight shot
LOB_FLIGHT = 0.95                  # seconds a lobbed shot stays in the air
LOB_APEX = 70.0                    # extra height (px) of the top of the arc
LOB_RADIUS = 12.0                  # landing zone half-width (px), plus the target's own half width

# ---- HUD (positions of the fixed parts; the slots below the life bar stack automatically) --------
HUD = dict(name=(10, 6), hp_bar=(10, 20), hp_num=(156, 18))
COMBO_BAR_MAX = 100                # points of damage (dealt + taken, weighted) that fill the combo meter (T12)
POTION_MAX_STOCK = 10              # potions the hero can carry (T10)

# ---- ogre AI ------------------------------------------------------------------------------
OGRE_ATTACK_DIST = 38              # distance at which the ogre stops walking and prepares to attack
OGRE_WAIT_BEFORE_ATTACK = (0.35, 0.65)   # random pause (seconds) before each swing: the player's window
OGRE_PATIENCE_DIST = 22            # if the hero steps back less than this, the ogre keeps its attack plan
OGRE_COOLDOWN = (0.8, 1.3)         # random rest (seconds) after a swing
OGRE_RETALIATE_WAIT = (0.15, 0.35) # shorter pause when the ogre has just recovered from a hit

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
    ('Mouse esquerdo', 'Atacar (segurar repete)'),
    ('1', 'Beber poção'),
    ('M', 'Liga / desliga o som'),
    ('F11', 'Tela cheia'),
    ('Esc', 'Menu'),
]
