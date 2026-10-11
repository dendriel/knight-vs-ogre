"""Tunable game settings. Change the numbers here to adjust difficulty and feel."""

# ---- screen -------------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 480, 270      # internal resolution (pixel art), scaled up by an integer factor
DEFAULT_SCALE = 3                  # window opens at 1440x810
FPS = 60
GROUND_Y = 217                     # screen row where the feet touch the ground
ANCHOR_X = 30                      # hip column inside a 64x64 frame (30 normal, 33 when mirrored)
ANCHOR_X_FLIP = 33

# ---- fighters -----------------------------------------------------------------------------
MAX_HP = 100
DAMAGE = 10                        # damage of every hit (both sides)
HERO_SPEED = 84.0                  # pixels per second
OGRE_SPEED = 50.0

# animation speed multipliers, applied on top of the fps stored in the sprite atlases (.json stays untouched)
ATTACK_ANIM_SPEED = 1.5            # attack animations AND their slash effects (they must stay in sync)
WALK_ANIM_SPEED = 1.2              # walk cycle; keep it proportional to the speeds above so the feet don't slide
ANIM_SPEED = {
    'knight': {'attack_sword': ATTACK_ANIM_SPEED, 'attack_axe': ATTACK_ANIM_SPEED, 'walk': WALK_ANIM_SPEED},
    'ogre': {'attack': ATTACK_ANIM_SPEED, 'walk': WALK_ANIM_SPEED},
    'vfx': {'sword_slash': ATTACK_ANIM_SPEED, 'axe_slash': ATTACK_ANIM_SPEED},
}
HURT_INVULN_EXTRA = 0.6            # extra invulnerable seconds after the hurt animation (prevents stun-lock)
SPAWN_INVULN = 1.0                 # a freshly spawned hero cannot be hit during this time
KNOCKBACK = 14.0                   # pixels the victim is pushed back
KNOCKBACK_TIME = 0.25
MIN_SEPARATION = 22.0              # hero cannot walk through a living ogre

# attack reach: interval in front of the attacker's hip (pixels), and which frames can hit
KNIGHT_REACH = (4, 40)
OGRE_REACH = (8, 44)
ACTIVE_FRAMES = (3, 4)             # the swing frames of both attack animations
HALF_WIDTH = {'knight': 8, 'ogre': 10}

# ---- ogre AI ------------------------------------------------------------------------------
OGRE_ATTACK_DIST = 38              # distance at which the ogre stops walking and prepares to attack
OGRE_WAIT_BEFORE_ATTACK = (0.55, 0.95)   # random pause (seconds) before each swing: the player's window
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
