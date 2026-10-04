# Part 9: What this setup cannot tell you

**Goal:** know where the checks stop, and what was actually run. **Time:** 10 minutes. **Previous:** [Part 8](08-freecads-live-bridge.md).
**Next:** [Part 10](10-from-a-drawing-to-a-rigged-model.md).

This would be overselling it if it stopped at the green checkmarks.

## It checks geometry, not fit

Every check in parts 3 and 4 asks "is this model correct". None asks "will this go together in PLA." Parts that meet at exactly 0.000 mm
in CAD will not mate in plastic: you need a real clearance budget (0.4 mm is where one project landed) and a check that fails below it.
When iterating fits, print full-scale *section coupons* of the real mating features, not a scaled-down model. Scaling is uniform and
manufacturing is not: at quarter scale a 0.4 mm clearance becomes 0.1 mm, below one extrusion width, and the parts fuse.

## It checks the holes you thought of

In the largest build this approach was used on, the single most expensive defect was **18 of 25 fasteners specified with a screw that
could not work.** Four separate fastener checks existed and all passed, because every one modelled the **hole**, and none modelled the
**screw** as an object with a length. A check suite is a statement about what you already worried about.

## Slicer orientation is a modelling decision

A slicer treats one file as one rigid body with one orientation. A flat panel with four feet, exported as a single file, forced supports
across the whole underside, "nearly impossible to remove" after printing. Anything that cannot share an orientation with the rest of the
part has to be its own file.

## The first real print is still the real test

The larger project this approach came out of, the [Dial Panel](https://github.com/slash-builder/hw-2015-dial-panel) (a wall-mounted
smart-home panel, generated from one parametric script and sliced plate by plate as a test), is labelled BETA in its own README for
exactly this reason: a real print found a ledge the slicer never warned about.

**The same caveat applies to everything in [part 10](10-from-a-drawing-to-a-rigged-model.md): none of those models has been sliced or
printed.**

## What was actually run, and when

The setup accumulated across several sessions on different machines. This is what was run, as opposed to relayed from vendor docs:

| Date | What | Where |
|---|---|---|
| 2026-10-04 | `mount_plate.py` good run (27 checks, exit 0) and `MOUNT_PLATE_BREAK=1` (5 failures, exit 1); the `freecadcmd` exit-code table in part 4; the `/tmp` sandbox trap; `render_stl_iso.py`; `check_rig.py` and the skinned-tube example (part 10) | FreeCAD 1.1.4 Flatpak, Linux |
| 2026-10-02 | `mount_plate.py` good and broken, the four `freecadcmd` behaviours, `doctor.sh`, `install.sh` (scratch dir), `install-freecad-addon.sh --dest`, the renderer | FreeCAD 1.0.2, macOS |
| 2026-10-02 | GIMP bridge 0.5.0: `install-plugin`, `doctor`, `smoke` (24 checks, headless), `mcp_probe.py` (39 tools, an image opened, a pixel read back to the known value) | GIMP 3.2.6, macOS |
| 2026-10-02 | FreeCAD bridge 0.1.25: 17 tools; plate + boss − bore volume 49175.7 mm³ against hand-computed 49175.7 through `execute_code` and `execute_code_headless`; a committed STEP loaded live read 24957.05 mm³ | FreeCAD 1.0.2, macOS |
| 2026-09-26 | Headless and GUI FreeCAD, GIMP batch, Bambu Studio opening the exported STL and independently reporting the same dimensions | Flatpak GIMP 3.2.6 and FreeCAD 1.1.3, Ubuntu 24.04 |
| 2026-09-19 | Both bridges driven over stdio; geometry read back against a hand-computed volume | GIMP 3.2.6, FreeCAD 1.1.3, macOS |

**Not run:** Windows; GIMP 2.10; any slicer other than Bambu Studio; the FreeCAD bridge's other tools (FEM, the parts library, async jobs);
the *Filters → Development → Start Agent Bridge* menu path in a live GUI window; Unity, Godot or Unreal for part 10's models.

If something does not reproduce for you, that is more useful than a star: open an issue.
