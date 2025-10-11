
import os
from pathlib import Path
import cv2
import random
from ctu import WholeCoco2SingleImgCoco, Coco2CocoRel, CocoRel2CocoSpecificSize
from ctu import ImgTransform, Visualize


def run():
    # Resolve dataset paths relative to the examples directory
    examples_dir = Path(__file__).resolve().parents[1]
    dataset_dir = examples_dir / 'datasets' / 'mini'
    coco_path = dataset_dir / 'coco-annotation.json'

    # Collect image paths (supports jpg/jpeg/png) from dataset root and nested folders like images/
    image_paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        image_paths.extend((dataset_dir).rglob(ext))

    if len(image_paths) == 0:
        raise Exception(f'No images detected in the directory: {dataset_dir}')

    # getting image address
    path = str(image_paths[random.randint(0, len(image_paths) - 1)])
    img_name = os.path.basename(path)


    # ----------------------------- < Original

    ## reading the image
    img = cv2.imread(path)

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco(annotation_path=str(coco_path), coco_di=None).run(img_name)

    ## draw with annotation
    print("\nOriginal")
    Visualize.draw_annotation(img, coco_ann_di)


    # ----------------------------- < Rescaling image size (With Aspect Ratio)

    ## reading the image
    img = cv2.imread(path)
    img = ImgTransform.resize_with_aspect_ratio(img, width=1000)

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco(annotation_path=str(coco_path), coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print("\nRescaling image size (With Aspect Ratio)")
    Visualize.draw_annotation(img, final_ann_di)

    # ----------------------------- < Rescaling image size (Without Aspect Ratio)

    wd_ht = (2000,1000)

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco(annotation_path=str(coco_path), coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print("\nRescaling image size (Without Aspect Ratio)")
    Visualize.draw_annotation(img, final_ann_di)


    # ----------------------------- < Rescaling image size + add padding to the image

    wd_ht = (1000,1000)
    padding_htwd = (0.55,0.15)

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)
    img = ImgTransform.add_relative_padding_to_image(
        img, rel_padding_ht_wd=padding_htwd, pad_color=(40,40,40))

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco(annotation_path=str(coco_path), coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di, offset="orig_to_pad", rel_padding_ht_wd=padding_htwd )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print("\nRescaling image size + add padding to the image")
    Visualize.draw_annotation(img, final_ann_di)


    # ----------------------------- < Rescaling image size + cropping the imagee & maintaing the annotation

    wd_ht = (1000,1000)
    crop_rel_pt1_pt2 = ((0.5,0.0), (1.0,0.75))

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)
    # img = ImgTransform.add_relative_padding_to_image(
    #     img, rel_padding_ht_wd=padding_htwd, pad_color=(40,40,40))
    img = ImgTransform.relative_size_based_crop(
        img, rel_pt1=crop_rel_pt1_pt2[0], rel_pt2=crop_rel_pt1_pt2[1])

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco(annotation_path=str(coco_path), coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di, offset=None, rel_crop_pt1_pt2=crop_rel_pt1_pt2 )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print("\nRescaling image size + cropping the image & maintaining the annotation")
    Visualize.draw_annotation(img, final_ann_di)


    # ----------------------------- < Rescaling image size + add padding to the image + cropping the imagee & maintaing the annotation

    wd_ht = (1000,1000)
    padding_htwd = (0.55,0.15)
    crop_rel_pt1_pt2 = ((0.5,0.0), (1.0,0.75))

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)
    img = ImgTransform.add_relative_padding_to_image(
        img, rel_padding_ht_wd=padding_htwd, pad_color=(40,40,40))
    img = ImgTransform.relative_size_based_crop(
        img, rel_pt1=crop_rel_pt1_pt2[0], rel_pt2=crop_rel_pt1_pt2[1])

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di, offset="orig_to_pad", rel_padding_ht_wd=padding_htwd, rel_crop_pt1_pt2=crop_rel_pt1_pt2 )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print("\nRescaling image size + add padding to the image + cropping the imagee & maintaing the annotation")
    Visualize.draw_annotation(img, final_ann_di)

    # ----------------------------------------------------------------------------------------------------------- #

if __name__=='__main__':
    run()
