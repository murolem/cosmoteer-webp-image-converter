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
arg_parser.add_argument("--keep-original", help="If set, the original image file will be kept instead of removing/replacing. In an image is already a .webp file, new image will have a suffix (N) appended.", default=False, action="store_true")
args = arg_parser.parse_args()

images_dirname = "images"
webp_quality = args.q
remove_whitespace = not args.keep_whitespace
keep_original = args.keep_original
resize_image = args.r > 0
resize_image_largest_dimension = args.r
pixel_count_limit_mp = args.mp
pixel_count_limit = pixel_count_limit_mp * 10 ** 6

# source: https://stackoverflow.com/a/10616717
def trim_whitespace(img: Image) -> Image:
    print("Searching for whitespace")

    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        print("Found some whitespace, trimming")
        return img.crop(bbox)
    else:
        return img

def resize_based_on_dimensions(img: Image) -> None:
    print(f"Checking if any image dimension is over the limit of {resize_image_largest_dimension}px")

    largest_dimension = max(img.width, img.height)
    if resize_image_largest_dimension < largest_dimension:
        print("One of the dimensions is larger than the limit, scaling down")
        shrink_factor = resize_image_largest_dimension / largest_dimension
        new_size = [floor(img.width * shrink_factor), floor(img.height * shrink_factor)]
        img.thumbnail(new_size, Image.Resampling.LANCZOS)

def resize_based_on_area(img: Image) -> None:
    print(f"Checking if image area is over the limit of {pixel_count_limit_mp} MP")

    pixels_total = img.width * img.height
    if pixels_total > pixel_count_limit:
        print("Image is over the MP limit, scaling down below the limit")

        shrink_factor = sqrt(pixel_count_limit / pixels_total)
        new_size = [floor(img.width * shrink_factor), floor(img.height * shrink_factor)]
        img.thumbnail(new_size, Image.Resampling.LANCZOS)

def generate_unoccupied_filename(dirpath: str, filename: str) -> str:
    """Given a directory path and a filename, checks if file it points to exist.
    If not, returns the same filename.
    If it does exist, suffixes the filename with `(N)` (before extension). If that exists, increases the N.
    """

    original_filepath = os.path.join(dirpath, filename)
    if not os.path.exists(original_filepath):
        return original_filepath

    filename_pathobj = Path(filename)
    filename_wout_ext = filename_pathobj.stem
    # with dot
    filename_ext = filename_pathobj.suffix
    loop_counter = 1
    while True:
        filename_variant = f"{filename_wout_ext} ({loop_counter}){filename_ext}"
        filepath = os.path.join(dirpath, filename_variant)
        if not os.path.exists(filepath):
            return filename_variant

        loop_counter += 1


def main():
    input_images = listdir(images_dirname)
    input_images = list(filter(lambda x: os.path.isfile(os.path.join(images_dirname, x)) and x != ".gitignore", input_images))

    if len(input_images) == 0:
        print("no image files found")
        return

    for i, input_image_filename in enumerate(input_images):
        print(f"[{i + 1} of {len(input_images)}] processing image: " + input_image_filename)

        input_image_path = os.path.abspath(os.path.join(images_dirname, input_image_filename))

        output_image_filename = Path(input_image_filename).stem + ".webp"
        if keep_original:
            output_image_filename = generate_unoccupied_filename(images_dirname, output_image_filename)
        output_image_path = os.path.abspath(os.path.join(images_dirname, output_image_filename))

        image = Image.open(input_image_path)

        try:
            if remove_whitespace:
                print("Trimming whitespace (if needed)")
                image = trim_whitespace(image)

            if resize_image:
                print("Resizing based on dimensions (if needed)")
                resize_based_on_dimensions(image)

            print("Resizing based on area (if needed)")
            resize_based_on_area(image)

            print(f"Saving as {output_image_filename}")
            webp.save_image(image, output_image_path, quality=webp_quality)

            # if keep original is enabled, keep the file.
            # if source file was a webp image, the new file would have another name (see above)
            if keep_original:
                continue

            # remove input image after conversion (only if it's not a webp image cuz it would have the same name)
            if not input_image_path.lower().endswith("webp"):
                print("Removing original")
                os.remove(input_image_path)
        finally:
            image.close()

    print("all done!")



if __name__ == '__main__':
    main()