# Part 4: Make it fail on purpose

**Goal:** see a broken part pass every topology check, and learn that `freecadcmd` can exit 0 on a failed build.
**Time:** 15 minutes. **Previous:** [Part 3](03-write-a-part-that-checks-itself.md). **Next:** [Part 5](05-look-at-the-part.md).

A check you have never seen fail is not a check.

## Break the part

The example has a switch that moves one mounting hole so its centre lands off the plate:

```sh
MOUNT_PLATE_BREAK=1 freecadcmd examples/mount-plate/mount_plate.py
```

Read the first block closely:

```
[built]
  ok    one solid (got 1)
  ok    shape is valid
  ok    solid 0: one shell, no enclosed void (got 1)
  ok    bounding box 80.000 x 50.000 x 10.000 == spec 80.000 x 50.000 x 10.000
  ok    fits the build volume with margin
  FAIL  volume 25011.53 mm3 vs hand-computed 24957.05 mm3 (0.2183% off)
[features]
  FAIL  hole 0 removed 0.00 mm3 (a real hole removes 54.48)
  FAIL  hole 0 keeps -9.70 mm of wall (min 1.20)
  FAIL  hole 0 centre is on the plate and open

5 CHECK(S) FAILED
```

The part has a missing hole and **every topology check is green**: one solid, valid, one shell, the right bounding box, fits the bed. A
boolean cut whose tool sits entirely outside the part "succeeds": it removes nothing and raises nothing. Only the checks that look at
*features* and *volume* catch it. This is a real defect, not a contrivance: a clearance hole whose centre landed a millimetre outside a
part removed 0.00 mm³ and left a tiny nick in the corner instead of a hole, while solid count, validity and interference all passed.

The exit code of that run is `1`. Which brings us to the thing that nearly made all of this pointless.

## `freecadcmd` will lie to you about success

Each of these was reproduced, on FreeCAD 1.0.2 (macOS, 2026-10-02) and again on **1.1.4 (Linux Flatpak, 2026-10-04)**; the results matched.

| You run | Result |
|---|---|
| `freecadcmd script.py`, script raises | prints `Exception while processing file: ... [boom]` and **exits 0** |
| `freecadcmd script.py`, script has a syntax error | same: **exits 0** |
| `freecadcmd -c "raise RuntimeError()"` | exits **1** (the inline form is honest) |
| script calls `sys.exit(3)` | exits **3**: the escape hatch works |
| script prints, then `sys.exit(3)`, output redirected to a file | the file is **empty** unless the `print` used `flush=True` |

Four consequences:

- **Any CI step or agent that trusts the exit code of a script file is trusting a number that cannot report failure.** The example's
  `check()` helper never raises: it records failures, and the script calls `sys.exit(1)` at the end.
- **A script that raises runs twice**: first with `__name__` set to the file's stem, then again as `__main__`. Side effects happen twice.
- **`__name__` is the filename, not `"__main__"`**, so the usual `if __name__ == "__main__":` guard silently runs nothing: no error,
  exit 0, zero files written. Call `main()` unconditionally.
- **Use `print(..., flush=True)` everywhere.** It is invisible in a terminal and only bites in CI, as a red build with no explanation.

One tidy-up: `freecadcmd` leaves a `__pycache__/` next to the script it runs. Put it in `.gitignore`.

## Check

- [ ] `MOUNT_PLATE_BREAK=1 freecadcmd ...` prints failures and `echo $?` gives `1`.
- [ ] You can name which checks passed anyway (all the topology ones) and which caught the problem (volume and features).
- [ ] You have, for your own toolchain, made a script fail on purpose and watched what the exit code said. Thirty seconds, cheap insurance.
