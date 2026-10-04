# Part 2: Install the tools

*Part 2 of 12 · about 10 minutes · in this part: get FreeCAD, GIMP 3 and `uv` installed, and dodge three traps.*

Last time we proved the headless path with a box. If you already have `freecadcmd` working you can skip to part 3 and come back for GIMP and `uv` at part 7. FreeCAD is all parts 1 to 6 need.

## macOS (Homebrew)

```sh
brew install --cask freecad gimp
brew install uv
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd --version
```

FreeCAD's command line lives inside the app bundle and is not on your `PATH`.

## Linux

Neither project maintains an official apt repository or PPA, so we use Flatpak:

```sh
flatpak install flathub org.gimp.GIMP org.freecad.FreeCAD
flatpak run --command=freecadcmd org.freecad.FreeCAD --version
```

Use `org.freecad.FreeCAD`; `org.freecadweb.FreeCAD` is the old, end-of-life ID.

## Three traps

1. **GIMP must be 3.2.x.** The bridge does not support 2.10, and Python-Fu is not packaged for 2.10 on current distributions. GIMP 3's Python API is a real break (no `pdb` object, colours are `Gegl.Color`), so don't carry 2.10 recipes over.
2. **The Flatpak FreeCAD cannot see `/tmp`.** Running a script from there fails with `Exception while processing file: x.py [Unknown file]` and **exit code 0**, which looks just like a script error. Keep scripts under `$HOME` and pass an absolute path. (Reproduced on FreeCAD 1.1.4, Linux, 2026-10-04.)
3. **Ask FreeCAD for its user data directory** instead of trusting a table:
   ```sh
   freecadcmd -c "import FreeCAD; print(FreeCAD.getUserAppDataDir())"
   ```
   It differs by build: unversioned on a macOS 1.0.2 install, `~/.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/` on the Linux Flatpak. Part 8 installs an addon there.

## Check

- [ ] `freecadcmd --version` (your form of it) prints a version.
- [ ] If you use the Flatpak, your scripts live under `$HOME`.

`./tools/doctor.sh` is a read-only report of what is installed and what is missing; run it whenever you are unsure.

---

**Next: [Part 3: Write a part that checks itself](03-write-a-part-that-checks-itself.md)**

[← Part 1: The idea, and the first check](01-the-idea-and-the-first-check.md) · [Series index](README.md)
