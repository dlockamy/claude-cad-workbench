# Part 4: Make it fail on purpose

*Part 4 of 12 · about 15 minutes · in this part: break the part, watch every topology check stay green, and learn why `freecadcmd`'s exit code can't be trusted.*

A check you have never seen fail is not a check, so let's break the plate. The example has a switch that moves one mounting hole off the plate:

```sh
MOUNT_PLATE_BREAK=1 freecadcmd examples/mount-plate/mount_plate.py
```

```
[built]
  ok    one solid (got 1)
  ok    shape is valid
  ok    bounding box 80.000 x 50.000 x 10.000 == spec 80.000 x 50.000 x 10.000
  FAIL  volume 25011.53 mm3 vs hand-computed 24957.05 mm3 (0.2183% off)
[features]
  FAIL  hole 0 removed 0.00 mm3 (a real hole removes 54.48)
  FAIL  hole 0 centre is on the plate and open

5 CHECK(S) FAILED
```

Look at what stayed green: one solid, valid, right bounding box. **A missing hole passes every topology check.** A boolean cut whose tool sits outside the part "succeeds": it removes nothing and raises nothing. Only the volume and feature checks catch it. (This is a real defect: a clearance hole once landed a millimetre outside a part, removed 0.00 mm³, and left a small nick instead of a hole.)

## The exit code

That run exits `1`. It is worth checking, because `freecadcmd` is not honest about failure:

| You run | Result |
|---|---|
| `freecadcmd script.py`, script raises | prints `Exception while processing file`, **exits 0** |
| `freecadcmd script.py`, syntax error | **exits 0** |
| `freecadcmd -c "raise RuntimeError()"` | exits 1 |
| script calls `sys.exit(3)` | exits 3 |
| script prints then `sys.exit(3)`, output redirected | **empty file**, unless `print(..., flush=True)` |

Reproduced on FreeCAD 1.0.2 (macOS) and 1.1.4 (Linux Flatpak). What it means for us:

- Don't trust the exit code of a script file. The example's `check()` helper records failures and the script ends with `sys.exit(1)`.
- A script that raises **runs twice** (once with `__name__` set to the file stem, once as `__main__`).
- `__name__` is the filename, so an `if __name__ == "__main__":` guard silently runs nothing. Call `main()` directly.
- Use `print(..., flush=True)` everywhere. It only bites in CI, as a red build with no explanation.
- `freecadcmd` leaves a `__pycache__/` beside the script; add it to `.gitignore`.

## Check

- [ ] The broken run prints failures and `echo $?` says `1`.
- [ ] You can name which checks passed anyway, and which caught it.
- [ ] You made your own toolchain fail on purpose once and read what the exit code said.

---

**Next: [Part 5: Look at the part, and check your checker](05-look-at-the-part.md)**

[← Part 3: Write a part that checks itself](03-write-a-part-that-checks-itself.md) · [Series index](README.md)
