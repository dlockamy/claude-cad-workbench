"""Minimal isometric flat-shaded STL preview (numpy + Pillow only).

For a display-less box, or a CI job, where you want to *look* at a part without
a CAD GUI, an X server, or a real renderer. Reads a BINARY STL, recomputes face
normals from the geometry (the stored ones are not trusted), applies a classic
isometric rotation, flat-shades against a fixed light, and rasterizes with a
real per-pixel z-buffer.

A z-buffer, not a painter's-algorithm depth sort: the sort leaves black
artifacts wherever coplanar triangles (a boss meeting a plate) order
ambiguously.

    python3 render_stl_iso.py part.stl preview.png

One view is a smoke test, not verification -- an isometric flatters detail and
hides profile. For a part whose defining feature is an angle or a taper, render
the orthographic view that feature lives in as well.
"""
import sys
import struct
import numpy as np
from PIL import Image, ImageDraw


def load_binary_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        (n,) = struct.unpack("<I", f.read(4))
        normals = np.empty((n, 3), dtype=np.float32)
        verts = np.empty((n, 3, 3), dtype=np.float32)
        for i in range(n):
            data = f.read(50)
            vals = struct.unpack("<12fH", data)
            normals[i] = vals[0:3]
            verts[i, 0] = vals[3:6]
            verts[i, 1] = vals[6:9]
            verts[i, 2] = vals[9:12]
    return verts, normals


def render(stl_path, out_path, size=1400, bg=(18, 18, 20), color=(190, 195, 205)):
    verts, normals = load_binary_stl(stl_path)

    # recompute normals from geometry (don't trust the file's stored ones)
    e1 = verts[:, 1] - verts[:, 0]
    e2 = verts[:, 2] - verts[:, 0]
    n = np.cross(e1, e2)
    norm = np.linalg.norm(n, axis=1, keepdims=True)
    norm[norm == 0] = 1
    n = n / norm

    # Classic isometric, Z up: spin 45 degrees about Z, then tip the model
    # TOWARD the camera by 90 - 35.264 = 54.736 degrees about X. The sign matters:
    # tipping the other way renders the part upside down on screen (+Z pointing
    # down), so a raised boss reads as a recess. Always check a known part.
    a = np.radians(45.0)
    b = -np.radians(90.0 - 35.264)
    Rz = np.array([[np.cos(a), -np.sin(a), 0],
                   [np.sin(a),  np.cos(a), 0],
                   [0, 0, 1]])
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(b), -np.sin(b)],
                   [0, np.sin(b),  np.cos(b)]])
    R = Rx @ Rz

    flat = verts.reshape(-1, 3) @ R.T
    proj = flat.reshape(-1, 3, 3)
    n_cam = n @ R.T

    # light from upper-left, toward the camera, fixed
    light = np.array([-0.45, 0.55, 0.70])
    light = light / np.linalg.norm(light)
    shade = np.clip(n_cam @ light, 0.12, 1.0)

    xy = proj[:, :, :2]
    minxy = xy.reshape(-1, 2).min(axis=0)
    maxxy = xy.reshape(-1, 2).max(axis=0)
    span = (maxxy - minxy).max()
    scale = size * 0.84 / span
    offset = (size / 2.0) - scale * (minxy + maxxy) / 2.0

    px = xy * scale + offset
    px[:, :, 1] = size - px[:, :, 1]  # flip Y for image coords
    depth = proj[:, :, 2]  # per-vertex depth, for barycentric interpolation

    zbuf = np.full((size, size), -1e9, dtype=np.float32)
    cbuf = np.zeros((size, size, 3), dtype=np.uint8)
    cbuf[:] = bg

    for i in range(len(px)):
        tri = px[i]
        x0 = max(int(np.floor(tri[:, 0].min())), 0)
        x1 = min(int(np.ceil(tri[:, 0].max())) + 1, size)
        y0 = max(int(np.floor(tri[:, 1].min())), 0)
        y1 = min(int(np.ceil(tri[:, 1].max())) + 1, size)
        if x1 <= x0 or y1 <= y0:
            continue

        xs, ys = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1))
        x, y = xs.astype(np.float32) + 0.5, ys.astype(np.float32) + 0.5

        (x1v, y1v), (x2v, y2v), (x3v, y3v) = tri
        denom = (y2v - y3v) * (x1v - x3v) + (x3v - x2v) * (y1v - y3v)
        if abs(denom) < 1e-9:
            continue
        w1 = ((y2v - y3v) * (x - x3v) + (x3v - x2v) * (y - y3v)) / denom
        w2 = ((y3v - y1v) * (x - x3v) + (x1v - x3v) * (y - y3v)) / denom
        w3 = 1 - w1 - w2
        inside = (w1 >= -1e-4) & (w2 >= -1e-4) & (w3 >= -1e-4)
        if not inside.any():
            continue

        z = w1 * depth[i, 0] + w2 * depth[i, 1] + w3 * depth[i, 2]
        sub_z = zbuf[y0:y1, x0:x1]
        closer = inside & (z > sub_z)
        if not closer.any():
            continue
        sub_z[closer] = z[closer]
        s = shade[i]
        col = np.array([c * s for c in color], dtype=np.uint8)
        sub_c = cbuf[y0:y1, x0:x1]
        sub_c[closer] = col

    Image.fromarray(cbuf, "RGB").save(out_path)
    print("wrote", out_path, "triangles:", len(verts))


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
