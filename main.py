import argparse
import os
from math import floor, sqrt
from os import listdir
from PIL import Image, ImageChops
import webp
from pathlib import Path

arg_parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
arg_parser.add_argument("-q", help="WEBP image quality, from 0 to 100", default=100, type=int)
arg_parser.add_argument("-r", help="Upper bound for any image dimension (width or height). Images with dimensions larger than the limit will be shrunk while preserving aspect-ratio. By default, there's no limit.", default=0, type=int)
arg_parser.add_argument("--mp", help="Upper bound for megapixel size of an image. Images larger than the limit will be shrunk while preserving aspect-ratio.", default=64, type=int)
arg_parser.add_argument("--keep-whitespace", help="If set, no whitespace around images will be removed", default=False, action="store_true")
args = arg_parser.parse_args()

images_dirname = "images"
webp_quality = args.q
remove_whitespace = not args.keep_whitespace
resize_image = args.r > 0
resize_image_largest_dimension = args.r
pixel_count_limit = args.mp * 10 ** 6

# source: https://stackoverflow.com/a/10616717
def trim(img: Image) -> Image:
    print("Trimming whitespace")

    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)
    else:
        return img

def resize(img: Image) -> None:
    print("Resizing enabled, checking if any dimension is larger than the limit")

    largest_dimension = max(img.width, img.height)
    if resize_image_largest_dimension < largest_dimension:
        print("One of the dimensions is larget than the limit, resizing")
        shrink_factor = resize_image_largest_dimension / largest_dimension
        new_size = [floor(img.width * shrink_factor), floor(img.height * shrink_factor)]
        img.thumbnail(new_size, Image.Resampling.LANCZOS)

def resize_if_over_mp_limit(img: Image) -> None:
    print("Checking MP limit")

    pixels_total = img.width * img.height
    if pixels_total > pixel_count_limit:
        print("Resizing due to MP limit")

        shrink_factor = sqrt(pixel_count_limit / pixels_total)
        new_size = [floor(img.width * shrink_factor), floor(img.height * shrink_factor)]
        img.thumbnail(new_size, Image.Resampling.LANCZOS)

def main():
    input_images = listdir(images_dirname)
    input_images = list(filter(lambda x: x != ".gitignore", input_images))

    if len(input_images) == 0:
        print("no image files found")
        return

    for i, image_filename in enumerate(input_images):
        print(f"[{i + 1} of {len(input_images)}] processing image: " + image_filename)

        input_image_path = os.path.join(images_dirname, image_filename)
        output_image_path = os.path.join(images_dirname, Path(image_filename).stem + ".webp")

        image = Image.open(input_image_path)

        if remove_whitespace:
            image = trim(image)

        if resize_image:
            resize(image)

        resize_if_over_mp_limit(image)

        webp.save_image(image, output_image_path, quality=webp_quality)

        # remove input images after conversion.
        # if converting a webp file (same ext before and after), do not delete it.
        if not input_image_path.lower().endswith("webp"):
            os.remove(input_image_path)

    print("all done!")

if __name__ == '__main__':
    main()