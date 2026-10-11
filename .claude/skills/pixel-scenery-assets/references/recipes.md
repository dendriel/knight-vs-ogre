# Recipes used for the medieval set (side view, knight scale = ~41 px tall)

All coordinates are for the canvas sizes below; the last solid row of a ground object is H-2 (row H-1 is the outline).

## Sizes (same scale as a 64x64 knight)
house 160x160 | tree 112x128 | well 48x64 | street tile 64x40 (tileable in x)
Door height should clear the character by a few px (the first house had a 41 px door for a 41 px knight: tight).

## Shared palette (keep it across all assets and the characters)
outline (18,18,30); stone 70/88/112/132/180 greys-blue; wood (74,48,30) (116,74,44) (156,104,60);
plaster (196,182,154) (224,212,186) (164,150,126); roof (104,34,40) (156,54,52) (198,86,64) (174,64,56);
leaves (28,66,48) (50,108,58) (88,152,72) (146,194,100); glass (110,160,196) + highlight (204,232,246).
Light comes from the top-left: highlight on top/left edges, shade on bottom/right.

## Building blocks (see scripts/scenery_gen.py)
- `stone_wall`: mortar-colored rect, then rows of blocks (random width 10-17, offset every other row), each with a 1px top highlight and bottom shade.
- `roof_tiles`: triangle by apex/base/half-width; rows of `rowh` px, light top line, dark bottom line, dark vertical gap every `tw` px staggered per row, ~1 in 5 tiles in a slightly different tone, dark rim on the slanted edges.
- Half-timbering: plaster fill with random specks, beams as rects with light left/top edge and dark right/bottom edge, X braces as two lines (dark width 5 under mid width 3).
- Jetty: dark beam under the upper floor + small triangular corbels.
- Windows: frame rect, glass, 1px cross muntin, 2-px highlight in the top-left corner, shutters as wood rects with a darker plank line; flower box = wood rect + 1px green tufts + colored pixels.
- Door: stone arch (ellipse + rect) behind a wood arch (smaller ellipse + rect), vertical plank lines, iron straps, gold handle.
- Tree canopy: 8 overlapping circles drawn back to front; each circle = 4 nested ellipses (dark, mid, light, highlight) shifted up-left; then dither boundaries between tones (30% chance to take the left/upper neighbor's tone); darken trunk pixels under the canopy; draw trunk with flared base and light/mid/dark vertical bands plus random dark bark streaks.
- Well: stone texture drawn on a temp layer and masked by a cylinder (rect + bottom ellipse), side-shaded by multiplying brightness, rim ellipse + water ellipse on top, posts planted on the rim, windlass log with rope, bucket, tiled roof.
- Street tile: draw 3 copies side by side on a 3W canvas using the *same* per-stone attributes (including speckles), then crop the middle W. Row widths must each sum to W; alternate rows are pre-offset.

## Ideas for the next assets
fence, barrel, crate, sign, bridge, ruins, tower, castle wall, market stall, torch, grass/dirt top tiles, background layers (hills, distant trees) for parallax.
