"""Background music of Knight vs Ogre: a medieval-sounding loop in D dorian (lute + flute + drone bass + frame drum).
Run from the project root:

    python .claude/skills/game-audio-synthesis/scripts/music_gen.py            # writes assets/music/medieval_theme.wav

16 bars of 4/4 at 108 bpm (~35 s), A section then B section. Tails of the last notes are folded onto the start so the
loop point has no cut.
"""
import argparse, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import synth
from synth import *

synth.SR = 22050                      # music is long: half the sample rate halves render time and file size
BPM = 108; SPB = 2                    # steps per beat (eighth notes); 8 steps per bar
BARS = 16; STEPS = BARS * 8
STEP_SEC = 60.0 / BPM / SPB

D4, E4, F4, G4, A4, B4, C5, D5, E5, F5, G5, A5 = 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81

# per bar: (bass root, lute triad)
CHORDS = {'Dm': (50, (57, 62, 65)), 'C': (48, (55, 60, 64)), 'F': (53, (57, 60, 65)),
          'Am': (45, (57, 60, 64)), 'G': (55, (55, 59, 62))}
PROG = ['Dm', 'C', 'F', 'C', 'Dm', 'Am', 'C', 'Dm',         # A
        'G', 'Dm', 'C', 'Am', 'G', 'F', 'C', 'Dm']          # B

# melody per bar: (step inside the bar, midi, length in steps)
MELODY = [
    [(0, A4, 2), (2, D5, 2), (4, F5, 2), (6, E5, 2)],
    [(0, E5, 4), (4, D5, 2), (6, C5, 2)],
    [(0, A4, 2), (2, C5, 2), (4, F5, 4)],
    [(0, E5, 2), (2, D5, 2), (4, C5, 4)],
    [(0, D5, 2), (2, F5, 2), (4, A5, 2), (6, G5, 2)],
    [(0, E5, 3), (3, D5, 1), (4, C5, 2), (6, A4, 2)],
    [(0, C5, 2), (2, E5, 2), (4, G5, 2), (6, E5, 2)],
    [(0, D5, 6), (6, A4, 2)],
    [(0, B4, 2), (2, D5, 2), (4, G5, 4)],
    [(0, F5, 2), (2, E5, 2), (4, D5, 4)],
    [(0, E5, 2), (2, G5, 2), (4, E5, 2), (6, C5, 2)],
    [(0, A4, 4), (4, C5, 2), (6, E5, 2)],
    [(0, D5, 2), (2, G5, 2), (4, E5, 2), (6, D5, 2)],
    [(0, C5, 2), (2, F5, 2), (4, A5, 4)],
    [(0, G5, 2), (2, E5, 2), (4, D5, 2), (6, C5, 2)],
    [(0, D5, 4), (4, F5, 2), (6, E5, 2)],
]


def render_lines():
    tail = 12                                           # extra steps rendered past the end, folded back later
    total = STEPS + tail
    melody, lute, bass = [], [], []
    for b in range(BARS):
        o = b * 8; root, triad = CHORDS[PROG[b]]
        melody += [(o + s, m, l) for s, m, l in MELODY[b]]
        for i, k in enumerate((0, 1, 2, 1, 0, 1, 2, 1)):        # lute arpeggio, eighth notes
            lute.append((o + i, triad[k], 2))
        bass += [(o, root, 4), (o + 4, root + 7, 4)]             # root, then the fifth
    flute = sequence(melody, BPM, SPB, total, shape='sine', tau=0.5, vibrato=(5.0, 0.008))
    flute2 = sequence(melody, BPM, SPB, total, shape='tri', tau=0.3)
    lutes = lowpass(sequence(lute, BPM, SPB, total, shape='square', duty=0.25, tau=0.18), 2600)
    drone = lowpass(sequence(bass, BPM, SPB, total, shape='tri', tau=0.6), 500)
    drums = render_drums(total)
    return mix([(flute, 0.55, 0), (flute2, 0.18, 0), (lutes, 0.30, 0), (drone, 0.55, 0), (drums, 0.5, 0)]), total


def render_drums(total_steps):
    r = random.Random('medieval_theme')
    thump = env_exp(tone(130, 0.18, 55, 'sine'), 0.07)
    tick = env_exp(highpass(noise(0.06, r), 3500), 0.012)
    parts = []
    for b in range(BARS + 2):
        o = b * 8
        for s in (0, 4): parts.append((thump, 1.0 if s == 0 else 0.75, (o + s) * STEP_SEC))
        for s in (2, 6): parts.append((tick, 0.45, (o + s) * STEP_SEC))
        parts.append((tick, 0.2, (o + 7) * STEP_SEC))                    # little pickup tick
    return mix(parts, length=frames(total_steps * STEP_SEC))


def build():
    x, total = render_lines()
    loop = frames(STEPS * STEP_SEC)
    head, tail = x[:loop], x[loop:]
    for i, v in enumerate(tail):                                        # fold the ringing tails onto the start
        if i < loop: head[i] += v
    peak = max(abs(s) for s in head)
    return [s * 0.8 / peak for s in head]                               # no fades: the loop point must stay seamless


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join('assets', 'music', 'medieval_theme.wav'))
    a = ap.parse_args()
    x = build(); write_wav(a.out, x, sr=synth.SR)
    rms = (sum(s * s for s in x) / len(x)) ** 0.5
    print(f'{a.out}: {len(x) / synth.SR:.1f}s  peak {max(abs(s) for s in x):.2f}  rms {rms:.3f}  '
          f'edges {abs(x[0]):.3f}/{abs(x[-1]):.3f}')


if __name__ == '__main__':
    main()
