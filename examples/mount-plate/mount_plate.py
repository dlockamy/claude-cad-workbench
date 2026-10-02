"""A mounting plate that checks itself.

Run headless:

    freecadcmd examples/mount-plate/mount_plate.py

Output goes to ./out/ (override with MOUNT_PLATE_OUT). The script exits 0 only
if every check passes and exits 1 otherwise -- see `check()` for why that is
not automatic under freecadcmd.

Set MOUNT_PLATE_BREAK=1 to move one mounting hole off the plate. The part still
builds, still exports, still has one valid solid -- and the run must FAIL. That
is the proof the checks can fail, which is the only reason to trust them when
they pass.

Everything that matters is a named constant at the top. The expected volume is
computed here from those constants *by hand*, not read back from the shape that
the same constants produced.
"""

import math
import os
import sys

import FreeCAD as App
import Part

# ---------------------------------------------------------------- parameters
PLATE_L = 80.0          # mm, X
PLATE_W = 50.0          # mm, Y
PLATE_T = 6.0           # mm, Z

HOLE_D = 3.4            # M3 clearance
HOLE_INSET = 8.0        # hole centre, from each plate edge

BOSS_D = 20.0           # centre boss, takes a heat-set insert
BOSS_H = 4.0            # height ABOVE the plate
BORE_D = 4.0            # insert bore (PLACEHOLDER: check your insert's datasheet)
BORE_DEPTH = 6.5        # blind, from the top of the boss

OVERLAP = 0.2           # boss sinks into the plate so the fuse is a real fuse

# Process limits. Name them, then assert against them.
BED_X, BED_Y, BED_Z = 250.0, 250.0, 250.0   # a 256 mm printer less a margin
NOZZLE = 0.4
MIN_WALL = 3 * NOZZLE   # three perimeters

TOL_VOL = 1e-4          # relative
TOL_LEN = 1e-6          # mm

OUT = os.environ.get("MOUNT_PLATE_OUT", os.path.join(os.getcwd(), "out"))
BREAK = os.environ.get("MOUNT_PLATE_BREAK") == "1"

failures = []


def check(ok, message):
    """Record a check. Never raise.

    freecadcmd catches an uncaught exception, prints 'Exception while
    processing file', and exits 0 -- so an `assert` here would make a failed
    build look like a green one. sys.exit() *does* propagate, so failures are
    collected and the script exits non-zero at the end.

    Every print is flushed for a related reason: on sys.exit() freecadcmd
    does not flush Python's stdout, so with output redirected (CI, a pipe, a
    file) an unflushed failure report is simply lost -- a red build with no
    explanation.
    """
    print(("  ok    " if ok else "  FAIL  ") + message, flush=True)
    if not ok:
        failures.append(message)


def hole_centres():
    xs = (HOLE_INSET, PLATE_L - HOLE_INSET)
    ys = (HOLE_INSET, PLATE_W - HOLE_INSET)
    centres = [(x, y) for x in xs for y in ys]
    if BREAK:
        # The real-world defect: a centre that lands outside the part. The
        # boolean "succeeds", removes nothing, and every topology check
        # still passes.
        centres[0] = (-HOLE_INSET, -HOLE_INSET)
    return centres


# --------------------------------------------------------------------- build
def build():
    plate = Part.makeBox(PLATE_L, PLATE_W, PLATE_T)

    boss = Part.makeCylinder(
        BOSS_D / 2, BOSS_H + OVERLAP,
        App.Vector(PLATE_L / 2, PLATE_W / 2, PLATE_T - OVERLAP),
    )
    body = plate.fuse(boss)
    check(len(body.Solids) == 1, f"fuse produced one solid (got {len(body.Solids)})")

    removed = []
    for (x, y) in hole_centres():
        tool = Part.makeCylinder(HOLE_D / 2, PLATE_T + 2, App.Vector(x, y, -1))
        before = body.Volume
        body = body.cut(tool)
        removed.append(before - body.Volume)

    top = PLATE_T + BOSS_H
    bore = Part.makeCylinder(
        BORE_D / 2, BORE_DEPTH + 1,
        App.Vector(PLATE_L / 2, PLATE_W / 2, top - BORE_DEPTH),
    )
    before = body.Volume
    body = body.cut(bore)
    bore_removed = before - body.Volume

    return body.removeSplitter(), removed, bore_removed


# -------------------------------------------------------------------- verify
def expected_volume():
    """By hand, from the constants -- not from the shape."""
    v = PLATE_L * PLATE_W * PLATE_T
    v += math.pi * (BOSS_D / 2) ** 2 * BOSS_H
    v -= 4 * math.pi * (HOLE_D / 2) ** 2 * PLATE_T
    v -= math.pi * (BORE_D / 2) ** 2 * BORE_DEPTH
    return v


def verify(shape, label):
    print(f"[{label}]", flush=True)
    check(len(shape.Solids) == 1, f"one solid (got {len(shape.Solids)})")
    check(shape.isValid(), "shape is valid")
    for i, sol in enumerate(shape.Solids):
        check(len(sol.Shells) == 1, f"solid {i}: one shell, no enclosed void (got {len(sol.Shells)})")

    bb = shape.BoundBox
    want = (PLATE_L, PLATE_W, PLATE_T + BOSS_H)
    got = (bb.XLength, bb.YLength, bb.ZLength)
    check(all(abs(g - w) < TOL_LEN for g, w in zip(got, want)),
          "bounding box %.3f x %.3f x %.3f == spec %.3f x %.3f x %.3f" % (*got, *want))
    check(got[0] <= BED_X and got[1] <= BED_Y and got[2] <= BED_Z,
          "fits the build volume with margin")

    ev = expected_volume()
    rel = abs(shape.Volume - ev) / ev
    check(rel < TOL_VOL,
          "volume %.2f mm3 vs hand-computed %.2f mm3 (%.4f%% off)" % (shape.Volume, ev, rel * 100))


def verify_features(shape, removed, bore_removed):
    """Assert the feature exists, not that the operation ran."""
    print("[features]", flush=True)
    per_hole = math.pi * (HOLE_D / 2) ** 2 * PLATE_T
    for i, r in enumerate(removed):
        check(abs(r - per_hole) / per_hole < 1e-3,
              "hole %d removed %.2f mm3 (a real hole removes %.2f)" % (i, r, per_hole))
    per_bore = math.pi * (BORE_D / 2) ** 2 * BORE_DEPTH
    check(abs(bore_removed - per_bore) / per_bore < 1e-3,
          "insert bore removed %.2f mm3 (expected %.2f)" % (bore_removed, per_bore))

    # Material left around each hole: the hole existing is not enough.
    for i, (x, y) in enumerate(hole_centres()):
        edge = min(x, PLATE_L - x, y, PLATE_W - y) - HOLE_D / 2
        check(edge >= MIN_WALL, "hole %d keeps %.2f mm of wall (min %.2f)" % (i, edge, MIN_WALL))

    # Cutting is not the same as having cut: probe the FINISHED part, so a
    # later boolean that fills a bore back in is caught too.
    mid_bore = App.Vector(PLATE_L / 2, PLATE_W / 2, PLATE_T + BOSS_H - BORE_DEPTH / 2)
    check(not shape.isInside(mid_bore, 1e-6, True), "insert bore is still open on the finished part")
    for i, (x, y) in enumerate(hole_centres()):
        probe = App.Vector(x, y, PLATE_T / 2)
        inside_plate = 0 <= x <= PLATE_L and 0 <= y <= PLATE_W
        check(inside_plate and not shape.isInside(probe, 1e-6, True),
              "hole %d centre is on the plate and open" % i)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("mount plate" + ("  [BREAK=1: expecting failures]" if BREAK else ""), flush=True)

    shape, removed, bore_removed = build()
    verify(shape, "built")
    verify_features(shape, removed, bore_removed)

    step = os.path.join(OUT, "mount-plate.step")
    stl = os.path.join(OUT, "mount-plate.stl")
    shape.exportStep(step)

    # Mesh once, explicitly, and write the mesh. A shape-level exportStl may
    # ignore your tolerance and hand back a 40x larger file.
    import MeshPart
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=0.3)
    mesh.write(stl)

    # Round trip: judge the file on disk, not the object that wrote it.
    back = Part.Shape()
    back.read(step)
    verify(back, "re-imported STEP")

    print("wrote", step, flush=True)
    print("wrote", stl, "(%d triangles)" % mesh.CountFacets, flush=True)

    if failures:
        print("\n%d CHECK(S) FAILED" % len(failures), flush=True)
        sys.exit(1)
    print("\nALL CHECKS PASSED", flush=True)


# Deliberately not gated on `if __name__ == "__main__":` -- under freecadcmd
# __name__ is the script's filename, so that guard silently runs nothing.
main()
