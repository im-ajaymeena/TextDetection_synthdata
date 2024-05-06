import os
from PIL import Image

def resize_images(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.jpg') or filename.endswith('.png'):
                filepath = os.path.join(root, filename)
                print(filepath)
                with Image.open(filepath) as img:
                    width, height = img.size
                    if width != 1280:
                        new_width = 1280
                        new_height = int((new_width / width) * height)
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        resized_img.save(filepath)
                        print(f"{filename} resized and replaced.")
                    else:
                        print(f"{filename} already has width 1280 pixels, skipping.")

# Replace 'directory_path' with the path to your directory containing images
directory_path = './raw_images'
resize_images(directory_path)
