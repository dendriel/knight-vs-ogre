"""A tiny stand-in for pygame built on Pillow. It only exists so the game code (main.py/view.py) can be run and
recorded in an environment without pygame or a screen. It implements just the calls the game uses."""
import types
from PIL import Image, ImageDraw, ImageFont

SRCALPHA = 1; RESIZABLE = 2; FULLSCREEN = 4; BLEND_RGB_MULT = 4096
QUIT, KEYDOWN, KEYUP = 256, 768, 769


class Event:
    """stand-in for pygame.event.Event: any keyword becomes an attribute (key, pos, button...)"""
    def __init__(self, type, **kw): self.type = type; self.__dict__.update(kw)

K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_d, K_w, K_s, K_SPACE, K_ESCAPE, K_F11, K_m = range(1000, 1012)
K_RETURN, K_1, K_2 = range(1012, 1015)
MOUSEBUTTONDOWN, MOUSEMOTION = 1025, 1024
MOUSE_RIGHT = 'mouse-right'   # put it in PRESSED to simulate the right button held
MOUSE_POS = [0, 0]
PRESSED = set(); EVENTS = []; FLIP_HOOK = [None]
MOUSE_LEFT = 'mouse-left'   # put it in PRESSED to simulate the left button held


def _rgba(c): return tuple(c) + (255,) if len(c) == 3 else tuple(c)


class Surface:
    def __init__(self, size, flags=0):
        if isinstance(size, Image.Image): self.img = size
        else: self.img = Image.new('RGBA', tuple(size), (0, 0, 0, 0) if flags & SRCALPHA else (0, 0, 0, 255))
    def get_size(self): return self.img.size
    def get_width(self): return self.img.width
    def get_height(self): return self.img.height
    def convert_alpha(self): return self
    def copy(self): return Surface(self.img.copy())
    def subsurface(self, rect): x, y, w, h = rect; return Surface(self.img.crop((x, y, x + w, y + h)))
    def blit(self, src, dest): self.img.paste(src.img, (int(dest[0]), int(dest[1])), src.img)
    def fill(self, color, rect=None, special_flags=0):
        if special_flags == BLEND_RGB_MULT:                      # multiply RGB, keep alpha (used for elite tints)
            r, g, b, a = self.img.split()
            m = [i.point(lambda v, k=c: v * k // 255) for i, c in zip((r, g, b), color[:3])]
            self.img = Image.merge('RGBA', (*m, a)); return
        if rect is None: self.img.paste(_rgba(color), (0, 0, self.img.width, self.img.height))
        else:
            x, y, w, h = rect; x, y = int(x), int(y)
            if w > 0 and h > 0: self.img.paste(_rgba(color), (x, y, x + int(w), y + int(h)))


def _load(path): return Surface(Image.open(path).convert('RGBA'))
def _tflip(s, fx, fy):
    im = s.img
    if fx: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if fy: im = im.transpose(Image.FLIP_TOP_BOTTOM)
    return Surface(im)
def _scale(s, size, dest=None): return Surface(s.img.resize(tuple(size), Image.NEAREST))
def _rect(surf, color, rect, width=0):
    x, y, w, h = [int(v) for v in rect]; ImageDraw.Draw(surf.img).rectangle([x, y, x + w - 1, y + h - 1], fill=_rgba(color))
def _circle(surf, color, center, r):
    cx, cy = center; ImageDraw.Draw(surf.img).ellipse([cx - r, cy - r, cx + r, cy + r], fill=_rgba(color))


class Font:
    def __init__(self, name, size): self.f = ImageFont.load_default(size=int(size * .8))
    def size(self, text): return (int(self.f.getlength(text)) + 3, int(self.f.size * 1.5))
    def render(self, text, aa, color):
        w, h = self.size(text); im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = '1'
        d.text((0, h - 5), text, font=self.f, fill=_rgba(color), anchor='ls'); return Surface(im)


class _Keys:
    def __getitem__(self, k): return k in PRESSED


class Clock:
    def tick(self, fps=0): return 16


_state = {'screen': None}
def _set_mode(size, flags=0):
    size = (1920, 1080) if tuple(size) == (0, 0) else tuple(size)
    _state['screen'] = Surface(size); return _state['screen']
def _flip():
    if FLIP_HOOK[0]: FLIP_HOOK[0](_state['screen'])
def _events():
    out = list(EVENTS); EVENTS.clear(); return out

N = types.SimpleNamespace
module = N(BLEND_RGB_MULT=BLEND_RGB_MULT, SRCALPHA=SRCALPHA, RESIZABLE=RESIZABLE, FULLSCREEN=FULLSCREEN, QUIT=QUIT, KEYDOWN=KEYDOWN, KEYUP=KEYUP,
           K_LEFT=K_LEFT, K_RIGHT=K_RIGHT, K_UP=K_UP, K_DOWN=K_DOWN, K_a=K_a, K_d=K_d, K_w=K_w, K_s=K_s,
           K_SPACE=K_SPACE, K_ESCAPE=K_ESCAPE, K_F11=K_F11, K_m=K_m, K_RETURN=K_RETURN, K_1=K_1, K_2=K_2,
           MOUSEBUTTONDOWN=MOUSEBUTTONDOWN, MOUSEMOTION=MOUSEMOTION, Surface=Surface,
           init=lambda: None, quit=lambda: None,
           display=N(set_caption=lambda s: None, set_mode=_set_mode, get_surface=lambda: _state['screen'], flip=_flip),
           image=N(load=_load), transform=N(flip=_tflip, scale=_scale),
           draw=N(rect=_rect, circle=_circle), font=N(Font=Font), time=N(Clock=Clock),
           event=N(get=_events), key=N(get_pressed=lambda: _Keys()),
           mouse=N(get_pressed=lambda: (MOUSE_LEFT in PRESSED, False, MOUSE_RIGHT in PRESSED),
                   get_pos=lambda: tuple(MOUSE_POS)))
