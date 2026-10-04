# Part 10: From a drawing to a rigged model, and checking the rig

**Goal:** understand how a single generated image becomes a skinned, rigged glTF, and run a check that catches the failures stills hide.
**Time:** 20 minutes. **Needs:** Python 3 and `numpy`. **Previous:** [Part 9](09-what-this-cannot-tell-you.md). **Back to:** [the index](README.md).

Parts 1–9 are about parts you print. This part is about the other thing this setup turned out to do: take a *drawing* of a character (here,
an image from a local image generator) to a textured, rigged 3D model that plays animation clips in a web viewer. It was done twice, on
two private experiments chosen to be different: a near-symmetric push-pop mascot (a revolve, so one front view is almost enough) and a
humanoid seen from the front only. What follows is the method, what broke, and the one check small enough to ship here.

> **Status, plainly.** Both models were built, validated and viewed. **Neither has been sliced or printed**, and nobody has watched the
> animations at real-time speed to judge how they feel. Part 9's caveat about the first real print applies in full.

## The method, in six steps

1. **Measure the drawing.** Matte the figure from its background and measure per-row widths. Do not eyeball dimensions.
2. **Write one parts spec.** A list of parts, each a stack of elliptical cross-sections along a path (sweeps) or an ellipsoid. Widths come
   from the measurement; depth is an **assumption** unless you have a second view. Mirror the second half.
3. **CAD from the spec**, headless, with the verification habits of parts 3–4: build, export STEP and STL, read it back, check one solid.
4. **Skin from the *same* spec.** Mesh the same cross-sections so the vertices land exactly on the silhouette, and project the drawing onto
   the front of each part as the texture. One spec feeding both CAD and skin keeps them from drifting apart.
5. **Rig.** A joint hierarchy, weights computed from position, and a few clips.
6. **Validate**, with checks that are independent of the code that built the rig.

## What each step taught

**The back is invented.** On the revolve, one view nearly covers everything. On the humanoid, **depth, the whole back, the scale and the
hidden half of anything it carries are all assumptions**, and the back atlas was a darkened, smoothed copy of the front with the face and
chest painted out. It renders nearly black. The honest verdict on the humanoid was: *works for the front; the rest is guessed.* Say that
in whatever you publish.

**Matte against the background you actually have.** The humanoid was dark grey on dark grey. A plain threshold filled the gap between the
legs and merged the floor shadow into the feet. What worked on the third attempt: fit a smooth polynomial to the backdrop (it was a
vignette, not a flat colour), threshold the *difference*, and rebuild the lower body separately so the leg gap stays open and the cast
shadow is dropped.

**A per-part check is not a whole-model check.** Every part was a valid solid; the fused model was not (an inside-out loft and two floating
part groups). Check the thing you will use.

**Stills hide rig bugs.** Both rigs looked right in every still render and had defects only a clip showed:

- On the revolve, the side of the cup was **one long quad strip**, so the `spine` and `chest` joints sat in the middle of it with no
  vertex near them. Those joints owned nothing, so every spine and chest rotation in the clips did nothing to the cup; the squash that was
  visible came from a blend between two other joints. Found by dumping the skin weights after a motion check reported tearing. Fix: add a vertex ring at least every 3 mm.
- On the humanoid, **both hand joints owned zero vertices** on the first run. The build now fails on that.
- Arm roots blended between chest and shoulder stretched to 2.9× and pinched to 0.2× when an arm was raised. At a 118° raise, 10.6% of the
  glove samples fell inside the body wall; 104° cleared it.

**A validator checks the file is well formed, not that it works.** The Khronos glTF validator reported 58,293 warnings on the first
revolve (unused joint slots holding non-zero indices) and 1,101 zero-area triangles at the revolve poles, both fixed. After that it
reported 0 errors and 0 warnings on a rig that, earlier, had joints doing nothing. **Validity and function are different claims.**

**Cross-check with a second tool, and distrust your own test first.** Blender 5.2 imported the file (14 bones, 14 vertex groups, 7 actions),
and its skinning matched an independent numpy evaluation within 0.004 mm. The first comparison disagreed by up to 7 mm, and the bug was in
the *test*: Blender's importer leaves every action as an NLA strip and does not reset pose bones between actions. Clearing both made it agree.

**A flaky test and a real bug look the same at first.** A viewer test harness had two bugs of its own (a speed measurement that wrapped
around a short clip, an invalid DevTools parameter). Trace before blaming the product.

## The check that fits in this repo

[`tools/check_rig.py`](../../tools/check_rig.py) reads a `.glb` (standard library + numpy) and fails on joints that deform nothing. The
example [`examples/skinned-tube/`](../../examples/skinned-tube/make_skinned_tube.py) writes a tiny rigged tube, and with `RIG_BREAK=1`
writes the same tube with two rings only: the long-quad-strip bug, in one short script.

```sh
pip install numpy
python3 examples/skinned-tube/make_skinned_tube.py /tmp/tube-good.glb
RIG_BREAK=1 python3 examples/skinned-tube/make_skinned_tube.py /tmp/tube-bad.glb
```

Both files pass the Khronos validator with **0 errors and 0 warnings** (checked, 2026-10-04). Now the rig check:

```sh
python3 tools/check_rig.py /tmp/tube-good.glb      # exit 0
python3 tools/check_rig.py /tmp/tube-bad.glb       # exit 1
```

```
skin 0: 3 joints, 252 vertices
  hips              120 vertices   total weight    66.00
  spine             228 vertices   total weight   120.00
  head              120 vertices   total weight    66.00
0 failure(s), 0 warning(s)
```
```
skin 0: 3 joints, 24 vertices
  hips               12 vertices   total weight    12.00
  spine               0 vertices   total weight     0.00
  head               12 vertices   total weight    12.00
  FAIL  joint 'spine' is animated, has no vertices of its own, and sits between weighted joints: nothing blends across it
1 failure(s), 0 warning(s)
```

**What the check does and does not claim.** A joint with no vertices still moves its *children*, so the broken tube's `Bend` clip is not a
no-op: by construction it swings the top ring rigidly and stretches one quad, with nothing bending in between. The first version of this checker said "its clips do nothing", which was
wrong, and it also failed the two real models' perfectly normal root joints. It now follows the hierarchy: a joint with no vertices and
no weighted descendants **fails**; an animated joint with no vertices *between* weighted joints **fails**; a root or pivot above the
weighted joints is just an `INFO` line. It also fails any vertex whose weights do not sum to 1, and warns on a joint that owns fewer than 3
vertices and on zero-weight slots that name a joint other than 0.

It passes both private models, with only the root `INFO` line. It was **not** run against the revolve's original, pre-fix file, which no
longer exists; the tube is a reconstruction of that bug's shape, not a replay of it.

## What is not in this repo

The motion QA that evaluates every clip as a player would (loop seams, one-frame snaps, mesh stretch, ground contact, clipping), the
Blender comparison, the browser viewer and its 50 headless-Chrome checks live in the private experiment repos. They found most of the
bugs above. If you build this workflow, build them: the influence check here is the cheapest of the set, not the most important.

## Check

- [ ] The good tube passes `check_rig.py` (exit 0) and the broken tube fails it (exit 1), and both pass the Khronos validator.
- [ ] You can explain why a clean validator run does not tell you the rig works.
- [ ] You can say, for a model you built from one image, which parts of it are measured and which are invented.
