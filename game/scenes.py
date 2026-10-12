"""Screens (T05). The game keeps a stack of scenes; only the top one gets events and updates, and every scene may draw
the ones below it first (the pause menu is drawn over the frozen game). Scenes talk to the `Game` object in main.py."""
import pygame
from . import config as C
from .ui import Menu


class Scene:
    transparent = False                 # True: the scene below is drawn first (overlays)
    def handle_event(self, e, game): pass
    def update(self, dt, game): pass
    def draw(self, surf, game): pass


def key_pressed(e, *keys): return e.type == pygame.KEYDOWN and e.key in keys


class SelectScene(Scene):
    """Class selection (T45): cards side by side with the idle frame, the attributes and the three attacks. <-/-> + Enter
    or a click on a card; Esc goes back to the title. `next_start` = stage id / 'endless' to start with the choice."""
    CARD_W, CARD_H, GAP = 108, 172, 8

    def __init__(self, game, next_start):
        from .logic import CLASSES, FIGHTER_DEFS
        self.next_start = next_start; self.classes = list(CLASSES); self.index = 0; self.hover = None
        n = len(self.classes); total = n * self.CARD_W + (n - 1) * self.GAP
        self.x0 = (C.SCREEN_W - total) // 2; self.y0 = 32
        self.defs = [FIGHTER_DEFS[c] for c in self.classes]
        self.portraits = []
        for c, d in zip(self.classes, self.defs):             # idle frame 0, enlarged 3x with nearest-neighbour scaling
            frame = game.view.frames[(d['sheet'], 'idle', False)][0]
            self.portraits.append(pygame.transform.scale(frame.subsurface((12, 6, 40, 54)).copy(), (80, 108)))
        self.index = self.classes.index(game.hero_class) if game.hero_class in self.classes else 0

    def rect(self, i):
        from .ui import Rect
        return Rect(self.x0 + i * (self.CARD_W + self.GAP), self.y0, self.CARD_W, self.CARD_H)

    def choose(self, game):
        game.hero_class = self.classes[self.index]; game.start(self.next_start)

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_LEFT, pygame.K_a): self.index = (self.index - 1) % len(self.classes)
        elif key_pressed(e, pygame.K_RIGHT, pygame.K_d): self.index = (self.index + 1) % len(self.classes)
        elif key_pressed(e, pygame.K_RETURN, pygame.K_SPACE): self.choose(game)
        elif key_pressed(e, pygame.K_ESCAPE): game.to_title()
        elif e.type == pygame.MOUSEMOTION:
            p = game.to_internal(e.pos)
            for i in range(len(self.classes)):
                if self.rect(i).contains(p): self.index = i; self.hover = i; return
            self.hover = None
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            p = game.to_internal(e.pos)
            for i in range(len(self.classes)):
                if self.rect(i).contains(p): self.index = i; self.choose(game); return

    def draw(self, surf, game):
        v = game.view
        surf.fill((26, 30, 48))
        v.title(surf, 'ESCOLHA SUA CLASSE', 14)
        labels = (('Vida', 'vida'), ('Vel.', 'vel'), ('Dano', 'dano'), ('Alc.', 'alcance'))
        for i, d in enumerate(self.defs):
            r = self.rect(i); sel = i == self.index
            pygame.draw.rect(surf, (255, 224, 120) if sel else (18, 18, 30), (r.x - 2, r.y - 2, r.w + 4, r.h + 4))
            pygame.draw.rect(surf, (52, 60, 96) if sel else (38, 42, 66), r.tuple())
            surf.blit(self.portraits[i], (r.x + (r.w - 80) // 2, r.y + 4))
            v.text(surf, d['label'], r.x + (r.w - v.font_big.size(d['label'])[0]) // 2, r.y + 114, (255, 236, 170), v.font_big)
            for k, (lab, key) in enumerate(labels):
                yy = r.y + 132 + k * 9
                v.text(surf, lab, r.x + 4, yy - 3, (200, 208, 230))
                for j in range(5):
                    col = (240, 200, 90) if j < d['stats'][key] else (60, 64, 88)
                    surf.fill(col, (r.x + 40 + j * 12, yy, 10, 4))
        d = self.defs[self.index]
        for k, line in enumerate(zip(('Ataque', 'Botao dir.', 'Especial'), d['card'])):
            v.text(surf, f'{line[0]}: {line[1]}', self.x0, self.y0 + self.CARD_H + 8 + k * 12, (235, 240, 255))
        v.center(surf, '<- ->: escolher   Enter / clique: jogar   Esc: voltar', C.SCREEN_H - 14, (180, 190, 215))


class TitleScene(Scene):
    """Start screen (T30): campaign (the three stages), the endless mode, controls, quit."""
    def __init__(self):
        self.menu = Menu([('Campanha', 'campaign', True), ('Modo infinito', 'endless', True),
                          ('Ver comandos', 'controls', True), ('Sair', 'quit', True)],
                         x=(C.SCREEN_W - 150) // 2, y=108, w=150, row_h=22)

    def act(self, action, game):
        if action == 'campaign': game.replace(SelectScene(game, 'stage1'))
        elif action == 'endless': game.replace(SelectScene(game, 'endless'))
        elif action == 'controls': game.push(ControlsScene())
        elif action == 'quit': game.running = False

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_UP, pygame.K_w): self.menu.move(-1)
        elif key_pressed(e, pygame.K_DOWN, pygame.K_s): self.menu.move(1)
        elif key_pressed(e, pygame.K_RETURN): self.act(self.menu.current(), game)
        elif e.type == pygame.MOUSEMOTION: self.menu.mouse_move(game.to_internal(e.pos))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            a = self.menu.click(game.to_internal(e.pos))
            if a: self.act(a, game)

    def draw(self, surf, game):
        game.view.draw(surf, game.world, 0.0, hud=False)        # the frozen world is the backdrop
        game.view.dim(surf, 120)
        game.view.title(surf, 'KNIGHT VS OGRE', 60)
        game.view.draw_menu(surf, self.menu)


class PlayScene(Scene):
    """The game itself: forwards input to the world; Esc opens the pause menu."""
    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_ESCAPE): game.push(PauseScene())

    def update(self, dt, game):
        game.world.update(dt, game.inputs())
        game.after_world_update()

    def draw(self, surf, game):
        game.view.draw(surf, game.world, game.t)


class PauseScene(Scene):
    """Esc menu: Continuar - Ver comandos - Reiniciar fase - Sair. The world and its clock stay frozen underneath."""
    transparent = True

    def __init__(self):
        self.menu = Menu([('Continuar', 'resume', True), ('Ver comandos', 'controls', True),
                          ('Reiniciar fase', 'restart', True), ('Sair', 'quit', True)],
                         x=(C.SCREEN_W - 150) // 2, y=100, w=150, row_h=22)

    def act(self, action, game):
        if action == 'resume': game.pop()
        elif action == 'controls': game.push(ControlsScene())
        elif action == 'restart': game.restart_stage()
        elif action == 'quit': game.running = False

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_ESCAPE): game.pop()
        elif key_pressed(e, pygame.K_UP, pygame.K_w): self.menu.move(-1)
        elif key_pressed(e, pygame.K_DOWN, pygame.K_s): self.menu.move(1)
        elif key_pressed(e, pygame.K_RETURN): self.act(self.menu.current(), game)
        elif e.type == pygame.MOUSEMOTION: self.menu.mouse_move(game.to_internal(e.pos))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            a = self.menu.click(game.to_internal(e.pos))
            if a: self.act(a, game)

    def draw(self, surf, game):
        game.view.dim(surf)
        game.view.title(surf, 'PAUSADO', 70)
        game.view.draw_menu(surf, self.menu)


class DefeatScene(Scene):
    """The hero fell in a stage (T37): pay REVIVE_COST gold to get up where he fell, or restart the stage."""
    transparent = True

    def __init__(self, game):
        w = game.world
        self.menu = Menu([(f'Renascer aqui - {C.REVIVE_COST} ouro', 'revive', w.gold >= C.REVIVE_COST),
                          ('Reiniciar a fase', 'restart', True), ('Menu inicial', 'title', True)],
                         x=(C.SCREEN_W - 190) // 2, y=112, w=190, row_h=22)
        self.menu.index = 0 if w.gold >= C.REVIVE_COST else 1

    def act(self, action, game):
        if action == 'revive':
            if game.world.revive(): game.pop()
        elif action == 'restart': game.restart_stage()
        elif action == 'title': game.to_title()

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_UP, pygame.K_w): self.menu.move(-1)
        elif key_pressed(e, pygame.K_DOWN, pygame.K_s): self.menu.move(1)
        elif key_pressed(e, pygame.K_RETURN): self.act(self.menu.current(), game)
        elif e.type == pygame.MOUSEMOTION: self.menu.mouse_move(game.to_internal(e.pos))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            a = self.menu.click(game.to_internal(e.pos))
            if a: self.act(a, game)

    def draw(self, surf, game):
        game.view.dim(surf, 150)
        game.view.title(surf, 'DERROTA', 70)
        w = game.world
        if w.gold < C.REVIVE_COST:
            game.view.center(surf, f'Ouro: {w.gold}  (faltam {C.REVIVE_COST - w.gold} para renascer)', 92, (255, 190, 150))
        else:
            game.view.center(surf, f'Ouro: {w.gold}', 92, (255, 214, 80))
        game.view.draw_menu(surf, self.menu)


class ShopScene(Scene):
    """Shop between stages (T50): spend the run's gold on potions, armor, pickup weapons and bombs, then go
    on to `next_stage`. Purchases change `run` (gold, potions, weapon, armor, bombs); it is what the stage starts with."""
    def __init__(self, game, next_stage, run):
        self.next_stage = next_stage; self.run = dict(run); self.msg = ''
        self.cls = game.hero_class
        self.menu = Menu(self._items(), x=(C.SCREEN_W - 260) // 2, y=58, w=260, row_h=20)
        self.menu.index = 0

    # item id -> (label, price, can buy?)
    def _entries(self):
        r = self.run; P = C.SHOP_PRICES; knight = True                       # every class can use the pickup weapons now
        out = [('potion', f"Pocao de vida  ({r['potions']}/{C.POTION_MAX_STOCK})", P['potion'], r['potions'] < C.POTION_MAX_STOCK),
               ('armor', f"Armadura  ({r['armor']}/{C.ARMOR_MAX})", P['armor'], r['armor'] < C.ARMOR_MAX),
               ('bomb', f"Bomba, tecla 2  ({r.get('bombs', 0)}/{C.BOMB_MAX_STOCK})", P['bomb'], r.get('bombs', 0) < C.BOMB_MAX_STOCK)]
        if knight:
            have = r['weapon']['id'] if r.get('weapon') else None
            for wid, name in (('axe', 'Machado'), ('bow', 'Arco'), ('xbow', 'Besta')):
                out.append((wid, f"{name}" + ('  (equipado)' if have == wid else ''), P[wid], True))
        return out

    def _items(self):
        items = []
        for iid, label, price, ok in self._entries():
            items.append((f'{label}   {price}', iid, ok and self.run['gold'] >= price))
        items.append(('Continuar', 'continue', True))
        return items

    def buy(self, iid, game):
        P = C.SHOP_PRICES; r = self.run
        if iid == 'continue': game.start(self.next_stage, self.run); return
        if r['gold'] < P[iid]: return
        r['gold'] -= P[iid]
        if iid == 'potion': r['potions'] += 1
        elif iid == 'armor': r['armor'] = C.ARMOR_MAX
        elif iid == 'bomb': r['bombs'] = r.get('bombs', 0) + 1
        else: r['weapon'] = dict(id=iid, durability=C.WEAPON_DURABILITY)
        game.shop_log.append(iid)
        keep = self.menu.index; self.menu.items = self._items(); self.menu.index = keep
        if not self.menu.items[keep][2]: self.menu.move(1)

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_UP, pygame.K_w): self.menu.move(-1)
        elif key_pressed(e, pygame.K_DOWN, pygame.K_s): self.menu.move(1)
        elif key_pressed(e, pygame.K_RETURN): self.buy(self.menu.current(), game) if self.menu.current() else None
        elif e.type == pygame.MOUSEMOTION: self.menu.mouse_move(game.to_internal(e.pos))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            a = self.menu.click(game.to_internal(e.pos))
            if a: self.buy(a, game)

    def draw(self, surf, game):
        v = game.view
        surf.fill((30, 28, 44))
        v.title(surf, 'LOJA', 14)
        v.center(surf, f"Ouro: {self.run['gold']}", 34, (255, 214, 80), v.font_big)
        v.draw_menu(surf, self.menu)
        v.center(surf, 'Cima/Baixo + Enter ou clique: comprar    Continuar: seguir para a fase', C.SCREEN_H - 14, (180, 190, 215))


class SummaryScene(Scene):
    """Stage completed (T31): the numbers of this stage only, then Continue (-> shop / next stage / the end)."""
    transparent = True

    def __init__(self, game):
        w = game.world; st = w.stats
        secs = int(w.time)
        self.rows = [('Monstros derrotados', str(st['kills'])), ('Dano causado', str(st['damage_dealt'])),
                     ('Dano recebido', str(st['damage_taken'])), ('Ouro adquirido', str(st['gold_gained'])),
                     ('Renascimentos', str(st['revives'])), ('Tempo', f'{secs // 60}:{secs % 60:02d}')]
        self.title = (w.stage.name if w.stage else 'FASE') + ' - COMPLETA'
        self.menu = Menu([('Continuar', 'continue', True)], x=(C.SCREEN_W - 150) // 2, y=C.SCREEN_H - 62, w=150, row_h=22)

    def act(self, action, game):
        if action == 'continue': game.after_summary()

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_RETURN, pygame.K_SPACE): self.act('continue', game)
        elif e.type == pygame.MOUSEMOTION: self.menu.mouse_move(game.to_internal(e.pos))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            a = self.menu.click(game.to_internal(e.pos))
            if a: self.act(a, game)

    def draw(self, surf, game):
        game.view.dim(surf, 190)
        game.view.title(surf, self.title, 30)
        y = 62
        for label, value in self.rows:
            game.view.text(surf, label, 130, y, (235, 240, 255))
            game.view.text(surf, value, 340, y, (255, 224, 150), align='right')
            y += 16
        game.view.draw_menu(surf, self.menu)


class EndScene(Scene):
    """After the last stage (the demo ends here)."""
    def __init__(self):
        self.menu = Menu([('Menu inicial', 'title', True), ('Sair', 'quit', True)], x=(C.SCREEN_W - 150) // 2, y=140, w=150, row_h=22)

    def act(self, action, game):
        if action == 'title': game.to_title()
        elif action == 'quit': game.running = False

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_UP, pygame.K_w): self.menu.move(-1)
        elif key_pressed(e, pygame.K_DOWN, pygame.K_s): self.menu.move(1)
        elif key_pressed(e, pygame.K_RETURN): self.act(self.menu.current(), game)
        elif e.type == pygame.MOUSEMOTION: self.menu.mouse_move(game.to_internal(e.pos))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            a = self.menu.click(game.to_internal(e.pos))
            if a: self.act(a, game)

    def draw(self, surf, game):
        game.view.draw(surf, game.world, 0.0, hud=False)
        game.view.dim(surf, 190)
        game.view.title(surf, 'FIM DA DEMO', 70)
        game.view.center(surf, 'Obrigado por jogar!', 98, (235, 240, 255))
        game.view.draw_menu(surf, self.menu)


class ControlsScene(Scene):
    """'Ver comandos': one table (config.CONTROLS) is the single source of the key list."""
    transparent = True

    def handle_event(self, e, game):
        if key_pressed(e, pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE) or \
                (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
            game.pop()

    def draw(self, surf, game):
        game.view.dim(surf, 255)
        game.view.title(surf, 'COMANDOS', 24)
        y = 52
        for keys, action in C.CONTROLS:
            game.view.text(surf, keys, 40, y, (255, 224, 150))
            game.view.text(surf, action, 190, y, (235, 240, 255))
            y += 15
        game.view.center(surf, 'Esc / Enter: voltar', C.SCREEN_H - 20)
