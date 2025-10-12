
# import the necessary packages
from __future__ import absolute_import
from ctu._version import __version__

from .utils.image_ops import ImageTransform, ImgTransform
from .utils.viz import AnnotationVisualizer, Visualize
from .utils.mask_utils import create_mask, save_mask
from .coco_image_slicer import CocoImageSlicer, WholeCoco2SingleImgCoco
from .coco_absolute_to_relative import Coco2CocoRel, CocoAbsoluteToRelative
from .coco_relative_to_absolute import CocoRelativeToAbsolute, CocoRel2CocoSpecificSize
from .coco_aggregator import CocoAggregator, AggregateCoco

from .coco_transform_wrappers import (
    modification_spec_template,
    normalize_modification_spec,
    get_modified_image,
    get_modified_coco_annotation,
    # Back-compat aliases
    sample_modif_step_di,
    get_modif_image,
    get_modif_coco_annotation,
    accept_and_process_modif_di
)

# Format exporters
from .formats.yolo import coco_to_yolo, compute_category_id_to_index  # noqa: F401
from .formats.voc import coco_to_voc_per_image  # noqa: F401
from .utils.dataset_view import DatasetView  # noqa: F401

__all__ = [
    "CocoImageSlicer",
    "modification_spec_template",
    "normalize_modification_spec",
    "get_modified_image",
    "get_modified_coco_annotation",
    "sample_modif_step_di",
    "get_modif_image",
    "get_modif_coco_annotation",
    "accept_and_process_modif_di",
    "ImageTransform",
    "AnnotationVisualizer",
    "ImgTransform",
    "Visualize",
    "create_mask",
    "save_mask",
    "WholeCoco2SingleImgCoco",
    "Coco2CocoRel",
    "CocoAbsoluteToRelative",
    "CocoRelativeToAbsolute",
    "CocoRel2CocoSpecificSize",
    "CocoAggregator",
    "AggregateCoco",
    # Formats
    "coco_to_yolo",
    "compute_category_id_to_index",
    "coco_to_voc_per_image",
    "DatasetView"
]
