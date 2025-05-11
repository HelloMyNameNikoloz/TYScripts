import os
import io
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

# === CONFIGURATION ===
INPUT_FOLDER = 'images'
OUTPUT_FOLDER = 'output_images'
FONT_PATH = './fonts/ArefRuqaa-Bold.ttf'

# Text settings
#LINE1_TEXT = 'Deutsche Lieder'
LINE1_TEXT = 'Nasheed'
# LINE1_TEXT = 'ბედნიერი ერი'
LINE2_TEXT = 'Playlist'
BASE_FONT_SIZE = 200
LINE_SPACING = 10

# File size thresholds (in bytes)
TWO_MB = 2 * 1024 * 1024            # 2 MB threshold
TARGET_SIZE = int(1.8 * 1024 * 1024)  # target ~1.8 MB

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Helper Functions for Cropping and Saving ---

def crop_to_aspect(image, target_aspect=16/9):
    """Center-crop the input image so its aspect ratio is exactly target_aspect."""
    w, h = image.size
    current_aspect = w / h
    if abs(current_aspect - target_aspect) < 0.01:
        return image
    if current_aspect > target_aspect:
        new_width = int(h * target_aspect)
        left = (w - new_width) // 2
        return image.crop((left, 0, left + new_width, h))
    else:
        new_height = int(w / target_aspect)
        top = (h - new_height) // 2
        return image.crop((0, top, w, top + new_height))

def save_with_max_size(image, output_path, size_threshold=TWO_MB, target_size=TARGET_SIZE, start_quality=95):
    """
    Save the given image (JPEG) to output_path. If the file is larger than size_threshold,
    iteratively reduce JPEG quality until the file size is ≤ target_size.
    Also, disable chroma subsampling (forcing 4:4:4) for crisp edges.
    """
    quality = start_quality
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, subsampling=0, optimize=True)
    file_size = len(buffer.getvalue())
    while file_size > target_size and quality > 10:
        quality -= 5
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, subsampling=0, optimize=True)
        file_size = len(buffer.getvalue())
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())

# --- Helper Functions for Text Rendering ---

def get_text_positions(image_size, text_width, text_height1, text_height2):
    """Calculate positions for line1 and line2 so that the text block is centered."""
    img_w, img_h = image_size
    total_text_height = text_height1 + LINE_SPACING + text_height2
    x = (img_w - text_width) // 2
    y = (img_h - total_text_height) // 2
    return (x, y), (x, y + text_height1 + LINE_SPACING)

def render_text_layer(size, text, font, position, fill):
    """Render the given text onto a transparent RGBA layer."""
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(position, text, font=font, fill=fill)
    return layer

def add_final_crisp_text(composite, pos1, pos2, crisp_color):
    """
    Renders the two lines of text in full opacity (without any blur or composite effects)
    and composites them on top of the given composite image. This guarantees that the final
    text edges are as crisp as possible.
    """
    crisp_layer = Image.new("RGBA", composite.size, (0, 0, 0, 0))
    crisp_layer = Image.alpha_composite(crisp_layer, render_text_layer(composite.size, LINE1_TEXT, font_line1, pos1, crisp_color))
    crisp_layer = Image.alpha_composite(crisp_layer, render_text_layer(composite.size, LINE2_TEXT, font_line2, pos2, crisp_color))
    return Image.alpha_composite(composite, crisp_layer)

# --- Load and Scale Fonts ---
font_line1 = ImageFont.truetype(FONT_PATH, BASE_FONT_SIZE)
dummy_img = Image.new('RGBA', (10, 10))
dummy_draw = ImageDraw.Draw(dummy_img)
bbox1 = dummy_draw.textbbox((0, 0), LINE1_TEXT, font=font_line1)
width1 = bbox1[2] - bbox1[0]
height1 = bbox1[3] - bbox1[1]
temp_font_line2 = ImageFont.truetype(FONT_PATH, BASE_FONT_SIZE)
bbox2 = dummy_draw.textbbox((0, 0), LINE2_TEXT, font=temp_font_line2)
width2 = bbox2[2] - bbox2[0]
scale_factor = width1 / width2 if width2 != 0 else 1
font_line2 = ImageFont.truetype(FONT_PATH, int(BASE_FONT_SIZE * scale_factor))
bbox2 = dummy_draw.textbbox((0, 0), LINE2_TEXT, font=font_line2)
height2 = bbox2[3] - bbox2[1]

# --- DESIGN FUNCTIONS ---
# We are using designs 1, 2, 4, 5, and 7.
# In designs 2, 5, and 7 the outline stroke ranges have been reduced.
# A final crisp text pass is added on top in each design.

# DESIGN 1: Vibrant Drop Shadow + Warm Gradient Overlay
def design_style_1(base_image):
    """Uses a warm red-to-orange gradient, strong drop shadow, and inner glow."""
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    # --- Drop Shadow ---
    shadow_color = (220, 30, 0, 210)  # deep red-orange
    shadow_offset = (10, 10)
    shadow_blur = 12
    shadow_layer = Image.new('RGBA', size, (0, 0, 0, 0))
    s1 = render_text_layer(size, LINE1_TEXT, font_line1, pos1, shadow_color).filter(ImageFilter.GaussianBlur(shadow_blur))
    s2 = render_text_layer(size, LINE2_TEXT, font_line2, pos2, shadow_color).filter(ImageFilter.GaussianBlur(shadow_blur))
    shadow_layer.paste(s1, shadow_offset, s1)
    shadow_layer.paste(s2, shadow_offset, s2)
    overlay = Image.alpha_composite(overlay, shadow_layer)
    
    # --- Gradient Fill (fiery red to warm orange) ---
    text_mask = Image.new('L', size, 0)
    draw_mask = ImageDraw.Draw(text_mask)
    draw_mask.text(pos1, LINE1_TEXT, font=font_line1, fill=255)
    draw_mask.text(pos2, LINE2_TEXT, font=font_line2, fill=255)
    gradient = Image.new('RGBA', size, (0, 0, 0, 0))
    top_color = (255, 20, 0, 255)     # bright red
    bottom_color = (255, 140, 0, 255) # warm orange
    for y in range(size[1]):
        ratio = y / float(size[1])
        r = int(top_color[0]*(1 - ratio) + bottom_color[0]*ratio)
        g = int(top_color[1]*(1 - ratio) + bottom_color[1]*ratio)
        b = int(top_color[2]*(1 - ratio) + bottom_color[2]*ratio)
        for x in range(size[0]):
            gradient.putpixel((x, y), (r, g, b, 255))
    gradient.putalpha(text_mask)
    overlay = Image.alpha_composite(overlay, gradient)
    
    # --- Inner Glow ---
    glow_color = (255, 240, 200, 150)
    glow_offset = (-5, -5)
    glow_blur = 4
    glow_layer = Image.new('RGBA', size, (0, 0, 0, 0))
    g1 = render_text_layer(size, LINE1_TEXT, font_line1, pos1, glow_color).filter(ImageFilter.GaussianBlur(glow_blur))
    g2 = render_text_layer(size, LINE2_TEXT, font_line2, pos2, glow_color).filter(ImageFilter.GaussianBlur(glow_blur))
    glow_layer.paste(g1, glow_offset, g1)
    glow_layer.paste(g2, glow_offset, g2)
    overlay = ImageChops.screen(overlay, glow_layer)
    
    composite = Image.alpha_composite(img, overlay)
    # --- Final Crisp Text Pass (use crisp white for design 1) ---
    return add_final_crisp_text(composite, pos1, pos2, (255, 255, 255, 255))

# DESIGN 2: Electric Neon + Multicolor Outline (Reduced Stroke)
def design_style_2(base_image):
    """
    Creates an electric neon look with a bright cyan glow,
    a thin alternating outline (neon pink / electric blue), and
    vibrant magenta main text.
    """
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    # --- Neon Glow ---
    glow_color = (0, 255, 255, 180)  # bright cyan
    mask1 = Image.new('L', size, 0)
    d1 = ImageDraw.Draw(mask1)
    d1.text(pos1, LINE1_TEXT, font=font_line1, fill=255)
    d1.text(pos2, LINE2_TEXT, font=font_line2, fill=255)
    glow_mask = mask1.filter(ImageFilter.GaussianBlur(12))
    glow_layer = Image.new('RGBA', size, glow_color)
    glow_layer.putalpha(glow_mask)
    overlay = Image.alpha_composite(overlay, glow_layer)
    
    # --- Reduced Stroke Outline (range -2..2) ---
    outline_layer = Image.new('RGBA', size, (0, 0, 0, 0))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            # Alternate between neon pink and electric blue
            color = (255, 20, 147, 255) if (dx + dy) % 2 == 0 else (30, 144, 255, 255)
            t1 = render_text_layer(size, LINE1_TEXT, font_line1, (pos1[0] + dx, pos1[1] + dy), color)
            t2 = render_text_layer(size, LINE2_TEXT, font_line2, (pos2[0] + dx, pos2[1] + dy), color)
            outline_layer = Image.alpha_composite(outline_layer, t1)
            outline_layer = Image.alpha_composite(outline_layer, t2)
    overlay = Image.alpha_composite(overlay, outline_layer)
    
    # --- Main Neon Text ---
    neon_text_color = (255, 0, 255, 255)  # vibrant magenta
    main_text_layer = render_text_layer(size, LINE1_TEXT, font_line1, pos1, neon_text_color)
    main_text_layer = Image.alpha_composite(main_text_layer, render_text_layer(size, LINE2_TEXT, font_line2, pos2, neon_text_color))
    overlay = Image.alpha_composite(overlay, main_text_layer)
    
    composite = Image.alpha_composite(img, overlay)
    # --- Final Crisp Text Pass (use vibrant magenta for design 2) ---
    return add_final_crisp_text(composite, pos1, pos2, (255, 0, 255, 255))

# DESIGN 4: Double Drop Shadow + Expressive Overlay (No Stroke)
def design_style_4(base_image):
    """
    Combines two layers of colored shadows (blue & magenta) and then overlays
    a bold turquoise text render.
    """
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    # --- First Shadow (Blue) ---
    shadow1_color = (0, 100, 255, 200)
    shadow1_offset = (12, 12)
    shadow1_blur = 10
    layer1 = Image.new('RGBA', size, (0, 0, 0, 0))
    t1 = render_text_layer(size, LINE1_TEXT, font_line1, pos1, shadow1_color).filter(ImageFilter.GaussianBlur(shadow1_blur))
    t2 = render_text_layer(size, LINE2_TEXT, font_line2, pos2, shadow1_color).filter(ImageFilter.GaussianBlur(shadow1_blur))
    layer1.paste(t1, shadow1_offset, t1)
    layer1.paste(t2, shadow1_offset, t2)
    overlay = Image.alpha_composite(overlay, layer1)
    
    # --- Second Shadow (Magenta) ---
    shadow2_color = (255, 0, 128, 220)
    shadow2_offset = (5, 5)
    shadow2_blur = 4
    layer2 = Image.new('RGBA', size, (0, 0, 0, 0))
    t1 = render_text_layer(size, LINE1_TEXT, font_line1, pos1, shadow2_color).filter(ImageFilter.GaussianBlur(shadow2_blur))
    t2 = render_text_layer(size, LINE2_TEXT, font_line2, pos2, shadow2_color).filter(ImageFilter.GaussianBlur(shadow2_blur))
    layer2.paste(t1, shadow2_offset, t1)
    layer2.paste(t2, shadow2_offset, t2)
    overlay = Image.alpha_composite(overlay, layer2)
    
    # --- Expressive Overlay (Turquoise) ---
    overlay_color = (64, 224, 208, 240)
    main_layer = render_text_layer(size, LINE1_TEXT, font_line1, pos1, overlay_color)
    main_layer = Image.alpha_composite(main_layer, render_text_layer(size, LINE2_TEXT, font_line2, pos2, overlay_color))
    overlay = Image.alpha_composite(overlay, main_layer)
    
    composite = Image.alpha_composite(img, overlay)
    # --- Final Crisp Text Pass (use bold turquoise for design 4) ---
    return add_final_crisp_text(composite, pos1, pos2, (64, 224, 208, 255))

# DESIGN 5: Bold Expressive Outline + Patterned Fill (Reduced Stroke)
def design_style_5(base_image):
    """
    Uses a bold violet outline (with reduced stroke thickness) and a dotted
    patterned fill in rich gold-yellow.
    """
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    # --- Bold Outline (range -2..2) ---
    outline_color = (138, 43, 226, 255)  # vivid violet
    outline_layer = Image.new('RGBA', size, (0, 0, 0, 0))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            t1 = render_text_layer(size, LINE1_TEXT, font_line1, (pos1[0] + dx, pos1[1] + dy), outline_color)
            t2 = render_text_layer(size, LINE2_TEXT, font_line2, (pos2[0] + dx, pos2[1] + dy), outline_color)
            outline_layer = Image.alpha_composite(outline_layer, t1)
            outline_layer = Image.alpha_composite(outline_layer, t2)
    overlay = Image.alpha_composite(overlay, outline_layer)
    
    # --- Patterned Fill (dotted noise in bright gold) ---
    fill_color = (255, 215, 0, 255)  # rich gold-yellow
    fill_layer = Image.new('RGBA', size, fill_color)
    text_mask = Image.new('L', size, 0)
    d = ImageDraw.Draw(text_mask)
    d.text(pos1, LINE1_TEXT, font=font_line1, fill=255)
    d.text(pos2, LINE2_TEXT, font=font_line2, fill=255)
    pattern = Image.new('L', size, 0)
    dp = ImageDraw.Draw(pattern)
    for x in range(0, size[0], 6):
        for y in range(0, size[1], 6):
            if random.random() < 0.5:
                dp.ellipse((x, y, x + 2, y + 2), fill=255)
    patterned_mask = ImageChops.multiply(text_mask, pattern)
    fill_layer.putalpha(patterned_mask)
    overlay = Image.alpha_composite(overlay, fill_layer)
    
    composite = Image.alpha_composite(img, overlay)
    # --- Final Crisp Text Pass (use bright gold for design 5) ---
    return add_final_crisp_text(composite, pos1, pos2, (255, 215, 0, 255))


from PIL import Image, ImageFilter, ImageChops, ImageDraw


from PIL import Image, ImageFilter, ImageChops, ImageDraw


def design_style_clickbait_neon(base_image):
    """
    Clickbait neon style: multi-layered pulsating neon glows + subtle lens flare spots.
    """
    img = base_image.copy()
    size = img.size
    # Determine text positions
    pos1, pos2 = get_text_positions(size, width1, height1, height2)

    # Measure text extents for flare placement using font masks
    mask1 = font_line1.getmask(LINE1_TEXT)
    w1, h1 = mask1.size
    mask2 = font_line2.getmask(LINE2_TEXT)
    w2, h2 = mask2.size

    overlay = Image.new('RGBA', size, (0, 0, 0, 0))

    # --- Multi-layered Neon Glows ---
    neon_layers = [
        {'color': (255,   0, 255, 150), 'blur': 8,  'offset': (0, 0)},   # Hot pink core glow
        {'color': (  0, 255, 255, 120), 'blur': 16, 'offset': (3, 3)},   # Electric cyan outer glow
    ]
    for layer in neon_layers:
        glow = Image.new('RGBA', size, (0, 0, 0, 0))
        # Render text in neon color
        t1 = render_text_layer(size, LINE1_TEXT, font_line1, pos1, layer['color'])
        t2 = render_text_layer(size, LINE2_TEXT, font_line2, pos2, layer['color'])
        glow = Image.alpha_composite(t1, t2)
        # Blur and offset for depth
        glow = glow.filter(ImageFilter.GaussianBlur(layer['blur']))
        glow = ImageChops.offset(glow, *layer['offset'])
        overlay = Image.alpha_composite(overlay, glow)

    # --- Subtle Lens Flares ---
    flare_layer = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(flare_layer)
    # place flare at start of LINE1 and end of LINE2
    flare_points = [pos1, (pos2[0] + w2, pos2[1])]
    for (x, y) in flare_points:
        for radius, alpha in [(5,  60), (15, 30), (30, 10)]:
            bbox = (x - radius, y - radius, x + radius, y + radius)
            draw.ellipse(bbox, fill=(255, 255, 255, alpha))
    # soften flares
    flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(5))
    # additive blend for bright spots
    overlay = ImageChops.add(overlay, flare_layer)

    # Composite and finalize with crisp text outline
    composite = Image.alpha_composite(img, overlay)
    # Use existing outline color for final text pass
    outline_color = (255, 165, 0, 255)
    return add_final_crisp_text(composite, pos1, pos2, outline_color)



# 11-15designs

# DESIGN 11: Georgian Gold Relief
def design_style_11(base_image):
    """Traditional gold text with deep red outline and subtle stone texture"""
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0,0,0,0))
    
    # Deep red shadow (3D effect)
    for i in range(1, 4):
        shadow = render_text_layer(size, LINE1_TEXT, font_line1, 
                                 (pos1[0]+i, pos1[1]+i), (94, 38, 18, 150))
        shadow = Image.alpha_composite(shadow, 
                  render_text_layer(size, LINE2_TEXT, font_line2, 
                                  (pos2[0]+i, pos2[1]+i), (94, 38, 18, 150)))
        overlay = Image.alpha_composite(overlay, shadow)
    
    # Gold text with bevel
    text_layer = render_text_layer(size, LINE1_TEXT, font_line1, pos1, (207, 181, 59, 255))
    text_layer = Image.alpha_composite(text_layer, 
                 render_text_layer(size, LINE2_TEXT, font_line2, pos2, (207, 181, 59, 255)))
    
    # Highlight (NW) and shadow (SE)
    highlight = render_text_layer(size, LINE1_TEXT, font_line1, 
                                (pos1[0]-1, pos1[1]-1), (255, 246, 193, 100))
    highlight = Image.alpha_composite(highlight, 
                 render_text_layer(size, LINE2_TEXT, font_line2, 
                                 (pos2[0]-1, pos2[1]-1), (255, 246, 193, 100)))
    
    shadow = render_text_layer(size, LINE1_TEXT, font_line1, 
                             (pos1[0]+1, pos1[1]+1), (64, 28, 14, 100))
    shadow = Image.alpha_composite(shadow, 
              render_text_layer(size, LINE2_TEXT, font_line2, 
                              (pos2[0]+1, pos2[1]+1), (64, 28, 14, 100)))
    
    overlay = Image.alpha_composite(overlay, highlight)
    overlay = Image.alpha_composite(overlay, shadow)
    overlay = Image.alpha_composite(overlay, text_layer)
    
    return Image.alpha_composite(img, overlay)

# DESIGN 12: Wine Red Emboss
def design_style_12(base_image):
    """Deep wine color with dual-tone embossing"""
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0,0,0,0))
    
    # Base wine color
    base = render_text_layer(size, LINE1_TEXT, font_line1, pos1, (86, 47, 14, 255))
    base = Image.alpha_composite(base, 
           render_text_layer(size, LINE2_TEXT, font_line2, pos2, (86, 47, 14, 255)))
    
    # Emboss effect
    highlight = render_text_layer(size, LINE1_TEXT, font_line1, 
                                (pos1[0]-2, pos1[1]-2), (170, 111, 115, 150))
    highlight = Image.alpha_composite(highlight, 
                 render_text_layer(size, LINE2_TEXT, font_line2, 
                                 (pos2[0]-2, pos2[1]-2), (170, 111, 115, 150)))
    
    shadow = render_text_layer(size, LINE1_TEXT, font_line1, 
                             (pos1[0]+2, pos1[1]+2), (45, 25, 6, 150))
    shadow = Image.alpha_composite(shadow, 
              render_text_layer(size, LINE2_TEXT, font_line2, 
                              (pos2[0]+2, pos2[1]+2), (45, 25, 6, 150)))
    
    overlay = Image.alpha_composite(overlay, shadow)
    overlay = Image.alpha_composite(overlay, highlight)
    overlay = Image.alpha_composite(overlay, base)
    
    # Vine pattern overlay
    vine_pattern = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(vine_pattern)
    for x in range(0, size[0], 50):
        draw.line((x,0,x,size[1]), fill=(34,139,34,30), width=2)
    overlay = Image.alpha_composite(overlay, vine_pattern)
    
    return Image.alpha_composite(img, overlay)

# DESIGN 13: Stone Carved
def design_style_13(base_image):
    """Simulates stone-carved text with moss accents"""
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0,0,0,0))
    
    # Deep shadow
    shadow = render_text_layer(size, LINE1_TEXT, font_line1, 
                             (pos1[0]+3, pos1[1]+3), (58, 58, 58, 150))
    shadow = Image.alpha_composite(shadow, 
              render_text_layer(size, LINE2_TEXT, font_line2, 
                              (pos2[0]+3, pos2[1]+3), (58, 58, 58, 150)))
    
    # Base stone color
    base = render_text_layer(size, LINE1_TEXT, font_line1, pos1, (169,169,169,255))
    base = Image.alpha_composite(base, 
           render_text_layer(size, LINE2_TEXT, font_line2, pos2, (169,169,169,255)))
    
    # Moss accents
    moss = render_text_layer(size, LINE1_TEXT, font_line1, 
                           (pos1[0]-1, pos1[1]), (34,139,34,80))
    moss = Image.alpha_composite(moss, 
           render_text_layer(size, LINE2_TEXT, font_line2, 
                            (pos2[0]-1, pos2[1]), (34,139,34,80)))
    
    overlay = Image.alpha_composite(overlay, shadow)
    overlay = Image.alpha_composite(overlay, base)
    overlay = Image.alpha_composite(overlay, moss)
    
    return Image.alpha_composite(img, overlay)

# DESIGN 14: Enamel Blue
def design_style_14(base_image):
    """Traditional Georgian enamel blue with gold outline"""
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0,0,0,0))
    
    # Outer glow
    for i in range(5, 0, -1):
        glow = render_text_layer(size, LINE1_TEXT, font_line1, pos1, (13, 71, 161, 20*i))
        glow = Image.alpha_composite(glow, 
               render_text_layer(size, LINE2_TEXT, font_line2, pos2, (13, 71, 161, 20*i)))
        overlay = Image.alpha_composite(overlay, glow.filter(ImageFilter.GaussianBlur(i*2)))
    
    # Gold outline
    for dx, dy in [(-1,-1),(1,1)]:
        outline = render_text_layer(size, LINE1_TEXT, font_line1, 
                                  (pos1[0]+dx, pos1[1]+dy), (207, 181, 59, 200))
        outline = Image.alpha_composite(outline, 
                  render_text_layer(size, LINE2_TEXT, font_line2, 
                                  (pos2[0]+dx, pos2[1]+dy), (207, 181, 59, 200)))
        overlay = Image.alpha_composite(overlay, outline)
    
    # Blue base
    base = render_text_layer(size, LINE1_TEXT, font_line1, pos1, (13, 71, 161, 255))
    base = Image.alpha_composite(base, 
           render_text_layer(size, LINE2_TEXT, font_line2, pos2, (13, 71, 161, 255)))
    
    overlay = Image.alpha_composite(overlay, base)
    return Image.alpha_composite(img, overlay)

# DESIGN 15: Rustic Iron
def design_style_15(base_image):
    """Aged iron look with oxidation effects"""
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0,0,0,0))
    
    # Base iron color
    base = render_text_layer(size, LINE1_TEXT, font_line1, pos1, (112, 128, 144, 255))
    base = Image.alpha_composite(base, 
           render_text_layer(size, LINE2_TEXT, font_line2, pos2, (112, 128, 144, 255)))
    
    # Rust effect
    rust = render_text_layer(size, LINE1_TEXT, font_line1, 
                           (pos1[0]+1, pos1[1]), (178, 34, 34, 150))
    rust = Image.alpha_composite(rust, 
           render_text_layer(size, LINE2_TEXT, font_line2, 
                            (pos2[0]+1, pos2[1]), (178, 34, 34, 150)))
    
    # Metallic highlights
    highlight = render_text_layer(size, LINE1_TEXT, font_line1, 
                                (pos1[0]-1, pos1[1]-1), (169, 169, 169, 100))
    highlight = Image.alpha_composite(highlight, 
                 render_text_layer(size, LINE2_TEXT, font_line2, 
                                 (pos2[0]-1, pos2[1]-1), (169, 169, 169, 100)))
    
    overlay = Image.alpha_composite(overlay, base)
    overlay = Image.alpha_composite(overlay, rust)
    overlay = Image.alpha_composite(overlay, highlight)
    
    return Image.alpha_composite(img, overlay)

def design_style_16(base_image):
    """
    "Georgian Depth" - Wine-red text with black glow and gold accents
    """
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    
    # --- Black Outer Glow System ---
    glow_params = [
        (30, 8, 2, 2),  # (opacity, blur, x_offset, y_offset)
        (50, 5, 1, 1),
        (70, 3, 0, 0)
    ]
    for opacity, blur, dx, dy in glow_params:
        glow = render_text_layer(size, LINE1_TEXT, font_line1, 
                               (pos1[0]+dx, pos1[1]+dy), (0, 0, 0, opacity))
        glow = Image.alpha_composite(glow, 
               render_text_layer(size, LINE2_TEXT, font_line2, 
                               (pos2[0]+dx, pos2[1]+dy), (0, 0, 0, opacity)))
        overlay = Image.alpha_composite(overlay, glow.filter(ImageFilter.GaussianBlur(blur)))
    
    # --- Gold Bevel Effect ---
    # Bottom-right highlight
    highlight = render_text_layer(size, LINE1_TEXT, font_line1, 
                                (pos1[0]+1, pos1[1]+1), (207, 181, 59, 150))
    highlight = Image.alpha_composite(highlight, 
                 render_text_layer(size, LINE2_TEXT, font_line2, 
                                 (pos2[0]+1, pos2[1]+1), (207, 181, 59, 150)))
    
    # Top-left accent
    accent = render_text_layer(size, LINE1_TEXT, font_line1, 
                             (pos1[0]-1, pos1[1]-1), (255, 246, 193, 80))
    accent = Image.alpha_composite(accent, 
              render_text_layer(size, LINE2_TEXT, font_line2, 
                              (pos2[0]-1, pos2[1]-1), (255, 246, 193, 80)))
    
    # --- Main Text ---
    main_color = (198, 43, 34, 255)  # Traditional Georgian red
    main_text = render_text_layer(size, LINE1_TEXT, font_line1, pos1, main_color)
    main_text = Image.alpha_composite(main_text, 
                 render_text_layer(size, LINE2_TEXT, font_line2, pos2, main_color))
    
    # Composite elements
    overlay = Image.alpha_composite(overlay, highlight)
    overlay = Image.alpha_composite(overlay, accent)
    overlay = Image.alpha_composite(overlay, main_text)
    
    return Image.alpha_composite(img, overlay)

def render_text_mask(size, pos1, pos2):
    """Create text shape mask for effects"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.text(pos1, LINE1_TEXT, font=font_line1, fill=255)
    draw.text(pos2, LINE2_TEXT, font=font_line2, fill=255)
    return mask

def design_style_17(base_image):
    """
    Ultra-premium design with refined layered metallic gold effects.
    
    This version features:
      - A subtle base texture overlay.
      - A gentle 3D engraving shadow effect.
      - A refined gold foil text fill via a radial gradient.
      - A light micro-embossing for fine detail.
      - A final crisp text overlay.
    """
    img = base_image.copy()
    size = img.size
    pos1, pos2 = get_text_positions(size, width1, height1, height2)
    
    # Start with a transparent overlay
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    
    # 1. Subtle Base Texture
    # A very light textured base to add depth without distraction.
    subtle_texture = Image.new('RGBA', size, (245, 240, 230, 60))  # nearly transparent warm tone
    overlay = Image.alpha_composite(overlay, subtle_texture)
    
    # 2. Refined 3D Engraving Effect (Subtle Drop Shadows)
    # Use very light shadows with small offsets for an embossed look.
    for i in range(1, 3):  # Two iterations for a subtle multi-layered shadow
        offset = (i, i)
        shadow_color = (0, 0, 0, 80)  # soft black shadow
        shadow_layer1 = render_text_layer(size, LINE1_TEXT, font_line1, (pos1[0] + offset[0], pos1[1] + offset[1]), shadow_color)
        shadow_layer2 = render_text_layer(size, LINE2_TEXT, font_line2, (pos2[0] + offset[0], pos2[1] + offset[1]), shadow_color)
        shadow_combined = Image.alpha_composite(shadow_layer1, shadow_layer2)
        # Apply a gentle blur that increases with each iteration for extra smoothness.
        blurred_shadow = shadow_combined.filter(ImageFilter.GaussianBlur(3 * i))
        overlay = Image.alpha_composite(overlay, blurred_shadow)
    
    # 3. Gold Foil Text Fill
    # Create a radial gradient, colorize it to gold, then mask it with the text shape.
    gold_gradient = Image.radial_gradient('L').resize(size)
    gold_layer = ImageOps.colorize(
        gold_gradient,
        (150, 130, 0),   # darker gold tone
        (255, 215, 0)    # bright, premium gold tone
    )
    text_mask = render_text_mask(size, pos1, pos2)
    gold_layer.putalpha(text_mask)
    overlay = Image.alpha_composite(overlay, gold_layer)
    
    # 4. Light Micro-Embossing (Optional, for fine engraved detail)
    emboss_kernel = ImageFilter.Kernel(
        (3, 3),
        [-1, -1, 0,
         -1,  1, 1,
          0,  1, 1],
        scale=1
    )
    emboss_layer1 = render_text_layer(size, LINE1_TEXT, font_line1, pos1, (255, 255, 255, 20))
    emboss_layer2 = render_text_layer(size, LINE2_TEXT, font_line2, pos2, (255, 255, 255, 20))
    emboss_layer = Image.alpha_composite(emboss_layer1, emboss_layer2)
    emboss_layer = emboss_layer.filter(emboss_kernel)
    overlay = Image.alpha_composite(overlay, emboss_layer)
    
    # 5. Final Crisp Text Pass
    # This final pass renders sharp edges over the composite for maximum clarity.
    composite = Image.alpha_composite(img, overlay)
    crisp_gold = (255, 215, 0, 255)  # use the refined gold for the crisp overlay
    composite = add_final_crisp_text(composite, pos1, pos2, crisp_gold)
    
    return composite


def add_vignette(image):
    """Apply 16:9 oval-shaped black gradient overlay"""
    width, height = image.size
    vignette = Image.new('RGBA', (width, height))
    
    # Create gradient mask with 16:9 aspect ellipse
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Calculate 16:9 ellipse dimensions
    ellipse_width = width * 0.5  # 80% of image width
    ellipse_height = ellipse_width * (9/16)  # Maintain 16:9 aspect
    
    ellipse_box = [
        (width - ellipse_width)/2,  # Left
        (height - ellipse_height)/2,  # Top
        (width + ellipse_width)/2,  # Right
        (height + ellipse_height)/2  # Bottom
    ]
    
    draw.ellipse(ellipse_box, fill=255)
    
    # Apply blur proportional to image size
    blur_radius = max(width, height) // 10
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Create black overlay using the mask
    vignette.paste((0, 0, 0, 180), mask=mask)
    
    return Image.alpha_composite(image, vignette)

# --- Modified Main Loop ---
def main():
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    designs = [
        design_style_2,
        design_style_5,
        design_style_clickbait_neon
    ]
    
    for index, filename in enumerate(files, start=1):
        input_path = os.path.join(INPUT_FOLDER, filename)
        base_image = Image.open(input_path).convert('RGBA')
        
        # Preprocessing steps
        base_image = crop_to_aspect(base_image, target_aspect=16/9)
        base_image = add_vignette(base_image)  # Apply vignette to all images
        
        for style_index, design in enumerate(designs, start=1):
            result = design(base_image)  # Designs get vignetted image
            output_filename = f"image-{index}-{style_index}.jpg"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            final_image = result.convert('RGB')
            save_with_max_size(final_image, output_path)
            print(f"Saved: {output_filename}")

if __name__ == "__main__":
    main()
