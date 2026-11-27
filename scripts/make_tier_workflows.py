"""Write tier-sized copies of Comfy's TRELLIS.2 image-to-mesh template into workflows/.

The template (MIT, Comfy-Org/workflow_templates) decimates to 700k faces and bakes
4096px textures. Each tier here changes only the face budget and texture sizes.

Usage: python scripts/make_tier_workflows.py
"""
import json
import urllib.request
from pathlib import Path

TEMPLATE_URL = ("https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/"
                "templates/3d_pixal3d_trellis2_image_to_model.json")
OUT = Path(__file__).resolve().parent.parent / "workflows"

# tier -> (target faces, base/metal/rough texture px, normal map px, AO px)
TIERS = {
    "roblox": (18_000, 1024, 1024, 512),   # Roblox caps a mesh at 20k triangles; leave headroom
    "game": (90_000, 2048, 2048, 1024),
    "hero": (700_000, 4096, 2048, 1024),   # the template's own settings
}


def set_widget(wf, node_type, index, value, expect_count=1):
    nodes = [n for n in wf["nodes"] if n["type"] == node_type]
    assert len(nodes) == expect_count, f"expected {expect_count} {node_type}, found {len(nodes)}"
    for n in nodes:
        n["widgets_values"][index] = value


def main():
    with urllib.request.urlopen(TEMPLATE_URL, timeout=60) as r:
        template = r.read().decode("utf-8")
    OUT.mkdir(exist_ok=True)
    for tier, (faces, tex, normal, ao) in TIERS.items():
        wf = json.loads(template)
        set_widget(wf, "DecimateMesh", 0, faces)
        set_widget(wf, "PrimitiveInt", 0, tex)            # feeds UnwrapMesh + BakeTextureFromVoxel
        set_widget(wf, "BakeNormalMapFromMesh", 0, normal)
        set_widget(wf, "BakeAmbientOcclusion", 0, ao)
        set_widget(wf, "Save3DAdvanced", 0, f"3d/{tier}")
        path = OUT / f"trellis2_image_to_mesh_{tier}.json"
        path.write_text(json.dumps(wf, indent=2), encoding="utf-8")
        print(f"wrote {path.name}: {faces:,} faces, {tex}px textures")


if __name__ == "__main__":
    main()
