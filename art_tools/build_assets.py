"""Regenerates every sprite sheet, atlas and scenery PNG into ../assets, then (optionally) the demo GIFs.

    python build_assets.py            # rebuild assets
    python build_assets.py --gifs     # ...and also write demo GIFs to ../out
    python build_assets.py --check    # only verify that ../assets matches what the generators produce (no writes)

Needs Pillow:  pip install -r ../requirements-art.txt
Row order of the sheets is part of the contract with the game (see ../CLAUDE.md): only append new animations at the end.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'assets')
SHEETS = ['knight_spritesheet.png', 'knight_spritesheet.json', 'knight_axe_spritesheet.png', 'knight_axe_spritesheet.json',
          'knight_bow_spritesheet.png', 'knight_bow_spritesheet.json', 'knight_xbow_spritesheet.png',
          'knight_xbow_spritesheet.json', 'ogre_spritesheet.png', 'ogre_spritesheet.json',
          'vfx_spritesheet.png', 'vfx_spritesheet.json']
SCENERY = ['tree.png', 'medieval_house.png', 'well.png', 'street_tile.png', 'box.png',
           'potion.png', 'coin_bag.png', 'coin.png',
           'proj_arrow.png', 'proj_bolt.png', 'proj_knife.png', 'proj_fireball.png', 'proj_rock.png',
           'proj_arrow_u45.png', 'proj_arrow_u90.png', 'proj_arrow_d45.png', 'proj_arrow_d90.png',
           'icon_armor.png', 'icon_sword.png', 'icon_axe.png', 'icon_bow.png', 'icon_xbow.png', 'icon_knife.png',
           'icon_staff.png']


def same(a, b):
    """PNGs are compared by pixels (file bytes can differ with the encoder); other files by content."""
    if a.endswith('.png'):
        from PIL import Image, ImageChops
        ia, ib = Image.open(a).convert('RGBA'), Image.open(b).convert('RGBA')
        return ia.size == ib.size and ImageChops.difference(ia, ib).getbbox() is None
    return open(a, 'rb').read() == open(b, 'rb').read()


def run(script, out):
    subprocess.run([sys.executable, os.path.join(HERE, script), out], cwd=HERE, check=True, stdout=subprocess.DEVNULL)


def main():
    check = '--check' in sys.argv
    tmp = tempfile.mkdtemp(prefix='ko_art_')
    try:
        for g in ('knight_gen.py', 'ogre_gen.py', 'vfx_gen.py', 'scenery_gen.py', 'proj_gen.py', 'icons_gen.py'): run(g, tmp)
        bad = []
        for name in SHEETS + SCENERY:
            src = os.path.join(tmp, name); dst = os.path.join(ASSETS, name)
            if not os.path.exists(src): bad.append(name + ' (not generated)'); continue
            if check:
                if not os.path.exists(dst) or not same(src, dst): bad.append(name)
            elif os.path.exists(dst) and same(src, dst): continue          # identical pixels: leave the file alone
            else:
                shutil.copyfile(src, dst); print('wrote', os.path.normpath(dst))
        if check:
            print('assets match the generators' if not bad else 'DIFFERENT: ' + ', '.join(bad)); sys.exit(1 if bad else 0)
        if '--gifs' in sys.argv:
            out = os.path.join(HERE, '..', 'out'); os.makedirs(out, exist_ok=True)
            subprocess.run([sys.executable, os.path.join(HERE, 'demo_gif.py'), ASSETS, ASSETS, out], cwd=HERE, check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
