# Visualization and Masks

```python
from ctu import AnnotationVisualizer, DatasetView
from ctu.utils.mask_utils import create_mask, union, intersect, invert, iou

# Draw overlays
AnnotationVisualizer.draw_annotation(
    img, ann, draw_what=["bbox", "polyline", "mask"], draw_text=True, same_color_per_category=True
)

# Masks
poly = ann["annotations"][0]["segmentation"]
mask = create_mask(img, poly, transparent_mask=False)
print("IoU:", iou(mask, mask))
```

See Visual Recipes for side-by-side transformation examples.



