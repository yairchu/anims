"""Cut the hand out of a black-background phone mockup into phone_hand.png.

uv run --with pillow --with numpy --with scipy python tools/extract_phone_hand.py phone_hand_source.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

# The mockup's phone outline, in source pixels: aligned to phone_scene's bezel.
PHONE_BOX = (221, 186, 731, 1197)
# Its screen, where app content (e.g. the beige avatar) could pass for skin.
SCREEN_BOX = (236, 198, 716, 1186)

source = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float)
red, blue = source[..., 0], source[..., 2]
# Skin and nails are warm; the background is black and the phone neutral grey.
warmth = red - blue
alpha = np.clip((warmth - 12) / 28, 0, 1)
x0, y0, x1, y1 = SCREEN_BOX
alpha[y0:y1, x0:x1] = 0
solid = ndimage.binary_fill_holes(ndimage.binary_opening(alpha > .5, iterations=2))
labels, count = ndimage.label(solid)
sizes = ndimage.sum(solid, labels, range(1, count + 1))
# The fingers on the far side are separate pieces; keep every sizable one.
solid = np.isin(labels, 1 + np.nonzero(sizes > 500)[0])
# Where the phone cut the hand off, extend it under the bezel so no seam shows,
# and across the dark contact line between the phone's bottom and the palm.
px0, py0, px1, py1 = PHONE_BOX
under_phone = np.zeros_like(solid)
under_phone[py0:py1 + 4, px0:px1] = True
solid |= ndimage.binary_dilation(solid, iterations=6) & under_phone
# Soft edges only along the hand's outline; drop specks elsewhere.
alpha = np.where(solid, 1, alpha * ndimage.binary_dilation(solid, iterations=3))
# Edge pixels are blended with black; take colors from the nearest solid pixel.
_, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
rgb = source[iy, ix]
ys, xs = np.nonzero(alpha)
top, bottom, left, right = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
rgba = np.dstack([rgb, alpha * 255])[top:bottom, left:right].round().astype(np.uint8)
out = Path(__file__).parent.parent / "phone_hand.png"
Image.fromarray(rgba, "RGBA").save(out, optimize=True)
print(f"Saved {out.name}: crop origin ({left}, {top}), size {right - left}×{bottom - top}, phone box {PHONE_BOX}")
