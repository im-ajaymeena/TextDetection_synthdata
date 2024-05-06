import docker
import os
from PIL import Image
import uuid

# wordart_themes = [
# 	'outline','up','arc','squeeze','inverted-arc','basic-stack',
# 	'italic-outline','slate','mauve','graydient','red-blue','brown-stack',
# 	'radial','purple','green-marble','rainbow','aqua','texture-stack',
# 	'paper-bag','sunset','tilt','blues','yellow-dash','green-stack',
# 	'chrome','marble-slab','gray-block','superhero','horizon','stack-3d'
# ]

wordart_themes_filtered = [
	'outline', 'arc','squeeze','inverted-arc','basic-stack',
	'italic-outline','slate','mauve','graydient','red-blue','brown-stack',
	'radial', 'rainbow','aqua','texture-stack',
	'paper-bag','sunset','tilt','blues','yellow-dash','green-stack',
	'chrome','marble-slab', 'horizon','stack-3d'
]

def generate_wordart(text, art_style="rainbow"):
    client = docker.from_env()  # Initialize Docker client
    
    output_path = "./output"  # Define the output path for the image
    for art_style in wordart_themes_filtered:
        try:
            container = client.containers.run(
                "toastymallows/wordart-on-demand:latest",
                f"-w '{text}' -a {art_style} ",
                remove=True,
                volumes={'/home/ajay/work/ocr/datasets/Synthetic_OCR_dataset/wordart_gen/output': {'bind': '/wordart/out', 'mode': 'rw'}}
            )
            # # Get the list of files in the output directory
            # output_files = os.listdir(output_path)
            # # Rename the image to a UUID
            # if len(output_files) == 1:  # Assuming only one image is generated
            #     original_image_name = output_files[0]
            #     new_image_name = str(uuid.uuid4()) + ".png"
            #     os.rename(os.path.join(output_path, original_image_name), os.path.join(output_path, new_image_name))
            #     return os.path.join(output_path, new_image_name)  # Return the path of the renamed image
            # else:
            #     print("Error: More than one image generated.")
            #     return None
        except docker.errors.APIError as e:
            print("Error executing Docker command:", e)
            # return None

# Example usage:
image_path = generate_wordart("Hello World")
if image_path:
    print("Image generated successfully at:", image_path)
else:
    print("Failed to generate image.")



def overlay_images(background_image_path, text_image_path, output_path, resize_factor=5):
    # Open the background image
    background_image = Image.open(background_image_path)
    
    # Open the text image with transparency
    text_image = Image.open(text_image_path)

    new_width = int(text_image.width * resize_factor)
    new_height = int(text_image.height * resize_factor)
    resized_text_image = text_image.resize((new_width, new_height))
    
    # Overlay the text image onto the background image
    background_image.paste(resized_text_image, (0, 0), resized_text_image)
    
    # Save the overlaid image
    background_image.save(output_path)

background_image_path = "/home/ajay/work/ocr/datasets/Synthetic_OCR_dataset/JPG.jpg"
text_image_path = "/home/ajay/work/ocr/datasets/Synthetic_OCR_dataset/wordart-gen/output/d06a24ac-1c0c-480c-819a-93f3b3a7dec7.png"
output_path = "JPG-out.png"

# overlay_images(background_image_path, text_image_path, output_path)