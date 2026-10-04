# Part 5: Look at the part, and check your checker

**Goal:** render an STL on a machine with no CAD GUI, and learn why the renderer itself needs a test. **Time:** 10 minutes.
**Needs:** Python 3, `numpy`, `Pillow`. **Previous:** [Part 4](04-make-it-fail-on-purpose.md). **Next:** [Part 6](06-teach-claude-the-house-rules.md).

Verification by numbers has a blind spot: you cannot tell a part looks wrong from its volume. You want to *see* it, including on a build
server or an SSH session with no display.

## The renderer

[`tools/render_stl_iso.py`](../../tools/render_stl_iso.py) is about 130 lines (numpy + Pillow). It parses a binary STL, recomputes face
normals from the geometry, applies a classic isometric rotation, shades against a fixed light, and rasterizes with a real **z-buffer**.

```sh
pip install numpy pillow
python3 tools/render_stl_iso.py examples/mount-plate/mount-plate.stl /tmp/plate.png
```

![The mounting plate rendered from its STL: four clearance holes and a raised centre boss with an insert bore](../img/mount-plate-iso.png)

(Also ran on Linux on 2026-10-04: it writes a 1400 × 1400 image of the same view. The file bytes differ from the committed PNG because the image
library version differs; the picture is the same.)

## The first renderer I wrote was wrong

That image is correct. The first one I rendered was not. The renderer I started from, put together earlier for a different part, tipped
the model the wrong way about the X axis, so **+Z pointed down the screen**. The part was upside down: the raised boss drew as a recess,
and the plate's edge walls showed on the far side. It looked plausible enough that it was only caught because I knew what the boss should
look like. An earlier preview from the same renderer had the same defect and sat in a notes folder, unnoticed, with a README that called
it "verified".

The bug was one sign. The classic isometric view spins the model 45° about Z, then tips it **toward** the camera by `90 − 35.264 = 54.736°`
about X. Use `+35.264°` and the model tips the other way.

Three rules came out of it:

1. **Test your checker against a part whose answer you already know.** Render an asymmetric reference (a plate with a boss on top) once,
   confirm the boss reads as raised, and only then trust the tool on real parts.
2. **Use a z-buffer, not a depth sort.** A painter's-algorithm sort leaves black artifacts where coplanar triangles meet, such as a boss
   on a plate.
3. **One view is not verification.** An isometric flatters detail and hides profile. For a part defined by an angle or a taper, render
   the orthographic view that feature lives in. (A canted-head device once looked right in isometric and was structurally wrong: the cant
   had been cut as a recess into a vertical face, and only a side view showed a flat rectangle where a wedge belonged.)

> **A side note on asking a model to find this bug.** The inverted renderer is a good test case for LLM code review because the answer is
> known. Three local models (3B, 7B coder, 7B general) were given the broken script and the symptom, three attempts each, and a 14B model
> three more. **All twelve answers blamed a different line (the image-Y flip, which is correct) and said to remove it.** They were fluent,
> specific and wrong. Reasoning about coordinate transforms is exactly where a plausible suspect beats the real one, so do not treat a model's
> confident review of geometry code as a substitute for rendering a known part.

## Check

- [ ] Your render shows four holes and a boss that reads as **raised**, with the plate's side walls on the near side.
- [ ] You have a rule for your own tooling: before a new preview tool judges a real part, it renders one you know.
