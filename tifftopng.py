import os
from PIL import Image

# We use the absolute path to guarantee the folder is found
base_path = "/Users/dr.ajayshukla/PycharmProjects/pythonProjectwriter/HRPQCT_BMD_TBS_FRAX/results/figures"

# Check if path exists first
if not os.path.exists(base_path):
    print(f"CRITICAL ERROR: Could not find folder at: {base_path}")
else:
    print(f"Processing images in: {base_path}")

    # Loop through files
    for filename in os.listdir(base_path):
        # Check for both .tiff and .tif (case insensitive)
        if filename.lower().endswith((".tiff", ".tif")):
            try:
                # Full path to image
                file_path = os.path.join(base_path, filename)

                # Open and Convert
                img = Image.open(file_path)
                new_filename = os.path.splitext(filename)[0] + ".png"
                save_path = os.path.join(base_path, new_filename)

                img.save(save_path, "PNG")
                print(f"✅ Converted: {filename} -> {new_filename}")

            except Exception as e:
                print(f"❌ Failed to convert {filename}: {e}")

    print("All done!")


