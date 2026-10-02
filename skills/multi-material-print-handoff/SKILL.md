---
name: multi-material-print-handoff
description: Get verified CAD geometry to a multi-colour or multi-material 3D print — badges, two-tone enclosures, inlaid logos, colour-coded keys — and fix models that open wrong in a slicer (upside down, detached parts, off the bed). Use after parametric-cad-verify when a part needs more than one filament.
---

# Multi-material print handoff

## The one fact that governs everything

**STL cannot carry colour.** So colour is not a property you attach; it is
*separate geometry plus a container that says which filament each piece uses*
(a slicer project such as `.3mf`). Everything below follows from that. Single
material? Export STL/3MF and stop.

## Procedure

1. **Model each colour's volume as its own solid from the start.** Fuse a copy
   only for the single-material export. Make the parts **meet, not overlap**, on
   a flat plane — coincident faces at a known Z give the slicer a clean layer
   transition. (Opposite of the fuse rule in `parametric-cad-verify`: that
   applies to solids that must *become one*.)
2. **Verify against the slicer, not a predicate.** Load every exported mesh into
   the real slicer's CLI and read what *it* says about manifoldness, part count
   and size. The modelling kernel and the slicer disagree; the slicer is the
   consumer.
3. **Never "repair" a mesh to clear a warning.** Repair calls delete facets. One
   cleared a non-manifold flag by carving a wedge out of a letter `k` — every
   assertion passed while a glyph was destroyed, and the slicer had called the
   original clean anyway. If the warning is cosmetic to the slicer, leave it; if
   real, fix the geometry.
4. **One object with N parts — not N objects.** Separate objects are re-seated
   on the bed independently at load, silently discarding relative position: a
   raised feature drops to Z=0 and ends up buried in the base.
5. **Place it explicitly.** Bed coordinates usually run `0..W`, not
   `-W/2..W/2`; geometry modelled about the origin loads half off the plate. Set
   the build transform to the bed centre and lift so the lowest face is Z=0.
6. **Assign a filament per part in the project's own metadata.** Generic 3MF
   `<basematerials>` is spec-compliant but slicers often ignore it and read
   their own per-part extruder metadata. Write both.
7. **Render it and look before handing over.** Every failure below passed its
   automated check.

## Raised or engraved text

- Needs a font **file path**, not a family name.
- **Variable fonts render as their default instance** (usually Regular — no
  bold). Instance a static cut first:
  `fontTools.varLib.instancer.instantiateVariableFont(f, {"wght": 700})`; ship
  the instanced file (and its licence) so the model regenerates.
- **Tracking is not "mm added per gap".** Measure: render at tracking 0 and 1,
  take the slope, solve for the target width, re-measure once. A model assumed
  from glyph count was wrong by 12%.
- **Assert the typographic intent** (two lines meant to share a width) in the
  build so it fails when it drifts.
- **A feature below the nozzle width is not a feature.** 0.06–0.18 mm strokes
  against a 0.4 mm nozzle are valid, correctly placed, slice without warning,
  and come off the bed blank.

## Gotchas

- **Tool disagreement is normal — pick the consumer.**
- **An intra-glyph defect can't be fixed by kerning.** Volume of an overlapping
  pair was identical at every tracking value, proving the overlap was inside one
  glyph. Measure before theorising.
- **Finer tessellation doesn't fix topology.**
- **A slicer CLI may crash on its own project files** (Bambu Studio 02.08
  segfaulted, exit 139, on `--info` for *any* project 3MF — proven with an
  unmodified control before blaming the hand-built file). Verify meshes as STL;
  leave project verification to the GUI.
- **A slicer is usually single-instance.** With the GUI open, CLI calls hand off
  to it and return nothing — which looks exactly like a hang.
- **Slicer CLIs drop artifacts in the working directory** (`result.json`).
  `.gitignore` them.
- **Filament-id flags map to input *files*, not parts.**

## Slicer adapter (Bambu Studio 2.08)

| Concern | Bambu Studio |
|---|---|
| Project format | `.3mf` with `Metadata/*.config` |
| One object, N parts | one `<object>` with N `<component>`s in `3D/3dmodel.model`; N `<part>`s in `model_settings.config` |
| Filament per part | `<metadata key="extruder" value="N"/>` on the part |
| Colour swatches | `filament_colour` in `project_settings.config` (extend every per-filament array to N) |
| Bed placement | `<item transform="…">`, bed `0..200` |
| Headless check | `--info` (STL only — crashes on projects) |
