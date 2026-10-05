# Part 12: Check the rig

*Part 12 of 12 · about 20 minutes · in this part: see why stills hide rig bugs, and run a small check that catches them.*

We have a skinned, rigged model. It looks right from every angle, and that is exactly the problem: both of ours had defects that only a *clip* showed.

## What stills hid

- **Joints that owned nothing.** On the revolve, the `spine` and `chest` joints sat in the middle of one long quad strip with no vertex near them, so every spine and chest rotation did nothing to the cup. Found by dumping the skin weights after a motion check reported tearing. Fix: a vertex ring at least every 3 mm. On the humanoid, both hand joints owned zero vertices on the first run.
- **Tearing and clipping.** Arm roots stretched to 2.9× and pinched to 0.2× when raised. At a 118° raise, 10.6% of the glove samples fell inside the body wall; 104° cleared it.
- **Validator noise, then a validator that says nothing.** The Khronos glTF validator first reported 58,293 warnings on the revolve (unused joint slots with non-zero indices) and 1,101 zero-area triangles; both were fixed. The warnings are real and worth fixing, but they are about file hygiene. **A validator does not know whether a joint does anything**: the deliberately broken tube below, with an inert joint, also passes it with 0 errors and 0 warnings. Valid and working are different claims.
- **A second tool disagreed, and the bug was the test.** Blender 5.2 matched an independent numpy evaluation within 0.004 mm, but the first comparison was off by 7 mm: Blender's importer leaves every action as an NLA strip and doesn't reset pose bones between actions.

## The check we can ship

[`tools/check_rig.py`](../../tools/check_rig.py) reads a `.glb` (standard library and numpy) and fails on joints that deform nothing. [`examples/skinned-tube/`](../../examples/skinned-tube/make_skinned_tube.py) writes a three-joint tube, and `RIG_BREAK=1` writes it with two rings only: the long-quad-strip bug in one short script.

```sh
pip install numpy
python3 examples/skinned-tube/make_skinned_tube.py /tmp/tube-good.glb
RIG_BREAK=1 python3 examples/skinned-tube/make_skinned_tube.py /tmp/tube-bad.glb
python3 tools/check_rig.py /tmp/tube-good.glb     # exit 0
python3 tools/check_rig.py /tmp/tube-bad.glb      # exit 1
```

Both files pass the Khronos validator with **0 errors and 0 warnings**. The checker passes the first and fails the second:

```
  hips               12 vertices   total weight    12.00
  spine               0 vertices   total weight     0.00
  head               12 vertices   total weight    12.00
  FAIL  joint 'spine' is animated, has no vertices of its own, and sits between weighted joints: nothing blends across it
```

## What the check claims, exactly

A joint with no vertices still moves its *children*, so the broken tube isn't a no-op: by construction it swings the top ring rigidly and stretches one quad, with nothing bending in between. Our first draft said "its clips do nothing" and also failed both real models' ordinary root joints. It now follows the hierarchy. It **fails** a joint with no vertices and no weighted descendants, and an animated one with no vertices *between* weighted joints; a root above the weighted joints gets an `INFO` line. It also fails any vertex whose weights don't sum to 1, and warns on a joint owning fewer than 3 vertices.

It passes both private models with only the root `INFO` line. We did **not** run it on the revolve's original pre-fix file, which no longer exists, so the tube is a reconstruction of that bug, not a replay.

## What isn't in this repo

The motion QA that evaluates each clip as a player would (loop seams, one-frame snaps, stretch, ground contact, clipping), the Blender comparison, and the browser viewer with its headless-Chrome tests live in the private experiments. They found most of the bugs above. If you build this workflow, build them: the influence check is the cheapest of the set, not the most important.

## Check

- [ ] The good tube exits 0 and the broken tube exits 1, and both pass the validator.
- [ ] You can explain why a clean validator run doesn't mean the rig works.

That is the end of the series. The [README](../../README.md) lists everything in the repo, and issues are welcome if something doesn't reproduce.

---

**You have reached the end of the series.**

[← Part 11: From a drawing to a model](11-from-a-drawing-to-a-model.md) · [Series index](README.md)
