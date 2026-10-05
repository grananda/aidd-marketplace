# AIDD maps

> **Español:** [docs/mapas/README.md](../mapas/README.md). The Spanish version is the source of truth: if the two ever disagree, the Spanish one wins.

Six diagrams that show which tools you have, when each one is used and what for. GitHub renders them right here.

| If you are wondering... | Map |
|---|---|
| Which plugins exist and which do I install? | [Plugins](plugins.md) |
| What does each plugin bring? | [Skills](skills.md) |
| What is used at each point of the project? | [The process](process.md) |
| I am mid-sprint: what do I use now? | [What do I use when...?](what-do-i-use-when.md) |
| Who does what to a change, and what gets written down? | [Life of a change](change-lifecycle.md) |
| Which document comes out of each step, and who reads it next? | [Artifacts](artifacts.md) |

**Where to start.** If you have just arrived, [Plugins](plugins.md) and then [The process](process.md). If you are already building, [What do I use when...?](what-do-i-use-when.md).

## How to read them

- **Solid line**: the next step, or what one step hands to another.
- **Dashed line**: optional, or only when that document exists.
- **Every node** carries the command and what it is for. On GitHub nodes are not clickable: the link to each skill is in the table below each diagram.

## Keeping them current

The maps are written by hand, and skills land in this repo often. `check_maps.py` fails in CI when a skill has no row in [Skills](skills.md) or is missing from its mindmap, when a plugin's skill count in [Plugins](plugins.md) is not the real one, or when a link in these maps points at a file or a section that does not exist. It checks the Spanish maps and these ones alike.

When you add a skill, touch them in this order:

1. Its row in [Skills](skills.md) and its branch in the mindmap.
2. Its plugin's count in [Plugins](plugins.md).
3. Its place in [The process](process.md) if it is a step, in [What do I use when...?](what-do-i-use-when.md) if it answers a dev's situation, and in [Artifacts](artifacts.md) if it writes or reads a document.
