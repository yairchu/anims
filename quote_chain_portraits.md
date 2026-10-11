# Portrait assets for the quote chain notebook

`feiglin.png` and `yitzhak_yosef.png` are still missing; the scene shows a
silhouette until each file exists. Generate each in its own call
with an image-generation tool, attaching `netanyahu.png` as the first (style)
reference and the likeness reference as the second, then the common prompt
followed by the subject prompt. Keep the generated alpha. The scene applies a
circular clip when displaying the images.

Likeness references are frames from the downloaded source videos, extracted to
`output/portrait_refs/` (ignored by Git):

- `ben_gvir_ref.png`: 6:02 of the Channel 14 "הפטריוטים" interview `[PAuHvMDXYLc]`.
- `saar_ref.png`: 0:09 of the Sa'ar clip `[-bFkn2tKHUg]`.
- Yair Netanyahu: no local video; supply a reference photo.
- Feiglin and Rabbi Yitzhak Yosef: no local video; supply a reference photo.

## Common prompt

Use case: illustration-story. Asset: a single circular bust portrait for a political explainer animation. The first reference image is STYLE ONLY: match its cream circular backdrop, crisp black ink outlines, restrained warm skin shading, recognizable editorial cartoon likeness, clean bold silhouette, near-front three-quarter view, shoulders cropped at the bottom of the circle. Generate a DIFFERENT person as specified. The second reference is his LIKENESS reference; ignore its setting, captions, logos and watermarks. Square composition, circle fills 90% of canvas, genuine transparent background outside the cream circle. No text, no flags, no extra people, no watermark. Keep expression neutral and composed, not sinister or heroic.

## Ben Gvir — `ben_gvir.png`

Subject: Itamar Ben Gvir, round face, short graying dark hair, large white knitted kippah, rimless rectangular glasses, clean shaven, dark navy suit with white shirt and light blue tie.

## Sa'ar — `saar.png`

Subject: Gideon Sa'ar, short salt-and-pepper hair, dark rectangular-framed glasses, clean shaven, dark navy suit with white shirt and understated blue tie (formal, unlike the polo shirt in the reference).

## Yair Netanyahu — `yair_netanyahu.png`

Subject: Yair Netanyahu, short dark hair, clean shaven, dark suit with white open-collared shirt, no tie.

## Feiglin — `feiglin.png`

Subject: Moshe Feiglin, small knitted kippah, dark suit with white open-collared shirt, no tie.

## Rabbi Yitzhak Yosef — `yitzhak_yosef.png`

Subject: Rabbi Yitzhak Yosef, white beard, black rabbinical hat, glasses, black rabbinical robe over white shirt.
