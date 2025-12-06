# Deprecations and Backward Compatibility

This library preserves several legacy names for backward compatibility. Prefer the modern names shown on the right.

- `ctu.cocout_wrapper` ➜ `ctu.coco_transform_wrappers`
- `ctu.cocout00_utils` ➜ `ctu.utils.*`
- `ctu.cocout01_slicer` ➜ `ctu.coco_image_slicer`
- `ctu.cocout02_invariant_format` ➜ `ctu.coco_absolute_to_relative`
- `ctu.cocout03_inv_to_coco` ➜ `ctu.coco_relative_to_absolute`
- `ctu.cocout04_agg_coco` ➜ `ctu.coco_aggregator`

Wrappers (function aliases):

- `sample_modif_step_di` ➜ `modification_spec_template`
- `accept_and_process_modif_di` ➜ `normalize_modification_spec`
- `get_modif_image` ➜ `get_modified_image`
- `get_modif_coco_annotation` ➜ `get_modified_coco_annotation`

Core modules and utils:

- `WholeCoco2SingleImgCoco` ➜ `CocoImageSlicer`
- `Coco2CocoRel` ➜ `CocoAbsoluteToRelative`
- `CocoRel2CocoSpecificSize` ➜ `CocoRelativeToAbsolute`
- `AggregateCoco` ➜ `CocoAggregator`
- `get_coco_value_categories` ➜ `collect_categories`
- `generate_imgs_and_annotations_li` ➜ `build_images_and_annotations`
- `ImgTransform` ➜ `ImageTransform`
- `Visualize` ➜ `AnnotationVisualizer`
- `BBox` ➜ `BoundingBox`
- `Polygons` ➜ `PolygonSet`
- `Mask` ➜ `BinaryMask`

All legacy names continue to work but may be removed in a future major release. Update imports and calls accordingly.
