---
name: game-audio-synthesis
description: Create 2D game sound effects (sword/axe swings, impacts, grunts and growls, death cries, spawn jingles, UI blips) and simple chiptune/medieval music loops procedurally with pure Python (standard library only), exported as .wav files and wired into a pygame game through world events. Use this whenever the user asks for sons, efeitos sonoros, SFX, som de golpe/dano/morte, música, trilha, loop de batalha, chiptune, or wants audio added to a game - even if they don't say "synthesize" or "procedural".
---

# Game audio synthesis (SFX + music)

> **Where the scripts live:** `scripts/` sits next to this file. `synth.py` is the library, `sfx_gen.py` is the complete
> example (10 sounds of Knight vs Ogre). Run from the **project root**; output goes to `assets/sfx/` by default.

Sounds are plain lists of floats built with code, so they can be regenerated, tweaked by editing a number, and have no
license issues. No numpy needed; the whole SFX set renders in well under a second.

**You cannot hear the result.** Never claim a sound "sounds good". Verify what you can (duration, peak, RMS, no clipping,
files load in the real mixer) and ask the user to listen and describe problems in plain words ("too shrill", "too
long", "too quiet"). Then adjust one parameter at a time.

## Workflow

1. **List the game events first**, not the sounds. Decide which moments need audio and who owns them (swing, hit,
   hurt voice, death, spawn, footstep, pickup, UI...). Reuse the events the game logic already has.
2. **Keep the logic free of audio.** The world appends semantic events `(name, kind)` to `world.events`
   (`('swing','knight')`, `('hit','ogre')`, `('death','ogre')`...). `main.py` drains the list every frame and
   `game/audio.py` maps `(name, kind) -> wav file`. Tests that run without a window keep working.
3. **Write one function per sound** in a generator script, register it in `SOUNDS`, run it, check the stats table.
4. **Balance by RMS, not by peak.** `finish()` normalizes every sound to the same peak, so square waves (loud) and noisy
   whooshes (quiet) end up unbalanced. Lower `peak=` for the loud ones (spawn blips used 0.4) and use `SFX_VOLUME`
   in `config.py` for the master level.
5. **Test in the real game**, ask for feedback, iterate.

## Building blocks (`synth.py`)

| need | use |
|---|---|
| pitched sound with glide | `tone(f0, dur, f1, shape='sine'/'square'/'saw'/'tri', duty, vibrato=(rate, depth))` |
| wind, crack, breath | `noise(dur, rng)` then `lowpass` / `highpass` / `bandpass` (cutoffs can glide `c0 -> c1`) |
| percussive decay | `env_exp(x, tau)`; whoosh shape: `env_hump(x, power, peak)` |
| growl / grit | `drive(x, amount)` (tanh clipping); lo-fi: `crush(x, bits, hold)` |
| layering and timing | `mix([(samples, gain, delay_seconds), ...])` |
| finalize | `finish(x, peak=0.9)` (normalize + click-free fades), `write_wav(path, x)` |
| notes / music | `midi_hz`, `note`, `sequence(notes, bpm, ...)` |

Use a **seeded** `random.Random(name)` per sound so regenerating is deterministic.

## Recipes that were used (starting points)

- **Sword swing** (0.2 s): noise -> lowpass 1.5k->7k -> highpass 700 Hz, `env_hump(power 1.6, peak .35)`; add a faint
  sine glide 2.6k->4.2k for the "shing".
- **Axe swing** (0.3 s): same idea, darker (lowpass 350->3000 Hz) plus a saw 110->55 Hz body at ~0.45 gain.
- **Hit on armor**: sine thud 150->48 Hz (`tau .07`) + 10 ms noise crack + three inharmonic square partials
  (1180/1770/2430 Hz, low duty) at low gain for the clank.
- **Hit on flesh/hide**: sine 95->38 Hz + lowpassed noise burst 1400->500 Hz + a very short highpassed "slice".
- **Grunt** (human): saw 230->150 Hz with 18 Hz vibrato, lowpass ~1.4k, fast attack (8 ms), plus a breath of noise.
- **Growl** (ogre): saw 88->58 Hz, vibrato 11 Hz, `drive(3)` after a lowpass 900->450, rasp noise underneath.
- **Death**: a long falling saw (300->70 Hz or 120->32 Hz) followed, ~0.6-0.85 s later, by a low thud + noise burst for
  the body hitting the ground.
- **Spawn**: hero = three rising square blips (G4, C5, G5, 70 ms apart); ogre = low saw horn 65->82 Hz, lowpassed.

Rules of thumb: size = pitch (big creature -> lower fundamental and slower decay); impact = low sine drop + very short
noise; metal = a few inharmonic partials; anger = drive; anything that must not click needs `finish()`.

## Music (first track made; awaiting the user's ear)

`scripts/music_gen.py` is the complete example: 16 bars of 4/4 at 108 bpm in D dorian, ~35 s, written to
`assets/music/medieval_theme.wav`. Layers: flute melody (sine + vibrato, plus a quiet triangle), lute arpeggio (narrow
square, lowpass 2.6 kHz, short decay), triangle drone bass (root + fifth), frame drum (low thump on beats 1/3, noise
ticks on 2/4). Chords/melody are plain tables per bar, so changing the tune means editing lists.

- `sequence(notes, bpm, steps_per_beat, length_steps, ...)` renders `(step, midi, length)` tuples. Render a few steps
  **past** the loop length and fold that tail onto the start, so the loop point is seamless; do not use `finish()`
  fades on a loop.
- Use `synth.SR = 22050` for music (set it before building; pass `sr=synth.SR` to `write_wav`): 2.4 s to render 35 s,
  1.5 MB file. Mono 16-bit.
- Keep music quieter than the SFX (`MUSIC_VOLUME` 0.35 vs `SFX_VOLUME` 0.7) and avoid the 1-4 kHz band being full
  of sustained notes, or the swings and grunts get masked.
- Playback: `pygame.mixer.music.load(...)`, `play(-1)`; mute with `set_volume(0)`.
- Ideas for other moods: battle = faster (130+ bpm), minor, more drum ticks; menu = slow, no drums; boss = lower
  octave, `drive` on the bass.

## Wiring into pygame (what the project does)

- `config.py`: `SFX_ENABLED`, `SFX_VOLUME`, `MUSIC_ENABLED`, `MUSIC_VOLUME`, `MUSIC_FILE`.
- `game/audio.py`: loads every `assets/sfx/*.wav` with `pygame.mixer.Sound`, `play_events(events)`, `toggle_mute()`;
  fails soft (no device or no mixer -> silent game). Key **M** mutes.
- `main.py`: `self.audio.play_events(self.world.events); self.world.events.clear()` after `world.update`.
- PyInstaller already bundles `assets/` (`--add-data "assets;assets"`), so the sounds ship in the .exe.
- Headless check with the real mixer: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -c "import main; ..."`.

## Gotchas

- `tests/fake_pygame.py` has no mixer: `Audio` handles that with `getattr(pygame, 'mixer', None)`. Add new keys
  (like `K_m`) to the fake module too, or `tests/simulate.py` breaks.
- Sounds fire on events, so holding the attack key can retrigger a swing every ~0.3 s; keep swings short and quiet.
- Don't put the swing sound at the start of the animation: the blow lands at frame 3, the game emits `swing` there.
- If the attack animation speed changes (`ATTACK_ANIM_SPEED`), sound durations stay fixed; shorten sounds that now
  outlast the animation.
