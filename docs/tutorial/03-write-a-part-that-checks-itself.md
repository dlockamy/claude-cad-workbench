# Part 3: Write a part that checks itself

*Part 3 of 12 · about 15 minutes · in this part: run the example plate and understand the three ideas that make its script a test.*

Now we have a working `freecadcmd`. The example part, [`examples/mount-plate/mount_plate.py`](../../examples/mount-plate/mount_plate.py), is deliberately boring: an 80 × 50 × 6 mm plate, four M3 clearance holes, and a centre boss with a blind bore for a heat-set insert. It is small enough to read in one sitting and still holds the failure modes that have cost real prints.

## Constants first

Every dimension is a named constant. Anything we had to guess carries a `PLACEHOLDER` comment, so an estimate can't pass for a measurement:

```python
PLATE_L, PLATE_W, PLATE_T = 80.0, 50.0, 6.0
HOLE_D = 3.4            # M3 clearance
BOSS_D, BOSS_H = 20.0, 4.0
BORE_D = 4.0            # PLACEHOLDER: check your insert's datasheet
BORE_DEPTH = 6.5
OVERLAP = 0.2           # boss sinks into the plate so the fuse is a real fuse
MIN_WALL = 3 * 0.4      # three perimeters at a 0.4 mm nozzle
```

## Three ideas

**1. Work out the expected answer by hand.** Not from the shape: a volume checked against a number derived from the same code checks nothing.

```python
def expected_volume():
    v = PLATE_L * PLATE_W * PLATE_T
    v += math.pi * (BOSS_D / 2) ** 2 * BOSS_H
    v -= 4 * math.pi * (HOLE_D / 2) ** 2 * PLATE_T
    v -= math.pi * (BORE_D / 2) ** 2 * BORE_DEPTH
    return v
```

**2. Verify the file you wrote, not the object that wrote it.** The script exports STEP, reads it back into a fresh shape, and runs the whole battery again: one solid, valid, one shell per solid (more than one is a sealed internal void), bounding box equal to spec, fits the bed with margin, volume equal to the hand calculation.

**3. Assert the feature, not the operation.** "I cut a hole" and "there is a hole" are different claims. The script measures what each boolean actually removed, then probes the *finished* part at each hole's centre to confirm it is open.

## Run it

```sh
freecadcmd examples/mount-plate/mount_plate.py
```

```
[built]
  ok    one solid (got 1)
  ok    shape is valid
  ok    bounding box 80.000 x 50.000 x 10.000 == spec 80.000 x 50.000 x 10.000
  ok    volume 24957.05 mm3 vs hand-computed 24957.05 mm3 (0.0000% off)
[features]
  ok    hole 0 removed 54.48 mm3 (a real hole removes 54.48)
  ...
ALL CHECKS PASSED
```

It writes `out/mount-plate.step` and `.stl`. On FreeCAD 1.1.4 (Linux) it passes 27 checks and exits 0.

## Check

- [ ] The run ends with `ALL CHECKS PASSED`, and `echo $?` says `0`.
- [ ] You can point at the line that computes the expected volume and see it uses only the constants.

---

**Next: [Part 4: Make it fail on purpose](04-make-it-fail-on-purpose.md)**

[← Part 2: Install the tools](02-install-the-tools.md) · [Series index](README.md)
