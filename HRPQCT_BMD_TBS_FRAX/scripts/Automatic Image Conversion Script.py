import os
from PIL import Image
from pathlib import Path


def convert_tiffs_to_png():
    # Use an absolute path based on your error log
    figures_path = Path("/Users/dr.ajayshukla/PycharmProjects/pythonProjectwriter/HRPQCT_BMD_TBS_FRAX/results/figures")

    if not figures_path.exists():
        print(f"❌ Path not found: {figures_path}")
        return

    print(f"🔍 Scanning: {figures_path}")

    for tiff_file in figures_path.glob("*.tiff"):
        png_file = tiff_file.with_suffix(".png")

        try:
            with Image.open(tiff_file) as img:
                # Handle multipage TIFFs (often found in medical imaging)
                img.seek(0)
                rgb_img = img.convert('RGB')
                rgb_img.save(png_file, "PNG", optimize=True)
                print(f"✅ Converted: {tiff_file.name}")
        except Exception as e:
            print(f"⚠️ Could not convert {tiff_file.name}: {e}")
            print(
                "💡 Tip: If this is an HR-pQCT stack, try exporting a single slice as PNG from your reconstruction software.")


if __name__ == "__main__":
    convert_tiffs_to_png()