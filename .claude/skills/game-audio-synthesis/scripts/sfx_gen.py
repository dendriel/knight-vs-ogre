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


SOUNDS = {f.__name__: f for f in (sword_swing, axe_swing, hit_knight, hit_ogre, hurt_knight, hurt_ogre,
                                  death_knight, death_ogre, spawn_hero, spawn_ogre)}


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
