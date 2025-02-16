import argparse
import os
from os import listdir
from PIL import Image, ImageChops
import webp
from pathlib import Path

arg_parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
arg_parser.add_argument("-q", help="WEBP image quality, from 0 to 100", default=90, type=int)
arg_parser.add_argument("--keep-whitespace", help="If set, no whitespace around images will be removed", default=False, action="store_true")
args = arg_parser.parse_args()

images_dirname = "images"
webp_quality = args.q
remove_whitespace = not args.keep_whitespace

# source: https://stackoverflow.com/a/10616717
def trim(img):
    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)
    else:
        return img

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

        webp.save_image(image, output_image_path, quality=webp_quality)

        # remove input images after conversion.
        # if converting a webp file (same ext before and after), do not delete it.
        if not input_image_path.lower().endswith("webp"):
            os.remove(input_image_path)

    print("all done!")

if __name__ == '__main__':
    main()