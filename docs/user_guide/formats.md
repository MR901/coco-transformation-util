# Format Exporters

Convert COCO annotations to other formats.

```python
from ctu import CocoImageSlicer, coco_to_yolo, coco_to_voc_per_image

# YOLO (per-image labels)
yolo_map = coco_to_yolo(coco_di)

# VOC (XML per image)
slicer = CocoImageSlicer(coco_di=coco_di)
single = slicer.get_image_annotation(0, index_type="general_index")
xml_str = coco_to_voc_per_image(single, as_string=True)
```

See Advanced Visuals for label previews.



