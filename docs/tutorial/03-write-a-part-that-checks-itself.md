# Part 3: Write a part that checks itself

**Goal:** run the example part and understand the three ideas that make its script a test. **Time:** 15 minutes.
**Previous:** [Part 2](02-install-the-tools.md). **Next:** [Part 4](04-make-it-fail-on-purpose.md).

The example, [`examples/mount-plate/mount_plate.py`](../../examples/mount-plate/mount_plate.py), is a deliberately boring mounting plate:
80 × 50 × 6 mm, four M3 clearance holes, and a centre boss with a blind bore for a heat-set insert. It is small enough to read in one
sitting and large enough to contain the failure modes that have actually cost prints.

## Dimensions are named constants

Every dimension is a constant at the top. Anything that had to be guessed carries a `PLACEHOLDER` comment, so an estimate can never pass
for a measurement:

```python
PLATE_L, PLATE_W, PLATE_T = 80.0, 50.0, 6.0
HOLE_D = 3.4            # M3 clearance
HOLE_INSET = 8.0
BOSS_D, BOSS_H = 20.0, 4.0
BORE_D = 4.0            # PLACEHOLDER: check your insert's datasheet
BORE_DEPTH = 6.5
OVERLAP = 0.2           # boss sinks into the plate so the fuse is a real fuse

NOZZLE = 0.4
MIN_WALL = 3 * NOZZLE   # three perimeters
```

## Three ideas carry the verification

None is clever. Each exists because a real part failed without it.

**1. Compute the expected answer by hand, not from the shape.** A shape's volume checked against a number derived from the same code that
built the shape checks nothing.

```python
def expected_volume():
    v = PLATE_L * PLATE_W * PLATE_T
    v += math.pi * (BOSS_D / 2) ** 2 * BOSS_H
    v -= 4 * math.pi * (HOLE_D / 2) ** 2 * PLATE_T
    v -= math.pi * (BORE_D / 2) ** 2 * BORE_DEPTH
    return v
```

**2. Verify the file you wrote, not the object that wrote it.** The script exports a STEP file, reads it back into a fresh shape, and runs
the whole battery again on that: one solid, `isValid()`, one shell per solid (more than one means a sealed internal void, which is
unprintable and invisible to the other two checks), bounding box equal to spec, fits the printer bed with a margin, and volume equal to
the hand calculation.

**3. Assert the feature, not the operation.** "I cut a hole" and "there is a hole" are different claims. The script measures the volume
each boolean actually removed and compares it with the cylinder it asked for, then probes the *finished* part at each hole's centre to
confirm it is open, so a later fuse that fills a bore back in is caught too.

## Run it

```sh
freecadcmd examples/mount-plate/mount_plate.py
```

(Flatpak: `flatpak run --command=freecadcmd org.freecad.FreeCAD "$PWD/examples/mount-plate/mount_plate.py"`; see [part 2](02-install-the-tools.md#three-traps).)

```
mount plate
  ok    fuse produced one solid (got 1)
[built]
  ok    one solid (got 1)
  ok    shape is valid
  ok    solid 0: one shell, no enclosed void (got 1)
  ok    bounding box 80.000 x 50.000 x 10.000 == spec 80.000 x 50.000 x 10.000
  ok    fits the build volume with margin
  ok    volume 24957.05 mm3 vs hand-computed 24957.05 mm3 (0.0000% off)
[features]
  ok    hole 0 removed 54.48 mm3 (a real hole removes 54.48)
  ...
  ok    insert bore is still open on the finished part
[re-imported STEP]
  ok    volume 24957.05 mm3 vs hand-computed 24957.05 mm3 (0.0000% off)

ALL CHECKS PASSED
```

It writes `out/mount-plate.step` and `out/mount-plate.stl` (a copy of each is committed under `examples/mount-plate/`). The same run,
on FreeCAD 1.1.4 on Linux, passes 27 checks and exits 0.

## Check

- [ ] The run ends with `ALL CHECKS PASSED` and exit code 0 (`echo $?` straight after).
- [ ] You can point at the line in the script where the expected volume is computed, and see that it uses only the constants.

That is the good run. The more important run is the next one.
