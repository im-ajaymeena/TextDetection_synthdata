import requests

# Step 1: Sign up for a Pixabay API key

# Step 2: Install the requests library
# pip install requests

# Step 3: Define the API endpoint and parameters
page = 1
while True:
    page += 1
    endpoint = "https://pixabay.com/api/"
    params = {
        "key": "35313189-a2602555f3fabe279b29261d1", # get your API key from  https://pixabay.com/api/docs/
        "q": "japan", # query for image search change accordingly to the domain
        "image_type": "photo",
        "per_page": 30,
        "page": page,
        "orientation": "horizontal",
    }

    # Step 4: Send a GET request to the API endpoint with the parameters
    response = requests.get(endpoint, params=params)

    # Step 5: Parse the response JSON data and extract the image URLs
    data = response.json()
    image_urls = [hit["largeImageURL"] for hit in data["hits"]]

    # Step 6: Download the raw_images and save them to a local directory
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        with open(f"./raw_images/image_pixalbay_p{page}_{i+1}.jpg", "wb") as f:
            f.write(response.content)
