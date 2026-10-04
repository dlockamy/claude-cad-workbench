# Part 6: Teach Claude the house rules

*Part 6 of 12 · about 10 minutes · in this part: install the skills and the CAD subagent so Claude doesn't relearn each mistake on your part.*

So far we have been doing the work by hand. Claude Code loads *skills*, folders with a `SKILL.md` and a description, when the description matches the task. This repo has four, plus a subagent:

| Skill / agent | What it carries |
|---|---|
| [`parametric-cad-verify`](../../skills/parametric-cad-verify/SKILL.md) | The headless workflow, the checks from parts 3 and 4, the `freecadcmd` traps, geometry gotchas |
| [`drive-desktop-app`](../../skills/drive-desktop-app/SKILL.md) | Choosing, installing and *proving* an MCP bridge (parts 7 to 9) |
| [`raster-compositing`](../../skills/raster-compositing/SKILL.md) | Layered, repeatable GIMP images, and what a raster editor can't do |
| [`multi-material-print-handoff`](../../skills/multi-material-print-handoff/SKILL.md) | Getting verified CAD into a multi-colour slicer project |
| [`mechanical-cad-engineer`](../../agents/mechanical-cad-engineer.md) | Implements a part spec and won't call it done until it has read the geometry back |

## Install

```sh
./install.sh        # symlinks skills and the agent into ~/.claude
./tools/doctor.sh   # read-only: what is installed, what is missing
```

`install.sh` only replaces symlinks it created itself. Its first version would have silently swapped an existing symlink pointing somewhere else, so it now skips anything it doesn't own and says so. `./install.sh --uninstall` removes exactly what it added. Prefer not to touch `~/.claude`? Run `claude --plugin-dir /path/to/claude-cad-workbench` to load everything for one session; the plugin is named `cad-workbench`, so the skills appear as `cad-workbench:parametric-cad-verify` and the agent as `cad-workbench:mechanical-cad-engineer`.

## Use

> Use the mechanical-cad-engineer agent to make a 60 × 40 × 5 mm bracket with two M4 clearance slots. It needs to fit a 220 mm bed.

## Why plain markdown is the point

There is no magic here. The skills hold the list of things that already went wrong once, so Claude doesn't rediscover them on your part, and the long-term value is that list getting longer. When you hit a new trap, add a line, with the date and what you saw.

## Check

- [ ] `./tools/doctor.sh` shows all four skills and the agent installed.
- [ ] Ask for a part and confirm the script Claude writes exits non-zero on failure. If it doesn't, that's a gap in a skill worth an issue.

---

**Next: [Part 7: The GIMP bridge](07-the-gimp-bridge.md)**

[← Part 5: Look at the part, and check your checker](05-look-at-the-part.md) · [Series index](README.md)
