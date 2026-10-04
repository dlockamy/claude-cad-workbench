# Tutorial: designing 3D models with Claude, FreeCAD and GIMP — and making the setup prove its own work

Ten short parts. Each takes 10–20 minutes, has one goal, ends with a check you can run, and links to the next. You can stop after any
part and have something that works.

The thread that runs through all of it: **getting Claude to drive CAD is the easy half. The hard half is getting the setup to tell you
when it is wrong.** FreeCAD's command line will exit `0` on a script that failed, a model with a hole missing passes the standard
topology checks, and a rigged character can have joints that do nothing and still pass its validator. Every part is about closing one
of those gaps.

| # | Part | You will | Needs |
|---|---|---|---|
| 1 | [The idea, and the first check](01-the-idea-and-the-first-check.md) | See the shape of the system and prove the headless path with one number you computed yourself | FreeCAD |
| 2 | [Install the tools](02-install-the-tools.md) | Install FreeCAD, GIMP and `uv` on macOS or Linux, and avoid the version traps | — |
| 3 | [Write a part that checks itself](03-write-a-part-that-checks-itself.md) | Generate a mounting plate whose script is a test that happens to emit a part | FreeCAD |
| 4 | [Make it fail on purpose](04-make-it-fail-on-purpose.md) | Break the part, see every topology check stay green, and learn that `freecadcmd` exits 0 on failure | FreeCAD |
| 5 | [Look at the part, and check your checker](05-look-at-the-part.md) | Render an STL with no CAD GUI and catch a renderer that draws everything upside down | Python, numpy, Pillow |
| 6 | [Teach Claude the house rules](06-teach-claude-the-house-rules.md) | Install the skills and the CAD subagent so Claude does not rediscover each mistake | Claude Code |
| 7 | [The GIMP bridge](07-the-gimp-bridge.md) | Let Claude make and measure raster images, headless | GIMP 3.2, `uv` |
| 8 | [FreeCAD's live bridge](08-freecads-live-bridge.md) | Add a live FreeCAD window, and prove a bridge over stdio before restarting Claude | FreeCAD GUI, `uv` |
| 9 | [What this setup cannot tell you](09-what-this-cannot-tell-you.md) | Know the limits: fit, the screw you did not model, slicer orientation, the first real print | — |
| 10 | [From a drawing to a rigged model](10-from-a-drawing-to-a-rigged-model.md) | Take a generated image to a skinned, rigged glTF and check the rig, using what two experiments taught | Python, numpy |

**If you only have 20 minutes:** read parts 1 and 4, run the two commands at the end of part 4, and stop. That is the whole idea.

## Conventions

- Commands assume you are at the root of this repository. On macOS `freecadcmd` is
  `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd`; on Linux with the Flatpak it is
  `flatpak run --command=freecadcmd org.freecad.FreeCAD` (part 2 explains why the script path must then be absolute and under `$HOME`).
  The tutorial writes `freecadcmd` and means whichever you have.
- A **Check** box at the end of a part is something you run and compare. If your output differs, that is worth an issue.
- Every claim about tool behaviour was reproduced on a real machine, and part 9 lists which, when, and what was **not** run.
  Where something is a suspicion rather than a finding, the text says so.
- The tutorial was reorganised from a single long blog post into parts. The ideas are the same; the parts are shorter and each is
  runnable on its own.
