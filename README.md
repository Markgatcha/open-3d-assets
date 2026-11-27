# Open 3D Assets

Free 3D models for Roblox, game development and anything else.
**MIT licensed**: use, modify and sell things made with them, commercially or not.
No sign-up, no attribution beyond keeping the license notice.

**Browse and preview:** the gallery on this repo's GitHub Pages site
(`https://<your-username>.github.io/open-3d-assets/`).

## Quality tiers

| Tier | Format | Budget | Use it for |
| --- | --- | --- | --- |
| **Roblox** | `.glb` mesh | ≤ 20,000 triangles, textures ≤ 1024 px | Roblox Studio (Import 3D) |
| **Game** | `.glb` mesh | ≤ 100,000 triangles, textures ≤ 2048 px | Unity, Unreal, Godot, web games |
| **Hero** | `.glb` mesh | high detail, textures ≤ 4096 px | Renders, close-ups, retopology source |
| **Splat** | `.spz` Gaussian splat | 262,144 gaussians | Photo-like viewing, AR/web previews |

Meshes come with PBR textures (base color, metallic, roughness, normal).
Splats look the most realistic but are not meshes: most engines need a plugin to show
them, and they cannot be rigged or used for collision.

Roblox's per-mesh cap is 20,000 triangles
([Roblox artist onboarding](https://create.roblox.com/docs/en-us/onboarding/artists));
the Roblox tier targets 18,000 to leave headroom.

## Categories

`characters` · `creatures` · `items` · `props` · `environment` · `vehicles`

Characters are invented: fictional, stylized, or realistic-looking people who do not
exist. Nothing here is made from a photo of a real person or from a copyrighted
character. See [ASSET_POLICY.md](ASSET_POLICY.md).

## How the models are made

```
prompt ──► Z-Image-Turbo / Qwen-Image ──► BiRefNet ──┬─► Idol ──────────► .spz splat
           (source image, Apache-2.0)    (MIT)       └─► TRELLIS.2 ─────► .glb mesh
                                                         (decimate + bake to tier budget)
```

Every generator in the chain is open-weight and licensed for commercial use
(Apache-2.0 or MIT). Each model's `asset.json` records the prompt, seed and every
model used, so anyone can check where it came from.

The ComfyUI workflows are in [`workflows/`](workflows):

| File | Makes |
| --- | --- |
| `idol_image_to_splat.json` | Splat tier (open in the Comfy Cloud editor) |
| `idol_image_to_splat_api.json` | Same, in API format for scripts |
| `trellis2_image_to_mesh_roblox.json` | Roblox tier mesh |
| `trellis2_image_to_mesh_game.json` | Game tier mesh |
| `trellis2_image_to_mesh_hero.json` | Hero tier mesh |

The TRELLIS.2 files are Comfy's official template (MIT) with only the face budget and
texture sizes changed; `scripts/make_tier_workflows.py` regenerates them.

## Repo layout

```
assets/<category>/<id>/
  asset.json      metadata and provenance (required)
  model.glb       or model.spz
  preview.webp    gallery thumbnail (optional, ~512 px)
catalog.json      generated index the gallery reads
index.html, site/ the GitHub Pages gallery
workflows/        ComfyUI workflows
scripts/          catalog builder/validator and helpers
```

## Adding a model

```sh
python scripts/new_asset.py props wooden-barrel roblox "Wooden Barrel"
# drop model.glb (and preview.webp) into assets/props/wooden-barrel/, fill in prompt and seed
python scripts/build_catalog.py
```

`build_catalog.py` rejects an asset that is over its tier's triangle or texture budget,
names an unapproved generator, lacks a prompt and seed, or exceeds 50 MB. The same check
runs on every push and pull request.

## Hosting notes

- **GitHub Pages** serves the gallery and the model files straight from `main`
  (Settings → Pages → Deploy from branch → `main` / root).
- **No Git LFS.** Pages does not serve LFS files, and free LFS bandwidth is small.
  Keep each model under 50 MB (GitHub refuses files over 100 MB).
- A Pages site is limited to 1 GB. When the repo nears that, move Hero models to
  GitHub Releases (2 GB per file) and link them from `asset.json`.

## License

[MIT](LICENSE). The models are provided as-is, without warranty.
