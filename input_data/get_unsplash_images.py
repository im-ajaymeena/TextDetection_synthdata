#! /bin/python3
import requests


# Step 1: Sign up for an Unsplash API key and set up dotenv

# Step 2: Install the requests ibraries

# Step 3: Define the API endpoint and parameters
page = 1
while True:
    page+=1
    endpoint = "https://api.unsplash.com/search/photos"
    params = {
        "client_id": "TiiWIqTuccOTsuKogpFw17rBbN75d690mSqfFcOipVE", # get your API key from  https://unsplash.com/developers
        "query": "japan", # query for image search change accordingly to the domain
        "per_page": 30,
        "page": page,
        "orientation": "landscape",
    }

    # Step 4: Send a GET request to the API endpoint with the parameters
    response = requests.get(endpoint, params=params)

    # Step 5: Parse the response JSON data and extract the image URLs
    data = response.json()
    image_urls = [result["urls"]["full"] for result in data["results"]]

    # Step 6: Download the raw_images and save them to a local directory
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        with open(f"./raw_images/image_unsplash_p{page}_{i+1}.jpg", "wb") as f:
            f.write(response.content)
