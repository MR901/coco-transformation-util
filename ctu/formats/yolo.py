"""YOLO exporter utilities.

Exports a COCO-style dict into YOLO label lines per image file. This function
assumes COCO `bbox` in [x, y, width, height] absolute pixels and converts to
YOLO normalized center-x, center-y, width, height in [0, 1].

It also provides a helper to compute a stable category index mapping (0-based)
from COCO `categories` entries, ordered by id ascending.
"""

from typing import Dict, List, Tuple


def compute_category_id_to_index(coco_di: Dict) -> Dict[int, int]:
    """Return a mapping from COCO category_id -> contiguous 0-based index.

    The mapping is derived by sorting categories by their id, then assigning
    indices 0..N-1 in that order.
    """
    categories = coco_di.get("categories", [])
    sorted_cats = sorted(categories, key=lambda c: c.get("id", 0))
    return {c["id"]: i for i, c in enumerate(sorted_cats)}


def _bbox_xywh_to_yolo(bbox_xywh: List[float], img_w: int, img_h: int) -> Tuple[float, float, float, float]:
    x, y, w, h = bbox_xywh
    cx = x + w / 2.0
    cy = y + h / 2.0
    return cx / img_w, cy / img_h, w / img_w, h / img_h


def coco_to_yolo(coco_di: Dict) -> Dict[str, List[str]]:
    """Convert a COCO-style dict to YOLO label lines per image path.

    Returns a dict mapping image path (or file_name if path missing) -> list of
    YOLO lines (strings: "<cls> cx cy w h" with 5-decimal precision).
    """
    # Build category id -> yolo index map
    cat_id_to_idx = compute_category_id_to_index(coco_di)

    # Prepare image id -> (path, width, height)
    img_meta = {}
    for img in coco_di.get("images", []):
        path = img.get("path", img.get("file_name"))
        img_meta[img["id"]] = (path, int(img.get("width", 0)), int(img.get("height", 0)))

    # Initialize per-image list
    yolo_map: Dict[str, List[str]] = {}
    for ann in coco_di.get("annotations", []):
        img_id = ann.get("image_id")
        cat_id = ann.get("category_id")
        bbox = ann.get("bbox")
        if img_id not in img_meta or bbox is None or cat_id not in cat_id_to_idx:
            # skip malformed entries
            continue
        path, width, height = img_meta[img_id]
        if width <= 0 or height <= 0:
            continue
        cx, cy, w, h = _bbox_xywh_to_yolo(bbox, width, height)
        label_idx = cat_id_to_idx[cat_id]
        line = f"{label_idx} {cx:.5f} {cy:.5f} {w:.5f} {h:.5f}"
        yolo_map.setdefault(path, []).append(line)

    return yolo_map



