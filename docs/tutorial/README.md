# Tutorial: designing 3D models with Claude, FreeCAD and GIMP

Twelve short parts, each a self-contained walk-through of about 10 to 20 minutes. Every part ends with a check you can run, and a link to the
next part, so you can read straight through without coming back here. You can stop after any part and have something that works.

The thread through all of it: **getting Claude to drive CAD is the easy half. The hard half is getting the setup to tell you when it is
wrong.** FreeCAD's command line exits `0` on a script that failed, a model with a hole missing passes the standard topology checks, and a
rigged character can have joints that do nothing and still pass its validator.

**[Start with Part 1: The idea, and the first check](01-the-idea-and-the-first-check.md)**

| # | Part | Time |
|---|---|---|
| 1 | [The idea, and the first check](01-the-idea-and-the-first-check.md) | 10 min |
| 2 | [Install the tools](02-install-the-tools.md) | 10 min |
| 3 | [Write a part that checks itself](03-write-a-part-that-checks-itself.md) | 15 min |
| 4 | [Make it fail on purpose](04-make-it-fail-on-purpose.md) | 15 min |
| 5 | [Look at the part, and check your checker](05-look-at-the-part.md) | 10 min |
| 6 | [Teach Claude the house rules](06-teach-claude-the-house-rules.md) | 10 min |
| 7 | [The GIMP bridge](07-the-gimp-bridge.md) | 15 min |
| 8 | [FreeCAD's live bridge](08-freecads-live-bridge.md) | 15 min |
| 9 | [Prove a bridge before you trust it](09-prove-a-bridge-before-you-trust-it.md) | 20 min |
| 10 | [What this setup cannot tell you](10-what-this-cannot-tell-you.md) | 10 min |
| 11 | [From a drawing to a model](11-from-a-drawing-to-a-model.md) | 15 min |
| 12 | [Check the rig](12-check-the-rig.md) | 20 min |

**Short on time:** read parts 1 and 4, run the two commands at the end of part 4, and stop. That is the whole idea.

## Conventions

- Commands assume the repository root. `freecadcmd` means: on macOS,
  `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd`; on Linux with the Flatpak,
  `flatpak run --command=freecadcmd org.freecad.FreeCAD` (part 2 explains why the script path must then be absolute and under `$HOME`).
- A **Check** list at the end of each part is something you run and compare. If your output differs, an issue is welcome.
- Every claim about tool behaviour was reproduced on a real machine. Part 10 and the README's [Verified on](../../README.md#verified-on) table
  say which, when, and what was **not** run. Where something is a suspicion, the text says so.
- This series was reorganised from one long blog post into parts. The ideas are the same; the parts are shorter and each is runnable alone.
