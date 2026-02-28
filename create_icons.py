#!/usr/bin/env python3
"""
Generates icon-192.png and icon-512.png for the PWA manifest.
Run once: python create_icons.py
Requires Pillow (already in requirements.txt).
"""
from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), "#3b82f6")   # blue background
    draw = ImageDraw.Draw(img)

    # Draw a simple QR-corner bracket pattern (purely decorative)
    m = size // 10          # margin
    t = size // 14          # stroke thickness
    b = size // 3           # bracket arm length

    def rect(x0, y0, x1, y1):
        draw.rectangle([min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)], fill="white")

    # top-left
    rect(m,        m,        m+b,    m+t)
    rect(m,        m,        m+t,    m+b)
    # top-right
    rect(size-m,   m,        size-m-b, m+t)
    rect(size-m,   m,        size-m-t, m+b)
    # bottom-left
    rect(m,        size-m,   m+b,    size-m-t)
    rect(m,        size-m,   m+t,    size-m-b)
    # bottom-right
    rect(size-m,   size-m,   size-m-b, size-m-t)
    rect(size-m,   size-m,   size-m-t, size-m-b)

    # Central "Q" letter
    font_size = size // 3
    font = None
    for path in ["arialbd.ttf", "arial.ttf", "Arial.ttf",
                 "/System/Library/Fonts/Helvetica.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except (IOError, OSError):
            pass
    if font is None:
        font = ImageFont.load_default()

    label = "Q"
    try:
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        tw, th = draw.textsize(label, font=font)

    draw.text(
        ((size - tw) // 2, (size - th) // 2),
        label, fill="white", font=font
    )
    return img


for sz, name in [(192, "icon-192.png"), (512, "icon-512.png")]:
    path = os.path.join(BASE, name)
    make_icon(sz).save(path, "PNG")
    print(f"  {name}  ({sz}x{sz})  saved")

print("Icons created.")
