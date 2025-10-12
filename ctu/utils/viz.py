import cv2
import matplotlib.pyplot as plt

from .geometry import PolygonSet
from .geometry import ColorRandom


class AnnotationVisualizer:
    def _view_img_using_matplot(self, image, title=None, figure_size=(6, 3)):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        fig = plt.figure(figsize=figure_size, dpi=150)
        if title is not None:
            plt.title(title)
        plt.imshow(img)
        plt.show()

    @staticmethod
    def draw_annotation(
        img, coco_ann_di=None, cls_mapper_di=None,
        draw_what=["bbox", "polyline", "mask"],
        thickness=10, alpha=0.5, title=None, figure_size=(6, 3),
        draw_text=False, text_scale=0.6, same_color_per_category=True
    ):
        draw_im = img.copy()
        color_di = {}

        if coco_ann_di is not None:
            for ann in coco_ann_di["annotations"]:
                # Determine color
                color = ColorRandom()._rgb
                if same_color_per_category:
                    cls = str(ann.get("category_id"))
                    if cls in color_di:
                        color = color_di[cls]
                    else:
                        color_di[cls] = color

                pol = PolygonSet.create(ann["segmentation"])
                if "bbox" in draw_what or draw_text:
                    bb = pol.proj_to_bbox()
                    if "bbox" in draw_what:
                        draw_im = bb.draw(image=draw_im, color=color, thickness=thickness)

                if "polyline" in draw_what:
                    draw_im = pol.draw(image=draw_im, color=color, thickness=thickness)

                if "mask" in draw_what:
                    msk = pol.proj_to_mask(width=img.shape[1], height=img.shape[0])
                    draw_im = msk.draw(image=draw_im, color=color, alpha=alpha)

                if draw_text:
                    cat_text = None
                    if cls_mapper_di is not None:
                        # map category id -> human readable name if provided
                        cat_text = cls_mapper_di.get(str(ann.get("category_id")))
                    if cat_text is None:
                        cat_text = str(ann.get("category_id"))
                    x, y = bb.min_point
                    cv2.putText(draw_im, cat_text, (int(x), int(y)),
                                cv2.FONT_HERSHEY_PLAIN, float(text_scale), (0,0,0), 2, cv2.LINE_AA)
                    cv2.putText(draw_im, cat_text, (int(x), int(y)),
                                cv2.FONT_HERSHEY_PLAIN, float(text_scale), (255,255,255), 1, cv2.LINE_AA)

        AnnotationVisualizer()._view_img_using_matplot(
            draw_im, title=title, figure_size=figure_size
        )


# Back-compat alias
Visualize = AnnotationVisualizer


