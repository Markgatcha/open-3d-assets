"""Create assets/<category>/<id>/asset.json with every field the validator expects.

Usage: python scripts/new_asset.py <category> <id> <tier> "<Display name>"
Example: python scripts/new_asset.py props wooden-barrel roblox "Wooden Barrel"
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    category, asset_id, tier, name = sys.argv[1:]
    folder = ROOT / "assets" / category / asset_id
    if (folder / "asset.json").exists():
        sys.exit(f"{folder} already has an asset.json")
    folder.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": asset_id,
        "name": name,
        "category": category,
        "tier": tier,
        "description": "",
        "tags": [],
        "license": "MIT",
        "files": {"model": "model.spz" if tier == "splat" else "model.glb", "preview": "preview.webp"},
        "source_image": {
            "origin": "generated",
            "generator": "Z-Image-Turbo",
            "prompt": "",
            "seed": 0,
        },
        "pipeline": [
            {"step": "background-removal", "model": "BiRefNet"},
            {"step": "image-to-splat" if tier == "splat" else "image-to-mesh",
             "model": "Idol" if tier == "splat" else "TRELLIS.2"},
        ],
        "created": date.today().isoformat(),
    }
    (folder / "asset.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"created {folder.relative_to(ROOT).as_posix()}/asset.json: add the model, preview, prompt and seed")


if __name__ == "__main__":
    main()
