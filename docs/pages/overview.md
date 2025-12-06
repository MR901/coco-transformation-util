---
title: Overview
---

# CTU Overview

CTU (COCO Transformation Util) is a Python library to apply geometric image
transformations and update the corresponding COCO annotations to remain in sync.

The library offers:

- Core building blocks for COCO coordinate conversions and dataset utilities
- High-level wrappers to normalize a modification spec, transform an image, and
  derive the aligned COCO annotation
- Format exporters to YOLO and VOC

## Key Concepts

- Image shape tuples are (height, width); OpenCV size tuples are (width, height).
- COCO-relative coordinates are in [0, 1] and scale by width/height to pixel
  coordinates.
- The modification spec describes desired transforms in a single dict.

## Public API (high level)

```python
from ctu import (
    modification_spec_template,
    normalize_modification_spec,
    get_modified_image,
    get_modified_coco_annotation,
)
```

See Getting Started for a quick end-to-end example.


