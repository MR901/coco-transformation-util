"""Read-only helpers to navigate COCO dicts.

These utilities avoid mutating the underlying COCO dict while providing
convenient iterators and mappers useful for analysis and export flows.
"""

from typing import Dict, Iterable, Iterator, Tuple


class DatasetView:
    def __init__(self, coco_di: Dict):
        self._c = coco_di
        self._images_by_id = {img["id"]: img for img in self._c.get("images", [])}
        self._categories_by_id = {c["id"]: c for c in self._c.get("categories", [])}

    def iter_images(self) -> Iterator[Dict]:
        for img in self._c.get("images", []):
            yield img

    def iter_annotations(self, image_id=None) -> Iterator[Dict]:
        anns = self._c.get("annotations", [])
        if image_id is None:
            for ann in anns:
                yield ann
        else:
            for ann in anns:
                if ann.get("image_id") == image_id:
                    yield ann

    def image_meta(self, image_id: int) -> Tuple[str, int, int]:
        """Return (path_or_name, width, height) for image id."""
        im = self._images_by_id.get(image_id)
        if not im:
            return ("", 0, 0)
        return (
            im.get("path", im.get("file_name", "")),
            int(im.get("width", 0)),
            int(im.get("height", 0)),
        )

    def category_name(self, category_id: int) -> str:
        cat = self._categories_by_id.get(category_id)
        if not cat:
            return str(category_id)
        return cat.get("name", str(category_id))

    def build_category_id_map(self) -> Dict[int, int]:
        """Map category_id -> 0-based contiguous index (sorted by id)."""
        cats = sorted(self._c.get("categories", []), key=lambda c: c.get("id", 0))
        return {c["id"]: i for i, c in enumerate(cats)}



