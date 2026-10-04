# Part 10: What this setup cannot tell you

*Part 10 of 12 · about 10 minutes · in this part: know where the checks stop, and what was actually run.*

Everything so far checks geometry. Before we move on, here is what it **doesn't** tell you.

## Fit

None of the checks ask "will this go together in PLA". Parts that meet at exactly 0.000 mm in CAD won't mate in plastic: you need a clearance budget (0.4 mm is where one project landed) and a check that fails below it. Iterate fits with full-scale *section coupons* of the real mating features. Scaling a model down is uniform and manufacturing isn't: at quarter scale a 0.4 mm clearance is 0.1 mm, below one extrusion width, and the parts fuse.

## The thing you didn't think of

In the largest build this approach was used on, the costliest defect was **18 of 25 fasteners specified with a screw that couldn't work.** Four fastener checks existed and all passed, because each modelled the **hole** and none modelled the **screw** as an object with a length. A check suite is a statement about what you already worried about.

## Slicer orientation

A slicer treats one file as one rigid body with one orientation. A flat panel with four feet, exported as one file, forced supports across the whole underside, "nearly impossible to remove". Anything that can't share an orientation with the rest has to be its own file.

## The first real print

The project this came out of, the [Dial Panel](https://github.com/slash-builder/hw-2015-dial-panel), is labelled BETA for exactly this reason: a real print found a ledge the slicer never warned about. **The same caveat applies to part 11's models: they slice, but none has been printed, and one would not have stayed on the bed.**

## What was actually run

The README's [Verified on](../../README.md#verified-on) table lists each run with its date, machine and tool versions. The latest, 2026-10-04 on FreeCAD 1.1.4 (Linux Flatpak): the good and broken plate runs, the exit-code table, the `/tmp` sandbox trap, the renderer, a headless Bambu Studio 2.8.2 slice of the plate and of both private models, and parts 11 and 12's tools.

**Not run:** Windows; GIMP 2.10; any slicer other than Bambu Studio; the FreeCAD bridge's FEM, parts-library and async tools; the *Start Agent Bridge* menu path in a live GUI window; Unity, Godot or Unreal for part 11's models. If something doesn't reproduce for you, an issue is more useful than a star.

## Check

- [ ] You can name one thing your checks would not catch on your own part.

---

**Next: [Part 11: From a drawing to a model](11-from-a-drawing-to-a-model.md)**

[← Part 9: Prove a bridge before you trust it](09-prove-a-bridge-before-you-trust-it.md) · [Series index](README.md)
