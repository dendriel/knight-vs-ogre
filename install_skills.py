"""OPTIONAL: install the project's skills as PERSONAL Claude Code skills (available in every project).

You usually do NOT need this: Claude Code loads the skills in ./.claude/skills automatically when you start it
inside this folder. Use this only if you want the skills in other folders too.

    python install_skills.py            # copy to ~/.claude/skills (an existing different copy is backed up first)
    python install_skills.py --dry-run  # show what would happen
"""
import os, shutil, sys, time, filecmp
from pathlib import Path

SRC = Path(__file__).resolve().parent / '.claude' / 'skills'
DST = Path.home() / '.claude' / 'skills'


def same_tree(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files: return False
    return all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def main():
    dry = '--dry-run' in sys.argv
    DST.mkdir(parents=True, exist_ok=True)
    for skill in sorted(p for p in SRC.iterdir() if (p / 'SKILL.md').exists()):
        target = DST / skill.name
        if target.exists():
            if same_tree(skill, target): print(f'= {skill.name}: already up to date'); continue
            backup = DST.parent / 'skills-backup' / f'{skill.name}-{time.strftime("%Y%m%d-%H%M%S")}'
            print(f'~ {skill.name}: updating (old copy -> {backup})')
            if not dry: backup.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(target), str(backup))
        else:
            print(f'+ {skill.name}: installing')
        if not dry: shutil.copytree(skill, target, ignore=shutil.ignore_patterns('__pycache__'))
    print('done' + (' (dry run, nothing written)' if dry else '') + f'. Personal skills folder: {DST}')


if __name__ == '__main__':
    main()
