"""VOC exporter utilities.

Produces a per-image VOC XML element from a COCO-style dict's single-image
sub-dict. Caller can first slice the dataset to one image (e.g., via
`CocoImageSlicer.get_image_annotation`) and then call this to obtain an XML
string or lxml element (
if lxml is available). Falls back to string building when lxml is missing.
"""

from typing import Dict, Any


def _voc_xml_string(image_di: Dict[str, Any]) -> str:
    # Minimal VOC XML as a string (no external deps). One <object> per bbox.
    # Note: category name is looked up via category_id; if not resolvable,
    # it uses the numeric id as string.
    im = image_di["images"][0]
    width = int(im.get("width", 0))
    height = int(im.get("height", 0))
    filename = im.get("file_name", im.get("path", ""))

    # Build map category_id -> name
    cat_map = {c.get("id"): c.get("name") for c in image_di.get("categories", [])}

    parts = []
    parts.append("<annotation>")
    parts.append(f"  <folder></folder>")
    parts.append(f"  <filename>{filename}</filename>")
    parts.append("  <size>")
    parts.append(f"    <width>{width}</width>")
    parts.append(f"    <height>{height}</height>")
    parts.append("    <depth>3</depth>")
    parts.append("  </size>")

    for ann in image_di.get("annotations", []):
        bbox = ann.get("bbox")  # [x, y, w, h]
        if bbox is None:
            continue
        x, y, w, h = bbox
        xmin, ymin = int(x), int(y)
        xmax, ymax = int(x + w), int(y + h)
        name = cat_map.get(ann.get("category_id"), str(ann.get("category_id")))
        parts.append("  <object>")
        parts.append(f"    <name>{name}</name>")
        parts.append("    <pose>Unspecified</pose>")
        parts.append("    <truncated>0</truncated>")
        parts.append("    <difficult>0</difficult>")
        parts.append("    <bndbox>")
        parts.append(f"      <xmin>{xmin}</xmin>")
        parts.append(f"      <ymin>{ymin}</ymin>")
        parts.append(f"      <xmax>{xmax}</xmax>")
        parts.append(f"      <ymax>{ymax}</ymax>")
        parts.append("    </bndbox>")
        parts.append("  </object>")

    parts.append("</annotation>")
    return "\n".join(parts)


def coco_to_voc_per_image(single_image_coco: Dict[str, Any], as_string: bool = True):
    """Export a single-image COCO dict to a VOC XML string or lxml element.

    If `as_string` is True, always returns a string. Otherwise tries to build
    lxml element; if lxml is not installed, falls back to string.
    """
    if as_string:
        return _voc_xml_string(single_image_coco)

    try:
        from lxml.builder import E
    except Exception:
        return _voc_xml_string(single_image_coco)

    im = single_image_coco["images"][0]
    width = int(im.get("width", 0))
    height = int(im.get("height", 0))
    filename = im.get("file_name", im.get("path", ""))
    cat_map = {c.get("id"): c.get("name") for c in single_image_coco.get("categories", [])}

    objects = []
    for ann in single_image_coco.get("annotations", []):
        bbox = ann.get("bbox")
        if bbox is None:
            continue
        x, y, w, h = bbox
        xmin, ymin = int(x), int(y)
        xmax, ymax = int(x + w), int(y + h)
        name = cat_map.get(ann.get("category_id"), str(ann.get("category_id")))
        objects.append(
            E("object",
              E("name", name),
              E("pose", "Unspecified"),
              E("truncated", "0"),
              E("difficult", "0"),
              E("bndbox",
                E("xmin", str(xmin)),
                E("ymin", str(ymin)),
                E("xmax", str(xmax)),
                E("ymax", str(ymax)),
              )
            )
        )

    element = E("annotation",
                E("folder"),
                E("filename", filename),
                E("size",
                  E("width", str(width)),
                  E("height", str(height)),
                  E("depth", str(3))
                ),
                *objects)
    return element



