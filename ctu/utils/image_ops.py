import cv2


class ImageTransform:
    """Basic image transformation utilities.

    - resize_with_aspect_ratio
    - add_relative_padding_to_image
    - relative_size_based_crop
    """

    @staticmethod
    def resize_with_aspect_ratio(frame, width=None, height=None, inter=cv2.INTER_AREA):
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
        scht, scwd = img.shape[:2]
        extra_x, extra_y = int(scht*rel_padding_ht_wd[0]), int(scwd*rel_padding_ht_wd[1])
        top, bottom = extra_x, extra_x
        left, right = extra_y, extra_y

        pdd_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, 
                                     value=pad_color)
        return pdd_img

    @staticmethod
    def relative_size_based_crop(img, rel_pt1=None, rel_pt2=None):
        if rel_pt1 is None:
            rel_pt1 = (0.0, 0.0)
        if rel_pt2 is None:
            rel_pt2 = (1.0, 1.0)

        x1, y1 = rel_pt1
        x2, y2 = rel_pt2

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


# Backwards-compatible aliases expected by __init__.py and examples
ImgTransform = ImageTransform


