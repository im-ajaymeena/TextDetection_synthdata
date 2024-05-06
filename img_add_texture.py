from PIL import Image
import random
import os

def add_texture(ImageA, a=None):
    width, height = ImageA.size

    texture_path_list = os.listdir("./input_data/texture_images/")
    texture_name = random.choice(texture_path_list)
    texture_path = os.path.join("./input_data/texture_images/", texture_name)

    replacement_image = Image.open(texture_path)

    region_width = int(width/random.randint(3,5))
    region_height = min(height-2, int(width/(1+random.random()*5)))
    
    x = random.randint(0, width - region_width + 1)
    y = random.randint(0, height - region_height + 1)

    region = (x, y, x + region_width, y + region_height)

    region_image = replacement_image.crop(region)
    ImageA.paste(region_image, region)

    return ImageA
