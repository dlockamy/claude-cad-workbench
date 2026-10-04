#!/usr/bin/env python3
"""Fail if a rigged glTF/GLB has joints that do nothing. Standard library + numpy only.

    python3 tools/check_rig.py model.glb         # exit 0 = clean, 1 = a hard failure, 2 = unreadable

What it checks, per skin (a joint with no vertices of its own still moves its children, so the check follows the hierarchy):
  FAIL  a joint with no vertices and no weighted descendants: nothing it does can move anything
  FAIL  an animated joint with no vertices that sits *between* weighted joints (a weighted ancestor and a weighted descendant): its
        clips swing the joints below it rigidly, and nothing blends across it, so a bend is a kink or a stretched quad
  FAIL  a vertex whose weights do not sum to 1 (within 0.01)
  INFO  a joint with no vertices and no weighted ancestor (a normal root or pivot joint)
  WARN  a weight-0 slot that names a joint other than 0 (the Khronos validator warns about this one too)
  WARN  a joint influencing fewer than 3 vertices (a handful of vertices is rarely the intent)

Why this exists: the Khronos validator checks that the file is *well formed*. A joint with no vertices is well formed. It looks right in
every still render and passes validation; only a clip shows it.
"""
import json, struct, sys
import numpy as np

CT = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

def load(path):
    raw = open(path, "rb").read()
    if raw[:4] != b"glTF": return json.loads(raw), b""
    off, js, binc = 12, None, b""
    while off < len(raw):
        n, t = struct.unpack_from("<II", raw, off); body = raw[off + 8: off + 8 + n]; off += 8 + n
        if t == 0x4E4F534A: js = json.loads(body)
        elif t == 0x004E4942: binc = body
    return js, binc

def read(g, binc, i):
    a = g["accessors"][i]; v = g["bufferViews"][a["bufferView"]]; k = NC[a["type"]]; fmt = CT[a["componentType"]]
    size = struct.calcsize(fmt); stride = v.get("byteStride") or size * k; base = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = np.empty((a["count"], k), dtype=np.float64)
    for r in range(a["count"]): out[r] = struct.unpack_from("<" + fmt * k, binc, base + r * stride)
    if a.get("normalized"): out /= {"B": 255.0, "H": 65535.0}.get(fmt, 1.0)
    return out

def main(path):
    try: g, binc = load(path)
    except Exception as e: print(f"cannot read {path}: {e}", flush=True); return 2
    fails, warns = [], []
    for si, skin in enumerate(g.get("skins", [])):
        joints = skin["joints"]; names = [g["nodes"][j].get("name", f"node{j}") for j in joints]
        users = [(mi, p) for n in g["nodes"] if n.get("skin") == si for mi, p in [(n["mesh"], q) for q in g["meshes"][n["mesh"]]["primitives"]]]
        count = np.zeros(len(joints)); mass = np.zeros(len(joints)); bad_sum = bad_slot = nverts = 0
        for _, p in users:
            sets = [s for s in range(8) if f"JOINTS_{s}" in p["attributes"]]
            J = np.hstack([read(g, binc, p["attributes"][f"JOINTS_{s}"]) for s in sets]).astype(int)
            W = np.hstack([read(g, binc, p["attributes"][f"WEIGHTS_{s}"]) for s in sets]); nverts += len(J)
            bad_sum += int((np.abs(W.sum(1) - 1.0) > 0.01).sum()); bad_slot += int(((W == 0) & (J != 0)).sum())
            for slot in range(J.shape[1]):
                live = W[:, slot] > 1e-4
                np.add.at(count, J[live, slot], 1); np.add.at(mass, J[live, slot], W[live, slot])
        print(f"skin {si}: {len(joints)} joints, {nverts} vertices", flush=True)
        for n, c, m in zip(names, count, mass): print(f"  {n:<14s} {int(c):6d} vertices   total weight {m:8.2f}", flush=True)
        animated = {g["nodes"][ch["target"]["node"]].get("name", "") for a in g.get("animations", []) for ch in a["channels"]}
        parent = {c: pi for pi, n in enumerate(g["nodes"]) for c in n.get("children", [])}
        carrying = {j for j, c in zip(joints, count) if c > 0}
        def below(j): return any(c in carrying or below(c) for c in g["nodes"][j].get("children", []))
        def above(j):
            while j in parent:
                j = parent[j]
                if j in carrying: return True
            return False
        for ji, (n, j) in enumerate(zip(names, joints)):
            if count[ji] == 0:
                if not below(j): fails.append(f"joint '{n}' has no vertices and no weighted descendants: it can move nothing")
                elif above(j) and n in animated:
                    fails.append(f"joint '{n}' is animated, has no vertices of its own, and sits between weighted joints: nothing blends across it")
                elif above(j): warns.append(f"joint '{n}' has no vertices and sits between weighted joints (not animated here)")
                else: print(f"  INFO  joint '{n}' has no vertices; it is a pivot above the weighted joints", flush=True)
            elif count[ji] < 3: warns.append(f"joint '{n}' influences only {int(count[ji])} vertices")
        if bad_sum: fails.append(f"{bad_sum} vertices have weights that do not sum to 1")
        if bad_slot: warns.append(f"{bad_slot} zero-weight slots name a joint other than 0")
    if not g.get("skins"): print("no skins in this file", flush=True)
    for w in warns: print("  WARN ", w, flush=True)
    for f in fails: print("  FAIL ", f, flush=True)
    print(f"{len(fails)} failure(s), {len(warns)} warning(s)", flush=True)
    return 1 if fails else 0

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit("usage: check_rig.py model.glb")
    sys.exit(main(sys.argv[1]))
