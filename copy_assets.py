import shutil
import os

src = r"C:\Users\Usman Computers\.gemini\antigravity-ide\brain\4c9c54bf-9f8a-4601-b233-5e40f0b7e223\typing_sprint_logo_1791110616790.jpg"
workspace = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(workspace, "assets")
os.makedirs(assets_dir, exist_ok=True)

dest_jpg = os.path.join(assets_dir, "logo.jpg")
shutil.copyfile(src, dest_jpg)

# Also try to create logo.png and favicon if PIL is available
try:
    from PIL import Image
    im = Image.open(dest_jpg)
    im.save(os.path.join(assets_dir, "logo.png"))
    
    # Create smaller resized icons for navbar, window icon, and web
    icon_64 = im.resize((64, 64), Image.Resampling.LANCZOS)
    icon_64.save(os.path.join(assets_dir, "icon-64.png"))

    icon_32 = im.resize((32, 32), Image.Resampling.LANCZOS)
    icon_32.save(os.path.join(assets_dir, "icon-32.png"))
    
    # Save .ico for Windows shortcut and window
    im.save(os.path.join(assets_dir, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Assets created with PIL successfully.")
except Exception as e:
    print(f"PIL not available or error: {e}, copied JPG directly.")

print(f"Logo copied to {dest_jpg}")
