---
name: pixel-scenery-assets
description: Create static 2D pixel-art scenery and props for games (trees, houses, wells, fences, barrels, signs, towers, bridges, tileable roads/ground/walls, parallax backgrounds) procedurally with Python + Pillow, exported as individual transparent PNGs plus a preview scene. Use this whenever the user asks for game scenery, cenário, tiles, tilesets, "casa medieval", "árvore", "poço", "rua", environment art, props or background elements for a 2D game, wants new props in the same style/scale as an existing character or earlier assets, or wants a tileable ground/road/wall texture - even if they don't say "pixel art" or "procedural".
---

# Pixel scenery assets

> **Where the scripts live:** `scripts/` and `references/` sit next to this file. If this skill was installed as instructions only (for example saved from claude.ai without its files), the same scripts are in the user's project under `art_tools/`; if they are missing there too, ask the user to attach them.

Draws static game scenery **with code** (Pillow primitives, seeded randomness, a shared palette), not with an image-generation model. Results are crisp, consistent between assets, and easy to vary (change a seed or parameter). Be upfront about the trade-off: the look is clean and somewhat geometric; very ornate or painterly art needs a human artist's retouch.

`scripts/scenery_gen.py` is a complete working example (medieval house, tree, well, tileable cobblestone street, plus a preview scene with a character for scale). Copy it to a working folder and extend it. `references/recipes.md` explains how each asset is built and lists the shared palette and sizes.

This skill pairs with `pixel-sprite-animation` (characters): use the same palette, outline color and scale so assets and characters match.

## Workflow

1. **Pin down the brief** (ask only what's missing, one question at a time): which assets, view (default: side view / front elevation), scale reference (character height in px), style/palette, whether any asset must tile, engine. If the user already has characters, **match their scale and palette** (e.g. a 40 px knight means a ~40 px door, 160 px wide house, 110 px tree, 40-48 px well).
2. **Run the template once** (`python scenery_gen.py <out_dir>`) to confirm the environment, then add or edit `make_<asset>()` functions. Each asset is a function returning an RGBA image.
3. **Build one asset at a time**, render, and look at it **zoomed 3-4x on a flat sky-colored background** (transparency hides flaws). Fix and re-render; expect 1-3 rounds.
4. **Compose a preview scene** with all assets on the street tile and a character for scale. This is the real test of proportions and palette harmony.
5. **QA** with `scripts/check_assets.py` (clipping; tile seams with `--tile`).
6. **Deliver** each asset as its own PNG (+ preview scene + generator script), using the file-delivery tool if the environment has one (otherwise just list the paths), and tell the user: sizes, the anchor/ground convention, which assets tile, and how the scale was chosen.

## Drawing rules that made these assets work

- **Opaque pixels only**, no anti-aliasing, no semi-transparency. Use `rectangle`, `line`, `polygon`, `ellipse`, `point`.
- **Shared palette** with ~4-5 tones per material (stone, wood, plaster, roof, leaves) and one dark outline color. Light from the top-left: highlight the top/left edge of every block, shade the bottom/right.
- **Outline pass at the end** (1 px dark, 4-neighbor) over the whole asset, so silhouettes read on any background. Always leave a 1 px transparent margin on every side for it; ground-standing objects end their solid art at row `H-2` so the outline fits at `H-1`.
- **Texture comes from structure + restrained noise**: random block widths with staggered rows (stone), tile rows with a light top line and dark bottom line (roof), beams with light/dark edges (timber), dithered tone boundaries (foliage), a handful of random specks (plaster, bark). Always seed the RNG so results are reproducible and variations are one parameter away.
- **Compose from layers/back-to-front**: things behind first (chimney before roof, posts before the front wall rim). Use a temp layer + mask when a texture must be clipped to a shape (cylinder well wall).
- **Tileable textures**: draw on a canvas 3 tiles wide using the *same* per-element attributes (including speckles) for every copy, then crop the middle tile. Make each row's element widths sum exactly to the tile width and pre-offset alternate rows. Check by repeating the tile (`check_assets.py --tile`).
- **Scale consistency** matters more than detail: place everything next to the character in the preview and adjust before polishing.
- Reuse building blocks (`stone_wall`, `roof_tiles`, shutters, windows, beams) so new assets automatically share the look.

## Ground and anchor convention

Every ground object is exported with the last solid row at `H-2` and the outline at `H-1`. In the preview, align that row with the same ground row as the character's soles, a few pixels below the top lip of the street tile. Tell the user to anchor sprites at bottom-center (or bottom-left for the house) and offset by that outline row if they want pixel-exact contact with the ground.

## QA checklist

- Zoomed view of each asset: readable silhouette, consistent light direction, no stray transparent holes, nothing cut at the sides or top (`python scripts/check_assets.py *.png`; a single outline pixel on the border is harmless, solid art there is clipped, so move things inward or enlarge the canvas).
- Tiles: `python scripts/check_assets.py --tile street_tile.png` and look for visible seams or an obviously repeating pattern; offer 2-3 variants to alternate if it repeats too noticeably.
- Door/window/furniture sizes make sense next to the character (door clearly taller than the character).
- Palette harmony: view the preview scene, not just single assets.

## When the user provides reference art or an existing tileset

Slice it into tiles/sprites, extract the exact palette (`Counter` of RGBA values) and the outline color, measure typical object sizes, then generate new assets with that palette and scale. Compare side by side with the originals. Be honest that matching a hand-painted style with code is approximate; simple low-resolution pixel art matches best.

## Gotchas learned

- Features that touch the canvas edge lose their outline (the first well had a crank on the right edge): keep 2 px of margin for anything sticking out.
- Roofs need an edge row (dark rim) or they look flat; an eave shadow strip under the roof on the wall below sells the depth.
- A door the same height as the character looks cramped; check against the character before finalizing.
- Multiplying colors for shading creates off-palette tones: fine in small doses (cylinder shading), but prefer explicit palette tones elsewhere.
- Repeating cobbles over long distances look monotonous: provide variations (puddle, crack, drain) to alternate.
