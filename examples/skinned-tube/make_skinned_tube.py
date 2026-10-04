#!/usr/bin/env python3
"""Write a tiny rigged GLB (a tube, three joints, one 'Bend' clip) with only numpy and the standard library.

    python3 make_skinned_tube.py out.glb              # dense mesh: every joint moves something
    RIG_BREAK=1 python3 make_skinned_tube.py out.glb  # two rings only: the middle joint owns no vertices

The broken file looks identical at rest and is a perfectly valid glTF. The middle joint is animated, owns no vertices, and so nothing
blends across it: the clip kinks the tube instead of bending it. That is the failure ../../tools/check_rig.py exists to catch. Part 12 of the tutorial walks through it.
"""
import json, math, os, struct, sys
import numpy as np

H, RADIUS, SEGMENTS = 60.0, 5.0, 12
JOINT_Y = [0.0, H / 2, H]                                   # joint heights in the rest pose
RINGS = 2 if os.environ.get("RIG_BREAK") else 21            # 2 rings = one long quad strip, the bug
out = next((a for a in sys.argv[1:] if not a.startswith("-")), "skinned-tube.glb")

# --- mesh: RINGS rings of SEGMENTS vertices, quads between consecutive rings
ys = np.linspace(0.0, H, RINGS)
pos, nrm, jnt, wgt = [], [], [], []
for y in ys:
    if y <= JOINT_Y[1]:  a, b, t = 0, 1, (y - JOINT_Y[0]) / (JOINT_Y[1] - JOINT_Y[0])   # blend joint 0 -> 1
    else:                a, b, t = 1, 2, (y - JOINT_Y[1]) / (JOINT_Y[2] - JOINT_Y[1])   # blend joint 1 -> 2
    for s in range(SEGMENTS):
        th = 2 * math.pi * s / SEGMENTS
        pos.append([RADIUS * math.cos(th), y, RADIUS * math.sin(th)]); nrm.append([math.cos(th), 0.0, math.sin(th)])
        w = [1.0 - t, t, 0.0, 0.0]; j = [a, b, 0, 0]
        j = [ji if wi > 0 else 0 for ji, wi in zip(j, w)]               # a slot with weight 0 must name joint 0, or the validator warns
        jnt.append(j); wgt.append(w)
idx = []
for r in range(RINGS - 1):
    for s in range(SEGMENTS):
        i0, i1 = r * SEGMENTS + s, r * SEGMENTS + (s + 1) % SEGMENTS
        j0, j1 = i0 + SEGMENTS, i1 + SEGMENTS
        idx += [i0, j0, i1, i1, j0, j1]
pos, nrm, wgt = (np.array(v, "<f4") for v in (pos, nrm, wgt)); jnt = np.array(jnt, "<u2"); idx = np.array(idx, "<u2")
ibm = np.array([[1,0,0,0, 0,1,0,0, 0,0,1,0, 0,-y,0,1] for y in JOINT_Y], "<f4")      # inverse bind matrices, column-major
times = np.array([0.0, 1.0, 2.0], "<f4")
half = math.radians(40) / 2                                                           # +/-40 degrees about Z, middle joint
quats = np.array([[0, 0, 0, 1], [0, 0, math.sin(half), math.cos(half)], [0, 0, 0, 1]], "<f4")

# --- pack into one buffer
blob, views, accs = bytearray(), [], []
def add(arr, comp, typ, target=None, mm=False):
    while len(blob) % 4: blob.append(0)
    views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": arr.nbytes, **({"target": target} if target else {})})
    blob.extend(arr.tobytes())
    acc = {"bufferView": len(views) - 1, "componentType": comp, "count": len(arr), "type": typ}
    if mm: acc["min"], acc["max"] = arr.min(0).tolist(), arr.max(0).tolist()
    accs.append(acc); return len(accs) - 1
FLOAT, USHORT = 5126, 5123
A = {"POSITION": add(pos, FLOAT, "VEC3", 34962, True), "NORMAL": add(nrm, FLOAT, "VEC3", 34962),
     "JOINTS_0": add(jnt, USHORT, "VEC4", 34962), "WEIGHTS_0": add(wgt, FLOAT, "VEC4", 34962)}
ai = add(idx, USHORT, "SCALAR", 34963); aibm = add(ibm.reshape(-1, 16), FLOAT, "MAT4")
at = add(times, FLOAT, "SCALAR", None, True); aq = add(quats, FLOAT, "VEC4")
for a in (accs[at],): a["min"], a["max"] = [float(times.min())], [float(times.max())]

nodes = [{"name": "Armature", "children": [1]},
         {"name": "hips", "children": [2]}, {"name": "spine", "translation": [0, H / 2, 0], "children": [3]},
         {"name": "head", "translation": [0, H / 2, 0]},
         {"name": "tube", "mesh": 0, "skin": 0}]
gltf = {"asset": {"version": "2.0", "generator": "make_skinned_tube.py"}, "scene": 0, "scenes": [{"nodes": [0, 4]}], "nodes": nodes,
        "meshes": [{"name": "tube", "primitives": [{"attributes": A, "indices": ai, "mode": 4}]}],
        "skins": [{"inverseBindMatrices": aibm, "joints": [1, 2, 3], "skeleton": 0}],
        "animations": [{"name": "Bend", "samplers": [{"input": at, "output": aq, "interpolation": "LINEAR"}],
                        "channels": [{"sampler": 0, "target": {"node": 2, "path": "rotation"}}]}],
        "buffers": [{"byteLength": len(blob)}], "bufferViews": views, "accessors": accs}
js = json.dumps(gltf, separators=(",", ":")).encode()
js += b" " * (-len(js) % 4); blob.extend(b"\0" * (-len(blob) % 4))
glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
open(out, "wb").write(glb)
print(f"wrote {out}: {RINGS} rings, {len(pos)} vertices, 3 joints, 1 clip ({len(glb)} bytes)", flush=True)
