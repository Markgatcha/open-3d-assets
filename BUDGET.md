# Budget: $50 of Comfy Cloud credits

## What $50 buys

Comfy sells credits at **211 credits per $1**, so $50 is about **10,550 credits**.
Open models (Idol, TRELLIS.2, Z-Image-Turbo) bill as GPU time, not per call:
**0.266 credits per second** on an RTX PRO 6000 ($3.49/hr). That is roughly
**11 hours of GPU time** in total.

Sources: [Comfy Cloud plans](https://comfy.org/pricing),
[Partner Node pricing](https://docs.comfy.org/tutorials/partner-nodes/pricing) (Cloud GPU row).

The paid 3D partner APIs (Hunyuan3D, Rodin, Tripo, Meshy) cost $0.20 to $2.00 per
model and are not used here: their output terms are not covered by our MIT promise
(see [ASSET_POLICY.md](ASSET_POLICY.md)).

## Step 1: pilot (about $2)

The run times below are **guesses**. Measure them before spending the rest:

1. Generate 4 source images with Z-Image-Turbo and keep the best 2.
2. Run each through `workflows/idol_image_to_splat.json`.
3. Run each through `workflows/trellis2_image_to_mesh_roblox.json` and `_game.json`.
4. Note each run's duration from Comfy Cloud's usage page, then replace the
   assumptions in the table below.

## Step 2: the plan (assumed costs, replace after the pilot)

| Item | Assumed GPU time | Credits each | $ each |
| --- | --- | --- | --- |
| Source image (Z-Image-Turbo, ~4 tries per keeper) | 60 s | 16 | $0.08 |
| Idol splat | 60 s | 16 | $0.08 |
| TRELLIS.2 mesh, any tier | 4 min | 64 | $0.30 |

One source image can feed several tiers, so pay for the image once and reuse it.

| Batch | Count | Credits |
| --- | --- | --- |
| Source images | 90 | 1,440 |
| Roblox meshes | 50 | 3,200 |
| Game meshes | 30 | 1,920 |
| Hero meshes | 10 | 640 |
| Idol splats (from the same images) | 60 | 960 |
| **Total** | **150 models** | **8,160 (~$39)** |
| Reserve for failed runs and re-rolls | | ~2,390 (~$11) |

## Rules that keep it cheap

- **Stop a deployment when you are done.** A deployment bills while it holds a
  worker, even when idle. Prefer the Cloud editor for batches like this.
- **Use the trimmed workflows.** They skip the orbit video, live previews and
  splat-to-mesh conversion, which cost GPU time and produce nothing we publish.
- **Do not raise `num_gaussians` above 262144.** It adds time without adding detail.
- **Re-roll the image, not the mesh.** A bad source image makes a bad model, and
  images are the cheapest step.
