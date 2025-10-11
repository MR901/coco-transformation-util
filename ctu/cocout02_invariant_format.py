
"""Utilities to convert COCO annotations to relative coordinates with options.

This module converts absolute pixel coordinates to relative [0, 1] values and
optionally offsets for padding and crops by a relative window.

Typical usage:
    >>> rel = CocoAbsoluteToRelative().run(
    ...     coco_di,
    ...     offset="orig_to_pad",            # or "pad_to_orig" or None
    ...     rel_padding_ht_wd=(0.15, 0.15),   # (height, width)
    ...     rel_crop_pt1_pt2=((0.1, 0.1), (0.9, 0.9))
    ... )

Note: image shape is (height, width); OpenCV sizes are (width, height).
"""

from copy import deepcopy
from ctu.cocout01_slicer import CocoImageSlicer


class CocoAbsoluteToRelative:
    """Convert COCO annotations to relative coordinates with optional offsets.

    Converts polygon and bbox coordinates in a COCO dict to relative values in
    [0, 1] based on each image's width and height. Optionally offsets for
    padding and crops by a relative window. The "area" field is removed.
    """

    def __init__(self, msg=False):
        self.msg = msg

    # convert coordinate to relative values
    def _is_x_coord(self, index):
        return index%2==0

    # Backwards-compatible alias methods will be kept; new clearer names are added below.

    def _is_x_index(self, index):
        return index % 2 == 0

    def _scale_coordinates_to_relative(self, coordinates, image_width, image_height):
        """
        coordinates: [3386.5929, 1049.7573, 97.5238, 1049.1674]
        to relative: [0.7349, 0.3037, 0.0211, 0.3036]
        """
        if (len(coordinates) > 1) and (max(coordinates) <= 1):
            print("Data is already scaled to relative dimensions")
            return coordinates
        return [
            value / image_width if self._is_x_index(i) else value / image_height
            for i, value in enumerate(coordinates)
        ]

    def _annotate_original_dimensions(self, image_info):
        """Attach original dimensions to the image dict."""
        image_info["orig_width"] = image_info["width"]
        image_info["orig_height"] = image_info["height"]
        return image_info

    def _convert_annotation_to_relative(self, image_info, annotation_info):
        """Convert segmentation and bbox to relative coordinates; drop area."""
        image_width, image_height = image_info["width"], image_info["height"]
        annotation_info["segmentation"] = [
            self._scale_coordinates_to_relative(polygon_coords, image_width, image_height)
            for polygon_coords in annotation_info["segmentation"]
        ]
        annotation_info["bbox"] = self._scale_coordinates_to_relative(
            annotation_info["bbox"], image_width, image_height
        )

        # Delete area key
        annotation_info.pop("area", None)

        return annotation_info

    def gen_coco_rel_anno(self, coco_annotation_dict):
        """Convert all annotations in a COCO dict to relative coordinates."""
        if self.msg:
            print("Following keys are present in coco annotation:", list(coco_annotation_dict.keys()))
            print("Note: \"area\" will been dropped from \"annotations\" as it hasn't been converted to relative measure")

        for annotation_index, _ in enumerate(coco_annotation_dict["annotations"]):
            annotation_info = coco_annotation_dict["annotations"][annotation_index]

            image_index = [idx for idx, img in enumerate(coco_annotation_dict["images"])
                           if img["id"] == annotation_info["image_id"]][0]

            image_info = coco_annotation_dict["images"][image_index]

            coco_annotation_dict["annotations"][annotation_index] = self._convert_annotation_to_relative(
                image_info, annotation_info)

            coco_annotation_dict["images"][image_index] = self._annotate_original_dimensions(image_info)

        return coco_annotation_dict

    # New, clearer public names (wrappers for backwards compatibility)
    def generate_relative_annotation(self, coco_annotation_dict):
        """Alias for `gen_coco_rel_anno` with a clearer name."""
        return self.gen_coco_rel_anno(coco_annotation_dict)

    # -------------------------------------------------------< Related to Offset (Start)

    def convert_coord_from_orig_to_pad_addition(
        self, original_rel_x=None, original_rel_y=None, rel_padding_ht_wd=(0.35, 0.35)
    ):
        """
        Desc: takes the old relative coordinate and converts to new as padding is added.
              (Image Size is Increased)


        will be used for offsetting the coordinate the image which is inside the padded image
        This padding was added on both sides

        padded_img:

        new origin (0,0)
            +-------------------------------+ --      ---
            |*******************************| pady    
            |*    old +-----------+*********| --      
            |* origin |           |*********|         
            |*********|           |*********| old_ht   new_ht
            |*********+-----------+ rel_pt2*| --
            |*******************************| pady    
            +-------------------------------+ --      --
            |  padx   |  old_wd   |   padx  | (When Pad is added)
            |            new_wd             |

            # New and old will both be 1 in relative coordinate


      Dimension Change:

              Initial Origin       Initial End
                      O-----------|

             pad relative to old added on both side
            |---------O-----------|---------|

            New Origin                    New End (New coord relative to this new origin and length)
            O---------|-----------|---------|


        eg. Input: old_rel_x=0.5, old_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5)
            Output: (0.5, 0.5)
        """
        if ((original_rel_x is None) and (original_rel_y is None)):
            raise Exception("Both the \"old_rel_x\" and \"old_rel_y\" can't be None")
        pady, padx = rel_padding_ht_wd
        # calculating the new rel_x after padding was added based on previous rel_x
        rx = ((padx + original_rel_x) / (1+2*padx)) if original_rel_x is not None else None
        ry = ((pady + original_rel_y) / (1+2*pady)) if original_rel_y is not None else None

        if (rx is not None) and (ry is not None):
            return rx, ry
        elif (rx is not None) and (ry is None):
            return rx
        elif (rx is None) and (ry is not None):
            return ry

    def convert_coord_from_pad_to_orig(
        self, padded_rel_x=None, padded_rel_y=None, rel_padding_ht_wd=(0.35, 0.35)
    ):
        """
        Desc: takes the old relative coordinate when the padding was used and converts it 
              to that of the original . (Image Size is Decreased)

        Note: "rel_padding_ht_wd" is still according to the very initial point when it was added

        Dimension Change:

               Old Origin                    Old End
                O---------|-----------|---------|

             pad relative to old added on both side
                |---------O-----------|---------|

            back to Initial Origin       Initial End
                          O-----------|


        eg. Input: old_rel_x=0.5, old_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5)
            Output: (0.5, 0.5)
        """
        if ((padded_rel_x is None) and (padded_rel_y is None)):
            raise Exception("Both the \"pad_rel_x\" and \"pad_rel_y\" can't be None")
        pady, padx = rel_padding_ht_wd

        # calculating the very old rel_x before padding was added based on the rel_x from the padded img
        old_rel_x = (padded_rel_x * (1+2*padx) - padx) if padded_rel_x is not None else None
        old_rel_y = (padded_rel_y * (1+2*pady) - pady) if padded_rel_y is not None else None

        if (old_rel_x is not None) and (old_rel_y is not None):
            return old_rel_x, old_rel_y
        elif (old_rel_x is not None) and (old_rel_y is None):
            return old_rel_x
        elif (old_rel_x is None) and (old_rel_y is not None):
            return old_rel_y

    def _offset_one_annotation(self, annotation_info, offset="orig_to_pad", rel_padding_ht_wd=(0.35, 0.35)):
        """Offset a single annotation for padding change."""
        o2p = self.convert_coord_from_orig_to_pad_addition
        p2o = self.convert_coord_from_pad_to_orig

        if offset in ["orig_to_pad", "pad_to_orig"]:

            # converting segmentation while preserving polygon structure
            new_seg = []
            for poly in annotation_info["segmentation"]:
                new_poly = []
                for i, e in enumerate(poly):
                    if offset == "pad_to_orig":
                        val = p2o(
                            pad_rel_x=(e if self._is_x_coord(i) else None),
                            pad_rel_y=(None if self._is_x_coord(i) else e),
                            rel_padding_ht_wd=rel_padding_ht_wd
                        )
                    else:
                        val = o2p(
                            old_rel_x=(e if self._is_x_coord(i) else None),
                            old_rel_y=(None if self._is_x_coord(i) else e),
                            rel_padding_ht_wd=rel_padding_ht_wd
                        )
                    new_poly.append(val)
                new_seg.append(new_poly)
            annotation_info["segmentation"] = new_seg

            # converting bbox
            annotation_info["bbox"] = [
                p2o(
                    pad_rel_x=(e if self._is_x_coord(i) else None),
                    pad_rel_y=(None if self._is_x_coord(i) else e),
                    rel_padding_ht_wd=rel_padding_ht_wd
                ) if offset=="pad_to_orig" else o2p(
                    old_rel_x=(e if self._is_x_coord(i) else None),
                    old_rel_y=(None if self._is_x_coord(i) else e),
                    rel_padding_ht_wd=rel_padding_ht_wd
                )
                for i,e in enumerate(annotation_info["bbox"])
            ]

        else:
            raise Exception("Unacceptable value for \"offset\"")

        return annotation_info

    def offset_whole_coco_annotation(
        self, coco_anno_di, offset="orig_to_pad", rel_padding_ht_wd=(0.35, 0.35)
    ):
        """Offset all annotations for padding additions/removals.

        Parameters
        ----------
        coco_anno_di: dict
            COCO dict with absolute or relative coordinates.
        offset: {"orig_to_pad", "pad_to_orig"}
            Direction of offset: original->padded, or padded->original.
        rel_padding_ht_wd: tuple(float, float)
            Relative padding applied (height, width), e.g., (0.35, 0.35).

        Returns
        -------
        dict
            Updated COCO dict with coordinates offset and padding metadata in
            the images entries.
        """
        new_anno_di = {}
        new_anno_di["info"] = coco_anno_di["info"]
        new_anno_di["images"] = []
        new_anno_di["annotations"] = []
        new_anno_di["categories"] = coco_anno_di["categories"]

        # working on each image
        for image_idx in range(len(coco_anno_di["images"])):

            # single coco annotation
            scdi = CocoImageSlicer(None, coco_anno_di).get_image_annotation(
                image_idx, index_type="general_index")

            # adding padding info in coco "images" li
            t_di = scdi["images"][0]  # only a single dict in list
            # scdi["images"][0] = { # causes other information if present to get loose
            #     "id": t_di["id"],
            #     "file_name": t_di["file_name"],
            #     "width": t_di["width"],
            #     "height": t_di["height"],
            #     "padx": int(rel_padding_ht_wd[1]*t_di["width"]),
            #     "pady": int(rel_padding_ht_wd[0]*t_di["height"]),
            #     "padded_width": int( t_di["width"]*(1+2*rel_padding_ht_wd[1]) ),
            #     "padded_height": int( t_di["height"]*(1+2*rel_padding_ht_wd[0]) )
            # }
            t_di["padx"] = int(rel_padding_ht_wd[1]*t_di["width"])
            t_di["pady"] = int(rel_padding_ht_wd[0]*t_di["height"])
            t_di["padded_width"] = int(t_di["width"]*(1+2*rel_padding_ht_wd[1]))
            t_di["padded_height"] = int(t_di["height"]*(1+2*rel_padding_ht_wd[0]))
            scdi["images"][0] = t_di

            # modifying coordinate based on information change according to padding
            scdi["annotations"] = [
                self._offset_one_annotation(
                    anno_info,
                    offset=offset,
                    rel_padding_ht_wd=rel_padding_ht_wd
                )
                for anno_info in scdi["annotations"]
            ]

            # adding element back to main di
            new_anno_di["images"].extend(scdi["images"])
            new_anno_di["annotations"].extend(scdi["annotations"])

        # return the processed di
        return new_anno_di

    # -------------------------------------------------------< Related to Offset (End)

    # -------------------------------------------------------< Related to Crop (Start)

    def _new_coord_after_crop(
        self, coordinates, rel_crop_pt1_pt2=((0.1,0.1), (0.9,0.9))
    ):
        """
        Desc:
        """
        (x1,y1), (x2,y2), = rel_crop_pt1_pt2
        x, y = (x2-x1), (y2-y1)
        return [
            (rel_coord-x1)/x if self._is_x_coord(i) else (rel_coord-y1)/y
            for i,rel_coord in enumerate(coordinates)
        ]

    def _crop_one_annotation(self, annotation_info, rel_crop_pt1_pt2=((0.1,0.1), (0.9,0.9))):
        """Crop a single annotation by a relative window."""

        if rel_crop_pt1_pt2 is not None:

            # converting segmentation
            annotation_info["segmentation"] = [
                self._new_coord_after_crop(anno, rel_crop_pt1_pt2)
                for anno in annotation_info["segmentation"]
            ]

            # converting bbox
            annotation_info["bbox"] = self._new_coord_after_crop(
                annotation_info["bbox"], rel_crop_pt1_pt2)

        else:
            raise Exception("\"rel_crop_pt1_pt2\" is None")

        return annotation_info

    def crop_annotation_based_on_rel_size(self, coco_rel_di, rel_crop_pt1_pt2=((0.1,0.1), (0.9,0.9))):
        """Crop annotations by a relative window.

        pt1 == a == (x1,y1); pt2 == c == (x2,y2)
            _________________________
           |  a ___________ b        |
           |   |           |         |
           |   |           |         |
           |   |___________|         |
           |  d            c         |
           |_________________________|

        Parameters
        ----------
        coco_rel_di: dict
            COCO dict with relative coordinates.
        rel_crop_pt1_pt2: ((float, float), (float, float))
            Top-left and bottom-right relative points: ((x1, y1), (x2, y2)).

        Returns
        -------
        dict
            Updated COCO dict with cropped coordinates and crop metadata.
        """
        new_anno_di = {}
        new_anno_di["info"] = coco_rel_di["info"]
        new_anno_di["images"] = []
        new_anno_di["annotations"] = []
        new_anno_di["categories"] = coco_rel_di["categories"]

        # working on each image
        for image_idx in range(len(coco_rel_di["images"])):

            # single coco annotation
            scdi = CocoImageSlicer(None, coco_rel_di).get_image_annotation(
                image_idx, index_type="general_index")

            # adding padding info in coco "images" li
            # t_di = scdi["images"][0]  # only a single dict in list
            # t_di["crop_pt1_pt2"] = rel_crop_pt1_pt2,
            # scdi["images"][0] = t_di

            li = []
            for image_dict in scdi["images"]:
                image_dict["crop_pt1_pt2"] = rel_crop_pt1_pt2
                li.append(image_dict)
            scdi["images"] = li

            # modifying coordinate based on information change according to padding
            scdi["annotations"] = [
                self._crop_one_annotation(
                    anno_info,
                    rel_crop_pt1_pt2=rel_crop_pt1_pt2
                )
                for anno_info in scdi["annotations"]
            ]

            # adding element back to main di
            new_anno_di["images"].extend(scdi["images"])
            new_anno_di["annotations"].extend(scdi["annotations"])

        # return the processed di
        return new_anno_di

    # -------------------------------------------------------< Related to Crop (End)

    def run(self, coco_di, offset=None, rel_padding_ht_wd=None, rel_crop_pt1_pt2=None, inplace=False):
        """Convert to relative coordinates, with optional padding offset and crop.

        Parameters
        ----------
        coco_di: dict
            Input COCO dictionary (absolute or relative coordinates).
        offset: None | {"orig_to_pad", "pad_to_orig"}
            Offset direction for padding. If None, no offset is applied.
        rel_padding_ht_wd: tuple(float, float) | None
            Relative padding (height, width) used, required if `offset` is not None.
        rel_crop_pt1_pt2: ((float, float), (float, float)) | None
            Optional relative crop window: ((x1, y1), (x2, y2)).
        inplace: bool
            If True, operate in place on `coco_di`.

        Returns
        -------
        dict
            COCO dictionary with coordinates in relative space.

        Examples
        --------
        >>> CocoAbsoluteToRelative().run(coco_di)
        >>> CocoAbsoluteToRelative().run(coco_di, offset="orig_to_pad", rel_padding_ht_wd=(0.5, 0.5))
        >>> CocoAbsoluteToRelative().run(coco_di, rel_crop_pt1_pt2=((0.25, 0.25), (0.75, 0.75)))
        """
        coco_ann_di = coco_di if inplace else deepcopy(coco_di)

        coco_rel_anno = self.gen_coco_rel_anno(coco_ann_di)

        # related to padding
        if offset is not None:
            if rel_padding_ht_wd is None:
                raise Exception("Relative padding size can't be \"None\" when transforming b/c of padding")

            coco_rel_anno = self.offset_whole_coco_annotation(
                coco_rel_anno, offset=offset, rel_padding_ht_wd=rel_padding_ht_wd
            )

        # related to cropping of annotation
        if rel_crop_pt1_pt2 is not None:
            coco_rel_anno = self.crop_annotation_based_on_rel_size(
                coco_rel_anno, rel_crop_pt1_pt2=rel_crop_pt1_pt2)

        return coco_rel_anno


# Backwards-compatible alias for external users
Coco2CocoRel = CocoAbsoluteToRelative

