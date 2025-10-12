# Advanced Visuals and Exports

Additional scenarios and label format previews.

## Rotate / Flip (conceptual)

Rotation and flipping are on the roadmap. When available, the same contract applies:
images are transformed, and COCO annotations are updated accordingly (both bbox and
segmentation). This page will be updated with visuals once implemented.

## YOLO Label Preview

First image's YOLO labels (class index, cx cy w h):

```text
.. literalinclude:: ../_static/example_yolo.txt
   :language: text
```

## VOC XML Preview

```xml
.. literalinclude:: ../_static/example_voc.xml
   :language: xml
```
