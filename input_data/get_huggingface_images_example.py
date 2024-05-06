from datasets import load_dataset
import os
import requests
from tqdm import tqdm

def download_image(url, save_path):
    try:
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return False

def main():
    # Load the dataset
    dataset = load_dataset("recruit-jp/japanese-image-classification-evaluation-dataset")

    # Create a directory to store images
    output_dir = "./raw_images"

    # Iterate through the dataset and download images
    for item in tqdm(dataset["train"]):
        image_url = item["url"]
        category = item["category"]
        category_dir = os.path.join(output_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)

        image_filename = os.path.basename(image_url)
        save_path = os.path.join(category_dir, image_filename)

        if not os.path.exists(save_path):
            download_image(image_url, save_path)

if __name__ == "__main__":
    main()
