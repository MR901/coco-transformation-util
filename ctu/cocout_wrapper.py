"""High-level wrappers for image transformation and COCO annotation updates.

This module exposes simple helper functions to:
- Normalize a user-provided modification spec
- Generate a modified image from the spec
- Produce a corresponding modified COCO annotation for that image

Backwards compatibility: legacy names are preserved as aliases.
"""

import cv2
from copy import deepcopy
from ctu.cocout00_utils import ImgTransform
from ctu.cocout01_slicer import WholeCoco2SingleImgCoco
from ctu.cocout02_invariant_format import Coco2CocoRel, CocoAbsoluteToRelative
from ctu.cocout03_inv_to_coco import CocoRelativeToAbsolute, CocoRel2CocoSpecificSize

# Template/specification for image modification. Values are placeholders and
# should be replaced by callers before normalization.
modification_spec_template = {
    "image_path": "<add path to a image>",
    "aspect_ratio": "maintain",  # options: None, "maintain", "dont maintain"
    "image_ht_wd": (1500, 2000),
    "padding_ht_wd": "eg: None, (0.15,0.15)",
    "padding_color": (10, 10, 10),
    "crop_pt1_pt2": "eg: None, ((0.1,0.1), (0.9,0.9))",
}


def _validate_modification_spec(spec):
    """Validate required keys and allowed values in modification spec.

    This function checks presence of required keys and that `aspect_ratio`
    is one of the supported options. It does not enforce types for placeholder
    defaults, as templates may carry strings that will be replaced by callers.
    """
    required_keys = (
        "image_path",
        "aspect_ratio",
        "image_ht_wd",
        "padding_ht_wd",
        "padding_color",
        "crop_pt1_pt2",
    )
    for key in required_keys:
        if key not in spec:
            raise ValueError(f"Missing required key in modification spec: '{key}'")

    allowed_aspect = (None, "maintain", "dont maintain")
    if spec.get("aspect_ratio") not in allowed_aspect:
        raise ValueError("aspect_ratio must be one of None, 'maintain', 'dont maintain'")

def normalize_modification_spec(modification_spec):
    """Normalize and enrich a modification spec for downstream functions.

    The normalization performs two adjustments:
    - If aspect ratio is None, sets image_ht_wd to None (no resizing).
    - If aspect ratio is "maintain", converts image_ht_wd to ("-", width)
      so that only width is used by the image generator.

    It also adds `img_name` derived from `image_path`.

    Parameters
    ----------
    modification_spec: dict
        User-provided spec describing desired transforms.

    Returns
    -------
    dict
        A deep-copied, normalized spec ready for image and annotation functions.
    """
    spec = deepcopy(modification_spec)
    _validate_modification_spec(spec)

    # Normalization
    if spec["aspect_ratio"] is None:
        spec["image_ht_wd"] = None
    if spec["aspect_ratio"] == "maintain":
        spec["image_ht_wd"] = ("-", spec["image_ht_wd"][1])
    spec["img_name"] = spec["image_path"].split("/")[-1]

    print(
        "Following Setting is being used:\n\t"
        + "\n\t".join([f"{k}\t: {item}" for k, item in spec.items()])
    )

    return spec


def get_modified_image(modification_spec):
    """Generate a modified image as described by the spec.

    Parameters
    ----------
    modification_spec: dict
        Normalized spec returned by `normalize_modification_spec`.

    Returns
    -------
    img: numpy.ndarray
        The transformed image.
    """
    spec = modification_spec

    # 1. Read
    img = cv2.imread(spec["image_path"])

    # 2. Size change
    if spec["image_ht_wd"] is not None:
        if spec["aspect_ratio"] == "maintain":
            img = ImgTransform.resize_with_aspect_ratio(img, width=spec["image_ht_wd"][1])
        else:
            img = cv2.resize(img, spec["image_ht_wd"][::-1], interpolation=cv2.INTER_AREA)

    # 3. Add padding
    if spec["padding_ht_wd"] is not None:
        img = ImgTransform.add_relative_padding_to_image(
            img, rel_padding_ht_wd=spec["padding_ht_wd"], pad_color=spec["padding_color"]
        )

    # 4. Crop
    if spec["crop_pt1_pt2"] is not None:
        img = ImgTransform.relative_size_based_crop(
            img, rel_pt1=spec["crop_pt1_pt2"][0], rel_pt2=spec["crop_pt1_pt2"][1]
        )

    return img


def get_modified_coco_annotation(img, coco_path, modification_spec):
    """Produce a modified COCO annotation aligned to a transformed image.

    Parameters
    ----------
    img: numpy.ndarray
        The transformed image returned by `get_modified_image`.
    coco_path: str | os.PathLike
        Path to the dataset's COCO annotation file.
    modification_spec: dict
        Normalized spec returned by `normalize_modification_spec`.

    Returns
    -------
    dict | None
        A COCO annotation dict, or None if the image is not found in COCO.
    """
    spec = modification_spec

    # 1. Get this Annotation from local
    coco_ann_di = WholeCoco2SingleImgCoco(annotation_path=coco_path, coco_di=None).run(
        spec.get("img_name") or spec["image_path"].split("/")[-1]
    )

    if coco_ann_di is None:
        return None

    # 2. Modify Invariant Annotation
    rel_coco_di = CocoAbsoluteToRelative().run(
        coco_ann_di,
        offset=("orig_to_pad" if spec["padding_ht_wd"] is not None else None),
        rel_padding_ht_wd=spec["padding_ht_wd"],
        rel_crop_pt1_pt2=spec["crop_pt1_pt2"],
    )

    # 3. Convert it back to absolute coordinate space for the image size
    final_ann_di = CocoRelativeToAbsolute().run(
        rel_coco_di, desired_ht_wd=img.shape[:2], crop_oof=True, area_thresh_for_oof=0
    )

    return final_ann_di


# Backwards-compatible aliases
sample_modif_step_di = modification_spec_template
accept_and_process_modif_di = normalize_modification_spec
get_modif_image = get_modified_image
get_modif_coco_annotation = get_modified_coco_annotation

