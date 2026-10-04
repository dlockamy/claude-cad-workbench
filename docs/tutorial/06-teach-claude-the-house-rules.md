# Part 6: Teach Claude the house rules

**Goal:** install the skills and the CAD subagent so Claude does not rediscover each mistake on your part. **Time:** 10 minutes.
**Needs:** Claude Code. **Previous:** [Part 5](05-look-at-the-part.md). **Next:** [Part 7](07-the-gimp-bridge.md).

Claude Code loads *skills*, folders with a `SKILL.md` and a frontmatter description, when the description matches the task. This repo has
four, plus a subagent.

| Skill / agent | What it carries |
|---|---|
| [`parametric-cad-verify`](../../skills/parametric-cad-verify/SKILL.md) | The headless workflow, the verification battery, the `freecadcmd` traps from part 4, and the geometry gotchas |
| [`drive-desktop-app`](../../skills/drive-desktop-app/SKILL.md) | How to choose, audit, install and *prove* an MCP bridge (parts 7 and 8) |
| [`raster-compositing`](../../skills/raster-compositing/SKILL.md) | Layered, repeatable GIMP images, and what a raster editor cannot do |
| [`multi-material-print-handoff`](../../skills/multi-material-print-handoff/SKILL.md) | Getting verified CAD into a multi-colour slicer project |
| [`mechanical-cad-engineer`](../../agents/mechanical-cad-engineer.md) (agent) | Implements a part spec and will not call it done until it has read the geometry back |

## Install

```sh
./install.sh        # symlinks skills + agent into ~/.claude
./tools/doctor.sh   # read-only: what is installed, what is missing
```

`install.sh` only ever replaces symlinks it created itself. That was tightened while testing: the first version would have silently
replaced an existing symlink pointing somewhere else, which on one machine would have swapped out a different, already-installed copy of
the CAD agent. It now skips anything it does not own and says so. `./install.sh --uninstall` removes exactly what it added.

Prefer not to touch `~/.claude`? The repo is also a Claude Code plugin: `claude --plugin-dir /path/to/claude-cad-workbench` loads the skills
and agent for that session only.

## Use

Then just ask:

> Use the mechanical-cad-engineer agent to make a 60 × 40 × 5 mm bracket with two M4 clearance slots. It needs to fit a 220 mm bed.

## Why plain markdown is the point

There is no magic in the skills. What they carry is the list of things that already went wrong once, so Claude does not have to
rediscover each of them on your part. **The long-term value of the repo is that list getting longer.** When you hit a new trap, the
right move is a line in the skill, with the date and what you saw. [Part 10](10-from-a-drawing-to-a-rigged-model.md) is what that looks
like when it is a whole new workflow.

## Check

- [ ] `./tools/doctor.sh` shows all four skills and the agent as installed.
- [ ] Asking Claude for a part makes it write a script that exits non-zero on failure. If it does not, say so in an issue: that is a gap in a skill.
