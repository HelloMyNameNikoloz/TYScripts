# /resizer/resize.py

import os
from PIL import Image, UnidentifiedImageError, ImageFilter
import io

BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
BRAND_PATH = os.path.join(BASE_DIR, 'brand.png')

MAX_SIZE_MB = 1.75
MAX_SIZE_BYTES = int(MAX_SIZE_MB * 1024 * 1024)

CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080

BRAND_PADDING = 30
BRAND_SCALE = 0.1  # Adjust this to change how big the logo is (as % of canvas width)

def ensure_directories():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_brand_logo():
    if not os.path.exists(BRAND_PATH):
        print("Warning: brand.png not found.")
        return None
    try:
        logo = Image.open(BRAND_PATH).convert("RGBA")
        # Resize based on scale
        target_width = int(CANVAS_WIDTH * BRAND_SCALE)
        ratio = target_width / logo.width
        new_size = (target_width, int(logo.height * ratio))
        logo = logo.resize(new_size, Image.LANCZOS)
        return logo
    except UnidentifiedImageError:
        print("Warning: Could not open brand.png")
        return None

def make_16_9_glow(img):
    img_ratio = img.width / img.height
    target_height = CANVAS_HEIGHT
    target_width = int(img_ratio * target_height)
    img_resized = img.resize((target_width, target_height), Image.LANCZOS)

    # Blurred background
    bg = img_resized.copy().resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=35))

    # Center original image
    result = bg.copy()
    offset_x = (CANVAS_WIDTH - img_resized.width) // 2
    offset_y = (CANVAS_HEIGHT - img_resized.height) // 2
    result.paste(img_resized, (offset_x, offset_y))
    return result

def add_brand_logo(base_img, logo_img):
    if logo_img is None:
        return base_img
    result = base_img.convert("RGBA")
    x = CANVAS_WIDTH - logo_img.width - BRAND_PADDING
    y = CANVAS_HEIGHT - logo_img.height - BRAND_PADDING
    result.paste(logo_img, (x, y), mask=logo_img)
    return result.convert("RGB")

def compress_to_jpeg_with_glow(img_path, brand_logo):
    try:
        img = Image.open(img_path).convert("RGB")
    except UnidentifiedImageError:
        print(f"Warning: Could not open image: {img_path}")
        return None

    img_final = make_16_9_glow(img)
    img_final = add_brand_logo(img_final, brand_logo)

    quality = 95
    step = 5

    while quality >= 20:
        buffer = io.BytesIO()
        img_final.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() <= MAX_SIZE_BYTES:
            return buffer.getvalue()
        quality -= step

    # Fallback
    buffer = io.BytesIO()
    img_final.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()

def main():
    ensure_directories()
    brand_logo = load_brand_logo()
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.png')]
    files.sort()

    for idx, filename in enumerate(files, start=1):
        input_path = os.path.join(INPUT_DIR, filename)
        image_data = compress_to_jpeg_with_glow(input_path, brand_logo)
        if image_data:
            output_filename = f"Thumb-{idx}.jpg"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            with open(output_path, 'wb') as f_out:
                f_out.write(image_data)
            print(f"Saved: {output_filename}")
        else:
            print(f"Skipped: {filename}")

if __name__ == "__main__":
    main()
