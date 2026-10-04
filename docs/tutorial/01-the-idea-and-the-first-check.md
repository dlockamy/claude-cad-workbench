# Part 1: The idea, and the first check

**Goal:** understand the shape of the system, and prove the headless path works with one number you computed yourself.
**Time:** 10 minutes. **Needs:** FreeCAD installed (part 2 if not). **Next:** [Part 2](02-install-the-tools.md).

## The shape of the system

Three tools, two ways of connecting them, and one of the two is optional.

| Layer | Tool | Runs headless? | When you need it |
|---|---|---|---|
| Driver | Claude Code | — | always |
| CAD | FreeCAD, via `freecadcmd` | **yes** | always: this is the main path |
| CAD (live window) | FreeCAD + the `freecad-mcp` bridge | **no** | only to *see* the model, or to iterate with a window open |
| Images | GIMP 3.2 + the `gimp-agent-mcp` bridge | **yes** | renders, concept sheets, labelled assets |

The default path involves **no bridge at all**. Claude writes a Python script; `freecadcmd` runs it; the script exports STEP and STL and
checks its own work. That is reproducible, runs unattended, and works in CI. The bridges add a live window on top: useful, but a
different thing. The FreeCAD one has a constraint ([part 8](08-freecads-live-bridge.md)) that decides how much you can lean on it.

## The idea in one sentence

**A CAD script should be a test that happens to emit a part**, not a part-maker that happens to print some numbers. The rest of the
tutorial is what that costs and what it buys.

## The first check

Do not install anything else until this works:

```sh
freecadcmd -c "
import Part
b = Part.makeBox(10, 20, 30)
print('volume=%.1f solids=%d valid=%s' % (b.Volume, len(b.Solids), b.isValid()))"
```

```
volume=6000.0 solids=1 valid=True
```

`10 × 20 × 30 = 6000`. That is the whole habit in miniature: **compare what the tool says against a number you computed yourself.**
Everything later is that habit applied to harder shapes.

## Check

- [ ] The command prints `volume=6000.0 solids=1 valid=True`.
- [ ] You can say, without looking, why you compared against `10 × 20 × 30` rather than against another call to FreeCAD.
  (A check whose expected value comes from the same code that built the shape checks nothing.)

If the command is not found, see the paths in the [tutorial index](README.md#conventions), then [part 2](02-install-the-tools.md).
