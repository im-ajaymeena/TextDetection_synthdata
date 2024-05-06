import docker
import os
from PIL import Image
import uuid
import random
random.seed(0)

wordart_themes_filtered = [
    'outline', 'arc','squeeze','inverted-arc','basic-stack',
    'italic-outline','slate','mauve','graydient','red-blue','brown-stack',
    'radial', 'rainbow','aqua','texture-stack',
    'paper-bag','sunset','tilt','blues','yellow-dash','green-stack',
    'chrome','marble-slab', 'horizon','stack-3d'
]

def generate_wordart_image(text):
    client = docker.from_env()  # Initialize Docker client
    
    # Choose a random art style from the filtered list
    art_style = random.choice(wordart_themes_filtered)
    
    try:
        container = client.containers.run(
            "toastymallows/wordart-on-demand:latest",
            f"-w '{text}' -a {art_style} ",
            remove=True,
            volumes={'/home/ajay/work/ocr/datasets/Synthetic_OCR_dataset/wordart_gen/output': {'bind': '/wordart/out', 'mode': 'rw'}}
        )
        
        output_path = "/home/ajay/work/ocr/datasets/Synthetic_OCR_dataset/wordart_gen/output"
        # Get the list of files in the output directory
        output_files = os.listdir(output_path)
        
        # Filter only image files and sort by modification time
        image_files = [f for f in output_files if f.endswith('.png')]
        image_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_path, x)), reverse=True)
        
        latest_image_path = os.path.join(output_path, image_files[0])
        return Image.open(latest_image_path),  art_style # Return the latest PIL format image
    except docker.errors.APIError as e:
        print("Error executing Docker command:", e)
        raise

def generate_wordart_images(text_list):
    wordart_images = []
    art_styles = []
    for text in text_list:
        wordart_image, art_style = generate_wordart_image(text)
        if wordart_image:
            wordart_images.append(wordart_image)
            art_styles.append(art_style)
    return wordart_images, art_styles


if __name__ == "__main__":
    # Example usage: this will save wordArt corresponding to following text in the current directory
    text_list = ["Hello World", "Python is awesome", "OpenAI is incredible"]
    images, _ = generate_wordart_images(text_list)
    for idx, image in enumerate(images):
        image.save(f"wordart_image_{idx}.png")
