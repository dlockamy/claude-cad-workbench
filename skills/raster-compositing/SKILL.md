---
name: raster-compositing
description: Build repeatable, layered raster images with GIMP 3 driven by Claude — product scenes, renders from CAD or SVG output, concept sheets, wallpapers, labelled assets. Use when the image must be regenerated when its source changes, and when layers, masks, text or filters matter. Not for plain resize/convert (use ImageMagick) and not for photoreal synthesis.
---

# Programmatic raster compositing

## When *not* to

- Plain conversion, resize, metadata strip, thumbnailing → **ImageMagick**. A
  layer-capable editor costs seconds of startup per call.
- **Photoreal synthesis.** A raster editor draws; it does not invent. It cannot
  produce a photograph, inpaint, or meaningfully upscale, and a flat-colour
  "remove background" only works on a flat field — on a photograph it destroys
  the image while appearing to succeed. Say so *before* starting, then offer
  what it can do: graphic, stylised, constructed looks (flat colour, gradients,
  grids, neon, chrome) are where it wins.

## Requirement

You must be able to **see the render back** mid-build (`gimp_render`).
Without that you are drawing blind.

## Procedure

1. **Isolate the subject before compositing.** Drawing-office source (concept
   sheets, elevations) carries a page background, dimension rules and callout
   badges. Fix it at the *source*: delete the background rect so alpha is
   genuinely transparent; remove annotation layers as whole groups, identified
   by a shared attribute (a stroke colour, a `r="10"` badge circle) rather than
   by eyeballing coordinates.
2. **Re-frame with a transform, not just a `viewBox`.** Changing an SVG's
   `viewBox` min-x/min-y is silently ignored by librsvg when an explicit render
   size is supplied — you get the whole sheet squeezed into the new aspect
   ratio. Wrap the content:
   `<svg viewBox="0 0 W H"><g transform="translate(-X,-Y)">…</g></svg>`
3. **Every element is its own named layer** — `sky`, `sun`, `grid`, `device`,
   `device-reflection`, `vignette`. Naming is what turns "make the sun smaller"
   into a ten-second change and makes the layered master useful afterwards.
4. **Construct, don't hand-place.** Gradients carry the mood (two or three stops
   beat any texture). A perspective grid is a vanishing point plus tapering
   polygons, with transverse lines spaced on a power curve so they compress
   toward the horizon. A reflection is all four of: duplicate, flip, squash to
   ~40%, drop opacity to ~25%, then a gradient layer mask to fade it out. Any
   three of them looks wrong.
5. **Bloom goes *behind* the emitting object, never over it.** Bloom on top
   washes out the very detail it sells. The most common self-inflicted error.
6. **Render and look after every meaningful step**, then inspect at 1:1 with a
   region render. A downscaled preview hides aliasing, moiré and clipped edges.
   Check nothing important is clipped and no glow has eaten a subject.
7. **Regenerate at native resolution; never upscale.** A procedural scene has no
   fixed size. Ask the target first. Scale texture-frequency effects with the
   canvas — scanlines every 4 px at 1080p must be every 8 px at 4K to read the
   same.
8. **Export both** a flat deliverable and the layered `.xcf` master, and say
   which layers are adjustable.

## Gotchas

- **Source SVGs routinely overflow their own `viewBox`.** Unwrapped `<text>` is
  clipped by *every* correct renderer — browser, Obsidian, GIMP. A defect in the
  asset, not the rasteriser. Wrap in `<tspan>` or widen the canvas; audit a
  generated set for it.
- **Foreground props clipped by the frame read as an accident**, not a crop.
- **Scale factor for placed layers:**
  `scene_x = layer_x + (src_x − src_origin) × (placed_w / src_w)`.
- **Not every GEGL op is a filter.** Source ops such as `gegl:linear-gradient`
  can't be applied to a drawable ("the filter is hidden"); use the native
  gradient-fill procedure.
- **Check the procedure exists on the installed version.** Names drift between
  GIMP majors; look it up (`gimp_pdb_search`) instead of trusting recall.
- **GIMP 3's Python API is a real break from 2.10**: no `pdb` object (flat
  `Gimp.*` functions), colours are `Gegl.Color` not tuples, fonts and gradients
  must be resolved with `Gimp.Font.get_by_name()` / `Gimp.Gradient.get_by_name()`
  (a bare string raises `TypeError`), Gaussian blur is a GEGL filter, and the
  classic Script-Fu logo scripts are gone. GIMP 2.10's Python-Fu is dead on
  current distros.
- **The layered master is large** (a 16-layer 4K scene ≈ 5 MB). Keep it out of
  git unless it is a deliverable.
- `gimp-agent-mcp` ships its own recipes (sprite sheets, stickers, web export)
  and skills — run `uvx gimp-agent-mcp install-skills`. Use them; don't rebuild.

See also: `drive-desktop-app` (install and verify the bridge).
