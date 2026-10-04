# Part 7: The GIMP bridge

**Goal:** let Claude make and measure raster images with a headless GIMP. **Time:** 15 minutes. **Needs:** GIMP 3.2.x, Python 3.11+, `uv`.
**Previous:** [Part 6](06-teach-claude-the-house-rules.md). **Next:** [Part 8](08-freecads-live-bridge.md).

GIMP is the easy bridge. [`gimp-agent-mcp`](https://github.com/SarutobiSasuke8/gimp-agent-mcp) (Apache-2.0, 39 tools at 0.5.0) runs as stdio
→ a token-authenticated loopback connection → a plug-in inside GIMP, and, unlike FreeCAD's bridge, it has a real headless mode. It is a
third-party project that exists to run code on your machine: read its source before installing it.

## Install

From the project's README:

```sh
uvx gimp-agent-mcp install-plugin
uvx gimp-agent-mcp install-skills --client claude
uvx gimp-agent-mcp doctor
```

(`install-skills` defaults to every agent client it finds; `--client claude` keeps it to Claude Code.)

**Start GIMP by hand once before `install-plugin`.** The plug-in installer needs GIMP's profile directory to exist, and without it says
"Could not find a GIMP 3 config directory." Start GIMP from the Finder or your launcher, **not from a shell**: on one Mac, a first
launch via `open -a GIMP` and via `gimp-console` both hung silently at 0% CPU. The app was freshly installed and quarantined, so a macOS
first-run approval invisible to a script is the suspect, but that was **not confirmed**. Launched by hand, GIMP opened without trouble and
everything after that worked as the README says.

Restart GIMP after the plug-in installs. Then either use *Filters → Development → Start Agent Bridge* in the open window, or have the
agent call `gimp_launch(mode="headless")` and skip the window entirely. Register it with Claude Code:

```sh
claude mcp add gimp -- uvx gimp-agent-mcp serve
```

(`claude mcp add <name> -- <command> [args]` is the right shape; it was checked against the installed CLI's own help.) The bridge ships its
*own* skills and recipes (sprite sheets, stickers, web export). Install those too rather than rebuilding them.

## What it is good for, and what it is not

Good: rendering concept images from CAD or SVG output, layered scenes, labelled assets, anything that must be regenerated when its source
changes. Not good: photorealism. A raster editor draws; it does not invent, and "remove the background" only works on a flat-colour
field. On a photograph it destroys the image while appearing to succeed, and the failure mode is a confident wrong answer.

## Two habits that earned their place

- **Make the agent look.** `gimp_render` returns the image and `gimp_measure` reads pixels and alpha bounds. Build one named layer per
  element (`sky`, `device`, `device-reflection`) so "make the sun smaller" is a ten-second change.
- **Bloom goes *behind* the thing that emits light.** Bloom on top washes out the detail it is meant to sell. It is the most common
  self-inflicted error in this kind of scene.

## Check

- [ ] `uvx gimp-agent-mcp doctor` finds the config directory and the plug-in.
- [ ] You know why you launched GIMP by hand before installing the plug-in.
- [ ] (After [part 8](08-freecads-live-bridge.md)'s probe) a headless launch, an image opened, and one pixel read back to a value you knew in advance.
