"""Knight vs Ogre - small demo. Run:  python main.py"""
import os, sys
import pygame
from game import config as C
from game.logic import World, Inputs, load_timing
from game.view import View
from game.scenes import PlayScene, TitleScene, DefeatScene, SummaryScene, EndScene, ShopScene
from game.stages import STAGES, CAMPAIGN
from game.audio import Audio


def base_dir():
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))   # works inside a PyInstaller .exe too


class Game:
    def __init__(self, start='title', hero_class='knight'):
        if sys.platform == 'win32':                       # avoid Windows blurring/rescaling the window on hi-dpi screens
            try:
                import ctypes; ctypes.windll.user32.SetProcessDPIAware()
            except Exception: pass
        pygame.init()
        pygame.display.set_caption('Knight vs Ogre')
        self.fullscreen = False
        self.window = pygame.display.set_mode((C.SCREEN_W * C.DEFAULT_SCALE, C.SCREEN_H * C.DEFAULT_SCALE), pygame.RESIZABLE)
        assets = os.path.join(base_dir(), 'assets')
        self.timing = load_timing(assets)
        self.view = View(assets, self.timing)
        self.world = World(self.timing)
        self.audio = Audio(os.path.join(assets, 'sfx'), os.path.join(assets, 'music'))
        self.screen = pygame.Surface((C.SCREEN_W, C.SCREEN_H))     # internal low-res canvas
        self.clock = pygame.time.Clock(); self.running = True; self.t = 0.0
        self.stage_id = 'endless'; self.hero_class = hero_class                 # chosen class (T45 sets it from the menu)
        self.run = dict(gold=0, potions=0, weapon=None, armor=0, bombs=0)  # what travels between stages (D6)
        self.shop_log = []                                           # ids bought (tests / stats)
        self.run_start = dict(self.run)                              # snapshot at the start of the stage (D9)
        self.scenes = [PlayScene()]                                 # scene stack: the last one is on top
        self._scale, self._off = 1, (0, 0)                          # window -> internal canvas mapping (set by present())
        self._prev = dict(attack=False, secondary=False, potion=False, bomb=False); self._attack_t = 0.0; self._lock = False
        self.cur = Inputs()
        if start == 'title': self.scenes = [TitleScene()]
        else: self.start(start)

    # ------------------------------------------------------------------ scenes
    @property
    def scene(self): return self.scenes[-1]
    def push(self, scene): self.scenes.append(scene); self._lock = True
    def pop(self):
        if len(self.scenes) > 1: self.scenes.pop()
        self._lock = True
    def replace(self, scene): self.scenes[-1] = scene; self._lock = True

    def start(self, stage_id, run=None):
        """Begins a stage ('stage1'...) or the endless mode ('endless') with a fresh world. `run` = the run state to
        carry in (default: the current one); it is also stored as the snapshot a restart goes back to (D9)."""
        self.stage_id = stage_id
        stage = STAGES.get(stage_id)
        if stage is None: run = dict(gold=0, potions=0, weapon=None, armor=0, bombs=0)     # endless: nothing carries over
        elif run is None: run = self.run
        self.run_start = {k: (dict(v) if isinstance(v, dict) else v) for k, v in run.items()}
        self.world = World(self.timing, stage=stage, hero_class=self.hero_class)
        self.world.apply_run(self.run_start)
        self.scenes = [PlayScene()]; self.t = 0.0; self._lock = True

    def start_with_shop(self, stage_id, run):
        """Opens the shop (when there is gold to spend) and starts `stage_id` with the purchases. Endless has no shop."""
        if stage_id not in STAGES or run.get('gold', 0) < min(C.SHOP_PRICES.values()):
            self.start(stage_id, run); return
        self.world = World(self.timing, hero_class=self.hero_class)       # a quiet backdrop for the scene stack
        self.scenes = [ShopScene(self, stage_id, run)]; self._lock = True

    def to_title(self):
        self.run = dict(gold=0, potions=0, weapon=None, armor=0, bombs=0)
        self.world = World(self.timing); self.scenes = [TitleScene()]; self._lock = True

    def restart_stage(self):
        """Restarts the current stage from scratch (the infinite mode has no stage state: a fresh world)."""
        self.start_with_shop(self.stage_id, self.run_start)    # back to the state the stage began with (D9), via the shop

    def after_world_update(self):
        """Reacts to what the world just decided: the defeat screen (T37); the summary arrives with T31."""
        w = self.world
        if w.defeated and not isinstance(self.scene, DefeatScene): self.push(DefeatScene(self))
        elif w.stage_clear and isinstance(self.scene, PlayScene): self.push(SummaryScene(self))

    def after_summary(self):
        """Continue after the stage summary: carry the run state to the next stage of the campaign, or end."""
        self.run = self.world.export_run()
        i = CAMPAIGN.index(self.stage_id) if self.stage_id in CAMPAIGN else -1
        if 0 <= i < len(CAMPAIGN) - 1: self.start_with_shop(CAMPAIGN[i + 1], self.run)
        else:
            self.scenes = [EndScene()]; self._lock = True

    # ------------------------------------------------------------------ input
    def to_internal(self, pos):
        s = self._scale or 1
        return ((pos[0] - self._off[0]) // s, (pos[1] - self._off[1]) // s)

    def sample_inputs(self, dt):
        """Raw keyboard / mouse -> Inputs with levels, press edges and how long the attack button has been held."""
        k = pygame.key.get_pressed(); m = pygame.mouse.get_pressed()
        attack, secondary, potion = bool(m[0]), bool(len(m) > 2 and m[2]), bool(k[pygame.K_1])
        bomb = bool(k[pygame.K_2])
        if self._lock:                                              # a click that closed a menu must not swing the sword
            if not (attack or secondary): self._lock = False
            attack = secondary = False
        i = Inputs(left=bool(k[pygame.K_LEFT] or k[pygame.K_a]), right=bool(k[pygame.K_RIGHT] or k[pygame.K_d]),
                   attack=attack, jump=bool(k[pygame.K_SPACE]), secondary=secondary)
        i.attack_pressed = attack and not self._prev['attack']
        i.attack_released = self._prev['attack'] and not attack
        i.secondary_pressed = secondary and not self._prev['secondary']
        i.potion_pressed = potion and not self._prev['potion']
        i.bomb_pressed = bomb and not self._prev['bomb']
        self._attack_t = self._attack_t + dt if attack else 0.0
        i.attack_held_t = self._attack_t
        self._prev.update(attack=attack, secondary=secondary, potion=potion, bomb=bomb)
        self.cur = i

    def inputs(self): return self.cur

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: self.running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11: self.toggle_fullscreen()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_m: self.audio.toggle_mute()
            else: self.scene.handle_event(e, self)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen: self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else: self.window = pygame.display.set_mode((C.SCREEN_W * C.DEFAULT_SCALE, C.SCREEN_H * C.DEFAULT_SCALE), pygame.RESIZABLE)

    def update(self, dt):
        self.sample_inputs(dt)
        if isinstance(self.scene, PlayScene): self.t += dt
        self.scene.update(dt, self)
        self.audio.play_events(self.world.events); self.world.events.clear()

    def draw(self):
        i = len(self.scenes) - 1
        while i > 0 and self.scenes[i].transparent: i -= 1          # overlays are drawn on top of the scenes below
        for sc in self.scenes[i:]: sc.draw(self.screen, self)

    def present(self):
        win = pygame.display.get_surface(); w, h = win.get_size()
        s = max(1, min(w // C.SCREEN_W, h // C.SCREEN_H))          # integer scale keeps the pixels square and sharp
        scaled = pygame.transform.scale(self.screen, (C.SCREEN_W * s, C.SCREEN_H * s))
        off = ((w - C.SCREEN_W * s) // 2, (h - C.SCREEN_H * s) // 2); self._scale, self._off = s, off
        win.fill((0, 0, 0)); win.blit(scaled, off)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            self.handle_events(); self.update(dt); self.draw(); self.present()
        pygame.quit()


if __name__ == '__main__':
    start = 'title'
    explicit_class = '--class' in sys.argv
    if '--endless' in sys.argv: start = 'endless'
    elif '--stage' in sys.argv:
        n = sys.argv[sys.argv.index('--stage') + 1]
        start = n if n in STAGES else 'stage' + n
    elif explicit_class: start = 'stage1'                       # --class alone starts the campaign with that class
    cls = sys.argv[sys.argv.index('--class') + 1] if '--class' in sys.argv else 'knight'
    Game(start, cls).run()
