# Part 11: From a drawing to a model

*Part 11 of 12 · about 15 minutes · in this part: turn one generated image into a skinned 3D model, and be honest about what is measured and what is guessed.*

The last two parts go beyond printing: taking a *drawing* of a character (from a local image generator) to a textured, rigged 3D model that plays clips in a web viewer. We did it twice, on two private experiments chosen to differ: a near-symmetric push-pop mascot, which is a revolve and nearly follows from one front view, and a humanoid seen from the front only.

> **Status.** Both were built, validated and viewed. **Neither has been sliced or printed**, and nobody has judged how the animations feel at real-time speed.

## Six steps

1. **Measure the drawing.** Matte the figure and take per-row widths. Don't eyeball dimensions.
2. **Write one parts spec.** Each part is a stack of elliptical cross-sections along a path, or an ellipsoid. Widths come from the measurement; depth is an **assumption** unless you have a second view. Mirror the second half.
3. **CAD from the spec**, headless, with parts 3 and 4's habits: export, read it back, check one solid.
4. **Skin from the same spec.** Mesh the same sections so vertices land on the silhouette, and project the drawing onto the front of each part. One spec feeding both CAD and skin keeps them from drifting.
5. **Rig.** A joint hierarchy, weights from position, a few clips.
6. **Validate** with checks independent of the code that built the rig (part 12).

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
