from PIL import Image, ImageDraw

def create_premium_icon(size=1024):
    # Base: Deep Dark Blue
    img = Image.new('RGB', (size, size), color=(2, 2, 5))
    draw = ImageDraw.Draw(img)
    
    # Gold Palette
    gold = (212, 165, 52)
    gold_light = (245, 200, 66)
    
    # Draw Crescent Moon
    center = size // 2
    outer_r = size // 3
    inner_r = outer_r - (size // 20)
    
    # Outer circle
    draw.ellipse([center - outer_r, center - outer_r, center + outer_r, center + outer_r], fill=gold)
    
    # Inner circle (offset to create crescent)
    offset = size // 15
    draw.ellipse([center - inner_r - offset, center - inner_r, center + inner_r - offset, center + inner_r], fill=(2, 2, 5))
    
    # Draw Play Button motif inside the crescent
    play_r = size // 8
    p1 = (center + size // 15, center - play_r)
    p2 = (center + size // 15 + play_r * 1.5, center)
    p3 = (center + size // 15, center + play_r)
    draw.polygon([p1, p2, p3], fill=gold_light)
    
    # Add subtle stars
    stars = [(100, 100), (900, 150), (800, 800), (150, 850)]
    for sx, sy in stars:
        r = 5
        draw.ellipse([sx-r, sy-r, sx+r, sy+r], fill=(255, 255, 255))

    return img

def create_splash(size_w=1080, size_h=1920):
    img = Image.new('RGB', (size_w, size_h), color=(0, 0, 0))
    icon = create_premium_icon(size=512)
    
    # Center icon
    pos = ((size_w - 512) // 2, (size_h - 512) // 2 - 100)
    img.paste(icon, pos)
    
    return img

# Generate and save
create_premium_icon().save('premium_icon.png')
create_splash().save('premium_splash.png')
print("Successfully generated premium_icon.png and premium_splash.png")
