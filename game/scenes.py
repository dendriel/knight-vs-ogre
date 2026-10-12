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


class TitleScene(Scene):
    """Start screen (T30): campaign (the three stages), the endless mode, controls, quit."""
    def __init__(self):
        self.menu = Menu([('Campanha', 'campaign', True), ('Modo infinito', 'endless', True),
                          ('Ver comandos', 'controls', True), ('Sair', 'quit', True)],
                         x=(C.SCREEN_W - 150) // 2, y=108, w=150, row_h=22)

    def act(self, action, game):
        if action == 'campaign': game.start('stage1')
        elif action == 'endless': game.start('endless')
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
