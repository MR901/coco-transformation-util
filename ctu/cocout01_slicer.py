"""COCO Image Slicer

Extract a single-image COCO annotation from a full COCO dataset.

ASCII map (image selection by index/id/name):
    +-------------------------+
    | COCO 'images' list ...  |  -> select one ->  single-image COCO
    +-------------------------+

What this does (short):
    - Accepts both COCO and COCO-relative annotation formats
    - Works as a COCO annotation slicer (per-image)
    - Lookup can be by index, COCO image_id, or file_name

Quick example:
    slicer = CocoImageSlicer(annotation_path="path/to/coco.json")
    single = slicer.get_image_annotation("Mangoes.jpeg")  # or 0, or 17 with index_type="coco_image_id"
"""

import json
from copy import deepcopy


class CocoImageSlicer:
    """Create a per-image COCO annotation from a full COCO annotation.

    Parameters
    ----------
    annotation_path: str | None
        Path to a COCO annotation JSON file.
        Example: "examples/datasets/mini/coco-annotation.json".
        Takes precedence over `coco_di` if both are provided.
    coco_di: dict | None
        Already-loaded COCO annotation dictionary (absolute or relative format).
        Example: CocoImageSlicer.read_annotation(".../coco.json").
    inplace: bool
        If False (default), a deep copy of `coco_di` is stored internally.
        If True, the provided `coco_di` reference is kept (mutations propagate).
    msg: bool
        If True, prints short status messages during initialization.
    """
    @classmethod
    def read_annotation(cls, annotation_path):
        """Read and return a COCO annotation dictionary from JSON file."""
        with open(annotation_path, "r") as file:
            coco_annotation = json.load(file)
        return coco_annotation

    def __init__(self, annotation_path=None, coco_di=None, inplace=False, msg=False):
        """Initialize the slicer.

        Parameters
        ----------
        annotation_path: str | None
            Path to COCO JSON; used when provided.
            Precedence to "annotation_path" is given
            Example: "examples/datasets/mini/coco-annotation.json".
        coco_di: dict | None
            In-memory COCO dict (absolute or relative). Used when `annotation_path` is None.
        inplace: bool
            False (default): deep copy `coco_di` before storing.
            True: keep the original `coco_di` reference.
        msg: bool
            If True, prints brief informational messages.

        Examples
        --------
        # From path
        slicer = CocoImageSlicer(annotation_path="examples/datasets/mini/coco-annotation.json")

        # From in-memory dict
        full = CocoImageSlicer.read_annotation(".../coco.json")
        slicer = CocoImageSlicer(coco_di=full, inplace=False)
        """
        self.msg = msg

        # Read Annotation File
        if annotation_path is not None:
            if self.msg: print("Annotation path is used to generate annotation.")
            self.coco_annotation = self.read_annotation(annotation_path)
        else:
            if self.msg: print("Provided annotation dict is used to generate annotation.")
            self.coco_annotation = coco_di if inplace else deepcopy(coco_di)

    def get_image_annotation(self, image_identifier, index_type="general_index"):
        """Return a single-image COCO annotation.

        Parameters
        ----------
        image_identifier: int | str
            identifier to look for image
            - if string then work as image name
              str: file name in COCO, e.g., "Mangoes.jpeg"
            - if integer then work as index
              int: 0-based list index (index_type="general_index")
                   or COCO image id (index_type="coco_image_id")
        index_type: str
            Valid: "general_index" (default) or "coco_image_id".

        Returns
        -------
        dict | None
            COCO annotation for that single image, or None if no match is found.

        Examples
        --------
        # by file name
        CocoImageSlicer(".../coco.json").get_image_annotation("Mangoes.jpeg")
        # by list index
        CocoImageSlicer(".../coco.json").get_image_annotation(0, index_type="general_index")
        # by COCO image_id
        CocoImageSlicer(".../coco.json").get_image_annotation(17, index_type="coco_image_id")
        """
        coco_annotation = self.coco_annotation

        # Resolve target image_id and its index in the images list
        if image_identifier is None:
            raise Exception(
                "Provide image name, index in coco['images'], or a COCO image id"
            )

        if isinstance(image_identifier, str):
            matching_indices = [
                i for i, e in enumerate(coco_annotation["images"])
                if e["file_name"] == image_identifier
            ]
            if len(matching_indices) > 1:
                print("Trying to locate:", image_identifier)
                print("Matched Index:", matching_indices)
                raise Exception("[Err1a] 2 or more images share the image name. Check your annotation")
            elif len(matching_indices) == 0:
                print("No Matching Index for image_name:", image_identifier)
                return None
            image_list_index = matching_indices[0]
            image_id = coco_annotation["images"][image_list_index]["id"]
        else:
            idx = image_identifier
            if index_type == "coco_image_id":
                image_id = idx
                matching_indices = [
                    i for i, e in enumerate(coco_annotation["images"])
                    if e["id"] == image_id
                ]
                if len(matching_indices) > 1:
                    print("Trying to locate:", image_id)
                    print("Matched Index:", matching_indices)
                    raise Exception("[Err2a] 2 or more images share the image index. Check your annotation")
                elif len(matching_indices) == 0:
                    print("No Matching Index for image_id:", image_id)
                    return None
                image_list_index = matching_indices[0]
            else:
                image_list_index = idx
                image_id = coco_annotation["images"][idx]["id"]

        # Collect annotations linked to this image_id
        annotation_indices = [
            i for i, e in enumerate(coco_annotation["annotations"])
            if e["image_id"] == image_id
        ]

        # Build single-image COCO dictionary
        single_image_coco = {}
        single_image_coco["info"] = coco_annotation["info"]
        single_image_coco["images"] = [coco_annotation["images"][image_list_index]]
        single_image_coco["annotations"] = [coco_annotation["annotations"][i] for i in annotation_indices]
        single_image_coco["categories"] = coco_annotation["categories"]

        return single_image_coco

    # Backwards-compatible method name
    def run(self, img_index_or_name, index_type="general_index"):
        return self.get_image_annotation(img_index_or_name, index_type=index_type)

# Backwards-compatible class alias
WholeCoco2SingleImgCoco = CocoImageSlicer
