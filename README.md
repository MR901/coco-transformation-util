<div align="center">

<h1>CTU — COCO Transformation Util</h1>

</div>

A Python library to apply the same geometric transforms to images and their COCO annotations. CTU offers low-level utilities and simple high-level wrappers to keep image and annotation perfectly in sync.


## Why CTU?

- **Consistent transforms**: Resize, pad, crop (and more) while updating COCO annotations accordingly.
- **Simple wrappers**: High-level functions to express a modification recipe and get the transformed image and its COCO.
- **Visualization**: Overlay bboxes, polygons, and masks; stable per-category colors; quick inspection utilities.
- **Format exporters**: Convert COCO to YOLO (per image) and VOC (XML) formats.
- **Mask utilities**: Create, union, intersect, invert masks; compute IoU.


## Installation

Python 3.6+ is required. Create and activate a virtual environment (recommended), then either install from Git or clone locally.

Install directly from Git:

```bash
pip install -U pip
pip install git+https://github.com/MR901/coco-transformation-util.git
```

Or clone and develop locally:

```bash
git clone https://github.com/MR901/coco-transformation-util.git
cd coco-transformation-util
pip install -U pip
pip install -e .
```

Check installation:

```python
import ctu
print(ctu.__version__)
```

Notes:
- Dependencies are pinned in `pyproject.toml` (e.g., `opencv-python-headless`, `numpy`, `matplotlib`).
- Prefer the headless OpenCV build on servers/CI.


## Quickstart (Wrappers)

Use the high-level wrapper API to define a modification spec, produce a transformed image, and update its COCO annotation.

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
    "aspect_ratio": "maintain",  # options: None, "maintain", "dont maintain"
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
```


## Core building blocks

Prefer these when you need fine control or want to compose your own pipelines.

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


## Visualization and masks

```python
from ctu import AnnotationVisualizer, DatasetView
from ctu.utils.mask_utils import create_mask, union, intersect, invert, iou

# Visualize
AnnotationVisualizer.draw_annotation(
    img, ann, draw_what=["bbox", "polyline", "mask"], draw_text=True, same_color_per_category=True
)

# Mask algebra on polygons (example poly format is COCO-like segmentation)
poly = ann["annotations"][0]["segmentation"]
mask = create_mask(img, poly, transparent_mask=False)

# Combine and compare masks
u = union(mask, mask)
inter = intersect(mask, mask)
print("IoU:", iou(mask, mask))

# Dataset utilities
dv = DatasetView(ann)
print("#images:", len(list(dv.iter_images())))
```


## Format exporters (COCO -> YOLO / VOC)

```python
from ctu import CocoImageSlicer, coco_to_yolo, coco_to_voc_per_image

# Convert a COCO dict to YOLO per-image labels
yolo_map = coco_to_yolo(coco_di)

# Export a single-image COCO to a VOC XML string
slicer = CocoImageSlicer(coco_di=coco_di)
single = slicer.get_image_annotation(0, index_type="general_index")
xml_str = coco_to_voc_per_image(single, as_string=True)
```


## Examples and sample data

Explore end-to-end usage with the included examples and data:

- `examples/scripts/example_highlevel_function.py`: Wrapper quickstart (transform + update COCO).
- `examples/scripts/example_core_modules.py`: Core APIs (resizing, padding, cropping with annotation updates).
- `examples/scripts/example_format_exports.py`: Export COCO to YOLO and VOC.
- `examples/scripts/example_highlevel_function_createmask.py`: Create and visualize masks.
- `examples/notebooks/RunExample.ipynb`: Interactive walkthrough.
- `examples/datasets/mini/`: Small test dataset with images and COCO JSON.
- `examples/outputs/Demo-SampleOutput.html`: Pre-rendered demo output.


## Documentation

Additional docs live under `docs/` and are mirrored into the site build. Start with:

- `docs/pages/overview.md`
- `docs/pages/getting_started.md`
- `docs/api/index.rst`


## Version history (high level)

- v0.1: Initial core modules (`WholeCoco2SingleImgCoco`, `CocoAbsoluteToRelative`, `CocoRel2CocoSpecificSize`).
- v0.2: Removed external dependency; added `AggregateCoco` (now exported as `CocoAggregator`); added `area` in annotations.
- v0.3: Out-of-frame coordinate cleanup; image fields updates; added `create_mask` and visualization utilities; exporters and examples.


## Roadmap

- Rotation (90° left/right), horizontal/vertical flips.
- Additional format exporters and advanced augmentation recipes.


