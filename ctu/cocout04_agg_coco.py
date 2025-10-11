"""Aggregate multiple COCO annotations into a single dataset.

This module provides a small utility to merge several COCO-style annotation
dicts into a single annotation dict. It remaps image and annotation IDs,
builds a unified category list (by category name), and handles duplicate
image file names either by skipping or by appending a numeric suffix.

Typical usage:

    aggregator = CocoAggregator(annotation_dicts)
    merged_coco = aggregator.run(if_img_name_match="append", show_warning=True)

Backwards compatibility: the historical class name `AggregateCoco` is kept as
an alias of `CocoAggregator`.
"""

import os
from copy import deepcopy


class CocoAggregator:
    """Merge multiple COCO annotation dicts into one.

    The constructor accepts either multiple dict arguments or a single list of
    dicts. Internally, all inputs are deep-copied to avoid mutating caller data.

    Parameters
    ----------
    *annotation_sources: dict | list[dict]
        One or more COCO annotation dicts, or a list of such dicts.
    """

    def __init__(self, *annotation_sources):
        # Normalize inputs to a flat list of dicts and deep copy to make
        # in-place remapping safe.
        copied_sources = deepcopy(annotation_sources)
        normalized_lists = [ [item] if isinstance(item, dict) else item for item in copied_sources ]
        self.annotation_dicts = [ann for sub in normalized_lists for ann in sub]

    def collect_categories(self):
        """Build a unified COCO category list and a name-to-id map.

        Returns
        -------
        categories_list: list[dict]
            COCO categories as dicts with fields `id` and `name`.
        category_name_to_id: dict[str, int]
            Mapping from category name to its 1-based category id.
        """
        unique_category_names = []
        for ann in self.annotation_dicts:
            for category in ann["categories"]:
                cat_name = category["name"]
                if cat_name not in unique_category_names:
                    unique_category_names.append(cat_name)

        category_name_to_id = {name: (i + 1) for i, name in enumerate(unique_category_names)}
        categories_list = [{"id": i + 1, "name": name} for i, name in enumerate(unique_category_names)]

        return categories_list, category_name_to_id

    def _generate_duplicate_suffix(self, file_name):
        # Generate next available suffix like "name (001).ext"
        stem, ext = os.path.splitext(file_name)
        stem = stem.rstrip()
        if stem.endswith(")") and "(" in stem:
            base = stem[:stem.rfind("(")].rstrip()
            num = stem[stem.rfind("(")+1 : -1]
            if len(num) == 3 and num.isdigit():
                nxt = int(num) + 1
                return f"{base} ({nxt:03d}){ext}"
        return f"{stem} (001){ext}"

    def build_images_and_annotations(
        self, category_name_to_id, if_img_name_match="skip", show_warning=True
    ):
        """Create unified images and annotations arrays.

        Parameters
        ----------
        category_name_to_id: dict[str, int]
            Mapping of category name to unified category id (1-based).
        if_img_name_match: {"skip", "append"}
            Behavior when encountering duplicate image file names:
            - "skip": ignore subsequent duplicates
            - "append": append " (NNN)" suffix to duplicates
        show_warning: bool
            Whether to print a warning when a duplicate image name is seen.

        Returns
        -------
        (images, annotations): tuple[list[dict], list[dict]]
            Unified COCO `images` and `annotations` lists.
        """
        images, annotations = [], []
        category_name_to_id = deepcopy(category_name_to_id)
        file_name_to_image_id = {}

        for ann in self.annotation_dicts:
            images_in_ann, annotations_in_ann = ann["images"], ann["annotations"]
            category_id_to_name = {c["id"]: c["name"] for c in ann["categories"]}

            # Map original image_id -> file_name before any remapping
            internal_image_id_to_file_name = {img["id"]: img["file_name"] for img in images_in_ann}

            # Process images
            for img_dict in images_in_ann:
                file_name = img_dict["file_name"]
                if file_name in file_name_to_image_id:
                    if show_warning:
                        print(f"There's already a record present for the image with name '{file_name}'.")
                    if if_img_name_match == "append":
                        file_name = self._generate_duplicate_suffix(file_name)
                        file_name_to_image_id[file_name] = len(file_name_to_image_id)
                    elif if_img_name_match == "skip":
                        continue
                else:
                    file_name_to_image_id[file_name] = len(file_name_to_image_id)

                img_dict["id"] = file_name_to_image_id[file_name]
                img_dict["file_name"] = file_name
                images.append(img_dict)

            # Process annotations
            for ann_dict in annotations_in_ann:
                # Map annotation's original image_id to the original file_name, then to new image id
                original_image_id = ann_dict["image_id"]
                category_name = category_id_to_name[ann_dict["category_id"]]
                original_file_name = internal_image_id_to_file_name[original_image_id]

                ann_dict["id"] = len(annotations)
                ann_dict["image_id"] = file_name_to_image_id[original_file_name]
                ann_dict["category_id"] = category_name_to_id[category_name]
                annotations.append(ann_dict)

        return images, annotations

    def run(self, if_img_name_match="skip", show_warning=True):
        """Aggregate all provided annotations and return a COCO dict.

        Parameters
        ----------
        if_img_name_match: {"skip", "append"}
            How to handle duplicate image file names.
        show_warning: bool
            Whether to print warnings on duplicates.

        Returns
        -------
        dict
            A COCO-style dict with keys: `info`, `categories`, `images`, `annotations`.
        """
        aggregated = {}
        aggregated["info"] = {"description": "agg-coco-data"}
        aggregated["categories"], category_name_to_id = self.collect_categories()
        aggregated["images"], aggregated["annotations"] = self.build_images_and_annotations(
            category_name_to_id, if_img_name_match=if_img_name_match, show_warning=show_warning
        )

        return aggregated

    # Backwards-compatible aliases (internal helpers)
    def get_coco_value_categories(self):  # legacy name
        return self.collect_categories()

    def generate_imgs_and_annotations_li(self, all_category_map_di, if_img_name_match="skip", show_warning=True):  # legacy name
        return self.build_images_and_annotations(all_category_map_di, if_img_name_match, show_warning)


# Backwards-compatible public alias
AggregateCoco = CocoAggregator

