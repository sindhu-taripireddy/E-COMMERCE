import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PRODUCT_DIR = BASE_DIR / "static" / "images" / "products"
LOGO_DIR = BASE_DIR / "static" / "images" / "logo"

PRODUCT_DIR.mkdir(parents=True, exist_ok=True)
LOGO_DIR.mkdir(parents=True, exist_ok=True)

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def create_gradient_background(width, height, top_color, bottom_color):
    base = Image.new('RGB', (width, height), top_color)
    top_rgb = hex_to_rgb(top_color)
    bottom_rgb = hex_to_rgb(bottom_color)
    
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(top_rgb[0] * (1 - ratio) + bottom_rgb[0] * ratio)
        g = int(top_rgb[1] * (1 - ratio) + bottom_rgb[1] * ratio)
        b = int(top_rgb[2] * (1 - ratio) + bottom_rgb[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base

def draw_luxury_bangles(draw, cx, cy, radius, primary_color, accent_color, count=5):
    # Draw stacked bangles with 3D depth and shimmer
    p_rgb = hex_to_rgb(primary_color)
    a_rgb = hex_to_rgb(accent_color)
    gold = (212, 175, 55)
    
    offset_step = 16
    start_y = cy - (count * offset_step) // 2
    
    for i in range(count):
        y = start_y + i * offset_step
        rx = radius + (i % 2) * 6
        ry = radius // 2.6
        
        # Outer shadow
        draw.ellipse([cx - rx - 2, y - ry - 2, cx + rx + 2, y + ry + 2], outline=(30, 15, 20), width=4)
        # Main bangle ring
        color = p_rgb if i % 2 == 0 else a_rgb
        draw.ellipse([cx - rx, y - ry, cx + rx, y + ry], outline=color, width=14)
        # Inner silk texture line
        draw.ellipse([cx - rx + 3, y - ry + 3, cx + rx - 3, y + ry - 3], outline=gold, width=2)
        # Kundan / pearl dots along top rim
        for dot_angle in range(-120, -60, 15):
            import math
            rad = math.radians(dot_angle)
            dx = cx + int((rx - 4) * math.cos(rad))
            dy = y + int((ry - 4) * math.sin(rad))
            draw.ellipse([dx-3, dy-3, dx+3, dy+3], fill=(255, 255, 255), outline=gold)

def draw_luxury_earrings(draw, cx, cy, primary_color, accent_color):
    p_rgb = hex_to_rgb(primary_color)
    gold = (212, 175, 55)
    
    # Left and right jhumkas
    for sign in [-1, 1]:
        ex = cx + sign * 90
        # Stud at top
        draw.ellipse([ex - 22, cy - 110, ex + 22, cy - 66], fill=p_rgb, outline=gold, width=3)
        draw.ellipse([ex - 10, cy - 98, ex + 10, cy - 78], fill=(255, 255, 255), outline=gold, width=2)
        
        # Connecting loop
        draw.line([(ex, cy - 66), (ex, cy - 40)], fill=gold, width=4)
        
        # Bell-shaped Jhumka dome
        dome_w = 60
        dome_h = 45
        draw.chord([ex - dome_w, cy - 40, ex + dome_w, cy + dome_h], 180, 360, fill=p_rgb, outline=gold, width=4)
        
        # Bell rim
        draw.rectangle([ex - dome_w, cy + 2, ex + dome_w, cy + 14], fill=gold)
        
        # Hanging pearl tassels
        for tassel_x in range(ex - 45, ex + 55, 15):
            draw.line([(tassel_x, cy + 14), (tassel_x, cy + 40)], fill=gold, width=2)
            draw.ellipse([tassel_x - 5, cy + 38, tassel_x + 5, cy + 48], fill=(255, 255, 250), outline=gold)

def draw_invisible_chain(draw, cx, cy, accent_color):
    # Delicate translucent cord with sparkling pendant
    cord_color = (200, 200, 220)
    gold = (212, 175, 55)
    
    # Curved nylon cord
    draw.arc([cx - 150, cy - 160, cx + 150, cy + 80], 30, 150, fill=cord_color, width=2)
    
    # Floating pendant mount
    py = cy + 70
    draw.ellipse([py - 4, py - 12, py + 4, py - 4], fill=gold)
    
    # Sparkling Solitaire / Teardrop Crystal
    draw.polygon([(cx, py - 6), (cx + 26, py + 24), (cx, py + 56), (cx - 26, py + 24)], 
                 fill=(245, 250, 255), outline=gold)
    # Facet lines
    draw.polygon([(cx, py + 4), (cx + 14, py + 24), (cx, py + 44), (cx - 14, py + 24)], 
                 fill=(255, 255, 255), outline=(180, 210, 240))
    # Sparkle rays
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        import math
        rad = math.radians(angle)
        sx = cx + int(38 * math.cos(rad))
        sy = (py + 24) + int(38 * math.sin(rad))
        draw.line([(cx, py + 24), (sx, sy)], fill=(255, 255, 220), width=1)

def draw_combo_set(draw, cx, cy, primary_color, accent_color):
    # Combines mini bangles, jhumka, and necklace
    draw_luxury_bangles(draw, cx - 70, cy + 40, 75, primary_color, accent_color, count=3)
    
    # Mini jhumka on right
    p_rgb = hex_to_rgb(primary_color)
    gold = (212, 175, 55)
    ex = cx + 90
    draw.ellipse([ex - 15, cy - 60, ex + 15, cy - 30], fill=p_rgb, outline=gold, width=2)
    draw.chord([ex - 40, cy - 25, ex + 40, cy + 30], 180, 360, fill=p_rgb, outline=gold, width=3)
    draw.rectangle([ex - 40, cy + 2, ex + 40, cy + 10], fill=gold)
    for tx in range(ex - 30, ex + 40, 15):
        draw.ellipse([tx - 4, cy + 18, tx + 4, cy + 26], fill=(255, 255, 255), outline=gold)
        
    # Floating mini pendant
    draw_invisible_chain(draw, cx, cy - 60, accent_color)

def generate_product_image(filename, category_type, title, primary_color, accent_color, subtitle):
    w, h = 600, 600
    # Elegant champagne / royal studio backdrop
    bg = create_gradient_background(w, h, "#1F0B12", "#0A0306")
    draw = ImageDraw.Draw(bg)
    
    # Subtle inner decorative border
    gold = (212, 175, 55)
    draw.rectangle([20, 20, w - 20, h - 20], outline=(80, 50, 35), width=1)
    draw.rectangle([26, 26, w - 26, h - 26], outline=(150, 115, 60), width=1)
    
    # Corner ornaments
    for x, y in [(26, 26), (w-26, 26), (26, h-26), (w-26, h-26)]:
        draw.ellipse([x-4, y-4, x+4, y+4], fill=gold)
        
    cx, cy = w // 2, h // 2 - 25
    
    if category_type == "bangles":
        draw_luxury_bangles(draw, cx, cy, 110, primary_color, accent_color, count=6)
    elif category_type == "earrings":
        draw_luxury_earrings(draw, cx, cy, primary_color, accent_color)
    elif category_type == "chains":
        draw_invisible_chain(draw, cx, cy, accent_color)
    elif category_type == "combo":
        draw_combo_set(draw, cx, cy, primary_color, accent_color)
    else:
        draw_luxury_bangles(draw, cx, cy, 100, primary_color, accent_color, count=4)
        
    # Brand watermark & title banner at bottom
    draw.rectangle([0, h - 100, w, h], fill=(15, 6, 9))
    draw.line([(0, h - 100), (w, h - 100)], fill=gold, width=2)
    
    # Text
    draw.text((w // 2, h - 75), title.upper(), fill=(250, 240, 220), anchor="mm")
    draw.text((w // 2, h - 45), f"KK_COLLECTIONS • {subtitle}".upper(), fill=(197, 160, 89), anchor="mm")
    draw.text((w // 2, h - 22), "Elegance That Completes You", fill=(140, 120, 100), anchor="mm")
    
    # Top badge
    draw.rectangle([w // 2 - 80, 12, w // 2 + 80, 38], fill=(91, 20, 38), outline=gold, width=1)
    draw.text((w // 2, 25), "HANDCRAFTED", fill=(245, 230, 200), anchor="mm")
    
    out_path = PRODUCT_DIR / filename
    bg.save(out_path, "JPEG", quality=92)
    print(f"Generated {out_path.name}")

def generate_logo():
    w, h = 400, 120
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    gold = (197, 160, 89)
    cream = (253, 251, 247)
    
    # Draw KK Monogram Crest
    draw.ellipse([30, 20, 100, 90], outline=gold, width=2)
    draw.text((65, 55), "KK", fill=gold, anchor="mm")
    
    # Brand Name
    draw.text((120, 42), "KK_COLLECTIONS", fill=cream, anchor="lm")
    draw.text((120, 72), "Elegance That Completes You", fill=gold, anchor="lm")
    
    logo_path = LOGO_DIR / "logo.png"
    im.save(logo_path, "PNG")
    print("Generated logo.png")

if __name__ == "__main__":
    generate_logo()
    
    products_to_gen = [
        # Thread Bangles
        ("bangles_thread_red.jpg", "bangles", "Classic Silk Thread Bangles", "#961C2C", "#D4AF37", "Silk Thread Set"),
        ("bangles_thread_pink.jpg", "bangles", "Rani Pink Thread Bangles", "#D63384", "#F8B4D9", "Festive Edition"),
        ("bangles_thread_green.jpg", "bangles", "Emerald Green Silk Bangles", "#198754", "#C5A059", "Traditional Style"),
        ("bangles_thread_blue.jpg", "bangles", "Royal Blue Kundan Bangles", "#0D6EFD", "#E0C27B", "Party Wear"),
        ("bangles_thread_gold.jpg", "bangles", "Golden Velvet Thread Bangles", "#D4AF37", "#FFFFFF", "Handmade Craft"),
        ("bangles_designer_kundan.jpg", "bangles", "Designer Kundan Chura Set", "#8B1E3F", "#E9D8A6", "Bridal Chura"),
        ("bangles_traditional_matte.jpg", "bangles", "Traditional Antique Gold Bangles", "#B8860B", "#FFE4B5", "Temple Jewelry"),
        ("bangles_bridal_heavy.jpg", "bangles", "Royal Bridal Chura & Latkan", "#800020", "#FFD700", "Bridal Luxury"),
        
        # Earrings
        ("earrings_thread_jhumka_pink.jpg", "earrings", "Pink Silk Thread Jhumkas", "#D63384", "#FFFFFF", "Handmade Pearls"),
        ("earrings_thread_jhumka_green.jpg", "earrings", "Emerald Green Thread Jhumkas", "#0F5132", "#FFD700", "Festive Glam"),
        ("earrings_traditional_temple.jpg", "earrings", "Traditional Antique Jhumkas", "#C5A059", "#8B0000", "Heritage Craft"),
        ("earrings_designer_cz.jpg", "earrings", "Designer Crystal Drop Earrings", "#3A0CA3", "#E2E8F0", "Party Glam"),
        ("earrings_bridal_chandbali.jpg", "earrings", "Royal Bridal Chandbali Earrings", "#800020", "#FFD700", "Kundan & Pearls"),
        ("earrings_thread_studs_yellow.jpg", "earrings", "Haldi Floral Thread Studs", "#E0A96D", "#FFF3CD", "Haldi Special"),
        
        # Chains
        ("chains_invisible_crystal.jpg", "chains", "Solitaire Invisible Crystal Chain", "#E2E8F0", "#FFFFFF", "Minimalist Elegance"),
        ("chains_invisible_pearl.jpg", "chains", "Floating Pearl Invisible Chain", "#F8F9FA", "#C5A059", "Subtle Beauty"),
        ("chains_pendant_rosegold.jpg", "chains", "Rose Gold Teardrop Pendant Chain", "#B76E79", "#FFD1DC", "Daily Wear"),
        ("chains_traditional_pendant.jpg", "chains", "Antique Gold Floral Pendant Chain", "#C5A059", "#5B1426", "Traditional Touch"),
        
        # Collections & Combos
        ("combo_bridal_set.jpg", "combo", "Royal Bridal Complete Combo Set", "#800020", "#D4AF37", "Bangles + Earrings + Chain"),
        ("combo_festive_pink.jpg", "combo", "Rani Pink Festive Matching Combo", "#D63384", "#FFF", "Set of 3"),
        ("combo_haldi_yellow.jpg", "combo", "Golden Haldi Special Set", "#FFC107", "#FFF3CD", "Bangles & Jhumka")
    ]
    
    for filename, cat, title, pcol, acol, sub in products_to_gen:
        generate_product_image(filename, cat, title, pcol, acol, sub)
        
    print("All assets successfully generated!")
