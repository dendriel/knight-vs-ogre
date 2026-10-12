"""Scenes, menus and input edges. Runs the real main.py with the Pillow stand-in for pygame (no window needed)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import fake_pygame as fp
sys.modules['pygame'] = fp.module
import main
from game import config as C
from game import scenes as S

DT = 1 / 60


def step(g, n=1):
    for _ in range(n):
        g.handle_events(); g.update(DT); g.draw(); g.present()


def key(g, k):
    fp.EVENTS.append(fp.Event(fp.KEYDOWN, key=k)); step(g)


def click(g, pos):
    """pos in INTERNAL canvas coordinates; converted to window pixels the way present() maps them back"""
    s, off = g._scale, g._off
    wp = (pos[0] * s + off[0] + 1, pos[1] * s + off[1] + 1)
    fp.EVENTS.append(fp.Event(fp.MOUSEBUTTONDOWN, pos=wp, button=1)); step(g)


def fresh():
    fp.PRESSED.clear(); fp.EVENTS.clear()
    g = main.Game(); step(g, 3); return g


# 1) Esc opens the pause menu and freezes the world; Esc again resumes
g = fresh(); step(g, 30); t0 = g.world.time
key(g, fp.K_ESCAPE); assert isinstance(g.scene, S.PauseScene)
step(g, 60); assert g.world.time == t0, 'the world must stay frozen while paused'
key(g, fp.K_ESCAPE); assert isinstance(g.scene, S.PlayScene)
step(g, 10); assert g.world.time > t0
print('1 ok: Esc pauses / resumes, world frozen')

# 2) keyboard navigation: Down + Enter = Ver comandos; Esc returns to the pause menu; Continuar via Enter
g = fresh(); key(g, fp.K_ESCAPE)
key(g, fp.K_DOWN); key(g, fp.K_RETURN); assert isinstance(g.scene, S.ControlsScene)
key(g, fp.K_ESCAPE); assert isinstance(g.scene, S.PauseScene)
key(g, fp.K_UP); key(g, fp.K_RETURN); assert isinstance(g.scene, S.PlayScene)
print('2 ok: menu by keyboard, controls screen and back')

# 3) mouse: clicking the 4th entry quits; clicking "Reiniciar fase" gives a brand-new world
g = fresh(); step(g, 120); old = g.world; g.world.gold = 55
key(g, fp.K_ESCAPE)
m = g.scene.menu; r = m.rect(2)
click(g, (r.x + 5, r.y + 5))
assert isinstance(g.scene, S.PlayScene) and g.world is not old and g.world.gold == 0 and g.world.time < 0.5
key(g, fp.K_ESCAPE); r = g.scene.menu.rect(3); assert g.running
click(g, (r.x + 5, r.y + 5)); assert not g.running
print('3 ok: restart builds a fresh world, Sair stops the game')

# 4) the controls table is the one the screen shows; and the click that closes a menu does not swing the sword
assert any('Esc' in k for k, a in C.CONTROLS)
g = fresh(); key(g, fp.K_ESCAPE)
fp.PRESSED.add(fp.MOUSE_LEFT)                         # left button still down when the menu closes
key(g, fp.K_ESCAPE); step(g, 5)
assert g.world.hero.state != 'attack', 'a held click must be ignored until released'
fp.PRESSED.discard(fp.MOUSE_LEFT); step(g, 2); fp.PRESSED.add(fp.MOUSE_LEFT); step(g, 2)
assert g.world.hero.state == 'attack'
print('4 ok: held button after a menu is ignored until released')

# 5) input edges and hold time
g = fresh(); fp.PRESSED.clear()
step(g); assert not g.cur.attack and not g.cur.attack_pressed
fp.PRESSED.add(fp.MOUSE_LEFT); step(g); assert g.cur.attack_pressed and g.cur.attack
step(g, 30); assert g.cur.attack and not g.cur.attack_pressed and g.cur.attack_held_t > 0.45
fp.PRESSED.discard(fp.MOUSE_LEFT); step(g); assert g.cur.attack_released and g.cur.attack_held_t == 0
fp.PRESSED.add(fp.MOUSE_RIGHT); step(g); assert g.cur.secondary_pressed
fp.PRESSED.add(fp.K_1); step(g); assert g.cur.potion_pressed
step(g); assert not g.cur.potion_pressed
print('5 ok: attack / secondary / potion edges and hold time')

print('ALL SCENE TESTS PASSED')
