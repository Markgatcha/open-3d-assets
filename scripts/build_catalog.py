"""Validate every asset under assets/ and write catalog.json for the gallery.

Usage:
    python scripts/build_catalog.py           # validate and write catalog.json
    python scripts/build_catalog.py --check   # validate and fail if catalog.json is stale

Standard library only, so it runs the same locally and in GitHub Actions.
"""
from __future__ import annotations

import argparse
import gzip
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CATALOG = ROOT / "catalog.json"

CATEGORIES = {"characters", "creatures", "items", "props", "environment", "vehicles"}

# tier -> (allowed model extensions, max triangles, max texture edge in px)
TIERS = {
    "roblox": ({".glb"}, 20_000, 1024),
    "game": ({".glb"}, 100_000, 2048),
    "hero": ({".glb"}, None, 4096),
    "splat": ({".spz"}, None, None),
}

# Approved generators and their licenses. Keep in sync with ASSET_POLICY.md.
APPROVED = {
    "Z-Image-Turbo": "Apache-2.0",
    "Qwen-Image": "Apache-2.0",
    "FLUX.2-klein-4B": "Apache-2.0",
    "BiRefNet": "MIT",
    "Idol": "Apache-2.0",
    "TripoSplat": "MIT",
    "TRELLIS.2": "MIT",
    "Pixal3D": "MIT",
    "MoGe-2": "MIT",
}

MAX_FILE_BYTES = 50 * 1024 * 1024  # GitHub hard limit is 100 MB; stay well under it


class AssetError(Exception):
    pass


# ---------------------------------------------------------------- file probes

def glb_stats(path: Path) -> dict:
    """Triangle count and largest embedded texture edge of a binary glTF."""
    data = path.read_bytes()
    magic, version, _length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2:
        raise AssetError(f"{path.name} is not a glTF 2.0 binary (.glb)")
    off, gltf, binchunk = 12, None, b""
    while off < len(data):
        clen, ctype = struct.unpack_from("<I4s", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == b"JSON":
            gltf = json.loads(chunk)
        elif ctype == b"BIN\x00":
            binchunk = chunk
        off += 8 + clen
    if gltf is None:
        raise AssetError(f"{path.name} has no JSON chunk")

    accessors = gltf.get("accessors", [])
    tris = 0
    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if prim.get("mode", 4) != 4:  # only TRIANGLES count toward budgets
                continue
            if "indices" in prim:
                tris += accessors[prim["indices"]]["count"] // 3
            else:
                tris += accessors[prim["attributes"]["POSITION"]]["count"] // 3

    max_edge = 0
    views = gltf.get("bufferViews", [])
    for img in gltf.get("images", []):
        if "bufferView" not in img:
            continue  # external image; not used by this repo's assets
        v = views[img["bufferView"]]
        start = v.get("byteOffset", 0)
        w, h = image_size(binchunk[start: start + v["byteLength"]])
        max_edge = max(max_edge, w, h)
    return {"triangles": tris, "max_texture": max_edge}


def image_size(b: bytes) -> tuple[int, int]:
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:2] == b"\xff\xd8":  # JPEG: walk segments to the first SOF marker
        i = 2
        while i < len(b):
            marker, seglen = b[i + 1], struct.unpack(">H", b[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return w, h
            i += 2 + seglen
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP" and b[12:16] == b"VP8 ":
        w, h = struct.unpack("<HH", b[26:30])
        return w & 0x3FFF, h & 0x3FFF
    return 0, 0  # unknown format: reported as 0, not a failure


def spz_stats(path: Path) -> dict:
    """Gaussian count from an .spz header (gzip-wrapped, magic 'NGSP')."""
    with gzip.open(path, "rb") as f:
        head = f.read(16)
    magic, version, points = struct.unpack_from("<III", head, 0)
    if magic != 0x5053474E:
        raise AssetError(f"{path.name} is not an .spz splat")
    return {"splat_points": points, "spz_version": version}


# ---------------------------------------------------------------- validation

def need(cond: bool, msg: str) -> None:
    if not cond:
        raise AssetError(msg)


def check_asset(folder: Path) -> dict:
    meta_path = folder / "asset.json"
    need(meta_path.exists(), "missing asset.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    need(meta.get("id") == folder.name, f"id must equal the folder name '{folder.name}'")
    need(bool(meta.get("name")), "name is required")
    need(meta.get("category") in CATEGORIES, f"category must be one of {sorted(CATEGORIES)}")
    need(meta.get("category") == folder.parent.name, "asset must live under assets/<category>/")
    need(meta.get("tier") in TIERS, f"tier must be one of {sorted(TIERS)}")
    need(meta.get("license") == "MIT", "license must be MIT")

    src = meta.get("source_image") or {}
    origin = src.get("origin")
    need(origin in {"generated", "own-photo"}, "source_image.origin must be 'generated' or 'own-photo'")
    if origin == "generated":
        need(src.get("generator") in APPROVED, f"source_image.generator must be one of {sorted(APPROVED)}")
        need(bool(src.get("prompt")), "source_image.prompt is required for generated images")
        need(isinstance(src.get("seed"), int), "source_image.seed must be an integer")
    else:
        need(src.get("contains_people") is False, "own photos must set contains_people: false")
        need(src.get("contains_logos") is False, "own photos must set contains_logos: false")

    pipeline = meta.get("pipeline") or []
    need(len(pipeline) > 0, "pipeline must list at least one step")
    for step in pipeline:
        need(step.get("model") in APPROVED, f"pipeline model '{step.get('model')}' is not approved")

    files = meta.get("files") or {}
    model = folder / files.get("model", "")
    need(model.is_file(), f"files.model '{files.get('model')}' not found")
    exts, max_tris, max_tex = TIERS[meta["tier"]]
    need(model.suffix.lower() in exts, f"tier '{meta['tier']}' needs a {'/'.join(sorted(exts))} model")
    size = model.stat().st_size
    need(size <= MAX_FILE_BYTES, f"{model.name} is {size / 2**20:.1f} MB; keep models under 50 MB")

    stats = glb_stats(model) if model.suffix.lower() == ".glb" else spz_stats(model)
    if max_tris is not None:
        need(stats["triangles"] <= max_tris,
             f"{stats['triangles']:,} triangles exceeds the {meta['tier']} budget of {max_tris:,}")
    if max_tex is not None:
        need(stats["max_texture"] <= max_tex,
             f"{stats['max_texture']}px texture exceeds the {meta['tier']} limit of {max_tex}px")

    preview = files.get("preview")
    if preview:
        need((folder / preview).is_file(), f"files.preview '{preview}' not found")

    rel = folder.relative_to(ROOT).as_posix()
    return {
        "id": meta["id"],
        "name": meta["name"],
        "category": meta["category"],
        "tier": meta["tier"],
        "description": meta.get("description", ""),
        "tags": meta.get("tags", []),
        "format": model.suffix.lower().lstrip("."),
        "model": f"{rel}/{model.name}",
        "preview": f"{rel}/{preview}" if preview else None,
        "bytes": size,
        **stats,
        "generators": sorted({s["model"] for s in pipeline} | ({src["generator"]} if origin == "generated" else set())),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if catalog.json is out of date")
    args = ap.parse_args()

    entries, errors = [], []
    folders = sorted(p.parent for p in ASSETS.glob("*/*/asset.json")) if ASSETS.exists() else []
    for folder in folders:
        try:
            entries.append(check_asset(folder))
        except (AssetError, OSError, ValueError, KeyError, struct.error) as e:
            errors.append(f"{folder.relative_to(ROOT).as_posix()}: {e}")

    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if errors:
        return 1

    text = json.dumps({"assets": entries}, indent=2) + "\n"
    if args.check:
        current = CATALOG.read_text(encoding="utf-8") if CATALOG.exists() else ""
        if current != text:
            print("ERROR catalog.json is stale: run python scripts/build_catalog.py", file=sys.stderr)
            return 1
        print(f"OK {len(entries)} assets, catalog up to date")
        return 0
    CATALOG.write_text(text, encoding="utf-8")
    print(f"OK wrote catalog.json with {len(entries)} assets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
