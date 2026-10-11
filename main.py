"""Knight vs Ogre - small demo. Run:  python main.py"""
import os, sys
import pygame
from game import config as C
from game.logic import World, Inputs, load_timing
from game.view import View
from game.audio import Audio


def base_dir():
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))   # works inside a PyInstaller .exe too


class Game:
    def __init__(self):
        if sys.platform == 'win32':                       # avoid Windows blurring/rescaling the window on hi-dpi screens
            try:
                import ctypes; ctypes.windll.user32.SetProcessDPIAware()
            except Exception: pass
        pygame.init()
        pygame.display.set_caption('Knight vs Ogre')
        self.fullscreen = False
        self.window = pygame.display.set_mode((C.SCREEN_W * C.DEFAULT_SCALE, C.SCREEN_H * C.DEFAULT_SCALE), pygame.RESIZABLE)
        assets = os.path.join(base_dir(), 'assets')
        timing = load_timing(assets)
        self.view = View(assets, timing)
        self.world = World(timing)
        self.audio = Audio(os.path.join(assets, 'sfx'), os.path.join(assets, 'music'))
        self.screen = pygame.Surface((C.SCREEN_W, C.SCREEN_H))     # internal low-res canvas
        self.clock = pygame.time.Clock(); self.running = True; self.t = 0.0

    def inputs(self):
        k = pygame.key.get_pressed()
        return Inputs(left=bool(k[pygame.K_LEFT] or k[pygame.K_a]),
                      right=bool(k[pygame.K_RIGHT] or k[pygame.K_d]),
                      attack=bool(k[pygame.K_SPACE]))

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: self.running = False
                elif e.key == pygame.K_F11: self.toggle_fullscreen()
                elif e.key == pygame.K_m: self.audio.toggle_mute()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen: self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else: self.window = pygame.display.set_mode((C.SCREEN_W * C.DEFAULT_SCALE, C.SCREEN_H * C.DEFAULT_SCALE), pygame.RESIZABLE)

    def update(self, dt):
        self.t += dt; self.world.update(dt, self.inputs())
        self.audio.play_events(self.world.events); self.world.events.clear()

    def draw(self):
        self.view.draw(self.screen, self.world, self.t)

    def present(self):
        win = pygame.display.get_surface(); w, h = win.get_size()
        s = max(1, min(w // C.SCREEN_W, h // C.SCREEN_H))          # integer scale keeps the pixels square and sharp
        scaled = pygame.transform.scale(self.screen, (C.SCREEN_W * s, C.SCREEN_H * s))
        win.fill((0, 0, 0)); win.blit(scaled, ((w - C.SCREEN_W * s) // 2, (h - C.SCREEN_H * s) // 2))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            self.handle_events(); self.update(dt); self.draw(); self.present()
        pygame.quit()


if __name__ == '__main__':
    Game().run()
