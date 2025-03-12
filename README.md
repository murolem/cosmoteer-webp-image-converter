This Python script is used to convert ship images from Cosmoteer.

Features:
- Conversion from PNGs and JPGs to WEBPs
- Removal of extra whitespace.
- Resizing based on largest side.
- Resizing based on amount of pixels (megapixels).

This was made for processing exported ship images from Cosmoteer, but can be used for anything else really.

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

By default, for each image:
- Quality is set to `100`.
- Extra whitespace is trimmed.
- If image is larger than 64 MP, it will be shrunk until it's equal to or below the limit.
- After processing, the original image **is removed**.

If an image is already a webp image, it would be processed anyway.

All of these options are configurable. To see all the options, type:

```bash
python main.py --help
```

All options:
```bash
python main.py -q <integer> -r <integer> --mp <integer> --keep-whitespace --keep-original
```
