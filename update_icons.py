import shutil
import os

logo_source = r"d:\ramadan2026\public\logo.png"
base_res_path = r"d:\ramadan2026\android\app\src\main\res"
folders = [
    "mipmap-hdpi",
    "mipmap-mdpi",
    "mipmap-xhdpi",
    "mipmap-xxhdpi",
    "mipmap-xxxhdpi"
]
files = [
    "ic_launcher.png",
    "ic_launcher_round.png",
    "ic_launcher_foreground.png"
]

for folder in folders:
    folder_path = os.path.join(base_res_path, folder)
    if os.path.exists(folder_path):
        for file in files:
            dest = os.path.join(folder_path, file)
            print(f"Copying to {dest}")
            shutil.copy2(logo_source, dest)
    else:
        print(f"Skipping missing folder: {folder}")
