"""Sound playback. Turns the world's events into sounds. Fails soft: with no audio device (or a stand-in pygame
without a mixer) the game simply runs silent."""
import os
import pygame
from . import config as C

# fighter kind -> sound family: every human-ish fighter sounds like the knight, every monster like the ogre
FAMILY = {'knight': 'knight', 'ranger': 'knight', 'crossbowman': 'knight', 'mage': 'knight', 'soldier': 'knight',
          'spearman': 'knight', 'archer': 'knight', 'shieldman': 'knight', 'black_knight': 'knight'}

# world event -> sound file name, or {family: sound file}. Events are (name, kind); kind = a fighter kind (mapped through
# FAMILY) or an item kind ('coins', 'potion'...).
SOUND_FOR = {
    'swing': {'knight': 'sword_swing', 'ogre': 'axe_swing'},
    'hit': {'knight': 'hit_knight', 'ogre': 'hit_ogre'},          # kind = the one who was hit
    'hurt': {'knight': 'hurt_knight', 'ogre': 'hurt_ogre'},
    'death': {'knight': 'death_knight', 'ogre': 'death_ogre'},
    'spawn': {'knight': 'spawn_hero', 'ogre': 'spawn_ogre'},
    'pickup': {'coins': 'coin_pickup', 'potion': 'coin_pickup', 'weapon': 'coin_pickup', 'armor': 'coin_pickup'},
    'heal': 'heal',                                                # any life recovery
    'potion': 'gulp', 'jump': 'jump', 'drop': 'impact',
    'shoot': 'shoot', 'throw': 'throw', 'impact': 'impact', 'explosion': 'explosion', 'spikes': 'spikes',
    'block': 'block', 'armor_hit': 'armor_hit', 'armor_break': 'armor_break', 'break': 'weapon_break',
    'charge': 'charge', 'special': 'special', 'telegraph': 'telegraph',
    'boss_start': 'boss_start', 'summon': 'spawn_ogre', 'boss_dead': 'victory', 'stage_clear': 'victory', 'revive': 'revive',
}


class Audio:
    def __init__(self, sfx_dir, music_dir=None):
        self.sounds = {}; self.muted = not C.SFX_ENABLED; self.music_ok = False
        mixer = getattr(pygame, 'mixer', None)
        if mixer is None: return
        try:
            if not mixer.get_init(): mixer.init()
            mixer.set_num_channels(16)
            for f in sorted(os.listdir(sfx_dir)):
                if f.endswith('.wav'):
                    s = mixer.Sound(os.path.join(sfx_dir, f)); s.set_volume(C.SFX_VOLUME)
                    self.sounds[f[:-4]] = s
        except Exception as e:                                  # no device / missing folder: stay silent
            print('audio disabled:', e); self.sounds = {}; return
        if music_dir and C.MUSIC_ENABLED:
            try:
                mixer.music.load(os.path.join(music_dir, C.MUSIC_FILE))
                mixer.music.set_volume(0 if self.muted else C.MUSIC_VOLUME); mixer.music.play(-1)
                self.music_ok = True
            except Exception as e: print('music disabled:', e)

    def play_events(self, events):
        if self.muted: return
        for name, kind in events:
            snd = SOUND_FOR.get(name)
            if isinstance(snd, dict): snd = snd.get(FAMILY.get(kind, 'ogre'))      # unknown kinds are monsters
            s = self.sounds.get(snd)
            if s: s.play()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.music_ok: pygame.mixer.music.set_volume(0 if self.muted else C.MUSIC_VOLUME)
