"""COCO Relative -> Absolute (for a target image size)

Convert a COCO-relative annotation (coordinates in [0, 1]) back to absolute
pixel coordinates for a specific image shape (height, width).

ASCII map (x right, y down):
    Relative (r_x, r_y)  --multiply-->  Absolute (x, y)
           x = r_x * width
           y = r_y * height
"""
from copy import deepcopy
from ctu.cocout00_utils import Polygons


class CocoRelativeToAbsolute:
    """Convert relative COCO coordinates to absolute for a target size.

    Quick example:
        conv = CocoRelativeToAbsolute()
        abs_coco = conv.run(rel_coco_di, desired_ht_wd=(1080, 1920), crop_oof=True)

    Notes
    -----
    - The tuple order for shapes is (height, width).
    - If both segmentation and bbox are present when computing area, segmentation is used.
    """

    # area calculation
    def _compute_annotation_area(self, img_ht_wd, segmentation=None, bbox=None):
        """Compute area in pixels. Segmentation takes priority over bbox."""
        if segmentation is not None:
            polygon = segmentation
        elif bbox is not None:
            x1, x2, y1, y2 = [bbox[0], bbox[0]+bbox[2], bbox[1], bbox[1]+bbox[3]]
            polygon = [[x1, y1, x1, y2, x2, y2, x2, y1]]
        else:
            raise Exception("Not Possible to calculate")

        pol = Polygons.create(polygon)
        mask = pol.proj_to_mask(width=img_ht_wd[1], height=img_ht_wd[0])
        return mask.area_of_mask()

    # convert coordinate to relative values
    def _index_is_x_coordinate(self, index):
        return index%2==0

    def _update_image_dimensions(self, image_info, desired_ht_wd):
        """Update image height and width to target shape."""
        image_info["height"], image_info["width"] = desired_ht_wd
        return image_info

    def _clamp_coordinate_to_image_bounds(self, ele, index, img_wd, img_ht):
        if self._index_is_x_coordinate(index):
            if ele < 0:
                return 0.0
            elif ele > img_wd:
                return float(img_wd)
            else:
                return ele
        else:
            if ele < 0:
                return 0.0
            elif ele > img_ht:
                return float(img_ht)
            else:
                return ele

    def _relative_to_absolute_coordinates(self, rel_coord_li, img_wd, img_ht, crop_out_of_frame):
        """Convert flattened [x1, y1, ...] relative list to absolute pixels.
        
        Example:
            rel_coord_li = [0.5, 0.5, 0.5, 0.5]
            img_wd = 100
            img_ht = 100
            crop_out_of_frame = True
            absolute_coord_li = [50, 50, 50, 50]
        """
        # sum([ e>1 for e in rel_coord_li ]) Disabling this warning
        #
        # if (len(rel_coord_li)>1) and (max(rel_coord_li)>1):
        #     raise Exception('Data is already in absolute dimensions.'
        #                      ' Please Generate the Coco Relative Annotation.')
        #     return rel_coord_li
        if crop_out_of_frame:
            temp_li = [
                coordinate*img_wd if self._index_is_x_coordinate(i) else coordinate*img_ht
                for i,coordinate in enumerate(rel_coord_li)
            ]
            return [self._clamp_coordinate_to_image_bounds(e, i, img_wd, img_ht) for i,e in enumerate(temp_li)]
        else:
            return [
                coordinate*img_wd if self._index_is_x_coordinate(i) else coordinate*img_ht
                for i,coordinate in enumerate(rel_coord_li)
            ]

    def _convert_annotation_to_absolute(self, anno_info, desired_ht_wd, crop_out_of_frame):
        """Convert a single annotation from relative to absolute coordinates."""
        img_ht, img_wd = desired_ht_wd

        anno_info["segmentation"] = [self._relative_to_absolute_coordinates(anno, img_wd, img_ht, crop_out_of_frame)
                                     for anno in anno_info["segmentation"]]
        anno_info["bbox"] = self._relative_to_absolute_coordinates(anno_info["bbox"], img_wd, img_ht, crop_out_of_frame)

        # calculated field
        anno_info["area"] = self._compute_annotation_area(desired_ht_wd, anno_info["segmentation"], anno_info["bbox"])
        anno_info["area"] = abs(int(anno_info["area"]))  # to make it json serializable

        # Delete area key if present
        # anno_info.pop("area", None)

        return anno_info

    def run(self, rel_coco_di, desired_ht_wd=(1000,1000), crop_oof=True, area_thresh_for_oof=0):
        """Convert a COCO-relative dict to absolute pixel coordinates.

        oof (out_of_frame)
        
        Parameters
        ----------
        rel_coco_di : dict
            COCO-like dict with coordinates in relative form (values in [0, 1]).
        desired_ht_wd : tuple[int, int]
            Target image shape as (height, width). Example: (1080, 1920)
        crop_oof : bool
            If True, clamp out-of-frame coordinates to the image bounds.
        area_thresh_for_oof : float
            Drop annotations with computed area strictly less than this threshold.

        Returns
        -------
        dict
            COCO-like dict with absolute pixel coordinates.

        Example
        -------
        >>> CocoRelativeToAbsolute().run(rel_coco_di, desired_ht_wd=(1000, 1000), crop_oof=True)
        """
        new_di = deepcopy(rel_coco_di)

        for i,k in enumerate(new_di["annotations"]):

            # anno_info
            anno_info = new_di["annotations"][i]
            new_di["annotations"][i] = self._convert_annotation_to_absolute(anno_info, desired_ht_wd, crop_oof)

            # image_info
            image_index = [i for i,e in enumerate(new_di["images"])
                           if e["id"]==anno_info["image_id"]][0]
            image_info = new_di["images"][image_index]
            new_di["images"][image_index] = self._update_image_dimensions(
                image_info, desired_ht_wd)

        # remove those annotation with area 0 or less
        new_di["annotations"] = [k for i,k in enumerate(new_di["annotations"]) if k["area"]>=float(area_thresh_for_oof)]

        return new_di


# Backwards-compatible alias
CocoRel2CocoSpecificSize = CocoRelativeToAbsolute
