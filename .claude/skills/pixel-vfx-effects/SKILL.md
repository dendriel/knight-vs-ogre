---
name: pixel-vfx-effects
description: Create pixel-art 2D game visual effects as spritesheets with Python + Pillow - weapon slash/swoosh trails that follow the real weapon path, impact sparks, blood splashes, ghost/spirit death effects, and similar (hit flashes, dust, magic, explosions) - plus a composite demo GIF that plays characters, effects and scenery together. Use this whenever the user asks for efeitos especiais, VFX, slash/rastro de ataque, splash de sangue, espírito saindo do corpo, particles, or wants effects synchronized with existing character animations - even if they don't say "pixel art".
---

# Pixel VFX effects

> **Where the scripts live:** `scripts/` and `references/` sit next to this file. If this skill was installed as instructions only (for example saved from claude.ai without its files), the same scripts are in the user's project under `art_tools/`; if they are missing there too, ask the user to attach them.

Effects are drawn **with code**, one 64x64 frame per step, 6 frames per effect, on the same grid and anchor as the characters so the game can draw them at the character's position with the same mirroring. `scripts/vfx_gen.py` is a complete example (4 effects); `scripts/demo_gif.py` composes characters + effects + scenery into GIFs.

It builds on the characters made with `pixel-sprite-animation` (same 64x64 frame, hip column 30, ground row 58) and the scenery from `pixel-scenery-assets`.

## Workflow

1. **Decide how each effect is synchronized** (this is the contract with the game):
   - *Attached to an attack*: effect frame `i` plays together with attack frame `3+i` (the active swing frames), same anchor, same mirroring. Spawn it when the attacker's frame index reaches 3.
   - *Attached to a victim*: blood splash is anchored on the victim's chest; spawn it at the moment of damage and mirror it with the victim (it sprays backwards, away from the attacker).
   - *Attached to a corpse*: the spirit rises from a body lying on the ground.
2. **Measure, don't guess**, for attack trails: render the attack frames with the character rig and read `LAST['hand']`, `LAST['S']`, the weapon angle (`wang`) and the per-frame `shift`. Weapon tip = `hand + length * vec(wang)` (sword ~21 px, axe ~25 px); then add the frame's `shift` to x (negative = left), because the character frame is moved by it but the effect frame is not. Take **three points on the swing** (start, middle, end) as the arc.
3. **Draw the effect on its own transparent frame**, 6 frames, ending with a faded or empty frame so the animation cleans itself up.
4. **Preview on a light AND a dark background** at 3x (dithered effects look different on each), then in the **composite demo** with the real characters. The demo is the real test: timing against the swing, size next to the character, readability at 1x.
5. **Export**: `vfx_spritesheet.png` (one row per effect) + `vfx_spritesheet.json` (frames, animations with fps, `loop: false`, a `meta.note` describing the synchronization contract above).

## Techniques that worked

- **Fake transparency with ordered dithering**: pixel art has no semi-transparency. Use a 4x4 Bayer matrix: a pixel with alpha `a` is drawn only if `a > (BAYER[y%4][x%4] + .5) / 16`. All colors stay opaque, so the sheet is clean and fades read as a stipple. See `put(im, x, y, col, alpha)`.
- **Slash = crescent along a circle through three points**: compute the circumcircle (`circumcircle`, `arc_through`), then draw a tapered band along the arc: thickness envelope `sin(pi*u)**0.7` between a `tail` and a `head` parameter, band tones from the leading edge inward (edge, core, mid, outer). Frame `i` has its own `(tail, head, max thickness, alpha)` window: the head advances, then the tail catches up and the band thins and dithers away. Sword: white-blue, thin and fast. Axe: orange, thicker, with an **impact burst** (radial lines + a white cross on the first impact frame) where the arc ends.
- **Sparks** are single pixels with a 50% chance of a second pixel along the radial direction, scattered around the arc where the head is.
- **Blood = ballistic particles**: position `o + v*t + .55*t^2` with random `v` (mostly backwards and up), 34 particles, ~60% drawn as 2x2 "big" drops with a streak line from the previous position. Frames 0-2 add a central burst (radial spikes + a filled blob with a highlight pixel). **Drops that reach the ground row stay as flat 2-3 px splats** in the following frames, so the floor is stained by the end. Palette: dark red (92,8,22), red (148,16,30), bright (204,34,44), highlight (238,88,80).
- **Spirit/ghost**: a signed-region function (round head + tapering wavy tail whose sway depends on frame phase), drawn with edge/highlight/body tones and a soft glow ring at low alpha; rises ~8 px per frame along a slight sine path, scales up then fades (alpha 0.45 -> 0.92 -> 0.3); two eye pixels and a small mouth; drifting sparkles with a cross shape on some frames. Starts slightly after the death animation begins (the game delays it by ~0.45 s).
- **Measure the character path** with a short script using the rig's `LAST` dict (this is how the slash arcs were placed):

```python
from sprite_rig import LAST, vec, render
import knight_gen as K
for i in (2, 3, 4, 5):
    p = K.atk_sword(i); render(p)
    h = LAST['hand']; v = vec(p['wang'])
    print(i, 'hand', h, 'tip', (h[0] + 21 * v[0], h[1] + 21 * v[1]), 'shift', p.get('shift', 0))
```

## demo_gif.py (composite)

`python demo_gif.py <sheets_dir> <scenery_dir> <out_dir>` builds three GIFs from the three sheets + scenery PNGs: a battle scene, a scene where the hero dies, and an overview grid of every animation with its fps. A scene is a list of **segments per actor** (`who`, `anim`, start time, optional movement `x0 -> x1`) plus a list of **effects** (`name`, start time, `on` = actor). The actor's flip is applied to its effects too. Use it to check timing and to give the user something to watch. It quantizes all frames to one shared palette to keep colors stable and file size low (~200 KB for 8 s at 2x).

## QA checklist

- Each effect has 6 frames, the last one empty or nearly empty.
- Slash crescents sit on the weapon's real path in the demo (not floating in front of or behind the blade).
- Sparks and splash drops may touch the frame border by a pixel or two; nothing important may be cut.
- Blood and spirit are readable on both light and dark backgrounds; the spirit does not hide the corpse.
- Effects mirror correctly with their actor (anchor column 30 normal, 33 mirrored).

## Gotchas learned

- A first blood splash looked weak and scattered: more particles with **mass** (2x2 drops, a real burst on the first frames) and **landing splats** made it read well.
- Dithered alpha at 1x looks like noise if too sparse; keep alpha >= 0.3 for anything that must stay visible.
- Don't change a character's attack frames without regenerating the slash effects: they were fitted to those exact poses.
- File size: record GIFs only over the moments that matter (windows of time), at ~10 fps, with a shared palette; a 60 s recording at 15 fps was 14 MB.
