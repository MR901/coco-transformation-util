
import json
import random
from pathlib import Path

import cv2

from ctu import (
    AnnotationVisualizer,
    DatasetView,
)
from ctu.utils.mask_utils import create_mask, union, intersect, invert, iou


def run():
    examples_dir = Path(__file__).resolve().parents[1]
    dataset_dir = examples_dir / "datasets" / "mini"
    coco_path = dataset_dir / "coco-annotation.json"

    with open(coco_path, "r") as f:
        coco_di = json.load(f)

    # Visualize with labels and stable colors
    image_paths = [str(p) for p in (dataset_dir).rglob("*.jpg")]
    if not image_paths:
        # fallback to any known name in images list
        image_paths = [str(dataset_dir / coco_di["images"][0]["file_name"])]
    img_path = random.choice(image_paths)
    img = cv2.imread(img_path)

    # Build a single-image coco by matching file_name
    file_name = Path(img_path).name
    single = {
        "info": {},
        "images": [next(i for i in coco_di["images"] if i["file_name"] == file_name)],
        "annotations": [a for a in coco_di["annotations"] if a["image_id"] == next(i["id"] for i in coco_di["images"] if i["file_name"] == file_name)],
        "categories": coco_di["categories"],
    }

    print("Showing visualization with labels...")
    AnnotationVisualizer.draw_annotation(
        img, single, draw_what=["bbox", "polyline", "mask"], draw_text=True, text_scale=0.8, same_color_per_category=True
    )

    # Mask algebra demo (synthetic two rectangles)
    h, w = img.shape[:2]
    mask1 = create_mask(img, [[[10, 10, w//3, 10, w//3, h//3, 10, h//3]]], transparent_mask=False)
    mask2 = create_mask(img, [[[w//4, h//4, w//2, h//4, w//2, h//2, w//4, h//2]]], transparent_mask=False)
    u = union(mask1, mask2)
    inter = intersect(mask1, mask2)
    print("IoU:", iou(mask1, mask2))
    inv = invert(mask1)
    # Save masks to temp dir for quick inspection
    temp_dir = examples_dir / "notebooks" / "temporary"
    temp_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(temp_dir / "mask_union.png"), (u.astype("uint8") * 255))
    cv2.imwrite(str(temp_dir / "mask_intersect.png"), (inter.astype("uint8") * 255))
    cv2.imwrite(str(temp_dir / "mask_invert.png"), (inv.astype("uint8") * 255))
    print("Saved mask_union.png, mask_intersect.png, mask_invert.png in", str(temp_dir))

    # DatasetView demo
    dv = DatasetView(coco_di)
    print("Total images:", len(list(dv.iter_images())))
    cat_map = dv.build_category_id_map()
    print("Category id -> idx map:", cat_map)


if __name__ == "__main__":
    run()


