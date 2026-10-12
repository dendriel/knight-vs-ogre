"""Sound effects of Knight vs Ogre, synthesized from scratch. Run from the project root:

    python .claude/skills/game-audio-synthesis/scripts/sfx_gen.py            # writes assets/sfx/*.wav
    python .../sfx_gen.py --only hit_ogre --out some/dir                      # one sound, another folder

Every sound uses its own seeded RNG, so regenerating gives byte-identical files.
"""
import argparse, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth import *


def rng(name): return random.Random(name)


# ---- weapon swings (played when the swing frames start) -------------------------------------------------------
def sword_swing():
    r = rng('sword_swing')
    air = env_hump(highpass(lowpass(noise(0.20, r), 1500, 7000), 700), power=1.6, peak=0.35)
    shing = env_hump(tone(2600, 0.20, 4200, 'sine'), power=2.0, peak=0.3)
    return finish(mix([(air, 1.0, 0), (shing, 0.10, 0)]))


def axe_swing():
    r = rng('axe_swing')
    air = env_hump(lowpass(noise(0.30, r), 350, 3000), power=1.4, peak=0.45)
    body = env_hump(tone(110, 0.30, 55, 'saw'), power=1.5, peak=0.4)
    return finish(mix([(air, 1.0, 0), (lowpass(body, 400), 0.45, 0)]))


# ---- impacts (played when a blow lands, on top of the victim's voice) ----------------------------------------
def hit_knight():          # axe on armor: thud + metallic clank
    r = rng('hit_knight')
    thud = env_exp(tone(150, 0.25, 48, 'sine'), 0.07)
    crack = env_exp(lowpass(noise(0.10, r), 3500), 0.02)
    clank = mix([(env_exp(tone(1180, 0.25, shape='square', duty=.35), 0.05), 0.5, 0),
                 (env_exp(tone(1770, 0.25, shape='square', duty=.35), 0.04), 0.35, 0),
                 (env_exp(tone(2430, 0.25, shape='square', duty=.35), 0.03), 0.2, 0)])
    return finish(mix([(thud, 1.0, 0), (crack, 0.7, 0), (clank, 0.28, 0)]))


def hit_ogre():            # sword on thick hide: deep, meaty thud with a short slice on top
    r = rng('hit_ogre')
    thud = env_exp(tone(95, 0.30, 38, 'sine'), 0.09)
    flesh = env_exp(lowpass(noise(0.14, r), 1400, 500), 0.035)
    slice_ = env_exp(highpass(noise(0.08, r), 2500), 0.015)
    return finish(mix([(thud, 1.0, 0), (flesh, 0.8, 0), (slice_, 0.35, 0)]))


# ---- voices ----------------------------------------------------------------------------------------------------
def hurt_knight():         # short human grunt "hnh"
    r = rng('hurt_knight')
    voice = lowpass(tone(230, 0.20, 150, 'saw', vibrato=(18, 0.03)), 1400, 700)
    voice = env_exp(voice, 0.09, attack=0.008)
    breath = env_exp(lowpass(noise(0.2, r), 1800), 0.05)
    return finish(mix([(voice, 1.0, 0), (breath, 0.25, 0)]))


def hurt_ogre():           # low, rough growl
    r = rng('hurt_ogre')
    voice = tone(88, 0.38, 58, 'saw', vibrato=(11, 0.05))
    voice = drive(lowpass(voice, 900, 450), 3.0)
    voice = env_exp(voice, 0.17, attack=0.012)
    rasp = env_exp(lowpass(noise(0.38, r), 700), 0.12)
    return finish(mix([(voice, 1.0, 0), (rasp, 0.3, 0)]), peak=0.8)


def death_knight():        # falling cry, then the body hits the ground
    r = rng('death_knight')
    cry = lowpass(tone(300, 0.70, 70, 'saw', vibrato=(9, 0.04)), 1800, 350)
    cry = env_exp(cry, 0.32, attack=0.01)
    fall = mix([(env_exp(tone(90, 0.3, 40, 'sine'), 0.09), 1.0, 0),
                (env_exp(lowpass(noise(0.2, r), 1200), 0.04), 0.6, 0)])
    return finish(mix([(cry, 1.0, 0), (fall, 0.9, 0.62)]))


def death_ogre():          # long bellow, then a heavy collapse
    r = rng('death_ogre')
    roar = drive(lowpass(tone(120, 1.0, 32, 'saw', vibrato=(7, 0.06)), 1000, 200), 3.5)
    roar = env_exp(roar, 0.5, attack=0.02)
    rasp = env_exp(lowpass(noise(1.0, r), 900, 250), 0.35)
    fall = mix([(env_exp(tone(70, 0.5, 30, 'sine'), 0.14), 1.0, 0),
                (env_exp(lowpass(noise(0.3, r), 900), 0.07), 0.7, 0)])
    return finish(mix([(roar, 1.0, 0), (rasp, 0.3, 0), (fall, 1.1, 0.85)]))


# ---- spawns --------------------------------------------------------------------------------------------------
def spawn_hero():          # three quick rising chiptune blips
    parts = [(env_exp(tone(f, 0.12, shape='square', duty=.25), 0.07), 1.0, i * 0.07)
             for i, f in enumerate((392, 523, 784))]
    return finish(mix(parts), peak=0.4)   # square waves are loud: keep them under the rest


def spawn_ogre():          # low horn-like blast announcing the new enemy
    horn = drive(lowpass(tone(65, 0.55, 82, 'saw'), 700, 350), 2.0)
    horn = env_hump(horn, power=0.8, peak=0.25)
    return finish(horn, peak=0.55)


# ---- pickups ---------------------------------------------------------------------------------------------------
def coin_pickup():         # classic two-note "ding-ding" with a bright ring
    parts = [(env_exp(tone(f, 0.30, shape='square', duty=.5), 0.07), 1.0, d) for f, d in ((988, 0.0), (1319, 0.07))]
    ring = env_exp(tone(2637, 0.30, shape='sine'), 0.10)
    return finish(mix(parts + [(ring, 0.25, 0.07)]), peak=0.45)


def heal():                # soft rising shimmer: a major arpeggio of bells with a warm pad underneath
    notes = [523, 659, 784, 1047]
    bells = [(env_exp(mix([(tone(f, 0.55), 1.0, 0), (tone(f * 2, 0.55), 0.25, 0)]), 0.16, attack=0.01), 1.0, i * 0.075)
             for i, f in enumerate(notes)]
    pad = env_hump(lowpass(tone(262, 0.7, 330, 'tri'), 1200), power=1.2, peak=0.4)
    return finish(mix(bells + [(pad, 0.35, 0)]), peak=0.6)


# ---- combat events added with the new features (not yet heard by the author: volumes / timbres to tune) ------------
def shoot():               # arrow / bolt / fireball leaving the weapon: a short airy "thwip"
    r = rng('shoot')
    air = env_hump(highpass(lowpass(noise(0.16, r), 3600, 1500), 900), power=1.2, peak=0.3)
    twang = env_exp(tone(420, 0.16, 190, 'tri'), 0.04)
    return finish(mix([(air, 1.0, 0), (twang, 0.5, 0)]), peak=0.7)


def throw():               # knife / bomb: a lighter whoosh
    r = rng('throw')
    air = env_hump(highpass(lowpass(noise(0.18, r), 3000, 1200), 1100), power=1.5, peak=0.35)
    return finish(air, peak=0.6)


def impact():              # a lobbed arrow / rock coming down: dull thud + a little dust
    r = rng('impact')
    thud = env_exp(tone(110, 0.2, 55, 'sine'), 0.06)
    dust = env_exp(lowpass(noise(0.12, r), 1800), 0.03)
    return finish(mix([(thud, 1.0, 0), (dust, 0.5, 0)]), peak=0.7)


def block():               # a blow stopped by a shield: bright metallic clang
    r = rng('block')
    clang = mix([(env_exp(tone(f, 0.35, shape='square', duty=.3), 0.09), a, 0)
                 for f, a in ((880, 0.5), (1320, 0.4), (1975, 0.3), (2790, 0.2))])
    crack = env_exp(highpass(noise(0.06, r), 2500), 0.012)
    return finish(mix([(clang, 1.0, 0), (crack, 0.6, 0)]), peak=0.6)


def armor_hit():           # armor soaking a hit: a duller clink than a shield
    r = rng('armor_hit')
    clink = env_exp(tone(1400, 0.2, 900, 'square', duty=.4), 0.05)
    thud = env_exp(tone(130, 0.15, 70, 'sine'), 0.05)
    return finish(mix([(clink, 0.5, 0), (thud, 0.9, 0), (env_exp(noise(0.05, r), 0.01), 0.3, 0)]), peak=0.6)


def armor_break():         # armor giving way: crunch + a few falling plates
    r = rng('armor_break')
    crunch = env_exp(lowpass(noise(0.35, r), 3000, 900), 0.1)
    plates = [(env_exp(tone(f, 0.2, shape='square', duty=.3), 0.05), 0.3, d) for f, d in ((1500, 0.05), (1100, 0.14), (800, 0.24))]
    return finish(mix([(crunch, 1.0, 0)] + plates), peak=0.75)


def weapon_break():        # a weapon snapping: sharp crack and splinters
    r = rng('weapon_break')
    crack = env_exp(highpass(noise(0.12, r), 1800), 0.025)
    snap = env_exp(tone(320, 0.15, 90, 'saw'), 0.04)
    bits = [(env_exp(tone(f, 0.1, shape='square', duty=.25), 0.03), 0.25, d) for f, d in ((2100, 0.1), (1700, 0.17), (2400, 0.22))]
    return finish(mix([(crack, 1.0, 0), (snap, 0.6, 0)] + bits), peak=0.75)


def charge():              # holding the special: a rising hum
    hum = env_hump(lowpass(tone(110, 0.5, 330, 'saw'), 1600, 700), power=1.0, peak=0.8)
    shimmer = env_hump(tone(660, 0.5, 1320, 'sine'), power=1.5, peak=0.7)
    return finish(mix([(hum, 0.6, 0), (shimmer, 0.25, 0)]), peak=0.5)


def special():             # releasing the special: a big whoosh with a ring
    r = rng('special')
    air = env_hump(highpass(lowpass(noise(0.5, r), 2400, 600), 300), power=1.1, peak=0.4)
    ring = env_exp(tone(880, 0.5, 440, 'tri'), 0.18)
    return finish(mix([(air, 1.0, 0), (ring, 0.35, 0.02)]), peak=0.85)


def spikes():              # stone spikes erupting: rumble + cracks
    r = rng('spikes')
    rumble = env_exp(lowpass(noise(0.4, r), 500, 200), 0.14)
    cracks = [(env_exp(highpass(noise(0.05, r), 1500), 0.01), 0.6, d) for d in (0.0, 0.05, 0.1)]
    return finish(mix([(rumble, 1.0, 0)] + cracks), peak=0.8)


def explosion():           # a fireball / bomb bursting: boom + crackle
    r = rng('explosion')
    boom = env_exp(tone(80, 0.5, 35, 'sine'), 0.16)
    blast = env_exp(lowpass(noise(0.45, r), 2600, 300), 0.12)
    return finish(mix([(boom, 1.0, 0), (blast, 0.8, 0)]), peak=0.9)


def telegraph():           # the minotaur warning: low snort / horn
    horn = drive(lowpass(tone(70, 0.5, 100, 'saw', vibrato=(9, 0.04)), 800, 400), 2.5)
    return finish(env_hump(horn, power=0.9, peak=0.5), peak=0.7)


def boss_start():          # the boss arrives: a long, low horn
    horn = drive(lowpass(tone(55, 1.1, 73, 'saw', vibrato=(5, 0.03)), 600, 300), 2.5)
    horn2 = lowpass(tone(110, 1.1, 146, 'saw'), 700, 300)
    return finish(mix([(env_hump(horn, power=0.7, peak=0.5), 1.0, 0), (env_hump(horn2, power=0.7, peak=0.5), 0.5, 0.05)]), peak=0.75)


def victory():             # boss defeated / stage complete: a short triumphant arpeggio
    notes = ((392, 0.0), (523, 0.11), (659, 0.22), (784, 0.33), (1047, 0.5))
    parts = [(env_exp(tone(f, 0.5, shape='square', duty=.4), 0.16), 1.0, d) for f, d in notes]
    pad = env_hump(lowpass(tone(262, 1.0, 262, 'tri'), 1500), power=1.0, peak=0.4)
    return finish(mix(parts + [(pad, 0.5, 0)]), peak=0.45)


def revive():              # paid revival: a rising chime
    bells = [(env_exp(mix([(tone(f, 0.6), 1.0, 0), (tone(f * 2, 0.6), 0.25, 0)]), 0.2, attack=0.01), 1.0, i * 0.09)
             for i, f in enumerate((330, 440, 554, 659, 880))]
    return finish(mix(bells), peak=0.6)


def gulp():                # drinking a potion
    r = rng('gulp')
    g1 = env_exp(tone(240, 0.1, 140, 'sine'), 0.04)
    g2 = env_exp(tone(200, 0.1, 110, 'sine'), 0.04)
    return finish(mix([(g1, 1.0, 0), (g2, 0.9, 0.12), (env_exp(lowpass(noise(0.25, r), 900), 0.05), 0.2, 0)]), peak=0.55)


def jump():                # a short rising whoosh (the hero leaves the ground)
    r = rng('jump')
    air = env_hump(highpass(lowpass(noise(0.14, r), 1800, 3200), 500), power=1.2, peak=0.35)
    return finish(air, peak=0.35)



def guard_break():         # a shield giving way: a heavy clang, a crack and metal pieces falling
    r = rng('guard_break')
    clang = mix([(env_exp(tone(f, 0.5, f * 0.7, 'square', duty=.3), 0.14), a, 0)
                 for f, a in ((660, 0.5), (990, 0.4), (1480, 0.3), (2210, 0.2))])
    crack = env_exp(highpass(noise(0.14, r), 1600), 0.03)
    thud = env_exp(tone(150, 0.25, 60, 'sine'), 0.07)
    bits = [(env_exp(tone(f, 0.12, shape='square', duty=.25), 0.035), 0.3, d) for f, d in ((1900, 0.12), (1500, 0.2), (2300, 0.28), (1200, 0.36))]
    return finish(mix([(clang, 1.0, 0), (crack, 0.9, 0), (thud, 0.8, 0)] + bits), peak=0.85)


SOUNDS = {f.__name__: f for f in (sword_swing, axe_swing, hit_knight, hit_ogre, hurt_knight, hurt_ogre,
                                  death_knight, death_ogre, spawn_hero, spawn_ogre, coin_pickup, heal,
                                  shoot, throw, impact, block, guard_break, armor_hit, armor_break, weapon_break, charge, special,
                                  spikes, explosion, telegraph, boss_start, victory, revive, gulp, jump)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join('assets', 'sfx'))
    ap.add_argument('--only', nargs='*', help='names of the sounds to generate (default: all)')
    a = ap.parse_args()
    print(f"{'sound':<14}{'sec':>6}{'peak':>7}{'rms':>7}")
    for name, fn in SOUNDS.items():
        if a.only and name not in a.only: continue
        x = fn(); write_wav(os.path.join(a.out, name + '.wav'), x)
        rms = (sum(s * s for s in x) / len(x)) ** 0.5
        print(f'{name:<14}{len(x) / SR:>6.2f}{max(abs(s) for s in x):>7.2f}{rms:>7.3f}')


if __name__ == '__main__':
    main()
