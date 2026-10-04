# Part 5: Look at the part, and check your checker

*Part 5 of 12 · about 10 minutes · in this part: render an STL with no CAD GUI, and see why the renderer needs a test too.*

Numbers can't tell you a part looks wrong, so we want to *see* it, even on a machine with no display. [`tools/render_stl_iso.py`](../../tools/render_stl_iso.py) is about 130 lines of numpy and Pillow: it parses a binary STL, recomputes normals, applies an isometric rotation, shades against a fixed light, and rasterizes with a z-buffer.

```sh
pip install numpy pillow
python3 tools/render_stl_iso.py examples/mount-plate/mount-plate.stl /tmp/plate.png
```

![The mounting plate rendered from its STL: four clearance holes and a raised centre boss with an insert bore](../img/mount-plate-iso.png)

That is the correct picture. The first one we rendered was not.

## The upside-down plate

The renderer we started from tipped the model the wrong way about the X axis, so +Z pointed down the screen. The raised boss drew as a recess. It looked plausible, and we only caught it because we knew what the boss should look like.

The classic isometric view spins the model 45° about Z, then tips it **toward** the camera by `90 − 35.264 = 54.736°` about X. Use `+35.264°` and it tips the other way. The whole bug was one sign.

Three rules came out of it:

1. **Test your checker on a part whose answer you know.** Render a plate with a boss once and confirm the boss reads as raised.
2. **Use a z-buffer.** A painter's-algorithm depth sort leaves black artifacts where coplanar triangles meet, such as a boss on a plate.
3. **One view is not verification.** An isometric flatters detail and hides profile. For a part defined by an angle or a taper, render the view that feature lives in.

(We also asked small local language models to find this bug, with the symptom: four models, three tries each, and all twelve answers blamed the one correct line. Don't treat a confident code review of geometry as a substitute for rendering a known part.)

## Check

- [ ] Your render shows four holes and a boss that reads as **raised**.
- [ ] Before you trust a new preview tool on a real part, you render one you already know.

---

**Next: [Part 6: Teach Claude the house rules](06-teach-claude-the-house-rules.md)**

[← Part 4: Make it fail on purpose](04-make-it-fail-on-purpose.md) · [Series index](README.md)
