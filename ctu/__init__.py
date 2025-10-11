
# import the necessary packages
from __future__ import absolute_import
from ctu._version import __version__

from .cocout00_utils import (
    ImageTransform,
    AnnotationVisualizer,
    create_mask,
    save_mask,
    # Back-compat aliases
    ImgTransform,
    Visualize,
)
from .cocout01_slicer import WholeCoco2SingleImgCoco
from .cocout02_invariant_format import Coco2CocoRel, CocoAbsoluteToRelative
from .cocout03_inv_to_coco import CocoRelativeToAbsolute, CocoRel2CocoSpecificSize
from .cocout04_agg_coco import CocoAggregator, AggregateCoco

from .cocout_wrapper import (
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

__all__ = [
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
    "AggregateCoco"
]
