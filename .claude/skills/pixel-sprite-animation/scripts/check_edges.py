"""Report frames whose pixels touch the frame border (= probably clipped).
Usage: python check_edges.py sheet.png [frame_size=64] [cols=6]"""
import sys
from PIL import Image
sheet = Image.open(sys.argv[1]).convert('RGBA'); F = int(sys.argv[2]) if len(sys.argv) > 2 else 64
cols = int(sys.argv[3]) if len(sys.argv) > 3 else sheet.width // F
rows = sheet.height // F; px = sheet.load(); bad = 0
for r in range(rows):
    for c in range(cols):
        hit = [(x, y) for x in (0, F - 1) for y in range(F) if px[c * F + x, r * F + y][3] > 0]
        hit += [(x, y) for y in (0, F - 1) for x in range(F) if px[c * F + x, r * F + y][3] > 0]
        if hit: bad += 1; print(f'row {r} col {c}: touches border at {hit[0]}')
print('clipped frames:', bad)
