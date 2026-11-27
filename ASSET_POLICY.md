# Asset policy

Every model in this repo is free for anyone to use, including commercially, under
the [MIT License](LICENSE). That promise only holds if every input that went into a
model was ours to give away. These rules exist to keep it true.

## Allowed inputs

A model's source image must be one of:

- **Generated** by an image model whose license allows commercial use of outputs,
  from a prompt written for this repo. Approved generators are listed below.
- **Your own photo of an object you own** (a mug, a chair, a toy you made).
  No people, no logos, no branded or trademarked designs in frame.

## Not allowed

- Photos or images of **real, identifiable people**, including celebrities,
  friends, or yourself. "Semi-real" or realistic characters are fine when they are
  invented, generated from a description, and do not depict a real person.
- **Copyrighted or trademarked characters, brands or logos** (anything from a
  game, film, show, comic, toy line or company), and prompts that name them
  ("in the style of <artist>", "<character> from <franchise>").
- Images found online, screenshots, stock photos, or any image you did not make.
- Output from any generator whose license restricts commercial use, restricts
  territories, or claims ownership of outputs.

## Approved generators

Only open-weight models whose licenses permit commercial use. Each asset records
which ones it used in `asset.json`.

| Step | Model | License |
| --- | --- | --- |
| Source image | Z-Image-Turbo (`Tongyi-MAI/Z-Image-Turbo`) | Apache-2.0 |
| Source image | Qwen-Image (`Qwen/Qwen-Image`) | Apache-2.0 |
| Source image | FLUX.2 [klein] 4B (`black-forest-labs/FLUX.2-klein-4B`) | Apache-2.0 |
| Background removal | BiRefNet (`Comfy-Org/BiRefNet`) | MIT |
| Image to Gaussian splat | Idol (`Comfy-Org/Idol`) | Apache-2.0 |
| Image to Gaussian splat | TripoSplat (`VAST-AI/TripoSplat`) | MIT |
| Image to textured mesh | TRELLIS.2 (`microsoft/TRELLIS.2-4B`) | MIT |
| Image to textured mesh | Pixal3D (`Comfy-Org/Pixal3D`) | MIT |
| Geometry estimation | MoGe-2 (`Ruicheng/moge-2-vitl-normal`) | MIT |

Not approved without a written review of their terms:

- **Hunyuan3D** open weights: the Tencent Hunyuan Community License excludes some
  territories and adds use restrictions.
- **Paid partner APIs** on Comfy Cloud (Hunyuan3D API, Rodin, Tripo, Meshy): output
  ownership and licensing depend on each provider's terms, not on Comfy's.

The DINOv3 image encoder used inside Idol, TripoSplat and Pixal3D ships under
Meta's DINOv3 License. It is a component of the generator, not part of any asset
in this repo. Check its terms if you redistribute the generator weights yourself.

## Every asset must record

`asset.json` carries the provenance that makes the license claim checkable:
the exact prompt, seed, generator models and their licenses, and where the source
image came from. `scripts/build_catalog.py` refuses an asset that is missing any
of it or that names a generator outside the approved list.
