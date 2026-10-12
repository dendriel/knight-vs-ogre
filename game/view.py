"""Everything that draws. Uses only simple pygame calls (Surface, blit, fill, draw.rect/circle, font)."""
import json, math, os, random
import pygame
from . import config as C
from .logic import slot_props, slot_boxes

SKY = (122, 178, 224)
DIRT = (70, 54, 46)
OUTLINE = (18, 18, 30)
STRIP_W = 960                      # width of the tileable cloud / hill strips


class View:
    def __init__(self, assets_dir, timing):
        self.timing = timing; self.assets = assets_dir
        self.frames = {}           # (sheet, anim, flipped) -> [6 surfaces]
        for sheet in ('knight', 'ogre', 'vfx'): self._load_sheet(sheet)
        load = lambda n: pygame.image.load(os.path.join(assets_dir, n + '.png')).convert_alpha()
        self.props = {n: load(n) for n in ('medieval_house', 'tree', 'well')}
        self.box = load('box')
        self.pickup_img = {'potion': load('potion'), 'coins': load('coin_bag')}; self.coin_icon = load('coin')
        self.icons = {n: load('icon_' + n) for n in ('armor', 'sword', 'axe', 'bow', 'xbow', 'knife', 'staff')}
        self.proj = {}
        for n in ('arrow', 'bolt', 'knife', 'fireball', 'rock', 'arrow_u45', 'arrow_u90', 'arrow_d45', 'arrow_d90'):
            im = load('proj_' + n); self.proj[(n, False)] = im; self.proj[(n, True)] = pygame.transform.flip(im, True, False)
        self.street = load('street_tile')
        self.street_h = self.street.get_height()
        self.font = pygame.font.Font(None, 16); self.font_big = pygame.font.Font(None, 20)
        self.clouds = self._make_clouds()
        self.hills_far = self._make_hills(70, (98, 156, 156), seed=3, amp=(20, 9, 5))
        self.hills_near = self._make_hills(44, (78, 134, 110), seed=9, amp=(13, 6, 3))
        self.slots = {}; self.boxes = {}

    # ------------------------------------------------------------------ assets
    def _load_sheet(self, sheet):
        img = pygame.image.load(os.path.join(self.assets, f'{sheet}_spritesheet.png')).convert_alpha()
        with open(os.path.join(self.assets, f'{sheet}_spritesheet.json')) as f: anims = list(json.load(f)['animations'])
        for r, name in enumerate(anims):
            row = [img.subsurface((i * 64, r * 64, 64, 64)).copy() for i in range(6)]
            self.frames[(sheet, name, False)] = row
            self.frames[(sheet, name, True)] = [pygame.transform.flip(s, True, False) for s in row]

    def _make_clouds(self):
        s = pygame.Surface((STRIP_W, 90), pygame.SRCALPHA); rnd = random.Random(4)
        for k in range(7):
            cx = 60 + k * (STRIP_W - 120) // 7 + rnd.randint(-20, 20); cy = rnd.randint(22, 60); w = rnd.randint(34, 60)
            for part in range(4):
                ox = int((part - 1.5) * w / 3.2); r = rnd.randint(9, 15) - abs(part - 1) * 2
                pygame.draw.circle(s, (206, 224, 242, 255), (cx + ox, cy + 4), r)
            for part in range(4):
                ox = int((part - 1.5) * w / 3.2); r = rnd.randint(9, 15) - abs(part - 1) * 2
                pygame.draw.circle(s, (244, 250, 255, 255), (cx + ox, cy), r)
            s.fill((0, 0, 0, 0), (cx - w, cy + 14, w * 2, 30))           # flat cloud bottom
        return s

    def _make_hills(self, height, color, seed, amp):
        s = pygame.Surface((STRIP_W, height), pygame.SRCALPHA); rnd = random.Random(seed)
        ph = [rnd.uniform(0, 6.28) for _ in amp]
        for x in range(STRIP_W):
            h = height - 6 - sum(a * (1 + math.sin(2 * math.pi * (k + 1) * (k + 2) * x / STRIP_W + ph[k])) for k, a in enumerate(amp))
            h = int(max(6, min(height, h)))
            s.fill(color + (255,), (x, h, 1, height - h))
        return s

    # ------------------------------------------------------------------ drawing
    def blit_char(self, surf, sheet, anim, idx, wx, cx, flip, oy=0):
        left = int(round(wx - cx)) - (C.ANCHOR_X_FLIP if flip else C.ANCHOR_X)
        surf.blit(self.frames[(sheet, anim, flip)][idx], (left, C.GROUND_Y - 60 + oy))

    def _strip(self, surf, strip, parallax, cx, y):
        off = -int(cx * parallax) % STRIP_W
        surf.blit(strip, (off - STRIP_W, y)); surf.blit(strip, (off, y))

    def draw(self, surf, world, clock_t):
        cx = int(round(world.cam_x())); oy = 0
        if world.shake > 0:
            rnd = random.Random(int(clock_t * 60)); cx += rnd.randint(-2, 2); oy = rnd.randint(-1, 1)
        top = C.GROUND_Y - 3 + oy
        surf.fill(SKY)
        self._strip(surf, self.clouds, 0.15, cx, 14 + oy)
        self._strip(surf, self.hills_far, 0.30, cx, top - self.hills_far.get_height() + 2)
        self._strip(surf, self.hills_near, 0.55, cx, top - self.hills_near.get_height() + 2)
        # ground: tiles repeat every 64 px, aligned with world x
        for x in range(-(cx % 64), C.SCREEN_W + 64, 64): surf.blit(self.street, (x, top))
        surf.fill(DIRT, (0, top + self.street_h, C.SCREEN_W, C.SCREEN_H))
        # scenery of the visible slots
        s0 = math.floor(cx / C.SLOT_W) - 1; s1 = math.floor((cx + C.SCREEN_W) / C.SLOT_W) + 1
        for s in range(s0, s1 + 1):
            if s not in self.slots: self.slots[s] = slot_props(s)
            for name, wx in self.slots[s]:
                img = self.props[name]; surf.blit(img, (wx - cx, C.GROUND_Y - (img.get_height() - 2) + oy))
        # boxes: stacked boxes share their outline row, so level L is drawn L * BOX_H above the ground
        for s in range(s0, s1 + 1):
            if s not in self.boxes: self.boxes[s] = slot_boxes(s)
            for bx, lvl in self.boxes[s]:
                surf.blit(self.box, (bx - cx, C.GROUND_Y + 1 - lvl * C.BOX_H + oy))
        # bodies stay where they fell, then the living fighters (the hero is drawn over the ogre when they overlap)
        for f in world.corpses:
            if -80 < f.x - cx < C.SCREEN_W + 80:
                self.blit_char(surf, f.sheet, f.anim, f.frame_index(self.timing), f.x, cx, f.facing < 0, oy - int(round(f.y)))
        for f in sorted(world.fighters(), key=lambda q: q is not world.hero):
            self.blit_char(surf, f.sheet, f.anim, f.frame_index(self.timing), f.x, cx, f.facing < 0, oy - int(round(f.y)))
        # layer order: scenery -> boxes -> bodies -> fighters -> pickups (in front of the characters) -> effects -> HUD
        for p in world.pickups:                                     # items bob a little once they have landed
            if -40 < p.x - cx < C.SCREEN_W + 40:
                img = self.pickup_img[p.kind]; bob = int(round(1.4 * math.sin(p.t * 4))) if p.y <= 0 else 0
                surf.blit(img, (int(round(p.x)) - cx - img.get_width() // 2,
                                C.GROUND_Y - (img.get_height() - 2) - int(round(p.y)) - bob + oy))
        self._projectiles(surf, world, cx, oy)
        for v in world.vfx:
            if v['t'] >= 0:
                k = int(v['t'] * self.timing['vfx'][v['name']])
                if 0 <= k < 6:
                    self.blit_char(surf, 'vfx', v['name'], k, v['x'], cx, v['flip'], oy - int(round(v.get('y', 0))))
        self._hud(surf, world, clock_t)

    def _projectiles(self, surf, world, cx, oy):
        for p in world.projectiles:
            sx = int(round(p.x)) - cx
            if not -20 < sx < C.SCREEN_W + 20: continue
            gy = C.GROUND_Y - int(round(p.base_y if p.kind == 'straight' else p.ty)) + oy
            if p.kind == 'lob':                                    # landing marker on the ground + shadow
                mx = int(round(p.tx)) - cx
                r = int(p.radius) + 6
                col = (230, 80, 70) if int(world.time * 8) % 2 else (255, 190, 90)
                surf.fill(col, (mx - r, gy - 1, 2 * r, 1)); surf.fill(col, (mx - r, gy + 1, 2 * r, 1))
                u = min(1.0, p.t / p.flight)
                name = p.sprite if p.sprite != 'arrow' else ('arrow_u90' if u < .25 else 'arrow_u45' if u < .45 else
                                                              'arrow' if u < .55 else 'arrow_d45' if u < .75 else 'arrow_d90')
                img = self.proj[(name, p.facing < 0)]
                surf.blit(img, (sx - img.get_width() // 2, gy - int(p.height) - img.get_height() // 2))
            else:
                img = self.proj[(p.sprite, p.facing < 0)]
                surf.fill((18, 18, 30), (sx - 3, gy, 6, 1))        # small shadow under the shot
                surf.blit(img, (sx - img.get_width() // 2, gy - int(p.height) - img.get_height() // 2))

    # ------------------------------------------------------------------ HUD
    def _text(self, surf, s, x, y, color=(255, 255, 255), font=None, align='left'):
        font = font or self.font
        w = font.size(s)[0] if hasattr(font, 'size') else 0
        if align == 'right': x -= w
        surf.blit(font.render(s, False, (0, 0, 0)), (x + 1, y + 1)); surf.blit(font.render(s, False, color), (x, y))

    def _bar(self, surf, x, y, hp, max_hp, color, align):
        w, h = 140, 12
        if align == 'right': x -= w
        pygame.draw.rect(surf, OUTLINE, (x - 2, y - 2, w + 4, h + 4))
        pygame.draw.rect(surf, (60, 28, 36), (x, y, w, h))
        fill = int(w * hp / max_hp)
        if fill > 0:
            fx = x if align == 'left' else x + w - fill
            pygame.draw.rect(surf, color, (fx, y, fill, h))
            pygame.draw.rect(surf, tuple(min(255, c + 60) for c in color), (fx, y, fill, 3))

    def _small_bar(self, surf, x, y, w, h, frac, color, back=(30, 32, 52)):
        pygame.draw.rect(surf, OUTLINE, (x - 1, y - 1, w + 2, h + 2))
        pygame.draw.rect(surf, back, (x, y, w, h))
        fill = int(round(w * max(0.0, min(1.0, frac))))
        if fill > 0: pygame.draw.rect(surf, color, (x, y, fill, h))

    def _hud(self, surf, world, t):
        """Hero panel in the left corner (slots stack top to bottom and only exist when their feature does), enemy
        panel in the right corner like a fighting game. Positions live in config.HUD."""
        h = world.hero; P = C.HUD; feats = world.features
        self._text(surf, 'HERÓI', *P['name'], (230, 240, 255), self.font_big)
        self._bar(surf, P['hp_bar'][0], P['hp_bar'][1], h.hp, h.max_hp, (84, 200, 96), 'left')
        self._text(surf, f'{h.hp}', *P['hp_num'], font=self.font_big)
        y = P['hp_bar'][1] + 16
        x0 = P['hp_bar'][0]
        if 'armor' in feats:                                     # blue bar under the life bar
            self._small_bar(surf, x0, y, 140, 6, h.armor / max(1, h.armor_max), (96, 150, 235))
            if h.armor > 0:
                surf.blit(self.icons['armor'], (x0 + 146, y - 3))
                self._text(surf, f'{h.armor}', x0 + 160, y - 3, (150, 190, 255))
            y += 10
        if 'combo' in feats:                                     # combo meter; blinks when full
            full = world.combo >= C.COMBO_BAR_MAX
            col = (255, 230, 90) if full and int(t * 6) % 2 else (240, 150, 60)
            self._small_bar(surf, x0, y, 140, 5, world.combo / C.COMBO_BAR_MAX, col)
            y += 9
        x = x0                                                   # equipment row: weapon - potions - gold
        if 'weapon' in feats:
            w = h.weapon
            surf.blit(self.icons[w['id'] if w else 'sword'], (x, y - 1))
            if w and w.get('durability') is not None:
                d = w['durability'] / 100.0
                self._small_bar(surf, x + 15, y + 3, 30, 4, d, (230, 200, 90) if d > .25 else (230, 80, 70))
            else:
                self._text(surf, 'inf', x + 15, y, (200, 210, 230))
            x += 58
        if 'potions' in feats:
            surf.blit(self.pickup_img['potion'], (x, y - 3))
            self._text(surf, f'{world.potions}/{C.POTION_MAX_STOCK}', x + 15, y, (255, 150, 150))
            x += 58
        surf.blit(self.coin_icon, (x, y)); self._text(surf, f'{world.gold}', x + 12, y, (255, 214, 80))
        self._text(surf, f'Derrotas: {world.hero_deaths}', x0, y + 15, (255, 220, 150))
        o = world.ogre                                           # enemy panel (the nearest / current enemy)
        if o is not None:
            self._text(surf, 'OGRO', C.SCREEN_W - 10, 6, (255, 220, 200), self.font_big, 'right')
            self._bar(surf, C.SCREEN_W - 10, 20, o.hp, o.max_hp, (222, 80, 60), 'right')
            self._text(surf, f'{o.hp}', C.SCREEN_W - 156, 18, font=self.font_big, align='right')
        self._text(surf, f'Derrotas: {world.ogre_deaths}', C.SCREEN_W - 10, 38, (255, 220, 150), align='right')
        if t < 8:
            self._center(surf, 'SETAS ou A D: andar   ESPACO: pular   MOUSE ESQ: atacar   ESC: menu', C.SCREEN_H - 14)

    # public helpers used by the scenes (T05)
    def text(self, surf, s, x, y, color=(255, 255, 255), font=None, align='left'): self._text(surf, s, x, y, color, font, align)
    def center(self, surf, s, y, color=(255, 255, 255), font=None):
        font = font or self.font; w = font.size(s)[0]; self._text(surf, s, (C.SCREEN_W - w) // 2, y, color, font)
    def title(self, surf, s, y): self.center(surf, s, y, (255, 230, 150), self.font_big)

    def dim(self, surf, alpha=150):
        ov = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA); ov.fill((8, 8, 20, alpha)); surf.blit(ov, (0, 0))

    def draw_menu(self, surf, menu):
        for i, (label, action, enabled) in enumerate(menu.items):
            r = menu.rect(i); sel = i == menu.index
            pygame.draw.rect(surf, OUTLINE, (r.x - 1, r.y - 1, r.w + 2, r.h + 2))
            pygame.draw.rect(surf, (74, 92, 140) if sel and enabled else (38, 40, 62), r.tuple())
            col = (255, 255, 255) if enabled else (120, 120, 140)
            w = self.font_big.size(label)[0]
            self._text(surf, label, r.x + (r.w - w) // 2, r.y + 3, col, self.font_big)

    def _center(self, surf, s, y):
        w = self.font.size(s)[0]; self._text(surf, s, (C.SCREEN_W - w) // 2, y)
