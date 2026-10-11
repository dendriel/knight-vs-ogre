"""QA helper for static pixel-art scenery.
Usage:
  python check_assets.py a.png b.png ...        -> reports side/top clipping (outline px on the border are OK)
  python check_assets.py --tile tile.png [n=4]  -> writes <tile>_seam_check.png (tile repeated n times, 3x zoom)
"""
import sys
from PIL import Image

def clipping(path):
    im = Image.open(path).convert('RGBA'); px = im.load(); w, h = im.size
    hits = [(x, y) for x in (0, w - 1) for y in range(h) if px[x, y][3] > 0] + [(x, 0) for x in range(w) if px[x, 0][3] > 0]
    # last row is expected to hold the bottom outline of ground-standing objects
    bottom = sum(1 for x in range(w) if px[x, h - 1][3] > 0)
    print(f'{path}: {w}x{h}, side/top border px = {len(hits)}, bottom-row px = {bottom}')
    if hits: print('   first hits:', hits[:5], '(a lone outline pixel at the edge is harmless; solid colors are clipped art)')

if sys.argv[1] == '--tile':
    t = Image.open(sys.argv[2]).convert('RGBA'); n = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = Image.new('RGBA', (t.width * n, t.height))
    for k in range(n): out.paste(t, (k * t.width, 0))
    p = sys.argv[2].rsplit('.', 1)[0] + '_seam_check.png'
    out.resize((out.width * 3, out.height * 3), Image.NEAREST).save(p); print('wrote', p)
else:
    for p in sys.argv[1:]: clipping(p)
