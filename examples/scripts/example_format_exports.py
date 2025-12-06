
import json
from pathlib import Path

from ctu import CocoImageSlicer, coco_to_yolo, coco_to_voc_per_image


def run():
    examples_dir = Path(__file__).resolve().parents[1]
    dataset_dir = examples_dir / "datasets" / "mini"
    coco_path = dataset_dir / "coco-annotation.json"

    # Load COCO dict
    with open(coco_path, "r") as f:
        coco_di = json.load(f)

    # Prepare output directories inside examples/notebooks/temporary
    temp_dir = examples_dir / "notebooks" / "temporary"
    yolo_dir = temp_dir / "yolo"
    voc_dir = temp_dir / "voc"
    yolo_dir.mkdir(parents=True, exist_ok=True)
    voc_dir.mkdir(parents=True, exist_ok=True)

    # --- YOLO export (per-image .txt)
    yolo_map = coco_to_yolo(coco_di)
    saved_yolo = 0
    for img_path, lines in yolo_map.items():
        # keep labels self-contained in temp dir
        name = Path(img_path).stem + ".txt"
        out_path = yolo_dir / name
        with open(out_path, "w") as f:
            f.write("\n".join(lines))
        saved_yolo += 1

    # --- VOC export for a few images
    slicer = CocoImageSlicer(coco_di=coco_di, inplace=False)
    saved_voc = 0
    for i in range(min(5, len(coco_di.get("images", [])))):
        single = slicer.get_image_annotation(i, index_type="general_index")
        xml_str = coco_to_voc_per_image(single, as_string=True)
        name = Path(single["images"][0]["file_name"]).with_suffix(".xml").name
        out_path = voc_dir / name
        with open(out_path, "w") as f:
            f.write(xml_str)
        saved_voc += 1

    print("Saved YOLO labels:", saved_yolo)
    print("Saved VOC xml:", saved_voc)
    print("YOLO dir:", str(yolo_dir))
    print("VOC dir:", str(voc_dir))


if __name__ == "__main__":
    run()


