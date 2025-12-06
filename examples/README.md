# Examples Layout

This folder contains runnable examples, notebooks, and a small sample dataset.

Directory structure:

```
examples/
  datasets/
    mini/                 # small sample dataset bundled with the repo
      coco-annotation.json
      images/             # optional: class-wise or flat images
      *.jpg|*.jpeg|*.png  # images at root are also supported
  scripts/                # runnable Python example scripts
  notebooks/              # Jupyter notebooks demonstrating functionality
  outputs/                # generated artifacts (images, html, json)
```

# Running the scripts

From the repository root:

```bash
python examples/scripts/example_core_modules.py
python examples/scripts/example_highlevel_function.py
python examples/scripts/example_highlevel_function-createmask.py
```

The scripts auto-resolve paths relative to `examples/datasets/mini`.

# Preparing sample data

To create your own small dataset under `examples/datasets/mini`:

1. Place a COCO instance segmentation JSON at:
   - `examples/datasets/mini/coco-annotation.json`
2. Place images in either of these locations:
   - Flat: put all images directly under `examples/datasets/mini/`
   - Structured: put images under `examples/datasets/mini/images/` with any nested folders allowed (e.g., class-wise subfolders)
3. Ensure that the `file_name` fields in `coco-annotation.json` match the image filenames (e.g., `images/mangoes/mangoes_001.jpg` if using nested paths).

## Minimal example

```
examples/datasets/mini/
  coco-annotation.json
  images/
    class_a/
      a_001.jpg
      a_002.jpg
    class_b/
      b_001.jpg
```

In `coco-annotation.json -> images[*].file_name`, set values like:

```json
{
  "images": [
    { "id": 1, "file_name": "images/class_a/a_001.jpg", "width": 1024, "height": 768 },
    { "id": 2, "file_name": "images/class_b/b_001.jpg", "width": 640, "height": 480 }
  ],
  "annotations": [
    { "id": 10, "image_id": 1, "category_id": 1, "segmentation": [[...]], "bbox": [x,y,w,h], "iscrowd": 0 }
  ],
  "categories": [
    { "id": 1, "name": "class_a" },
    { "id": 2, "name": "class_b" }
  ]
}
```

# Notes

- Scripts will search for `*.jpg|*.jpeg|*.png` recursively under `examples/datasets/mini`.
- Outputs (images/annotations/HTML) are written to `examples/outputs/` or temporary folders the scripts create.
- If you swap in your own dataset, keep COCO schema compatibility intact.


