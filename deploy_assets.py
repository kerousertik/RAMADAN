import os
from PIL import Image

def resize_and_save(src_path, dst_path, size):
    img = Image.open(src_path)
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    img.save(dst_path)
    print(f"Saved {dst_path} ({size}x{size})")

# Icon configurations (Launcher)
icon_configs = [
    ("mipmap-mdpi", 48),
    ("mipmap-hdpi", 72),
    ("mipmap-xhdpi", 96),
    ("mipmap-xxhdpi", 144),
    ("mipmap-xxxhdpi", 192)
]

base_res = "android/app/src/main/res"

for folder, size in icon_configs:
    resize_and_save("premium_icon.png", f"{base_res}/{folder}/ic_launcher.png", size)
    resize_and_save("premium_icon.png", f"{base_res}/{folder}/ic_launcher_round.png", size)

# Splash configuration
splash_configs = [
    ("drawable", 1024), # Generic
    ("drawable-land-mdpi", 480),
    ("drawable-land-hdpi", 800),
    ("drawable-land-xhdpi", 1280),
    ("drawable-land-xxhdpi", 1600),
    ("drawable-land-xxxhdpi", 1920),
    ("drawable-port-mdpi", 320),
    ("drawable-port-hdpi", 480),
    ("drawable-port-xhdpi", 720),
    ("drawable-port-xxhdpi", 960),
    ("drawable-port-xxxhdpi", 1280),
]

for folder, size in splash_configs:
    # Use generic splash (centered icon on black)
    img = Image.open('premium_splash.png')
    # For simplicity in this script, we just scale but keeping aspect ratio is better.
    # We'll just replace the center drawable for Capacitor.
    os.makedirs(os.path.dirname(f"{base_res}/{folder}/splash.png"), exist_ok=True)
    img.save(f"{base_res}/{folder}/splash.png")

print("\n✅ All native branding assets replaced successfully!")
