This Python script is used to convert PNGs and JPGs to WEBPs, while removing extra whitespace around each image.

This is specifically for processing exported ship images from Cosmoteer.

# Installation

Requires Python 3.

Install dependencies

```bash
pip install -r requirements.txt
```

# Usage

Put images in `images` folder.

Run:

```bash
python main.py
```

This will process all the images, converting them to webp with `90` quality and removing whitespace. Note that original images will be removed.

If an image is already a webp image, it would be processed anyway.

For convenience, both the quality and the whitespace removal options can be configured via arguments. For help, type:

```bash
python main.py --help
```
