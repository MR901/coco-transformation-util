
import os
from pathlib import Path
import cv2
import random
import ctu

def run():
    examples_dir = Path(__file__).resolve().parents[1]
    dataset_dir = examples_dir / "datasets" / "mini"
    coco_path = dataset_dir / "coco-annotation.json"

    # collect images recursively
    image_paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        image_paths.extend((dataset_dir).rglob(ext))
    image_paths = sorted([str(p) for p in image_paths])

    if len(image_paths) == 0:
        raise Exception(f'No images detected in the directory: {dataset_dir}')

    path = image_paths[min(2, len(image_paths)-1)]

    # reading the image
    modif_di = {
        "image_path": path,
        "aspect_ratio": "dont maintain",
        # "options: None, 'maintain', 'dont maintain'",
        "image_ht_wd": (1000, 1500),
        # (1500, 2000),
        "padding_ht_wd": None,# (0.15,0.15),
        # "eg: None, (0.15,0.15)",
        "padding_color": (10, 10, 10),
        "crop_pt1_pt2": ((0.25,0.25), (0.75,0.75)),
        # "eg: None, ((0.1,0.1), (0.9,0.9))"
    }

    modif_di = ctu.normalize_modification_spec(modif_di)
    img = ctu.get_modified_image(modif_di)
    anno = ctu.get_modified_coco_annotation(img, str(coco_path), modif_di)

    ctu.AnnotationVisualizer.draw_annotation(
        img,
        coco_ann_di=anno,
        cls_mapper_di=None,
        draw_what=["mask"], # "bbox", "polyline", 
        thickness=10,
        alpha=0.98,
        title="Mask overlay",
        figure_size=(8, 4)
    )

    # print(anno)

    # creating a mask
    poly = anno["annotations"][0]["segmentation"]
    mask = ctu.create_mask(img, poly, transparent_mask=True)
    # visualize or save as needed

    mask = ctu.create_mask(img, poly, category_fill_value=1, transparent_mask=False)
    # visualize or save as needed
    
    
if __name__=="__main__":
    run()
