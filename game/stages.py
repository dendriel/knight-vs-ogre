"""Stages (T30): a stage is DATA - a finite path from left to right with a theme, encounters and (later) a boss.
No pygame and no rules in here; logic.World reads it. The infinite mode is simply "no stage" (see World)."""
from . import config as C


# Each stage is split in three sections by progress p = x / length (T36): opening, middle, pre-boss.
SECTIONS = ((0.0, 0.35), (0.35, 0.75), (0.75, 1.0001))

# Rough "danger" of each kind, only used to validate that encounter tables grow (tests) and for tuning.
THREAT = {'goblin': 1.0, 'kobold': 1.5, 'soldier': 2.0, 'archer': 2.5, 'ogre': 3.0, 'spearman': 3.0, 'shieldman': 3.5,
          'orc': 4.0, 'minotaur': 7.0}
ELITE_THREAT = 1.4                  # an elite counts this much more


class Stage:
    """id | name (HUD) | theme (key of THEMES) | length (px of the path) | start_x | encounters | boss | music
    encounters: list of dicts  {'p': progress 0..1 where it triggers, 'enemies': [(kind, elite or None), ...]}  sorted by p.
    difficulty: ((max_alive, max_attackers) per section) | elites: (from_p, fraction at from_p, fraction at the end)
    | loot: coin-bag multiplier at the start and at the end of the stage."""
    def __init__(self, id, name, theme, length, encounters, boss=None, start_x=40, music=None, arena_at=0.9,
                 difficulty=((2, 1), (3, 2), (3, 2)), elites=(0.75, 0.1, 0.2), loot=(1.0, 1.5)):
        self.id, self.name, self.theme, self.length, self.start_x = id, name, theme, float(length), float(start_x)
        self.encounters = sorted(encounters, key=lambda e: e['p'])
        self.boss, self.music, self.arena_at = boss, music, arena_at
        self.difficulty_table, self.elites, self.loot = difficulty, elites, loot

    def trigger_x(self, enc): return self.start_x + enc['p'] * (self.length - self.start_x)

    def progress(self, x): return max(0.0, min(1.0, (x - self.start_x) / max(1.0, self.length - self.start_x)))

    def difficulty(self, p):
        """What the stage asks of the player at progress p: simultaneous enemies, attack tokens, elite chance, loot."""
        sec = next(i for i, (a, b) in enumerate(SECTIONS) if a <= p < b)
        alive, att = self.difficulty_table[sec]
        f0, e0, e1 = self.elites
        frac = 0.0 if p < f0 else e0 + (e1 - e0) * (p - f0) / max(1e-6, 1.0 - f0)
        return dict(section=sec, max_alive=alive, max_attackers=att, elite_frac=frac,
                    loot_mult=self.loot[0] + (self.loot[1] - self.loot[0]) * p)

    def threat(self, section):
        """Sum of THREAT of the encounters that fire inside a section (explicit elites weigh ELITE_THREAT)."""
        a, b = SECTIONS[section]; total = 0.0
        for enc in self.encounters:
            if a <= enc['p'] < b:
                total += sum(THREAT[k] * (ELITE_THREAT if el else 1.0) for k, el in enc['enemies'])
        return total


def enc(p, *kinds):
    """enc(0.25, 'ogre', ('soldier', 'veteran')) -> encounter at 25% of the path."""
    return {'p': p, 'enemies': [(k, None) if isinstance(k, str) else tuple(k) for k in kinds]}


# Visual themes (T33-T35): colours, parallax layers, ground tile and which scenery props appear. Props of a slot are
# drawn from a table [(prop name, probability)] per slot parity (cumulative, like slot_props always did).
# hills_*: (colour, height px, (amplitudes), seed). extras: optional parallax decorations ('castle', 'fog', 'wall').
THEMES = {
    'village': dict(sky=(122, 178, 224), hills_far=((98, 156, 156), 70, (20, 9, 5), 3), hills_near=((78, 134, 110), 44, (13, 6, 3), 9),
                    dirt=(70, 54, 46), ground='street_tile', extras=(),
                    props_even=[('medieval_house', .6), ('well', .18)], props_odd=[('tree', .6), ('well', .12)]),
    'plain': dict(sky=(146, 194, 228), hills_far=((120, 158, 130), 66, (16, 8, 4), 21), hills_near=((98, 144, 84), 40, (11, 5, 3), 33),
                  dirt=(70, 54, 46), ground='grass_tile', extras=('castle',),
                  props_even=[('tent', .30), ('banner', .16), ('palisade', .20), ('cart', .12)],
                  props_odd=[('dead_tree', .28), ('planted_swords', .18), ('campfire', .14), ('banner', .12)]),
}
# where a prop may stand inside its slot: x offset in randint(first, SLOT_W - last)
PROP_PLACE = {'medieval_house': (0, 160), 'well': (8, 56), 'tree': (0, 112), 'tent': (0, 82), 'banner': (4, 28),
              'palisade': (0, 68), 'planted_swords': (4, 38), 'dead_tree': (0, 64), 'cart': (0, 80), 'campfire': (8, 28)}

# ---- the campaign (three stages; T36 fills in the difficulty curve, T32-T35 the bosses and the themes) ---------------
STAGES = {
    'stage1': Stage('stage1', 'FASE 1 - PLANÍCIE', 'plain', 3000, [
        enc(0.10, 'soldier'), enc(0.25, 'ogre'), enc(0.45, 'soldier', 'ogre'), enc(0.60, 'spearman', 'soldier'),
        enc(0.80, 'archer', 'spearman', 'ogre'), enc(0.92, ('soldier', 'veteran'), 'spearman', 'archer')],
        difficulty=((2, 1), (3, 2), (3, 2)), elites=(0.75, 0.15, 0.25), loot=(1.0, 1.4)),
    'stage2': Stage('stage2', 'FASE 2 - FLORESTA', 'village', 3400, [
        enc(0.08, 'goblin', 'goblin'), enc(0.22, 'goblin', 'kobold', 'goblin'), enc(0.38, 'shieldman', 'goblin'),
        enc(0.55, 'goblin', 'goblin', 'kobold', 'orc'), enc(0.78, 'shieldman', 'archer', 'kobold'),
        enc(0.88, ('goblin', 'agile'), ('goblin', 'agile'), 'orc', 'kobold', 'archer')],
        difficulty=((3, 2), (4, 2), (5, 3)), elites=(0.5, 0.15, 0.3), loot=(1.3, 1.8)),
    'stage3': Stage('stage3', 'FASE 3 - CIDADE', 'village', 3800, [
        enc(0.08, 'shieldman', 'spearman', 'soldier'), enc(0.22, 'orc', 'archer', 'archer'), enc(0.40, 'minotaur'),
        enc(0.58, 'shieldman', 'spearman', 'orc', 'archer', ('soldier', 'veteran')),
        enc(0.78, ('orc', 'brute'), 'shieldman', 'archer', 'archer', 'spearman'),
        enc(0.90, ('spearman', 'veteran'), ('shieldman', 'veteran'), ('orc', 'brute'), 'archer', 'archer', 'minotaur')],
        difficulty=((4, 2), (5, 3), (6, 3)), elites=(0.3, 0.2, 0.45), loot=(1.6, 2.2)),
}
CAMPAIGN = ['stage1', 'stage2', 'stage3']
