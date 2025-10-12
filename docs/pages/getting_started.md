# Getting Started

Install from source:

```bash
git clone https://github.com/MR901/coco-transformation-util.git
cd coco-transformation-util
python3 setup.py install
```

Quick start with wrappers:

```python
from ctu import (
    modification_spec_template,
    normalize_modification_spec,
    get_modified_image,
    get_modified_coco_annotation,
)

# 1) Build a modification spec (copy and edit the template)
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

# 2) Produce a transformed image
img = get_modified_image(spec)

# 3) Update COCO annotation for this transformed image
coco_path = "examples/datasets/mini/coco-annotation.json"
ann = get_modified_coco_annotation(img, coco_path, spec)

# ann is a COCO-like dict bound to the transformed image
```

Core modules example:

```python
from ctu import CocoAbsoluteToRelative, CocoRelativeToAbsolute, CocoImageSlicer

# Load a single-image COCO annotation by file name
single = CocoImageSlicer(annotation_path="examples/datasets/mini/coco-annotation.json") \
    .get_image_annotation("Mangoes.jpeg")

# Convert absolute -> relative
rel = CocoAbsoluteToRelative().run(single)

# Convert relative -> absolute with a target size
abs_back = CocoRelativeToAbsolute().run(rel, desired_ht_wd=(600, 800))
```
