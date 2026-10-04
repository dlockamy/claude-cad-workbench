# Part 7: The GIMP bridge

*Part 7 of 12 · about 15 minutes · in this part: let Claude make and measure raster images with a headless GIMP.*

Parts 3 to 6 were all CAD. Next, the images around it: renders, concept sheets, labelled assets. [`gimp-agent-mcp`](https://github.com/SarutobiSasuke8/gimp-agent-mcp) (Apache-2.0, 39 tools at 0.5.0) is the easy bridge: stdio to a token-authenticated loopback connection to a plug-in inside GIMP, and unlike FreeCAD's bridge it has a real headless mode. It is third-party code that runs on your machine, so read its source first.

## Install

```sh
uvx gimp-agent-mcp install-plugin
uvx gimp-agent-mcp install-skills --client claude
uvx gimp-agent-mcp doctor
```

**Start GIMP by hand once before `install-plugin`**, from the launcher, not a shell. The installer needs GIMP's profile directory to exist ("Could not find a GIMP 3 config directory" otherwise). On one Mac, a first launch from a shell (`open -a GIMP`, then `gimp-console`) hung at 0% CPU. A first-run approval for a quarantined app is the suspect, but that is **not confirmed**. Launched by hand, it opened normally.

Restart GIMP, then register the bridge:

```sh
claude mcp add gimp -- uvx gimp-agent-mcp serve
```

Use *Filters → Development → Start Agent Bridge* in an open window, or have the agent call `gimp_launch(mode="headless")` and skip the window. Install the bridge's own skills too (sprite sheets, stickers, web export); don't rebuild them.

## Good at, and not good at

Good: renders from CAD or SVG output, layered scenes, labelled assets, anything regenerated when its source changes. Not good: photorealism. A raster editor draws; it doesn't invent. "Remove the background" only works on a flat-colour field, and on a photograph it destroys the image while appearing to succeed.

## Two habits worth keeping

- **Make the agent look.** `gimp_render` returns the image and `gimp_measure` reads pixels. Build one named layer per element (`sky`, `device`, `device-reflection`) so "make the sun smaller" is a ten-second change.
- **Bloom goes *behind* the thing that emits light.** On top, it washes out the detail it is meant to sell.

## Check

- [ ] `uvx gimp-agent-mcp doctor` finds the config directory and the plug-in.
- [ ] You know why GIMP was started by hand first.

---

**Next: [Part 8: FreeCAD's live bridge](08-freecads-live-bridge.md)**

[← Part 6: Teach Claude the house rules](06-teach-claude-the-house-rules.md) · [Series index](README.md)
