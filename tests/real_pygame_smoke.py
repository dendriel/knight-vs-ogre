"""Runs the game with the REAL pygame in headless mode (SDL dummy drivers) for a few seconds, driving it with posted
events. Catches API differences between pygame and the Pillow stand-in. Skips itself when pygame is missing."""
import os, sys
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy'); os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
try:
    import pygame
except ImportError:
    print('pygame not installed: smoke test skipped'); sys.exit(0)
import main


def post_key(k): pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k))


g = main.Game('endless')
frames = 0


def run(n):
    global frames
    for _ in range(n):
        g.handle_events(); g.update(1 / 60); g.draw(); g.present(); frames += 1


run(120)
post_key(pygame.K_ESCAPE); run(5)
assert type(g.scene).__name__ == 'PauseScene', type(g.scene).__name__
post_key(pygame.K_DOWN); post_key(pygame.K_RETURN); run(5)
assert type(g.scene).__name__ == 'ControlsScene'
post_key(pygame.K_ESCAPE); run(2); post_key(pygame.K_ESCAPE); run(5)
assert type(g.scene).__name__ == 'PlayScene'
run(300)
print('real pygame smoke ok:', frames, 'frames,', pygame.version.ver)
pygame.quit()
