# design-system

Design system et outils Studio Kito.

## Skills

| Skill | Rôle |
|---|---|
| [`skills/croquis-annote`](skills/croquis-annote/SKILL.md) | Photo de meuble → croquis crayon + aquarelle en perspective, annoté, planche PDF client avec cartouche Studio Kito. |

### Installer une skill dans claude.ai

1. Télécharger `dist/croquis-annote.zip` (ou zipper le dossier `skills/croquis-annote`).
2. claude.ai → Paramètres → Capacités → Skills → « Importer une skill » → choisir le zip.
3. Vérifier que l'exécution de code est activée (nécessaire pour `scripts/annotate.py`).

Dans Claude Code : copier le dossier dans `~/.claude/skills/` (ou `.claude/skills/` d'un projet).
