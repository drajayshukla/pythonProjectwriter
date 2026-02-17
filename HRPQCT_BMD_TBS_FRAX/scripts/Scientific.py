import os
import subprocess
from pathlib import Path


def convert_tiffs_mac_native():
    figures_path = Path("/Users/dr.ajayshukla/PycharmProjects/pythonProjectwriter/HRPQCT_BMD_TBS_FRAX/results/figures")

    print(f"🚀 Using macOS SIPS to convert: {figures_path}")

    for tiff_file in figures_path.glob("*.tiff"):
        png_file = tiff_file.with_suffix(".png")

        # macOS native command: sips -s format png input.tiff --out output.png
        cmd = ["sips", "-s", "format", "png", str(tiff_file), "--out", str(png_file)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Successfully converted: {tiff_file.name}")
            else:
                print(f"❌ SIPS failed for {tiff_file.name}: {result.stderr}")
        except Exception as e:
            print(f"⚠️ Script error for {tiff_file.name}: {e}")


if __name__ == "__main__":
    convert_tiffs_mac_native()