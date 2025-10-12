API Reference
=============

.. toctree::
   :maxdepth: 2


High-level wrappers
-------------------

.. autosummary::
   :toctree: generated
   :nosignatures:

   ctu.modification_spec_template
   ctu.normalize_modification_spec
   ctu.get_modified_image
   ctu.get_modified_coco_annotation

Core modules
------------

.. autosummary::
   :toctree: generated
   :nosignatures:

   ctu.CocoImageSlicer
   ctu.CocoAbsoluteToRelative
   ctu.CocoRelativeToAbsolute
   ctu.CocoAggregator

Utilities and formats
---------------------

.. autosummary::
   :toctree: generated
   :nosignatures:

   ctu.ImageTransform
   ctu.AnnotationVisualizer
   ctu.create_mask
   ctu.save_mask
   ctu.coco_to_yolo
   ctu.coco_to_voc_per_image
   ctu.DatasetView
