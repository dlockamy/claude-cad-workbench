# Part 11: From a drawing to a model

*Part 11 of 12 · about 15 minutes · in this part: turn one generated image into a skinned 3D model, and be honest about what is measured and what is guessed.*

The last two parts go beyond printing: taking a *drawing* of a character (from a local image generator) to a textured, rigged 3D model that plays clips in a web viewer. We did it twice, on two private experiments chosen to differ: a near-symmetric push-pop mascot, which is a revolve and nearly follows from one front view, and a humanoid seen from the front only.

> **Status.** Both were built, validated, viewed and **sliced** (step 7). **Neither has been printed**, and nobody has judged how the animations feel at real-time speed.

## Seven steps

1. **Measure the drawing.** Matte the figure and take per-row widths. Don't eyeball dimensions.
2. **Write one parts spec.** Each part is a stack of elliptical cross-sections along a path, or an ellipsoid. Widths come from the measurement; depth is an **assumption** unless you have a second view. Mirror the second half.
3. **CAD from the spec**, headless, with parts 3 and 4's habits: export, read it back, check one solid.
4. **Skin from the same spec.** Mesh the same sections so vertices land on the silhouette, and project the drawing onto the front of each part. One spec feeding both CAD and skin keeps them from drifting.
5. **Rig.** A joint hierarchy, weights from position, a few clips.
6. **Validate** with checks independent of the code that built the rig (part 12).
7. **Slice it**, even if you only meant to animate it. A clean slice is not a printable model, as the next section shows.

## Slice it before you believe it

Bambu Studio can slice from the command line with no window. Inside the Flatpak the profiles are under `/app/share/BambuStudio/profiles/BBL`:

```sh
P=/app/share/BambuStudio/profiles/BBL
flatpak run --filesystem=$HOME --command=bambu-studio com.bambulab.BambuStudio --slice 0 --arrange 1 \
  --load-settings "$P/machine/Bambu Lab A1 0.4 nozzle.json;$P/process/0.20mm Standard @BBL A1.json" \
  --load-filaments "$P/filament/Generic PLA @BBL A1.json" \
  --outputdir "$HOME/slice-out" "$HOME/model.stl"
python3 tools/slice_report.py "$HOME/slice-out/plate_1.gcode"
```

[`tools/slice_report.py`](../../tools/slice_report.py) prints the time, layers and filament, and the one number the slicer won't warn you about: **how much plastic the first layer is.** On Bambu Studio 2.8.2 (A1, 0.4 mm nozzle, 0.20 mm layers, generic PLA, no supports, 2026-10-04):

| Model | Slicer result | Est. time | First layer |
|---|---|---|---|
| The part-3 plate | Success | 1 h 37 m | 11,319 mm of path |
| Humanoid | Success | 4 h 33 m | 649 mm (two feet) |
| Push-pop mascot | Success | 2 h 56 m | **38 mm of path, no flat face on the bed** |

All three "succeed". The mascot's stick ends in a rounded tip, so it stands on something close to a dot and will not stay on the bed, and nothing in the slicer's output says so. Turning supports on (same settings) raises the humanoid to 7 h 23 m and the mascot to 4 h 54 m, about 55 to 60% more filament each, which is also a hint that neither was designed to be printed upright. They were designed to be *looked at*. That is the same lesson as part 10, one stage later.

## What we learned on the way

**The back is invented.** On the revolve, one view nearly covers everything. On the humanoid, depth, the whole back, the scale and any hidden half of what it carries are all guesses. The back texture was a darkened, smoothed copy of the front with the face painted out, and it renders nearly black. The honest verdict: *works for the front; the rest is guessed.* Say so wherever you publish.

**Matte against the background you actually have.** The humanoid was dark grey on dark grey, and a plain threshold filled the gap between the legs and merged the floor shadow into the feet. What worked on the third attempt: fit a smooth polynomial to the backdrop (it was a vignette), threshold the *difference*, and rebuild the lower body separately so the leg gap stays open and the shadow is dropped.

**A per-part check is not a whole-model check.** Every part was a valid solid and the fused model wasn't (an inside-out loft and two floating groups). Check the thing you will use.

## Check

- [ ] For a model you built from one image, you can say which parts are measured and which are invented.
- [ ] Your CAD and your skin come from the same spec.

---

**Next: [Part 12: Check the rig](12-check-the-rig.md)**

[← Part 10: What this setup cannot tell you](10-what-this-cannot-tell-you.md) · [Series index](README.md)
