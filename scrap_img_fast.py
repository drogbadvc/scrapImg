import os
import json
import requests
from slugify import slugify
from concurrent.futures import ThreadPoolExecutor

def download_image(item, index):
    title = slugify(item['title'])
    media = item['media']

    file_name = f"downloaded_images/{title}.jpg"
    if os.path.exists(file_name):
        file_name = f"downloaded_images/{title}_{index}.jpg"

    try:
        img_response = requests.get(media, stream=True)
        img_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors du téléchargement de l'image {media}: {e}")
        return

    with open(file_name, 'wb') as f:
        for chunk in img_response.iter_content(1024):
            f.write(chunk)

def search_image(query):
    url = f"https://api.qwant.com/v3/search/images?t=images&q={query}&count=50&locale=fr_FR&offset=0&device=desktop&safesearch=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la récupération des données de l'API : {e}")
        return

    data = json.loads(response.text)
    items = data['data']['result']['items']

    if not os.path.exists('downloaded_images'):
        os.makedirs('downloaded_images')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for index, item in enumerate(items):
            executor.submit(download_image, item, index)
