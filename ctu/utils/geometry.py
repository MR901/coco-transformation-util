import numpy as np
import cv2


class BoundingBox:
    _c_polygons = None

    INSTANCE_TYPES = (np.ndarray, list, tuple)
    STYLE_MIN_MAX = "minmax"
    STYLE_WIDTH_HEIGHT = "widthheight"

    @classmethod
    def create(cls, bbox, style=None):
        """Factory: accept list/tuple/ndarray or BoundingBox and return instance or None."""
        if isinstance(bbox, BoundingBox):
            return bbox
        if isinstance(bbox, cls.INSTANCE_TYPES):
            return BoundingBox(bbox, style=style)
        return None

    def __init__(self, bbox, style=None):
        assert len(bbox) == 4
        self.style = style if style else BBox.STYLE_MIN_MAX

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
        return self._xmin, self._ymin

    @property
    def max_point(self):
        return self._xmax, self._ymax

    @property
    def size(self):
        return self.width, self.height

    def area(self):
        return int(self.width) * int(self.height)

    def _as_minmax_tuple(self):
        return (self._xmin, self._ymin, self._xmax, self._ymax)

    def __eq__(self, other):
        if isinstance(other, self.INSTANCE_TYPES):
            other = BoundingBox(other)
        if isinstance(other, BoundingBox):
            return tuple(self._as_minmax_tuple()) == tuple(other._as_minmax_tuple())
        return False

    def draw(self, image, color=None, thickness=2):
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

    INSTANCE_TYPES = (list, tuple)

    def __init__(self, polygons):
        self.polygons = [np.array(polygon).flatten() for polygon in polygons]

    @property
    def style_points(self):
        if not self._c_points:
            self._c_points = [
                np.array(point).reshape(-1, 2).round().astype(int)
                for point in self.polygons
            ]
        return self._c_points

    @property
    def style_segmentation(self):
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
        if not self._c_mask:
            if height is None or width is None:
                xmax, ymax = self.proj_to_bbox().max_point
                width = int(xmax)
                height = int(ymax)
            size = (int(height), int(width))
            mask = np.zeros(size, dtype=np.uint8)
            cv2.fillPoly(mask, self.style_points, 1)
            self._c_mask = BinaryMask(mask)
            self._c_mask._c_polygons = self
        return self._c_mask

    def draw(self, image, color=None, thickness=3):
        if color is None:
            color = Visualize()._random_rgb_color()
        image_copy = image.copy()
        cv2.polylines(image_copy, self.style_points, isClosed=True, color=color, thickness=thickness)
        return image_copy


class BinaryMask:
    _c_polygons = None
    INSTANCE_TYPES = (np.ndarray,)

    def __init__(self, array):
        self.array = np.array(array, dtype=bool)

    def area_of_mask(self):
        return self.array.sum()

    def draw(self, image, color=None, alpha=0.5):
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


class ColorRandom:
    @property
    def _rgb(self):
        color = list(np.random.choice(range(256), size=3))
        return (int(color[0]), int(color[1]), int(color[2]))


# Back-compat aliases expected by other modules
BBox = BoundingBox
Polygons = PolygonSet
Mask = BinaryMask


