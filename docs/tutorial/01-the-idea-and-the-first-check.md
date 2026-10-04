# Part 1: The idea, and the first check

*Part 1 of 12 · about 10 minutes · in this part: see the shape of the system and prove the headless path with one number you computed yourself.*

This series sets up Claude Code, FreeCAD and GIMP to design 3D-printable parts. The part that took the longest was not getting Claude to drive CAD. It was getting the setup to **tell us when it is wrong**, so most of what follows is about that.

## The shape of the system

| Layer | Tool | Headless? | When you need it |
|---|---|---|---|
| Driver | Claude Code | n/a | always |
| CAD | FreeCAD via `freecadcmd` | **yes** | always: this is the main path |
| CAD, live window | FreeCAD + the `freecad-mcp` bridge | **no** | only to *see* the model |
| Images | GIMP 3.2 + the `gimp-agent-mcp` bridge | **yes** | renders, concept sheets, labelled assets |

The default path has **no bridge**. Claude writes a Python script, `freecadcmd` runs it, and the script exports STEP and STL and checks its own work. That is reproducible, runs unattended, and works in CI. The bridges come later (parts 7 to 9).

The one idea to hold on to: **a CAD script should be a test that happens to emit a part.**

## The first check

Before installing anything else, prove the headless path:

```sh
freecadcmd -c "
import Part
b = Part.makeBox(10, 20, 30)
print('volume=%.1f solids=%d valid=%s' % (b.Volume, len(b.Solids), b.isValid()))"
```

```
volume=6000.0 solids=1 valid=True
```

`10 × 20 × 30 = 6000`. That is the whole habit in miniature: **compare what the tool says with a number you worked out yourself.** Everything later is that habit applied to harder shapes.

(No `freecadcmd` yet? Part 2 installs it. Where it lives on your machine is in the [index](README.md#conventions).)

## Check

- [ ] The command prints `volume=6000.0 solids=1 valid=True`.
- [ ] You can say why we compared against `10 × 20 × 30` and not against a second FreeCAD call. A check whose expected value comes from the code under test checks nothing.

---

**Next: [Part 2: Install the tools](02-install-the-tools.md)**

[← Series index](README.md) · [Series index](README.md)
