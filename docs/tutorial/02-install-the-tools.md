# Part 2: Install the tools

**Goal:** FreeCAD, GIMP 3 and `uv` installed, with the version traps avoided. **Time:** 10–15 minutes.
**Previous:** [Part 1](01-the-idea-and-the-first-check.md). **Next:** [Part 3](03-write-a-part-that-checks-itself.md).

You can skip GIMP and `uv` until parts 7 and 8. FreeCAD is all parts 1–6 need.

## macOS (Homebrew)

The cask names exist (checked with `brew info`):

```sh
brew install --cask freecad gimp
brew install uv
```

FreeCAD's command line ships *inside* the app bundle and is not on your `PATH`:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd --version
```

## Linux

Neither GIMP nor FreeCAD maintains an official apt repository or PPA (checked, not assumed). The upstream-blessed routes are Flatpak
or AppImage; this tutorial uses Flatpak:

```sh
flatpak install flathub org.gimp.GIMP org.freecad.FreeCAD
flatpak run --command=freecadcmd org.freecad.FreeCAD --version
```

Mind the app ID: `org.freecadweb.FreeCAD` is the old, end-of-life one.

## Three traps

1. **GIMP must be 3.2.x.** The bridge does not support 2.10, and Python-Fu is not packaged for 2.10 on current distributions (there is no
   `gimp-python` on Ubuntu 24.04). GIMP 3's Python API is a genuine break: there is no `pdb` object, colours are `Gegl.Color` rather
   than tuples, and fonts and gradients are looked up as objects. Do not carry 2.10 recipes across.
2. **The Flatpak FreeCAD cannot see `/tmp`.** Flatpak sandboxes give each app a private `/tmp`, so:
   ```sh
   flatpak run --command=freecadcmd org.freecad.FreeCAD /tmp/x.py
   ```
   fails with `Exception while processing file: x.py [Unknown file]` and **exit code 0**, which looks exactly like a script error.
   Keep scripts and outputs under `$HOME` and pass an **absolute** path. (Reproduced on FreeCAD 1.1.4, Linux, 2026-10-04. It is per-app,
   not universal: check each Flatpak you use.)
3. **Ask FreeCAD where its per-user data directory is; do not copy it from a table.** It differs by build:
   ```sh
   freecadcmd -c "import FreeCAD; print(FreeCAD.getUserAppDataDir())"
   ```
   gave the unversioned `…/FreeCAD/` on a macOS 1.0.2 install, and `~/.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/` on the Linux
   Flatpak 1.1.4. This matters in [part 8](08-freecads-live-bridge.md), which installs an addon into it.

## Check

- [ ] `freecadcmd --version` (your form of it) prints a FreeCAD version.
- [ ] You know which `freecadcmd` form you will use for the rest of the tutorial, and (Flatpak) that your scripts live under `$HOME`.
- [ ] (Optional now) GIMP reports 3.2.x; `uv --version` works.

Run `./tools/doctor.sh` at any point: it is read-only and tells you what is installed and what is missing.
