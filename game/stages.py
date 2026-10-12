"""Stages (T30): a stage is DATA - a finite path from left to right with a theme, encounters and (later) a boss.
No pygame and no rules in here; logic.World reads it. The infinite mode is simply "no stage" (see World)."""
from . import config as C


class Stage:
    """id | name (HUD) | theme (key of THEMES) | length (px of the path) | start_x | encounters | boss | music
    encounters: list of dicts  {'p': progress 0..1 where it triggers, 'enemies': [(kind, elite or None), ...]}  sorted by p."""
    def __init__(self, id, name, theme, length, encounters, boss=None, start_x=40, music=None, arena_at=0.9, difficulty=None):
        self.id, self.name, self.theme, self.length, self.start_x = id, name, theme, float(length), float(start_x)
        self.encounters = sorted(encounters, key=lambda e: e['p'])
        self.boss, self.music, self.arena_at = boss, music, arena_at
        self.difficulty = difficulty             # T36: list of sections (p_from, dict(max_alive, max_attackers, ...))

    def trigger_x(self, enc): return self.start_x + enc['p'] * (self.length - self.start_x)


def enc(p, *kinds):
    """enc(0.25, 'ogre', ('soldier', 'veteran')) -> encounter at 25% of the path."""
    return {'p': p, 'enemies': [(k, None) if isinstance(k, str) else tuple(k) for k in kinds]}


# Visual themes: colours, which scenery props appear (T33-T35 add real ones); the game draws from this table.
THEMES = {
    'village': dict(sky=(122, 178, 224), hills_far=(98, 156, 156), hills_near=(78, 134, 110), dirt=(70, 54, 46),
                    ground='street_tile'),
}

# ---- the campaign (three stages; T36 fills in the difficulty curve, T32-T35 the bosses and the themes) ---------------
STAGES = {
    'stage1': Stage('stage1', 'FASE 1 - PLANÍCIE', 'village', 3000, [
        enc(0.10, 'soldier'), enc(0.22, 'ogre'), enc(0.38, 'soldier', 'ogre'),
        enc(0.55, 'spearman', 'soldier'), enc(0.72, 'archer', 'spearman', 'ogre'),
        enc(0.88, ('soldier', 'veteran'), 'spearman', 'archer')]),
    'stage2': Stage('stage2', 'FASE 2 - FLORESTA', 'village', 3400, [
        enc(0.08, 'goblin', 'goblin'), enc(0.20, 'goblin', 'kobold', 'goblin'), enc(0.34, 'shieldman'),
        enc(0.50, 'goblin', 'goblin', 'kobold', 'orc'), enc(0.66, 'shieldman', 'archer', 'kobold'),
        enc(0.84, ('goblin', 'agile'), ('goblin', 'agile'), 'orc', 'kobold')]),
    'stage3': Stage('stage3', 'FASE 3 - CIDADE', 'village', 3800, [
        enc(0.08, 'shieldman', 'spearman'), enc(0.22, 'orc', 'archer', 'archer'), enc(0.38, 'minotaur'),
        enc(0.54, 'shieldman', 'spearman', 'orc', 'archer'), enc(0.70, ('orc', 'brute'), 'shieldman', 'archer', 'archer'),
        enc(0.86, ('spearman', 'veteran'), ('shieldman', 'veteran'), ('orc', 'brute'), 'archer')]),
}
CAMPAIGN = ['stage1', 'stage2', 'stage3']
