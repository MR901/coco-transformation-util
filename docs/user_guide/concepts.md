# Core Concepts

- Image shape tuples are (height, width); OpenCV size tuples are (width, height).
- Color channel ordering is BGR when using OpenCV.
- COCO-relative coordinates are in [0, 1] and scale by width/height to pixel coordinates.
- A single-image COCO slice narrows a full COCO to one image entry with its annotations and the same categories list.

## Modification Spec

CTU uses a single dict (modification spec) to express desired geometric transforms. Typical keys:

- `image_path`: path to the source image
- `aspect_ratio`: one of None, "maintain", or "dont maintain"
- `image_ht_wd`: target image size as (height, width)
- `padding_ht_wd`: fractional padding on (height, width)
- `padding_color`: BGR tuple for padding color
- `crop_pt1_pt2`: normalized top-left and bottom-right crop points, each as (y_frac, x_frac)

Validate keys before use and prefer `normalize_modification_spec` to fill defaults.



