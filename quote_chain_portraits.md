# Portrait assets for the quote chain notebook

All quote-chain speakers now have portrait assets. For regeneration, generate
each in its own call with an image-generation tool, attaching `netanyahu.png`
as the first (style) reference and, when available, the likeness reference as
the second, then the common prompt followed by the subject prompt. Keep the
generated alpha. The scene applies a circular clip when displaying the images.

The Shas media statement uses a party badge (`shas.png`, rendered from
`shas.svg`) instead of a portrait of Aryeh Deri. Its source label is
`הודעה לתקשורת · 2024`. The user-supplied logo is preserved in
`shas_logo.png` and embedded in `shas.svg`, centered with padding inside the
same cream circle as the portraits. The statement was attributed to Shas in
[Ynet's June 18, 2024 report](https://www.ynet.co.il/news/article/b18bcekia).

Feiglin and Yitzhak Yosef were generated with the built-in image-generation
tool using `netanyahu.png` as the style reference and the subject descriptions
below. Reference-photo downloads were unavailable, so the photos were linked
in the prompts rather than attached:

- [Feiglin reference](https://static.timesofisrael.com/blogs/uploads/2019/03/feiglin.jpg)
- [Yitzhak Yosef reference](https://images1.ynet.co.il/picserver5/crop_images/2024/05/12/r1LiTUCGC/r1LiTUCGC_0_195_1102_1406_0_x-large.jpg)

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

Subject: Moshe Feiglin, Israeli politician, recognizable likeness: balding head with short gray hair at the sides, small knitted kippah, thin round wire-rim glasses, narrow long face and prominent nose, close-trimmed gray beard and mustache, dark suit with white open-collared shirt, no tie.

## Rabbi Yitzhak Yosef — `yitzhak_yosef.png`

Subject: Rabbi Yitzhak Yosef, the Sephardic rabbi from Israel, recognizable likeness: broad round face, full white beard and mustache, glasses with lightly tinted lenses, traditional flat-topped black Sephardic rabbinical hat with gold embroidered band, black rabbinical robe with restrained gold embroidered trim over white shirt. The hat must fit completely inside the cream circle, with a small gap above.
