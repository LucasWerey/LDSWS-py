import os
from dotenv import load_dotenv
import requests


load_dotenv()
JSON_URL = os.getenv("JSON_URL")


def download_json_from_url(url):
    response = requests.get(url)
    return response


def main():
    data = download_json_from_url(JSON_URL)
    with open("data.json", "wb") as f:
        f.write(data.content)


if __name__ == "__main__":
    main()
