
"""
img = cv2.imread("example_data/Coffee-beans.jpeg")
img = Transform.resize_with_aspect_ratio(img, width=300, height=900)
Visualize().draw_annotation(img)
"""


"""
mask = create_mask(image, poly, transparent_mask=True)
aml.viewImage(mask)
"""


""" # Sample Code
coco_path= "data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json"

# Reading whole annotation from a path
whole_anno_di = CocoImageSlicer.read_annotation(coco_path)

# (1) Create annotation for single image: (1) Using already read coco_di
single_coco_di = CocoImageSlicer(annotation_path=coco_path).get_image_annotation(0)
print(single_coco_di)

# (1) Create annotation for single image: (2) Using the path
single_coco_di = CocoImageSlicer(coco_di=whole_anno_di).get_image_annotation(0)
print(single_coco_di)

# (2) Create annotation for single image: (1) Image selection Based on Image Index present in List
single_coco_di = CocoImageSlicer(coco_path).get_image_annotation(0, index_type="general_index")
print(single_coco_di)  # observe images: id will be+1 to index by default

# (2) Create annotation for single image: (2) Image selection Based on Image ID (present in coco)
single_coco_di = CocoImageSlicer(coco_path).get_image_annotation(1, index_type="coco_image_id")
print(single_coco_di)

# (2) Create annotation for single image: (3) Image selection Based on Image Name
single_coco_di = CocoImageSlicer(coco_path).get_image_annotation("IMG_20210302_102203_wt98.jpg")
print(single_coco_di)

# (3) Create annotation for single image: (1) Using Coco Annotation
single_coco_di = CocoImageSlicer(coco_di=whole_anno_di).get_image_annotation(0)
print(single_coco_di)

# (3) Create annotation for single image: (2) Using Relative Coco Annotation
rel_coco_di = CocoAbsoluteToRelative().run(whole_anno_di)
# print(rel_coco_di)
single_coco_di = CocoImageSlicer(coco_di=rel_coco_di).get_image_annotation(0)
print(single_coco_di)
# """



"""
self=1
convert_coord_from_orig_to_pad_addition(self, old_rel_x=0.5, old_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5))
# (0.5, 0.5)
convert_coord_from_orig_to_pad_addition(self, old_rel_x=0, old_rel_y=1, rel_padding_ht_wd=(0.5, 0.5))
# (0.25, 0.75)
"""


"""
self=1
convert_coord_from_pad_to_orig(self, pad_rel_x=0.5, pad_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5))
# (0.5, 0.5)
convert_coord_from_pad_to_orig(self, pad_rel_x=0, pad_rel_y=1, rel_padding_ht_wd=(0.5, 0.5))
# (-0.5, 1.5)  # mean the coordinate is in the padding region
"""


""" # Sample Code
        coco_path= 'data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json'

# Reading Whole annotation from a path
whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)
        print( whole_anno_di['annotations'][0]['bbox'] )

# (1) Convert Coco Annotation to Coco Relative Annotation: (1) inplace OFF
        rel_coco_di = CocoAbsoluteToRelative().run(whole_anno_di)
        print( rel_coco_di['annotations'][0]['bbox'] )

# (1) Convert Coco Annotation to Coco Relative Annotation: (2) inplace ON
        CocoAbsoluteToRelative().run(whole_anno_di, inplace=True)
        print( whole_anno_di['annotations'][0]['bbox'] )

# (2) Auto Detection of Coco Relative Annotation to NOT operate again
# "Data is already scaled to relative dimensions" - msg gets displayed but no exceeption
        rel_coco_di = CocoAbsoluteToRelative().run(whole_anno_di)
        print('\n AutoDetection: - Operations NOT Performed')
        print( whole_anno_di['annotations'][0]['bbox'] )
        print( rel_coco_di['annotations'][0]['bbox'] )

# (3) Effect of Padding Addition:
whole_anno_di = CocoImageSlicer.read_annotation(coco_path)
single_coco_di = CocoImageSlicer(coco_di=whole_anno_di).get_image_annotation(0)

        print('Without Offset, Coco Annotation\n{}\n{}'.format(
            str(single_coco_di['images'][0]), str(single_coco_di['annotations'][0]['segmentation'])))

        rel_coco_di = CocoAbsoluteToRelative().run(single_coco_di)
        print('\n\nWithout Offset, Coco Relative Annotation\n{}\n{}'.format(
            str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

# (3) Offset the Abs Coordinate: (1) B/C padding(relative dim) was added
        rel_coco_di = CocoAbsoluteToRelative().run(single_coco_di, offset='orig_to_pad', rel_padding_ht_wd=(0.5,0.5))
        print('\n\nAbsolute Coord Offset: orig_to_pad\n{}\n{}'.format(
            str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

# (3) Offset the Abs Coordinate: (2) B/C added padding(relative dim) was removed
        rel_coco_di = CocoAbsoluteToRelative().run(single_coco_di, offset='pad_to_orig', rel_padding_ht_wd=(0.5,0.5))
        print('\n\nAbsolute Coord Offset: pad_to_orig\n{}\n{}'.format(
            str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))


# (4) Offset the relative coordinate
        print('-'*100)
        rel_coco_di = CocoAbsoluteToRelative().run(single_coco_di)
        rel_coco_di = CocoAbsoluteToRelative().run(rel_coco_di, offset='pad_to_orig', rel_padding_ht_wd=(0.5,0.5))
        print('\n\nRelative Coord Offset: \n{}\n{}'.format(
            str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

# (5) Cropping the annotation
        print('-'*100)
whole_anno_di = CocoImageSlicer.read_annotation(coco_path)
rel_coco_di = CocoAbsoluteToRelative().run(single_coco_di)
        print('\n\nRelative Coord Before Crop: \n{}\n{}'.format(
            str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

rel_coco_di = CocoAbsoluteToRelative().run(rel_coco_di, rel_crop_pt1_pt2=((0.25,0.25), (0.75,0.75)))

        print('\n\nRelative Coord After Crop: \n{}\n{}'.format(
            str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

        # """

        """
        coco_path= 'data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json'
        whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)
        single_coco_di = WholeCoco2SingleImgCoco(coco_di=whole_anno_di).run(0)
        rel_coco_di = CocoAbsoluteToRelative().run(single_coco_di)
        print(rel_coco_di['annotations'][0]['bbox'])

        # On Single
        crop_rel_coco_di = CocoAbsoluteToRelative().run(whole_anno_di, rel_crop_pt1_pt2=((0.25,0.25), (0.75,0.75)))
        print('\n',crop_rel_coco_di['annotations'][0]['bbox'])

        # On Whole
        crop_rel_coco_di = CocoAbsoluteToRelative().run(whole_anno_di, rel_crop_pt1_pt2=((0.25,0.25), (0.75,0.75)))
        print('\n',crop_rel_coco_di['annotations'][0]['bbox'])
        """


    """
# Getting COCO & COCO Relative annotation
coco_path= "data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json"
whole_anno_di = CocoImageSlicer.read_annotation(coco_path)
single_coco_di = CocoImageSlicer(coco_di=whole_anno_di).get_image_annotation(0)
rel_coco_di = CocoAbsoluteToRelative().run(single_coco_di)

# Msg
print('\nCOCO Annotation:\n', single_coco_di["annotations"][0]["segmentation"])
print('\nCOCO Relative Annotation:\n', rel_coco_di["annotations"][0]["segmentation"])

# Convert it back to Absolute Coordinate System for any image size: (1) From Coco Relative
new_coco_di = CocoRelativeToAbsolute().run(rel_coco_di, desired_ht_wd=(100,100))
print('\nNew COCO Relative Annotation for (100,100):\n', new_coco_di["annotations"][0]["segmentation"])

# Convert it back to Absolute Coordinate System for any image size: (2) From Coco
# --> Error gets Generated
new_coco_di = CocoRelativeToAbsolute().run(single_coco_di, desired_ht_wd=(100,100))
# """

"""
agg_coco_di = AggregateCoco
(annotation_li).run(if_img_name_match="skip")
# agg_coco_di = AggregateCoco
(annotation_li).run(if_img_name_match="append")

print('#images :', len(agg_coco_di['images']))
print('#annotation :', len(agg_coco_di['annotations']))

"""


