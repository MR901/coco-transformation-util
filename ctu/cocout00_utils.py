"""Core image utilities and lightweight COCO helpers.

This module provides:
- Image transforms commonly needed before updating COCO annotations
- Small geometry helpers for polygons, masks, and bounding boxes
- A simple visualizer for drawing annotations on images

Conventions
- Image shape is (height, width[, channels])
- OpenCV size is (width, height)
"""

import cv2
import os
import numpy as np
import matplotlib.pyplot as plt


class ImageTransform:
    """Basic image transformation utilities.

    Examples
    --------
    Resize keeping aspect ratio by width only:
        img2 = ImageTransform.resize_with_aspect_ratio(img, width=300)

    Add relative padding (15% height, 15% width) with dark gray:
        padded = ImageTransform.add_relative_padding_to_image(img, (0.15, 0.15), (10, 10, 10))

    Crop a centered square region using relative points:
        cropped = ImageTransform.relative_size_based_crop(img, (0.25, 0.25), (0.75, 0.75))
    """

    @staticmethod
    def resize_with_aspect_ratio(frame, width=None, height=None, inter=cv2.INTER_AREA):
        """Resize while preserving aspect ratio.

        Parameters
        ----------
        frame : np.ndarray
            Input image (H x W x C).
        width : int | None, optional
            Target width. If both width and height are provided, width takes priority.
        height : int | None, optional
            Target height (used only when width is None).
        inter : int, optional
            OpenCV interpolation flag, default cv2.INTER_AREA.

        Returns
        -------
        np.ndarray
            Resized image.

        Notes
        -----
        Example using OpenCV signature:
            cv2.resize(image, (0, 0), None, .25, .25)
        """
        dim = None
        (h, w) = frame.shape[:2]

        if width is None and height is None:
            return frame
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(frame, dim, interpolation=inter)

    @staticmethod
    def add_relative_padding_to_image(img, rel_padding_ht_wd=(0.15,0.15), pad_color=(10,10,10)):
        """Add symmetric padding relative to image size.

        The image is kept centered and padding is added on all sides based on
        fractions of the original height and width.

        ASCII diagram (not to scale):
            +---------------------+  <- extra_y (top)
            |                     |
            |   a ----------- b   |
            |    |           |    |
            |    |           |    |
            |   d ----------- c   |
            |                     |
            +---------------------+  <- extra_y (bottom)
            |----|           |----|
             extra_x        extra_x

        Parameters
        ----------
        img : np.ndarray
            Input image.
        rel_padding_ht_wd : tuple[float, float]
            Fractions of (height, width), e.g., (0.15, 0.15) means 15% of height
            on top and bottom, 15% of width on left and right.
        pad_color : tuple[int, int, int]
            BGR padding color.

        Returns
        -------
        np.ndarray
            Padded image.

        Examples
        --------
        padded = ImageTransform.add_relative_padding_to_image(img, (0.1, 0.2), (0, 0, 0))
        """
        scht, scwd = img.shape[:2]
        extra_x, extra_y = int(scht*rel_padding_ht_wd[0]), int(scwd*rel_padding_ht_wd[1])
        top, bottom = extra_x, extra_x
        left, right = extra_y, extra_y

        pdd_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, 
                                     value=pad_color)
        return pdd_img

    @staticmethod
    def relative_size_based_crop(img, rel_pt1=None, rel_pt2=None):
        """Crop using relative coordinates within [0, 1].

        ASCII diagram (x right, y down):
                a ___________ b
                 |           |
                 |           |
                 |___________|
                d            c

        Parameters
        ----------
        img : np.ndarray
            Input image.
        rel_pt1 : tuple[float, float] | None
            Top-left point a as (x1, y1) in [0, 1]; None -> (0.0, 0.0)
        rel_pt2 : tuple[float, float] | None
            Bottom-right point c as (x2, y2) in [0, 1]; None -> (1.0, 1.0)

        Returns
        -------
        np.ndarray
            Cropped image.

        Raises
        ------
        ValueError
            If rel_pt2 is not strictly greater than rel_pt1.

        Examples
        --------
        cropped = ImageTransform.relative_size_based_crop(img, (0.1, 0.1), (0.9, 0.9))
        """
        if rel_pt1 is None:
            rel_pt1 = (0.0, 0.0)
        if rel_pt2 is None:
            rel_pt2 = (1.0, 1.0)

        x1, y1 = rel_pt1
        x2, y2 = rel_pt2

        # clamp to [0,1]
        x1 = min(max(x1, 0.0), 1.0)
        y1 = min(max(y1, 0.0), 1.0)
        x2 = min(max(x2, 0.0), 1.0)
        y2 = min(max(y2, 0.0), 1.0)

        if x2 <= x1 or y2 <= y1:
            raise ValueError("Invalid crop: rel_pt2 must be strictly greater than rel_pt1")

        ht, wd = img.shape[:2]
        x1p, y1p = int(wd * x1), int(ht * y1)
        x2p, y2p = int(wd * x2), int(ht * y2)
        return img[y1p:y2p, x1p:x2p]


# -------------------------------------------------------------------------------------------------------- #

class BoundingBox:
    """Axis-aligned bounding box helper.

    Represents a rectangular box either as (x1, y1, x2, y2) or
    (x1, y1, width, height). Provides convenience methods to draw.
    """
    _c_polygons = None

    # Value types of :class:`BBox`
    INSTANCE_TYPES = (np.ndarray, list, tuple)
    # Bounding box format style [x1, y1, x2, y2]
    STYLE_MIN_MAX = "minmax"
    # Bounding box format style [x1, y1, width, height]
    STYLE_WIDTH_HEIGHT = "widthheight"

    def __init__(self, bbox, style=None):
        """Initialize a bounding box.

        Parameters
        ----------
        bbox : array-like (np.ndarray, list, tuple) of length 4
            Box coordinates per style.
        style : str | None
            One of {"minmax", "widthheight"}
            defaults to "minmax"
             - if "minmax" format style [x1, y1, x2, y2]
             - if"widthheight" format style [x1, y1, width, height]
            
        """
        assert len(bbox) == 4
        self.style = style if style else BBox.STYLE_MIN_MAX  # None == False

        self._xmin = int(bbox[0])
        self._ymin = int(bbox[1])
        if self.style == self.STYLE_MIN_MAX:
            self._xmax = int(bbox[2])
            self._ymax = int(bbox[3])
            self.width = self._xmax - self._xmin
            self.height = self._ymax - self._ymin
        if self.style == self.STYLE_WIDTH_HEIGHT:
            self.width = int(bbox[2])
            self.height = int(bbox[3])
            self._xmax = self._xmin + self.width
            self._ymax = self._ymin + self.height

    @property
    def min_point(self):
        """Minimum point of bounding box (x1, y1)."""
        return self._xmin, self._ymin

    @property
    def max_point(self):
        """Maximum point of bounding box (x2, y2)."""
        return self._xmax, self._ymax

    def draw(self, image, color=None, thickness=2):
        """Draw the bounding box on a copy of the input image and return it.

        Parameters
        ----------
        image : np.ndarray
            Input image.
        color : tuple or list [int, int, int] or None
            RGB color. If None, a random color is chosen.
        thickness : int
            Line thickness in pixels.
        """
        if color is None:
            color = ColorRandom()._rgb
        image_copy = image.copy()
        cv2.rectangle(image_copy, self.min_point, self.max_point, color=color, thickness=thickness)
        return image_copy


class PolygonSet:

    _c_bbox = None
    _c_mask = None

    _c_points = None
    _c_segmentation = None

    #: Polygon instance types
    INSTANCE_TYPES = (list, tuple)

    def __init__(self, polygons):
        # Store as 1D arrays for COCO segmentation compatibility
        self.polygons = [np.array(polygon).flatten() for polygon in polygons]

    @property
    def style_points(self):
        """
        Return polygons in point format:
            [
                [[x1, y1], [x2, y2], [x3, y3], ...],
                [[x1, y1], [x2, y2], [x3, y3], ...],
                ...
            ]
        """
        if not self._c_points:
            self._c_points = [
                np.array(point).reshape(-1, 2).round().astype(int)
                for point in self.polygons ]
        return self._c_points

    @property
    def style_segmentation(self):
        """
        Return polygons in segmentation format:
            [
                [x1, y1, x2, y2, x3, y3, ...],
                [x1, y1, x2, y2, x3, y3, ...],
                ...
            ]
        """
        if not self._c_segmentation:
            self._c_segmentation = [polygon.tolist() for polygon in self.polygons]
        return self._c_segmentation

    @classmethod
    def create(cls, polygons):
        if isinstance(polygons, PolygonSet.INSTANCE_TYPES):
            return PolygonSet(polygons)
        if isinstance(polygons, PolygonSet):
            return polygons
        return None

    def proj_to_bbox(self):
        """
        Desc: Returns or generates `BoundingBox` class representation of polygons.
        Return:
            `BoundingBox` class representation
        """
        if not self._c_bbox:

            y_min = x_min = float("inf")
            y_max = x_max = float("-inf")

            for point_list in self.style_points:
                minx, miny = np.min(point_list, axis=0)
                maxx, maxy = np.max(point_list, axis=0)

                y_min = min(miny, y_min)
                x_min = min(minx, x_min)
                y_max = max(maxy, y_max)
                x_max = max(maxx, x_max)

            self._c_bbox = BoundingBox((x_min, y_min, x_max, y_max))
            self._c_bbox._c_polygons = self

        return self._c_bbox

    def proj_to_mask(self, width=None, height=None):
        """
        Desc: Returns or generates `BinaryMask` class representation of polygons.
        Retun:
            `BinaryMask` class representation
        """
        if not self._c_mask:
            # Determine target size as (height, width)
            if height is None or width is None:
                # bbox max_point returns (xmax, ymax) == (width, height)
                xmax, ymax = self.proj_to_bbox().max_point
                width = int(xmax)
                height = int(ymax)
            size = (int(height), int(width))

            # Generate uint8 mask from polygons
            mask = np.zeros(size, dtype=np.uint8)
            cv2.fillPoly(mask, self.style_points, 1)
            self._c_mask = BinaryMask(mask)
            self._c_mask._c_polygons = self
        return self._c_mask

    def draw(self, image, color=None, thickness=3):
        """
        Desc: Draws the polygons to the image array of shape (width, height, 3)
              *This function modifies the image array*
        Inputs:
            color: RGB color representation (type: tuple, list)
            thickness: pixel thickness of box (type: int)
        """
        if color is None:
            color = Visualize()._random_rgb_color()
        image_copy = image.copy()
        cv2.polylines(image_copy, self.style_points, isClosed=True, color=color, thickness=thickness)
        return image_copy


class BinaryMask:
    """Binary mask wrapper around a boolean array."""
    _c_polygons = None

    INSTANCE_TYPES = (np.ndarray,)

    def __init__(self, array):
        self.array = np.array(array, dtype=bool)

    def area_of_mask(self):
        return self.array.sum()

    def draw(self, image, color=None, alpha=0.5):
        """Overlay the mask on an image with a solid color.

        Parameters
        ----------
        image : np.ndarray
            Input image.
        color : tuple | list[int, int, int] | None
            RGB overlay color. If None, a random color is chosen.
        alpha : float
            Opacity in [0, 1].
        """
        if color is None:
            color = ColorRandom()._rgb
        image_copy = image.copy()
        for c in range(3):
            image_copy[:, :, c] = np.where(
                self.array,
                image_copy[:, :, c] * (1 - alpha) + alpha * color[c],
                image_copy[:, :, c]
            )
        return image_copy


# -------------------------------------------------------------------------------------------------------- #

class ColorRandom:
    @property
    def _rgb(self):
        color = list(np.random.choice(range(256), size=3))
        # color = np.random.randint(0, 255, size=(3, ))

        #convert data types int64 to int and return
        return (int(color[0]), int(color[1]), int(color[2])) 


class AnnotationVisualizer:
    """Simple COCO annotation visualizer."""

    def _view_img_using_matplot(self, image, title=None, figure_size=(6, 3)):
        """matplotlib-based image view."""
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        fig = plt.figure(figsize=figure_size, dpi=150)  # no visible frame
        if title is not None: plt.title(title)
        plt.imshow(img)
        plt.show()

    @staticmethod
    def draw_annotation(img, coco_ann_di=None, cls_mapper_di=None,
                        draw_what=["bbox", "polyline", "mask"], thickness=10):
        """Draw COCO annotations on an image.

        Parameters
        ----------
        img : np.ndarray
            Input image (BGR).
        coco_ann_di : dict | None
            COCO annotation dict containing "annotations" and (optionally) "images".
        cls_mapper_di : dict[str, str] | None
            Optional mapping from category_id (as string) to display name.
        draw_what : list[str]
            Subset of {"bbox", "polyline", "mask"} controls what to draw.
        thickness : int
            Line thickness for bbox/polylines.

        Examples
        --------
        AnnotationVisualizer.draw_annotation(
            img, anno, draw_what=["polyline", "mask"],
            cls_mapper_di = {
                "0": "reference_object",
                "1": "orange",
                "2": "carrot",
                "3": "potato"
            }
        )    
        """
        draw_im = img.copy()
        color_di = {}

        if coco_ann_di is not None:
            for ann in coco_ann_di["annotations"]:

                # assign and get color for the class
                if cls_mapper_di is None:
                    color = ColorRandom()._rgb
                else:
                    cls = str(ann["category_id"])
                    color = ColorRandom()._rgb

                    # if already assigned then pick that color
                    if cls in color_di.keys():
                        color = color_di[cls]
                    else:
                        color_di[cls] = color

                # draw what ever is asked
                pol = PolygonSet.create(ann["segmentation"])
                if "bbox" in draw_what:
                    bb = pol.proj_to_bbox()
                    draw_im = bb.draw(image=draw_im, color=color, thickness=thickness)

                if "polyline" in draw_what:
                    draw_im = pol.draw(image=draw_im, color=color, thickness=thickness)

                if "mask" in draw_what:
                    msk = pol.proj_to_mask(width=img.shape[1], height=img.shape[0])
                    # mask_as_array = msk.array
                    draw_im = msk.draw(image=draw_im, color=color)

        # Show the Image
        AnnotationVisualizer()._view_img_using_matplot(draw_im)


def create_mask(image, poly, category_fill_value=1, transparent_mask=True, save_path=None):
    """Create a mask from polygon segmentation and optionally save it.

    Parameters
    ----------
    image : np.ndarray
        BGR image; used for shape and for transparent mask blending.
    poly : list[list[float]]
        Segmentation polygons. Example:
            [[300.63, 194.93, 324.29, 189.40, ... , 287.35, 201.20]]
    category_fill_value : int
        Fill value for non-transparent mask; background remains 0.
    transparent_mask : bool
        If True, return a colorized transparent overlay; otherwise return a
        uint8 binary mask with specified category_fill_value.
    save_path : str | None
        Optional path to save the mask (PNG only). e.g., dir1/dir2/mask.png

    Returns
    -------
    np.ndarray
        Transparent overlay (H x W x 3) if transparent_mask else binary mask (H x W).
    """
    # creating blank mask
    mask = np.zeros(image.shape[:2], dtype="uint8")

    # marking poly-area in mask
    poly_pt_format = PolygonSet(poly).style_points
    cv2.fillPoly(mask, poly_pt_format, color=255 if transparent_mask else category_fill_value)

    # creating transparent mask if asked
    if transparent_mask:
        mask = cv2.bitwise_and(image, image, mask=mask)

    # saving mask
    if save_path is not None:
        save_mask(save_path, mask)

    return mask


def save_mask(save_path, mask):
    """Save a mask to disk.

    Notes
    -----
    Must be saved as PNG to preserve raw mask values; using other formats may
    alter pixel values due to compression.

    Parameters
    ----------
    save_path : str
        Destination path; must end with .png
    mask : np.ndarray
        Binary mask (H x W) or color overlay (H x W x 3).
    """
    if save_path is None or save_path.split(".")[-1].lower() != "png":
        raise Exception("Error: Saving mask as only png is supported.")

    # Ensure directory exists
    dir_path = os.path.dirname(save_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    cv2.imwrite(save_path, mask, [cv2.IMWRITE_PNG_COMPRESSION, 0])

# ------------------------------------------------------------------------------------
# Backwards-compatible aliases
ImgTransform = ImageTransform
Visualize = AnnotationVisualizer
BBox = BoundingBox
Polygons = PolygonSet
Mask = BinaryMask