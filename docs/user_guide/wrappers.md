# High-level Wrappers

The wrapper workflow mirrors a typical pipeline:

1. Build a modification spec using `modification_spec_template`.
2. Normalize it with `normalize_modification_spec`.
3. Produce a transformed image via `get_modified_image`.
4. Update COCO for the transformed image via `get_modified_coco_annotation`.

```python
from ctu import (
    modification_spec_template,
    normalize_modification_spec,
    get_modified_image,
    get_modified_coco_annotation,
)

spec = dict(modification_spec_template)
spec.update({
    "image_path": "examples/datasets/mini/Mangoes.jpeg",
    "aspect_ratio": "maintain",
    "image_ht_wd": (600, 800),
    "padding_ht_wd": (0.15, 0.15),
    "padding_color": (10, 10, 10),
    "crop_pt1_pt2": ((0.1, 0.1), (0.9, 0.9)),
})

spec = normalize_modification_spec(spec)
img = get_modified_image(spec)
ann = get_modified_coco_annotation(img, "examples/datasets/mini/coco-annotation.json", spec)
```

See also the Example Gallery for more recipes.



