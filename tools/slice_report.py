#!/usr/bin/env python3
"""Summarise a sliced G-code file (Bambu Studio / OrcaSlicer style comments) and flag what a clean slice does not tell you.

    python3 tools/slice_report.py plate_1.gcode

A slicer reports "Success" for a model that will not print. This prints the numbers worth reading before you commit hours of plastic:
estimated time, layers, filament, how many layers each feature appears in, and the length of the *first layer*. A model whose first
layer is a few centimetres of line is standing on a dot (a rounded tip, a point), and will not stay on the bed.

The first-layer threshold below is a heuristic, not a rule: tune it for your printer and your parts.
"""
import math, re, sys

FIRST_LAYER_MIN_MM = 100.0       # heuristic: less extruded path than this on layer 1 is a very small footprint

def main(path):
    t = open(path, errors="ignore").read()
    def find(rx):
        m = re.search(rx, t); return m.group(1).strip() if m else "?"
    print(f"file:            {path}")
    print(f"estimated time:  {find(r'total estimated time: ([^\n]*)')}")
    print(f"layers:          {find(r'total layer number: (\d+)')}   max z {find(r'max_z_height: ([\d.]+)')} mm")
    print(f"filament:        {find(r'total filament length \[mm\] : ([\d.]+)')} mm")
    feats = {}
    for name in re.findall(r"^; FEATURE: (.+)$", t, flags=re.M): feats[name] = feats.get(name, 0) + 1
    print("features (extrusion blocks): " + ", ".join(f"{k} {v}" for k, v in sorted(feats.items())))
    layers = t.split("; CHANGE_LAYER")
    first = layers[1] if len(layers) > 1 else ""
    x = y = None; length = 0.0
    for line in first.splitlines():
        m = re.match(r"G1 X([-\d.]+) Y([-\d.]+) E", line)
        if m:
            nx, ny = float(m.group(1)), float(m.group(2))
            if x is not None: length += math.hypot(nx - x, ny - y)
            x, y = nx, ny
        else:
            m = re.match(r"G[01] X([-\d.]+) Y([-\d.]+)", line)
            if m: x, y = float(m.group(1)), float(m.group(2))
    print(f"first layer:     {length:.0f} mm of extruded path")
    warn = []
    if length < FIRST_LAYER_MIN_MM: warn.append(f"first layer is only {length:.0f} mm of path: the part stands on a very small footprint and may not stay on the bed")
    if "Bottom surface" not in feats: warn.append("no 'Bottom surface' anywhere: nothing in the model has a flat face on the bed")
    for w in warn: print("  WARN ", w)
    if feats.get("Floating vertical shell"):
        print(f"  INFO  the slicer reports 'Floating vertical shell' in {feats['Floating vertical shell']} blocks; read it as a prompt to look, "
              "not a defect (a plain test plate shows some too)")
    print(f"{len(warn)} warning(s)")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit("usage: slice_report.py file.gcode")
    sys.exit(main(sys.argv[1]))
