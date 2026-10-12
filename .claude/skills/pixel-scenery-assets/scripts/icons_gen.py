"""HUD icons (T06): 12x12 equipment icons drawn from small character grids, same outline/palette as the scenery.

    python icons_gen.py [out_dir]     -> icon_armor, icon_sword, icon_axe, icon_bow, icon_xbow, icon_knife, icon_staff
"""
import os, sys
from PIL import Image

out = sys.argv[1] if len(sys.argv) > 1 else './icons'
os.makedirs(out, exist_ok=True)


def C(r, g, b): return (r, g, b, 255)


OUT = C(18, 18, 30)
PAL = {'O': OUT,
       'S': C(214, 224, 238), 's': C(150, 164, 186), 'H': C(252, 253, 255),     # steel: light, shade, highlight
       'W': C(134, 86, 48), 'w': C(92, 58, 34),                                 # wood
       'L': C(116, 74, 44), 'G': C(238, 192, 72),                               # leather, gold
       'B': C(84, 120, 200), 'b': C(52, 78, 150), 'h': C(150, 184, 240),        # blue armor
       'R': C(176, 38, 48), 'F': C(255, 190, 70), 'f': C(232, 100, 40)}         # red, fire


def make(rows):
    w = max(len(r) for r in rows); im = Image.new('RGBA', (w, len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in PAL: im.putpixel((x, y), PAL[ch])
    return im


ICONS = {
    'armor': ["..OO....OO..",
              ".OBBOOOOBBO.",
              "OBhBBBBBBbBO",
              "OBBBBBBBBBbO",
              ".OBBBGGBBbO.",
              ".OBBBGGBBbO.",
              ".OBBBBBBBbO.",
              "..OBBBBBbO..",
              "..OBBBBbbO..",
              "...OBBbbO...",
              "....OBbO....",
              ".....OO....."],
    'sword': ["..........OO",
              ".........OSO",
              "........OSHO",
              ".......OSHO.",
              "......OSHO..",
              ".....OSHO...",
              "..O.OSHO....",
              "..OGOHO.....",
              "...OGO......",
              "..OLOGO.....",
              ".OLO.OO.....",
              "..O........."],
    'axe': ["....OOOO....",
            "...OSSHSO...",
            "..OSSHSssO..",
            "..OSHSOsO...",
            "...OSOWO....",
            "....OWwO....",
            "....OWO.....",
            "...OWwO.....",
            "...OWO......",
            "..OWwO......",
            "..OLO.......",
            "...O........"],
    'bow': ["...OOO......",
            "..OWWwO.....",
            ".OWwOOwO....",
            ".OWO..SO....",
            "OWwO..sO....",
            "OWO...SO....",
            "OWO...sO....",
            "OWwO..SO....",
            ".OWO..SO....",
            ".OWwOOwO....",
            "..OWWwO.....",
            "...OOO......"],
    'xbow': ["............",
             "..OO....OO..",
             ".OWwO..OwWO.",
             ".OWwOOOOwWO.",
             "..OWSSSSWO..",
             "...OOLWOO...",
             "....OLWO....",
             "....OLWO....",
             "....OLWO....",
             ".....OLO....",
             ".....OO.....",
             "............"],
    'knife': ["..........OO",
              ".........OSO",
              "........OSHO",
              ".......OSHO.",
              "......OSsO..",
              ".....OSsO...",
              "....OSsO....",
              "..OOGOO.....",
              ".OLGOO......",
              ".OLO........",
              "..O.........",
              "............"],
    'staff': ["....OOOO....",
              "...OFffFO...",
              "..OFfRRfFO..",
              "..OfRFFRfO..",
              "..OFfRRfFO..",
              "...OFffFO...",
              "....OWwO....",
              "....OWO.....",
              "...OWwO.....",
              "...OWO......",
              "..OWwO......",
              "...OO......."],
}
for name, rows in ICONS.items():
    make(rows).save(f'{out}/icon_{name}.png')
print('ok', len(ICONS))
