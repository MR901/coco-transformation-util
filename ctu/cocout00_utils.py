"""Deprecated shim: use `ctu.utils.*` instead.

This module re-exports a consolidated API from the split utils modules to
preserve backward compatibility with older imports (ctu.cocout00_utils).
"""

from .utils.image_ops import ImageTransform as ImgTransform  # noqa: F401
from .utils.viz import AnnotationVisualizer as Visualize  # noqa: F401
from .utils.mask_utils import create_mask, save_mask  # noqa: F401
from .utils.geometry import (
    BoundingBox as BBox,
    PolygonSet as Polygons,
    BinaryMask as Mask,
)  # noqa: F401


