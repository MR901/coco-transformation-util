import os
import numpy as np
import cv2

from .geometry import PolygonSet


def create_mask(image, poly, category_fill_value=1, transparent_mask=True, save_path=None):
    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a numpy ndarray")
    if image.ndim not in (2, 3):
        raise ValueError("image must have 2 or 3 dimensions (H, W[, C])")
    if image.dtype != np.uint8:
        raise TypeError("image dtype must be uint8")
    if not isinstance(poly, (list, tuple)) or len(poly) == 0:
        raise ValueError("poly must be a non-empty list/tuple of polygons")
    for polygon in poly:
        if not isinstance(polygon, (list, tuple, np.ndarray)):
            raise ValueError("each polygon must be a sequence of coordinates")
        flat_len = int(np.array(polygon).size)
        if flat_len < 6 or flat_len % 2 != 0:
            raise ValueError("each polygon must have an even number of coords >= 6")

    mask = np.zeros(image.shape[:2], dtype="uint8")
    poly_pt_format = PolygonSet(poly).style_points
    cv2.fillPoly(mask, poly_pt_format, color=255 if transparent_mask else category_fill_value)

    if transparent_mask:
        mask = cv2.bitwise_and(image, image, mask=mask)

    if save_path is not None:
        save_mask(save_path, mask)

    return mask


def save_mask(save_path, mask):
    if save_path is None or not isinstance(save_path, str):
        raise Exception("Error: save_path must be a string ending with .png")
    _, ext = os.path.splitext(save_path)
    if ext.lower() != ".png":
        raise Exception("Error: Saving mask as only png is supported.")

    dir_path = os.path.dirname(save_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    cv2.imwrite(save_path, mask, [cv2.IMWRITE_PNG_COMPRESSION, 0])


def _ensure_mask_array(mask):
    """Validate and coerce mask to boolean ndarray of shape (H, W)."""
    if isinstance(mask, np.ndarray):
        arr = mask
    else:
        raise TypeError("mask must be a numpy ndarray")
    if arr.ndim == 3:
        # allow 3-channel binary, reduce to single channel
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    if arr.ndim != 2:
        raise ValueError("mask must have shape (H, W) or (H, W, C)")
    return arr.astype(bool)


def union(mask_a, mask_b):
    """Return boolean union of two masks as uint8 (0/1)."""
    a = _ensure_mask_array(mask_a)
    b = _ensure_mask_array(mask_b)
    if a.shape != b.shape:
        raise ValueError("mask shapes must match for union")
    return np.logical_or(a, b)


def intersect(mask_a, mask_b):
    """Return boolean intersection of two masks as uint8 (0/1)."""
    a = _ensure_mask_array(mask_a)
    b = _ensure_mask_array(mask_b)
    if a.shape != b.shape:
        raise ValueError("mask shapes must match for intersect")
    return np.logical_and(a, b)


def invert(mask):
    """Return inverted mask (boolean)."""
    a = _ensure_mask_array(mask)
    return np.logical_not(a)


def iou(mask_a, mask_b):
    """Compute intersection-over-union of two masks (float in [0, 1])."""
    a = _ensure_mask_array(mask_a)
    b = _ensure_mask_array(mask_b)
    if a.shape != b.shape:
        raise ValueError("mask shapes must match for iou")
    inter = np.logical_and(a, b).sum()
    uni = np.logical_or(a, b).sum()
    if uni == 0:
        return 0.0
    return float(inter) / float(uni)


