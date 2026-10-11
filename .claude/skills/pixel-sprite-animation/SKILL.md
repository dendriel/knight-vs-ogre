---
name: pixel-sprite-animation
description: Create 2D pixel-art character spritesheets and animation sets (idle, walk, run, melee attacks, bow/crossbow, hurt, death, etc.) for one or several characters (heroes, enemies) procedurally with Python + Pillow, exporting a PNG sheet, a JSON atlas and a GIF preview. Use this whenever the user wants game sprites, spritesheets, character or enemy animations, sprite frames (32x32, 64x64...), "animação de personagem", "spritesheet", "sprite de jogo 2D", wants to ADD animations (hurt, death, new weapons) or a NEW CHARACTER (ogre, skeleton, etc.) in the same style, or provides an existing spritesheet and wants new poses/recolors - even if they never say "pixel art" or "procedural".
---

# Pixel sprite animation

> **Where the scripts live:** `scripts/` and `references/` sit next to this file. If this skill was installed as instructions only (for example saved from claude.ai without its files), the same scripts are in the user's project under `art_tools/`; if they are missing there too, ask the user to attach them.

Builds sprite animations by **drawing the character with code** (a skeleton rig with two-bone IK + pixel-perfect drawing), not with an image-generation model. Frames come out consistent, grid-aligned and easy to extend. Be upfront about the trade-off: the look is clean and a bit rigid compared to hand-made art; fine shading or very detailed characters need a human artist's retouch.

## What is in `scripts/`

| file | role |
|---|---|
| `sprite_rig.py` | **Shared rig**: palette, `outline`, `layer`, `limb`, `ik`, leg/arm/torso/head/weapon drawing, `render()` for melee poses and `render_ranged()` for bow/crossbow, `tint()` (hit flash), `LAST` (records shoulder/hip/hand positions of the last render, used to align effects). |
| `knight_gen.py` | The knight: 64x64 frames, 6 frames per animation, **9 animations** (idle, walk, run, attack_sword, attack_axe, attack_bow, attack_crossbow, hurt, death). Poses are lists per frame index. Run it: `python knight_gen.py <out_dir>`. |
| `ogre_gen.py` | A **second character** built on the same rig (wider body, own drawing functions, own `o_render`): idle, walk, attack (axe), hurt, death. The template for any new enemy. |
| `check_edges.py` | Lists frames whose pixels touch the frame border (clipping). |

Copy these to a working folder and extend them instead of starting from scratch. `references/poses.md` has the numeric pose values of everything already built, which are good starting points.

## Workflow

1. **Pin down the brief** (ask only what's missing, one question at a time): frame size, frames per animation, animation list, character/theme, weapon or props, engine. Defaults: one facing direction (right; the game mirrors it), transparent background, 6 frames, 64x64.
2. **Run the existing generators once** to confirm the environment (Pillow is enough) and to have a reference for scale.
3. **Add poses or a character** (see below). For a new character copy `ogre_gen.py`, change palette, proportions and drawing functions; keep the pose dicts, the layer/outline pipeline and the export code.
4. **Look at the result before delivering**: render a 3x preview on a flat background and inspect every row with the image viewer. Fix what looks wrong and re-render. Expect 1-3 rounds.
5. **Run `check_edges.py <sheet.png>`** (clipping), and for additions to an existing sheet **diff the old rows** (see "Never break existing rows").
6. **Deliver**: sheet PNG, JSON atlas, GIF preview and the generator scripts (so work can be resumed later). Summarize each animation frame by frame, give suggested fps, and mention engine notes (facing, anchor, hit frames, spawn frames for projectiles, per-frame shift).

## Never break existing rows

The user's engine already points at row numbers and frame names. When appending animations:
- add new rows **at the end**, never reorder;
- after any refactor of the rig, render the old animations again and compare with the previous sheet using `ImageChops.difference(new, old).getbbox()`; it must be `None` for the old rows. This is the cheap guarantee that a refactor (like splitting the rig into `sprite_rig.py`) changed nothing the engine depends on.

## How the rig works

- **Angle convention**: 0 = pointing down, 90 = forward (right), 180 = up, 270 = back. `vec(a) = (sin a, cos a)`. Use it for weapons, aim and limb directions.
- **Layers + outline**: every body part is drawn on its own transparent layer, gets a 1 px dark outline, then layers are composited in depth order (far arm, far leg, plume, torso, head, near leg, near arm, weapon). This gives clean inner outlines for free. Do not outline 1 px-thin things (arrow shafts, strings, trails): draw them on a layer with `ol=False`.
- **No anti-aliasing**: Pillow primitives (`line`, `polygon`, `ellipse`, `point`) with opaque colors only; round float coordinates with `rd()`.
- **Two-bone IK** (`ik(a, b, l1, l2, prefer)`): legs take ankle targets, arms take hand targets. `prefer`: `'x'` elbow/knee points forward, `'xm'` backward (archer's drawing elbow), `'y'` downward, `'ym'` upward (knees of a body lying on its back). Targets beyond reach are clamped, so limbs never break.
- **Hip height is automatic**: computed from the feet targets so the feet stay on the ground row (`GY = 58`). `sink` adds a crouch. Never set hip height by hand or feet will float or slide. Leg reach is the sum of the two leg bones (knight: 16.8 inside `render`; ogre: the `REACH = 15.6` constant in `ogre_gen.py`).
- **Pose dict** (all optional except feet/hands/weapon): `hx` body shift, `footN/footF` ankles (lifted = smaller y), `sink`, `lean` degrees forward, `tdy` torso compression (breathing), `handN/handF` hand offsets from the shoulder, `wang` weapon angle, `plume`, `flap`, `trail`, `shift` (whole-frame x shift to avoid clipping), `flash` (white tint 0-1), `headoff`, and for lying poses `rot_head`, `head_rot`, `knee`, `cloth_ang`, `wpos`, `wback`.
- **Weapons are functions** returning layers. To add one (spear, mace, shield, staff) write `def spear(hand, angle)` with a local frame `P(t, s)` (t along the weapon, s across it) and add a branch in `render`. Ranged weapons go through `render_ranged`.
- **Anchor**: the hip column inside the frame is `CX` (30). A mirrored frame has it at 63 - 30 = 33. Engines should place sprites by this column and by the ground row so mirrored sprites don't jump.

## Authoring poses

- Think in **keyframes per frame index** as lists (one value per frame). Change one parameter family at a time and re-render.
- **Looping cycles** (idle, walk, run): the last frame must lead into the first. Use sine/cosine phases (`p = i*60deg + offset`) so they close by construction. Walk: body is lowest when the feet are far apart. Run: longer stride, higher foot lift, forward lean, trailing cloth/plume.
- **Attacks** work as six beats: ready, windup (move opposite to the strike, lean back), peak, strike, impact/follow-through, recovery. Fast motion = big pose jumps between frames; slow beats = small jumps. Frames 3-4 are the "active" swing frames, which is where a game should apply damage and where slash effects start.
- **Ranged attacks**: raise, aim, draw, release, recovery. Keep string/loaded state tied to the pose (`pull`, `loaded`). On release the string snaps back and the drawing hand keeps moving back for a frame; crossbows kick the muzzle up.
- **Projectiles** are drawn only in the release frame (index 4). Tell the user which frame to spawn the real projectile at and offer separate projectile sprites.
- **Hurt** (6 frames): frames 0-1 flash white (`flash=.85`, `.3`) while the body snaps back (negative `lean`, `hx` back, head pushed back); then recover to the idle pose. The game should treat the whole animation as "stunned".
- **Death** (6 frames): stagger, drop the weapon (`wback=True` draws it behind the body and `wpos` places it), fall on the back (`lean` toward -90, `rot_head`/`head_rot`, `knee='ym'`, rotate cloth with `cloth_ang`), last 2-3 frames hold the lying pose so the corpse can stay in the world. The corpse must fit inside the frame (check edges).
- **A new enemy**: change proportions (ogre: leg bones 8+8, limbs 5-6 px wide, torso 14 px, forward-stooped `lean=18`), keep the same pose vocabulary, give it a **different dominant color** and a silhouette that reads at 1x (tusks, horn, big weapon). Mirror the facing in the game, not in the sheet.
- **Weapon consistency**: if idle/walk show one weapon and an attack shows another, say so and offer variants of the base cycles per weapon (the ogre only ever carries its axe, so it has no mismatch).

## QA checklist

- View the enlarged preview; every frame must read at 1x: weapon visible, silhouette not a blob, far side darker than near side.
- `python check_edges.py sheet.png [frame_size] [cols]` lists frames touching the border (all four sides). Fix by reducing reach, moving `CX`, adding a `shift` (negative = left), lowering `sink`, or rotating cloth. A lone outline pixel on the border is harmless; weapons and heads must never be cut.
- Feet on the same ground row in all grounded frames (no jitter between frames).
- Limb lengths constant inside an animation (IK guarantees this).
- Pixel-diff old rows after any refactor (see above).

## Export format

- **Sheet**: one row per animation (declared order), one column per frame, cells exactly `frame_size`, transparent background. Size = `cols*F` x `rows*F`.
- **Atlas JSON**: `frames` (`name_i` with x, y, w, h), `animations` (frame names, fps, loop flag), `meta` (image, frame size, facing). Attacks, hurt and death use `loop: false`. Easy to adapt to Phaser, Godot, Unity or a custom loader (the Python game in this project reads `fps` from it).
- **GIF preview**: animations side by side at 3x, ~110 ms per frame, on a flat background (GIF has no real alpha). For a game-like preview use the `pixel-vfx-effects` skill's `demo_gif.py`.
- Suggested fps: idle 6, walk 10, run 12, attacks 10-12, hurt 10, death 8.

## When the user provides an existing spritesheet

1. View it and detect the grid by slicing with code; extract the exact palette (`Counter` of RGBA values) and note the outline color and anchor (feet row, horizontal center).
2. **Recolors**: remap palette entries (exact-match replacement keeps pixel art crisp).
3. **Recombinations**: mirror, shift, or reassemble existing frames with code.
4. **New poses**: rebuild the character with the rig using the same palette, proportions and outline style, then compare side by side with the originals. Fidelity drops for detailed or painterly art; simple low-resolution pixel art matches well.
5. Keep the original frame size, anchor and palette so new frames drop into the same engine setup.

## Gotchas learned

- A weapon swung with arm angles but no hand IK looks broken; drive hands with targets and the weapon with its own angle. Two-handed weapons (axe): the far hand follows the handle (`hand - dir*4..5`).
- Large swings and forward-pointing projectiles clip at the right border first; keep about 30 px free to the right of `CX` and use `shift` on the extreme frames. Bodies lying down clip at the bottom/right: lower `sink`, move the dropped weapon inward.
- A weapon on the back looks like a hat when it overlaps the head: lower the hand and increase the weapon angle (ogre idle uses `wang=228`, `handN=(4,2)`).
- Don't draw 1 px lines on outlined layers; don't shade with transparency; don't use more than ~5 tones per material.
- A walk cycle with the wrong stride-to-speed ratio looks like skating: pick the game's walk speed from the stride (`foot travel per cycle`) instead of the other way round, or tune fps.
- Tell the user what is NOT animated or varies (weapon changes between animations, projectile only drawn on one frame, per-frame shift) so they can adapt their game code.
